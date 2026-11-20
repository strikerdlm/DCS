UPDATE publication_source
SET url = 'https://pubmed.ncbi.nlm.nih.gov/11766705/',
    identifier = 'PMID:11766705; SMME:1999:12:3:157',
    access = 'primary_abstract',
    locator = 'Author abstract, Methods and Results',
    source_sha256 = '20e3e9366cfd0d33d650eb2110291241ff354b413935081ce9b43c2626f682da',
    note = 'The authors report 43 study participants. They describe age and prebreathe comparisons without exact event numerators, arm denominators or published outcome tables in the public abstract. No outcome row is supported by this edition.'
WHERE source_id = 'zhang99_dcs_susceptibility' AND access = 'metadata' AND disposition = 'lead';

UPDATE publication_overlap
SET related_source = 'marbarger57_denit',
    evidence = 'Both original articles are now available. The 1957 series contrasts 120 minutes of oxygen across five starting conditions and a separate direct ascent control, with 120 minutes at target. The 1961 trial series varies ambient-air residence at 12,000 ft and has a 60-minute target limit with standardized exercise. Trial protocols differ. The reports do not supply shared participant identifiers.'
WHERE source_id = 'marotta61_partial'
  AND related_source = 'Marbarger et al. 1957, J Aviat Med 28:127–133 (NASA AD245)'
  AND relationship = 'unresolved';
