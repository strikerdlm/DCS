CREATE TABLE publication_chamber_case_altitude_stage (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    stage INTEGER NOT NULL CHECK (stage > 0),
    setting TEXT NOT NULL CHECK (setting IN ('surface', 'chamber')),
    reported_altitude_ft INTEGER CHECK (reported_altitude_ft > 0),
    reported_duration_min INTEGER CHECK (reported_duration_min > 0),
    gas_as_reported TEXT,
    locator TEXT NOT NULL,
    PRIMARY KEY (source_id, stratum, endpoint, stage),
    FOREIGN KEY (source_id, stratum, endpoint) REFERENCES publication_observation,
    CHECK ((setting = 'chamber') = (reported_altitude_ft IS NOT NULL))
) STRICT;
