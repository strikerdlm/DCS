CREATE TABLE publication_navy_1944_participant (
    source_id TEXT NOT NULL REFERENCES publication_source,
    reported_outcome_group TEXT NOT NULL CHECK(reported_outcome_group IN ('good','fair','poor')),
    subject_number_within_table INTEGER NOT NULL CHECK(subject_number_within_table > 0),
    age_years INTEGER NOT NULL CHECK(age_years > 0),
    weight_lb REAL NOT NULL CHECK(weight_lb > 0),
    cardiovascular_score_as_printed INTEGER NOT NULL CHECK(cardiovascular_score_as_printed > 0),
    specific_gravity_as_printed INTEGER CHECK(specific_gravity_as_printed > 0),
    test_1_time_min REAL NOT NULL CHECK(test_1_time_min > 0 AND test_1_time_min <= 120),
    test_1_time_basis TEXT NOT NULL CHECK(test_1_time_basis IN (
        'duration_at_altitude','time_at_altitude_before_bends'
    )),
    test_2_duration_min REAL CHECK(test_2_duration_min > 0 AND test_2_duration_min <= 120),
    test_3_duration_min REAL CHECK(test_3_duration_min > 0 AND test_3_duration_min <= 120),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,reported_outcome_group,subject_number_within_table),
    CHECK((test_1_time_basis = 'time_at_altitude_before_bends') = (reported_outcome_group = 'poor')),
    CHECK(reported_outcome_group <> 'poor' OR (test_2_duration_min IS NULL AND test_3_duration_min IS NULL))
) STRICT;
