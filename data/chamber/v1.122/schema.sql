CREATE TABLE publication_interim_onset_summary (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL CHECK(endpoint IN ('dcs_as_reported','any_vge','grade_iii_iv_vge')),
    exposed_people INTEGER NOT NULL CHECK(exposed_people > 0),
    event_sample_size INTEGER CHECK(event_sample_size BETWEEN 1 AND exposed_people),
    mean_onset_min REAL NOT NULL CHECK(mean_onset_min >= 0),
    standard_deviation_min REAL NOT NULL CHECK(standard_deviation_min >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint)
) STRICT;
