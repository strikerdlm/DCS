CREATE TABLE publication_selection_course_role_year (
    source_id TEXT NOT NULL REFERENCES publication_source,
    course_year INTEGER NOT NULL CHECK(course_year > 0),
    role TEXT NOT NULL CHECK(role IN ('pilots','observers','r_aircrew','civilians','others')),
    category_a INTEGER NOT NULL CHECK(category_a >= 0),
    category_b INTEGER NOT NULL CHECK(category_b >= 0),
    category_c INTEGER NOT NULL CHECK(category_c >= 0),
    printed_dash_categories TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,course_year,role),
    CHECK((category_a=0)=(instr(printed_dash_categories,'A')>0)),
    CHECK((category_b=0)=(instr(printed_dash_categories,'B')>0)),
    CHECK((category_c=0)=(instr(printed_dash_categories,'C')>0))
) STRICT;

CREATE TABLE publication_selection_course_attendance (
    source_id TEXT NOT NULL REFERENCES publication_source,
    courses_per_person INTEGER NOT NULL CHECK(courses_per_person > 0),
    people INTEGER NOT NULL CHECK(people > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,courses_per_person)
) STRICT;

CREATE TABLE publication_selection_course_protocol (
    source_id TEXT PRIMARY KEY REFERENCES publication_source,
    peak_altitude_ft INTEGER NOT NULL CHECK(peak_altitude_ft > 0),
    ascent_within_min INTEGER NOT NULL CHECK(ascent_within_min > 0),
    planned_dwell_per_run_min INTEGER NOT NULL CHECK(planned_dwell_per_run_min > 0),
    planned_consecutive_runs INTEGER NOT NULL CHECK(planned_consecutive_runs > 0),
    preoxygenation_min INTEGER NOT NULL CHECK(preoxygenation_min >= 0),
    oxygen_delivery_as_reported TEXT NOT NULL,
    category_a_definition TEXT NOT NULL,
    category_b_definition TEXT NOT NULL,
    category_c_definition TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL
) STRICT;
