import pytest

from flip.models import PlanningApp
from flip.planning_rules import readability, triage_rule


def app(desc, relation="street", ref="24/01234/HFUL"):
    a = PlanningApp(ref=ref, description=desc, relation=relation)
    a.readability = readability(a)
    return a


@pytest.mark.parametrize("desc,link", [
    ("Erection of 1no. dwelling on land to the rear of 12 Mill Road", "split"),
    ("Single storey rear extension", "extension"),
    ("Loft conversion with rear dormer and rooflights", "extension"),
    ("Change of use from C3 to C4 HMO", "split"),
    ("Prior approval for a larger home extension (6m)", "extension"),
    ("Variation of condition 3 of 21/00001/FUL", "value"),
    ("Single storey rear extension and replacement windows", "extension"),
])
def test_material(desc, link):
    t = triage_rule(app(desc))
    assert t.relevance == "material" and t.flip_link == link


@pytest.mark.parametrize("desc", [
    "Replacement windows to front elevation",
    "Installation of satellite dish",
    "Erection of 1.8m timber fence",
    "Crown reduction of 1 no. oak tree (T1)",
    "Discharge of condition 4 (materials)",
])
def test_routine(desc):
    assert triage_rule(app(desc)).relevance == "routine"


def test_unmatched_goes_to_llm():
    assert triage_rule(app("Alterations to front porch")) is None


def test_missing_or_unreadable_never_routine():
    assert triage_rule(app(None)).relevance == "uncertain"
    assert triage_rule(app("Repl�cement w�ndows")).relevance == "uncertain"


def test_subject_consent_escalated():
    t = triage_rule(app("Listed building consent for replacement windows", relation="subject"))
    assert t.relevance == "material"


def test_readability_levels():
    assert app("Replacement windows to front elevation").readability == "readable"
    assert app("Extension").readability == "partial"
    assert app("   ").readability == "missing"
