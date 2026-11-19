CREATE TABLE publication_chamber_flight (
    source_id TEXT NOT NULL REFERENCES publication_source,
    exposure_id TEXT NOT NULL,
    investigator_code TEXT NOT NULL,
    expedition_day INTEGER NOT NULL CHECK(expedition_day > 0),
    altitude_m INTEGER NOT NULL CHECK(altitude_m > 0),
    duration_table1_min INTEGER NOT NULL CHECK(duration_table1_min > 0),
    duration_table2_footnote_min INTEGER CHECK(duration_table2_footnote_min > 0),
    prebreathe_min INTEGER CHECK(prebreathe_min >= 0),
    dcs_symptoms INTEGER NOT NULL CHECK(dcs_symptoms IN (0,1)),
    symptom_report_min INTEGER CHECK(symptom_report_min >= 0 AND symptom_report_min <= duration_table1_min),
    symptom TEXT,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((dcs_symptoms=1) = (symptom_report_min IS NOT NULL AND symptom IS NOT NULL)),
    PRIMARY KEY(source_id,exposure_id),
    UNIQUE(source_id,investigator_code,expedition_day)
) STRICT;
