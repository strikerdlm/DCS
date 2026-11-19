# COMEX’97 expedition flights and historical aviation archives

Release 1.10 adds 32 original COMEX’97 investigator-flight records and 11 summaries or case observations. It replaces two abstract-only COMEX percentages with exact counts in the rebuilt database. The frozen v1.3 source files retain the original abstract extraction. The search log covers 85 hits and retrieval attempts across 15 operations. [Flights](../data/chamber/v1.10/flights.csv) · [Observed counts](../data/chamber/v1.10/observations.csv) · [Source registry](../data/chamber/v1.10/sources.csv) · [Search runs](../data/chamber/v1.10/search_runs.csv) · [Screening log](../data/chamber/v1.10/search_hits.csv)

## COMEX’97

Eight investigators made 32 chamber flights during the 1997 expedition experiment. The authors recorded bends symptoms on five flights involving three investigators. Table 1 and the Results verify **5/32 overall** and **4/8 at 8,000 m or higher**, including flights at exactly 8,000 m. The altitude rows below partition those same flights. [Original article, Tables 1–2 and Results](https://doi.org/10.1378/chest.121.1.173)

| Target altitude | Flights with DCS symptoms | Flights with detected VGE among those monitored |
| --- | ---: | ---: |
| 5,000 m | 0/10 | 0/2 |
| 6,000 m | 1/6 | 0/2 |
| 7,000 m | 0/8 | 2/2 |
| 8,000 m | 2/4 | 3/4 |
| 8,848 m | 2/4 | 2/4 |

The flight table preserves repeat-investigator codes, published exposure duration and reported symptom times. Ultrasound was available for selected flights below 8,000 m. At 8,848 m, two emergency flights had no oxygen prebreathe and only a measurement on arrival. Table 1 and a Table 2 footnote report different durations for these flights, so both values are retained. The article gives conflicting prebreathe cutoffs in Methods and Discussion. Values below 8,000 m remain blank. [Original article, Methods and Tables 1–2](https://journal.chestnet.org/article/S0012-3692%2815%2934656-0/fulltext)

## Aviation archives

- **Singapore, 1983.** Lim et al. report one pilot trainee with suspected DCS after a Mark III chamber flight. Tingling was recalled at 18,000 ft and symptoms became prominent around the reported 33,000-ft peak. The selected case has no exposed-population denominator. The publication’s other case occurred on an aircraft. [Case 2, p. 351](https://smj.sma.org.sg/2406/2406smj6.pdf)
- **Canada, wartime programme.** The official history reports approximately 7,000 people and more than 20,000 ascents across mixed experiments and routine tests. A cited RCAF Halifax report, C-2683, names 6,566 people and 16,293 simulated 35,000-ft exposures. The DCS numerator for that report remains unavailable, and the two denominators likely overlap. Both are indexed as archival leads. [Canadian official history, p. 368](https://www.canada.ca/content/dam/themes/defence/caf/militaryhistory/dhh/official/book-1953-medical-services-2-en.pdf) · [CHEST reference 3](https://journal.chestnet.org/article/S0012-3692%2815%2934656-0/fulltext) · [DTIC reference 28](https://apps.dtic.mil/sti/tr/pdf/ADA297023.pdf)
- **US Navy historical review.** Smedal’s public 1948 report points to several original lower-altitude aviation cadet reports, including Gray’s 23,000-ft study. The archive review serves as a citation lead. [Report and references](https://apps.dtic.mil/sti/tr/pdf/AD0622158.pdf)

```powershell
python -m scripts.build_chamber_database --expedition-supplement
```

The command writes `artifacts/chamber-v1.10/observed.sqlite`. The `--fac-official` option writes `artifacts/chamber-fac-official/observed-v1.10.sqlite` with the official Colombian Air Force aggregates included. [Cohort links](../data/chamber/v1.10/overlap.csv) · [Input digests](../data/chamber/v1.10/manifest.json)
