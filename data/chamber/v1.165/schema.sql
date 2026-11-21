CREATE TABLE publication_nasa_crossover_link (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    nasa_test_id TEXT NOT NULL REFERENCES nasa_test,
    archive_case_source_id TEXT NOT NULL REFERENCES literature_source,
    archive_procedure_number INTEGER NOT NULL CHECK(archive_procedure_number > 0),
    archive_locator TEXT NOT NULL,
    journal_locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    UNIQUE(source_id,nasa_test_id),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;

CREATE TABLE literature_case_report_timing (
    source_id TEXT NOT NULL,
    published_case_number INTEGER NOT NULL,
    first_report_min INTEGER NOT NULL CHECK(first_report_min >= 0),
    noticed_lower_min INTEGER NOT NULL CHECK(noticed_lower_min >= 0),
    noticed_upper_min INTEGER NOT NULL CHECK(noticed_upper_min BETWEEN noticed_lower_min AND first_report_min),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,published_case_number),
    FOREIGN KEY(source_id,published_case_number) REFERENCES literature_case_table_i
) STRICT;
