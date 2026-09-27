"""Stage J: the Flip Report. Tables are written by code; the optional narrative by the LLM,
which may not introduce numbers (checked against everything the report already contains)."""

from __future__ import annotations

import re
from typing import Any

from flip.ledger import Ledger
from flip.llm import runner
from flip.models import ReportNarrative

NUM_RE = re.compile(r"(£)?\s?(\d[\d,]*(?:\.\d+)?)(?:\s?(k|m|bn)\b|(%))?", re.I)


def _money(x: float | None) -> str:
    return "—" if x is None else f"£{x:,.0f}"


def numbers_in(text: str) -> set[float]:
    out = set()
    for m in NUM_RE.finditer(text):
        v = float(m.group(2).replace(",", ""))
        unit = (m.group(3) or "").lower() if m.group(1) else ""  # k/m only as money: "£1.2m"
        out.add(v * 1000 if unit == "k" else v * 1_000_000 if unit == "m" else v)
    return out


def unsupported_numbers(narrative: str, allowed_text: str) -> list[float]:
    allowed = numbers_in(allowed_text)
    bad = []
    for n in numbers_in(narrative):
        if n < 100:  # small counts, years-as-ages, percentages are checked loosely
            continue
        if not any(abs(n - a) <= max(0.005 * a, 500) for a in allowed):
            bad.append(n)
    return bad


