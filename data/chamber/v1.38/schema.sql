UPDATE publication_source
SET url='https://doi.org/10.1109/AERO66936.2026.11520147',
    identifier='10.1109/AERO66936.2026.11520147',
    access='primary_abstract',
    disposition='extracted',
    locator='Conference abstract reproduced in EurekaMag accession 107645870',
    note='Crossref verifies the DOI and six authors. The conference abstract reports eight ground-test participants and no DCS symptoms across ground and flight. The eight-person ground observation is retained. The abstract gives no individual records, exact ultrasound outcomes or fixed post-exposure symptom window.'
WHERE source_id='polaris26_eva' AND access='metadata';

UPDATE publication_source
SET url='https://asma.kglmeridian.com/downloadpdf/view/journals/asem/61/8/article-p685.pdf',
    identifier='PMID:2400370',
    access='full_text',
    disposition='crosswalk',
    locator='Methods p. 686 and Table I p. 687',
    source_sha256='0ed0a12123752ac7d205f6aaca64d84325cde1ca5bf26ea07fe1c97cbc03a2ae',
    note='Secondary compilation. Original printed counts and profile data are held in publication_threshold_profile for provenance. Some rows reproduce groups already recorded, use narrower endpoints or different protocol descriptions, or lack an identifiable primary table.'
WHERE source_id='kumar90' AND access='primary_abstract';

CREATE TABLE publication_threshold_profile (
    source_id TEXT NOT NULL REFERENCES publication_source,
    printed_row INTEGER NOT NULL CHECK(printed_row > 0),
    altitude_ft INTEGER NOT NULL CHECK(altitude_ft > 0),
    exposure_count INTEGER NOT NULL CHECK(exposure_count > 0),
    duration_h_min REAL NOT NULL CHECK(duration_h_min > 0),
    duration_h_max REAL NOT NULL CHECK(duration_h_max >= duration_h_min),
    denitrogenation_h REAL NOT NULL CHECK(denitrogenation_h >= 0),
    exercise_schedule TEXT NOT NULL,
    ascent_ft_per_min INTEGER NOT NULL CHECK(ascent_ft_per_min > 0),
    symptom_count INTEGER NOT NULL CHECK(symptom_count BETWEEN 0 AND exposure_count),
    printed_reference TEXT NOT NULL,
    related_source_id TEXT REFERENCES publication_source,
    reconciliation_status TEXT NOT NULL CHECK(reconciliation_status IN (
        'counts_concordant', 'scope_discrepancy', 'unverified'
    )),
    reconciliation_note TEXT NOT NULL,
    CHECK(related_source_id IS NOT NULL OR reconciliation_status='unverified'),
    PRIMARY KEY(source_id, printed_row)
) STRICT;
