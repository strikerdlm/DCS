CREATE TABLE literature_case_table_i (
    source_id TEXT NOT NULL REFERENCES literature_source,
    published_case_number INTEGER NOT NULL CHECK(published_case_number>0),
    endpoint TEXT NOT NULL CHECK(endpoint='dcs_type_i_historical'),
    published_subject_code TEXT NOT NULL,
    published_test_code TEXT NOT NULL,
    test_site TEXT NOT NULL CHECK(test_site IN ('JSC','Duke','Hermann','DCIEM')),
    test_date TEXT NOT NULL,
    vge_detection_status TEXT NOT NULL CHECK(vge_detection_status IN ('detected','not_detected')),
    first_vge_detection_min INTEGER CHECK(first_vge_detection_min>=0),
    dcs_time_as_published TEXT NOT NULL,
    dcs_time_basis TEXT NOT NULL CHECK(dcs_time_basis IN (
        'first_report','noticed_before_in_test_report','recalled_at_debrief','onset_unavailable'
    )),
    dcs_time_min INTEGER CHECK(dcs_time_min>=0),
    symptom_site TEXT NOT NULL CHECK(symptom_site IN ('lower','upper','both','other')),
    locator TEXT NOT NULL,
    CHECK((vge_detection_status='detected') = (first_vge_detection_min IS NOT NULL)),
    CHECK(dcs_time_as_published = CASE dcs_time_basis
        WHEN 'onset_unavailable' THEN '---'
        WHEN 'noticed_before_in_test_report' THEN coalesce(dcs_time_min,'') || '#'
        WHEN 'recalled_at_debrief' THEN coalesce(dcs_time_min,'') || '+'
        ELSE coalesce(CAST(dcs_time_min AS TEXT),'')
    END),
    CHECK((dcs_time_basis='onset_unavailable') = (dcs_time_min IS NULL)),
    PRIMARY KEY(source_id,published_case_number)
) STRICT;

CREATE TRIGGER literature_case_table_i_disjoint
BEFORE INSERT ON literature_case_table_i
WHEN EXISTS (
    SELECT 1 FROM literature_case
    WHERE source_id=NEW.source_id AND published_case_number=NEW.published_case_number
)
BEGIN
    SELECT RAISE(ABORT,'Case is already represented by its published narrative');
END;

CREATE TABLE literature_case_timing_review (
    source_id TEXT NOT NULL,
    published_case_number INTEGER NOT NULL,
    endpoint TEXT NOT NULL CHECK(endpoint IN ('dcs','vge')),
    narrative_time_min INTEGER NOT NULL CHECK(narrative_time_min>=0),
    interpretation TEXT NOT NULL CHECK(interpretation IN ('narrative_preferred','different_symptom')),
    narrative_locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,published_case_number,endpoint),
    FOREIGN KEY(source_id,published_case_number) REFERENCES literature_case_table_i
) STRICT;

CREATE VIEW literature_case_index AS
SELECT source_id, published_case_number, endpoint, first_symptom_report_min AS dcs_time_min,
       'first_report_in_narrative' AS dcs_time_basis, vge_detection_status,
       first_vge_detection_min, locator
FROM literature_case
UNION ALL
SELECT source_id, published_case_number, endpoint, dcs_time_min, dcs_time_basis,
       vge_detection_status, first_vge_detection_min, locator
FROM literature_case_table_i;
