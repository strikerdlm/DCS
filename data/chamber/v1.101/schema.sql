CREATE TABLE publication_repeat_chamber_protocol_count (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    repeat_runs INTEGER NOT NULL CHECK(repeat_runs > 0),
    altitude_min_m INTEGER NOT NULL CHECK(altitude_min_m > 0),
    altitude_max_m INTEGER NOT NULL CHECK(altitude_max_m >= altitude_min_m),
    prebreathe_min_min INTEGER NOT NULL CHECK(prebreathe_min_min >= 0),
    prebreathe_max_min INTEGER NOT NULL CHECK(prebreathe_max_min >= prebreathe_min_min),
    population TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum)
) STRICT;

CREATE TABLE publication_biomarker_summary (
    source_id TEXT NOT NULL REFERENCES publication_source,
    analyte TEXT NOT NULL,
    assay TEXT NOT NULL,
    unit TEXT NOT NULL,
    reported_n INTEGER CHECK(reported_n > 0),
    baseline_mean REAL CHECK(baseline_mean >= 0),
    baseline_se REAL CHECK(baseline_se >= 0),
    t8_mean REAL CHECK(t8_mean >= 0),
    t8_se REAL CHECK(t8_se >= 0),
    t24_mean REAL CHECK(t24_mean >= 0),
    t24_se REAL CHECK(t24_se >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,analyte),
    CHECK (
        (baseline_mean IS NULL AND baseline_se IS NULL AND t8_mean IS NULL
         AND t8_se IS NULL AND t24_mean IS NULL AND t24_se IS NULL)
        OR
        (baseline_mean IS NOT NULL AND baseline_se IS NOT NULL AND t8_mean IS NOT NULL
         AND t8_se IS NOT NULL AND t24_mean IS NOT NULL AND t24_se IS NOT NULL)
    )
) STRICT;
