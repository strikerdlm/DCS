CREATE TABLE citation_source (
    source_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    access TEXT NOT NULL CHECK(access IN ('full_text','primary_abstract')),
    source_sha256 TEXT CHECK(length(source_sha256)=64),
    note TEXT NOT NULL
) STRICT;

CREATE TABLE citation_observation (
    source_id TEXT NOT NULL REFERENCES citation_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    numerator INTEGER CHECK(numerator >= 0 AND numerator <= denominator),
    denominator INTEGER NOT NULL CHECK(denominator > 0),
    denominator_unit TEXT NOT NULL CHECK(denominator_unit IN (
        'student_exposure','observer_exposure','person_exposure','participant','dcs_case','treated_dcs_case'
    )),
    reported_percent REAL CHECK(reported_percent BETWEEN 0 AND 100),
    period TEXT,
    altitude_ft INTEGER CHECK(altitude_ft > 0),
    planned_altitude_min INTEGER CHECK(planned_altitude_min > 0),
    prebreathe_min INTEGER CHECK(prebreathe_min >= 0),
    protocol TEXT NOT NULL,
    outcome_window TEXT NOT NULL,
    locator TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role IN ('overlap_hold','overlapping_margin','conditional')),
    CHECK((numerator IS NULL) <> (reported_percent IS NULL)),
    PRIMARY KEY(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE citation_overlap (
    source_id TEXT NOT NULL REFERENCES citation_source,
    related_source TEXT NOT NULL,
    relationship TEXT NOT NULL,
    evidence TEXT NOT NULL,
    PRIMARY KEY(source_id,related_source)
) STRICT;

CREATE TABLE citation_reference (
    citing_source_id TEXT NOT NULL REFERENCES citation_source,
    ref_no INTEGER NOT NULL CHECK(ref_no > 0),
    reference_page INTEGER NOT NULL,
    printed_reference TEXT NOT NULL,
    matched_title TEXT,
    crossref_doi TEXT,
    openalex_id TEXT,
    openalex_doi TEXT,
    pmid TEXT,
    indexed_oa_status TEXT,
    indexed_oa_url TEXT,
    zotero_item_keys TEXT,
    zotero_pdf_keys TEXT,
    europe_pmc_fulltext_url TEXT,
    access_checked TEXT NOT NULL CHECK(access_checked IN (
        'full_text_inspected','primary_abstract_inspected','indexed_fulltext_link','no_verified_copy'
    )),
    source_id TEXT REFERENCES citation_source,
    screen TEXT NOT NULL,
    note TEXT,
    PRIMARY KEY(citing_source_id,ref_no)
) STRICT;

CREATE TABLE citation_citer (
    cited_source_id TEXT NOT NULL REFERENCES citation_source,
    openalex_id TEXT NOT NULL,
    title TEXT NOT NULL,
    year INTEGER,
    doi TEXT,
    venue TEXT,
    PRIMARY KEY(cited_source_id,openalex_id)
) STRICT;

CREATE TABLE citation_paired_dcs (
    source_id TEXT NOT NULL REFERENCES citation_source,
    arm_a TEXT NOT NULL,
    arm_b TEXT NOT NULL,
    participants INTEGER NOT NULL CHECK(participants > 0),
    both_dcs INTEGER NOT NULL CHECK(both_dcs >= 0),
    a_only INTEGER NOT NULL CHECK(a_only >= 0),
    b_only INTEGER NOT NULL CHECK(b_only >= 0),
    neither INTEGER NOT NULL CHECK(neither >= 0),
    locator TEXT NOT NULL,
    CHECK(both_dcs+a_only+b_only+neither=participants),
    PRIMARY KEY(source_id,arm_a,arm_b)
) STRICT;

CREATE TABLE citation_participant_cell (
    source_id TEXT NOT NULL REFERENCES citation_source,
    study_participant INTEGER NOT NULL,
    arm TEXT NOT NULL,
    accomplished INTEGER NOT NULL CHECK(accomplished IN (0,1)),
    symptom_listed INTEGER CHECK(symptom_listed IN (0,1)),
    severe_vge_marked INTEGER CHECK(severe_vge_marked IN (0,1)),
    symptom_text TEXT,
    hbo_marked INTEGER CHECK(hbo_marked IN (0,1)),
    postflight_marked INTEGER CHECK(postflight_marked IN (0,1)),
    locator TEXT NOT NULL,
    CHECK((accomplished=1)=(symptom_listed IS NOT NULL)),
    CHECK((accomplished=1)=(severe_vge_marked IS NOT NULL)),
    CHECK((accomplished=1)=(hbo_marked IS NOT NULL)),
    CHECK((accomplished=1)=(postflight_marked IS NOT NULL)),
    CHECK((coalesce(symptom_listed,0)=1)=(symptom_text IS NOT NULL)),
    PRIMARY KEY(source_id,study_participant,arm)
) STRICT;
