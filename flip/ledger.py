"""Evidence ledger: every fact the verdict relies on, with its status and source."""

from __future__ import annotations

import datetime as dt
from typing import Any

from pydantic import BaseModel

from flip.models import EvidenceStatus


class Evidence(BaseModel):
    key: str
    value: Any
    status: EvidenceStatus
    source: str
    as_of: str
    note: str | None = None


class Ledger:
    def __init__(self) -> None:
        self.items: list[Evidence] = []

    def add(self, key: str, value: Any, status: EvidenceStatus, source: str,
            note: str | None = None, as_of: str | None = None) -> Any:
        self.items.append(Evidence(key=key, value=value, status=status, source=source,
                                   as_of=as_of or dt.date.today().isoformat(), note=note))
        return value

    def get(self, key: str) -> Evidence | None:
        for item in reversed(self.items):
            if item.key == key:
                return item
        return None

    def status(self, key: str) -> EvidenceStatus:
        item = self.get(key)
        return item.status if item else "unknown"

    def numbers(self) -> set[float]:
        out: set[float] = set()
        for item in self.items:
            if isinstance(item.value, (int, float)) and not isinstance(item.value, bool):
                out.add(float(item.value))
        return out

    def dump(self) -> list[dict]:
        return [i.model_dump() for i in self.items]
