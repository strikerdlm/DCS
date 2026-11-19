CREATE TABLE review_retrieval (
    run_id TEXT PRIMARY KEY,
    run_date TEXT NOT NULL,
    provider TEXT NOT NULL,
    operation TEXT NOT NULL,
    parameters_json TEXT NOT NULL CHECK(json_valid(parameters_json)),
    reported_total INTEGER CHECK(reported_total >= 0),
    retrieved INTEGER NOT NULL CHECK(retrieved >= 0),
    status TEXT NOT NULL,
    note TEXT NOT NULL,
    snapshot TEXT NOT NULL REFERENCES frozen_input(path)
) STRICT;

CREATE TABLE review_workflow_document (
    input_path TEXT PRIMARY KEY REFERENCES frozen_input(path),
    content_json TEXT NOT NULL CHECK(json_valid(content_json))
) STRICT;

CREATE TABLE review_report (
    report_id TEXT PRIMARY KEY,
    display_title TEXT NOT NULL
) STRICT;

CREATE TABLE review_record (
    record_key TEXT PRIMARY KEY,
    report_id TEXT NOT NULL REFERENCES review_report,
    stream TEXT NOT NULL,
    source_key TEXT NOT NULL,
    input_path TEXT NOT NULL REFERENCES frozen_input(path),
    run_id TEXT REFERENCES review_retrieval,
    result_position INTEGER CHECK(result_position >= 1),
    title TEXT NOT NULL, year INTEGER, doi TEXT, pmid TEXT, openalex_id TEXT, url TEXT,
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    UNIQUE(stream, source_key), UNIQUE(run_id, result_position),
    CHECK((run_id IS NULL) = (result_position IS NULL))
) STRICT;
CREATE INDEX review_record_report_idx ON review_record(report_id);
CREATE INDEX review_record_doi_idx ON review_record(doi);
CREATE VIEW review_publication_catalog AS
    SELECT p.report_id,p.display_title,
           group_concat(DISTINCT r.year) AS reported_years,
           group_concat(DISTINCT r.pmid) AS pmids,
           group_concat(DISTINCT r.doi) AS dois,
           group_concat(DISTINCT r.openalex_id) AS openalex_ids,
           count(*) AS record_count,
           count(r.run_id) AS new_retrieval_records
    FROM review_report p JOIN review_record r USING(report_id) GROUP BY p.report_id;

CREATE VIEW review_identifier_disagreement AS
    SELECT record_key,report_id,json_extract(metadata_json,'$.crossref_doi') AS crossref_doi,
           json_extract(metadata_json,'$.openalex_doi') AS openalex_doi
    FROM review_record
    WHERE nullif(lower(trim(json_extract(metadata_json,'$.crossref_doi'))),'') <>
          nullif(lower(trim(json_extract(metadata_json,'$.openalex_doi'))),'');

CREATE TABLE review_identity_assignment (
    record_key TEXT PRIMARY KEY REFERENCES review_record,
    report_id TEXT NOT NULL REFERENCES review_report,
    basis TEXT NOT NULL, evidence_url TEXT NOT NULL
) STRICT;
CREATE TABLE review_identity_candidate (
    left_key TEXT NOT NULL REFERENCES review_record, right_key TEXT NOT NULL REFERENCES review_record,
    reason TEXT NOT NULL, PRIMARY KEY(left_key, right_key, reason), CHECK(left_key != right_key)
) STRICT;

CREATE TABLE review_study (
    study_id TEXT PRIMARY KEY, label TEXT NOT NULL, period TEXT NOT NULL, setting TEXT NOT NULL
) STRICT;
CREATE TABLE review_study_report (
    study_id TEXT NOT NULL REFERENCES review_study, report_id TEXT NOT NULL REFERENCES review_report,
    role TEXT NOT NULL, locator TEXT NOT NULL, PRIMARY KEY(study_id, report_id)
) STRICT;
CREATE TABLE review_report_relation (
    left_report TEXT NOT NULL REFERENCES review_report, right_report TEXT NOT NULL REFERENCES review_report,
    relationship TEXT NOT NULL, evidence TEXT NOT NULL, evidence_url TEXT NOT NULL,
    PRIMARY KEY(left_report, right_report, relationship), CHECK(left_report != right_report)
) STRICT;

-- Providers audit a DOI. Multiple bibliographic reports can carry the same DOI.
CREATE TABLE review_quality_check (
    doi TEXT NOT NULL, checked_on TEXT NOT NULL, provider TEXT NOT NULL,
    query TEXT NOT NULL, status TEXT NOT NULL, detail TEXT NOT NULL, evidence_url TEXT NOT NULL,
    PRIMARY KEY(doi, checked_on, provider, query)
) STRICT;

