"""Stage D: blob-first planning triage for the subject and its neighbours, then deep dives."""

from __future__ import annotations

import re
from pathlib import Path

from flip.ledger import Ledger
from flip.llm import runner
from flip.models import DeepDive, PlanningApp, PlanningResult, Property, TriageBatch
from flip.planning_rules import readability, triage_rule

RELATION_ORDER = {"subject": 0, "adjoining": 1, "opposite": 2, "street": 3, "nearby": 4}
SCHEME_PATTERNS = [
    ("new_dwelling", r"erection of .*(dwelling|house|bungalow)|new dwelling|land (to the )?rear|backland"),
    ("conversion", r"conver.*(flat|dwelling|hmo)|change of use|subdivi"),
    ("loft", r"loft|dormer|hip.to.gable|mansard"),
    ("side_extension", r"side extension|side return|wrap"),
    ("rear_extension", r"rear extension|larger home extension|single storey|two storey|extension"),
    ("demolition_rebuild", r"demoli"),
]


def decision_class(decision: str | None) -> str:
    d = (decision or "").lower()
    if re.search(r"refus|reject|dismiss", d):
        return "refused"
    if re.search(r"approv|grant|permit|not required|lawful|allowed", d):
        return "approved"
    if re.search(r"withdr", d):
        return "withdrawn"
    return "pending/unknown"


def scheme_type(desc: str | None) -> str:
    for name, pat in SCHEME_PATTERNS:
        if desc and re.search(pat, desc, re.I):
            return name
    return "other"


def planning(p: Property, apps: list[PlanningApp], snapshot: str | None, ledger: Ledger,
             max_deep_dives: int = 12, chunk: int = 50) -> PlanningResult:
    res = PlanningResult(apps=apps, snapshot_at=snapshot)
    if snapshot:
        ledger.add("planning_snapshot_at", snapshot, "verified", "local planning DB")
    for a in apps:
        a.readability = readability(a)

    # D2: rules first, then the LLM in chunks for the rest
    pending: list[PlanningApp] = []
    for a in apps:
        t = triage_rule(a)
        if t:
            res.triage[a.ref] = t
        else:
            pending.append(a)
    for i in range(0, len(pending), chunk):
        part = pending[i:i + chunk]
        ctx = "\n".join(f"- ref: {a.ref} | relation: {a.relation} | address: {a.address} | "
                        f"description: {a.description}" for a in part)
        try:
            out = runner.run("triage", TriageBatch, ctx)
        except runner.LLMUnavailable as e:
            ledger.add("llm_triage", str(e), "unknown", "claude")
            out = None
        got = {t.ref: t for t in (out.items if out else [])}
        for a in part:
            res.triage[a.ref] = got.get(a.ref) or triage_rule_fallback(a)

    counts = {k: sum(1 for t in res.triage.values() if t.relevance == k)
              for k in ("material", "routine", "uncertain")}
    ledger.add("planning_apps_screened", len(apps), "verified", "local planning DB",
               note=f"material {counts['material']}, routine {counts['routine']}, uncertain {counts['uncertain']}")

    # D3: deep dives on material/uncertain apps that have readable documents, subject first
    todo = sorted((a for a in apps if res.triage[a.ref].relevance != "routine"),
                  key=lambda a: (RELATION_ORDER[a.relation], a.distance_m or 0))
    done = 0
    for a in todo:
        files = [d.path for d in a.documents if d.path and Path(d.path).exists()]
        if not files or done >= max_deep_dives:
            continue
        ctx = (f"ref: {a.ref}\naddress: {a.address}\ndescription: {a.description}\n"
               f"decision (from DB): {a.decision}\ndocuments:\n"
               + "\n".join(f"- doc_id {d.doc_id}: {d.title} -> {d.path}" for d in a.documents if d.path))
        try:
            dd = runner.run("deepdive", DeepDive, ctx, files=files)
        except runner.LLMUnavailable as e:
            ledger.add("llm_deepdive", str(e), "unknown", "claude")
            break
        if dd:
            _check_citations(dd, a, ledger)
            res.deep_dives[a.ref] = dd
            done += 1

    subject_dd = [d for r, d in res.deep_dives.items()
                  if next(a for a in apps if a.ref == r).relation == "subject"]
    if any(c.removes_pd_rights for d in subject_dd for c in d.conditions):
        res.pd_rights_removed = True
        ledger.add("pd_rights_removed", True, "verified", "planning condition (cited)")
    elif subject_dd:
        res.pd_rights_removed = False
        ledger.add("pd_rights_removed", False, "inference", "subject decision notices read",
                   note="No PD-removal condition found in the documents read.")
    else:
        ledger.add("pd_rights_removed", None, "unknown", "stage D",
                   note="No subject decision notices were read.")

    res.precedent = precedent_table(apps, res)
    return res


def triage_rule_fallback(a: PlanningApp):
    from flip.models import TriageItem
    return TriageItem(ref=a.ref, relevance="uncertain", flip_link="none",
                      reason="no rule matched and LLM unavailable")


def _check_citations(dd: DeepDive, app: PlanningApp, ledger: Ledger) -> None:
    """Every cited page must exist in the cited document."""
    from pypdf import PdfReader

    pages: dict[str, int] = {}
    for d in app.documents:
        if d.path and d.path.lower().endswith(".pdf") and Path(d.path).exists():
            try:
                pages[d.doc_id] = len(PdfReader(d.path).pages)
            except Exception:  # noqa: BLE001 - unreadable PDF: can't verify
                pages[d.doc_id] = 0
    bad = [c for c in [*dd.citations, *(x.citation for x in dd.conditions)]
           if c.doc_id in pages and pages[c.doc_id] and not 1 <= c.page <= pages[c.doc_id]]
    if bad:
        ledger.add(f"citation_check:{app.ref}", len(bad), "unknown", "stage D",
                   note="Some cited pages don't exist; treat this deep dive as unreliable.")


def precedent_table(apps: list[PlanningApp], res: PlanningResult) -> dict[str, dict]:
    """Per scheme type near the subject: approvals vs refusals, typical depth, refusal reasons."""
    table: dict[str, dict] = {}
    for a in apps:
        if a.relation == "subject" or res.triage[a.ref].relevance == "routine":
            continue
        dd = res.deep_dives.get(a.ref)
        st = dd.scheme_type if dd else scheme_type(a.description)
        dc = decision_class(dd.decision if dd and dd.decision else a.decision)
        row = table.setdefault(st, {"approved": 0, "refused": 0, "other": 0, "depths_m": [],
                                    "refusal_reasons": [], "refs": []})
        row["approved" if dc == "approved" else "refused" if dc == "refused" else "other"] += 1
        row["refs"].append(f"{a.ref} ({a.relation}, {dc})")
        if dd and dd.approved_depth_m and dc == "approved":
            row["depths_m"].append(dd.approved_depth_m)
        if dd and dc == "refused":
            row["refusal_reasons"].extend(dd.refusal_reasons[:3])
    return table


def consent_likelihood(precedent: dict[str, dict], scheme: str) -> tuple[str, str]:
    row = precedent.get(scheme)
    if not row or row["approved"] + row["refused"] == 0:
        return "unknown", f"no decided {scheme.replace('_', ' ')} applications nearby"
    a, r = row["approved"], row["refused"]
    level = "good" if a >= 2 and a > 2 * r else "mixed" if a >= r else "poor"
    return level, f"{a} approved / {r} refused nearby"
