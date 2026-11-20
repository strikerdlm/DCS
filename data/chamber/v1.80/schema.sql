CREATE TABLE publication_u2_series_row (
    source_id TEXT NOT NULL REFERENCES publication_source,
    source_table TEXT NOT NULL CHECK(source_table IN ('I','II')),
    source_row INTEGER NOT NULL CHECK(source_row > 0),
    pilot_code TEXT NOT NULL,
    age_years INTEGER CHECK(age_years > 0),
    body_mass_index INTEGER CHECK(body_mass_index > 0),
    in_flight_medication_listed INTEGER NOT NULL CHECK(in_flight_medication_listed IN (0,1)),
    physiological_altitude_m INTEGER CHECK(physiological_altitude_m > 0),
    physiological_altitude_ft INTEGER CHECK(physiological_altitude_ft > 0),
    altitude_relation TEXT CHECK(altitude_relation IN ('reported_point','greater_than')),
    exposure_hours REAL CHECK(exposure_hours > 0),
    exposure_relation TEXT CHECK(exposure_relation IN ('reported_point','greater_than')),
    cns_certainty TEXT CHECK(cns_certainty IN ('confirmed','probable','possible')),
    pulmonary_listed INTEGER NOT NULL CHECK(pulmonary_listed IN (0,1)),
    joint_pain_listed INTEGER NOT NULL CHECK(joint_pain_listed IN (0,1)),
    additional_confirmed_cns_from_footnote INTEGER
        CHECK(additional_confirmed_cns_from_footnote IS NULL OR
              (additional_confirmed_cns_from_footnote = 1 AND source_table = 'I' AND cns_certainty IS 'confirmed')),
    multiple_incidents_or_symptoms_noted INTEGER
        CHECK(multiple_incidents_or_symptoms_noted IS NULL OR
              (multiple_incidents_or_symptoms_noted = 1 AND source_table = 'II')),
    locator TEXT NOT NULL,
    PRIMARY KEY (source_id,source_table,source_row),
    CHECK((physiological_altitude_m IS NULL) = (physiological_altitude_ft IS NULL)),
    CHECK((physiological_altitude_m IS NULL) = (altitude_relation IS NULL)),
    CHECK((exposure_hours IS NULL) = (exposure_relation IS NULL)),
    CHECK(cns_certainty IS NOT NULL OR pulmonary_listed = 1 OR joint_pain_listed = 1)
) STRICT;

CREATE TABLE publication_u2_series_case_link (
    source_id TEXT NOT NULL,
    source_table TEXT NOT NULL,
    source_row INTEGER NOT NULL,
    case_source_id TEXT NOT NULL,
    case_stratum TEXT NOT NULL,
    case_endpoint TEXT NOT NULL,
    linkage TEXT NOT NULL CHECK(linkage IN ('likely','possible')),
    basis TEXT NOT NULL,
    PRIMARY KEY (source_id,source_table,source_row),
    FOREIGN KEY (source_id,source_table,source_row) REFERENCES publication_u2_series_row,
    FOREIGN KEY (case_source_id,case_stratum,case_endpoint) REFERENCES publication_u2_episode
) STRICT;
