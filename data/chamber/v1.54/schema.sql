CREATE TABLE publication_crossover_run (
    source_id TEXT NOT NULL REFERENCES publication_source,
    participant_number INTEGER NOT NULL CHECK(participant_number > 0),
    condition TEXT NOT NULL,
    symptom_status TEXT NOT NULL CHECK(symptom_status IN ('reported','absent','unresolved')),
    symptom_onset_min INTEGER CHECK(symptom_onset_min BETWEEN 0 AND 90),
    forced_descent_status TEXT NOT NULL CHECK(forced_descent_status IN ('reported','absent','unresolved')),
    forced_descent_min INTEGER CHECK(forced_descent_min BETWEEN 0 AND 90),
    maximum_symptom_grade INTEGER CHECK(maximum_symptom_grade BETWEEN 1 AND 9),
    grade_annotation TEXT,
    locator TEXT NOT NULL,
    analysis_role TEXT NOT NULL DEFAULT 'overlap_hold' CHECK(analysis_role='overlap_hold'),
    PRIMARY KEY(source_id, participant_number, condition),
    CHECK((symptom_status='reported') = (maximum_symptom_grade IS NOT NULL)),
    CHECK(symptom_onset_min IS NULL OR symptom_status='reported'),
    CHECK((forced_descent_status='reported') = (forced_descent_min IS NOT NULL)),
    CHECK(grade_annotation IS NULL OR maximum_symptom_grade IS NOT NULL),
    CHECK(symptom_onset_min IS NULL OR forced_descent_min IS NULL OR symptom_onset_min <= forced_descent_min)
) STRICT;

UPDATE publication_source
SET access='full_text',
    disposition='crosswalk',
    url='https://asma.kglmeridian.com/downloadpdf/view/journals/joam/18/2/article-p165.pdf',
    locator='Methods and case series pp. 165–166 and Summary pp. 167–168',
    source_sha256='a5ce682ecad1aa8eafabc0646a9f42bc65a8dc9bf0db66131c2a8e233bdce278',
    note='The same 20-person cohort is retained under Navy report AD0622164. The journal remains the source of the incapacitating-bends margin. Case 3 specifies descent from 21,000 ft, while the summary gives an 18,000–20,000-ft range for the visual episodes. The 387 program ascents lack individual linkage.'
WHERE source_id='houston47_low_altitude';
