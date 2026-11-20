CREATE TABLE publication_piwinski_halo_case (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    case_number INTEGER NOT NULL CHECK(case_number BETWEEN 1 AND 4),
    reported_age_years INTEGER NOT NULL CHECK(reported_age_years > 0),
    printed_type TEXT NOT NULL CHECK(printed_type IN ('I','II')),
    onset_description TEXT NOT NULL,
    reported_onset_clock TEXT,
    symptoms TEXT NOT NULL,
    resolution TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,case_number),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;

UPDATE publication_source
SET url='https://asma.kglmeridian.com/downloadpdf/view/journals/asem/57/6/article-p600.pdf',
    access='full_text',
    locator='Printed pp. 600–602, Case Histories, Figure 1 and Discussion',
    source_sha256='529a33c35a24a5b3cd67b323df7058da8f0c0ed68cf61af33c5a6db6540072b0',
    note='Original journal article distinguishes the affected nine-person flight from the wider 27-exposure profile experience. Both counts include the same four DCS cases.'
WHERE source_id='piwinski86_halo' AND access='primary_abstract';

UPDATE publication_observation
SET prebreathe_min=30,
    protocol='Selected nine-person HALO chamber flight. The narrative reports 30 minutes of preoxygenation, a 32,500-ft peak during the first chamber flight, and a subsequent rapid-decompression simulation. The students then took a short aircraft flight after training.',
    outcome_window='The four patients reported symptoms the following morning. Exact elapsed onset and follow-up for noncases are unavailable.',
    locator='Printed pp. 600–601, Case Histories and Discussion',
    note='The four cases in this nine-person flight are also the numerator in the article’s wider 4/27 profile margin. The earlier 63-month routine surveillance excludes HALO. Figure 1 depicts a peak higher than the completed peak given in the case narrative.'
WHERE source_id='piwinski86_halo' AND stratum='single-halo-training-flight'
  AND endpoint='dcs' AND numerator=4 AND denominator=9;
