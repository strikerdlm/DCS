import sqlite3
from contextlib import closing

from scripts.build_chamber_database import build


def test_rojas_tables_preserve_sample_units_and_unallocated_case(tmp_path):
    output = tmp_path / "observed.sqlite"
    assert build(output, rojas_supplement=True) == build(output, rojas_supplement=True)
    with closing(sqlite3.connect(output)) as db:
        assert db.execute(
            "SELECT grouping,categories,cases_tabulated,controls_tabulated,"
            "cases_outside_table,controls_outside_table "
            "FROM rojas_table_coverage ORDER BY grouping"
        ).fetchall() == [
            ("afsc", 40, 122, None, 1, None),
            ("alcohol", 4, 55, 163, 68, 206),
            ("sex", 2, 123, 369, 0, 0),
            ("tobacco", 2, 55, 163, 68, 206),
        ]
        assert db.execute(
            "SELECT label,case_count,sampled_control_count FROM rojas_observation "
            "WHERE grouping='alcohol' AND category='at_least_4_per_week'"
        ).fetchone() == (">= 4 times per week", 2, 2)
        assert db.execute(
            "SELECT exposure,p_comparison,p_reported FROM rojas_result ORDER BY exposure"
        ).fetchall() == [
            ("alcohol", "=", 0.651),
            ("high_risk_occupation", "<", 1e-7),
            ("tobacco", "=", 0.4776),
        ]
        assert db.execute(
            "SELECT sharepoint_source_id,relationship FROM rojas_overlap"
        ).fetchone() == ("rojas15", "same_study")
        assert db.execute(
            "SELECT count(*) FROM sharepoint_observation WHERE source_id='rojas15'"
        ).fetchone() == (6,)
        assert db.execute(
            "SELECT sum(dcs_cases),sum(dcs_denominator) FROM development_counts"
        ).fetchone() == (124, 885)
        assert not db.execute("PRAGMA foreign_key_check").fetchone()
