-- Measurements from an existing outcome stratum, conditional on detected events.
CREATE TABLE publication_outcome_onset (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    time_basis TEXT NOT NULL CHECK(time_basis IN ('single_detection','mean_sd')),
    onset_min REAL NOT NULL CHECK(onset_min > 0),
    standard_deviation_min REAL CHECK(standard_deviation_min >= 0),
    associated_vge_grades TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((time_basis = 'mean_sd') = (standard_deviation_min IS NOT NULL)),
    PRIMARY KEY(source_id,stratum,endpoint),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;
