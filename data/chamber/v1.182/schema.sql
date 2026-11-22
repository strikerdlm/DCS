-- The highest plotted grade describes a chamber session. It gives no participant count.
CREATE TABLE discovery_eva_vge_plot_maximum (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    clinical_endpoint TEXT NOT NULL,
    modality TEXT NOT NULL,
    grading_scale TEXT NOT NULL,
    highest_plotted_grade INTEGER NOT NULL CHECK(highest_plotted_grade >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,clinical_endpoint,modality),
    FOREIGN KEY(source_id,stratum,clinical_endpoint) REFERENCES discovery_observation,
    CHECK((modality='doppler' AND grading_scale='Spencer' AND highest_plotted_grade <= 4)
        OR (modality='cardiac_ultrasonography' AND grading_scale='Modified Eftedal–Brubakk'
            AND highest_plotted_grade <= 7))
) STRICT;
