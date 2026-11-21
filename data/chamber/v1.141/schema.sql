CREATE TABLE publication_nasa_serious_dcs_reference (
    source_id TEXT NOT NULL REFERENCES publication_source,
    reference_number INTEGER NOT NULL CHECK(reference_number BETWEEN 1 AND 73),
    printed_reference_page INTEGER NOT NULL CHECK(printed_reference_page BETWEEN 31 AND 36),
    citation TEXT NOT NULL CHECK(length(citation) > 0),
    related_source_id TEXT REFERENCES publication_source,
    ascent_source_id TEXT,
    ascent_reference_number INTEGER,
    PRIMARY KEY(source_id, reference_number),
    FOREIGN KEY(ascent_source_id, ascent_reference_number) REFERENCES publication_ascent_reference,
    CHECK((ascent_source_id IS NULL) = (ascent_reference_number IS NULL)),
    CHECK(related_source_id IS NULL OR related_source_id <> source_id)
) STRICT;
