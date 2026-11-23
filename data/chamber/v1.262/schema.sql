CREATE TABLE publication_chamber_altitude_trace (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    elapsed_sec INTEGER NOT NULL CHECK(elapsed_sec >= 0),
    altitude_ft INTEGER NOT NULL CHECK(altitude_ft >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,elapsed_sec),
    FOREIGN KEY(source_id,stratum) REFERENCES publication_chamber_trial_scope(source_id,stratum)
) STRICT;
