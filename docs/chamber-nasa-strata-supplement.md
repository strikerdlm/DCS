# NASA session and technician counts and FAA source verification

Release 1.32 adds 16 protocol or session outcome rows, three source records and five cohort links. The NASA rows refine existing programs. The original FAA journal table verifies two student profiles that had been staged in the intake. [Sources](../data/chamber/v1.32/sources.csv) · [Protocol outcomes](../data/chamber/v1.32/observations.csv) · [Session outcomes](../data/chamber/v1.32/daily_exposures.csv) · [Cohort links](../data/chamber/v1.32/overlap.csv)

| Source | Evidence and scope |
| --- | --- |
| Conkin et al., NASA TM-58278, 1987 | Nine Doppler technicians contributed 29 exposures. With the 210-minute oxygen prebreathe protocol, Table 2 reports **2/12 Type I DCS** and **5/12 any-grade VGE**. With the 240-minute protocol it reports **7/17 Type I DCS** and **9/17 any-grade VGE**. Planned altitude durations differed between protocols. The four rows are held for probable overlap with the later 219-exposure JSC technician series. The research-volunteer rows match NASA and NEDU Tests 2a and 3a and were not repeated. [Original NASA report](https://ntrs.nasa.gov/api/citations/19870017960/downloads/19870017960.pdf) · [Later technician series](https://ntrs.nasa.gov/citations/20030063917) |
| Garbino, NASA Exploration Atmosphere, Tests 1 and 2 | The published cumulative chart gives 25 analyzed exposures in each test. The ten increments preserve **EA1 2/25 and EA2 0/25** within the existing 2/50 aggregate. Both EA1 cases were Type I, at session 1 and session 5. The chart excludes one of the six listed participants at EA1 session 5 and one of the six at EA2 session 1. Their exposure and follow-up cannot be classified from the chart. The 2023 overview's **2/30** for the initial 2022 test is retained as an earlier denominator account. [2024 slides 29–30](https://ntrs.nasa.gov/api/citations/20240005151/downloads/2024_05_06_Garbino_EA_final.pdf#page=29) · [2023 report, p. 30](https://ntrs.nasa.gov/api/citations/20230013523/downloads/Evidence%20Report%20Draft%20Hypoxia%20and%20DCS_20230918.pdf) |
| Valdez, FAA, 1977 | Original journal Table I verifies **0/3,034 Type A and 0/1,725 Type B** student exposures with evolved-gas reactions as defined in the report. The two public agency scans omit the corresponding printed pages. The cumulative build now carries the two profile rows. The journal also describes two technicians with bends at 28,000 and 29,000 ft without a technician denominator. Their cases remain linked for likely overlap with the later 1965–1989 survey. [Original journal Table I](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/48/8/article-p718.pdf#page=3) · [FAA agency scan](https://rosap.ntl.bts.gov/view/dot/55970) · [Later survey](https://rosap.ntl.bts.gov/view/dot/21318) |

The 1987 report prints 28% beside six cases in 28 volunteer exposures. The exact fraction is about 21%. The database retains the existing exact count. The report also notes that its 3.5-hour technician onset summary used one timed event, although Table 2 records two cases. The time summary is not a substitute for the incidence numerator.

Tavily and Firecrawl searches, source extraction and direct verification yielded 47 logged operations and 234 results or checks. [Queries](../data/chamber/v1.32/search_runs.csv) · [Search results](../data/chamber/v1.32/search_hits.csv)

```sh
python -m scripts.build_chamber_database --chamber-nasa-strata-supplement
python -m scripts.build_chamber_database --chamber-nasa-strata-supplement --fac-official
```

The public build writes `artifacts/chamber-v1.32/observed.sqlite`. The FAC aggregate build writes `artifacts/chamber-fac-official/observed-v1.32.sqlite`. [Input checksums](../data/chamber/v1.32/manifest.json)

Both builds passed integrity and foreign-key checks. The row-by-row audit against v1.31 verified the 16 outcome additions and preserved all prior rows and the locked external benchmark. The public rebuild was byte-identical, and all 24 benchmark tests passed.
