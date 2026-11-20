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
        """).fetchone() == (106, 106, 106)
        assert db.execute("""
            SELECT source_id,onset_min,first_assessment_min,recurrence_report_day,recurrence_free_followup_min
            FROM shared_case_evidence
            WHERE source_id IN ('case17_delayed','yoneda98_skin_bends') ORDER BY source_id
        """).fetchall() == [
            ("case17_delayed", 180, 2880, 14, None),
            ("yoneda98_skin_bends", None, None, None, 1440),
        ]
        assert db.execute("""
            SELECT dcs_time_min,preferred_dcs_time_min FROM dcs_case WHERE published_case_number=30
        """).fetchone() == (86, 68)
        assert db.execute("SELECT count(*) FROM dcs_case").fetchone() == (103,)
        assert db.execute("SELECT count(*) FROM literature_symptomatic_noncase").fetchone() == (32,)
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id),min(report_id)
            FROM review.review_record WHERE lower(title) LIKE 'investigation of a cluster of decompression%'
        """).fetchone() == (125, 1, "doi:10.28920/dhm51.1.82-85")
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


def test_u2_care_abstract_versions_share_one_descriptive_report(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT count(*), count(DISTINCT report_id), sum(
                json_extract(metadata_json,'$.version')='published_meeting_abstract'
            )
            FROM review.review_record WHERE report_id='asma:2026:220'
        """).fetchone() == (2, 1, 1)
        assert db.execute("""
            SELECT observation_id, cases, denominator, denominator_unit, reported_rate,
                   reported_rate_unit
            FROM review.review_search_observation WHERE report_id='asma:2026:220'
            ORDER BY observation_id
        """).fetchall() == [
            ("u2-care-modified-per-flight", 3, None, "flights", 0.0088, "percent per flight"),
            ("u2-care-modified-per-flight-hour", None, None, "flight hours",
             0.1897, "cases per 10,000 flight hours"),
            ("u2-care-modified-severe-subset", 1, None, None, None, None),
            ("u2-unmodified-per-flight", None, None, "flights", 0.018, "percent per flight"),
        ]
        assert db.execute("""
            SELECT right_report, relationship FROM review.review_report_relation
            WHERE left_report='asma:2026:220'
        """).fetchall() == [("pmid:23066619", "historical_comparator")]
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence
            WHERE report_id='asma:2026:220'
        """).fetchone() == (0,)


def test_armstrong_archive_preserves_two_reports_and_one_incidence_count(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT l.report_id,p.numerator,p.denominator,p.analysis_role
            FROM publication_observation p JOIN model_report_link l USING(source_id)
            JOIN review.review_study_report s USING(report_id)
            WHERE s.study_id='armstrong-demboski-1983-1993' AND p.endpoint='dcs'
        """).fetchall() == [("ntrs:19940029137", 309, 1163, "overlap_hold")]
        assert db.execute("""
            SELECT count(*) FROM review.review_study_report
            WHERE study_id='armstrong-demboski-1983-1993'
        """).fetchone() == (2,)
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='demboski94_soar' AND endpoint='symptom_recurrence_source'
        """).fetchone() == (2, 261)
        assert db.execute("""
            SELECT reported_percent FROM publication_reported_rate
            WHERE source_id IN ('demboski94_soar','demboski94_asma91')
            ORDER BY reported_percent
        """).fetchall() == [("98.5",), ("99.2",), ("99.23",)]


