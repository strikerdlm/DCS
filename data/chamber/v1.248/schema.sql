CREATE TABLE publication_navy_1940_run (
    source_id TEXT NOT NULL REFERENCES publication_source,
    run_number INTEGER NOT NULL CHECK(run_number > 0),
    exposure_date TEXT NOT NULL,
    participant_codes TEXT NOT NULL,
    symptom_label TEXT NOT NULL CHECK(symptom_label IN (
        'explicit_bends','limb_pain_without_bends_label','no_symptoms_reported','other_symptoms_or_signs'
    )),
    case_source_id TEXT,
    case_stratum TEXT,
    case_endpoint TEXT,
    case_match TEXT CHECK(case_match IN ('confirmed','likely_date_conflict')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,run_number),
    FOREIGN KEY(case_source_id,case_stratum,case_endpoint) REFERENCES publication_observation,
    CHECK((case_source_id IS NULL) = (case_stratum IS NULL) AND
          (case_source_id IS NULL) = (case_endpoint IS NULL) AND
          (case_source_id IS NULL) = (case_match IS NULL))
) STRICT;

CREATE TABLE publication_navy_1940_run_stage (
    source_id TEXT NOT NULL,
    run_number INTEGER NOT NULL,
    stage INTEGER NOT NULL CHECK(stage > 0),
    setting TEXT NOT NULL CHECK(setting IN ('surface','chamber')),
    reported_altitude_ft INTEGER CHECK(reported_altitude_ft > 0),
    reported_duration_min INTEGER NOT NULL CHECK(reported_duration_min > 0),
    gas_as_reported TEXT,
    PRIMARY KEY(source_id,run_number,stage),
    FOREIGN KEY(source_id,run_number) REFERENCES publication_navy_1940_run,
    CHECK(setting <> 'surface' OR reported_altitude_ft IS NULL)
) STRICT;

CREATE TABLE publication_navy_1940_table_ii_bends (
    source_id TEXT NOT NULL REFERENCES publication_source,
    row_number INTEGER NOT NULL CHECK(row_number > 0),
    table_i_run_number INTEGER CHECK(table_i_run_number > 0),
    exposure_date TEXT NOT NULL,
    participant_code TEXT NOT NULL,
    bends_reported INTEGER NOT NULL CHECK(bends_reported IN (0,1)),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,row_number),
    UNIQUE(source_id,table_i_run_number),
    FOREIGN KEY(source_id,table_i_run_number) REFERENCES publication_navy_1940_run
) STRICT;
