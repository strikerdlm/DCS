CREATE TABLE publication_pressure_stage_vge_range (
    source_id TEXT NOT NULL REFERENCES publication_source,
    condition TEXT NOT NULL,
    phase TEXT NOT NULL CHECK(phase IN ('ascent','descent')),
    altitude_ft INTEGER NOT NULL CHECK(altitude_ft >= 0),
    participants_as_reported INTEGER NOT NULL CHECK(participants_as_reported > 0),
    measurement_context TEXT NOT NULL,
    grade_scale TEXT NOT NULL,
    minimum_grade INTEGER NOT NULL CHECK(minimum_grade BETWEEN 0 AND 5),
    median_grade REAL NOT NULL CHECK(median_grade BETWEEN minimum_grade AND maximum_grade),
    maximum_grade INTEGER NOT NULL CHECK(maximum_grade BETWEEN minimum_grade AND 5),
    p_less_than_vs_final_descent_24000 REAL CHECK(p_less_than_vs_final_descent_24000 > 0 AND p_less_than_vs_final_descent_24000 <= 1),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,condition,phase,altitude_ft,measurement_context)
) STRICT;

CREATE TABLE literature_vge_repeatability_cohort (
    source_id TEXT PRIMARY KEY REFERENCES literature_source,
    participants INTEGER NOT NULL CHECK(participants > 0),
    participants_in_both_short_gas_groups INTEGER NOT NULL CHECK(participants_in_both_short_gas_groups BETWEEN 0 AND participants),
    participants_with_dcs_in_contributing_experiments INTEGER NOT NULL CHECK(participants_with_dcs_in_contributing_experiments BETWEEN 0 AND participants),
    locator TEXT NOT NULL,
    note TEXT NOT NULL
) STRICT;

CREATE TABLE literature_vge_repeatability (
    source_id TEXT NOT NULL REFERENCES literature_vge_repeatability_cohort,
    comparison TEXT NOT NULL,
    participants INTEGER NOT NULL CHECK(participants > 0),
    nominal_altitude_ft INTEGER NOT NULL CHECK(nominal_altitude_ft > 0),
    oxygen_percent INTEGER CHECK(oxygen_percent BETWEEN 1 AND 100),
    observation_min_lower INTEGER NOT NULL CHECK(observation_min_lower > 0),
    observation_min_upper INTEGER NOT NULL CHECK(observation_min_upper >= observation_min_lower),
    minimum_grade_difference INTEGER NOT NULL CHECK(minimum_grade_difference BETWEEN 0 AND 4),
    median_grade_difference REAL NOT NULL CHECK(median_grade_difference BETWEEN minimum_grade_difference AND maximum_grade_difference),
    maximum_grade_difference INTEGER NOT NULL CHECK(maximum_grade_difference BETWEEN minimum_grade_difference AND 4),
    icc REAL CHECK(icc BETWEEN -1 AND 1),
    icc_lower REAL CHECK(icc_lower BETWEEN -1 AND icc),
    icc_upper REAL CHECK(icc_upper BETWEEN icc AND 1),
    threshold_grade INTEGER NOT NULL CHECK(threshold_grade BETWEEN 1 AND 4),
    participants_crossing_threshold INTEGER CHECK(participants_crossing_threshold BETWEEN 0 AND participants),
    crossing_percent_reported REAL CHECK(crossing_percent_reported BETWEEN 0 AND 100),
    crossing_ci_lower REAL CHECK(crossing_ci_lower BETWEEN 0 AND crossing_percent_reported),
    crossing_ci_upper REAL CHECK(crossing_ci_upper BETWEEN crossing_percent_reported AND 100),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,comparison),
    CHECK((icc IS NULL) = (icc_lower IS NULL) AND (icc IS NULL) = (icc_upper IS NULL)),
    CHECK((participants_crossing_threshold IS NULL) = (crossing_percent_reported IS NULL)),
    CHECK((crossing_percent_reported IS NULL) = (crossing_ci_lower IS NULL)),
    CHECK((crossing_percent_reported IS NULL) = (crossing_ci_upper IS NULL))
) STRICT;

CREATE TABLE literature_vge_repeatability_grade_range (
    source_id TEXT NOT NULL,
    comparison TEXT NOT NULL,
    minimum_grade INTEGER NOT NULL CHECK(minimum_grade BETWEEN 0 AND 4),
    maximum_grade INTEGER NOT NULL CHECK(maximum_grade BETWEEN minimum_grade AND 4),
    participants INTEGER NOT NULL CHECK(participants > 0),
    locator TEXT NOT NULL,
    extraction_method TEXT NOT NULL,
    PRIMARY KEY(source_id,comparison,minimum_grade,maximum_grade),
    FOREIGN KEY(source_id,comparison) REFERENCES literature_vge_repeatability(source_id,comparison)
) STRICT;
