CREATE TABLE web_chamber_source_extract (
    source_id TEXT PRIMARY KEY REFERENCES web_source,
    full_text_url TEXT NOT NULL,
    full_text_sha256 TEXT NOT NULL CHECK(length(full_text_sha256)=64),
    locator TEXT NOT NULL,
    note TEXT NOT NULL
) STRICT;

CREATE TABLE web_chamber_protocol_plateau (
    source_id TEXT NOT NULL REFERENCES web_chamber_source_extract,
    condition TEXT NOT NULL,
    stage INTEGER NOT NULL CHECK(stage > 0),
    altitude_ft INTEGER NOT NULL CHECK(altitude_ft > 0),
    planned_duration_min INTEGER NOT NULL CHECK(planned_duration_min > 0),
    target_inspired_po2_kpa REAL CHECK(target_inspired_po2_kpa > 0),
    breathing_gas TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,condition,stage)
) STRICT;

CREATE TABLE web_chamber_clinical_case (
    source_id TEXT NOT NULL REFERENCES web_chamber_source_extract,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    condition TEXT NOT NULL,
    source_onset_stage INTEGER NOT NULL CHECK(source_onset_stage > 0),
    source_onset_description TEXT NOT NULL,
    symptom TEXT NOT NULL,
    diagnosis_as_reported TEXT NOT NULL,
    treatment TEXT NOT NULL,
    immediate_outcome TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    FOREIGN KEY(source_id,condition,source_onset_stage) REFERENCES web_chamber_protocol_plateau(source_id,condition,stage)
) STRICT;

CREATE TABLE web_chamber_reported_dcs_rate (
    source_id TEXT NOT NULL REFERENCES web_chamber_source_extract,
    scope TEXT NOT NULL,
    percent_as_reported REAL NOT NULL CHECK(percent_as_reported BETWEEN 0 AND 100),
    numerator INTEGER CHECK(numerator >= 0),
    denominator INTEGER CHECK(denominator > 0 AND (numerator IS NULL OR numerator <= denominator)),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,scope)
) STRICT;

CREATE TABLE web_chamber_vge_summary (
    source_id TEXT NOT NULL REFERENCES web_chamber_source_extract,
    condition TEXT NOT NULL,
    median_peak_rest_grade REAL NOT NULL CHECK(median_peak_rest_grade BETWEEN 0 AND 4),
    median_peak_rest_and_knee_bends_grade REAL NOT NULL CHECK(median_peak_rest_and_knee_bends_grade BETWEEN 0 AND 4),
    median_last_grade REAL NOT NULL CHECK(median_last_grade BETWEEN 0 AND 4),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,condition)
) STRICT;

CREATE TABLE web_chamber_nitrogen_exchange (
    source_id TEXT NOT NULL,
    condition TEXT NOT NULL,
    stage INTEGER NOT NULL,
    scope TEXT NOT NULL,
    participants INTEGER NOT NULL CHECK(participants > 0),
    mean_washout_ml_min REAL NOT NULL,
    sd_washout_ml_min REAL CHECK(sd_washout_ml_min >= 0),
    ci_lower REAL CHECK(ci_lower <= mean_washout_ml_min),
    ci_upper REAL CHECK(ci_upper >= mean_washout_ml_min),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,condition,stage,scope),
    FOREIGN KEY(source_id,condition,stage) REFERENCES web_chamber_protocol_plateau(source_id,condition,stage),
    CHECK((ci_lower IS NULL) = (ci_upper IS NULL))
) STRICT;
