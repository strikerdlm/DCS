CREATE TABLE publication_prp_analysis_counts (
    source_id TEXT NOT NULL REFERENCES sharepoint_source,
    phase TEXT NOT NULL CHECK(phase IN ('I','II','III','IV','V-1','V-2','V-3')),
    total_exposures INTEGER NOT NULL CHECK(total_exposures > 0),
    hypothesis_exposures INTEGER NOT NULL CHECK(hypothesis_exposures BETWEEN 1 AND total_exposures),
    hypothesis_dcs_cases INTEGER NOT NULL CHECK(hypothesis_dcs_cases BETWEEN 0 AND hypothesis_exposures),
    nasa_model_exposures INTEGER NOT NULL CHECK(nasa_model_exposures BETWEEN 1 AND total_exposures),
    nasa_model_dcs_cases INTEGER NOT NULL CHECK(nasa_model_dcs_cases BETWEEN 0 AND nasa_model_exposures),
    research_model_exposures INTEGER NOT NULL CHECK(research_model_exposures BETWEEN 1 AND total_exposures),
    research_model_dcs_cases INTEGER NOT NULL CHECK(research_model_dcs_cases BETWEEN 0 AND research_model_exposures),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,phase)
) STRICT;
