import os
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from scripts.analyze_fac_flight_dates import ANALYSIS_SQL, analyze
from scripts.build_chamber_database import build


def test_official_annual_release_preserves_units_coverage_and_precedence(tmp_path):
    output = tmp_path / "official.sqlite"
    assert build(output, fac_official=True) == build(output, fac_official=True)
    with closing(sqlite3.connect(output)) as db:
        assert db.execute(
            "SELECT COUNT(*), SUM(registered_dcs_events), SUM(student_dcs_events), "
            "SUM(instructor_dcs_events), SUM(hypoxia), SUM(rapid_decompression), "
            "SUM(trained_crew) FROM fac_official_chamber_year"
        ).fetchone() == (11, 54, 35, 19, 5030, 1715, 7599)
        assert db.execute(
            "SELECT COUNT(*), SUM(registered_dcs_events), SUM(student_dcs_events) "
            "FROM fac_official_annual WHERE year NOT BETWEEN 2010 AND 2020"
        ).fetchone() == (6, None, None)
        assert db.execute(
            "SELECT partial_through,ejection FROM fac_official_annual WHERE year=2021"
        ).fetchone() == ("2021-03-31", None)
        assert db.execute(
            "SELECT COUNT(thesis_cases),SUM(registered_dcs_events=thesis_cases), "
            "SUM(chamber_activities),SUM(thesis_training_count) FROM fac_celis_annual_reconciliation"
        ).fetchone() == (11, 11, 6745, 8993)
        assert (
            db.execute("SELECT name FROM sqlite_master WHERE name='fac_official_case'").fetchone()
            is None
        )
        assert dict(
            db.execute(
                "SELECT category, events FROM fac_official_observation WHERE dimension='dcs_subtype'"
            )
        ) == {"I": 2, "II": 1, "unspecified": 51}


def test_original_workbooks_reproduce_roles_and_case_missingness(tmp_path):
    paths = [os.environ.get(k) for k in ("FAC_CASE_REGISTER", "FAC_TRAINING_REGISTER")]
    if not all(paths):
        pytest.skip("Requires the two original FAC workbooks")
    sources = [Path(p) for p in paths]
    output = tmp_path / "cases.sqlite"
    digest = build(output, fac_workbooks=sources)
    assert build(output, fac_workbooks=sources) == digest
    with closing(sqlite3.connect(output)) as db:
        assert db.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        assert db.execute(
            "SELECT COUNT(*),SUM(dcs),COUNT(age_years),COUNT(flight_date),COUNT(document_group),"
            "COUNT(DISTINCT document_group), COUNT(treatment_source) FROM fac_official_case"
        ).fetchone() == (54, 54, 46, 53, 47, 41, 6)
        assert db.execute(
            "SELECT year, flight_date, invalid_source_date FROM fac_official_case WHERE source_row=28"
        ).fetchone() == (2016, None, "15/93/2016")
        # Both sex and role have 35/19 margins. Check the cross-table to detect swapped columns.
        assert db.execute(
            "SELECT role,sex,COUNT(*) FROM fac_official_case GROUP BY role,sex ORDER BY role,sex"
        ).fetchall() == [
            ("ALUMNO", "FEM", 9),
            ("ALUMNO", "MAS", 26),
            ("INSTRUCTOR", "FEM", 10),
            ("INSTRUCTOR", "MAS", 9),
        ]
    with pytest.raises(ValueError, match="differs from the registered"):
        build(output, fac_workbooks=sources[::-1])
    history = tmp_path / "history.sqlite"
    assert analyze(output, history) == analyze(output, history)
    with closing(sqlite3.connect(history)) as db:
        assert db.execute(
            "SELECT count(*),sum(case_records),sum(case_dates),sum(case_records=2) "
            "FROM fac_instructor_case_week"
        ).fetchone() == (16, 18, 17, 2)
        assert db.execute(
            "SELECT days_since_prior_dated_case_flight FROM fac_instructor_case_intervals "
            "WHERE prior_dated_case_flight IS NOT NULL ORDER BY 1"
        ).fetchall() == [(97,), (362,), (800,), (862,), (923,)]


def test_fac_weeks_and_reported_combined_session():
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("CREATE TABLE fac_official_case(source_row, role, document_group, flight_date)")
        db.executemany(
            "INSERT INTO fac_official_case VALUES (?, 'INSTRUCTOR', ?, ?)",
            [
                (1, 1, "2020-12-31"),
                (2, 1, "2021-01-01"),
                (3, 1, "2021-01-04"),
                (4, None, "2021-01-04"),
                (5, 2, None),
            ],
        )
        db.executescript(ANALYSIS_SQL.read_text(encoding="utf-8"))
        assert db.execute(
            "SELECT source_row,days_since_prior_dated_case_flight,same_iso_week "
            "FROM fac_instructor_case_intervals ORDER BY source_row"
        ).fetchall() == [(1, None, None), (2, 1, 1), (3, 3, 0)]
        assert db.execute(
            "SELECT week_start_monday,case_records FROM fac_instructor_case_week ORDER BY 1"
        ).fetchall() == [("2020-12-28", 2), ("2021-01-04", 2)]
        assert db.execute(
            "SELECT facility_rd_exercises_per_week,facility_25000_ft_flights_per_week,"
            "combined_sessions_per_week,individual_flights_per_week_cap "
            "FROM fac_protocol_calendar ORDER BY period"
        ).fetchall() == [(2, 3, None, None), (1, 1, 1, 1)]
        assert db.execute(
            "SELECT calculated_transit_min,stated_hold_min FROM fac_nominal_profile_phase "
            "WHERE phase>=5 ORDER BY phase"
        ).fetchall() == [(6.656, None), (None, 10), (2.8, None), (None, 10), (3.856, None)]
