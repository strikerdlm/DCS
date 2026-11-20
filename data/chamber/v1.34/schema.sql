UPDATE publication_source
SET url='https://pmc.ncbi.nlm.nih.gov/articles/PMC11363104/',
    identifier='DOI:10.1113/EP091853; PMID:38923893; PMCID:PMC11363104; DiVA:1909222',
    citation='Gottschalk F, Gennser M, Günther M, Eiken O, Elia A. Eccentric exercise before a 90 min exposure at 24,000 ft increases decompression strain depending on body region but not total muscle mass recruited. Exp Physiol. 2024;109:1517–1528.',
    access='full_text',
    disposition='extracted',
    locator='Methods sections 2.8–2.9, Results section 3.4 and Table 1',
    source_sha256='c765feb647f0618b4d385afc90bda1520250be8d72878e727e6c1f83cd23b5ce',
    note='Digest identifies Europe PMC full-text XML. Firecrawl and XML Table 1 agree for the 33 protocol-by-participant VGE sessions. Exact clinical counts and individual examination times are unavailable. The full participant-level study dataset is available by author request under the paper''s data availability statement.'
WHERE source_id='gottschalk24_region' AND access='primary_abstract' AND disposition='lead';

CREATE TABLE publication_postdive_exposure (
    source_id TEXT NOT NULL REFERENCES publication_source,
    participant_code TEXT NOT NULL,
    exposure_code TEXT NOT NULL,
    altitude_m INTEGER NOT NULL CHECK(altitude_m>0),
    prior_dive_depth_m INTEGER CHECK(prior_dive_depth_m>0),
    prior_dive_duration_min INTEGER CHECK(prior_dive_duration_min>0),
    surface_interval_h INTEGER CHECK(surface_interval_h>0),
    planned_altitude_min INTEGER NOT NULL CHECK(planned_altitude_min>0),
    grade1_min INTEGER CHECK(grade1_min BETWEEN 0 AND planned_altitude_min),
    grade2_min INTEGER CHECK(grade2_min BETWEEN 0 AND planned_altitude_min),
    grade3_min INTEGER CHECK(grade3_min BETWEEN 0 AND planned_altitude_min),
    grade4_min INTEGER CHECK(grade4_min BETWEEN 0 AND planned_altitude_min),
    clinical_status TEXT NOT NULL CHECK(clinical_status IN (
        'confirmed','questionable','no_symptoms_reported'
    )),
    symptom_onset_lower_min INTEGER CHECK(symptom_onset_lower_min>=0),
    symptom_onset_upper_min INTEGER CHECK(symptom_onset_upper_min>=symptom_onset_lower_min),
    reported_recompression_min INTEGER CHECK(reported_recompression_min>=symptom_onset_upper_min),
    symptom_site TEXT,
    locator TEXT NOT NULL,
    note TEXT,
    CHECK((prior_dive_depth_m IS NULL) = (prior_dive_duration_min IS NULL)),
    CHECK((prior_dive_depth_m IS NULL) = (surface_interval_h IS NULL)),
    CHECK((prior_dive_depth_m IS NULL) = (exposure_code='no-dive')),
    CHECK((symptom_onset_lower_min IS NULL) = (symptom_onset_upper_min IS NULL)),
    CHECK((clinical_status='no_symptoms_reported') = (symptom_onset_lower_min IS NULL)),
    CHECK((clinical_status='no_symptoms_reported') = (symptom_site IS NULL)),
    CHECK((clinical_status='confirmed') = (reported_recompression_min IS NOT NULL)),
    PRIMARY KEY(source_id, participant_code, altitude_m, exposure_code)
) STRICT;

CREATE TABLE publication_vge_peak (
    source_id TEXT NOT NULL REFERENCES publication_source,
    participant_code TEXT NOT NULL,
    protocol TEXT NOT NULL,
    peak_eb_grade_rest INTEGER NOT NULL CHECK(peak_eb_grade_rest BETWEEN 0 AND 5),
    peak_eb_grade_knee_flex INTEGER NOT NULL CHECK(peak_eb_grade_knee_flex BETWEEN 0 AND 5),
    peak_eb_grade_arm_flex INTEGER NOT NULL CHECK(peak_eb_grade_arm_flex BETWEEN 0 AND 5),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,participant_code,protocol)
) STRICT;
