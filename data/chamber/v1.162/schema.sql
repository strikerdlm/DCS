CREATE TABLE publication_flight_safety_count (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    numerator INTEGER NOT NULL CHECK(numerator >= 0),
    denominator INTEGER CHECK(denominator > 0 AND numerator <= denominator),
    counting_unit TEXT NOT NULL CHECK(counting_unit IN (
        'reported_depressurization_incident','dcs_affected_aircraft','dcs_affected_aircrew','person','symptom_occurrence'
    )),
    scope TEXT NOT NULL CHECK(scope IN ('reported_cohort','nested_stratum','table_partition','overlapping_margin','source_conflict')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE publication_aircraft_pressure_excursion (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    excursion_number INTEGER NOT NULL CHECK(excursion_number > 0),
    source_section TEXT NOT NULL,
    aircraft_altitude_ft INTEGER NOT NULL CHECK(aircraft_altitude_ft > 0),
    cabin_start_altitude_ft INTEGER NOT NULL CHECK(cabin_start_altitude_ft > 0),
    cabin_end_altitude_ft INTEGER NOT NULL CHECK(cabin_end_altitude_ft > cabin_start_altitude_ft),
    cabin_start_ata REAL NOT NULL CHECK(cabin_start_ata > 0),
    cabin_end_ata REAL CHECK(cabin_end_ata > 0 AND cabin_end_ata < cabin_start_ata),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint,excursion_number,source_section),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;
