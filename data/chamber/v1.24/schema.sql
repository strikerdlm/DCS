-- Replace metadata-only leads in place using their verified originals.
UPDATE publication_source
SET url='https://archive.org/download/in.ernet.dli.2015.71421/2015.71421.United-States-Armed-Forces-Medical-Journal912_djvu.txt',
    access='full_text',
    disposition='extracted',
    locator='Training Problem p. 939, Tables 2–3 pp. 940–941 and Summary pp. 947–948',
    source_sha256='4176bf3e686d1949347fa6b0ce4e3739dc99db46b5b5212ff4c2a2f3d2cea627',
    note='Primary USAF source prints 125 Grade IV hospitalization reactions over 1950–1955. No total exposure denominator for that six-year count. The 51,580 denominator applies to the separate 1955 rate table. The archive OCR is hashed and the exact counts and rates were visually checked.'
WHERE source_id='berry58_training' AND access='metadata' AND disposition='lead';

UPDATE publication_source
SET url='https://archive.org/download/in.ernet.dli.2015.71418/2015.71418.United-States-Armed-Forces-Medical-Journal612_djvu.txt',
    access='full_text',
    disposition='crosswalk',
    locator='Case Report pp. 1364–1370, particularly p. 1365 (Internet Archive leaf 1139)',
    source_sha256='9938366f6245bd7aac6b304ef48a2677119f8f6d6af51fe6cf816498d38a3366',
    note='This is the 1954 chamber episode already indexed as Berry and King Case 1. Matching signature includes peak 43,000 ft, shoulder pain after 30 seconds, unconsciousness and involuntary urination on descent through 30,000 ft, and the subsequent hospital course.'
WHERE source_id='halbouty55_collapse' AND access='metadata' AND disposition='lead';

UPDATE publication_overlap
SET evidence='Both originals are now available. The 1958 selected operational cases and the 1959 follow-up share a reporting network and have potentially matching dates. Case identities cannot be established from the degraded 1958 table. The 1958 outcomes entered here are chamber surveillance summaries.'
WHERE source_id='berry58_training' AND related_source='berry59_king' AND relationship='unresolved';
