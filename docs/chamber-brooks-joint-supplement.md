# Brooks joint outcomes and early ADRAC validation

## Clinical DCS and Doppler observations

Webb and Pilmanis report **1,034 DCS cases in 2,077 chamber exposures** selected from 83 profiles across 15 protocols. Selection required at least 10% DCS in the profile. The two tables classify the same exposures using different bubble thresholds. The database records the clinical margin once and links both joint tables to it. The parent Brooks archive and related analyses overlap to an unknown degree. [Brooks review, Table I, pp. A3–A4](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/82/5%3ASupplement/article-pA1.pdf#page=4) · [Joint counts](../data/chamber/v1.46/joint_outcomes.csv) · [Overlap register](../data/chamber/v1.46/overlap.csv)

| Bubble threshold | DCS with VGE | No DCS with VGE | DCS without VGE at threshold | No DCS without VGE at threshold |
| --- | ---: | ---: | ---: | ---: |
| Any VGE | 809 | 575 | 225 | 468 |
| Grade IV VGE | 471 | 268 | 563 | 775 |

The table supports comparisons within the selected exposures. For example, 225 of the 1,034 symptomatic exposures had no detected VGE. The article reports exposure-level co-occurrence. Individual event order and standardized follow-up are unavailable for this subset.

## Loglogistic development sample

Kannan et al. give 975 exposures and 469 right-censored observations without symptoms, yielding 506 observed cases by subtraction. Two groups used 231 mmHg, mild exercise and a planned 240-minute plateau. The reported totals and symptom-free observations give 57/102 with 75 minutes of preoxygenation and 49/115 with 135 minutes. Both groups are part of the 975 exposures. The article lacks identifiers and joint gas histories to link these groups to individual DNT arms. [Kannan et al., p. 967](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/69/10/article-p965.pdf#page=3) · [Outcome extraction](../data/chamber/v1.46/observations.csv)

## Prospective ADRAC results across versions

The original 1999 symposium scan reports predicted and actual percentages for the five validation profiles later published in 2004. Altitude, preoxygenation and activity align the profiles. The 35,000-ft profile gives an actual value of 91% in 1999 and a Kaplan–Meier estimate of 94% in 2004. The other four observed percentages match the corresponding journal rows. The printed values remain attached to their respective reports, and their cohort link prevents double-counting. The early percentages supply no exact case counts. [1999 Table 1, PDF p. 6](https://archive.org/download/DTIC_ADA397485/DTIC_ADA397485.pdf#page=6) · [2004 journal article](https://pubmed.ncbi.nlm.nih.gov/15460625/) · [Profile crosswalk](../data/chamber/v1.46/validation_estimates.csv)

The earlier 1995 feasibility report supplies provenance for the predecessor archive. It describes 1,076 exposures recorded by September 1992 and 211 data fields per exposure, with no accompanying clinical numerator. [Feasibility report, §12.A, p. 54](https://citeseerx.ist.psu.edu/document?doi=15fb6346e7ba81f154087239f8edbdab92a2a20c&repid=rep1&type=pdf)

The 1998 and 1999 results were checked against the article and report scans. The 2011 joint tables were transcribed from indexed publisher PDF text and reconciled against the printed margins and accompanying formulas. The 2011 page images could not be retrieved. Search history also records the still-unavailable companion Air Force guide and a Chinese probability-model abstract without an identifiable cohort denominator. [Search and retrieval log](../data/chamber/publication-review/retrievals-2026-11-20-brooks-joint.json)

```sh
python -m scripts.chamber_products --output-dir artifacts/chamber-products/2026-11-20-v1.46
```

Both databases passed integrity and foreign-key checks. The paired audit retained all prior outcome records and verified both shared cohort links. The benchmark reproduced the prior evaluation, and all 51 tests in the linked database, publication review, report identity and observed benchmark suites passed.
