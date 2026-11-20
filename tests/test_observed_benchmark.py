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


def test_nasa_case_supplement_preserves_distinct_cases_and_timing(tmp_path):
    target = tmp_path / "cases.sqlite"
    build(target, chamber_nasa_cases_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        cases = db.execute(
            "SELECT published_case_number, endpoint FROM literature_case_index "
            "WHERE source_id='nasa03' ORDER BY published_case_number"
        ).fetchall()
        type_ii_cases = {26, 52, 53, 65, 77, 95}
        assert cases == [
            (
                number,
                "dcs_type_ii_historical" if number in type_ii_cases else "dcs_type_i_historical",
            )
            for number in range(1, 104)
        ]
        assert db.execute(
            "SELECT published_case_number, dcs_time_as_published, dcs_time_min, dcs_time_basis "
            "FROM literature_case_table_i WHERE published_case_number IN (11, 19, 22, 76) "
            "ORDER BY published_case_number"
        ).fetchall() == [
            (11, "166+", 166, "recalled_at_debrief"),
            (19, "---", None, "onset_unavailable"),
            (22, "206#", 206, "noticed_before_in_test_report"),
            (76, "---", None, "onset_unavailable"),
        ]
        assert db.execute(
            "SELECT published_case_number, endpoint, narrative_time_min, interpretation "
            "FROM literature_case_timing_review ORDER BY published_case_number"
        ).fetchall() == [
            (30, "dcs", 68, "narrative_preferred"),
            (34, "dcs", 180, "different_symptom"),
            (37, "vge", 133, "narrative_preferred"),
            (90, "dcs", 110, "narrative_preferred"),
        ]
        assert db.execute(
            "SELECT endpoint, numerator, denominator, analysis_role FROM publication_observation "
            "WHERE source_id='balldin77_negative_pressure' AND stratum='negative-pressure-oxygen' "
            "ORDER BY endpoint"
        ).fetchall() == [
            ("dcs_bends_source", 3, 5, "overlap_hold"),
            ("questionable_bends_source", 1, 5, "overlap_hold"),
            ("vge_any", 3, 5, "overlap_hold"),
        ]
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_paired_chamber_exposures_reproduce_source_counts(tmp_path):
    target = tmp_path / "paired.sqlite"
    build(target, chamber_paired_exposures_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        for horizon, expected in (
            (15, [(None, 5, 0, 0, 0), (12, 10, 3, 6, 3), (18, 10, 1, 4, 0), (24, 10, 0, 0, 0)]),
            (60, [(None, 5, 0, 2, 0), (12, 10, 4, 7, 4), (18, 10, 5, 8, 5), (24, 10, 2, 7, 4)]),
        ):
            assert (
                db.execute(
                    "SELECT surface_interval_h, count(*), "
                    "sum(clinical_status='confirmed' AND symptom_onset_upper_min <= ?), "
                    "sum(coalesce(grade1_min <= ?,0)), sum(coalesce(grade4_min <= ?,0)) "
                    "FROM publication_postdive_exposure WHERE source_id='balldin78_postdive' "
                    "GROUP BY surface_interval_h ORDER BY surface_interval_h",
                    (horizon, horizon, horizon),
                ).fetchall()
                == expected
            )
        assert db.execute(
            "SELECT altitude_m, count(*), count(grade1_min), count(grade2_min), count(grade3_min), "
            "sum(clinical_status='questionable') FROM publication_postdive_exposure "
            "WHERE source_id='balldin80_postdive' GROUP BY altitude_m ORDER BY altitude_m"
        ).fetchall() == [(1000, 4, 2, 2, 0, 1), (2000, 7, 6, 4, 2, 1), (3000, 20, 12, 7, 2, 0)]
        assert db.execute(
            "SELECT protocol, count(*), "
            "sum(max(peak_eb_grade_rest,peak_eb_grade_knee_flex,peak_eb_grade_arm_flex)>0) "
            "FROM publication_vge_peak WHERE source_id='gottschalk24_region' "
            "GROUP BY protocol ORDER BY protocol"
        ).fetchall() == [("ECCu", 11, 8), ("ECCw", 11, 7), ("control", 11, 4)]
        assert db.execute(
            "SELECT count(*) FROM publication_postdive_exposure "
            "WHERE source_id='balldin78_chokes' OR source_id='gottschalk24_region'"
        ).fetchone() == (0,)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_staged_exposures_keep_source_conflicts_and_stage_risk_sets(tmp_path):
    target = tmp_path / "stages.sqlite"
    build(target, chamber_staged_exposures_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute(
            "SELECT printed_table,count(*) FROM publication_staged_symptom "
            "WHERE source_id='edel69_interval' GROUP BY printed_table ORDER BY printed_table"
        ).fetchall() == [("III", 9), ("IV", 24), ("V", 8), ("VI", 6)]
        assert db.execute(
            "SELECT count(*),sum(later_phase_pain_grade) FROM publication_staged_symptom "
            "WHERE source_id='edel69_interval' AND printed_table='III' AND surface_interval_min=5"
        ).fetchone() == (5, 0)
        assert db.execute(
            "SELECT stratum,numerator,denominator,analysis_role FROM publication_observation "
            "WHERE source_id='edel69_interval' "
            "AND stratum IN ('work-40-5','working-deep-5-later') ORDER BY stratum"
        ).fetchall() == [
            ("work-40-5", 1, 6, "denominator_conflict"),
            ("working-deep-5-later", 1, 5, "overlap_hold"),
        ]
        assert db.execute(
            "SELECT count(*),sum(numerator),sum(denominator) FROM publication_observation "
            "WHERE source_id='edel70_nasa' AND endpoint='dcs_bends_source'"
        ).fetchone() == (11, 5, 48)
        assert db.execute(
            "SELECT stratum,numerator,denominator,altitude FROM publication_observation "
            "WHERE source_id='edel70_nasa' AND endpoint='dcs_bends_later_reported' ORDER BY stratum"
        ).fetchall() == [
            ("C-2-later", 2, None, None),
            ("C-3-later", 1, None, None),
            ("C-4-later", 1, None, None),
            ("C-5-later", 1, None, None),
        ]
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_treated_case_supplement_preserves_printed_scopes(tmp_path):
    target = tmp_path / "treated.sqlite"
    build(target, chamber_treated_case_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        for groups, total in (
            (("male", "female"), (429, 740505)),
            (("student", "physiology-trainer"), (429, 740710)),
        ):
            assert (
                db.execute(
                    "SELECT sum(numerator),sum(denominator) FROM publication_observation "
                    "WHERE source_id='weien90' AND endpoint='hbo_treated_chamber_dcs' "
                    "AND analysis_role='overlap_hold' AND stratum IN (?,?)",
                    groups,
                ).fetchone()
                == total
            )
        assert db.execute(
            "SELECT sum(numerator),min(denominator),max(denominator) "
            "FROM publication_observation WHERE source_id='weien90' "
            "AND endpoint='symptom_onset_among_hbo_treated_dcs'"
        ).fetchone() == (526, 526, 526)
        assert db.execute(
            "SELECT stratum,numerator,denominator FROM publication_observation "
            "WHERE source_id='wirjosemito89_typeii' AND stratum IN "
            "('extremity-numbness','extremity-weakness') ORDER BY stratum"
        ).fetchall() == [("extremity-numbness", 6, 133), ("extremity-weakness", 22, 133)]
        assert db.execute(
            "SELECT count(*) FROM publication_observation WHERE source_id='cialoni14_flight'"
        ).fetchone() == (0,)
        assert db.execute(
            "SELECT numerator,denominator FROM publication_observation "
            "WHERE source_id='cialoni15_flight' AND stratum='return-aircraft' "
            "AND endpoint='vge_any'"
        ).fetchone() == (8, 56)
        assert db.execute(
            "SELECT reported_percent,denominator FROM publication_reported_rate "
            "WHERE source_id='duffner60'"
        ).fetchone() == ("55", 18)
        assert db.execute(
            "SELECT count(*) FROM publication_observation WHERE source_id='duffner60'"
        ).fetchone() == (0,)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_case_detail_supplement_keeps_missing_cells_and_paired_scopes(tmp_path):
    target = tmp_path / "details.sqlite"
    build(target, chamber_case_detail_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute(
            "SELECT count(*),sum(type_i_bcp),sum(type_i_no_bcp),sum(type_ii_bcp), "
            "sum(type_ii_no_bcp),count(type_i_no_bcp) FROM publication_menstrual_case_margin "
            "WHERE source_id='rudge90_menstrual'"
        ).fetchone() == (30, 17, 44, 5, 13, 29)
        assert db.execute(
            "SELECT sum(type_i_bcp)+sum(type_i_no_bcp),sum(type_ii_bcp)+sum(type_ii_no_bcp) "
            "FROM publication_menstrual_case_margin WHERE days_since_lmp_start BETWEEN 5 AND 9"
        ).fetchone() == (12, 4)
        assert db.execute(
            "SELECT days_since_lmp_start FROM publication_menstrual_case_margin "
            "WHERE type_i_no_bcp IS NULL"
        ).fetchall() == [(8,)]
        assert db.execute(
            "SELECT endpoint,sum(numerator) FROM publication_observation "
            "WHERE source_id='rudge90_menstrual' AND stratum LIKE 'lmp-%' "
            "GROUP BY endpoint ORDER BY endpoint"
        ).fetchall() == [
            ("type_i_case_day_distribution", 62),
            ("type_ii_case_day_distribution", 19),
        ]
        assert db.execute(
            "SELECT condition,count(*),count(post_exercise_peak_grade) "
            "FROM web_vge_exercise_peak WHERE source_id='eiken23' "
            "GROUP BY condition ORDER BY condition"
        ).fetchall() == [("H", 10, 9), ("N", 10, 10)]
        assert db.execute(
            "SELECT participant_number,condition,pre_exercise_peak_grade "
            "FROM web_vge_exercise_peak WHERE post_exercise_peak_grade IS NULL"
        ).fetchall() == [(10, "H", 4)]
        assert db.execute(
            "SELECT count(*) FROM citation_observation WHERE source_id='krause00'"
        ).fetchone() == (14,)
        assert db.execute(
            "SELECT access FROM citation_source WHERE source_id='krause00'"
        ).fetchone() == ("full_text",)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_threshold_supplement_preserves_source_grain(tmp_path):
    target = tmp_path / "threshold.sqlite"
    build(target, chamber_threshold_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute(
            "SELECT printed_row FROM publication_threshold_profile ORDER BY printed_row"
        ).fetchall() == [(i,) for i in range(1, 37)]
        assert db.execute(
            "SELECT exposure_count,symptom_count,reconciliation_status "
            "FROM publication_threshold_profile WHERE printed_row IN (1,5,17,33) "
            "ORDER BY printed_row"
        ).fetchall() == [
            (7, 0, "scope_discrepancy"),
            (31, 1, "counts_concordant"),
            (71, 12, "scope_discrepancy"),
            (65, 8, "scope_discrepancy"),
        ]
        assert db.execute(
            "SELECT source_id,numerator,denominator,denominator_unit,analysis_role "
            "FROM publication_observation WHERE source_id IN "
            "('kumar90','conkin87_tm100456','polaris_program_chamber',"
            "'kumar88_treadmill','polaris26_eva') ORDER BY source_id"
        ).fetchall() == [
            ("kumar88_treadmill", 1, None, None, "selected_cluster"),
            ("polaris26_eva", 0, 8, "person", "descriptive"),
        ]
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_bubble_outcomes_supplement_keeps_subset_and_case_scopes(tmp_path):
    target = tmp_path / "bubble-outcomes.sqlite"
    build(target, chamber_bubble_outcomes_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute(
            "SELECT source_id,stratum,endpoint,numerator,denominator,analysis_role "
            "FROM publication_observation WHERE source_id IN "
            "('smead86_suit83','webb88_blood_vge','studer15_chamber') ORDER BY source_id,stratum"
        ).fetchall() == [
            (
                "studer15_chamber",
                "rapid-decompression-training",
                "dcs_type_ii_presumptive_source",
                1,
                None,
                "selected_cluster",
            ),
            ("webb88_blood_vge", "blood-subset-men", "vge_grade_3_or_4", 5, 20, "overlap_hold"),
            ("webb88_blood_vge", "blood-subset-women", "vge_grade_3_or_4", 3, 10, "overlap_hold"),
        ]
        assert db.execute(
            "SELECT endpoint,reported_percent,denominator,analysis_role "
            "FROM publication_reported_rate WHERE source_id='smead86_suit83'"
        ).fetchall() == [("significant_intravascular_bubbling", "25.8", 31, "overlapping_margin")]
        assert db.execute(
            "SELECT relationship FROM publication_overlap "
            "WHERE source_id='webb88_blood_vge' AND related_source='smead86_suit83'"
        ).fetchone() == ("partial_overlap",)


def test_diagnosis_supplement_keeps_report_and_rating_denominators(tmp_path):
    target = tmp_path / "diagnosis.sqlite"
    build(target, chamber_diagnosis_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute(
            "SELECT count(*),sum(reports),sum(original_dcs_labels),"
            "sum(outside_ratings),sum(outside_dcs_ratings) "
            "FROM publication_diagnostic_stratum WHERE source_id='conkin06_diagnostic'"
        ).fetchone() == (6, 135, 103, 675, 406)
        assert db.execute(
            "SELECT count(*),count(DISTINCT published_exposure_code),sum(peak_vge_grade=4) "
            "FROM literature_symptomatic_noncase WHERE source_id='nasa03'"
        ).fetchone() == (32, 32, 11)
        assert db.execute(
            "SELECT narrative_number,first_report_min,first_report_basis "
            "FROM literature_symptomatic_noncase WHERE first_report_basis<>'test_elapsed' "
            "ORDER BY narrative_number"
        ).fetchall() == [
            (1, None, "after_test"),
            (7, 30, "after_test"),
            (24, 350, "after_test"),
            (27, None, "before_target_ascent"),
        ]
        assert db.execute(
            "SELECT stratum,numerator,denominator,analysis_role FROM publication_observation "
            "WHERE source_id='conkin06_diagnostic'"
        ).fetchall() == [("trial-n", 7, 48, "overlap_hold")]


def test_vge_reconciliation_supplement_preserves_printed_conflicts(tmp_path):
    target = tmp_path / "vge-reconciliation.sqlite"
    build(target, chamber_vge_reconciliation_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute(
            "SELECT earlier_cases,reconciled_cases,denominator "
            "FROM literature_observation_count_revision "
            "WHERE source_id='waligora87' AND endpoint='any_vge'"
        ).fetchall() == [(18, 11, 38)]
        assert db.execute(
            "SELECT stratum,cases,denominator,analysis_role FROM literature_observation "
            "WHERE source_id='waligora87' AND endpoint='any_vge' ORDER BY stratum"
        ).fetchall() == [
            ("360min-prebreathe", 11, 38, "overlap_hold"),
            ("480min-prebreathe", 0, 8, "overlap_hold"),
        ]
        assert db.execute(
            "SELECT numerator,denominator,analysis_role FROM publication_observation "
            "WHERE source_id='kumar93_cmb' AND stratum='peak_grade_iv'"
        ).fetchone() == (20, 31, "denominator_conflict")
        assert db.execute(
            "SELECT endpoint,numerator,denominator FROM publication_observation "
            "WHERE source_id IN ('skedina98_ru','skedina98_acta')"
        ).fetchall() == [("vge_grade_3_or_4", 24, 32)]


def test_repeated_eva_supplement_keeps_participant_and_exposure_scopes(tmp_path):
    target = tmp_path / "repeated-eva.sqlite"
    build(target, chamber_repeated_eva_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute(
            "SELECT stratum,endpoint,numerator,denominator,denominator_unit,analysis_role "
            "FROM publication_observation WHERE source_id='ryabtsev96_repeat' ORDER BY stratum"
        ).fetchall() == [
            (
                "series-3-exposures",
                "suspected_dcs_source",
                1,
                540,
                "person_exposure",
                "descriptive",
            ),
            (
                "series-3-participants",
                "suspected_dcs_source",
                1,
                18,
                "person",
                "overlapping_margin",
            ),
        ]
        assert db.execute(
            "SELECT count(*) FROM publication_observation "
            "WHERE source_id IN ('kazakova78_oxygen_envelope','ryabtsev91_repeat_lead')"
        ).fetchone() == (0,)
        assert db.execute(
            "SELECT count(*) FROM publication_source WHERE identifier='Medical-diss:564651'"
        ).fetchone() == (1,)


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


def test_raf_release_preserves_distinct_analyses_and_staged_arm_denominators(tmp_path):
    target = tmp_path / "raf.sqlite"
    assert build(target, raf_supplement=True) == build(target, raf_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator,denominator_unit
            FROM publication_observation WHERE source_id='fryer69_raf'
            AND endpoint='dcs_symptoms_source_defined'
            AND stratum IN ('selection_exposures','selection_people') ORDER BY stratum
        """).fetchall() == [
            ("selection_exposures", 165, 4956, "person_exposure"),
            ("selection_people", 141, 2606, "person"),
        ]
        assert db.execute("""
            SELECT sum(numerator),sum(denominator),count(*)
            FROM publication_observation WHERE source_id='fryer69_raf'
            AND stratum LIKE 'selection_age_%_first_runs' AND analysis_role='denominator_conflict'
        """).fetchone() == (96, 2635, 6)
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='fryer69_raf' AND stratum='selection_cluster_analysis'
        """).fetchone() == (164, None)
        assert db.execute("""
            SELECT endpoint,numerator,denominator,altitude FROM publication_observation
            WHERE source_id='fryer69_raf' AND stratum='rapid_decompression_training'
            ORDER BY endpoint
        """).fetchall() == [
            ("bends", 1, 7685, None),
            ("formication", 1, 7685, None),
            ("unspecified_pain_pressure_breathing", 2, 7685, None),
        ]
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='fryer69_raf' AND endpoint='dcs_forced_descent' ORDER BY stratum
        """).fetchall() == [(9, 30), (6, 10), (3, 40), (10, 39)]
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_clinical_series_release_holds_overlaps_and_uncertain_denominators(tmp_path):
    target = tmp_path / "clinical-series.sqlite"
    assert build(target, clinical_series_supplement=True) == build(
        target, clinical_series_supplement=True
    )
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT endpoint,numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='nasa_pfo24' AND stratum='altitude_refresher_since_2015'
            ORDER BY endpoint
        """).fetchall() == [
            ("dcs_all_types", 12, 1650, "overlapping_margin"),
            ("dcs_type_i_source", 6, 1650, "overlap_hold"),
            ("dcs_type_ii_source", 6, 1650, "overlap_hold"),
        ]
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id='nasa_pfo24' AND stratum='research_and_hardware_development'
            ORDER BY numerator
        """).fetchall() == [(1, None, None), (3, None, None)]
        assert db.execute("""
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE source_id='balldin02_posture' ORDER BY endpoint
        """).fetchall() == [
            ("prospective_adynamia", 20, 39),
            ("prospective_adynamia", 17, 39),
            ("prospective_adynamia", 13, 39),
        ]
        assert db.execute("""
            SELECT numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='skedina97' AND stratum='pooled_simulated_eva' ORDER BY numerator
        """).fetchall() == [(7, 32, "denominator_conflict"), (27, 32, "denominator_conflict")]
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='nasa_pfo26'
        """).fetchone() == (0,)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_crossover_release_retains_paired_counts_and_denominator_conflict(tmp_path):
    target = tmp_path / "crossover.sqlite"
    assert build(target, crossover_supplement=True) == build(target, crossover_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT altitude,numerator,denominator FROM publication_observation
            WHERE source_id='lupa05' AND endpoint='dcs_signs_or_symptoms_source'
            ORDER BY altitude
        """).fetchall() == [(17500, 0, 10), (35000, 0, 10)]
        assert db.execute("""
            SELECT stratum,numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='balldin73_immersion' AND stratum LIKE 'dry_%' ORDER BY stratum
        """).fetchall() == [
            ("dry_nitrogen_loaded", 3, 3, "selected_cluster"),
            ("dry_published_total", 9, 10, "overlapping_margin"),
            ("dry_standard", 6, 7, "descriptive"),
        ]
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='lee_hay01' AND analysis_role='denominator_conflict'
        """).fetchall() == [(6, 115)]
        assert db.execute("""
            SELECT count(*),sum(numerator),sum(denominator) FROM publication_observation
            WHERE source_id='lee_hay01' AND endpoint='dci_symptoms_recompression'
        """).fetchone() == (7, 33, 105)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_historical_chamber_release_keeps_courses_distinct_from_experiments(tmp_path):
    target = tmp_path / "historical-chamber.sqlite"
    assert build(target, historic_chamber_supplement=True) == build(
        target, historic_chamber_supplement=True
    )
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT grouping,sum(course_count),sum(category_a),sum(category_b),sum(category_c)
            FROM publication_selection_course WHERE source_id='kenyon72_hast'
            GROUP BY grouping ORDER BY grouping
        """).fetchall() == [(group, 2565, 1667, 764, 134) for group in ("role", "total", "year")]
        assert db.execute("""
            SELECT course_count,category_b+category_c FROM publication_selection_course
            WHERE source_id='kenyon72_hast' AND stratum='year_1957'
        """).fetchone() == (174, 70)
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='kenyon72_hast'
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT stratum,numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='genin80' AND endpoint='hds_source'
                AND stratum IN ('suited_03','suited_09','unsuited_7') ORDER BY stratum
        """).fetchall() == [
            ("suited_03", 0, 10, "denominator_conflict"),
            ("suited_09", 0, 60, "overlap_hold"),
            ("unsuited_7", 14, None, "denominator_conflict"),
        ]
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_spaceflight_release_reconciles_original_denominator_and_air_breaks(tmp_path):
    target = tmp_path / "spaceflight.sqlite"
    assert build(target, spaceflight_supplement=True) == build(target, spaceflight_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='cooke74' AND stratum='oxygen-30-min' AND endpoint='dcs_symptoms'
        """).fetchall() == [(6, 22)]
        assert db.execute("""
            SELECT previous_denominator,denominator,evidence_source_id
            FROM publication_observation_revision WHERE stratum='oxygen-30-min'
        """).fetchone() == (20, 22, "cooke74_primary")
        assert db.execute("""
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE source_id='cooke76_airbreak' AND analysis_role='descriptive' ORDER BY stratum
        """).fetchall() == [
            ("flight_type_1", 0, 17),
            ("flight_type_2", 2, 10),
            ("flight_type_3", 1, 11),
            ("flight_type_4", 1, 10),
            ("flight_type_5", 1, 13),
            ("flight_type_6", 1, 12),
            ("flight_type_7", 1, 15),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_observation
            WHERE source_id IN ('cooke75_air_tech','damato63_journal')
        """).fetchone() == (0,)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_denitrogenation_release_keeps_source_rates_and_conflicting_counts(tmp_path):
    target = tmp_path / "denitrogenation.sqlite"
    build(target, denitrogenation_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT count(*),sum(denominator) FROM publication_reported_rate
            WHERE source_id='allen71_body_fat' AND analysis_role='overlap_hold'
        """).fetchone() == (26, 883)
        assert db.execute("""
            SELECT reported_percent,denominator FROM publication_reported_rate
            WHERE source_id='allen71_body_fat' AND stratum='27k-o2-0-lt12'
        """).fetchone() == ("8.4", 12)
        assert db.execute("""
            SELECT numerator,denominator,prebreathe_min FROM publication_observation
            WHERE source_id='allen71_body_fat' AND analysis_role='denominator_conflict'
            ORDER BY denominator
        """).fetchall() == [(1, 130, None), (5, 383, None)]
        assert db.execute("""
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE source_id='waligora84_shuttle' AND endpoint='dcs_symptoms'
        """).fetchall() == [("series2-oxygen-210", 7, 22)]
        assert db.execute("""
            SELECT relationship FROM publication_overlap
            WHERE source_id='waligora84_shuttle' AND related_source='gerth18'
        """).fetchone() == ("same_cohort",)
        assert db.execute("""
            SELECT dcs_cases,dcs_denominator FROM nasa_test WHERE test_id='2a'
        """).fetchone() == (7, 23)
        assert db.execute("""
            SELECT exact_cases,exposures FROM a1309_profile WHERE profile LIKE 'Test 2a; %'
        """).fetchone() == (7, 23)
        assert db.execute("""
            SELECT stratum,numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='waligora84_shuttle' AND endpoint='any_vge_source'
        """).fetchall() == [("series2-oxygen-210", 14, 22, "denominator_conflict")]
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id='cherniakov76_repeat' AND analysis_role='overlap_hold'
        """).fetchone() == (0, 6, "person")
        assert db.execute("""
            SELECT stratum,numerator,denominator,analysis_role
            FROM publication_observation
            WHERE source_id='taubman06_fab' AND stratum IN ('all-flight-profiles','helicopter')
                AND endpoint='any_self_reported_chamber_symptom'
            ORDER BY stratum
        """).fetchall() == [
            ("all-flight-profiles", 223, 848, "descriptive"),
            ("helicopter", 23, 106, "denominator_conflict"),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_observation
            WHERE source_id='taubman06_fab' AND endpoint NOT LIKE '%self_reported%'
        """).fetchone() == (0,)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_international_release_preserves_outcome_units_and_links_existing_case(tmp_path):
    target = tmp_path / "international.sqlite"
    build(target, international_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit,altitude,altitude_unit
            FROM publication_observation WHERE source_id='peng16_eva_chamber'
        """).fetchall() == [(0, 17, "person", 7200.0, "m")]
        assert db.execute("""
            SELECT endpoint,numerator,denominator,denominator_unit,analysis_role
            FROM publication_observation WHERE source_id='lee21_taiwan_training'
            ORDER BY endpoint
        """).fetchall() == [
            ("training_interruption_any_cause", 572, None, None, "denominator_conflict"),
            ("training_noncompletion_any_cause", 57, 18487, "trainee_exposure", "descriptive"),
        ]
        assert db.execute("""
            SELECT numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='kutz23_chamber_referral'
        """).fetchall() == [(1, None, "selected_cluster")]
        assert db.execute("""
            SELECT related_source,relationship FROM publication_overlap
            WHERE source_id IN ('gibbons03_rapid_ascent','ho88_taiwan_survey','tong19_taiwan_training')
            ORDER BY source_id
        """).fetchall() == [
            ("pilmanis03", "partial_overlap"),
            ("wen88_taiwan_survey", "likely_overlap"),
            ("lee21_taiwan_training", "same_cohort"),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_observation
            WHERE source_id IN (
                'gibbons03_rapid_ascent','ho88_taiwan_survey','wen88_taiwan_survey',
                'tong19_taiwan_training'
            )
        """).fetchone() == (0,)
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_archival_release_keeps_distinct_followup_and_stage_risk_sets(tmp_path):
    target = tmp_path / "archival.sqlite"
    build(target, archival_trial_supplement=True)
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE source_id='bridge44_38000'
                AND endpoint='postflight_symptoms_in_joints_affected_at_altitude'
            ORDER BY stratum
        """).fetchall() == [
            ("postflight-respondents", 19, 120),
            ("respondents-with-altitude-joint-pain", 19, 74),
        ]
        assert db.execute("""
            SELECT endpoint,numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id='cheetham47_lyttelton'
                AND endpoint IN ('joint_symptoms_source','people_with_joint_symptoms_source')
            ORDER BY endpoint
        """).fetchall() == [
            ("joint_symptoms_source", 16, 83, "person_exposure"),
            ("people_with_joint_symptoms_source", 11, 28, "person"),
        ]
        assert db.execute("""
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE source_id='allen_beard69_2h' AND stratum LIKE '293-mixed-%' ORDER BY stratum
        """).fetchall() == [("293-mixed-cabin", 18, 36), ("293-mixed-suit", 10, 22)]
        assert db.execute("""
            SELECT source_id,access,disposition FROM publication_source
            WHERE source_id IN ('allen_beard69_2h','meade67') ORDER BY source_id
        """).fetchall() == [
            ("allen_beard69_2h", "full_text", "extracted"),
            ("meade67", "full_text", "extracted"),
        ]
        assert db.execute("""
            SELECT related_source,relationship FROM publication_overlap
            WHERE source_id='allen71_body_fat'
                AND related_source IN ('allen_beard69_2h','mciver67_eva')
            ORDER BY related_source
        """).fetchall() == [
            ("allen_beard69_2h", "partial_overlap"),
            ("mciver67_eva", "partial_overlap"),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='mciver66_case_series'
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT numerator,denominator,analysis_role
            FROM publication_observation WHERE source_id='meade67'
        """).fetchall() == [(36, 958, "selected_cluster")]
        assert db.execute("SELECT count(*) FROM locked_external").fetchone() == (5,)


def test_reconciliation_release_keeps_one_houston_cohort(tmp_path):
    output = tmp_path / "reconciled.sqlite"
    build(output, chamber_reconciliation_supplement=True)

    with closing(sqlite3.connect(output)) as db:
        assert db.execute("""
            SELECT source_id, endpoint, numerator, denominator
            FROM publication_observation
            WHERE source_id IN ('houston46_navy', 'houston47_low_altitude')
            ORDER BY source_id, endpoint
        """).fetchall() == [
            ("houston46_navy", "aeroembolism_symptomatic_person_source", 6, 20),
            ("houston46_navy", "persistent_unilateral_temporal_blindness_source", 2, 20),
            ("houston46_navy", "scotoma_person_source", 3, 20),
            ("houston47_low_altitude", "incapacitating_bends_source", 2, 20),
        ]
        assert db.execute("""
            SELECT numerator, denominator, retained_source_id
            FROM publication_observation_superseded
            WHERE source_id = 'houston47_low_altitude'
            ORDER BY stratum
        """).fetchall() == [
            (6, 20, "houston46_navy"),
            (3, 20, "houston46_navy"),
            (2, 3, "houston46_navy"),
        ]
        assert db.execute("""
            SELECT relationship
            FROM publication_overlap
            WHERE source_id = 'houston46_navy' AND related_source = 'houston47_low_altitude'
        """).fetchone() == ("same_cohort",)


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
