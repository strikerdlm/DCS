-- Printed cells from a treated-case archive. Onset and maximum-altitude
-- margins share cases and have no chamber exposure denominators.
CREATE TABLE publication_butler_case_margin (
    source_id TEXT NOT NULL REFERENCES citation_source,
    panel TEXT NOT NULL CHECK(panel IN ('onset', 'maximum_altitude')),
    case_period TEXT NOT NULL,
    exposure_setting TEXT NOT NULL CHECK(exposure_setting IN (
        'pooled', 'chamber', 'operations'
    )),
    category_order INTEGER NOT NULL CHECK(category_order > 0),
    category_as_printed TEXT NOT NULL,
    cases_as_printed INTEGER CHECK(cases_as_printed >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,panel,case_period,exposure_setting,category_order)
) STRICT;

-- Preserve printed percentages across source scopes, including the unresolved
-- 1,137-case narrative count. These are not estimated cumulative event rates.
CREATE TABLE publication_butler_case_percentage (
    source_id TEXT NOT NULL REFERENCES citation_source,
    panel TEXT NOT NULL CHECK(panel IN (
        'onset_table_total', 'maximum_altitude_table_total', 'onset_narrative'
    )),
    case_period TEXT NOT NULL,
    category_as_printed TEXT NOT NULL,
    reported_percent INTEGER NOT NULL CHECK(reported_percent BETWEEN 0 AND 100),
    case_denominator_as_printed INTEGER CHECK(case_denominator_as_printed > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,panel,case_period,category_as_printed),
    CHECK(case_denominator_as_printed IS NULL OR panel='onset_narrative')
) STRICT;
