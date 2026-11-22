CREATE TABLE publication_sam216_group (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    label TEXT NOT NULL,
    person_exposures INTEGER NOT NULL CHECK(person_exposures > 0),
    planned_peak_min INTEGER CHECK(planned_peak_min > 0),
    descent_window_min INTEGER NOT NULL CHECK(
        descent_window_min > 0 AND (planned_peak_min IS NULL OR descent_window_min <= planned_peak_min)
    ),
    oxygen_stop_ft INTEGER CHECK(oxygen_stop_ft >= 0),
    oxygen_stop_min INTEGER CHECK(oxygen_stop_min > 0),
    mean_min_to_descent_for_severe_bends INTEGER NOT NULL CHECK(
        mean_min_to_descent_for_severe_bends BETWEEN 0 AND descent_window_min
    ),
    bends_or_chokes_descent_percent REAL NOT NULL CHECK(bends_or_chokes_descent_percent BETWEEN 0 AND 100),
    reported_se_percentage_points REAL CHECK(reported_se_percentage_points >= 0),
    reported_protection_percent REAL CHECK(reported_protection_percent <= 100),
    narrative_comparison_percent REAL CHECK(narrative_comparison_percent BETWEEN 0 AND 100),
    linked_rate_source_id TEXT,
    linked_rate_stratum TEXT,
    linked_rate_endpoint TEXT CHECK(linked_rate_endpoint='descent_any_recorded_cause'),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((oxygen_stop_ft IS NULL)=(oxygen_stop_min IS NULL)),
    CHECK((linked_rate_source_id IS NULL)=(linked_rate_stratum IS NULL)
      AND (linked_rate_source_id IS NULL)=(linked_rate_endpoint IS NULL)),
    PRIMARY KEY(source_id,stratum),
    FOREIGN KEY(linked_rate_source_id,linked_rate_stratum,linked_rate_endpoint)
        REFERENCES publication_reported_rate(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE publication_sam216_group_membership (
    source_id TEXT NOT NULL,
    pooled_stratum TEXT NOT NULL,
    member_stratum TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,pooled_stratum,member_stratum),
    CHECK(pooled_stratum<>member_stratum),
    FOREIGN KEY(source_id,pooled_stratum) REFERENCES publication_sam216_group,
    FOREIGN KEY(source_id,member_stratum) REFERENCES publication_sam216_group
) STRICT;

CREATE TABLE publication_sam253_postflight_pressure (
    source_id TEXT NOT NULL REFERENCES publication_source,
    historical_bends_grade INTEGER NOT NULL CHECK(historical_bends_grade IN (3,4)),
    minutes_after_descent INTEGER NOT NULL CHECK(minutes_after_descent BETWEEN 0 AND 120),
    positive_pressure_n INTEGER NOT NULL CHECK(positive_pressure_n > 0),
    positive_pressure_mean_mm_hg REAL NOT NULL CHECK(positive_pressure_mean_mm_hg > 0),
    demand_n INTEGER NOT NULL CHECK(demand_n > 0),
    demand_mean_mm_hg REAL NOT NULL CHECK(demand_mean_mm_hg > 0),
    difference_as_printed_mm_hg REAL,
    difference_se_mm_hg REAL CHECK(difference_se_mm_hg >= 0),
    probability_lower REAL CHECK(probability_lower BETWEEN 0 AND 1),
    probability_upper REAL CHECK(probability_upper BETWEEN probability_lower AND 1),
    locator TEXT NOT NULL,
    CHECK((difference_as_printed_mm_hg IS NULL)=(difference_se_mm_hg IS NULL)),
    CHECK((probability_lower IS NULL)=(probability_upper IS NULL)),
    PRIMARY KEY(source_id,historical_bends_grade,minutes_after_descent)
) STRICT;

CREATE TABLE publication_sam253_postflight_lab (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    analyte_as_printed TEXT NOT NULL,
    minutes_after_descent INTEGER NOT NULL CHECK(minutes_after_descent IN (0,120,240)),
    sample_count INTEGER NOT NULL CHECK(sample_count > 0),
    printed_mean REAL CHECK(printed_mean > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,analyte_as_printed,minutes_after_descent)
) STRICT;
