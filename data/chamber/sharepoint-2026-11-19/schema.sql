CREATE TABLE sharepoint_source (
    source_id TEXT PRIMARY KEY,
    citation TEXT NOT NULL,
    kind TEXT NOT NULL,
    disposition TEXT NOT NULL CHECK(disposition IN
        ('extracted', 'already_indexed', 'methods', 'timeline_lead')),
    access TEXT NOT NULL CHECK(access IN
        ('sharepoint_full_text', 'hash_matched_synced_file', 'public_crosscheck')),
    source_file TEXT,
    source_sha256 TEXT CHECK(length(source_sha256) = 64),
    public_url TEXT,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    CHECK(access = 'public_crosscheck' OR (source_file IS NOT NULL AND source_sha256 IS NOT NULL))
) STRICT;

CREATE TABLE sharepoint_observation (
    source_id TEXT NOT NULL REFERENCES sharepoint_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    analysis_role TEXT NOT NULL CHECK(analysis_role IN
        ('descriptive', 'overlap_hold', 'overlapping_margin', 'denominator_conflict', 'same_cohort',
         'case_conditional', 'case_control', 'doppler_readings', 'joint_cell', 'count_only',
         'secondary_distribution')),
    events INTEGER CHECK(events >= 0),
    denominator INTEGER CHECK(denominator > 0 AND (events IS NULL OR events <= denominator)),
    denominator_unit TEXT NOT NULL,
    reported_percent REAL CHECK(reported_percent BETWEEN 0 AND 100),
    pressure_psia REAL CHECK(pressure_psia > 0),
    altitude_ft INTEGER CHECK(altitude_ft > 0),
    planned_plateau_min INTEGER CHECK(planned_plateau_min > 0),
    source_ratio REAL CHECK(source_ratio > 0),
    ambulatory INTEGER CHECK(ambulatory IN (0, 1)),
    protocol TEXT NOT NULL,
    outcome_window TEXT NOT NULL,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id, stratum, endpoint),
    CHECK((events IS NULL) <> (reported_percent IS NULL)),
    CHECK((denominator IS NULL) = (analysis_role IN
        ('count_only', 'joint_cell', 'secondary_distribution'))),
    CHECK((denominator_unit = 'doppler_grade_reading') = (analysis_role = 'doppler_readings'))
) STRICT;

-- The row number locates a printed table entry. It cannot link people across tests.
CREATE TABLE sharepoint_vge_positive_record (
    source_id TEXT NOT NULL REFERENCES sharepoint_source,
    source_table INTEGER NOT NULL CHECK(source_table IN (14, 15)),
    source_row INTEGER NOT NULL CHECK(source_row BETWEEN 1 AND 13),
    phase TEXT NOT NULL CHECK(phase IN ('I', 'II')),
    ergometry_order TEXT NOT NULL CHECK(ergometry_order IN ('first', 'second')),
    age_years REAL NOT NULL CHECK(age_years > 0),
    weight_kg REAL NOT NULL CHECK(weight_kg > 0),
    height_m REAL NOT NULL CHECK(height_m > 0),
    source_male INTEGER NOT NULL CHECK(source_male IN (0, 1)),
    bmi_kg_m2 REAL NOT NULL CHECK(bmi_kg_m2 > 0),
    dcs INTEGER NOT NULL CHECK(dcs IN (0, 1)),
    post_exposure_dcs_mark INTEGER CHECK(
        post_exposure_dcs_mark IS NULL OR (post_exposure_dcs_mark = 1 AND dcs = 1)
    ),
    max_spencer_grade TEXT NOT NULL CHECK(max_spencer_grade IN ('I', 'II', 'III', 'IV')),
    first_vge_detection_min INTEGER NOT NULL CHECK(first_vge_detection_min >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id, source_table, source_row),
    CHECK((source_table = 14) = (ergometry_order = 'first'))
) STRICT;

CREATE TABLE sharepoint_overlap (
    source_id TEXT NOT NULL REFERENCES sharepoint_source,
    related_source TEXT NOT NULL,
    relationship TEXT NOT NULL CHECK(relationship IN
        ('same_cohort', 'subset', 'same_protocol', 'likely_overlap', 'possible_overlap',
         'edition_reprint', 'model_reference', 'secondary_reference', 'conference_precursor')),
    evidence TEXT NOT NULL,
    PRIMARY KEY(source_id, related_source)
) STRICT;

