# Chamber evidence release v1.40

## NASA symptomatic reports

The NASA technical memorandum describes 32 chamber exposures with documented symptoms and a final classification of no DCS. The release adds those selected records under the existing `nasa03` citation, with the printed exposure code, procedure, age, sex, maximum Doppler grade, timing and page locator. Eleven had a reported peak VGE grade of IV. The records are useful for studying how symptoms and bubbles were interpreted in this already indexed cohort. The selection covered symptomatic reports and gives no roster of exposures without symptoms. [NASA technical memorandum, printed pp. 71–85](https://ntrs.nasa.gov/api/citations/20030063917/downloads/20030063917.pdf#page=79) · [Transcription](../data/chamber/v1.40/symptomatic_noncases.csv)

First symptom report and symptom recollection use separate fields. Three reports occurred after the test, one preceded ascent to the target pressure and 28 were recorded during the test. Narrative 1 gives an estimated 120 minutes in its summary and recalls the beginning of the second hour in the narrative. Its debrief report time is unavailable. Narrative 24 gives 590 minutes from test start and 350 minutes from test end for the same report. Narrative 3 records a Type I diagnosis revised at a one-week review. [Narratives, printed pp. 71–72 and 82](https://ntrs.nasa.gov/api/citations/20030063917/downloads/20030063917.pdf#page=79)

## Diagnostic ratings and anonymous trial

Conkin and colleagues compared the original diagnoses of the same 135 selected reports with blinded reviewers’ ratings. Table III contains 103 original DCS labels over 135 reports and 406 positive ratings over 675 outside ratings. Four to six experts rated each report. For all six symptom and VGE strata, the database preserves both denominators and counts. The authors’ estimates of diagnostic error require a latent model with unobserved true diagnoses. The peak VGE and symptom variables were observed during or after exposure. [Original article, Methods and Table III](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/77/8/article-p816.pdf) · [Observed rating matrix](../data/chamber/v1.40/diagnostic_strata.csv)

Table VIII gives seven original DCS diagnoses across 48 exposures in a protocol identified only as Trial N. The database preserves the grouped observation under an overlap hold because the paper gives neither the profile nor exposure identifiers. [Original article, Table VIII](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/77/8/article-p816.pdf)

## Provenance and rebuild

Tavily and Firecrawl supported discovery and source checks. The original publisher PDF and the already indexed NASA report support the data. Duplicate search hits include the Polish training and Everest II studies. [Queries](../data/chamber/v1.40/search_runs.csv) · [Search results](../data/chamber/v1.40/search_hits.csv) · [Input checksums](../data/chamber/v1.40/manifest.json)

```sh
python -m scripts.build_chamber_database --chamber-diagnosis-supplement
python -m scripts.build_chamber_database --chamber-diagnosis-supplement --fac-official
```

The public and Colombian aggregate outputs are `artifacts/chamber-v1.40/observed.sqlite` and `artifacts/chamber-fac-official/observed-v1.40.sqlite`.

Both builds passed SQLite integrity and foreign-key checks. Comparison to v1.39 verified all prior rows and the five locked external strata. The historical case index contains the original 103 NASA DCS cases and the new symptomatic report table has 32 unique exposure codes. The Grade IV count of 11 in those 32 reports agrees with the diagnostic matrix. The public rebuild was byte-identical. All 32 benchmark tests passed.
