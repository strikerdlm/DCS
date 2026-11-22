-- Session timings complement the outcome margins. The original incidence denominators remain in discovery_observation.
CREATE TABLE discovery_eva_prebreathe_timing (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    duration_as_printed TEXT NOT NULL,
    reported_duration_seconds INTEGER NOT NULL CHECK(reported_duration_seconds > 0),
    reported_resolution_seconds INTEGER NOT NULL CHECK(reported_resolution_seconds IN (1, 60)),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES discovery_observation,
    CHECK(reported_duration_seconds % reported_resolution_seconds = 0)
) STRICT;
