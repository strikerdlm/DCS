CREATE TABLE publication_radiograph_scope (
    source_id TEXT NOT NULL REFERENCES publication_source,
    scope_id TEXT NOT NULL,
    parent_scope_id TEXT,
    film_count INTEGER CHECK(film_count > 0),
    participant_count INTEGER CHECK(participant_count > 0),
    reported_total_area_sq_in REAL CHECK(reported_total_area_sq_in >= 0),
    reported_mean_area_sq_in REAL CHECK(reported_mean_area_sq_in >= 0),
    analysis_role TEXT NOT NULL CHECK(analysis_role IN ('overlap_hold','denominator_conflict')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,scope_id),
    FOREIGN KEY(source_id,parent_scope_id) REFERENCES publication_radiograph_scope(source_id,scope_id),
    CHECK(parent_scope_id IS NULL OR parent_scope_id <> scope_id),
    CHECK(film_count IS NOT NULL OR participant_count IS NOT NULL),
    CHECK((reported_total_area_sq_in IS NULL) = (reported_mean_area_sq_in IS NULL))
) STRICT;

CREATE TABLE publication_radiograph_bends_cross_tab (
    source_id TEXT NOT NULL,
    scope_id TEXT NOT NULL,
    source_table TEXT NOT NULL,
    classification TEXT NOT NULL,
    condition TEXT NOT NULL,
    bends_present_films INTEGER NOT NULL CHECK(bends_present_films >= 0),
    bends_absent_films INTEGER NOT NULL CHECK(bends_absent_films >= 0),
    all_films INTEGER NOT NULL CHECK(all_films > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,source_table,condition),
    FOREIGN KEY(source_id,scope_id) REFERENCES publication_radiograph_scope(source_id,scope_id),
    CHECK(all_films = bends_present_films + bends_absent_films)
) STRICT;

CREATE TABLE publication_radiograph_planimetry_cell (
    source_id TEXT NOT NULL,
    scope_id TEXT NOT NULL,
    printed_block INTEGER NOT NULL CHECK(printed_block > 0),
    printed_row INTEGER NOT NULL CHECK(printed_row > 0),
    area_as_printed TEXT NOT NULL,
    area_sq_in REAL CHECK(area_sq_in >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,scope_id,printed_block,printed_row),
    FOREIGN KEY(source_id,scope_id) REFERENCES publication_radiograph_scope(source_id,scope_id)
) STRICT;

CREATE TABLE publication_radiograph_cardiac_shadow (
    source_id TEXT NOT NULL,
    scope_id TEXT NOT NULL,
    participant_ordinal INTEGER NOT NULL CHECK(participant_ordinal > 0),
    film_count INTEGER NOT NULL CHECK(film_count > 0),
    diameter_lower_cm REAL NOT NULL CHECK(diameter_lower_cm > 0),
    diameter_upper_cm REAL NOT NULL CHECK(diameter_upper_cm >= diameter_lower_cm),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,scope_id,participant_ordinal),
    FOREIGN KEY(source_id,scope_id) REFERENCES publication_radiograph_scope(source_id,scope_id)
) STRICT;
