import sqlite3
from contextlib import closing

from scripts.build_chamber_database import build


def test_zotero_intake_reuses_prior_evidence_and_keeps_eva_increments(tmp_path):
    path = tmp_path / "evidence.sqlite"
    assert build(path, zotero_dcs_supplement=True) == build(path, zotero_dcs_supplement=True)
    with closing(sqlite3.connect(path)) as db:
        assert db.execute(
            "SELECT parse_mode,count(*) FROM zotero_dcs_source GROUP BY parse_mode ORDER BY 1"
        ).fetchall() == [("agentic", 14), ("reused", 9)]
        assert db.execute("SELECT count(*) FROM zotero_dcs_overlap").fetchone() == (33,)
        assert db.execute(
            "SELECT count(*) FROM zotero_dcs_overlap "
            "WHERE relationship='exact_file' AND related_key LIKE 'attachments/%'"
        ).fetchone() == (6,)
        assert db.execute(
            "SELECT sum(reported_2013_person_evas),sum(additional_person_evas),"
            "sum(reported_2016_person_evas),sum(additional_reported_dcs) "
            "FROM zotero_dcs_eva_totals_2016"
        ).fetchone() == (213, 31, 244, 0)
        assert db.execute(
            "SELECT count(*) FROM zotero_dcs_observation AS o "
            "JOIN zotero_dcs_source AS s USING(source_id) WHERE s.disposition!='extended'"
        ).fetchone() == (0,)
        assert db.execute("SELECT count(*) FROM zotero_dcs_case").fetchone() == (6,)
        assert db.execute("SELECT count(*) FROM zotero_dcs_eva_break").fetchone() == (7,)
        assert db.execute(
            "SELECT measured_or_reported_seconds,assumed_break_seconds FROM zotero_dcs_eva_break "
            "WHERE eva_key='INC-50 EVA 38'"
        ).fetchone() == (13.0, 240.0)
        assert db.execute(
            "SELECT count(*),sum(dcs_cases),sum(dcs_denominator) FROM development_counts"
        ).fetchone() == (41, 124, 885)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
