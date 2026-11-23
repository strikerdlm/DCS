CREATE TABLE publication_conkin_fitness_summary (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    reported_male_n INTEGER NOT NULL CHECK(reported_male_n >= 0),
    reported_female_n INTEGER NOT NULL CHECK(reported_female_n >= 0),
    mean_peak_vo2_ml_kg_min REAL NOT NULL CHECK(mean_peak_vo2_ml_kg_min > 0),
    sd_peak_vo2_ml_kg_min REAL NOT NULL CHECK(sd_peak_vo2_ml_kg_min >= 0),
    mean_age_years REAL NOT NULL CHECK(mean_age_years > 0),
    mean_exposure_pressure_psia REAL NOT NULL CHECK(mean_exposure_pressure_psia > 0),
    mean_exposure_duration_min INTEGER NOT NULL CHECK(mean_exposure_duration_min > 0),
    reported_ambulation_pct REAL NOT NULL CHECK(reported_ambulation_pct BETWEEN 0 AND 100),
    table_dcs_pct REAL NOT NULL CHECK(table_dcs_pct BETWEEN 0 AND 100),
    figure_caption_dcs_pct REAL NOT NULL CHECK(figure_caption_dcs_pct BETWEEN 0 AND 100),
    reported_vge_pct REAL NOT NULL CHECK(reported_vge_pct BETWEEN 0 AND 100),
    mean_dcs_onset_min INTEGER NOT NULL CHECK(mean_dcs_onset_min >= 0),
    mean_vge_onset_min INTEGER NOT NULL CHECK(mean_vge_onset_min >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;

CREATE TABLE publication_conkin_fitness_association (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK(outcome IN ('dcs','vge')),
    log_odds_coefficient_per_ml_kg_min REAL NOT NULL,
    abstract_p_value REAL NOT NULL CHECK(abstract_p_value BETWEEN 0 AND 1),
    figure_caption_p_value REAL CHECK(figure_caption_p_value BETWEEN 0 AND 1),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,outcome),
    FOREIGN KEY(source_id,stratum) REFERENCES publication_conkin_fitness_summary
) STRICT;
