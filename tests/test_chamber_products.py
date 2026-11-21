import json
import shutil
import sqlite3

import pytest

from scripts.chamber_products import PRODUCTS, connect_pair, publish_pair
from scripts.evaluate_chamber_benchmark import run


def test_hitchcock_and_lockheed_keep_trial_scopes_and_endpoints_distinct(release):
    with connect_pair(release) as db:
        sources = {
            "hitchcock51_fulton_bends": "fulton1951:explosive-decompression",
            "barron55_lockheed_training": "pmid:13233153",
        }
        for model, report in sources.items():
            model_rows = db.execute("""
                SELECT stratum,endpoint,numerator,denominator,denominator_unit
                FROM publication_observation WHERE source_id=? ORDER BY stratum,endpoint
            """, (model,)).fetchall()
            review_rows = db.execute("""
                SELECT reported_group,endpoint,cases,denominator,denominator_unit
                FROM review.review_search_observation WHERE report_id=? AND cases IS NOT NULL
                ORDER BY reported_group,endpoint
            """, (report,)).fetchall()
            assert model_rows
            assert review_rows == model_rows
        assert db.execute("""
            SELECT stratum,numerator,denominator,analysis_role
            FROM publication_observation
            WHERE source_id='hitchcock51_fulton_bends'
              AND endpoint='incapacitating_bends_as_reported'
              AND stratum IN ('group-ii-slow','group-iv-rapid-208','group-iv-slow')
            ORDER BY stratum
        """).fetchall() == [
            ("group-ii-slow", 62, 111, "denominator_conflict"),
            ("group-iv-rapid-208", 36, 42, "overlap_hold"),
            ("group-iv-slow", 28, 45, "overlap_hold"),
        ]
        assert db.execute("""
            SELECT stratum,reported_percent,denominator FROM publication_reported_rate
            WHERE source_id='hitchcock51_fulton_bends'
              AND (stratum='group-ii-slow'
                OR (stratum='45000-completed-program-slow' AND endpoint='gas_symptoms_as_reported'))
            ORDER BY stratum
        """).fetchall() == [
            ("45000-completed-program-slow", "6.3", 32), ("group-ii-slow", "55.0", 111),
        ]
        assert db.execute("""
            SELECT cases,denominator,reported_rate_percent
            FROM review.review_search_observation
            WHERE report_id='fulton1951:explosive-decompression'
              AND reported_group='45000-completed-program-slow'
              AND endpoint='gas_symptoms_as_reported'
        """).fetchone() == (None, 32, 6.3)
        assert db.execute("""
            SELECT stratum,parent_stratum,trial_count FROM publication_chamber_trial_scope
            WHERE source_id='hitchcock51_fulton_bends' AND stratum LIKE 'group-v-rapid-%'
            ORDER BY stratum
        """).fetchall() == [
            ("group-v-rapid-104", "group-v-rapid-both", 25),
            ("group-v-rapid-208", "group-v-rapid-both", 25),
            ("group-v-rapid-both", "group-v", 50),
        ]
        assert db.execute("""
            SELECT stratum,trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE source_id='barron55_lockheed_training' ORDER BY stratum
        """).fetchall() == [
            ("instructor-exposures", 72, 4), ("trainees-20000ft", None, 147),
            ("trainees-25000ft", None, 234), ("trainees-with-rapid-exercise", None, 381),
        ]
        assert db.execute("""
            SELECT endpoint,denominator_unit FROM publication_observation
            WHERE source_id='barron55_lockheed_training' ORDER BY endpoint
        """).fetchall() == [
            ("dental_discomfort_as_reported", "person"),
            ("significant_confusion_as_reported", "person_exposure"),
            ("transient_chest_pain_without_other_reported_findings", "person"),
            ("tympanic_membrane_perforation_as_reported", "person"),
        ]
        assert db.execute("""
            SELECT count(*) FROM review.review_report_relation
            WHERE left_report='pmid:13221521' AND right_report='fulton1951:explosive-decompression'
              AND relationship='partial_overlap_program_overview'
        """).fetchone() == (1,)


def test_vakar_genin_and_petrukhin_translations_share_only_verified_outcomes(release):
    with connect_pair(release) as db:
        source_map = {
            "vakar77_jprs_69964": "ntrs:n78-18758",
            "genin75_jprs_65301": "ntrs:n75-28682",
            "petrukhin75_jprs_65301": "ntrs:n75-28683",
            "gramenitskiy74_vakar77_citation": "pmid:4610560",
        }
        for model_source, review_report in source_map.items():
            model = db.execute("""
                SELECT stratum,endpoint,numerator,denominator,denominator_unit
                FROM publication_observation WHERE source_id=?
            """, (model_source,)).fetchall()
            review = db.execute("""
                SELECT reported_group,endpoint,cases,denominator,denominator_unit
                FROM review.review_search_observation WHERE report_id=?
            """, (review_report,)).fetchall()
            assert model
            assert sorted(review) == sorted(model)
        assert db.execute("""
            SELECT cases,denominator,reported_rate_percent
            FROM review.review_search_observation WHERE report_id='ntrs:n78-18758'
            ORDER BY cases
        """).fetchall() == [(2, 434, 0.41), (8, 49, 16.3)]
        assert db.execute("""
            SELECT relationship FROM publication_overlap
            WHERE source_id='vakar77_jprs_69964' AND related_source='genin80'
        """).fetchone() == ("partial_overlap",)
        assert db.execute("""
            SELECT right_report FROM review.review_report_relation
            WHERE left_report='openalex:W89590632'
              AND relationship='re_reports_same_experiment_cells'
        """).fetchall() == [("ntrs:n78-18758",)]
        canonical_reports = {
            "2026-11-20-formal-chamber-openalex#W89590632": "openalex:W89590632",
            "2026-11-20-formal-chamber-openalex#W2993993201": "pmid:1152407",
            "legacy:data/chamber/v1.15/sources.csv#gramenitskiy74": "pmid:4610560",
            "legacy:data/chamber/v1.15/search_hits.csv#historic_v15_ntrs_archives:11":
                "ntrs:n75-28683",
        }
        for record_key, report in canonical_reports.items():
            assert db.execute("""
                SELECT report_id FROM review.review_record WHERE record_key=?
            """, (record_key,)).fetchone() == (report,)
        assert db.execute("""
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE source_id='genin75_jprs_65301'
            ORDER BY stratum
        """).fetchall() == [
            ("series-1", 0, 20), ("series-2-completed-chamber", 0, 15),
            ("series-2-meteorism-episode", 1, None), ("series-2-suited", 0, 2),
        ]
        assert db.execute("""
            SELECT endpoint,numerator,denominator FROM publication_observation
            WHERE source_id='petrukhin75_jprs_65301' AND denominator IS NOT NULL
            ORDER BY endpoint
        """).fetchall() == [
            ("minor_transient_neurological_findings", 10, 133),
            ("more_pronounced_neurological_findings", 3, 133),
        ]
        assert db.execute("""
            SELECT source_classification,count(*) FROM publication_chamber_case_episode
            WHERE source_id='petrukhin75_jprs_65301' AND parent_stratum='human-series'
            GROUP BY source_classification ORDER BY source_classification
        """).fetchall() == [
            ("acute_decompression_disease_as_reported", 2),
            ("prominent_neurological_findings_uncertain_dcs", 1),
        ]


def test_chadov_cabin_risk_sets_and_barer_full_text_reconcile(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id='chadov87_cabin_p910' AND denominator IS NOT NULL
            ORDER BY stratum,denominator_unit
        """).fetchall() == [
            ("experiment-1", 1, 25, "person"), ("experiment-1", 2, 35, "person_exposure"),
            ("experiment-2", 0, 26, "person"), ("experiment-2", 0, 31, "person_exposure"),
        ]
        assert db.execute("""
            SELECT count(DISTINCT participant_code),count(*),max(months_after_previous_episode),min(parent_stratum)
            FROM publication_chamber_case_episode WHERE source_id='chadov87_cabin_p910'
        """).fetchone() == (1, 2, 6, "experiment-1")
        assert db.execute("""
            SELECT stratum,stage,printed_nominal_pressure,printed_nominal_unit,printed_alternate_pressure,
                   printed_alternate_unit,oxygen_percent,nitrogen_percent
            FROM publication_chamber_native_pressure_stage ORDER BY stratum,stage
        """).fetchall() == [
            ("experiment-1", 1, 1.142, "atm", 1120, "gPa", None, None),
            ("experiment-1", 2, .58, "atm", 569, "gPa", 38, 62),
            ("experiment-1", 3, .24, "atm", None, None, 95, 5),
            ("experiment-2", 1, 1.142, "atm", 1120, "gPa", None, None),
            ("experiment-2", 2, .62, "atm", 608, "gPa", 36, 64),
            ("experiment-2", 3, .25, "atm", None, None, 95, 5),
        ]
        assert db.execute("""
            SELECT source_id,numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id IN ('barer82_jprs_80323','barer83_jprs_84412') AND stratum='all-trials'
              AND endpoint <> 'premature_trial_termination' ORDER BY source_id,denominator_unit
        """).fetchall() == [
            ("barer82_jprs_80323", 13, 43, "person"), ("barer82_jprs_80323", 14, 74, "person_exposure"),
            ("barer83_jprs_84412", 20, 70, "person"), ("barer83_jprs_84412", 22, 191, "person_exposure"),
        ]
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='barer82_jprs_80323' AND endpoint='altitude_caisson_disease_as_reported'
              AND stratum NOT IN ('all-trials','selected-susceptible') ORDER BY denominator,numerator
        """).fetchall() == [(1, 5), (1, 8), (1, 20), (8, 20), (3, 21)]
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='barer83_jprs_84412' AND endpoint='altitude_decompression_disorders_as_reported'
              AND stratum <> 'all-trials' ORDER BY denominator
        """).fetchall() == [(2, 6), (4, 16), (9, 28), (4, 48), (8, 64), (3, 93)]
        assert db.execute("""
            SELECT stratum,parent_stratum FROM publication_chamber_trial_scope
            WHERE source_id='barer83_jprs_84412' AND stratum LIKE 'air-break-%' ORDER BY stratum
        """).fetchall() == [
            ("air-break-10-minutes", "0p4-to-5-percent-nitrogen-air-break"),
            ("air-break-3-minutes", "0p4-to-5-percent-nitrogen-air-break"),
        ]
        assert db.execute("""
            SELECT report_id,count(*) FROM review.review_search_observation
            WHERE report_id IN ('ntrs:19890006135:p910','ntrs:n82-20839','ntrs:n83-36648','pmid:7062695','pmid:6620957')
            GROUP BY report_id ORDER BY report_id
        """).fetchall() == [("ntrs:19890006135:p910", 6), ("ntrs:n82-20839", 12), ("ntrs:n83-36648", 10)]
        assert db.execute("""
            SELECT count(*) FROM historical_case_catalog WHERE source_id='chadov87_cabin_p910'
        """).fetchone() == (0,)


def test_katuntsev_component_keeps_first_pain_and_recurrence_distinct(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id='katuntsev74_chamber_pain_jprs' AND analysis_role='overlap_hold'
            ORDER BY stratum
        """).fetchall() == [
            ("all-research-ascents", 284, None, None),
            ("previous-pain-resolved", 44, 52, "person_exposure"),
            ("previously-symptom-free", 29, 142, "person_exposure"),
        ]
        assert db.execute("""
            SELECT stratum,trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE source_id='katuntsev74_chamber_pain_jprs' ORDER BY stratum
        """).fetchall() == [
            ("all-research-ascents", 357, 61), ("previous-pain-resolved", 52, 29),
            ("previously-symptom-free", 142, 42), ("selected-additional-ascent", 194, None),
            ("selected-local-compression", 49, 24),
        ]
        assert db.execute("""
            SELECT endpoint,numerator,denominator FROM publication_observation
            WHERE source_id='katuntsev74_chamber_pain_jprs' AND analysis_role='overlapping_margin'
            ORDER BY endpoint
        """).fetchall() == [
            ("first_pain_at_additional_target", 13, 142), ("first_pain_during_additional_ascent", 16, 142),
            ("pain_recurrence_at_additional_target", 8, 52), ("pain_recurrence_during_additional_ascent", 36, 52),
        ]
        assert db.execute("""
            SELECT endpoint,numerator,denominator,denominator_basis FROM publication_observation
            WHERE source_id='katuntsev74_chamber_pain_jprs' AND denominator_unit='symptom_report'
            ORDER BY endpoint
        """).fetchall() == [
            ("pain_eliminated_as_reported", 6, 57, "author_reconstructed"),
            ("pain_reappeared_after_cuff_removal", 19, 57, "author_reconstructed"),
            ("pain_reappeared_during_pressure_release", 32, 57, "author_reconstructed"),
            ("pain_resolved_during_local_compression", 57, 62, "source_reported"),
        ]
        assert db.execute("""
            SELECT hour_at_altitude,reported_percent,denominator FROM publication_chamber_pain_onset_percentage
            ORDER BY hour_at_altitude
        """).fetchall() == [(1, 30.4, None), (2, 32.3, None), (3, 20.4, None),
                             (4, 11.6, None), (5, 2.4, None), (6, 2.9, None)]
        assert db.execute("""
            SELECT cases,denominator FROM review.review_search_observation
            WHERE study_id='katuntsev-imbp-altitude-experimental-program' AND endpoint='dcs_symptoms_source'
        """).fetchall() == [(931, 1778)]
        assert db.execute("""
            SELECT count(*) FROM review.review_study_report
            WHERE study_id='katuntsev-imbp-altitude-experimental-program'
              AND report_id IN ('ntrs:n74-33560','kosmbio:1974:8:4:66')
        """).fetchone() == (2,)
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation WHERE report_id='ntrs:n74-33560'
        """).fetchone() == (17,)
        assert db.execute("""
            SELECT related_source,relationship FROM publication_overlap WHERE source_id='katuntsev74_chamber_pain_jprs'
        """).fetchall() == [("katuntsev96_human", "likely_overlap")]


def test_iseev_archive_completes_one_risk_set_and_keeps_nested_findings(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT p.source_id,p.numerator,p.denominator,p.denominator_unit,p.denominator_basis,
                   p.analysis_role,l.report_id
            FROM publication_observation p JOIN publication_observation_denominator_completion c
                USING(source_id,stratum,endpoint)
            JOIN model_report_link l ON l.source_id=c.evidence_source_id AND l.source_table='publication_source'
            WHERE p.source_id='iseev88_chamber'
        """).fetchall() == [(
            "iseev88_chamber", 250, 2444, "person_exposure", "source_reported", "overlap_hold", "ntrs:n88-26074"
        )]
        assert db.execute("""
            SELECT source_id FROM publication_observation
            WHERE source_id IN ('iseev88_chamber','iseev88_archive_jprs') AND denominator=2444
        """).fetchall() == [("iseev88_chamber",)]
        assert db.execute("""
            SELECT cases,denominator FROM review.review_search_observation
            WHERE study_id='iseev-1975-1986-experimental-chamber' AND denominator=2444
        """).fetchall() == [(250, 2444)]
        assert db.execute("""
            SELECT trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE source_id='iseev88_chamber'
        """).fetchall() == [(2444, 130)]
        assert db.execute("""
            SELECT endpoint,numerator,denominator FROM publication_observation
            WHERE source_id='iseev88_archive_jprs' AND analysis_role='case_conditional' ORDER BY endpoint
        """).fetchall() == [
            ("cutaneous_primary_category", 22, 250), ("cutaneous_with_musculo_articular_features", 3, 22),
            ("musculo_articular_primary_category", 219, 250), ("neurocirculatory_primary_category", 4, 250),
            ("pulmonary_primary_category", 5, 250),
        ]
        assert db.execute("""
            SELECT cases,denominator FROM review.review_search_observation
            WHERE endpoint='musculo_articular_other_cases_mentioned' AND report_id='ntrs:n88-26074'
        """).fetchall() == [(221, None)]
        assert db.execute("""
            SELECT count(DISTINCT stratum),count(*) FROM publication_case_milestone
            WHERE source_id='iseev88_archive_jprs'
        """).fetchone() == (7, 26)
        assert db.execute("""
            SELECT stratum,elapsed,elapsed_reference FROM publication_case_milestone
            WHERE source_id='iseev88_archive_jprs' AND milestone IN ('bradycardia_observed','vertigo_reported')
            ORDER BY stratum
        """).fetchall() == [
            ("precollapse-neurocirculatory", 20.0, "time at chamber altitude"),
            ("repeated-ascent-neurocirculatory", 5.0, "start of step exercise on day four"),
        ]
        assert db.execute("""
            SELECT count(*) FROM historical_case_catalog WHERE source_id='iseev88_archive_jprs'
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit,analysis_role FROM publication_observation
            WHERE source_id='filipenkov07_chamber_repeats'
        """).fetchall() == [(0, 123, "person", "overlap_hold")]
        assert db.execute("""
            SELECT right_report FROM review.review_report_relation
            WHERE left_report='nrcerm:2012:1:45' AND relationship='cites' ORDER BY right_report
        """).fetchall() == [
            ("extrem:1982:kazakova:275",), ("gmik:2007:filipenkov",),
            ("thesis-abstract:2011:starovoyt",), ("thesis:1994:volkov",),
        ]
        assert db.execute("""
            SELECT right_report FROM review.review_report_relation
            WHERE left_report='thesis-abstract:2011:starovoyt' AND relationship='author_summary_of'
        """).fetchall() == [("rsl:01005087415",)]


def test_soviet_chamber_translation_preserves_units_and_shared_populations(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,endpoint,numerator,denominator,denominator_unit,analysis_role
            FROM publication_observation
            WHERE source_id='chadov87_staged_jprs' AND analysis_role='overlap_hold'
            ORDER BY stratum,denominator_unit
        """).fetchall() == [
            ("12h-staging", "people_with_altitude_decompression_disorders_as_reported", 6, 27, "person", "overlap_hold"),
            ("12h-staging", "altitude_decompression_disorders_as_reported", 6, 36, "person_exposure", "overlap_hold"),
            ("18h-staging", "people_with_altitude_decompression_disorders_as_reported", 1, 30, "person", "overlap_hold"),
            ("18h-staging", "altitude_decompression_disorders_as_reported", 1, 51, "person_exposure", "overlap_hold"),
            ("24h-staging", "people_with_altitude_decompression_disorders_as_reported", 0, 37, "person", "overlap_hold"),
            ("24h-staging", "altitude_decompression_disorders_as_reported", 0, 69, "person_exposure", "overlap_hold"),
        ]
        assert db.execute("""
            SELECT stage,planned_duration_min,pressure_hpa,oxygen_percent_lower,oxygen_percent_upper
            FROM publication_chamber_exposure_stage WHERE stratum='18h-staging' ORDER BY stage
        """).fetchall() == [
            (1, 120, 1120.0, None, None), (2, 1080, 733.3, 29.0, 30.0), (3, 360, 293.3, 95.0, 96.0),
        ]
        assert db.execute("""
            SELECT milestone,elapsed FROM publication_case_milestone
            WHERE source_id='chadov87_staged_jprs' AND elapsed IS NOT NULL ORDER BY milestone
        """).fetchall() == [("pain_persisted_through_rest", 5.0), ("right_elbow_and_wrist_pain", 75.0)]
        assert db.execute("""
            SELECT stratum,trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE source_id='chadov86_head_down' ORDER BY stratum
        """).fetchall() == [("180-mmhg", None, None), ("220-mmhg", 22, 12), ("all", 47, 22)]
        assert db.execute("""
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE source_id='chadov86_head_down' ORDER BY stratum
        """).fetchall() == [
            ("180-mmhg-head-down", 5, None), ("180-mmhg-seated", 6, None),
            ("220-mmhg-head-down", 0, None), ("220-mmhg-upright", 2, None),
        ]
        assert db.execute("""
            SELECT endpoint,numerator,denominator FROM publication_observation
            WHERE source_id='iseev88_threshold_original' ORDER BY endpoint
        """).fetchall() == [
            ("people_with_disorder_threshold_identified", 28, 40),
            ("people_with_vge_threshold_identified", 31, 40),
        ]
        assert db.execute("""
            SELECT reported_group,reported_rate_lower,reported_rate_upper,reported_rate_unit,
                   cases,denominator,reported_rate_percent
            FROM review.review_search_observation WHERE endpoint='dcs_symptoms_by_vge_grade'
            ORDER BY reported_group
        """).fetchall() == [
            ("grade-1-2", 10, 16, "percent", None, None, None),
            ("grade-3-4", 50, 75.9, "percent", None, None, None),
        ]
        assert db.execute("""
            SELECT stratum,reported_percent_lower,reported_percent_upper
            FROM publication_vge_dcs_percent_range ORDER BY stratum
        """).fetchall() == [("grade-1-2", 10.0, 16.0), ("grade-3-4", 50.0, 75.9)]
        assert db.execute("""
            SELECT right_report,relationship FROM review.review_report_relation
            WHERE left_report='ntrs:n87-25740' ORDER BY right_report
        """).fetchall() == [
            ("ntrs:n88-26074", "possible_overlap_historical_chamber_archive"),
            ("pmid:3560843", "translation_of"),
        ]


def test_russian_reports_and_connolly_companions_keep_distinct_outcome_units(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit,analysis_role
            FROM publication_observation
            WHERE source_id='filipenkov89_suit_chamber' ORDER BY denominator
        """).fetchall() == [
            (26, 193, "person", "overlap_hold"),
            (29, 1179, "person_exposure", "overlap_hold"),
        ]
        assert db.execute("""
            SELECT repeat_runs,altitude_min_m,altitude_max_m,prebreathe_min_min,prebreathe_max_min
            FROM publication_repeat_chamber_protocol_count ORDER BY altitude_min_m,prebreathe_min_min
        """).fetchall() == [
            (223, 7000, 8000, 30, 30),
            (14, 7000, 8000, 60, 60),
            (121, 9000, 12000, 90, 120),
        ]
        assert db.execute("""
            SELECT cases,denominator FROM review.review_search_observation
            WHERE endpoint='dcs_clinical_outcomes_unenumerated' ORDER BY denominator
        """).fetchall() == [(None, 14), (None, 121), (None, 223)]
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='filipenkov15_doppler' AND stratum='musculoskeletal-no-bubble-signal'
        """).fetchall() == [(3, None)]
        assert db.execute("""
            SELECT report_id,onset_min FROM shared_case_evidence
            WHERE source_id IN ('dvornikov19_su24m','dvornikov19_academy')
        """).fetchall() == [("doi:10.17816/rmmj72843", None)]
        assert db.execute("""
            SELECT left_report,right_report,relationship FROM review.review_report_relation
            WHERE left_report='doi:10.17816/brmma20678'
        """).fetchall() == [
            ("doi:10.17816/brmma20678", "doi:10.17816/rmmj72843", "same_published_case"),
        ]
        assert db.execute("""
            SELECT source_id,endpoint,numerator,denominator FROM publication_observation
            WHERE source_id IN ('connolly23_early_biomarkers','connolly24_brain_lung_assays')
        """).fetchall() == [
            ("connolly23_early_biomarkers", "heavy_and_persistent_vge_as_reported", 11, 15),
        ]
        assert db.execute("""
            SELECT COUNT(*),COUNT(baseline_mean),COUNT(t8_mean),COUNT(t24_mean),
                   COUNT(reported_n) FROM publication_biomarker_summary
        """).fetchone() == (12, 9, 9, 9, 7)
        assert db.execute("""
            SELECT analyte,reported_n,t8_mean,t8_se FROM publication_biomarker_summary
            WHERE analyte IN ('CD14','RAGE','Tau') ORDER BY analyte
        """).fetchall() == [
            ("CD14", None, 2994.0, 1049.0), ("RAGE", 14, 1.56, 0.1), ("Tau", 1, None, None),
        ]
        assert db.execute("""
            SELECT COUNT(DISTINCT report_id),COUNT(*) FROM review.review_record
            WHERE rtrim(url,'/') LIKE 'https://biofizpribor.ru/%'
                || 'ultrazvukovaya-diagnostika-ustoichivosti-k-dekompressii-pri-imitatsii-letnoi-deyatelnosti'
        """).fetchone() == (1, 8)
        assert db.execute("""
            SELECT report_id,COUNT(*) FROM review.review_record
            WHERE report_id IN ('doi:10.17816/rmmj73430','doi:10.21949/1403478')
            GROUP BY report_id ORDER BY report_id
        """).fetchall() == [("doi:10.17816/rmmj73430", 9), ("doi:10.21949/1403478", 8)]


def test_raf_sortie_year_survey_and_army_case_keep_published_counting_units(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,analysis_role,numerator,denominator,denominator_unit
            FROM publication_observation
            WHERE source_id IN ('posselt19_raf_sortie','hodkinson19_raf_revision',
                                'connolly24_raf_mri','mciver24_raf_dispatcher')
            ORDER BY stratum
        """).fetchall() == [
            ("2017-dispatcher-series", "overlap_hold", 3, None, None),
            ("2017-neurological-component", "case_conditional", 2, 3, "dcs_case"),
            ("2017-respiratory-component", "case_conditional", 1, 3, "dcs_case"),
            ("affected-sortie", "selected_cluster", 2, None, None),
            ("c130-dispatcher-case", "overlap_hold", 1, None, None),
            ("phase2-research-mri-subgroup", "overlapping_margin", 0, 6, "person"),
        ]
        assert db.execute("""
            SELECT respondent_count,altitude_cutoff_ft,COUNT(*),
                   COUNT(above_item_denominator),COUNT(below_item_denominator)
            FROM publication_altitude_symptom_survey
            JOIN publication_altitude_symptom_survey_item USING(source_id)
            GROUP BY source_id
        """).fetchall() == [(64, 16000, 9, 0, 0)]
        assert db.execute("""
            SELECT reported_group,reported_rate_percent,cases,denominator
            FROM review.review_search_observation WHERE endpoint='survey_visual_disturbance'
            ORDER BY reported_group
        """).fetchall() == [("above-16000-ft", 10.2, None, None), ("below-16000-ft", 1.75, None, None)]
        assert db.execute("""
            SELECT report_id,onset_min,first_assessment_min FROM shared_case_evidence
            WHERE source_id='belmonte24_army_chamber'
        """).fetchall() == [("abstract:asma-2024-belmonte-292", None, None)]
        assert db.execute("""
            SELECT COUNT(*),COUNT(elapsed) FROM publication_case_milestone
            WHERE source_id='belmonte24_army_chamber'
        """).fetchone() == (5, 0)
        assert db.execute("""
            SELECT COUNT(*),COUNT(DISTINCT report_id),MIN(report_id) FROM review.review_record
            WHERE record_key='legacy:data/chamber/v1.6/sources.csv#connolly23'
               OR record_key GLOB 'legacy:data/chamber/intake-2026-11-19/outcome_sources.csv#connolly23:*'
        """).fetchone() == (6, 1, "pmid:37587625")
        assert db.execute("""
            SELECT COUNT(*) FROM review.review_report_relation
            WHERE right_report='abstract:asma-2019-posselt-100'
              AND relationship GLOB 'possible_overlap_*'
        """).fetchone() == (3,)


def test_japanese_training_reports_and_flight_case_preserve_risk_sets(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_id,analysis_role,numerator,denominator,denominator_unit
            FROM publication_observation
            WHERE source_id IN ('ito15_chamber_dcs_pair','ito14_chamber_dcs_abstract',
                                'ishiyama16_shizuoka_referrals','inuzuka22_operational_dci',
                                'inuzuka23_japanese_translation')
            ORDER BY source_id
        """).fetchall() == [
            ("inuzuka22_operational_dci", "selected_cluster", 1, None, None),
            ("ishiyama16_shizuoka_referrals", "case_conditional", 2, 173, "treated_referral"),
            ("ito15_chamber_dcs_pair", "overlap_hold", 2, None, None),
        ]
        assert db.execute("""
            SELECT milestone,elapsed,elapsed_qualifier,aircraft_altitude_ft,altitude_qualifier
            FROM publication_aircraft_case_milestone
            WHERE milestone IN ('exposure_above_18000_ft','chest_pain_and_paresthesia')
            ORDER BY milestone
        """).fetchall() == [
            ("chest_pain_and_paresthesia", None, None, None, None),
            ("exposure_above_18000_ft", 3.0, "less_than", 18000, "above_threshold"),
        ]
        assert db.execute("""
            SELECT left_report,right_report,relationship FROM review.review_report_relation
            WHERE left_report IN ('jshm:58-2-44','jachod:11-2-106','minder:17-2-ishiyama')
            ORDER BY left_report
        """).fetchall() == [
            ("jachod:11-2-106", "jachod:12-1-20", "likely_prior_report_of_same_case_pair"),
            ("jshm:58-2-44", "pmid:35690900", "same_published_case"),
            ("minder:17-2-ishiyama", "jachod:12-1-20", "possible_overlap_hospital_referrals"),
        ]
        assert db.execute("""
            SELECT report_id,onset_min FROM shared_case_evidence
            WHERE source_id='inuzuka22_operational_dci'
        """).fetchall() == [("pmid:35690900", None)]
        assert db.execute("""
            SELECT COUNT(*) FROM review.review_search_observation
            WHERE study_id IN ('jasdf-inuzuka-jet-rapid-decompression','shizuoka-ito-chamber-dcs-pair',
                               'shizuoka-ishiyama-recompression-series')
        """).fetchone() == (3,)


def test_usaf_table8_and_webb_interim_outcomes_keep_source_scope(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT dcs_label,COUNT(*),COUNT(DISTINCT participant_ordinal),SUM(tt8_outcome='success')
            FROM publication_tt8_episode GROUP BY dcs_label ORDER BY dcs_label
        """).fetchall() == [("I", 11, 10, 10), ("II", 2, 2, 1)]
        assert db.execute("""
            SELECT episode_number,exposure_year,recurrence_reported,tt8_outcome
            FROM publication_tt8_episode WHERE participant_ordinal=10 ORDER BY episode_number
        """).fetchall() == [(1, 1988, 0, "success"), (2, 1989, 1, "failure")]
        assert db.execute("""
            SELECT COUNT(*),COUNT(altitude_ft),SUM(treatment_delay_relation='less_than'),
                   COUNT(resolution_min),COUNT(tt6_conversion_documented)
            FROM publication_tt8_episode
        """).fetchone() == (13, 12, 10, 8, 1)
        assert db.execute("""
            SELECT resolution_min,unresolved_at_assessment_min,tt8_outcome
            FROM publication_tt8_episode WHERE tt6_conversion_documented=1
        """).fetchone() == (None, 30, "failure")
        assert db.execute("""
            SELECT type_i_participants,resolved_without_reported_recurrence,reprint_source_id,completed_source_id
            FROM publication_tt8_interim_tally
        """).fetchall() == [(10, 10, "dart98_usaf_tt8_review", "butler02_usaf_tt8")]
        assert db.execute("""
            SELECT COUNT(*) FROM publication_observation
            WHERE source_id IN ('topper89_usaf_tt8_interim','dart98_usaf_tt8_review')
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT arm,exposures,marked_dcs_cases,abstract_dcs_percent,results_dcs_percent,
                   resolved_on_recompression,respiratory_dcs_cases
            FROM publication_webb94_interim_group ORDER BY arm
        """).fetchall() == [
            ("exercise10_rest50", 22, 8, 38, 36, 8, None),
            ("rest60", 22, None, 76, 77, None, 2),
        ]
        assert db.execute("""
            SELECT e.final_participant_ordinal,c.hbo_marked,c.symptom_text
            FROM publication_webb94_case_link e
            JOIN citation_participant_cell c
                ON (c.source_id,c.study_participant,c.arm)=(e.final_source_id,e.final_participant_ordinal,e.final_arm)
        """).fetchall() == [(14, 1, "Chokes")]
        assert db.execute("""
            SELECT COUNT(*),SUM(o.numerator=r.cases AND o.denominator=r.denominator)
            FROM publication_observation o
            JOIN model_report_link l ON l.source_id=o.source_id AND l.source_table='publication_source'
            JOIN review.review_search_observation r ON r.report_id=l.report_id
                AND r.endpoint=o.endpoint AND r.reported_group=o.stratum
            WHERE o.source_id IN ('butler02_usaf_tt8','webb94_brooks_prebreathe_interim')
        """).fetchone() == (4, 4)
        assert db.execute("""
            SELECT COUNT(*),COUNT(DISTINCT report_id) FROM review.review_record
            WHERE record_key IN (
                'legacy:data/chamber/v1.5/sources.csv#webb96_preoxygenation',
                '2026-11-20-formal-chamber-pubmed#8830940',
                '2026-11-20-formal-chamber-europe-pmc#MED:8830940',
                'legacy:data/chamber/v1.13/search_hits.csv#clinical_series_tavily_comparison:2'
            )
        """).fetchone() == (4, 1)


