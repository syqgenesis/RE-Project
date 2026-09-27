"""Stage D1/D2 rules layer: readability check and the regex taxonomy for planning descriptions.

A regex taxonomy is a fixed list of keyword patterns, each mapped to a category. It labels the
obvious descriptions instantly and identically every time; only unmatched ones go to the LLM.
"""

from __future__ import annotations

import re

from flip.models import PlanningApp, Readability, TriageItem

REF_RE = re.compile(r"^\s*[A-Z]?\d{2}/\d{4,5}/[A-Z0-9]+\s*$", re.I)

# (pattern, flip_link). Checked before ROUTINE so "extension ... and replacement windows" is material.
MATERIAL = [
    (r"\berection of\b.*\b(dwelling|house|bungalow|flats?|units?)\b", "split"),
    (r"\b(new|detached|additional)\s+(dwelling|house|bungalow)s?\b", "split"),
    (r"\bland (to the )?(rear|adj|adjacent|side|r/o)\b|\bland at\b", "split"),
    (r"\b(subdivision|sub-division|conversion|convert(ed|ing)?)\b.*\b(flats?|dwellings?|units?|hmo)\b", "split"),
    (r"\bchange of use\b", "split"),
    (r"\bdemolition\b|\bdemolish", "split"),
    (r"\bbackland\b|\bplot\b", "split"),
    (r"\bextension\b|\bextend(ing)?\b", "extension"),
    (r"\bloft\b|\bdormer|\broof ?lights?\b.*\bconversion\b|\bhip[- ]to[- ]gable\b|\bmansard\b", "extension"),
    (r"\bstorey\b|\bstory\b|\boutrigger\b|\bwrap[- ]around\b|\bside return\b", "extension"),
    (r"\bbasement\b|\bannex(e)?\b|\boutbuilding\b|\bgarage conversion\b", "extension"),
    (r"\bprior approval\b|\blarger home extension\b|\bclass (a|aa|b|ma)\b", "extension"),
    (r"\bcertificate of lawful|\blawful development|\bclopud\b|\bcleud\b|\bldc\b", "extension"),
    (r"\bvariation of condition|\bremoval of condition|\bs73\b|\bsection 73\b", "value"),
    (r"\benforcement\b|\bbreach\b|\bunauthori[sz]ed\b", "value"),
    (r"\blisted building consent\b|\blbc\b", "value"),
]

ROUTINE = [
    r"\breplacement (of )?(existing )?(windows?|doors?|glazing)\b",
    r"^\s*(replace(ment)?|new|install(ation of)?)\s+(upvc |timber |aluminium )?(windows?|doors?)\b",
    r"\bsatellite dish\b|\bantenna\b|\baerial\b",
    r"\bfenc(e|ing)\b|\bgates?\b|\bboundary wall\b",
    r"\badverti[sz]ement\b|\bsignage\b|\bsigns?\b",
    r"\bboiler\b|\bflue\b|\bair source heat pump\b|\bsolar (pv|panels?)\b|\bev charg",
    r"\btree works\b|\b(fell|crown|prune|pollard)(ing)?\b.*\btrees?\b|\btpo\b.*\bworks\b",
    r"\bdischarge of condition|\bapproval of details\b",
]

_mat = [(re.compile(p, re.I), link) for p, link in MATERIAL]
_rout = [re.compile(p, re.I) for p in ROUTINE]


def readability(app: PlanningApp) -> Readability:
    d = app.description
    if d is None or not d.strip():
        return "missing"
    if "�" in d or re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", d):
        return "unreadable"
    if len(d.strip()) < 12 or d.rstrip().endswith(("...", "…")) or re.search(r"<[a-z/][^>]*>", d, re.I):
        return "partial"
    return "readable"


def triage_rule(app: PlanningApp) -> TriageItem | None:
    """Label by rules; None means 'send to the LLM'."""
    if app.readability in ("missing", "unreadable"):
        return TriageItem(ref=app.ref, relevance="uncertain", flip_link="none",
                          reason=f"description {app.readability}; never assumed routine")
    d = app.description or ""
    for rx, link in _mat:
        if rx.search(d):
            return TriageItem(ref=app.ref, relevance="material", flip_link=link,
                              reason=f"rule: /{rx.pattern}/")
    if app.relation == "subject" and re.search(r"listed|conservation|consent", d, re.I):
        return TriageItem(ref=app.ref, relevance="material", flip_link="value",
                          reason="rule: consent type on the subject may imply restrictions")
    for rx in _rout:
        if rx.search(d):
            return TriageItem(ref=app.ref, relevance="routine", flip_link="none",
                              reason=f"rule: /{rx.pattern}/")
    return None
