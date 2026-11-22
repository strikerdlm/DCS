CREATE TABLE publication_cmb_timing_stratum (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL CHECK(stratum IN ('early-cmb-detection','late-cmb-detection')),
    people INTEGER NOT NULL CHECK(people > 0),
    age_mean_years REAL NOT NULL,
    age_sd_years REAL NOT NULL,
    bmi_mean REAL NOT NULL,
    bmi_sd REAL NOT NULL,
    activity_score_mean REAL NOT NULL,
    activity_score_sd REAL NOT NULL,
    initial_spencer_grade_mean REAL NOT NULL,
    initial_spencer_grade_sd REAL NOT NULL,
    cmb_duration_mean_min REAL NOT NULL,
    cmb_duration_sd_min REAL NOT NULL,
    men INTEGER NOT NULL CHECK(men >= 0),
    women INTEGER NOT NULL CHECK(women >= 0),
    at_9144_m_as_printed INTEGER NOT NULL CHECK(at_9144_m_as_printed >= 0),
    at_6400_m_as_printed INTEGER NOT NULL CHECK(at_6400_m_as_printed >= 0),
    prebreathe_0_min INTEGER NOT NULL CHECK(prebreathe_0_min >= 0),
    prebreathe_210_min INTEGER NOT NULL CHECK(prebreathe_210_min >= 0),
    prebreathe_240_min INTEGER NOT NULL CHECK(prebreathe_240_min >= 0),
    prebreathe_360_min INTEGER NOT NULL CHECK(prebreathe_360_min >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK(men+women=people),
    CHECK(at_9144_m_as_printed+at_6400_m_as_printed=people),
    CHECK(prebreathe_0_min+prebreathe_210_min+prebreathe_240_min+prebreathe_360_min=people),
    PRIMARY KEY(source_id,stratum)
) STRICT;

CREATE TABLE publication_cmb_timing_reconciliation (
    source_id TEXT NOT NULL REFERENCES publication_source,
    annual_report_source_id TEXT NOT NULL REFERENCES publication_source,
    symptomatic_header_as_printed INTEGER NOT NULL,
    asymptomatic_header_as_printed INTEGER NOT NULL,
    symptomatic_from_verified_cells INTEGER NOT NULL,
    asymptomatic_from_verified_cells INTEGER NOT NULL,
    annual_report_locator TEXT NOT NULL,
    journal_locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,annual_report_source_id)
) STRICT;

CREATE TABLE publication_cmb_after_dcs_delay (
    source_id TEXT NOT NULL REFERENCES publication_source,
    time_from_symptoms_to_first_cmb_min INTEGER NOT NULL CHECK(time_from_symptoms_to_first_cmb_min > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,time_from_symptoms_to_first_cmb_min)
) STRICT;
