"""Stage F: resale value from sold comparables (code), sense-checked by the LLM, recomputed by code."""

from __future__ import annotations

import datetime as dt
import re
from typing import Any

from flip.ledger import Ledger
from flip.llm import runner
from flip.models import Comp, CompReview, Property, Valuation
from flip.sources import land_registry, web
from flip.sources.user_db import haversine_m

SAME_TYPE = {"detached": {"detached"}, "bungalow": {"detached"}, "semi": {"semi"},
             "terrace": {"terrace"}, "end-terrace": {"terrace", "semi"}}


def wquantile(values: list[float], weights: list[float], q: float) -> float:
    pairs = sorted(zip(values, weights))
    total = sum(w for _, w in pairs)
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= q * total:
            return v
    return pairs[-1][0]


def gather_comps(p: Property, cfg: dict[str, Any], ledger: Ledger, use_web: bool,
                 today: dt.date | None = None) -> tuple[list[Comp], bool]:
    v = cfg["valuation"]
    today = today or dt.date.today()
    if not p.postcode:
        return [], False
    rows = land_registry.price_paid({land_registry.sector(p.postcode)},
                                    today - dt.timedelta(days=30 * v["comps_expand_months"]))
    if not rows:
        ledger.add("comps_source", None, "unknown", "HMLR Price Paid",
                   note="No Price Paid files in data/ppd/ (or no sales in the sector).")
        return [], False
    wanted = SAME_TYPE.get(p.property_type or "", {"detached", "semi", "terrace"})
    rows = [r for r in rows if r["property_type"] in wanted]
    coords = web.bulk_geocode([r["postcode"] for r in rows]) if (use_web and p.lat is not None) else {}
    comps = []
    for r in rows:
        d = None
        if r["postcode"] in coords and p.lat is not None:
            d = haversine_m(p.lat, p.lon, *coords[r["postcode"]])
        comps.append(Comp(address=r["address"], postcode=r["postcode"], date=r["date"], price=r["price"],
                          property_type=r["property_type"], tenure=r["tenure"], distance_m=d))

    def within(c: Comp, radius: float, months: int) -> bool:
        recent = dt.date.fromisoformat(c.date) >= today - dt.timedelta(days=30 * months)
        near = c.distance_m is None or c.distance_m <= radius
        return recent and near

    tight = [c for c in comps if within(c, v["comps_radius_m"], v["comps_months"])]
    widened = len(tight) < v["min_comps"]
    chosen = [c for c in comps if within(c, v["comps_expand_radius_m"], v["comps_expand_months"])] if widened else tight
    chosen.sort(key=lambda c: (c.distance_m if c.distance_m is not None else 9e9, c.date))
    chosen = chosen[:25]

    # floor areas from EPC, per comp postcode
    if use_web:
        epc_cache: dict[str, list[dict] | None] = {}
        for c in chosen:
            if c.postcode not in epc_cache:
                epc_cache[c.postcode] = web.epc_by_postcode(c.postcode)
            num = re.match(r"^(\d+[A-Za-z]?)\b", c.address)
            for e in epc_cache[c.postcode] or []:
                if num and re.match(rf"^{re.escape(num.group(1))}\b", e["address"], re.I):
                    c.floor_area_m2 = e["floor_area_m2"]
                    break
    return chosen, widened


def compute(val: Valuation, p: Property, cfg: dict[str, Any]) -> Valuation:
    v = cfg["valuation"]
    live = [c for c in val.comps if not c.excluded]
    with_area = [c for c in live if c.ppsm]
    val.street_ceiling = max((c.price for c in live), default=None)
    if with_area and p.floor_area_m2:
        vals, w = [c.ppsm for c in with_area], [c.weight for c in with_area]
        val.ppsm_median = round(wquantile(vals, w, 0.5))
        val.ppsm_as_is = round(wquantile(vals, w, v["as_is_quantile"]))
        val.ppsm_refurbished = round(wquantile(vals, w, v["refurbished_quantile"]))
        val.value_as_is = round(val.ppsm_as_is * p.floor_area_m2, -3)
        val.value_refurbished = round(val.ppsm_refurbished * p.floor_area_m2, -3)
    elif live:  # no floor areas: price-only fallback
        prices, w = [c.price for c in live], [c.weight for c in live]
        val.value_as_is = round(wquantile(prices, w, v["as_is_quantile"]), -3)
        val.value_refurbished = round(wquantile(prices, w, v["refurbished_quantile"]), -3)
    if val.value_refurbished and val.street_ceiling:
        val.value_refurbished = min(val.value_refurbished, val.street_ceiling * v["street_ceiling_multiple"])
    return val


def valuation(p: Property, cfg: dict[str, Any], ledger: Ledger, scope: str,
              use_web: bool = True, comps: list[Comp] | None = None) -> Valuation:
    if comps is None:
        comps, widened = gather_comps(p, cfg, ledger, use_web)
    else:
        widened = False
    val = compute(Valuation(comps=comps, search_widened=widened), p, cfg)
    ledger.add("comps_used", len(comps), "verified", "HMLR Price Paid",
               note="search widened" if widened else None)
    if not comps:
        return val
    val.pre_review_value_refurbished = val.value_refurbished

    listing = (p.description or "")[:2000]
    table = "\n".join(
        f"[{i}] {c.address} {c.postcode} | {c.date} | £{c.price:,.0f} | {c.property_type} | "
        f"{c.floor_area_m2 or '?'} m2 | £/m2 {round(c.ppsm) if c.ppsm else '?'} | "
        f"{round(c.distance_m) if c.distance_m is not None else '?'} m" for i, c in enumerate(comps))
    ctx = (f"Subject: {p.address}, {p.property_type}, {p.bedrooms} bed, {p.floor_area_m2} m2, "
           f"condition scope {scope}.\nListing: {listing}\n\nComparables:\n{table}\n\n"
           f"Computed: median £/m2 {val.ppsm_median}, as-is value {val.value_as_is}, "
           f"refurbished value {val.value_refurbished}, street ceiling {val.street_ceiling}")
    try:
        review = runner.run("comps_review", CompReview, ctx)
    except runner.LLMUnavailable as e:
        ledger.add("llm_comps_review", str(e), "unknown", "claude")
        review = None
    if review:
        for adj in review.adjustments:
            if adj.comp_index is None or not 0 <= adj.comp_index < len(comps):
                continue
            c = comps[adj.comp_index]
            if adj.action == "exclude":
                c.excluded, c.exclusion_reason = True, adj.reason
            elif adj.action == "weight" and adj.weight is not None:
                c.weight = max(0.2, min(2.0, adj.weight))
        val = compute(val, p, cfg)
        val.review_comment = review.comment
        if val.pre_review_value_refurbished and val.value_refurbished:
            val.review_shift = round(val.value_refurbished / val.pre_review_value_refurbished - 1, 4)
        ledger.add("comps_review", review.comment, "inference", "LLM sense-check, code recompute",
                   note=f"{len(review.adjustments)} adjustments; shift {val.review_shift}")

    status = "estimate" if (val.ppsm_median and p.floor_area_m2) else "inference"
    for k in ("ppsm_median", "value_as_is", "value_refurbished", "street_ceiling"):
        if getattr(val, k) is not None:
            ledger.add(k, getattr(val, k), status, "HMLR Price Paid + EPC floor areas")
    return val