-- Resolve only reviewed identities. All printed rows remain available for audit.
CREATE VIEW citation_reference_reprint AS
    SELECT repeated.citing_source_id, repeated.ref_no, original.ref_no AS canonical_ref_no
    FROM citation_reference repeated
    JOIN citation_reference original USING(citing_source_id, openalex_id)
    WHERE repeated.citing_source_id = 'mahon2014'
      AND repeated.ref_no = 84 AND original.ref_no = 53
      AND repeated.openalex_id = 'W1552966748';

CREATE VIEW citation_deduplicated_reference AS
    SELECT r.* FROM citation_reference r
    WHERE NOT EXISTS (
        SELECT 1 FROM citation_reference_reprint x
        WHERE x.citing_source_id = r.citing_source_id AND x.ref_no = r.ref_no
    );

CREATE VIEW a1309_profile_reprint AS
    SELECT x.profile, 'nasa_test' AS canonical_table, n.source_id AS canonical_source_id,
           n.test_id AS canonical_stratum, 'dcs' AS endpoint
    FROM a1309_nasa_overlap x
    JOIN a1309_profile p USING(profile)
    JOIN nasa_test n USING(test_id)
    WHERE x.agreement = 'same printed n and cases'
      AND p.exposures = n.dcs_denominator AND p.exact_cases = n.dcs_cases
    UNION ALL
    SELECT p.profile, 'citation_observation', o.source_id, o.stratum, o.endpoint
    FROM a1309_profile p
    JOIN citation_observation o ON o.source_id = 'webb96_preoxygenation'
        AND o.stratum = 'exercise10_rest50' AND o.endpoint = 'dcs'
    WHERE p.profile = 'PE1-A'
      AND p.exposures = o.denominator AND p.exact_cases = o.numerator;

CREATE VIEW a1309_deduplicated_profile AS
    SELECT p.* FROM a1309_profile p
    WHERE NOT EXISTS (SELECT 1 FROM a1309_profile_reprint x WHERE x.profile = p.profile);

CREATE VIEW sharepoint_observation_reprint AS
    WITH nasa_protocol(stratum, test_id) AS (
        VALUES ('3a','3a'), ('3b','3b'), ('8a','8a'),
               ('Phase_I','P I'), ('Phase_II','P II'), ('Phase_IV','P IV')
    )
    SELECT a.source_id, a.stratum, a.endpoint,
           'sharepoint_observation' AS canonical_table, b.source_id AS canonical_source_id,
           b.stratum AS canonical_stratum
    FROM sharepoint_observation a
    JOIN sharepoint_observation b ON b.source_id = 'celis23_thesis'
        AND b.endpoint = a.endpoint
        AND ((a.stratum = 'results_total' AND b.stratum = 'results_total')
          OR (a.stratum = 'diagnosed_cases' AND b.stratum = 'resumen_cases'))
    WHERE a.source_id = 'celis23_abstract'
      AND a.denominator_unit = b.denominator_unit
      AND a.denominator = b.denominator AND a.events = b.events
    UNION ALL
    SELECT s.source_id, s.stratum, s.endpoint, 'nasa_test', n.source_id, n.test_id
    FROM sharepoint_observation s
    JOIN nasa_protocol p ON p.stratum = s.stratum
    JOIN nasa_test n ON n.test_id = p.test_id
    WHERE s.source_id = 'nasa_treatment' AND s.endpoint = 'dcs'
      AND s.denominator = n.dcs_denominator AND s.pressure_psia = n.pressure_psia
      AND s.planned_plateau_min = n.duration_hours * 60
      AND s.reported_percent = round(100.0 * n.dcs_cases / n.dcs_denominator, 1);

CREATE VIEW sharepoint_deduplicated_observation AS
    SELECT o.* FROM sharepoint_observation o
    WHERE NOT EXISTS (
        SELECT 1 FROM sharepoint_observation_reprint x
        WHERE x.source_id = o.source_id AND x.stratum = o.stratum AND x.endpoint = o.endpoint
    );