def test_nasa_severity_reprints_and_lunar_missing_denominators(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT exposures,all_dcs,serious_dcs,tr360,pressure_psia,altitude_exposure_min
            FROM publication_nasa_f3_stratum WHERE cited_source_id='vann95_duke_perfusion'
            ORDER BY table_row
        """).fetchall() == [
            (14, 8, 1, 1.77, 4.3, 240),
            (18, 8, 1, 1.77, 4.3, 240),
            (10, 2, 1, 1.70, 4.3, 240),
            (15, 5, 1, 1.77, 4.3, 240),
        ]
        assert db.execute("""
            SELECT f.exposures,f.all_dcs,f.serious_dcs,t.dcs_denominator,t.dcs_cases,
                   (SELECT COUNT(*) FROM publication_nasa_f2_case c WHERE c.nasa_test_id=t.test_id)
            FROM publication_nasa_f3_stratum f JOIN nasa_test t ON t.test_id=f.nasa_test_id
        """).fetchall() == [(22, 6, 1, 22, 6, 1)]
        assert db.execute("""
            SELECT COUNT(*),SUM(classification='historical_skin_mottling'),SUM(prescribed_prebreathe_exercise)
            FROM publication_nasa_f2_case
        """).fetchone() == (7, 1, 2)
        assert db.execute("""
            SELECT nasa_test_id FROM publication_nasa_f2_case
            WHERE classification='historical_skin_mottling'
        """).fetchall() == [("8b",)]
        assert db.execute("""
            SELECT exposures,all_dcs,serious_dcs FROM publication_nasa_f3_stratum
            WHERE cited_source_id='allen71_body_fat'
        """).fetchall() == [(26, 11, 1)]
        assert db.execute("""
            SELECT volunteers_selected,groups_reported,pressure_regimes,test_cycles_reported,
                   planned_eva_days_per_cycle,evaluable_dcs_person_evas,evaluable_vge_person_evas
            FROM publication_lunar_pressure_campaign
        """).fetchall() == [(19, 4, 2, 7, 4, None, None)]
        assert db.execute("""
            SELECT COUNT(*),SUM(o.numerator=r.cases AND o.denominator IS r.denominator),
                   SUM(o.denominator IS NULL),SUM(o.analysis_role='overlap_hold')
            FROM publication_observation o
            JOIN model_report_link l ON l.source_id=o.source_id AND l.source_table='publication_source'
            JOIN review.review_search_observation r ON r.report_id=l.report_id
                AND r.endpoint=o.endpoint AND r.reported_group=o.stratum
            WHERE o.source_id IN ('vann95_duke_perfusion','liu23_lunar_pressure_campaign')
        """).fetchone() == (10, 10, 2, 10)
        assert db.execute("""
            SELECT COUNT(*),COUNT(DISTINCT report_id) FROM review.review_record
            WHERE record_key IN (
                'legacy:data/chamber/v1/sources.csv#nasa19',
                '2026-11-20-nasa-severity-lunar-primary#nasa-2019-f2-f3',
                '2026-11-20-eds-training#maiaqbbnfr',
                '2026-11-20-formal-chamber-openalex#W3166782986'
            )
        """).fetchone() == (4, 1)


def test_duke_prebreathe_keeps_ascent_series_and_overlapping_reports_distinct(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT p.ascent_min, p.protocol_code, p.prebreathe_min, o.numerator, o.denominator,
                   o.denominator_basis, o.analysis_role
            FROM publication_duke_prebreathe_protocol p
            JOIN publication_observation o ON p.source_id=o.source_id AND p.protocol_code=o.stratum
            ORDER BY p.ascent_min,p.protocol_code
        """).fetchall() == [
            (9, "HDR", 210, 2, 5, "author_reconstructed", "overlap_hold"),
            (9, "SE", 210, 0, 6, "author_reconstructed", "overlap_hold"),
            (9, "SR", 210, 4, 6, "author_reconstructed", "overlap_hold"),
            (30, "HDR", 210, 1, 10, "source_reported", "overlap_hold"),
            (30, "SE2", 150, 5, 10, "source_reported", "overlap_hold"),
            (30, "SE3", 210, 0, 5, "source_reported", "overlap_hold"),
            (30, "SHR", 210, 1, 7, "source_reported", "overlap_hold"),
        ]
        assert db.execute("""
            SELECT count(DISTINCT participant_ordinal), COUNT(*), SUM(dcs),
                   COUNT(dcs_onset_min_approx), COUNT(vge_onset_min_approx)
            FROM publication_duke_prebreathe_exposure
        """).fetchone() == (6, 17, 6, 4, 2)
        assert db.execute("""
            SELECT e.protocol_code, SUM(e.dcs), COUNT(*), o.numerator, o.denominator
            FROM publication_duke_prebreathe_exposure e
            JOIN publication_observation o ON o.source_id=e.source_id AND o.stratum=e.protocol_code
            GROUP BY e.protocol_code,o.numerator,o.denominator ORDER BY e.protocol_code
        """).fetchall() == [("HDR", 2, 5, 2, 5), ("SE", 0, 6, 0, 6), ("SR", 4, 6, 4, 6)]
        assert db.execute("""
            SELECT participant_ordinal, protocol_code, dcs_onset_min_approx, vge_onset_min_approx
            FROM publication_duke_prebreathe_exposure WHERE vge_onset_min_approx>dcs_onset_min_approx
        """).fetchall() == [(2, "HDR", 171, 176)]
        assert db.execute("""
            SELECT protocol_code,exercise_rest_min FROM publication_duke_prebreathe_protocol
            WHERE protocol_code IN ('SE2','SE3') ORDER BY protocol_code
        """).fetchall() == [("SE2", 40), ("SE3", None)]
        assert db.execute("""
            SELECT protocol_code,historical_participants,historical_dcs_percent
            FROM publication_duke_prebreathe_protocol WHERE phase='historical_summary'
            ORDER BY protocol_code
        """).fetchall() == [("prior-exercise", 10, 0), ("prior-rest", 16, 63)]
        assert db.execute("""
            SELECT COUNT(*), SUM(o.numerator=r.cases AND o.denominator=r.denominator)
            FROM publication_observation o
            JOIN model_report_link l ON l.source_id=o.source_id AND l.source_table='publication_source'
            JOIN review.review_search_observation r ON r.report_id=l.report_id
                AND r.endpoint=o.endpoint AND r.reported_group=o.stratum
            WHERE o.source_id IN ('vann89_duke_prebreathe_duration','gerth89_duke_nitrogen_workshop')
        """).fetchone() == (7, 7)
        assert db.execute("""
            SELECT COUNT(*) FROM review.review_search_observation
            WHERE report_id='abstract:asma-1989-duke-gerth-072'
        """).fetchone() == (0,)


def test_usafsam_appendix_editions_and_abstract_denominators(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_id, COUNT(*), COUNT(exposures_grade2_pct)
            FROM publication_usafsam_appendix_a GROUP BY source_id ORDER BY source_id
        """).fetchall() == [
            ('webb88_protocol_bibliography', 20, 0),
            ('webb90_protocol_bibliography_revised', 21, 21),
        ]
        assert dict(db.execute("""
            SELECT relationship, COUNT(*) FROM publication_usafsam_appendix_a_link
            GROUP BY relationship
        """)) == {
            'shared_summary_values': 18,
            'revised_counts_unresolved': 1,
            'planned_design_to_duration_result': 2,
        }
        assert db.execute("""
            SELECT onset_status, participant_count, reported_exposure_count, scheduled_max_hours,
                   participants_grade2_first_pct, participants_grade2_ever_pct, exposures_grade2_pct
            FROM publication_usafsam_appendix_a WHERE study_number=8 ORDER BY source_id,row_number
        """).fetchall() == [
            ('study_in_progress', 30, 120, None, None, None, None),
            ('reported', 23, 77, 3, 26, 30, 12),
            ('reported', 13, 49, 6, 92, 100, 86),
        ]
        assert db.execute("""
            SELECT participant_count, reported_exposure_count, participants_grade2_first_pct,
                   exposures_grade2_pct, mean_grade2_onset_min
            FROM publication_usafsam_appendix_a
            WHERE study_number=1 AND pressure_altitude_ft=25000 ORDER BY source_id
        """).fetchall() == [(29, 30, 69, None, 151), (27, 28, 74, 75, 151)]
        assert db.execute("""
            SELECT participants_max_vge_3_4_pct, participants_max_vge_1_2_pct, participants_max_vge_0_pct
            FROM publication_usafsam_appendix_a WHERE pressure_psia=9.00
        """).fetchall() == [(23, 14, 64), (23, 14, 64)]
        assert db.execute("""
            SELECT numerator, denominator, mean_min, earliest_min, latest_min, analysis_role
            FROM publication_usafsam_pilot_onset
            JOIN publication_observation USING (source_id)
            WHERE altitude_ft=altitude ORDER BY altitude_ft
        """).fetchall() == [
            (8, 10, 133, 82, 234, 'overlap_hold'),
            (6, 10, 127, 59, 204, 'overlap_hold'),
            (10, 10, 93.5, 42, 172, 'overlap_hold'),
        ]
        assert db.execute("""
            SELECT cases, reported_percent, reported_exposures
            FROM publication_usafsam_co2_interim_arm
        """).fetchall() == [(4, 10.3, None), (4, 10.3, None)]
        assert db.execute("""
            SELECT endpoint, numerator, denominator, analysis_role FROM publication_observation
            WHERE source_id IN ('smead87_bsi_preliminary','baas89_co2_interim') ORDER BY endpoint
        """).fetchall() == [
            ('bubbles_preceded_bends', 93, 126, 'overlap_hold'),
            ('grade2_limb_bends', 126, 190, 'overlap_hold'),
            ('no_significant_vge', 31, 64, 'overlap_hold'),
            ('persistent_dcs_as_reported', 8, 78, 'overlap_hold'),
        ]
        assert db.execute("""
            SELECT COUNT(*) FROM review.review_report_relation
            WHERE relationship='reprints_study_abstract'
              AND left_report='report:ada231355'
              AND right_report IN (
                  'abstract:asma-1984-adams-bends-susceptibility',
                  'abstract:space-life-sciences-1987-smead-bsi',
                  'abstract:asma-1989-baas-co2-prebreathe'
              )
        """).fetchone() == (3,)
        assert db.execute("""
            SELECT COUNT(*), SUM(o.numerator=r.cases AND o.denominator=r.denominator)
            FROM publication_observation o
            JOIN model_report_link l ON l.source_id=o.source_id AND l.source_table='publication_source'
            JOIN review.review_search_observation r ON r.report_id=l.report_id AND r.endpoint=o.endpoint
                AND r.reported_group=o.stratum
            WHERE o.source_id IN ('adams84_bsi_pilot','smead87_bsi_preliminary','baas89_co2_interim')
        """).fetchone() == (7, 7)


@pytest.fixture(scope="module")
def release(tmp_path_factory):
    folder = tmp_path_factory.mktemp("chamber") / "release"
    publish_pair(folder)
    return folder


def test_aircraft_incidents_keep_distinct_reported_risk_sets(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT p.report_id, s.study_id, i.peak_cabin_altitude_m,
                   c.measure, c.numerator, c.denominator, c.denominator_unit,
                   r.cases, r.denominator, r.denominator_unit
            FROM publication_aircraft_incident i
            JOIN publication_aircraft_incident_count c USING (source_id)
            JOIN model_report_link p USING (source_id)
            JOIN review.review_study_report s ON s.report_id=p.report_id
            JOIN review.review_search_observation r ON r.report_id=p.report_id
                AND r.study_id=s.study_id AND r.endpoint=c.measure
            WHERE p.source_table='publication_source' AND c.evidence_role='incident_diagnosis'
            ORDER BY p.report_id
        """).fetchall() == [
            ("pmid:18457302", "johnston-c130-fall-2005", 7317,
             "reported_dcs_any", 4, 66, "aircraft_occupant", 4, 66, "aircraft_occupant"),
            ("pmid:30487030", "mancini-military-aircraft-6400m", 6400,
             "reported_type_ii_dcs", 6, 49, "exposed_passenger", 6, 49, "exposed_passenger"),
        ]
        assert db.execute("""
            SELECT measure,numerator,denominator,evidence_role,reported_pct
            FROM publication_aircraft_incident_count
            WHERE measure IN ('presumptive_spinal_dcs','remaining_symptomatic_narrative','headache')
            ORDER BY measure
        """).fetchall() == [
            ("headache", 23, 49, "overlapping_symptom", 46.93),
            ("presumptive_spinal_dcs", 1, 66, "diagnostic_component", None),
            ("remaining_symptomatic_narrative", 26, None, "unreconciled_narrative", None),
        ]
        assert db.execute("""
            SELECT count(DISTINCT report_id) FROM review.review_record WHERE pmid='30487030'
        """).fetchone() == (1,)
        assert db.execute("""
            SELECT report_id FROM review.review_record
            WHERE record_key='2026-11-20-aircraft-depressurization-f-jarosz#jarosz-mirror'
        """).fetchone() == ("doi:10.13174/pjamp.21.01.2015.01",)
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence
            WHERE report_id IN (
                SELECT p.report_id FROM model_report_link p
                JOIN publication_aircraft_incident i USING (source_id)
                WHERE p.source_table='publication_source'
            )
        """).fetchone() == (0,)


def test_historical_u2_counts_and_case_selected_flights(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit,analysis_role
            FROM publication_aviation_group WHERE source_id='bruneau62_u2' AND metric GLOB 'dysbarism*'
            ORDER BY numerator DESC
        """).fetchall() == [
            (17, 6048, "aircraft_flight", "overlap_hold"),
            (1, 271, "reported_decompression_event", "overlapping_margin"),
        ]
        assert db.execute("""
            SELECT count(*),count(DISTINCT crew_code),count(onset_hours),sum(decompression_events)
            FROM publication_meader_reported_flight WHERE source_id='meade67'
        """).fetchone() == (36, 11, 24, 2)
        assert db.execute("""
            SELECT flight_no, peak_cabin_ft, peak_cabin_relation, decompression_min, onset_hours
            FROM publication_meader_reported_flight WHERE decompression_events>0 ORDER BY flight_no
        """).fetchall() == [(9, 60000, ">", 10, None), (12, 60000, ">", 20, None)]
        assert db.execute("""
            SELECT sum(numerator),sum(denominator) FROM publication_aviation_group
            WHERE source_id='meade67' AND stratum GLOB 'crew-*'
        """).fetchone() == (36, 958)
        assert db.execute("""
            WITH bins(stratum,lo,hi) AS (VALUES
                ('preoxygenation-30-39-min',30,39),
                ('preoxygenation-40-49-min',40,49),
                ('preoxygenation-50-60-min',50,60)
            )
            SELECT g.numerator,g.denominator,g.rate_as_printed,g.analysis_role,count(f.flight_no)
            FROM publication_aviation_group g
            JOIN bins b USING (stratum)
            JOIN publication_meader_reported_flight f
              ON f.source_id=g.source_id AND f.crew_code!='I'
              AND f.preoxygenation_min BETWEEN b.lo AND b.hi
            WHERE g.source_id='meade67'
            GROUP BY g.stratum ORDER BY g.stratum
        """).fetchall() == [
            (5, 139, ".036", "overlapping_margin", 5),
            (11, 556, ".020", "overlapping_margin", 11),
            (1, 114, ".009", "overlapping_margin", 1),
        ]
        assert db.execute("""
            SELECT numerator,denominator,rate_as_printed,analysis_role
            FROM publication_aviation_group WHERE source_id='meade67' AND stratum='crew-H'
        """).fetchone() == (4, 139, "1.8", "denominator_conflict")
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE lower(url) LIKE '%ad0658348%' OR lower(url) LIKE '%aeme/38/3/article-p301%'
        """).fetchall() == [("report:ad0658348",)]
        assert db.execute("""
            SELECT report_id FROM model_report_link WHERE source_table='publication_source' AND source_id='meade67'
        """).fetchone() == ("report:ad0658348",)
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence WHERE report_id IN ('report:ad0658348','pmid:13873988')
        """).fetchone() == (0,)


def test_neurological_archive_preserves_case_selection_and_report_links(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT setting,count(*) FROM publication_liske_case_profile GROUP BY setting ORDER BY setting
        """).fetchall() == [("aircraft", 7), ("chamber", 6)]
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit,analysis_role
            FROM publication_observation
            WHERE source_id='liske67_focal' AND endpoint='focal_neurological_subset'
        """).fetchone() == (13, 37, "dcs_case", "case_conditional")
        assert db.execute("""
            SELECT patient_number,max_cabin_altitude_ft,time_at_max_altitude_min_low,time_at_max_altitude_min_high
            FROM publication_liske_case_profile WHERE patient_number IN (3,6,9) ORDER BY patient_number
        """).fetchall() == [(3, 29000, None, None), (6, None, 30, 30), (9, 19000, 13, 30)]
        assert db.execute("""
            SELECT patient_number,postconvalescent_eeg FROM publication_liske_case_profile
            WHERE persistent_eeg_abnormality_reported='yes' ORDER BY patient_number
        """).fetchall() == [
            (2, "normal"), (7, "diffuse slowing more prominent on the right"), (8, "normal"),
        ]
        assert db.execute("""
            SELECT report_id FROM review.review_study_report WHERE study_id='hook-swedish-1954-chamber-case'
            ORDER BY report_id
        """).fetchall() == [("pmid:13234873",), ("pmid:13563380",)]
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='pmid:13563380' AND right_report='pmid:13234873'
        """).fetchone() == ("same_published_case",)
        assert db.execute("""
            SELECT case_id,report_id,source_time_min FROM historical_case_catalog WHERE source_id GLOB 'hook*'
        """).fetchall() == [("hook58_swedish_chamber:swedish-1954-chamber-index", "pmid:13563380", None)]
        assert db.execute("""
            SELECT elapsed,elapsed_unit,elapsed_reference FROM publication_case_milestone
            WHERE source_id='hook58_swedish_chamber' AND milestone='paralysis_by_ten_minutes'
        """).fetchone() == (10.0, "minutes", "return_to_ground")
        assert db.execute("""
            SELECT milestone,chamber_altitude_ft FROM publication_case_milestone
            WHERE source_id='hook58_swedish_chamber'
                AND milestone IN ('hand_paresthesias_near_peak','reported_chamber_apex')
            ORDER BY milestone
        """).fetchall() == [("hand_paresthesias_near_peak", None), ("reported_chamber_apex", 40000)]
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence
            WHERE report_id IN ('pmid:13234873','pmid:13563380','pmid:14495081','aeme:38:3:304')
        """).fetchone() == (0,)


def test_lewis_case_series_and_nasa_reprints_preserve_original_risk_sets(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_stratum,count(*) FROM publication_lewis_case_profile
            WHERE source_id='lewis72_usaf_flight' GROUP BY source_stratum ORDER BY source_stratum
        """).fetchall() == [("bends_only", 7), ("neurological", 6)]
        assert db.execute("""
            SELECT published_row,cabin_altitude_ft,time_at_altitude_before_onset_min
            FROM publication_lewis_case_profile
            WHERE source_stratum='neurological' AND published_row IN (1,5,6)
            ORDER BY published_row
        """).fetchall() == [(1, 23000, 210), (5, 24000, 53), (6, 19000, 10)]
        assert db.execute("""
            SELECT endpoint,numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id='lewis72_usaf_flight' AND stratum='reported-case-series' ORDER BY endpoint
        """).fetchall() == [("reported_dcs", 14, None, None), ("sufficiently_described_dcs", 13, 14, "dcs_case")]
        assert db.execute("""
            SELECT count(*),sum(numerator),min(denominator),max(denominator) FROM publication_observation
            WHERE source_id='lewis72_usaf_flight' AND stratum='bends-location-occurrences'
        """).fetchone() == (12, 15, 15, 15)
        assert db.execute("""
            SELECT count(DISTINCT report_id),min(report_id) FROM review.review_record
            WHERE lower(title) LIKE 'decompression sickness in usaf operational flying%'
        """).fetchone() == (1, "pmid:4634276")
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE url LIKE '%19730022270%' OR openalex_id='W280567427'
        """).fetchall() == [("openalex:W280567427",)]
        assert db.execute("""
            SELECT report_id FROM model_report_link
            WHERE source_table='publication_source' AND source_id='berry58_training'
        """).fetchone() == ("pmid:13569694",)
        assert db.execute("""
            SELECT source_id,count(*) FROM publication_reported_rate WHERE denominator=51580
            GROUP BY source_id
        """).fetchall() == [("berry58_training", 12)]
        assert db.execute("""
            SELECT count(*) FROM publication_observation
            WHERE source_id IN ('west_parker73_dcs','billings73_barometric') OR denominator=51530
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence WHERE report_id='pmid:4634276'
        """).fetchone() == (0,)


def test_formal_search_flow_and_source_identities(release):
    with connect_pair(release) as db:
        flow, = db.execute("""
            SELECT content_json FROM review.review_workflow_document
            WHERE input_path LIKE '%/prisma-flow.json'
        """).fetchone()
        totals = dict(db.execute("""
            SELECT q.operation, count(*) FROM review.review_retrieval q
            JOIN review.review_record r USING (run_id)
            WHERE json_extract(q.parameters_json, '$.counts_toward_formal_identification') = 1
            GROUP BY q.operation
        """))
        flow = json.loads(flow)
        assert totals["formal_database_search"] == flow["formal_database_records_exported"]
        assert totals["formal_citation_search"] == flow["formal_citation_records_exported"]
        assert sum(totals.values()) == flow["formal_records_exported"]
        assert db.execute("""
            SELECT reported_total, retrieved FROM review.review_retrieval
            WHERE run_id='2026-11-20-formal-chamber-lilacs'
        """).fetchone() == (None, 0)
        assert db.execute("""
            SELECT report_id, doi, json_extract(metadata_json, '$.reported_doi')
            FROM review.review_record
            WHERE record_key='2026-11-20-formal-chamber-openalex#W1898307'
        """).fetchone() == ("pmid:1898307", None, "10.24471/shigaku.115.9_1617")
        assert db.execute("""
            SELECT report_id FROM review.review_record WHERE record_key IN (
                'legacy:data/chamber/v1.17/search_hits.csv#denit_v17_allen:1',
                'legacy:data/chamber/v1.17/sources.csv#allen71_body_fat',
                '2026-11-20-formal-chamber-pubmed#5155138') ORDER BY record_key
        """).fetchall() == [
            ("pmid:5155138",), ("retrieval:fitness-for-divers-scribd-420648411",), ("pmid:5155138",)
        ]


def test_davis_case_crosswalk_and_hbo_endpoint(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT case_id, report_id, source_time_min FROM historical_case_catalog
            WHERE source_id IN ('davis71_neurological', 'lewis72_usaf_flight') ORDER BY case_id
        """).fetchall() == [
            ("davis71_neurological:first-training-flight-case-02", "pmid:5099868", None),
            ("lewis72_usaf_flight:neurological-case-06", "pmid:5099868", None),
        ]
        assert db.execute("""
            SELECT left_report,right_report FROM review.review_report_relation
            WHERE left_report='pmid:5099868' AND relationship='same_published_case'
        """).fetchone() == ("pmid:5099868", "pmid:4634276")
        assert db.execute("""
            SELECT milestone,clock_time,chamber_altitude_ft FROM publication_case_milestone
            WHERE source_id='davis71_neurological'
              AND milestone IN ('paresthesia_at_ascent_pause','apparent_recovery','observed_incoordination')
            ORDER BY clock_time
        """).fetchall() == [
            ("paresthesia_at_ascent_pause", "09:03", 25000),
            ("apparent_recovery", "10:00", None),
            ("observed_incoordination", "10:35", None),
        ]
        assert db.execute("""
            SELECT period, count(*), sum(numerator), sum(denominator) FROM publication_observation
            WHERE source_id='davis77_hyperbaric' AND endpoint='hyperbaric_treated_altitude_dcs'
              AND analysis_role='overlap_hold' GROUP BY period ORDER BY period
        """).fetchall() == [("1973", 4, 7, 63019), ("1974", 4, 19, 65361),
                             ("1975", 4, 30, 55667), ("1976", 4, 14, 58305)]
        assert db.execute("""
            SELECT denominator FROM publication_observation
            WHERE source_id='davis77_hyperbaric' AND stratum='davis77-1974-above_25000_ft-trainee'
        """).fetchone() == (51441,)
        assert db.execute("""
            SELECT denominator_unit, sum(numerator), sum(denominator) FROM publication_observation
            WHERE source_id='davis77_hyperbaric' AND endpoint='hyperbaric_treated_altitude_dcs'
            GROUP BY denominator_unit ORDER BY denominator_unit
        """).fetchall() == [("observer_exposure", 31, 48148), ("trainee_exposure", 39, 194204)]
        mismatch = db.execute("""
            SELECT p.stratum FROM publication_observation p
            LEFT JOIN review.review_search_observation r
              ON (r.observation_id,r.endpoint,r.cases,r.denominator)=
                 (p.stratum,p.endpoint,p.numerator,p.denominator)
              AND r.report_id='pmid:889546' AND r.study_id='usaf-1973-1976-treated'
              AND r.denominator_unit='chamber_exposures'
              AND p.denominator_unit=CASE r.chamber_role
                WHEN 'staff' THEN 'observer_exposure' WHEN 'trainee' THEN 'trainee_exposure' END
            WHERE p.source_id='davis77_hyperbaric' AND p.endpoint='hyperbaric_treated_altitude_dcs'
              AND r.record_key IS NULL
        """).fetchall()
        assert mismatch == []
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE report_id='pmid:889546' AND endpoint='hyperbaric_treated_altitude_dcs'
        """).fetchone() == (16,)
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence WHERE report_id='pmid:889546'
        """).fetchone() == (0,)


def test_operator_history_and_treatment_archive_keep_distinct_denominators(release):
    with connect_pair(release) as db:
        for pattern, expected in (("%-chamber-hours-%", 15), ("%-age-%", 9)):
            assert db.execute("""
                SELECT count(*),sum(numerator),sum(denominator)
                FROM publication_observation
                WHERE source_id='hodgson68_operator_followup' AND stratum LIKE ?
                  AND analysis_role='overlapping_margin' AND denominator_unit='person'
            """, (pattern,)).fetchone() == (expected, 107, 164)
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='hodgson68_operator_followup'
              AND stratum='hodgson-1966-chamber-hours-not-given'
        """).fetchone() == (5, 8)
        assert db.execute("""
            SELECT count(*),sum(numerator),min(denominator),max(denominator)
            FROM publication_observation WHERE source_id='hodgson68_operator_followup'
              AND endpoint='self_reported_episode_category' AND denominator_unit='symptom_report'
        """).fetchone() == (5, 571, 571, 571)
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE report_id='pmid:5658347' AND cases=107 AND denominator=164
        """).fetchone() == (1,)
        assert db.execute("""
            SELECT json_extract(metadata_json,'$.chamber_hours_conflict.table_i_above_20000_ft'),
                   json_extract(metadata_json,'$.chamber_hours_conflict.table_v_sum')
            FROM review.review_record WHERE source_key='5658347-full-text' AND report_id='pmid:5658347'
        """).fetchone() == (27724, 27575)
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit,analysis_role
            FROM publication_observation WHERE source_id='heimbach76_usaf_hyperbaric'
            ORDER BY stratum
        """).fetchall() == [(11, 127, "treated_referral", "overlap_hold"),
                             (11, 11, "treated_referral", "case_conditional"),
                             (80, None, None, "overlap_hold")]
        assert db.execute("""
            SELECT left_report,right_report FROM review.review_report_relation
            WHERE left_report='report:ada036031' AND relationship='likely_overlapping_treated_case_series'
        """).fetchone() == ("report:ada036031", "pmid:889546")
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id),min(report_id) FROM review.review_record
            WHERE url LIKE '%ADA036031.pdf'
        """).fetchone() == (6, 1, "report:ada036031")
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence WHERE report_id IN ('pmid:5658347','report:ada036031')
        """).fetchone() == (0,)


