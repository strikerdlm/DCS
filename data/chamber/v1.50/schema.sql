CREATE TABLE publication_case_milestone (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    milestone TEXT NOT NULL,
    reporting_source_id TEXT NOT NULL REFERENCES publication_source,
    chamber_altitude_ft INTEGER CHECK(chamber_altitude_ft > 0),
    clock_time TEXT CHECK(clock_time GLOB '[0-2][0-9]:[0-5][0-9]' AND clock_time < '24:00'),
    elapsed REAL CHECK(elapsed >= 0),
    elapsed_unit TEXT CHECK(elapsed_unit IN ('seconds','minutes','hours','days')),
    elapsed_reference TEXT,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY (source_id, stratum, endpoint, milestone),
    FOREIGN KEY (source_id, stratum, endpoint) REFERENCES publication_observation,
    CHECK((elapsed IS NULL) = (elapsed_unit IS NULL)),
    CHECK((elapsed IS NULL) = (elapsed_reference IS NULL))
) STRICT;

UPDATE publication_source
SET access='full_text',
    disposition='crosswalk',
    url='https://babel.hathitrust.org/cgi/ssd?id=uiug.30112104083990;seq=451',
    locator='Case report, printed pp. 1364–1368',
    note='The original 19 March 1954 chamber event matches Berry and King Case 1 on profile, patient characteristics and clinical course. The existing case ID is retained.'
WHERE source_id='halbouty55_collapse';

UPDATE publication_source
SET access='full_text',
    disposition='extracted',
    url='https://archive.org/details/in.ernet.dli.2015.71422/page/n6/mode/1up',
    locator='Cases pp. 2–10 and comparison table p. 11',
    note='The original follow-up pages document five selected index cases. Case 1 is the 1954 event in Halbouty and Heisler. The 1943 episode in case 2 is a distinct recurrent exposure. No inception-cohort denominator.'
WHERE source_id='berry59_king';

UPDATE publication_observation
SET period='1954-03-19',
    locator='Halbouty and Heisler pp. 1364–1368 and Berry and King Case 1 pp. 2–3 and Table 2 p. 11',
    note='The original supplies the date and the follow-up reports earlier abdominal pain on ascent. The chamber team first observed signs 30 seconds after peak arrival. The two papers describe one selected chamber event. No ascertainable exposure denominator.'
WHERE source_id='berry59_king' AND stratum='case-01' AND endpoint='severe_dysbarism_source'
    AND period='1954-03';
