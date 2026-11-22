CREATE TABLE publication_berkeley_denitrogenation_group (
    source_id TEXT NOT NULL REFERENCES publication_source,
    protocol_id TEXT NOT NULL,
    protocol TEXT NOT NULL,
    reported_tests INTEGER NOT NULL CHECK(reported_tests > 0),
    planned_target_altitude_ft INTEGER NOT NULL CHECK(planned_target_altitude_ft > 0),
    planned_target_duration_min INTEGER NOT NULL CHECK(planned_target_duration_min > 0),
    locator TEXT NOT NULL,
    overlap_note TEXT NOT NULL,
    PRIMARY KEY(source_id,protocol_id)
) STRICT;

CREATE TABLE publication_berkeley_symptom_grade (
    source_id TEXT NOT NULL,
    protocol_id TEXT NOT NULL,
    category_order INTEGER NOT NULL CHECK(category_order > 0),
    symptom_category TEXT NOT NULL,
    reported_tests INTEGER NOT NULL CHECK(reported_tests >= 0),
    cumulative_percent_as_printed REAL CHECK(cumulative_percent_as_printed BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,protocol_id,category_order),
    UNIQUE(source_id,protocol_id,symptom_category),
    FOREIGN KEY(source_id,protocol_id) REFERENCES publication_berkeley_denitrogenation_group(source_id,protocol_id)
) STRICT;

CREATE TABLE publication_berkeley_pain_timing (
    source_id TEXT NOT NULL REFERENCES publication_source,
    maximum_pain_grade INTEGER NOT NULL CHECK(maximum_pain_grade BETWEEN 1 AND 5),
    entry_in_grade INTEGER NOT NULL CHECK(entry_in_grade > 0),
    minutes_after_reaching_38000_ft INTEGER NOT NULL CHECK(minutes_after_reaching_38000_ft >= 0),
    minutes_to_maximum_after_reaching_38000_ft INTEGER
        CHECK(minutes_to_maximum_after_reaching_38000_ft >= minutes_after_reaching_38000_ft),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,maximum_pain_grade,entry_in_grade)
) STRICT;

CREATE TABLE publication_rapid_decompression_case_detail (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    standard_prebreathe_min INTEGER CHECK(standard_prebreathe_min >= 0),
    standard_decompression_start_ft INTEGER NOT NULL CHECK(standard_decompression_start_ft >= 0),
    standard_target_ft INTEGER NOT NULL CHECK(standard_target_ft > standard_decompression_start_ft),
    standard_decompression_approx_seconds INTEGER CHECK(standard_decompression_approx_seconds > 0),
    symptom_onset_ft INTEGER CHECK(symptom_onset_ft > 0),
    first_distress_signal_ft INTEGER NOT NULL CHECK(first_distress_signal_ft > 0),
    actual_peak_ft INTEGER NOT NULL CHECK(actual_peak_ft >= first_distress_signal_ft),
    emergency_descent_ft_per_min INTEGER CHECK(emergency_descent_ft_per_min > 0),
    onset_text TEXT NOT NULL,
    clinical_diagnosis TEXT NOT NULL,
    imaging TEXT NOT NULL,
    visual_recovery_hours_after_first_treatment INTEGER CHECK(visual_recovery_hours_after_first_treatment > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation(source_id,stratum,endpoint)
) STRICT;
