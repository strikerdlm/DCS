# Six-PDF chamber and operational evidence intake

The SQLite supplement registers six attachments by SHA-256 and records 18 overlap decisions. It loads 150 observations or reported values, 40 NASA test crosswalks and 122 flights from one U-2 pilot. LlamaParse Agentic processed all pages of the four short documents and the relevant sections of the two long reports. The source register gives the page selections and printed locators. Numerical claims were checked against the PDF text layer or rendered pages. [Source inventory](../data/chamber/attachments-2026-11-19/sources.csv) · [Overlap register](../data/chamber/attachments-2026-11-19/overlap.csv)

| Attachment | Evidence added | Handling in TinyDCS |
| --- | --- | --- |
| Smart and Cable, ADF training | All-centre year and certainty counts from Box 2 reproduce 57 definite, 11 probable and 18 possible DCI cases. The 68 definite or probable cases also have site, severity, treatment and sequelae margins. | The PDF hash matches the benchmark copy. The AVMED risk set of 42 cases in 10,851 exposures and its profile margins already exist. The 68 all-centre cases cover a wider population and have no comparable denominator. [Source, Boxes 2–6](https://jmvh.org/wp-content/uploads/2025/11/ADFHealth_5_1_03-10.pdf) |
| Webb, Woodrow and Maresh, U-2 operations | Table 3 follows 122 high flights by one pilot, with individual high-altitude durations and prebreathe exercise and rest durations. Cases prompting mission abort are documented on flights 19 and 25. Flights 71 and 104 have symptom entries. | Flights 26–61 were reported previously. The database stores the continuous series once. The other 118 rows have blank symptom entries. Flight 25 gives 300 minutes to symptoms and 260 minutes at high altitude. The time origins remain unresolved. [USAF report, Table 3](https://archive.org/details/DTIC_ADA518839) |
| NASA DCS evidence report | Table 1 reports zero DCS in 4 in-suit, 145 campout, 48 CEVIS and 16 ISLE person-EVAs through 1 August 2013. Ground-trial percentages and model estimates are recorded with their published limits. Table 7 adds diagnostic metrics. | Table 3 has 31 rows that agree with `nasa_test` on sex and outcome counts. The supplement adds the reported mean ages, condition marks and explicit Type II flags. The nine Phase rows carry alternate cohort counts alongside the benchmark. Table 5 and the Figure 8 joint DCS/VGE series match earlier extractions. [NASA report, Tables 1, 3, 5 and 7](https://ntrs.nasa.gov/citations/20140003729) |
| Brandt, Morrison and Butler, Shaw AFB | FY04 had **6 DCS diagnoses in 323 inside-observer exposures** and **4 in 780 student exposures**. The source questions two student diagnoses. Its observer workload regression reported a **2.1 risk ratio per additional monthly flight** with 95% CI 1.20–3.61. Table I adds group summaries, including reported delays of 20 minutes and 72 hours for two male observers. | The seven observer-month strata in Table II already exist in v1.1. FY04 is nested in the four-year review. Table I's FY01/FY02 altitude counts do not reconcile within year with the classified case counts, so both printed columns remain visible without reallocation. [Original article](https://pubmed.ncbi.nlm.nih.gov/19522370/) |
| Kluis and Diaz-Artiles, SmartSuit | Three habitat atmospheres, the 360-minute tissue half-time, and five printed tissue-ratio examples. | These are model inputs and outputs. Tissue ratio `R` is dimensionless. The calibration sample described by the review is already cited in the underlying literature. [Original article, Table 2 and equations](https://www.nature.com/articles/s41526-021-00175-3) |
| Valdez, FAA-AM-77-4 | The primary abstract gives **0 evolved-gas problems in 4,759 students** in 1965–1971 and 1973–1975. The Methods distinguish peak altitude, decompression timing and exposure durations for profiles A and B. | The 3,034 and 1,725 profile denominators are already staged from the Conkin 2018 summary. The database keeps the primary pooled total once. The later FAA CAMI report overlaps this period. The scanned attachment skips printed pages 4 and 5. [FAA report and archive checksum](https://rosap.ntl.bts.gov/view/dot/55970) |

Published risks and diagnostic statistics retain their sampling units. The role-specific Shaw counts inform the historical instructor workload question. They cannot establish an effect of the 2022 FAC policy. U-2 flight records and revised NASA Phase counts remain outside the frozen fitting and external-evaluation sets.

## Shaw AFB FY04: published and count-derived role ratios

Brandt, Morrison and Butler report symptomatic DCS among inside observers and students at Shaw AFB. The original [Person results and Table I (printed p. 571)](https://uhms.org/images/DCS-and-AGE-Journal-Watch/brandt_umo_decompression_sic.pdf#page=2) and the [continuation of Person (printed p. 572)](https://uhms.org/images/DCS-and-AGE-Journal-Watch/brandt_umo_decompression_sic.pdf#page=3) give the following. The crude ratio divides the inside-observer case proportion by the student case proportion using the unrounded counts in the [existing observations](../data/chamber/attachments-2026-11-19/observations.csv).

| FY04 outcome definition | Inside-observer cases / person-exposures | Student cases / person-exposures | Published ratio | Crude ratio from counts |
| --- | ---: | ---: | ---: | ---: |
| All attending-physician diagnoses | 6 / 323 | 4 / 780 | 3.22 | 3.62 |
| Sensitivity excluding two questioned student diagnoses | 6 / 323 | 2 / 780 | 7.15 | 7.24 |

Neither published point estimate is reproduced by the displayed counts. The reason is unresolved; retain the printed values as reported and label the recalculations separately. The two questioned cases had symptoms the authors considered compatible with hypoxia or hyperventilation, but were diagnosed as DCS by the attending physicians. The sensitivity reclassifies outcomes in the same student denominator; it is not an independent comparison. FY04 is also nested within the four-year review. These are descriptive, exposure-level contrasts, not adjusted or causal estimates. Do not carry the paper's inferential statements over to the recalculated ratios: independence of repeated exposures and comparability of surveillance are not established. Keep both contrasts out of quantitative pooling pending independent appraisal of case certainty, exposure dependence and surveillance.

## Build and query

```sh
python -m scripts.build_chamber_database --attachment-supplement
python -m scripts.build_chamber_database --fac-official --publication-supplement --rojas-supplement --attachment-supplement
```

The first command creates `artifacts/chamber-six-pdfs/observed.sqlite`. The second creates `artifacts/chamber-fac-official/observed-v1.7-rojas-attachments.sqlite`. Consult the register before combining counts across reports or across observation units.

```sql
SELECT source_id, scope, prior_source, relationship, disposition
FROM attachment_overlap ORDER BY source_id, scope;

SELECT * FROM attachment_nasa_count_comparison ORDER BY test_id;

SELECT flight_number, high_altitude_minutes, prebreathe_exercise_min,
       symptom_time_reported_min, outcome_documentation
FROM attachment_u2_flight
WHERE outcome_documentation IN ('dcs_abort','symptom_report')
ORDER BY flight_number;
```
