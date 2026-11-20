CREATE TABLE publication_neurological_episode_margin (
    source_id TEXT NOT NULL REFERENCES publication_source,
    parent_source_id TEXT NOT NULL REFERENCES publication_source,
    series TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    numerator INTEGER NOT NULL CHECK(numerator >= 0 AND numerator <= denominator),
    denominator INTEGER NOT NULL CHECK(denominator > 0),
    denominator_unit TEXT NOT NULL CHECK(denominator_unit='syndrome_episode'),
    peak_altitude_ft INTEGER CHECK(peak_altitude_ft > 0),
    outcome_window TEXT NOT NULL,
    printed_page INTEGER NOT NULL CHECK(printed_page > 0),
    pdf_page INTEGER NOT NULL CHECK(pdf_page > 0),
    analysis_role TEXT NOT NULL CHECK(analysis_role='case_conditional'),
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,series,endpoint),
    CHECK(source_id != parent_source_id)
) STRICT;
