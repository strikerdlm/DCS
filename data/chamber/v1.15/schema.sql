CREATE TABLE publication_selection_course (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    grouping TEXT NOT NULL CHECK(grouping IN ('total','year','role')),
    period TEXT NOT NULL,
    course_count INTEGER NOT NULL CHECK(course_count > 0),
    category_a INTEGER NOT NULL CHECK(category_a >= 0),
    category_b INTEGER NOT NULL CHECK(category_b >= 0),
    category_c INTEGER NOT NULL CHECK(category_c >= 0),
    peak_altitude_ft INTEGER NOT NULL CHECK(peak_altitude_ft > 0),
    planned_runs_per_course INTEGER NOT NULL CHECK(planned_runs_per_course > 0),
    planned_dwell_per_run_min INTEGER NOT NULL CHECK(planned_dwell_per_run_min > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK(course_count = category_a + category_b + category_c),
    PRIMARY KEY(source_id,stratum)
) STRICT;
