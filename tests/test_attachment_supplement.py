import sqlite3
from contextlib import closing

from scripts.build_chamber_database import build


def test_attachment_intake_reuses_existing_counts_and_preserves_alternate_evidence(tmp_path):
    output = tmp_path / "attachments.sqlite"
    assert build(output, attachment_supplement=True) == build(output, attachment_supplement=True)
    with closing(sqlite3.connect(output)) as db:
        assert db.execute("SELECT count(*) FROM attachment_source").fetchone() == (6,)
        assert db.execute("SELECT count(*) FROM attachment_overlap").fetchone() == (18,)
        assert db.execute("SELECT count(*) FROM attachment_observation").fetchone() == (150,)
        assert db.execute(
            """SELECT relationship,count(*),count(alternate_dcs)
               FROM attachment_nasa_test GROUP BY relationship ORDER BY relationship"""
        ).fetchall() == [("alternate_counts", 9, 9), ("reprint", 31, 0)]
        assert db.execute(
            """SELECT report_total,f1_total,report_dcs,f1_dcs
               FROM attachment_nasa_count_comparison WHERE test_id='P IV'"""
        ).fetchone() == (56, 65, 8, 8)
        assert db.execute(
            """SELECT outcome_documentation,count(*)
               FROM attachment_u2_flight GROUP BY outcome_documentation ORDER BY 1"""
        ).fetchall() == [("dcs_abort", 2), ("no_symptom_entry", 118), ("symptom_report", 2)]
        assert db.execute(
            """SELECT flight_number,high_altitude_minutes,symptom_time_reported_min
               FROM attachment_u2_flight WHERE outcome_documentation='dcs_abort'
               ORDER BY flight_number"""
        ).fetchall() == [(19, 410, "300"), (25, 260, "300")]
        assert db.execute(
            """SELECT stratum,events,denominator,denominator_unit FROM attachment_observation
               WHERE source_id='brandt09_attachment' AND endpoint='dcs'
                 AND analysis_role='descriptive' ORDER BY stratum"""
        ).fetchall() == [
            ("fy04_observers", 6, 323, "person_exposures"),
            ("fy04_students", 4, 780, "person_exposures"),
        ]
        assert db.execute(
            """SELECT count(*),sum(denominator),sum(value)
               FROM attachment_observation WHERE denominator_unit='person_evas'"""
        ).fetchone() == (4, 213, 0.0)
        assert db.execute(
            "SELECT count(*),sum(dcs_cases),sum(dcs_denominator) FROM development_counts"
        ).fetchone() == (41, 124, 885)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
