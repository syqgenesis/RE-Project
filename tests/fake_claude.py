#!/usr/bin/env python3
"""Stands in for `claude -p ... --output-format json --json-schema ...` in tests."""

import json
import re
import sys

args = sys.argv[1:]
prompt = args[args.index("-p") + 1]
schema = json.loads(args[args.index("--json-schema") + 1])
props = schema.get("properties", {})

if "items" in props:  # triage
    refs = re.findall(r"- ref: (\S+)", prompt)
    out = {"items": [{"ref": r, "relevance": "routine", "flip_link": "none",
                      "reason": "fake: minor works"} for r in refs]}
elif "adjustments" in props:  # comps review: exclude the first flat it sees
    idx = next((int(m.group(1)) for m in re.finditer(r"\[(\d+)\][^\n]*\| flat \|", prompt)), None)
    adj = [{"action": "exclude", "comp_index": idx, "reason": "fake: flat"}] if idx is not None else []
    out = {"adjustments": adj, "comment": "fake review"}
elif "summary" in props:  # report narrative
    out = {"summary": "Fake summary citing £999,999 which is not in the analysis.",
           "key_risks": ["risk"], "pre_exchange_checks": ["title"]}
elif "grades" in props:
    out = {"grades": [{"area": "kitchen", "grade": 4, "evidence": "old", "photo_index": 0}],
           "structural_concern": False, "notes": "fake"}
else:
    out = {}
print(json.dumps({"type": "result", "is_error": False, "result": "", "structured_output": out}))
