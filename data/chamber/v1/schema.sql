PRAGMA foreign_keys = ON;
CREATE TABLE cohort (
    cohort_id TEXT PRIMARY KEY,
    partition TEXT NOT NULL CHECK (partition IN ('development','separate_study','overlap_hold','descriptive','locked_external','endpoint_only','methods_only')),
    population TEXT NOT NULL, ascertainment TEXT NOT NULL, window TEXT NOT NULL
) STRICT;
CREATE TABLE source (
    source_id TEXT PRIMARY KEY, cohort_id TEXT NOT NULL REFERENCES cohort,
    title TEXT NOT NULL, edition TEXT NOT NULL, url TEXT, cache_file TEXT NOT NULL,
    sha256 TEXT NOT NULL CHECK (length(sha256)=64), locator TEXT NOT NULL,
    extraction TEXT NOT NULL, access_note TEXT NOT NULL
) STRICT;
CREATE TABLE source_overlap (
    source_a TEXT REFERENCES source, source_b TEXT REFERENCES source,
    relationship TEXT NOT NULL, evidence TEXT NOT NULL,
    PRIMARY KEY(source_a,source_b), CHECK(source_a<>source_b)
) STRICT;
CREATE TABLE endpoint (endpoint TEXT PRIMARY KEY, definition TEXT NOT NULL) STRICT;
CREATE TABLE source_statistic (
    source_id TEXT REFERENCES source, locator TEXT NOT NULL, quantity TEXT NOT NULL,
    value REAL NOT NULL, unit TEXT NOT NULL, interpretation TEXT NOT NULL,
    PRIMARY KEY (source_id,locator,quantity)
) STRICT;
CREATE TABLE nasa_test (
    test_id TEXT PRIMARY KEY, family TEXT NOT NULL, pressure_psia REAL NOT NULL,
    duration_hours REAL NOT NULL, male_exposures INTEGER NOT NULL, female_exposures INTEGER NOT NULL,
    dcs_cases INTEGER NOT NULL, dcs_denominator INTEGER NOT NULL,
    mean_tr360 REAL NOT NULL, f1_no_ambulation_mark INTEGER NOT NULL,
    table2_ambulatory INTEGER NOT NULL, any_grade_vge_cases INTEGER, grade_iv_vge_cases INTEGER,
    source_id TEXT NOT NULL DEFAULT 'nasa19' REFERENCES source,
    CHECK(dcs_denominator BETWEEN dcs_cases AND male_exposures+female_exposures),
    CHECK(dcs_cases>=0 AND dcs_denominator>0),
    CHECK((any_grade_vge_cases IS NULL)=(grade_iv_vge_cases IS NULL)),
    CHECK(grade_iv_vge_cases BETWEEN 0 AND any_grade_vge_cases)
) STRICT;
CREATE TABLE afrl_test (
    test_id INTEGER PRIMARY KEY, exposures INTEGER NOT NULL, source_sex TEXT NOT NULL CHECK(source_sex IN ('F','M')),
    pb_including_ascent_min REAL NOT NULL, pressure_mmhg REAL NOT NULL,
    assigned_max_vo2_ml_kg_min REAL NOT NULL, dcs_cases INTEGER NOT NULL,
    printed_incidence REAL NOT NULL, source_id TEXT NOT NULL DEFAULT 'afrl13' REFERENCES source,
    CHECK(exposures>0 AND dcs_cases BETWEEN 0 AND exposures)
) STRICT;
CREATE TABLE a1309_profile (
    page TEXT NOT NULL, program TEXT NOT NULL, profile TEXT PRIMARY KEY, source_schedule TEXT NOT NULL,
    exposures INTEGER NOT NULL CHECK(exposures>0), printed_events TEXT NOT NULL,
    exact_cases INTEGER CHECK(exact_cases BETWEEN 0 AND exposures),
    source_id TEXT NOT NULL DEFAULT 'gerth18' REFERENCES source,
    CHECK((exact_cases IS NULL AND instr(printed_events,'.')>0) OR
          (exact_cases IS NOT NULL AND CAST(exact_cases AS TEXT)=printed_events))
) STRICT;
CREATE TABLE a1309_nasa_overlap (
    profile TEXT PRIMARY KEY REFERENCES a1309_profile, test_id TEXT NOT NULL REFERENCES nasa_test,
    agreement TEXT NOT NULL
) STRICT;
CREATE TABLE air_break_arm (
    arm TEXT PRIMARY KEY, source_group_size INTEGER NOT NULL CHECK(source_group_size>0),
    pre_break_o2_min REAL, air_break_min REAL NOT NULL, post_break_o2_min REAL,
    uninterrupted_o2_min REAL, planned_plateau_h REAL, posture TEXT NOT NULL,
    detail TEXT NOT NULL, source_id TEXT NOT NULL DEFAULT 'pilmanis10' REFERENCES source,
    UNIQUE(arm,source_group_size)
) STRICT;
CREATE TABLE air_break_estimate (
    arm TEXT NOT NULL, source_group_size INTEGER NOT NULL, endpoint TEXT NOT NULL REFERENCES endpoint,
    horizon_h REAL NOT NULL CHECK(horizon_h>0), km_percent REAL NOT NULL CHECK(km_percent BETWEEN 0 AND 100),
    PRIMARY KEY(arm,endpoint,horizon_h), FOREIGN KEY(arm,source_group_size) REFERENCES air_break_arm(arm,source_group_size)
) STRICT;
CREATE TABLE aviation_count (
    source_id TEXT REFERENCES source, stratum TEXT NOT NULL, use_class TEXT NOT NULL
      CHECK(use_class IN ('primary','overlapping_margin','outside_chamber')),
    period TEXT NOT NULL, role TEXT NOT NULL, profile TEXT NOT NULL, endpoint TEXT NOT NULL REFERENCES endpoint,
    denominator INTEGER, cases INTEGER NOT NULL CHECK(cases>=0), denominator_unit TEXT NOT NULL,
    altitude_ft REAL, prebreathe_min REAL, plateau_min REAL, locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum), CHECK(denominator IS NULL OR (denominator>0 AND cases<=denominator)),
    CHECK((denominator IS NULL)=(denominator_unit='unreported'))
) STRICT;
CREATE TABLE adf_exposure_margin (
    year TEXT PRIMARY KEY, profile_a INTEGER NOT NULL, profile_b INTEGER NOT NULL,
    profile_c INTEGER NOT NULL, other INTEGER NOT NULL,
    source_id TEXT NOT NULL DEFAULT 'smart04' REFERENCES source,
    FOREIGN KEY(source_id,year) REFERENCES aviation_count(source_id,stratum)
) STRICT;
CREATE TABLE vge_interval (
    id INTEGER PRIMARY KEY, age_years INTEGER NOT NULL, source_male INTEGER NOT NULL CHECK(source_male IN (0,1)),
    tr360 REAL NOT NULL, ambulatory INTEGER NOT NULL CHECK(ambulatory IN (0,1)),
    left_h REAL NOT NULL CHECK(left_h>=0), right_h REAL, censoring TEXT NOT NULL,
    source_id TEXT NOT NULL DEFAULT 'hdsd' REFERENCES source,
    CHECK((censoring='right' AND right_h IS NULL) OR
          (censoring='interval' AND right_h IS NOT NULL AND right_h>left_h))
) STRICT;
CREATE TABLE activity_summary (
    source_id TEXT REFERENCES source, task TEXT NOT NULL, n_workload INTEGER NOT NULL,
    mean_task_vo2_ml_kg_min REAL, highest_1min_vo2_ml_kg_min REAL NOT NULL,
    measurement_context TEXT NOT NULL, historical_dcs_percent REAL, PRIMARY KEY(source_id,task)
) STRICT;
CREATE TABLE source_finding (
    finding_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source,
    locator TEXT NOT NULL, finding TEXT NOT NULL, action TEXT NOT NULL
) STRICT;
CREATE TABLE frozen_input (path TEXT PRIMARY KEY, sha256 TEXT NOT NULL) STRICT;
CREATE TABLE external_lock (
    source_id TEXT NOT NULL, stratum TEXT NOT NULL, population_scope TEXT NOT NULL,
    window_code TEXT NOT NULL, single_protocol INTEGER NOT NULL CHECK(single_protocol IN (0,1)),
    body_pressure_psia REAL, mean_tr360 REAL, ambulatory INTEGER CHECK(ambulatory IN (0,1)),
    PRIMARY KEY(source_id,stratum), FOREIGN KEY(source_id,stratum) REFERENCES aviation_count
) STRICT;
CREATE VIEW development_counts AS
    SELECT * FROM nasa_test WHERE duration_hours BETWEEN 2 AND 6
       AND table2_ambulatory=1-f1_no_ambulation_mark;
CREATE VIEW locked_external AS
    SELECT a.*,c.population,c.ascertainment,c.window,l.population_scope,l.window_code,
           l.single_protocol,l.body_pressure_psia,l.mean_tr360,l.ambulatory
    FROM external_lock l JOIN aviation_count a USING(source_id,stratum)
    JOIN source s USING(source_id) JOIN cohort c USING(cohort_id)
    WHERE c.partition='locked_external' AND a.use_class='primary';
