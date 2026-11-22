CREATE TABLE publication_jsc_survival_profile (
    source_id TEXT NOT NULL REFERENCES publication_source,
    profile TEXT NOT NULL,
    exposures INTEGER NOT NULL CHECK(exposures > 0),
    maximum_exposure_min_as_printed INTEGER CHECK(maximum_exposure_min_as_printed > 0),
    locator TEXT NOT NULL,
    CHECK((profile='all')=(maximum_exposure_min_as_printed IS NULL)),
    PRIMARY KEY(source_id,profile)
) STRICT;

CREATE TABLE publication_jsc_survival_summary (
    source_id TEXT NOT NULL,
    profile TEXT NOT NULL,
    endpoint TEXT NOT NULL CHECK(endpoint IN ('cmb','dcs','symptom_related_forced_descent')),
    incidence_free_mean_min REAL NOT NULL CHECK(incidence_free_mean_min >= 0),
    incidence_free_se_min REAL CHECK(incidence_free_se_min >= 0),
    survival_percent_at_180_min REAL NOT NULL CHECK(survival_percent_at_180_min BETWEEN 0 AND 100),
    survival_se_at_180_min_as_printed REAL CHECK(survival_se_at_180_min_as_printed >= 0),
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,profile,endpoint),
    FOREIGN KEY(source_id,profile) REFERENCES publication_jsc_survival_profile
) STRICT;

CREATE TABLE publication_jsc_cmb_grade_outcome (
    source_id TEXT NOT NULL REFERENCES publication_source,
    maximum_spencer_grade INTEGER NOT NULL CHECK(maximum_spencer_grade BETWEEN 0 AND 4),
    with_dcs INTEGER NOT NULL CHECK(with_dcs >= 0),
    without_dcs INTEGER NOT NULL CHECK(without_dcs >= 0),
    cumulative_survival REAL NOT NULL CHECK(cumulative_survival BETWEEN 0 AND 1),
    cumulative_survival_se REAL NOT NULL CHECK(cumulative_survival_se >= 0),
    cumulative_hazard REAL NOT NULL CHECK(cumulative_hazard >= 0),
    cumulative_hazard_se REAL NOT NULL CHECK(cumulative_hazard_se >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,maximum_spencer_grade)
) STRICT;

CREATE TABLE publication_jsc_exposure_association (
    source_id TEXT NOT NULL REFERENCES publication_source,
    estimate_id TEXT NOT NULL,
    contrast TEXT NOT NULL,
    method TEXT NOT NULL,
    estimate REAL NOT NULL CHECK(estimate > 0),
    ci95_lower REAL NOT NULL CHECK(ci95_lower > 0 AND ci95_lower <= estimate),
    ci95_upper REAL NOT NULL CHECK(ci95_upper >= estimate),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,estimate_id)
) STRICT;

CREATE TABLE publication_jsc_participant_factor (
    source_id TEXT NOT NULL REFERENCES publication_source,
    outcome TEXT NOT NULL CHECK(outcome IN ('ever_dcs','ever_cmb')),
    factor TEXT NOT NULL,
    reference_label TEXT NOT NULL,
    contrast_label TEXT NOT NULL,
    reference_absent INTEGER NOT NULL CHECK(reference_absent >= 0),
    reference_present INTEGER NOT NULL CHECK(reference_present >= 0),
    contrast_absent INTEGER NOT NULL CHECK(contrast_absent >= 0),
    contrast_present INTEGER NOT NULL CHECK(contrast_present >= 0),
    reference_absent_pct_printed INTEGER NOT NULL CHECK(reference_absent_pct_printed BETWEEN 0 AND 100),
    reference_present_pct_printed INTEGER NOT NULL CHECK(reference_present_pct_printed BETWEEN 0 AND 100),
    contrast_absent_pct_printed INTEGER NOT NULL CHECK(contrast_absent_pct_printed BETWEEN 0 AND 100),
    contrast_present_pct_printed INTEGER NOT NULL CHECK(contrast_present_pct_printed BETWEEN 0 AND 100),
    crude_odds_ratio REAL NOT NULL CHECK(crude_odds_ratio > 0),
    crude_ci95_lower REAL NOT NULL CHECK(crude_ci95_lower > 0 AND crude_ci95_lower <= crude_odds_ratio),
    crude_ci95_upper REAL NOT NULL CHECK(crude_ci95_upper >= crude_odds_ratio),
    adjusted_odds_ratio REAL NOT NULL CHECK(adjusted_odds_ratio > 0),
    adjusted_ci95_lower REAL NOT NULL CHECK(adjusted_ci95_lower > 0 AND adjusted_ci95_lower <= adjusted_odds_ratio),
    adjusted_ci95_upper REAL NOT NULL CHECK(adjusted_ci95_upper >= adjusted_odds_ratio),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,outcome,factor)
) STRICT;
