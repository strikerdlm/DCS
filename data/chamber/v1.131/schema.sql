CREATE TABLE publication_chamber_proportion_without_counts (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    reported_percent_lower REAL NOT NULL CHECK(reported_percent_lower BETWEEN 0 AND 100),
    reported_percent_upper REAL NOT NULL CHECK(reported_percent_upper BETWEEN reported_percent_lower AND 100),
    protocol TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint)
) STRICT;
