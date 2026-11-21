CREATE TABLE publication_postexercise_flow (
    source_id TEXT NOT NULL REFERENCES publication_source,
    group_id TEXT NOT NULL,
    parent_group_id TEXT,
    population_count INTEGER NOT NULL CHECK(population_count > 0),
    dcs_during_exposure INTEGER CHECK(dcs_during_exposure BETWEEN 0 AND population_count),
    vge_count_as_reported INTEGER CHECK(vge_count_as_reported BETWEEN 0 AND population_count),
    postexposure_dcs INTEGER CHECK(postexposure_dcs BETWEEN 0 AND population_count),
    assignment TEXT CHECK(assignment IN ('exercise','rest','excluded_before_allocation')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,group_id),
    FOREIGN KEY(source_id,parent_group_id) REFERENCES publication_postexercise_flow,
    CHECK(parent_group_id IS NULL OR parent_group_id != group_id),
    CHECK(postexposure_dcs IS NULL OR assignment IS 'exercise' OR assignment IS 'rest')
) STRICT;

CREATE TABLE publication_repeated_exposure_timing (
    preliminary_source_id TEXT NOT NULL REFERENCES publication_source,
    final_source_id TEXT NOT NULL REFERENCES web_source,
    condition TEXT NOT NULL CHECK(condition IN ('A','B','C')),
    endpoint TEXT NOT NULL CHECK(endpoint IN ('dcs','any_vge')),
    protocol_sessions INTEGER NOT NULL CHECK(protocol_sessions > 0),
    matched_event_count INTEGER NOT NULL CHECK(matched_event_count BETWEEN 0 AND protocol_sessions),
    preliminary_mean_min REAL NOT NULL CHECK(preliminary_mean_min >= 0),
    preliminary_plus_minus_min REAL NOT NULL CHECK(preliminary_plus_minus_min >= 0),
    final_mean_min REAL NOT NULL CHECK(final_mean_min >= 0),
    final_plus_minus_min REAL NOT NULL CHECK(final_plus_minus_min >= 0),
    preliminary_locator TEXT NOT NULL,
    final_locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(preliminary_source_id,final_source_id,condition,endpoint)
) STRICT;

CREATE TABLE publication_repeated_exposure_joint_count (
    source_id TEXT NOT NULL REFERENCES web_source,
    dcs_condition_a INTEGER NOT NULL CHECK(dcs_condition_a IN (0,1)),
    dcs_condition_b INTEGER NOT NULL CHECK(dcs_condition_b IN (0,1)),
    dcs_condition_c INTEGER NOT NULL CHECK(dcs_condition_c IN (0,1)),
    participants INTEGER NOT NULL CHECK(participants >= 0),
    locator TEXT NOT NULL,
    reconstruction_basis TEXT NOT NULL,
    PRIMARY KEY(source_id,dcs_condition_a,dcs_condition_b,dcs_condition_c)
) STRICT;
