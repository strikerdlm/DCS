CREATE TABLE literature_age_figure_group (
    source_id TEXT NOT NULL REFERENCES literature_source,
    figure_number INTEGER NOT NULL CHECK(figure_number BETWEEN 1 AND 3),
    altitude_scope TEXT NOT NULL,
    age_label_as_printed TEXT NOT NULL,
    printed_n INTEGER NOT NULL CHECK(printed_n > 0),
    n_basis TEXT NOT NULL,
    plotted_percent_approx INTEGER CHECK(plotted_percent_approx BETWEEN 0 AND 100),
    archive_source_id TEXT,
    archive_stratum TEXT,
    archive_endpoint TEXT,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,figure_number,altitude_scope,age_label_as_printed),
    FOREIGN KEY(archive_source_id,archive_stratum,archive_endpoint)
        REFERENCES publication_observation(source_id,stratum,endpoint),
    CHECK((figure_number=1 AND altitude_scope='all_altitudes')
       OR (figure_number=2 AND altitude_scope IN ('below_25000_ft','above_25000_ft'))
       OR (figure_number=3 AND altitude_scope='29500_to_30000_ft')),
    CHECK((figure_number=2 AND n_basis='unresolved_figure_n_label'
            AND plotted_percent_approx IS NOT NULL
            AND archive_source_id IS NULL AND archive_stratum IS NULL AND archive_endpoint IS NULL)
       OR (figure_number IN (1,3) AND n_basis='subject_exposure_denominator'
            AND plotted_percent_approx IS NULL
            AND archive_source_id IS NOT NULL AND archive_stratum IS NOT NULL AND archive_endpoint IS NOT NULL))
) STRICT;
