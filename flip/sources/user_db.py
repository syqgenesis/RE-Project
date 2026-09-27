"""Read-only adapter for the user's local PostgreSQL planning database.

`discover()` introspects the live schema, guesses which table/columns hold planning applications,
their one-line descriptions and their documents, and writes config/db_mapping.yaml for review.
`PlanningDB` then queries applications for the subject and its neighbours inside one
REPEATABLE READ, READ ONLY transaction (a consistent snapshot while collection keeps appending).
"""

from __future__ import annotations

import datetime as dt
import math
import os
import re
from pathlib import Path
from typing import Any

import psycopg
import yaml
from psycopg import sql
from psycopg.rows import dict_row

from flip.config import CONFIG_DIR, load_db_mapping
from flip.models import PlanningApp, PlanningDoc, Property

# role -> name patterns, best first
APP_ROLES: dict[str, list[str]] = {
    "ref": [r"^(application_)?ref(erence)?(_no|_number)?$", r"^case_?ref", r"^app(lication)?_?(no|number|id)$", r"ref"],
    "description": [r"^(proposal|description|development_description|proposal_description)$",
                    r"proposal", r"description", r"summary", r"blob"],
    "address": [r"^(site_)?address$", r"address", r"location", r"site"],
    "postcode": [r"^postcode$", r"post_?code"],
    "decision": [r"^decision$", r"decision(?!_date)", r"status", r"outcome"],
    "decision_date": [r"decision_?date", r"decided", r"determin"],
    "received_date": [r"(received|validated|registered|valid)(_date)?", r"date_received"],
    "app_type": [r"^(application_)?type$", r"app_type", r"type"],
    "uprn": [r"^uprn$", r"uprn"],
    "lat": [r"^lat(itude)?$"],
    "lon": [r"^(lon|lng|long|longitude)$"],
    "id": [r"^id$", r"^application_id$", r"^app_id$"],
}
DOC_ROLES: dict[str, list[str]] = {
    "app_key": [r"^application_id$", r"^app_id$", r"^(application_)?ref(erence)?$", r"application", r"ref"],
    "path": [r"(local_)?(file_)?path", r"filename", r"file"],
    "url": [r"url", r"link", r"href"],
    "title": [r"title", r"name", r"doc(ument)?_?type", r"description"],
    "id": [r"^id$", r"doc(ument)?_id"],
    "blob": [r"content", r"data", r"bytes", r"blob"],
}


def connect(url: str | None = None) -> psycopg.Connection:
    url = url or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set (see .env.example).")
    conn = psycopg.connect(url, row_factory=dict_row, autocommit=False)
    conn.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
    conn.read_only = True
    return conn


def _columns(conn) -> dict[tuple[str, str], list[tuple[str, str]]]:
    rows = conn.execute("""
        select table_schema, table_name, column_name, data_type
        from information_schema.columns
        where table_schema not in ('pg_catalog', 'information_schema')
        order by table_schema, table_name, ordinal_position""").fetchall()
    out: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for r in rows:
        out.setdefault((r["table_schema"], r["table_name"]), []).append((r["column_name"], r["data_type"]))
    return out


def _match(cols: list[tuple[str, str]], roles: dict[str, list[str]]) -> dict[str, str]:
    found: dict[str, str] = {}
    used: set[str] = set()
    for role, patterns in roles.items():
        for pat in patterns:
            hit = next((c for c, _ in cols if c not in used and re.search(pat, c, re.I)), None)
            if hit:
                found[role] = hit
                used.add(hit)
                break
    return found


def discover(conn, out_path: Path | None = None, sample: int = 2000) -> dict[str, Any]:
    """Guess the mapping from the live schema and write it (plus a readability report)."""
    tables = _columns(conn)
    counts = {f"{s}.{t}": r["n"] for r in conn.execute("""
        select n.nspname as s, c.relname as t, greatest(c.reltuples, 0)::bigint as n
        from pg_class c join pg_namespace n on n.oid = c.relnamespace
        where c.relkind in ('r','p','m','v') and n.nspname not in ('pg_catalog','information_schema')
    """).fetchall() for s, t in [(r["s"], r["t"])]}

    def app_score(m: dict[str, str]) -> int:
        return (3 * ("description" in m) + 2 * ("ref" in m) + 2 * ("address" in m)
                + ("decision" in m) + ("postcode" in m) + ("decision_date" in m))

    cands = sorted(((app_score(m), key, m) for key, cols in tables.items()
                    for m in [_match(cols, APP_ROLES)]), key=lambda x: -x[0])
    if not cands or cands[0][0] < 5:
        raise RuntimeError("No table looks like planning applications; set config/db_mapping.yaml by hand.")
    _, (a_schema, a_table), a_map = cands[0]

    doc = None
    for (s, t), cols in tables.items():
        if (s, t) == (a_schema, a_table):
            continue
        m = _match(cols, DOC_ROLES)
        if "app_key" in m and ({"path", "url", "blob"} & m.keys()):
            doc = {"schema": s, "table": t, "columns": m,
                   "joins_on": "id" if re.search(r"_id$", m["app_key"]) and "id" in a_map else "ref"}
            break

    mapping = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "note": "Auto-detected. Check each column, then keep this file.",
        "applications": {"schema": a_schema, "table": a_table, "columns": a_map},
        "documents": doc,
        "documents_root": os.environ.get("FLIP_DOCS_ROOT", ""),
    }
    out = out_path or CONFIG_DIR / "db_mapping.yaml"
    out.write_text(yaml.safe_dump(mapping, sort_keys=False))
    report = readability_report(conn, mapping, sample=sample)
    return {"mapping": mapping, "row_counts": counts, "tables": {f"{s}.{t}": [c for c, _ in cols]
            for (s, t), cols in tables.items()}, "readability": report}


