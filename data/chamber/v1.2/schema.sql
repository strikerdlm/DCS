CREATE TABLE web_source (
    source_id TEXT PRIMARY KEY,
    citation TEXT NOT NULL,
    url TEXT NOT NULL,
    access TEXT NOT NULL CHECK(access IN ('full_text','abstract','registry')),
    disposition TEXT NOT NULL CHECK(disposition IN ('extracted','lead_only')),
    extraction TEXT NOT NULL,
    source_sha256 TEXT CHECK(length(source_sha256)=64),
    note TEXT NOT NULL
) STRICT;

CREATE TABLE web_observation (
    source_id TEXT NOT NULL REFERENCES web_source,
    stratum TEXT NOT NULL,
    period TEXT,
    endpoint TEXT NOT NULL CHECK(endpoint IN (
        'dcs','dcs_type_i','dcs_type_ii_neurologic','dcs_type_ii_psi_1',
        'dcs_type_ii_psi_3','dcs_serious_respiratory_or_neurologic',
        'suspected_dcs','suspected_dcs_type_i','suspected_dcs_type_ii',
        'any_vge','spencer_grade_iii_or_iv_vge'
    )),
    analysis_role TEXT NOT NULL CHECK(analysis_role IN (
        'descriptive_stratum','descriptive_total','overlapping_margin','overlap_hold'
    )),
    cases INTEGER NOT NULL CHECK(cases>=0),
    denominator INTEGER NOT NULL CHECK(denominator>0 AND cases<=denominator),
    denominator_unit TEXT NOT NULL CHECK(denominator_unit IN (
        'person_exposure','person_protocol_session','trainee_record',
        'chamber_decompression','investigator_flight','investigator'
    )),
    altitude_low_ft INTEGER CHECK(altitude_low_ft>0),
    altitude_high_ft INTEGER CHECK(altitude_high_ft>=altitude_low_ft),
    planned_target_min INTEGER CHECK(planned_target_min>0),
    prebreathe_min INTEGER CHECK(prebreathe_min>=0),
    protocol TEXT NOT NULL,
    outcome_window TEXT NOT NULL,
    event_time_summary TEXT,
    locator TEXT NOT NULL,
    note TEXT,
    CHECK((altitude_low_ft IS NULL)=(altitude_high_ft IS NULL)),
    PRIMARY KEY(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE web_overlap (
    source_id TEXT NOT NULL REFERENCES web_source,
    related_source TEXT NOT NULL,
    relationship TEXT NOT NULL CHECK(relationship IN (
        'same_cohort','suspected_overlap','unresolved','distinct_protocol'
    )),
    evidence TEXT NOT NULL,
    PRIMARY KEY(source_id,related_source)
) STRICT;
