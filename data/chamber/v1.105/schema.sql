CREATE TABLE publication_chamber_native_pressure_stage (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    stage INTEGER NOT NULL CHECK(stage > 0),
    planned_duration_min INTEGER NOT NULL CHECK(planned_duration_min > 0),
    printed_nominal_pressure REAL NOT NULL CHECK(printed_nominal_pressure > 0),
    printed_nominal_unit TEXT NOT NULL,
    printed_alternate_pressure REAL CHECK(printed_alternate_pressure > 0),
    printed_alternate_unit TEXT,
    oxygen_percent REAL CHECK(oxygen_percent BETWEEN 0 AND 100),
    nitrogen_percent REAL CHECK(nitrogen_percent BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,stage),
    FOREIGN KEY(source_id,stratum) REFERENCES publication_chamber_trial_scope,
    CHECK((printed_alternate_pressure IS NULL) = (printed_alternate_unit IS NULL))
) STRICT;

CREATE TABLE publication_chamber_case_episode (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    parent_stratum TEXT NOT NULL,
    parent_endpoint TEXT NOT NULL,
    participant_code TEXT NOT NULL,
    episode_order INTEGER NOT NULL CHECK(episode_order > 0),
    months_after_previous_episode REAL CHECK(months_after_previous_episode > 0),
    source_classification TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    UNIQUE(source_id,participant_code,episode_order),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation,
    FOREIGN KEY(source_id,parent_stratum,parent_endpoint) REFERENCES publication_observation,
    CHECK((episode_order = 1) = (months_after_previous_episode IS NULL))
) STRICT;
