CREATE TABLE publication_ultrasound_vge_context (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    clinical_endpoint TEXT NOT NULL,
    measurement_context TEXT NOT NULL CHECK(measurement_context IN ('supine_rest','after_knee_bends')),
    nominal_interval_min INTEGER NOT NULL CHECK(nominal_interval_min > 0),
    nominal_dwell_min INTEGER NOT NULL CHECK(nominal_dwell_min >= nominal_interval_min),
    grade_scale TEXT NOT NULL,
    median_grade_as_reported REAL NOT NULL CHECK(median_grade_as_reported BETWEEN 0 AND 4),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,clinical_endpoint,measurement_context),
    FOREIGN KEY(source_id,stratum,clinical_endpoint) REFERENCES publication_observation(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE publication_ultrasound_vge_maximum (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    clinical_endpoint TEXT NOT NULL,
    measurement_context TEXT NOT NULL,
    participant_ordinal INTEGER NOT NULL CHECK(participant_ordinal > 0),
    maximum_grade INTEGER NOT NULL CHECK(maximum_grade BETWEEN 0 AND 4),
    PRIMARY KEY(source_id,stratum,clinical_endpoint,measurement_context,participant_ordinal),
    FOREIGN KEY(source_id,stratum,clinical_endpoint,measurement_context)
        REFERENCES publication_ultrasound_vge_context(source_id,stratum,clinical_endpoint,measurement_context)
) STRICT;
