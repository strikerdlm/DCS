CREATE TABLE publication_bryce_headache_sequence (
    source_id TEXT NOT NULL REFERENCES publication_source,
    published_subject_number INTEGER NOT NULL CHECK(published_subject_number IN (1,2)),
    sequence_in_subject INTEGER NOT NULL CHECK(sequence_in_subject > 0),
    age_years INTEGER NOT NULL CHECK(age_years > 0),
    chamber_altitude_ft INTEGER NOT NULL CHECK(chamber_altitude_ft > 0),
    prebreathe_min INTEGER CHECK(prebreathe_min >= 0),
    symptom_elapsed_min INTEGER NOT NULL CHECK(symptom_elapsed_min >= 0),
    symptom_time_basis TEXT NOT NULL CHECK(symptom_time_basis IN (
        'from_protocol_start','after_reported_chamber_flight'
    )),
    symptoms TEXT NOT NULL,
    exam_and_course TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,published_subject_number,sequence_in_subject)
) STRICT;
