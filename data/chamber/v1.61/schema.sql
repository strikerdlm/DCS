CREATE TABLE publication_gray_age_comparison (
    source_id TEXT NOT NULL REFERENCES publication_source,
    reprint_source_id TEXT NOT NULL REFERENCES publication_source,
    site TEXT NOT NULL,
    flight_pattern TEXT NOT NULL,
    age_range_years TEXT NOT NULL,
    age_mean_years REAL NOT NULL CHECK(age_mean_years > 0),
    reprint_subject_count INTEGER NOT NULL CHECK(reprint_subject_count > 0),
    reprint_severe_count INTEGER NOT NULL CHECK(reprint_severe_count BETWEEN 0 AND reprint_subject_count),
    reprint_rate_pct REAL NOT NULL CHECK(reprint_rate_pct BETWEEN 0 AND 100),
    reprint_relative_susceptibility INTEGER NOT NULL CHECK(reprint_relative_susceptibility >= 0),
    primary_subject_count INTEGER CHECK(primary_subject_count > 0),
    primary_severe_count INTEGER CHECK(primary_severe_count >= 0),
    primary_rate_pct REAL CHECK(primary_rate_pct BETWEEN 0 AND 100),
    note TEXT,
    analysis_role TEXT NOT NULL DEFAULT 'overlap_hold' CHECK(analysis_role='overlap_hold'),
    PRIMARY KEY(source_id,site,age_range_years),
    CHECK(source_id != reprint_source_id),
    CHECK(primary_severe_count <= primary_subject_count)
) STRICT;

CREATE TABLE publication_gray_density (
    source_id TEXT NOT NULL REFERENCES publication_source,
    site TEXT NOT NULL,
    flight_pattern TEXT NOT NULL,
    peak_altitude_ft INTEGER CHECK(peak_altitude_ft > 0),
    density_range TEXT NOT NULL,
    density_mean REAL NOT NULL CHECK(density_mean > 0),
    subject_count INTEGER NOT NULL CHECK(subject_count > 0),
    severe_symptom_count INTEGER NOT NULL CHECK(severe_symptom_count BETWEEN 0 AND subject_count),
    reported_pct REAL NOT NULL CHECK(reported_pct BETWEEN 0 AND 100),
    relative_susceptibility INTEGER NOT NULL CHECK(relative_susceptibility >= 0),
    printed_page INTEGER NOT NULL CHECK(printed_page > 0),
    pdf_page INTEGER NOT NULL CHECK(pdf_page > 0),
    analysis_role TEXT NOT NULL DEFAULT 'overlap_hold' CHECK(analysis_role='overlap_hold'),
    PRIMARY KEY(source_id,site,density_range)
) STRICT;

CREATE TABLE publication_motley_density (
    source_id TEXT NOT NULL REFERENCES publication_source,
    weight_height_lb_per_in TEXT NOT NULL,
    subject_count INTEGER NOT NULL CHECK(subject_count > 0),
    bearable_grades_1_2_pct REAL NOT NULL CHECK(bearable_grades_1_2_pct BETWEEN 0 AND 100),
    unbearable_grades_3_4_pct REAL NOT NULL CHECK(unbearable_grades_3_4_pct BETWEEN 0 AND 100),
    all_bends_pct REAL NOT NULL CHECK(all_bends_pct BETWEEN 0 AND 100),
    reported_bearable_unbearable_ratio REAL NOT NULL CHECK(reported_bearable_unbearable_ratio >= 0),
    reanalysis_source_id TEXT NOT NULL,
    reanalysis_site TEXT NOT NULL,
    reanalysis_density_range TEXT NOT NULL,
    printed_page INTEGER NOT NULL CHECK(printed_page > 0),
    pdf_page INTEGER NOT NULL CHECK(pdf_page > 0),
    analysis_role TEXT NOT NULL DEFAULT 'overlap_hold' CHECK(analysis_role='overlap_hold'),
    PRIMARY KEY(source_id,weight_height_lb_per_in),
    FOREIGN KEY(reanalysis_source_id,reanalysis_site,reanalysis_density_range)
        REFERENCES publication_gray_density
) STRICT;
