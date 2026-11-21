CREATE TABLE publication_historical_visual_summary (
    citing_source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    cited_report_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    measure TEXT NOT NULL,
    count_as_cited INTEGER CHECK(count_as_cited >= 0),
    counting_unit TEXT NOT NULL CHECK(counting_unit IN (
        'person','chamber_ascent','reported_visual_episode','collapse_case'
    )),
    denominator_as_cited INTEGER CHECK(denominator_as_cited > 0),
    denominator_unit TEXT CHECK(denominator_unit IN ('person','chamber_ascent','collapse_case')),
    percent_as_cited REAL CHECK(percent_as_cited BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    scope_note TEXT NOT NULL,
    PRIMARY KEY(citing_source_id,cited_report_id,stratum,measure),
    CHECK((denominator_as_cited IS NULL) = (denominator_unit IS NULL)),
    CHECK(count_as_cited IS NOT NULL OR percent_as_cited IS NOT NULL),
    CHECK(count_as_cited IS NULL OR denominator_as_cited IS NULL OR count_as_cited <= denominator_as_cited),
    CHECK(percent_as_cited IS NULL OR denominator_as_cited IS NOT NULL)
) STRICT;
