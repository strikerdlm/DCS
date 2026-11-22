CREATE TABLE publication_exercise_bout_vo2 (
    source_id TEXT NOT NULL REFERENCES publication_source,
    exercise_mode TEXT NOT NULL CHECK(exercise_mode IN ('isometric','isotonic')),
    limb TEXT NOT NULL CHECK(limb IN ('arm','leg')),
    average_interval_min INTEGER NOT NULL CHECK(average_interval_min > 0),
    mean_vo2_ml_min REAL NOT NULL CHECK(mean_vo2_ml_min > 0),
    workload_selection_participants INTEGER NOT NULL CHECK(workload_selection_participants > 0),
    verification_participants INTEGER CHECK(verification_participants > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,exercise_mode,limb)
) STRICT;

CREATE TABLE publication_model_development_scope (
    source_id TEXT PRIMARY KEY REFERENCES publication_source,
    profile_count INTEGER NOT NULL CHECK(profile_count > 0),
    subjects_as_reported INTEGER NOT NULL CHECK(subjects_as_reported > 0),
    lower_altitude_ft INTEGER NOT NULL CHECK(lower_altitude_ft > 0),
    upper_altitude_ft INTEGER NOT NULL CHECK(upper_altitude_ft >= lower_altitude_ft),
    dcs_case_count INTEGER CHECK(dcs_case_count >= 0),
    locator TEXT NOT NULL
) STRICT;
