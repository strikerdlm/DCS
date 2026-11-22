CREATE TABLE publication_diurnal_chamber_outcome (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    clock_window TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    trainees_reaching_target INTEGER NOT NULL CHECK(trainees_reaching_target > 0),
    reported_outcomes INTEGER NOT NULL CHECK(reported_outcomes BETWEEN 0 AND trainees_reaching_target),
    percent_as_printed REAL NOT NULL CHECK(percent_as_printed BETWEEN 0 AND 100),
    count_percent_discrepancy INTEGER NOT NULL CHECK(count_percent_discrepancy IN (0,1)),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint)
) STRICT;

CREATE TABLE publication_classification_chamber_descent (
    source_id TEXT NOT NULL REFERENCES publication_source,
    station TEXT NOT NULL,
    stratification TEXT NOT NULL CHECK(stratification IN ('time_of_day','barometric_pressure','weekday')),
    stratum TEXT NOT NULL,
    initial_pressure_range_mmhg_as_printed TEXT,
    no_descent INTEGER NOT NULL CHECK(no_descent >= 0),
    aeroembolism_descent INTEGER NOT NULL CHECK(aeroembolism_descent >= 0),
    other_descent INTEGER NOT NULL CHECK(other_descent >= 0),
    screening_exclusions INTEGER NOT NULL CHECK(screening_exclusions >= 0),
    classified_man_flights INTEGER NOT NULL CHECK(classified_man_flights=no_descent+aeroembolism_descent+other_descent),
    total_subjects_run_as_printed INTEGER CHECK(total_subjects_run_as_printed >= 0),
    percent_no_descent_as_printed REAL NOT NULL CHECK(percent_no_descent_as_printed BETWEEN 0 AND 100),
    percent_aeroembolism_descent_as_printed REAL NOT NULL CHECK(percent_aeroembolism_descent_as_printed BETWEEN 0 AND 100),
    percent_other_descent_as_printed REAL NOT NULL CHECK(percent_other_descent_as_printed BETWEEN 0 AND 100),
    percent_screening_exclusion_as_printed REAL NOT NULL CHECK(percent_screening_exclusion_as_printed BETWEEN 0 AND 100),
    percent_total_subjects_run_as_printed REAL CHECK(percent_total_subjects_run_as_printed BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,station,stratification,stratum)
) STRICT;

CREATE TABLE publication_classification_symptom_hour (
    source_id TEXT NOT NULL REFERENCES publication_source,
    station TEXT NOT NULL,
    symptom TEXT NOT NULL,
    hour_at_altitude INTEGER NOT NULL CHECK(hour_at_altitude BETWEEN 1 AND 3),
    reported_symptom_count INTEGER NOT NULL CHECK(reported_symptom_count >= 0),
    percent_of_symptom_total_as_printed REAL NOT NULL CHECK(percent_of_symptom_total_as_printed BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,station,symptom,hour_at_altitude)
) STRICT;

CREATE TABLE publication_staff_chamber_followup (
    source_id TEXT PRIMARY KEY REFERENCES publication_source,
    sampling_basis TEXT NOT NULL,
    people INTEGER NOT NULL CHECK(people > 0),
    type_64_examinations INTEGER NOT NULL CHECK(type_64_examinations >= people),
    training_units INTEGER CHECK(training_units > 0),
    cumulative_chamber_hours INTEGER CHECK(cumulative_chamber_hours > 0),
    maximum_individual_chamber_hours INTEGER CHECK(maximum_individual_chamber_hours > 0),
    reported_bends_susceptibility_people INTEGER NOT NULL CHECK(reported_bends_susceptibility_people BETWEEN 0 AND people),
    locator TEXT NOT NULL,
    note TEXT NOT NULL
) STRICT;

CREATE TABLE publication_staff_chamber_case_mention (
    source_id TEXT NOT NULL REFERENCES publication_staff_chamber_followup,
    mention_id TEXT NOT NULL,
    age_years INTEGER CHECK(age_years > 0),
    cumulative_chamber_hours INTEGER CHECK(cumulative_chamber_hours > 0),
    flight_number INTEGER CHECK(flight_number > 0),
    locator TEXT NOT NULL,
    reported_history TEXT NOT NULL,
    PRIMARY KEY(source_id,mention_id)
) STRICT;
