CREATE TABLE literature_hdsd_compilation (
    source_id TEXT NOT NULL REFERENCES literature_source,
    report_number INTEGER NOT NULL CHECK(report_number > 0),
    printed_page INTEGER NOT NULL,
    person_exposures INTEGER NOT NULL CHECK(person_exposures >= 200),
    altitude_psia REAL NOT NULL CHECK(altitude_psia > 0),
    altitude_hours REAL NOT NULL CHECK(altitude_hours > 0),
    exercise INTEGER NOT NULL CHECK(exercise IN (0,1)),
    dcs_pct REAL CHECK(dcs_pct BETWEEN 0 AND 100),
    serious_dcs_pct REAL CHECK(serious_dcs_pct BETWEEN 0 AND 100),
    related_source_id TEXT REFERENCES publication_source,
    related_stratum TEXT,
    analysis_role TEXT NOT NULL CHECK(analysis_role = 'overlap_hold'),
    PRIMARY KEY (source_id, report_number),
    CHECK((related_source_id IS NULL) = (related_stratum IS NULL))
) STRICT;

UPDATE literature_source
SET access='full_text',
    disposition='extracted',
    url='https://asma.kglmeridian.com/downloadpdf/view/journals/asem/63/9/article-p819.pdf',
    extraction='Table III p. 821, endpoint definitions p. 820 and availability statement p. 822',
    source_sha256='b4b6b303c8787c050083474632248c34c90203c1168c26005f498c7a609817ed',
    note='The original article prints 27 historical group summaries. Four match Motley et al. by denominator and both reported outcomes, and other groups may overlap earlier reports. The complete 378-record HDSD was described as available on request. A public machine-readable copy was not found.'
WHERE source_id='conkin92';
