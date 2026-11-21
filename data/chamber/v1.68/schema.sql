-- Only the affected crew described in Lewis Tables II and III are present.
CREATE TABLE publication_lewis_case_profile (
    source_id TEXT NOT NULL REFERENCES publication_source,
    source_stratum TEXT NOT NULL CHECK(source_stratum IN ('bends_only','neurological')),
    published_row INTEGER NOT NULL CHECK(published_row > 0),
    aircraft_type TEXT NOT NULL,
    crew_position TEXT NOT NULL,
    age_years INTEGER NOT NULL CHECK(age_years > 0),
    height_in INTEGER NOT NULL CHECK(height_in > 0),
    weight_lb INTEGER NOT NULL CHECK(weight_lb > 0),
    max_allowable_weight_lb INTEGER NOT NULL CHECK(max_allowable_weight_lb > 0),
    cabin_altitude_ft INTEGER NOT NULL CHECK(cabin_altitude_ft > 0),
    time_at_altitude_before_onset_min INTEGER NOT NULL CHECK(time_at_altitude_before_onset_min > 0),
    reported_phenotype TEXT NOT NULL,
    printed_page INTEGER NOT NULL CHECK(printed_page > 0),
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,source_stratum,published_row)
) STRICT;
