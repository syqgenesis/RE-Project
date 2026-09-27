"""HM Land Registry open data kept on disk: Price Paid CSVs and INSPIRE index polygons.

- Price Paid: download the yearly files (pp-2025.csv, pp-2026.csv ...) from GOV.UK into data/ppd/.
- INSPIRE: download the Cambridge GML from use-land-property-data.service.gov.uk into data/inspire/.
"""

from __future__ import annotations

import csv
import datetime as dt
import re
from functools import lru_cache
from pathlib import Path

from flip.config import ROOT

PPD_DIR = ROOT / "data" / "ppd"
INSPIRE_DIR = ROOT / "data" / "inspire"

# Price Paid column order (files have no header)
PPD_COLS = ["txn", "price", "date", "postcode", "type", "new_build", "duration", "paon", "saon",
            "street", "locality", "town", "district", "county", "category", "status"]
TYPE_MAP = {"D": "detached", "S": "semi", "T": "terrace", "F": "flat", "O": "other"}


def sector(postcode: str) -> str:
    pc = postcode.upper().strip()
    out, _, inw = pc.partition(" ")
    return f"{out} {inw[:1]}" if inw else pc[:-2]


def price_paid(postcode_sectors: set[str], since: dt.date, ppd_dir: Path = PPD_DIR) -> list[dict]:
    rows: list[dict] = []
    for f in sorted(ppd_dir.glob("*.csv")):
        with open(f, newline="", encoding="utf-8", errors="replace") as fh:
            for rec in csv.reader(fh):
                if len(rec) < 15:
                    continue
                r = dict(zip(PPD_COLS, rec))
                if r["status"] == "D" or not r["postcode"]:
                    continue
                if sector(r["postcode"]) not in postcode_sectors:
                    continue
                d = dt.date.fromisoformat(r["date"][:10])
                if d < since or r["category"] != "A":  # standard price-paid only
                    continue
                address = " ".join(x for x in (r["saon"], r["paon"], r["street"]) if x).title()
                rows.append({"address": address, "street": r["street"].title(), "postcode": r["postcode"],
                             "date": d.isoformat(), "price": float(r["price"]),
                             "property_type": TYPE_MAP.get(r["type"], "other"),
                             "tenure": "freehold" if r["duration"] == "F" else "leasehold",
                             "new_build": r["new_build"] == "Y"})
    return rows


# ---------- INSPIRE ----------

@lru_cache(maxsize=1)
def _inspire_polygons(inspire_dir: str = str(INSPIRE_DIR)):
    from shapely.geometry import Polygon

    polys = []
    for f in Path(inspire_dir).glob("*.gml"):
        text = f.read_text(errors="replace")
        for m in re.finditer(r"<gml:posList[^>]*>([^<]+)</gml:posList>", text):
            nums = [float(v) for v in m.group(1).split()]
            pts = list(zip(nums[0::2], nums[1::2]))
            if len(pts) >= 4:
                polys.append(Polygon(pts))
    return polys


def plot_for_point(lat: float, lon: float) -> dict | None:
    """Freehold title polygon containing the point (British National Grid metres)."""
    polys = _inspire_polygons()
    if not polys:
        return None
    from pyproj import Transformer
    from shapely.geometry import Point

    x, y = Transformer.from_crs(4326, 27700, always_xy=True).transform(lon, lat)
    pt = Point(x, y)
    hits = [p for p in polys if p.contains(pt)]
    if not hits:
        return {"found": False}
    poly = min(hits, key=lambda p: p.area)
    rect = poly.minimum_rotated_rectangle
    xs = list(rect.exterior.coords)
    sides = sorted(((xs[i][0] - xs[i + 1][0]) ** 2 + (xs[i][1] - xs[i + 1][1]) ** 2) ** 0.5 for i in range(2))
    return {"found": True, "area_m2": round(poly.area, 1), "short_side_m": round(sides[0], 1),
            "long_side_m": round(sides[1], 1)}