def test_jprs_translation_reconciles_exposure_and_symptomatic_rows_once(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT p.stratum,p.numerator,p.denominator,p.prebreathe_min,count(t.reported_row)
            FROM publication_observation p JOIN model_report_link l USING(source_id)
            JOIN review.review_study_report s USING(report_id)
            LEFT JOIN publication_chamber_reported_onset t USING(source_id,stratum,endpoint)
            WHERE s.study_id='ussr-kazakova-poleshchuk-11000m' AND p.analysis_role='descriptive'
            GROUP BY p.source_id,p.stratum,p.endpoint ORDER BY p.stratum
        """).fetchall() == [
            ("control-5h", 4, 6, 300, 4),
            ("control-6h", 9, 15, 360, 9),
            ("control-8h", 1, 2, 480, 1),
            ("suit-5-or-6h", 8, 11, None, 8),
            ("suit-8h", 3, 4, 480, 3),
        ]
        assert db.execute("""
            SELECT p.stratum,p.numerator,p.denominator
            FROM publication_observation p JOIN model_report_link l USING(source_id)
            JOIN review.review_study_report s USING(report_id)
            WHERE s.study_id='ussr-kazakova-poleshchuk-11000m' AND p.analysis_role='overlapping_margin'
            ORDER BY p.stratum
        """).fetchall() == [("control-total", 14, 23), ("suit-total", 11, 15)]
        assert db.execute("""
            SELECT count(*) FROM review.review_study_report
            WHERE study_id='ussr-kazakova-poleshchuk-11000m'
        """).fetchone() == (2,)


def test_usafsam_archive_keeps_profile_conflicts_and_one_staging_case(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator,analysis_role
            FROM publication_observation
            WHERE source_id='webb10_usafsam_database' ORDER BY stratum
        """).fetchall() == [
            ("archive-completed-exposures", 1190, 2946, "overlap_hold"),
            ("archive-person-margin", 356, 573, "overlapping_margin"),
        ]
        assert db.execute("""
            SELECT count(*),sum(printed_subject_n),count(nedu_profile),
                   sum(printed_subject_n != p.exposures)
            FROM publication_adrac_profile_inventory i
            LEFT JOIN a1309_profile p ON i.nedu_profile=p.profile
        """).fetchone() == (41, 1013, 29, 7)
        assert db.execute("""
            SELECT s.reported_dcs_pct,s.reported_exposures,p.exact_cases,p.exposures
            FROM publication_archive_protocol_summary s JOIN a1309_profile p
            ON p.profile=s.candidate_nedu_profile WHERE s.stratum='16500ft'
        """).fetchall() == [(0.0, 94, 1, 94)]
        assert db.execute("""
            SELECT count(*),sum(reported_exposures IS NULL)
            FROM publication_archive_protocol_summary
        """).fetchone() == (24, 12)
        assert db.execute("""
            SELECT o.cases,o.denominator,a.stage_altitude_ft,a.onset_min_since_stage_arrival
            FROM literature_observation o JOIN literature_observation_case_annotation a
            USING(source_id,stratum,endpoint)
        """).fetchall() == [(1, 173, 18000, 105)]


def test_brooks_joint_tables_and_validation_versions_reuse_their_cohorts(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT vge_definition,dcs_with_vge,no_dcs_with_vge,dcs_without_vge,no_dcs_without_vge,
                   o.numerator,o.denominator
            FROM publication_joint_dcs_vge j JOIN publication_observation o
            ON (j.source_id,j.stratum,j.clinical_endpoint)=(o.source_id,o.stratum,o.endpoint)
            ORDER BY vge_definition
        """).fetchall() == [
            ("any_vge", 809, 575, 225, 468, 1034, 2077),
            ("grade_iv_vge", 471, 268, 563, 775, 1034, 2077),
        ]
        assert db.execute("""
            SELECT stratum,numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='kannan98_loglogistic' ORDER BY stratum
        """).fetchall() == [
            ("231mmhg-mild-135min", 49, 115, "overlapping_margin"),
            ("231mmhg-mild-75min", 57, 102, "overlapping_margin"),
            ("all-model-exposures", 506, 975, "overlap_hold"),
        ]
        assert db.execute("""
            SELECT source_profile,nedu_profile,predicted_dcs_pct,reported_actual_dcs_pct
            FROM publication_validation_snapshot WHERE source_id='pilmanis99_adrac_development'
            ORDER BY source_profile
        """).fetchall() == [
            ("1", "MV-A", 93.0, 91.0), ("2", "MV-B", 62.0, 61.0),
            ("3", "MV-E", 52.0, 58.0), ("4", "MV-D", 17.0, 13.0),
            ("5", "MV-C", 38.0, 30.0),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='pilmanis99_adrac_development'
        """).fetchone() == (0,)


