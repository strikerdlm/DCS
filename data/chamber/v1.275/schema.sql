CREATE TABLE publication_rice05_timing_summary (
    source_id TEXT NOT NULL REFERENCES discovery_source,
    clinical_group TEXT NOT NULL CHECK(clinical_group IN (
        'type_i','paresthesia_only','other_type_ii'
    )),
    metric TEXT NOT NULL CHECK(metric IN ('symptom_resolution','time_to_treatment')),
    unit TEXT NOT NULL CHECK(
        (metric='symptom_resolution' AND unit='min') OR
        (metric='time_to_treatment' AND unit='h')
    ),
    table_group_cases INTEGER NOT NULL CHECK(table_group_cases > 0),
    timing_observed_n INTEGER CHECK(timing_observed_n BETWEEN 0 AND table_group_cases),
    reported_missing_n INTEGER CHECK(reported_missing_n BETWEEN 0 AND table_group_cases),
    table_mean REAL NOT NULL CHECK(table_mean >= 0),
    table_sd REAL NOT NULL CHECK(table_sd >= 0),
    table_median REAL NOT NULL CHECK(table_median >= 0),
    reported_ci_lower REAL CHECK(reported_ci_lower >= 0),
    reported_ci_upper REAL CHECK(reported_ci_upper >= reported_ci_lower),
    ci_print TEXT NOT NULL,
    results_mean REAL CHECK(results_mean >= 0),
    discussion_mean REAL CHECK(discussion_mean >= 0),
    period TEXT NOT NULL,
    outcome_window TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,clinical_group,metric)
) STRICT;
