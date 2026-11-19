CREATE TABLE rojas_source (
    source_id TEXT PRIMARY KEY,
    citation TEXT NOT NULL,
    public_url TEXT NOT NULL,
    pdf_sha256 TEXT NOT NULL CHECK(length(pdf_sha256)=64),
    design TEXT NOT NULL,
    case_definition TEXT NOT NULL,
    matching TEXT NOT NULL,
    abstract_period TEXT NOT NULL,
    methods_period TEXT NOT NULL,
    case_total INTEGER NOT NULL CHECK(case_total>0),
    control_total INTEGER NOT NULL CHECK(control_total>0),
    reported_mean_age_years REAL NOT NULL CHECK(reported_mean_age_years>0),
    survey_records_available INTEGER NOT NULL CHECK(
        survey_records_available BETWEEN 0 AND case_total+control_total
    ),
    locator TEXT NOT NULL
) STRICT;

CREATE TABLE rojas_observation (
    source_id TEXT NOT NULL REFERENCES rojas_source,
    grouping TEXT NOT NULL CHECK(grouping IN ('afsc','sex','tobacco','alcohol')),
    category TEXT NOT NULL,
    label TEXT NOT NULL,
    case_count INTEGER NOT NULL CHECK(case_count>=0),
    sampled_control_count INTEGER CHECK(sampled_control_count>=0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,grouping,category),
    CHECK((sampled_control_count IS NULL)=(grouping='afsc'))
) STRICT;

CREATE TABLE rojas_overlap (
    source_id TEXT NOT NULL REFERENCES rojas_source,
    sharepoint_source_id TEXT NOT NULL REFERENCES sharepoint_source,
    relationship TEXT NOT NULL CHECK(relationship='same_study'),
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,sharepoint_source_id)
) STRICT;

CREATE TABLE rojas_result (
    source_id TEXT NOT NULL REFERENCES rojas_source,
    exposure TEXT NOT NULL CHECK(exposure IN ('high_risk_occupation','tobacco','alcohol')),
    odds_ratio_reported REAL,
    ci95_low_reported REAL,
    ci95_high_reported REAL,
    test_reported TEXT NOT NULL,
    statistic_reported REAL NOT NULL,
    df_reported INTEGER,
    p_comparison TEXT NOT NULL CHECK(p_comparison IN ('=','<')),
    p_reported REAL NOT NULL CHECK(p_reported>0 AND p_reported<=1),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,exposure)
) STRICT;

-- Counts refer to sampled records. The missing control column in Table 1 stays NULL.
CREATE VIEW rojas_table_coverage AS
    SELECT grouping, count(*) AS categories, sum(case_count) AS cases_tabulated,
           sum(sampled_control_count) AS controls_tabulated,
           case_total, control_total, case_total-sum(case_count) AS cases_outside_table,
           control_total-sum(sampled_control_count) AS controls_outside_table
    FROM rojas_observation JOIN rojas_source USING(source_id)
    GROUP BY source_id,grouping;
