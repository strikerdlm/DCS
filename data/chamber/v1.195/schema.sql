CREATE TABLE publication_chamber_diagnostic_run (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    run_number INTEGER NOT NULL CHECK(run_number > 0),
    actual_peak_ft INTEGER NOT NULL CHECK(actual_peak_ft > 0),
    sham_indicated_ft INTEGER CHECK(sham_indicated_ft > 0),
    prebreathe_min INTEGER CHECK(prebreathe_min >= 0),
    days_after_first_actual_run INTEGER CHECK(days_after_first_actual_run >= 0),
    symptom_reported INTEGER NOT NULL CHECK(symptom_reported IN (0,1)),
    onset_min_after_exercise INTEGER CHECK(onset_min_after_exercise >= 0),
    peak_pain_grade INTEGER CHECK(peak_pain_grade > 0),
    symptom_resolution_altitude_ft INTEGER CHECK(symptom_resolution_altitude_ft BETWEEN 0 AND actual_peak_ft),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint,run_number),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation,
    CHECK(symptom_reported=1 OR (
        onset_min_after_exercise IS NULL AND peak_pain_grade IS NULL AND symptom_resolution_altitude_ft IS NULL
    ))
) STRICT;