def test_katuntsev_program_total_reuses_source_and_retains_nested_endpoints(release):
    with connect_pair(release) as db:
        report_id = "record:legacy:data/chamber/v1.21/search_hits.csv#prog_v21_russian_author:1"
        assert db.execute("""
            SELECT l.report_id, s.note LIKE '%931 ascents with DCS symptoms%'
            FROM publication_source s JOIN model_report_link l USING(source_id)
            WHERE s.source_id='katuntsev96_human' AND l.source_table='publication_source'
        """).fetchone() == (report_id, 1)
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id) FROM review.review_record
            WHERE url LIKE '%vysotnaya-dekompressionnaya-bolezn-eksperimentalnoe%'
        """).fetchone() == (4, 1)
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit,analysis_role FROM publication_observation
            WHERE source_id='katuntsev96_human' AND stratum='program-all-chamber-ascents'
        """).fetchone() == (931, 1778, "person_exposure", "overlap_hold")
        assert db.execute("""
            SELECT sum(numerator),min(denominator),max(denominator) FROM publication_observation
            WHERE source_id='katuntsev96_human' AND endpoint IN
                ('dcs_main_altitude_phase_source','dcs_additional_decompression_phase_source')
              AND denominator_unit='dcs_case' AND analysis_role='overlapping_margin'
        """).fetchone() == (931, 931, 931)
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id='katuntsev96_human' AND stratum='program-intense-symptoms'
        """).fetchone() == (562, 931, "dcs_case")
        assert db.execute("""
            SELECT endpoint,numerator,denominator FROM publication_observation
            WHERE source_id='katuntsev96_human' AND stratum='selected-8100-9000m-experiments'
            ORDER BY endpoint
        """).fetchall() == [("dcs_lower_limb_pain_source", 174, 228), ("vge_detected_source", 212, 228)]
        assert db.execute("""
            SELECT count(*) FROM publication_observation p
            JOIN review.review_search_observation r
              ON (r.observation_id,r.endpoint,r.cases,r.denominator,r.denominator_unit)=
                 ('katuntsev96-' || p.stratum || '-' || p.endpoint,p.endpoint,
                  p.numerator,p.denominator,p.denominator_unit)
            WHERE p.source_id='katuntsev96_human' AND r.report_id=?
        """, (report_id,)).fetchone() == (9,)
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE report_id=? AND denominator=1778
        """, (report_id,)).fetchone() == (1,)
        assert db.execute("""
            SELECT json_extract(metadata_json,'$.issue_as_reported_by_dissertation'),
                   json_extract(metadata_json,'$.issue_as_reported_by_grigorev_2015')
            FROM review.review_record
            WHERE report_id='cited:katuntsev-shcherbakova-1994-pulmonary-dcs'
        """).fetchall() == [("5", "3")]
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence WHERE report_id=?
        """, (report_id,)).fetchone() == (0,)


def test_lunar_case_timelines_link_to_existing_nasa_trial_outcomes(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT p.case_number,p.trial_stratum,p.trial_endpoint,p.linkage,p.nominal_target_psia,
                   p.prebreathe_min,o.numerator,o.denominator,o.target_pressure_kpa
            FROM publication_trial_case_profile p JOIN discovery_observation o
              ON (o.source_id,o.stratum,o.endpoint)=(p.trial_source_id,p.trial_stratum,p.trial_endpoint)
            WHERE p.source_id='lam26_nasa_neuro' AND p.trial_source_id='garbino_ea34'
            ORDER BY p.case_number
        """).fetchall() == [
            (1, "90-min-prebreathe", "dcs_neurological", "likely_same_episode", 4.3, 90, 1, 5, 29.6),
            (2, "20-min-prebreathe", "dcs_type_ii_source", "likely_same_episode", 5.2, 20, 1, 16, None),
        ]
        assert db.execute("""
            SELECT case_number,count(*) FROM publication_trial_case_milestone
            WHERE source_id='lam26_nasa_neuro' GROUP BY case_number ORDER BY case_number
        """).fetchall() == [(1, 4), (2, 7)]
        assert db.execute("""
            SELECT event_type,elapsed_from_target_min,time_basis FROM publication_trial_case_milestone
            WHERE source_id='lam26_nasa_neuro' AND case_number=2
              AND milestone IN ('transient_tingling_reported','next_day_neurological_exam') ORDER BY milestone
        """).fetchall() == [("followup_exam", None, "next_day"), ("symptom_report", 7, "approximate_target_elapsed")]
        assert db.execute("""
            SELECT decision,accepted_value FROM discovery_adjudication WHERE issue_id='ea34-target-pressure'
        """).fetchone() == ("unresolved", None)
        for doc_id in ("20260004151", "20240013238"):
            assert db.execute("""
                SELECT count(*),count(DISTINCT report_id) FROM review.review_record WHERE url LIKE ?
            """, (f"%{doc_id}%",)).fetchone() == (3, 1)
        assert db.execute("""
            SELECT json_array_length(metadata_json,'$.case_profiles'),
                   json_array_length(metadata_json,'$.case_milestones')
            FROM review.review_record WHERE source_key='ntrs-20260004151-v2'
        """).fetchone() == (2, 11)
        assert db.execute("""
            SELECT count(*),sum(numerator),count(denominator) FROM discovery_observation
            WHERE source_id='garbino_ea34'
        """).fetchone() == (3, 2, 3)
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='lam26_nasa_neuro'
        """).fetchone() == (0,)


def test_nasa_ea_presentation_completes_original_risk_sets_and_exposes_attrition(release):
    with connect_pair(release) as db:
        source = "garbino_ea345_slides"
        expected = [
            (20, 5.2, 16, 16, 1, 2), (50, 5.2, 21, 19, 0, 3),
            (90, 4.3, 5, 5, 1, 1), (150, 4.3, 24, 24, 0, 5),
        ]
        assert db.execute("""
            SELECT prebreathe_min,target_pressure_psia,
                   sum(participating_exposures),sum(evaluated_exposures),sum(cases),count(*)
            FROM discovery_eva_session WHERE source_id=?
            GROUP BY prebreathe_min,target_pressure_psia ORDER BY prebreathe_min
        """, (source,)).fetchall() == expected
        assert db.execute("""
            SELECT participating_exposures,evaluated_exposures,cases
            FROM discovery_eva_session WHERE source_id=? AND test_number=4 AND eva_number=4
        """, (source,)).fetchone() == (7, 5, 0)
        assert db.execute("""
            SELECT o.stratum,o.endpoint,o.numerator,o.denominator,c.target_pressure_psia
            FROM discovery_observation o
            JOIN discovery_observation_completion c USING (source_id,stratum,endpoint)
            WHERE o.source_id='garbino_ea34' AND c.evidence_source_id=?
            ORDER BY o.stratum
        """, (source,)).fetchall() == [
            ("150-min-prebreathe", "dcs", 0, 24, 4.3),
            ("20-min-prebreathe", "dcs_type_ii_source", 1, 16, 5.2),
            ("90-min-prebreathe", "dcs_neurological", 1, 5, 4.3),
        ]
        assert db.execute("""
            SELECT stratum,endpoint,numerator,denominator,analysis_role
            FROM discovery_observation WHERE source_id=?
        """, (source,)).fetchall() == [("50-min-5-2-psia-ea4-ea5", "dcs", 0, 19, "overlapping_margin")]
        assert db.execute("""
            SELECT reported_group,endpoint,cases,denominator,denominator_unit,role_review
            FROM review.review_search_observation
            WHERE run_id='2026-11-21-nasa-ea-protocol-denominators-verified'
                AND report_id='ntrs:20250004535'
            ORDER BY reported_group
        """).fetchall() == [
            ("150-min-prebreathe", "dcs", 0, 24, "person_exposure", "overlap_hold"),
            ("20-min-prebreathe", "dcs_type_ii_source", 1, 16, "person_exposure", "overlap_hold"),
            ("50-min-5-2-psia-ea4-ea5", "dcs", 0, 19, "person_exposure", "overlap_hold"),
            ("90-min-prebreathe", "dcs_neurological", 1, 5, "person_exposure", "overlap_hold"),
        ]
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='ntrs:20250004535'
                AND right_report='record:legacy:data/chamber/v1.6/sources.csv#garbino_ea34'
        """).fetchone() == ("partial_overlap",)


def test_nasa_prp_counts_preserve_three_overlapping_analysis_populations(release):
    with connect_pair(release) as db:
        db.row_factory = sqlite3.Row
        counts = db.execute("""
            SELECT * FROM publication_prp_analysis_counts WHERE source_id='nasa04_exercise' ORDER BY phase
        """).fetchall()
        assert [tuple(row)[1:9] for row in counts] == [
            ("I", 49, 47, 9, 47, 9, 49, 7),
            ("II", 50, 45, 0, 45, 0, 47, 0),
            ("III", 10, 9, 2, 4, 2, 9, 2),
            ("IV", 65, 56, 8, 3, 0, 62, 8),
            ("V-1", 10, 9, 3, 9, 3, 9, 3),
            ("V-2", 4, 3, 1, 3, 1, 3, 1),
            ("V-3", 50, 48, 7, 48, 7, 50, 7),
        ]
        report_id, review_counts, nedu_exposures, nedu_weighted_dcs = db.execute("""
            SELECT r.report_id,json_extract(r.metadata_json,'$.table_6_analysis_populations'),
                   json_extract(r.metadata_json,'$.phase_iv_crosswalk.nedu_exposures'),
                   json_extract(r.metadata_json,'$.phase_iv_crosswalk.nedu_weighted_dcs')
            FROM review.review_record r JOIN model_report_link m USING (report_id)
            WHERE r.source_key='ntrs-20040191712-table-6' AND m.source_table='sharepoint_source'
              AND m.source_id='nasa04_exercise'
        """).fetchone()
        assert [dict(row) for row in counts] == json.loads(review_counts)
        assert (nedu_exposures, nedu_weighted_dcs) == (69, 8.3)
        prp_occurrences, first_report, last_report = db.execute("""
            SELECT count(*),min(report_id),max(report_id) FROM review.review_record
            WHERE url LIKE '%20040191712%' OR openalex_id='W118136854'
        """).fetchone()
        assert prp_occurrences >= 6
        assert first_report == last_report == report_id
        assert db.execute("SELECT count(*) FROM chamber_group_evidence WHERE report_id=?", (report_id,)).fetchone()[0] == 0


def test_duke_trials_preserve_distinct_enrollment_without_inferred_outcomes(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT s.study_id,r.report_id,json_extract(r.metadata_json,'$.registered_enrollment.count'),
                   json_extract(r.metadata_json,'$.registered_enrollment.type'),
                   json_extract(r.metadata_json,'$.duke_protocol'),
                   json_extract(r.metadata_json,'$.has_results'),
                   json_extract(r.metadata_json,'$.evaluable_person_exposures'),
                   json_extract(r.metadata_json,'$.observed_cases')
            FROM review.review_study_report s JOIN review.review_record r USING (report_id)
            WHERE r.source_key IN ('NCT06740305','NCT07702539') ORDER BY s.study_id
        """).fetchall() == [
            ("duke-nct06740305", "nct:NCT06740305", 19, "ACTUAL", "Pro00116846", 0, None, None),
            ("duke-nct07702539", "nct:NCT07702539", 30, "ESTIMATED", "Pro00120426", 0, None, None),
        ]
        assert db.execute("""
            SELECT report_id FROM review.review_record WHERE url='https://ctv.veeva.com/study/nasa-prebreathe-study'
        """).fetchone() == ("nct:NCT06740305",)
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation WHERE report_id IN ('nct:NCT06740305','nct:NCT07702539')
        """).fetchone() == (0,)


def test_left_heart_gas_case_crosswalk_preserves_source_discrepancies(release):
    with connect_pair(release) as db:
        db.row_factory = sqlite3.Row
        cases = db.execute("SELECT * FROM publication_left_heart_gas_case ORDER BY case_number").fetchall()
        assert [
            (r["case_number"], r["journal_altitude_ft"], r["journal_detection_min"],
             r["workshop_altitude_ft"], r["workshop_detection_min"], r["linkage"])
            for r in cases
        ] == [
            (1, 25000, 153, 25500, 143, "likely_with_discrepancies"),
            (2, 29500, 27, 29000, 27, "likely_with_discrepancies"),
            (3, 19500, 229, 19500, 229, "altitude_and_time_match"),
            (4, 29500, 195, 29500, 195, "altitude_and_time_match"),
            (5, 29500, 91, 29500, 91, "altitude_and_time_match"),
            (6, 25000, 216, None, None, "journal_only"),
        ]
        assert cases[2]["journal_symptoms"] is None
        assert cases[3]["vge_left_leg"] == 3
        assert all(row["vge_right_leg"] == 4 for row in cases)
        review_profiles, = db.execute("""
            SELECT json_extract(r.metadata_json,'$.case_profiles') FROM review.review_record r
            JOIN model_report_link m USING (report_id)
            WHERE r.source_key='8908349-full-table' AND m.source_id='pilmanis96_age'
        """).fetchone()
        assert [dict(r) for r in cases] == json.loads(review_profiles)


def test_soar_counts_preserve_distinct_endpoints_and_overlapping_denominators(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT o.stratum,o.endpoint,o.numerator,o.denominator,o.denominator_unit,o.analysis_role
            FROM publication_observation o JOIN model_report_link m USING (source_id)
            JOIN review.review_search_observation r
              ON r.report_id=m.report_id AND (r.reported_group,r.endpoint)=(o.stratum,o.endpoint)
              AND (r.cases,r.denominator,r.denominator_unit)=(o.numerator,o.denominator,o.denominator_unit)
            WHERE o.source_id IN ('pilmanis93_soar_age','pilmanis96_age','powell93_soar_joint','norfleet93_soar_tcd')
            ORDER BY o.stratum
        """).fetchall() == [
            ("journal-first-to-sixth-detection", "left_ventricular_gas_detected", 6, 369, "person_exposure", "overlap_hold"),
            ("journal-six-detections", "symptoms_at_left_ventricular_gas_detection", 5, 6, "person", "case_conditional"),
            ("jsc-dcs-cases-with-site", "dcs_first_ankle_knee_or_hip", 73, 88, "dcs_case", "case_conditional"),
            ("jsc-doppler-grade-iii-or-higher", "arterial_bubbles_detected", 1, 13, "person", "overlap_hold"),
            ("jsc-resting-pfo", "spencer_grade_iv_venous_bubbles", 2, 3, "person", "overlapping_margin"),
            ("soar-five-detections", "symptoms_at_left_ventricular_gas_detection", 4, 5, "person", "case_conditional"),
            ("soar-three-protocols", "left_ventricular_gas_detected", 5, 79, "person_exposure", "overlap_hold"),
        ]
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence
            WHERE report_id IN ('ntrs:19940007071','pmid:8908349','openalex:W808314617','openalex:W650078426')
        """).fetchone() == (0,)


def test_argo_doppler_pairs_link_to_existing_arms_and_preserve_missingness(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT a.arm,a.reported_doppler_n,a.reported_any_vge,a.reported_grade_iv,
                   n.test_id,n.dcs_cases,n.dcs_denominator,n.any_grade_vge_cases,n.grade_iv_vge_cases
            FROM publication_argo_phase_i_arm a JOIN nasa_test n ON n.test_id=a.nasa_test_id
            ORDER BY a.arm
        """).fetchall() == [
            ("ambulatory", 24, 12, 7, "9a", 1, 24, 12, 7),
            ("bed_rest", 22, 5, 1, "9b", 2, 23, 6, 1),
        ]
        assert db.execute("""
            SELECT count(*),sum(ambulatory_grade>0),sum(bed_rest_grade>0),
                   sum(ambulatory_grade>0 AND bed_rest_grade=0)
            FROM publication_argo_phase_i_doppler
            WHERE ambulatory_grade IS NOT NULL AND bed_rest_grade IS NOT NULL
        """).fetchone() == (20, 11, 5, 6)
        assert db.execute("""
            SELECT count(*),count(ambulatory_grade),count(bed_rest_grade),
                   count(ambulatory_tcd_bubbles),sum(ambulatory_tcd_bubbles),count(bed_rest_tcd_bubbles),
                   sum(bed_rest_tcd_bubbles),sum(saline_contrast_status='resting_arterialization'),
                   sum(saline_contrast_status IN ('resting_arterialization','no_arterialization'))
            FROM publication_argo_phase_i_doppler
        """).fetchone() == (27, 24, 21, 10, 1, 5, 0, 4, 14)
        assert db.execute("""
            SELECT c.finding,a.nasa_test_id,c.roster_row,d.ambulatory_tcd_bubbles,d.bed_rest_status,d.bed_rest_grade
            FROM publication_argo_phase_i_clinical c JOIN publication_argo_phase_i_arm a USING (source_id,arm)
            LEFT JOIN publication_argo_phase_i_doppler d USING (source_id,roster_row)
            ORDER BY c.finding
        """).fetchall() == [
            ("mild_joint_pain_dcs", "9b", None, None, None, None),
            ("rash_and_orthostatic_instability", "9b", 21, None, "atypical_signal", None),
            ("source_type_ii_dcs", "9a", 8, 1, "withdrawn", None),
        ]
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE endpoint IN ('dcs_first_ankle_knee_or_hip','arterial_bubbles_detected','spencer_grade_iv_venous_bubbles')
              AND report_id IN ('openalex:W808314617','openalex:W650078426','ntrs:19940006763')
        """).fetchone() == (3,)
        db.row_factory = sqlite3.Row
        raw, = db.execute("""
            SELECT r.metadata_json FROM review.review_record r JOIN model_report_link m USING (report_id)
            WHERE r.source_key='19940006763' AND m.source_id='powell93_argo'
        """).fetchone()
        for table, field, key in (
            ("publication_argo_phase_i_arm", "phase_i_arms", "arm"),
            ("publication_argo_phase_i_doppler", "doppler_roster", "roster_row"),
            ("publication_argo_phase_i_clinical", "clinical_findings", "finding"),
        ):
            rows = [dict(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY {key}")]
            assert rows == sorted(json.loads(raw)[field], key=lambda row: row[key])


def test_duke_posture_counts_preserve_endpoints_and_monitoring_denominators(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT o.stratum,o.endpoint,o.numerator,o.denominator,o.analysis_role
            FROM publication_observation o JOIN model_report_link m USING (source_id)
            JOIN review.review_search_observation r
              ON r.report_id=m.report_id AND (r.reported_group,r.endpoint)=(o.stratum,o.endpoint)
              AND (r.cases,r.denominator,r.denominator_unit)=(o.numerator,o.denominator,o.denominator_unit)
            WHERE r.study_id='duke-altitude-posture-vann-gerth-1997'
            ORDER BY o.stratum,o.endpoint
        """).fetchall() == [
            ("duke-reclining", "arm_dcs", 2, 18, "overlapping_margin"),
            ("duke-reclining", "arm_doppler_grade_gt_ii", 3, 18, "overlapping_margin"),
            ("duke-reclining", "dcs_source_defined", 3, 18, "overlap_hold"),
            ("duke-reclining", "leg_dcs", 1, 18, "overlapping_margin"),
            ("duke-reclining", "leg_doppler_grade_gt_ii", 1, 18, "overlapping_margin"),
            ("duke-standing", "arm_dcs", 2, 19, "overlapping_margin"),
            ("duke-standing", "arm_doppler_grade_gt_ii", 1, 18, "overlapping_margin"),
            ("duke-standing", "dcs_source_defined", 12, 19, "overlap_hold"),
            ("duke-standing", "leg_dcs", 10, 19, "overlapping_margin"),
            ("duke-standing", "leg_doppler_grade_gt_ii", 8, 18, "overlapping_margin"),
        ]
        assert db.execute("""
            SELECT report_id FROM model_report_link WHERE source_id='conkin01_lba'
        """).fetchone() == ("pmid:11277286",)
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence WHERE study_id='duke-altitude-posture-vann-gerth-1997'
        """).fetchone() == (0,)


def test_argo_table_ii_keeps_named_and_unresolved_archive_links(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT a.arm,l.nasa_test_id,l.status,a.exposures,a.dcs_cases,a.vge_cases,n.any_grade_vge_cases
            FROM publication_lba_argo_arm a JOIN publication_lba_argo_test_link l USING(source_id,arm)
            JOIN nasa_test n ON n.test_id=l.nasa_test_id
            ORDER BY a.arm,l.nasa_test_id
        """).fetchall() == [
            ("phase-i-ambulatory", "9a", "matched_named_arm", 24, 1, 12, 12),
            ("phase-i-reclining", "9b", "matched_named_arm", 23, 2, 6, 6),
            ("phase-ii-adynamia", "9d", "candidate_arm", 7, 0, 2, 2),
            ("phase-ii-adynamia", "9e", "candidate_arm", 7, 0, 2, 2),
            ("phase-ii-ambulatory", "9c", "matched_named_arm", 11, 3, 5, 5),
            ("phase-iii-adynamia", "11a", "matched_named_arm", 28, 3, 7, 9),
        ]
        db.row_factory = sqlite3.Row
        raw, = db.execute("""
            SELECT metadata_json FROM review.review_record WHERE source_key='11277286-table-ii'
        """).fetchone()
        for table, field in (
            ("publication_lba_argo_arm", "argo_table_ii"),
            ("publication_lba_argo_test_link", "argo_table_ii_test_links"),
        ):
            assert [dict(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY rowid")] == json.loads(raw)[field]


def test_vann_appendix_partitions_link_to_existing_flight_total(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT count(*),sum(g.printed_exposures),sum(g.dcs_cases),max(o.denominator),max(o.cases)
            FROM publication_vann04_flight_group g JOIN cohort_observation o
              ON (g.source_id,g.parent_stratum,g.parent_endpoint)=(o.source_id,o.stratum,o.endpoint)
            WHERE o.source_id='vann04' AND o.exposure_context='post_dive_hypobaric'
        """).fetchone() == (30, 802, 40, 802, 40)
        assert db.execute("""
            SELECT g.profile,g.preflight_surface_interval_hours,g.dcs_cases,count(c.case_number)
            FROM publication_vann04_flight_group g LEFT JOIN publication_vann04_case c
              USING (source_id,profile,preflight_surface_interval_hours)
            GROUP BY g.source_id,g.profile,g.preflight_surface_interval_hours
            HAVING g.dcs_cases != count(c.case_number)
        """).fetchall() == []
        assert db.execute("""
            SELECT printed_exposures,dcs_cases,printed_dcs_percent FROM publication_vann04_flight_group
            WHERE profile='repeat-60-55-60-20-60-20' AND preflight_surface_interval_hours=14
        """).fetchone() == (10, 1, 9.1)
        assert db.execute("""
            SELECT count(*),sum(printed_exposures),sum(dcs_cases) FROM publication_vann04_flight_group
            WHERE preflight_surface_interval_hours=17
        """).fetchone() == (2, 52, 0)
        assert db.execute("""
            SELECT onset_phase,count(*) FROM publication_vann04_case GROUP BY onset_phase ORDER BY onset_phase
        """).fetchall() == [("chamber_exit", 1), ("in_flight", 23), ("post_flight", 16)]
        assert db.execute("""
            SELECT case_number,reported_onset_min,first_dive_bottom_min_override,linked_appendix_a_case
            FROM publication_vann04_case WHERE case_number IN (1,13,36,37,40) ORDER BY case_number
        """).fetchall() == [
            (1, None, None, None), (13, None, None, None), (36, 240, 12, None),
            (37, 138, 12, None), (40, 150, None, 11),
        ]
        assert db.execute("""
            SELECT report_id FROM model_report_link WHERE source_id='vann04' AND source_table='cohort_source'
        """).fetchone() == ("pmid:15686274",)
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence WHERE report_id='pmid:15686274'
        """).fetchone() == (0,)


def test_vann_appendix_case_metadata_matches_model_data(release):
    with connect_pair(release) as db:
        db.row_factory = sqlite3.Row
        raw, = db.execute("""
            SELECT metadata_json FROM review.review_record WHERE source_key='vann-2004-appendix-b'
        """).fetchone()
        for table, field in (
            ("publication_vann04_dive_profile", "dive_profiles"),
            ("publication_vann04_flight_group", "flight_groups"),
            ("publication_vann04_case", "case_profiles"),
        ):
            assert [dict(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY rowid")] == json.loads(raw)[field]


def test_israeli_case_rows_reuse_existing_chamber_and_flight_counts(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT c.exposure_stratum,count(*),a.cases,a.denominator,a.denominator_unit
            FROM publication_iaf_adcs_case c JOIN aviation_count a
              ON (a.source_id,a.stratum)=(c.source_id,c.exposure_stratum)
            GROUP BY c.exposure_stratum ORDER BY c.exposure_stratum
        """).fetchall() == [
            ("chamber", 11, 11, 2279, "trainees_instructors_unresolved"),
            ("flight", 4, 4, None, "unreported"),
        ]
        assert db.execute("""
            SELECT count(*),sum(reported_tail_treatments>0),sum(reported_tail_treatments)
            FROM publication_iaf_adcs_case WHERE reported_treatment IN ('USNTT5','USNTT6')
        """).fetchone() == (13, 7, 10)
        assert db.execute("""
            SELECT case_number,reported_treatment,reported_tail_treatments FROM publication_iaf_adcs_case
            WHERE case_number IN (2,7,9) ORDER BY case_number
        """).fetchall() == [(2, "USNTT5", 0), (7, None, None), (9, "100% oxygen", None)]
        db.row_factory = sqlite3.Row
        raw, = db.execute("""
            SELECT metadata_json FROM review.review_record WHERE source_key='benari-2026-table-2'
        """).fetchone()
        assert [dict(row) for row in db.execute("""
            SELECT * FROM publication_iaf_adcs_case ORDER BY case_number
        """)] == json.loads(raw)["case_rows"]


def test_old_vestibular_episode_is_counted_once_and_keeps_conflicting_gain(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT report_id,source_time_min,first_assessment_min FROM historical_case_catalog
            WHERE source_id IN ('nachum99_iedcs','shupak97_iedcs')
        """).fetchall() == [("pmid:10608608", 20, 360)]
        assert db.execute("""
            SELECT milestone,elapsed,elapsed_reference FROM publication_case_milestone
            WHERE source_id='nachum99_iedcs' AND elapsed IS NOT NULL ORDER BY elapsed
        """).fetchall() == [
            ("joint_and_headache_onset", 20, "after_descent"),
            ("vestibular_symptom_onset", 210, "after_descent"),
            ("first_examination", 360, "after_exposure_completion"),
            ("first_recompression", 720, "after_descent"),
        ]
        assert db.execute("""
            SELECT reporting_source_id,note LIKE '%normal gain%',note LIKE '%low gain%'
            FROM publication_case_milestone WHERE source_id='nachum99_iedcs'
            AND milestone LIKE 'three_month_%' ORDER BY milestone
        """).fetchall() == [("shupak97_iedcs", 1, 0), ("nachum99_iedcs", 0, 1)]
        assert db.execute("""
            SELECT count(*),coalesce(sum(cases),0),count(denominator) FROM review.review_search_observation
            WHERE study_id='israel-vestibular-chamber-case-reported-1997'
        """).fetchone() == (1, 1, 0)


def test_u2_flight_episodes_preserve_pilot_linkage_and_symptom_time_origin(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_id,report_pilot_key,episode_sequence,reported_year,
                   approximate_interval_from_prior_episode_months,first_symptom_phase,
                   approximate_onset_min_low,approximate_onset_min_high,onset_reference
            FROM publication_u2_episode ORDER BY source_id,episode_sequence
        """).fetchall() == [
            ("jersey10_u2_case", "index-pilot", 1, 2006, None, "in_flight", 150, 150, "from_flight_start"),
            ("pickard03_u2_case", "index-pilot", 1, 2002, None, "in_flight", 240, 300, "from_flight_start"),
            ("rhodes97_u2_pfo", "index-pilot", 1, None, None, "in_flight", None, None, None),
            ("rhodes97_u2_pfo", "index-pilot", 2, None, 6, "in_flight", None, None, None),
        ]
        assert db.execute("""
            SELECT count(*),sum(numerator),count(denominator),count(source_time_min)
            FROM publication_u2_episode u
            JOIN publication_observation p USING(source_id,stratum,endpoint)
            JOIN historical_case_catalog c ON c.case_id=u.source_id || ':' || u.stratum
            WHERE p.analysis_role='selected_cluster'
        """).fetchone() == (4, 4, 0, 0)
        assert db.execute("""
            SELECT elapsed,elapsed_unit,elapsed_reference
            FROM publication_case_milestone
            WHERE source_id='pickard03_u2_case' AND milestone='clinical_notification'
        """).fetchone() == (18, "hours", "after_landing")
        assert db.execute("""
            SELECT count(*),min(report_id),count(DISTINCT report_id) FROM review.review_record
            WHERE lower(title) LIKE '%severe neurological decompression sickness in a u-2 pilot%'
        """).fetchone() == (9, "pmid:20058739", 1)
        assert db.execute("""
            SELECT left_report,relationship FROM review.review_report_relation
            WHERE right_report='pmid:23066619'
            AND relationship IN ('possible_cohort_overlap','cited_case_in_surveillance')
            ORDER BY left_report
        """).fetchall() == [
            ("abstract:asma-1997-rhodes-141", "possible_cohort_overlap"),
            ("pmid:12688456", "cited_case_in_surveillance"),
            ("pmid:20058739", "cited_case_in_surveillance"),
        ]
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE report_id='dtic:ada526033'
        """).fetchone() == (0,)


def test_u2_case_series_rows_reconcile_footnotes_and_preserve_case_overlap(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_table,count(*),count(DISTINCT pilot_code),
                   sum(cns_certainty='confirmed'),sum(cns_certainty='probable'),
                   coalesce(sum(additional_confirmed_cns_from_footnote),0)
            FROM publication_u2_series_row GROUP BY source_table ORDER BY source_table
        """).fetchall() == [("I", 17, 16, 13, 4, 3), ("II", 6, 5, 3, 1, 0)]
        assert db.execute("""
            SELECT source_table,source_row,physiological_altitude_ft,altitude_relation,
                   exposure_hours,exposure_relation
            FROM publication_u2_series_row
            WHERE (source_table='II' AND source_row IN (1,3)) OR pilot_code='MP6'
            ORDER BY source_table,source_row
        """).fetchall() == [
            ("I", 6, 25000, "greater_than", 6.0, "reported_point"),
            ("II", 1, 25000, "greater_than", 8.0, "greater_than"),
            ("II", 3, None, None, None, None),
        ]
        assert db.execute("""
            SELECT pilot_code,cns_certainty,case_source_id,linkage FROM publication_u2_series_case_link
            JOIN publication_u2_series_row USING(source_id,source_table,source_row)
            ORDER BY source_row
        """).fetchall() == [
            ("MP1", "confirmed", "pickard03_u2_case", "possible"),
            ("MP7", "confirmed", "jersey10_u2_case", "likely"),
        ]
        assert db.execute("""
            SELECT count(*),sum(numerator),min(denominator),max(denominator)
            FROM publication_observation WHERE source_id='jersey11_u2_series'
            AND endpoint='source_cns_symptom_recognition' AND denominator_unit='dcs_case'
        """).fetchone() == (4, 20, 20, 20)
        assert db.execute("""
            SELECT analysis_role,numerator,denominator FROM publication_observation
            WHERE source_id='jersey11_u2_series' AND endpoint='source_confirmed_cns_dcs'
            ORDER BY stratum
        """).fetchall() == [("case_conditional", 16, 45), ("case_conditional", 3, 24)]
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id)
            FROM review.review_record WHERE report_id='pmid:21748904'
        """).fetchone() == (7, 1)
        assert db.execute("""
            SELECT count(*) FROM historical_case_catalog WHERE source_id='jersey11_u2_series'
        """).fetchone() == (0,)


def test_chamber_training_histories_use_original_peak_and_preserve_denominator(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_id,altitude,prebreathe_min,numerator,denominator,analysis_role
            FROM publication_observation WHERE source_id='allan03'
        """).fetchall() == [("allan03", 26000.0, None, 3, None, "selected_cluster")]
        assert db.execute("""
            SELECT study_day,altitude_ft,duration_min FROM publication_allan_chamber_plateau
            ORDER BY order_in_description
        """).fetchall() == [(1, 26000, 33), (1, 18000, 18), (3, 26000, 24)]
        assert db.execute("""
            SELECT patient_label,self_reported_resolution_min_from_hbot_start
            FROM publication_allan_dci_case JOIN publication_observation USING(source_id,stratum,endpoint)
            WHERE source_id='allan03' ORDER BY patient_label
        """).fetchall() == [("A", 90), ("B", 60), ("C", 120)]
        assert db.execute("""
            SELECT endpoint,cases,denominator,reported_rate FROM review.review_search_observation
            WHERE report_id='report:dtic-adp011075'
        """).fetchall() == [("source_reported_broad_dysbarism", None, None, 10)]
        assert db.execute("""
            SELECT l.report_id,s.access
            FROM publication_source s JOIN model_report_link l USING(source_id)
            WHERE s.source_id='dosel01_sazel_chamber'
        """).fetchone() == ("report:dtic-adp011075", "full_text")
        assert db.execute("""
            SELECT count(*) FROM historical_case_catalog
            WHERE source_id IN ('allan03','dosel01_sazel_chamber')
        """).fetchone() == (0,)


def test_halo_nested_counts_and_usaf_timing_margin_remain_source_specific(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator,analysis_role,prebreathe_min
            FROM publication_observation
            WHERE source_id='piwinski86_halo' AND endpoint='dcs' ORDER BY stratum
        """).fetchall() == [
            ("halo-profile-experience", 4, 27, "overlapping_margin", None),
            ("single-halo-training-flight", 4, 9, "selected_cluster", 30),
        ]
        assert db.execute("""
            SELECT case_number,printed_type,reported_onset_clock
            FROM publication_piwinski_halo_case ORDER BY case_number
        """).fetchall() == [(1, "II", "06:00"), (2, "I", None), (3, "II", "03:00"), (4, "II", None)]
        assert db.execute("""
            SELECT endpoint,sum(numerator),count(denominator) FROM publication_observation
            WHERE source_id='neubauer88_pulmonary' AND stratum LIKE 'table-ii-19%'
            GROUP BY endpoint ORDER BY endpoint
        """).fetchall() == [("source_delayed_symptoms", 122, 0), ("source_inflight_symptoms", 64, 0)]
        assert db.execute("""
            SELECT p.numerator,p.denominator,p.analysis_role,r.reported_rate,r.reported_rate_unit
            FROM publication_observation p JOIN review.review_search_observation r
            ON r.report_id='pmid:3240220' AND r.observation_id=p.stratum
            WHERE p.source_id='neubauer88_pulmonary' AND p.stratum='table-ii-student-total'
        """).fetchone() == (186, 178305, "overlap_hold", 105, "cases per 100,000 student exposures")
        assert db.execute("""
            SELECT source_id,report_id,source_time_min FROM historical_case_catalog
            WHERE source_id IN ('neubauer88_pulmonary','usaf_aib_c17_2023') ORDER BY source_id
        """).fetchall() == [
            ("neubauer88_pulmonary", "pmid:3240220", None),
            ("usaf_aib_c17_2023", "aib:usaf-c17-2023-08-21", None),
        ]
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation WHERE report_id='amc:3740477'
        """).fetchone() == (0,)


