# Swedish post-dive chamber exposures and exercise crossover VGE grades

Release 1.34 adds 66 exposure records from two previously unindexed Swedish chamber studies, 33 participant-by-protocol VGE records from a previously indexed lead and 24 aggregate outcome rows. The source registry includes a separate pulmonary case report linked to its original exposure. [Post-dive records](../data/chamber/v1.34/postdive_exposures.csv) · [Crossover VGE records](../data/chamber/v1.34/vge_peaks.csv) · [Aggregate outcomes](../data/chamber/v1.34/observations.csv) · [Cohort links](../data/chamber/v1.34/overlap.csv)

## Post-dive chamber flights

The 1978 study reported 35 flights from five participants. The original table includes the same five participants in all six post-dive conditions and the no-dive control. Over the observed flights, the source classified 14 cases as certain and three as questionable. The appendix preserves the four grade-onset columns, symptom onset, and the timing reported in the recompression column. The three questionable symptoms faded at altitude. The pulmonary case began at 90 minutes, with recompression at 100 minutes and symptoms persisting at surface until treatment. Its companion report describes the same exposure. [Original chamber study, Table I and Results](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/49/11/article-p1314.xml?isSearch=true) · [Companion case report](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/49/11/article-p1350.xml?isSearch=true)

| Surface interval in the 9,000 m series | Flights | Source-confirmed DCS | Questionable symptoms | Any VGE |
| --- | ---: | ---: | ---: | ---: |
| No prior dive | 5 | 0 | 1 | 3 |
| 12 hours | 10 | 4 | 0 | 7 |
| 18 hours | 10 | 6 | 0 | 8 |
| 24 hours | 10 | 4 | 2 | 7 |

The totals cover the observed flights, including cases after one hour. The 15- and 60-minute numbers in the article are checkpoints within these flights. The regression test verifies that the exposure records reproduce the published checkpoint counts.

The 1980 study recorded 31 flights after a three-hour surface interval. Follow-up at the lower altitudes depended on VGE in the preceding experiments. One participant had two questionable episodes, both of which resolved during the flights. The shared 5–15 minute symptom onset range is preserved as bounds. The 1978 and 1980 articles share at least one likely participant based on the published initials, height and mass. Their protocols describe distinct exposures. [1980 original, Table I and Results](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/51/7/article-p649.xml?isSearch=true)

| Simulated altitude | Flights | Source-confirmed DCS | Questionable symptoms | Any VGE |
| --- | ---: | ---: | ---: | ---: |
| 3,000 m | 20 | 0 | 0 | 12 |
| 2,000 m, selected | 7 | 0 | 1 | 6 |
| 1,000 m, selected | 4 | 0 | 1 | 2 |

## Exercise crossover

The full article and Table 1 upgrade the existing Gottschalk et al. 2024 source in place. Each of 11 participants contributes three observed protocol records with resting, knee-flex and arm-flex peak grades. Any VGE was observed in 4/11 control, 7/11 whole-body exercise and 8/11 upper-body exercise sessions. The authors randomized the order of control and whole-body exercise. Upper-body exercise came last for all participants. These grades use the Eftedal–Brubakk scale. The article gives no exact clinical DCS count. [Original article, Methods and Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC11363104/#eph13593-tbl-0001)

## Provenance and rebuild

Tavily and Firecrawl searches and extraction are recorded with source and disposition. The Swedish journal PDFs were rendered and transcribed, and the 99 crossover peak grades matched the independently retrieved Europe PMC XML. The profile summaries use the same exposure records and carry their within-study dependence, follow-up selection or cross-study overlap. [Queries](../data/chamber/v1.34/search_runs.csv) · [Results](../data/chamber/v1.34/search_hits.csv) · [Input checksums](../data/chamber/v1.34/manifest.json)

```sh
python -m scripts.build_chamber_database --chamber-paired-exposures-supplement
python -m scripts.build_chamber_database --chamber-paired-exposures-supplement --fac-official
```

The public and combined outputs are `artifacts/chamber-v1.34/observed.sqlite` and `artifacts/chamber-fac-official/observed-v1.34.sqlite`.

Both builds passed SQLite integrity and foreign-key checks. The Gottschalk source upgrade was the only revision to a prior row. The five locked external strata were preserved. The public rebuild was byte-identical, and all 26 benchmark tests passed.
