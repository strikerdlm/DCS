CREATE TABLE publication_gottschalk24_protocol (
    source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    condition TEXT NOT NULL CHECK(condition IN ('Control','ECCw','ECCu')),
    exercise_24h_before TEXT NOT NULL,
    trial_order TEXT NOT NULL,
    participant_exposures INTEGER NOT NULL CHECK(participant_exposures > 0),
    target_altitude_ft INTEGER NOT NULL CHECK(target_altitude_ft > 0),
    planned_duration_min INTEGER NOT NULL CHECK(planned_duration_min > 0),
    oxygen_fraction REAL NOT NULL CHECK(oxygen_fraction BETWEEN 0 AND 1),
    oxygen_start_before_ascent_sec_min INTEGER NOT NULL CHECK(oxygen_start_before_ascent_sec_min >= 0),
    oxygen_start_before_ascent_sec_max INTEGER NOT NULL
        CHECK(oxygen_start_before_ascent_sec_max >= oxygen_start_before_ascent_sec_min),
    vge_assessment_method TEXT NOT NULL,
    vge_scale TEXT NOT NULL CHECK(vge_scale = 'Eftedal-Brubakk 0-5'),
    rest_assessment_interval_min INTEGER NOT NULL CHECK(rest_assessment_interval_min > 0),
    provocation_assessment_interval_min INTEGER NOT NULL CHECK(provocation_assessment_interval_min > 0),
    exposures_with_visible_vge INTEGER NOT NULL CHECK(exposures_with_visible_vge BETWEEN 0 AND participant_exposures),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,condition)
) STRICT;

CREATE TABLE publication_gottschalk24_vge_peak (
    source_id TEXT NOT NULL,
    participant_number INTEGER NOT NULL CHECK(participant_number > 0),
    condition TEXT NOT NULL,
    rest_eb_grade INTEGER NOT NULL CHECK(rest_eb_grade BETWEEN 0 AND 5),
    knee_flex_eb_grade INTEGER NOT NULL CHECK(knee_flex_eb_grade BETWEEN 0 AND 5),
    arm_flex_eb_grade INTEGER NOT NULL CHECK(arm_flex_eb_grade BETWEEN 0 AND 5),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,participant_number,condition),
    FOREIGN KEY(source_id,condition) REFERENCES publication_gottschalk24_protocol(source_id,condition)
) STRICT;

CREATE TABLE publication_gottschalk24_safety_stop (
    source_id TEXT NOT NULL,
    condition TEXT NOT NULL,
    altitude_elapsed_min INTEGER NOT NULL CHECK(altitude_elapsed_min > 0),
    reported_stop_count INTEGER NOT NULL CHECK(reported_stop_count > 0),
    reported_trigger TEXT NOT NULL CHECK(reported_trigger = 'EB score >=4'),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,condition,altitude_elapsed_min),
    FOREIGN KEY(source_id,condition) REFERENCES publication_gottschalk24_protocol(source_id,condition)
) STRICT;
