CREATE TABLE publication_ea_rehearsal_pilot (
    source_id TEXT PRIMARY KEY REFERENCES publication_source(source_id),
    volunteer_count INTEGER NOT NULL CHECK(volunteer_count > 0),
    technician_count INTEGER NOT NULL CHECK(technician_count >= 0),
    simulated_eva_sessions INTEGER NOT NULL CHECK(simulated_eva_sessions > 0),
    acclimation_hours INTEGER NOT NULL CHECK(acclimation_hours > 0),
    planned_eva_min INTEGER NOT NULL CHECK(planned_eva_min > 0),
    prebreathe_min INTEGER NOT NULL CHECK(prebreathe_min >= 0),
    habitat_pressure_methods_kpa REAL NOT NULL CHECK(habitat_pressure_methods_kpa > 0),
    habitat_oxygen_fraction REAL NOT NULL CHECK(habitat_oxygen_fraction BETWEEN 0 AND 1),
    eva_oxygen_fraction REAL NOT NULL CHECK(eva_oxygen_fraction BETWEEN 0 AND 1),
    eva_pressure_pilot_methods_kpa REAL NOT NULL CHECK(eva_pressure_pilot_methods_kpa > 0),
    eva_pressure_medical_overview_psia REAL NOT NULL CHECK(eva_pressure_medical_overview_psia > 0),
    peak_doppler_grade_as_reported TEXT NOT NULL,
    peak_eftedal_brubakk_score INTEGER NOT NULL CHECK(peak_eftedal_brubakk_score >= 0),
    pressure_status TEXT NOT NULL CHECK(pressure_status = 'conflicting_reports'),
    locator TEXT NOT NULL
) STRICT;

CREATE TABLE publication_ea_rehearsal_summary (
    campaign_source_id TEXT NOT NULL REFERENCES discovery_source(source_id),
    rehearsal_year INTEGER NOT NULL,
    campaign_month TEXT NOT NULL,
    facility_start_date TEXT NOT NULL,
    facility_end_date TEXT NOT NULL CHECK(facility_end_date >= facility_start_date),
    reported_attendance INTEGER NOT NULL CHECK(reported_attendance > 0),
    reported_dcs_cases INTEGER NOT NULL CHECK(reported_dcs_cases >= 0),
    dcs_endpoint_as_reported TEXT NOT NULL,
    outcome_denominator INTEGER CHECK(outcome_denominator >= reported_dcs_cases),
    pilot_source_id TEXT REFERENCES publication_ea_rehearsal_pilot(source_id),
    linkage_status TEXT NOT NULL CHECK(linkage_status = 'likely_same_rehearsal'),
    role_and_scope_note TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(campaign_source_id,rehearsal_year)
) STRICT;
