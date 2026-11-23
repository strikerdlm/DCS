UPDATE publication_source
SET locator='Methods and Results p. 997, Table I and treatment results p. 998',
    note='AFRL archive from 22 protocols. Source distinguishes 29 pulmonary-symptom exposures in 27 people. Abstract and Methods give 2,525 exposures. Results and Discussion give 2,584. Table I has paired symptom and ultrasound onset times without participant or protocol identifiers.'
WHERE source_id='balldin02';

CREATE TABLE publication_balldin_pulmonary_onset (
    source_id TEXT NOT NULL REFERENCES publication_source,
    printed_row INTEGER NOT NULL CHECK(printed_row > 0),
    pulmonary_symptom_count INTEGER NOT NULL CHECK(pulmonary_symptom_count BETWEEN 1 AND 3),
    pulmonary_dcs_onset_min INTEGER NOT NULL CHECK(pulmonary_dcs_onset_min >= 0),
    vge_onset_min INTEGER CHECK(vge_onset_min >= 0),
    severe_vge_onset_min INTEGER CHECK(severe_vge_onset_min >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,printed_row),
    CHECK(severe_vge_onset_min IS NULL OR vge_onset_min IS NOT NULL)
) STRICT;

CREATE TABLE publication_balldin_pulmonary_treatment (
    source_id TEXT NOT NULL REFERENCES publication_source,
    pulmonary_symptom_count INTEGER NOT NULL CHECK(pulmonary_symptom_count BETWEEN 1 AND 3),
    case_exposures INTEGER NOT NULL CHECK(case_exposures > 0),
    resolved_after_ground_recompression INTEGER NOT NULL CHECK(resolved_after_ground_recompression >= 0),
    resolved_after_hyperbaric_oxygen INTEGER NOT NULL CHECK(resolved_after_hyperbaric_oxygen >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,pulmonary_symptom_count),
    CHECK(resolved_after_ground_recompression + resolved_after_hyperbaric_oxygen = case_exposures)
) STRICT;
