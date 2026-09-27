"""Orchestrates stages A→J for one case. Early exit on exclusion; every stage writes the ledger."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from flip.config import ROOT
from flip.ledger import Ledger
from flip.models import CaseInput, Comp, Constraints, PlanningApp, PlanningResult, Valuation
from flip.stages import report
from flip.stages.comps import valuation
from flip.stages.condition import condition
from flip.stages.eligibility import eligibility
from flip.stages.identify import identify
from flip.stages.imagery import imagery
from flip.stages.planning import planning
from flip.stages.schemes import build_schemes
from flip.stages.verdict import appraise, decide

RUNS = ROOT / "runs"

AppsFn = Callable[[Any], tuple[list[PlanningApp], str | None]]


def run_case(case: CaseInput, cfg: dict[str, Any], apps_fn: AppsFn | None = None,
             use_web: bool = True, use_llm: bool = True, comps: list[Comp] | None = None,
             out_dir: Path | None = None) -> dict[str, Any]:
    ledger = Ledger()
    run_dir = (out_dir or RUNS) / case.case_id
    run_dir.mkdir(parents=True, exist_ok=True)
    ledger.add("assumptions_as_of", cfg["as_of"], "verified", "config/assumptions.yaml")

    p = identify(case, ledger, use_web=use_web)
    constraints, excluded = eligibility(p, cfg, ledger, use_web=use_web)
    result: dict[str, Any] = {"property": p.model_dump(), "constraints": constraints.model_dump(),
                              "valuation": None, "planning": None, "imagery": None,
                              "schemes": [], "appraisals": []}
    if excluded:
        v = decide(p, constraints, excluded, None, None, None, [], [], cfg, ledger)
        return _finish(result, v, ledger, run_dir, use_llm)

    scope, assessment = condition(p, cfg, run_dir, ledger, use_web=use_web)
    result["condition"] = assessment.model_dump() if assessment else None

    if apps_fn is not None:
        apps, snapshot = apps_fn(p)
    else:
        apps, snapshot = [], None
        ledger.add("planning_db", None, "unknown", "stage D",
                   note="No planning database connected; planning history not screened.")
    plan = planning(p, apps, snapshot, ledger)
    result["planning"] = plan.model_dump()

    img = imagery(p, plan, run_dir, ledger, use_web=use_web)
    result["imagery"] = img.model_dump()

    val = valuation(p, cfg, ledger, scope, use_web=use_web, comps=comps)
    result["valuation"] = val.model_dump()

    schemes = build_schemes(p, val, constraints, plan, scope, cfg, ledger)
    appraisals = [a for a in (appraise(s, p.asking_price, cfg) for s in schemes) if a]
    result["schemes"] = [s.model_dump() for s in schemes]
    result["appraisals"] = [a.model_dump() for a in appraisals]

    v = decide(p, constraints, None, val, plan, img, schemes, appraisals, cfg, ledger)
    return _finish(result, v, ledger, run_dir, use_llm)


def _finish(result, verdict, ledger: Ledger, run_dir: Path, use_llm: bool) -> dict[str, Any]:
    result["verdict"] = verdict.model_dump()
    result["ledger"] = ledger.dump()
    md = report.render(result, ledger, use_llm=use_llm)
    (run_dir / "report.md").write_text(md)
    (run_dir / "result.json").write_text(json.dumps(result, indent=2, default=str))
    result["report_path"] = str(run_dir / "report.md")
    return result


__all__ = ["run_case", "Constraints", "PlanningResult", "Valuation"]
