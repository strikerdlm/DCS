# SharePoint evidence for the hypobaric chamber database

**19 November 2026.** The review registered 34 works or editions from the connected library, including six textbook editions, and checked one public conference abstract against the corresponding thesis. Ten source records yielded 208 aggregate observations. A NASA report also supplied 26 subject rows with linked DCS and VGE observations. Thirteen sources corroborate earlier database entries, eight supply methods or definitions, and four are leads for clinical timelines. These counts describe the reviewed material across the selected collections. [Source register](../data/chamber/sharepoint-2026-11-19/sources.csv) · [Aggregate observations](../data/chamber/sharepoint-2026-11-19/observations.csv) · [Subject rows](../data/chamber/sharepoint-2026-11-19/vge_positive_records.csv)

The search covered all 15 files in **Books 2026 → Aerospace MedOps → DCS Papers**, the aviation medicine books, the ASEM journal archive, and relevant FAC altitude-chamber research, instructor and teaching folders. The thesis review used reported aggregates. Exact file hashes identified identical copies, and study titles, centers, periods and protocol identifiers identified other editions and overlapping cohorts. The source register records the library file’s SHA-256. For two large textbooks the locally synchronized PDF matched the hash supplied by SharePoint. The permission-bound file links are available in the local `artifacts/chamber-sharepoint/library-links.csv`. [Cohort and edition relationships](../data/chamber/sharepoint-2026-11-19/overlap.csv)

## Evidence for fitting

