CREATE TABLE literature_source (
    source_id TEXT PRIMARY KEY,
    citation TEXT NOT NULL,
    url TEXT NOT NULL,
    access TEXT NOT NULL CHECK(access IN ('full_text','abstract','catalog')),
    disposition TEXT NOT NULL CHECK(disposition IN ('extracted','lead_only')),
    extraction TEXT NOT NULL,
    source_sha256 TEXT CHECK(length(source_sha256)=64),
    note TEXT NOT NULL
) STRICT;

CREATE TABLE literature_observation (
    source_id TEXT NOT NULL REFERENCES literature_source,
    stratum TEXT NOT NULL,
    period TEXT,
    endpoint TEXT NOT NULL CHECK(endpoint IN (
        'dcs','dcs_symptoms','suspected_dcs','dcs_type_i','dcs_type_ii_historical',
        'any_vge','spencer_grade_iv_vge','dcs_and_any_vge','early_termination_dcs_symptoms_or_high_vge'
    )),
    observation_kind TEXT NOT NULL CHECK(observation_kind IN ('exact_count','case_count_only','reported_percent')),
    analysis_role TEXT NOT NULL CHECK(analysis_role IN ('descriptive','overlap_hold','overlapping_margin')),
    cases INTEGER CHECK(cases>=0),
    denominator INTEGER CHECK(denominator>0 AND (cases IS NULL OR cases<=denominator)),
    denominator_unit TEXT CHECK(denominator_unit IN (
        'trainee_record','person_exposure','person_protocol_session','investigator_flight'
    )),
    reported_percent REAL CHECK(reported_percent BETWEEN 0 AND 100),
    nominal_altitude_ft INTEGER CHECK(nominal_altitude_ft>0),
    target_pressure_psia REAL CHECK(target_pressure_psia>0),
    observed_horizon_min INTEGER CHECK(observed_horizon_min>0),
    prebreathe_min INTEGER CHECK(prebreathe_min>=0),
    protocol TEXT NOT NULL,
    outcome_window TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((denominator IS NULL)=(denominator_unit IS NULL)),
    CHECK((observation_kind='exact_count' AND cases IS NOT NULL AND denominator IS NOT NULL AND reported_percent IS NULL)
       OR (observation_kind='case_count_only' AND cases IS NOT NULL AND denominator IS NULL AND reported_percent IS NULL)
       OR (observation_kind='reported_percent' AND cases IS NULL AND denominator IS NOT NULL AND reported_percent IS NOT NULL)),
    PRIMARY KEY(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE literature_overlap (
    source_id TEXT NOT NULL REFERENCES literature_source,
    related_source TEXT NOT NULL,
    relationship TEXT NOT NULL CHECK(relationship IN ('same_cohort','subset','likely_overlap','unresolved','distinct_protocol')),
    evidence TEXT NOT NULL,
    PRIMARY KEY(source_id,related_source)
) STRICT;

CREATE TABLE literature_case (
    source_id TEXT NOT NULL REFERENCES literature_source,
    published_case_number INTEGER NOT NULL CHECK(published_case_number>0),
    procedure_number INTEGER NOT NULL CHECK(procedure_number>0),
    endpoint TEXT NOT NULL CHECK(endpoint='dcs_type_ii_historical'),
    first_symptom_report_min INTEGER NOT NULL CHECK(first_symptom_report_min>=0),
    vge_detection_status TEXT NOT NULL CHECK(vge_detection_status IN ('detected','not_detected')),
    first_vge_detection_min INTEGER CHECK(first_vge_detection_min>=0),
    max_vge_grade_reported INTEGER CHECK(max_vge_grade_reported BETWEEN 0 AND 4),
    phenotype TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((vge_detection_status='detected' AND first_vge_detection_min IS NOT NULL
        AND max_vge_grade_reported IS NOT NULL AND max_vge_grade_reported>0)
       OR (vge_detection_status='not_detected' AND first_vge_detection_min IS NULL AND coalesce(max_vge_grade_reported,0)=0)),
    PRIMARY KEY(source_id,published_case_number)
) STRICT;
