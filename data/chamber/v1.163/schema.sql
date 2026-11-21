CREATE TABLE publication_pressure_loss_record (
    source_id TEXT NOT NULL REFERENCES publication_source,
    incident_number INTEGER NOT NULL CHECK(incident_number > 0),
    incident_date TEXT NOT NULL,
    aircraft TEXT NOT NULL,
    reported_altitude_ft INTEGER CHECK(reported_altitude_ft > 0),
    altitude_entry TEXT NOT NULL CHECK(altitude_entry IN ('reported','climbout','unknown')),
    speed_class TEXT NOT NULL CHECK(speed_class IN ('massive','intermediate','slow')),
    documented_cabin_altitude_ft INTEGER CHECK(documented_cabin_altitude_ft > 0),
    locator TEXT NOT NULL,
    note TEXT,
    PRIMARY KEY(source_id,incident_number),
    CHECK((reported_altitude_ft IS NOT NULL) = (altitude_entry = 'reported'))
) STRICT;
