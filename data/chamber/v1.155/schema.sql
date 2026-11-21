CREATE TABLE discovery_observation_completion (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    evidence_source_id TEXT NOT NULL REFERENCES discovery_source,
    numerator INTEGER NOT NULL CHECK(numerator >= 0),
    denominator INTEGER NOT NULL CHECK(denominator > 0 AND denominator >= numerator),
    target_pressure_psia REAL NOT NULL CHECK(target_pressure_psia > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES discovery_observation
) STRICT;

CREATE TABLE discovery_eva_session (
    source_id TEXT NOT NULL REFERENCES discovery_source,
    test_number INTEGER NOT NULL CHECK(test_number > 0),
    eva_number INTEGER NOT NULL CHECK(eva_number > 0),
    test_month TEXT NOT NULL,
    prebreathe_min INTEGER NOT NULL CHECK(prebreathe_min >= 0),
    target_pressure_psia REAL NOT NULL CHECK(target_pressure_psia > 0),
    participating_exposures INTEGER NOT NULL CHECK(participating_exposures > 0),
    evaluated_exposures INTEGER NOT NULL CHECK(evaluated_exposures BETWEEN 1 AND participating_exposures),
    endpoint TEXT NOT NULL,
    cases INTEGER NOT NULL CHECK(cases BETWEEN 0 AND evaluated_exposures),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,test_number,eva_number)
) STRICT;
