CREATE TABLE publication_arm_exercise_scope (
    source_id TEXT NOT NULL REFERENCES publication_source PRIMARY KEY,
    reported_runs INTEGER CHECK(reported_runs > 0),
    approximate_people INTEGER CHECK(approximate_people > 0),
    reported_group_count INTEGER CHECK(reported_group_count > 0),
    nominal_target_altitude_ft INTEGER CHECK(nominal_target_altitude_ft > 0),
    locator TEXT NOT NULL,
    CHECK(reported_runs IS NOT NULL OR approximate_people IS NOT NULL)
) STRICT;

CREATE TABLE publication_arm_exercise_group (
    source_id TEXT NOT NULL REFERENCES publication_arm_exercise_scope,
    exercise_as_printed TEXT NOT NULL,
    number_of_subjects_as_printed INTEGER NOT NULL CHECK(number_of_subjects_as_printed > 0),
    work_foot_pounds INTEGER NOT NULL CHECK(work_foot_pounds >= 0),
    weight_multiplied_by_jerks_as_printed INTEGER NOT NULL CHECK(weight_multiplied_by_jerks_as_printed >= 0),
    mild_symptoms_percent REAL NOT NULL CHECK(mild_symptoms_percent BETWEEN 0 AND 100),
    moderate_symptoms_percent REAL NOT NULL CHECK(moderate_symptoms_percent BETWEEN 0 AND 100),
    incapacitation_percent REAL NOT NULL CHECK(incapacitation_percent BETWEEN 0 AND 100),
    analysis_role TEXT NOT NULL CHECK(analysis_role='overlap_hold'),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,exercise_as_printed)
) STRICT;
