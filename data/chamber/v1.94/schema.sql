CREATE TABLE publication_olson88_protocol (
    source_id TEXT PRIMARY KEY REFERENCES publication_source(source_id),
    archive_source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    vax_title_code INTEGER NOT NULL CHECK(vax_title_code > 0),
    reported_participants INTEGER NOT NULL CHECK(reported_participants > 0),
    reported_exposures INTEGER NOT NULL CHECK(reported_exposures >= reported_participants),
    target_altitude_ft INTEGER NOT NULL CHECK(target_altitude_ft > 0),
    target_pressure_psia REAL NOT NULL CHECK(target_pressure_psia > 0),
    scheduled_max_min INTEGER NOT NULL CHECK(scheduled_max_min > 0),
    prebreathe_min INTEGER NOT NULL CHECK(prebreathe_min >= 0),
    breathing_oxygen_fraction REAL NOT NULL CHECK(breathing_oxygen_fraction BETWEEN 0 AND 1),
    doppler_check_interval_min INTEGER NOT NULL CHECK(doppler_check_interval_min > 0),
    doppler_endpoint_definition TEXT NOT NULL,
    locator TEXT NOT NULL
) STRICT;

CREATE TABLE publication_olson88_exposure (
    source_id TEXT NOT NULL REFERENCES publication_olson88_protocol(source_id),
    table_subject_ordinal INTEGER NOT NULL CHECK(table_subject_ordinal > 0),
    table_subject_code TEXT NOT NULL,
    outcome_column TEXT NOT NULL CHECK(outcome_column IN ('with_bends','without_bends')),
    within_column_order INTEGER NOT NULL CHECK(within_column_order > 0),
    participant_link_status TEXT NOT NULL CHECK(participant_link_status IN (
        'table_linked','narrative_conflict'
    )),
    linked_participant_ordinal INTEGER,
    bubble_detection_min INTEGER CHECK(bubble_detection_min >= 0),
    bends_onset_min INTEGER CHECK(bends_onset_min >= 0),
    intermittent_pain_only_marked INTEGER NOT NULL CHECK(intermittent_pain_only_marked IN (0,1)),
    pdf_page INTEGER NOT NULL CHECK(pdf_page IN (2,3)),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,table_subject_ordinal,outcome_column,within_column_order),
    CHECK((participant_link_status='table_linked' AND linked_participant_ordinal IS table_subject_ordinal)
       OR (participant_link_status='narrative_conflict' AND linked_participant_ordinal IS NULL)),
    CHECK((outcome_column='with_bends') = (bends_onset_min IS NOT NULL)),
    CHECK(intermittent_pain_only_marked=0 OR bends_onset_min IS NOT NULL)
) STRICT;
