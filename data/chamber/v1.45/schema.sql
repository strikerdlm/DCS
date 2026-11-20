CREATE TABLE publication_adrac_profile_inventory (
    source_id TEXT NOT NULL REFERENCES publication_source,
    profile TEXT NOT NULL,
    printed_subject_n INTEGER NOT NULL CHECK(printed_subject_n > 0),
    nedu_profile TEXT REFERENCES a1309_profile(profile),
    locator TEXT NOT NULL,
    PRIMARY KEY (source_id, profile)
) STRICT;

CREATE TABLE publication_archive_protocol_summary (
    source_id TEXT NOT NULL REFERENCES publication_source,
    protocol_family TEXT NOT NULL,
    stratum TEXT NOT NULL,
    row_basis TEXT NOT NULL CHECK(row_basis IN ('protocol_group', 'reported_mean')),
    target_altitude_ft INTEGER NOT NULL CHECK(target_altitude_ft > 0),
    planned_duration_min INTEGER NOT NULL CHECK(planned_duration_min > 0),
    prebreathe_altitude_ft INTEGER CHECK(prebreathe_altitude_ft >= 0),
    prebreathe_min INTEGER NOT NULL CHECK(prebreathe_min >= 0),
    exposure_oxygen_pct INTEGER NOT NULL CHECK(exposure_oxygen_pct BETWEEN 0 AND 100),
    reported_participants INTEGER CHECK(reported_participants > 0),
    reported_exposures INTEGER CHECK(reported_exposures >= coalesce(reported_participants, 1)),
    reported_dcs_pct REAL NOT NULL CHECK(reported_dcs_pct BETWEEN 0 AND 100),
    reported_any_vge_pct REAL CHECK(reported_any_vge_pct BETWEEN 0 AND 100),
    reported_spencer_iii_iv_pct REAL CHECK(reported_spencer_iii_iv_pct BETWEEN 0 AND 100),
    reported_spencer_i_ii_pct REAL CHECK(reported_spencer_i_ii_pct BETWEEN 0 AND 100),
    reported_mean_dcs_min INTEGER CHECK(reported_mean_dcs_min BETWEEN 0 AND planned_duration_min),
    candidate_nedu_profile TEXT REFERENCES a1309_profile(profile),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY (source_id, protocol_family, stratum)
) STRICT;

-- Attach source-reported details to an event within an existing outcome row.
CREATE TABLE literature_observation_case_annotation (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    case_ordinal INTEGER NOT NULL CHECK(case_ordinal > 0),
    evidence_source_id TEXT NOT NULL REFERENCES publication_source,
    stage_altitude_ft INTEGER NOT NULL CHECK(stage_altitude_ft > 0),
    planned_stage_min INTEGER NOT NULL CHECK(planned_stage_min > 0),
    onset_min_since_stage_arrival INTEGER NOT NULL
        CHECK(onset_min_since_stage_arrival BETWEEN 0 AND planned_stage_min),
    reported_feature TEXT NOT NULL,
    resolution_phase TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY (source_id, stratum, endpoint, case_ordinal, evidence_source_id),
    FOREIGN KEY (source_id, stratum, endpoint)
        REFERENCES literature_observation(source_id, stratum, endpoint)
) STRICT;
