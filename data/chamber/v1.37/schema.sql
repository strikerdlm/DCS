UPDATE citation_source
SET url='https://asma.kglmeridian.com/downloadpdf/view/journals/asem/71/2/article-p115.pdf',
    access='full_text',
    source_sha256='4fb884a386484222c49ac3878f88191caa527cac25ee59b099ab3f0ce58d3819',
    note='Original publisher PDF, Methods and Results pp. 115–117. Table and text detail the treatment, onset and ultrasound follow-up of selected research cases. The prior clinical exposure and overall treatment outcome remain in their original rows.'
WHERE source_id='krause00' AND access='primary_abstract';

CREATE TABLE publication_menstrual_case_margin (
    source_id TEXT NOT NULL REFERENCES publication_source,
    days_since_lmp_start INTEGER NOT NULL CHECK(days_since_lmp_start BETWEEN 0 AND 29),
    type_i_bcp INTEGER CHECK(type_i_bcp>=0),
    type_i_no_bcp INTEGER CHECK(type_i_no_bcp>=0),
    type_ii_bcp INTEGER CHECK(type_ii_bcp>=0),
    type_ii_no_bcp INTEGER CHECK(type_ii_no_bcp>=0),
    locator TEXT NOT NULL,
    note TEXT,
    PRIMARY KEY(source_id, days_since_lmp_start)
) STRICT;

CREATE TABLE web_vge_exercise_peak (
    source_id TEXT NOT NULL REFERENCES web_source,
    participant_number INTEGER NOT NULL CHECK(participant_number>0),
    condition TEXT NOT NULL CHECK(condition IN ('N','H')),
    pre_exercise_peak_grade INTEGER NOT NULL CHECK(pre_exercise_peak_grade BETWEEN 0 AND 5),
    post_exercise_peak_grade INTEGER CHECK(post_exercise_peak_grade BETWEEN 0 AND 5),
    locator TEXT NOT NULL,
    note TEXT,
    CHECK(post_exercise_peak_grade IS NOT NULL OR note IS NOT NULL),
    PRIMARY KEY(source_id, participant_number, condition)
) STRICT;
