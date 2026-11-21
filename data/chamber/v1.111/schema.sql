-- Reanalysis cohorts are linked to existing NASA test IDs and stay outside the development counts.
CREATE TABLE publication_nasa_reanalysis_test (
    source_id TEXT NOT NULL REFERENCES publication_source,
    test_number INTEGER NOT NULL CHECK (test_number > 0),
    stratum TEXT NOT NULL,
    nasa_test_id TEXT NOT NULL REFERENCES nasa_test(test_id),
    linkage_status TEXT NOT NULL CHECK (linkage_status IN ('documented_program_group', 'documented_protocol', 'likely_same_test')),
    pressure_psia REAL NOT NULL CHECK (pressure_psia > 0),
    planned_duration_min INTEGER NOT NULL CHECK (planned_duration_min > 0),
    pure_oxygen_total_min INTEGER NOT NULL CHECK (pure_oxygen_total_min > 0),
    ascent_min INTEGER NOT NULL CHECK (ascent_min > 0 AND ascent_min <= pure_oxygen_total_min),
    exercise_in_prebreathe INTEGER NOT NULL CHECK (exercise_in_prebreathe IN (0, 1)),
    exercise_at_altitude INTEGER NOT NULL CHECK (exercise_at_altitude IN (0, 1)),
    lower_body_adynamic INTEGER NOT NULL CHECK (lower_body_adynamic IN (0, 1)),
    mixed_gas_min INTEGER CHECK (mixed_gas_min > 0),
    mixed_gas_pressure_psia REAL CHECK (mixed_gas_pressure_psia > 0),
    mixed_gas_oxygen_percent REAL CHECK (mixed_gas_oxygen_percent BETWEEN 0 AND 100),
    type_ii_dcs_as_reported INTEGER NOT NULL CHECK (type_ii_dcs_as_reported >= 0),
    comparison_locator TEXT NOT NULL,
    linkage_evidence TEXT NOT NULL,
    PRIMARY KEY (source_id, test_number),
    UNIQUE (source_id, stratum),
    UNIQUE (source_id, nasa_test_id),
    CHECK ((mixed_gas_min IS NULL) = (mixed_gas_pressure_psia IS NULL)),
    CHECK ((mixed_gas_min IS NULL) = (mixed_gas_oxygen_percent IS NULL))
) STRICT;

-- Appendix row ordinals identify printed records, not people across studies.
CREATE TABLE publication_nasa_reanalysis_removal (
    source_id TEXT NOT NULL,
    table_row INTEGER NOT NULL CHECK (table_row > 0),
    test_number INTEGER NOT NULL,
    dcs_reported INTEGER NOT NULL CHECK (dcs_reported IN (0, 1)),
    symptom_report_min INTEGER CHECK (symptom_report_min >= 0),
    chamber_removal_min INTEGER NOT NULL CHECK (chamber_removal_min > 0),
    source_marks_end_of_test INTEGER NOT NULL CHECK (source_marks_end_of_test IN (0, 1)),
    maximum_spencer_grade INTEGER NOT NULL CHECK (maximum_spencer_grade BETWEEN 0 AND 4),
    first_symptom_location TEXT,
    locator TEXT NOT NULL,
    PRIMARY KEY (source_id, table_row),
    FOREIGN KEY (source_id, test_number) REFERENCES publication_nasa_reanalysis_test,
    CHECK ((dcs_reported = 0) = (symptom_report_min IS NULL)),
    CHECK ((dcs_reported = 0) = (first_symptom_location IS NULL)),
    CHECK (symptom_report_min <= chamber_removal_min)
) STRICT;

-- The time-window margins reuse the study cohort and have distinct observed risk sets.
CREATE TABLE publication_nasa_reanalysis_vge_margin (
    source_id TEXT NOT NULL REFERENCES publication_source,
    window_label TEXT NOT NULL,
    exposures INTEGER NOT NULL CHECK (exposures > 0),
    mean_time_min INTEGER NOT NULL CHECK (mean_time_min > 0),
    time_sd_min INTEGER NOT NULL CHECK (time_sd_min >= 0),
    grade_0 INTEGER NOT NULL CHECK (grade_0 >= 0),
    grade_i INTEGER NOT NULL CHECK (grade_i >= 0),
    grade_ii INTEGER NOT NULL CHECK (grade_ii >= 0),
    grade_iii INTEGER NOT NULL CHECK (grade_iii >= 0),
    grade_iv INTEGER NOT NULL CHECK (grade_iv >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY (source_id, window_label),
    CHECK (grade_0 + grade_i + grade_ii + grade_iii + grade_iv = exposures)
) STRICT;
