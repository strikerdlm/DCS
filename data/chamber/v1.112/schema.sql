-- The literature selections preserve published values on overlap hold.
CREATE TABLE publication_nasa_long_exposure (
    report_source_id TEXT NOT NULL REFERENCES source(source_id),
    table_label TEXT NOT NULL CHECK(table_label IN ('F4', 'F5')),
    reported_group INTEGER NOT NULL CHECK(reported_group > 0),
    printed_author TEXT NOT NULL,
    exposures INTEGER NOT NULL CHECK(exposures > 0),
    prebreathe_as_printed TEXT NOT NULL,
    pn2_360_psia_as_printed REAL NOT NULL CHECK(pn2_360_psia_as_printed > 0),
    tr360_as_printed REAL NOT NULL CHECK(tr360_as_printed > 0),
    pressure_psia REAL NOT NULL CHECK(pressure_psia > 0),
    exercise_flag INTEGER NOT NULL CHECK(exercise_flag IN (0, 1)),
    planned_altitude_min INTEGER NOT NULL,
    dcs_cases INTEGER NOT NULL CHECK(dcs_cases BETWEEN 0 AND exposures),
    dcs_percent_as_printed REAL NOT NULL CHECK(dcs_percent_as_printed BETWEEN 0 AND 100),
    serious_cases INTEGER NOT NULL CHECK(serious_cases BETWEEN 0 AND dcs_cases),
    nasa_test_id TEXT REFERENCES nasa_test(test_id),
    linkage_status TEXT NOT NULL CHECK(linkage_status IN (
        'matched_group', 'matched_component', 'likely_subset', 'unresolved'
    )),
    locator TEXT NOT NULL,
    comparison_locator TEXT NOT NULL,
    comparison_url TEXT NOT NULL,
    linkage_evidence TEXT NOT NULL,
    analysis_role TEXT NOT NULL DEFAULT 'overlap_hold' CHECK(analysis_role = 'overlap_hold'),
    PRIMARY KEY(report_source_id, table_label, reported_group),
    CHECK((table_label = 'F4' AND planned_altitude_min > 360)
          OR (table_label = 'F5' AND planned_altitude_min = 360))
) STRICT;
