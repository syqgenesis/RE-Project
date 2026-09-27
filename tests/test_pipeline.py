"""End-to-end golden cases with simulated web sources (no network) and a fake `claude`."""

import os
import stat
import sys
from pathlib import Path

import pytest

from flip.config import load_assumptions
from flip.llm import runner
from flip.models import CaseInput, Comp, PlanningApp
from flip.pipeline import run_case
from flip.sources import web

CFG = load_assumptions()
HERE = Path(__file__).parent


@pytest.fixture(autouse=True)
def offline(monkeypatch, tmp_path):
    monkeypatch.setattr(web, "fetch_listing", lambda url: None)
    monkeypatch.setattr(web, "geocode_postcode", lambda pc: {
        "lat": 52.2, "lon": 0.14, "outward_code": pc.split()[0], "postcode": pc})
    monkeypatch.setattr(web, "epc_by_postcode", lambda pc: None)
    monkeypatch.setattr(web, "bulk_geocode", lambda pcs: {})
    monkeypatch.setattr(web, "stitch_tiles", lambda *a, **k: None)
    monkeypatch.setattr(web, "wayback_releases", lambda: [])
    monkeypatch.setattr(web, "planning_entities", lambda wkt, ds=None: [])
    monkeypatch.setenv("FLIP_LLM", "off")
    monkeypatch.setattr(runner, "CACHE", tmp_path / "llmcache")


def comps(ppsm=6000, n=5, area=100):
    return [Comp(address=f"{i} Mill Road", postcode="CB1 2AB", date="2026-05-01",
                 price=ppsm * area * (0.95 + 0.025 * i), property_type="semi",
                 floor_area_m2=area, distance_m=100 + 20 * i) for i in range(n)]


def base_case(**kw):
    d = dict(case_id="t", address="12 Mill Road, Cambridge", postcode="CB1 2AB",
             asking_price=450_000, tenure="Freehold", property_type="Semi-Detached",
             floor_area_m2=95)
    d.update(kw)
    return CaseInput(**d)


def run(case, tmp_path, apps=None, cmp=None):
    return run_case(case, CFG, apps_fn=(lambda p: (apps or [], "2026-09-27T10:00")),
                    use_web=True, use_llm=True, comps=cmp if cmp is not None else comps(),
                    out_dir=tmp_path)


def test_leasehold_excluded(tmp_path):
    r = run(base_case(tenure="Leasehold"), tmp_path)
    assert r["verdict"]["code"] == "EXCLUDED"


def test_share_of_freehold_excluded(tmp_path):
    r = run(base_case(tenure="Share of Freehold"), tmp_path)
    assert r["verdict"]["code"] == "EXCLUDED"


def test_outside_cb1_excluded(tmp_path):
    r = run(base_case(postcode="CB10 1AA"), tmp_path)
    assert r["verdict"]["code"] == "EXCLUDED" and "CB10" in r["verdict"]["reasons"][0]


def test_listed_excluded(tmp_path, monkeypatch):
    monkeypatch.setattr(web, "planning_entities", lambda wkt, ds=None: [
        {"dataset": "listed-building", "name": "12 Mill Road (Grade II)"}])
    r = run(base_case(), tmp_path)
    assert r["verdict"]["code"] == "EXCLUDED" and "listed" in r["verdict"]["reasons"][0].lower()


def test_no_comps_is_insufficient(tmp_path):
    r = run(base_case(), tmp_path, cmp=[])
    assert r["verdict"]["code"] == "INSUFFICIENT_EVIDENCE"


def test_cheap_house_viable_once_title_checked(tmp_path):
    apps = [PlanningApp(ref="22/00001/HFUL", address="12 Mill Road", description="Replacement windows",
                        decision="Approved", relation="subject"),
            PlanningApp(ref="23/00002/HFUL", address="14 Mill Road",
                        description="Single storey rear extension", decision="Approved", relation="adjoining")]
    r = run(base_case(title_checked=True, asking_price=260_000), tmp_path, apps=apps)
    assert r["verdict"]["code"] == "VIABLE", r["verdict"]
    tri = r["planning"]["triage"]
    assert tri["22/00001/HFUL"]["relevance"] == "routine"
    assert tri["23/00002/HFUL"]["relevance"] == "material"
    assert r["verdict"]["max_price"] >= 260_000
    assert Path(r["report_path"]).read_text().startswith("# Flip report")


def test_same_house_conditional_without_title(tmp_path):
    r = run(base_case(asking_price=260_000), tmp_path)
    assert r["verdict"]["code"] == "CONDITIONAL"
    assert any("title register" in c for c in r["verdict"]["conditions"])


def test_overpriced_not_viable(tmp_path):
    r = run(base_case(asking_price=900_000), tmp_path)
    assert r["verdict"]["code"] == "NOT_VIABLE"


def test_llm_paths_with_fake_claude(tmp_path, monkeypatch):
    fake = tmp_path / "claude"
    fake.write_text(f"#!/bin/sh\nexec {sys.executable} {HERE / 'fake_claude.py'} \"$@\"\n")
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("FLIP_CLAUDE_BIN", str(fake))
    monkeypatch.setenv("FLIP_LLM", "on")
    cmp = comps()
    cmp.append(Comp(address="Flat 3 Mill Road", postcode="CB1 2AB", date="2026-05-01", price=250_000,
                    property_type="flat", floor_area_m2=50, distance_m=50))
    apps = [PlanningApp(ref="24/00003/HFUL", address="20 Mill Road",
                        description="Alterations to front porch", relation="street")]
    r = run(base_case(asking_price=380_000), tmp_path, apps=apps, cmp=cmp)
    # triage fell through the rules to the (fake) LLM
    assert r["planning"]["triage"]["24/00003/HFUL"]["reason"] == "fake: minor works"
    # the reviewer excluded the flat and code recomputed
    flat = [c for c in r["valuation"]["comps"] if c["property_type"] == "flat"][0]
    assert flat["excluded"] and r["valuation"]["review_comment"] == "fake review"
    # narrative with an invented number is flagged
    assert "not found in the analysis" in Path(r["report_path"]).read_text()


def test_base_ok_but_fails_downside_is_conditional(tmp_path):
    # with a low 5% profit target the base case clears at 370k, but GDV -10% / works +15% loses money
    import copy
    cfg = copy.deepcopy(CFG)
    cfg["hurdles"]["target_profit_on_cost"] = 0.05
    cfg["hurdles"]["min_profit_gbp"] = 0
    r = run_case(base_case(title_checked=True, asking_price=370_000), cfg,
                 apps_fn=lambda p: ([], None), comps=comps(), out_dir=tmp_path)
    assert r["verdict"]["code"] == "CONDITIONAL"
    assert any("downside" in c for c in r["verdict"]["conditions"])


def test_slightly_overpriced_conditional_with_price(tmp_path):
    r = run(base_case(title_checked=True, asking_price=360_000), tmp_path)
    assert r["verdict"]["code"] == "CONDITIONAL"
    assert r["verdict"]["conditions"][0].startswith("Only works at or below")
