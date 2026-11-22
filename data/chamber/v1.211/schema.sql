CREATE TABLE publication_zero_prebreathe_series (
    source_id TEXT PRIMARY KEY REFERENCES publication_source,
    overall_subjects_as_reported INTEGER NOT NULL CHECK(overall_subjects_as_reported > 0),
    maximum_altitude_duration_min INTEGER CHECK(maximum_altitude_duration_min > 0),
    sex_description_as_reported TEXT,
    exposure_per_person_as_reported INTEGER CHECK(exposure_per_person_as_reported > 0),
    prebreathe_min INTEGER NOT NULL CHECK(prebreathe_min=0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL
) STRICT;

CREATE TABLE publication_zero_prebreathe_group (
    source_id TEXT NOT NULL REFERENCES publication_zero_prebreathe_series,
    altitude_ft_as_printed INTEGER NOT NULL CHECK(altitude_ft_as_printed > 0),
    group_subjects_as_printed INTEGER NOT NULL CHECK(group_subjects_as_printed > 0),
    explicit_dcs_cases INTEGER CHECK(explicit_dcs_cases=0),
    dcs_percent REAL NOT NULL CHECK(dcs_percent BETWEEN 0 AND 100),
    dcs_basis TEXT NOT NULL CHECK(dcs_basis IN ('explicit_zero','reported_percent','figure_approximation')),
    vge_percent REAL CHECK(vge_percent BETWEEN 0 AND 100),
    vge_basis TEXT CHECK(vge_basis IN ('described_probit_curve','figure_approximation')),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,altitude_ft_as_printed),
    CHECK((dcs_basis='explicit_zero' AND explicit_dcs_cases IS NOT NULL AND dcs_percent=0)
       OR (dcs_basis<>'explicit_zero' AND explicit_dcs_cases IS NULL)),
    CHECK((vge_percent IS NULL)=(vge_basis IS NULL))
) STRICT;

CREATE TABLE publication_zero_prebreathe_checkpoint (
    source_id TEXT NOT NULL,
    altitude_ft_as_printed INTEGER NOT NULL,
    endpoint TEXT NOT NULL CHECK(endpoint IN ('dcs_symptoms','any_vge')),
    figure_number INTEGER NOT NULL,
    elapsed_min INTEGER NOT NULL CHECK(elapsed_min BETWEEN 60 AND 360 AND elapsed_min%60=0),
    percent_approx INTEGER NOT NULL CHECK(percent_approx BETWEEN 0 AND 100),
    figure_subjects_as_printed INTEGER CHECK(figure_subjects_as_printed > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,altitude_ft_as_printed,endpoint,figure_number,elapsed_min),
    FOREIGN KEY(source_id,altitude_ft_as_printed)
        REFERENCES publication_zero_prebreathe_group(source_id,altitude_ft_as_printed),
    CHECK((figure_number=2 AND endpoint='any_vge' AND figure_subjects_as_printed IS NULL)
       OR (figure_number=4 AND endpoint='dcs_symptoms' AND figure_subjects_as_printed IS NOT NULL))
) STRICT;

CREATE TABLE publication_age_abstract_margin (
    source_id TEXT NOT NULL REFERENCES publication_source,
    altitude_scope TEXT NOT NULL CHECK(altitude_scope IN ('all_altitudes','29500_to_30000_ft')),
    age_label_as_printed TEXT NOT NULL,
    percent_as_printed TEXT NOT NULL CHECK(percent_as_printed GLOB '*[0-9]*'
        AND percent_as_printed NOT GLOB '*[^0-9.]*'
        AND length(percent_as_printed)-length(replace(percent_as_printed,'.',''))<=1
        AND CAST(percent_as_printed AS REAL) BETWEEN 0 AND 100),
    archive_source_id TEXT NOT NULL,
    archive_stratum TEXT NOT NULL,
    archive_endpoint TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,altitude_scope,age_label_as_printed),
    FOREIGN KEY(archive_source_id,archive_stratum,archive_endpoint)
        REFERENCES publication_observation(source_id,stratum,endpoint)
) STRICT;
