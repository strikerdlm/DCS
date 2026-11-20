CREATE TABLE publication_observation_revision (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    evidence_source_id TEXT NOT NULL REFERENCES publication_source,
    numerator INTEGER NOT NULL CHECK(numerator >= 0),
    previous_denominator INTEGER NOT NULL CHECK(previous_denominator > 0),
    denominator INTEGER NOT NULL CHECK(denominator > 0),
    outcome_window TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK(numerator <= previous_denominator AND numerator <= denominator),
    PRIMARY KEY(source_id,stratum,endpoint),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;
