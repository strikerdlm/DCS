CREATE TABLE publication_chamber_trial_scope (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    parent_stratum TEXT,
    evidence_source_id TEXT NOT NULL REFERENCES publication_source,
    trial_count INTEGER CHECK(trial_count > 0),
    participant_count INTEGER CHECK(participant_count > 0),
    pressure_mmhg REAL CHECK(pressure_mmhg > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum),
    FOREIGN KEY(source_id,parent_stratum) REFERENCES publication_chamber_trial_scope(source_id,stratum),
    CHECK(parent_stratum IS NULL OR parent_stratum <> stratum),
    CHECK(trial_count IS NOT NULL OR participant_count IS NOT NULL OR pressure_mmhg IS NOT NULL)
) STRICT;

CREATE TABLE publication_chamber_exposure_stage (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    stage INTEGER NOT NULL CHECK(stage > 0),
    planned_duration_min INTEGER NOT NULL CHECK(planned_duration_min > 0),
    pressure_hpa REAL NOT NULL CHECK(pressure_hpa > 0),
    oxygen_percent_lower REAL CHECK(oxygen_percent_lower BETWEEN 0 AND 100),
    oxygen_percent_upper REAL CHECK(oxygen_percent_upper BETWEEN oxygen_percent_lower AND 100),
    gas_as_described TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint,stage),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation,
    CHECK((oxygen_percent_lower IS NULL) = (oxygen_percent_upper IS NULL))
) STRICT;

CREATE TABLE publication_vge_dcs_percent_range (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    bubble_grade_lower INTEGER NOT NULL CHECK(bubble_grade_lower BETWEEN 0 AND 4),
    bubble_grade_upper INTEGER NOT NULL CHECK(bubble_grade_upper BETWEEN bubble_grade_lower AND 4),
    reported_percent_lower REAL NOT NULL CHECK(reported_percent_lower BETWEEN 0 AND 100),
    reported_percent_upper REAL NOT NULL CHECK(reported_percent_upper BETWEEN reported_percent_lower AND 100),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum)
) STRICT;
