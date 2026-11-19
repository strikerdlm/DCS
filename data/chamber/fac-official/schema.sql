CREATE TABLE fac_official_source (
    source_id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    sha256 TEXT UNIQUE NOT NULL CHECK(length(sha256)=64),
    sheet TEXT NOT NULL,
    locator TEXT NOT NULL,
    unit TEXT NOT NULL
) STRICT;

CREATE TABLE fac_official_annual (
    source_id TEXT NOT NULL REFERENCES fac_official_source,
    year INTEGER PRIMARY KEY,
    source_row INTEGER UNIQUE NOT NULL,
    partial_through TEXT,
    trained_crew INTEGER NOT NULL,
    fac_crew INTEGER NOT NULL,
    army_crew INTEGER NOT NULL,
    navy_crew INTEGER NOT NULL,
    police_crew INTEGER NOT NULL,
    other_crew INTEGER NOT NULL,
    deb INTEGER NOT NULL,
    dea INTEGER NOT NULL,
    nvt INTEGER NOT NULL,
    nvg INTEGER NOT NULL,
    hypoxia INTEGER NOT NULL CHECK(hypoxia>=0),
    rapid_decompression INTEGER NOT NULL CHECK(rapid_decompression>=0),
    ejection INTEGER,
    total_training_activities INTEGER NOT NULL,
    courses INTEGER NOT NULL,
    course_attendees INTEGER NOT NULL,
    registered_dcs_events INTEGER CHECK(registered_dcs_events>=0),
    student_dcs_events INTEGER CHECK(student_dcs_events>=0),
    instructor_dcs_events INTEGER CHECK(instructor_dcs_events>=0),
    case_source_id TEXT REFERENCES fac_official_source,
    CHECK(trained_crew=fac_crew+army_crew+navy_crew+police_crew+other_crew),
    CHECK((registered_dcs_events IS NULL)=(case_source_id IS NULL)),
    CHECK((student_dcs_events IS NULL)=(case_source_id IS NULL)),
    CHECK((instructor_dcs_events IS NULL)=(case_source_id IS NULL)),
    CHECK(registered_dcs_events=student_dcs_events+instructor_dcs_events)
) STRICT;

CREATE TABLE fac_official_observation (
    source_id TEXT NOT NULL REFERENCES fac_official_source,
    dimension TEXT NOT NULL,
    category TEXT NOT NULL,
    events INTEGER NOT NULL CHECK(events>=0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,dimension,category)
) STRICT;

CREATE TABLE fac_official_overlap (
    source_id TEXT NOT NULL REFERENCES fac_official_source,
    related_source TEXT NOT NULL,
    years TEXT NOT NULL,
    interpretation TEXT NOT NULL,
    PRIMARY KEY(source_id, related_source)
) STRICT;

-- Annual case registrations and activity counts have distinct units.
CREATE VIEW fac_official_chamber_year AS
    SELECT year, registered_dcs_events, student_dcs_events, instructor_dcs_events,
           hypoxia, rapid_decompression,
           hypoxia+rapid_decompression AS chamber_activities, trained_crew
    FROM fac_official_annual WHERE case_source_id IS NOT NULL;

CREATE VIEW fac_celis_annual_reconciliation AS
    SELECT f.*, s.events AS thesis_cases, s.denominator AS thesis_training_count
    FROM fac_official_chamber_year f
    LEFT JOIN sharepoint_observation s ON s.source_id='celis23_thesis'
        AND s.endpoint='dcs' AND s.stratum=CAST(f.year AS TEXT);
