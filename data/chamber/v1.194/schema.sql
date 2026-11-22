CREATE TABLE publication_chamber_activity_tally (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    counting_unit TEXT NOT NULL CHECK(counting_unit IN (
        'chamber_run','distinct_people','person_exposure',
        'people_trained_as_reported','attendee','symptom_prompted_chamber_descent'
    )),
    reported_count INTEGER NOT NULL CHECK(reported_count > 0),
    count_qualifier TEXT NOT NULL CHECK(count_qualifier IN ('as_printed','approximate','greater_than')),
    through_date TEXT,
    altitude_ft INTEGER CHECK(altitude_ft > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,counting_unit)
) STRICT;
