# Chamber evidence release v1.38

The release adds two clinical observations. It also preserves 36 rows from Kumar et al. 1990 Table I in `publication_threshold_profile` to document links and discrepancies with earlier studies. The table is outside the observation and model benchmark inputs.

## Clinical observations

- **Polaris Dawn ground study.** The conference abstract reports no DCS symptoms across ground and flight evaluations. The ground cohort included eight people, comprising four crew and four matched volunteers. The database records 0/8 participants during observed ground testing. The flight used a revised profile with the same four crew. The abstract supplies no detailed pressure history, ultrasound outcome counts or fixed delayed follow-up. The team report corroborates the NASA chamber study and covers the crew subset. [IEEE paper](https://doi.org/10.1109/AERO66936.2026.11520147) · [Indexed copy of the conference abstract](https://eurekamag.com/research/107/645/107645870.php) · [Polaris Program report](https://polarisprogram.com/polaris-dawn-crew-participates-in-a-decompression-sickness-study-at-nasas-johnson-space-center/)
- **Kumar 1988 chamber accident.** During ambient-air treadmill exercise, the chamber inadvertently descended from about 15,000 to 6,000 ft and returned to 15,000 ft while the participant was still exercising. The author reported DCS symptoms about ten minutes after return to ground level. The observation records one selected case with a null incidence denominator. [Original case report](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/59/11/article-p1080.pdf)

## Table I reconciliation

All 36 rows were checked against the rendered publisher page. The extraction includes printed case and exposure counts, altitude, duration or duration range, denitrogenation, exercise schedule, ascent rate and original attribution. `counts_concordant` applies to outcome and denominator agreement. Protocol details can still differ and are recorded in the notes. `scope_discrepancy` flags a difference in endpoint, denominator or protocol. `unverified` indicates that an exact primary-source match has yet to be established. [Original compilation, p. 687](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/61/8/article-p685.pdf) · [Transcription and reconciliation](../data/chamber/v1.38/threshold_profiles.csv)

- At 8.3 psia, the combined 1/31 in Kumar matches two previously indexed NEDU margins, 1/20 and 0/11. At 7.8 psia, the 1/32 corresponds to the first day of a repeat-exposure series. The NEDU margin covers 94 repeated male exposures. The 10,000-ft denominator varies across the available versions of the work. Kumar prints seven, the NASA memorandum prints eight at 10.0 psia and NEDU prints nine at 10.0 psia. [NASA TM-100456](https://ntrs.nasa.gov/api/citations/19870019681/downloads/19870019681.pdf) · [Curated NEDU Appendix E](../data/chamber/v1/nedu_appendix_e.csv)
- The Smedal exercise margins in Kumar match individual severity percentages more closely than the any-bends percentages. The original protocol used 20 minutes. Kumar prints 0.4 h. Damato’s report uses 96 for the main exposure series, which includes tests without an 18,000-ft equilibration stage. A rate of 3/96 specifically for that stage is unsupported. [Smedal Table I](https://asma.kglmeridian.com/downloadpdf/view/journals/joam/17/1/article-p67.pdf) · [Damato Results](https://asma.kglmeridian.com/downloadpdf/view/journals/aeme/34/11/article-p1037.pdf)

Tavily and Firecrawl located and retrieved the Polaris abstract and team account. The EBSCO UNAL skill requires a local credential file, which was absent in both checked Windows skill locations. The authenticated search remains blocked. [Search queries](../data/chamber/v1.38/search_runs.csv) · [Search hit ledger](../data/chamber/v1.38/search_hits.csv) · [Frozen input checksums](../data/chamber/v1.38/manifest.json)

```sh
python -m scripts.build_chamber_database --chamber-threshold-supplement
python -m scripts.build_chamber_database --chamber-threshold-supplement --fac-official
```

The public and combined builds are `artifacts/chamber-v1.38/observed.sqlite` and `artifacts/chamber-fac-official/observed-v1.38.sqlite`.

Both builds passed SQLite integrity and foreign-key checks. The historical reconciliation records nine count matches, 11 scope discrepancies and 16 unverified rows. A comparison against v1.37 confirmed two additions to `publication_observation` and identical contents for all five locked external strata. The public rebuild was byte-identical. All 30 benchmark tests passed.
