CREATE TABLE publication_nasa_archive_chart_cell (
    source_id TEXT NOT NULL REFERENCES publication_source,
    panel TEXT NOT NULL CHECK(panel IN ('dcs_classification','vge_grade','pain_trajectory')),
    category_as_printed TEXT NOT NULL,
    denominator_as_reported INTEGER NOT NULL CHECK(denominator_as_reported > 0),
    denominator_unit TEXT NOT NULL CHECK(denominator_unit IN ('person_exposure','unspecified')),
    count_as_printed INTEGER CHECK(count_as_printed BETWEEN 0 AND denominator_as_reported),
    percent_as_printed REAL NOT NULL CHECK(percent_as_printed BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    CHECK(panel <> 'pain_trajectory' OR count_as_printed IS NOT NULL),
    PRIMARY KEY(source_id,panel,category_as_printed)
) STRICT;
