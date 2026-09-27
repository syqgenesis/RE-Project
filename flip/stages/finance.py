"""Stage H: basic residual appraisal + simple sensitivity. Pure arithmetic, no LLM."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def sdlt(price: float, cfg: dict[str, Any]) -> float:
    """SDLT on a residential purchase for the configured buyer type."""
    s = cfg["sdlt"]
    buyer = cfg["investor"]["buyer_type"]
    if (buyer == "company" and price > 500_000
            and not cfg["investor"].get("company_developer_relief", False)):
        return price * s["company_flat_rate_over_500k"]
    surcharge = s["additional_dwelling_surcharge"] if buyer in ("individual_additional", "company") else 0.0
    tax, lower = 0.0, 0.0
    for upper, rate in s["bands"]:
        top = price if upper is None else min(price, upper)
        if top > lower:
            tax += (top - lower) * (rate + surcharge)
        if upper is None or price <= upper:
            break
        lower = upper
    return round(tax, 2)


@dataclass
class DealInputs:
    gdv: float
    works: float           # before contingency
    planning_fee: float
    months: int


def cost_lines(price: float, d: DealInputs, cfg: dict[str, Any]) -> dict[str, float]:
    c, f = cfg["costs"], cfg["finance"]
    works = d.works * (1 + c["contingency"])
    loan = price * f["ltv_on_purchase"] + (works if f.get("works_funded_by_loan") else 0.0)
    return {
        "purchase": price,
        "sdlt": sdlt(price, cfg),
        "legal_purchase": c["legal_purchase_gbp"],
        "survey": c["survey_gbp"],
        "works_incl_contingency": works,
        "professional_fees": d.works * c["professional_fees_pct_of_works"],
        "planning": d.planning_fee,
        "finance_interest": loan * f["monthly_rate"] * d.months,
        "finance_fees": loan * (f["arrangement_fee"] + f["exit_fee"]),
        "holding": c["holding_per_month_gbp"] * d.months,
        "selling": d.gdv * c["agent_fee_pct_of_gdv"] + c["legal_sale_gbp"],
    }


def profit(price: float, d: DealInputs, cfg: dict[str, Any]) -> tuple[float, float]:
    """Returns (profit, total_cost) at a given purchase price."""
    total = sum(cost_lines(price, d, cfg).values())
    return d.gdv - total, total


def max_price(d: DealInputs, cfg: dict[str, Any], target_poc: float | None = None) -> float | None:
    """Residual: highest price at which profit / total cost >= target. Bisection, since
    SDLT and finance depend on price. Returns None if no positive price works."""
    target = cfg["hurdles"]["target_profit_on_cost"] if target_poc is None else target_poc

    def ok(p: float) -> bool:
        pr, tot = profit(p, d, cfg)
        return pr >= target * tot

    lo, hi = 0.0, d.gdv
    if not ok(lo):
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if ok(mid):
            lo = mid
        else:
            hi = mid
    return round(lo, -2) if lo >= 100 else round(lo, 2)


def sensitivity(d: DealInputs, cfg: dict[str, Any], asking: float | None) -> list[dict]:
    rows = []
    for gdv_shift in (-0.10, -0.05, 0.0, 0.05):
        for works_shift in (0.0, 0.15):
            dd = DealInputs(gdv=d.gdv * (1 + gdv_shift), works=d.works * (1 + works_shift),
                            planning_fee=d.planning_fee, months=d.months)
            row = {"gdv_shift": gdv_shift, "works_shift": works_shift,
                   "max_price": max_price(dd, cfg)}
            if asking:
                pr, tot = profit(asking, dd, cfg)
                row["profit_at_asking"] = round(pr)
                row["poc_at_asking"] = round(pr / tot, 4) if tot else None
            rows.append(row)
    return rows
