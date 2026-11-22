-- The ratio is the document's probability expression. Its terms do not count
-- observed cases or exposures.
CREATE TABLE publication_nasa_cliff_probability (
    source_id TEXT NOT NULL REFERENCES publication_source,
    scenario TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    probability_as_reported REAL NOT NULL CHECK(probability_as_reported BETWEEN 0 AND 1),
    ratio_numerator INTEGER CHECK(ratio_numerator >= 0),
    ratio_denominator INTEGER CHECK(ratio_denominator > 0 AND ratio_numerator <= ratio_denominator),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,scenario,endpoint),
    CHECK((ratio_numerator IS NULL) = (ratio_denominator IS NULL))
) STRICT;

-- The historical total uses the printed EVA unit. Person-EVA equivalence and
-- overlap with published program rosters are unresolved.
CREATE TABLE publication_nasa_cliff_eva_history (
    source_id TEXT NOT NULL REFERENCES publication_source,
    scope TEXT NOT NULL,
    documented_dcs_cases INTEGER NOT NULL CHECK(documented_dcs_cases >= 0),
    eva_count INTEGER NOT NULL CHECK(eva_count > 0 AND documented_dcs_cases <= eva_count),
    unit_as_printed TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,scope)
) STRICT;
