"""Stage C: existing condition from listing photos (vision LLM) -> refurb scope."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from flip.ledger import Ledger
from flip.llm import runner
from flip.models import ConditionAssessment, Property
from flip.sources import web


def local_images(urls_or_paths: list[str], dest: Path, prefix: str, limit: int = 20) -> list[str]:
    out = []
    for i, u in enumerate(urls_or_paths[:limit]):
        if Path(u).exists():
            out.append(u)
        elif u.startswith("http"):
            ext = Path(u.split("?")[0]).suffix or ".jpg"
            got = web.download(u, dest / f"{prefix}_{i:02d}{ext}")
            if got:
                out.append(got)
    return out


def scope_from(assessment: ConditionAssessment | None) -> str | None:
    if assessment is None or not assessment.grades:
        return None
    avg = sum(g.grade for g in assessment.grades) / len(assessment.grades)
    if assessment.structural_concern:
        return "structural"
    if avg >= 3.2:
        return "heavy"
    if avg >= 2.4:
        return "medium"
    return "light"


def condition(p: Property, cfg: dict[str, Any], run_dir: Path, ledger: Ledger,
              use_web: bool = True) -> tuple[str, ConditionAssessment | None]:
    photos = local_images(p.photos, run_dir / "photos", "photo") if use_web or p.photos else []
    plans = local_images(p.floorplans, run_dir / "photos", "floorplan", limit=3) if use_web else []
    assessment = None
    if photos:
        ctx = (f"Property: {p.property_type or 'house'}, {p.bedrooms or '?'} bed, "
               f"{p.floor_area_m2 or '?'} m2.\nListing text:\n{(p.description or '')[:3000]}\n"
               f"Photos are files 0..{len(photos) - 1}; floorplans follow.")
        try:
            assessment = runner.run("condition", ConditionAssessment, ctx, files=photos + plans)
        except runner.LLMUnavailable as e:
            ledger.add("llm_condition", str(e), "unknown", "claude")
    scope = scope_from(assessment)
    if scope:
        ledger.add("refurb_scope", scope, "inference", "vision grading of listing photos",
                   note=assessment.notes if assessment else None)
    else:
        scope = cfg["works"]["default_scope_when_unknown"]
        ledger.add("refurb_scope", scope, "unknown", "config default",
                   note="No photo grading available; default scope assumed.")
    return scope, assessment