def _qual(schema: str, table: str) -> sql.Composed:
    return sql.SQL("{}.{}").format(sql.Identifier(schema), sql.Identifier(table))


def readability_report(conn, mapping: dict[str, Any], sample: int = 2000) -> dict[str, Any]:
    from flip.planning_rules import readability

    a = mapping["applications"]
    c = a["columns"]
    q = sql.SQL("select {ref} as ref, {desc} as description from {tbl} limit %s").format(
        ref=sql.Identifier(c["ref"]) if "ref" in c else sql.SQL("null"),
        desc=sql.Identifier(c["description"]), tbl=_qual(a["schema"], a["table"]))
    counts: dict[str, int] = {"readable": 0, "partial": 0, "unreadable": 0, "missing": 0}
    examples: dict[str, list[str]] = {k: [] for k in counts}
    for r in conn.execute(q, (sample,)).fetchall():
        level = readability(PlanningApp(ref=str(r["ref"] or "?"), description=_text(r["description"])))
        counts[level] += 1
        if len(examples[level]) < 3:
            examples[level].append(f"{r['ref']}: {str(_text(r['description']))[:90]!r}")
    docs: dict[str, int] = {}
    d = mapping.get("documents")
    if d and "path" in d["columns"]:
        root = Path(mapping.get("documents_root") or ".")
        q = sql.SQL("select {p} as p from {tbl} limit %s").format(
            p=sql.Identifier(d["columns"]["path"]), tbl=_qual(d["schema"], d["table"]))
        for r in conn.execute(q, (min(sample, 500),)).fetchall():
            docs[doc_status(root, r["p"])] = docs.get(doc_status(root, r["p"]), 0) + 1
    conn.rollback()
    return {"descriptions": counts, "examples": examples, "documents": docs}


def doc_status(root: Path, path: str | None) -> str:
    if not path:
        return "missing"
    p = Path(path) if Path(path).is_absolute() else root / path
    if not p.exists():
        return "file_not_found"
    if p.stat().st_size == 0:
        return "empty"
    with open(p, "rb") as f:
        head = f.read(5)
    if p.suffix.lower() == ".pdf" and head != b"%PDF-":
        return "not_a_pdf"
    return "readable"


def _text(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, (bytes, memoryview)):
        b = bytes(v)
        for enc in ("utf-8", "latin-1"):
            try:
                return b.decode(enc)
            except UnicodeDecodeError:
                continue
        return b.decode("utf-8", "replace")
    return str(v)


_NUM = re.compile(r"^\s*(\d+)([a-z]?)\b", re.I)


def house_number(address: str | None) -> int | None:
    if not address:
        return None
    m = _NUM.search(address.split(",")[0]) or re.search(r"\b(\d+)[a-z]?\s+[A-Z]", address)
    return int(m.group(1)) if m else None


def relation_for(prop: Property, address: str | None, distance_m: float | None,
                 gap: int = 2) -> str:
    a = (address or "").lower()
    street = (prop.street or "").lower()
    n_subject = house_number(prop.address)
    n = house_number(address)
    if street and street in a:
        if n is not None and n_subject is not None:
            if n == n_subject:
                return "subject"
            if n % 2 == n_subject % 2 and abs(n - n_subject) <= gap:
                return "adjoining"
            if n % 2 != n_subject % 2 and abs(n - n_subject) <= gap + 1:
                return "opposite"
        return "street"
    if distance_m is not None and distance_m < 25:
        return "subject"
    return "nearby"


def haversine_m(lat1, lon1, lat2, lon2) -> float:
    r = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


