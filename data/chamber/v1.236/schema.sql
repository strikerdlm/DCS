CREATE TABLE literature_hdsd_primary_rate_link (
    source_id TEXT NOT NULL,
    report_number INTEGER NOT NULL,
    archive_endpoint TEXT NOT NULL CHECK(archive_endpoint IN ('dcs_pct','serious_dcs_pct')),
    primary_source_id TEXT NOT NULL,
    primary_stratum TEXT NOT NULL,
    primary_endpoint TEXT NOT NULL,
    relationship TEXT NOT NULL CHECK(relationship = 'same_profile_and_denominator_endpoint_conflict'),
    evidence TEXT NOT NULL,
    PRIMARY KEY(source_id,report_number,archive_endpoint,primary_source_id,primary_stratum,primary_endpoint),
    FOREIGN KEY(source_id,report_number) REFERENCES literature_hdsd_compilation,
    FOREIGN KEY(primary_source_id,primary_stratum,primary_endpoint) REFERENCES publication_reported_rate
) STRICT;
