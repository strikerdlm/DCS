CREATE TABLE citation_ssr_sample (
    source_id TEXT NOT NULL REFERENCES citation_source,
    sample_id TEXT NOT NULL,
    parent_sample_id TEXT,
    participants INTEGER CHECK(participants > 0),
    exposures INTEGER CHECK(exposures > 0),
    profiles INTEGER CHECK(profiles > 0),
    minimum_exposures_per_participant INTEGER CHECK(minimum_exposures_per_participant > 0),
    outcome_stratum TEXT,
    outcome_endpoint TEXT,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,sample_id),
    FOREIGN KEY(source_id,parent_sample_id) REFERENCES citation_ssr_sample(source_id,sample_id),
    FOREIGN KEY(source_id,outcome_stratum,outcome_endpoint)
        REFERENCES citation_observation(source_id,stratum,endpoint),
    CHECK((outcome_stratum IS NULL)=(outcome_endpoint IS NULL)),
    CHECK(parent_sample_id IS NULL OR parent_sample_id<>sample_id),
    CHECK(participants IS NOT NULL OR exposures IS NOT NULL)
) STRICT;

CREATE TABLE citation_ssr_covariate (
    source_id TEXT NOT NULL,
    sample_id TEXT NOT NULL,
    sex_as_reported TEXT NOT NULL CHECK(sex_as_reported IN ('Women','Men','All')),
    covariate TEXT NOT NULL CHECK(covariate IN ('age','weight','height','bmi','body_fat_percent','vo2max')),
    participants_in_group INTEGER NOT NULL CHECK(participants_in_group > 0),
    participants_in_regression INTEGER NOT NULL CHECK(participants_in_regression BETWEEN 1 AND participants_in_group),
    mean_as_reported REAL CHECK(mean_as_reported > 0),
    mean_unit TEXT,
    slope_as_printed TEXT NOT NULL,
    r_squared REAL NOT NULL CHECK(r_squared BETWEEN 0 AND 1),
    p_value REAL NOT NULL CHECK(p_value BETWEEN 0 AND 1),
    regression_locator TEXT NOT NULL,
    mean_locator TEXT,
    PRIMARY KEY(source_id,sample_id,sex_as_reported,covariate),
    FOREIGN KEY(source_id,sample_id) REFERENCES citation_ssr_sample(source_id,sample_id),
    CHECK((mean_as_reported IS NULL)=(mean_unit IS NULL)
          AND (mean_as_reported IS NULL)=(mean_locator IS NULL))
) STRICT;

CREATE TABLE citation_ssr_bin (
    source_id TEXT NOT NULL,
    sample_id TEXT NOT NULL,
    bin_order INTEGER NOT NULL CHECK(bin_order > 0),
    label_as_printed TEXT NOT NULL,
    participant_count INTEGER NOT NULL CHECK(participant_count > 0),
    count_basis TEXT NOT NULL CHECK(count_basis IN ('stated_in_text','digitized_from_graph')),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,sample_id,bin_order),
    FOREIGN KEY(source_id,sample_id) REFERENCES citation_ssr_sample(source_id,sample_id)
) STRICT;

CREATE TABLE citation_ssr_repeat_contrast (
    source_id TEXT NOT NULL,
    sample_id TEXT NOT NULL,
    exposures_per_block INTEGER NOT NULL CHECK(exposures_per_block > 0),
    mean_ssr_change_second_minus_first REAL NOT NULL,
    sd_ssr_change REAL NOT NULL CHECK(sd_ssr_change >= 0),
    min_ssr_change REAL NOT NULL CHECK(min_ssr_change <= mean_ssr_change_second_minus_first),
    max_ssr_change REAL NOT NULL CHECK(max_ssr_change >= mean_ssr_change_second_minus_first),
    profile_dcs_change_percent_as_reported REAL NOT NULL,
    significance_as_reported TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,sample_id),
    FOREIGN KEY(source_id,sample_id) REFERENCES citation_ssr_sample(source_id,sample_id)
) STRICT;
