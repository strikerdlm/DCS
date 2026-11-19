"""Regression checks for denominators, endpoints, holdout leakage and prospective ascertainment."""

import hashlib
import json
import sqlite3
from contextlib import closing
from copy import deepcopy

import pytest

from scripts.build_chamber_database import ROOT, build, populate
from scripts.evaluate_chamber_benchmark import assess_external, family_blocks, vge_check
from scripts.fac_chamber_registry import append, initialize
from tinydcs.study_models import GROUP, read_study


def test_zotero_supplement_preserves_denominators_and_model_holdout(tmp_path):
    target = tmp_path / "supplemented.sqlite"
    digest = build(target, zotero_supplement=True)
    assert build(target, zotero_supplement=True) == digest
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("SELECT count(*) FROM zotero_source").fetchone() == (9,)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)
        assert db.execute(
            "SELECT sum(cases), sum(denominator) FROM zotero_observation "
            "WHERE source_id='crowell83' AND locator LIKE 'Table II%'"
        ).fetchone() == (69, 19573)
        assert db.execute(
            "SELECT cases, denominator FROM zotero_observation "
            "WHERE source_id='crowell83' AND stratum='results_all'"
        ).fetchone() == (69, 21423)
        assert db.execute(
            "SELECT count(*), count(cases) FROM zotero_observation WHERE source_id='ohrui02'"
        ).fetchone() == (16, 0)
        assert db.execute(
            "SELECT sum(cases), sum(denominator) FROM zotero_observation "
            "WHERE source_id='brandt09' AND denominator_unit='observer_months'"
        ).fetchone() == (6, 810)


@pytest.fixture
def evidence():
    with closing(sqlite3.connect(":memory:")) as db:
        db.row_factory = sqlite3.Row
        populate(db)
        yield db


def test_web_supplement_reconciles_sources_and_preserves_frozen_benchmark(tmp_path):
    target = tmp_path / "web.sqlite"
    build(target, web_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("SELECT count(*) FROM zotero_source").fetchone() == (9,)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)
        assert db.execute(
            "SELECT count(*) FROM web_source WHERE disposition='extracted'"
        ).fetchone() == (9,)
        assert db.execute(
            "SELECT source_id, count(*), sum(cases), sum(denominator) FROM web_observation "
            "WHERE source_id IN ('olaya25','malconian87') AND analysis_role='descriptive_stratum' "
            "GROUP BY source_id ORDER BY source_id"
        ).fetchall() == [("malconian87", 11, 28, 274), ("olaya25", 11, 15, 10280)]
        assert db.execute(
            "SELECT cases, denominator, altitude_low_ft FROM web_observation "
            "WHERE source_id='olaya25' AND stratum='year-2015'"
        ).fetchone() == (1, 828, None)
        assert db.execute(
            "SELECT cases, denominator, analysis_role FROM web_observation "
            "WHERE source_id='davenport97' AND endpoint='suspected_dcs'"
        ).fetchone() == (12, 5851, "overlap_hold")
        assert db.execute(
            "SELECT stratum, cases, denominator FROM web_observation "
            "WHERE source_id='anell21_hyperoxic' AND analysis_role='descriptive_stratum' ORDER BY stratum"
        ).fetchall() == [("ALT-HYP", 1, 13), ("H-HYP", 2, 13), ("H-NOR", 3, 13)]
        assert db.execute(
            "SELECT count(*) FROM web_observation JOIN web_source USING (source_id) "
            "WHERE disposition='lead_only'"
        ).fetchone() == (0,)


def test_source_counts_and_noninterchangeable_endpoints(evidence):
    row = evidence.execute("SELECT * FROM a1309_profile WHERE profile='PRP IV'").fetchone()
    assert (row["exposures"], row["printed_events"], row["exact_cases"]) == (69, "8.3", None)
    assert evidence.execute("SELECT count(*) FROM a1309_nasa_overlap").fetchone()[0] == 35
    assert (
        evidence.execute(
            "SELECT denominator FROM aviation_count WHERE stratum='flight'"
        ).fetchone()[0]
        is None
    )
    assert evidence.execute("SELECT count(*) FROM air_break_estimate").fetchone()[0] == 24
    assert (
        evidence.execute(
            "SELECT any_grade_vge_cases FROM nasa_test WHERE test_id='1b10.2'"
        ).fetchone()[0]
        is None
    )
    rows = evidence.execute("SELECT * FROM development_counts").fetchall()
    assert len(set(family_blocks(rows))) == 8
    assert tuple(
        evidence.execute(
            "SELECT sum(dcs_cases),sum(dcs_denominator) FROM development_counts"
        ).fetchone()
    ) == (124, 885)
    assert vge_check(evidence)["interval_nll"]["predictor"] == pytest.approx(1.1912390611)


