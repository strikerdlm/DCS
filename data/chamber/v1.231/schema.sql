CREATE TABLE publication_post_dive_series (
    source_id TEXT NOT NULL REFERENCES publication_source,
    series TEXT NOT NULL,
    abstract_source_id TEXT NOT NULL REFERENCES publication_source,
    participants_before_exclusions INTEGER,
    participants_in_report INTEGER NOT NULL CHECK(participants_in_report > 0),
    participants_in_abstract INTEGER NOT NULL CHECK(participants_in_abstract > 0),
    lower_altitude_ft INTEGER NOT NULL CHECK(lower_altitude_ft > 0),
    lower_stage_planned_min INTEGER NOT NULL CHECK(lower_stage_planned_min > 0),
    upper_altitude_ft INTEGER NOT NULL CHECK(upper_altitude_ft > lower_altitude_ft),
    upper_stage_planned_min INTEGER NOT NULL CHECK(upper_stage_planned_min > 0),
    locator TEXT NOT NULL,
    CHECK(participants_before_exclusions >= participants_in_report),
    PRIMARY KEY(source_id,series)
) STRICT;

CREATE TABLE publication_post_dive_flight_profile (
    source_id TEXT NOT NULL,
    series TEXT NOT NULL,
    stratum TEXT NOT NULL,
    clinical_endpoint TEXT NOT NULL,
    dive_schedule_as_printed TEXT NOT NULL,
    mean_dive_descent_min REAL CHECK(mean_dive_descent_min > 0),
    mean_bottom_exposure_min REAL NOT NULL CHECK(mean_bottom_exposure_min > 0),
    mean_dive_ascent_min REAL NOT NULL CHECK(mean_dive_ascent_min > 0),
    vge_abort_flights INTEGER NOT NULL CHECK(vge_abort_flights >= 0),
    vge_completed_flights INTEGER NOT NULL CHECK(vge_completed_flights >= 0),
    no_vge_flights INTEGER NOT NULL CHECK(no_vge_flights >= 0),
    lower_stage_vge INTEGER NOT NULL CHECK(lower_stage_vge >= 0),
    lower_stage_vge_aborts INTEGER NOT NULL CHECK(lower_stage_vge_aborts BETWEEN 0 AND lower_stage_vge),
    lower_stage_clinical_aborts INTEGER NOT NULL CHECK(lower_stage_clinical_aborts >= 0),
    upper_stage_entries_reconstructed INTEGER NOT NULL CHECK(upper_stage_entries_reconstructed > 0),
    upper_stage_vge INTEGER NOT NULL CHECK(upper_stage_vge BETWEEN 0 AND upper_stage_entries_reconstructed),
    upper_stage_vge_aborts INTEGER NOT NULL CHECK(upper_stage_vge_aborts BETWEEN 0 AND upper_stage_vge),
    upper_stage_clinical_aborts INTEGER NOT NULL CHECK(upper_stage_clinical_aborts >= 0),
    reported_skin_itches INTEGER NOT NULL CHECK(reported_skin_itches >= 0),
    locator TEXT NOT NULL,
    CHECK(vge_abort_flights = lower_stage_vge_aborts + upper_stage_vge_aborts),
    PRIMARY KEY(source_id,stratum),
    UNIQUE(source_id,series,dive_schedule_as_printed),
    FOREIGN KEY(source_id,series) REFERENCES publication_post_dive_series(source_id,series),
    FOREIGN KEY(source_id,stratum,clinical_endpoint)
        REFERENCES publication_observation(source_id,stratum,endpoint)
) STRICT;
