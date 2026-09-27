"""Runs the DB adapter against a throwaway PostgreSQL cluster with an Idox-like schema."""

import os
import shutil
import socket
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

from flip.models import Property
from flip.sources import user_db

PG_BIN = next((p for p in ("/usr/lib/postgresql/16/bin", "/usr/lib/postgresql/15/bin",
                           "/opt/homebrew/bin", "/usr/local/bin") if Path(p, "initdb").exists()), None)
pytestmark = pytest.mark.skipif(PG_BIN is None or os.geteuid() == 0 and not shutil.which("su"),
                                reason="no local PostgreSQL binaries")


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="module")
def pg():
    tmp = Path(tempfile.mkdtemp())
    os.chmod(tmp, 0o777)
    data, port = tmp / "data", _free_port()
    run_as = ["su", "postgres", "-s", "/bin/sh", "-c"] if os.geteuid() == 0 else None

    def sh(cmd):
        full = run_as + [cmd] if run_as else ["sh", "-c", cmd]
        subprocess.run(full, check=True, capture_output=True)

    sh(f"{PG_BIN}/initdb -D {data} -U flip --auth=trust")
    sh(f"{PG_BIN}/pg_ctl -D {data} -o '-p {port} -k {tmp} -c listen_addresses=127.0.0.1' -l {tmp}/log start")
    time.sleep(1.5)
    url = f"postgresql://flip@127.0.0.1:{port}/postgres"
    docs = tmp / "docs"
    docs.mkdir()
    (docs / "a1.pdf").write_bytes(b"%PDF-1.4 fake")
    (docs / "bad.pdf").write_bytes(b"<html>")
    import psycopg
    with psycopg.connect(url, autocommit=True) as c:
        c.execute("""
          create table planning_applications (id serial primary key, reference text, proposal text,
            site_address text, postcode text, decision text, decision_date date, date_received date,
            application_type text, lat double precision, lon double precision);
          create table documents (id serial primary key, application_id int, document_type text,
            file_path text, url text);
          create table collection_log (id serial, started_at timestamptz, note text);
          insert into planning_applications (reference, proposal, site_address, postcode, decision,
            decision_date, lat, lon) values
           ('23/01111/HFUL','Single storey rear extension','12 Mill Road Cambridge','CB1 2AB','Approved','2023-05-01',52.2000,0.1400),
           ('22/02222/HFUL','Replacement windows','14 Mill Road Cambridge','CB1 2AB','Approved','2022-03-01',52.2001,0.1401),
           ('21/03333/FUL','Erection of dwelling on land rear of 13 Mill Road','13 Mill Road Cambridge','CB1 2AC','Refused','2021-01-01',52.2002,0.1402),
           ('20/04444/FUL',NULL,'40 Mill Road Cambridge','CB1 2AD',NULL,NULL,52.2010,0.1410),
           ('19/05555/FUL','Loft conversion','5 Far Street Ely','CB7 4AA','Approved','2019-01-01',52.4,0.26);
          insert into documents (application_id, document_type, file_path) values
           (1,'Decision notice','a1.pdf'), (1,'Officer report','bad.pdf'), (3,'Decision notice','missing.pdf');
        """)
    os.environ["FLIP_DOCS_ROOT"] = str(docs)
    yield url, tmp
    sh(f"{PG_BIN}/pg_ctl -D {data} stop -m fast")


def test_discover_and_query(pg):
    url, tmp = pg
    conn = user_db.connect(url)
    result = user_db.discover(conn, out_path=tmp / "db_mapping.yaml")
    m = result["mapping"]
    assert m["applications"]["table"] == "planning_applications"
    cols = m["applications"]["columns"]
    assert cols["description"] == "proposal"
    assert cols["ref"] == "reference" and cols["address"] == "site_address"
    assert m["documents"]["table"] == "documents" and m["documents"]["joins_on"] == "id"
    r = result["readability"]
    assert r["descriptions"]["missing"] == 1
    assert r["documents"] == {"readable": 1, "not_a_pdf": 1, "file_not_found": 1}

    prop = Property(case_id="t", address="12 Mill Road, Cambridge", street="Mill Road",
                    postcode="CB1 2AB", lat=52.2000, lon=0.1400)
    apps, snapshot = user_db.PlanningDB(conn, m).applications_for(prop)
    by_ref = {a.ref: a for a in apps}
    assert "19/05555/FUL" not in by_ref                      # Ely: out of range
    assert by_ref["23/01111/HFUL"].relation == "subject"
    assert by_ref["22/02222/HFUL"].relation == "adjoining"
    assert by_ref["21/03333/FUL"].relation == "opposite"
    assert by_ref["20/04444/FUL"].description is None
    assert [d.title for d in by_ref["23/01111/HFUL"].documents] == ["Decision notice", "Officer report"]
    assert snapshot
    # connection is read-only
    import psycopg
    with pytest.raises(psycopg.errors.ReadOnlySqlTransaction):
        conn.execute("insert into collection_log (note) values ('x')")
    conn.rollback()
