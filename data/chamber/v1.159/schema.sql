CREATE TABLE publication_naval_decompression_event (
    source_id TEXT NOT NULL REFERENCES publication_source,
    event_number INTEGER NOT NULL CHECK(event_number > 0),
    aircraft TEXT NOT NULL,
    aircraft_altitude_ft INTEGER NOT NULL CHECK(aircraft_altitude_ft > 0),
    cabin_altitude_before_ft INTEGER NOT NULL CHECK(cabin_altitude_before_ft > 0),
    cabin_altitude_after_ft INTEGER CHECK(cabin_altitude_after_ft > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,event_number)
) STRICT;

CREATE TABLE publication_naval_decompression_aviator (
    source_id TEXT NOT NULL,
    aviator_number INTEGER NOT NULL CHECK(aviator_number > 0),
    event_number INTEGER NOT NULL CHECK(event_number > 0),
    age_years INTEGER NOT NULL CHECK(age_years > 0),
    briefing_room TEXT NOT NULL CHECK(briefing_room IN ('planning','staging')),
    symptomatic_as_reported INTEGER NOT NULL CHECK(symptomatic_as_reported IN (0,1)),
    hyperbaric_treatment_reported INTEGER NOT NULL CHECK(hyperbaric_treatment_reported IN (0,1)),
    symptom_summary TEXT,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,aviator_number),
    FOREIGN KEY(source_id,event_number) REFERENCES publication_naval_decompression_event,
    CHECK(hyperbaric_treatment_reported <= symptomatic_as_reported),
    CHECK((symptom_summary IS NOT NULL) = (symptomatic_as_reported = 1))
) STRICT;
