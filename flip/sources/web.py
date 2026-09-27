"""Online sources: listing page, geocoding, planning constraints, EPC, imagery.

All network calls go through `http()` so they can be swapped in tests. Each function degrades to
None/[] on failure; the calling stage records the gap in the evidence ledger.
"""

from __future__ import annotations

import io
import json
import math
import os
import re
from pathlib import Path
from typing import Any

import httpx

UA = {"User-Agent": "Mozilla/5.0 (flip-analyser; personal research)"}
_client: httpx.Client | None = None


def http() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(headers=UA, timeout=30, follow_redirects=True)
    return _client


# ---------- listing ----------

def fetch_listing(url: str) -> dict[str, Any] | None:
    try:
        html = http().get(url).text
    except httpx.HTTPError:
        return None
    return parse_listing_html(html, url)


def parse_listing_html(html: str, url: str = "") -> dict[str, Any] | None:
    """Rightmove embeds `window.PAGE_MODEL = {...}`; Zoopla embeds __NEXT_DATA__."""
    m = re.search(r"window\.PAGE_MODEL\s*=\s*(\{.*?\})\s*</script>", html, re.S)
    if m:
        pd = json.loads(m.group(1)).get("propertyData", {})
        addr = pd.get("address", {}) or {}
        tenure = (pd.get("tenure") or {}).get("tenureType")
        sizings = pd.get("sizings") or []
        sqm = next((s.get("minimumSize") for s in sizings if s.get("unit") == "sqm"), None)
        loc = pd.get("location") or {}
        return {
            "source": "rightmove",
            "address": addr.get("displayAddress"),
            "postcode": " ".join(p for p in (addr.get("outcode"), addr.get("incode")) if p) or None,
            "asking_price": _num((pd.get("prices") or {}).get("primaryPrice")),
            "tenure": tenure,
            "property_type": pd.get("propertySubType"),
            "bedrooms": pd.get("bedrooms"),
            "floor_area_m2": sqm,
            "description": re.sub(r"<[^>]+>", " ", (pd.get("text") or {}).get("description") or ""),
            "key_features": pd.get("keyFeatures") or [],
            "photos": [i.get("url") for i in pd.get("images") or [] if i.get("url")],
            "floorplans": [i.get("url") for i in pd.get("floorplans") or [] if i.get("url")],
            "lat": loc.get("latitude"), "lon": loc.get("longitude"),
            "epc_graphs": [i.get("url") for i in pd.get("epcGraphs") or []],
        }
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if m:
        data = json.loads(m.group(1))
        listing = _find_key(data, "listingDetails") or {}
        return {
            "source": "zoopla",
            "address": listing.get("displayAddress"),
            "postcode": (listing.get("location") or {}).get("postalCode"),
            "asking_price": _num((listing.get("pricing") or {}).get("value")),
            "tenure": (listing.get("tenure") or {}).get("type") if isinstance(listing.get("tenure"), dict) else listing.get("tenure"),
            "property_type": listing.get("propertyType"),
            "bedrooms": (listing.get("counts") or {}).get("numBedrooms"),
            "floor_area_m2": None,
            "description": listing.get("detailedDescription"),
            "photos": [], "floorplans": [],
            "lat": ((listing.get("location") or {}).get("coordinates") or {}).get("latitude"),
            "lon": ((listing.get("location") or {}).get("coordinates") or {}).get("longitude"),
        }
    return None


