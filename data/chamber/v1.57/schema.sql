CREATE TABLE publication_meeting_measure (
    source_id TEXT NOT NULL REFERENCES publication_source,
    study_group TEXT NOT NULL,
    measure TEXT NOT NULL,
    unit TEXT NOT NULL CHECK(unit IN ('participants','imaging_observations','bubble_count',
        'streaking_score_sum','combined_score_sum','cases_per_1000_runs')),
    reported_value INTEGER NOT NULL CHECK(reported_value >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    analysis_role TEXT NOT NULL DEFAULT 'overlap_hold' CHECK(analysis_role='overlap_hold'),
    PRIMARY KEY(source_id,study_group,measure)
) STRICT;
