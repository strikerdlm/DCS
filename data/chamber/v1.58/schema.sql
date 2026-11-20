CREATE TABLE publication_repeat_descent (
    source_id TEXT NOT NULL REFERENCES publication_source,
    source_table TEXT NOT NULL CHECK(source_table IN ('I','II')),
    target_altitude_ft INTEGER NOT NULL CHECK(target_altitude_ft > 0),
    ascent_min INTEGER NOT NULL CHECK(ascent_min > 0),
    planned_dwell_min INTEGER NOT NULL CHECK(planned_dwell_min > 0),
    flight_number INTEGER NOT NULL CHECK(flight_number BETWEEN 1 AND 6),
    prior_descents TEXT NOT NULL CHECK(prior_descents IN ('all','0','1','2','3','4','5')),
    exposure_count INTEGER NOT NULL CHECK(exposure_count > 0),
    reported_group_pct REAL NOT NULL CHECK(reported_group_pct BETWEEN 0 AND 100),
    descent_count INTEGER NOT NULL CHECK(descent_count BETWEEN 0 AND exposure_count),
    reported_descent_pct REAL NOT NULL CHECK(reported_descent_pct BETWEEN 0 AND 100),
    printed_page INTEGER NOT NULL CHECK(printed_page IN (160,161)),
    analysis_role TEXT NOT NULL DEFAULT 'overlap_hold' CHECK(analysis_role='overlap_hold'),
    PRIMARY KEY(source_id,source_table,flight_number,prior_descents),
    CHECK(prior_descents='all' OR CAST(prior_descents AS INTEGER) < flight_number)
) STRICT;

CREATE TABLE publication_repeat_classification (
    source_id TEXT NOT NULL REFERENCES publication_source,
    first_result TEXT NOT NULL CHECK(first_result IN ('pass','doubtful','fail')),
    second_result TEXT NOT NULL CHECK(second_result IN ('all','pass','doubtful','fail')),
    third_position INTEGER NOT NULL CHECK(third_position BETWEEN 0 AND 3),
    third_printed_label TEXT CHECK(third_printed_label IN ('P','D','F')),
    reported_count INTEGER NOT NULL CHECK(reported_count >= 0),
    analysis_role TEXT NOT NULL DEFAULT 'overlap_hold' CHECK(analysis_role='overlap_hold'),
    PRIMARY KEY(source_id,first_result,second_result,third_position),
    CHECK((third_position=0) = (third_printed_label IS NULL)),
    CHECK(second_result!='all' OR third_position=0)
) STRICT;

CREATE TABLE publication_archival_cohort_size (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    measure TEXT NOT NULL,
    reported_value INTEGER NOT NULL CHECK(reported_value > 0),
    value_basis TEXT NOT NULL CHECK(value_basis IN ('exact','strict_lower_bound')),
    unit TEXT NOT NULL CHECK(unit IN ('person','person_exposure')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    analysis_role TEXT NOT NULL DEFAULT 'overlap_hold' CHECK(analysis_role='overlap_hold'),
    PRIMARY KEY(source_id,stratum,measure)
) STRICT;
