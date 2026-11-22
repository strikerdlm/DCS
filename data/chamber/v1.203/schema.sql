CREATE TABLE publication_chamber_vge_protocol (
    source_id TEXT NOT NULL REFERENCES publication_source,
    condition TEXT NOT NULL,
    preparation TEXT NOT NULL,
    cohort_participants INTEGER NOT NULL CHECK(cohort_participants > 0),
    nominal_altitude_ft INTEGER NOT NULL CHECK(nominal_altitude_ft > 0),
    nominal_dwell_min INTEGER NOT NULL CHECK(nominal_dwell_min > 0),
    nominal_pressure_change_ft_min INTEGER NOT NULL CHECK(nominal_pressure_change_ft_min > 0),
    target_inspired_po2_kpa REAL NOT NULL CHECK(target_inspired_po2_kpa > 0),
    grade_scale TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role IN ('descriptive','overlap_hold')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,condition)
) STRICT;

CREATE TABLE publication_pressure_stage_vge_mean (
    source_id TEXT NOT NULL,
    condition TEXT NOT NULL,
    phase TEXT NOT NULL CHECK(phase IN ('ascent','descent')),
    stage_index INTEGER NOT NULL CHECK(stage_index > 0),
    altitude_ft INTEGER NOT NULL CHECK(altitude_ft >= 0),
    mean_rest_grade REAL NOT NULL CHECK(mean_rest_grade BETWEEN 0 AND 4),
    mean_after_knee_bends_grade REAL NOT NULL CHECK(mean_after_knee_bends_grade BETWEEN 0 AND 4),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,condition,phase,altitude_ft),
    UNIQUE(source_id,condition,phase,stage_index),
    FOREIGN KEY(source_id,condition) REFERENCES publication_chamber_vge_protocol(source_id,condition)
) STRICT;

CREATE TABLE publication_chamber_vge_detection_summary (
    source_id TEXT NOT NULL,
    condition TEXT NOT NULL,
    measurement_context TEXT NOT NULL CHECK(measurement_context IN ('rest','after_knee_bends')),
    highest_observed_grade INTEGER NOT NULL CHECK(highest_observed_grade BETWEEN 0 AND 4),
    first_detection_mean_min REAL NOT NULL CHECK(first_detection_mean_min >= 0),
    first_detection_spread_min REAL NOT NULL CHECK(first_detection_spread_min >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,condition,measurement_context),
    FOREIGN KEY(source_id,condition) REFERENCES publication_chamber_vge_protocol(source_id,condition)
) STRICT;
