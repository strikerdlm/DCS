"""Add the reported FAC protocol and case-flight chronology to a local database copy."""

import argparse
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

from scripts.build_chamber_database import FAC_PRIVATE_OUTPUT, ROOT, publish, sha256

ANALYSIS_SQL = ROOT / "data" / "chamber" / "fac-flight-history" / "analysis.sql"
DEFAULT_OUTPUT = FAC_PRIVATE_OUTPUT.with_name("flight-history.local.sqlite")


def analyze(source, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as folder:
        staged = Path(folder) / "analysis.sqlite"
        with closing(sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)) as original:
            if not original.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='fac_official_case'"
            ).fetchone():
                raise ValueError("Use the case database generated with --fac-workbooks.")
            with closing(sqlite3.connect(staged)) as db:
                original.backup(db)
                db.execute("PRAGMA foreign_keys=ON")
                db.executescript(ANALYSIS_SQL.read_text(encoding="utf-8"))
                db.execute(
                    "INSERT INTO frozen_input VALUES (?,?)",
                    (ANALYSIS_SQL.relative_to(ROOT).as_posix(), sha256(ANALYSIS_SQL)),
                )
                if db.execute("PRAGMA foreign_key_check").fetchone() or db.execute(
                    "PRAGMA integrity_check"
                ).fetchone() != ("ok",):
                    raise ValueError("Chronology database failed integrity checks")
                db.commit()
        publish(staged, output)
    return sha256(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=FAC_PRIVATE_OUTPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(f"{analyze(args.source, args.output)}  {args.output}")