def test_kannan_report_records_margins_without_counting_the_journal_subset_twice(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT numerator,denominator,analysis_role
            FROM publication_observation WHERE source_id='kannan98_survival_report'
        """).fetchall() == [(518, 1426, "overlap_hold")]
        assert db.execute("""
            SELECT dimension,count(*),sum(cases),sum(right_censored)
            FROM publication_exposure_outcome_margin GROUP BY dimension ORDER BY dimension
        """).fetchall() == [
            ("exercise_code", 3, 518, 908),
            ("final_pressure_mmhg", 21, 518, 908),
            ("maximum_spencer_grade", 5, 516, 907),
            ("prebreathe_min", 7, 518, 908),
        ]
        assert db.execute("""
            SELECT sum(cases),sum(right_censored)
            FROM publication_exposure_outcome_margin
            WHERE dimension='final_pressure_mmhg' AND level<=314
        """).fetchone() == (506, 469)
        assert db.execute("""
            SELECT report_id,role FROM review.review_study_report
            WHERE study_id='usafsam-brooks-kannan-survival' ORDER BY report_id
        """).fetchall() == [
            ("pmid:9773897", "nested_analysis_subset"),
            ("report:ada338089", "original_full_text"),
        ]
        assert db.execute("""
            SELECT report_id FROM model_report_link
            WHERE source_table='publication_source' AND source_id='kannan98_survival_report'
        """).fetchall() == [("report:ada338089",)]


def test_adrac_proceedings_adds_reported_estimates_to_the_existing_cohort(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT nedu_profile,predicted_dcs_pct,reported_actual_dcs_pct,
                   reported_actual_dcs_plus_minus_pp
            FROM publication_validation_snapshot
            WHERE source_id='pilmanis01_adrac_proceedings' ORDER BY nedu_profile
        """).fetchall() == [
            ("MV-A", 94.0, 94.0, 9.0),
            ("MV-B", 62.0, 61.0, 17.0),
            ("MV-C", 38.0, 30.0, 16.0),
            ("MV-D", 17.0, 13.0, 12.0),
            ("MV-E", 50.0, 58.0, 17.0),
        ]
        assert db.execute("""
            SELECT related_source,relationship FROM publication_overlap
            WHERE source_id='pilmanis01_adrac_proceedings' ORDER BY related_source
        """).fetchall() == [
            ("adrac04", "same_cohort"), ("gerth18", "likely_overlap"),
            ("pilmanis99_adrac_development", "same_cohort"),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_observation
            WHERE source_id='pilmanis01_adrac_proceedings'
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT report_id FROM model_report_link WHERE source_id='pilmanis01_adrac_proceedings'
        """).fetchone() == ("report:adp011090",)
        assert db.execute("""
            SELECT report_id FROM review.review_study_report
            WHERE study_id='usafsam-adrac-five-profile-validation' ORDER BY report_id
        """).fetchall() == [
            ("abstract:asma-1999-krause-364",), ("abstract:asma-2000-pilmanis-272",),
            ("pmid:15460625",), ("report:ada397485",), ("report:adp011090",),
        ]


def test_berry_training_keeps_annual_reactors_distinct_from_case_conditioned_symptoms(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE source_id='berry58_training' AND endpoint='grade_iv_hospitalizing_reaction_source'
            ORDER BY stratum
        """).fetchall() == [("1950-1955-all-reported", 125, None), ("1956-annual-reported", 48, None)]
        assert db.execute("""
            SELECT r.stratum,count(*),min(r.denominator),max(r.denominator)
            FROM publication_reported_rate r
            WHERE r.source_id='berry58_training' AND r.stratum LIKE 'grade-iv-group-%'
            GROUP BY r.stratum ORDER BY r.stratum
        """).fetchall() == [
            ("grade-iv-group-1", 16, 65, 65), ("grade-iv-group-2", 10, 4, 4),
            ("grade-iv-group-3", 11, 4, 4), ("grade-iv-group-4", 8, 5, 5),
            ("grade-iv-group-5", 17, 47, 47),
        ]
        assert db.execute("""
            SELECT cases,denominator,reported_rate,reported_rate_unit FROM review.review_search_observation
            WHERE observation_id='usaf-1956-grade-iv-rate-and-count'
        """).fetchone() == (48, None, 110, "per 100000 trainees")
        assert db.execute("""
            SELECT related_source,relationship FROM publication_overlap
            WHERE source_id='berry57_stockholm' AND related_source='berry58_training'
        """).fetchone() == ("berry58_training", "same_cohort")
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='citation:korea-eom-1974-dysbarism' AND right_report='kiss:4019953'
        """).fetchone() == ("possible_overlap",)


def test_halbouty_chamber_case_links_two_reports_to_one_existing_observation(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT period,numerator,denominator FROM publication_observation
            WHERE source_id='berry59_king' AND stratum='case-01'
        """).fetchall() == [("1954-03-19", 1, None)]
        assert db.execute("""
            SELECT report_id FROM shared_case_evidence
            WHERE source_id='berry59_king' AND stratum='case-01' ORDER BY report_id
        """).fetchall() == [("pmid:13247522",), ("pmid:13625439",)]
        assert db.execute("""
            SELECT report_id,source_time_min FROM historical_case_catalog
            WHERE case_id='berry59_king:case-01'
        """).fetchall() == [("pmid:13247522", None)]
        assert db.execute("""
            SELECT relationship FROM publication_overlap
            WHERE source_id='halbouty55_collapse' AND related_source='berry59_king'
        """).fetchall() == [("partial_overlap",)]
        assert db.execute("""
            SELECT milestone,chamber_altitude_ft,elapsed,elapsed_unit,elapsed_reference
            FROM publication_case_milestone
            WHERE milestone IN ('abdominal_pain_reported','first_chamber_observed_signs')
            ORDER BY milestone
        """).fetchall() == [
            ("abdominal_pain_reported", 35000, None, None, None),
            ("first_chamber_observed_signs", 43000, 30.0, "seconds", "peak_arrival"),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_case_milestone
            WHERE source_id='berry59_king' AND stratum='case-01'
        """).fetchone() == (11,)


def test_nasa_ascent_compilation_reconciles_without_adding_clinical_counts(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT count(*),sum(person_exposures),count(DISTINCT reference_number)
            FROM publication_ascent_compilation WHERE analysis_role='overlap_hold'
        """).fetchone() == (150, 14123, 36)
        assert db.execute("""
            WITH totals AS (
                SELECT CASE WHEN exercise_cycles_per_hour IS NULL THEN 'rest' ELSE 'exercise' END AS activity,
                       CASE WHEN ground_denitrogenation_hours=0 THEN 'no' ELSE 'yes' END AS denitrogenation,
                       sum(person_exposures) AS reconstructed_exposures
                FROM publication_ascent_compilation GROUP BY 1,2
            )
            SELECT activity,denitrogenation,reconstructed_exposures,person_exposures
            FROM publication_ascent_compilation_total JOIN totals USING(activity,denitrogenation)
            ORDER BY activity,denitrogenation
        """).fetchall() == [
            ("exercise", "no", 5885, 5885), ("exercise", "yes", 1649, 1649),
            ("rest", "no", 5897, 5897), ("rest", "yes", 692, 692),
        ]
        assert db.execute("""
            SELECT person_exposures,symptom_pct,forced_descent_pct,reference_number
            FROM publication_ascent_compilation
            WHERE printed_page=58 AND row_on_page IN (37,38) ORDER BY row_on_page
        """).fetchall() == [(223, None, 33, 37), (204, None, 11, 36)]
        assert db.execute("""
            SELECT symptom_pct,forced_descent_pct FROM publication_ascent_compilation
            WHERE printed_page=56 AND altitude_ft=20000
        """).fetchone() == (None, 0)
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='kumar89_ascent'
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT count(*),min(report_id),max(report_id) FROM review.review_record
            WHERE lower(title) LIKE '%different rates of ascent%' OR title=url AND url LIKE '%19890012936%'
        """).fetchone() == (30, "ntrs:19890012936", "ntrs:19890012936")
        assert db.execute("""
            SELECT count(*) FROM review.review_report_relation
            WHERE left_report='ntrs:19890012936' AND relationship='cites_as_compilation_source'
        """).fetchone() == (26,)


def test_ascent_source_reconciliation_preserves_denominator_conflicts(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='dixon86_suit95' ORDER BY stratum
        """).fetchall() == [
            ("validation-all", 0, 30, "denominator_conflict"),
            ("validation-men", 4, 20, "overlap_hold"),
            ("validation-women", 0, 10, "overlap_hold"),
        ]
        assert db.execute("""
            SELECT stratum,numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='damato65_acel529' ORDER BY stratum
        """).fetchall() == [
            ("equilibration-phase", 4, None, "overlap_hold"),
            ("post-equilibration-phase", 1, None, "overlap_hold"),
        ]
        assert db.execute("""
            SELECT reference_number,related_source_id FROM publication_ascent_reference
            WHERE source_id='kumar89_ascent' AND reference_number IN (12,22) ORDER BY reference_number
        """).fetchall() == [(12, "bridge44_38000"), (22, "degner65_orbital")]
        assert db.execute("""
            SELECT source_id,report_id FROM model_report_link
            WHERE source_id IN ('dixon86_suit95','damato65_acel529') ORDER BY source_id
        """).fetchall() == [
            ("damato65_acel529", "report:naec-acel-529"),
            ("dixon86_suit95", "ntrs:19860063003"),
        ]


