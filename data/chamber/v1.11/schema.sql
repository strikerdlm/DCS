CREATE TABLE publication_reported_rate (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role IN (
        'descriptive','overlapping_margin','overlap_hold','selected_cluster'
    )),
    reported_percent TEXT NOT NULL CHECK(
        reported_percent NOT GLOB '*[^0-9.]*'
        AND reported_percent GLOB '*[0-9]*'
        AND length(reported_percent) - length(replace(reported_percent,'.','')) <= 1
        AND CAST(reported_percent AS REAL) BETWEEN 0 AND 100
    ),
    denominator INTEGER NOT NULL CHECK(denominator > 0),
    denominator_unit TEXT NOT NULL CHECK(denominator_unit IN (
        'person_exposure','trainee_record','person'
    )),
    target_altitude_ft INTEGER CHECK(target_altitude_ft > 0),
    target_duration_min INTEGER CHECK(target_duration_min > 0),
    prebreathe_min INTEGER CHECK(prebreathe_min >= 0),
    chamber_temperature_f INTEGER,
    protocol TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint)
) STRICT;

UPDATE publication_source
SET disposition='extracted',
    locator='Original cold-chamber cohort, pp. 6–7; additional historical citations in the review',
    note='The original Pensacola arm-mixed cohort is reported on pp. 6–7. Earlier cited cohorts remain linked through the source crosswalk.'
WHERE source_id='smedal48_review';
