-- The original archive and the archived author abstract resolve two earlier leads.
UPDATE publication_source
SET url='https://archive.org/download/in.ernet.dli.2015.71422/2015.71422.United-States-Armed-Forces-Medical-Journal10124-12_djvu.txt',
    access='full_text',
    disposition='extracted',
    locator='Case Reports pp. 2–10 and Table 2 p. 11 (Internet Archive scan leaf 15)',
    source_sha256='900d0f1dd5928db231cb53f50ff9befe52f02fa4a9525d18307672eed46af0c4',
    note='Five selected survivors, with three chamber and two aircraft index episodes. Case 2 also has a distinct earlier 1943 chamber episode. No source-wide exposure denominator. The digest is for the original archive OCR and the summary counts and altitudes were checked against the page scans.'
WHERE source_id='berry59_king'
  AND access='metadata'
  AND disposition='lead';

UPDATE publication_source
SET url='https://ntrs.nasa.gov/api/citations/19700011380/downloads/19700011380.pdf#page=34',
    identifier='DOI:10.1152/jappl.1969.26.2.182; PMID:5765207; AIAA:A69-41292',
    access='primary_abstract',
    disposition='extracted',
    locator='Author abstract A69-41292, bibliography p. 27 (PDF p. 34)',
    source_sha256='64c2d29b9705e2a3063deb3661c94d37c262ed1abe7a9d4e5d0182695ad39e2c',
    note='The NASA-hosted bibliography reprints the authors'' abstract. It gives 44 participants and 322 flights. Exposure-level counts are for symptomatic participants at rest only. Full journal tables and linkage to the other USAFSAM studies are unavailable.'
WHERE source_id='allen69_zoom'
  AND access='metadata'
  AND disposition='lead';

UPDATE publication_overlap
SET relationship='unresolved',
    evidence='Malette cites the Berry and King follow-up. All five patients in the original cohort survived. The aggregate review does not establish which, if any, of the Berry and King episodes it tabulates.'
WHERE source_id='berry59_king' AND related_source='malette62_dysbarism'
  AND relationship='likely_overlap';
