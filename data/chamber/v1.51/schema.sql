CREATE TABLE publication_ascent_reference (
    source_id TEXT NOT NULL REFERENCES publication_source,
    reference_number INTEGER NOT NULL CHECK(reference_number > 0),
    printed_reference_page INTEGER NOT NULL,
    citation TEXT NOT NULL,
    related_source_id TEXT REFERENCES publication_source,
    PRIMARY KEY (source_id, reference_number)
) STRICT;

CREATE TABLE publication_ascent_compilation (
    source_id TEXT NOT NULL REFERENCES publication_source,
    printed_page INTEGER NOT NULL CHECK(printed_page BETWEEN 56 AND 59),
    row_on_page INTEGER NOT NULL CHECK(row_on_page > 0),
    altitude_ft INTEGER NOT NULL CHECK(altitude_ft > 0),
    person_exposures INTEGER NOT NULL CHECK(person_exposures > 0),
    altitude_hours REAL NOT NULL CHECK(altitude_hours > 0),
    ground_denitrogenation_hours REAL NOT NULL CHECK(ground_denitrogenation_hours >= 0),
    exercise_cycles_per_hour INTEGER CHECK(exercise_cycles_per_hour > 0),
    ascent_rate_ft_min INTEGER NOT NULL CHECK(ascent_rate_ft_min > 0),
    symptom_pct INTEGER CHECK(symptom_pct BETWEEN 0 AND 100),
    forced_descent_pct INTEGER CHECK(forced_descent_pct BETWEEN 0 AND 100),
    reference_number INTEGER NOT NULL,
    reported_outcome_window_min INTEGER CHECK(reported_outcome_window_min > 0),
    analysis_role TEXT NOT NULL CHECK(analysis_role = 'overlap_hold'),
    PRIMARY KEY (source_id, printed_page, row_on_page),
    FOREIGN KEY (source_id, reference_number) REFERENCES publication_ascent_reference
) STRICT;

CREATE TABLE publication_ascent_compilation_total (
    source_id TEXT NOT NULL REFERENCES publication_source,
    locator TEXT NOT NULL,
    activity TEXT NOT NULL CHECK(activity IN ('rest','exercise')),
    denitrogenation TEXT NOT NULL CHECK(denitrogenation IN ('yes','no')),
    person_exposures INTEGER NOT NULL CHECK(person_exposures > 0),
    PRIMARY KEY (source_id, activity, denitrogenation)
) STRICT;

UPDATE publication_source
SET locator='Results p. 8, Table 1 p. 23, and Appendix B pp. 56–59',
    note='Historical compilation. The 150 Appendix B rows sum to 14,123 person-exposure entries and reconcile to the four Table 1 subtotals. Rounded symptom and forced-descent rates are held for cohort linkage and excluded from fitting and pooling.'
WHERE source_id='kumar89_ascent';