def test_literature_supplement_preserves_reported_precision_and_case_scope(tmp_path):
    target = tmp_path / "literature.sqlite"
    build(target, literature_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)
        assert db.execute("SELECT count(*) FROM zotero_source").fetchone() == (9,)
        assert db.execute("SELECT count(*) FROM web_observation").fetchone() == (57,)
        assert db.execute(
            "SELECT observation_kind, count(*) FROM literature_observation "
            "GROUP BY observation_kind ORDER BY observation_kind"
        ).fetchall() == [("case_count_only", 1), ("exact_count", 16), ("reported_percent", 72)]
        assert db.execute(
            "SELECT stratum, cases, denominator, analysis_role FROM literature_observation "
            "WHERE source_id='faa90' ORDER BY stratum"
        ).fetchall() == [
            ("all-roles-reported", 10, None, "overlapping_margin"),
            ("student-suspected", 3, 12759, "overlap_hold"),
        ]
        assert db.execute(
            "SELECT count(*), count(first_vge_detection_min) FROM literature_case "
            "WHERE source_id='nasa03' AND endpoint='dcs_type_ii_historical'"
        ).fetchone() == (6, 5)
        assert db.execute(
            "SELECT cases, denominator, reported_percent FROM literature_observation "
            "WHERE source_id='webb05' AND stratum='22500ft-240min' AND endpoint='dcs'"
        ).fetchone() == (None, 19, 26.3)


def test_cohort_supplement_preserves_exposure_history_and_case_denominators(tmp_path):
    target = tmp_path / "cohort.sqlite"
    build(target, cohort_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("SELECT count(*) FROM literature_case").fetchone() == (6,)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)
        assert db.execute(
            "SELECT count(*), count(cases), count(reported_percent) FROM cohort_observation"
        ).fetchone() == (73, 61, 12)
        assert db.execute(
            "SELECT exposure_context, sum(cases), sum(denominator) FROM cohort_observation "
            "WHERE source_id='pollock03' AND endpoint='dcs' AND analysis_role='descriptive' "
            "GROUP BY exposure_context ORDER BY exposure_context"
        ).fetchall() == [("hypobaric_research", 1, 59), ("post_dive_hypobaric", 2, 96)]
        assert db.execute(
            "SELECT cases, denominator, denominator_unit FROM cohort_observation "
            "WHERE source_id='rush90' AND stratum='all-years' "
            "AND endpoint='dcs_after_air_travel_among_treated'"
        ).fetchone() == (7, 292, "treated_dcs_case")
        assert db.execute(
            "SELECT cases, denominator, reported_percent FROM cohort_observation "
            "WHERE source_id='pilmanis03' AND stratum='slow-all' AND endpoint='dcs_symptoms'"
        ).fetchone() == (None, 40, 47.5)


def test_eligibility_precedes_scoring(evidence):
    model = read_study(GROUP)
    external = evidence.execute("SELECT * FROM locked_external").fetchall()
    assert len(external) == 5
    assert all(assess_external(r, model)["expected"] is None for r in external)
    # Source-compatible positive control uses the actual F1 test 2a covariates and outcomes.
    context = dict(
        source_id="nasa19",
        stratum="2a",
        endpoint="dcs",
        cases=7,
        denominator=23,
        denominator_unit="exposures",
        population_scope="nasa_chamber_research",
        window_code="nasa_test_ascertainment",
        single_protocol=True,
        plateau_min=240,
        body_pressure_psia=4.3,
        mean_tr360=1.69,
        ambulatory=True,
    )
    fit = assess_external(context, model)
    assert fit["expected"] == pytest.approx(23 * 0.2266, abs=0.002)
    assert fit["observed_to_expected"] == pytest.approx(7 / fit["expected"])
    assert assess_external({**context, "mean_tr360": 1.68}, model)["expected"] is None
    assert assess_external({**context, "plateau_min": 10}, model)["log_loss"] is None
    assert assess_external({**context, "endpoint": "grade_iv_vge"}, model)["brier"] is None


