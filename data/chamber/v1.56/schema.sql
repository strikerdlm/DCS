CREATE TABLE publication_preoxygen_group (
    source_id TEXT NOT NULL REFERENCES publication_source,
    source_table TEXT NOT NULL CHECK(source_table IN ('I','II','III')),
    group_key TEXT NOT NULL,
    target_altitude_ft INTEGER NOT NULL CHECK(target_altitude_ft > 0),
    planned_window_min INTEGER NOT NULL CHECK(planned_window_min > 0),
    window_origin TEXT NOT NULL CHECK(window_origin IN ('target_altitude','exercise_onset')),
    preoxygen_label TEXT NOT NULL,
    stated_preoxygen_min INTEGER CHECK(stated_preoxygen_min > 0),
    oxygen_advance_vs_control_min INTEGER CHECK(oxygen_advance_vs_control_min >= 0),
    group_size INTEGER CHECK(group_size > 0),
    group_size_unit TEXT CHECK(group_size_unit IN ('participants','ascents','unspecified_stratum_n')),
    group_size_basis TEXT CHECK(group_size_basis IN ('stated_in_methods','stated_table_n','ascents_per_condition_from_design')),
    value_basis TEXT NOT NULL CHECK(value_basis IN ('reported','within_participant_average','interpolated_weighted','unweighted_reference')),
    context_note TEXT NOT NULL,
    analysis_role TEXT NOT NULL DEFAULT 'overlap_hold' CHECK(analysis_role='overlap_hold'),
    PRIMARY KEY(source_id, source_table, group_key),
    CHECK((group_size IS NULL) = (group_size_unit IS NULL)),
    CHECK((group_size IS NULL) = (group_size_basis IS NULL)),
    CHECK(value_basis NOT IN ('interpolated_weighted','unweighted_reference') OR group_size IS NULL)
) STRICT;

CREATE TABLE publication_preoxygen_measure (
    source_id TEXT NOT NULL,
    source_table TEXT NOT NULL,
    group_key TEXT NOT NULL,
    measure TEXT NOT NULL CHECK(measure IN ('with_symptoms','with_grade_3_symptoms','incapacitated',
        'mean_symptom_onset','mean_grade_3_occurrence','mean_incapacitation_occurrence','mean_flight_time')),
    unit TEXT NOT NULL CHECK(unit IN ('pct','min')),
    source_value REAL CHECK(source_value >= 0),
    reported_numerator INTEGER CHECK(reported_numerator >= 0),
    printed_page INTEGER NOT NULL CHECK(printed_page > 0),
    note TEXT,
    PRIMARY KEY(source_id, source_table, group_key, measure),
    FOREIGN KEY(source_id, source_table, group_key)
        REFERENCES publication_preoxygen_group(source_id, source_table, group_key),
    CHECK((unit='pct') = (measure NOT LIKE 'mean_%')),
    CHECK(unit!='pct' OR source_value BETWEEN 0 AND 100),
    CHECK(reported_numerator IS NULL OR (unit='pct' AND note IS NOT NULL)),
    CHECK(source_value IS NOT NULL OR note IS NOT NULL)
) STRICT;
