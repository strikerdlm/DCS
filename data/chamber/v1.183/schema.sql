-- The planned diagram supplies nominal altitudes and approximate elapsed times.
CREATE TABLE zotero_chamber_profile_point (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    point_number INTEGER NOT NULL CHECK(point_number > 0),
    elapsed_min_approx INTEGER NOT NULL CHECK(elapsed_min_approx >= 0),
    altitude_ft_nominal INTEGER NOT NULL CHECK(altitude_ft_nominal >= 0),
    stage_boundary TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,point_number),
    FOREIGN KEY(source_id,stratum) REFERENCES zotero_observation
) STRICT;

-- A narrative result with its own surveillance window and unspecified exposure count.
CREATE TABLE zotero_chamber_post_change_followup (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    duration_months INTEGER NOT NULL CHECK(duration_months > 0),
    reported_dcs_cases INTEGER NOT NULL CHECK(reported_dcs_cases >= 0),
    exposure_denominator INTEGER CHECK(exposure_denominator > 0 AND exposure_denominator >= reported_dcs_cases),
    prebreathe_min_as_described INTEGER NOT NULL CHECK(prebreathe_min_as_described >= 0),
    ascent_ft_min_as_described INTEGER NOT NULL CHECK(ascent_ft_min_as_described > 0),
    rotary_ceiling_ft_as_described INTEGER NOT NULL CHECK(rotary_ceiling_ft_as_described > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum),
    FOREIGN KEY(source_id,stratum) REFERENCES zotero_observation
) STRICT;