def _find_key(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = _find_key(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _find_key(v, key)
            if r is not None:
                return r
    return None


def _num(v: Any) -> float | None:
    if v is None:
        return None
    s = re.sub(r"[^\d.]", "", str(v))
    return float(s) if s else None


def download(url: str, dest: Path) -> str | None:
    if dest.exists():
        return str(dest)
    try:
        r = http().get(url)
        r.raise_for_status()
    except httpx.HTTPError:
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)
    return str(dest)


# ---------- geocoding (postcodes.io, no key) ----------

def geocode_postcode(postcode: str) -> dict[str, Any] | None:
    try:
        r = http().get(f"https://api.postcodes.io/postcodes/{postcode.replace(' ', '')}")
        if r.status_code != 200:
            return None
        res = r.json()["result"]
        return {"lat": res["latitude"], "lon": res["longitude"], "outward_code": res["outcode"],
                "postcode": res["postcode"]}
    except (httpx.HTTPError, KeyError, ValueError):
        return None


def bulk_geocode(postcodes: list[str]) -> dict[str, tuple[float, float]]:
    out: dict[str, tuple[float, float]] = {}
    uniq = sorted({p for p in postcodes if p})
    for i in range(0, len(uniq), 100):
        try:
            r = http().post("https://api.postcodes.io/postcodes", json={"postcodes": uniq[i:i + 100]})
            for item in r.json().get("result", []):
                res = item.get("result")
                if res:
                    out[item["query"]] = (res["latitude"], res["longitude"])
        except (httpx.HTTPError, ValueError):
            continue
    return out


# ---------- planning constraints (planning.data.gov.uk, OGL, no key) ----------

CONSTRAINT_DATASETS = ["conservation-area", "listed-building", "listed-building-outline",
                       "article-4-direction-area", "tree-preservation-zone", "tree",
                       "green-belt", "flood-risk-zone"]


def buffer_wkt(lat: float, lon: float, metres: float) -> str:
    dlat = metres / 111_000
    dlon = metres / (111_000 * math.cos(math.radians(lat)))
    pts = [(lon - dlon, lat - dlat), (lon + dlon, lat - dlat), (lon + dlon, lat + dlat),
           (lon - dlon, lat + dlat), (lon - dlon, lat - dlat)]
    return "POLYGON((" + ", ".join(f"{x:.6f} {y:.6f}" for x, y in pts) + "))"


def planning_entities(geometry_wkt: str, datasets: list[str] | None = None) -> list[dict] | None:
    params: list[tuple[str, str]] = [("geometry", geometry_wkt), ("geometry_relation", "intersects"),
                                     ("limit", "100")]
    params += [("dataset", d) for d in (datasets or CONSTRAINT_DATASETS)]
    try:
        r = http().get("https://www.planning.data.gov.uk/entity.json", params=params)
        r.raise_for_status()
        return r.json().get("entities", [])
    except (httpx.HTTPError, ValueError):
        return None


# ---------- EPC (floor areas) ----------

def epc_by_postcode(postcode: str) -> list[dict] | None:
    """EPC register search. Base URL and auth are configurable because the service has moved."""
    token = os.environ.get("EPC_API_TOKEN")
    if not token:
        return None
    base = os.environ.get("EPC_API_BASE", "https://epc.opendatacommunities.org/api/v1/domestic/search")
    auth_header = os.environ.get("EPC_AUTH_HEADER", f"Basic {token}")
    try:
        r = http().get(base, params={"postcode": postcode, "size": 500},
                       headers={"Accept": "application/json", "Authorization": auth_header})
        r.raise_for_status()
        rows = r.json().get("rows", [])
    except (httpx.HTTPError, ValueError):
        return None
    return [{"address": " ".join(x for x in (row.get("address1"), row.get("address2")) if x),
             "postcode": row.get("postcode"), "uprn": row.get("uprn"),
             "floor_area_m2": _num(row.get("total-floor-area")),
             "property_type": row.get("property-type"), "built_form": row.get("built-form"),
             "rating": row.get("current-energy-rating"),
             "score": _num(row.get("current-energy-efficiency")),
             "lodged": row.get("lodgement-date")} for row in rows]


# ---------- imagery (Esri World Imagery + Wayback, no key) ----------

def _tile_xy(lat: float, lon: float, z: int) -> tuple[float, float]:
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def stitch_tiles(url_tpl: str, lat: float, lon: float, z: int = 19, span: int = 3) -> bytes | None:
    """Fetch span x span tiles around the point and return a PNG centred on it."""
    from PIL import Image

    fx, fy = _tile_xy(lat, lon, z)
    cx, cy = int(fx), int(fy)
    half = span // 2
    canvas = Image.new("RGB", (256 * span, 256 * span))
    got = 0
    for dx in range(-half, half + 1):
        for dy in range(-half, half + 1):
            url = url_tpl.format(z=z, x=cx + dx, y=cy + dy, level=z, col=cx + dx, row=cy + dy)
            try:
                r = http().get(url)
                if r.status_code != 200:
                    continue
                tile = Image.open(io.BytesIO(r.content)).convert("RGB")
            except (httpx.HTTPError, OSError):
                continue
            canvas.paste(tile, ((dx + half) * 256, (dy + half) * 256))
            got += 1
    if not got:
        return None
    px = (half + fx - cx) * 256
    py = (half + fy - cy) * 256
    draw_size = 6
    from PIL import ImageDraw
    d = ImageDraw.Draw(canvas)
    d.ellipse([px - draw_size, py - draw_size, px + draw_size, py + draw_size], outline="red", width=3)
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue()


ESRI_CURRENT = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
WAYBACK_CONFIG = "https://s3-us-west-2.amazonaws.com/config.maptiles.arcgis.com/waybackconfig.json"


def wayback_releases() -> list[dict]:
    """[{release, date, url_tpl}] oldest first."""
    try:
        cfg = http().get(WAYBACK_CONFIG).json()
    except (httpx.HTTPError, ValueError):
        return []
    out = []
    for num, item in cfg.items():
        m = re.search(r"(\d{4}-\d{2}-\d{2})", item.get("itemTitle", ""))
        tpl = item.get("itemURL")
        if m and tpl:
            out.append({"release": num, "date": m.group(1),
                        "url_tpl": tpl.replace("{level}", "{z}").replace("{row}", "{y}").replace("{col}", "{x}")})
    return sorted(out, key=lambda r: r["date"])


def pick_spread(releases: list[dict], n: int = 4) -> list[dict]:
    """One release per era: oldest, newest, and evenly spaced between."""
    if len(releases) <= n:
        return releases
    idx = sorted({round(i * (len(releases) - 1) / (n - 1)) for i in range(n)})
    return [releases[i] for i in idx]