-- Anchor decisions to a permanent source occurrence so later identity curation
-- can change the report grouping without losing a reviewer's original decision.
CREATE TABLE review_screening (
    record_key TEXT NOT NULL REFERENCES review_record,
    reviewer TEXT NOT NULL CHECK(length(trim(reviewer)) > 0),
    stage TEXT NOT NULL CHECK(stage IN ('title_abstract','full_text')),
    revision INTEGER NOT NULL CHECK(revision >= 1),
    decided_on TEXT NOT NULL, decision TEXT NOT NULL CHECK(decision IN ('include','exclude','uncertain')),
    reason TEXT, locator TEXT,
    PRIMARY KEY(record_key, reviewer, stage, revision),
    CHECK(decision != 'exclude' OR length(trim(coalesce(reason,''))) > 0),
    CHECK(stage != 'full_text' OR length(trim(coalesce(locator,''))) > 0)
) STRICT;
CREATE VIEW review_current_screening AS
    SELECT r.report_id, s.* FROM review_screening s JOIN review_record r USING(record_key)
    WHERE NOT EXISTS (
        SELECT 1 FROM review_screening t WHERE t.record_key=s.record_key AND t.reviewer=s.reviewer
        AND t.stage=s.stage AND t.revision>s.revision
    );
CREATE VIEW review_run_counts AS
    SELECT q.run_id,q.provider,q.reported_total,q.retrieved,count(DISTINCT r.report_id) AS report_groups
    FROM review_retrieval q LEFT JOIN review_record r USING(run_id) GROUP BY q.run_id;

CREATE VIEW review_historical_search_record AS
    SELECT r.record_key,r.report_id,r.stream,h.search_id,h.rank,q.searched_on,q.tool,q.database,
           q.query,q.status,h.disposition AS original_disposition
    FROM review_record r
    JOIN publication_search_hit h
      ON h.search_id=json_extract(r.metadata_json,'$.search_id')
     AND h.rank=CAST(json_extract(r.metadata_json,'$.rank') AS INTEGER)
    JOIN publication_search_run q USING(search_id)
    WHERE r.stream LIKE 'data/chamber/%/search_hits.csv';

-- Pilot eligibility examples. Keep the published cells and their locators.
-- Piwinski contributes three disjoint altitude strata per role.
CREATE VIEW review_seed_role_cell AS
WITH cells(report_id, source_table, source_cell, chamber_role, cases, exposures, locator) AS (
    SELECT report_id, 'review_record', source_key,
           CASE json_extract(metadata_json,'$.group') WHEN 'trainees' THEN 'trainee' ELSE 'staff' END,
           CAST(nullif(json_extract(metadata_json,'$.cases'),'') AS INTEGER),
           CAST(nullif(json_extract(metadata_json,'$.denominator'),'') AS INTEGER),
           json_extract(metadata_json,'$.locator')
    FROM review_record WHERE stream='data/chamber/intake-2026-11-19/outcome_sources.csv'
      AND source_key IN ('bason76:trainees:dcs','bason76:inside_observers:dcs',
                         'bason91:trainees:dcs','bason91:inside_observers:dcs')
    UNION ALL
    SELECT 'pmid:12546299','aviation_count',stratum,
           CASE role WHEN 'Student' THEN 'trainee' ELSE 'staff' END,cases,denominator,locator
    FROM aviation_count WHERE source_id='rice03' AND stratum IN ('I-IO-all','I-Student-all')
    UNION ALL
    SELECT 'pmid:3790029','zotero_observation',stratum,
           CASE WHEN stratum LIKE 'student_%' THEN 'trainee' ELSE 'staff' END,cases,denominator,locator
    FROM zotero_observation WHERE source_id='piwinski86' AND analysis_role='descriptive_stratum'
    UNION ALL
    SELECT 'pmid:32574436','zotero_observation',stratum,
           CASE stratum WHEN 'trainees_all' THEN 'trainee' ELSE 'staff' END,cases,denominator,locator
    FROM zotero_observation WHERE source_id='ercan20' AND stratum IN ('trainees_all','inside_observer')
    UNION ALL
    SELECT 'pmid:30352646','cohort_observation',stratum,
           CASE stratum WHEN 'students-all-profiles' THEN 'trainee' ELSE 'staff' END,cases,denominator,locator
    FROM cohort_observation WHERE source_id='conkin18' AND stratum IN ('students-all-profiles','inside-observers-all')
)
SELECT l.study_id,c.* FROM cells c JOIN review_study_report l USING(report_id) WHERE l.role='primary';

CREATE VIEW review_supplementary_role_cell AS
WITH cells(study_id,source_table,source_id,stratum,cases,exposures,denominator_basis,locator,note) AS (
    SELECT 'usn-1959-1968','publication_observation',source_id,stratum,numerator,denominator,
           denominator_basis,locator,note FROM publication_observation
    WHERE source_id='furry73' AND endpoint='dcs' AND stratum IN ('trainees','inside-observers')
    UNION ALL
    SELECT 'usaf-1985-1987','discovery_observation',source_id,stratum,numerator,denominator,
           'role subtotals differ from overall total',locator,note FROM discovery_observation
    WHERE source_id='baumgartner92' AND endpoint='dcs' AND stratum IN ('students','inside-observers')
    UNION ALL
    SELECT 'usaf-shaw-fy2004','attachment_observation',source_id,stratum,events,denominator,
           'source_reported',locator,note FROM attachment_observation
    WHERE source_id='brandt09_attachment' AND endpoint='dcs' AND stratum IN ('fy04_students','fy04_observers')
)
SELECT c.*,l.report_id FROM cells c JOIN review_study_report l USING(study_id)
WHERE l.role='supplementary_candidate';
