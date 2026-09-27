"""Stage G: build the three strategies. PD rules and arithmetic in code; each scheme stands alone."""

from __future__ import annotations

from typing import Any

from flip.ledger import Ledger
from flip.models import Constraints, PlanningResult, Property, Scheme, Valuation
from flip.stages.planning import consent_likelihood

PD_KIND = {"terrace": "terrace", "end-terrace": "terrace", "semi": "semi",
           "detached": "detached", "bungalow": "detached"}


def refurb(p: Property, v: Valuation, scope: str, cfg: dict[str, Any]) -> Scheme:
    s = Scheme(strategy="refurb", feasible=None, route="no consent needed (internal works)")
    s.months = cfg["programme_months"]["refurb"][scope]
    if not p.floor_area_m2 or not v.value_refurbished:
        s.notes.append("Floor area or refurbished value unknown; can't appraise.")
        return s
    s.works_cost = round(p.floor_area_m2 * cfg["works"]["refurb_per_m2"][scope], -2)
    s.gdv = v.value_refurbished
    s.feasible = True
    s.notes.append(f"{scope} refurbishment of {p.floor_area_m2:.0f} m2.")
    return s


def extension(p: Property, v: Valuation, c: Constraints, plan: PlanningResult, scope: str,
              cfg: dict[str, Any]) -> Scheme:
    s = Scheme(strategy="extension", feasible=None, route="")
    kind = PD_KIND.get(p.property_type or "")
    if not kind:
        s.feasible = False if p.property_type == "flat" else None
        s.notes.append("House type unknown; PD limits can't be applied.")
        return s
    pd_blocked = plan.pd_rights_removed is True or c.article_4 is True
    defaults = cfg["extension"]["added_m2_default"]
    rear_m2, loft_m2 = defaults["rear_single_storey"][kind], defaults["loft"][kind]
    routes, fee = [], 0.0
    fees = cfg["costs"]["planning_fee_gbp"]

    if pd_blocked:
        routes.append("rear: householder planning (PD removed or Article 4)")
        fee += fees["householder"]
        s.consent_required = True
    else:
        routes.append("rear: PD, prior approval for larger home extension (6 m attached / 8 m detached)")
        fee += fees["prior_approval"]
    if pd_blocked or c.conservation_area:
        routes.append("loft: householder planning (Class B not available"
                      + (" in a conservation area)" if c.conservation_area else ")"))
        fee += fees["householder"]
        s.consent_required = True
    else:
        routes.append(f"loft: PD Class B (max {40 if kind == 'terrace' else 50} m3 added volume)")
    if plan.pd_rights_removed is None:
        s.risks.append("PD rights not confirmed: subject's decision notices not read.")
    if c.article_4 is None:
        s.risks.append("Article 4 status unknown.")
    if s.consent_required:
        for scheme in ("rear_extension", "loft"):
            level, why = consent_likelihood(plan.precedent, scheme)
            s.notes.append(f"Consent likelihood ({scheme.replace('_', ' ')}): {level}, {why}.")
            if level == "poor":
                s.risks.append(f"Nearby refusals for {scheme.replace('_', ' ')}.")

    s.route = "; ".join(routes)
    s.added_area_m2 = rear_m2 + loft_m2
    s.planning_fee = fee
    s.months = (cfg["programme_months"]["refurb"][scope]
                + cfg["programme_months"]["extension_full_planning_extra" if s.consent_required
                                          else "extension_pd_extra"])
    if not (p.floor_area_m2 and v.value_refurbished and v.ppsm_refurbished):
        s.notes.append("Needs floor area and £/m2 comps to value added space.")
        return s
    added_value = s.added_area_m2 * v.ppsm_refurbished * cfg["valuation"]["extension_marginal_ratio"]
    gdv = v.value_refurbished + added_value
    if v.street_ceiling:
        cap = v.street_ceiling * cfg["valuation"]["street_ceiling_multiple"]
        if gdv > cap:
            s.risks.append(f"GDV capped at street ceiling £{cap:,.0f}.")
            gdv = cap
    s.gdv = round(gdv, -3)
    s.works_cost = round(p.floor_area_m2 * cfg["works"]["refurb_per_m2"][scope]
                         + rear_m2 * cfg["works"]["extension_per_m2"]
                         + loft_m2 * cfg["works"]["loft_per_m2"], -2)
    s.feasible = True
    s.notes.append(f"Added area {s.added_area_m2} m2 is a default by house type (estimate), "
                   "not measured from the plot.")
    return s


def split(p: Property, v: Valuation, c: Constraints, plan: PlanningResult,
          cfg: dict[str, Any]) -> Scheme:
    sp = cfg["split"]
    s = Scheme(strategy="split", feasible=None, route="full planning for a new dwelling",
               consent_required=True, planning_fee=cfg["costs"]["planning_fee_gbp"]["full_dwelling"],
               months=cfg["programme_months"]["split"])
    if c.green_belt:
        s.feasible = False
        s.notes.append("Green Belt: new dwelling not credible.")
        return s
    if c.plot_area_m2 is None or c.plot_frontage_m is None:
        s.notes.append("Plot geometry unknown (no INSPIRE polygon); can't test a plot split.")
        return s
    if c.plot_area_m2 < sp["min_plot_area_m2"] or c.plot_frontage_m < sp["min_frontage_m"]:
        s.feasible = False
        s.notes.append(f"Plot {c.plot_area_m2:.0f} m2 / frontage {c.plot_frontage_m:.0f} m below "
                       f"thresholds ({sp['min_plot_area_m2']} m2 / {sp['min_frontage_m']} m).")
        return s
    level, why = consent_likelihood(plan.precedent, "new_dwelling")
    s.notes.append(f"Consent likelihood (new dwelling): {level}, {why}.")
    if level == "poor":
        s.risks.append("Nearby refusals for new dwellings.")
    if c.tpo:
        s.risks.append("Tree Preservation Order nearby.")
    if c.flood_zone and c.flood_zone >= 3:
        s.risks.append("Flood Zone 3: sequential test for a new dwelling.")
    if not (v.ppsm_refurbished and v.value_as_is):
        s.notes.append("Needs £/m2 comps to value the plot.")
        return s
    new_gdv = sp["new_dwelling_m2"] * v.ppsm_refurbished
    build = sp["new_dwelling_m2"] * cfg["works"]["new_build_per_m2"]
    plot_value = new_gdv * (1 - sp["developer_margin_on_plot"]) - build
    if plot_value <= 0:
        s.feasible = False
        s.notes.append("Residual plot value is not positive.")
        return s
    s.gdv = round(v.value_as_is * (1 - sp["garden_loss_discount"]) + plot_value, -3)
    s.works_cost = 0.0
    s.feasible = True
    s.notes.append(f"Sell the house (less {sp['garden_loss_discount']:.0%} for garden loss) plus a "
                   f"consented plot worth about £{plot_value:,.0f} (residual).")
    return s


def build_schemes(p, v, c, plan, scope, cfg, ledger: Ledger) -> list[Scheme]:
    out = [refurb(p, v, scope, cfg), extension(p, v, c, plan, scope, cfg), split(p, v, c, plan, cfg)]
    for s in out:
        ledger.add(f"scheme:{s.strategy}", "feasible" if s.feasible else
                   "not feasible" if s.feasible is False else "undetermined",
                   "inference", "stage G", note="; ".join(s.notes + s.risks)[:400] or None)
    return out
