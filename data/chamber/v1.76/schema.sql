CREATE TABLE publication_lba_argo_arm (
    source_id TEXT NOT NULL REFERENCES publication_source,
    arm TEXT NOT NULL,
    exposures INTEGER NOT NULL CHECK(exposures > 0),
    dcs_cases INTEGER NOT NULL CHECK(dcs_cases BETWEEN 0 AND exposures),
    vge_cases INTEGER NOT NULL CHECK(vge_cases BETWEEN 0 AND exposures),
    before_pb_hours REAL NOT NULL CHECK(before_pb_hours >= 0),
    during_pb_hours REAL NOT NULL CHECK(during_pb_hours >= 0),
    at_p2_hours REAL NOT NULL CHECK(at_p2_hours >= 0),
    target_psia REAL NOT NULL CHECK(target_psia > 0),
    printed_tr REAL NOT NULL CHECK(printed_tr > 0),
    adynamic_condition INTEGER NOT NULL CHECK(adynamic_condition BETWEEN 0 AND 3),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,arm)
) STRICT;

CREATE TABLE publication_lba_argo_test_link (
    source_id TEXT NOT NULL,
    arm TEXT NOT NULL,
    nasa_test_id TEXT NOT NULL REFERENCES nasa_test(test_id),
    status TEXT NOT NULL CHECK(status IN ('matched_named_arm','candidate_arm')),
    evidence TEXT NOT NULL,
    PRIMARY KEY(source_id,arm,nasa_test_id),
    FOREIGN KEY(source_id,arm) REFERENCES publication_lba_argo_arm
) STRICT;

CREATE UNIQUE INDEX publication_lba_one_matched_argo_test
ON publication_lba_argo_test_link(source_id,arm) WHERE status = 'matched_named_arm';
