"""Stage E: current + historical aerial imagery, vision comparison, reconciliation with planning."""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel

from flip.ledger import Ledger
from flip.llm import runner
from flip.models import ImageryObservation, ImageryResult, PlanningResult, Property
from flip.sources import web
from flip.stages.planning import decision_class


class ImageryLLM(BaseModel):
    observations: list[ImageryObservation]


def imagery(p: Property, plan: PlanningResult, run_dir: Path, ledger: Ledger,
            use_web: bool = True, n_historical: int = 4) -> ImageryResult:
    res = ImageryResult()
    out_dir = run_dir / "imagery"
    out_dir.mkdir(parents=True, exist_ok=True)
    if p.lat is not None and use_web:
        cur = out_dir / "current_esri.png"
        if not cur.exists():
            png = web.stitch_tiles(web.ESRI_CURRENT, p.lat, p.lon)
            if png:
                cur.write_bytes(png)
        if cur.exists():
            res.images.append({"path": str(cur), "date": "current", "source": "Esri World Imagery"})
        for rel in web.pick_spread(web.wayback_releases(), n_historical):
            f = out_dir / f"wayback_{rel['date']}.png"
            if not f.exists():
                png = web.stitch_tiles(rel["url_tpl"], p.lat, p.lon)
                if png:
                    f.write_bytes(png)
            if f.exists():
                res.images.append({"path": str(f), "date": rel["date"], "source": "Esri Wayback"})
    for h in p.historical_images:  # manual captures: Google Earth Pro, CUCAP, Historic England
        m = re.search(r"(19|20)\d{2}", Path(h).name)
        if Path(h).exists():
            res.images.append({"path": h, "date": m.group(0) if m else "unknown", "source": "manual"})

    if len(res.images) < 2:
        ledger.add("imagery", len(res.images), "unknown", "stage E",
                   note="Fewer than two dated images; no change detection.")
        return res
    res.images.sort(key=lambda i: "9999" if i["date"] == "current" else i["date"])
    ctx = "Images in date order:\n" + "\n".join(
        f"- {Path(i['path']).name}: {i['date']} ({i['source']})" for i in res.images)
    try:
        out = runner.run("imagery", ImageryLLM, ctx, files=[i["path"] for i in res.images])
    except runner.LLMUnavailable as e:
        ledger.add("llm_imagery", str(e), "unknown", "claude")
        out = None
    res.observations = out.observations if out else []

    consented = [a for a in plan.apps if a.relation in ("subject", "adjoining")
                 and decision_class(a.decision) == "approved"]
    for o in res.observations:
        kind = "dwelling" if re.search(r"dwelling|house|backland", o.change, re.I) else \
               "loft" if re.search(r"dormer|loft|roof", o.change, re.I) else "extension"
        if not any(re.search(kind if kind != "loft" else "loft|dormer", a.description or "", re.I)
                   for a in consented):
            res.unmatched_changes.append(f"{o.change} ({o.date_range}): no matching consent found")
    ledger.add("imagery_changes", len(res.observations), "inference", "vision comparison of dated aerials")
    for u in res.unmatched_changes:
        ledger.add("possible_unconsented_change", u, "inference", "imagery vs planning record",
                   note="Verify lawful status: affects PD allowances and title/indemnity.")
    return res
