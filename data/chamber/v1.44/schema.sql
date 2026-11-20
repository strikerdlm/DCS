-- Published symptomatic rows with group denominators retained in publication_observation.
CREATE TABLE publication_chamber_reported_onset (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    reported_row INTEGER NOT NULL CHECK(reported_row > 0),
    published_subject_code TEXT NOT NULL,
    onset_min INTEGER NOT NULL CHECK(onset_min >= 0),
    time_at_altitude_min INTEGER NOT NULL CHECK(time_at_altitude_min >= onset_min),
    locator TEXT NOT NULL,
    PRIMARY KEY (source_id, stratum, endpoint, reported_row),
    FOREIGN KEY (source_id, stratum, endpoint)
        REFERENCES publication_observation(source_id, stratum, endpoint)
) STRICT;