def test_historical_crossover_and_attendant_outcomes_keep_their_counting_units(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT count(*),count(DISTINCT participant_number),count(DISTINCT condition)
            FROM publication_crossover_run WHERE analysis_role='overlap_hold'
        """).fetchone() == (84, 21, 4)
        assert db.execute("""
            SELECT condition,sum(symptom_status='reported'),sum(symptom_status='unresolved'),
                   sum(forced_descent_status='reported')
            FROM publication_crossover_run GROUP BY condition ORDER BY condition
        """).fetchall() == [
            ("aminophyllin", 20, 0, 6), ("codeine_and_aspirin", 19, 0, 7),
            ("control", 19, 0, 10), ("demerol", 19, 1, 10),
        ]
        assert db.execute("""
            SELECT symptom_onset_min,forced_descent_min,maximum_symptom_grade,grade_annotation
            FROM publication_crossover_run WHERE participant_number=14 ORDER BY condition
        """).fetchall() == [(45, 56, 7, "ch"), (None, 37, 5, None), (20, 58, 2, None), (25, 25, 3, None)]
        assert db.execute("""
            SELECT endpoint,numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id='houston47_low_altitude' ORDER BY endpoint
        """).fetchall() == [("incapacitating_bends_source", 2, 20, "person")]
        assert db.execute("""
            SELECT count(*),min(retained_source_id) FROM publication_observation_superseded
            WHERE source_id='houston47_low_altitude'
        """).fetchone() == (3, "houston46_navy")
        assert db.execute("""
            SELECT report_id FROM model_report_link WHERE source_id IN ('houston47_low_altitude','williams46_drug_crossover')
            ORDER BY source_id
        """).fetchall() == [("pmid:20296024",), ("joam:17-6-602",)]


def test_henry_preselection_rates_preserve_printed_values_and_derived_controls(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_table, value_basis, count(*), count(validation_exposure_denominator)
            FROM publication_preselection_rate GROUP BY 1,2 ORDER BY 1,2
        """).fetchall() == [
            ("I", "reported_validation_rate", 48, 6),
            ("III", "calculated_control_rate", 27, 0),
            ("III", "reported_validation_rate", 27, 0),
            ("IV", "reported_validation_rate", 27, 0),
        ]
        assert db.execute("""
            SELECT validation_group, reported_pct, validation_exposure_denominator
            FROM publication_preselection_rate WHERE source_table='I'
              AND endpoint='total_symptoms' AND proportion_selected_pct=100
            ORDER BY validation_group
        """).fetchall() == [("isometric_v", 57.5, 33), ("isotonic_ii", 76.5, 34), ("mixed_exercise", 67.2, 67)]
        assert db.execute("""
            SELECT value_basis, reported_pct FROM publication_preselection_rate
            WHERE source_table='III' AND endpoint='forced_descents' AND proportion_selected_pct=100
            ORDER BY value_basis
        """).fetchall() == [("calculated_control_rate", 53.3), ("reported_validation_rate", 17.0)]
        assert db.execute("""
            SELECT report_id FROM model_report_link WHERE source_id='henry47_preselection'
        """).fetchone() == ("pmid:20251251",)
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='henry47_preselection'
        """).fetchone() == (0,)


def test_henry_cook_preserves_counting_units_and_links_reused_controls(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_table, count(*), count(source_value), count(reported_numerator)
            FROM publication_preoxygen_measure GROUP BY 1 ORDER BY 1
        """).fetchall() == [("I", 28, 28, 1), ("II", 21, 21, 0), ("III", 35, 34, 0)]
        assert db.execute("""
            SELECT m.source_value, m.reported_numerator, g.group_size, g.group_size_unit,
                   g.planned_window_min, g.oxygen_advance_vs_control_min
            FROM publication_preoxygen_measure m
            JOIN publication_preoxygen_group g USING (source_id, source_table, group_key)
            WHERE m.source_table='I' AND m.group_key='nominal_two_hours' AND m.measure='incapacitated'
        """).fetchone() == (23.0, 14, 61, "ascents", 110, 111)
        assert db.execute("""
            SELECT source_value FROM publication_preoxygen_measure
            WHERE source_table='III' AND group_key='four_hours'
            AND measure IN ('incapacitated','mean_incapacitation_occurrence') ORDER BY measure
        """).fetchall() == [(0.0,), (None,)]
        assert db.execute("""
            SELECT m.source_value, h.reported_pct FROM publication_preoxygen_measure m
            JOIN publication_preselection_rate h ON h.endpoint=CASE m.measure
                WHEN 'with_symptoms' THEN 'total_symptoms'
                WHEN 'with_grade_3_symptoms' THEN 'moderate_or_severe_symptoms'
                WHEN 'incapacitated' THEN 'forced_descents' END
            WHERE m.source_table='II' AND m.group_key='all_runs_unweighted_control'
            AND h.source_id='henry47_preselection' AND h.source_table='III'
            AND h.proportion_selected_pct=100 AND h.value_basis='calculated_control_rate'
            ORDER BY m.source_value
        """).fetchall() == [(53.3, 53.3), (66.0, 66.0), (82.8, 82.8)]
        assert db.execute("""
            SELECT report_id FROM model_report_link WHERE source_id='henry45_cook'
        """).fetchone() == ("pmid:21005555",)
        assert db.execute("""
            SELECT report_id FROM review.review_record
            WHERE record_key='2026-11-20-henry-cook-backref-t#19890012936'
        """).fetchone() == ("ntrs:19890012936",)
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='pmid:20251251' AND right_report='pmid:21005555'
            ORDER BY relationship
        """).fetchall() == [("derives_control_baseline_from",), ("possible_overlap",)]
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='henry45_cook'
        """).fetchone() == (0,)


