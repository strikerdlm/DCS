-- Published aviation counts remain descriptive and preserve the printed counting unit.
CREATE TABLE publication_aviation_group (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    metric TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role IN (
        'overlap_hold','overlapping_margin','exposure_profile','selected_cluster',
        'denominator_conflict','denominator_unreported'
    )),
    numerator INTEGER CHECK(numerator >= 0),
    numerator_basis TEXT CHECK(numerator_basis IN ('source_reported','enumerated_table_rows')),
    denominator INTEGER CHECK(denominator > 0 AND (numerator IS NULL OR numerator <= denominator)),
    denominator_unit TEXT NOT NULL CHECK(denominator_unit IN ('aircraft_flight','reported_decompression_event')),
    rate_as_printed TEXT,
    rate_unit TEXT CHECK(rate_unit IN ('percent','fraction')),
    outcome_window TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((numerator IS NULL) = (numerator_basis IS NULL)),
    CHECK((rate_as_printed IS NULL) = (rate_unit IS NULL)),
    CHECK(numerator IS NOT NULL OR rate_as_printed IS NOT NULL),
    CHECK((denominator IS NULL) = (analysis_role='denominator_unreported')),
    CHECK(rate_as_printed IS NULL OR (
        rate_as_printed NOT GLOB '*[^0-9.]*' AND rate_as_printed GLOB '*[0-9]*'
        AND length(rate_as_printed) - length(replace(rate_as_printed,'.','')) <= 1
        AND CAST(rate_as_printed AS REAL) BETWEEN 0 AND CASE rate_unit WHEN 'percent' THEN 100 ELSE 1 END
    )),
    PRIMARY KEY(source_id,stratum,metric)
) STRICT;

-- The paper lists the affected flights and printed crew codes. Individual records for the other flights are unavailable.
CREATE TABLE publication_meader_reported_flight (
    source_id TEXT NOT NULL REFERENCES publication_source,
    flight_no INTEGER NOT NULL CHECK(flight_no > 0),
    crew_code TEXT NOT NULL CHECK(crew_code GLOB '[A-K]'),
    preoxygenation_min INTEGER NOT NULL CHECK(preoxygenation_min > 0),
    season TEXT NOT NULL CHECK(season IN ('W','Sp','Su','F')),
    day_period TEXT CHECK(day_period IN ('AM','PM')),
    flight_hours REAL NOT NULL CHECK(flight_hours > 0),
    onset_hours REAL CHECK(onset_hours BETWEEN 0 AND flight_hours),
    peak_cabin_ft INTEGER NOT NULL CHECK(peak_cabin_ft > 0),
    peak_cabin_relation TEXT NOT NULL CHECK(peak_cabin_relation IN ('=','>')),
    hours_above_25000_ft REAL NOT NULL CHECK(hours_above_25000_ft BETWEEN 0 AND flight_hours),
    decompression_events INTEGER NOT NULL CHECK(decompression_events >= 0),
    decompression_min INTEGER CHECK(decompression_min IS NULL OR (decompression_min > 0 AND decompression_events > 0)),
    pain_location TEXT,
    printed_page INTEGER NOT NULL CHECK(printed_page > 0),
    PRIMARY KEY(source_id,flight_no)
) STRICT;
