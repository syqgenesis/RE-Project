"""Stages H + I: residual appraisal per scheme, then deterministic verdict rules."""

from __future__ import annotations

from typing import Any

from flip.ledger import Ledger
from flip.models import Appraisal, Constraints, ImageryResult, PlanningResult, Property, Scheme, Valuation, Verdict
from flip.stages.finance import DealInputs, cost_lines, max_price, profit, sensitivity


def appraise(s: Scheme, asking: float | None, cfg: dict[str, Any]) -> Appraisal | None:
    if not s.feasible or not s.gdv or s.works_cost is None or s.months is None:
        return None
    d = DealInputs(gdv=s.gdv, works=s.works_cost, planning_fee=s.planning_fee, months=s.months)
    a = Appraisal(strategy=s.strategy, gdv=s.gdv, max_price=max_price(d, cfg),
                  profit_at_asking=None, poc_at_asking=None, total_cost_at_asking=None,
                  months=s.months, sensitivity=sensitivity(d, cfg, asking))
    stress = DealInputs(gdv=s.gdv * 0.9, works=s.works_cost * 1.15, planning_fee=s.planning_fee,
                        months=s.months)
    a.stress_max_price = max_price(stress, cfg, target_poc=0.0)
    if asking:
        pr, tot = profit(asking, d, cfg)
        a.profit_at_asking, a.total_cost_at_asking = round(pr), round(tot)
        a.poc_at_asking = round(pr / tot, 4)
        a.cost_lines_at_asking = {k: round(v) for k, v in cost_lines(asking, d, cfg).items()}
        a.stress_profit_at_asking = round(profit(asking, stress, cfg)[0])
    return a


def decide(p: Property, c: Constraints, excluded: str | None, v: Valuation | None,
           plan: PlanningResult | None, img: ImageryResult | None, schemes: list[Scheme],
           appraisals: list[Appraisal], cfg: dict[str, Any], ledger: Ledger) -> Verdict:
    h = cfg["hurdles"]
    if excluded:
        return Verdict(code="EXCLUDED", reasons=[excluded])
    reasons: list[str] = []
    if p.identity_confidence == "low":
        reasons.append("Property not identified reliably (no postcode/address).")
    if not p.asking_price:
        reasons.append("No asking price.")
    if not appraisals:
        reasons.append("No strategy could be valued (missing comps, floor area or plot data).")
        for s in schemes:
            reasons += [f"{s.strategy}: {n}" for n in s.notes if "unknown" in n.lower() or "needs" in n.lower()]
    if reasons:
        return Verdict(code="INSUFFICIENT_EVIDENCE", reasons=reasons)

    best = max(appraisals, key=lambda a: a.max_price or -1)
    scheme = next(s for s in schemes if s.strategy == best.strategy)
    asking = p.asking_price

    conditions: list[str] = []
    if ledger.status("tenure") != "verified":
        conditions.append("Confirm freehold on the HMLR title register (£7) and check covenants.")
    if c.listed_subject is None:
        conditions.append("Listed-building status not cleared (constraints lookup unavailable).")
    if c.listed_adjacent:
        conditions.append("Listed building adjacent: check curtilage listing and setting.")
    if scheme.consent_required:
        conditions.append(f"Planning consent needed: {scheme.route}.")
    if v and v.review_shift is not None and abs(v.review_shift) > h["comps_review_max_shift"]:
        conditions.append(f"Comps review moved value by {v.review_shift:+.0%}: human review of comps.")
    if best.strategy == "extension" and plan and plan.pd_rights_removed is None:
        conditions.append("Confirm PD rights are intact (read the subject's past decision notices).")
    if img:
        conditions += [f"Verify lawful status: {u}" for u in img.unmatched_changes]
    conditions += [f"Risk: {r}" for r in scheme.risks]

    mp = best.max_price or 0
    reasons = [f"Best strategy: {best.strategy}. GDV £{best.gdv:,.0f}; residual max price "
               f"£{mp:,.0f} vs asking £{asking:,.0f}.",
               f"At asking: profit £{best.profit_at_asking:,.0f} "
               f"({best.poc_at_asking:.0%} on cost); stress case (GDV -10%, works +15%) "
               f"£{best.stress_profit_at_asking:,.0f}."]
    failed = []
    if (best.stress_profit_at_asking or -1) < 0:
        failed.append(f"Fails the downside test at asking; downside break-even price "
                      f"£{best.stress_max_price or 0:,.0f}.")
    if (best.profit_at_asking or 0) < h["min_profit_gbp"]:
        failed.append(f"Profit at asking below the £{h['min_profit_gbp']:,.0f} minimum.")
    if best.months > h["max_duration_months"]:
        failed.append(f"Programme {best.months} months exceeds the {h['max_duration_months']}-month limit.")

    if mp >= asking and not failed:
        hard = [x for x in conditions if not x.startswith("Risk:")]
        code = "CONDITIONAL" if hard else "VIABLE"
    elif mp >= asking:
        code = "CONDITIONAL"
        conditions = failed + conditions
    elif mp and mp >= h["conditional_floor"] * asking:
        code = "CONDITIONAL"
        conditions = [f"Only works at or below £{mp:,.0f} (asking £{asking:,.0f})."] + failed + conditions
    else:
        code = "NOT_VIABLE"
        reasons += failed
    return Verdict(code=code, best_strategy=best.strategy, max_price=best.max_price,
                   reasons=reasons, conditions=conditions)
