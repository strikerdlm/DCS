CREATE TABLE publication_prebreathe_series_scope (
    source_id TEXT PRIMARY KEY REFERENCES publication_source,
    exposures INTEGER NOT NULL CHECK(exposures > 0),
    exposure_unit TEXT NOT NULL CHECK(exposure_unit='person_exposure'),
    participants INTEGER CHECK(participants BETWEEN 1 AND exposures),
    altitude_ft INTEGER NOT NULL CHECK(altitude_ft > 0),
    pressure_mmhg INTEGER NOT NULL CHECK(pressure_mmhg > 0),
    minimum_prebreathe_min INTEGER NOT NULL CHECK(minimum_prebreathe_min >= 0),
    maximum_prebreathe_min INTEGER NOT NULL CHECK(maximum_prebreathe_min >= minimum_prebreathe_min),
    activity_at_altitude TEXT NOT NULL,
    endpoints_monitored TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL
) STRICT;

CREATE TABLE publication_prebreathe_chart (
    chart_id TEXT PRIMARY KEY,
    publication_source_id TEXT REFERENCES publication_source,
    attachment_source_id TEXT REFERENCES attachment_source,
    cited_series_id TEXT NOT NULL REFERENCES publication_prebreathe_series_scope,
    scope_as_reported TEXT NOT NULL,
    axis_unit_as_printed TEXT NOT NULL,
    duration_unit_supported_by_prose TEXT NOT NULL CHECK(duration_unit_supported_by_prose='hour'),
    altitude_ft INTEGER NOT NULL CHECK(altitude_ft > 0),
    target_duration_min INTEGER CHECK(target_duration_min > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((publication_source_id IS NULL)<>(attachment_source_id IS NULL))
) STRICT;

CREATE TABLE publication_prebreathe_chart_marker (
    chart_id TEXT NOT NULL REFERENCES publication_prebreathe_chart,
    axis_value REAL NOT NULL CHECK(axis_value > 0),
    prebreathe_min INTEGER NOT NULL CHECK(prebreathe_min=axis_value*60),
    plotted_percent_approx INTEGER NOT NULL CHECK(plotted_percent_approx BETWEEN 0 AND 100),
    prose_percent_approx INTEGER CHECK(prose_percent_approx BETWEEN 0 AND 100),
    note TEXT NOT NULL,
    PRIMARY KEY(chart_id,prebreathe_min)
) STRICT;

CREATE TABLE publication_prebreathe_arm_crosswalk (
    source_id TEXT NOT NULL REFERENCES publication_source,
    arm_label_as_printed TEXT NOT NULL,
    subjects_as_reported INTEGER NOT NULL CHECK(subjects_as_reported > 0),
    dcs_percent_as_reported INTEGER NOT NULL CHECK(dcs_percent_as_reported BETWEEN 0 AND 100),
    exercise_prebreathe_min INTEGER NOT NULL CHECK(exercise_prebreathe_min >= 0),
    supine_rest_prebreathe_min INTEGER NOT NULL CHECK(supine_rest_prebreathe_min > 0),
    citation_source_id TEXT,
    literature_source_id TEXT,
    related_stratum TEXT NOT NULL,
    related_endpoint TEXT NOT NULL CHECK(related_endpoint='dcs'),
    relationship TEXT NOT NULL CHECK(relationship IN ('documented_reprint','likely_overlap')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,arm_label_as_printed),
    FOREIGN KEY(citation_source_id,related_stratum,related_endpoint)
        REFERENCES citation_observation(source_id,stratum,endpoint),
    FOREIGN KEY(literature_source_id,related_stratum,related_endpoint)
        REFERENCES literature_observation(source_id,stratum,endpoint),
    CHECK((citation_source_id IS NULL)<>(literature_source_id IS NULL))
) STRICT;
