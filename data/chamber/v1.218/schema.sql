CREATE TABLE publication_washout_archive_context (
    source_id TEXT PRIMARY KEY REFERENCES publication_source,
    chamber_source_id TEXT NOT NULL REFERENCES publication_source,
    series_count INTEGER NOT NULL CHECK(series_count > 0),
    reused_person_exposures INTEGER NOT NULL CHECK(reused_person_exposures > 0),
    linked_washout_people INTEGER NOT NULL CHECK(linked_washout_people > 0),
    symptom_percent_as_printed REAL NOT NULL CHECK(symptom_percent_as_printed BETWEEN 0 AND 100),
    vge_percent_as_printed REAL NOT NULL CHECK(vge_percent_as_printed BETWEEN 0 AND 100),
    comparison_interval_min INTEGER NOT NULL CHECK(comparison_interval_min > 0),
    estimated_power_min_percent REAL NOT NULL CHECK(estimated_power_min_percent BETWEEN 0 AND 100),
    estimated_power_max_percent REAL NOT NULL CHECK(estimated_power_max_percent BETWEEN estimated_power_min_percent AND 100),
    locator TEXT NOT NULL,
    note TEXT NOT NULL
) STRICT;

CREATE TABLE publication_washout_response_group (
    source_id TEXT NOT NULL REFERENCES publication_washout_archive_context,
    response_group TEXT NOT NULL,
    response_pattern_as_printed TEXT NOT NULL,
    people INTEGER NOT NULL CHECK(people > 0),
    group_basis TEXT NOT NULL CHECK(group_basis IN ('source_partition', 'overlapping_pool')),
    plotted_group TEXT,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,response_group)
) STRICT;

CREATE TABLE publication_washout_mean_difference (
    source_id TEXT NOT NULL REFERENCES publication_washout_archive_context,
    washout_min INTEGER NOT NULL CHECK(washout_min > 0),
    measurement TEXT NOT NULL,
    unit_as_printed TEXT NOT NULL,
    contrast_group TEXT NOT NULL,
    reference_group TEXT NOT NULL,
    mean_difference_as_printed REAL NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,washout_min,measurement),
    FOREIGN KEY(source_id,contrast_group) REFERENCES publication_washout_response_group(source_id,response_group),
    FOREIGN KEY(source_id,reference_group) REFERENCES publication_washout_response_group(source_id,response_group)
) STRICT;

CREATE TABLE publication_hydration_washout_subject (
    source_id TEXT NOT NULL REFERENCES publication_source,
    study_local_subject INTEGER NOT NULL CHECK(study_local_subject > 0),
    age_years INTEGER NOT NULL CHECK(age_years > 0),
    weight_kg REAL NOT NULL CHECK(weight_kg > 0),
    height_cm REAL NOT NULL CHECK(height_cm > 0),
    body_fat_percent REAL NOT NULL CHECK(body_fat_percent BETWEEN 0 AND 100),
    body_density_as_printed REAL NOT NULL CHECK(body_density_as_printed > 0),
    estimated_tissue_n2_ml REAL NOT NULL CHECK(estimated_tissue_n2_ml > 0),
    mean_measured_tissue_n2_removed_ml REAL NOT NULL CHECK(mean_measured_tissue_n2_removed_ml > 0),
    washout_efficiency_percent_as_printed REAL NOT NULL CHECK(washout_efficiency_percent_as_printed BETWEEN 0 AND 100),
    respiration_rate_as_printed REAL NOT NULL CHECK(respiration_rate_as_printed > 0),
    tidal_volume_ml REAL NOT NULL CHECK(tidal_volume_ml > 0),
    breaths_in_3_hours INTEGER NOT NULL CHECK(breaths_in_3_hours > 0),
    total_exhaled_o2_l REAL NOT NULL CHECK(total_exhaled_o2_l > 0),
    n2_removal_after_3_hours_ml_min REAL NOT NULL CHECK(n2_removal_after_3_hours_ml_min > 0),
    n2_concentration_after_3_hours_percent REAL NOT NULL CHECK(n2_concentration_after_3_hours_percent BETWEEN 0 AND 100),
    baseline_washouts INTEGER NOT NULL CHECK(baseline_washouts > 0),
    hydrated_washouts INTEGER NOT NULL CHECK(hydrated_washouts > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,study_local_subject)
) STRICT;
