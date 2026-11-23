CREATE TABLE publication_source_count_pair (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    period TEXT NOT NULL,
    numerator INTEGER NOT NULL CHECK (numerator >= 0),
    reported_denominator INTEGER NOT NULL CHECK (reported_denominator > 0),
    reported_denominator_label TEXT NOT NULL CHECK (length(reported_denominator_label) > 0),
    denominator_unit TEXT NOT NULL,
    outcome_window TEXT,
    analysis_role TEXT NOT NULL CHECK (analysis_role IN ('descriptive', 'overlap_hold')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY (source_id, stratum, endpoint, period)
);
