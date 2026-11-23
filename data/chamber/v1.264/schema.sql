CREATE TABLE publication_chamber_test_record_outcome (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role = 'overlap_hold'),
    cases INTEGER NOT NULL CHECK(cases >= 0),
    test_records INTEGER NOT NULL CHECK(test_records > 0 AND cases <= test_records),
    reported_percent REAL NOT NULL CHECK(reported_percent BETWEEN 0 AND 100),
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL CHECK(period_end >= period_start),
    target_altitude_m INTEGER NOT NULL CHECK(target_altitude_m > 0),
    planned_hold_min INTEGER NOT NULL CHECK(planned_hold_min > 0),
    protocol TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id, stratum, endpoint)
) STRICT;

UPDATE publication_source
SET url = 'https://babel.hathitrust.org/cgi/ssd?id=mdp.39015009662837&seq=369',
    identifier = 'German Aviation Medicine, World War II:IV-L',
    access = 'full_text',
    disposition = 'extracted',
    locator = 'Printed pp. 354–394, including Figure IV-154 (p. 357) and the Halle-Dölau case (p. 364)',
    note = 'Michigan scans 366–406. The Illinois scan independently confirms Figure IV-154. The count repeats the register reported by Becker-Freyseng in chapter XI-E. Other reported rates lack exact counts.'
WHERE source_id = 'hornberger50_review' AND access = 'metadata';