def test_prp_pfo_and_headache_outcomes_keep_person_and_case_denominators(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator,denominator_unit,denominator_basis,analysis_role
            FROM publication_observation WHERE source_id='sullivan01_prp_pfo'
            AND endpoint='source_type_i_dci' ORDER BY stratum
        """).fetchall() == [
            ("all-screened-test-subjects", 4, 29, "person", "source_reported", "overlap_hold"),
            ("echo-probable-pfo", 0, 5, "person", "source_reported", "overlap_hold"),
            ("pfo-not-detected-by-tte", 4, 24, "person", "author_reconstructed", "overlap_hold"),
        ]
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='sullivan01_prp_pfo' AND stratum='echo-probable-pfo'
            AND endpoint IN ('source_spencer_vge_grade_3','source_spencer_vge_grade_4')
            ORDER BY endpoint
        """).fetchall() == [(1, 5), (1, 5)]
        assert db.execute("""
            SELECT json_extract(metadata_json,'$.source_discrepancy.abstract_echo_probable_pfo_grade_iv'),
                   json_extract(metadata_json,'$.source_discrepancy.table_1_echo_probable_pfo_grade_iv')
            FROM review.review_record
            WHERE run_id='2026-11-20-prp-pfo-headache-odland' AND source_key='sullivan-2001-table-1'
        """).fetchone() == (2, 1)
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit FROM publication_observation
            WHERE source_id='bryce01_headache' ORDER BY stratum
        """).fetchall() == [(44, 70, "dcs_case"), (16, 70, "dcs_case"), (70, 480, "dcs_case")]
        assert db.execute("""
            SELECT published_subject_number,sequence_in_subject,symptom_elapsed_min,symptom_time_basis
            FROM publication_bryce_headache_sequence ORDER BY published_subject_number,sequence_in_subject
        """).fetchall() == [
            (1, 1, 135, "from_protocol_start"),
            (2, 1, 540, "after_reported_chamber_flight"),
            (2, 2, 120, "after_reported_chamber_flight"),
        ]


def test_odland_and_robie_share_one_fatal_flight_case_with_conflicting_dates(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT numerator,denominator,period,altitude FROM publication_observation
            WHERE source_id='odland59_flight'
        """).fetchone() == (1, None, None, 22000.0)
        assert db.execute("""
            SELECT count(*),count(DISTINCT case_id)
            FROM historical_case_catalog WHERE source_id='odland59_flight'
        """).fetchone() == (1, 1)
        assert db.execute("""
            SELECT report_id FROM shared_case_evidence
            WHERE source_id='odland59_flight' ORDER BY report_id
        """).fetchall() == [("aeme:31-11-885",), ("pmid:14428293",)]
        assert db.execute("""
            SELECT elapsed,elapsed_reference FROM publication_case_milestone
            WHERE source_id='odland59_flight' AND milestone LIKE 'chest_symptom_%'
            ORDER BY elapsed
        """).fetchall() == [(25, "from_flight_start"), (30, "from_flight_start")]
        assert db.execute("""
            SELECT json_extract(metadata_json,'$.chronology.printed_event_date'),
                   json_extract(metadata_json,'$.chronology.printed_meeting_date'),
                   json_extract(metadata_json,'$.chronology.normalized_event_date')
            FROM review.review_record
            WHERE run_id='2026-11-20-prp-pfo-headache-odland' AND source_key='odland-1959-primary'
        """).fetchone() == ("1959-10-13", "1959-04-28", None)


def test_postexercise_trial_keeps_interim_rest_event_and_final_rest_gap(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT parent.source_id,parent.group_id FROM publication_postexercise_flow parent
            JOIN publication_postexercise_flow child ON child.source_id=parent.source_id
              AND child.parent_group_id=parent.group_id
            GROUP BY parent.source_id,parent.group_id
            HAVING sum(child.population_count) != parent.population_count
        """).fetchall() == []
        assert db.execute("""
            SELECT source_id,population_count FROM publication_postexercise_flow
            WHERE group_id='initial-exposures' ORDER BY source_id
        """).fetchall() == [("pilmanis01_sof_outcomes", 54), ("webb02_postexercise_journal", 67)]
        assert db.execute("""
            SELECT population_count,postexposure_dcs FROM publication_postexercise_flow
            WHERE source_id='pilmanis01_sof_outcomes' AND group_id='no-initial-dcs-rest'
        """).fetchone() == (12, 1)
        assert db.execute("""
            SELECT assignment,population_count,postexposure_dcs FROM publication_postexercise_flow
            WHERE source_id='webb02_postexercise_journal' AND group_id GLOB 'all-assigned-*'
            ORDER BY assignment
        """).fetchall() == [("exercise", 31, 0), ("rest", 29, None)]
        assert db.execute("""
            SELECT numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='webb02_postexercise_journal' AND stratum='afrl-delayed-or-recurrent-archive'
        """).fetchone() == (33, 2810, "overlap_hold")


def test_ground_oxygen_flow_preserves_treatment_and_followup_denominators(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT child.source_id, child.group_id FROM publication_ground_oxygen_flow child
            JOIN publication_ground_oxygen_flow parent ON parent.source_id=child.source_id
              AND parent.group_id=child.parent_group_id
            WHERE child.population_count > parent.population_count
        """).fetchall() == []
        assert db.execute("""
            SELECT child.group_id,child.population_count,parent.population_count,child.counting_unit
            FROM publication_ground_oxygen_flow child JOIN publication_ground_oxygen_flow parent
              ON (child.source_id,child.parent_group_id)=(parent.source_id,parent.group_id)
            WHERE child.source_id='krause00_full' AND child.group_id IN (
                'recurrent-or-delayed-symptoms', 'hbo-after-recurrent-or-delayed-symptoms',
                'resolved-without-further-treatment-after-symptoms', 'source-defined-glo-success',
                'incomplete-vge-record', 'complete-vge-record', 'symptoms-resolved-during-descent')
            ORDER BY child.group_id
        """).fetchall() == [
            ("complete-vge-record", 260, 613, "dcs_case"),
            ("hbo-after-recurrent-or-delayed-symptoms", 9, 10, "dcs_case"),
            ("incomplete-vge-record", 353, 613, "dcs_case"),
            ("recurrent-or-delayed-symptoms", 10, 728, "dcs_case"),
            ("resolved-without-further-treatment-after-symptoms", 1, 10, "dcs_case"),
            ("source-defined-glo-success", 739, 749, "dcs_case"),
            ("symptoms-resolved-during-descent", 852, 907, "symptom_report"),
        ]
        assert db.execute("""
            SELECT child.group_id,child.population_count,parent.population_count,child.count_basis
            FROM publication_ground_oxygen_flow child JOIN publication_ground_oxygen_flow parent
              ON (child.source_id,child.parent_group_id)=(parent.source_id,parent.group_id)
            WHERE child.source_id='rudge92_chamber_onset' AND child.group_id IN (
                'abstract-initial-glo', 'table-initial-glo', 'table-glo-hbo-for-symptoms',
                'table-glo-hbo-any', 'ground-onset-hbo-while-asymptomatic', 'ground-onset-recurrence')
            ORDER BY child.group_id
        """).fetchall() == [
            ("abstract-initial-glo", 175, 221, "source_reported"),
            ("ground-onset-hbo-while-asymptomatic", 4, 45, "source_reported"),
            ("ground-onset-recurrence", 5, 41, "source_reported"),
            ("table-glo-hbo-any", 53, 176, "reconstructed"),
            ("table-glo-hbo-for-symptoms", 49, 176, "reconstructed"),
            ("table-initial-glo", 176, 221, "reconstructed"),
        ]
        assert db.execute("""
            SELECT count(*), count(DISTINCT report_id), min(report_id)
            FROM review.review_record WHERE record_key IN (
                'legacy:data/chamber/v1.5/sources.csv#krause00',
                'legacy:data/chamber/v1.5/references.csv#mahon2014:124',
                'legacy:data/chamber/v1.85/sources.csv#krause00_full',
                '2026-11-20-formal-chamber-pubmed#10685583',
                '2026-11-20-formal-chamber-europe-pmc#MED:10685583',
                '2026-11-20-formal-chamber-openalex#W93154131',
                '2026-11-20-ground-oxygen-source-verification#krause-2000-original')
        """).fetchone() == (7, 1, "openalex:W93154131")
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='krause00_full'
        """).fetchone() == (0,)


def test_regional_exercise_keeps_ultrasound_grades_and_unlinked_stops(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT p.condition,p.participant_exposures,count(*),p.exposures_with_visible_vge,
                   sum(max(v.rest_eb_grade,v.knee_flex_eb_grade,v.arm_flex_eb_grade)>0),
                   sum(max(v.rest_eb_grade,v.knee_flex_eb_grade,v.arm_flex_eb_grade)>=4),
                   p.rest_assessment_interval_min,p.provocation_assessment_interval_min
            FROM publication_gottschalk24_protocol p JOIN publication_gottschalk24_vge_peak v
                USING(source_id,condition)
            GROUP BY p.source_id,p.condition ORDER BY p.condition
        """).fetchall() == [("Control", 11, 11, 4, 4, 1, 5, 15),
                           ("ECCu", 11, 11, 8, 8, 3, 5, 15), ("ECCw", 11, 11, 7, 7, 1, 5, 15)]
        assert db.execute("""
            SELECT condition,sum(reported_stop_count) FROM publication_gottschalk24_safety_stop
            GROUP BY condition ORDER BY condition
        """).fetchall() == [("Control", 2), ("ECCu", 3), ("ECCw", 3)]
        assert db.execute("""
            SELECT condition,rest_eb_grade,knee_flex_eb_grade,arm_flex_eb_grade
            FROM publication_gottschalk24_vge_peak WHERE participant_number=10 ORDER BY condition
        """).fetchall() == [("Control", 0, 0, 0), ("ECCu", 1, 0, 1), ("ECCw", 2, 2, 0)]
        assert db.execute("""
            SELECT report_id FROM model_report_link
            WHERE source_table='publication_source' AND source_id='gottschalk24_region'
        """).fetchone() == ("pmid:38923893",)
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record WHERE doi='10.1113/ep091853'
        """).fetchall() == [("pmid:38923893",)]
        assert db.execute("""
            SELECT right_report FROM review.review_report_relation
            WHERE left_report='pmid:39667826' AND relationship='reuses_subset_of_chamber_exposures'
            ORDER BY right_report
        """).fetchall() == [("pmid:37140728",), ("pmid:38923893",)]
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence WHERE report_id IN ('pmid:38923893','pmid:39667826')
        """).fetchone() == (0,)


def test_nasa_rehearsals_preserve_published_roles_and_outcome_scope(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT p.volunteer_count,p.technician_count,p.simulated_eva_sessions,p.planned_eva_min,
                   p.eva_pressure_pilot_methods_kpa,p.eva_pressure_medical_overview_psia,
                   p.peak_doppler_grade_as_reported,p.peak_eftedal_brubakk_score,p.pressure_status
            FROM publication_ea_rehearsal_pilot p WHERE p.source_id='garbino22_ea_pilot'
        """).fetchone() == (6, 2, 1, 360, 34.0, 4.3, "II", 5, "conflicting_reports")
        assert db.execute("""
            SELECT rehearsal_year,campaign_month,facility_start_date,reported_attendance,
                   reported_dcs_cases,outcome_denominator,pilot_source_id
            FROM publication_ea_rehearsal_summary
            WHERE campaign_source_id='garbino_ea12' ORDER BY rehearsal_year
        """).fetchall() == [
            (2022, "2022-03", "2022-05-09", 8, 1, None, "garbino22_ea_pilot"),
            (2023, "2023-03", "2023-05-01", 8, 0, None, None),
        ]
        assert db.execute("""
            SELECT o.endpoint,o.numerator,o.denominator,o.denominator_unit,o.altitude,
                   r.cases,r.denominator,r.chamber_role,o.analysis_role
            FROM publication_observation o
            JOIN model_report_link l ON o.source_id=l.source_id AND l.source_table='publication_source'
            JOIN review.review_search_observation r ON l.report_id=r.report_id AND o.endpoint=r.endpoint
            WHERE o.source_id='garbino22_ea_pilot' ORDER BY o.endpoint
        """).fetchall() == [
            ("dcs_diagnosed", 0, 6, "person", None, 0, 6, "research_volunteer", "descriptive"),
            ("vge_any_grade", 3, 6, "person", None, 3, 6, "research_volunteer", "descriptive"),
        ]
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id) FROM review.review_record
            WHERE record_key IN (
                'legacy:data/chamber/v1.6/sources.csv#garbino_ea12',
                'legacy:data/chamber/v1.32/search_hits.csv#nasa_strata_v32_originals:4',
                '2026-11-20-nasa-rehearsals-primary#garbino-campaign-full-slides'
            )
        """).fetchone() == (3, 1)
        assert db.execute("""
            SELECT numerator,denominator FROM discovery_observation
            WHERE source_id='garbino_ea12' AND stratum='volunteer-evas' AND endpoint='dcs_type_i'
        """).fetchone() == (2, 50)
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence
            WHERE study_id LIKE 'nasa-exploration-atmosphere-%-dress-rehearsal'
        """).fetchone() == (0,)


def test_brooks_abstracts_keep_conditional_doppler_and_unreported_dcs_outcomes(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT s.reported_exposures,s.reported_protocol_hours_min,s.reported_protocol_hours_max,s.grading_scale,
                   s.reported_pct_dcs_symptoms_with_early_termination,o.numerator,o.denominator,
                   o.analysis_role,r.cases,r.denominator
            FROM publication_brooks91_doppler_scope s JOIN publication_observation o USING(source_id)
            JOIN model_report_link l ON l.source_id=s.source_id AND l.source_table='publication_source'
            JOIN review.review_search_observation r ON r.report_id=l.report_id AND r.endpoint=o.endpoint
            WHERE s.source_id='webb91_doppler_resolution' AND o.endpoint='vge_reduced_to_spencer_0_or_1'
        """).fetchall() == [(215, 7, 8, "Spencer", 66.0, 13, 35, "overlap_hold", 13, 35)]
        assert db.execute("""
            SELECT cases,denominator,reported_rate,reported_rate_unit
            FROM review.review_search_observation
            WHERE run_id='2026-11-20-brooks-doppler-original'
              AND observation_id='printed-dcs-termination-percentage'
        """).fetchall() == [(None, 215, 66, "percent")]
        assert db.execute("""
            SELECT participants,altitude_ft_lower,altitude_ft_upper,oxygen_prebreathe_min,
                   exercise_min_per_cycle,exercise_cycle_min,ultrasound_interval_min
            FROM publication_olson91_paired_protocol WHERE source_id='olson91_paired_latency'
        """).fetchone() == (14, 25000, 30000, 60, 1, 16, 16)
        assert db.execute("""
            SELECT left_report,right_report,relationship FROM review.review_report_relation
            WHERE left_report IN ('abstract:asma-1991-olson-krutz-045',
                                  'abstract:asma-1991-webb-pilmanis-219')
              AND relationship IN ('potential_invoked_in_vitro_predecessor','possible_overlap_archive_profiles')
            ORDER BY left_report
        """).fetchall() == [
            ("abstract:asma-1991-olson-krutz-045", "pmid:2031629", "potential_invoked_in_vitro_predecessor"),
            ("abstract:asma-1991-webb-pilmanis-219", "pmid:15672984", "possible_overlap_archive_profiles"),
        ]
        assert db.execute("""
            SELECT endpoint FROM publication_observation
            WHERE source_id IN ('olson91_paired_latency','webb91_doppler_resolution') ORDER BY endpoint
        """).fetchall() == [("vge_reduced_to_spencer_0_or_1",)]
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence
            WHERE report_id IN ('abstract:asma-1991-olson-krutz-045','abstract:asma-1991-webb-pilmanis-219')
        """).fetchone() == (0,)


def test_olson_flights_keep_joint_outcomes_timing_and_ambiguous_link(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT reported_participants,reported_exposures,vax_title_code,target_altitude_ft,
                   target_pressure_psia,scheduled_max_min,prebreathe_min,doppler_check_interval_min
            FROM publication_olson88_protocol WHERE source_id='olson88_precordial'
        """).fetchone() == (32, 82, 17, 27500, 4.892, 480, 60, 15)
        assert db.execute("""
            SELECT outcome_column,bubble_detection_min IS NOT NULL,count(*)
            FROM publication_olson88_exposure
            WHERE source_id='olson88_precordial' GROUP BY 1,2 ORDER BY 1,2
        """).fetchall() == [
            ("with_bends", 0, 15), ("with_bends", 1, 49),
            ("without_bends", 0, 11), ("without_bends", 1, 7),
        ]
        assert db.execute("""
            SELECT count(linked_participant_ordinal),count(DISTINCT linked_participant_ordinal),
                   count(bends_onset_min)+count(bubble_detection_min),
                   sum(bubble_detection_min>bends_onset_min),sum(intermittent_pain_only_marked),
                   max(bends_onset_min)
            FROM publication_olson88_exposure WHERE source_id='olson88_precordial'
        """).fetchone() == (81, 32, 120, 5, 3, 344)
        assert db.execute("""
            SELECT table_subject_code,outcome_column,linked_participant_ordinal,bends_onset_min,bubble_detection_min
            FROM publication_olson88_exposure
            WHERE source_id='olson88_precordial' AND participant_link_status='narrative_conflict'
        """).fetchall() == [("SK", "without_bends", None, None, None)]
        assert db.execute("""
            SELECT o.endpoint,o.numerator,o.denominator,o.analysis_role,r.cases,r.denominator
            FROM publication_observation o
            JOIN model_report_link l ON l.source_id=o.source_id AND l.source_table='publication_source'
            JOIN review.review_search_observation r ON l.report_id=r.report_id AND r.endpoint=o.endpoint
            WHERE o.source_id='olson88_precordial' ORDER BY o.endpoint
        """).fetchall() == [
            ("bends_as_reported", 64, 82, "overlap_hold", 64, 82),
            ("vge_above_ignored_grade_i", 56, 82, "overlap_hold", 56, 82),
        ]
        assert db.execute("""
            SELECT right_report,relationship FROM review.review_report_relation
            WHERE left_report='report:ada231355'
              AND relationship IN ('same_published_exposure_subset_in_archive','revised_version_of')
            ORDER BY right_report
        """).fetchall() == [
            ("pmid:3044322", "same_published_exposure_subset_in_archive"),
            ("record:legacy:data/chamber/v1.9/search_hits.csv#protocol_extract_initial:1", "revised_version_of"),
        ]


def test_crowell_keeps_chamber_runs_and_overlapping_exposure_counts(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT i.summary_stratum, i.type_i_to_iv_chamber_runs, o.cases, o.denominator,
                   i.reported_total_incidents, o.cases + i.sinus_incidents + i.dental_incidents
                       + i.ear_incidents + i.gastrointestinal_incidents
                       + i.hypoxia_or_hyperventilation_incidents + i.other_incidents
            FROM publication_crowell83_chamber_incidents i JOIN zotero_observation o
                ON (i.source_id,i.summary_stratum)=(o.source_id,o.stratum)
            WHERE o.analysis_role='overlap_hold'
            ORDER BY i.summary_stratum
        """).fetchall() == [
            ("results_all", 2744, 69, 21423, 1687, 1689),
            ("results_lahr", 232, 3, 1389, 124, 124),
            ("results_toronto", 393, 7, 3482, 237, 237),
            ("results_trenton", 1216, 10, 7024, 598, 600),
            ("results_winnipeg_edmonton", 903, 49, 9528, 728, 728),
        ]
        assert db.execute("""
            SELECT sum(cases),sum(denominator) FROM zotero_observation
            WHERE source_id='crowell83' AND stratum NOT GLOB 'results_*'
        """).fetchone() == (69, 19573)


def test_vann_preflight_cases_stay_outside_existing_flight_outcomes(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT g.profile, g.printed_trials, sum(f.printed_exposures)
            FROM publication_vann04_preflight_group g JOIN publication_vann04_flight_group f
                USING (source_id,profile)
            GROUP BY g.profile ORDER BY g.profile
        """).fetchall() == [
            ("repeat-100-15-60-35", 111, 109),
            ("repeat-40-60-40-60", 119, 117),
            ("repeat-60-55-60-20-60-20", 100, 100),
            ("repeat-60-55-60-30", 36, 34),
            ("single-100-20", 109, 107),
        ]
        assert db.execute("""
            SELECT flight_disposition,count(*) FROM publication_vann04_preflight_case
            GROUP BY flight_disposition ORDER BY flight_disposition
        """).fetchall() == [
            ("did_not_fly", 7), ("flew_with_distinct_episode", 1),
            ("flew_with_recurrence", 1), ("flew_without_new_symptoms", 2),
        ]
        assert db.execute("""
            SELECT a.case_number,b.case_number FROM publication_vann04_preflight_case a
            JOIN publication_vann04_case b ON (a.source_id,a.linked_appendix_b_case,a.profile)
                =(b.source_id,b.case_number,b.profile)
            WHERE a.case_number=b.linked_appendix_a_case
        """).fetchall() == [(11, 40)]
        assert db.execute("""
            SELECT count(*) FROM publication_vann04_case WHERE source_id='vann04'
        """).fetchone() == (40,)
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id) FROM review.review_record
            WHERE record_key IN ('legacy:data/chamber/v1.4/sources.csv#vann04',
                '2026-11-20-original-chamber-incidents-appendix-a#vann-appendix-a')
        """).fetchone() == (2, 1)


def test_fryer_fatalities_preserve_chamber_scope_and_case_identity(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT country_as_reported,count(*),count(case_date_as_reported)
            FROM publication_fryer69_chamber_fatality
            GROUP BY country_as_reported ORDER BY country_as_reported
        """).fetchall() == [("Canada", 1, 0), ("UK", 2, 2), ("USA", 7, 7)]
        assert db.execute("""
            SELECT case_date_as_reported,table_peak_altitude_ft,narrative_symptom_onset_min,
                   table_time_to_death_hours_min,table_lucid_interval_as_reported
            FROM publication_fryer69_chamber_fatality WHERE case_number=10
        """).fetchone() == (None, 35000, 110, 17.0, "2¼ h")
        assert db.execute("""
            SELECT case_number,table_time_to_death_hours_min,table_time_to_death_hours_max
            FROM publication_fryer69_chamber_fatality WHERE case_number IN (1,3,4,5,6,7,9)
            ORDER BY case_number
        """).fetchall() == [
            (1, 8.5, 8.5), (3, 16.75, 16.75), (4, 17.25, 17.25), (5, 13.0, 14.0),
            (6, 38.5, 38.5), (7, 55.5, 55.5), (9, 5.25, 5.25),
        ]
        assert db.execute("""
            SELECT case_number,cited_case_label FROM publication_fryer69_fatality_citation
            WHERE cited_report_id='pmid:15401759' AND linkage_basis='fryer_identifies_same_case'
            ORDER BY case_number
        """).fetchall() == [(1, "1"), (2, "5"), (3, "2"), (4, "3"), (7, "4")]
        assert db.execute("""
            SELECT case_number,cited_report_id FROM publication_fryer69_fatality_citation
            WHERE linkage_basis='possible_same_case'
        """).fetchall() == [(10, "pmid:6651730")]
        assert db.execute("""
            SELECT count(*),count(r.report_id) FROM publication_fryer69_fatality_citation f
            LEFT JOIN review.review_report r ON r.report_id=f.cited_report_id
        """).fetchone() == (37, 37)
        assert db.execute("""
            SELECT count(*) FROM review.review_record WHERE report_id='report:ada111509'
              AND (run_id IS NULL OR run_id IN ('2026-11-20-original-agard-fatalities',
                  '2026-11-20-chamber-fatality-tavily', '2026-11-20-formal-chamber-openalex'))
        """).fetchone() == (14,)


def test_moon_accessions_link_existing_fatalities_with_original_time_origins(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT m.pathology_accession,f.case_number,m.listed_time_to_death_hours,
                   f.table_time_to_death_hours_min,m.narrative_time_to_death_hours,m.narrative_time_origin
            FROM publication_moon48_chamber_case m JOIN publication_fryer69_chamber_fatality f
                ON (m.fryer_source_id,m.fryer_case_number)=(f.source_id,f.case_number)
            JOIN review.review_report r ON r.report_id=m.report_id
            WHERE r.report_id='pmid:18904642' ORDER BY f.case_number
        """).fetchall() == [
            (95412, 1, 10, 8.5, None, None),
            (100893, 2, 47, 71.0, 45, "after_hospital_admission"),
            (103767, 3, 17, 16.75, None, None),
            (100822, 4, 24, 17.25, 24, "after_chamber_test"),
            (127451, 7, 55, 55.5, None, None),
        ]
        assert db.execute("""
            SELECT m.pathology_accession,c.cited_case_label FROM publication_moon48_chamber_case m
            JOIN publication_fryer69_fatality_citation c
                ON (m.fryer_source_id,m.fryer_case_number)=(c.source_id,c.case_number)
            WHERE c.cited_report_id='pmid:15401759' ORDER BY m.fryer_case_number
        """).fetchall() == [(95412, "1"), (100893, "5"), (103767, "2"), (100822, "3"), (127451, "4")]
        assert db.execute("""
            SELECT report_id,json_extract(metadata_json,'$.excluded_endpoint.source_section'),
                   json_extract(metadata_json,'$.excluded_endpoint.accession')
            FROM review.review_record WHERE record_key=
                '2026-11-20-moon-original-pathology-scans#moon-original-p248-p251'
        """).fetchone() == ("pmid:18904642", "Anoxia", 83172)


def test_flinn_history_keeps_subject_scope_control_and_chamber_milestones(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_phase,count(*),sum(antecedent_neurologic_episode)
            FROM publication_flinn63_exposure GROUP BY source_phase ORDER BY source_phase
        """).fetchall() == [("antecedent_history", 10, 8), ("medical_evaluation", 2, None)]
        assert db.execute("""
            SELECT sequence_number,reported_altitude_ft,altitude_description,inside_suit_equivalent_ft,
                   altitude_stated_to_subject_ft,prebreathe_min,first_subjective_symptom_min,
                   first_symptom_phase,symptom_free_observation_min
            FROM publication_flinn63_exposure WHERE sequence_number IN (2,8,9,11,12)
            ORDER BY sequence_number
        """).fetchall() == [
            (2, 100000, "outer_chamber", 40000, None, 90, None, "after_chamber", None),
            (8, 30000, "chamber", None, None, 0, 180, "at_altitude", None),
            (9, 12000, "chamber_upper_bound", None, 30000, None, None, None, 240),
            (11, 30000, "chamber", None, None, None, 26, "at_altitude", None),
            (12, 30000, "chamber", None, None, 20, 94, "at_altitude", None),
        ]
        assert db.execute("""
            SELECT sequence_number,finding,elapsed_min,elapsed_reference,precision
            FROM publication_flinn63_milestone WHERE finding IN (
                'scotoma_onset_after_initial_abdominal_symptoms','mapped_right_homonymous_scotoma',
                'residual_local_findings_at_exam','scratching_without_reported_itch','anterior_chest_mottling')
            ORDER BY sequence_number,elapsed_min
        """).fetchall() == [
            (8, "scotoma_onset_after_initial_abdominal_symptoms", 15, "after_first_symptom", "upper_bound"),
            (11, "mapped_right_homonymous_scotoma", 125, "at_altitude", "source_value"),
            (11, "residual_local_findings_at_exam", 2880, "postflight", "source_value"),
            (12, "scratching_without_reported_itch", 35, "at_altitude", "source_value"),
            (12, "anterior_chest_mottling", 114, "at_altitude", "derived_from_source_timing"),
        ]
        assert db.execute("""
            SELECT right_report,relationship FROM review.review_report_relation
            WHERE left_report='pmid:14050686'
              AND relationship IN ('same_published_case','explicit_same_pilot_and_eight_prior_episodes')
            ORDER BY right_report
        """).fetchall() == [
            ("faa-horizons:1963-08:17:flinn-womack", "same_published_case"),
            ("unpublished:scherman-neurologic-dysbarism", "explicit_same_pilot_and_eight_prior_episodes"),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='flinn63_recurrent'
        """).fetchone() == (0,)


def test_historical_visual_margins_preserve_counting_units_and_source_identity(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,measure,count_as_cited,counting_unit,denominator_as_cited,denominator_unit
            FROM publication_historical_visual_summary WHERE cited_report_id='pmid:20997673'
            ORDER BY stratum,measure
        """).fetchall() == [
            ("quoted-visual-subset", "chamber_ascents", 15, "chamber_ascent", None, None),
            ("quoted-visual-subset", "scotoma_observations", 8, "reported_visual_episode", None, None),
            ("quoted-visual-subset", "subjects_with_scotomas", 6, "person", None, None),
            ("whole-series", "chamber_ascents", 100, "chamber_ascent", None, None),
            ("whole-series", "dcs_related_ascent_terminations", 37, "chamber_ascent", 100, "chamber_ascent"),
            ("whole-series", "enrolled_subjects", 41, "person", None, None),
        ]
        assert db.execute("""
            SELECT count_as_cited,denominator_as_cited,percent_as_cited
            FROM publication_historical_visual_summary WHERE measure='broad_visual_symptoms'
            ORDER BY stratum
        """).fetchall() == [(None, 314, 28.0), (12, 35, None)]
        assert db.execute("""
            SELECT count_as_cited,denominator_as_cited
            FROM publication_historical_visual_summary WHERE measure='prior_typical_migraine_history'
            ORDER BY denominator_as_cited
        """).fetchall() == [(11, 16), (10, 102)]
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id),min(report_id) FROM review.review_record
            WHERE record_key IN ('legacy:data/chamber/v1.31/sources.csv#engel44_scotomas',
                'legacy:data/chamber/v1.31/search_hits.csv#reconciliation_v31_original_sources:4',
                '2026-11-20-scotoma-firecrawl#engel-bibliography')
        """).fetchone() == (3, 1, "journal:war-medicine:1944:5:304")
        assert db.execute("""
            SELECT endpoint,cases,denominator FROM review.review_search_observation
            WHERE run_id='2026-11-20-flinn-cited-scotoma-counts'
            AND endpoint IN ('scotoma_observations','subjects_with_scotomas') ORDER BY endpoint
        """).fetchall() == [("scotoma_observations", 8, None), ("subjects_with_scotomas", 6, None)]


def test_repeat_exposure_report_preserves_joint_counts_and_changed_timing(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT dcs_condition_a,dcs_condition_b,dcs_condition_c,participants
            FROM publication_repeated_exposure_joint_count
            ORDER BY dcs_condition_a,dcs_condition_b,dcs_condition_c
        """).fetchall() == [
            (0, 0, 0, 12), (0, 0, 1, 1), (0, 1, 0, 0), (0, 1, 1, 0),
            (1, 0, 0, 12), (1, 0, 1, 0), (1, 1, 0, 6), (1, 1, 1, 1),
        ]
        assert db.execute("""
            SELECT t.condition,t.endpoint,t.matched_event_count,t.preliminary_mean_min,
                   t.preliminary_plus_minus_min,t.final_mean_min,t.final_plus_minus_min
            FROM publication_repeated_exposure_timing t
            JOIN web_observation w ON (w.source_id,w.stratum,w.endpoint)=
                (t.final_source_id,t.condition,t.endpoint)
            WHERE w.cases=t.matched_event_count AND w.denominator=t.protocol_sessions
            ORDER BY t.condition,t.endpoint
        """).fetchall() == [
            ("A", "any_vge", 28, 32.0, 5.0, 30.0, 23.0),
            ("A", "dcs", 19, 70.0, 7.0, 70.0, 29.0),
            ("B", "any_vge", 21, 40.0, 8.0, 41.0, 35.0),
            ("B", "dcs", 7, 54.0, 10.0, 60.0, 34.0),
            ("C", "any_vge", 21, 43.0, 8.0, 41.0, 37.0),
            ("C", "dcs", 2, 40.0, 13.0, 40.0, 18.0),
        ]
        assert db.execute("""
            SELECT count(DISTINCT study_id)
            FROM review.review_study_report WHERE report_id='report:adp011093'
        """).fetchone() == (2,)


