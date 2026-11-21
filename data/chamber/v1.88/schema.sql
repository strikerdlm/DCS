CREATE TABLE publication_moon48_chamber_case (
    report_id TEXT NOT NULL,
    pathology_accession INTEGER NOT NULL CHECK(pathology_accession > 0),
    fryer_source_id TEXT NOT NULL,
    fryer_case_number INTEGER NOT NULL,
    listed_altitude_ft INTEGER NOT NULL CHECK(listed_altitude_ft > 0),
    listed_time_at_altitude_min INTEGER CHECK(listed_time_at_altitude_min > 0),
    listed_time_to_death_hours INTEGER NOT NULL CHECK(listed_time_to_death_hours > 0),
    narrative_time_to_death_hours INTEGER CHECK(narrative_time_to_death_hours > 0),
    narrative_time_origin TEXT CHECK(narrative_time_origin IN ('after_chamber_test','after_hospital_admission')),
    reported_hematocrit_percent REAL CHECK(reported_hematocrit_percent > 0 AND reported_hematocrit_percent <= 100),
    reported_max_temp_f REAL CHECK(reported_max_temp_f > 0),
    clinical_and_pathology_findings TEXT NOT NULL,
    moon_locator TEXT NOT NULL,
    fryer_accession_locator TEXT NOT NULL,
    PRIMARY KEY(report_id,pathology_accession),
    UNIQUE(report_id,fryer_source_id,fryer_case_number),
    FOREIGN KEY(fryer_source_id,fryer_case_number)
        REFERENCES publication_fryer69_chamber_fatality(source_id,case_number),
    CHECK((narrative_time_to_death_hours IS NULL) = (narrative_time_origin IS NULL))
) STRICT;
