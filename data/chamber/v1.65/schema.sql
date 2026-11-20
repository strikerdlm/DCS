-- Each source describes one aircraft incident. These counts are descriptive aviation evidence.
CREATE TABLE publication_aircraft_incident (
    source_id TEXT PRIMARY KEY REFERENCES publication_source,
    aircraft TEXT NOT NULL,
    cabin_altitude_before_low_m INTEGER NOT NULL CHECK(cabin_altitude_before_low_m > 0),
    cabin_altitude_before_high_m INTEGER NOT NULL CHECK(cabin_altitude_before_high_m >= cabin_altitude_before_low_m),
    peak_cabin_altitude_m INTEGER NOT NULL CHECK(peak_cabin_altitude_m > cabin_altitude_before_high_m),
    pressure_gas_history TEXT NOT NULL,
    outcome_ascertainment TEXT NOT NULL,
    locator TEXT NOT NULL
) STRICT;

CREATE TABLE publication_aircraft_incident_count (
    source_id TEXT NOT NULL REFERENCES publication_aircraft_incident,
    measure TEXT NOT NULL,
    numerator INTEGER NOT NULL CHECK(numerator >= 0),
    denominator INTEGER CHECK(denominator > 0 AND denominator >= numerator),
    denominator_unit TEXT CHECK(denominator_unit IN (
        'exposed_passenger','aircraft_occupant','clinic_treated_passenger',
        'more_severely_symptomatic_passenger','hyperbaric_treated_passenger','source_identified_dcs_case'
    )),
    evidence_role TEXT NOT NULL CHECK(evidence_role IN (
        'incident_diagnosis','diagnostic_component','overlapping_symptom',
        'ascertainment','care_process','care_response','followup_outcome','unreconciled_narrative'
    )),
    reported_pct REAL CHECK(reported_pct BETWEEN 0 AND 100),
    outcome_window TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK((denominator IS NULL) = (denominator_unit IS NULL)),
    CHECK((denominator IS NULL) = (evidence_role='unreconciled_narrative')),
    CHECK(reported_pct IS NULL OR denominator IS NOT NULL),
    PRIMARY KEY(source_id, measure)
) STRICT;

CREATE UNIQUE INDEX publication_aircraft_incident_primary_count
    ON publication_aircraft_incident_count(source_id) WHERE evidence_role='incident_diagnosis';
