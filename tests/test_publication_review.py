import sqlite3

import pytest

from scripts.build_chamber_database import build


def test_publication_register_build(tmp_path):
    path = tmp_path / "observed.sqlite"
    digest = build(path, publication_review=True)
    assert build(path, publication_review=True) == digest
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        assert db.execute(
            "SELECT sum(registered_dcs_events) FROM fac_official_chamber_year"
        ).fetchone() == (54,)
        assert db.execute("SELECT count(*) FROM review_record WHERE run_id IS NULL").fetchone() == (
            993,
        )
        assert db.execute(
            "SELECT count(*) FROM review_record WHERE run_id IS NOT NULL"
        ).fetchone() == (66,)
        assert db.execute(
            "SELECT count(*) FROM review_study_report WHERE role='primary'"
        ).fetchone() == (6,)
        groups = db.execute(
            "SELECT report_id, chamber_role, sum(cases), sum(exposures) FROM review_seed_role_cell "
            "GROUP BY report_id, chamber_role"
        ).fetchall()
        assert len(groups) == 12
        assert ("pmid:971183", "staff", 57, 14959) in groups
        assert ("pmid:3790029", "trainee", 8, 12596) in groups
        assert db.execute("SELECT count(*) FROM review_supplementary_role_cell").fetchone() == (6,)
        assert db.execute("SELECT count(*) FROM review_historical_search_record").fetchone() == (
            473,
        )
        assert db.execute("SELECT count(*) FROM publication_search_run").fetchone() == (72,)
        comments = db.execute(
            "SELECT left_report FROM review_report_relation "
            "WHERE right_report='pmid:33875060' AND relationship='comment_on'"
        ).fetchall()
        assert set(comments) == {("pmid:34642007",), ("pmid:34642008",)}
        assert db.execute("SELECT count(*) FROM review_current_screening").fetchone() == (0,)
        key = db.execute(
            "SELECT record_key FROM review_record ORDER BY record_key LIMIT 1"
        ).fetchone()[0]
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO review_screening VALUES (?,'reviewer','full_text',1,'2026-11-19',"
                "'exclude','','')",
                (key,),
            )
        db.executemany(
            "INSERT INTO review_screening VALUES (?,'reviewer','title_abstract',"
            "?,'2026-11-19',?,NULL,NULL)",
            [(key, 1, "uncertain"), (key, 2, "include")],
        )
        assert db.execute("SELECT revision, decision FROM review_current_screening").fetchall() == [
            (2, "include")
        ]
