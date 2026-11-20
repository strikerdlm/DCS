# NASA case timing and Swedish paired chamber outcomes

Release 1.33 adds 97 records from the original NASA case report and five outcome observations from a Swedish paired chamber study. The NASA records extend the existing `nasa03` source. The Swedish study has one new source entry and an overlap link to its predecessor. [NASA case transcription](../data/chamber/v1.33/nasa_table_i_cases.csv) · [Swedish observations](../data/chamber/v1.33/observations.csv) · [Cohort link](../data/chamber/v1.33/overlap.csv)

## NASA case timing

Conkin, Klein and Acock reported 103 DCS cases diagnosed across 731 chamber exposures from 1982 through 1999. The 97 historical Type I cases were transcribed from Table I. The six historical Type II cases already have narrative records. The `literature_case_index` view includes each of the 103 cases once, with source, case number, endpoint, time basis, VGE detection and locator. These are cases from an already indexed cohort. The report provides no linked roster of event-free exposures for this case series. [NASA report, pp. 8–12](https://ntrs.nasa.gov/api/citations/20030063917/downloads/20030063917.pdf#page=16)

| DCS time in Table I | Type I records | Stored interpretation |
| --- | ---: | --- |
| Unmarked | 63 | First report during the test |
| `#` | 28 | Symptom noticed earlier and reported later during the test |
| `+` | 4 | Symptom time recalled during debriefing |
| `---` | 2 | Onset timing unavailable for cases 19 and 76 |

The transcription preserves published subject and test codes, site, date, symptom site and the printed DCS time token. First Doppler detection is recorded in 91 Type I cases. Six had no VGE detected during the test. The Type I extraction covers Table I, which lacks maximum bubble grade.

The timing review records three conflicts. For cases 30 and 90, the detailed narratives support first symptom report at 68 and 110 minutes, compared with 86 and 108 in Table I. For case 37, both narrative sections support first VGE detection at 133 minutes. Table I gives 113. Case 34 describes two distinct symptoms, with wrist tingling reported at 180 minutes and the ankle symptom attributed to DCS reported at 300 minutes. The case index retains the published time values and the review provides the linked interpretations. [Timing review](../data/chamber/v1.33/nasa_timing_review.csv)

## Swedish paired chamber study

Balldin and Borgström compared normal-pressure and negative-pressure oxygen prebreathe in five volunteers, with two reported exposures per person. The normal-pressure exposures were selected to provoke symptoms and VGE. Three volunteers underwent prior hyperbaric air loading. The two arms were paired in fixed order. [Original 1977 article, pp. 1008–1010](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/48/11/article-p1007.xml?isSearch=true)

| Endpoint | Normal-pressure oxygen | Negative-pressure oxygen |
| --- | ---: | ---: |
| Positive bends by study definition | 5/5 | 3/5 |
| Questionable bends | | 1/5 |
| Any VGE by precordial Doppler | 5/5 | 3/5 |

Three participants match the 1976 article by published initials, height and mass. Their reported symptom times, first Doppler detection times and protocols differ. The new rows carry an overlap hold and remain descriptive evidence from a selected paired experiment. [1976 original, Table I](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/47/2/article-p113.xml?isSearch=true)

## Provenance and rebuild

The ledger contains 25 search, extraction and verification operations and 121 ranked results or source checks. It records the FAA pilot survey as an attitudes study and the Zhang susceptibility paper as a lead pending group outcome counts. Firecrawl verified the NASA catalogue entry. The Swedish publisher PDFs were checked directly after Tavily extraction could not fetch the article. [Queries](../data/chamber/v1.33/search_runs.csv) · [Results](../data/chamber/v1.33/search_hits.csv) · [Input checksums](../data/chamber/v1.33/manifest.json)

```sh
python -m scripts.build_chamber_database --chamber-nasa-cases-supplement
python -m scripts.build_chamber_database --chamber-nasa-cases-supplement --fac-official
```

The public and combined outputs are `artifacts/chamber-v1.33/observed.sqlite` and `artifacts/chamber-fac-official/observed-v1.33.sqlite`.

Both builds passed SQLite integrity and foreign-key checks. The comparison with v1.32 verified that all prior rows and the five locked external strata were preserved. The independent public rebuild was byte-identical, and all 25 benchmark tests passed.
