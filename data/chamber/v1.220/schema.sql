CREATE TABLE publication_flight_questionnaire (
    source_id TEXT PRIMARY KEY REFERENCES publication_source,
    questionnaires_received INTEGER NOT NULL CHECK(questionnaires_received > 0),
    questionnaires_excluded INTEGER NOT NULL CHECK(questionnaires_excluded >= 0),
    people_retained INTEGER NOT NULL CHECK(people_retained > 0),
    minimum_combat_altitude_ft INTEGER NOT NULL CHECK(minimum_combat_altitude_ft > 0),
    minimum_missions_with_demand_oxygen INTEGER NOT NULL CHECK(minimum_missions_with_demand_oxygen > 0),
    sorties_approx_as_printed INTEGER NOT NULL CHECK(sorties_approx_as_printed > 0),
    crewmate_symptom_reports INTEGER NOT NULL CHECK(crewmate_symptom_reports >= 0),
    conditional_sorties_per_case_as_printed INTEGER NOT NULL CHECK(conditional_sorties_per_case_as_printed > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK(questionnaires_received=questionnaires_excluded+people_retained)
) STRICT;

CREATE TABLE publication_flight_questionnaire_role (
    source_id TEXT NOT NULL REFERENCES publication_flight_questionnaire,
    crew_position TEXT NOT NULL,
    people_retained INTEGER NOT NULL CHECK(people_retained >= 0),
    people_questioned_about_bends INTEGER CHECK(people_questioned_about_bends BETWEEN 1 AND people_retained),
    people_reporting_pain INTEGER CHECK(people_reporting_pain BETWEEN 0 AND people_questioned_about_bends),
    reported_pain_occurrences INTEGER CHECK(reported_pain_occurrences >= people_reporting_pain),
    reported_symptom_altitude_min_ft INTEGER CHECK(reported_symptom_altitude_min_ft > 0),
    reported_symptom_altitude_max_ft INTEGER CHECK(reported_symptom_altitude_max_ft >= reported_symptom_altitude_min_ft),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,crew_position),
    CHECK((people_questioned_about_bends IS NULL)=(people_reporting_pain IS NULL)),
    CHECK((people_reporting_pain IS NULL)=(reported_pain_occurrences IS NULL)),
    CHECK((reported_symptom_altitude_min_ft IS NULL)=(reported_symptom_altitude_max_ft IS NULL))
) STRICT;

CREATE TABLE publication_historical_flight_survey_summary (
    source_id TEXT NOT NULL REFERENCES publication_source,
    survey_group TEXT NOT NULL,
    people_questioned INTEGER NOT NULL CHECK(people_questioned > 0),
    people_reporting_bends INTEGER NOT NULL CHECK(people_reporting_bends BETWEEN 0 AND people_questioned),
    missions_flown_as_printed INTEGER CHECK(missions_flown_as_printed > 0),
    minimum_man_flights_per_case_as_printed INTEGER CHECK(minimum_man_flights_per_case_as_printed > 0),
    recurring_symptoms_percent_as_printed REAL CHECK(recurring_symptoms_percent_as_printed BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,survey_group)
) STRICT;
