CREATE TABLE publication_repeat_exposure_participant_cell (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratification TEXT NOT NULL CHECK(stratification IN ('none','sex','cmb_runs','tr360')),
    stratum TEXT NOT NULL,
    cumulative_exposure_band TEXT NOT NULL CHECK(cumulative_exposure_band IN ('at_most_3','more_than_3')),
    without_dcs INTEGER NOT NULL CHECK(without_dcs >= 0),
    with_dcs INTEGER NOT NULL CHECK(with_dcs >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((stratification='none')=(stratum='all')),
    PRIMARY KEY(source_id,stratification,stratum,cumulative_exposure_band)
) STRICT;

CREATE TABLE publication_repeat_exposure_odds_ratio (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratification TEXT NOT NULL CHECK(stratification IN ('none','sex','cmb_runs','tr360')),
    method TEXT NOT NULL CHECK(method IN ('crude_cross_product','mantel_haenszel')),
    odds_ratio REAL NOT NULL CHECK(odds_ratio > 0),
    ci95_lower REAL NOT NULL CHECK(ci95_lower > 0 AND ci95_lower <= odds_ratio),
    ci95_upper REAL NOT NULL CHECK(ci95_upper >= odds_ratio),
    marked_chi_square_p_lt_005 INTEGER CHECK(marked_chi_square_p_lt_005=1),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((stratification='none')=(method='crude_cross_product')),
    PRIMARY KEY(source_id,stratification)
) STRICT;
