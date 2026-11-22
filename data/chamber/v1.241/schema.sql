CREATE TABLE publication_cited_collapse_series (
    citing_source_id TEXT NOT NULL REFERENCES publication_source,
    cited_source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role = 'overlap_hold'),
    decompressions_as_cited INTEGER NOT NULL CHECK(decompressions_as_cited > 0),
    severe_collapses_as_cited INTEGER NOT NULL CHECK(
        severe_collapses_as_cited BETWEEN 0 AND decompressions_as_cited
    ),
    fatal_subset_as_cited INTEGER NOT NULL CHECK(
        fatal_subset_as_cited BETWEEN 0 AND severe_collapses_as_cited
    ),
    severe_collapse_percent_as_cited REAL NOT NULL CHECK(
        severe_collapse_percent_as_cited BETWEEN 0 AND 100
    ),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(citing_source_id,cited_source_id,stratum),
    CHECK(citing_source_id <> cited_source_id)
) STRICT;
