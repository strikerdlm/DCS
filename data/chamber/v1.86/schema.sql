CREATE TABLE publication_crowell83_chamber_incidents (
    source_id TEXT NOT NULL,
    summary_stratum TEXT NOT NULL,
    type_i_to_iv_chamber_runs INTEGER NOT NULL CHECK(type_i_to_iv_chamber_runs > 0),
    reported_total_incidents INTEGER NOT NULL CHECK(reported_total_incidents >= 0),
    sinus_incidents INTEGER NOT NULL CHECK(sinus_incidents >= 0),
    dental_incidents INTEGER NOT NULL CHECK(dental_incidents >= 0),
    ear_incidents INTEGER NOT NULL CHECK(ear_incidents >= 0),
    gastrointestinal_incidents INTEGER NOT NULL CHECK(gastrointestinal_incidents >= 0),
    hypoxia_or_hyperventilation_incidents INTEGER NOT NULL CHECK(hypoxia_or_hyperventilation_incidents >= 0),
    other_incidents INTEGER NOT NULL CHECK(other_incidents >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,summary_stratum),
    FOREIGN KEY(source_id,summary_stratum) REFERENCES zotero_observation(source_id,stratum)
) STRICT;

CREATE TABLE publication_vann04_preflight_group (
    source_id TEXT NOT NULL,
    profile TEXT NOT NULL,
    printed_trials INTEGER NOT NULL CHECK(printed_trials > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,profile),
    FOREIGN KEY(source_id,profile) REFERENCES publication_vann04_dive_profile(source_id,profile)
) STRICT;

CREATE TABLE publication_vann04_preflight_case (
    source_id TEXT NOT NULL,
    case_number INTEGER NOT NULL CHECK(case_number > 0),
    profile TEXT NOT NULL,
    first_reported_symptom_phase TEXT NOT NULL CHECK(first_reported_symptom_phase IN (
        'during_dive','dive_ascent','surface_after_dive'
    )),
    flight_disposition TEXT NOT NULL CHECK(flight_disposition IN (
        'did_not_fly','flew_without_new_symptoms','flew_with_recurrence','flew_with_distinct_episode'
    )),
    linked_appendix_b_case INTEGER CHECK(linked_appendix_b_case > 0),
    symptoms TEXT NOT NULL,
    outcome TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,case_number),
    UNIQUE(source_id,linked_appendix_b_case),
    FOREIGN KEY(source_id,profile) REFERENCES publication_vann04_preflight_group(source_id,profile),
    FOREIGN KEY(source_id,linked_appendix_b_case) REFERENCES publication_vann04_case(source_id,case_number),
    CHECK((flight_disposition = 'flew_with_distinct_episode') = (linked_appendix_b_case IS NOT NULL))
) STRICT;
