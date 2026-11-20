CREATE TABLE publication_exposure_outcome_margin (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    dimension TEXT NOT NULL,
    level INTEGER NOT NULL,
    level_label TEXT NOT NULL,
    cases INTEGER NOT NULL CHECK(cases >= 0),
    right_censored INTEGER NOT NULL CHECK(right_censored >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY (source_id, stratum, endpoint, dimension, level),
    FOREIGN KEY (source_id, stratum, endpoint)
        REFERENCES publication_observation(source_id, stratum, endpoint),
    CHECK(cases + right_censored > 0),
    CHECK(
        (dimension = 'final_pressure_mmhg' AND level > 0)
        OR (dimension = 'prebreathe_min' AND level >= 0)
        OR (dimension = 'exercise_code' AND level BETWEEN 1 AND 3)
        OR (dimension = 'maximum_spencer_grade' AND level BETWEEN 0 AND 4)
    )
) STRICT;
