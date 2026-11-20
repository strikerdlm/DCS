CREATE TABLE publication_trial_case_profile (
    source_id TEXT NOT NULL REFERENCES publication_source,
    case_number INTEGER NOT NULL CHECK(case_number > 0),
    trial_source_id TEXT NOT NULL,
    trial_stratum TEXT NOT NULL,
    trial_endpoint TEXT NOT NULL,
    linkage TEXT NOT NULL CHECK(linkage IN ('likely_same_episode','confirmed_same_episode')),
    saturation_pressure_psia REAL NOT NULL CHECK(saturation_pressure_psia > 0),
    saturation_oxygen_percent REAL NOT NULL CHECK(saturation_oxygen_percent BETWEEN 0 AND 100),
    prebreathe_min INTEGER NOT NULL CHECK(prebreathe_min >= 0),
    prebreathe_oxygen_percent REAL NOT NULL CHECK(prebreathe_oxygen_percent BETWEEN 0 AND 100),
    nominal_target_psia REAL NOT NULL CHECK(nominal_target_psia > 0),
    decompression_min INTEGER NOT NULL CHECK(decompression_min > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,case_number),
    FOREIGN KEY(trial_source_id,trial_stratum,trial_endpoint)
        REFERENCES discovery_observation(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE publication_trial_case_milestone (
    source_id TEXT NOT NULL,
    case_number INTEGER NOT NULL,
    milestone TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK(event_type IN (
        'systemic_bubble_detection','symptom_report','neurological_exam','symptom_resolution','followup_exam'
    )),
    elapsed_from_target_min INTEGER CHECK(elapsed_from_target_min >= 0),
    time_basis TEXT NOT NULL CHECK(time_basis IN (
        'at_target_elapsed','approximate_target_elapsed','during_eva_unspecified','during_repressurization','next_day'
    )),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((elapsed_from_target_min IS NOT NULL) = (time_basis IN ('at_target_elapsed','approximate_target_elapsed'))),
    PRIMARY KEY(source_id,case_number,milestone),
    FOREIGN KEY(source_id,case_number) REFERENCES publication_trial_case_profile
) STRICT;
