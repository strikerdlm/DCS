CREATE TABLE publication_repeat_flight_profile (
    source_id TEXT NOT NULL REFERENCES publication_source,
    profile_id TEXT NOT NULL,
    site TEXT NOT NULL,
    table_altitude_ft INTEGER NOT NULL CHECK(table_altitude_ft > 0),
    narrative_altitude_ft INTEGER CHECK(narrative_altitude_ft > 0),
    planned_dwell_min INTEGER NOT NULL CHECK(planned_dwell_min > 0),
    ascent_rate_ft_min INTEGER CHECK(ascent_rate_ft_min > 0),
    protocol TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    locator TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role='overlap_hold'),
    PRIMARY KEY(source_id,profile_id)
) STRICT;

CREATE TABLE publication_repeat_flight_count (
    source_id TEXT NOT NULL,
    profile_id TEXT NOT NULL,
    flight_number INTEGER NOT NULL CHECK(flight_number > 0),
    prior_descents TEXT NOT NULL,
    exposure_count INTEGER NOT NULL CHECK(exposure_count >= 0),
    reported_group_pct REAL NOT NULL CHECK(reported_group_pct >= 0),
    descent_count INTEGER CHECK(descent_count BETWEEN 0 AND exposure_count),
    reported_descent_pct REAL CHECK(reported_descent_pct BETWEEN 0 AND 100),
    printed_page INTEGER NOT NULL CHECK(printed_page > 0),
    note TEXT,
    PRIMARY KEY(source_id,profile_id,flight_number,prior_descents),
    FOREIGN KEY(source_id,profile_id) REFERENCES publication_repeat_flight_profile,
    CHECK(prior_descents='all' OR
        (prior_descents=CAST(CAST(prior_descents AS INTEGER) AS TEXT)
         AND CAST(prior_descents AS INTEGER) BETWEEN 0 AND flight_number-1)),
    CHECK((exposure_count=0) = (descent_count IS NULL)),
    CHECK((descent_count IS NULL) = (reported_descent_pct IS NULL)),
    CHECK(reported_group_pct <= 100 OR coalesce(length(note),0) > 0)
) STRICT;

CREATE TABLE publication_descent_interval (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    interval_start_min INTEGER NOT NULL CHECK(interval_start_min >= 0),
    interval_end_min INTEGER NOT NULL CHECK(interval_end_min > interval_start_min),
    descent_count INTEGER NOT NULL CHECK(descent_count >= 0),
    printed_page INTEGER NOT NULL CHECK(printed_page > 0),
    PRIMARY KEY(source_id,stratum,endpoint,interval_start_min),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;
