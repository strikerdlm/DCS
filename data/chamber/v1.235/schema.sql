CREATE TABLE literature_hdsd_source_category (
    source_id TEXT NOT NULL REFERENCES literature_source,
    category TEXT NOT NULL,
    report_count INTEGER NOT NULL CHECK(report_count > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,category)
) STRICT;

CREATE TABLE literature_hdsd_publication_band (
    source_id TEXT NOT NULL REFERENCES literature_source,
    band_id TEXT NOT NULL,
    first_publication_year INTEGER,
    last_publication_year INTEGER,
    record_count INTEGER NOT NULL CHECK(record_count > 0),
    male_person_exposures INTEGER NOT NULL CHECK(male_person_exposures >= 0),
    female_person_exposures INTEGER NOT NULL CHECK(female_person_exposures >= 0),
    reported_percent TEXT CHECK(CAST(reported_percent AS REAL) BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    CHECK((first_publication_year IS NULL) = (last_publication_year IS NULL)),
    CHECK(first_publication_year <= last_publication_year),
    PRIMARY KEY(source_id,band_id)
) STRICT;

CREATE TABLE literature_hdsd_serious_group_link (
    source_id TEXT NOT NULL,
    report_number INTEGER NOT NULL,
    serious_source_id TEXT NOT NULL,
    serious_printed_page INTEGER NOT NULL,
    serious_row_on_page INTEGER NOT NULL,
    original_source_id TEXT REFERENCES publication_source,
    relationship TEXT NOT NULL CHECK(relationship IN ('same_source_group','candidate_overlap')),
    evidence TEXT NOT NULL,
    PRIMARY KEY(source_id,report_number,serious_source_id,serious_printed_page,serious_row_on_page),
    FOREIGN KEY(source_id,report_number) REFERENCES literature_hdsd_compilation,
    FOREIGN KEY(serious_source_id,serious_printed_page,serious_row_on_page)
        REFERENCES publication_nasa_serious_dcs_group,
    CHECK(relationship <> 'same_source_group' OR original_source_id IS NOT NULL)
) STRICT;
