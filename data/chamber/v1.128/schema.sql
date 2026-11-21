CREATE TABLE publication_powell_doppler_margin (
    source_id TEXT NOT NULL REFERENCES publication_source,
    table_row INTEGER NOT NULL CHECK(table_row > 0),
    modeled_tissue_ratio REAL NOT NULL CHECK(modeled_tissue_ratio > 0),
    any_vge_percent_as_printed INTEGER NOT NULL CHECK(any_vge_percent_as_printed BETWEEN 0 AND 100),
    grade_iii_iv_fraction_numerator INTEGER NOT NULL CHECK(grade_iii_iv_fraction_numerator >= 0),
    grade_iii_iv_fraction_denominator INTEGER NOT NULL CHECK(grade_iii_iv_fraction_denominator > 0),
    comparison_source_id TEXT NOT NULL REFERENCES publication_source,
    conkin_procedures TEXT NOT NULL,
    concordance TEXT NOT NULL CHECK(concordance IN ('rounded_profile_concordance','potential_combination')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,table_row),
    CHECK(grade_iii_iv_fraction_numerator <= grade_iii_iv_fraction_denominator)
) STRICT;

CREATE TABLE publication_dervay_doppler_visit (
    source_id TEXT NOT NULL REFERENCES publication_source,
    source_subject_number INTEGER NOT NULL CHECK(source_subject_number > 0),
    condition_as_reported TEXT NOT NULL CHECK(condition_as_reported IN ('A','B','C')),
    rest_before_decompression_min INTEGER NOT NULL CHECK(rest_before_decompression_min IN (0,60,120)),
    visit_order INTEGER NOT NULL CHECK(visit_order BETWEEN 1 AND 3),
    completed_crossover INTEGER NOT NULL CHECK(completed_crossover IN (0,1)),
    first_vge_detection_min INTEGER CHECK(first_vge_detection_min BETWEEN 15 AND 120 AND first_vge_detection_min % 15 = 0),
    first_spencer_grade INTEGER NOT NULL CHECK(first_spencer_grade BETWEEN 0 AND 4),
    highest_spencer_grade INTEGER NOT NULL CHECK(highest_spencer_grade BETWEEN first_spencer_grade AND 4),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,source_subject_number,condition_as_reported),
    UNIQUE(source_id,source_subject_number,visit_order),
    CHECK((first_vge_detection_min IS NULL) = (first_spencer_grade = 0)),
    CHECK((first_spencer_grade = 0) = (highest_spencer_grade = 0)),
    CHECK(completed_crossover = 1 OR visit_order = 1),
    CHECK(rest_before_decompression_min = CASE condition_as_reported WHEN 'A' THEN 120 WHEN 'B' THEN 60 ELSE 0 END)
) STRICT;
