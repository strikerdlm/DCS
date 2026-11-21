CREATE TABLE publication_cadet_fitness_comparison (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    fitness_test TEXT NOT NULL,
    unaffected_mean_points REAL NOT NULL,
    affected_mean_points REAL NOT NULL,
    reported_mean_difference_points REAL NOT NULL,
    reported_critical_ratio REAL NOT NULL CHECK(reported_critical_ratio >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY (source_id,stratum,endpoint),
    FOREIGN KEY (source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;