def test_separate_products_join_without_duplicate_cases_or_strata(release):
    with connect_pair(release) as db:
        for schema in ("main", "review"):
            assert db.execute(f"PRAGMA {schema}.integrity_check").fetchone() == ("ok",)
            assert db.execute(f"PRAGMA {schema}.foreign_key_check").fetchall() == []
            for (view,) in db.execute(f"SELECT name FROM {schema}.sqlite_schema WHERE type='view'"):
                db.execute(f'SELECT * FROM {schema}."{view}" LIMIT 1').fetchone()
        assert db.execute("SELECT 1 FROM review.sqlite_schema WHERE name='nasa_test'").fetchone() is None
        assert db.execute("SELECT 1 FROM main.sqlite_schema WHERE name='review_screening'").fetchone() is None
        total_cases, unique_cases, linked_cases = db.execute("""
            SELECT count(*), count(DISTINCT c.case_id), count(r.record_key)
            FROM historical_case_catalog c LEFT JOIN review.review_record r
            ON (r.record_key,r.report_id)=(c.record_key,c.report_id)
        """).fetchone()
        assert total_cases > 0
        assert total_cases == unique_cases == linked_cases
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
        cluster_occurrences, cluster_reports, cluster_report = db.execute("""
            SELECT count(*),count(DISTINCT report_id),min(report_id)
            FROM review.review_record WHERE lower(title) LIKE 'investigation of a cluster of decompression%'
        """).fetchone()
        assert cluster_occurrences >= 129
        assert (cluster_reports, cluster_report) == (1, "doi:10.28920/dhm51.1.82-85")
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
        ascent_occurrences, first_report, last_report = db.execute("""
            SELECT count(*),min(report_id),max(report_id) FROM review.review_record
            WHERE lower(title) LIKE '%different rates of ascent%' OR title=url AND url LIKE '%19890012936%'
        """).fetchone()
        assert ascent_occurrences >= 30
        assert first_report == last_report == "ntrs:19890012936"
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
            ("severe_neurological_reaction_source", 1, None, None, "case_conditional"),
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
        """).fetchone() == (1,)


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


def test_gray_age_and_density_keep_conflicts_and_prevent_maxwell_duplication(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT count(*),sum(reprint_subject_count) FILTER(WHERE age_range_years='all')
            FROM publication_gray_age_comparison
        """).fetchone() == (29, 52313)
        assert db.execute("""
            SELECT age_range_years,primary_subject_count,primary_severe_count,
                   reprint_subject_count,reprint_severe_count,primary_rate_pct,reprint_rate_pct
            FROM publication_gray_age_comparison
            WHERE site='Pensacola' AND age_range_years IN ('25–26','all')
            ORDER BY age_range_years
        """).fetchall() == [("25–26", 179, 38, 179, 38, 15.5, 15.5), ("all", 946, 78, 946, 88, 8.25, 8.25)]
        assert db.execute("""
            SELECT primary_rate_pct,reprint_rate_pct FROM publication_gray_age_comparison
            WHERE site='RCAF' AND age_range_years='24–26'
        """).fetchone() == (None, 32.6)
        assert db.execute("""
            SELECT site,severe_symptom_count,subject_count
            FROM publication_gray_density WHERE density_range='total' ORDER BY site
        """).fetchall() == [
            ("Kingman Field", 99, 2217), ("Las Vegas Field", 575, 2312),
            ("Maxwell Field", 1400, 44197),
        ]
        assert db.execute("""
            SELECT g.density_range,sum(m.subject_count),g.subject_count
            FROM publication_gray_density g JOIN publication_motley_density m
              ON (m.reanalysis_source_id,m.reanalysis_site,m.reanalysis_density_range)
                 = (g.source_id,g.site,g.density_range)
            GROUP BY g.density_range,g.subject_count ORDER BY g.density_range
        """).fetchall() == [
            ("1.8–2.0", 2054, 2054), ("2.0–2.2", 12695, 12695), ("2.2–2.4", 16514, 16514),
            ("2.4–2.6", 10417, 10417), ("2.6+", 2517, 2517),
        ]
        assert db.execute("""
            SELECT count(DISTINCT report_id) FROM review.review_record
            WHERE record_key IN (
                'legacy:data/chamber/v1.61/sources.csv#gray51_constitutional_book',
                'legacy:data/chamber/v1.30/sources.csv#gray51_constitutional',
                '2026-11-20-gray-motley-strata-primary#fulton1951-gray-chapter7'
            )
            HAVING count(*)=3
        """).fetchone() == (1,)


def test_ferris_engel_preserves_syndrome_denominators_and_reuses_the_berkeley_case(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT parent_source_id,endpoint,numerator,denominator,denominator_unit,analysis_role
            FROM publication_neurological_episode_margin ORDER BY parent_source_id,endpoint
        """).fetchall() == [
            ("romano44_ana", "coexisting_vasodepressor_syncope", 17, 46, "syndrome_episode", "case_conditional"),
            ("romano44_ana", "onset_at_altitude_unmodified_by_descent", 8, 46, "syndrome_episode", "case_conditional"),
            ("romano44_ana", "onset_first_30_min_after_descent", 32, 46, "syndrome_episode", "case_conditional"),
            ("romano44_ana", "scotoma_course_completed_at_altitude", 6, 46, "syndrome_episode", "case_conditional"),
            ("stewart_halifax_c2683", "no_preceding_dcs_symptoms", 4, 50, "syndrome_episode", "case_conditional"),
            ("stewart_halifax_c2683", "onset_at_altitude", 27, 50, "syndrome_episode", "case_conditional"),
            ("stewart_halifax_c2683", "onset_during_or_after_descent", 23, 50, "syndrome_episode", "case_conditional"),
        ]
        assert db.execute("""
            SELECT milestone,reporting_source_id,chamber_altitude_ft,elapsed,elapsed_unit,elapsed_reference
            FROM publication_case_milestone WHERE stratum='berkeley-delayed-neurological-case'
            ORDER BY milestone
        """).fetchall() == [
            ("bends_and_chokes_at_peak", "ferris51_clinical_nature", 38000, 18, "minutes", "arrival_at_peak"),
            ("partial_visual_recovery", "ferris51_clinical_nature", None, 48, "hours", "descent"),
            ("scotoma_during_descent", "ferris51_clinical_nature", None, None, None, None),
            ("worsening_chapter_account", "ferris51_clinical_nature", None, 105, "minutes", "descent"),
            ("worsening_minutes_account", "cam44_meeting14", None, 90, "minutes", "descent"),
        ]
        assert db.execute("""
            SELECT case_id,report_id,source_time_min FROM historical_case_catalog
            WHERE case_id LIKE '%berkeley-delayed-neurological-case'
        """).fetchall() == [
            ("cam44_meeting14:berkeley-delayed-neurological-case", "fulton1951:clinical-nature", None),
        ]
        assert db.execute("""
            SELECT right_report FROM review.review_report_relation
            WHERE left_report='nlm:101085500x796:meeting-14' AND relationship='same_published_case'
            ORDER BY right_report
        """).fetchall() == [("fulton1951:clinical-nature",), ("report:cam-396",)]


def test_operation_everest_i_keeps_staff_cases_and_resident_followup_separate(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,period,endpoint,numerator,denominator,altitude,analysis_role
            FROM publication_observation WHERE source_id='navy46_operation_everest' ORDER BY period
        """).fetchall() == [
            ("staff-july19", "1946-07-19", "cerebral_bends_source", 1, None, None, "case_conditional"),
            ("observer-july21", "1946-07-21", "cerebral_bends_source", 1, None, None, "case_conditional"),
        ]
        assert db.execute("""
            SELECT observation_id,chamber_role,reported_value,counting_unit
            FROM publication_everest_context
            WHERE observation_id IN ('lock-ascents','crew-roster','support-roster','resident-follow-up')
            ORDER BY observation_id
        """).fetchall() == [
            ("crew-roster", "operating_crew", 14, "roster_member"),
            ("lock-ascents", "lock", 409, "lock_ascent"),
            ("resident-follow-up", "resident_subject", 3, "day"),
            ("support-roster", "all_support_staff", 40, "roster_member"),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_everest_context
            WHERE counting_unit IN ('protocol_change','qualitative_frequency') AND reported_value IS NULL
        """).fetchone() == (3,)
        assert db.execute("""
            SELECT report_id FROM review.review_study_report
            WHERE study_id='usn-operation-everest-i-1946' ORDER BY report_id
        """).fetchall() == [("aaj:12194731100",), ("nlm:35721900r",), ("pmid:20276818",)]
        assert db.execute("""
            SELECT count(*),sum(cases),count(denominator),count(DISTINCT report_id)
            FROM review.review_search_observation WHERE study_id='usn-operation-everest-i-1946'
        """).fetchone() == (2, 2, 0, 1)
        assert db.execute("""
            SELECT report_id FROM review.review_record
            WHERE record_key='legacy:data/chamber/v1.32/search_hits.csv#nasa_strata_v32_ever:2'
        """).fetchone() == ("pmid:20251062",)
        assert db.execute("""
            SELECT count(*) FROM chamber_group_evidence WHERE study_id='usn-operation-everest-i-1946'
        """).fetchone() == (0,)


def test_asma_case_keeps_assessment_timing_and_reuses_the_published_report(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT numerator,denominator,period,altitude,prebreathe_min,analysis_role
            FROM publication_observation WHERE source_id='mendelsohn26_familiarization'
        """).fetchall() == [(1, None, None, 25000.0, 45, "case_conditional")]
        assert db.execute("""
            SELECT report_id,source_time_min,first_assessment_min,recurrence_free_followup_min
            FROM historical_case_catalog
            WHERE case_id='mendelsohn26_familiarization:familiarization-flight'
        """).fetchall() == [("record:2026-11-20-eds-training#kjur5ccdyv", None, 60, None)]
        assert db.execute("""
            SELECT milestone,elapsed,elapsed_reference FROM publication_case_milestone
            WHERE source_id='mendelsohn26_familiarization' ORDER BY milestone
        """).fetchall() == [
            ("clinical_improvement", 60, "initial_recompression_treatment"),
            ("first_clinic_assessment", 60, "return_to_ground"),
            ("in_flight_symptoms", None, None),
            ("mask_replaced_at_altitude", 4, "mask_removed_at_altitude"),
            ("symptom_resolution", None, None),
            ("symptoms_persisted_at_initial_check", 20, "initial_recompression_treatment"),
        ]
        assert db.execute("""
            SELECT count(*) FROM review.review_record WHERE report_id='record:2026-11-20-eds-training#kjur5ccdyv'
        """).fetchone() == (4,)
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id) FROM review.review_record
            WHERE url LIKE '%20260003261%'
        """).fetchone() == (7, 1)
        assert db.execute("""
            SELECT report_id FROM review.review_study_report
            WHERE study_id='nasa-exploration-atmosphere-test-6' ORDER BY role
        """).fetchall() == [
            ("record:2026-11-20-eds-training#rfxje4gd3n",),
            ("record:legacy:data/chamber/v1.6/sources.csv#garbino_ea6",),
        ]
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE study_id='nasa-exploration-atmosphere-test-6'
        """).fetchone() == (0,)


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

def test_early_navy_chamber_evidence_keeps_case_and_denominator_boundaries(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id),count(onset_min)
            FROM shared_case_evidence WHERE source_id='boothby_lovelace38_chamber'
        """).fetchone() == (2, 2, 0)
        assert db.execute("""
            SELECT case_id,source_time_min,recurrence_free_followup_min
            FROM historical_case_catalog WHERE source_id='boothby_lovelace38_chamber'
        """).fetchall() == [("boothby_lovelace38_chamber:35000ft-neurologic-episode", None, None)]
        assert db.execute("""
            SELECT stratum,setting,reported_altitude_ft,reported_duration_min,gas_as_reported
            FROM publication_chamber_case_altitude_stage
            WHERE source_id='behnke47_navy_altitude'
              AND ((stratum='navy-1940-11-11' AND stage=1) OR (stratum='navy-1940-12-06' AND stage=3))
            ORDER BY stratum
        """).fetchall() == [
            ("navy-1940-11-11", "surface", None, 45, "Oxygen inhalation, fraction unspecified"),
            ("navy-1940-12-06", "chamber", 37000, None, None),
        ]
        assert db.execute("""
            SELECT source_id,numerator,denominator,denominator_unit,analysis_role
            FROM publication_observation
            WHERE endpoint IN ('loss_of_consciousness_as_reported','source_reported_aircraft_bends',
                               'group_2_collapse_with_aeroembolism_symptoms_before_descent')
              AND source_id IN ('behnke47_navy_altitude','gemmill42_pensacola','korb42_patrol_indoctrination')
            ORDER BY source_id
        """).fetchall() == [
            ("behnke47_navy_altitude", 14, 55, "symptom_report", "case_conditional"),
            ("gemmill42_pensacola", 34, 208, "person", "case_conditional"),
            ("korb42_patrol_indoctrination", 3, None, None, "selected_cluster"),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_case_milestone WHERE source_id='korb42_patrol_indoctrination'
        """).fetchone() == (0,)

def test_mayo_reports_share_one_program_and_keep_streltsov_on_hold(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,parent_stratum,trial_count,participant_count
            FROM publication_chamber_trial_scope
            WHERE source_id='boothby40_mayo_altitude' AND trial_count IS NOT NULL
            ORDER BY trial_count DESC
        """).fetchall() == [
            ("mayo-ascents-at-least-30000ft", None, 102, None),
            ("mayo-ascents-at-least-35000ft", "mayo-ascents-at-least-30000ft", 80, None),
            ("mayo-ascents-to-40000ft", "mayo-ascents-at-least-35000ft", 30, None),
            ("35000ft-135min-two-person-run", "mayo-ascents-at-least-35000ft", 1, 2),
        ]
        assert db.execute("""
            SELECT source_id,analysis_role,numerator,denominator,denominator_unit,prebreathe_min
            FROM publication_observation
            WHERE endpoint IN ('untoward_symptoms_as_reported','source_reported_joint_or_neuritic_symptoms',
                               'joint_pain_as_quoted_by_carson')
              AND source_id IN ('boothby40_mayo_altitude','lovelace41_mayo_aeroembolism',
                                'carson42_streltsov_joint_pain')
            ORDER BY source_id
        """).fetchall() == [
            ("boothby40_mayo_altitude", "descriptive", 0, 2, "person", None),
            ("carson42_streltsov_joint_pain", "overlap_hold", 55, 800, "person", None),
            ("lovelace41_mayo_aeroembolism", "selected_cluster", 2, 2, "person", 20),
        ]
        assert db.execute("""
            SELECT count(DISTINCT study_id),count(DISTINCT report_id)
            FROM review.review_study_report
            WHERE study_id='mayo-early-altitude-chamber-program'
        """).fetchone() == (1, 4)
        assert db.execute("""
            SELECT case_id,source_time_min,recurrence_free_followup_min
            FROM historical_case_catalog WHERE source_id='lovelace41_mayo_aeroembolism'
        """).fetchall() == [("lovelace41_mayo_aeroembolism:40000ft-cough-episode", None, None)]
        assert db.execute("""
            SELECT milestone,elapsed,elapsed_unit
            FROM publication_case_milestone
            WHERE source_id='lovelace41_mayo_aeroembolism' AND stratum='40000ft-cough-episode'
              AND elapsed IS NOT NULL ORDER BY elapsed
        """).fetchall() == [
            ("cough_persisted_after_descent", 2.0, "hours"),
            ("chest_soreness_duration", 24.0, "hours"),
        ]

def test_ocular_cases_keep_distinct_exposures_and_canonical_citations(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_id,report_id,source_time_min,first_assessment_min,recurrence_report_day
            FROM historical_case_catalog
            WHERE source_id IN ('butler91_parachute_optic','pokroy09_f16_optic','steig03_optic')
            ORDER BY source_id
        """).fetchall() == [
            ("butler91_parachute_optic", "pmid:2031639", None, None, None),
            ("pokroy09_f16_optic", "pmid:19817243", None, None, None),
            ("steig03_optic", "pmid:14503679", None, None, 21),
        ]
        assert db.execute("""
            SELECT reported_altitude_ft,reported_duration_min,gas_as_reported
            FROM publication_chamber_case_altitude_stage WHERE source_id='steig03_optic'
        """).fetchall() == [(25000, 9, None)]
        assert db.execute("""
            SELECT milestone,elapsed,elapsed_unit,chamber_altitude_ft FROM publication_case_milestone
            WHERE source_id='pokroy09_f16_optic'
              AND milestone IN ('presentation_as_described_in_abstract','documented_ophthalmic_exam',
                                'in_flight_cabin_reading_after_suspected_leak')
            ORDER BY milestone
        """).fetchall() == [
            ("documented_ophthalmic_exam", 3.0, "days", None),
            ("in_flight_cabin_reading_after_suspected_leak", 10.0, "seconds", None),
            ("presentation_as_described_in_abstract", 2.0, "days", None),
        ]
        assert db.execute("""
            SELECT pmid,min(report_id),count(DISTINCT report_id)
            FROM review.review_record WHERE pmid IN ('14503679','7980334')
            GROUP BY pmid ORDER BY pmid
        """).fetchall() == [("14503679", "pmid:14503679", 1), ("7980334", "pmid:7980334", 1)]
        assert db.execute("""
            SELECT relationship FROM publication_overlap
            WHERE source_id='butler91_parachute_optic' AND related_source='fitz94_visual'
        """).fetchone() == ("unresolved",)

def test_nasa_reanalysis_preserves_shared_trials_and_selected_censoring(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT nasa_test_id,linkage_status,pure_oxygen_total_min,ascent_min,mixed_gas_min,
                   type_ii_dcs_as_reported
            FROM publication_nasa_reanalysis_test ORDER BY test_number
        """).fetchall() == [
            ("P I", "documented_program_group", 150, 30, 30, 0),
            ("P II", "documented_program_group", 150, 30, 30, 0),
            ("P III", "documented_program_group", 150, 30, 30, 1),
            ("P IV", "documented_program_group", 150, 30, 30, 0),
            ("2a", "documented_protocol", 240, 30, None, 0),
            ("3a", "documented_protocol", 270, 30, None, 0),
            ("11a", "likely_same_test", 186, 6, None, 0),
        ]
        assert db.execute("""
            SELECT endpoint,count(*),sum(numerator),sum(denominator),min(analysis_role)
            FROM publication_observation WHERE source_id='conkin03_age_vge'
            GROUP BY endpoint ORDER BY endpoint
        """).fetchall() == [
            ("any_spencer_vge_during_exposure", 7, 97, 238, "overlap_hold"),
            ("dcs_as_reported_in_2003_reanalysis", 7, 33, 238, "overlap_hold"),
        ]
        assert db.execute("""
            SELECT symptom_report_min,chamber_removal_min,maximum_spencer_grade
            FROM publication_nasa_reanalysis_removal WHERE dcs_reported=0
            ORDER BY chamber_removal_min
        """).fetchall() == [(None, 76, 0), (None, 148, 0), (None, 153, 3)]
        assert db.execute("""
            SELECT count(*),sum(dcs_reported),sum(chamber_removal_min<180),
                   sum(chamber_removal_min<240),sum(source_marks_end_of_test)
            FROM publication_nasa_reanalysis_removal
        """).fetchone() == (36, 33, 19, 22, 13)
        assert db.execute("""
            SELECT exposures,grade_iv FROM publication_nasa_reanalysis_vge_margin
            ORDER BY mean_time_min
        """).fetchall() == [(235, 6), (218, 10), (224, 20), (208, 20), (238, 36)]
        assert db.execute("""
            SELECT DISTINCT report_id
            FROM review.review_record WHERE pmid='14620470'
        """).fetchall() == [("pmid:14620470",)]
        for new, previous in [
            ("2026-11-21-conkin-nasa-timing-fulltext#nasa-1987",
             "legacy:data/chamber/v1.38/search_hits.csv#threshold_v38_primary:2"),
            ("2026-11-21-conkin-nasa-timing-catalog#hdsd",
             "legacy:data/chamber/v1/sources.csv#hdsd"),
        ]:
            assert db.execute("""
                SELECT count(*),min(report_id),max(report_id)
                FROM review.review_record WHERE record_key IN (?,?)
            """, (new, previous)).fetchone() == (2, "record:" + previous, "record:" + previous)


def test_nasa_long_exposure_tables_preserve_source_counts_and_overlap(release):
    with connect_pair(release) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("""
            SELECT * FROM publication_nasa_long_exposure ORDER BY table_label,reported_group
        """).fetchall()
        assert len(rows) == 23
        assert {row["analysis_role"] for row in rows} == {"overlap_hold"}
        assert [tuple(row) for row in db.execute("""
            SELECT table_label,count(*),sum(exposures),sum(dcs_cases),sum(serious_cases)
            FROM publication_nasa_long_exposure GROUP BY table_label ORDER BY table_label
        """)] == [("F4", 7, 241, 156, 0), ("F5", 16, 337, 51, 0)]
        assert [tuple(row) for row in db.execute("""
            SELECT nasa_test_id,sum(g.dcs_cases),sum(g.exposures),t.dcs_cases,t.dcs_denominator
            FROM publication_nasa_long_exposure g JOIN nasa_test t ON g.nasa_test_id=t.test_id
            GROUP BY nasa_test_id ORDER BY nasa_test_id
        """)] == [
            ("3a", 6, 28, 6, 28), ("3b", 8, 35, 8, 35), ("3c", 3, 14, 3, 14),
            ("3d", 2, 12, 2, 12), ("5a", 4, 38, 4, 38), ("5b", 0, 11, 0, 11),
            ("6", 1, 29, 1, 29),
        ]
        indexed = {row["reported_group"]: row for row in rows}
        assert indexed[212]["prebreathe_as_printed"] == "60"
        assert "240 min at ground pressure plus 30 min" in indexed[212]["linkage_evidence"]
        assert indexed[291]["linkage_status"] == "unresolved"
        assert indexed[291]["nasa_test_id"] is None
        assert indexed[307]["dcs_percent_as_printed"] == 66.6
        assert "suited 3/4 and control 1/2" in indexed[307]["linkage_evidence"]
        report, crosswalk = db.execute("""
            SELECT report_id,json_extract(metadata_json,'$.group_crosswalk')
            FROM review.review_record WHERE source_key='nasa-2019-f4-f5'
        """).fetchone()
        assert report == "record:legacy:data/chamber/v1/sources.csv#nasa19"
        assert [dict(row) for row in rows] == json.loads(crosswalk)
        assert [tuple(row) for row in db.execute("""
            SELECT endpoint,count(*)
            FROM review.review_search_observation
            WHERE record_key='2026-11-21-nasa-long-exposure-primary#nasa-2019-f4-f5'
            GROUP BY endpoint ORDER BY endpoint
        """)] == [("dcs_as_compiled_by_nasa", 23), ("serious_dcs_as_compiled_by_nasa", 23)]
        assert db.execute("SELECT count(*) FROM publication_observation WHERE source_id='nasa19'").fetchone()[0] == 0


def test_faa_oxygen_studies_keep_outcomes_separate_from_instrument_traces(release):
    with connect_pair(release) as db:
        counts = db.execute("""
            SELECT source_id,stratum,numerator,denominator,denominator_unit,analysis_role
            FROM publication_observation WHERE source_id IN ('campbell_jay25_ofos','garner96_mask40k')
            ORDER BY source_id
        """).fetchall()
        assert counts == [
            ("campbell_jay25_ofos", "completed-participant-profiles", 0, 12, "person_exposure", "descriptive"),
            ("garner96_mask40k", "mask-test-participants", 0, 4, "person", "descriptive"),
        ]
        assert db.execute("""
            SELECT stratum,trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE source_id='campbell_jay25_ofos' ORDER BY stratum
        """).fetchall() == [
            ("aborted-chamber-attempts", 4, None),
            ("all-chamber-attempts", 16, 14),
            ("completed-participant-profiles", 12, 12),
        ]
        assert db.execute("""
            SELECT report_id,cases,denominator,denominator_unit FROM review.review_search_observation
            WHERE report_id IN ('doi:10.21949/1529724','dot:21429','dot:86852','doi:10.48321/d1caaba6e8')
            ORDER BY report_id
        """).fetchall() == [("doi:10.21949/1529724", 0, 12, "person_exposure"), ("dot:21429", 0, 4, "person")]
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id),min(report_id) FROM review.review_record
            WHERE record_key LIKE '%#W7233631745'
               OR record_key='legacy:data/chamber/v1.8/search_hits.csv#historical_ferris:6'
        """).fetchone() == (3, 1, "doi:10.21949/1529724")
        assert db.execute("""
            SELECT report_id FROM review.review_study_report
            WHERE study_id='faa-cami-ofos-2025-chamber' ORDER BY report_id
        """).fetchall() == [("doi:10.21949/1529724",), ("doi:10.48321/d1caaba6e8",), ("dot:86852",)]
        assert db.execute("""
            SELECT files_checked,sample_count,invalid_samples,nonincreasing_clock_intervals,
                   recorded_gaps_gt_0_1s,files_with_altitude_at_least_44000_ft
            FROM publication_chamber_pressure_trace_audit
        """).fetchone() == (12, 6422333, 0, 0, 0, 12)
        db.row_factory = sqlite3.Row
        audit = db.execute("SELECT * FROM publication_chamber_pressure_trace_audit").fetchone()
        raw = db.execute("""
            SELECT json_extract(metadata_json,'$.pressure_audit') FROM review.review_record
            WHERE report_id='dot:86852' AND source_key='smartlab-archive'
        """).fetchone()
        assert dict(audit) == json.loads(raw[0])


def test_mcfadden_bends_abort_preserves_one_case_and_separate_stage_denominators(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator,denominator_unit,analysis_role,altitude
            FROM publication_observation WHERE source_id='mcfadden66_mask_bends' ORDER BY stratum
        """).fetchall() == [
            ("six-instrumented-subjects", 1, 6, "person", "descriptive", None),
            ("table-1-block-01-bends-abort", 1, None, None, "selected_cluster", None),
        ]
        assert db.execute("""
            SELECT stratum,participant_count,pressure_mmhg FROM publication_chamber_trial_scope
            WHERE source_id='mcfadden66_mask_bends' ORDER BY stratum
        """).fetchall() == [
            ("six-instrumented-subjects", 6, None),
            ("subjects-with-35000ft-measurement", 6, 179.0),
            ("subjects-with-40000ft-measurement", 5, 141.0),
        ]
        assert db.execute("""
            SELECT milestone,chamber_altitude_ft,elapsed FROM publication_case_milestone
            WHERE source_id='mcfadden66_mask_bends' ORDER BY milestone
        """).fetchall() == [
            ("flight_aborted_for_bends", None, None),
            ("last_explicit_pre_abort_altitude", 35000, None),
        ]
        assert db.execute("""
            SELECT reported_altitude_ft,reported_duration_min FROM publication_chamber_case_altitude_stage
            WHERE source_id='mcfadden66_mask_bends' ORDER BY stage
        """).fetchall() == [(altitude, None) for altitude in (10000, 14000, 14000, 14000, 21500, 29000, 35000)]
        assert db.execute("""
            SELECT case_id,report_id,source_time_min FROM historical_case_catalog
            WHERE source_id='mcfadden66_mask_bends'
        """).fetchall() == [("mcfadden66_mask_bends:table-1-block-01-bends-abort", "dot:20771", None)]
        assert db.execute("""
            SELECT count(*) FROM review.review_record WHERE report_id='dot:20771'
        """).fetchone() == (6,)
        assert db.execute("""
            SELECT report_id,reported_group,cases,denominator FROM review.review_search_observation
            WHERE report_id IN ('dot:20771','dot:20821','dot:20989','dot:21252','dtic:ada168832')
            ORDER BY reported_group
        """).fetchall() == [
            ("dot:20771", "six-instrumented-subjects", 1, 6),
            ("dot:20771", "table-1-block-01-bends-abort", 1, None),
        ]


def test_cessna_observer_case_uses_abort_time_and_keeps_observer_denominator_unknown(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT endpoint,numerator,denominator,analysis_role,altitude,prebreathe_min
            FROM publication_observation WHERE source_id='mcfadden79_cessna_observer'
        """).fetchall() == [("observer_bends_as_reported", 1, None, "selected_cluster", None, None)]
        assert db.execute("""
            SELECT milestone,chamber_altitude_ft,elapsed,elapsed_unit,elapsed_reference
            FROM publication_case_milestone WHERE source_id='mcfadden79_cessna_observer'
        """).fetchall() == [
            ("flight_aborted_with_observer_bends", 30000, 32.0, "minutes", "after reaching 30,000 ft"),
        ]
        assert db.execute("""
            SELECT reported_altitude_ft,reported_duration_min,gas_as_reported
            FROM publication_chamber_case_altitude_stage WHERE source_id='mcfadden79_cessna_observer'
        """).fetchall() == [(30000, 32.0, None)]
        assert db.execute("""
            SELECT report_id,source_time_min FROM historical_case_catalog
            WHERE source_id='mcfadden79_cessna_observer'
        """).fetchall() == [("faa:aac-119-77-8s", None)]
        assert db.execute("""
            SELECT related_source,relationship FROM publication_overlap
            WHERE source_id='mcfadden79_cessna_observer'
        """).fetchall() == [("mcfadden66_mask_bends", "unresolved")]
        assert db.execute("""
            SELECT cases,denominator FROM review.review_search_observation
            WHERE report_id IN ('faa:aac-119-77-8s','dot:21164','faa:am79-13-flight27','ntsb:aar7502')
        """).fetchall() == [(1, None)]
        assert db.execute("""
            SELECT json_extract(metadata_json,'$.reported_outcome.source_characterizations[0].source_descriptor'),
                   json_extract(metadata_json,'$.reported_outcome.source_characterizations[1].source_descriptor')
            FROM review.review_record WHERE source_key='cessna-chapter'
        """).fetchall() == [("light", "moderate")]
        assert db.execute("""
            SELECT report_id FROM review.review_study_report
            WHERE study_id='national-airlines-flight27-1973' ORDER BY report_id
        """).fetchall() == [("faa:am79-13-flight27",), ("ntsb:aar7502",)]
        assert db.execute("""
            SELECT report_id,count(*) FROM review.review_record
            WHERE record_key IN ('2026-11-20-rapid-decompression-o-history#W1597299230',
                'legacy:data/chamber/v1.20/search_hits.csv#rd_v20_web_rcaf_iam:1')
               OR source_key IN ('mask66-catalog','mask66-scan','methods67-catalog')
            GROUP BY report_id ORDER BY report_id
        """).fetchall() == [("dot:20789", 3), ("faa:am67-03", 2)]


