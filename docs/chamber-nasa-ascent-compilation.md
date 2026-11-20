# NASA ascent-rate compilation

Kumar and Waligora's NASA TM-100472 compiles historical altitude chamber experiments. Tavily located the PDF and Firecrawl confirmed the NASA catalog and public reuse status. The original scan supplies the Appendix B data on printed pages 56–59 (PDF pages 62–65). [NASA catalog](https://ntrs.nasa.gov/citations/19890012936) · [Archived original](../data/chamber/publication-review/full-text/technical-reports/1989-kumar-waligora-ascent-nasa-tm-100472.pdf)

The four pages contain 31, 44, 46 and 29 rows. Their 14,123 person-exposure entries reproduce all four Table 1 subtotals and all 24 Table 2 ascent-rate cells. The scan restored two rows skipped on the first pass because the PDF text layer omitted their denominators (223 and 204 on printed page 58). These totals describe the source compilation. A person may contribute more than one exposure, and multiple source reports may describe the same exposures.

| At altitude | No ground denitrogenation | With ground denitrogenation |
| --- | ---: | ---: |
| Rest | 5,897 | 692 |
| Exercise | 5,885 | 1,649 |

The model database stores profile rows, Table 1 totals and reference numbers in `publication_ascent_compilation`, `publication_ascent_compilation_total` and `publication_ascent_reference`. Symptom and forced-descent percentages retain the report's whole-percent rounding. Blank percentages represent printed dashes. An exercise-frequency dash is retained as a blank frequency and identifies the rest group for the Table 1 reconciliation. The outcome-window footnote gives 120 minutes for references 59 and 60. The table's altitude duration remains the source-reported protocol field. No case counts or follow-up times were reconstructed from the percentages.

Appendix B uses 36 distinct reference numbers. The report describes 42 source reports overall, and the printed row citations establish 36 numbered bibliography links. Nineteen citations match existing source IDs. The review database resolves repeated retrievals of NASA TM-100472 to one report and links the 19 cited reports. The model database holds all 150 rows for overlap review and excludes them from the clinical fitting and validation populations. An example is Smedal, Brown and Hoffman's six 1946 profiles, which already have primary-source observations in v1.11. [Original 1946 paper](https://pubmed.ncbi.nlm.nih.gov/21018675/)

The search also consolidated repeated catalog records for Conkin, Bedahl and Van Liew's 1992 HDSD article under its PMID. A follow-up retrieval found the public article and its printed subset. [HDSD Table III intake](chamber-hdsd-compilation.md)
