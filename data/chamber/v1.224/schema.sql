CREATE TABLE publication_berkeley_chest_symptom (
    source_id TEXT NOT NULL REFERENCES publication_source,
    series TEXT NOT NULL,
    table_row INTEGER NOT NULL CHECK(table_row > 0),
    minutes_after_arrival_at_38000_ft INTEGER NOT NULL CHECK(minutes_after_arrival_at_38000_ft >= 0),
    chest_pain_grade TEXT NOT NULL CHECK(chest_pain_grade IN ('mild','moderate')),
    cough TEXT NOT NULL CHECK(cough IN ('yes','-')),
    bends_grade TEXT NOT NULL CHECK(bends_grade IN ('mild','moderate','severe','-')),
    vasomotor_reaction TEXT NOT NULL CHECK(vasomotor_reaction IN ('yes','-')),
    visual_symptom_footnote TEXT NOT NULL CHECK(visual_symptom_footnote IN ('present','-')),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,series,table_row)
) STRICT;

CREATE TABLE publication_berkeley_visual_episode (
    source_id TEXT NOT NULL REFERENCES publication_source,
    table_row INTEGER NOT NULL CHECK(table_row > 0),
    visual_symptoms TEXT NOT NULL,
    associated_symptoms TEXT NOT NULL,
    scotoma_resolution_phase TEXT NOT NULL CHECK(scotoma_resolution_phase IN ('after_ground','during_descent')),
    scotoma_resolution_min_after_ground INTEGER CHECK(scotoma_resolution_min_after_ground >= 0),
    headache_observed TEXT NOT NULL CHECK(headache_observed IN ('present','absent')),
    headache_onset_reference TEXT CHECK(headache_onset_reference IN ('scotoma_onset','ground')),
    headache_onset_min_from_reference INTEGER CHECK(headache_onset_min_from_reference >= 0),
    headache_duration_min INTEGER CHECK(headache_duration_min > 0),
    headache_description TEXT,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,table_row),
    CHECK((scotoma_resolution_phase='after_ground') = (scotoma_resolution_min_after_ground IS NOT NULL)),
    CHECK((headache_onset_reference IS NULL) = (headache_onset_min_from_reference IS NULL)),
    CHECK(headache_observed='present' OR
          (headache_onset_reference IS NULL AND headache_duration_min IS NULL AND headache_description IS NULL))
) STRICT;

CREATE TABLE publication_berkeley_discrepant_margin (
    source_id TEXT NOT NULL REFERENCES publication_source,
    endpoint TEXT NOT NULL,
    source_section TEXT NOT NULL,
    risk_set TEXT NOT NULL,
    count_basis TEXT NOT NULL CHECK(count_basis IN ('narrative','table_sum','row_count')),
    reported_cases INTEGER NOT NULL CHECK(reported_cases >= 0),
    records_in_risk_set INTEGER NOT NULL CHECK(records_in_risk_set >= reported_cases),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,endpoint,source_section)
) STRICT;
