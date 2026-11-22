CREATE TABLE publication_chamber_composite_trial (
    source_id TEXT NOT NULL REFERENCES publication_source,
    experiment_no INTEGER NOT NULL CHECK (experiment_no > 0),
    print_order INTEGER NOT NULL CHECK (print_order > 0),
    date_as_printed TEXT NOT NULL,
    oxygen_percent_as_printed TEXT NOT NULL,
    preparation_duration_min INTEGER CHECK (preparation_duration_min > 0),
    preparation_altitude_as_printed TEXT NOT NULL,
    planned_chamber_altitude_ft INTEGER NOT NULL CHECK (planned_chamber_altitude_ft > 0),
    planned_chamber_duration_min INTEGER NOT NULL CHECK (planned_chamber_duration_min > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY (source_id, experiment_no),
    UNIQUE (source_id, print_order)
) STRICT;

CREATE TABLE publication_chamber_composite_score (
    source_id TEXT NOT NULL,
    experiment_no INTEGER NOT NULL,
    subject_no INTEGER NOT NULL CHECK (subject_no BETWEEN 1 AND 4),
    score_as_printed TEXT NOT NULL,
    score_points INTEGER CHECK (score_points BETWEEN 0 AND 360),
    PRIMARY KEY (source_id, experiment_no, subject_no),
    FOREIGN KEY (source_id, experiment_no) REFERENCES publication_chamber_composite_trial,
    CHECK ((score_as_printed = '--') = (score_points IS NULL))
) STRICT;

CREATE TABLE publication_chamber_oxygen_flow (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    sample_no INTEGER NOT NULL CHECK (sample_no > 0),
    clock_as_printed TEXT NOT NULL,
    setting TEXT NOT NULL CHECK (setting IN ('ground', 'chamber', 'descent_start')),
    reported_altitude_ft INTEGER CHECK (reported_altitude_ft > 0),
    target_o2_l_min_stpd REAL CHECK (target_o2_l_min_stpd > 0),
    delivered_o2_l_min_stpd REAL CHECK (delivered_o2_l_min_stpd > 0),
    alveolar_co2_a_mmhg INTEGER CHECK (alveolar_co2_a_mmhg > 0),
    alveolar_co2_b_mmhg INTEGER CHECK (alveolar_co2_b_mmhg > 0),
    alveolar_o2_a_mmhg INTEGER CHECK (alveolar_o2_a_mmhg > 0),
    alveolar_o2_b_mmhg INTEGER CHECK (alveolar_o2_b_mmhg > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY (source_id, stratum, endpoint, sample_no),
    FOREIGN KEY (source_id, stratum, endpoint) REFERENCES publication_observation,
    CHECK ((setting = 'chamber') = (reported_altitude_ft IS NOT NULL))
) STRICT;
