UPDATE publication_source
SET access='secondary_table',
    disposition='extracted',
    locator='Fryer 1969, printed p. 265 (PDF p. 259) for counts and p. 310 (PDF p. 304) for citation',
    source_sha256='cb7a216891a203b06ac4f8d9ab3acb4f5924c4f400aad1c53fe8481faee03000',
    note='Fryer attributes the admission series to Cutler. SHA-256 describes the reproducing AGARDograph. The original proceedings, exact enrollment dates and case surveillance beyond hospital admission are unavailable.'
WHERE source_id='cutler62_aircent';

UPDATE publication_overlap
SET evidence='Fryer explicitly attributes the USAF series of 20,000 exposures to Cutler. Record the reproduced counts under Cutler once. The adjacent RAF Table 12-1 is a different training program.'
WHERE source_id='cutler62_aircent' AND related_source='v1.12/fryer69_raf/p. 265 US comparison';

CREATE TABLE publication_meader_recurrence_group (
    source_id TEXT NOT NULL REFERENCES publication_source,
    crew_code TEXT NOT NULL CHECK(crew_code GLOB '[A-K]'),
    episodes_as_printed INTEGER NOT NULL CHECK(episodes_as_printed > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,crew_code)
) STRICT;

CREATE TABLE publication_meader_recurrence_site (
    source_id TEXT NOT NULL,
    crew_code TEXT NOT NULL,
    site_as_reported TEXT NOT NULL,
    occurrences_as_printed INTEGER NOT NULL CHECK(occurrences_as_printed > 0),
    PRIMARY KEY(source_id,crew_code,site_as_reported),
    FOREIGN KEY(source_id,crew_code)
        REFERENCES publication_meader_recurrence_group(source_id,crew_code)
) STRICT;
