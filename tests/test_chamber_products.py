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
        """).fetchone() == (3, 1)
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
            (1, "90-min-prebreathe", "dcs_neurological", "likely_same_episode", 4.3, 90, 1, None, 29.6),
            (2, "20-min-prebreathe", "dcs_type_ii_source", "likely_same_episode", 5.2, 20, 1, None, None),
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
        """).fetchone() == (3, 2, 0)
        assert db.execute("""
            SELECT count(*) FROM publication_observation WHERE source_id='lam26_nasa_neuro'
        """).fetchone() == (0,)


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
        assert tuple(db.execute("""
            SELECT count(*),count(DISTINCT report_id) FROM review.review_record
            WHERE url LIKE '%20040191712%' OR openalex_id='W118136854'
        """).fetchone()) == (5, 1)
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
        assert db.execute("SELECT count(*) FROM historical_case_catalog").fetchone() == (119,)


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
        assert db.execute("SELECT count(*) FROM historical_case_catalog").fetchone() == (119,)


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
            WHERE left_report='pmid:14050686' ORDER BY right_report
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
        assert db.execute("""
            SELECT count(*), count(DISTINCT c.case_id), count(r.record_key)
            FROM historical_case_catalog c LEFT JOIN review.review_record r
            ON (r.record_key,r.report_id)=(c.record_key,c.report_id)
        """).fetchone() == (119, 119, 119)
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
        """).fetchone() == (129, 1, "doi:10.28920/dhm51.1.82-85")
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
