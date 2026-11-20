# ADRAC validation across three publications

The June 2001 proceedings paper documents the five AFRL chamber profiles tested in 1999. It gives the same actual symptomatic DCS percentages as the 2004 journal article. The 35,000-ft profile is 94% in both, compared with 91% in the 1999 SAFE proceedings. The 2001 and 2004 predictions differ for three profiles. Each source's printed values remain attached to its version. [1999 SAFE proceedings, Table 1](https://archive.org/download/DTIC_ADA397485/DTIC_ADA397485.pdf#page=6) · [2001 RTO proceedings, Table 1](https://archive.org/download/DTIC_ADP011090/DTIC_ADP011090.pdf#page=4) · [2004 journal article, Table III](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/75/9/article-p749.pdf#page=8)

| Journal profile | Altitude (ft) | 1999 actual (%) | 2001 actual (%) | 2004 actual (%) | Model predictions, 1999 / 2001 / 2004 (%) |
| --- | ---: | ---: | ---: | ---: | --- |
| A | 35,000 | 91 | 94 ± 9 | 94 +6/−9 | 93 / 94 / 94 |
| B | 25,000 | 61 | 61 ± 17 | 61 ± 17 | 62 / 62 / 53 |
| C | 22,500 | 30 | 30 ± 16 | 30 ± 16 | 38 / 38 / 44 |
| D | 18,000 | 13 | 13 ± 12 | 13 ± 12 | 17 / 17 / 17 |
| E | 30,000 | 58 | 58 ± 17 | 58 ± 17 | 52 / 50 / 63 |

The 2001 report describes 30 exposures per profile and prints a plus-minus value beside each actual estimate. The 2004 journal footnote identifies its own margins as 95% confidence intervals for Kaplan–Meier estimates. The 2001 printed values are preserved without deriving counts or interval endpoints from them. NEDU Appendix E gives 29/31 for MV-A under its own counting scope. The sources still leave the reason for the 91% value and the exact numerator behind each Kaplan–Meier estimate unresolved. [Extracted estimates](../data/chamber/v1.48/validation_estimates.csv) · [NEDU Appendix E](../data/chamber/v1/nedu_appendix_e.csv)

The review links three full reports and two cited abstracts to the existing validation study. The abstracts from 1999 and 2000 remain citation-only. The model database adds five rows to `publication_validation_snapshot` and records same-cohort links to both full reports and likely overlap with the NEDU compilation. The cohort initially tested the earlier model. The 2001 authors say they subsequently used the validation results to revise the model, so those same exposures cannot independently test the revised version. The study supplies no staff-to-trainee risk set. [Report crosswalk](../data/chamber/v1.48/overlap.csv) · [2001 proceedings, Results and Conclusions](https://archive.org/download/DTIC_ADP011090/DTIC_ADP011090.pdf#page=3)

Tavily found the primary proceedings paper and indexed Table 1. Firecrawl verified the public archive download. LlamaParse extracted the table, and the values were checked against the PDF page and its embedded text. The DTIC notice authorizes unlimited distribution. [Original PDF index](../data/chamber/publication-review/full-text/index.csv) · [Search and retrieval log](../data/chamber/publication-review/retrievals-2026-11-20-adrac-proceedings.json)

```sh
python -m scripts.chamber_products --output-dir artifacts/chamber-products/2026-11-20-v1.48-r2
```

Both SQLite databases passed integrity and foreign-key checks, and all 53 tests in the paired database, review, identity and benchmark suites passed. The benchmark reproduced v1.47. All 783 clinical outcome rows, 105 catalogued cases and 26 role-specific groups were identical between releases.
