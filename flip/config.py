"""Loads config/assumptions.yaml and the optional DB column mapping."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"


def load_assumptions(path: Path | None = None) -> dict[str, Any]:
    with open(path or CONFIG_DIR / "assumptions.yaml") as f:
        return yaml.safe_load(f)


def load_db_mapping(path: Path | None = None) -> dict[str, Any] | None:
    p = path or CONFIG_DIR / "db_mapping.yaml"
    if not p.exists():
        return None
    with open(p) as f:
        return yaml.safe_load(f)


def load_dotenv(path: Path | None = None) -> None:
    """Minimal .env loader so the tool has no extra dependency."""
    p = path or ROOT / ".env"
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())
