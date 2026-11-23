CREATE TABLE publication_stratex_balloon_flight (
    source_id TEXT NOT NULL REFERENCES publication_source,
    flight_number INTEGER NOT NULL CHECK(flight_number BETWEEN 1 AND 3),
    flight_date TEXT NOT NULL UNIQUE,
    reported_ambient_release_altitude_ft INTEGER NOT NULL CHECK(reported_ambient_release_altitude_ft > 0),
    ascent_duration_min INTEGER NOT NULL CHECK(ascent_duration_min > 0),
    freefall_duration_sec INTEGER NOT NULL CHECK(freefall_duration_sec > 0),
    reporting_suit_source_id TEXT NOT NULL REFERENCES publication_source,
    nominal_suit_pressure_differential_psi REAL NOT NULL CHECK(nominal_suit_pressure_differential_psi > 0),
    alternative_ambient_release_altitude_ft INTEGER CHECK(alternative_ambient_release_altitude_ft > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id, flight_number)
) STRICT;
