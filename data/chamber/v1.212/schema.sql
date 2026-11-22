CREATE TABLE publication_chamber_planned_exposure (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    reference_endpoint TEXT NOT NULL,
    chamber_role TEXT NOT NULL CHECK(chamber_role IN ('research_subject','inside_observer')),
    planned_altitude_duration_min INTEGER NOT NULL CHECK(planned_altitude_duration_min > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum),
    FOREIGN KEY(source_id,stratum,reference_endpoint) REFERENCES publication_observation(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE publication_chamber_onset_mean_sem (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL CHECK(endpoint IN ('dcs_symptoms_as_reported','any_vge_as_reported')),
    mean_onset_min REAL NOT NULL CHECK(mean_onset_min >= 0),
    standard_error_min REAL NOT NULL CHECK(standard_error_min >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation(source_id,stratum,endpoint)
) STRICT;
