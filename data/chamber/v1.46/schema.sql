CREATE TABLE publication_joint_dcs_vge (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    clinical_endpoint TEXT NOT NULL CHECK(clinical_endpoint = 'dcs'),
    vge_definition TEXT NOT NULL CHECK(vge_definition IN ('any_vge','grade_iv_vge')),
    dcs_with_vge INTEGER NOT NULL CHECK(dcs_with_vge >= 0),
    no_dcs_with_vge INTEGER NOT NULL CHECK(no_dcs_with_vge >= 0),
    dcs_without_vge INTEGER NOT NULL CHECK(dcs_without_vge >= 0),
    no_dcs_without_vge INTEGER NOT NULL CHECK(no_dcs_without_vge >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY (source_id, stratum, clinical_endpoint, vge_definition),
    FOREIGN KEY (source_id, stratum, clinical_endpoint)
        REFERENCES publication_observation(source_id, stratum, endpoint)
) STRICT;

CREATE TABLE publication_validation_snapshot (
    source_id TEXT NOT NULL REFERENCES publication_source,
    source_profile TEXT NOT NULL,
    nedu_profile TEXT NOT NULL REFERENCES a1309_profile(profile),
    later_journal_profile TEXT NOT NULL,
    altitude_ft INTEGER NOT NULL CHECK(altitude_ft > 0),
    preoxygenation_min INTEGER NOT NULL CHECK(preoxygenation_min >= 0),
    exercise_label TEXT NOT NULL,
    reported_design_exposures INTEGER NOT NULL CHECK(reported_design_exposures > 0),
    predicted_dcs_pct REAL NOT NULL CHECK(predicted_dcs_pct BETWEEN 0 AND 100),
    reported_actual_dcs_pct REAL NOT NULL CHECK(reported_actual_dcs_pct BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    PRIMARY KEY (source_id, source_profile),
    UNIQUE (source_id, nedu_profile)
) STRICT;
