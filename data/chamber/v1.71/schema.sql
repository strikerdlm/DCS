-- The original wording remains in the sealed v1.21 sources.csv.
UPDATE publication_source
SET locator='Methods and Table 1, Results sections 1, 3 and 5–7, and Table 2',
    note='The author summary reports 931 ascents with DCS symptoms in 1,778 chamber person-ascents by the human research program. The 205 male volunteers and 13 simulated dives are distinct counting units. Results section 1 and section 3 margins were verified in the same archived author-summary transcription as v1.21. The full dissertation and page-image reader remain unavailable. The program total and nested comparisons overlap.'
WHERE source_id='katuntsev96_human'
  AND source_sha256='1c500ace0b7d95cb519e2404b0a4f81e550313e0ba9557f6cdc5bfb136e9bd7a'
  AND note='Author summary reports 205 male volunteers, 1,778 simulated person-ascents and 13 simulated dives across the program. The full dissertation and page-image reader were unavailable. Counts copied from the original wording in the public author-summary transcription. No program-wide case count was given.';
