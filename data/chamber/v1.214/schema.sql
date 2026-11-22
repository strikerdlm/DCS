CREATE TABLE publication_hdsd_calibration_bin (
    source_id TEXT NOT NULL REFERENCES publication_source,
    comparison_source_id TEXT NOT NULL REFERENCES publication_source,
    lower_probability_pct INTEGER NOT NULL CHECK(lower_probability_pct BETWEEN 0 AND 90 AND lower_probability_pct % 10 = 0),
    upper_probability_pct INTEGER NOT NULL CHECK(upper_probability_pct = lower_probability_pct + 10),
    observed_dcs_cases INTEGER NOT NULL CHECK(observed_dcs_cases >= 0),
    journal_denominator INTEGER NOT NULL CHECK(journal_denominator > 0 AND journal_denominator >= observed_dcs_cases),
    nasa_denominator_as_printed INTEGER NOT NULL CHECK(nasa_denominator_as_printed > 0 AND nasa_denominator_as_printed >= observed_dcs_cases),
    analysis_role TEXT NOT NULL CHECK(analysis_role = 'in_sample_with_vge_observed_during_exposure'),
    journal_locator TEXT NOT NULL,
    nasa_locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK(source_id <> comparison_source_id),
    PRIMARY KEY(source_id,lower_probability_pct)
) STRICT;
