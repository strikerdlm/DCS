CREATE TABLE zotero_dcs_source (
    source_id TEXT PRIMARY KEY,
    item_key TEXT NOT NULL,
    collection_key TEXT NOT NULL,
    title TEXT NOT NULL,
    identifier TEXT,
    pdf_sha256 TEXT NOT NULL CHECK(length(pdf_sha256)=64),
    pdf_pages INTEGER NOT NULL CHECK(pdf_pages>0),
    parse_mode TEXT NOT NULL CHECK(parse_mode IN ('agentic','reused')),
    parsed_pages TEXT NOT NULL,
    markdown_sha256 TEXT NOT NULL CHECK(length(markdown_sha256)=64),
    disposition TEXT NOT NULL CHECK(disposition IN ('extended','reused','methods','alternate_copy')),
    note TEXT NOT NULL
) STRICT;

CREATE TABLE zotero_dcs_observation (
    source_id TEXT NOT NULL REFERENCES zotero_dcs_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role IN (
        'selected_cluster','case_margin','overlap_hold','modeled','nested_increment'
    )),
    events INTEGER CHECK(events>=0),
    denominator INTEGER CHECK(denominator>0 AND (events IS NULL OR events<=denominator)),
    denominator_unit TEXT,
    value REAL CHECK(value>=0),
    value_unit TEXT,
    peak_altitude_ft INTEGER CHECK(peak_altitude_ft>0),
    prebreathe_min INTEGER CHECK(prebreathe_min>=0),
    planned_horizon_min INTEGER CHECK(planned_horizon_min>0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    CHECK((events IS NULL) != (value IS NULL)),
    CHECK((denominator IS NULL)=(denominator_unit IS NULL)),
    CHECK((value IS NULL)=(value_unit IS NULL)),
    CHECK(analysis_role!='modeled' OR events IS NULL)
) STRICT;

CREATE TABLE zotero_dcs_overlap (
    source_id TEXT NOT NULL REFERENCES zotero_dcs_source,
    scope TEXT NOT NULL,
    related_key TEXT NOT NULL,
    relationship TEXT NOT NULL CHECK(relationship IN (
        'exact_file','same_work','reprint','overlapping_cohort','updated_snapshot','reference_only'
    )),
    disposition TEXT NOT NULL,
    PRIMARY KEY(source_id,scope,related_key)
) STRICT;

CREATE TABLE zotero_dcs_case (
    source_id TEXT NOT NULL REFERENCES zotero_dcs_source,
    case_label TEXT NOT NULL,
    age_years INTEGER NOT NULL CHECK(age_years>0),
    earliest_symptom TEXT NOT NULL,
    onset_anchor TEXT,
    onset_min REAL,
    timing_qualifier TEXT NOT NULL,
    presentation_delay_h INTEGER CHECK(presentation_delay_h>=0),
    other_symptoms TEXT,
    treatment_reported TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,case_label),
    CHECK(onset_min IS NULL OR onset_anchor IS NOT NULL)
) STRICT;

CREATE TABLE zotero_dcs_eva_break (
    source_id TEXT NOT NULL REFERENCES zotero_dcs_source,
    eva_key TEXT NOT NULL,
    date_label TEXT NOT NULL,
    protocol TEXT NOT NULL,
    break_type TEXT NOT NULL,
    measured_or_reported_seconds REAL CHECK(measured_or_reported_seconds>0),
    assumed_break_seconds REAL CHECK(assumed_break_seconds>0),
    payback_seconds REAL CHECK(payback_seconds>0),
    time_to_depress_min REAL CHECK(time_to_depress_min>0),
    time_to_depress_qualifier TEXT,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,eva_key)
) STRICT;

-- The later cumulative table shares the original person-EVAs. Sum only increments.
CREATE VIEW zotero_dcs_eva_totals_2016 AS
    SELECT base.stratum, base.denominator AS reported_2013_person_evas,
           extension.denominator AS additional_person_evas,
           base.denominator+extension.denominator AS reported_2016_person_evas,
           extension.events AS additional_reported_dcs,
           extension.locator
    FROM attachment_observation base
    JOIN zotero_dcs_observation extension USING(stratum)
    WHERE base.source_id='nasa_dcs_evidence_2013'
      AND base.denominator_unit='person_evas'
      AND extension.source_id='N4C7X768' AND extension.analysis_role='nested_increment';
