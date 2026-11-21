CREATE TABLE publication_chamber_case_milestone (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    milestone TEXT NOT NULL,
    elapsed REAL CHECK(elapsed >= 0),
    elapsed_unit TEXT CHECK(elapsed_unit IN ('minutes','hours','days','months','years')),
    elapsed_reference TEXT,
    elapsed_qualifier TEXT CHECK(elapsed_qualifier IN ('reported','approximate')),
    assessment_date TEXT,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint,milestone),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation,
    CHECK((elapsed IS NULL) = (elapsed_unit IS NULL)),
    CHECK((elapsed IS NULL) = (elapsed_reference IS NULL)),
    CHECK((elapsed IS NULL) = (elapsed_qualifier IS NULL))
) STRICT;

CREATE TABLE publication_case_anam (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    milestone TEXT NOT NULL,
    subtest TEXT NOT NULL,
    normative_category TEXT NOT NULL CHECK(normative_category IN ('average_or_above','below_average','clearly_below')),
    baseline_comparison_as_printed REAL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint,milestone,subtest),
    FOREIGN KEY(source_id,stratum,endpoint,milestone) REFERENCES publication_chamber_case_milestone
) STRICT;
