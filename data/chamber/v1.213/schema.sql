CREATE TABLE publication_exercise_trial (
    source_id TEXT PRIMARY KEY REFERENCES publication_source,
    participants INTEGER NOT NULL CHECK(participants > 0),
    altitude_ceiling_ft INTEGER NOT NULL CHECK(altitude_ceiling_ft > 0),
    planned_altitude_duration_min INTEGER NOT NULL CHECK(planned_altitude_duration_min > 0),
    ascent_ft_per_min INTEGER NOT NULL CHECK(ascent_ft_per_min > 0),
    prebreathe_min INTEGER NOT NULL CHECK(prebreathe_min >= 0),
    scheduled_oxygen_fraction REAL NOT NULL CHECK(scheduled_oxygen_fraction BETWEEN 0 AND 1),
    exercise_min_per_cycle INTEGER NOT NULL CHECK(exercise_min_per_cycle > 0),
    exercise_cycle_min INTEGER NOT NULL CHECK(exercise_cycle_min >= exercise_min_per_cycle),
    postbreathe_min INTEGER NOT NULL CHECK(postbreathe_min >= 0),
    vge_method TEXT NOT NULL,
    dcs_endpoint TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role = 'overlap_hold'),
    locator TEXT NOT NULL,
    note TEXT NOT NULL
) STRICT;

CREATE TABLE publication_exercise_arm (
    source_id TEXT NOT NULL REFERENCES publication_exercise_trial,
    arm TEXT NOT NULL CHECK(arm IN ('rest','dynamic_arm','dynamic_leg','isometric_arm','isometric_leg')),
    dcs_pct_printed INTEGER NOT NULL CHECK(dcs_pct_printed BETWEEN 0 AND 100),
    any_vge_pct_printed INTEGER NOT NULL CHECK(any_vge_pct_printed BETWEEN 0 AND 100),
    severe_vge_pct_printed INTEGER NOT NULL CHECK(severe_vge_pct_printed BETWEEN 0 AND any_vge_pct_printed),
    vo2_mean_ml_kg_min REAL,
    vo2_sd_ml_kg_min REAL CHECK(vo2_sd_ml_kg_min >= 0),
    vo2_min_ml_kg_min REAL,
    vo2_max_ml_kg_min REAL,
    vo2_measurement_definition TEXT,
    vo2_locator TEXT,
    outcome_locator TEXT NOT NULL,
    CHECK((arm='rest')=(vo2_mean_ml_kg_min IS NULL)),
    CHECK((vo2_mean_ml_kg_min IS NULL)=(vo2_sd_ml_kg_min IS NULL)),
    CHECK((vo2_mean_ml_kg_min IS NULL)=(vo2_min_ml_kg_min IS NULL)),
    CHECK((vo2_mean_ml_kg_min IS NULL)=(vo2_max_ml_kg_min IS NULL)),
    CHECK((vo2_mean_ml_kg_min IS NULL)=(vo2_measurement_definition IS NULL)),
    CHECK((vo2_mean_ml_kg_min IS NULL)=(vo2_locator IS NULL)),
    CHECK(vo2_min_ml_kg_min <= vo2_mean_ml_kg_min AND vo2_mean_ml_kg_min <= vo2_max_ml_kg_min),
    PRIMARY KEY(source_id,arm)
) STRICT;

CREATE TABLE publication_exercise_participant_exposure (
    source_id TEXT NOT NULL,
    study_participant INTEGER NOT NULL CHECK(study_participant > 0),
    arm TEXT NOT NULL,
    selected_altitude_ft INTEGER NOT NULL CHECK(selected_altitude_ft > 0),
    dcs_endpoint_observed INTEGER NOT NULL CHECK(dcs_endpoint_observed IN (0,1)),
    vge_band TEXT NOT NULL CHECK(vge_band IN ('none_detected','spencer_1_2','spencer_3_4')),
    locator TEXT NOT NULL,
    CHECK(arm <> 'rest' OR dcs_endpoint_observed = 0),
    PRIMARY KEY(source_id,study_participant,arm),
    FOREIGN KEY(source_id,arm) REFERENCES publication_exercise_arm(source_id,arm)
) STRICT;

CREATE TABLE publication_exercise_preliminary_rate (
    source_id TEXT NOT NULL REFERENCES publication_source,
    arm_as_reported TEXT NOT NULL CHECK(arm_as_reported IN ('isotonic_arm','isotonic_leg','isometric_arm','isometric_leg')),
    overall_study_participants INTEGER NOT NULL CHECK(overall_study_participants > 0),
    dcs_pct_printed INTEGER NOT NULL CHECK(dcs_pct_printed BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,arm_as_reported)
) STRICT;

CREATE TABLE publication_exercise_pretest_subject (
    source_id TEXT NOT NULL REFERENCES publication_source,
    pretest_participant TEXT NOT NULL CHECK(pretest_participant IN ('A','B','C','D')),
    height_cm REAL NOT NULL CHECK(height_cm > 0),
    weight_kg REAL NOT NULL CHECK(weight_kg > 0),
    body_fat_pct REAL NOT NULL CHECK(body_fat_pct BETWEEN 0 AND 100),
    max_voluntary_contraction_kg REAL NOT NULL CHECK(max_voluntary_contraction_kg > 0),
    vo2max_l_min REAL NOT NULL CHECK(vo2max_l_min > 0),
    vo2max_ml_kg_min REAL NOT NULL CHECK(vo2max_ml_kg_min > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,pretest_participant)
) STRICT;

CREATE TABLE publication_exercise_pretest_vo2 (
    source_id TEXT NOT NULL,
    pretest_participant TEXT NOT NULL,
    arm TEXT NOT NULL CHECK(arm IN ('isometric_arm','isotonic_arm')),
    rest_4min_mean_ml_min INTEGER NOT NULL CHECK(rest_4min_mean_ml_min > 0),
    work_4min_mean_ml_min INTEGER NOT NULL CHECK(work_4min_mean_ml_min > 0),
    recovery_4min_mean_ml_min INTEGER NOT NULL CHECK(recovery_4min_mean_ml_min > 0),
    overall_12min_mean_ml_min INTEGER NOT NULL CHECK(overall_12min_mean_ml_min > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,pretest_participant,arm),
    FOREIGN KEY(source_id,pretest_participant) REFERENCES publication_exercise_pretest_subject(source_id,pretest_participant)
) STRICT;
