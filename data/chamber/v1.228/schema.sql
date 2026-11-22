CREATE TABLE publication_usafsam_repository_snapshot (
    source_id TEXT PRIMARY KEY REFERENCES publication_source,
    repository_id TEXT NOT NULL,
    report_year INTEGER NOT NULL,
    snapshot_as_of TEXT,
    reported_people INTEGER CHECK(reported_people > 0),
    people_count_basis TEXT CHECK(people_count_basis IN ('exact','more_than')),
    reported_exposures INTEGER NOT NULL CHECK(reported_exposures > 0 AND reported_exposures >= reported_people),
    exposure_count_basis TEXT NOT NULL CHECK(exposure_count_basis IN ('exact','approximate','more_than')),
    locator TEXT NOT NULL,
    UNIQUE(repository_id,report_year),
    CHECK((reported_people IS NULL) = (people_count_basis IS NULL))
) STRICT;

CREATE TABLE publication_usafsam_repeated_vge (
    source_id TEXT NOT NULL REFERENCES publication_source,
    subject_number INTEGER NOT NULL CHECK(subject_number > 0),
    bubble_pattern_group TEXT NOT NULL CHECK(bubble_pattern_group IN ('A','B','C','D')),
    study_day INTEGER NOT NULL CHECK(study_day BETWEEN 1 AND 3),
    peak_grade INTEGER CHECK(peak_grade BETWEEN 0 AND 4),
    peak_site TEXT CHECK(peak_site IN ('RL','LL','RA','LA','AL','BL','BA')),
    exposure_status TEXT NOT NULL CHECK(exposure_status IN ('observed','withdrawn_after_day_one_dcs')),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,subject_number,study_day),
    CHECK((peak_grade IS NOT NULL) = (exposure_status='observed')),
    CHECK((peak_site IS NOT NULL) = coalesce(peak_grade > 0,0))
) STRICT;

CREATE VIEW publication_usafsam_repeated_vge_recurrence AS
WITH complete_subjects AS (
    SELECT source_id, subject_number, sum(peak_grade > 0) AS positive_days
    FROM publication_usafsam_repeated_vge
    WHERE exposure_status='observed'
    GROUP BY source_id, subject_number HAVING count(*)=3
)
SELECT source_id, 'all_three_day_completers' AS risk_set, count(*) AS denominator,
       sum(positive_days >= 2) AS positive_on_at_least_two_days,
       sum(positive_days = 3) AS positive_on_all_three_days
FROM complete_subjects GROUP BY source_id
UNION ALL
SELECT source_id, 'three_day_completers_with_vge', count(*),
       sum(positive_days >= 2), sum(positive_days = 3)
FROM complete_subjects WHERE positive_days>0 GROUP BY source_id;

CREATE TABLE publication_usafsam_threshold_vge (
    source_id TEXT NOT NULL REFERENCES publication_source,
    subject_row INTEGER NOT NULL CHECK(subject_row > 0),
    lower_pressure_psia REAL NOT NULL CHECK(lower_pressure_psia > 0),
    upper_pressure_psia REAL NOT NULL CHECK(upper_pressure_psia >= lower_pressure_psia),
    peak_grade INTEGER CHECK(peak_grade BETWEEN 0 AND 4),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,subject_row,lower_pressure_psia,upper_pressure_psia)
) STRICT;

CREATE TABLE publication_usafsam_threshold_symptom (
    source_id TEXT NOT NULL REFERENCES publication_source,
    symptom_row INTEGER NOT NULL CHECK(symptom_row > 0),
    subject_row INTEGER NOT NULL,
    pressure_psia REAL NOT NULL,
    lower_pressure_psia REAL NOT NULL,
    upper_pressure_psia REAL NOT NULL,
    symptom_as_reported TEXT NOT NULL,
    site_as_reported TEXT NOT NULL,
    peak_grade INTEGER NOT NULL CHECK(peak_grade BETWEEN 0 AND 4),
    dcs_class_as_reported TEXT,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,symptom_row),
    FOREIGN KEY(source_id,subject_row,lower_pressure_psia,upper_pressure_psia)
        REFERENCES publication_usafsam_threshold_vge(source_id,subject_row,lower_pressure_psia,upper_pressure_psia),
    CHECK(pressure_psia BETWEEN lower_pressure_psia AND upper_pressure_psia)
) STRICT;
