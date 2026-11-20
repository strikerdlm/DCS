CREATE TABLE publication_preselection_rate (
    source_id TEXT NOT NULL REFERENCES publication_source,
    source_table TEXT NOT NULL,
    printed_page INTEGER NOT NULL CHECK(printed_page > 0),
    proportion_selected_pct INTEGER NOT NULL CHECK(proportion_selected_pct BETWEEN 1 AND 100),
    validation_group TEXT NOT NULL,
    endpoint TEXT NOT NULL CHECK(endpoint IN ('total_symptoms','moderate_or_severe_symptoms','forced_descents')),
    reported_pct REAL NOT NULL CHECK(reported_pct BETWEEN 0 AND 100),
    value_basis TEXT NOT NULL CHECK(value_basis IN ('reported_validation_rate','calculated_control_rate')),
    validation_exposure_denominator INTEGER CHECK(validation_exposure_denominator > 0),
    validation_altitude_ft INTEGER CHECK(validation_altitude_ft > 0),
    outcome_horizon_min INTEGER NOT NULL CHECK(outcome_horizon_min > 0),
    analysis_role TEXT NOT NULL DEFAULT 'overlap_hold' CHECK(analysis_role='overlap_hold'),
    PRIMARY KEY(source_id, source_table, proportion_selected_pct, validation_group, endpoint),
    CHECK(validation_exposure_denominator IS NULL OR
          (value_basis='reported_validation_rate' AND proportion_selected_pct=100))
) STRICT;
