CREATE TABLE publication_asma_abstract_locator_revision (
    source_id TEXT PRIMARY KEY REFERENCES publication_source,
    previous_abstract_number INTEGER NOT NULL CHECK(previous_abstract_number > 0),
    verified_abstract_number INTEGER NOT NULL CHECK(
        verified_abstract_number > 0 AND verified_abstract_number <> previous_abstract_number
    ),
    printed_page INTEGER NOT NULL CHECK(printed_page > 0),
    pdf_page INTEGER NOT NULL CHECK(pdf_page > 0),
    evidence_url TEXT NOT NULL,
    locator TEXT NOT NULL
) STRICT;