def test_citation_release_preserves_reference_direction_and_paired_outcomes(tmp_path):
    target = tmp_path / "citation.sqlite"
    build(target, citation_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute(
            "SELECT min(ref_no), max(ref_no), count(*) FROM citation_reference "
            "WHERE citing_source_id='mahon2014'"
        ).fetchone() == (1, 243, 243)
        assert db.execute(
            "SELECT count(*) FROM citation_citer WHERE cited_source_id='mahon2014'"
        ).fetchone() == (50,)
        assert db.execute(
            "SELECT count(*), count(symptom_listed), count(DISTINCT study_participant) "
            "FROM citation_participant_cell"
        ).fetchone() == (78, 74, 26)
        for arm_a, arm_b, *printed in db.execute(
            "SELECT arm_a, arm_b, participants, both_dcs, a_only, b_only, neither "
            "FROM citation_paired_dcs WHERE source_id='webb96_preoxygenation'"
        ):
            calculated = db.execute(
                "SELECT count(*), sum(a.symptom_listed AND b.symptom_listed), "
                "sum(a.symptom_listed AND NOT b.symptom_listed), "
                "sum(NOT a.symptom_listed AND b.symptom_listed), "
                "sum(NOT a.symptom_listed AND NOT b.symptom_listed) "
                "FROM citation_participant_cell a JOIN citation_participant_cell b "
                "USING(source_id, study_participant) WHERE a.source_id='webb96_preoxygenation' "
                "AND a.arm=? AND b.arm=? AND a.accomplished AND b.accomplished",
                (arm_a, arm_b),
            ).fetchone()
            assert list(calculated) == printed
        assert db.execute(
            "SELECT numerator, denominator FROM citation_observation "
            "WHERE source_id='webb02_postexercise' AND endpoint='dcs' "
            "AND stratum IN ('All exposed','Eligible for randomization') ORDER BY stratum"
        ).fetchall() == [(36, 67), (29, 60)]
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_discovery_release_preserves_conflicts_and_source_scope(tmp_path):
    target = tmp_path / "discovery.sqlite"
    assert build(target, discovery_supplement=True) == build(target, discovery_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit
            FROM discovery_observation WHERE source_id='zainal25'
        """).fetchone() == (4, 395, "person")
        assert db.execute("""
            SELECT sum(numerator),sum(denominator),max(reported_cumulative_denominator)
            FROM discovery_observation
            WHERE source_id='garbino_ea6' AND stratum LIKE 'day-%'
        """).fetchone() == (3, 61, 62)
        assert db.execute("""
            SELECT numerator,denominator,analysis_role FROM discovery_observation
            WHERE source_id='garbino_ea6' AND stratum='all-reported'
        """).fetchone() == (3, 62, "denominator_conflict")
        assert db.execute("""
            SELECT numerator,denominator,reported_percent,analysis_role FROM discovery_observation
            WHERE source_id='webb04_meep' AND endpoint='dcs'
              AND stratum LIKE 'meep-30-min%'
            ORDER BY reported_percent
        """).fetchall() == [(None, None, 40, "outcome_conflict"), (None, 40, 43, "overlap_hold")]
        assert db.execute("""
            SELECT numerator,denominator,target_pressure_kpa FROM discovery_observation
            WHERE source_id='garbino_ea12' AND endpoint='vge_eftedal_brubakk_grade_7'
        """).fetchone() == (1, 50, 29.6)
        assert db.execute("""
            SELECT numerator,denominator FROM discovery_observation
            WHERE source_id='conkin17' AND stratum='nuc-3'
              AND endpoint='spencer_grade_iii_or_iv_vge'
        """).fetchone() == (6, 41)
        assert db.execute("""
            SELECT count(*) FROM discovery_observation
            WHERE source_id='conkin17' AND endpoint IN ('dcs','any_vge','grade_iv_vge')
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT count(*) FROM discovery_overlap
            WHERE source_id='conkin17' AND relationship='same_cohort'
        """).fetchone() == (2,)
        assert db.execute("""
            SELECT issue_id,decision,accepted_value FROM discovery_adjudication
            WHERE issue_id IN ('ea12-target-pressure','ea6-day15','meep30-dcs-rate')
            ORDER BY issue_id
        """).fetchall() == [
            ("ea12-target-pressure", "supported", "29.6 kPa nominal target"),
            ("ea6-day15", "unresolved", None),
            ("meep30-dcs-rate", "supported", "43% at four hours"),
        ]
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)
        assert db.execute("SELECT count(*) FROM a1309_deduplicated_profile").fetchone() == (82,)


def test_publication_release_preserves_source_units_and_search_provenance(tmp_path):
    target = tmp_path / "publications.sqlite"
    assert build(target, publication_supplement=True) == build(target, publication_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT numerator,denominator,denominator_basis FROM publication_observation
            WHERE source_id='furry73' AND stratum='inside-observers'
        """).fetchone() == (35, 60000, "author_reconstructed")
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id='olea18' AND endpoint='dcs'
        """).fetchone() == (2, 3, "treated_referral")
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='balldin02' AND analysis_role='denominator_conflict'
            ORDER BY denominator
        """).fetchall() == [(29, 2525), (29, 2584)]
        assert db.execute("""
            SELECT sum(numerator),max(denominator),min(denominator_unit)
            FROM publication_observation WHERE source_id='muehlberger04'
        """).fetchone() == (1699, 1699, "symptom_report")
        assert (
            db.execute("""
            SELECT r.search_id FROM publication_search_run r
            LEFT JOIN publication_search_hit h USING (search_id)
            GROUP BY r.search_id
            HAVING count(h.rank) <> r.screened_count
                OR sum(h.disposition='extracted') <> r.selected_count
        """).fetchall()
            == []
        )
        assert db.execute("""
            SELECT status,screened_count FROM publication_search_run WHERE search_id='ebsco_unal'
        """).fetchone() == ("blocked", 0)
        assert db.execute("SELECT count(*) FROM discovery_adjudication").fetchone() == (13,)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_historical_release_preserves_exposures_and_links_repeated_volunteers(tmp_path):
    target = tmp_path / "historical.sqlite"
    assert build(target, historical_supplement=True) == build(target, historical_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT source_id,count(*),sum(numerator),sum(denominator)
            FROM publication_observation WHERE source_id IN ('maio69','maio70')
            GROUP BY source_id ORDER BY source_id
        """).fetchall() == [("maio69", 4, 21, 60), ("maio70", 4, 16, 70)]
        assert db.execute("""
            SELECT relationship FROM publication_overlap
            WHERE source_id='maio69' AND related_source='v1.8/maio70'
        """).fetchone() == ("partial_overlap",)
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='meade67'
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='furry73'
        """).fetchone() == (5,)
        assert (
            db.execute("""
            SELECT identifier FROM publication_source WHERE identifier IS NOT NULL
            GROUP BY identifier HAVING count(*) > 1
        """).fetchall()
            == []
        )
        assert db.execute("""
            SELECT count(*) FROM publication_search_hit WHERE search_id LIKE 'historical_%'
        """).fetchone() == (96,)


