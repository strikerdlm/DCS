# Chamber evidence release v1.41

## Waligora six-hour prebreathe count

The published abstract gives 18/38 for venous gas emboli after six hours of oxygen prebreathe. Table II reports 29% and the six-hour group in Figure 2 gives 11 bubble-positive participants. NASA Test 5a lists 11/38, 19 men and 19 women, and four DCS cases under the same pressure and duration. The database now uses **11/38** for the canonical historical VGE row. The correction table preserves the earlier 18/38, both locators and the evidence for the revision. The eight-hour sample had zero events in eight men in the paper and zero in eleven exposures in NASA Test 5b. Those margins retain their separate source scopes. [Waligora et al., abstract, Table II and Fig. 2](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/58/9/article-pA110.pdf) · [NASA TP-2020-220529, Table F1](https://www.nasa.gov/wp-content/uploads/2023/03/conkin-dcs-survival-models-tp220529-2020.pdf) · [Jauchem et al., corroborating abstract](https://ntrs.nasa.gov/citations/20050023610)

## DCS in men with Doppler bubbles

Kumar and Powell report **24 mild DCS cases among 59 men selected for detectable Doppler bubbles**. The Grade IV subgroup has 31 people. Table 1 gives 20 cases in that subgroup, and Tables 2 and 4 print 11. The 20-case version sums to the published 24 total and reproduces the crude ratio of 4.52 and its 95% interval of 1.76–11.61 when compared with 4/28 in grades I–III. The Grade IV row records both conflicting values and carries a discrepancy flag. Peak grade and DCS were observed during exposure. The paper analyzes historical NASA data after selecting for detected bubbles. [Original paper, especially p. 565](https://ntrs.nasa.gov/api/citations/19940007074/downloads/19940007074.pdf#page=3)

## Skedina repeat-exposure series

The Russian journal abstract reports **24 of 32 experiments with peak Grade III–IV Doppler signals**. Its sample, pressure range, seven clinical cases and 27 VGE-positive experiments match the conference report already indexed in v1.13. The new measurement is linked to that study. The 32-exposure denominator still conflicts with the older description of two exposures per person among ten volunteers. Pressure-specific denominators and assignment to individual runs were unavailable. [Russian journal abstract](https://pubmed.ncbi.nlm.nih.gov/9883330/) · [Conference report](https://ntrs.nasa.gov/api/citations/19980024361/downloads/19980024361.pdf#page=6) · [Acta Astronautica publication](https://doi.org/10.1016/S0094-5765(98)00145-3)

Tavily and Firecrawl supported source discovery and verification. The original rendered pages were used to check the conflicting counts. [Queries](../data/chamber/v1.41/search_runs.csv) · [Results](../data/chamber/v1.41/search_hits.csv) · [Frozen input checksums](../data/chamber/v1.41/manifest.json)

```sh
python -m scripts.build_chamber_database --chamber-vge-reconciliation-supplement
python -m scripts.build_chamber_database --chamber-vge-reconciliation-supplement --fac-official
```

The public and combined outputs are `artifacts/chamber-v1.41/observed.sqlite` and `artifacts/chamber-fac-official/observed-v1.41.sqlite`.

The public, combined and publication-review builds passed SQLite integrity and foreign-key checks. The public rebuild was byte-identical. Comparison to v1.40 verified the expected Waligora source and outcome revisions and preserved all five locked external strata. All 33 benchmark tests passed.
