CREATE TABLE publication_historical_workload_margin (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    cited_source_id TEXT NOT NULL REFERENCES publication_source,
    condition_as_reported TEXT NOT NULL CHECK(condition_as_reported IN ('exercise','no-exercise')),
    affected_count INTEGER CHECK(affected_count >= 0),
    unaffected_count INTEGER CHECK(unaffected_count >= 0),
    reported_dcs_percent INTEGER NOT NULL CHECK(reported_dcs_percent BETWEEN 0 AND 100),
    reported_no_dcs_percent INTEGER CHECK(reported_no_dcs_percent BETWEEN 0 AND 100),
    denominator_unit TEXT CHECK(denominator_unit IN ('man_flight')),
    target_altitude_ft INTEGER CHECK(target_altitude_ft > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    analysis_role TEXT NOT NULL DEFAULT 'overlap_hold' CHECK(analysis_role = 'overlap_hold'),
    PRIMARY KEY(source_id,stratum),
    CHECK((affected_count IS NULL) = (unaffected_count IS NULL)),
    CHECK(affected_count + unaffected_count > 0)
) STRICT;
