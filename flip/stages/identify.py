"""Stage A: resolve the input to one identified property."""

from __future__ import annotations

import re

from flip.ledger import Ledger
from flip.models import CaseInput, Property
from flip.sources import web

POSTCODE_RE = re.compile(r"\b([A-Z]{1,2}\d[A-Z\d]?)\s*(\d[A-Z]{2})\b", re.I)


def split_address(address: str | None) -> tuple[str | None, str | None]:
    """'12a Mill Road, Cambridge' -> ('12a', 'Mill Road')."""
    if not address:
        return None, None
    first = address.split(",")[0].strip()
    m = re.match(r"^(flat\s+\w+\s+)?(\d+[a-z]?)\s+(.+)$", first, re.I)
    if m:
        return m.group(2), m.group(3).strip().title()
    return None, first.title() if first else None


def normalise_type(raw: str | None) -> str | None:
    if not raw:
        return None
    r = raw.lower()
    for key, val in (("maisonette", "flat"), ("flat", "flat"), ("apartment", "flat"),
                     ("end", "end-terrace"), ("semi", "semi"), ("terrace", "terrace"), ("town", "terrace"),
                     ("bungalow", "bungalow"), ("detached", "detached"), ("cottage", "terrace")):
        if key in r:
            return val
    return r


def identify(case: CaseInput, ledger: Ledger, use_web: bool = True) -> Property:
    listing = web.fetch_listing(case.url) if (case.url and use_web) else None
    src = "listing" if listing else "case input"
    if case.url and use_web and not listing:
        ledger.add("listing_fetch", "failed", "unknown", case.url,
                   note="Listing page not parsed; using case input only.")
    listing = listing or {}

    def pick(field: str):
        v = getattr(case, field, None)
        if v not in (None, "", []):
            return v, "case input"
        v = listing.get(field)
        return (v, src) if v not in (None, "", []) else (None, None)

    p = Property(case_id=case.case_id, listing_url=case.url)
    for field in ("address", "postcode", "asking_price", "tenure", "bedrooms", "floor_area_m2",
                  "description", "photos", "floorplans"):
        val, source = pick(field)
        if val is not None:
            setattr(p, field, val)
            if field not in ("description", "photos", "floorplans"):
                ledger.add(field, val, "verified" if field == "asking_price" else "estimate",
                           source or "")
    ptype, source = pick("property_type")
    p.property_type = normalise_type(ptype)
    if p.property_type:
        ledger.add("property_type", p.property_type, "estimate", source or "")
    p.historical_images = case.historical_images
    p.title_checked = case.title_checked

    if not p.postcode and p.address:
        m = POSTCODE_RE.search(p.address)
        if m:
            p.postcode = f"{m.group(1)} {m.group(2)}".upper()
    if p.postcode:
        p.postcode = p.postcode.upper()
    p.house_number, p.street = split_address(p.address)

    lat, lon = listing.get("lat"), listing.get("lon")
    geo = web.geocode_postcode(p.postcode) if (p.postcode and use_web) else None
    if geo:
        p.outward_code = geo["outward_code"]
        p.postcode = geo["postcode"]
        if lat is None:
            lat, lon = geo["lat"], geo["lon"]
            ledger.add("location", f"{lat:.5f},{lon:.5f}", "estimate", "postcodes.io",
                       note="Postcode centroid, not the exact house.")
    elif p.postcode:
        p.outward_code = p.postcode.split()[0] if " " in p.postcode else p.postcode[:-3]
    p.lat, p.lon = lat, lon
    if lat is not None and listing.get("lat") is not None:
        ledger.add("location", f"{lat:.5f},{lon:.5f}", "estimate", "listing map pin")

    # EPC: floor area, UPRN, and the house number when the portal hides it
    epc = web.epc_by_postcode(p.postcode) if (p.postcode and use_web) else None
    if epc:
        match = None
        if p.house_number:
            match = next((e for e in epc if re.match(rf"^(flat \w+,? )?{re.escape(p.house_number)}\b",
                                                        e["address"], re.I)), None)
        elif p.floor_area_m2:
            close = [e for e in epc if e["floor_area_m2"] and abs(e["floor_area_m2"] - p.floor_area_m2) <= 2]
            if len(close) == 1:
                match = close[0]
                ledger.add("address_from_epc", match["address"], "inference", "EPC register",
                           note="Matched on postcode + floor area; confirm on Street View.")
                p.address = f"{match['address']}, {p.postcode}"
                p.house_number, p.street = split_address(match["address"])
        if match:
            p.uprn = match.get("uprn")
            if not p.floor_area_m2 and match.get("floor_area_m2"):
                p.floor_area_m2 = match["floor_area_m2"]
                ledger.add("floor_area_m2", p.floor_area_m2, "verified", "EPC register")
            ledger.add("epc_rating", match.get("rating"), "verified", "EPC register")

    if p.house_number and p.postcode:
        p.identity_confidence = "high" if p.uprn or p.lat else "medium"
    elif p.street and p.postcode:
        p.identity_confidence = "medium"
    ledger.add("identity_confidence", p.identity_confidence, "inference", "stage A")
    return p