| Source | What can be extracted | How to use it |
| --- | --- | --- |
| NASA exercise prebreathe, 2004 | Tables 14–15 print 13 VGE-positive subjects in each ergometry-order group, among 27 subjects per group. The 26 rows give phase, ergometry order, age, weight, height, source sex code, BMI, DCS status, maximum Spencer grade and minutes to first VGE detection. Four rows have DCS, including two reports marked after altitude exposure. | Any VGE was detected in **13/27 in each group**. The 28 subjects without detected VGE have group summaries only. The recorded time is to the first bubble of any grade. The time of first Grade IV detection is unknown. Table 16 counts **683 and 555 repeated Doppler grades**, each with its own measurement denominator. [Tables 14–16, pp. 55–58](https://ntrs.nasa.gov/api/citations/20040191712/downloads/20040191712.pdf) |
| NASA historical DCS/VGE series, 2011 | The text reports **78 both, 150 VGE only, 4 DCS only and 317 neither**, totaling 549 by addition. Table 3 separately gives 14 paired DCS and VGE group results across threshold studies, with pressure and reported nitrogen-to-pressure ratio. | The four cells preserve joint outcome information. Table 4’s diagnostic-performance denominators of 1,322 and 1,210 belong to a different analysis. The threshold studies include repeated days and some volunteers selected for previous DCS or VGE. [Table 3, p. 17 and text following Table 4, p. 25](https://www.nasa.gov/wp-content/uploads/2023/03/conkin-prebreathe-overview-tp216147-2011.pdf) |
| NASA treatment research report | Tables VII and IX give observed DCS and VGE percentages for eight named protocols with pressure, duration, mean tissue ratio and ambulation. The reported clinical model sample has **119/968**. | The observed columns can be checked against later NASA tables. The adjacent columns contain fitted probabilities. For the VGE sample the report gives **345/842** in Fig. 30 and the summary, and **334/841** in the paragraph before Table VIII. Both versions are in the database. [Tables VII–IX and Fig. 30](https://ntrs.nasa.gov/citations/20140012081) |
| USAF training, Hancock et al. | The report gives **38/57,366** trainee exposures in 1997–1998 and **50/58,737** in 1999–2000. Their Type I/II counts are **30/8** and **37/13**, respectively. Thirteen inside-observer cases have an unknown exposure denominator. | Before the change, trainees used two profiles. The pre-change annual rows are 17/28,290 and 21/29,046, which sum to **38/57,336**, 30 exposures below the published subtotal. The post-change annual rows reconcile. Use the policy periods descriptively and retain the pre-change discrepancy. [Report identification and Tables 1–2 locator](../data/chamber/sharepoint-2026-11-19/sources.csv) |
| USAF chamber research, Balldin et al. | **1,108 DCS cases in 2,843 subject-exposures**. Among 49 CNS cases, **55.1%** had any VGE and **34.7%** had Grade IV VGE. Ultrasound was sampled every 10–15 minutes with a modified Spencer scale. | These percentages estimate VGE frequency conditional on a clinical diagnosis. The 49 CNS cases are a subset of the 218 neurological cases. The historical AFRL archive also appears in other studies. [Methods, Results and Table II](https://pubmed.ncbi.nlm.nih.gov/15558997/) |
| USAF chamber research, Webb et al. | Table II gives DCS, any-VGE and Grade IV percentages in the upper and lower thirds of six characteristics within each reported sex. The 72 values retain the source denominators and reported ranges. | Each characteristic describes a different grouping of the same study exposures. The reported range for the shortest female third excludes its stated mean. The six sex-specific totals and the separate repeat-volunteer paper are already available in the Mahon citation supplement. [Primary article](https://pubmed.ncbi.nlm.nih.gov/12546293/) · [Earlier extraction](chamber-mahon-citations.md) |
| Matched USAF case-control study, Rojas | Among 123 cases identified by billing code, the study reported eight U-2 pilots and 28 chamber technicians. One of 369 sampled controls held one of the two designated occupations. | These rows describe occupation within sampled cases and controls. The supplemental extraction includes all 40 printed occupation rows, the tobacco and alcohol tables, and the reported estimates. [Rojas extraction and reconciliation](chamber-rojas-2015.md) |

## Colombian training records

The official FAC workbooks subsequently supplied for 2010–2020 take precedence for registered events, recorded role and training activity counts. The table below preserves what the publications reported. The register marks 35 students and 19 instructors. The training workbook explains the 6,745 total as the sum of two activity columns. [Official records and comparison](chamber-fac-official.md)

The Celis working thesis, the conference abstract and the Olaya chapter report related DIMAE training data. Calendar years overlap from 2013 through 2020. The seven annual denominators for 2013–2019 match between the thesis figure and Olaya Table 2. For 2020 the thesis lists 120 trained and Olaya lists 117 exposures. Individual linkage and a common neurological case definition are unavailable. [Olaya chapter, Tables 2–3](https://esdeglibros.edu.co/index.php/editorial/catalog/download/371/277/4828?inline=1)

| Source location | Overall result as printed | Severity and role as printed |
| --- | --- | --- |
| Thesis, Spanish summary | 54/8,993, reported as 0.6% | 45 Type I, 9 Type II. The summary groups 34 instructors or inside observers. |
| Thesis, main Results and Tables 9 and 11 | 54/6,745, reported as 0.80%. The 11 annual rows underlying Fig. 3 instead sum to 54/8,993. | 38 Type I, 16 Type II. Table 9 lists 20 instructors and 34 students. |
| AsMA abstract 340 | 54/6,745, reported as 0.8% | 45 Type I, 9 Type II. The abstract groups 34 instructors or inside observers. |

Table 9 also assigns 2 diagnosed cases to cruise, 2 to descent, 14 to ground, 5 to postflight within 24 hours and 31 to the later category. These are case-conditional counts. The source reports recurrent events in five people and lacks exposure counts per inside observer. Reconciliation needs the counting unit for each total, repeat-exposure linkage and the adjudication version used for severity and role. [Thesis source record](../data/chamber/sharepoint-2026-11-19/sources.csv) · [Conference abstract 340](https://asma.kglmeridian.com/downloadpdf/view/journals/amhp/94/4/article-p237.pdf)

## What the books contribute

| Book and locator | Database use |
| --- | --- |
| *Ernsting’s Aviation Medicine*, 4th ed., ch. 7, Tables 7.1–7.2. *Ernsting’s Aviation and Space Medicine*, 5th ed., ch. 34, Tables 34.1–34.2, pp. 568–569 | The same seven-category symptom distribution appears in both editions for two-hour exposures at 28,000 and 37,000 ft. The 14 percentages are transcribed once with unknown denominators. Both editions also document the Doppler grading convention. |
| *Fundamentals of Aerospace Medicine*, 5th ed., ch. 17, Tables 17-8–17-10, pp. 328–331 | Clinical terminology, the Spencer Doppler scale and the expanded Eftedal–Brubakk two-dimensional echo scale support explicit fields for method, scale and grade. |
| *Fundamentals of Aerospace Medicine*, 4th ed., ch. 3, Figs. 3-5–3-7 | Fig. 3-5 is an ADRAC model output. Fig. 3-6 points to threshold research already represented in the chamber database. |
| Martin, *Aerospace Physiology*, ch. 7, §§7.2–7.6, and Reinhart, *Basic Flight Physiology*, 3rd ed., pp. 76–80 | Altitude symptoms, anatomical presentation and prior diving supply terminology for case and exposure histories. |

## Reproduction

The source checks covered the 26 NASA subject rows, the ten Doppler grade counts, both endpoints in all 14 NASA threshold profiles, the USAF annual and period DCS counts, and all 72 Webb subgroup percentages. The 11 Colombian annual rows and their total were checked against the table in the original Word file.

```sh
python -m scripts.build_chamber_database --sharepoint-supplement
python -m pytest -q tests/test_sharepoint_supplement.py
```

The offline build creates `artifacts/chamber-deduplicated/observed.sqlite`. It loads the frozen benchmark, supplements through v1.5 and four library tables. `sharepoint_source` records provenance, `sharepoint_observation` stores aggregates, `sharepoint_vge_positive_record` holds the selected NASA subject rows, and `sharepoint_overlap` records relationships. In `sharepoint_observation`, 98 rows have an exact event count and 110 have a reported percentage. A null denominator preserves a missing source denominator. A null `post_exposure_dcs_mark` preserves the absence of an asterisk in the printed subject row. [Frozen input hashes](../data/chamber/sharepoint-2026-11-19/manifest.json) · [Model development plan](../README.md#the-observed-outcome-database)

## Deduplicated database

The combined build already stores the six sex-specific results from Webb 2003 and the Webb 2005 repeat-volunteer result once in `citation_observation`. The library source records link to these rows, and its 72 additional Webb 2003 subgroup values remain queryable.

| View | Records returned | Canonical evidence |
| --- | ---: | --- |
| `a1309_deduplicated_profile` | 82 of 117 NEDU profiles | 34 reprinted NASA DCS counts use Table F1. NEDU PE1-A uses the primary Webb 1996 count in `citation_observation`. NEDU PRP IV and PE1-B have differing counts and retain both source versions. |
| `sharepoint_deduplicated_observation` | 200 of 208 library aggregates | Four repeated abstract results use the corresponding thesis rows. Four NASA treatment-report percentages use the corresponding exact counts in Table F1 where protocol, pressure, duration, denominator and printed rounding agree. |
| `citation_deduplicated_reference` | 242 of 243 bibliography entries | Reference 53 represents NEDU Technical Report 09-03. Both printed reference numbers, 53 and 84, are available in `citation_reference`. |

The corresponding `*_reprint` views give the source and canonical row keys for each exclusion. Use them to inspect the underlying tables. For example, this query traces the NEDU version of Webb’s prebreathe result.

```sql
SELECT p.profile, p.exposures, p.exact_cases, r.canonical_table,
       r.canonical_source_id, r.canonical_stratum
FROM a1309_profile AS p
JOIN a1309_profile_reprint AS r USING (profile)
WHERE p.profile = 'PE1-A';
```

These views remove confirmed reprints. The thesis’s denominator and severity variants, distinct endpoints, nested scopes and unresolved cohort overlap remain documented in the source tables. The views do not establish independent exposures for statistical pooling. The frozen development view still contains 124 cases in 885 evaluable exposures, and the external lock has five strata.

```sql
SELECT ergometry_order, count(*) AS vge_positive_subjects,
       sum(dcs) AS dcs_cases, count(post_exposure_dcs_mark) AS marked_after_exposure,
       min(first_vge_detection_min) AS earliest_detection_min,
       max(first_vge_detection_min) AS latest_detection_min
FROM sharepoint_vge_positive_record
GROUP BY ergometry_order
ORDER BY ergometry_order;
```
