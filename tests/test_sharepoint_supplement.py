import sqlite3
from contextlib import closing

from scripts.build_chamber_database import build


def test_library_supplement_preserves_risk_sets_and_published_disagreements(tmp_path):
    database = tmp_path / "observed.sqlite"
    digest = build(database, sharepoint_supplement=True)
    assert build(database, sharepoint_supplement=True) == digest
    with closing(sqlite3.connect(database)) as db:
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        assert db.execute(
            "SELECT COUNT(*), SUM(dcs_cases), SUM(dcs_denominator) FROM development_counts"
        ).fetchone() == (41, 124, 885)
        assert db.execute("SELECT COUNT(*) FROM locked_external").fetchone() == (5,)
        assert db.execute(
            "SELECT ergometry_order, COUNT(*), SUM(dcs), COUNT(post_exposure_dcs_mark), "
            "SUM(max_spencer_grade='IV') FROM sharepoint_vge_positive_record "
            "GROUP BY ergometry_order ORDER BY ergometry_order"
        ).fetchall() == [("first", 13, 3, 1, 1), ("second", 13, 1, 1, 3)]
        assert db.execute(
            "SELECT events, denominator FROM sharepoint_observation "
            "WHERE source_id='nasa04_exercise' AND endpoint='any_vge' ORDER BY stratum"
        ).fetchall() == [(13, 27), (13, 27)]
        assert db.execute(
            "SELECT SUM(events), MIN(denominator), MAX(denominator) FROM sharepoint_observation "
            "WHERE analysis_role='doppler_readings' GROUP BY stratum ORDER BY stratum"
        ).fetchall() == [(683, 683, 683), (555, 555, 555)]
        assert db.execute(
            "SELECT events, denominator FROM sharepoint_observation "
            "WHERE source_id='celis23_thesis' AND stratum IN ('results_total','year_table_total') "
            "ORDER BY stratum"
        ).fetchall() == [(54, 6745), (54, 8993)]
        assert db.execute(
            "SELECT events, denominator FROM sharepoint_observation "
            "WHERE source_id='nasa_treatment' AND endpoint='any_vge' "
            "AND analysis_role='denominator_conflict' ORDER BY denominator"
        ).fetchall() == [(334, 841), (345, 842)]
        assert db.execute(
            "SELECT SUM(events), SUM(denominator) FROM sharepoint_observation "
            "WHERE source_id='hancock20' AND stratum IN ('1997','1998')"
        ).fetchone() == (38, 57336)
        assert db.execute(
            "SELECT events, denominator FROM sharepoint_observation WHERE source_id='hancock20' "
            "AND stratum='1997–1998' AND endpoint='dcs'"
        ).fetchone() == (38, 57366)
        assert db.execute(
            "SELECT COUNT(*), COUNT(events), COUNT(reported_percent) "
            "FROM sharepoint_observation WHERE source_id='webb03_sex'"
        ).fetchone() == (72, 0, 72)
        assert db.execute(
            "SELECT COUNT(*) FROM citation_observation WHERE source_id='webb03_sex' "
            "AND stratum IN ('Men','Women') AND endpoint IN ('dcs','any_vge','grade_iv_vge')"
        ).fetchone() == (6,)
        assert db.execute(
            "SELECT COUNT(*) FROM sharepoint_observation WHERE source_id='webb05_susceptibility'"
        ).fetchone() == (0,)
        assert db.execute(
            "SELECT COUNT(*) FROM citation_observation WHERE source_id='webb05_susceptibility' "
            "AND denominator=1879 AND endpoint='dcs'"
        ).fetchone() == (1,)


def test_deduplicated_views_resolve_reprints_and_preserve_disagreements(tmp_path):
    database = tmp_path / "observed.sqlite"
    build(database, sharepoint_supplement=True)
    with closing(sqlite3.connect(database)) as db:
        assert db.execute("SELECT COUNT(*) FROM a1309_deduplicated_profile").fetchone() == (82,)
        assert db.execute(
            "SELECT canonical_table, canonical_source_id, canonical_stratum "
            "FROM a1309_profile_reprint WHERE profile='PE1-A'"
        ).fetchone() == ("citation_observation", "webb96_preoxygenation", "exercise10_rest50")
        assert db.execute(
            "SELECT profile, exposures FROM a1309_deduplicated_profile "
            "WHERE profile IN ('PRP IV', 'PE1-A', 'PE1-B') ORDER BY profile"
        ).fetchall() == [("PE1-B", 28), ("PRP IV", 69)]
        assert db.execute(
            "SELECT ref_no FROM citation_deduplicated_reference WHERE ref_no IN (53, 84)"
        ).fetchall() == [(53,)]
        assert db.execute("SELECT COUNT(*) FROM citation_reference").fetchone() == (243,)
        assert db.execute("SELECT COUNT(*) FROM citation_deduplicated_reference").fetchone() == (
            242,
        )
        assert db.execute(
            "SELECT source_id, stratum, endpoint, canonical_stratum "
            "FROM sharepoint_observation_reprint ORDER BY source_id, stratum, endpoint"
        ).fetchall() == [
            ("celis23_abstract", "diagnosed_cases", "dcs_type_i", "resumen_cases"),
            ("celis23_abstract", "diagnosed_cases", "dcs_type_ii", "resumen_cases"),
            (
                "celis23_abstract",
                "diagnosed_cases",
                "instructor_or_inside_observer",
                "resumen_cases",
            ),
            ("celis23_abstract", "results_total", "dcs", "results_total"),
            ("nasa_treatment", "3a", "dcs", "3a"),
            ("nasa_treatment", "8a", "dcs", "8a"),
            ("nasa_treatment", "Phase_II", "dcs", "P II"),
            ("nasa_treatment", "Phase_IV", "dcs", "P IV"),
        ]
        assert db.execute("SELECT COUNT(*) FROM sharepoint_observation").fetchone() == (208,)
        assert db.execute(
            "SELECT COUNT(*) FROM sharepoint_deduplicated_observation"
        ).fetchone() == (200,)
        assert db.execute(
            "SELECT stratum, reported_percent FROM sharepoint_deduplicated_observation "
            "WHERE source_id='nasa_treatment' AND endpoint='dcs' "
            "AND stratum IN ('3b','Phase_I') ORDER BY stratum"
        ).fetchall() == [("3b", 22.8), ("Phase_I", 18.3)]
