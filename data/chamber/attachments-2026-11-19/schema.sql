CREATE TABLE attachment_source (
    source_id TEXT PRIMARY KEY,
    citation TEXT NOT NULL,
    public_url TEXT NOT NULL,
    filename TEXT NOT NULL,
    sha256 TEXT UNIQUE NOT NULL CHECK(length(sha256)=64),
    pdf_pages INTEGER NOT NULL CHECK(pdf_pages>0),
    parsed_pages TEXT NOT NULL,
    locator TEXT NOT NULL,
    disposition TEXT NOT NULL
) STRICT;

CREATE TABLE attachment_observation (
    source_id TEXT NOT NULL REFERENCES attachment_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role IN (
        'descriptive','case_margin','source_total','overlap_hold','published_estimate','modeled'
    )),
    events INTEGER CHECK(events>=0),
    denominator INTEGER CHECK(denominator>0),
    denominator_unit TEXT,
    value REAL,
    value_unit TEXT,
    lower_bound REAL,
    upper_bound REAL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    CHECK((events IS NULL) != (value IS NULL)),
    CHECK((denominator IS NULL)=(denominator_unit IS NULL)),
    CHECK((value IS NULL)=(value_unit IS NULL)),
    CHECK((lower_bound IS NULL)=(upper_bound IS NULL)),
    CHECK(lower_bound<=value AND value<=upper_bound),
    CHECK(events<=denominator),
    CHECK(analysis_role!='modeled' OR events IS NULL)
) STRICT;

CREATE TABLE attachment_overlap (
    source_id TEXT NOT NULL REFERENCES attachment_source,
    scope TEXT NOT NULL,
    prior_source TEXT NOT NULL,
    relationship TEXT NOT NULL CHECK(relationship IN (
        'exact_file','same_study','reprinted_rows','alternate_counts','overlapping_cohort',
        'candidate_already_logged','secondary_reference','calibration_reference'
    )),
    disposition TEXT NOT NULL,
    PRIMARY KEY(source_id,scope,prior_source)
) STRICT;

CREATE TABLE attachment_nasa_test (
    source_id TEXT NOT NULL REFERENCES attachment_source,
    test_id TEXT NOT NULL REFERENCES nasa_test,
    printed_test TEXT NOT NULL,
    conditions TEXT NOT NULL,
    mean_age_years REAL NOT NULL CHECK(mean_age_years>0),
    type_ii_marked_cases INTEGER CHECK(type_ii_marked_cases BETWEEN 1 AND 2),
    relationship TEXT NOT NULL CHECK(relationship IN ('reprint','alternate_counts')),
    alternate_male INTEGER CHECK(alternate_male>=0),
    alternate_female INTEGER CHECK(alternate_female>=0),
    alternate_dcs INTEGER CHECK(alternate_dcs>=0 AND alternate_dcs<=alternate_male+alternate_female),
    alternate_any_vge INTEGER CHECK(alternate_any_vge>=0 AND alternate_any_vge<=alternate_male+alternate_female),
    alternate_grade_iv INTEGER CHECK(alternate_grade_iv>=0 AND alternate_grade_iv<=alternate_any_vge),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,test_id),
    CHECK((relationship='alternate_counts')=(alternate_male IS NOT NULL)),
    CHECK((alternate_male IS NULL)=(alternate_female IS NULL)),
    CHECK((alternate_male IS NULL)=(alternate_dcs IS NULL)),
    CHECK((alternate_male IS NULL)=(alternate_any_vge IS NULL)),
    CHECK((alternate_male IS NULL)=(alternate_grade_iv IS NULL))
) STRICT;

CREATE VIEW attachment_nasa_count_comparison AS
    SELECT a.test_id, relationship, alternate_male+alternate_female AS report_total,
           n.dcs_denominator AS f1_total, alternate_dcs AS report_dcs, dcs_cases AS f1_dcs,
           alternate_any_vge AS report_vge, any_grade_vge_cases AS f1_vge,
           alternate_grade_iv AS report_grade_iv, grade_iv_vge_cases AS f1_grade_iv
    FROM attachment_nasa_test a JOIN nasa_test n USING(test_id)
    WHERE relationship='alternate_counts';

CREATE TABLE attachment_u2_flight (
    source_id TEXT NOT NULL REFERENCES attachment_source,
    pilot_series TEXT NOT NULL,
    flight_number INTEGER NOT NULL CHECK(flight_number BETWEEN 1 AND 122),
    flight_type TEXT NOT NULL,
    high_altitude_minutes INTEGER NOT NULL CHECK(high_altitude_minutes>0),
    prebreathe_exercise_min INTEGER NOT NULL CHECK(prebreathe_exercise_min>=0),
    prebreathe_rest_min INTEGER NOT NULL CHECK(prebreathe_rest_min>=0),
    exercise_equipment TEXT,
    symptom_time_reported_min TEXT,
    symptom_summary TEXT,
    disposition TEXT,
    source_footnote TEXT,
    outcome_documentation TEXT NOT NULL CHECK(outcome_documentation IN (
        'dcs_abort','symptom_report','no_symptom_entry'
    )),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,pilot_series,flight_number),
    CHECK((prebreathe_exercise_min=0)=(exercise_equipment IS NULL)),
    CHECK((outcome_documentation='no_symptom_entry')=(symptom_summary IS NULL))
) STRICT;
