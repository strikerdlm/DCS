# Zotero DCS collection review

The Zotero DCS collection contains **23 PDF attachments**. Agentic LlamaParse processed 108 relevant pages from 14 attachments. Nine used prior parse results from the same PDF or study, including six byte-identical files from the six-PDF intake. The source register records the Zotero attachment and item keys, file and Markdown hashes, page selection, and disposition. The 33 crosswalk entries identify exact copies, alternate PDFs, reprinted observations, and overlapping risk sets. [Source register](../data/chamber/zotero-dcs-2026-11-19/sources.csv) · [Overlap register](../data/chamber/zotero-dcs-2026-11-19/overlap.csv)

## Data added

| Source | Data added and how to use them |
| --- | --- |
| NASA 2016 evidence report | The four operational prebreathe protocols reported **0 DCS in 244 person-EVAs** by 6 May 2016. The 2013 snapshot covered 213. The database adds only the 31 additional person-EVAs, by protocol, and reconstructs the 2016 totals in a view. The older table's confidence limits appear unchanged alongside the larger denominators, so the increments carry no confidence limits. The Nuc-3 result is an interim 30-exposure subset. The report gives 21 monitored Nuc-1 exposures and 20 evaluable DCS exposures after a left-ventricular gas emboli termination. [NASA evidence reports](https://www.nasa.gov/directorates/esdmd/hhp/risk-of-decompression-sickness/) |
| NASA exercise prebreathe, 2004 | The 104-page and 95-page copies report the same NASA technical publication. Tables 6, 11 and 13 add five alternate fit-sample DCS count pairs plus the fitted percentages and estimated mean cumulative oxygen consumption for both models. The seven hypothesis-test outcome rows and the positive-subject VGE records already exist. RM and NM select different subsets and use different DCS time windows. [NASA/TP-2004-213158](https://ntrs.nasa.gov/citations/20040191712) |
| NASA symptom-resolution report | Added five initial categories among **220 symptom reports in 119 DCS cases**, the nested 195 reports with pressure information, and the recurrence or new-symptom margin. Table XIII adds symptom-level treatment and Type I/II counts by ambulation condition. Its DCS strata are **78/591** and **41/378** and sum to 969 exposures, while the separately reported fit sample uses 968. The report's USAF margins reuse the Muehlberger archive. [NASA treatment report](https://ntrs.nasa.gov/citations/20140012081) |
| Pilmanis et al., ADRAC prospective study | Five groups of 30 reported actual Kaplan–Meier DCS, any VGE and model-predicted DCS percentages. These are the same validation profiles as NEDU MV-A through MV-E. The archive reports denominators of 30 or 31. The supplement keeps the article's percentages and avoids rounding them back to cases. [Primary article](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/75/9/article-p749.pdf) |
| Butler, 1996 AC-130 cluster | Six of 17 crew were diagnosed on a single selected mission that peaked at 17,000 ft. The six narratives retain symptom onset anchors and reported timing. Four presented about 32 hours after the flight. Some had symptoms at landing. The four other historical clusters in Butler's review are cross-references. [Primary case report](https://pubmed.ncbi.nlm.nih.gov/12182221/) |
| NASA breaks in prebreathe | Added the seven distinct operational interruptions in Table 3. The second STS-128 line is linked purge detail for the same EVA. The INC-50 report gives a 13-second observed interval and a separate four-minute assumption. The ground chamber study was already loaded. The timeline rows have no individual DCS outcome assigned. [NASA report](https://ntrs.nasa.gov/citations/20240016139) |

The existing Rice, Ohrui, Bason, Piwinski, Brandt, Hancock, Australian, FAA, 2013 NASA, U-2 and SmartSuit outcomes are reused. The Singapore conference abstract repeats the comparison already in Cheok's final paper. Howle's BIG292 diving cohort and the T-38 modeling example stay in the source register as methods references.

## Build and query

The intake contains 82 extracted observations or estimates, six AC-130 case records, and seven EVA interruption records. Clinical cases, symptoms, person-EVAs and model percentages retain their original units. All extracts and their manifest build offline.

```sh
python -m scripts.build_chamber_database --zotero-dcs-supplement
python -m scripts.build_chamber_database --fac-official --rojas-supplement --expedition-supplement --zotero-dcs-supplement
```

The first command writes `artifacts/chamber-zotero-dcs/observed.sqlite`. The second writes `artifacts/chamber-fac-official/observed-v1.10-rojas-zotero-dcs.sqlite` and includes the earlier six-PDF, FAC, Rojas and literature supplements.

```sql
SELECT * FROM zotero_dcs_eva_totals_2016 ORDER BY stratum;

SELECT source_id, scope, related_key, relationship, disposition
FROM zotero_dcs_overlap ORDER BY source_id, scope;
```
