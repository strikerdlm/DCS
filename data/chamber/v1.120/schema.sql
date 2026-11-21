CREATE TABLE publication_doppler_diagnostic_threshold (
    source_id TEXT NOT NULL REFERENCES publication_source,
    minimum_grade INTEGER NOT NULL CHECK(minimum_grade BETWEEN 1 AND 4),
    sensitivity_percent INTEGER NOT NULL CHECK(sensitivity_percent BETWEEN 0 AND 100),
    specificity_percent INTEGER NOT NULL CHECK(specificity_percent BETWEEN 0 AND 100),
    false_positive_percent INTEGER NOT NULL CHECK(false_positive_percent BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id, minimum_grade),
    CHECK(specificity_percent + false_positive_percent = 100)
) STRICT;
