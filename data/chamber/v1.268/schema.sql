CREATE TABLE publication_flight_surveillance_tally (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    measure TEXT NOT NULL,
    unit TEXT NOT NULL CHECK(unit IN ('reported_mishap','aircraft_flying_hour')),
    reported_count INTEGER NOT NULL CHECK(reported_count >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id, stratum, measure)
) STRICT;
