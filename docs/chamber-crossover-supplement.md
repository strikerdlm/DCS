# British and Swedish chamber outcomes, release 1.14

Release 1.14 adds 50 outcome rows from four primary reports, including overlapping totals and selected repeats. The ledger records 57 retrieval results across 10 search and verification operations. [Source registry](../data/chamber/v1.14/sources.csv) · [Outcome rows](../data/chamber/v1.14/observations.csv) · [Overlap register](../data/chamber/v1.14/overlap.csv) · [Search runs](../data/chamber/v1.14/search_runs.csv) · [Search results](../data/chamber/v1.14/search_hits.csv)

| Source | Recorded outcomes | Analysis scope |
| --- | --- | --- |
| Lupa and D’Oyly (2005) | **0/10** DCS signs or symptoms and **0/10** any VGE at each peak altitude, 17,500 and 35,000 ft. | The same ten parachutists completed both profiles. Each included 15 min at peak altitude, a 35 min descent and 45 min of monitored ground exercise. Scheduled monitoring ends with the study exercise. [Original proceedings, §§2–3](https://citeseerx.ist.psu.edu/document?doi=b4b736332a7295f7266a1bc09b7a0dcc2a3476d3&repid=rep1&type=pdf) |
| Lee and Hay (2001) | Source-defined DCI symptoms prompting recompression affected **1, 1, 8, 9, 0, 6 and 8** of 15 exposures per profile in Table 1 order. Any VGE, Grade IV VGE and left ventricular gas are also recorded. | The plots give cumulative observed counts through up to four hours. Early termination could follow symptoms or left-heart gas. Participant linkage across profiles is unavailable. The discussion's pooled 6/115 left-heart gas result is flagged because the seven profile denominators total 105. [Figures 4–6 and Tables 1–3](https://diving-rov-specialists.com/index-b-documents_htm_files/scient-c_628-altitude-deco-illness.pdf) |
| Balldin (1973) | At 38,000 ft, there were **6/7** bends cases after dry preoxygenation and **2/7** after warm immersion during preoxygenation in the standard pairs. Selected repeat pairs with extra nitrogen loading yielded **3/3** and **0/3**, respectively. | The published 9/10 and 2/10 totals contain both strata. Their rows are marked as overlapping margins. Temperature and immersion were varied together. [Original Results and Table I](https://gupea.ub.gu.se/server/api/core/bitstreams/625b8f6a-26a8-42f5-80af-e2fd64cca377/content#page=14) |
| Balldin and Borgström (1976) | The five repeat volunteers had **0, 0 and 2** author-diagnosed bends cases at 8,000, 9,000 and 11,500 m. Any VGE occurred in **0, 2 and 4**, respectively. | One spontaneously resolving symptom at 9,000 m is recorded as questionable. Both nitrogen-loading tests at 11,500 m enrolled selected prior non-cases. [Original Results and Table I](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/47/2/article-p113.pdf) |

Tavily and Firecrawl contributed discovery and retrieval records. The Gothenburg scan exceeded Firecrawl's file-size limit and was verified locally. The original Lupa and D’Oyly text was verified from the indexed proceedings copy. Direct PDF retrieval failed, so its hash is blank. The Gould and Parsons selection-test publications and the unverified Chadov group denominators remain in the search ledger. [Input digests](../data/chamber/v1.14/manifest.json)

```powershell
python -m scripts.build_chamber_database --crossover-supplement
```

The builder writes `artifacts/chamber-v1.14/observed.sqlite`. Add `--fac-official` to include the official Colombian aggregates. The supplement supplies descriptive research cohorts. Its rows are outside the five locked external benchmark strata.
