-- These are source-level checks of raw channel coverage. There is no clinical row for a trace.
CREATE TABLE publication_chamber_pressure_trace_audit (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    archive_url TEXT NOT NULL,
    archive_sha256 TEXT NOT NULL CHECK(length(archive_sha256) = 64),
    files_checked INTEGER NOT NULL CHECK(files_checked > 0),
    sample_count INTEGER NOT NULL CHECK(sample_count > 0),
    invalid_samples INTEGER NOT NULL CHECK(invalid_samples BETWEEN 0 AND sample_count),
    nonincreasing_clock_intervals INTEGER NOT NULL CHECK(nonincreasing_clock_intervals >= 0),
    recorded_gaps_gt_0_1s INTEGER NOT NULL CHECK(recorded_gaps_gt_0_1s >= 0),
    files_with_altitude_at_least_44000_ft INTEGER NOT NULL
        CHECK(files_with_altitude_at_least_44000_ft BETWEEN 0 AND files_checked),
    shortest_logged_seconds REAL NOT NULL CHECK(shortest_logged_seconds > 0),
    longest_logged_seconds REAL NOT NULL CHECK(longest_logged_seconds >= shortest_logged_seconds),
    lowest_absolute_pressure_psi REAL NOT NULL CHECK(lowest_absolute_pressure_psi > 0),
    lowest_trace_peak_altitude_ft REAL NOT NULL CHECK(lowest_trace_peak_altitude_ft > 0),
    highest_trace_peak_altitude_ft REAL NOT NULL
        CHECK(highest_trace_peak_altitude_ft >= lowest_trace_peak_altitude_ft),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum),
    FOREIGN KEY(source_id,stratum) REFERENCES publication_chamber_trial_scope
) STRICT;
