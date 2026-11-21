CREATE TABLE publication_fryer69_chamber_fatality (
    source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    case_number INTEGER NOT NULL CHECK(case_number BETWEEN 1 AND 10),
    country_as_reported TEXT NOT NULL,
    case_date_as_reported TEXT,
    age_years INTEGER NOT NULL CHECK(age_years > 0),
    table_peak_altitude_ft INTEGER NOT NULL CHECK(table_peak_altitude_ft > 0),
    table_altitude_and_time TEXT NOT NULL,
    narrative_symptom_onset_min INTEGER CHECK(narrative_symptom_onset_min >= 0),
    narrative_onset_reference TEXT,
    table_time_to_death_hours_min REAL NOT NULL CHECK(table_time_to_death_hours_min > 0),
    table_time_to_death_hours_max REAL NOT NULL,
    table_lucid_interval_as_reported TEXT NOT NULL,
    report_case_summary TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,case_number),
    CHECK((narrative_symptom_onset_min IS NULL) = (narrative_onset_reference IS NULL)),
    CHECK(table_time_to_death_hours_max >= table_time_to_death_hours_min)
) STRICT;

CREATE TABLE publication_fryer69_fatality_citation (
    source_id TEXT NOT NULL,
    case_number INTEGER NOT NULL,
    cited_report_id TEXT NOT NULL,
    cited_case_label TEXT,
    linkage_basis TEXT NOT NULL CHECK(linkage_basis IN ('fryer_identifies_same_case','possible_same_case')),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,case_number,cited_report_id),
    FOREIGN KEY(source_id,case_number) REFERENCES publication_fryer69_chamber_fatality(source_id,case_number)
) STRICT;
