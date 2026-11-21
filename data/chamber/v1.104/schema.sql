CREATE TABLE publication_chamber_pain_onset_percentage (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    hour_at_altitude INTEGER NOT NULL CHECK(hour_at_altitude > 0),
    reported_percent REAL NOT NULL CHECK(reported_percent BETWEEN 0 AND 100),
    denominator INTEGER CHECK(denominator > 0),
    denominator_unit TEXT CHECK(denominator_unit IN ('symptom_report','person_exposure')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,hour_at_altitude),
    FOREIGN KEY(source_id,stratum) REFERENCES publication_chamber_trial_scope,
    CHECK((denominator IS NULL) = (denominator_unit IS NULL))
) STRICT;
