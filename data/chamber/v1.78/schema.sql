CREATE TABLE publication_iaf_adcs_case (
    source_id TEXT NOT NULL,
    case_number INTEGER NOT NULL CHECK(case_number > 0),
    exposure_stratum TEXT NOT NULL CHECK(exposure_stratum IN ('chamber','flight')),
    reported_age_years INTEGER NOT NULL CHECK(reported_age_years > 0),
    reported_sex TEXT NOT NULL CHECK(reported_sex IN ('female','male')),
    reported_role TEXT NOT NULL,
    reported_altitude_ft INTEGER NOT NULL CHECK(reported_altitude_ft > 0),
    reported_altitude_km REAL NOT NULL CHECK(reported_altitude_km > 0),
    symptoms TEXT NOT NULL,
    reported_classification TEXT NOT NULL,
    reported_treatment TEXT CHECK(reported_treatment IN ('USNTT5','USNTT6','100% oxygen')),
    reported_tail_treatments INTEGER CHECK(reported_tail_treatments >= 0),
    locator TEXT NOT NULL,
    CHECK((reported_tail_treatments IS NOT NULL) = COALESCE(reported_treatment IN ('USNTT5','USNTT6'),0)),
    PRIMARY KEY(source_id,case_number),
    FOREIGN KEY(source_id,exposure_stratum) REFERENCES aviation_count(source_id,stratum)
) STRICT;
