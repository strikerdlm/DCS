CREATE TABLE publication_nasa_f2_case (
    report_source_id TEXT NOT NULL REFERENCES source(source_id),
    table_row INTEGER NOT NULL CHECK(table_row > 0),
    nasa_test_id TEXT NOT NULL REFERENCES nasa_test(test_id),
    classification TEXT NOT NULL CHECK(classification IN ('reported_type_ii','historical_skin_mottling')),
    mean_tr360 REAL NOT NULL CHECK(mean_tr360 > 0),
    mean_bgi360 REAL NOT NULL CHECK(mean_bgi360 >= 0),
    prescribed_prebreathe_exercise INTEGER NOT NULL CHECK(prescribed_prebreathe_exercise IN (0,1)),
    locator TEXT NOT NULL,
    PRIMARY KEY(report_source_id,table_row)
) STRICT;

CREATE TABLE publication_nasa_f3_stratum (
    report_source_id TEXT NOT NULL REFERENCES source(source_id),
    table_row INTEGER NOT NULL CHECK(table_row > 0),
    cited_source_id TEXT REFERENCES publication_source(source_id),
    nasa_test_id TEXT REFERENCES nasa_test(test_id),
    label_as_printed TEXT NOT NULL,
    exposures INTEGER NOT NULL CHECK(exposures > 0),
    all_dcs INTEGER NOT NULL CHECK(all_dcs BETWEEN 0 AND exposures),
    serious_dcs INTEGER NOT NULL CHECK(serious_dcs BETWEEN 0 AND all_dcs),
    dcs_percent_as_printed REAL NOT NULL CHECK(dcs_percent_as_printed BETWEEN 0 AND 100),
    tr360 REAL NOT NULL CHECK(tr360 > 0),
    pressure_psia REAL NOT NULL CHECK(pressure_psia > 0),
    altitude_exposure_min INTEGER NOT NULL CHECK(altitude_exposure_min > 0),
    locator TEXT NOT NULL,
    evidence TEXT NOT NULL,
    PRIMARY KEY(report_source_id,table_row),
    CHECK((cited_source_id IS NULL) <> (nasa_test_id IS NULL))
) STRICT;

CREATE TABLE publication_lunar_pressure_campaign (
    source_id TEXT PRIMARY KEY REFERENCES publication_source(source_id),
    volunteers_selected INTEGER NOT NULL CHECK(volunteers_selected > 0),
    groups_reported INTEGER NOT NULL CHECK(groups_reported BETWEEN 1 AND volunteers_selected),
    pressure_regimes INTEGER NOT NULL CHECK(pressure_regimes > 0),
    test_cycles_reported INTEGER NOT NULL CHECK(test_cycles_reported > 0),
    planned_days_per_cycle INTEGER NOT NULL CHECK(planned_days_per_cycle > 0),
    planned_eva_days_per_cycle INTEGER NOT NULL CHECK(planned_eva_days_per_cycle BETWEEN 1 AND planned_days_per_cycle),
    planned_eva_hours_per_day INTEGER NOT NULL CHECK(planned_eva_hours_per_day BETWEEN 1 AND 24),
    evaluable_dcs_person_evas INTEGER CHECK(evaluable_dcs_person_evas > 0),
    evaluable_vge_person_evas INTEGER CHECK(evaluable_vge_person_evas > 0),
    locator TEXT NOT NULL
) STRICT;
