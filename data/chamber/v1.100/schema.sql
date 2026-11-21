CREATE TABLE publication_altitude_symptom_survey (
    source_id TEXT PRIMARY KEY REFERENCES publication_source,
    respondent_count INTEGER NOT NULL CHECK(respondent_count > 0),
    altitude_cutoff_ft INTEGER NOT NULL CHECK(altitude_cutoff_ft > 0),
    population TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL
) STRICT;

CREATE TABLE publication_altitude_symptom_survey_item (
    source_id TEXT NOT NULL REFERENCES publication_altitude_symptom_survey,
    symptom TEXT NOT NULL,
    above_cutoff_percent TEXT NOT NULL CHECK(CAST(above_cutoff_percent AS REAL) BETWEEN 0 AND 100
        AND above_cutoff_percent GLOB '*[0-9]*' AND above_cutoff_percent NOT GLOB '*[^0-9.]*'
        AND length(above_cutoff_percent) - length(replace(above_cutoff_percent,'.','')) <= 1),
    below_cutoff_percent TEXT NOT NULL CHECK(CAST(below_cutoff_percent AS REAL) BETWEEN 0 AND 100
        AND below_cutoff_percent GLOB '*[0-9]*' AND below_cutoff_percent NOT GLOB '*[^0-9.]*'
        AND length(below_cutoff_percent) - length(replace(below_cutoff_percent,'.','')) <= 1),
    above_item_denominator INTEGER CHECK(above_item_denominator > 0),
    below_item_denominator INTEGER CHECK(below_item_denominator > 0),
    PRIMARY KEY(source_id,symptom)
) STRICT;
