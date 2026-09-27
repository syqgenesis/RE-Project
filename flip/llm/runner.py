"""Runs one LLM node through Claude Code in headless mode, on the user's Claude subscription.

    claude -p <prompt> --model claude-opus-5-5 --output-format json --json-schema <schema>

Output is validated against a Pydantic model; one retry with the validation error. Results are
cached by input hash so an interrupted run resumes without repeating calls. Set FLIP_LLM=off to
skip every LLM node (stages then fall back to rules / "unknown").
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from flip.config import ROOT

T = TypeVar("T", bound=BaseModel)

MODEL = os.environ.get("FLIP_MODEL", "claude-opus-5-5")
PROMPTS = Path(__file__).parent / "prompts"
CACHE = ROOT / ".cache" / "llm"


class LLMUnavailable(RuntimeError):
    pass


def enabled() -> bool:
    return os.environ.get("FLIP_LLM", "on").lower() not in ("off", "0", "false")


def load_prompt(name: str) -> str:
    return (PROMPTS / f"{name}.md").read_text()


def _extract_json(text: str) -> object:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    start = min((i for i in (text.find("{"), text.find("[")) if i >= 0), default=-1)
    if start > 0:
        text = text[start:]
    return json.loads(text)


def _call_claude(prompt: str, schema: dict, files: list[str]) -> object:
    claude_bin = os.environ.get("FLIP_CLAUDE_BIN", "claude")
    cmd = [claude_bin, "-p", prompt, "--model", MODEL, "--output-format", "json",
           "--json-schema", json.dumps(schema), "--allowedTools", "Read"]
    for d in sorted({str(Path(f).resolve().parent) for f in files if Path(f).exists()}):
        cmd += ["--add-dir", d]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=int(os.environ.get("FLIP_LLM_TIMEOUT", "900")))
    except FileNotFoundError as e:
        raise LLMUnavailable("`claude` CLI not found. Install Claude Code and log in.") from e
    if proc.returncode != 0:
        raise LLMUnavailable(f"claude exited {proc.returncode}: {proc.stderr.strip()[:500]}")
    envelope = json.loads(proc.stdout)
    if isinstance(envelope, dict):
        if envelope.get("is_error"):
            raise LLMUnavailable(f"claude error: {str(envelope.get('result'))[:500]}")
        if envelope.get("structured_output") is not None:
            return envelope["structured_output"]
        if "result" in envelope:
            return _extract_json(str(envelope["result"]))
    return envelope


def run(node: str, model_cls: type[T], context: str, files: list[str] | None = None) -> T | None:
    """Run prompt `node` with `context`; return a validated `model_cls` or None if LLM is off."""
    if not enabled():
        return None
    files = files or []
    base = load_prompt(node)
    file_block = "\n".join(f"- {Path(f).resolve()}" for f in files)
    prompt = (f"{base}\n\n## Input\n\n{context}\n"
              + (f"\n## Files to read (use the Read tool)\n{file_block}\n" if files else "")
              + "\nReturn only JSON matching the schema.")
    schema = model_cls.model_json_schema()
    key = hashlib.sha256(json.dumps([MODEL, prompt, schema, [_mtime(f) for f in files]],
                                    sort_keys=True).encode()).hexdigest()[:24]
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / f"{node}-{key}.json"
    if cached.exists():
        return model_cls.model_validate_json(cached.read_text())

    raw = _call_claude(prompt, schema, files)
    try:
        result = model_cls.model_validate(raw)
    except ValidationError as err:
        retry = f"{prompt}\n\nYour previous output failed validation:\n{err}\nFix it."
        result = model_cls.model_validate(_call_claude(retry, schema, files))
    cached.write_text(result.model_dump_json())
    return result


def _mtime(path: str) -> float | None:
    p = Path(path)
    return p.stat().st_mtime if p.exists() else None
