CREATE TABLE publication_observation_counting_unit_revision (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    evidence_source_id TEXT NOT NULL REFERENCES publication_source,
    previous_unit TEXT NOT NULL,
    revised_unit TEXT NOT NULL CHECK(revised_unit IN ('person_exposure','person')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK(revised_unit <> previous_unit),
    PRIMARY KEY(source_id,stratum,endpoint),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;

UPDATE publication_observation
SET denominator_unit = 'person_exposure'
WHERE source_id = 'powell91_tm102176'
  AND endpoint = 'dcs_conditional_on_maximum_vge_grade'
  AND analysis_role = 'overlap_hold' AND denominator_unit = 'person';

UPDATE publication_overlap
SET relationship = 'likely_overlap',
    evidence = 'Vann AD-A151800 Fig. 12 matches Powell''s five grade cells and identifies 173 NASA Shuttle chamber exposures. The 1983 JSC report describes 173 Doppler-monitored runs to validate a Shuttle decompression procedure. Exposure-level identifiers remain unavailable.'
WHERE source_id = 'powell91_tm102176' AND related_source = 'waligora83_tm58257';
