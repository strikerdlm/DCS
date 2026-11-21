CREATE TABLE publication_ground_oxygen_flow (
    source_id TEXT NOT NULL REFERENCES publication_source,
    group_id TEXT NOT NULL,
    parent_group_id TEXT,
    population_count INTEGER NOT NULL CHECK(population_count >= 0),
    counting_unit TEXT NOT NULL CHECK(counting_unit IN ('dcs_case','symptom_report')),
    count_basis TEXT NOT NULL CHECK(count_basis IN ('source_reported','reconstructed')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,group_id),
    UNIQUE(source_id,group_id,counting_unit),
    FOREIGN KEY(source_id,parent_group_id,counting_unit)
        REFERENCES publication_ground_oxygen_flow(source_id,group_id,counting_unit),
    CHECK(parent_group_id IS NULL OR parent_group_id != group_id)
) STRICT;
