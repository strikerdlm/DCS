CREATE TABLE publication_diagnostic_stratum (
    source_id TEXT NOT NULL REFERENCES publication_source,
    maximum_vge_grade_iv INTEGER NOT NULL CHECK(maximum_vge_grade_iv IN (0,1)),
    pain_persisted_through_test INTEGER NOT NULL CHECK(pain_persisted_through_test IN (0,1)),
    pain_cleared_on_repressurization INTEGER NOT NULL CHECK(pain_cleared_on_repressurization IN (0,1)),
    reports INTEGER NOT NULL CHECK(reports > 0),
    original_dcs_labels INTEGER NOT NULL CHECK(original_dcs_labels BETWEEN 0 AND reports),
    outside_ratings INTEGER NOT NULL CHECK(outside_ratings BETWEEN 4*reports AND 6*reports),
    outside_dcs_ratings INTEGER NOT NULL CHECK(outside_dcs_ratings BETWEEN 0 AND outside_ratings),
    locator TEXT NOT NULL,
    CHECK(pain_cleared_on_repressurization <= pain_persisted_through_test),
    PRIMARY KEY(source_id, maximum_vge_grade_iv, pain_persisted_through_test, pain_cleared_on_repressurization)
) STRICT;

CREATE TABLE literature_symptomatic_noncase (
    source_id TEXT NOT NULL REFERENCES literature_source,
    narrative_number INTEGER NOT NULL CHECK(narrative_number > 0),
    published_exposure_code TEXT NOT NULL,
    procedure_number INTEGER NOT NULL CHECK(procedure_number > 0),
    age_years INTEGER NOT NULL CHECK(age_years > 0),
    reported_sex TEXT NOT NULL CHECK(reported_sex IN ('female','male')),
    peak_vge_grade INTEGER NOT NULL CHECK(peak_vge_grade BETWEEN 0 AND 4),
    first_vge_min INTEGER CHECK(first_vge_min >= 0),
    first_report_min INTEGER CHECK(first_report_min >= 0),
    first_report_basis TEXT NOT NULL CHECK(first_report_basis IN (
        'test_elapsed', 'after_test', 'before_target_ascent'
    )),
    symptom_noticed_test_min INTEGER CHECK(symptom_noticed_test_min >= 0),
    locator TEXT NOT NULL,
    note TEXT,
    CHECK((peak_vge_grade = 0) = (first_vge_min IS NULL)),
    CHECK(first_report_basis <> 'test_elapsed' OR first_report_min IS NOT NULL),
    CHECK(first_report_basis <> 'before_target_ascent' OR first_report_min IS NULL),
    PRIMARY KEY(source_id, narrative_number),
    UNIQUE(source_id, published_exposure_code)
) STRICT;
