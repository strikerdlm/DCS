# USAF treated-case surveillance and commercial-flight observations

Release 1.36 adds 50 outcome rows, one citation-based reported rate, six source records and eight overlap links. [Outcomes](../data/chamber/v1.36/observations.csv) · [Reported rate](../data/chamber/v1.36/reported_rates.csv) · [Source register](../data/chamber/v1.36/sources.csv) · [Overlap links](../data/chamber/v1.36/overlap.csv)

## USAF treatment archive

Weien and Baumgartner reviewed 528 treated cases from 1977 through 1986, comprising 507 chamber cases and 21 aircraft cases. Exact published chamber exposure figures cover 1979 through 1986. The two tables preserve separate margins over the same 429 treated cases. [Original article, Tables I–V](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/61/9/article-p833.pdf)

| Published margin | Groups, treated cases / exposure figure | Total |
| --- | --- | ---: |
| Sex, Table II | Male 334 / 694,583. Female 95 / 45,922. | 429 / 740,505 |
| Duty role, Table IV | Student 348 / 601,126. Physiological trainer 81 / 139,584. | 429 / 740,710 |

Both tables label the exposure column “Exposed Non-Cases.” Their published incidence calculations use that column directly as the denominator. The two denominators differ by 205, and the source supplies no joint cross-tabulation or explanation for the difference. The database preserves the two published scopes and flags likely overlap with the 1985–1987 USAF chamber surveillance and the 1982–1987 Rush treatment archive.

Among the 526 cases with known onset, 123 were recorded at altitude, 178 within two hours at surface and 225 in the latest reported category. The Results describes the last category as two hours or more. Table I says greater than two hours. The 527 cases with a final diagnosis are indexed under the original combinations of skin, limb pain, peripheral nervous system, neurological and pulmonary findings. These are distributions among treated cases.

Wirjosemito and colleagues identified 126 chamber and seven aircraft cases in their selected series of 133 treated historical Type II cases. The database adds the 16 marginal clinical manifestations and four severity categories from the original tables. Some combination counts exceed their component margins. For example, Table IIa lists 13 joint-pain and numbness cases while Table II gives six numbness cases. The combination rows are withheld. The earlier Davis cases and cases potentially represented in the later Weien series are linked for overlap. [Original article, Tables II–III](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/60/3/article-p256.pdf)

## Commercial flights after diving

Cialoni and colleagues observed return-flight VGE in 8 of 56 divers. The outbound and pre-return scans were negative in all 56, and the Results reported no symptomatic DCS during the study. Two selected participants with longer preflight intervals remained bubble-free. The earlier publication from the same team is linked as a potential overlap and contributes no additional outcome rows. Both papers use commercial flights. [Original 2015 article](https://www.dhmjournal.com/images/IndividArticles/45March/Cialoni_dhm.45.1.10-15.pdf) · [Earlier article](https://pubmed.ncbi.nlm.nih.gov/25245898/)

## Duffner report and source verification

The original NEDU report remains a bibliographic lead. Furry and colleagues report 55% among 18 subjects after a 45-minute surface interval. Sheffield reproduces 55% and describes a 15-minute interval. One rate row preserves the reported percentage and denominator, with an unresolved surface interval and no exact case numerator. [NEDU index](https://pubmed.ncbi.nlm.nih.gov/14409013/) · [Furry p. 826](https://asma.kglmeridian.com/downloadpdf/view/journals/aeme/38/8/article-p825.xml?isSearch=true#page=2) · [Sheffield p. 1131](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/61/12/article-p1130.pdf#page=2)

The provenance ledger records Tavily and Firecrawl discovery and extraction, 10 operations and 50 search results or source checks. [Queries](../data/chamber/v1.36/search_runs.csv) · [Results](../data/chamber/v1.36/search_hits.csv) · [Input checksums](../data/chamber/v1.36/manifest.json)

```sh
python -m scripts.build_chamber_database --chamber-treated-case-supplement
python -m scripts.build_chamber_database --chamber-treated-case-supplement --fac-official
```

The public and combined outputs are `artifacts/chamber-v1.36/observed.sqlite` and `artifacts/chamber-fac-official/observed-v1.36.sqlite`.

Both outputs passed SQLite integrity and foreign-key checks. All prior rows and the five locked external strata were preserved. The six original source digests matched the registry, the public rebuild was byte-identical, and all 28 benchmark tests passed.
