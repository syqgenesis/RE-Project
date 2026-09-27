"""Command line.

    python -m flip check                 # what's connected: DB, claude, keys, data files
    python -m flip discover              # map your Postgres schema -> config/db_mapping.yaml
    python -m flip run cases/cases.yaml  # analyse every case; reports in runs/<case_id>/
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

import yaml

from flip.config import ROOT, load_assumptions, load_db_mapping, load_dotenv
from flip.models import CaseInput


def cmd_check(_args) -> int:
    ok = True
    print(f"assumptions: config/assumptions.yaml (as_of {load_assumptions()['as_of']})")
    print(f"claude CLI : {shutil.which(os.environ.get('FLIP_CLAUDE_BIN', 'claude')) or 'NOT FOUND'}")
    print(f"LLM        : {'on' if os.environ.get('FLIP_LLM', 'on') != 'off' else 'off'} "
          f"(model {os.environ.get('FLIP_MODEL', 'claude-opus-5-5')})")
    url = os.environ.get("DATABASE_URL")
    if url:
        try:
            from flip.sources.user_db import connect
            conn = connect(url)
            conn.execute("select 1")
            conn.rollback()
            print("database   : connected (read-only)")
        except Exception as e:  # noqa: BLE001
            ok = False
            print(f"database   : FAILED ({e})")
    else:
        print("database   : DATABASE_URL not set")
    print(f"db mapping : {'config/db_mapping.yaml' if load_db_mapping() else 'missing: run `discover`'}")
    print(f"EPC token  : {'set' if os.environ.get('EPC_API_TOKEN') else 'not set (floor areas from listing only)'}")
    ppd = list((ROOT / 'data' / 'ppd').glob('*.csv'))
    print(f"Price Paid : {len(ppd)} file(s) in data/ppd/")
    ins = list((ROOT / 'data' / 'inspire').glob('*.gml'))
    print(f"INSPIRE    : {len(ins)} file(s) in data/inspire/")
    return 0 if ok else 1


def cmd_discover(args) -> int:
    from flip.sources.user_db import connect, discover
    conn = connect()
    res = discover(conn, sample=args.sample)
    out = ROOT / "runs" / "discovery.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(res, indent=2, default=str))
    m = res["mapping"]
    print("Planning applications table:", f"{m['applications']['schema']}.{m['applications']['table']}")
    for role, col in m["applications"]["columns"].items():
        print(f"  {role:14s} -> {col}")
    print("Documents:", m["documents"] and f"{m['documents']['schema']}.{m['documents']['table']}")
    print("Description readability (sample):", res["readability"]["descriptions"])
    print("Document files (sample):", res["readability"]["documents"])
    print(f"\nWrote config/db_mapping.yaml and {out}. Check the mapping before `run`.")
    return 0


def load_cases(path: Path) -> list[CaseInput]:
    data = yaml.safe_load(path.read_text())
    items = data.get("cases", data) if isinstance(data, dict) else data
    return [CaseInput(**c) for c in items]


def cmd_run(args) -> int:
    from flip.pipeline import run_case
    cfg = load_assumptions()
    if args.no_llm:
        os.environ["FLIP_LLM"] = "off"
    apps_fn = None
    if not args.no_db and os.environ.get("DATABASE_URL"):
        from flip.sources.user_db import PlanningDB, connect
        db = PlanningDB(connect(), radius_m=cfg["neighbours"]["radius_m"])
        apps_fn = db.applications_for
    elif not args.no_db:
        print("warning: DATABASE_URL not set; planning history will be skipped", file=sys.stderr)
    cases = load_cases(Path(args.cases))
    if args.case:
        cases = [c for c in cases if c.case_id in args.case]
    summary = []
    for case in cases:
        print(f"\n=== {case.case_id} ===", flush=True)
        try:
            r = run_case(case, cfg, apps_fn=apps_fn, use_web=not args.no_web, use_llm=not args.no_llm)
        except Exception as e:  # noqa: BLE001 - one bad case must not stop the batch
            print(f"FAILED: {type(e).__name__}: {e}")
            summary.append({"case": case.case_id, "verdict": "ERROR", "detail": str(e)})
            continue
        v = r["verdict"]
        print(f"{v['code']}  best={v.get('best_strategy')}  max_price={v.get('max_price')}")
        print(f"report: {r['report_path']}")
        summary.append({"case": case.case_id, "verdict": v["code"], "best": v.get("best_strategy"),
                        "max_price": v.get("max_price"),
                        "asking": r["property"].get("asking_price")})
    out = ROOT / "runs" / "summary.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(summary, indent=2))
    print(f"\nSummary: {out}")
    return 0


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    ap = argparse.ArgumentParser(prog="flip")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    d = sub.add_parser("discover")
    d.add_argument("--sample", type=int, default=2000)
    d.set_defaults(fn=cmd_discover)
    r = sub.add_parser("run")
    r.add_argument("cases")
    r.add_argument("--case", action="append", help="only these case_ids")
    r.add_argument("--no-llm", action="store_true", help="rules and code only")
    r.add_argument("--no-web", action="store_true", help="no network calls")
    r.add_argument("--no-db", action="store_true", help="skip the planning database")
    r.set_defaults(fn=cmd_run)
    args = ap.parse_args(argv)
    sys.exit(args.fn(args))
