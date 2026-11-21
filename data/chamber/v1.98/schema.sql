CREATE TABLE publication_tt8_episode (
    source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    table_row INTEGER NOT NULL CHECK(table_row > 0),
    participant_ordinal INTEGER NOT NULL CHECK(participant_ordinal > 0),
    episode_number INTEGER NOT NULL CHECK(episode_number > 0),
    age INTEGER NOT NULL CHECK(age > 0),
    sex_as_printed TEXT NOT NULL CHECK(sex_as_printed IN ('F','M')),
    exposure_year INTEGER NOT NULL,
    altitude_ft INTEGER CHECK(altitude_ft > 0),
    dcs_label TEXT NOT NULL CHECK(dcs_label IN ('I','II')),
    signs_as_reported TEXT NOT NULL,
    onset_location TEXT NOT NULL CHECK(onset_location IN ('altitude','ground')),
    treatment_delay_bound_min INTEGER NOT NULL CHECK(treatment_delay_bound_min > 0),
    treatment_delay_relation TEXT NOT NULL CHECK(treatment_delay_relation IN ('equal','less_than')),
    resolution_min INTEGER CHECK(resolution_min > 0),
    resolution_status TEXT NOT NULL CHECK(resolution_status IN (
        'reported_minutes','at_depth','unresolved_by_assessment'
    )),
    unresolved_at_assessment_min INTEGER CHECK(unresolved_at_assessment_min > 0),
    recurrence_reported INTEGER NOT NULL CHECK(recurrence_reported IN (0,1)),
    tt8_outcome TEXT NOT NULL CHECK(tt8_outcome IN ('success','failure')),
    tt6_conversion_documented INTEGER CHECK(tt6_conversion_documented=1),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,table_row),
    UNIQUE(source_id,participant_ordinal,episode_number),
    CHECK((resolution_status='reported_minutes') = (resolution_min IS NOT NULL)),
    CHECK((resolution_status='unresolved_by_assessment') = (unresolved_at_assessment_min IS NOT NULL)),
    CHECK(tt8_outcome='failure' OR (recurrence_reported=0 AND unresolved_at_assessment_min IS NULL))
) STRICT;

CREATE TABLE publication_tt8_interim_tally (
    source_id TEXT PRIMARY KEY REFERENCES publication_source(source_id),
    reprint_source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    completed_source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    type_i_participants INTEGER NOT NULL CHECK(type_i_participants > 0),
    resolved_without_reported_recurrence INTEGER NOT NULL
        CHECK(resolved_without_reported_recurrence BETWEEN 0 AND type_i_participants),
    locator TEXT NOT NULL,
    scope_note TEXT NOT NULL,
    CHECK(source_id <> reprint_source_id AND source_id <> completed_source_id AND reprint_source_id <> completed_source_id)
) STRICT;

CREATE TABLE publication_webb94_interim_group (
    source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    final_source_id TEXT NOT NULL REFERENCES citation_source(source_id),
    arm TEXT NOT NULL CHECK(arm IN ('exercise10_rest50','rest60')),
    exposures INTEGER NOT NULL CHECK(exposures > 0),
    marked_dcs_cases INTEGER CHECK(marked_dcs_cases BETWEEN 0 AND exposures),
    abstract_dcs_percent INTEGER NOT NULL CHECK(abstract_dcs_percent BETWEEN 0 AND 100),
    results_dcs_percent INTEGER NOT NULL CHECK(results_dcs_percent BETWEEN 0 AND 100),
    resolved_on_recompression INTEGER CHECK(resolved_on_recompression BETWEEN 0 AND marked_dcs_cases),
    respiratory_dcs_cases INTEGER CHECK(respiratory_dcs_cases BETWEEN 0 AND exposures),
    nominal_start_pressure_psia REAL NOT NULL CHECK(nominal_start_pressure_psia > 0),
    target_pressure_psia REAL NOT NULL CHECK(target_pressure_psia > 0),
    planned_plateau_min INTEGER NOT NULL CHECK(planned_plateau_min > 0),
    prebreathe_min INTEGER NOT NULL CHECK(prebreathe_min > 0),
    prebreathe_exercise_min INTEGER NOT NULL CHECK(prebreathe_exercise_min BETWEEN 0 AND prebreathe_min),
    prescribed_prebreathe_pct_peak_vo2 INTEGER CHECK(prescribed_prebreathe_pct_peak_vo2 BETWEEN 1 AND 100),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,arm),
    CHECK(resolved_on_recompression IS NULL OR marked_dcs_cases IS NOT NULL),
    CHECK((prebreathe_exercise_min=0) = (prescribed_prebreathe_pct_peak_vo2 IS NULL))
) STRICT;

CREATE TABLE publication_webb94_case_link (
    source_id TEXT NOT NULL,
    interim_arm TEXT NOT NULL,
    final_source_id TEXT NOT NULL,
    final_participant_ordinal INTEGER NOT NULL,
    final_arm TEXT NOT NULL,
    evidence TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,interim_arm),
    FOREIGN KEY(source_id,interim_arm) REFERENCES publication_webb94_interim_group(source_id,arm),
    FOREIGN KEY(final_source_id,final_participant_ordinal,final_arm)
        REFERENCES citation_participant_cell(source_id,study_participant,arm)
) STRICT;
