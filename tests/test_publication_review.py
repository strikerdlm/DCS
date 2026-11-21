import sqlite3

import pytest

from scripts.build_chamber_database import build


def test_publication_register_build(tmp_path):
    path = tmp_path / "observed.sqlite"
    digest = build(path, publication_review=True)
    assert build(path, publication_review=True) == digest
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        assert db.execute(
            "SELECT sum(registered_dcs_events) FROM fac_official_chamber_year"
        ).fetchone() == (54,)
        assert db.execute("SELECT count(*) FROM review_record WHERE run_id IS NULL").fetchone() == (
            4395,
        )
        assert db.execute(
            "SELECT source_key,report_id FROM review_record "
            "WHERE stream='data/chamber/v1.62/sources.csv' ORDER BY source_key"
        ).fetchall() == [
            ("ferris51_clinical_nature", "fulton1951:clinical-nature"),
            ("lawrence45_two_reactions", "bumed:1945:4-7:3"),
            ("lund44_cam396", "report:cam-396"),
        ]
        assert db.execute(
            "SELECT count(*) FROM review_record JOIN review_retrieval USING(run_id) "
            "WHERE run_date='2026-11-19'"
        ).fetchone() == (66,)
        run_counts = db.execute(
            "SELECT c.run_id,c.reported_total,c.retrieved FROM review_run_counts c "
            "JOIN review_retrieval q USING(run_id) "
            "WHERE q.snapshot LIKE '%/retrievals-2026-11-20.json' ORDER BY c.run_id"
        ).fetchall()
        assert run_counts == [
            ("2026-11-20-eds-role", 27, 15),
            ("2026-11-20-eds-seed", 21, 9),
            ("2026-11-20-eds-training", 249, 40),
            ("2026-11-20-primary-followup", None, 2),
        ]
        assert db.execute(
            "SELECT provider, sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-supplementary.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0 "
            "GROUP BY provider ORDER BY provider"
        ).fetchall() == [("Firecrawl", 25), ("OpenAlex", 95), ("Tavily", 42), ("Undermind", 67)]
        assert db.execute(
            "SELECT count(*),count(doi) FROM review_record "
            "WHERE run_id LIKE '2026-11-20-undermind-%' AND source_key='Bas76' "
            "AND report_id='pmid:971183'"
        ).fetchone() == (3, 0)
        assert db.execute(
            "SELECT report_id FROM review_record WHERE run_id='2026-11-20-firecrawl-bason-doi'"
        ).fetchone() == ("doi:10.1097/00006534-197708000-00114",)
        assert db.execute(
            "SELECT provider, sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-followup.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0 "
            "GROUP BY provider ORDER BY provider"
        ).fetchall() == [("Firecrawl", 23), ("OpenAlex", 61), ("Tavily", 65), ("Undermind", 35)]
        assert db.execute(
            "SELECT report_id,doi FROM review_record WHERE record_key='2026-11-20-undermind-references#Dav77'"
        ).fetchone() == ("pmid:889546", None)
        assert db.execute(
            "SELECT report_id FROM review_record WHERE run_id='2026-11-20-followup-firecrawl-davis-digest'"
        ).fetchone() == ("doi:10.1097/00006534-197805000-00116",)
        assert db.execute(
            "SELECT provider, sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-archival.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0 "
            "GROUP BY provider ORDER BY provider"
        ).fetchall() == [
            ("Firecrawl", 5), ("OpenAlex", 61), ("Source citation audit", 2),
            ("Tavily", 43), ("Undermind", 20),
        ]
        assert db.execute(
            "SELECT provider,sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-role-coverage.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0 "
            "GROUP BY provider ORDER BY provider"
        ).fetchall() == [
            ("Firecrawl", 11), ("OpenAlex", 12), ("Source citation audit", 1),
            ("Tavily", 74), ("Undermind", 20),
        ]
        seed_reports = {
            row[0]
            for row in db.execute(
                "SELECT report_id FROM review_record WHERE run_id='2026-11-20-eds-seed' "
                "AND json_extract(metadata_json,'$.role_review')='existing_role_candidate'"
            )
        }
        assert seed_reports == {
            "pmid:971183",
            "pmid:3790029",
            "pmid:1755801",
            "pmid:12546299",
            "pmid:30352646",
            "pmid:32574436",
        }
        observations = {
            observation_id: (cases, denominator, rate)
            for observation_id, cases, denominator, rate in db.execute(
                "SELECT observation_id,cases,denominator,reported_rate_percent "
                "FROM review_search_observation JOIN review_retrieval USING(run_id) "
                "WHERE snapshot LIKE '%/retrievals-2026-11-20.json' "
                "OR snapshot LIKE '%/retrievals-2026-11-20-supplementary.json'"
            )
        }
        assert observations == {
            "iaf-api": (4, None, None),
            "iaf-non-api": (7, None, None),
            "itaf-dcs-rounded": (None, 1777, 0.1),
            "morgagni10-evaluable-trainees": (1, 1241, 0.08),
            "morgagni10-observer-report": (0, None, None),
            "nakdimon22-staff-rate": (None, 364, 0.55),
            "nakdimon22-trainee-rate": (None, 1263, 0.55),
            "polaris-ground-dcs": (0, 8, None),
            "polaris-ground-vge": (4, 8, None),
            "sweden-simulated-eva-vge": (2, 20, None),
            "uk-research-dcs-episodes": (10, None, None),
            "uk-research-dcs-person": (5, 20, None),
        }
        assert db.execute(
            "SELECT count(*) FROM review_study_report WHERE role='primary'"
        ).fetchone() == (9,)
        groups = db.execute(
            "SELECT report_id, chamber_role, sum(cases), sum(exposures) FROM review_seed_role_cell "
            "GROUP BY report_id, chamber_role"
        ).fetchall()
        assert len(groups) == 12
        assert ("pmid:971183", "staff", 57, 14959) in groups
        assert ("pmid:3790029", "trainee", 8, 12596) in groups
        assert db.execute("SELECT count(*) FROM review_supplementary_role_cell").fetchone() == (10,)
        assert db.execute(
            "SELECT stratum, cases, exposures, report_id FROM review_supplementary_role_cell "
            "WHERE study_id='usaf-howard-1979-1981' ORDER BY stratum"
        ).fetchall() == [
            ("inside-observers", 67, 47921, "abstract:howard-sheffield-matos-1982"),
            ("trainees", 139, 203315, "abstract:howard-sheffield-matos-1982"),
        ]
        assert db.execute(
            "SELECT s.period, json_extract(r.metadata_json, '$.period_for_extracted_counts.end'), "
            "json_extract(r.metadata_json, '$.surveillance_period_described.end') "
            "FROM review_study s JOIN review_study_report l USING(study_id) "
            "JOIN review_record r USING(report_id) WHERE s.study_id='usaf-howard-1979-1981' "
            "AND r.source_key='howard-1982-original'"
        ).fetchone() == ("1979-01-01 to 1981-08-31", "1981-08-31", "1981-12-31")
        assert db.execute(
            "SELECT source_key, report_id, json_extract(metadata_json, '$.source_counts.dcs_episodes'), "
            "json_extract(metadata_json, '$.source_counts.investigator_flights_above_15000_ft_body'), "
            "json_extract(metadata_json, '$.source_counts.investigator_flights_above_15000_ft_abstract_and_table') "
            "FROM review_record WHERE source_key='ada168595-original'"
        ).fetchone() == ("ada168595-original", "report:ada168595", 28, 275, 274)
        assert db.execute(
            "SELECT cases,exposures,denominator_basis FROM review_supplementary_role_cell "
            "WHERE study_id='usaf-bassett-1973-1977' ORDER BY stratum"
        ).fetchall() == [(60, 222425, "student_exposure"), (61, 59925, "observer_exposure")]
        assert db.execute(
            "SELECT study_id,chamber_role,cases,exposures,report_id "
            "FROM review_secondary_role_cell ORDER BY study_id,chamber_role"
        ).fetchall() == [
            ("usn-1976-1977", "staff", 20, 6470, "pmid:1755801"),
            ("usn-1976-1977", "trainee", 10, 31645, "pmid:1755801"),
            ("usn-1978-1981", "staff", 48, 10020, "pmid:1755801"),
            ("usn-1978-1981", "trainee", 39, 47380, "pmid:1755801"),
        ]
        assert db.execute(
            "SELECT chamber_role,count(*),sum(cases),sum(denominator) "
            "FROM review_search_observation "
            "WHERE study_id='usaf-1973-1976-treated' AND endpoint='hyperbaric_treated_altitude_dcs' "
            "GROUP BY chamber_role ORDER BY chamber_role"
        ).fetchall() == [("staff", 8, 31, 48148), ("trainee", 8, 39, 194204)]
        assert db.execute(
            "SELECT cases,denominator FROM review_search_observation "
            "WHERE study_id='usaf-1973-1976-treated' AND exposure_year=1974 "
            "AND altitude_band='above_25000_ft' AND chamber_role='trainee'"
        ).fetchone() == (10, 51441)
        berry = db.execute(
            "SELECT cases,denominator,reported_rate,reported_rate_unit "
            "FROM review_search_observation WHERE observation_id IN "
            "('berry57-grade-iv-1950-1955','berry57-grade-iv-rate-1955') ORDER BY observation_id"
        ).fetchall()
        assert berry == [(125, None, None, None), (None, 51580, 85, "per_100000_trainees")]
        assert db.execute(
            "SELECT cases,denominator,denominator_unit,report_id FROM review_search_observation "
            "WHERE study_id='usaf-watson-1965-1967' ORDER BY observation_id"
        ).fetchall() == [
            (31, 37219, "students_as_reported", "pmid:30352646"),
            (103, 162285, "students_as_reported", "pmid:30352646"),
        ]
        assert db.execute(
            "SELECT 1 FROM review_report_relation WHERE left_report='report:faa-am-77-4' "
            "AND right_report='utmb:2152.3/7868' AND relationship='historical_reprint'"
        ).fetchone() == (1,)
        assert db.execute(
            "SELECT chamber_role,cases,denominator,denominator_unit,reported_rate "
            "FROM review_search_observation WHERE study_id='usaf-weien-1979-1986-treated' "
            "AND endpoint='hyperbaric_treated_altitude_dcs' ORDER BY chamber_role"
        ).fetchall() == [
            ("staff", 81, 139584, "printed_exposed_non_cases", 58.03),
            ("trainee", 348, 601126, "printed_exposed_non_cases", 57.89),
        ]
        assert db.execute(
            "SELECT chamber_role,cases,denominator,reported_rate_percent "
            "FROM review_search_observation WHERE study_id='usaf-brooks-1996-1997' ORDER BY chamber_role"
        ).fetchall() == [("staff", None, None, 0.097), ("trainee", None, None, 0.422)]
        assert db.execute(
            "SELECT relationship FROM review_report_relation "
            "WHERE left_report='pmid:30352646' AND right_report='abstract:bassett-1973-asma'"
        ).fetchone() == ("secondary_counts_scope_discrepancy",)
        assert db.execute(
            "SELECT chamber_role,cases,denominator FROM review_search_observation "
            "WHERE study_id='usafsam-bassett-1968-1972' ORDER BY cases"
        ).fetchall() == [("trainee", 2, 9056), ("trainee", 7, 3190)]
        assert db.execute(
            "SELECT display_title FROM review_report WHERE report_id='report:adp011059'"
        ).fetchone() == (
            "USAF Experience with Hyperbaric Therapy of Altitude Decompression Sickness (1941–1999)",
        )
        assert db.execute(
            "SELECT endpoint,chamber_role,cases,denominator,denominator_unit "
            "FROM review_search_observation WHERE study_id IN ('jasdf-1960-1998','jordan-1986-1994') "
            "ORDER BY observation_id"
        ).fetchall() == [
            ("hyperbaric_treated_altitude_dcs", "trainee", 0, 58454, "trainee_exposures"),
            ("at_least_one_recorded_physiological_reaction", "trainee", 39, 705, "trainees"),
            ("recorded_symptomatic_dcs", "trainee", 0, 705, "trainees"),
        ]
        assert db.execute(
            "SELECT report_id,count(*) FROM review_record "
            "WHERE run_id LIKE '2026-11-20-regional-%' "
            "AND title LIKE 'Physiological incidents of hypobaric chamber training for aircrew%' "
            "GROUP BY report_id"
        ).fetchall() == [("openalex:W2286393360", 3)]
        assert db.execute(
            "SELECT provider,sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-regional.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0 "
            "GROUP BY provider ORDER BY provider"
        ).fetchall() == [
            ("Firecrawl", 11), ("OpenAlex", 50), ("Publisher full text", 2),
            ("Tavily", 39), ("Undermind", 0),
        ]
        assert db.execute(
            "SELECT observation_id,chamber_role,cases,denominator FROM review_search_observation "
            "WHERE study_id='itaf-pratica-di-mare-2003-2009' ORDER BY observation_id"
        ).fetchall() == [
            ("itaf-icmm-instructor-exposures", "staff", None, 344),
            ("itaf-icmm-trainee-dcs", "trainee", 1, 1254),
            ("morgagni10-evaluable-trainees", "trainee", 1, 1241),
            ("morgagni10-observer-report", "staff", 0, None),
        ]
        assert db.execute(
            "SELECT count(*),sum(json_extract(y.value,'$.sessions')),"
            "sum(json_extract(y.value,'$.trainees')),"
            "sum(json_extract(y.value,'$.instructor_exposures')) "
            "FROM review_record r JOIN json_each(r.metadata_json,'$.exposure_tables.by_year') y "
            "WHERE r.run_id='2026-11-20-italian-icmm-original' "
            "AND json_extract(r.metadata_json,'$.exposure_tables.instructor_count')=10"
        ).fetchone() == (7, 171, 1254, 344)
        assert db.execute(
            "SELECT relationship FROM review_report_relation "
            "WHERE left_report='undermind:mor10b-italian-chamber-safety' "
            "AND right_report='pmid:20824995'"
        ).fetchone() == ("same_underlying_cohort",)
        assert db.execute(
            "SELECT count(*),sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-italian.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0"
        ).fetchone() == (18, 77)
        assert db.execute(
            "SELECT observation_id,cases,denominator FROM review_search_observation "
            "WHERE run_id LIKE '2026-11-20-citation-audit-%' ORDER BY observation_id"
        ).fetchall() == [
            ("davenport-staff-unspecified-events", 9, None),
            ("davenport-suspected-trainee-dcs", 12, 5851),
            ("degroot-everest-ii-dcs-overlap", 28, None),
            ("rice-table-iv-furr-printed-student-count", 22, 31645),
            ("wirjosemito-treated-chamber-type-ii", 126, None),
        ]
        assert db.execute(
            "SELECT count(*),count(DISTINCT report_id),min(report_id) FROM review_record "
            "WHERE pmid='3619843' OR record_key='2026-11-20-undermind-references#Mal87'"
        ).fetchone() == (10, 1, "pmid:3619843")
        assert db.execute(
            "SELECT relationship FROM review_report_relation "
            "WHERE left_report='pmid:14503681' AND right_report='pmid:3619843'"
        ).fetchone() == ("same_events_excluded",)
        assert db.execute(
            "SELECT count(*),sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-iaf.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0"
        ).fetchone() == (17, 94)
        assert db.execute(
            "SELECT chamber_role,cases,denominator,denominator_unit,reported_rate_percent "
            "FROM review_search_observation WHERE study_id='iaf-ramat-gan-2015-2019' "
            "AND role_review='rounded_count_reconstructed_exposure_unit_unverified' "
            "ORDER BY chamber_role"
        ).fetchall() == [
            ("staff", 2, 364, "individuals_as_reported", 0.55),
            ("trainee", 7, 1263, "individuals_as_reported", 0.55),
        ]
        assert db.execute(
            "SELECT report_id,endpoint,cases,denominator FROM review_search_observation "
            "WHERE study_id='iaf-ramat-gan-2015-2022' AND denominator IS NOT NULL "
            "ORDER BY observation_id"
        ).fetchall() == [
            ("pmid:42345225", "symptomatic_altitude_dcs", 11, 2279),
            ("pmid:42345225", "hyperbaric_treated_altitude_dcs", 10, 2279),
        ]
        assert db.execute(
            "SELECT relationship FROM review_report_relation "
            "WHERE left_report='pmid:42345225' AND right_report='pmid:36309795'"
        ).fetchone() == ("likely_overlap",)
        assert db.execute(
            "SELECT count(*),sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-turkey.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0"
        ).fetchone() == (18, 86)
        assert db.execute(
            "SELECT study_id,chamber_role,cases,denominator FROM review_search_observation "
            "WHERE run_id LIKE '2026-11-20-turkey-%' "
            "AND role_review='outcome_selected_cluster_no_incidence_risk_set' "
            "AND chamber_role IS NOT NULL ORDER BY study_id,chamber_role"
        ).fetchall() == [
            ("eskisehir-ata-single-session", "staff", 1, 1),
            ("eskisehir-ata-single-session", "trainee", 2, 10),
            ("eskisehir-demir-two-sessions", "staff", 0, 2),
            ("eskisehir-demir-two-sessions", "trainee", 5, 16),
        ]
        assert db.execute(
            "SELECT reported_rate,reported_rate_unit,cases,denominator "
            "FROM review_search_observation WHERE observation_id='ercan20-published-staff-trainee-odds-ratio'"
        ).fetchone() == (3.574, "odds_ratio", None, None)
        assert db.execute(
            "SELECT relationship FROM review_report_relation "
            "WHERE left_report='pmid:36243908' AND right_report='doi:10.28920/dhm51.1.82-85'"
        ).fetchone() == ("distinct_reported_events",)
        assert db.execute(
            "SELECT report_id,json_extract(metadata_json,'$.sample_count'), "
            "json_extract(metadata_json,'$.role_review') FROM review_record "
            "WHERE run_id='2026-11-20-latin-firecrawl-236'"
        ).fetchone() == ("lilacs:biblio-910830", 236, "sample_selected_by_hypoxia_symptoms_no_dcs_incidence")
        assert db.execute(
            "SELECT report_id FROM review_record "
            "WHERE record_key='legacy:data/chamber/v1.7/sources.csv#lapostol24'"
        ).fetchone() == ("hdl:11447/9961",)
        assert db.execute(
            "SELECT count(*),sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-latin.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0"
        ).fetchone() == (21, 114)
        assert db.execute(
            "SELECT report_id,chamber_role,cases,denominator,denominator_unit "
            "FROM review_search_observation WHERE run_id LIKE '2026-11-20-latin-%'"
        ).fetchall() == [("pmid:3718386", "trainee", 4, 9, "attendees_in_selected_sessions")]
        assert db.execute(
            "SELECT relationship FROM review_report_relation "
            "WHERE left_report='pmid:3718386' AND right_report='pmid:3790029'"
        ).fetchone() == ("explicitly_excluded_profile",)
        assert db.execute(
            "SELECT count(*),sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-russian.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0"
        ).fetchone() == (18, 92)
        assert db.execute(
            "SELECT report_id, cases, denominator, chamber_role, role_review "
            "FROM review_search_observation WHERE run_id LIKE '2026-11-20-russian-%' ORDER BY report_id"
        ).fetchall() == [
            ("ntrs:n88-26074", 250, 2444, None, "experimental_volunteers_no_operational_role_comparison"),
            ("pmid:11385985", 0, 24, None, "experimental_eva_abstract_only"),
        ]
        assert db.execute(
            "SELECT relationship FROM review_report_relation "
            "WHERE left_report='ntrs:n88-26074' AND right_report='pmid:3361829'"
        ).fetchone() == ("translation_of",)
        assert db.execute(
            "SELECT report_id,count(*) FROM review_record "
            "WHERE run_id='2026-11-20-russian-und-search' GROUP BY report_id ORDER BY report_id"
        ).fetchall() == [("pmid:11385985", 2), ("pmid:3361829", 2)]
        assert db.execute(
            "SELECT report_id FROM review_record "
            "WHERE record_key='legacy:data/chamber/v1.6/sources.csv#chadov01'"
        ).fetchone() == ("pmid:11496423",)
        assert db.execute(
            "SELECT count(*),sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-fort-rucker.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0"
        ).fetchone() == (23, 83)
        assert db.execute(
            "SELECT cases,denominator,reported_rate,reported_rate_unit FROM review_search_observation "
            "WHERE study_id='fort-rucker-1984-1989' ORDER BY observation_id"
        ).fetchall() == [(42, 21498, 195.37, "cases_per_100000_person_exposures"), (None, None, 3.17, "rate_ratio")]
        assert db.execute(
            "SELECT chamber_role,cases,denominator FROM review_search_observation "
            "WHERE study_id='fort-rucker-1990-post-overhaul' ORDER BY observation_id"
        ).fetchall() == [(None, 7, 518), ("staff", 2, None), ("trainee", 5, None), (None, 3, 518)]
        assert db.execute(
            "SELECT relationship FROM review_report_relation "
            "WHERE left_report='workshop:ada257612-weien-army' AND right_report='pmid:3790029'"
        ).fetchone() == ("possible_overlap",)
        assert db.execute(
            "SELECT count(*),sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-navy-outbreaks.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0"
        ).fetchone() == (16, 80)
        assert db.execute(
            "SELECT study_id,endpoint,chamber_role,cases,denominator FROM review_search_observation "
            "WHERE run_id LIKE '2026-11-20-navy-outbreaks-%' ORDER BY observation_id"
        ).fetchall() == [
            ("usn-1981-1988", "symptomatic_type_ii_altitude_dcs", "staff", 30, 25022),
            ("usn-1981-1988", "symptomatic_type_ii_altitude_dcs", "trainee", 38, 111674),
            ("usn-1988-reported-cluster", "reported_chamber_dcs_cluster_cases", None, 6, None),
            ("usn-1990-reported-cluster", "reported_chamber_dcs_cluster_cases", None, 5, None),
            ("adf-1995-reported-cluster", "definite_or_probable_decompression_illness", None, 13, None),
        ]
        assert db.execute(
            "SELECT left_report,right_report,relationship FROM review_report_relation "
            "WHERE left_report IN ('workshop:ada257612-bason-navy-chamber','abstract:asma-1991-weien-krieger') "
            "ORDER BY left_report"
        ).fetchall() == [
            ("abstract:asma-1991-weien-krieger", "workshop:ada257612-weien-army", "same_underlying_outbreak"),
            ("workshop:ada257612-bason-navy-chamber", "pmid:1755801", "same_underlying_cohort"),
        ]
        assert db.execute(
            "SELECT count(*),sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-raf.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0"
        ).fetchone() == (20, 84)
        assert db.execute(
            "SELECT chamber_role,cases,denominator,reported_rate FROM review_search_observation "
            "WHERE study_id IN ('raf-amtc-1983-1987','raf-henlow-year-before-oct-2000') "
            "ORDER BY study_id"
        ).fetchall() == [("trainee", 5, None, 0.41), (None, 1, None, 1.0)]
        assert db.execute(
            "SELECT endpoint,chamber_role,cases,denominator FROM review_search_observation "
            "WHERE study_id='raf-cam-manton-case-series' ORDER BY observation_id"
        ).fetchall() == [
            ("symptomatic_altitude_dcs", None, 1, None),
            ("reported_decompression_illness", "trainee", 1, None),
            ("suspected_arterial_gas_embolism", "trainee", 1, None),
        ]
        assert db.execute(
            "SELECT left_report FROM review_report_relation "
            "WHERE right_report='dissertation:thornton-1988-fom' ORDER BY left_report"
        ).fetchall() == [
            ("chapter:rto-mp-21-morris",),
            ("report:adp011069",),
            ("workshop:ada257612-harding",),
        ]
        assert db.execute(
            "SELECT DISTINCT report_id FROM review_record "
            "WHERE record_key IN ('2026-11-20-openalex-training#W2435088829', "
            "'2026-11-20-raf-oa-uk-new#W2435088829', '2026-11-20-raf-wrigley#26867422')"
        ).fetchall() == [("pmid:26867422",)]
        assert db.execute(
            "SELECT count(*),sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-canada.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0"
        ).fetchone() == (19, 100)
        assert db.execute(
            "SELECT reported_group,altitude_band,cases,denominator,reported_rate "
            "FROM review_search_observation WHERE report_id='abstract:asma-1994-glass-brooks-93' "
            "ORDER BY reported_group,altitude_band"
        ).fetchall() == [
            ("Edmonton staff", "25,000 ft", None, None, 7.9),
            ("Edmonton staff", "43,000 ft", None, None, 10.3),
            ("Edmonton trainee", "25,000 ft", None, None, 7),
            ("Edmonton trainee", "43,000 ft", None, None, 11.3),
            ("Greenwood, chamber program overall", None, 0, None, None),
            ("Trenton staff", "25,000 ft", None, None, 0),
            ("Trenton staff", "43,000 ft", None, None, 0),
            ("Trenton trainee", "25,000 ft", None, None, 3.2),
            ("Trenton trainee", "43,000 ft", None, None, 0),
        ]
        assert db.execute(
            "SELECT cases,denominator,chamber_role,altitude_band FROM review_search_observation "
            "WHERE study_id='cf-winnipeg-chamber-and-flight-case-series'"
        ).fetchall() == [(3, None, "trainee", "18,000–26,000 ft in chamber")]
        assert db.execute(
            "SELECT json_extract(metadata_json,'$.source_counts.table_ii_exposures'), "
            "json_extract(metadata_json,'$.source_counts.results_exposures') "
            "FROM review_record WHERE run_id='2026-11-20-canada-crowell-primary'"
        ).fetchall() == [(19573, 21423)]
        assert db.execute(
            "SELECT count(*),sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-case-verification.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0"
        ).fetchone() == (26, 77)
        assert db.execute(
            "SELECT cases,denominator,chamber_role FROM review_search_observation "
            "WHERE observation_id IN ('skinner89-point-cook-all-six','skinner89-point-cook-case-5', "
            "'whitfield95-alfred-treated-altitude-dcs','gentry17-delayed-trainee-dcs', "
            "'studer15-trainee-dcs-late-presentation') ORDER BY observation_id"
        ).fetchall() == [
            (1, None, "trainee"),
            (6, None, None),
            (1, None, "staff"),
            (1, None, "trainee"),
            (11, None, None),
        ]
        assert db.execute(
            "SELECT count(*) FROM review_record r, json_each(r.metadata_json,'$.observations') o "
            "WHERE r.run_id='2026-11-20-case-verification-skinner-primary' "
            "AND json_extract(o.value,'$.parent_observation_id')='skinner89-point-cook-all-six'"
        ).fetchone() == (6,)
        assert db.execute(
            "SELECT left_report,right_report FROM review_report_relation "
            "WHERE relationship='secondary_denominator_scope_discrepancy' AND left_report='pmid:28518008'"
        ).fetchall() == [("pmid:28518008", "pmid:14557320")]
        assert db.execute(
            "SELECT DISTINCT report_id FROM review_record "
            "WHERE pmid='28518008' OR doi='10.3357/amhp.4691.2017'"
        ).fetchall() == [("pmid:28518008",)]
        assert db.execute(
            "SELECT count(*),sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-french-german.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0"
        ).fetchone() == (27, 160)
        assert db.execute(
            "SELECT endpoint,chamber_role,cases,denominator FROM review_search_observation "
            "WHERE study_id='france-dmao-hypobaric-program-reported-2014' "
            "ORDER BY chamber_role"
        ).fetchall() == [
            ("reported_bends", "staff", None, None),
            ("reported_aeroembolic_incidents", "trainee", 0, None),
        ]
        assert db.execute(
            "SELECT count(*) FROM review_search_observation WHERE study_id IN "
            "('france-dmao-normobaric-2018-2019','ledderhos-four-country-chamber-instructors-mri')"
        ).fetchone() == (0,)
        assert db.execute(
            "SELECT right_report,relationship FROM review_report_relation "
            "WHERE left_report='journal:coulange-2014-bmsh-24-89' "
            "AND relationship LIKE 'secondary_%_discrepancy' ORDER BY right_report"
        ).fetchall() == [
            ("pmid:16173680", "secondary_case_count_discrepancy"),
            ("pmid:6651730", "secondary_denominator_unit_discrepancy"),
        ]
        assert db.execute(
            "SELECT count(*),sum(retrieved) FROM review_retrieval "
            "WHERE snapshot LIKE '%/retrievals-2026-11-20-japan-followup.json' "
            "AND json_extract(parameters_json,'$.counts_toward_formal_identification')=0"
        ).fetchone() == (18, 71)
        assert db.execute(
            "SELECT report_id,endpoint,chamber_role,cases,denominator,denominator_unit "
            "FROM review_search_observation WHERE run_id LIKE '2026-11-20-japan-followup-%' "
            "ORDER BY observation_id"
        ).fetchall() == [
            ("pmid:11952064", "reported_joint_pain_type_i_dcs", "trainee", 0, 257, "trainees_by_profile"),
            ("pmid:11952064", "reported_joint_pain_type_i_dcs", "trainee", 0, 8230, "trainees_by_profile"),
            ("doi:10.1097/mao.0b013e31816c7c59", "reported_ear_pain", "trainee", 740, 17935, "exposures"),
            ("doi:10.1097/mao.0b013e31816c7c59", "reported_ear_pain", "trainee", 429, 7047, "trainees"),
            ("journal:watanabe-yamazaki-1964-amlr-5-4", "reported_any_symptoms", "trainee", 872, 4645, "trainees"),
            ("pmid:9681378", "probable_cutaneous_altitude_dcs", "trainee", 1, None, None),
        ]
        assert db.execute(
            "SELECT evidence_url FROM review_search_observation "
            "WHERE observation_id='jasdf-watanabe-1964-any-symptoms'"
        ).fetchone() == (
            "https://www.jstage.jst.go.jp/article/jasdfaml/58/4/58_41/_supplement/_download/58_41_1.pdf#page=73",
        )
        assert db.execute(
            "SELECT left_report,relationship FROM review_report_relation WHERE right_report='pmid:11952064' "
            "AND (relationship LIKE 'possible_%' OR relationship='same_program_denominator_discrepancy') "
            "ORDER BY left_report"
        ).fetchall() == [
            ("abstract:ogata-jasdf-altitude-dcs-2000", "possible_overlap_with_historical_chamber_surveillance"),
            ("doi:10.1097/mao.0b013e31816c7c59", "same_program_denominator_discrepancy"),
            ("journal:watanabe-yamazaki-1964-amlr-5-4", "possible_overlapping_training_periods"),
            ("openalex:W2286393360", "possible_overlap"),
            ("pmid:9681378", "possible_overlap_case_membership_unverified"),
        ]
        assert db.execute(
            "SELECT endpoint,cases,denominator,denominator_unit,reported_rate_percent "
            "FROM review_search_observation WHERE study_id LIKE 'jasdf-ogata-%' "
            "ORDER BY observation_id"
        ).fetchall() == [
            ("bends_as_reported", 236, 30763, "trainee_count_as_reported", None),
            ("neurologic_dcs_as_reported", 6, 30763, "trainee_count_as_reported", None),
            ("skin_bends_as_reported", 1, 30763, "trainee_count_as_reported", None),
            ("suspected_altitude_dcs", 243, 30763, "trainee_count_as_reported", 0.93),
            ("reported_altitude_dcs", 12, 9668, "trainee_count_as_reported", 0.12),
        ]
        assert db.execute(
            "SELECT relationship FROM review_report_relation "
            "WHERE left_report='report:ogata-ide-kusano-jasdf-altitude-dcs-2001' "
            "AND right_report='pmid:11952064'"
        ).fetchone() == ("substantial_calendar_and_program_overlap_unresolved_case_linkage",)
        assert db.execute(
            "SELECT observation_id,endpoint,chamber_role,cases,denominator,denominator_unit "
            "FROM review_search_observation WHERE run_id LIKE '2026-11-20-rapid-decompression-%' "
            "ORDER BY observation_id"
        ).fetchall() == [
            ("cable-2000-aircrew-cage", "reported_cerebral_arterial_gas_embolism", "unreported", 1, None, None),
            ("prague-sazel-2008-dcs-symptoms", "reported_dcs_symptoms", "trainee", 0, None, None),
            ("prague-tlapak-2020-lung-barotrauma", "reported_pulmonary_barotrauma", "trainee", 1, 566,
             "single_occupant_chamber_runs"),
            ("rios-1997-controller-age", "presumptive_arterial_gas_embolism", "unreported", 1, None, None),
            ("rudge-1992-inside-observer-age", "presumptive_arterial_gas_embolism", "staff", 1, None, None),
        ]
        assert db.execute(
            "SELECT right_report,relationship FROM review_report_relation "
            "WHERE left_report='doi:10.3357/asem.3254.2012' ORDER BY right_report"
        ).fetchall() == [
            ("pmid:10685592", "secondary_assessment_same_case"),
            ("pmid:1567322", "secondary_exclusion_by_diagnostic_criteria"),
            ("pmid:9383503", "secondary_assessment_same_case"),
        ]
        assert db.execute(
            "SELECT cases, denominator, denominator_unit FROM review_search_observation "
            "WHERE observation_id='rudge-shafer-1984-1988-dcs-early-count'"
        ).fetchone() == (128, 233, "treated_dcs_cases")
        assert db.execute(
            "SELECT denominator, chamber_role FROM review_search_observation "
            "WHERE observation_id='rush-wirjosemito-1982-1987-treated-trainees'"
        ).fetchone() == (None, "trainee")
        assert db.execute(
            "SELECT cases, denominator, denominator_unit FROM review_search_observation "
            "WHERE observation_id='rush-wirjosemito-1989-local-after-passenger-flight'"
        ).fetchone() == (4, 26, "treated_dcs_cases")
        assert db.execute(
            "SELECT study_id FROM review_study_report WHERE report_id='abstract:asma-1989-baumgartner-178'"
        ).fetchone() == ("usaf-1985-1987",)
        assert db.execute(
            "SELECT DISTINCT report_id, doi, json_extract(metadata_json, '$.reported_doi') "
            "FROM review_record WHERE openalex_id='W1898307' AND run_id LIKE '2026-11-20-usaf-treatment-o-%'"
        ).fetchall() == [("pmid:1898307", None, "10.24471/shigaku.115.9_1617")]
        assert db.execute(
            "SELECT reported_rate, json_extract(metadata_json, '$.source_counts.reported_ci95[0]'), "
            "json_extract(metadata_json, '$.derived_effects.comparisons[0].ci95[0]'), "
            "json_extract(metadata_json, '$.derived_effects.printed_interval_reproduction_check.ci95[1]') "
            "FROM review_search_observation JOIN review_record USING(record_key) "
            "WHERE observation_id='weien-baumgartner-1979-1986-reported-role-rr'"
        ).fetchone() == (1.0024, 0.0956, 0.78714824, 10.50214196)
        assert db.execute(
            "SELECT report_id, endpoint, cases, denominator FROM review_search_observation "
            "WHERE observation_id IN ('los-1998-soesterberg-hypobaric-dcs', "
            "'morris-1997-am-raf-trainee-dcs', 'valentiner-since-1995-rule-out-dcs', "
            "'taubman-24h-reported-post-training-symptoms') ORDER BY observation_id"
        ).fetchall() == [
            ("chapter:rto-mp-21-los", "reported_known_dcs_after_operational_chamber_training", 0, 699),
            ("chapter:rto-mp-21-morris", "reported_dcs_after_operational_chamber_training", 0, 1559),
            ("journal:taubman-unifa-2006-18-21", "self_reported_post_training_symptoms_through_24_hours", 0, None),
            ("chapter:rto-mp-21-valentiner", "rule_out_dcs_diagnoses", 3, 5300),
        ]
        assert db.execute(
            "SELECT observation_id, chamber_role, cases, denominator "
            "FROM review_search_observation WHERE run_id LIKE '2026-11-20-europe-staff-%' "
            "ORDER BY observation_id"
        ).fetchall() == [
            ("kopka-wiml-20-year-reported-dcs", "unreported", 0, None),
            ("szabo-hungary-repeated-staff-cutaneous-dcs", "staff", None, None),
        ]
        assert db.execute(
            "SELECT right_report, relationship FROM review_report_relation "
            "WHERE left_report='poster:rojas-dohn-voss-wright-mph-170'"
        ).fetchone() == ("openalex:W2344433097", "companion_poster_same_case_control_sample")
        assert db.execute(
            "SELECT left_report, right_report FROM review_report_relation "
            "WHERE relationship IN ('cites_corresponding_chamber_pulmonary_overexpansion_event', "
            "'same_experimental_crossover_as_full_article') ORDER BY left_report"
        ).fetchall() == [
            ("abstract:asma-2023-anell-228", "doi:10.1007/s00421-023-05173-9"),
            ("doi:10.4321/s1887-85712018000300008", "pmid:9383503"),
        ]
        assert db.execute(
            "SELECT report_id, chamber_role, cases, denominator FROM review_search_observation "
            "WHERE study_id='rsaf-chamber-2011-2017-prebreathing-policy' ORDER BY denominator"
        ).fetchall() == [
            ("pmid:33875060", "unreported", 2, 1530),
            ("pmid:33875060", "unreported", 2, 1729),
        ]
        assert db.execute(
            "SELECT right_report, relationship FROM review_report_relation "
            "WHERE left_report='abstract:asma-2018-cheok-koh-038'"
        ).fetchone() == ("pmid:33875060", "same_policy_cohort_as_full_article")
        assert db.execute(
            "SELECT chamber_role, cases, denominator, reported_rate_percent "
            "FROM review_search_observation WHERE study_id='rmaf-iam-2024-hypoxia-indoctrination' "
            "ORDER BY observation_id"
        ).fetchall() == [
            ("multiple_unseparated", 4, 395, 1.01),
            ("staff", None, 46, None),
            ("multiple_unseparated", 4, None, 0.04),
            ("trainee", None, 349, None),
        ]
        assert db.execute(
            "SELECT endpoint, chamber_role, cases, denominator FROM review_search_observation "
            "WHERE study_id IN ('saryanto-2021-irani-barotrauma', 'saryanto-2007-sastranegara-barotitis') "
            "ORDER BY observation_id"
        ).fetchall() == [
            ("clinically_diagnosed_otic_barotrauma", "trainee", 3, 97),
            ("suspected_otic_barotrauma", "trainee", 1, 97),
            ("clinically_diagnosed_barotitis_media", "participant", 100, 177),
            ("clinically_diagnosed_barotitis_media", "participant", 22, 52),
            ("clinically_diagnosed_barotitis_media", "trainee", 78, 125),
        ]
        assert db.execute(
            "SELECT DISTINCT report_id FROM review_record "
            "WHERE run_id LIKE '2026-11-20-trainee-cohorts-%' "
            "AND (doi='10.33657/jurkessia.v16i1.1129' OR source_key='w:3f55e3b6-ef26-4f69-ac5f-3e14729e48c8')"
        ).fetchall() == [("doi:10.33657/jurkessia.v16i1.1129",)]
        assert db.execute("SELECT count(*) FROM review_historical_search_record").fetchone() == (
            3603,
        )
        assert db.execute("SELECT count(*) FROM publication_search_run").fetchone() == (779,)
        comments = db.execute(
            "SELECT left_report FROM review_report_relation "
            "WHERE right_report='pmid:33875060' AND relationship='comment_on'"
        ).fetchall()
        assert set(comments) == {("pmid:34642007",), ("pmid:34642008",)}
        assert db.execute("SELECT count(*) FROM review_current_screening").fetchone() == (0,)
        key = db.execute(
            "SELECT record_key FROM review_record ORDER BY record_key LIMIT 1"
        ).fetchone()[0]
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO review_screening VALUES (?,'reviewer','full_text',1,'2026-11-19',"
                "'exclude','','')",
                (key,),
            )
        db.executemany(
            "INSERT INTO review_screening VALUES (?,'reviewer','title_abstract',"
            "?,'2026-11-19',?,NULL,NULL)",
            [(key, 1, "uncertain"), (key, 2, "include")],
        )
        assert db.execute("SELECT revision, decision FROM review_current_screening").fetchall() == [
            (2, "include")
        ]
