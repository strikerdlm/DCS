CREATE TABLE publication_nasa20_test_summary (
    test_id TEXT PRIMARY KEY REFERENCES nasa_test(test_id),
    report_source_id TEXT NOT NULL REFERENCES source(source_id),
    mean_age_years REAL NOT NULL CHECK(mean_age_years > 0),
    mean_bmi_kg_m2 REAL NOT NULL CHECK(mean_bmi_kg_m2 > 0),
    mean_bgi REAL NOT NULL CHECK(mean_bgi >= 0),
    repressurization_flag INTEGER NOT NULL CHECK(repressurization_flag IN (0, 1)),
    prescribed_prebreathe_exercise INTEGER NOT NULL CHECK(prescribed_prebreathe_exercise IN (0, 1)),
    dcs_pct_as_printed REAL NOT NULL CHECK(dcs_pct_as_printed BETWEEN 0 AND 100),
    any_vge_pct_as_printed REAL CHECK(any_vge_pct_as_printed BETWEEN 0 AND 100),
    grade_iv_vge_pct_as_printed REAL CHECK(grade_iv_vge_pct_as_printed BETWEEN 0 AND 100),
    type_ii_dcs_cases_marked INTEGER NOT NULL CHECK(type_ii_dcs_cases_marked BETWEEN 0 AND 2),
    locator TEXT NOT NULL,
    CHECK((any_vge_pct_as_printed IS NULL) = (grade_iv_vge_pct_as_printed IS NULL))
) STRICT;

-- Compare the rates with the nominal sample and the matched integer counts.
-- A tolerance of one last-place digit accommodates rounding or truncation.
-- The nominal sample does not establish exposure-level VGE monitoring.
CREATE VIEW publication_nasa20_vge_rate_disagreement AS
WITH rates AS (
    SELECT s.test_id, 'any_vge' AS endpoint, s.any_vge_pct_as_printed AS printed_pct,
           n.any_grade_vge_cases AS appendix_count, n.male_exposures + n.female_exposures AS nominal_sample,
           s.locator
    FROM publication_nasa20_test_summary s JOIN nasa_test n USING(test_id)
    UNION ALL
    SELECT s.test_id, 'grade_iv_vge', s.grade_iv_vge_pct_as_printed, n.grade_iv_vge_cases,
           n.male_exposures + n.female_exposures, s.locator
    FROM publication_nasa20_test_summary s JOIN nasa_test n USING(test_id)
)
SELECT test_id, endpoint, printed_pct, appendix_count, nominal_sample,
       100.0 * appendix_count / nominal_sample AS pct_from_nominal_sample, locator
FROM rates
WHERE round(abs(printed_pct - 100.0 * appendix_count / nominal_sample), 8) > 0.1;
