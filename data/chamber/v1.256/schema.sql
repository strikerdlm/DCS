CREATE TABLE publication_diesel_exposure (
    source_id TEXT NOT NULL REFERENCES publication_source,
    printed_subject INTEGER NOT NULL CHECK(printed_subject > 0),
    exposure_duration_min INTEGER NOT NULL CHECK(exposure_duration_min > 0),
    final_altitude_ft INTEGER NOT NULL CHECK(final_altitude_ft > 0),
    max_spencer_vge_grade INTEGER NOT NULL CHECK(max_spencer_vge_grade BETWEEN 0 AND 4),
    reported_dcs_symptoms TEXT NOT NULL,
    symptom_pattern TEXT NOT NULL CHECK(symptom_pattern IN ('constant', 'intermittent', 'none')),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id, printed_subject),
    CHECK((symptom_pattern = 'none') = (reported_dcs_symptoms = 'None'))
) STRICT;
