# Rojas 2015 USAF occupation and DCS data

TinyDCS already registered Jaime Rojas's 2015 Wright State University MPH project as `rojas15`, with six case-control occupation counts. The supplied PDF is a different file copy of the same study. The supplemental build links the two source records and adds 48 detailed counts and three reported statistical results. The six headline counts remain available under the existing source ID. [Wright State University record](https://corescholar.libraries.wright.edu/mph/170/) · [Attachment hash and study metadata](../data/chamber/rojas-2015/sources.csv) · [Source crosswalk](../data/chamber/rojas-2015/overlap.csv)

The author identified active-duty USAF cases from archived ICD-9 993.3 billing codes and selected three controls per case by age, sex, rank and race. Two cases used the other matching factors without race. Occupation was recorded at the case's diagnosis date. The abstract gives 2005–2010 and the Methods and Table 1 give 2006–2010. Both are recorded in the source table.

| Source location | What the supplement adds | Reconciliation |
| --- | --- | --- |
| Results p. 9 | 27 female cases and 81 controls, 96 male cases and 288 controls, and reported mean age of 28 years | The sex counts reconcile to 123 cases and 369 controls. |
| Table 1 p. 10 | 40 Air Force Specialty Code (AFSC) counts among cases | The printed rows total **122**, one fewer than the **123** cases in the Results. The missing classification is unresolved. The table lacks a control breakdown by AFSC. |
| Results p. 11 | Reported odds ratio **150.6**, 95% CI **28.3–3131**, and reported chi-squared **111.5** | The pooled comparison uses 36 high-risk and 87 other cases, with 1 high-risk and 368 other controls. The single high-risk control's occupation is unspecified. |
| Table 2 p. 11 | Tobacco status by case or control, including 6 of 55 cases and 24 of 163 controls with positive status | Counts reconcile to **218** records. Of the full 492-person sample, 274 lack the data needed for this analysis. |
| Table 3 p. 11 | Four alcohol-use categories by case or control, including **2 cases and 2 controls** reported in the `>= 4 times per week` category | The table again covers 55 cases and 163 controls. Each category retains its printed bounds. |

The paper reports occupation without a count of all personnel at risk, a denominator of flights or chamber exposures, or a reconstructed pressure history. The data support case-control association and case descriptions. Neither incidence per chamber flight nor an absolute DCS prediction can be fitted from these counts. Case-level matched sets and VGE outcomes are also unavailable.

## Comparison with the companion poster

The university's companion poster by Rojas, Dohn and Voss reports the same 2006–2010 sample of 123 cases and 369 controls, including eight U-2 aviators and 28 hypobaric technicians among the cases. Its Table 1 has 40 occupation rows that sum to 123 cases. Three counts differ from the project report. The source register links both reports to the same sample and keeps the published counts for each version. The cause of the differences remains unresolved. [Wright State poster, Results and Table 1](https://corescholar.libraries.wright.edu/cgi/viewcontent.cgi?article=1171&context=mph&filename=0&type=additional) · [Firecrawl retrieval and comparison](../data/chamber/publication-review/retrievals-2026-11-20-europe-staff.json)

| Occupation | Project report | Companion poster |
| --- | ---: | ---: |
| Airborne Battle Management or Airborne Operations (1A4X1) | 4 | 3 |
| Airborne Cryptologic Linguist (1A8X1) | 1 | 2 |
| Basic Enlisted Airman | 1 | 2 |
| Total across the 40 occupation rows | 122 | 123 |

## Verification and build

LlamaParse Agentic was used on the abstract and study pages. The extracted numerical cells and AFSC codes were checked against the PDF text layer and rendered tables. The rendered Table 3 shows `>= 4 times per week`, where LlamaParse omitted the greater-than sign. The database uses the printed label. Source locators distinguish the printed page from the PDF page.

An independent calculation from the pooled occupation cells reproduces the reported odds ratio and interval using the conditional estimate (150.624) and a two-sided mid-P interval (28.311–3131.109). The tobacco Pearson test reproduces the printed p-value of 0.4776. Enumeration of the fixed-margin alcohol table gives a two-sided exact p-value of 0.651115, consistent with 0.651 in the paper. The meaning of the printed alcohol statistic 1.727 and one degree of freedom is unclear, so both are retained as reported.

```sh
python -m scripts.build_chamber_database --rojas-supplement
python -m scripts.build_chamber_database --fac-official --rojas-supplement
python -m scripts.build_chamber_database --fac-official --publication-supplement --rojas-supplement
```

The first command builds `artifacts/chamber-rojas-2015/observed.sqlite`. The second adds the official Colombian aggregates and creates `artifacts/chamber-fac-official/observed-rojas.sqlite`. The third includes the v1.7 literature update and creates `artifacts/chamber-fac-official/observed-v1.7-rojas.sqlite`. All three build offline from the frozen inputs.

```sql
SELECT grouping, categories, cases_tabulated, controls_tabulated,
       case_total, control_total, cases_outside_table, controls_outside_table
FROM rojas_table_coverage ORDER BY grouping;

SELECT category, label, case_count, sampled_control_count, locator
FROM rojas_observation WHERE grouping = 'afsc'
ORDER BY case_count DESC, category;
```