def test_cam_minutes_keep_chokes_exposures_separate_from_reported_rates_and_scores(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT endpoint,numerator,denominator,denominator_unit,analysis_role
            FROM publication_observation WHERE source_id='cam44_meeting14' ORDER BY endpoint
        """).fetchall() == [
            ("chokes_source", 132, 719, "person_exposure", "overlap_hold"),
            ("circulatory_collapse_source", 6, None, None, "overlap_hold"),
        ]
        assert db.execute("""
            SELECT reported_value,unit FROM publication_meeting_measure
            WHERE source_id='cam44_meeting14' AND measure='severe_chokes_frequency'
        """).fetchone() == (1, "cases_per_1000_runs")
        assert db.execute("""
            SELECT measure,reported_value FROM publication_meeting_measure
            WHERE source_id='cam44_meeting14' AND study_group='knee-bends' ORDER BY measure
        """).fetchall() == [
            ("combined_bubble_and_streaking", 63),
            ("fascial_streaking", 37),
            ("popliteal_bubbles", 46),
        ]
        assert db.execute("""
            SELECT report_id FROM model_report_link WHERE source_id='cam44_meeting14'
        """).fetchone() == ("nlm:101085500x796:meeting-14",)
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='nlm:101085500x796:meeting-14'
            AND right_report='doi:10.7326/0003-4819-22-3-398'
        """).fetchone() == ("likely_overlap",)
        assert db.execute("""
            SELECT count(*) FROM historical_case_catalog WHERE source_id='cam44_meeting14'
        """).fetchone() == (0,)


