CREATE TABLE publication_brooks91_doppler_scope (
    source_id TEXT PRIMARY KEY REFERENCES publication_source(source_id),
    reported_exposures INTEGER NOT NULL CHECK(reported_exposures > 0),
    reported_protocol_hours_min INTEGER NOT NULL CHECK(reported_protocol_hours_min > 0),
    reported_protocol_hours_max INTEGER NOT NULL CHECK(reported_protocol_hours_max >= reported_protocol_hours_min),
    ground_pressure_mmhg INTEGER NOT NULL CHECK(ground_pressure_mmhg > 0),
    altitude_pressure_mmhg_min INTEGER NOT NULL CHECK(altitude_pressure_mmhg_min > 0),
    altitude_pressure_mmhg_max INTEGER NOT NULL CHECK(altitude_pressure_mmhg_max >= altitude_pressure_mmhg_min),
    breathing_oxygen_fraction REAL NOT NULL CHECK(breathing_oxygen_fraction BETWEEN 0 AND 1),
    grading_scale TEXT NOT NULL,
    reported_pct_dcs_symptoms_with_early_termination REAL NOT NULL
        CHECK(reported_pct_dcs_symptoms_with_early_termination BETWEEN 0 AND 100),
    overlap_status TEXT NOT NULL CHECK(overlap_status = 'possible_overlap'),
    locator TEXT NOT NULL
) STRICT;

CREATE TABLE publication_olson91_paired_protocol (
    source_id TEXT PRIMARY KEY REFERENCES publication_source(source_id),
    participants INTEGER NOT NULL CHECK(participants > 0),
    altitude_ft_lower INTEGER NOT NULL CHECK(altitude_ft_lower > 0),
    altitude_ft_upper INTEGER NOT NULL CHECK(altitude_ft_upper > altitude_ft_lower),
    oxygen_prebreathe_min INTEGER NOT NULL CHECK(oxygen_prebreathe_min >= 0),
    prebreathe_oxygen_fraction REAL NOT NULL CHECK(prebreathe_oxygen_fraction BETWEEN 0 AND 1),
    exercise_min_per_cycle INTEGER NOT NULL CHECK(exercise_min_per_cycle > 0),
    exercise_cycle_min INTEGER NOT NULL CHECK(exercise_cycle_min >= exercise_min_per_cycle),
    ultrasound_interval_min INTEGER NOT NULL CHECK(ultrasound_interval_min > 0),
    reported_onset_pattern TEXT NOT NULL,
    reported_resolution_pattern TEXT NOT NULL,
    locator TEXT NOT NULL
) STRICT;
