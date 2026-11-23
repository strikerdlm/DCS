CREATE TABLE publication_source (
    source_id TEXT PRIMARY KEY,
    citation TEXT NOT NULL,
    url TEXT NOT NULL,
    identifier TEXT,
    country TEXT NOT NULL,
    access TEXT NOT NULL CHECK(access IN ('full_text','primary_abstract','metadata','secondary_table')),
    disposition TEXT NOT NULL CHECK(disposition IN ('extracted','crosswalk','lead','excluded')),
    locator TEXT NOT NULL,
    source_sha256 TEXT CHECK(length(source_sha256)=64),
    note TEXT NOT NULL
) STRICT;

CREATE TABLE publication_observation (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role IN (
        'descriptive','overlapping_margin','overlap_hold','selected_cluster','case_conditional',
        'denominator_conflict'
    )),
    numerator INTEGER NOT NULL CHECK(numerator >= 0 AND (denominator IS NULL OR numerator <= denominator)),
    denominator INTEGER CHECK(denominator > 0),
    denominator_unit TEXT CHECK(denominator_unit IN (
        'person_exposure','trainee_exposure','observer_exposure','person',
        'dcs_case','pulmonary_dcs_case','treated_referral','symptom_report','chamber_run'
    )),
    denominator_basis TEXT CHECK(denominator_basis IN ('source_reported','author_reconstructed')),
    period TEXT,
    altitude REAL CHECK(altitude > 0),
    altitude_unit TEXT CHECK(altitude_unit IN ('ft','m')),
    prebreathe_min INTEGER CHECK(prebreathe_min >= 0),
    protocol TEXT NOT NULL,
    outcome_window TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((denominator IS NULL) = (denominator_unit IS NULL)),
    CHECK((denominator IS NULL) = (denominator_basis IS NULL)),
    CHECK((altitude IS NULL) = (altitude_unit IS NULL)),
    PRIMARY KEY(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE publication_overlap (
    source_id TEXT NOT NULL REFERENCES publication_source,
    related_source TEXT NOT NULL,
    relationship TEXT NOT NULL CHECK(relationship IN ('same_cohort','partial_overlap','likely_overlap','unresolved')),
    evidence TEXT NOT NULL,
    PRIMARY KEY(source_id,related_source)
) STRICT;

CREATE TABLE publication_search_run (
    search_id TEXT PRIMARY KEY,
    searched_on TEXT NOT NULL,
    tool TEXT NOT NULL,
    database TEXT NOT NULL,
    query TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('completed','blocked','failed')),
    matched_count INTEGER CHECK(matched_count >= 0),
    screened_count INTEGER NOT NULL CHECK(screened_count >= 0),
    selected_count INTEGER NOT NULL CHECK(selected_count BETWEEN 0 AND screened_count),
    note TEXT NOT NULL
) STRICT;

CREATE TABLE publication_search_hit (
    search_id TEXT NOT NULL REFERENCES publication_search_run,
    rank INTEGER NOT NULL CHECK(rank > 0),
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    identifier TEXT,
    source_id TEXT REFERENCES publication_source,
    disposition TEXT NOT NULL CHECK(disposition IN ('extracted','already_indexed','lead','excluded','alternate_copy')),
    note TEXT NOT NULL,
    PRIMARY KEY(search_id,rank)
) STRICT;