def test_cam_bulletin_preserves_repeat_flight_totals_and_neurological_counting_units(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_table, count(*) FROM publication_repeat_descent GROUP BY 1 ORDER BY 1
        """).fetchall() == [("I", 26), ("II", 8)]
        assert db.execute("""
            SELECT flight_number,descent_count,exposure_count,reported_descent_pct
            FROM publication_repeat_descent WHERE source_table='I' AND prior_descents='all'
            ORDER BY flight_number
        """).fetchall() == [
            (1, 26, 89, 29.2), (2, 26, 88, 28.6), (3, 23, 87, 26.4),
            (4, 26, 91, 28.6), (5, 20, 82, 24.4), (6, 19, 79, 24.0),
        ]
        assert db.execute("""
            SELECT descent_count,exposure_count FROM publication_repeat_descent
            WHERE source_table='II' AND prior_descents='all' ORDER BY flight_number
        """).fetchall() == [(117, 955), (123, 955), (157, 955)]
        assert db.execute("""
            SELECT third_position,third_printed_label,reported_count FROM publication_repeat_classification
            WHERE first_result='fail' AND second_result='pass' ORDER BY third_position
        """).fetchall() == [(0, None, 37), (1, "F", 23), (2, "D", 8), (3, "F", 6)]
        assert db.execute("SELECT count(*) FROM publication_repeat_classification").fetchone() == (39,)
        assert db.execute("""
            SELECT endpoint,numerator,denominator,denominator_unit
            FROM publication_observation WHERE source_id='romano44_ana' ORDER BY endpoint
        """).fetchall() == [
            ("migraine_like_syndrome_episodes_source", 46, None, None),
            ("migraine_like_syndrome_people_source", 17, 155, "person"),
        ]
        assert db.execute("""
            SELECT source_id,measure,reported_value,value_basis FROM publication_archival_cohort_size
            WHERE source_id IN ('romano44_ana','klingman44_ana') ORDER BY source_id,measure
        """).fetchall() == [
            ("klingman44_ana", "people_examined", 40000, "strict_lower_bound"),
            ("romano44_ana", "exposures", 1361, "exact"),
            ("romano44_ana", "participants_questioned", 115, "exact"),
        ]
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='nlm:101085500x233:159'
            AND right_report='record:legacy:data/chamber/v1.10/sources.csv#stewart_halifax_c2683'
        """).fetchone() == ("subset_of",)


