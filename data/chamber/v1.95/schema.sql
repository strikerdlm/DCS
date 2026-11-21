CREATE TABLE publication_usafsam_appendix_a (
    source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    row_number INTEGER NOT NULL CHECK(row_number > 0),
    study_number INTEGER NOT NULL CHECK(study_number BETWEEN 1 AND 8),
    pressure_psia REAL NOT NULL CHECK(pressure_psia > 0),
    pressure_mmhg INTEGER NOT NULL CHECK(pressure_mmhg > 0),
    pressure_altitude_ft INTEGER NOT NULL CHECK(pressure_altitude_ft > 0),
    prebreathe_min INTEGER NOT NULL CHECK(prebreathe_min >= 0),
    exposure_oxygen_percent INTEGER NOT NULL CHECK(exposure_oxygen_percent BETWEEN 0 AND 100),
    participant_count INTEGER NOT NULL CHECK(participant_count > 0),
    sex_as_printed TEXT NOT NULL CHECK(sex_as_printed IN ('M','F')),
    exposures_per_participant_min INTEGER CHECK(exposures_per_participant_min > 0),
    exposures_per_participant_max INTEGER NOT NULL CHECK(exposures_per_participant_max > 0),
    scheduled_max_hours INTEGER CHECK(scheduled_max_hours > 0),
    reported_exposure_count INTEGER NOT NULL CHECK(reported_exposure_count >= participant_count),
    exposure_count_kind TEXT NOT NULL CHECK(exposure_count_kind IN ('observed_total','design_total')),
    exercise_code TEXT NOT NULL CHECK(exercise_code IN ('A','B','C')),
    participants_grade2_first_pct INTEGER CHECK(participants_grade2_first_pct BETWEEN 0 AND 100),
    participants_grade2_ever_pct INTEGER CHECK(participants_grade2_ever_pct BETWEEN 0 AND 100),
    exposures_grade2_pct INTEGER CHECK(exposures_grade2_pct BETWEEN 0 AND 100),
    mean_grade2_onset_min INTEGER CHECK(mean_grade2_onset_min > 0),
    onset_status TEXT NOT NULL CHECK(onset_status IN ('reported','not_applicable','study_in_progress')),
    participants_max_vge_3_4_pct INTEGER CHECK(participants_max_vge_3_4_pct BETWEEN 0 AND 100),
    participants_max_vge_1_2_pct INTEGER CHECK(participants_max_vge_1_2_pct BETWEEN 0 AND 100),
    participants_max_vge_0_pct INTEGER CHECK(participants_max_vge_0_pct BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,row_number),
    CHECK(exposures_per_participant_min <= exposures_per_participant_max),
    CHECK(participants_grade2_first_pct <= participants_grade2_ever_pct),
    CHECK((mean_grade2_onset_min IS NOT NULL) = (onset_status='reported')),
    CHECK((exposure_count_kind='design_total') = (onset_status='study_in_progress')),
    CHECK(exposure_count_kind='observed_total' OR (
        participants_grade2_first_pct IS NULL AND participants_grade2_ever_pct IS NULL
        AND exposures_grade2_pct IS NULL AND participants_max_vge_3_4_pct IS NULL
        AND participants_max_vge_1_2_pct IS NULL AND participants_max_vge_0_pct IS NULL
    ))
) STRICT;

CREATE TABLE publication_usafsam_appendix_a_link (
    earlier_source_id TEXT NOT NULL,
    earlier_row INTEGER NOT NULL,
    later_source_id TEXT NOT NULL,
    later_row INTEGER NOT NULL,
    relationship TEXT NOT NULL CHECK(relationship IN (
        'shared_summary_values','revised_counts_unresolved','planned_design_to_duration_result'
    )),
    evidence TEXT NOT NULL,
    PRIMARY KEY(earlier_source_id,earlier_row,later_source_id,later_row),
    CHECK(earlier_source_id <> later_source_id),
    FOREIGN KEY(earlier_source_id,earlier_row) REFERENCES publication_usafsam_appendix_a(source_id,row_number),
    FOREIGN KEY(later_source_id,later_row) REFERENCES publication_usafsam_appendix_a(source_id,row_number)
) STRICT;

CREATE TABLE publication_usafsam_pilot_onset (
    source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    altitude_ft INTEGER NOT NULL CHECK(altitude_ft > 0),
    mean_min REAL NOT NULL,
    earliest_min INTEGER NOT NULL CHECK(earliest_min >= 0),
    latest_min INTEGER NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,altitude_ft),
    CHECK(mean_min BETWEEN earliest_min AND latest_min)
) STRICT;

CREATE TABLE publication_usafsam_co2_interim_arm (
    source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    prebreathe_gas TEXT NOT NULL,
    cases INTEGER NOT NULL CHECK(cases >= 0),
    reported_percent REAL NOT NULL CHECK(reported_percent BETWEEN 0 AND 100),
    reported_exposures INTEGER CHECK(reported_exposures >= cases),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,prebreathe_gas)
) STRICT;
