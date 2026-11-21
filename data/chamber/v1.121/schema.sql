CREATE TABLE publication_prp_prebreathe_oxygen (
    source_id TEXT NOT NULL REFERENCES sharepoint_source,
    printed_row INTEGER NOT NULL CHECK(printed_row > 0),
    phase_as_printed TEXT NOT NULL,
    linked_phase TEXT,
    phase_link_status TEXT NOT NULL CHECK(phase_link_status IN ('identified','phase_label_conflict')),
    estimate_liters_stpd REAL NOT NULL CHECK(estimate_liters_stpd > 0),
    estimate_spread_liters_stpd REAL NOT NULL CHECK(estimate_spread_liters_stpd >= 0),
    estimate_n INTEGER NOT NULL CHECK(estimate_n > 0),
    measured_liters_stpd REAL CHECK(measured_liters_stpd > 0),
    measured_spread_liters_stpd REAL CHECK(measured_spread_liters_stpd >= 0),
    measured_n INTEGER CHECK(measured_n > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,printed_row),
    FOREIGN KEY(source_id,linked_phase) REFERENCES publication_prp_analysis_counts(source_id,phase),
    CHECK((linked_phase IS NULL) = (phase_link_status = 'phase_label_conflict')),
    CHECK((measured_liters_stpd IS NULL) = (measured_spread_liters_stpd IS NULL)),
    CHECK((measured_liters_stpd IS NULL) = (measured_n IS NULL))
) STRICT;

CREATE TABLE publication_calibration_workload (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    metric TEXT NOT NULL,
    unit TEXT NOT NULL,
    mean REAL NOT NULL CHECK(mean > 0),
    standard_error REAL NOT NULL CHECK(standard_error >= 0),
    sample_n INTEGER NOT NULL CHECK(sample_n > 0),
    measurement_context TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,metric),
    CHECK (
        (metric = 'metabolic_rate' AND unit = 'kcal/h') OR
        (metric = 'task_fraction_of_vo2max' AND unit = 'percent' AND mean <= 100) OR
        (metric = 'vo2max' AND unit = 'mL/kg/min')
    )
) STRICT;

CREATE TABLE publication_prebreathe_compilation_rate (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    cited_protocol_as_printed TEXT NOT NULL,
    reporting_group TEXT NOT NULL CHECK(reporting_group IN
        ('resting','prebreathe_exercise','seated_combined')),
    reported_percent INTEGER CHECK(reported_percent BETWEEN 0 AND 100),
    denominator_as_printed INTEGER CHECK(denominator_as_printed > 0),
    denominator_unit TEXT CHECK(denominator_unit IN ('as_reported_n','flight')),
    related_source TEXT,
    relationship_status TEXT NOT NULL CHECK(relationship_status IN
        ('linked_reprint','overlap_hold','possible_overlap','underlying_source_pending')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,reporting_group),
    CHECK((denominator_as_printed IS NULL) = (denominator_unit IS NULL)),
    CHECK(related_source IS NOT NULL OR relationship_status = 'underlying_source_pending')
) STRICT;
