CREATE TABLE publication_aviation_referral_review (
    source_id TEXT NOT NULL REFERENCES publication_source,
    case_number INTEGER NOT NULL CHECK(case_number > 0),
    dcs_votes INTEGER NOT NULL CHECK(dcs_votes >= 0),
    reviewers INTEGER NOT NULL CHECK(reviewers > 0 AND dcs_votes <= reviewers),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,case_number)
) STRICT;

CREATE TABLE publication_aviation_referral_case (
    source_id TEXT NOT NULL,
    case_number INTEGER NOT NULL,
    age_years INTEGER NOT NULL CHECK(age_years > 0),
    sex_as_reported TEXT NOT NULL,
    pressure_change_atm_as_printed REAL NOT NULL CHECK(pressure_change_atm_as_printed > 0),
    symptom_summary TEXT NOT NULL,
    onset_as_reported TEXT NOT NULL,
    exam_summary TEXT NOT NULL,
    treatment_as_reported TEXT NOT NULL,
    linked_stratum TEXT,
    linked_endpoint TEXT,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,case_number),
    FOREIGN KEY(source_id,case_number) REFERENCES publication_aviation_referral_review,
    FOREIGN KEY(source_id,linked_stratum,linked_endpoint) REFERENCES publication_observation,
    CHECK((linked_stratum IS NULL) = (linked_endpoint IS NULL))
) STRICT;

CREATE TABLE publication_aviation_referral_stage (
    source_id TEXT NOT NULL,
    case_number INTEGER NOT NULL,
    stage_number INTEGER NOT NULL CHECK(stage_number > 0),
    setting_as_reported TEXT NOT NULL,
    timing_as_reported TEXT,
    aircraft_altitude_column_ft INTEGER NOT NULL,
    cabin_altitude_column_ft INTEGER NOT NULL,
    decompression_value INTEGER,
    decompression_unit TEXT CHECK(decompression_unit IN ('ft','fsw')),
    decompression_missing_reason TEXT CHECK(decompression_missing_reason IN ('unknown','not_applicable_as_printed')),
    exposures_reported INTEGER CHECK(exposures_reported > 0),
    exposures_relation TEXT CHECK(exposures_relation IN ('=','>')),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,case_number,stage_number),
    FOREIGN KEY(source_id,case_number) REFERENCES publication_aviation_referral_case,
    CHECK((decompression_value IS NULL) = (decompression_unit IS NULL)),
    CHECK((decompression_value IS NULL) = (decompression_missing_reason IS NOT NULL)),
    CHECK((exposures_reported IS NULL) = (exposures_relation IS NULL))
) STRICT;

CREATE TABLE publication_aviation_referral_comparison (
    source_id TEXT NOT NULL REFERENCES publication_source,
    criterion_as_reported TEXT NOT NULL,
    reviewer_dcs_count INTEGER NOT NULL CHECK(reviewer_dcs_count >= 0),
    reviewer_dcs_total INTEGER NOT NULL CHECK(reviewer_dcs_total >= reviewer_dcs_count AND reviewer_dcs_total > 0),
    alternative_count INTEGER NOT NULL CHECK(alternative_count >= 0),
    alternative_total INTEGER NOT NULL CHECK(alternative_total >= alternative_count AND alternative_total > 0),
    p_value_relation TEXT NOT NULL CHECK(p_value_relation IN ('=','<')),
    p_value_as_reported REAL NOT NULL CHECK(p_value_as_reported BETWEEN 0 AND 1),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,criterion_as_reported)
) STRICT;
