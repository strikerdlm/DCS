# USAFSAM archive and ADRAC development profiles

The public Air Force manual documents the Brooks altitude chamber research archive. Table 1 reports **1,190 DCS-positive exposures out of 2,946 completed exposures** and **356 people with DCS out of 573 people with a completed exposure**. These are overlapping summaries of the same archive. The table also lists 3,007 under “all completed subject-exposures” and 2,041 exposure days. The source gives no matching case numerator for the 3,007 line. The exposure count is on overlap hold because the archive reuses work described in earlier Armstrong reports. The publication provides summary data and a data dictionary. The exposure-level Access file remains with the custodian. [USAFSAM manual, Table 1, p. 6](https://dtic.minsky.ai/index/ADA521198/pdf) · [NTIS catalogue](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/ADA521198.xhtml) · [Overlap register](../data/chamber/v1.45/overlap.csv)

## ADRAC development profile inventory

Appendix D gives 41 development profile labels with a column titled “Subject N.” The printed entries sum to 1,013. The prose gives 1,012 completed exposures and says three exposures in the 2004 paper's 1,015 total lacked valid endpoints. The manual does not allocate the remaining difference between its printed cells and prose to a particular profile. The database preserves the values and records the comparison with the Navy compilation. Of 29 shared profile names, seven have different printed counts. These comparisons support record linkage and denominator review. Case counts from the Navy compilation stay with their own source denominators. [Appendix D, pp. 56–57](https://citeseerx.ist.psu.edu/document?doi=fd54938fecafffcd0289e96c8a985a53a922bc3e&repid=rep1&type=pdf) · [NEDU Appendix E](https://apps.dtic.mil/sti/trecms/pdf/AD1101527.pdf) · [Profile inventory](../data/chamber/v1.45/archive_profiles.csv)

## Workshop and meeting evidence

The supplement includes 24 printed summary rows from the workshop and the 1991 meeting abstract. The Bends Screening Index and mixed-gas suit tables report DCS and Doppler percentages, exposure totals and mean onset where applicable. The Doppler columns retain Spencer grades I–II and III–IV. The reported mean rows and preliminary denitrogenation cells have no printed evaluable denominators. The 1991 abstract describes 15 volunteers and eight conditions, while its two printed ground-level percentage pairs lack per-cell denominators. No event counts were inferred from these percentages. [Workshop pp. 337–340](https://archive.org/download/DTIC_ADA257612/DTIC_ADA257612.pdf#page=352) · [AsMA abstract 46](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/62/5/article-p445.pdf#page=8) · [Protocol summary rows](../data/chamber/v1.45/protocol_summaries.csv)

The workshop reports 0% DCS at 16,500 ft in 94 mixed-gas suit exposures. NEDU lists one case in 94 for its male 7.8-psia arm, and Dixon et al. report one clinical bends case. For the 30,000-ft Bends Screening Index exercise arm, the workshop gives 82% among 38 exposures, while NEDU reports 32 in 36. The source crosswalk records the conflicting values and the uncertainty over which exposures match. [Workshop p. 338](https://archive.org/download/DTIC_ADA257612/DTIC_ADA257612.pdf#page=352) · [Dixon et al.](https://pubmed.ncbi.nlm.nih.gov/3964151/) · [NEDU Appendix E](https://apps.dtic.mil/sti/trecms/pdf/AD1101527.pdf)

## Case linkage and verification

The manual identifies joint pain 105 minutes after arrival at the 18,000-ft stage, with resolution during descent. Its attribution to the Webb 2000 study and its description of the only staging-altitude case match the journal report. The timing annotates the existing one case in 173 staged exposures through `literature_observation_case_annotation`. The linked publication review stores the basis for the case match. [Manual p. 11](https://dtic.minsky.ai/index/ADA521198/pdf) · [Webb et al., Results p. 694](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/71/7/article-p692.pdf#page=3) · [Case annotation](../data/chamber/v1.45/case_annotations.csv)

The workshop tables were checked against the archived page images and the 1991 meeting abstract against the publisher's PDF. Firecrawl and Tavily supplied the public manual text and catalog information. An independent index of the PDF reproduced the Table 1 and D1 values. A direct PDF download of the manual remained unavailable. [Search and retrieval log](../data/chamber/publication-review/retrievals-2026-11-20-usafsam-archive.json)

```sh
python -m scripts.chamber_products --output-dir artifacts/chamber-products/2026-11-20-v1.45
```

Both databases passed integrity and foreign-key checks. The case annotation resolves to the original outcome row. The benchmark reproduced the previous evaluation, and all 50 tests in the linked database, publication review, report identity and observed benchmark suites passed.
