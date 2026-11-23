CREATE TABLE publication_ata_standard_stage (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    phase INTEGER NOT NULL CHECK(phase > 0),
    procedure TEXT NOT NULL,
    starting_altitude_ft INTEGER NOT NULL CHECK(starting_altitude_ft > 0),
    excursion_altitude_ft INTEGER CHECK(excursion_altitude_ft > 0),
    ending_altitude_ft INTEGER NOT NULL CHECK(ending_altitude_ft > 0),
    vertical_rate_ft_per_min INTEGER CHECK(vertical_rate_ft_per_min > 0),
    nominal_pressure_mmhg REAL CHECK(nominal_pressure_mmhg > 0),
    nominal_pressure_kpa REAL CHECK(nominal_pressure_kpa > 0),
    mask_on INTEGER NOT NULL CHECK(mask_on IN (0,1)),
    intended_oxygen_pct REAL NOT NULL CHECK(intended_oxygen_pct BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint,phase),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;

CREATE TABLE publication_ata_cluster_case (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    local_case_code TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('trainee','inside_observer')),
    age_years INTEGER NOT NULL CHECK(age_years > 0),
    joint_pain_site TEXT NOT NULL,
    onset_phase TEXT NOT NULL,
    time_of_useful_consciousness_sec INTEGER CHECK(time_of_useful_consciousness_sec > 0),
    treatment_start_within_min_after_ground INTEGER NOT NULL CHECK(treatment_start_within_min_after_ground > 0),
    outcome TEXT NOT NULL,
    investigation_note TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint,local_case_code),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;