def test_cam_multicenter_preserves_source_counts_and_overlap(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT p.site, p.table_altitude_ft, p.narrative_altitude_ft,
                   c.exposure_count, c.descent_count
            FROM publication_repeat_flight_profile p
            JOIN publication_repeat_flight_count c USING (source_id,profile_id)
            WHERE c.flight_number=1 AND c.prior_descents='all'
            ORDER BY p.profile_id
        """).fetchall() == [
            ("University of Pennsylvania", 38000, 35000, 18, 15),
            ("U.S. Navy Pensacola", 40000, None, 105, 14),
            ("Randolph Field", 35000, None, 122, 36),
            ("Randolph Field", 38000, None, 51, 17),
            ("Wright Field", 35000, None, 187, 25),
        ]
        assert db.execute("SELECT count(*) FROM publication_repeat_flight_count").fetchone() == (82,)
        assert db.execute("""
            SELECT profile_id,exposure_count,reported_group_pct,descent_count,reported_descent_pct
            FROM publication_repeat_flight_count
            WHERE (profile_id='randolph-35000' AND flight_number=3 AND prior_descents='2')
               OR (profile_id='pensacola' AND flight_number=1)
               OR (profile_id='wright-35000' AND flight_number=2 AND prior_descents='0')
               OR (profile_id='pennsylvania' AND flight_number=3 AND prior_descents='1')
            ORDER BY profile_id
        """).fetchall() == [
            ("pennsylvania", 0, 0.0, None, None),
            ("pensacola", 105, 105.0, 14, 13.3),
            ("randolph-35000", 66, 6.9, 3, 50.0),
            ("wright-35000", 162, 88.6, 19, 11.7),
        ]
        assert db.execute("""
            SELECT o.numerator,o.denominator,sum(i.descent_count),count(*)
            FROM publication_observation o JOIN publication_descent_interval i
            USING (source_id,stratum,endpoint)
            GROUP BY o.source_id,o.stratum,o.endpoint ORDER BY o.stratum
        """).fetchall() == [(145, 380, 145, 8), (12, 51, 12, 3), (24, 51, 24, 3)]
        assert db.execute("""
            SELECT o.numerator,o.denominator,r.reported_percent
            FROM publication_observation o JOIN publication_reported_rate r
            USING (source_id,stratum,endpoint)
            WHERE o.source_id='wigodsky42_randolph'
        """).fetchone() == (7, 24, "71")
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='report:cam-330' AND right_report='nlm:101085500x796:meeting-14'
        """).fetchone() == ("same_cohort",)
        assert db.execute("""
            SELECT count(*) FROM publication_observation
            WHERE numerator=132 AND denominator=719 AND source_id IN ('bridge44_cam330','cam44_meeting14')
        """).fetchone() == (1,)