def test_space_activity_suit_observer_pressure_is_distinct_from_subject_timing(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator,altitude,prebreathe_min
            FROM publication_observation WHERE source_id='webb67_sas_observer'
        """).fetchall() == [("table-i-test-13-observer", 1, None, None, None)]
        assert db.execute("""
            SELECT stratum,trial_count,participant_count,pressure_mmhg
            FROM publication_chamber_trial_scope WHERE source_id='webb67_sas_observer' ORDER BY stratum
        """).fetchall() == [
            ("altitude-chamber-garment-trials", 6, 2, None),
            ("table-i-test-13-observer", 1, None, 155.0),
        ]
        assert db.execute("""
            SELECT elapsed,chamber_altitude_ft FROM publication_case_milestone
            WHERE source_id='webb67_sas_observer'
        """).fetchall() == [(None, None)]
        assert db.execute("""
            SELECT report_id,source_time_min FROM historical_case_catalog
            WHERE source_id='webb67_sas_observer'
        """).fetchall() == [("ntrs:19680002042", None)]
        assert db.execute("""
            SELECT report_id,cases,denominator FROM review.review_search_observation
            WHERE report_id IN ('ntrs:19680002042','ntrs:19650004856','ntrs:20190027194','dot:20777')
        """).fetchall() == [("ntrs:19680002042", 1, None)]
        assert db.execute("""
            SELECT report_id,count(*) FROM review.review_record
            WHERE report_id IN ('ntrs:19680002042','ntrs:19650004856','dot:20777')
            GROUP BY report_id ORDER BY report_id
        """).fetchall() == [
            ("dot:20777", 4),
            ("ntrs:19650004856", 2),
            ("ntrs:19680002042", 5),
        ]
        assert db.execute("""
            SELECT report_id,count(*) FROM review.review_record
            WHERE record_key IN (
                'legacy:data/chamber/v1.32/search_hits.csv#nasa_strata_v32_spa:6',
                '2026-11-20-formal-chamber-ntrs-setting#20190027194',
                '2026-11-21-nasa-observer-primary#nasa-history'
            )
            GROUP BY report_id
        """).fetchall() == [("ntrs:20190027194", 3)]


def test_chile_cmae_keeps_incident_and_training_periods_separate(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,endpoint,numerator,denominator,denominator_unit,period
            FROM publication_observation
            WHERE source_id='montiglio23_chile_cmae'
              AND endpoint IN ('dcs_as_recorded','people_trained_as_reported','instructions_as_reported')
            ORDER BY stratum
        """).fetchall() == [
            ("hypoxia-recognition-2022-instructions", "instructions_as_reported", 427, None, None, "2022"),
            ("hypoxia-recognition-incident-register", "dcs_as_recorded", 0, None, None, "March 1982–December 2022"),
            ("hypoxia-recognition-people-trained", "people_trained_as_reported", 24173, None, None, "March 1972–December 2022"),
            ("rapid-decompression-people-trained", "people_trained_as_reported", 3257, None, None, "March 1972–December 2022"),
        ]
        # Only incident endpoints enter the review outcome view.
        review_incidents = db.execute("""
            SELECT endpoint,cases,denominator FROM review.review_search_observation
            WHERE report_id='fach-investiga:2023:2-1:27' ORDER BY endpoint
        """).fetchall()
        assert review_incidents == [
            ("barodontalgia_as_recorded", 7, None),
            ("barosinusitis_as_recorded", 162, None),
            ("barotitis_as_recorded", 595, None),
            ("dcs_as_recorded", 0, None),
            ("gastrointestinal_gas_colic_as_recorded", 87, None),
            ("hyperventilation_syndrome_as_recorded", 19, None),
            ("loss_of_consciousness_as_recorded", 14, None),
            ("oxygen_mask_apprehension_as_recorded", 9, None),
        ]
        assert db.execute("""
            SELECT endpoint,numerator,denominator FROM publication_observation
            WHERE source_id='montiglio23_chile_cmae' AND stratum='hypoxia-recognition-incident-register'
            ORDER BY endpoint
        """).fetchall() == review_incidents
        assert db.execute("""
            SELECT right_report,relationship FROM review.review_report_relation
            WHERE left_report='fach-investiga:2023:2-1:27' ORDER BY right_report
        """).fetchall() == [
            ("doi:10.3390/s24134168", "overlapping_program_scope"),
            ("fach:cmae-6000-flight-hours-2021", "overlapping_program_scope"),
            ("hdl:11447/9961", "overlapping_program_scope"),
        ]
        assert db.execute("""
            SELECT count(*) FROM review.review_record WHERE report_id='fach:cmae-6000-flight-hours-2021'
        """).fetchone() == (2,)


def test_cr1892_keeps_one_case_and_preserves_its_three_clock_values(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT numerator,denominator,altitude,prebreathe_min
            FROM publication_observation WHERE source_id='annis71_sas_chamber'
        """).fetchall() == [(1, None, 80000.0, None)]
        assert db.execute("""
            SELECT milestone,elapsed,elapsed_reference FROM publication_case_milestone
            WHERE source_id='annis71_sas_chamber' ORDER BY milestone
        """).fetchall() == [
            ("foot_pain_onset_from_target_plateau", 5.0, "approximately after reaching target pressure"),
            ("foot_pain_onset_from_test_start", 26.0, "after start of test 4-3"),
            ("pain_subsided_during_repressurization", None, None),
            ("reported_total_test_duration", 42.0, "after start of test 4-3"),
        ]
        assert db.execute("""
            SELECT stratum,trial_count,participant_count,pressure_mmhg
            FROM publication_chamber_trial_scope WHERE source_id='annis71_sas_chamber' ORDER BY stratum
        """).fetchall() == [
            ("altitude-chamber-suit-trials", 8, 2, None),
            ("phase-i-trials", 5, 2, None),
            ("phase-ii-trials", 3, 2, None),
            ("test-2-1", 1, 1, 523.0),
            ("test-2-2", 1, 1, 141.0),
            ("test-2-3", 1, 1, 54.4),
            ("test-2-4", 1, 1, 20.9),
            ("test-2-5", 1, 1, 15.0),
            ("test-4-1", 1, 1, 226.0),
            ("test-4-2", 1, 1, 46.0),
            ("test-4-3-subject-c-bends", 1, 1, 20.9),
        ]
        assert db.execute("""
            SELECT report_id,source_time_min FROM historical_case_catalog
            WHERE source_id='annis71_sas_chamber'
        """).fetchall() == [("ntrs:19720005428", None)]
        assert db.execute("""
            SELECT report_id,cases,denominator FROM review.review_search_observation
            WHERE report_id IN ('ntrs:19720005428','ntrs:20190027194','pmid:5678082')
        """).fetchall() == [("ntrs:19720005428", 1, None)]
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='ntrs:20190027194' AND right_report='ntrs:19720005428'
        """).fetchall() == [("same_published_case",)]
        assert db.execute("""
            SELECT record_key,report_id FROM review.review_record
            WHERE record_key IN ('2026-11-20-formal-chamber-ntrs-setting#19720005428',
                '2026-11-21-nasa-cr1892-primary#sharpe-retelling')
            ORDER BY record_key
        """).fetchall() == [
            ("2026-11-20-formal-chamber-ntrs-setting#19720005428", "ntrs:19720005428"),
            ("2026-11-21-nasa-cr1892-primary#sharpe-retelling", "ntrs:20190027194"),
        ]
        assert db.execute("""
            SELECT json_extract(metadata_json,'$.case_details.target_pressure_mmhg'),
                   json_extract(metadata_json,'$.case_details.prerepressurization_pressure_mmhg'),
                   json_extract(metadata_json,'$.case_details.repressurized_pressure_mmhg')
            FROM review.review_record WHERE source_key='cr1892-original'
        """).fetchall() == [(20.9, 20.8, 62)]


def test_hdsd_reanalysis_preserves_two_partitions_and_original_vge_discrepancy(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_id,numerator,denominator,analysis_role
            FROM publication_observation
            WHERE (source_id,stratum) IN (
                ('conkin98_vge_dcs_archive','selected-vge-available-records'),
                ('thompson03_dcs_survival','analysis-records'))
            ORDER BY source_id
        """).fetchall() == [
            ("conkin98_vge_dcs_archive", 168, 1322, "overlap_hold"),
            ("thompson03_dcs_survival", 167, 1321, "overlap_hold"),
        ]
        for table, expected in [
            ("table-1a", [(2, 64), (5, 278), (1, 91), (13, 276), (11, 63), (66, 325), (13, 45), (56, 179)]),
            ("table-1b", [(16, 110), (69, 387), (11, 46), (36, 130), (0, 68), (34, 336), (0, 39), (1, 205)]),
        ]:
            extracted = db.execute("""
                SELECT numerator,denominator FROM publication_observation
                WHERE source_id='thompson03_dcs_survival' AND stratum GLOB ?
                  AND endpoint='type_i_dcs_symptoms_as_reported' AND analysis_role='overlap_hold'
                ORDER BY stratum
            """, (f"{table}-bin-*-exer-*",)).fetchall()
            assert extracted == expected
            assert tuple(map(sum, zip(*extracted))) == (167, 1321)
        assert db.execute("""
            SELECT stratum,numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='conkin98_vge_dcs_archive' AND endpoint='any_grade_vge_as_reported'
            ORDER BY stratum
        """).fetchall() == [
            ("table-i-vge-detected", 480, 1322, "denominator_conflict"),
            ("table-ii-vge-detected", 479, 1322, "denominator_conflict"),
        ]
        assert dict(db.execute("""
            SELECT stratum,printf('%d/%d',numerator,denominator)
            FROM publication_observation WHERE source_id='conkin98_vge_dcs_archive'
              AND endpoint='dcs_by_maximum_vge_grade_as_reported'
        """).fetchall()) == {
            "table-ii-grade-0": "13/843", "table-ii-grade-i": "5/45",
            "table-ii-grade-ii": "6/67", "table-ii-grade-iii": "23/118",
            "table-ii-grade-iv": "121/249",
        }
        assert db.execute("""
            SELECT report_id,role FROM review.review_study_report
            WHERE study_id='hdsd-vge-complete-1322' ORDER BY report_id
        """).fetchall() == [
            ("ntrs:20030019353", "subset_reanalysis"), ("pmid:9451528", "primary_outcome"),
        ]
        assert db.execute("""
            SELECT report_id FROM review.review_record
            WHERE record_key='2026-11-20-formal-chamber-openalex#W2143038161'
        """).fetchone() == ("ntrs:20030019353",)
        assert db.execute("""
            SELECT report_id,cases,denominator FROM review.review_search_observation
            WHERE study_id='hdsd-vge-complete-1322'
              AND reported_group IN ('analysis-records','selected-vge-available-records')
            ORDER BY report_id
        """).fetchall() == [("ntrs:20030019353", 167, 1321), ("pmid:9451528", 168, 1322)]


def test_nasa_doppler_margins_and_postdive_adjudication(release):
    with connect_pair(release) as db:
        margins = db.execute(
            """
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE source_id='powell93_cmb125' AND endpoint='type_i_pain_dcs_as_reported'
            """
        ).fetchall()
        rows = {stratum: (events, people) for stratum, events, people in margins}
        assert rows['all-subjects'] == (22, 125)
        for partition in (
            ('cmb-detected', 'cmb-undetected'),
            ('men', 'women'),
            ('upper-test-altitude', 'lower-test-altitude'),
            ('prebreathe-nil', 'prebreathe-3-5-h', 'prebreathe-4-h', 'prebreathe-6-h'),
        ):
            counts = zip(*(rows[group] for group in partition), strict=True)
            assert tuple(map(sum, counts)) == (22, 125)
        assert db.execute(
            "SELECT sensitivity_percent,specificity_percent,false_positive_percent "
            "FROM publication_doppler_diagnostic_threshold ORDER BY minimum_grade"
        ).fetchall() == [(96, 68, 32), (91, 70, 30), (85, 80, 20), (73, 86, 14)]
        assert db.execute(
            "SELECT DISTINCT cases,denominator FROM review.review_search_observation "
            "WHERE study_id='nasa-jsc-cmb-time-81'"
        ).fetchall() == [(17, 81)]
        assert db.execute(
            "SELECT numerator,denominator,analysis_role FROM publication_observation "
            "WHERE source_id='norfleet93_postdive' AND endpoint='dcs_as_reported'"
        ).fetchone() == (0, 19, 'denominator_conflict')
        assert db.execute(
            "SELECT dcs_cases,dcs_denominator FROM nasa_test WHERE test_id='10'"
        ).fetchone() == (1, 19)
        assert db.execute(
            "SELECT case_id,source_time_min FROM historical_case_catalog WHERE case_id='nasa03:81'"
        ).fetchall() == [('nasa03:81', 158)]
        assert db.execute(
            "SELECT report_id FROM review.review_study_report "
            "WHERE study_id='nasa-jsc-doppler-516' ORDER BY report_id"
        ).fetchall() == [('pmid:11540992',), ('pmid:9125093',)]


def test_prebreathe_measurements_preserve_units_phase_conflict_and_reuse(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT phase_as_printed,linked_phase,estimate_n,measured_n
            FROM publication_prp_prebreathe_oxygen ORDER BY printed_row
        """).fetchall() == [
            ('I', 'I', 49, 19), ('I', None, 47, 19),
            ('III', 'III', 9, 19), ('IV', 'IV', 62, 19), ('V-1', 'V-1', 9, 18),
            ('V-2', 'V-2', 3, None), ('V-3', 'V-3', 21, None),
        ]
        assert db.execute("""
            SELECT mean,standard_error,sample_n FROM publication_calibration_workload
            WHERE source_id='loftin93_task_posture' AND stratum='upright-rope-pull'
        """).fetchone() == (247.0, 21.7, 4)
        assert db.execute("""
            SELECT reporting_group,reported_percent,denominator_as_printed,related_source
            FROM publication_prebreathe_compilation_rate
            WHERE stratum='powell-1995' ORDER BY reporting_group
        """).fetchall() == [
            ('resting', 27, 11, 'conkin01_lba'), ('seated_combined', 0, 7, 'conkin01_lba')
        ]
        assert db.execute("""
            SELECT count(*),count(reported_percent),count(denominator_as_printed)
            FROM publication_prebreathe_compilation_rate
        """).fetchone() == (18, 17, 16)
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE study_id='loftin-1997-prebreathe-analysis' AND cases IS NOT NULL
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='ntrs:20070011616' AND relationship LIKE 'reuses_published%'
        """).fetchone() == ('reuses_published_prebreathe_model_population',)


def test_asma_interim_abstracts_keep_reported_risk_sets_and_overlap(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT endpoint,numerator,denominator,analysis_role
            FROM publication_observation WHERE source_id='rice01_navy_interim'
            AND endpoint IN ('dcs_as_reported','first_symptoms_after_chamber_exit')
            ORDER BY endpoint
        """).fetchall() == [
            ('dcs_as_reported', 41, 20778, 'overlap_hold'),
            ('first_symptoms_after_chamber_exit', 30, 41, 'case_conditional'),
        ]
        assert db.execute("""
            SELECT reported_group,reported_rate_percent,cases,denominator
            FROM review.review_search_observation WHERE report_id='abstract:asma-2001-066'
            AND reported_rate_percent IS NOT NULL AND denominator IS NULL
            ORDER BY reported_group
        """).fetchall() == [
            ('25000ft-observers', 0.12, None, None), ('25000ft-trainees', 0.24, None, None),
            ('all-profiles-observers', 0.18, None, None), ('all-profiles-trainees', 0.21, None, None),
        ]
        assert db.execute("""
            SELECT stratum,endpoint,numerator,denominator FROM publication_observation
            WHERE source_id='webb01_postexercise_interim' ORDER BY stratum,endpoint
        """).fetchall() == [
            ('all-exposures', 'dcs_during_exposure', 32, 57),
            ('all-exposures', 'referred_for_possible_hbo', 7, 57),
            ('post-exposure-exercise', 'delayed_or_recurrent_dcs', 0, 25),
            ('post-exposure-rest', 'recurrent_joint_pain_dcs', 1, None),
        ]
        assert db.execute("""
            SELECT reported_percent,denominator FROM publication_reported_rate
            WHERE source_id='pilmanis01_40000ft_interim' AND endpoint='dcs_as_reported'
        """).fetchone() == ('47.5', 40)
        assert db.execute("""
            SELECT count(*),count(event_sample_size) FROM publication_interim_onset_summary
        """).fetchone() == (8, 0)
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE pmid='12182217' OR url='https://ntrs.nasa.gov/citations/20040088175'
        """).fetchall() == [('pmid:12182217',)]
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id),min(report_id) FROM review.review_record
            WHERE run_id IN ('2026-11-21-asma-interim-firecrawl-1','2026-11-21-asma-interim-firecrawl-2')
              AND url='https://pmc.ncbi.nlm.nih.gov/articles/PMC8313775/'
        """).fetchone() == (2, 1, 'doi:10.28920/dhm51.1.82-85')
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE report_id='journal:watanabe-yamazaki-1964-amlr-5-4'
              AND endpoint='reported_any_symptoms' AND cases=872 AND denominator=4645
        """).fetchone() == (1,)
        assert dict(db.execute("""
            SELECT related_source,relationship FROM publication_overlap
            WHERE source_id='pilmanis01_40000ft_interim'
        """)) == {'gerth18': 'unresolved', 'pilmanis03': 'likely_overlap'}


def test_qinetiq_dispatcher_counts_link_one_event_to_two_publications(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,parent_stratum,trial_count,participant_count
            FROM publication_chamber_trial_scope
            WHERE source_id='connolly26_dispatcher_chamber' ORDER BY stratum
        """).fetchall() == [
            ('planned-ascents', None, 44, 11),
            ('uneventful-completions', 'planned-ascents', 42, None),
        ]
        assert db.execute("""
            SELECT p.cases,p.denominator,p.denominator_unit,l.report_id
            FROM web_observation p JOIN model_report_link l USING(source_id)
            WHERE p.source_id='connolly26' AND l.source_table='web_source'
        """).fetchall() == [(1, 43, 'chamber_decompression', 'doi:10.3357/amhp.6973.2026')]
        assert db.execute("""
            SELECT report_id,cases,denominator,denominator_unit FROM review.review_search_observation
            WHERE study_id='qinetiq-connolly-two-day-dispatcher-chamber'
        """).fetchall() == [('doi:10.3357/amhp.6973.2026', 1, 43, 'chamber_decompression')]
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE lower(title) LIKE '%human tolerance of frequent altitude decompression%'
        """).fetchall() == [('doi:10.3357/amhp.6973.2026',)]
        assert db.execute("""
            SELECT count(*) FROM review.review_record WHERE report_id='abstract:asma-2026-connolly-253'
        """).fetchone() == (4,)
        assert db.execute("""
            SELECT right_report,relationship FROM review.review_report_relation
            WHERE left_report='abstract:asma-2026-connolly-253'
            ORDER BY right_report
        """).fetchall() == [
            ('doi:10.3357/amhp.6973.2026', 'same_chamber_experiment'),
            ('pmid:37587625', 'distinct_reported_exposure_schedules_participant_overlap_unresolved'),
        ]


def test_air_surgeons_bulletin_retains_counts_rates_and_cohort_links(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='karpovich44_fitness_bends' AND endpoint='bends_requiring_early_descent'
        """).fetchone() == (30, 197, 'overlap_hold')
        assert db.execute("""
            SELECT unaffected_mean_points,affected_mean_points,reported_mean_difference_points,reported_critical_ratio
            FROM publication_cadet_fitness_comparison
            WHERE source_id='karpovich44_fitness_bends'
        """).fetchone() == (49.2, 47.63, 1.57, 1.3)
        assert db.execute("""
            SELECT stratum,reported_percent,denominator,denominator_unit,analysis_role
            FROM publication_reported_rate WHERE source_id='guest44_diurnal_bends'
            ORDER BY stratum
        """).fetchall() == [
            ('afternoon', '15.4', 2593, 'trainee_record', 'overlap_hold'),
            ('evening', '20.7', 1341, 'trainee_record', 'overlap_hold'),
            ('morning', '30', 2693, 'trainee_record', 'overlap_hold'),
            ('night', '11.9', 210, 'trainee_record', 'overlap_hold'),
        ]
        assert db.execute("""
            SELECT count(*),count(cases),sum(denominator) FROM review.review_search_observation
            WHERE report_id='asb:1944:1:6:5:guest'
        """).fetchone() == (4, 0, 6837)
        assert db.execute("""
            SELECT report_id,count(*) FROM review.review_record
            WHERE report_id IN ('asb:1944:1:6:5:guest','asb:1944:1:6:5:karpovich')
            GROUP BY report_id ORDER BY report_id
        """).fetchall() == [('asb:1944:1:6:5:guest', 3), ('asb:1944:1:6:5:karpovich', 3)]
        assert db.execute("""
            SELECT cases,denominator FROM review.review_search_observation
            WHERE report_id='asb:1944:1:7:8:cincinnati-migraine'
        """).fetchall() == [(5, 17)]
        assert db.execute("""
            SELECT related_source FROM publication_overlap
            WHERE source_id='asb44_cincinnati_migraine' AND relationship='same_cohort'
        """).fetchone() == ('romano44_ana',)
        assert db.execute("""
            SELECT relationship FROM publication_overlap
            WHERE source_id='guest44_diurnal_bends' AND related_source='gray51_constitutional_book'
        """).fetchone() == ('unresolved',)


def test_wartime_reexposure_retains_scope_and_deduplicates_cases(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT endpoint,numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='rodbard44_kingman_reflight'
              AND stratum IN ('prior-bends-reflights','any-bends-on-reflight')
            ORDER BY endpoint
        """).fetchall() == [
            ('any_site_bends_as_reported', 70, 149, 'selected_cluster'),
            ('bends_at_new_site_only', 7, 70, 'case_conditional'),
            ('bends_at_original_site', 63, 70, 'case_conditional'),
        ]
        assert db.execute("""
            SELECT stratum,reported_percent,denominator FROM publication_reported_rate
            WHERE source_id='rodbard44_kingman_reflight' ORDER BY stratum
        """).fetchall() == [('rest-121-180', '38', 13), ('rest-21-60', '50', 52), ('rest-61-120', '52', 52)]
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE report_id='asb:1944:1:11:6:rodbard' AND cases IS NULL AND denominator IS NOT NULL
        """).fetchone() == (3,)
        assert db.execute("""
            SELECT source_id,numerator,denominator FROM publication_observation
            WHERE (source_id='tobias44_bends_primary' OR source_id='lawrence45_b24')
              AND stratum IN ('actual-subject-flights','b24-duty-crew')
            ORDER BY source_id
        """).fetchall() == [('lawrence45_b24', 10, 72), ('tobias44_bends_primary', 17, 36)]
        assert db.execute("""
            SELECT study_id,count(*) FROM review.review_study_report
            WHERE report_id IN ('asb:1944:1:11:9','pmid:21005550') GROUP BY study_id
        """).fetchall() == [('berkeley-liberator-chamber-flight-experiments', 2)]
        assert db.execute("""
            SELECT link.catalog_case_number,link.link_status,link.source_altitude_ft,link.source_death_hours,
                   old.table_peak_altitude_ft,old.table_time_to_death_hours_min
            FROM publication_chamber_fatality_crosswalk link
            JOIN publication_fryer69_chamber_fatality old
              ON (old.source_id,old.case_number)=(link.catalog_source_id,link.catalog_case_number)
            WHERE link.source_id='masland44_altitude_collapse' ORDER BY link.catalog_case_number
        """).fetchall() == [(1, 'confirmed', 38000, 11.0, 38000, 8.5), (2, 'likely', 30000, 70.0, 38000, 71.0)]
        assert db.execute("""
            SELECT numerator,denominator,trial_count FROM publication_observation
            JOIN publication_chamber_trial_scope USING(source_id,stratum)
            WHERE source_id='masland44_altitude_collapse'
        """).fetchone() == (5, None, 800000)
        assert db.execute("""
            SELECT count(*) FROM historical_case_catalog
            WHERE source_id IN ('masland44_altitude_collapse','york44_aeroembolism')
        """).fetchone() == (0,)


def test_brown_smith_preserve_nested_descents_and_reported_cells(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT endpoint,numerator,denominator FROM publication_observation
            WHERE source_id='brown46_chamber_syncope' AND stratum='all-runs' ORDER BY endpoint
        """).fetchall() == [
            ('early_descent_any_cause_source', 134, 225),
            ('early_descent_bends_primary_source', 89, 225),
        ]
        assert db.execute("""
            SELECT count(*),sum(numerator),min(denominator),max(denominator) FROM publication_observation
            WHERE source_id='brown46_chamber_syncope' AND stratum='early-descent-reasons'
        """).fetchone() == (11, 134, 134, 134)
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='brown46_chamber_syncope' AND endpoint='syncope_major_or_minor_printed_composite'
        """).fetchone() == (64, 134)
        assert db.execute("""
            SELECT syncope_absent_count,mild_syncope_count,severe_syncope_count,reported_any_syncope_percent
            FROM publication_bends_grade_syncope
            WHERE source_id='brown46_chamber_syncope' AND bends_grade=9
        """).fetchone() == (3, 2, None, 66)
        assert db.execute("""
            SELECT stratum,participant_count FROM publication_chamber_trial_scope
            WHERE source_id='smith46_treated_joint_pain' ORDER BY stratum
        """).fetchall() == [('symptom-treatment', 15), ('treated-physiology', 6)]
        assert db.execute("""
            SELECT numerator,denominator,analysis_role FROM publication_observation
            WHERE source_id='smith46_treated_joint_pain' AND endpoint='joint_decompression_pain_source'
        """).fetchone() == (2, 6, 'selected_cluster')
        assert db.execute("""
            SELECT report_id,count(*) FROM review.review_search_observation
            WHERE report_id IN ('pmid:20994853','pmid:20994854') GROUP BY report_id ORDER BY report_id
        """).fetchall() == [('pmid:20994853', 29), ('pmid:20994854', 2)]
        assert db.execute("""
            SELECT json_array_length(metadata_json,'$.table_iii.rows'),
                   json_array_length(metadata_json,'$.table_iv.rows')
            FROM review.review_record
            WHERE report_id='pmid:20994853' AND json_type(metadata_json,'$.table_iii')='object'
        """).fetchall() == [(15, 8)]


def test_fac_followup_uses_original_cohort_and_reconciles_chapter_records(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT count(*),sum(cases),sum(denominator) FROM web_observation
            WHERE source_id='olaya25' AND endpoint='dcs_type_ii_neurologic'
                AND stratum LIKE 'year-%'
        """).fetchone() == (11, 15, 10280)
        assert db.execute("""
            SELECT w.cases,w.denominator,d.alternate_case_count
            FROM web_observation w JOIN publication_web_count_discrepancy d USING(source_id,stratum,endpoint)
            WHERE source_id='olaya25' AND stratum='year-2015'
        """).fetchall() == [(1, 828, 0)]
        assert db.execute("""
            SELECT role_as_reported,reported_cases,observed_role_exposures,rate_per_1000,
                   ci_lower_per_1000,ci_upper_per_1000,denominator_basis
            FROM publication_role_incidence_estimate WHERE source_id='olaya25' ORDER BY role_as_reported
        """).fetchall() == [
            ('ico', 5, None, 1.82, 0.78, 4.26, 'author_estimated_staffing'),
            ('non-ico', 10, None, 1.33, 0.72, 2.44, 'author_estimated_staffing'),
        ]
        assert db.execute("""
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE source_id='olaya25' AND endpoint='received_hyperbaric_oxygen_source' ORDER BY stratum
        """).fetchall() == [('all-neurologic-cases', 13, 15), ('latency-gt-60-min-source', 9, 9),
                             ('latency-le-60-min-source', 4, 6)]
        assert db.execute("""
            SELECT DISTINCT denominator_unit,analysis_role FROM publication_observation WHERE source_id='olaya25'
        """).fetchall() == [('dcs_case', 'case_conditional')]
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE openalex_id LIKE '%W7162995450' OR doi LIKE '%9786287818279.12'
        """).fetchall() == [('doi:10.25062/9786287818279.12',)]
        assert db.execute("""
            SELECT count(*) FROM review.review_identity_assignment
            WHERE record_key LIKE '%#W7162995450' AND report_id='doi:10.25062/9786287818279.12'
        """).fetchone() == (6,)


def test_powell_margins_and_dervay_visits_preserve_risk_sets_and_identity(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE source_id='powell91_tm102176' AND analysis_role='overlap_hold'
            ORDER BY stratum
        """).fetchall() == [
            ("max-spencer-0", 0, 75),
            ("max-spencer-I", 1, 6),
            ("max-spencer-II", 2, 12),
            ("max-spencer-III", 8, 25),
            ("max-spencer-IV", 29, 55),
        ]
        assert db.execute("""
            SELECT concordance,count(*) FROM publication_powell_doppler_margin
            GROUP BY concordance ORDER BY concordance
        """).fetchall() == [("potential_combination", 2), ("rounded_profile_concordance", 12)]
        assert db.execute("""
            SELECT modeled_tissue_ratio,any_vge_percent_as_printed,grade_iii_iv_fraction_numerator,
                   grade_iii_iv_fraction_denominator,conkin_procedures
            FROM publication_powell_doppler_margin WHERE table_row=5
        """).fetchone() == (1.68, 57, 15, 26, "8")
        assert db.execute("""
            SELECT trial_count,participant_count
            FROM publication_chamber_trial_scope WHERE source_id='waligora83_tm58257'
        """).fetchone() == (173, None)
        assert db.execute("""
            SELECT condition_as_reported,count(*),sum(highest_spencer_grade > 0),
                   sum(highest_spencer_grade >= 3)
            FROM publication_dervay_doppler_visit WHERE completed_crossover=1
            GROUP BY condition_as_reported ORDER BY condition_as_reported
        """).fetchall() == [("A", 20, 6, 2), ("B", 20, 8, 5), ("C", 20, 10, 9)]
        assert db.execute("""
            SELECT source_subject_number,condition_as_reported,visit_order,first_vge_detection_min,highest_spencer_grade
            FROM publication_dervay_doppler_visit WHERE completed_crossover=0
            ORDER BY source_subject_number
        """).fetchall() == [(7, "A", 1, None, 0), (10, "A", 1, None, 0), (23, "B", 1, None, 0)]
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit,analysis_role,outcome_window
            FROM publication_observation
            WHERE source_id='dervay02_fulltext' AND endpoint='reported_dcs_during_altitude'
        """).fetchone() == (0, 60, "person_exposure", "overlapping_margin", "During the 120-minute altitude exposure.")
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE pmid='11817616' OR source_key IN ('dervay02','dervay02_fulltext')
        """).fetchall() == [("pmid:11817616",)]
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE openalex_id='W920476218' OR source_key IN ('W920476218','powell91_tm102176')
        """).fetchall() == [("openalex:W920476218",)]
        assert db.execute("""
            SELECT count(*) FROM review.review_report_relation
            WHERE relationship='cited_source_scope_discrepancy' AND left_report='openalex:W920476218'
        """).fetchone() == (1,)


