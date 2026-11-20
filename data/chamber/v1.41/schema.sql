CREATE TABLE literature_observation_count_revision (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    denominator INTEGER NOT NULL CHECK(denominator > 0),
    earlier_cases INTEGER NOT NULL CHECK(earlier_cases BETWEEN 0 AND denominator),
    reconciled_cases INTEGER NOT NULL CHECK(reconciled_cases BETWEEN 0 AND denominator),
    earlier_locator TEXT NOT NULL,
    reconciled_locator TEXT NOT NULL,
    evidence TEXT NOT NULL,
    CHECK(earlier_cases <> reconciled_cases),
    PRIMARY KEY(source_id, stratum, endpoint),
    FOREIGN KEY(source_id, stratum, endpoint)
        REFERENCES literature_observation(source_id, stratum, endpoint)
) STRICT;

INSERT INTO literature_observation_count_revision
SELECT source_id, stratum, endpoint, denominator, cases, 11, locator,
       'Table II and Figure 2 p. A111; NASA/TP-2020-220529 Table F1 Test 5a',
       'The publisher abstract and NTRS print 18. Table II prints 29%, Figure 2 gives n=11, and the NASA Test 5a archive gives 11 of 38. The matches include 19 men, 19 women, the six-hour protocol, and four DCS cases.'
FROM literature_observation
WHERE source_id='waligora87' AND stratum='360min-prebreathe' AND endpoint='any_vge'
      AND cases=18 AND denominator=38;

UPDATE literature_observation
SET cases=(
        SELECT reconciled_cases FROM literature_observation_count_revision
        WHERE source_id='waligora87' AND stratum='360min-prebreathe' AND endpoint='any_vge'
    ),
    locator='Results Table II and Figure 2 p. A111, reconciled with NASA Table F1 Test 5a',
    note='The abstract prints 18/38. The article body and the NASA archive support 11/38. See literature_observation_count_revision.'
WHERE source_id='waligora87' AND stratum='360min-prebreathe' AND endpoint='any_vge'
      AND cases=18 AND denominator=38;

UPDATE literature_source
SET url='https://asma.kglmeridian.com/downloadpdf/view/journals/asem/58/9/article-pA110.pdf',
    access='full_text',
    source_sha256='ee1d8fb3fd151aaaa7ca8738de08336e788391403527eec1f350669080a624d7',
    extraction='Original publisher PDF pp. A110–A112 and NASA F1 tests 5a and 5b',
    note='Six-hour cohort matches the NASA archive. The abstract conflicts with the body on venous bubbles after a six-hour prebreathe. The eight-person published margin is preserved alongside the later eleven-person archived arm.'
WHERE source_id='waligora87' AND access='abstract';
