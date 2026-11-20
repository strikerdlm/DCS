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
            "SELECT count(*) FROM review_record JOIN review_retrieval USING(run_id) "
            "WHERE run_date='2026-11-19'"
        ).fetchone() == (66,)
        run_counts = db.execute(
            "SELECT run_id,reported_total,retrieved FROM review_run_counts "
            "WHERE run_id LIKE '2026-11-20-%' ORDER BY run_id"
        ).fetchall()
        assert run_counts == [
            ("2026-11-20-eds-role", 27, 15),
            ("2026-11-20-eds-seed", 21, 9),
            ("2026-11-20-eds-training", 249, 40),
            ("2026-11-20-primary-followup", None, 2),
        ]
        seed_reports = {
            row[0]
            for row in db.execute(
                "SELECT report_id FROM review_record WHERE run_id='2026-11-20-eds-seed' "
                "AND json_extract(metadata_json,'$.role_review')='existing_role_candidate'"
            )
        }
        assert seed_reports == {
            "pmid:971183",
            "pmid:3790029",
            "pmid:1755801",
            "pmid:12546299",
            "pmid:30352646",
            "pmid:32574436",
        }
        observations = {
            observation_id: (cases, denominator, rate)
            for observation_id, cases, denominator, rate in db.execute(
                "SELECT observation_id,cases,denominator,reported_rate_percent "
                "FROM review_search_observation"
            )
        }
        assert observations == {
            "iaf-api": (4, None, None),
            "iaf-non-api": (7, None, None),
            "itaf-dcs-rounded": (None, 1777, 0.1),
            "polaris-ground-dcs": (0, 8, None),
            "polaris-ground-vge": (4, 8, None),
            "sweden-simulated-eva-vge": (2, 20, None),
            "uk-research-dcs-episodes": (10, None, None),
            "uk-research-dcs-person": (5, 20, None),
        }
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
