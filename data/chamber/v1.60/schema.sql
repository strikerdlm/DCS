CREATE TABLE publication_paired_chamber_arm (
    source_id TEXT NOT NULL REFERENCES publication_source,
    arm TEXT NOT NULL,
    shared_cohort_key TEXT NOT NULL,
    participant_count INTEGER NOT NULL CHECK(participant_count > 0),
    target_altitude_ft INTEGER NOT NULL CHECK(target_altitude_ft > 0),
    planned_window_min INTEGER NOT NULL CHECK(planned_window_min > 0),
    window_origin TEXT NOT NULL,
    protocol TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role='overlap_hold'),
    PRIMARY KEY(source_id,arm)
) STRICT;

CREATE TABLE publication_paired_chamber_count (
    source_id TEXT NOT NULL,
    arm TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    window_end_min INTEGER NOT NULL CHECK(window_end_min > 0),
    cumulative_count INTEGER NOT NULL CHECK(cumulative_count >= 0),
    printed_page INTEGER NOT NULL CHECK(printed_page > 0),
    PRIMARY KEY(source_id,arm,endpoint,window_end_min),
    FOREIGN KEY(source_id,arm) REFERENCES publication_paired_chamber_arm
) STRICT;

CREATE TABLE publication_narrative_chamber_rate (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    reported_percent TEXT NOT NULL CHECK(
        reported_percent NOT GLOB '*[^0-9.]*'
        AND reported_percent GLOB '*[0-9]*'
        AND length(reported_percent) - length(replace(reported_percent,'.','')) <= 1
        AND CAST(reported_percent AS REAL) BETWEEN 0 AND 100
    ),
    source_denominator INTEGER CHECK(source_denominator > 0),
    target_altitude_ft INTEGER NOT NULL CHECK(target_altitude_ft > 0),
    planned_dwell_min INTEGER NOT NULL CHECK(planned_dwell_min > 0),
    reported_preoxygenation_total_min INTEGER CHECK(reported_preoxygenation_total_min > 0),
    printed_page INTEGER NOT NULL CHECK(printed_page > 0),
    note TEXT NOT NULL,
    analysis_role TEXT NOT NULL DEFAULT 'overlap_hold' CHECK(analysis_role='overlap_hold'),
    PRIMARY KEY(source_id,stratum,endpoint)
) STRICT;
