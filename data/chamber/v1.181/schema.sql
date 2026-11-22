-- Companion reports can use different grading or reading sets for the same exposures.
CREATE TABLE publication_vge_grade_comparison (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    modality TEXT NOT NULL,
    reported_peak_grade INTEGER NOT NULL CHECK(reported_peak_grade >= 0),
    reported_scale TEXT,
    plotted_source_id TEXT NOT NULL REFERENCES discovery_source,
    plotted_grade INTEGER NOT NULL CHECK(plotted_grade >= 0),
    plotted_scale TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    plot_locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint,modality),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;
