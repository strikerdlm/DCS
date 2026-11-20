CREATE TABLE publication_everest_context (
    source_id TEXT NOT NULL REFERENCES publication_source,
    observation_id TEXT NOT NULL,
    period TEXT NOT NULL,
    chamber_role TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    reported_value INTEGER CHECK(reported_value > 0),
    counting_unit TEXT NOT NULL CHECK(counting_unit IN (
        'lock_ascent', 'roster_member', 'resident_participant',
        'symptomatic_person', 'qualitative_frequency', 'protocol_change', 'day'
    )),
    reported_altitude_ft INTEGER CHECK(reported_altitude_ft > 0),
    printed_page INTEGER NOT NULL CHECK(printed_page > 0),
    pdf_page INTEGER NOT NULL CHECK(pdf_page > 0),
    analysis_role TEXT NOT NULL CHECK(analysis_role='descriptive_context'),
    note TEXT NOT NULL,
    PRIMARY KEY (source_id, observation_id),
    CHECK((reported_value IS NULL) = (counting_unit IN ('qualitative_frequency', 'protocol_change')))
) STRICT;