def test_protocol_release_preserves_repeated_measures_and_nedu_overlap(tmp_path):
    target = tmp_path / "protocols.sqlite"
    assert build(target, protocol_supplement=True) == build(target, protocol_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='krutz87' AND endpoint='grade_2_bends_author_defined'
            ORDER BY stratum
        """).fetchall() == [(12, 14, "overlap_hold"), (8, 14, "overlap_hold")]
        assert db.execute("""
            SELECT endpoint,numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id='dixon88' AND endpoint LIKE 'dcs_%'
            ORDER BY endpoint
        """).fetchall() == [
            ("dcs_first_reported_day_4", 2, 5, "dcs_case"),
            ("dcs_source_defined", 5, 30, "person"),
        ]
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id='webb89_tolerance' AND endpoint='dcs_source_defined'
        """).fetchone() == (0, 21, "person")
        assert db.execute("""
            SELECT DISTINCT endpoint,analysis_role FROM publication_observation
            WHERE source_id='webb93_mixture' ORDER BY endpoint
        """).fetchall() == [("any_vge", "overlap_hold"), ("vge_grade_3_or_4", "overlap_hold")]
        assert (
            db.execute("""
            SELECT numerator,denominator,prebreathe_min FROM publication_observation
            WHERE source_id='elia21_vibration' AND endpoint='dcs_symptoms_during_exposure'
        """).fetchall()
            == [(0, 8, None)] * 3
        )
        assert db.execute("""
            SELECT exposures,exact_cases FROM a1309_profile
            WHERE profile IN ('BSI-A', 'BSI-B') ORDER BY profile
        """).fetchall() == [(17, 10), (36, 32)]
        assert (
            db.execute("""
            SELECT r.search_id FROM publication_search_run r
            LEFT JOIN publication_search_hit h USING (search_id)
            WHERE r.search_id LIKE 'protocol_%'
            GROUP BY r.search_id
            HAVING count(h.rank) <> r.screened_count
                OR sum(h.disposition='extracted') <> r.selected_count
        """).fetchall()
            == []
        )
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_expedition_release_promotes_existing_comex_margins(tmp_path):
    target = tmp_path / "expedition.sqlite"
    assert build(target, expedition_supplement=True) == build(target, expedition_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT cases,denominator,observation_kind,reported_percent
            FROM literature_observation WHERE source_id='molenat02' ORDER BY denominator
        """).fetchall() == [(4, 8, "exact_count", None), (5, 32, "exact_count", None)]
        assert db.execute("""
            SELECT count(*),count(DISTINCT investigator_code),sum(dcs_symptoms),
                   count(DISTINCT CASE WHEN dcs_symptoms=1 THEN investigator_code END)
            FROM publication_chamber_flight WHERE source_id='molenat02_fulltext'
        """).fetchone() == (32, 8, 5, 3)
        assert db.execute("""
            SELECT altitude_m,sum(dcs_symptoms),count(*) FROM publication_chamber_flight
            GROUP BY altitude_m ORDER BY altitude_m
        """).fetchall() == [(5000, 0, 10), (6000, 1, 6), (7000, 0, 8), (8000, 2, 4), (8848, 2, 4)]
        assert db.execute("""
            SELECT duration_table1_min,duration_table2_footnote_min,prebreathe_min
            FROM publication_chamber_flight WHERE duration_table2_footnote_min IS NOT NULL
        """).fetchall() == [(60, 90, 0), (60, 90, 0)]
        assert db.execute("""
            SELECT sum(numerator),sum(denominator) FROM publication_observation
            WHERE source_id='molenat02_fulltext' AND endpoint='any_vge'
        """).fetchone() == (7, 14)
        assert db.execute("""
            SELECT numerator,denominator,endpoint FROM publication_observation
            WHERE source_id='lim83_rsaf'
        """).fetchall() == [(1, None, "suspected_dcs")]
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_cadet_release_preserves_printed_rates_and_disjoint_source_groups(tmp_path):
    target = tmp_path / "cadet.sqlite"
    assert build(target, cadet_supplement=True) == build(target, cadet_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT reported_percent,denominator,analysis_role FROM publication_reported_rate
            WHERE source_id='motley45' AND stratum LIKE 'training_group_%'
                AND endpoint='bends_any_grade' ORDER BY stratum
        """).fetchall() == [
            ("27.4", 7664, "overlap_hold"),
            ("13.4", 46683, "overlap_hold"),
            ("10.6", 4337, "overlap_hold"),
            ("7.3", 9738, "overlap_hold"),
        ]
        assert db.execute("""
            SELECT denominator,reported_percent FROM publication_reported_rate
            WHERE source_id='smedal46' AND stratum IN ('30000_exercise_room','30000_rest_room')
                AND endpoint='bends_pain_requiring_descent' ORDER BY stratum
        """).fetchall() == [(122, "11.5"), (92, "0")]
        assert db.execute("""
            SELECT denominator,reported_percent FROM publication_reported_rate
            WHERE source_id='gray_masland46' AND target_altitude_ft=23000
                AND endpoint='bends_any_severity' ORDER BY denominator
        """).fetchall() == [(117, "7.7"), (195, "12.8")]
        assert db.execute("""
            SELECT count(*) FROM publication_reported_rate
            WHERE source_id='gray_mahady46' AND denominator=180
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='motley45'
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id='smedal48_review' AND stratum='pensacola_cold_chamber_30000'
        """).fetchone() == (93, 753, "person")
        assert db.execute("""
            SELECT disposition FROM publication_source WHERE source_id='smedal48_review'
        """).fetchone() == ("extracted",)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_database_build_is_idempotent_and_preserves_other_files(tmp_path):
    target = tmp_path / "out.sqlite"
    assert build(target) == build(target)
    other = tmp_path / "other"
    other.write_bytes(b"existing research file")
    with pytest.raises(FileExistsError):
        build(other)
    assert other.read_bytes() == b"existing research file"


