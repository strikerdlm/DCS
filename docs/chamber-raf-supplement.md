# Royal Air Force chamber outcomes and staged oxygen trials

Release 1.12 adds 44 observed outcome rows from three series in Fryer’s public 1969 AGARDograph. Discovery and verification used Tavily, Firecrawl and the complete archived monograph. The log retains 110 search hits and URL-level retrieval attempts across 22 operations. [Observations](../data/chamber/v1.12/observations.csv) · [Source registry](../data/chamber/v1.12/sources.csv) · [Search runs](../data/chamber/v1.12/search_runs.csv) · [Search hits](../data/chamber/v1.12/search_hits.csv)

## Selection at 28,000 ft

The Appendix reports **4,956 exposures by 2,606 people**. Of these, **141 people** had symptoms in at least one run and **38 people** required a premature descent at least once. There were **165 symptomatic runs**, obtained by summing the observed weekday cells in Table 6-1. The Appendix’s repeat-run outcomes reconcile to the same numerator. [Table 6-1](https://archive.org/download/DTIC_ADA111509/DTIC_ADA111509.pdf#page=86) · [Appendix](https://archive.org/download/DTIC_ADA111509/DTIC_ADA111509.pdf#page=293)

The 164-case session-clustering analysis has an unspecified eligible denominator. The age tables use 2,635 analytical subjects or first runs and 2,304 in the paired or severe-first-run analysis. The original record linkage between those groups and the Appendix’s 2,606 people is unavailable. The database marks the age rows with a denominator conflict and keeps each analysis scoped to its source table. The Appendix also prints “414” once. Its explicit total, occupation subtotals and repeat-run counts agree on 141. [Age tables](https://archive.org/download/DTIC_ADA111509/DTIC_ADA111509.pdf#page=93) · [Cluster analysis](https://archive.org/download/DTIC_ADA111509/DTIC_ADA111509.pdf#page=110) · [Overlap register](../data/chamber/v1.12/overlap.csv)

## Rapid-decompression training and staged oxygen exposures

- **RAF rapid-decompression training.** In **7,685 runs**, Fryer recorded one bends report, one formication report and two pain reports he attributed to pressure breathing. The exercises used 60 minutes of preoxygenation and a brief exposure within the source’s 48,000–70,000 ft range. The source does not give a separate denominator by target altitude. [Table 12-1](https://archive.org/download/DTIC_ADA111509/DTIC_ADA111509.pdf#page=259)
- **1953 V-bomber simulation.** Fryer reports the following exposure-arm results at a 40,000-ft target. The narrative gives 120 exposures from 40 volunteers, while the four arm denominators sum to 119 and one withdrawal is described. Volunteers could contribute to more than one condition. The air-control run ended early because of symptoms. [Results, p. 271](https://archive.org/download/DTIC_ADA111509/DTIC_ADA111509.pdf#page=265)

| Staging condition | DCS-related forced descent | Tolerable DCS symptoms |
| --- | ---: | ---: |
| 180 min air at 8,000 ft | 6/10 | 2/10 |
| 180 min oxygen at 8,000 ft | 3/40 | 4/40 |
| 90 min oxygen at 8,000 ft | 10/39 | 7/39 |
| 180 min oxygen at 25,000 ft | 9/30 | 7/30 |

The earlier Fryer selection survey is linked to the monograph’s 28,000-ft series. The Cutler USAF comparison, the Cotes and Morant 610-person series, and the Gould Royal Navy report remain source leads. Their original tables or exposure linkage were unavailable. [Source register](../data/chamber/v1.12/sources.csv) · [Overlap register](../data/chamber/v1.12/overlap.csv)

```powershell
python -m scripts.build_chamber_database --raf-supplement
```

The command writes `artifacts/chamber-v1.12/observed.sqlite`. The `--fac-official` option includes the official Colombian Air Force aggregates. [Input digests](../data/chamber/v1.12/manifest.json)
