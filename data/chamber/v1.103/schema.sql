CREATE TABLE publication_observation_denominator_completion (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    evidence_source_id TEXT NOT NULL REFERENCES publication_source,
    numerator INTEGER NOT NULL CHECK(numerator >= 0),
    denominator INTEGER NOT NULL CHECK(denominator > 0 AND denominator >= numerator),
    denominator_unit TEXT NOT NULL CHECK(denominator_unit IN (
        'person_exposure','trainee_exposure','observer_exposure','person',
        'dcs_case','pulmonary_dcs_case','treated_referral','symptom_report'
    )),
    period TEXT,
    protocol TEXT NOT NULL,
    outcome_window TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;