def test_consecutive_registry_revisions_and_missing_followup(tmp_path):
    dbfile = tmp_path / "private.sqlite"
    initialize(dbfile)
    entry = dict(
        schema_version="fac-chamber/1",
        participant_id="P1",
        exposure_id="E1",
        chamber_session_id="S1",
        protocol_id="research",
        protocol_version="draft",
        revision=1,
        revision_reason="synthetic first entry",
        start_utc="2026-01-01T12:00:00Z",
        recorded_at_utc="2026-01-01T12:00:00Z",
        source_reference="fixture",
        source_version="v1",
        source_sha256=hashlib.sha256(b"fixture").hexdigest(),
        extraction_method="synthetic test",
    )
    planned = json.loads((ROOT / "docs/examples/aviation-table5.json").read_bytes())
    planned["prediction_request"]["prediction_origin"] = "profile_start"
    entry.update(planned=planned, planned_as_of_utc="2026-01-01T11:00:00Z")

    def enc(doc):
        return json.dumps(doc).encode()

    assert append(dbfile, enc(entry)) == "recorded"
    assert append(dbfile, enc(entry)) == "already_recorded"
    with closing(sqlite3.connect(dbfile)) as db:
        assert db.execute("SELECT count(*) FROM clinical_followup").fetchone() == (0,)
    actual = deepcopy(planned)
    del actual["prediction_request"]
    for seg in actual["segments"]:
        seg["timing_basis"] = "observed"
    observation = dict(
        endpoint="dcs",
        status="no_event_observed",
        certainty="confirmed",
        definition_version="example",
        followup_through_min=400.0,
        event_free_through_min=400.0,
        censor_min=400.0,
        ascertainment="scheduled interview",
        source_reference="fixture",
    )
    later = {
        **entry,
        "revision": 2,
        "revision_reason": "actual history and first follow-up",
        "recorded_at_utc": "2026-01-02T12:00:00Z",
        "actual": actual,
        "clinical": [observation],
        "segments": [
            dict(
                history="actual",
                segment_id=actual["segments"][0]["id"],
                mask_state="on",
                gas_basis="documented",
                workload_basis="unknown",
                source_reference="fixture",
            )
        ],
    }
    with pytest.raises(ValueError, match="event-free coverage"):
        append(
            dbfile, enc({**later, "clinical": [{**observation, "event_free_through_min": None}]})
        )
    with pytest.raises(ValueError, match="forecast is frozen"):
        append(dbfile, enc({**later, "planned": None, "planned_as_of_utc": None}))
    late_evidence = {
        **later["segments"][0],
        "history": "planned",
        "available_at_utc": later["recorded_at_utc"],
    }
    with pytest.raises(ValueError, match="available by the forecast"):
        append(dbfile, enc({**later, "segments": [late_evidence]}))
    assert append(dbfile, enc(later)) == "recorded"
    with pytest.raises(ValueError, match="conflicting"):
        append(dbfile, enc({**later, "revision_reason": "different snapshot at revision 2"}))
    with pytest.raises(FileExistsError):
        initialize(dbfile)
    with closing(sqlite3.connect(dbfile)) as db:
        assert db.execute("SELECT count(*) FROM snapshot").fetchone() == (2,)
        assert db.execute("SELECT count(*) FROM current_exposure").fetchone() == (1,)
        assert db.execute("SELECT count(*) FROM doppler_observation").fetchone() == (0,)
        assert db.execute(
            "SELECT json_extract(observation,'$.event_free_through_min') FROM clinical_followup"
        ).fetchone() == (400.0,)
