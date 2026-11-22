CREATE TABLE publication_hypobaric_model_archive_scope (
    source_id TEXT PRIMARY KEY REFERENCES publication_source,
    profile_count INTEGER NOT NULL CHECK(profile_count > 0),
    profile_count_unit TEXT NOT NULL CHECK(profile_count_unit IN (
        'experimental_pressure_profile','individual_profile_record'
    )),
    locator TEXT NOT NULL,
    note TEXT NOT NULL
) STRICT;
