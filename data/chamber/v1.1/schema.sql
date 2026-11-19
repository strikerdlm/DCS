CREATE TABLE zotero_source (
    source_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    publication_year INTEGER NOT NULL,
    url TEXT NOT NULL,
    zotero_item_key TEXT NOT NULL,
    zotero_attachment_key TEXT,
    pdf_sha256 TEXT NOT NULL CHECK(length(pdf_sha256)=64),
    parse_sha256 TEXT NOT NULL CHECK(length(parse_sha256)=64),
    pdf_pages INTEGER NOT NULL CHECK(pdf_pages>0)
) STRICT;

CREATE TABLE zotero_observation (
    source_id TEXT NOT NULL REFERENCES zotero_source,
    stratum TEXT NOT NULL,
    period TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role IN
        ('descriptive_stratum','overlapping_margin','case_timing','rate_only','overlap_hold','historical_reprint','observer_months')),
    cases INTEGER CHECK(cases>=0),
    denominator INTEGER NOT NULL CHECK(denominator>0),
    denominator_unit TEXT NOT NULL,
    reported_rate REAL CHECK(reported_rate>=0),
    rate_unit TEXT CHECK(rate_unit IN ('percent','per_1000')),
    nominal_altitude_ft INTEGER CHECK(nominal_altitude_ft>0),
    nominal_prebreathe_min INTEGER CHECK(nominal_prebreathe_min>=0),
    onset_window TEXT,
    locator TEXT NOT NULL,
    note TEXT,
    PRIMARY KEY(source_id,stratum),
    CHECK(cases IS NULL OR cases<=denominator),
    CHECK((reported_rate IS NULL)=(rate_unit IS NULL)),
    CHECK(reported_rate IS NULL OR reported_rate<=CASE rate_unit WHEN 'percent' THEN 100 ELSE 1000 END),
    CHECK((analysis_role='rate_only' AND cases IS NULL AND reported_rate IS NOT NULL)
        OR (analysis_role='overlap_hold' AND (cases IS NOT NULL OR reported_rate IS NOT NULL))
        OR (analysis_role NOT IN ('rate_only','overlap_hold') AND cases IS NOT NULL)),
    CHECK(analysis_role<>'case_timing' OR (denominator_unit='dcs_cases' AND onset_window IS NOT NULL)),
    CHECK(analysis_role<>'observer_months' OR denominator_unit='observer_months')
) STRICT;

CREATE TABLE zotero_overlap (
    source_id TEXT NOT NULL REFERENCES zotero_source,
    related_source TEXT NOT NULL,
    relationship TEXT NOT NULL,
    evidence TEXT NOT NULL,
    PRIMARY KEY(source_id,related_source)
) STRICT;
