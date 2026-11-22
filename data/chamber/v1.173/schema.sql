-- Historical scopes and reported rates without compatible incidence denominators.
CREATE TABLE publication_halifax_program_metric (
    source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    stratum TEXT NOT NULL,
    measure TEXT NOT NULL,
    reported_value REAL NOT NULL CHECK(reported_value > 0),
    upper_value REAL,
    value_basis TEXT NOT NULL CHECK(value_basis IN ('approximate', 'strict_lower_bound', 'range')),
    unit TEXT NOT NULL CHECK(unit IN ('person', 'person_exposure', 'percent')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id, stratum, measure),
    CHECK((value_basis = 'range') = (upper_value IS NOT NULL)),
    CHECK(upper_value IS NULL OR upper_value > reported_value),
    CHECK(unit != 'percent' OR (reported_value <= 100 AND coalesce(upper_value, reported_value) <= 100))
) STRICT;
