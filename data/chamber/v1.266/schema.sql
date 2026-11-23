CREATE TABLE publication_balloon_flight_measurement (
    source_id TEXT NOT NULL REFERENCES publication_source,
    program_id TEXT NOT NULL,
    flight_date TEXT NOT NULL,
    reporting_section TEXT NOT NULL,
    ambient_altitude_kind TEXT NOT NULL CHECK(ambient_altitude_kind IN (
        'exit_altitude_as_reported','flight_altitude_as_reported'
    )),
    ambient_altitude_ft REAL NOT NULL CHECK(ambient_altitude_ft > 0),
    ambient_altitude_m REAL NOT NULL CHECK(ambient_altitude_m > 0),
    freefall_sec INTEGER CHECK(freefall_sec > 0),
    under_parachute_sec INTEGER CHECK(under_parachute_sec > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id, program_id, flight_date, reporting_section)
) STRICT;
