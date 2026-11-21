CREATE TABLE publication_nasa_serious_dcs_group (
    source_id TEXT NOT NULL REFERENCES publication_source,
    printed_page INTEGER NOT NULL CHECK(printed_page BETWEEN 40 AND 45),
    row_on_page INTEGER NOT NULL CHECK(row_on_page BETWEEN 1 AND 45),
    male_exposures INTEGER NOT NULL CHECK(male_exposures > 0),
    serious_cases INTEGER NOT NULL CHECK(serious_cases BETWEEN 0 AND male_exposures),
    reference_number INTEGER NOT NULL CHECK(reference_number BETWEEN 1 AND 73),
    reference_printed_page INTEGER NOT NULL CHECK(reference_printed_page BETWEEN 31 AND 36),
    source_annotation TEXT,
    footnote_summary TEXT,
    analysis_role TEXT NOT NULL CHECK(analysis_role = 'overlap_hold'),
    PRIMARY KEY(source_id,printed_page,row_on_page),
    CHECK((source_annotation IS NULL) = (footnote_summary IS NULL)),
    CHECK(printed_page NOT IN (40,45) OR row_on_page <= 39)
) STRICT;

UPDATE publication_source
SET url = 'https://www.nasa.gov/wp-content/uploads/2023/03/conkin-dcs-estimation-tp210196-2001.pdf#page=39',
    locator = 'Bibliographic citation in NASA/TP-2001-210196 Appendix A, reference 29, printed p. 33',
    note = 'The standalone CAM Report 363 remains unavailable. The link leads to the NASA bibliography that cites it.'
WHERE source_id = 'ferris44_cam363' AND url = 'https://ntrs.nasa.gov/citations/20010020946';
