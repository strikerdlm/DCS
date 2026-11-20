# UNAL EBSCO search for altitude decompression sickness

On 20 November 2026, an authenticated search of the UNAL EBSCO Discovery Service retrieved 64 ranked occurrences from three searches. They represent 58 EDS accessions and 50 provisional report identities in the publication register. Two additional public primary documents were checked. The register preserves the exact queries, settings, ranks, content providers, and follow-up decisions. These discovery and calibration searches sit outside the formal PRISMA identification count. [Retrieval snapshot](../data/chamber/publication-review/retrievals-2026-11-20.json) · [Review protocol](chamber-publication-review.md)

## Search coverage

| Search | EDS headline hits | Records captured | Purpose |
| --- | ---: | ---: | --- |
| Bilingual title and abstract search | 249 | 40 | First four relevance-ranked pages for chamber training and related altitude DCS studies |
| Supplementary chamber personnel search | 27 | 15 | Look for staff, technicians, instructors, and observers. EDS displayed 10 records on page one and five on page two, with no enabled next page. |
| Six known report titles | 21 | 9 | All six original papers were visible. The other hits were two news records and a 1977 same-title journal record with a different citation. |

Advanced search used Boolean/Phrase mode, all dates and relevance order. The library-availability limiter and equivalent-subject expansion were turned off. The previously unidentified default limiter was **Available in Library Collection**. Content-provider labels included MEDLINE, Scopus, and other sources. Separate searches in CINAHL and SPORTDiscus remain unverified. The headline totals are EDS estimates, and the exact-title test measures recovery of the six known papers under a lookup query. [EDS hit counts and deduplication](https://connect.ebsco.com/s/article/How-are-Hit-Counts-Calculated) · [19 November strategy](chamber-review-search.md)

## Evidence for the staff-to-trainee comparison

The six benchmark reports already have role-specific cells in the database. The table gives the source-reported case and exposure counts used in the register. Confirm the counting unit and follow-up before pooling, especially when staff had repeated exposures.

| Program and report | Staff cases / exposures | Trainee cases / exposures |
| --- | ---: | ---: |
| US Navy 1972–1975, [Bason et al.](https://pubmed.ncbi.nlm.nih.gov/971183/) | 57 / 14,959 | 22 / 73,561 |
| US Army, 63 months, [Piwinski et al., Table I](https://pubmed.ncbi.nlm.nih.gov/3790029/) | 12 / 1,949 | 8 / 12,596 |
| US Navy 1981–1988, [Bason and Yacavone](https://pubmed.ncbi.nlm.nih.gov/1755801/) | 62 / 25,022 | 78 / 111,674 |
| US Navy 1993–2002, [Rice et al., Table I](https://pubmed.ncbi.nlm.nih.gov/12546299/) | 11 / 6,293 | 83 / 31,860 |
| NASA JSC 1999–2016, [Conkin et al., original cohort and Table I](https://asma.kglmeridian.com/downloadpdf/view/journals/amhp/89/11/article-p941.pdf) | 1 / 3,612 | 6 / 9,560 |
| Eskişehir 2011–2018, [Ercan et al., Table 1](https://doi.org/10.22462/04.06.2020.5) | 2 / 615 | 6 / 6,657 |

- **Israeli Air Force.** Table 2 of Ben-Ari et al. identifies four aviation physiology instructors and seven other chamber cases. The report gives a combined total of 2,279 trainees and instructors. The 2015–2019 Nakdimon report covers some of the same calendar years. Pooling requires matched staff and trainee exposure counts and a case crosswalk between the two reports. [Ben-Ari et al., pp. 353–354](https://ima-files.s3.amazonaws.com/882985_368c23cf-11df-4519-bd21-98b0968b5113.pdf) · [Nakdimon and Ben-Ari](https://pubmed.ncbi.nlm.nih.gov/36309795/)
- **FAA Civil Aeromedical Institute.** Valdez's report, retrieved through the personnel search, lists three suspected reactions among 12,759 trainee records and describes suspected reactions among inside observers. The observer case narratives include a research flight and alternative diagnoses. The reported training-flight count therefore cannot establish a matched observer risk set for the listed reactions. The archive already includes the trainee and combined suspected-DCS rows. [Valdez, Tables 1–2 and pp. 5–6](https://www.govinfo.gov/content/pkg/GOVPUB-TD4_200-PURL-LPS83855/pdf/GOVPUB-TD4_200-PURL-LPS83855.pdf)
- **Shaw Air Force Base.** The staff search recovered the FY2004 outbreak report. The database already records 6 cases in 323 staff exposures and 4 in 780 student exposures. The investigators later questioned two student diagnoses. Preserve the outbreak designation and evaluate case definition before using this period. [Brandt et al., pp. 571–572](https://uhms.org/images/DCS-and-AGE-Journal-Watch/brandt_umo_decompression_sic.pdf)
- **Italian Air Force.** Biselli reported 0.1% DCS among 1,777 trainees. The chapter gives a rounded rate, without exact cases, a calendar window or instructor denominators. Resolve possible overlap with Morgagni's 2003–2009 series before using the trainee rate in any synthesis. [Biselli, printed p. 78](https://publicaciones.defensa.gob.es/media/downloadable/files/links/k/i/kindelan_25_linea.pdf) · [Morgagni et al.](https://pubmed.ncbi.nlm.nih.gov/20824995/)

This pass found no additional independent operational cohort with confirmed symptomatic DCS counts and matched staff and trainee person-exposure denominators.

## Additional chamber evidence

| Source | Extracted observation and interpretation |
| --- | --- |
| Polaris Dawn, [Rosenberg et al., AsMA abstract 14](https://asma.kglmeridian.com/downloadpdf/view/journals/amhp/95/8/article-p1.pdf) | Ground simulation yielded 0/8 participants with reported DCS symptoms and 4/8 with VGE. The 2026 IEEE report describes the same ground cohort and a modified flight profile. Count the ground cohort once. [IEEE report](https://ieeexplore.ieee.org/document/11520147) |
| UK MRI cohort, [Connolly et al., Results p. 779](https://asma.kglmeridian.com/downloadpdf/view/journals/amhp/89/9/article-p777.pdf) | Five of 20 selected volunteers reported a total of 10 historical research DCS episodes. The 1,417 total decompressions combine research and training and do not provide the denominator for the 10 episodes. |
| Swedish simulated EVA, [Karlsson et al., abstract](https://pubmed.ncbi.nlm.nih.gov/19442591/) | Two of 20 chamber participants had Doppler-detected VGE, including one detected only during provocation. The abstract does not provide an observed clinical DCS count for that group. |

The eight extracted observations are available in `review_search_observation`. Null counts and denominators preserve missing data. The six benchmark reports' original cells remain in `review_seed_role_cell`. Use `review_supplementary_role_cell` for the previously identified Shaw, Furry, and Baumgartner evidence. The linked source locations and overlap decisions support independent verification before formal screening and synthesis.
