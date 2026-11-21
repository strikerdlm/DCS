CREATE TABLE publication_role_incidence_estimate (
    source_id TEXT NOT NULL REFERENCES publication_source,
    role_as_reported TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    reported_cases INTEGER NOT NULL CHECK(reported_cases >= 0),
    observed_role_exposures INTEGER CHECK(observed_role_exposures >= reported_cases AND observed_role_exposures > 0),
    rate_per_1000 REAL NOT NULL CHECK(rate_per_1000 BETWEEN 0 AND 1000),
    ci_lower_per_1000 REAL NOT NULL CHECK(ci_lower_per_1000 BETWEEN 0 AND rate_per_1000),
    ci_upper_per_1000 REAL NOT NULL CHECK(ci_upper_per_1000 BETWEEN rate_per_1000 AND 1000),
    confidence_level REAL NOT NULL CHECK(confidence_level > 0 AND confidence_level < 1),
    nominal_ico_per_exercise REAL NOT NULL CHECK(nominal_ico_per_exercise > 0),
    mean_students_per_exercise REAL NOT NULL CHECK(mean_students_per_exercise > 0),
    denominator_basis TEXT NOT NULL CHECK(denominator_basis = 'author_estimated_staffing'),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,role_as_reported,endpoint),
    CHECK(observed_role_exposures IS NULL)
) STRICT;

CREATE TABLE publication_web_count_discrepancy (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    alternate_case_count INTEGER NOT NULL CHECK(alternate_case_count >= 0),
    alternate_locator TEXT NOT NULL,
    corroborating_locators TEXT NOT NULL,
    resolution TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint,alternate_locator),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES web_observation(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE publication_treatment_session_summary (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    treated_cases INTEGER NOT NULL CHECK(treated_cases > 0),
    median_sessions REAL NOT NULL CHECK(median_sessions > 0),
    q1_sessions REAL NOT NULL CHECK(q1_sessions <= median_sessions),
    q3_sessions REAL NOT NULL CHECK(q3_sessions >= median_sessions),
    minimum_sessions INTEGER NOT NULL CHECK(minimum_sessions > 0 AND minimum_sessions <= q1_sessions),
    maximum_sessions INTEGER NOT NULL CHECK(maximum_sessions >= q3_sessions),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum)
) STRICT;
