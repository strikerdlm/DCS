UPDATE publication_source
SET citation='Fryer DI. A survey of an RAF decompression test at 28,000 feet. AGARD Conference Proceedings No. 2. 1965 meeting, printed pp. 279–293, including tables and figures.',
    url='https://publications.sto.nato.int/publications/AGARD/AGARD-CP-2/AGARD-CP-2.pdf#page=290',
    access='full_text',
    disposition='extracted',
    locator='Results pp. 282–285, Tables I–IV pp. 288–289 and Figure 4 pp. 292–293',
    source_sha256='93c76e17c673921009fe3cde96b5de15e884981558ae0772b7fb8ee590b3da23',
    note='Original conference report for the existing RAF 28,000-ft selection series. The SHA-256 is for the NATO proceedings volume. New severity, retest, weight and session details supplement the later monograph. The overall cohort, symptomatic runs and age cells already represented by the monograph are reused.'
WHERE source_id='fryer65_selection';

CREATE TABLE publication_fryer_retest_group (
    source_id TEXT NOT NULL REFERENCES publication_source,
    group_as_reported TEXT NOT NULL CHECK(group_as_reported IN (
        'first_test','second_after_mild_or_moderate','second_after_nil'
    )),
    people INTEGER NOT NULL CHECK(people > 0),
    severe INTEGER NOT NULL CHECK(severe >= 0),
    mild_or_moderate INTEGER NOT NULL CHECK(mild_or_moderate >= 0),
    nil INTEGER NOT NULL CHECK(nil >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,group_as_reported),
    CHECK(severe + mild_or_moderate + nil = people)
) STRICT;

CREATE TABLE publication_fryer_chamber_cluster (
    source_id TEXT NOT NULL REFERENCES publication_source,
    people_reporting_symptoms INTEGER NOT NULL CHECK(people_reporting_symptoms >= 0),
    sessions_as_reported INTEGER CHECK(sessions_as_reported >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,people_reporting_symptoms)
) STRICT;
