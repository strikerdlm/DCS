CREATE TABLE web_chamber_case_measurement (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    participant_ordinal INTEGER NOT NULL CHECK(participant_ordinal > 0),
    experiment_order INTEGER NOT NULL CHECK(experiment_order > 0),
    pain_at_altitude INTEGER NOT NULL CHECK(pain_at_altitude BETWEEN 0 AND 10),
    pain_at_ground INTEGER NOT NULL CHECK(pain_at_ground BETWEEN 0 AND 10),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    UNIQUE(source_id,participant_ordinal,experiment_order),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES web_chamber_clinical_case(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE web_chamber_case_onset_claim (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    claim_id TEXT NOT NULL,
    report_id TEXT NOT NULL,
    support_scope TEXT NOT NULL CHECK(support_scope IN ('individual_table_row','same_condition_narrative','companion_condition_narrative')),
    onset_min_lower INTEGER CHECK(onset_min_lower >= 0),
    onset_min_upper INTEGER CHECK(onset_min_upper >= onset_min_lower),
    timing_basis TEXT NOT NULL,
    source_description TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint,claim_id),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES web_chamber_clinical_case(source_id,stratum,endpoint),
    CHECK((onset_min_lower IS NULL) = (onset_min_upper IS NULL))
) STRICT;

CREATE TABLE web_chamber_vge_analysis_scope (
    source_id TEXT NOT NULL REFERENCES web_chamber_source_extract,
    scope_id TEXT NOT NULL,
    participants INTEGER NOT NULL CHECK(participants > 0),
    imputed_grade_after_dcs INTEGER CHECK(imputed_grade_after_dcs BETWEEN 0 AND 5),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,scope_id)
) STRICT;

CREATE TABLE web_chamber_vge_condition_summary (
    source_id TEXT NOT NULL,
    scope_id TEXT NOT NULL,
    condition TEXT NOT NULL,
    minimum_last_30_min_peak_grade INTEGER NOT NULL CHECK(minimum_last_30_min_peak_grade >= 0),
    median_last_30_min_peak_grade REAL NOT NULL CHECK(median_last_30_min_peak_grade BETWEEN minimum_last_30_min_peak_grade AND maximum_last_30_min_peak_grade),
    maximum_last_30_min_peak_grade INTEGER NOT NULL CHECK(maximum_last_30_min_peak_grade <= 5),
    first_positive_mean_min REAL NOT NULL CHECK(first_positive_mean_min >= 0),
    first_positive_spread_min REAL NOT NULL CHECK(first_positive_spread_min >= 0),
    first_positive_after_initial_30_mean_min REAL NOT NULL CHECK(first_positive_after_initial_30_mean_min >= 30),
    first_positive_after_initial_30_spread_min REAL NOT NULL CHECK(first_positive_after_initial_30_spread_min >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,scope_id,condition),
    FOREIGN KEY(source_id,scope_id) REFERENCES web_chamber_vge_analysis_scope(source_id,scope_id)
) STRICT;
