CREATE TABLE cohort_rush_standard_profile (
    source_id TEXT NOT NULL REFERENCES cohort_source,
    profile TEXT NOT NULL,
    peak_flight_level INTEGER NOT NULL CHECK(peak_flight_level > 0),
    minutes_above_fl250 INTEGER CHECK(minutes_above_fl250 >= 0),
    nominal_hypoxia_demonstration_fl INTEGER CHECK(nominal_hypoxia_demonstration_fl > 0),
    reported_profile_duration_min INTEGER NOT NULL CHECK(reported_profile_duration_min > 0),
    ground_prebreathe_min INTEGER CHECK(ground_prebreathe_min >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id, profile)
) STRICT;

CREATE TABLE cohort_rush_post_chamber_case (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    printed_row INTEGER NOT NULL CHECK(printed_row > 0),
    status_as_reported TEXT NOT NULL,
    base_chamber_profile TEXT NOT NULL,
    rapid_decompression_recorded INTEGER NOT NULL CHECK(rapid_decompression_recorded IN (0, 1)),
    approx_surface_interval_h REAL NOT NULL CHECK(approx_surface_interval_h >= 0),
    approx_air_travel_duration_h REAL NOT NULL CHECK(approx_air_travel_duration_h > 0),
    onset_phase TEXT NOT NULL CHECK(onset_phase IN ('aircraft_ascent', 'at_aircraft_altitude', 'after_landing')),
    reported_landing_to_onset_h REAL CHECK(reported_landing_to_onset_h >= 0),
    symptoms_as_reported TEXT NOT NULL,
    reported_peak_cabin_altitude_ft INTEGER CHECK(reported_peak_cabin_altitude_ft > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id, stratum, endpoint, printed_row),
    FOREIGN KEY(source_id, stratum, endpoint) REFERENCES cohort_observation,
    FOREIGN KEY(source_id, base_chamber_profile) REFERENCES cohort_rush_standard_profile,
    CHECK((onset_phase = 'after_landing') = (reported_landing_to_onset_h IS NOT NULL))
) STRICT;