def test_marseille_separates_reported_subjects_sessions_and_hypoxic_events(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT trial_count,participant_count,pressure_mmhg
            FROM publication_chamber_trial_scope
            WHERE source_id='coulange22_marseille_hypobaric'
        """).fetchone() == (39, 294, None)
        assert db.execute("""
            SELECT stratum,endpoint,numerator,denominator,denominator_unit,analysis_role,altitude
            FROM publication_observation
            WHERE source_id='coulange22_marseille_hypobaric' ORDER BY stratum
        """).fetchall() == [
            ("aircrew-hypoxia-familiarization", "reported_vagal_malaise_source", 1, None, None, "descriptive", None),
            ("mixed-hypobaric-testing", "reported_decompression_incident_source", 0, 294, "person", "descriptive", None),
            ("oxygen-system-evaluations", "reported_hypoxic_syncope_source", 3, None, None, "descriptive", None),
        ]
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id)
            FROM review.review_record WHERE source_key='coulange22_marseille_hypobaric'
        """).fetchone() == (2, 1)
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='abstract:coulange-2022-bmsh-32-30' AND right_report='journal:coulange-2014-bmsh-24-89'
        """).fetchone() == ("distinct_exposure_modalities",)


def test_brook_preserves_exposed_denominator_and_hall_unifies_two_pmids(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT numerator,denominator,denominator_unit,analysis_role,altitude,prebreathe_min
            FROM publication_observation WHERE source_id='brook95_hypobaric_complement'
        """).fetchall() == [(0, 13, "person", "overlap_hold", 25000.0, None)]
        assert db.execute("""
            SELECT related_source,relationship FROM publication_overlap
            WHERE source_id='brook95_hypobaric_complement'
        """).fetchall() == [("smart04", "unresolved")]
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE pmid='7619033' OR source_key='brook95_hypobaric_complement'
        """).fetchall() == [("pmid:7619033",)]
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id),count(DISTINCT pmid)
            FROM review.review_record
            WHERE report_id='report:usn-mr005-13-1002-subtask-9-report-3'
        """).fetchone() == (9, 1, 2)
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE pmid IN ('14131303','14166642') OR source_key='hall63_43000'
        """).fetchall() == [("report:usn-mr005-13-1002-subtask-9-report-3",)]


def test_russian_chamber_scope_keeps_unmatched_proportions_out_of_clinical_counts(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_id,trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE source_id IN ('chadov97_sae_pcc270','kalyuzhny76_h_reflex') ORDER BY source_id
        """).fetchall() == [("chadov97_sae_pcc270", 1828, 123), ("kalyuzhny76_h_reflex", None, 15)]
        assert db.execute("""
            SELECT stratum,reported_percent_lower,reported_percent_upper
            FROM publication_chamber_proportion_without_counts
            WHERE source_id='chadov97_staged' AND endpoint='doppler_venous_bubbles_as_reported'
            ORDER BY stratum
        """).fetchall() == [
            ("24-h-stage-550-mmhg", 6.0, 6.0),
            ("24-h-stage-600-mmhg", 12.0, 12.0),
            ("nominal-30-min-prebreathe", 49.0, 49.0),
        ]
        assert db.execute("""
            SELECT cases,denominator,reported_rate_lower,reported_rate_upper
            FROM review.review_search_observation
            WHERE report_id='pmid:966672' AND endpoint='h_reflex_stable_or_reduced_before_leg_pain_source'
        """).fetchall() == [(None, None, 65, 75)]
        assert db.execute("""
            SELECT count(*) FROM publication_overlap
            WHERE source_id='chadov97_sae_pcc270' AND relationship='unresolved'
        """).fetchone() == (3,)
        assert db.execute("""
            SELECT count(*) FROM publication_observation
            WHERE source_id IN ('chadov97_sae_pcc270','kalyuzhny76_h_reflex')
        """).fetchone() == (0,)


def test_dak_case_links_both_databases_without_imputing_exposure_or_pooling(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT numerator,denominator,analysis_role,period,altitude,prebreathe_min
            FROM publication_observation WHERE source_id='dak19_pulmonary_training_case'
        """).fetchall() == [(1, None, "case_conditional", None, None, None)]
        assert db.execute("""
            SELECT e.endpoint,h.source_time_min,o.cases,o.denominator,
                   json_extract(r.metadata_json,'$.case_facts.routine_protocol_altitude_ft'),
                   json_extract(r.metadata_json,'$.case_facts.patient_actual_altitude_ft')
            FROM shared_case_evidence e
            JOIN historical_case_catalog h USING(source_id,endpoint,report_id)
            JOIN review.review_search_observation o
              ON (o.record_key,o.observation_id,o.report_id)=(e.record_key,e.observation_id,e.report_id)
            JOIN review.review_record r ON r.record_key=e.record_key
            WHERE e.source_id='dak19_pulmonary_training_case'
        """).fetchall() == [("pulmonary_dcs_author_diagnosed", None, 1, None, 25000, None)]
        assert db.execute("""
            SELECT related_source,relationship FROM publication_overlap
            WHERE source_id='dak19_pulmonary_training_case'
        """).fetchall() == [("ercan20", "unresolved")]
        assert db.execute("""
            SELECT count(*) FROM review.review_record WHERE report_id=(
                SELECT report_id FROM shared_case_evidence WHERE source_id='dak19_pulmonary_training_case'
            )
        """).fetchone() == (3,)
        assert db.execute("""
            SELECT count(*) FROM review.review_report_relation
            WHERE relationship='possible_turkish_chamber_cohort_overlap'
              AND 'pmid:32574436' IN (left_report,right_report)
        """).fetchone() == (1,)


def test_polish_flight_case_links_three_reports_without_counting_three_cases(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT numerator,denominator,analysis_role,altitude,altitude_unit
            FROM publication_observation WHERE source_id GLOB 'siewiera*'
        """).fetchall() == [(1, None, "case_conditional", 28000.0, "ft")]
        assert db.execute("""
            SELECT case_id,report_id,source_time_min,first_assessment_min FROM historical_case_catalog
            WHERE source_id='siewiera20_polish_flight'
        """).fetchall() == [("siewiera20_polish_flight:flight-index-case", "pmid:31980050", None, None)]
        assert db.execute("""
            SELECT report_id FROM shared_case_evidence
            WHERE source_id='siewiera20_polish_flight' ORDER BY report_id
        """).fetchall() == [("abstract:tricon2018:d17",), ("gumed:96430",), ("pmid:31980050",)]
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record WHERE pmid='31980050'
        """).fetchall() == [("pmid:31980050",)]
        assert db.execute("""
            SELECT count(*) FROM review.review_report_relation
            WHERE relationship='same_published_case' AND 'pmid:31980050' IN (left_report,right_report)
        """).fetchone() == (2,)
        assert db.execute("""
            SELECT milestone,elapsed,elapsed_reference,aircraft_altitude_ft
            FROM publication_aircraft_case_milestone WHERE source_id='siewiera20_polish_flight'
            AND milestone IN ('in_flight_symptom_onset','warsaw_emergency_department',
                'journal_ecmo_last_marked','journal_ecmo_discontinued') ORDER BY milestone
        """).fetchall() == [
            ("in_flight_symptom_onset", None, None, 28000),
            ("journal_ecmo_discontinued", 7.0, "ordinal_day_in_journal_case_narrative", None),
            ("journal_ecmo_last_marked", 9.0, "ordinal_treatment_day_in_journal_table_i", None),
            ("warsaw_emergency_department", 6.0, "emergency_landing", None),
        ]
        assert db.execute("""
            SELECT json_extract(r.metadata_json,'$.case_facts.vv_ecmo_start_ordinal_day_of_treatment')
            FROM review.review_record r JOIN shared_case_evidence e USING(record_key)
            WHERE e.source_id='siewiera20_polish_flight' AND e.report_id='abstract:tricon2018:d17'
        """).fetchall() == [(2,)]
        assert db.execute("""
            SELECT report_id FROM review.review_record
            WHERE record_key GLOB '2026-11-21-polish-flight-dcs-case-firecrawl-regional#*'
              AND (pmid IS NOT NULL OR doi IS NOT NULL) ORDER BY report_id
        """).fetchall() == [
            ("doi:10.28920/dhm51.1.82-85",), ("pmid:19522370",), ("pmid:32574436",),
            ("pmid:39518919",), ("pmid:42345225",),
        ]


def test_verified_chamber_mirrors_and_baker_case_reuse_existing_reports(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE lower(url) LIKE '%/brandt_umo_decompression_sic.pdf'
        """).fetchall() == [("pmid:19522370",)]
        assert db.execute("""
            SELECT report_id FROM review.review_record
            WHERE record_key='legacy:data/chamber/v1.7/search_hits.csv#tavily_general:10'
        """).fetchone() == ("pmid:19522370",)
        assert db.execute("""
            SELECT numerator,denominator,altitude,altitude_unit,analysis_role
            FROM publication_observation WHERE source_id='baker26_f35c_flight'
        """).fetchall() == [(1, None, 26000.0, "ft", "case_conditional")]
        assert db.execute("""
            SELECT report_id,source_time_min,first_assessment_min FROM historical_case_catalog
            WHERE source_id='baker26_f35c_flight'
        """).fetchall() == [("abstract:asma-2026-baker-188", None, None)]
        assert db.execute("""
            SELECT elapsed,elapsed_reference,aircraft_altitude_ft
            FROM publication_aircraft_case_milestone
            WHERE source_id='baker26_f35c_flight' AND milestone='descent_and_cabin_repressurization'
        """).fetchall() == [(2.0, "controlled_descent_start", 16000)]
        assert db.execute("""
            SELECT json_extract(r.metadata_json,'$.case_facts.cabin_altitude_after_repressurization_ft'),
                   json_extract(r.metadata_json,'$.case_facts.aircraft_altitude_at_depressurization_ft')
            FROM review.review_record r JOIN shared_case_evidence e USING(record_key)
            WHERE e.source_id='baker26_f35c_flight'
        """).fetchall() == [(8000, None)]
        assert db.execute("""
            SELECT report_id FROM review.review_record
            WHERE record_key IN ('2026-11-20-asma-chamber-case-pages#baker-188',
                '2026-11-21-brandt-baker-imae-baker-primary#baker-188',
                '2026-11-21-brandt-baker-imae-imae-official#imae-34980',
                '2026-11-21-brandt-baker-imae-imae-mirror#imae-defesanet')
            ORDER BY record_key
        """).fetchall() == [("abstract:asma-2026-baker-188",)] * 2 + [("web:fab:34980",)] * 2
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE report_id IN ('web:fab:34980','pmid:11740422','doi:10.56083/rcv3n4-015')
              AND record_key GLOB '2026-11-21-brandt-baker-imae-*'
        """).fetchone() == (0,)


def test_historical_flight_case_sources_preserve_certainty_and_time_origins(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT source_id,endpoint,numerator,denominator,altitude FROM publication_observation
            WHERE source_id IN ('rudge90_b52_flight','voge89_naval_flight','wolf89_commercial_flight')
            ORDER BY source_id
        """).fetchall() == [
            ("rudge90_b52_flight", "presumptive_altitude_dcs_as_reported", 1, None, None),
            ("voge89_naval_flight", "probable_altitude_bends_as_reported", 1, None, 14000.0),
            ("wolf89_commercial_flight", "severe_altitude_dcs_author_attributed", 1, None, 29000.0),
        ]
        assert db.execute("""
            SELECT report_id,source_time_min FROM historical_case_catalog
            WHERE source_id IN ('rudge90_b52_flight','voge89_naval_flight','wolf89_commercial_flight')
            ORDER BY source_id
        """).fetchall() == [("pmid:2256876", None), ("pmid:2818403", None), ("pmid:2803166", None)]
        assert db.execute("""
            SELECT elapsed,elapsed_unit,elapsed_reference FROM publication_aircraft_case_milestone
            WHERE milestone IN ('transient_cabin_pressure_altitude','right_knee_pain_at_altitude',
                                'abstract_collapse_and_edema','narrative_waking_with_dyspnea')
              AND source_id IN ('rudge90_b52_flight','voge89_naval_flight','wolf89_commercial_flight')
            ORDER BY source_id,milestone
        """).fetchall() == [
            (0.5, "minutes", "duration_of_reported_cabin_excursion"),
            (40.0, "minutes", "start_of_flight_at_14000_ft"),
            (8.0, "hours", "landing_in_abstract"),
            (8.0, "hours", "duration_asleep_in_case_narrative"),
        ]
        assert db.execute("""
            SELECT json_extract(r.metadata_json,'$.case_facts.cabin_altitude_at_onset_ft'),
                   json_extract(r.metadata_json,'$.case_facts.cabin_transient_altitude_ft'),
                   json_extract(r.metadata_json,'$.case_facts.case_narrative_prior_dive_elapsed_days')
            FROM review.review_record r JOIN shared_case_evidence e USING(record_key)
            WHERE e.source_id='rudge90_b52_flight'
        """).fetchall() == [(None, 10000, 10)]
        assert db.execute("""
            SELECT related_source,relationship FROM publication_overlap WHERE source_id='rudge90_b52_flight'
        """).fetchall() == [("weien90", "unresolved")]
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE record_key GLOB '2026-11-21-historical-flight-case-sources-context-*'
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record WHERE pmid='20296024'
        """).fetchall() == [("pmid:20296024",)]
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record WHERE url LIKE '%/PMC203284%'
        """).fetchall() == [("pmid:14557320",)]


def test_asma_2012_reuses_existing_review_outcomes_and_keeps_endpoints_distinct(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT o.endpoint,o.altitude,o.altitude_unit,o.numerator,r.cases,r.denominator,
                   e.onset_min,r.chamber_role
            FROM shared_case_evidence e JOIN publication_observation o USING(source_id,stratum,endpoint)
            JOIN review.review_search_observation r
              ON (r.record_key,r.observation_id)=(e.record_key,e.observation_id)
            WHERE e.source_id='manton12_raf_chamber' AND o.denominator IS NULL
              AND o.analysis_role='case_conditional'
            ORDER BY o.altitude
        """).fetchall() == [
            ("symptomatic_altitude_dcs", 15748.0, "ft", 1, 1, None, None, None),
            ("reported_decompression_illness", 17500.0, "ft", 1, 1, None, None, "trainee"),
            ("suspected_arterial_gas_embolism", 25000.0, "ft", 1, 1, None, None, "trainee"),
        ]
        assert db.execute("""
            SELECT o.endpoint,o.numerator,o.denominator,o.denominator_unit,r.cases,r.denominator
            FROM publication_observation o JOIN model_report_link l USING(source_id)
            JOIN review.review_search_observation r ON (r.report_id,r.endpoint)=(l.report_id,o.endpoint)
            WHERE o.source_id='hok12_swedish_chamber' ORDER BY o.endpoint
        """).fetchall() == [
            ("arterial_bubbles_detected", 0, None, None, 0, None),
            ("symptomatic_altitude_dcs", 0, 6, "person", 0, 6),
        ]
        assert db.execute("""
            SELECT s.participant_count,s.trial_count,count(o.source_id)
            FROM publication_chamber_trial_scope s LEFT JOIN publication_observation o USING(source_id)
            WHERE s.source_id='blackadder12_raf_ent_chamber' GROUP BY s.source_id
        """).fetchall() == [(41, None, 0)]
        assert db.execute("""
            SELECT related_source,relationship FROM publication_overlap
            WHERE source_id='manton12_raf_chamber'
        """).fetchall() == [("mcloughlin00", "unresolved")]


def test_chinese_flight_counts_use_incident_strata_and_one_dcs_report(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT o.stratum,o.endpoint,o.analysis_role,o.numerator,o.denominator,o.denominator_unit,
                   r.cases,r.denominator
            FROM publication_observation o JOIN model_report_link l USING(source_id)
            JOIN review.review_search_observation r
              ON (l.report_id,o.endpoint,o.stratum)=(r.report_id,r.endpoint,r.reported_group)
            WHERE o.source_id IN ('zheng05_chinese_flight_decompression','liu08_chinese_flight_nursing')
            ORDER BY o.stratum
        """).fetchall() == [
            ("a-three-incidents", "type_ii_altitude_dcs_as_reported", "selected_cluster", 7, 10,
             "person_exposure", 7, 10),
            ("all-incident-pilot-records", "returned_to_flight_after_rapid_decompression", "overlap_hold",
             18, 19, "person_exposure", 18, 19),
            ("b-two-incidents", "type_ii_altitude_dcs_as_reported", "selected_cluster", 0, 9,
             "person_exposure", 0, 9),
        ]
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id) FROM review.review_record
            WHERE doi='10.3760/cma.j.issn.1007-6239.2005.02.013'
               OR report_id='doi:10.3760/cma.j.issn.1007-6239.2005.02.013'
        """).fetchone() == (3, 1)
        assert db.execute("""
            SELECT related_source,relationship FROM publication_overlap
            WHERE source_id='zheng05_chinese_flight_decompression'
        """).fetchall() == [("liu08_chinese_flight_nursing", "likely_overlap")]
        assert db.execute("""
            SELECT count(*) FROM historical_case_catalog
            WHERE source_id IN ('zheng05_chinese_flight_decompression','liu08_chinese_flight_nursing')
        """).fetchone() == (0,)


def test_chamber_severity_reuses_the_kumar_trial_and_preserves_prague_barotrauma(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT o.endpoint,o.numerator,o.denominator,o.denominator_unit,
                   o.analysis_role,r.cases,r.denominator
            FROM publication_observation o JOIN model_report_link l USING(source_id)
            JOIN review.review_search_observation r
              ON (l.report_id,o.endpoint,o.stratum)=(r.report_id,r.endpoint,r.reported_group)
            WHERE o.source_id IN ('kumar92_prior_exercise','oniscenko23_prague_gi_barotrauma')
              AND r.run_id='2026-11-21-chamber-symptom-grades-primary'
            ORDER BY o.endpoint
        """).fetchall() == [
            ("gastrointestinal_barotrauma_source", 1, None, None, "case_conditional", 1, None),
            ("type_i_grade_1_awareness_without_pain", 8, 15, "dcs_case", "case_conditional", 8, 15),
            ("type_i_grade_2_delayed_onset_after_testing", 1, 3, "dcs_case", "case_conditional", 1, 3),
            ("type_i_grade_2_mild_pain", 3, 15, "dcs_case", "case_conditional", 3, 15),
            ("type_i_grade_2_or_3_pain", 7, 78, "person_exposure", "overlap_hold", 7, 78),
            ("type_i_grade_3_task_interfering_pain", 4, 15, "dcs_case", "case_conditional", 4, 15),
        ]
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='kumar92_prior_exercise'
              AND stratum='both-arms' AND endpoint='dcs_pain_only_source'
        """).fetchone() == (15, 78)
        assert db.execute("""
            SELECT left_report,right_report,relationship FROM review.review_report_relation
            WHERE left_report='abstract:asma-1991-kumar-182'
        """).fetchall() == [("abstract:asma-1991-kumar-182", "pmid:1417653", "same_underlying_crossover_trial")]
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='kumar91_prior_exercise_abstract'
        """).fetchone() == (0,)


def test_public_chamber_physiology_keeps_measurements_separate_from_dcs_outcomes(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT participant_count,trial_count,evidence_source_id
            FROM publication_chamber_trial_scope WHERE source_id='jia26_chamber_physiology'
        """).fetchall() == [(20, None, "jia25_figshare_chamber_data_v1")]
        assert db.execute("""
            SELECT json_extract(metadata_json,'$.data_inventory.data_rows'),
                   json_array_length(metadata_json,'$.data_inventory.file_checks'),
                   json_extract(metadata_json,'$.data_inventory.clinical_dcs_outcomes_present'),
                   json_extract(metadata_json,'$.data_inventory.data_files_with_4500_m')
            FROM review.review_record WHERE source_key='jia25_figshare_chamber_data_v1' AND run_id IS NOT NULL
        """).fetchall() == [(158580, 24, 0, 16)]
        assert db.execute("""
            SELECT a.source_id,b.source_id,r.relationship FROM review.review_report_relation r
            JOIN model_report_link a ON a.report_id=r.left_report
            JOIN model_report_link b ON b.report_id=r.right_report
            WHERE r.relationship='describes_same_physiology_dataset'
        """).fetchall() == [("jia26_chamber_physiology", "jia25_figshare_chamber_data_v1",
                              "describes_same_physiology_dataset")]
        assert db.execute("""
            SELECT source_id,endpoint,numerator,denominator
            FROM publication_observation
            WHERE source_id IN ('jia26_chamber_physiology','jia25_figshare_chamber_data_v1','raju22_iaf_oxygen_trial')
            ORDER BY stratum
        """).fetchall() == [("raju22_iaf_oxygen_trial", "observed_hypoxia_symptoms_as_reported", 0, 1)] * 2
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id) FROM review.review_record
            WHERE url LIKE '%/retro-fitment-of-an-oxygen-system%'
              OR report_id='doi:10.25259/ijasm_28_2021'
        """).fetchone() == (6, 1)


def test_bangalore_treadmill_reports_reuse_one_dcs_case(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT case_id,report_id,source_time_min FROM historical_case_catalog
            WHERE source_id='kumar88_treadmill'
        """).fetchall() == [("kumar88_treadmill:treadmill-chamber-accident", "pmid:3202791", None)]
        assert db.execute("""
            SELECT source_id,numerator,denominator,analysis_role
            FROM publication_observation WHERE source_id IN ('kumar86_treadmill_case','kumar88_treadmill')
        """).fetchall() == [("kumar88_treadmill", 1, None, "selected_cluster")]
        assert db.execute("""
            SELECT country FROM publication_source
            WHERE source_id IN ('kumar86_treadmill_case','kumar88_treadmill')
        """).fetchall() == [("India",), ("India",)]
        assert db.execute("""
            SELECT s.report_id, s.onset_min,
                   json_extract(r.metadata_json,'$.clinical_as_reported.left_elbow_pain_min_as_reported'),
                   json_extract(r.metadata_json,'$.clinical_as_reported.asymptomatic_by_day'),
                   json_extract(r.metadata_json,'$.clinical_as_reported.native_symptom_grade')
            FROM shared_case_evidence s JOIN review.review_record r USING(record_key,report_id)
            WHERE s.source_id='kumar88_treadmill'
            ORDER BY s.report_id
        """).fetchall() == [("article:iam-1986-kumar-92", None, 15, 5, 4), ("pmid:3202791", None, 10, 3, None)]
        assert db.execute("""
            SELECT count(*),count(DISTINCT report_id) FROM review.review_record
            WHERE source_key='reconciliation_v31_india2:6' OR report_id='article:iam-1986-kumar-92'
        """).fetchone() == (3, 1)


def test_majumdar_chamber_milestones_reuse_the_original_review_case(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT a.period,a.altitude,a.numerator,a.denominator,c.report_id,c.source_time_min
            FROM publication_observation a JOIN historical_case_catalog c
              ON c.case_id=a.source_id || ':' || a.stratum AND c.endpoint=a.endpoint
            WHERE a.source_id='majumdar57_iaf_chamber'
        """).fetchall() == [("1957-06-05", 37000, 1, None, "journal:maj-1957-ijasm-4-1-9", None)]
        assert db.execute("""
            SELECT r.observation_id,r.cases,r.denominator
            FROM shared_case_evidence e
            JOIN review.review_search_observation r USING(record_key,observation_id,report_id)
            WHERE r.report_id='journal:maj-1957-ijasm-4-1-9'
        """).fetchall() == [("maj-1957-preconversion-altitude-chamber-dcs", 1, None)]
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE report_id='journal:maj-1957-ijasm-4-1-9'
        """).fetchone() == (1,)
        assert db.execute("""
            SELECT milestone,chamber_altitude_ft,clock_time,elapsed,elapsed_unit
            FROM publication_case_milestone
            WHERE source_id='majumdar57_iaf_chamber'
              AND milestone IN ('new_symptoms_at_altitude','recurrent_hypotension','documented_asymptomatic')
            ORDER BY milestone
        """).fetchall() == [
            ("documented_asymptomatic", None, "10:00", 22.0, "hours"),
            ("new_symptoms_at_altitude", 37000, None, 51.0, "minutes"),
            ("recurrent_hypotension", None, "14:30", 1.5, "hours"),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_case_milestone WHERE source_id='majumdar57_iaf_chamber'
        """).fetchone() == (8,)
        assert db.execute("""
            SELECT period FROM review.review_study
            WHERE study_id='iaf-new-delhi-june-1957-preconversion-chamber-case'
        """).fetchone() == ("1957-06-05",)


def test_italian_rate_and_taiwan_training_margins_reuse_existing_reports(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT l.report_id,p.reported_percent,p.denominator,p.denominator_unit,p.analysis_role,
                   o.related_source,o.relationship
            FROM publication_reported_rate p JOIN model_report_link l USING(source_id)
            JOIN publication_overlap o USING(source_id)
            WHERE p.source_id='biselli16_itaf_training'
        """).fetchall() == [
            ("proceedings:kindelan-25-biselli", "0.1", 1777, "trainee_record", "overlap_hold",
             "morgagni10", "unresolved")
        ]
        assert db.execute("""
            SELECT l.report_id,s.stratum,s.parent_stratum,s.trial_count,s.participant_count
            FROM publication_chamber_trial_scope s JOIN model_report_link l USING(source_id)
            WHERE s.source_id='huang26_taiwan_training' ORDER BY s.stratum
        """).fetchall() == [
            ("pmid:41881514", "all-enrolled", None, 5, 47),
            ("pmid:41881514", "inside-observers", "all-enrolled", None, 10),
            ("pmid:41881514", "trainees", "all-enrolled", None, 37),
            ("pmid:41881514", "type-i-35000-ft", "all-enrolled", 3, 31),
            ("pmid:41881514", "type-v-25000-ft", "all-enrolled", 2, 16),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_observation
            WHERE source_id IN ('biselli16_itaf_training','huang26_taiwan_training')
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT cases,denominator FROM review.review_search_observation
            WHERE report_id='proceedings:kindelan-25-biselli' AND observation_id='itaf-dcs-rounded'
        """).fetchall() == [(None, 1777)]
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE lower(title) LIKE '%oxidative stress response to simulated altitude training%'
               OR url LIKE '%military-2025-003189%'
        """).fetchall() == [("pmid:41881514",)]


def test_nasa_serious_dcs_appendix_retains_reported_counts_and_overlap(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT printed_page,count(*),sum(male_exposures),sum(serious_cases)
            FROM publication_nasa_serious_dcs_group GROUP BY printed_page ORDER BY printed_page
        """).fetchall() == [
            (40, 39, 1674, 0), (41, 45, 1178, 4), (42, 45, 61896, 375),
            (43, 45, 2891, 4), (44, 45, 9551, 195), (45, 39, 2176, 340),
        ]
        assert db.execute("""
            SELECT count(*),count(DISTINCT reference_number),sum(male_exposures),sum(serious_cases)
            FROM publication_nasa_serious_dcs_group WHERE analysis_role='overlap_hold'
        """).fetchone() == (258, 73, 79366, 918)
        assert db.execute("""
            SELECT serious_cases,source_annotation,reference_number
            FROM publication_nasa_serious_dcs_group WHERE source_annotation LIKE '%+++%'
            ORDER BY row_on_page
        """).fetchall() == [(0, "NASA 0+++", 41), (1, "NASA 1++++", 55)]
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE lower(title) LIKE '%evidence%based approach%serious decompression%'
        """).fetchall() == [("ntrs:20010020946",)]
        assert db.execute("""
            SELECT url FROM publication_source WHERE source_id='ferris44_cam363'
        """).fetchone()[0].endswith("conkin-dcs-estimation-tp210196-2001.pdf#page=39")
        assert db.execute("""
            SELECT source_id,report_id FROM model_report_link
            WHERE source_id IN ('conkin01_serious_archive','ferris44_cam363') ORDER BY source_id
        """).fetchall() == [
            ("conkin01_serious_archive", "ntrs:20010020946"),
            ("ferris44_cam363", "record:legacy:data/chamber/v1.12/search_hits.csv#raf_primary_verification:8"),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='conkin01_serious_archive'
        """).fetchone() == (0,)


def test_nasa_serious_references_link_publications_without_merging_outcomes(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT count(*),count(related_source_id),count(ascent_reference_number)
            FROM publication_nasa_serious_dcs_reference
        """).fetchone() == (73, 44, 22)
        assert db.execute("""
            SELECT count(*) FROM publication_nasa_serious_dcs_group g
            JOIN publication_nasa_serious_dcs_reference r
            ON (g.source_id,g.reference_number,g.reference_printed_page) =
               (r.source_id,r.reference_number,r.printed_reference_page)
        """).fetchone() == (258,)
        assert db.execute("""
            SELECT DISTINCT r.reference_number,a.reference_number,a.reported_outcome_window_min
            FROM publication_nasa_serious_dcs_reference r JOIN publication_ascent_compilation a
            ON (r.ascent_source_id,r.ascent_reference_number) = (a.source_id,a.reference_number)
            WHERE r.reference_number IN (56,57) AND a.analysis_role='overlap_hold'
            ORDER BY r.reference_number
        """).fetchall() == [(56, 59, 120), (57, 60, 120)]
        assert db.execute("""
            SELECT r.related_source_id,sum(g.serious_cases),sum(g.male_exposures)
            FROM publication_nasa_serious_dcs_group g
            JOIN publication_nasa_serious_dcs_reference r USING(source_id,reference_number)
            WHERE r.reference_number=9 GROUP BY r.related_source_id
        """).fetchone() == ("barer82_jprs_80323", 0, 74)
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='barer82_jprs_80323' AND stratum='all-trials'
              AND endpoint='altitude_caisson_disease_as_reported'
        """).fetchone() == (14, 74)
        assert db.execute("""
            SELECT report_id FROM model_report_link WHERE source_id='sedov80_waste_gas'
        """).fetchone() == ("pmid:6102169",)
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='sedov80_waste_gas'
        """).fetchone() == (0,)


def test_nasa_prebreathe_windows_and_grade_iv_archive_overlap(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE source_id='conkin04_sex_prebreathe' AND endpoint='dcs_as_reported'
              AND analysis_role='overlap_hold' ORDER BY stratum
        """).fetchall() == [
            ("exercise-female", 11, 51), ("exercise-male", 19, 166),
            ("resting-female", 11, 96), ("resting-male", 71, 453),
        ]
        assert db.execute("""
            SELECT sum(timed_events),count(*) FROM publication_outcome_latency_summary
            WHERE source_id='conkin04_sex_prebreathe' AND endpoint='dcs_as_reported'
        """).fetchone() == (110, 4)
        assert db.execute("""
            SELECT timed_events,mean_minutes,standard_deviation_minutes
            FROM publication_outcome_latency_summary
            WHERE source_id='conkin04_sex_prebreathe' AND endpoint='dcs_as_reported'
              AND stratum='exercise-female'
        """).fetchone() == (9, 118.2, 29.3)
        assert db.execute("""
            SELECT substr(stratum,1,8),sum(numerator),sum(denominator)
            FROM publication_observation WHERE source_id='thompson02_grade_iv'
              AND endpoint='grade_iv_vge' AND analysis_role='overlap_hold'
              AND stratum LIKE 'table-%' GROUP BY substr(stratum,1,8) ORDER BY stratum
        """).fetchall() == [(f"table-2{table}", 123, 548) for table in "abcd"]
        assert db.execute("""
            SELECT numerator,denominator FROM publication_observation
            WHERE source_id='thompson02_grade_iv' AND stratum='full-before-equipment-exclusion'
        """).fetchone() == (124, 549)
        assert db.execute("""
            SELECT source_id,report_id FROM model_report_link
            WHERE source_id IN ('conkin04_sex_prebreathe','thompson02_grade_iv') ORDER BY source_id
        """).fetchall() == [
            ("conkin04_sex_prebreathe", "openalex:W2181311634"),
            ("thompson02_grade_iv", "openalex:W1651164841"),
        ]
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE report_id IN ('openalex:W2181311634','openalex:W1651164841')
              AND role_review='overlap_hold'
        """).fetchone() == (42,)
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE lower(title) LIKE '%limited failure population model with random effects%'
        """).fetchall() == [("openalex:W1651164841",)]


