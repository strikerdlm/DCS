CREATE TABLE publication_bends_grade_syncope (
    source_id TEXT NOT NULL REFERENCES publication_source,
    bends_grade INTEGER NOT NULL CHECK(bends_grade BETWEEN 1 AND 10),
    syncope_absent_count INTEGER CHECK(syncope_absent_count >= 0),
    mild_syncope_count INTEGER CHECK(mild_syncope_count >= 0),
    severe_syncope_count INTEGER CHECK(severe_syncope_count >= 0),
    reported_any_syncope_percent INTEGER CHECK(reported_any_syncope_percent BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,bends_grade)
) STRICT;
