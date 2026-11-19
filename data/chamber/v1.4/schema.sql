CREATE TABLE cohort_source (
    source_id TEXT PRIMARY KEY,
    citation TEXT NOT NULL,
    url TEXT NOT NULL,
    access TEXT NOT NULL CHECK(access IN ('full_text','abstract','catalog')),
    disposition TEXT NOT NULL CHECK(disposition IN ('extracted','lead_only')),
    extraction TEXT NOT NULL,
    source_sha256 TEXT CHECK(length(source_sha256)=64),
    note TEXT NOT NULL
) STRICT;

CREATE TABLE cohort_observation (
    source_id TEXT NOT NULL REFERENCES cohort_source,
    stratum TEXT NOT NULL,
    period TEXT,
    exposure_context TEXT NOT NULL CHECK(exposure_context IN (
        'operational_training','hypobaric_research','post_dive_hypobaric',
        'mixed_flight_only_and_prior_dive','case_series'
    )),
    endpoint TEXT NOT NULL CHECK(endpoint IN (
        'dcs','dcs_symptoms','dcs_pulmonary','dcs_cns','dcs_serious_as_defined',
        'any_vge','spencer_grade_iv_vge','dcs_onset_le_2h_among_treated',
        'dcs_onset_gt_2h_among_treated','dcs_after_air_travel_among_treated'
    )),
    analysis_role TEXT NOT NULL CHECK(analysis_role IN ('descriptive','overlap_hold','overlapping_margin')),
    cases INTEGER CHECK(cases>=0),
    denominator INTEGER NOT NULL CHECK(denominator>0 AND (cases IS NULL OR cases<=denominator)),
    denominator_unit TEXT NOT NULL CHECK(denominator_unit IN (
        'student_exposure','observer_exposure','person_exposure','person_protocol_session','treated_dcs_case'
    )),
    reported_percent REAL CHECK(reported_percent BETWEEN 0 AND 100),
    nominal_altitude_ft INTEGER CHECK(nominal_altitude_ft>0),
    target_pressure_psia REAL CHECK(target_pressure_psia>0),
    planned_at_altitude_min INTEGER CHECK(planned_at_altitude_min>0),
    prebreathe_min INTEGER CHECK(prebreathe_min>=0),
    preflight_surface_interval_min INTEGER CHECK(preflight_surface_interval_min>=0),
    protocol TEXT NOT NULL,
    outcome_window TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((cases IS NULL)<>(reported_percent IS NULL)),
    CHECK((exposure_context='case_series')=(denominator_unit='treated_dcs_case')),
    CHECK((exposure_context='case_series')=(endpoint IN (
        'dcs_onset_le_2h_among_treated','dcs_onset_gt_2h_among_treated',
        'dcs_after_air_travel_among_treated'
    ))),
    CHECK(preflight_surface_interval_min IS NULL OR exposure_context='post_dive_hypobaric'),
    PRIMARY KEY(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE cohort_overlap (
    source_id TEXT NOT NULL REFERENCES cohort_source,
    related_source TEXT NOT NULL,
    relationship TEXT NOT NULL CHECK(relationship IN ('same_cohort','subset','likely_overlap','unresolved','distinct_protocol')),
    evidence TEXT NOT NULL,
    PRIMARY KEY(source_id,related_source)
) STRICT;