def test_nasa_shuttle_doppler_counting_unit_revision_preserves_existing_rows(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT o.stratum,o.numerator,o.denominator,r.previous_unit,r.revised_unit
            FROM publication_observation_counting_unit_revision r
            JOIN publication_observation o USING(source_id,stratum,endpoint)
            WHERE r.evidence_source_id='vann85_ada151800'
              AND o.denominator_unit=r.revised_unit AND o.analysis_role='overlap_hold'
            ORDER BY o.stratum
        """).fetchall() == [
            ("max-spencer-0", 0, 75, "person", "person_exposure"),
            ("max-spencer-I", 1, 6, "person", "person_exposure"),
            ("max-spencer-II", 2, 12, "person", "person_exposure"),
            ("max-spencer-III", 8, 25, "person", "person_exposure"),
            ("max-spencer-IV", 29, 55, "person", "person_exposure"),
        ]
        assert db.execute("""
            SELECT count(*) FROM publication_observation
            WHERE source_id IN ('vann85_ada151800','horrigan84_six_hour_doppler')
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT source_id,report_id FROM model_report_link
            WHERE source_id IN ('vann85_ada151800','horrigan84_six_hour_doppler') ORDER BY source_id
        """).fetchall() == [
            ("horrigan84_six_hour_doppler", "abstract:asma-1984-horrigan-451"),
            ("vann85_ada151800", "report:ada151800"),
        ]
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='openalex:W920476218' AND right_report='report:ada151800'
        """).fetchall() == [("same_altitude_counts_by_doppler_grade",)]


def test_temperature_sources_and_delayed_case_preserve_outcomes(release):
    with connect_pair(release) as db:
        grades = db.execute("""
            SELECT stratum,endpoint,numerator,denominator,denominator_unit
            FROM publication_observation WHERE source_id='fraser42_rose_thermal'
              AND analysis_role='overlapping_margin' AND denominator_basis='author_reconstructed'
            ORDER BY stratum,endpoint
        """).fetchall()
        assert [(group, count, denominator) for group, _, count, denominator, _ in grades] == [
            ("cold", 23, 94), ("cold", 17, 94), ("cold", 14, 94), ("cold", 40, 94),
            ("warm", 46, 93), ("warm", 17, 93), ("warm", 11, 93), ("warm", 19, 93),
        ]
        assert db.execute("""
            SELECT reported_group,endpoint,cases,denominator,denominator_unit
            FROM review.review_search_observation
            WHERE report_id='report:nrcc-fraser-rose-1942-low-temperature'
              AND role_review='overlapping_margin'
            ORDER BY reported_group,endpoint
        """).fetchall() == grades
        assert db.execute("""
            SELECT reported_group,cases,reported_rate_percent,denominator,denominator_unit
            FROM review.review_search_observation WHERE report_id='report:cam-352'
              AND role_review='overlapping_margin'
            ORDER BY reported_group
        """).fetchall() == [
            ("paired-control", None, 61.8, 34, "person"),
            ("paired-left-leg-diathermy", None, 14.7, 34, "person"),
        ]
        assert db.execute("""
            SELECT stratum,reported_percent,denominator
            FROM publication_reported_rate WHERE source_id='tobias44_cam352_thermal'
            ORDER BY stratum
        """).fetchall() == [("paired-control", "61.8", 34), ("paired-left-leg-diathermy", "14.7", 34)]
        assert db.execute("""
            SELECT e.report_id,e.onset_min,r.cases,r.denominator,o.analysis_role
            FROM shared_case_evidence e
            JOIN review.review_search_observation r USING(record_key,observation_id,report_id)
            JOIN publication_observation o USING(source_id,stratum,endpoint)
            WHERE e.source_id='laverdiere25_chamber_case' AND r.role_review='selected_cluster'
        """).fetchall() == [("abstract:asma-2025-laverdiere-208", None, 1, None, "selected_cluster")]
        assert db.execute("""
            SELECT milestone,elapsed FROM publication_case_milestone
            WHERE source_id='laverdiere25_chamber_case' ORDER BY milestone
        """).fetchall() == [
            ("delayed_symptom_report_after_exercise", None),
            ("hyperbaric_treatment_adverse_event", None),
            ("hypobaric_chamber_exposure", None),
            ("return_to_duties", None),
        ]


def test_altitude_residence_keeps_overlapping_chamber_outcomes_once(release):
    with connect_pair(release) as db:
        expected = [
            ("morococha-38000", 0, 10, "person"),
            ("mount-evans-i-38000-after-48h", 2, 7, "person"),
            ("mount-evans-ii-40000", 0, 2, "person"),
            ("mount-evans-ii-50000", 1, 2, "person"),
        ]
        assert db.execute("""
            SELECT stratum,numerator,denominator,denominator_unit
            FROM publication_observation WHERE source_id IN (
                'balke59_altitude_residence','clark60_space_medicine_residence',
                'roth67_sp117_altitude_residence','balke59_usaf_ad226473'
            ) AND analysis_role='overlap_hold' ORDER BY stratum
        """).fetchall() == expected
        assert db.execute("""
            SELECT reported_group,cases,denominator,denominator_unit
            FROM review.review_search_observation
            WHERE run_id='2026-11-21-altitude-residence-verified' AND role_review='overlap_hold'
            ORDER BY reported_group
        """).fetchall() == expected
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id IN (
                'roth67_sp117_altitude_residence','balke59_usaf_ad226473'
            )
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT report_id,relationship FROM model_report_link JOIN publication_overlap USING(source_id)
            WHERE related_source='balke59_altitude_residence' ORDER BY report_id
        """).fetchall() == [
            ("ntrs:19670013549", "partial_overlap"),
            ("pmid:13810481", "partial_overlap"),
            ("report:ad226473:balke-man-in-space", "likely_overlap"),
        ]
        assert db.execute("""
            SELECT json_extract(metadata_json,'$.discrepancies[0].clark'),
                   json_extract(metadata_json,'$.discrepancies[0].roth')
            FROM review.review_record
            WHERE record_key='2026-11-21-altitude-residence-verified#roth67_sp117_altitude_residence'
        """).fetchone() == (455, 446)


def test_wartime_cadet_results_preserve_native_endpoints_and_conflicts(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator,analysis_role
            FROM publication_observation
            WHERE source_id IN ('aaf_wartime_dcs_summary','gemmill42_cam_pensacola_classification')
            ORDER BY stratum
        """).fetchall() == [
            ("pensacola-one-hour-classification", 40, 500, "overlap_hold"),
            ("randolph-four-hour-38000", 283, 723, "denominator_conflict"),
        ]
        assert db.execute("""
            SELECT cases,denominator,reported_rate_percent
            FROM review.review_search_observation
            WHERE report_id='report:aaf-c-509-1' AND reported_group='randolph-four-hour-38000'
        """).fetchall() == [(283, 723, 37.0)]
        model_rates = db.execute("""
            SELECT stratum,endpoint,CAST(reported_percent AS REAL),denominator,denominator_unit
            FROM publication_reported_rate
            WHERE source_id='aaf_wartime_dcs_summary' AND analysis_role='overlap_hold'
            ORDER BY stratum,endpoint
        """).fetchall()
        assert len(model_rates) == 8
        assert [row[1:4] for row in model_rates if row[0] == "pensacola-35000"] == [
            ("chokes_as_reported", 0.8, 500), ("joint_pain_as_reported", 24.0, 500),
            ("skin_symptoms_as_reported", 15.0, 500),
        ]
        assert db.execute("""
            SELECT reported_group,endpoint,reported_rate_percent,denominator,denominator_unit
            FROM review.review_search_observation WHERE report_id='report:aaf-c-509-1' AND cases IS NULL
            ORDER BY reported_group,endpoint
        """).fetchall() == model_rates
        assert db.execute("""
            SELECT report_id FROM review.review_record
            WHERE record_key='legacy:data/chamber/v1.40/search_hits.csv#diagnosis_v40_status:1'
        """).fetchone() == ("report:aaf-c-509-1",)
        assert db.execute("""
            SELECT relationship FROM publication_overlap
            WHERE source_id='aaf_wartime_dcs_summary' AND related_source='gray47_selection'
        """).fetchone() == ("partial_overlap",)
        assert db.execute("""
            SELECT trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE source_id='aaf_wartime_dcs_summary' AND stratum='wright-1941-91'
        """).fetchone() == (396, 91)


def test_halifax_and_cincinnati_use_original_counts_and_keep_units_separate(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,numerator,denominator,denominator_unit
            FROM publication_observation
            WHERE source_id='stewart43_halifax_standard_524'
              AND endpoint IN ('decompression_sickness_as_reported','ever_dcs_as_reported')
            ORDER BY stratum
        """).fetchall() == [
            ("all-flights", 1102, 1268, "person_exposure"), ("all-people", 498, 524, "person"),
            ("first-flight", 458, 524, "person_exposure"), ("one-run-only", 73, 84, "person"),
            ("second-flight", 380, 440, "person_exposure"), ("third-flight", 264, 304, "person_exposure"),
            ("three-runs-only", 296, 304, "person"), ("two-runs-only", 129, 136, "person"),
        ]
        assert db.execute("""
            SELECT stratum,SUM(numerator),MIN(denominator),MAX(denominator)
            FROM publication_observation
            WHERE source_id='stewart43_halifax_standard_524' AND endpoint GLOB 'classification_?'
            GROUP BY stratum ORDER BY stratum
        """).fetchall() == [
            ("all-flights", 1268, 1268, 1268), ("first-flight", 524, 524, 524),
            ("second-flight", 440, 440, 440), ("third-flight", 304, 304, 304),
        ]
        assert db.execute("""
            SELECT endpoint,numerator,denominator FROM publication_observation
            WHERE source_id='ferris43_cincinnati_selection'
              AND endpoint IN ('bends_grade_iv_descent_as_reported','chokes_severe_descent_as_reported')
            ORDER BY endpoint
        """).fetchall() == [("bends_grade_iv_descent_as_reported", 44, 102), ("chokes_severe_descent_as_reported", 2, 102)]
        assert db.execute("""
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE source_id='ferris42_fulton_letter' ORDER BY stratum
        """).fetchall() == [("delayed-local-pain", 4, None), ("early-35000", 9, 9)]
        assert db.execute("""
            SELECT count(*) FROM publication_reported_rate
            WHERE source_id='henry_ivy51_preselection' AND endpoint GLOB 'classification_*'
              AND (stratum GLOB 'cincinnati-*' OR stratum GLOB 'halifax-*')
        """).fetchone() == (0,)
        assert db.execute("""
            SELECT count(*) FROM review.review_search_observation
            WHERE run_id='2026-11-21-cincinnati-halifax-verified' AND role_review='overlap_hold'
        """).fetchone() == (51,)


def test_chamber_retest_paths_reconcile_without_duplicate_clinical_events(release):
    with connect_pair(release) as db:
        run_id = "2026-11-21-chamber-retest-paths-verified"
        review_rows = db.execute("""
            SELECT report_id,reported_group,endpoint,cases,denominator,denominator_unit,role_review,locator
            FROM review.review_search_observation WHERE run_id=?
            ORDER BY report_id,reported_group,endpoint
        """, (run_id,)).fetchall()
        assert len(review_rows) == 80
        assert {row[0] for row in review_rows} == {
            "nlm:101085500x233:220:ferris", "nlm:101085500x233:228:halifax-validation",
        }
        assert {(row[5], row[6]) for row in review_rows} == {("person", "overlap_hold")}
        assert db.execute("""
            SELECT DISTINCT m.report_id,p.stratum,p.endpoint,p.numerator,p.denominator,
                            p.denominator_unit,p.analysis_role,p.locator
            FROM publication_observation p JOIN model_report_link m USING(source_id)
            JOIN review.review_search_observation r ON r.report_id=m.report_id
                 AND r.reported_group=p.stratum AND r.endpoint=p.endpoint
            WHERE r.run_id=? AND m.source_table='publication_source'
            ORDER BY m.report_id,p.stratum,p.endpoint
        """, (run_id,)).fetchall() == review_rows

        groups = {}
        for _, group, endpoint, count, total, *_ in review_rows:
            groups.setdefault(group, {})[endpoint] = (count, total)

        for altitude, size, tables in [
            (38000, 16, {
                (0, 1): [27, 13, 13, 25], (0, 2): [29, 11, 11, 27],
                (1, 3): [26, 14, 14, 24], (0, 3): [27, 13, 13, 25],
            }),
            (35000, 8, {(0, 1): [32, 7, 8, 31], (0, 2): [28, 11, 11, 28]}),
        ]:
            rows = groups[f"cincinnati-retest-{altitude}"]
            assert len(rows) == size
            assert {total for _, total in rows.values()} == {78}
            paths = {key.removeprefix("classification_path_"): count for key, (count, _) in rows.items()}
            assert sum(paths.values()) == 78
            for (i, j), counts in tables.items():
                assert [
                    sum(count for path, count in paths.items() if (path[i], path[j]) == (first, second))
                    for first in "pf" for second in "pf"
                ] == counts
        assert db.execute("""
            SELECT json_extract(metadata_json,'$.discrepancies[0].printed_table[1][0]'),
                   json_extract(metadata_json,'$.discrepancies[0].diagram[1][0]')
            FROM review.review_record WHERE run_id=? AND source_key='ferris43_cincinnati_selection'
        """, (run_id,)).fetchone() == (7, 8)

        for group, total, size, unchanged, crossed in [
            ("halifax-two-test-path", 136, 16, 53, 54),
            ("halifax-three-test-pattern", 304, 20, 78, 156),
        ]:
            rows = groups[group]
            margin = "classification_crossed_ab_cd_threshold_as_reported"
            assert rows[margin] == (crossed, total)
            assert {denominator for _, denominator in rows.values()} == {total}
            patterns = {key.split("_")[-1]: count for key, (count, _) in rows.items() if key != margin}
            assert len(patterns) == size
            assert sum(patterns.values()) == total
            assert sum(count for key, count in patterns.items() if len(set(key)) == 1) == unchanged
            assert sum(
                count for key, count in patterns.items() if set(key) & {"a", "b"} and set(key) & {"c", "d"}
            ) == crossed

        assert groups["halifax-three-test-pattern"]["classification_unordered_pattern_bdc"] == (6, 304)
        for group, counts, total, censoring in [
            ("halifax-three-test-all-descended", [11, 25, 19, 15, 9, 6, 3, 1, 0], 89, 0),
            ("halifax-three-test-descent-and-completion", [9, 16, 14, 22, 32, 30, 21, 13, 1], 158, 1),
        ]:
            assert list(groups[group].values()) == [(count, total) for count in counts]
            assert db.execute("""
                SELECT DISTINCT json_extract(o.value,'$.latest_descent_right_censored')
                FROM review.review_record r JOIN json_each(r.metadata_json,'$.observations') o
                WHERE r.run_id=? AND json_extract(o.value,'$.group')=?
            """, (run_id, group)).fetchall() == [(censoring,)]


def test_standard_test_comparisons_keep_rounding_and_denominator_scope(release):
    with connect_pair(release) as db:
        run_id = "2026-11-21-standard-test-comparisons-verified"
        checked = {
            "california-classification": (53, [50, 15, 17, 7]),
            "pennsylvania-first-flight": (37, [30, 19, 35, 15]),
            "yale-first-flight": (92, [9, 12, 61, 18]),
        }
        expected = [
            (group, f"classification_{grade}", pct, count)
            for group, (count, percentages) in checked.items()
            for grade, pct in zip("abcd", percentages, strict=True)
        ]
        assert db.execute("""
            SELECT stratum,endpoint,CAST(reported_percent AS REAL),denominator
            FROM publication_reported_rate WHERE stratum IN (?,?,?) AND analysis_role='overlap_hold'
            ORDER BY stratum,endpoint
        """, tuple(checked)).fetchall() == expected
        assert db.execute("""
            SELECT reported_group,endpoint,reported_rate_percent,denominator
            FROM review.review_search_observation
            WHERE run_id=? AND reported_rate_percent IS NOT NULL AND denominator IS NOT NULL
            ORDER BY reported_group,endpoint
        """, (run_id,)).fetchall() == expected
        assert db.execute("""
            SELECT reported_group,endpoint,reported_rate_percent
            FROM review.review_search_observation WHERE run_id=? AND denominator IS NULL
              AND cases IS NULL AND role_review='overlap_hold' ORDER BY reported_group,endpoint
        """, (run_id,)).fetchall() == [
            (f"pennsylvania-retests-first-{first}", f"classification_{grade}", pct)
            for first, rates in [
                ("a", [79, 9, 12, 0]), ("all", [48, 13, 28, 11]), ("b", [38, 14, 29, 19]),
                ("c", [33, 13, 41, 13]), ("d", [39, 17, 28, 17]),
            ]
            for grade, pct in zip("abcd", rates, strict=True)
        ] + [("yale-second-flight-first-ab", "classification_ab", 68),
             ("yale-second-flight-first-cd", "classification_ab", 23)]
        assert db.execute("""
            SELECT count(*) FROM publication_reported_rate
            WHERE stratum GLOB 'pennsylvania-retests-*' OR stratum GLOB 'yale-second-flight-*'
        """).fetchone() == (0,)

        expected_counts = [("california-classification", 44, 53), ("cincinnati-seven-test-discussion", 2, 83)]
        assert db.execute("""
            SELECT stratum,numerator,denominator FROM publication_observation
            WHERE stratum IN ('california-classification','cincinnati-seven-test-discussion')
              AND analysis_role='overlap_hold' AND denominator_unit='person' ORDER BY stratum
        """).fetchall() == expected_counts
        assert db.execute("""
            SELECT reported_group,cases,denominator FROM review.review_search_observation
            WHERE run_id=? AND cases IS NOT NULL AND role_review='overlap_hold' ORDER BY reported_group
        """, (run_id,)).fetchall() == expected_counts
        assert db.execute("""
            SELECT json_extract(metadata_json,'$.discrepancies[0].investigator_minutes[0]'),
                   json_extract(metadata_json,'$.discrepancies[0].later_table_74[0]')
            FROM review.review_record WHERE run_id=? AND source_key='lawrence43_california_preselection'
        """, (run_id,)).fetchone() == (50, 60)
        assert db.execute("""
            SELECT report_id FROM review.review_study_report
            WHERE study_id='grenell-1944-yale-preselection' ORDER BY report_id
        """).fetchall() == [("fulton1951:preselection-tests",), ("report:cam-355",)]


def test_historical_taiwan_surveillance_preserves_sessions_and_all_cause_reactions(release):
    with connect_pair(release) as db:
        report = "isbn:9789572950715:fang-taiwan-aviation-medicine"
        assert db.execute("""
            SELECT endpoint,numerator,denominator,denominator_unit,analysis_role
            FROM publication_observation WHERE source_id='fang99_taiwan_chamber_reactions'
        """).fetchall() == [("any_chamber_reaction_as_reported", 696, 15370, "person_exposure", "overlap_hold")]
        assert db.execute("""
            SELECT endpoint,cases,denominator,denominator_unit,role_review,reported_rate_percent
            FROM review.review_search_observation WHERE report_id=?
        """, (report,)).fetchall() == [
            ("any_chamber_reaction_as_reported", 696, 15370, "person_exposure", "overlap_hold", 4.5),
        ]
        assert db.execute("""
            SELECT trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE source_id='fang99_taiwan_chamber_reactions'
        """).fetchall() == [(1578, None)]
        assert db.execute("""
            SELECT report_id,count(*) FROM review.review_record
            WHERE url='https://irvingthofoundation.github.io/drfang_book_full_version.pdf'
            GROUP BY report_id
        """).fetchall() == [("isbn:9789572950715", 5)]
        assert db.execute("""
            SELECT right_report FROM review.review_report_relation WHERE left_report=?
              AND relationship='likely_overlap' ORDER BY right_report
        """, (report,)).fetchall() == [
            ("pmid:3167655",), ("record:legacy:data/chamber/v1.18/sources.csv#ho88_taiwan_survey",),
        ]
        assert db.execute("""
            SELECT source_id FROM publication_observation
            WHERE source_id IN ('wen88_taiwan_survey','ho88_taiwan_survey','dlr19_protected_registry')
        """).fetchall() == []
        assert db.execute("""
            SELECT trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE source_id='dlr19_protected_registry'
        """).fetchall() == [(None, 6)]
        assert db.execute("""
            SELECT json_extract(metadata_json,'$.actual_enrolled'),
                   json_type(metadata_json,'$.clinical_dcs_count')
            FROM review.review_record WHERE report_id='drks:00016337' AND run_id IS NOT NULL
        """).fetchone() == (6, "null")


def test_lee_hay_outcome_checkpoints_link_to_existing_terminal_totals(release):
    with connect_pair(release) as db:
        checkpoints = db.execute("""
            SELECT c.stratum,c.endpoint,c.elapsed_min,c.cumulative_events,
                   p.denominator,c.analysis_role,c.locator,p.numerator
            FROM publication_outcome_checkpoint c JOIN publication_observation p USING(source_id,stratum,endpoint)
            WHERE c.source_id='lee_hay01'
            ORDER BY c.stratum,c.endpoint,c.elapsed_min
        """).fetchall()
        assert len(checkpoints) == 147
        assert db.execute("""
            SELECT reported_group,endpoint,elapsed_min,cases,denominator,role_review,locator
            FROM review.review_search_observation
            WHERE run_id='2026-11-21-lee-hay-outcome-timing-verified' AND denominator_unit='person_exposure'
            ORDER BY reported_group,endpoint,elapsed_min
        """).fetchall() == [row[:-1] for row in checkpoints]

        curves = {}
        for group, endpoint, minute, count, denominator, role, _, final in checkpoints:
            assert denominator == 15 and role == "overlap_hold"
            assert 0 <= count <= final <= denominator
            curves.setdefault((group, endpoint), []).append((minute, count))
        assert len(curves) == 21
        for values in curves.values():
            minutes, counts = zip(*values, strict=True)
            assert minutes == tuple(range(30, 240, 30))
            assert list(counts) == sorted(counts)
        assert [
            [count for _, count in values]
            for (_, endpoint), values in curves.items() if endpoint == "dci_symptoms_recompression"
        ] == [
            [0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 1, 1], [0, 1, 1, 3, 8, 9, 9],
            [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 4, 5, 6, 8], [0, 0, 1, 1, 2, 4, 6], [0, 1, 3, 6, 7, 7, 8],
        ]
        for group in {key[0] for key in curves}:
            assert all(
                high_grade <= any_grade for (_, high_grade), (_, any_grade) in zip(
                    curves[group, "spencer_grade_iv_vge"], curves[group, "vge_any"], strict=True,
                )
            )
        assert db.execute("""
            SELECT endpoint,count(*),sum(numerator) FROM publication_observation
            WHERE source_id='lee_hay01' AND denominator=15
              AND endpoint IN ('dci_symptoms_recompression','spencer_grade_iv_vge','vge_any')
            GROUP BY endpoint ORDER BY endpoint
        """).fetchall() == [("dci_symptoms_recompression", 7, 33), ("spencer_grade_iv_vge", 7, 54), ("vge_any", 7, 78)]
        assert db.execute("""
            SELECT count(DISTINCT report_id),count(*) FROM review.review_record WHERE record_key IN (
                'legacy:data/chamber/v1.14/sources.csv#lee_hay01',
                'legacy:data/chamber/v1.14/search_hits.csv#crossover_v14_originals:3',
                'legacy:data/chamber/v1.15/search_hits.csv#historic_v15_harding:1',
                '2026-11-21-lee-hay-outcome-timing-verified#lee_hay01'
            )
        """).fetchone() == (1, 4)


def test_barron_cabin_decompression_counts_preserve_the_printed_disagreement(release):
    with connect_pair(release) as db:
        model = db.execute("""
            SELECT stratum,endpoint,numerator,denominator,denominator_unit,analysis_role
            FROM publication_observation WHERE source_id='barron58_12_second_decompression'
            ORDER BY stratum
        """).fetchall()
        review = db.execute("""
            SELECT reported_group,endpoint,cases,denominator,denominator_unit
            FROM review.review_search_observation
            WHERE run_id='2026-11-21-cabin-decompression-scopes-verified' AND report_id='pmid:13575359'
            ORDER BY reported_group
        """).fetchall()
        assert review == [row[:-1] for row in model]
        assert len(model) == 24
        assert {row[1] for row in model} == {"hypoxia_reactions_as_reported"}
        assert {row[-1] for row in model} == {"denominator_conflict"}
        assert model[-1][0] == "barron58-printed-overall"
        assert model[-1][2:4] == (88, 154)
        assert tuple(map(sum, zip(*(row[2:4] for row in model[:-1])))) == (89, 154)
        assert db.execute("""
            SELECT trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE source_id='barron58_12_second_decompression' AND stratum='barron58-combined-flights'
        """).fetchone() == (154, None)
        assert db.execute("""
            SELECT count(*) FROM publication_overlap
            WHERE source_id='barron58_12_second_decompression' AND relationship='unresolved'
        """).fetchone() == (2,)


def test_donaldson_cabin_protocols_count_repeat_exposures_once(release):
    with connect_pair(release) as db:
        assert db.execute("""
            SELECT stratum,trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE source_id='donaldson60_cabin_descent'
            ORDER BY stratum
        """).fetchall() == [
            ("donaldson60-alcohol-repeat", 3, 3),
            ("donaldson60-four-oxygen-conditions", 35, 10),
            ("donaldson60-oxygen-15-second-delay", 10, 10),
            ("donaldson60-oxygen-30-second-delay", 9, 9),
            ("donaldson60-oxygen-immediate", 9, 9),
            ("donaldson60-oxygen-none", 7, 4),
        ]
        assert db.execute("""
            SELECT endpoint,numerator,denominator
            FROM publication_observation WHERE source_id='donaldson60_cabin_descent'
        """).fetchall() == [("protocol_noncompletion_as_reported", 2, 7)]
        assert db.execute("""
            SELECT endpoint,cases,denominator FROM review.review_search_observation
            WHERE run_id='2026-11-21-cabin-decompression-scopes-verified' AND report_id='pmid:13723694'
        """).fetchall() == [("protocol_noncompletion_as_reported", 2, 7)]


def test_pressure_breathing_reports_keep_their_native_outcomes_and_counts(release):
    with connect_pair(release) as db:
        expected = [
            ("barron-variable-decompression", "aeroembolism_symptoms_as_reported", 0, 8, "person_exposure", "overlap_hold"),
            ("marotte-pressure-schedule", "aeroembolism_symptoms_as_reported", 0, None, None, "overlap_hold"),
            ("marotte-pressure-schedule", "dysbaric_disturbance_analysis_exclusion", 1, 11, "person", "descriptive"),
        ]
        assert db.execute("""
            SELECT stratum,endpoint,numerator,denominator,denominator_unit,analysis_role
            FROM publication_observation WHERE source_id IN (
                'barron65_variable_decompression','marotte90_pressure_schedule',
                'marotte90_transport_hypoxia','holness80_phoenix','ernsting60_mask_helmet'
            ) ORDER BY stratum,endpoint
        """).fetchall() == expected
        assert db.execute("""
            SELECT reported_group,endpoint,cases,denominator,denominator_unit
            FROM review.review_search_observation
            WHERE run_id='2026-11-21-pressure-breathing-outcomes-verified'
            ORDER BY reported_group,endpoint
        """).fetchall() == [row[:-1] for row in expected]
        assert db.execute("""
            SELECT source_id,trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE stratum IN ('marotte-rapid-decompression-tests','marotte-pressure-schedule')
            ORDER BY source_id
        """).fetchall() == [
            ("marotte90_pressure_schedule", None, 11),
            ("marotte90_transport_hypoxia", 105, 10),
        ]
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='pmid:2205195' AND right_report='pmid:2302122'
        """).fetchone() == ("unresolved",)
        assert db.execute("""
            SELECT DISTINCT report_id FROM review.review_record
            WHERE doi='10.1518/001872097778940641' OR pmid='9302882'
        """).fetchall() == [("doi:10.1518/001872097778940641",)]


def test_lee_hay_left_ventricular_onset_uses_existing_profile_events(release):
    with connect_pair(release) as db:
        record = db.execute("""
            SELECT report_id, metadata_json FROM review.review_record
            WHERE record_key='2026-11-21-pressure-breathing-outcomes-verified#lee_hay01'
        """).fetchone()
        assert record[0] == "record:legacy:data/chamber/v1.14/search_hits.csv#crossover_v14_originals:3"
        source = json.loads(record[1])["left_ventricular_onset"]
        expected = [
            ("ft20500_o2_56_prebreathe_0", 1, "single_detection", 212, None, "4"),
            ("ft22500_o2_56_prebreathe_0", 1, "single_detection", 77, None, "3"),
            ("ft25000_o2_100_prebreathe_0", 1, "single_detection", 195, None, "4"),
            ("ft25000_o2_63_prebreathe_0", 2, "mean_sd", 63, 24, "4/4"),
            ("ft35000_o2_100_prebreathe_60", 1, "single_detection", 150, None, "4"),
        ]
        assert sorted(
            (row["stratum"], row["detections_in_existing_stratum"], row["time_basis"],
             row["onset_min"], row["standard_deviation_min"], row["associated_vge_grades"])
            for row in source
        ) == expected
        assert db.execute("""
            SELECT n.stratum,o.numerator,n.time_basis,n.onset_min,n.standard_deviation_min,n.associated_vge_grades
            FROM publication_outcome_onset n
            JOIN publication_observation o USING (source_id,stratum,endpoint)
            WHERE n.source_id='lee_hay01' AND n.endpoint='left_ventricular_gas_source'
            ORDER BY n.stratum
        """).fetchall() == expected


def test_rapid_decompression_zeros_are_limited_to_the_verified_crossover(release):
    with connect_pair(release) as db:
        run_id = "2026-11-21-brief-rapid-decompression-verified"
        expected = [
            (arm, endpoint, 0, 8, "person_exposure", "overlap_hold")
            for arm in ("fraser-combat-edge", "fraser-tlss")
            for endpoint in ("dcs_symptoms_as_reported", "doppler_any_vge_as_reported")
        ]
        assert db.execute("""
            SELECT stratum,endpoint,numerator,denominator,denominator_unit,analysis_role
            FROM publication_observation WHERE source_id='fraser94_rapid_decompression'
              AND altitude=60000 AND altitude_unit='ft' AND prebreathe_min IS NULL
            ORDER BY stratum,endpoint
        """).fetchall() == expected
        assert db.execute("""
            SELECT reported_group,endpoint,cases,denominator,denominator_unit,role_review
            FROM review.review_search_observation WHERE run_id=? ORDER BY reported_group,endpoint
        """, (run_id,)).fetchall() == expected
        assert db.execute("""
            SELECT stratum,trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE source_id IN ('fraser94_rapid_decompression','fraser92_rapid_abstract') ORDER BY stratum
        """).fetchall() == [
            ("fraser-combat-edge", 8, 8), ("fraser-familiarization", None, 8),
            ("fraser-preliminary-abstract", None, 6), ("fraser-randomized-comparison", 16, 8),
            ("fraser-tlss", 8, 8),
        ]
        assert db.execute("""
            SELECT json_type(metadata_json,'$.dcs_follow_up_min'),
                   json_extract(metadata_json,'$.vge_follow_up_min'),
                   json_extract(metadata_json,'$.observations[0].prebreathe_min_lower_bound')
            FROM review.review_record WHERE run_id=? AND report_id='pmid:8185549'
        """, (run_id,)).fetchone() == ("null", 120, 60)
        assert db.execute("""
            SELECT relationship FROM review.review_report_relation
            WHERE left_report='asma:1992:524' AND right_report='pmid:8185549'
        """).fetchone() == ("likely_overlap",)
        assert db.execute("""
            SELECT source_id,trial_count,participant_count FROM publication_chamber_trial_scope
            WHERE source_id IN ('bancroft64_rapid_decompression','connolly13_rapid_decompression') ORDER BY source_id
        """).fetchall() == [("bancroft64_rapid_decompression", 7, 5), ("connolly13_rapid_decompression", 12, 6)]
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id IN (
                'fraser92_rapid_abstract','bancroft64_rapid_decompression',
                'connolly13_rapid_decompression','gradwell93_thesis'
            )
        """).fetchone() == (0,)
