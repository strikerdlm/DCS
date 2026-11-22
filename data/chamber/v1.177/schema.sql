-- Billings reproduced Berry's symptom margins on a scale of 100,000 man-flights.
-- The rate base is distinct from the exposure denominator. Dashes remain null.
CREATE TABLE publication_berry_trapped_gas_rate (
    source_id TEXT NOT NULL REFERENCES publication_source,
    original_source_id TEXT NOT NULL REFERENCES publication_source,
    symptom TEXT NOT NULL CHECK(symptom IN (
        'ear_pain', 'abdominal_pain', 'sinus_pain', 'toothache', 'total'
    )),
    severity_grade TEXT NOT NULL CHECK(severity_grade IN ('I', 'II', 'III', 'IV', 'total')),
    rate_per_100000_person_flights INTEGER CHECK(rate_per_100000_person_flights BETWEEN 0 AND 100000),
    exposure_denominator INTEGER NOT NULL CHECK(exposure_denominator > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id, symptom, severity_grade),
    CHECK(source_id <> original_source_id)
) STRICT;