class PlanningDB:
    """Planning applications for a subject property and its neighbours."""

    def __init__(self, conn, mapping: dict[str, Any] | None = None, radius_m: float = 150):
        self.conn = conn
        self.mapping = mapping or load_db_mapping()
        if not self.mapping:
            raise RuntimeError("config/db_mapping.yaml missing: run `python -m flip discover` first.")
        self.radius_m = radius_m

    def applications_for(self, prop: Property) -> tuple[list[PlanningApp], str]:
        a = self.mapping["applications"]
        c = a["columns"]
        tbl = _qual(a["schema"], a["table"])
        where, params = [], []
        if prop.street and "address" in c:
            where.append(sql.SQL("{} ilike %s").format(sql.Identifier(c["address"])))
            params.append(f"%{prop.street}%")
        if prop.postcode and "postcode" in c:
            where.append(sql.SQL("replace(upper({}),' ','') = %s").format(sql.Identifier(c["postcode"])))
            params.append(prop.postcode.replace(" ", "").upper())
        elif prop.postcode and "address" in c:
            where.append(sql.SQL("replace(upper({}),' ','') like %s").format(sql.Identifier(c["address"])))
            params.append(f"%{prop.postcode.replace(' ', '').upper()}%")
        if prop.lat is not None and "lat" in c and "lon" in c:
            dlat = self.radius_m / 111_000
            dlon = self.radius_m / (111_000 * math.cos(math.radians(prop.lat)))
            where.append(sql.SQL("({lat} between %s and %s and {lon} between %s and %s)").format(
                lat=sql.Identifier(c["lat"]), lon=sql.Identifier(c["lon"])))
            params += [prop.lat - dlat, prop.lat + dlat, prop.lon - dlon, prop.lon + dlon]
        if not where:
            return [], _now()
        cols = sql.SQL(", ").join(sql.SQL("{} as {}").format(sql.Identifier(v), sql.Identifier(k))
                                  for k, v in c.items())
        q = sql.SQL("select {cols} from {tbl} where {w}").format(
            cols=cols, tbl=tbl, w=sql.SQL(" or ").join(where))

        self.conn.rollback()  # start a fresh snapshot (REPEATABLE READ, READ ONLY via connect())
        try:
            snapshot = self.conn.execute("select now()::text as t").fetchone()["t"]
            rows = self.conn.execute(q, params).fetchall()
            docs = self._documents(rows)
        finally:
            self.conn.rollback()

        apps = []
        for r in rows:
            dist = None
            if prop.lat is not None and r.get("lat") is not None and r.get("lon") is not None:
                dist = haversine_m(prop.lat, prop.lon, float(r["lat"]), float(r["lon"]))
                if dist > self.radius_m and prop.street and prop.street.lower() not in str(r.get("address", "")).lower():
                    continue
            key = r.get("id") if self._joins_on() == "id" else r.get("ref")
            apps.append(PlanningApp(
                ref=str(r.get("ref") or r.get("id")),
                address=_text(r.get("address")),
                description=_text(r.get("description")),
                decision=_text(r.get("decision")),
                decision_date=_text(r.get("decision_date")),
                received_date=_text(r.get("received_date")),
                app_type=_text(r.get("app_type")),
                distance_m=dist,
                relation=relation_for(prop, _text(r.get("address")), dist),
                documents=docs.get(str(key), []),
            ))
        return apps, snapshot

    def _joins_on(self) -> str:
        d = self.mapping.get("documents")
        return d.get("joins_on", "ref") if d else "ref"

    def _documents(self, app_rows: list[dict]) -> dict[str, list[PlanningDoc]]:
        d = self.mapping.get("documents")
        if not d or not app_rows:
            return {}
        c = d["columns"]
        keys = [str(r.get("id") if self._joins_on() == "id" else r.get("ref")) for r in app_rows]
        sel = [sql.SQL("{}::text as app_key").format(sql.Identifier(c["app_key"]))]
        for role in ("id", "title", "path", "url"):
            if role in c:
                sel.append(sql.SQL("{} as {}").format(sql.Identifier(c[role]), sql.Identifier(role)))
        q = sql.SQL("select {s} from {t} where {k}::text = any(%s)").format(
            s=sql.SQL(", ").join(sel), t=_qual(d["schema"], d["table"]), k=sql.Identifier(c["app_key"]))
        root = self.mapping.get("documents_root") or ""
        out: dict[str, list[PlanningDoc]] = {}
        for i, r in enumerate(self.conn.execute(q, (keys,)).fetchall()):
            path = r.get("path")
            if path and root and not Path(path).is_absolute():
                path = str(Path(root) / path)
            out.setdefault(r["app_key"], []).append(PlanningDoc(
                doc_id=str(r.get("id") or f"doc{i}"), title=_text(r.get("title")),
                path=path, url=_text(r.get("url"))))
        return out


def _now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")
