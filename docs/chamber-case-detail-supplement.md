# Treated-case distributions, follow-up and individual bubble grades

Release 1.37 adds 30 rows from a treated-case table, 27 grouped observations and 20 participant-protocol records with published venous gas emboli (VGE) grades. The Krause source is upgraded in place. The original Eiken source and prior group rows are reused. [Rudge daily table](../data/chamber/v1.37/case_margins.csv) · [Rudge group outcomes](../data/chamber/v1.37/observations.csv) · [Krause follow-up](../data/chamber/v1.37/krause_outcomes.csv) · [Eiken peaks](../data/chamber/v1.37/eiken_stage_peaks.csv)

## Rudge, 1990

The USAF review screened 125 treated chamber cases from 1978 to 1988. Of 85 records with a recorded last menstrual period, 81 met the author's inclusion criteria. The analyzed series contains 62 historical Type I cases and 19 neurological Type II cases. The paper reports no corresponding exposure denominators by cycle day or oral contraceptive use. The database stores these data as distributions among cases and links likely overlap with Weien and Wirjosemito. [Original article, Table I and Figure 1](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/61/7/article-p657.pdf#page=2) · [Cohort links](../data/chamber/v1.37/overlap.csv)

| Days since onset of the last menstrual period | Type I cases | Type II cases |
| --- | ---: | ---: |
| 0–4 | 16 | 6 |
| 5–9 | 13 | 5 |
| 10–14 | 13 | 4 |
| 15–19 | 9 | 2 |
| 20–24 | 8 | 1 |
| 25–29 | 3 | 1 |

Table I's Type I cell for day 8 without reported birth-control pill use is blank. The legible daily counts yield 61 Type I and 18 Type II cases, compared with 62 and 19 in Figure 1. Both differences occur in days 5–9. The daily blank remains null. The transcribed daily cells and the separately published figure margins are preserved.

## Krause and Pilmanis, 2000

The original article details follow-up of the already indexed research archive. Of 801 diagnosed cases, 794 began at altitude. Among the selected 749 cases receiving ground-level oxygen, 728 were already asymptomatic at the beginning of that treatment. Case severity informed treatment allocation. Among the 613 cases with VGE in that treatment group, 260 had complete VGE follow-up. In those 260 cases, 10 resolved before descent, 69 during descent or before the first ground-level scan and 181 at ground level. The latter counts describe VGE resolution conditional on complete monitoring. The previous 801/2,001 clinical exposure row and 739/749 outcome row were preserved. [Original article, Results pp. 116–117](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/71/2/article-p115.pdf)

## Eiken and colleagues, 2023

Table 1 provides peak scores before and after the altitude exercise for the two conditions completed by ten jumpmasters. One hypobaric-preoxygenation trial ended with DCS before the exercise intervention. Its pre-exercise peak of 4 is preserved and its post-exercise value is null. The study's clinical DCS and overall VGE counts already appear under `eiken23`. [Original article, Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC10363086/)

## Source tracking and rebuild

Tavily and Firecrawl returned the original Rudge and Eiken results and the NASA Test 6 archival material. The Test 6 slides were a byte-identical copy of the source in v1.6 and retain the unresolved 61 versus 62 reported exposures. The Polaris Dawn conference article is recorded as a lead. Public metadata gave no extractable clinical or ultrasound results. [NASA archive](https://ntrs.nasa.gov/citations/20260003261) · [Polaris Dawn citation](https://jglobal.jst.go.jp/en/detail?JGLOBAL_ID=202602254030260187) · [Search queries](../data/chamber/v1.37/search_runs.csv) · [Search results](../data/chamber/v1.37/search_hits.csv) · [Input checksums](../data/chamber/v1.37/manifest.json)

```sh
python -m scripts.build_chamber_database --chamber-case-detail-supplement
python -m scripts.build_chamber_database --chamber-case-detail-supplement --fac-official
```

The public and combined outputs are `artifacts/chamber-v1.37/observed.sqlite` and `artifacts/chamber-fac-official/observed-v1.37.sqlite`.

Both builds passed SQLite integrity and foreign-key checks. All prior outcome rows and the five locked external strata were preserved. The four checked original PDF digests matched the database, the public rebuild was byte-identical, and all 29 benchmark tests passed.
