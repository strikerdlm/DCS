CREATE TABLE publication_chamber_fatality_crosswalk (
    source_id TEXT NOT NULL REFERENCES publication_source,
    source_case_label TEXT NOT NULL,
    catalog_source_id TEXT NOT NULL,
    catalog_case_number INTEGER NOT NULL,
    link_status TEXT NOT NULL CHECK(link_status IN ('confirmed','likely')),
    source_age_years INTEGER CHECK(source_age_years > 0),
    source_altitude_ft INTEGER NOT NULL CHECK(source_altitude_ft > 0),
    source_onset_min INTEGER NOT NULL CHECK(source_onset_min >= 0),
    source_death_hours REAL NOT NULL CHECK(source_death_hours > 0),
    source_death_clock TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    comparison_note TEXT NOT NULL,
    PRIMARY KEY(source_id,source_case_label),
    FOREIGN KEY(catalog_source_id,catalog_case_number)
        REFERENCES publication_fryer69_chamber_fatality(source_id,case_number)
) STRICT;
