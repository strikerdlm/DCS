CREATE TABLE publication_armstrong_probe_comparison (
    source_id TEXT NOT NULL REFERENCES publication_source,
    probe_type TEXT NOT NULL CHECK(probe_type IN ('combined_echo_doppler','separate_probes')),
    reported_subject_exposures INTEGER NOT NULL CHECK(reported_subject_exposures > 0),
    lower_altitude_ft INTEGER NOT NULL CHECK(lower_altitude_ft > 0),
    upper_altitude_ft INTEGER NOT NULL CHECK(upper_altitude_ft >= lower_altitude_ft),
    dcs_with_bubbles INTEGER NOT NULL CHECK(dcs_with_bubbles BETWEEN 0 AND dcs_total),
    dcs_total INTEGER NOT NULL CHECK(dcs_total > 0),
    non_dcs_without_bubbles INTEGER NOT NULL CHECK(non_dcs_without_bubbles BETWEEN 0 AND non_dcs_total),
    non_dcs_total INTEGER NOT NULL CHECK(non_dcs_total > 0),
    sensitivity_percent_as_printed INTEGER NOT NULL CHECK(sensitivity_percent_as_printed BETWEEN 0 AND 100),
    specificity_percent_as_printed INTEGER NOT NULL CHECK(specificity_percent_as_printed BETWEEN 0 AND 100),
    analysis_role TEXT NOT NULL CHECK(analysis_role IN ('overlap_hold','denominator_conflict')),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,probe_type),
    CHECK((dcs_total+non_dcs_total!=reported_subject_exposures) = (analysis_role='denominator_conflict'))
) STRICT;
