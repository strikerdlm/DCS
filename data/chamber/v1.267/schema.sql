CREATE TABLE publication_u2_survey_wave (
    source_id TEXT NOT NULL REFERENCES publication_source,
    survey_group TEXT NOT NULL CHECK(survey_group IN ('preliminary','hfhs_i','hfhs_ii')),
    initial_address_list INTEGER CHECK(initial_address_list >= distributed),
    distributed INTEGER NOT NULL CHECK(distributed > 0),
    returned INTEGER NOT NULL CHECK(returned BETWEEN 1 AND distributed),
    usable INTEGER NOT NULL CHECK(usable BETWEEN 1 AND returned),
    response_percent_as_printed REAL NOT NULL CHECK(response_percent_as_printed BETWEEN 0 AND 100),
    mean_age_years REAL NOT NULL CHECK(mean_age_years > 0),
    mean_total_flying_hours INTEGER NOT NULL CHECK(mean_total_flying_hours > 0),
    mean_high_flight_hours INTEGER NOT NULL CHECK(mean_high_flight_hours > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id, survey_group)
) STRICT;

CREATE TABLE publication_u2_survey_result (
    source_id TEXT NOT NULL REFERENCES publication_source,
    survey_group TEXT NOT NULL CHECK(survey_group IN ('preliminary','hfhs_i','hfhs_ii','combined_ps_hfhs_i')),
    endpoint TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role IN ('descriptive','overlapping_margin','denominator_conflict')),
    numerator INTEGER CHECK(numerator >= 0),
    denominator INTEGER CHECK(denominator > 0 AND (numerator IS NULL OR numerator <= denominator)),
    counting_unit TEXT NOT NULL CHECK(counting_unit IN (
        'questionnaire_response','symptomatic_response','pressure_loss_history_response',
        'reported_mission','reported_episode','unspecified_survey_response'
    )),
    reported_percent REAL CHECK(reported_percent BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK(numerator IS NOT NULL OR reported_percent IS NOT NULL),
    PRIMARY KEY(source_id, survey_group, endpoint)
) STRICT;

CREATE TABLE publication_u2_arthritis_effect (
    source_id TEXT NOT NULL,
    survey_group TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    odds_ratio REAL NOT NULL CHECK(odds_ratio > 0),
    lower_95_ci REAL NOT NULL CHECK(lower_95_ci > 0 AND lower_95_ci <= odds_ratio),
    upper_95_ci REAL NOT NULL CHECK(upper_95_ci >= odds_ratio),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id, survey_group, endpoint),
    FOREIGN KEY(source_id, survey_group) REFERENCES publication_u2_survey_wave
) STRICT;
