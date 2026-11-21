-- Each checkpoint subdivides the original observation and shares its initial cohort.
CREATE TABLE publication_outcome_checkpoint (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    elapsed_min INTEGER NOT NULL CHECK(elapsed_min > 0),
    cumulative_events INTEGER NOT NULL CHECK(cumulative_events >= 0),
    analysis_role TEXT NOT NULL CHECK(analysis_role = 'overlap_hold'),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint,elapsed_min),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;
