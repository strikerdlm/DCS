CREATE TABLE publication_outcome_latency_summary (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    timed_events INTEGER NOT NULL CHECK(timed_events > 0),
    mean_minutes REAL NOT NULL CHECK(mean_minutes >= 0),
    standard_deviation_minutes REAL NOT NULL CHECK(standard_deviation_minutes >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;
