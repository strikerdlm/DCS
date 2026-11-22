CREATE TABLE publication_chamber_crew_training (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    person_endpoint TEXT NOT NULL,
    distinct_crews INTEGER NOT NULL CHECK(distinct_crews > 0),
    chamber_crew_runs INTEGER NOT NULL CHECK(chamber_crew_runs >= distinct_crews),
    reported_person_exposures INTEGER NOT NULL CHECK(reported_person_exposures >= chamber_crew_runs),
    jeopardized_crew_runs INTEGER NOT NULL CHECK(jeopardized_crew_runs >= 0),
    other_crew_runs INTEGER NOT NULL CHECK(other_crew_runs >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum),
    FOREIGN KEY(source_id,stratum,person_endpoint) REFERENCES publication_observation,
    CHECK(chamber_crew_runs = jeopardized_crew_runs + other_crew_runs)
) STRICT;

CREATE TABLE publication_chamber_crew_run (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    run_number INTEGER NOT NULL CHECK(run_number > 0),
    squadron INTEGER NOT NULL CHECK(squadron > 0),
    crew_number INTEGER NOT NULL CHECK(crew_number > 0),
    exposure_date TEXT NOT NULL,
    reported_peak_ft INTEGER NOT NULL CHECK(reported_peak_ft > 0),
    log_assessment TEXT NOT NULL CHECK(log_assessment IN (
        'incapacitation_with_mission_effect',
        'pain_forced_descent_mission_unrated',
        'other_or_qualified_mission_effect',
        'no_serious_bends_effect_reported'
    )),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,run_number),
    FOREIGN KEY(source_id,stratum) REFERENCES publication_chamber_crew_training
) STRICT;
