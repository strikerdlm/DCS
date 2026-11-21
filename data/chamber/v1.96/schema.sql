CREATE TABLE publication_duke_prebreathe_protocol (
    source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    protocol_code TEXT NOT NULL,
    phase TEXT NOT NULL CHECK(phase IN ('workshop_figure','conference_results','historical_summary')),
    prebreathe_min INTEGER CHECK(prebreathe_min > 0),
    oxygen_fraction REAL NOT NULL CHECK(oxygen_fraction > 0 AND oxygen_fraction <= 1),
    measured_washout_min INTEGER CHECK(measured_washout_min BETWEEN 1 AND prebreathe_min),
    reported_transfer_min INTEGER CHECK(reported_transfer_min BETWEEN 1 AND prebreathe_min),
    posture_and_activity TEXT NOT NULL,
    exercise_rest_min INTEGER CHECK(exercise_rest_min BETWEEN 0 AND prebreathe_min),
    target_psia REAL NOT NULL CHECK(target_psia > 0),
    ascent_min INTEGER NOT NULL CHECK(ascent_min > 0),
    planned_exposure_min INTEGER CHECK(planned_exposure_min > 0),
    historical_participants INTEGER CHECK(historical_participants > 0),
    historical_dcs_percent INTEGER CHECK(historical_dcs_percent BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    note TEXT,
    PRIMARY KEY(source_id,protocol_code),
    CHECK((phase='historical_summary') = (historical_participants IS NOT NULL)),
    CHECK((phase='historical_summary') = (historical_dcs_percent IS NOT NULL))
) STRICT;

CREATE TABLE publication_duke_prebreathe_exposure (
    source_id TEXT NOT NULL,
    protocol_code TEXT NOT NULL,
    participant_ordinal INTEGER NOT NULL CHECK(participant_ordinal > 0),
    dcs INTEGER NOT NULL CHECK(dcs IN (0,1)),
    dcs_onset_min_approx INTEGER CHECK(dcs_onset_min_approx >= 0),
    vge_grade2_or_higher INTEGER CHECK(vge_grade2_or_higher IN (0,1)),
    vge_onset_min_approx INTEGER CHECK(vge_onset_min_approx >= 0),
    vge_onset_as_printed TEXT,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,protocol_code,participant_ordinal),
    FOREIGN KEY(source_id,protocol_code) REFERENCES publication_duke_prebreathe_protocol(source_id,protocol_code),
    CHECK(dcs=1 OR dcs_onset_min_approx IS NULL),
    CHECK(vge_onset_min_approx IS NULL OR (vge_grade2_or_higher IS 1 AND vge_onset_as_printed IS NOT NULL))
) STRICT;
