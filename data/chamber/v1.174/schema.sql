-- A digitized published curve provides descriptive percentages only.
-- It cannot establish clinical numerator, risk set, or censoring.
CREATE TABLE publication_chamber_time_curve (
    source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    series TEXT NOT NULL CHECK(series IN ('all', 'mild', 'moderate', 'severe')),
    minute_at_altitude INTEGER NOT NULL CHECK(minute_at_altitude > 0),
    target_altitude_ft INTEGER NOT NULL CHECK(target_altitude_ft > 0),
    prebreathe_min INTEGER NOT NULL CHECK(prebreathe_min >= 0),
    activity TEXT NOT NULL,
    digitized_percent REAL NOT NULL CHECK(digitized_percent BETWEEN 0 AND 100),
    printed_percent REAL CHECK(printed_percent BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id, series, minute_at_altitude)
) STRICT;
