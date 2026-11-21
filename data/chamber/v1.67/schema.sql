-- Liske's Table I concerns selected cases that survived neurological dysbarism.
-- The article does not enumerate the chamber or aircraft exposure populations.
CREATE TABLE publication_liske_case_profile (
    source_id TEXT NOT NULL REFERENCES publication_source,
    patient_number INTEGER NOT NULL CHECK(patient_number > 0),
    setting TEXT NOT NULL CHECK(setting IN ('chamber','aircraft')),
    aircraft TEXT,
    age_years INTEGER NOT NULL CHECK(age_years > 0),
    weight_lb INTEGER CHECK(weight_lb > 0),
    body_fat_pct REAL CHECK(body_fat_pct BETWEEN 0 AND 100),
    max_cabin_altitude_ft INTEGER CHECK(max_cabin_altitude_ft > 0),
    time_at_max_altitude_min_low INTEGER CHECK(time_at_max_altitude_min_low > 0),
    time_at_max_altitude_min_high INTEGER CHECK(time_at_max_altitude_min_high >= time_at_max_altitude_min_low),
    prior_dysbaric_symptoms TEXT CHECK(prior_dysbaric_symptoms='yes'),
    observed_by_neurologist_during_episode TEXT NOT NULL CHECK(observed_by_neurologist_during_episode IN ('yes','no')),
    observed_by_flight_surgeon_during_episode TEXT NOT NULL CHECK(observed_by_flight_surgeon_during_episode IN ('yes','no')),
    focal_symptom_summary TEXT NOT NULL,
    focal_exam_summary TEXT NOT NULL,
    postconvalescent_eeg TEXT NOT NULL,
    persistent_eeg_abnormality_reported TEXT CHECK(persistent_eeg_abnormality_reported='yes'),
    locator TEXT NOT NULL,
    note TEXT,
    CHECK((setting='aircraft') = (aircraft IS NOT NULL)),
    CHECK((time_at_max_altitude_min_low IS NULL) = (time_at_max_altitude_min_high IS NULL)),
    PRIMARY KEY(source_id,patient_number)
) STRICT;
