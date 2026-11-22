-- Source-level counts and symptom percentages with distinct counting units.
-- These measures supply neither an adjudicated DCS count nor a clinical risk set.
CREATE TABLE publication_andean_chamber_measure (
    source_id TEXT NOT NULL REFERENCES publication_source,
    scope TEXT NOT NULL,
    measure TEXT NOT NULL,
    unit TEXT NOT NULL CHECK(unit IN (
        'aircrew_person', 'chamber_flight', 'matrix_row', 'flight_ordinal',
        'combined_course_person', 'announced_delegation_person', 'percent_as_printed'
    )),
    count_value INTEGER CHECK(count_value > 0),
    percent_as_printed REAL CHECK(percent_as_printed BETWEEN 0 AND 100),
    basis TEXT NOT NULL CHECK(basis IN (
        'reported_count', 'counted_visible_rows', 'verified_label_rows', 'reported_percent'
    )),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id, scope, measure),
    CHECK(
        (basis = 'reported_percent' AND unit = 'percent_as_printed'
            AND percent_as_printed IS NOT NULL AND count_value IS NULL)
        OR
        (basis <> 'reported_percent' AND unit <> 'percent_as_printed'
            AND percent_as_printed IS NULL AND count_value IS NOT NULL)
    ),
    CHECK(basis NOT IN ('counted_visible_rows', 'verified_label_rows') OR unit = 'matrix_row')
) STRICT;