def test_cam_paired_outcomes_reuse_cohort_and_canonical_reports(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT shared_cohort_key,count(*),min(participant_count),max(participant_count)
            FROM publication_paired_chamber_arm GROUP BY shared_cohort_key
        """).fetchall() == [("ferris43-same-24", 2, 24, 24)]
        curves = db.execute("""
            SELECT arm,endpoint,count(*),group_concat(cumulative_count)
            FROM (
                SELECT arm,endpoint,cumulative_count
                FROM publication_paired_chamber_count ORDER BY arm,endpoint,window_end_min
            ) GROUP BY arm,endpoint ORDER BY arm,endpoint
        """).fetchall()
        assert curves == [
            ("placebo", "any_bends_or_chokes_source", 6, "4,10,18,20,23,24"),
            ("placebo", "incapacitating_bends_or_chokes_source", 6, "1,6,15,18,21,21"),
            ("stimulant", "any_bends_or_chokes_source", 6, "6,15,20,22,24,24"),
            ("stimulant", "incapacitating_bends_or_chokes_source", 6, "2,10,18,19,19,20"),
        ]
        assert db.execute("""
            SELECT stratum,reported_percent,source_denominator
            FROM publication_narrative_chamber_rate
            WHERE source_id='stewart43_retest' AND endpoint='no_symptoms_source' ORDER BY stratum
        """).fetchall() == [("afternoon", "72", None), ("forenoon", "54", None)]
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='stewart43_retest' AND endpoint='same_altitude_test_classification_source'
        """).fetchone() == (32, 32)
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='nlm:101085500x233:138:ferris' AND right_report='report:cam-112'
        """).fetchone() == ("same_cohort",)
        assert db.execute("""
            SELECT report_id,count(*) FROM review.review_record
            WHERE url='https://jamanetwork.com/journals/jama/fullarticle/291560'
            GROUP BY report_id
        """).fetchall() == [("doi:10.1001/jama.1947.02880060015004", 6)]
        assert db.execute("""
            SELECT report_id FROM review.review_record
            WHERE run_id='2026-11-20-cam-paired-archive-f' ORDER BY report_id
        """).fetchall() == [
            ("record:legacy:data/chamber/v1.12/sources.csv#cotes52_fprc",),
            ("record:legacy:data/chamber/v1.12/sources.csv#morant52_fprc",),
        ]


def test_hdsd_table_iii_retains_published_rates_and_links_reprinted_groups(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT count(*),sum(person_exposures) FROM literature_hdsd_compilation
            WHERE source_id='conkin92' AND analysis_role='overlap_hold'
        """).fetchone() == (27, 117422)
        assert db.execute("""
            SELECT report_number,dcs_pct,serious_dcs_pct FROM literature_hdsd_compilation
            WHERE report_number IN (93,109,351) ORDER BY report_number
        """).fetchall() == [(93, None, None), (109, 0.0, 0.0), (351, None, 0.4)]
        assert db.execute("""
            SELECT count(*),sum(h.person_exposures)
            FROM literature_hdsd_compilation h
            JOIN publication_reported_rate r
              ON (r.source_id,r.stratum,r.denominator)=(h.related_source_id,h.related_stratum,h.person_exposures)
            JOIN publication_reported_rate s
              ON (s.source_id,s.stratum,s.denominator)=(h.related_source_id,h.related_stratum,h.person_exposures)
            WHERE r.endpoint='bends_any_grade' AND CAST(r.reported_percent AS REAL)=h.dcs_pct
              AND s.endpoint='bends_grade_4' AND CAST(s.reported_percent AS REAL)=h.serious_dcs_pct
        """).fetchone() == (4, 68422)
        assert db.execute("""
            SELECT count(*) FROM literature_observation WHERE source_id='conkin92'
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT report_id FROM model_report_link
            WHERE source_table='literature_source' AND source_id='conkin92'
        """).fetchone() == ("pmid:1524540",)


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
