# Zotero chamber outcomes supplement

**Release 1.1 · 19 November 2026**

This supplement adds 103 published observations and 13 overlap links from nine papers located in Zotero. LlamaParse Agentic processed 48 pages. Eight PDFs came from Zotero and the Crowell PDF came from the publisher using the Zotero citation. The [source register](../data/chamber/v1.1/sources.csv) records the PDF and parsed Markdown hashes, Zotero item key, and attachment key when available. The [observation table](../data/chamber/v1.1/observations.csv) records native denominator units and a source locator for each row.

## Source findings

| Paper | What the supplement adds |
| --- | --- |
| Crowell, Canadian Forces | Twenty site-year cells total 69 DCS cases in 19,573 exposures. The narrative gives the same 69 cases in 21,423 exposures. Winnipeg/Edmonton accounts for 1,840 of the 1,850-exposure difference and Trenton for 10. The cause is unresolved. Both versions are held from pooling. [Primary report, Table II and Results](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/54/11/article-p1034.pdf) |
| Piwinski et al., U.S. Army | Table I gives 20 cases in 14,545 exposures. Six role and altitude strata distinguish 8/12,596 student exposures from 12/1,949 technician exposures. Table I prints 13,106 m for the highest group, while the Methods pair that altitude with 45,000 ft. The feet field is blank for those strata. Table II's 25,000-ft non-event count differs from the mutually reconciling Tables I, IV and VI. [Primary paper](https://pubmed.ncbi.nlm.nih.gov/3790029/) |
| Ercan et al., Türkiye | The full text confirms exposure denominators. There were 6/6,657 evaluable trainee exposures and 2/615 inside-observer exposures from ten observers. Five of 6,662 trainee records were excluded. Table 1's 7,193 denominator combines male trainees and observers. The 79 female trainee exposures carry an explicit zero case count. [Primary paper](https://pubmed.ncbi.nlm.nih.gov/32574436/) |
| Morgagni et al., Italian Air Force | The numerical analysis uses 1,241 exposed trainees after exclusions from the 1,254 reported in the abstract. Table II gives 1/918 with pre-chamber clinical selection and 0/323 in controls. The only case was Type I during ascent. Screening and the Type 2a restriction groups overlap. [Primary paper and Table II](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/81/9/article-p873.pdf) |
| Bason and Yacavone, U.S. Navy | Of 140 confirmed cases, 65 first presented at altitude and 75 after return. Three of the 75 were reported in the open-ended bin above 20 hours. The 19 timing bins describe confirmed cases. The full text supplies no corresponding exposure-level censoring times. Four earlier Navy cohorts are marked as reprints. [Primary paper, Tables III–IV](https://pubmed.ncbi.nlm.nih.gov/1755801/) |
| Brandt et al., Shaw AFB | The workload table records six events across 596 observer-months with at least one chamber flight and also lists 214 zero-flight observer-months. Visual inspection of the original shows the last category is more than five flights per month. The LlamaParse table dropped the greater-than sign. [Primary paper, Table II](https://pubmed.ncbi.nlm.nih.gov/19522370/) |
| Ohrui et al., Japan | Fifteen fiscal periods and the overall total retain the published joint-pain Type I DCS rates. Exact case counts are unavailable, including for values printed as 0%. [Primary paper, Table I](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/73/4/article-p395.pdf) |
| Nakdimon and Ben-Ari, Israeli Air Force | The role-specific DCS rates remain percentages with empty case numerators. The center and calendar period overlap the existing 2015–2022 Israeli source in release 1.0. [Primary paper, Table I](https://doi.org/10.3357/AMHP.6048.2022) |
| Conkin et al., NASA and USAF | The 66 historical tests contributed 211 clinical cases in 1,075 exposures. The any-VGE result uses a separate monitored denominator of 1,026. Participant linkage and study-level deduplication remain unresolved. [Primary paper](https://www.nasa.gov/wp-content/uploads/2023/03/conkin-dcs-survival-analysis-1996.pdf) |

## Rebuild and query

```sh
python -m scripts.build_chamber_database --zotero-supplement
```

The command writes `artifacts/chamber-v1.1/observed.sqlite` with the frozen 1.0 tables plus `zotero_source`, `zotero_observation`, and `zotero_overlap`. The existing `development_counts` and `locked_external` views remain the inputs to the original benchmark. The 103 new records include counts, percentages, overlapping views of the same exposures, and case-conditional or person-month frequencies. Use each row's `analysis_role`, `endpoint` and `denominator_unit` when specifying analysis eligibility. [Input checksums](../data/chamber/v1.1/manifest.json) · [Overlap register](../data/chamber/v1.1/overlap.csv)

```sql
SELECT stratum, cases, denominator, denominator_unit, locator, note
FROM zotero_observation
WHERE source_id = 'crowell83'
ORDER BY stratum;
```

The extraction audit checked the original PDF text, LlamaParse output, and selected rendered pages. This included all 20 Crowell site-year cells, all six Piwinski Table I role-by-altitude strata, all 16 Ohrui exposure/rate pairs, and all 19 Bason onset frequencies. Exact cases, percentages, participant exposures, observer-months and counts conditional on diagnosis occupy distinct fields. Full PDFs and raw parser output are local in `artifacts/chamber-zotero`.
