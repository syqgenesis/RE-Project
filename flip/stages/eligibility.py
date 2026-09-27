"""Stage B: eligibility gate (CB1, freehold house, not listed) + constraint record."""

from __future__ import annotations

from typing import Any

from flip.ledger import Ledger
from flip.models import Constraints, Property
from flip.sources import land_registry, web


def tenure_class(tenure: str | None) -> str:
    t = (tenure or "").lower()
    if "share" in t:
        return "share_of_freehold"
    if "lease" in t:
        return "leasehold"
    if "free" in t:
        return "freehold"
    return "unknown"


def eligibility(p: Property, cfg: dict[str, Any], ledger: Ledger,
                use_web: bool = True) -> tuple[Constraints, str | None]:
    """Returns (constraints, exclusion_reason or None)."""
    c = Constraints()

    if p.outward_code and p.outward_code.upper() not in cfg["scope"]["outward_codes"]:
        return c, f"Outside scope: {p.outward_code} is not in {cfg['scope']['outward_codes']}."
    if not p.outward_code:
        ledger.add("in_scope", None, "unknown", "stage B", note="No postcode, so CB1 can't be confirmed.")

    if p.property_type == "flat":
        return c, "Flat/maisonette: not a house."

    tc = tenure_class(p.tenure)
    if tc in ("leasehold", "share_of_freehold"):
        return c, f"Tenure is {tc.replace('_', ' ')}; only freehold houses qualify."
    if tc == "freehold" and p.title_checked:
        ledger.add("tenure", tc, "verified", "HMLR title register (per case input)")
    else:
        ledger.add("tenure", tc, "estimate" if tc == "freehold" else "unknown",
                   "listing text", note="Verify with the HMLR title register (£7) before offer.")

    if p.lat is not None:
        plot = land_registry.plot_for_point(p.lat, p.lon)
        if plot and plot.get("found"):
            c.freehold_polygon_found = True
            c.plot_area_m2 = plot["area_m2"]
            c.plot_frontage_m = plot["short_side_m"]
            ledger.add("plot_area_m2", c.plot_area_m2, "estimate", "HMLR INSPIRE polygon")
            ledger.add("plot_frontage_m", c.plot_frontage_m, "estimate", "INSPIRE min. rectangle (short side)")
        elif plot is not None:
            c.freehold_polygon_found = False
            ledger.add("freehold_polygon", False, "inference", "HMLR INSPIRE",
                       note="No freehold polygon at this point: location may be a centroid, or land unregistered.")

    if p.lat is None or not use_web:
        ledger.add("constraints", None, "unknown", "planning.data.gov.uk",
                   note="Not checked (no location or web disabled). Listing status NOT cleared.")
        return c, None

    near = web.planning_entities(web.buffer_wkt(p.lat, p.lon, 30))
    if near is None:
        ledger.add("constraints", None, "unknown", "planning.data.gov.uk",
                   note="API unavailable. Listing status NOT cleared.")
        return c, None
    subject = web.planning_entities(web.buffer_wkt(p.lat, p.lon, 6),
                                    ["listed-building", "listed-building-outline"]) or []

    def any_ds(ents, *ds):
        return [e for e in ents if e.get("dataset") in ds]

    c.listed_subject = bool(subject)
    c.listed_adjacent = bool(any_ds(near, "listed-building", "listed-building-outline")) and not c.listed_subject
    c.conservation_area = bool(any_ds(near, "conservation-area"))
    c.article_4 = bool(any_ds(near, "article-4-direction-area"))
    c.tpo = bool(any_ds(near, "tree-preservation-zone", "tree"))
    c.green_belt = bool(any_ds(near, "green-belt"))
    zones = [int(str(e.get("flood-risk-level", "0"))[:1] or 0) for e in any_ds(near, "flood-risk-zone")]
    c.flood_zone = max(zones) if zones else 1
    src = "planning.data.gov.uk"
    note_pt = None if p.identity_confidence == "high" else "Location is approximate; confirm on site."
    for key in ("listed_subject", "listed_adjacent", "conservation_area", "article_4", "tpo",
                "green_belt", "flood_zone"):
        ledger.add(key, getattr(c, key), "verified" if note_pt is None else "estimate", src, note=note_pt)

    if c.listed_subject:
        names = ", ".join(e.get("name", "") for e in subject)[:120]
        return c, f"Statutory listed building ({names}). Excluded."
    return c, None
