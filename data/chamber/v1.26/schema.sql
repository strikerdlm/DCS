CREATE TABLE publication_chamber_participant (
    source_id TEXT NOT NULL REFERENCES publication_source,
    participant_id TEXT NOT NULL,
    age_y INTEGER CHECK(age_y > 0),
    mass_kg REAL CHECK(mass_kg > 0),
    height_cm REAL CHECK(height_cm > 0),
    specific_gravity REAL CHECK(specific_gravity > 0),
    body_fat_pct REAL CHECK(body_fat_pct BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id, participant_id)
) STRICT;

CREATE TABLE publication_chamber_trial_time (
    source_id TEXT NOT NULL,
    participant_id TEXT NOT NULL,
    exposure_label TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    stage_altitude_ft INTEGER CHECK(stage_altitude_ft > 0),
    stage_minutes INTEGER NOT NULL CHECK(stage_minutes >= 0),
    final_altitude_ft INTEGER NOT NULL CHECK(final_altitude_ft > 0),
    observation_limit_min INTEGER NOT NULL CHECK(observation_limit_min > 0),
    reported_time_pct INTEGER NOT NULL CHECK(reported_time_pct BETWEEN 0 AND 100),
    event_status TEXT NOT NULL CHECK(event_status IN ('event', 'right_censored', 'unresolved')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((stage_altitude_ft IS NULL) = (stage_minutes = 0)),
    CHECK(event_status <> 'right_censored' OR reported_time_pct = 100),
    PRIMARY KEY(source_id, participant_id, exposure_label, endpoint),
    FOREIGN KEY(source_id, participant_id) REFERENCES publication_chamber_participant
) STRICT;
