CREATE TABLE publication_vann04_dive_profile (
    source_id TEXT NOT NULL REFERENCES cohort_source,
    profile TEXT NOT NULL,
    dive_1_depth_fsw INTEGER NOT NULL CHECK(dive_1_depth_fsw > 0),
    dive_1_bottom_min INTEGER NOT NULL CHECK(dive_1_bottom_min > 0),
    first_surface_interval_min INTEGER CHECK(first_surface_interval_min > 0),
    dive_2_depth_fsw INTEGER CHECK(dive_2_depth_fsw > 0),
    dive_2_bottom_min INTEGER CHECK(dive_2_bottom_min > 0),
    second_surface_interval_min INTEGER CHECK(second_surface_interval_min > 0),
    dive_3_depth_fsw INTEGER CHECK(dive_3_depth_fsw > 0),
    dive_3_bottom_min INTEGER CHECK(dive_3_bottom_min > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((first_surface_interval_min IS NULL) = (dive_2_depth_fsw IS NULL)),
    CHECK((first_surface_interval_min IS NULL) = (dive_2_bottom_min IS NULL)),
    CHECK((second_surface_interval_min IS NULL) = (dive_3_depth_fsw IS NULL)),
    CHECK((second_surface_interval_min IS NULL) = (dive_3_bottom_min IS NULL)),
    CHECK(second_surface_interval_min IS NULL OR first_surface_interval_min IS NOT NULL),
    PRIMARY KEY(source_id,profile)
) STRICT;

CREATE TABLE publication_vann04_flight_group (
    source_id TEXT NOT NULL,
    profile TEXT NOT NULL,
    preflight_surface_interval_hours INTEGER NOT NULL CHECK(preflight_surface_interval_hours > 0),
    printed_exposures INTEGER NOT NULL CHECK(printed_exposures > 0),
    dcs_cases INTEGER NOT NULL CHECK(dcs_cases BETWEEN 0 AND printed_exposures),
    printed_dcs_percent REAL NOT NULL CHECK(printed_dcs_percent BETWEEN 0 AND 100),
    parent_stratum TEXT NOT NULL,
    parent_endpoint TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,profile,preflight_surface_interval_hours),
    FOREIGN KEY(source_id,profile) REFERENCES publication_vann04_dive_profile,
    FOREIGN KEY(source_id,parent_stratum,parent_endpoint) REFERENCES cohort_observation(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE publication_vann04_case (
    source_id TEXT NOT NULL,
    case_number INTEGER NOT NULL CHECK(case_number > 0),
    profile TEXT NOT NULL,
    preflight_surface_interval_hours INTEGER NOT NULL,
    onset_phase TEXT NOT NULL CHECK(onset_phase IN ('in_flight','post_flight','chamber_exit')),
    reported_onset_min INTEGER CHECK(reported_onset_min >= 0),
    first_dive_bottom_min_override INTEGER CHECK(first_dive_bottom_min_override > 0),
    linked_appendix_a_case INTEGER CHECK(linked_appendix_a_case > 0),
    symptoms TEXT NOT NULL,
    treatment TEXT,
    resolution TEXT NOT NULL,
    locator TEXT NOT NULL,
    CHECK(onset_phase != 'chamber_exit' OR reported_onset_min IS NULL),
    PRIMARY KEY(source_id,case_number),
    FOREIGN KEY(source_id,profile,preflight_surface_interval_hours) REFERENCES publication_vann04_flight_group
) STRICT;
