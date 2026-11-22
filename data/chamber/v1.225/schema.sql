CREATE TABLE publication_historical_program_population (
    source_id TEXT NOT NULL REFERENCES publication_source,
    scope TEXT NOT NULL,
    tested_description TEXT NOT NULL,
    approximate_people_tested INTEGER CHECK(approximate_people_tested > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,scope)
) STRICT;

CREATE TABLE publication_historical_program_rate (
    source_id TEXT NOT NULL REFERENCES publication_source,
    program_as_printed TEXT NOT NULL,
    scope TEXT NOT NULL,
    reported_percent REAL NOT NULL CHECK(reported_percent BETWEEN 0 AND 100),
    site_count_for_range INTEGER CHECK(site_count_for_range > 0),
    site_min_percent REAL CHECK(site_min_percent BETWEEN 0 AND reported_percent),
    site_max_percent REAL CHECK(site_max_percent BETWEEN reported_percent AND 100),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,program_as_printed),
    FOREIGN KEY(source_id,scope) REFERENCES publication_historical_program_population(source_id,scope),
    CHECK((site_count_for_range IS NULL) = (site_min_percent IS NULL)),
    CHECK((site_count_for_range IS NULL) = (site_max_percent IS NULL))
) STRICT;

CREATE TABLE publication_berkeley_interim_group (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    altitude_ft INTEGER NOT NULL CHECK(altitude_ft > 0),
    exercise_interval_min REAL NOT NULL CHECK(exercise_interval_min > 0),
    reported_runs INTEGER NOT NULL CHECK(reported_runs > 0),
    percent_having_symptoms REAL NOT NULL CHECK(percent_having_symptoms BETWEEN 0 AND 100),
    percent_incapacitated REAL NOT NULL CHECK(percent_incapacitated BETWEEN 0 AND percent_having_symptoms),
    mean_first_symptom_min REAL NOT NULL CHECK(mean_first_symptom_min >= 0),
    mean_incapacitation_min REAL NOT NULL CHECK(mean_incapacitation_min >= 0),
    mean_maximum_intensity_as_printed REAL NOT NULL CHECK(mean_maximum_intensity_as_printed >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum)
) STRICT;

CREATE TABLE publication_fraser_ascent_group (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    comparison TEXT NOT NULL CHECK(comparison IN ('table_i','table_ii')),
    intermediate_altitude_ft INTEGER CHECK(intermediate_altitude_ft > 0),
    intermediate_hold_min INTEGER CHECK(intermediate_hold_min > 0),
    reported_people INTEGER NOT NULL CHECK(reported_people > 0),
    reported_runs INTEGER NOT NULL CHECK(reported_runs >= reported_people),
    sum_of_subject_means_as_printed INTEGER NOT NULL CHECK(sum_of_subject_means_as_printed >= 0),
    overall_mean_score_as_printed INTEGER NOT NULL CHECK(overall_mean_score_as_printed >= 0),
    percent_of_control_score_as_printed INTEGER NOT NULL CHECK(percent_of_control_score_as_printed > 0),
    no_symptoms_percent_as_printed INTEGER NOT NULL CHECK(no_symptoms_percent_as_printed BETWEEN 0 AND 100),
    mild_only_percent_as_printed INTEGER NOT NULL CHECK(mild_only_percent_as_printed BETWEEN 0 AND 100),
    moderate_or_severe_percent_as_printed INTEGER NOT NULL CHECK(moderate_or_severe_percent_as_printed BETWEEN 0 AND 100),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum),
    CHECK((intermediate_altitude_ft IS NULL) = (intermediate_hold_min IS NULL))
) STRICT;

CREATE TABLE publication_fraser_ascent_score (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    subject_number INTEGER NOT NULL CHECK(subject_number > 0),
    reported_runs INTEGER NOT NULL CHECK(reported_runs > 0),
    mean_symptom_score INTEGER NOT NULL CHECK(mean_symptom_score >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,subject_number),
    FOREIGN KEY(source_id,stratum) REFERENCES publication_fraser_ascent_group(source_id,stratum)
) STRICT;