def render(result: dict[str, Any], ledger: Ledger, use_llm: bool = True) -> str:
    p, v, verdict = result["property"], result["valuation"], result["verdict"]
    lines = [f"# Flip report: {p.get('address') or p['case_id']}", ""]
    lines += [f"**Verdict: {verdict['code']}**"
              + (f" · best strategy **{verdict['best_strategy']}**" if verdict.get("best_strategy") else "")
              + (f" · max purchase price **{_money(verdict['max_price'])}**" if verdict.get("max_price") else "")
              + f" · asking {_money(p.get('asking_price'))}", ""]
    lines += [f"- {r}" for r in verdict["reasons"]]
    if verdict["conditions"]:
        lines += ["", "**Conditions / open points**", ""] + [f"- {c}" for c in verdict["conditions"]]

    if result["appraisals"]:
        lines += ["", "## Strategies (residual appraisal)", "",
                  "| Strategy | GDV | Max price | Profit at asking | Profit on cost | Stress profit | Months |",
                  "|---|---|---|---|---|---|---|"]
        for a in result["appraisals"]:
            poc = f"{a['poc_at_asking']:.0%}" if a.get("poc_at_asking") is not None else "—"
            lines.append(f"| {a['strategy']} | {_money(a['gdv'])} | {_money(a['max_price'])} | "
                         f"{_money(a['profit_at_asking'])} | {poc} | {_money(a['stress_profit_at_asking'])} "
                         f"| {a['months']} |")
        best = next((a for a in result["appraisals"] if a["strategy"] == verdict.get("best_strategy")), None)
        if best and best["sensitivity"]:
            lines += ["", f"**Sensitivity ({best['strategy']})**", "",
                      "| GDV | Works | Max price | Profit at asking |", "|---|---|---|---|"]
            for r in best["sensitivity"]:
                lines.append(f"| {r['gdv_shift']:+.0%} | {r['works_shift']:+.0%} | {_money(r['max_price'])} "
                             f"| {_money(r.get('profit_at_asking'))} |")
        if best and best["cost_lines_at_asking"]:
            lines += ["", "**Cost stack at asking price**", ""]
            lines += [f"- {k.replace('_', ' ')}: {_money(x)}" for k, x in best["cost_lines_at_asking"].items()]

    lines += ["", "## Schemes", ""]
    for s in result["schemes"]:
        state = {True: "feasible", False: "not feasible", None: "undetermined"}[s["feasible"]]
        lines.append(f"- **{s['strategy']}** ({state}): {s['route']}. "
                     + " ".join(s["notes"] + [f"Risk: {r}" for r in s["risks"]]))

    if v:
        lines += ["", "## Valuation", "",
                  f"Comps: {len(v['comps'])}" + (" (search widened)" if v["search_widened"] else "")
                  + f" · median £/m² {v['ppsm_median'] or '—'} · as-is {_money(v['value_as_is'])}"
                  f" · refurbished {_money(v['value_refurbished'])} · street ceiling {_money(v['street_ceiling'])}"]
        if v.get("review_comment"):
            lines.append(f"\nLLM comps review: {v['review_comment']} (pre-review refurbished value "
                         f"{_money(v['pre_review_value_refurbished'])}, shift {v['review_shift']})")
        if v["comps"]:
            lines += ["", "| # | Address | Date | Price | Type | m² | £/m² | Dist m | Used |",
                      "|---|---|---|---|---|---|---|---|---|"]
            for i, c in enumerate(v["comps"]):
                ppsm = round(c["price"] / c["floor_area_m2"]) if c.get("floor_area_m2") else "—"
                used = "no: " + (c["exclusion_reason"] or "") if c["excluded"] else f"w={c['weight']}"
                lines.append(f"| {i} | {c['address']} {c['postcode']} | {c['date']} | {_money(c['price'])} | "
                             f"{c['property_type']} | {c.get('floor_area_m2') or '—'} | {ppsm} | "
                             f"{round(c['distance_m']) if c.get('distance_m') is not None else '—'} | {used} |")

    plan = result.get("planning")
    if plan:
        lines += ["", "## Planning (subject + neighbours)", "",
                  f"Snapshot: {plan.get('snapshot_at') or '—'} · PD rights removed: {plan.get('pd_rights_removed')}"]
        mat = [a for a in plan["apps"] if plan["triage"][a["ref"]]["relevance"] != "routine"]
        if mat:
            lines += ["", "| Ref | Relation | Description | Decision | Triage |", "|---|---|---|---|---|"]
            for a in sorted(mat, key=lambda a: a["relation"]):
                t = plan["triage"][a["ref"]]
                lines.append(f"| {a['ref']} | {a['relation']} | {(a['description'] or '—')[:90]} | "
                             f"{a['decision'] or '—'} | {t['relevance']} ({t['flip_link']}) |")
        routine = len(plan["apps"]) - len(mat)
        lines.append(f"\n{routine} routine applications screened out by their one-line description.")
        if plan["precedent"]:
            lines += ["", "**Neighbour precedent**", ""]
            for st, row in plan["precedent"].items():
                lines.append(f"- {st.replace('_', ' ')}: {row['approved']} approved, {row['refused']} refused"
                             + (f"; refusal reasons: {'; '.join(row['refusal_reasons'][:3])}" if row["refusal_reasons"] else ""))

    img = result.get("imagery")
    if img and img["images"]:
        lines += ["", "## Imagery", ""] + [f"- {i['date']} · {i['source']} · `{i['path']}`" for i in img["images"]]
        lines += [f"- change: {o['change']} ({o['date_range']}, {o['confidence']})" for o in img["observations"]]

    c = result.get("constraints") or {}
    lines += ["", "## Constraints", ""] + [f"- {k.replace('_', ' ')}: {c[k]}" for k in c]

    body = "\n".join(lines)
    if use_llm and runner.enabled():
        try:
            n = runner.run("report", ReportNarrative, body + "\n\n## Ledger\n" + ledger_table(ledger))
        except runner.LLMUnavailable:
            n = None
        if n:
            bad = unsupported_numbers(" ".join([n.summary, *n.key_risks, *n.pre_exchange_checks]),
                                      body + ledger_table(ledger))
            head = ["## Summary", "", n.summary, "", "**Key risks**", ""] + [f"- {r}" for r in n.key_risks]
            head += ["", "**Before exchange**", ""] + [f"- {x}" for x in n.pre_exchange_checks]
            if bad:
                head += ["", f"> ⚠ Narrative contained numbers not found in the analysis: {bad}. "
                             "Treat the summary as unreliable; the tables below are authoritative."]
            body = body.replace("\n\n", "\n\n" + "\n".join(head) + "\n\n", 1)
    return body + "\n\n## Evidence ledger\n\n" + ledger_table(ledger) + "\n"


def ledger_table(ledger: Ledger) -> str:
    rows = ["| Fact | Value | Status | Source | Note |", "|---|---|---|---|---|"]
    for e in ledger.items:
        val = str(e.value)[:60].replace("|", "/")
        rows.append(f"| {e.key} | {val} | {e.status} | {e.source} | {(e.note or '').replace('|', '/')[:120]} |")
    return "\n".join(rows)
