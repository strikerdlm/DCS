import json
import shutil
import sqlite3

import pytest

from scripts.chamber_products import PRODUCTS, connect_pair, publish_pair
from scripts.evaluate_chamber_benchmark import run


@pytest.fixture(scope="module")
def release(tmp_path_factory):
    folder = tmp_path_factory.mktemp("chamber") / "release"
    publish_pair(folder)
    return folder


def test_separate_products_join_without_duplicate_cases_or_strata(release):
    with connect_pair(release) as db:
        for schema in ("main", "review"):
            assert db.execute(f"PRAGMA {schema}.integrity_check").fetchone() == ("ok",)
            assert db.execute(f"PRAGMA {schema}.foreign_key_check").fetchall() == []
            for (view,) in db.execute(f"SELECT name FROM {schema}.sqlite_schema WHERE type='view'"):
                db.execute(f'SELECT * FROM {schema}."{view}" LIMIT 1').fetchone()
        assert db.execute("SELECT 1 FROM review.sqlite_schema WHERE name='nasa_test'").fetchone() is None
        assert db.execute("SELECT 1 FROM main.sqlite_schema WHERE name='review_screening'").fetchone() is None
        assert db.execute("""
            SELECT count(*), count(DISTINCT c.case_id), count(r.record_key)
            FROM historical_case_catalog c LEFT JOIN review.review_record r
            ON (r.record_key,r.report_id)=(c.record_key,c.report_id)
        """).fetchone() == (105, 105, 105)
        assert db.execute("""
            SELECT source_id,onset_min,first_assessment_min,recurrence_report_day,recurrence_free_followup_min
            FROM shared_case_evidence ORDER BY source_id
        """).fetchall() == [
            ("case17_delayed", 180, 2880, 14, None),
            ("yoneda98_skin_bends", None, None, None, 1440),
        ]
        assert db.execute("""
            SELECT dcs_time_min,preferred_dcs_time_min FROM dcs_case WHERE published_case_number=30
        """).fetchone() == (86, 68)
        assert db.execute("SELECT count(*) FROM dcs_case").fetchone() == (103,)
        assert db.execute("""
            SELECT cases,exposures FROM chamber_group_evidence
            WHERE study_id='usaf-howard-1979-1981' ORDER BY stratum
        """).fetchall() == [(67, 47921), (139, 203315)]
        assert db.execute("""
            SELECT count(*),sum(dcs_cases),sum(dcs_denominator) FROM development_counts
        """).fetchone() == (41, 124, 885)
        assert db.execute("SELECT count(*) FROM vge_interval").fetchone() == (238,)
        assert db.execute("""
            SELECT count(*) FROM model_report_link l LEFT JOIN review.review_record r
            ON (r.record_key,r.report_id)=(l.record_key,l.report_id) WHERE r.record_key IS NULL
        """).fetchone() == (0,)
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            db.execute("DELETE FROM main.shared_case_evidence")


def test_benchmark_reproduces_original_without_the_review_file(release, tmp_path):
    model = tmp_path / PRODUCTS["model"]
    shutil.copyfile(release / model.name, model)
    shutil.copyfile(release / "release.json", tmp_path / "release.json")
    result = run(model)
    assert result.pop("database_release_id") == json.loads((release / "release.json").read_bytes())["evidence_sha256"]
    assert result == run()


def test_mixed_or_edited_files_rejected(release, tmp_path):
    folder = tmp_path / "edited"
    shutil.copytree(release, folder)
    with sqlite3.connect(folder / PRODUCTS["review"]) as db:
        db.execute("UPDATE dataset_release SET release_id='different'")
    with pytest.raises(ValueError, match="checksum"):
        with connect_pair(folder):
            pytest.fail("modified release was opened")
    # A verified rebuild must also preserve an existing destination with user changes.
    with pytest.raises(FileExistsError):
        publish_pair(folder)
    with sqlite3.connect(folder / PRODUCTS["review"]) as db:
        assert db.execute("SELECT release_id FROM dataset_release").fetchone() == ("different",)
