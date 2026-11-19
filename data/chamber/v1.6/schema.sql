CREATE TABLE discovery_source (
    source_id TEXT PRIMARY KEY,
    citation TEXT NOT NULL,
    url TEXT NOT NULL,
    access TEXT NOT NULL CHECK(access IN (
        'full_text','presentation','primary_abstract','bibliographic'
    )),
    disposition TEXT NOT NULL CHECK(disposition IN ('extracted','crosswalk','lead')),
    locator TEXT NOT NULL,
    source_sha256 TEXT CHECK(length(source_sha256)=64),
    note TEXT NOT NULL
) STRICT;

CREATE TABLE discovery_observation (
    source_id TEXT NOT NULL REFERENCES discovery_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role IN (
        'descriptive','overlap_hold','overlapping_margin','denominator_conflict',
        'case_conditional','selected_cluster','outcome_conflict'
    )),
    numerator INTEGER CHECK(numerator >= 0 AND (denominator IS NULL OR numerator <= denominator)),
    denominator INTEGER CHECK(denominator > 0),
    denominator_unit TEXT CHECK(denominator_unit IN (
        'person_exposure','student_exposure','observer_exposure','person',
        'dcs_case','type_ii_dcs_case'
    )),
    reported_percent REAL CHECK(reported_percent BETWEEN 0 AND 100),
    reported_cumulative_denominator INTEGER CHECK(reported_cumulative_denominator >= denominator),
    period TEXT,
    altitude_ft INTEGER CHECK(altitude_ft > 0),
    target_pressure_kpa REAL CHECK(target_pressure_kpa > 0),
    planned_altitude_min INTEGER CHECK(planned_altitude_min > 0),
    prebreathe_min INTEGER CHECK(prebreathe_min >= 0),
    protocol TEXT NOT NULL,
    outcome_window TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((numerator IS NULL) <> (reported_percent IS NULL)),
    CHECK((denominator IS NULL) = (denominator_unit IS NULL)),
    PRIMARY KEY(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE discovery_overlap (
    source_id TEXT NOT NULL REFERENCES discovery_source,
    related_source TEXT NOT NULL,
    relationship TEXT NOT NULL CHECK(relationship IN (
        'same_cohort','partial_overlap','likely_overlap','unresolved','publication_version'
    )),
    evidence TEXT NOT NULL,
    PRIMARY KEY(source_id,related_source)
) STRICT;

CREATE TABLE discovery_adjudication (
    issue_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES discovery_source,
    field TEXT NOT NULL,
    primary_report TEXT NOT NULL,
    alternative_report TEXT NOT NULL,
    decision TEXT NOT NULL CHECK(decision IN ('supported','reported_only','distinct_scope','unresolved')),
    accepted_value TEXT,
    evidence TEXT NOT NULL,
    remaining_evidence TEXT,
    CHECK((decision IN ('supported','reported_only')) = (accepted_value IS NOT NULL)),
    CHECK(decision NOT IN ('reported_only','unresolved') OR remaining_evidence IS NOT NULL)
) STRICT;
