# Published chamber outcomes, release 1.0

[Public source search update and ADRAC validation crosswalk, 19 November 2026](chamber-source-search-2026-11-19.md)

[Release 1.1 Zotero supplement and build instructions](chamber-zotero-supplement.md)

[Release 1.2 public web sources and build instructions](chamber-web-supplement.md)

[Release 1.3 literature supplement and build instructions](chamber-literature-supplement.md)

[Release 1.4 chamber cohorts and prior pressure exposure](chamber-cohort-supplement.md)

[Release 1.5 Mahon citation database and linked chamber outcomes](chamber-mahon-citations.md)

[Release 1.6 public chamber outcome search and SQLite build](chamber-discovery-supplement.md)

[Release 1.7 EBSCO UNAL workflow, public literature intake and search log](2026-11-19_ebsco_altitude-dcs.md)

[Release 1.8 historical human chamber studies and cohort checks](chamber-historical-supplement.md)

[Release 1.9 pressure-suit and crossover studies](chamber-protocol-supplement.md)

[Release 1.10 COMEX expedition flights and historical aviation archives](chamber-expedition-supplement.md)

[Release 1.11 cadet chamber protocols and published outcome rates](chamber-cadet-supplement.md)

[Release 1.12 Royal Air Force chamber records and staged oxygen trials](chamber-raf-supplement.md)

[Release 1.13 NASA, AFRL and Russian clinical chamber series](chamber-clinical-series-supplement.md)

[Release 1.14 British and Swedish chamber outcomes](chamber-crossover-supplement.md)

[Release 1.15 historical chamber trials and Royal Navy selection courses](chamber-historic-supplement.md)

[Release 1.16 simulated spaceflight, air interruptions and source reconciliation](chamber-spaceflight-supplement.md)

[Release 1.17 denitrogenation strata, repeated exposures and Brazilian chamber survey](chamber-denitrogenation-supplement.md)

[Release 1.18 international chamber evidence and clinical case linkage](chamber-international-supplement.md)

[Release 1.19 archival chamber and flight trials](chamber-archival-trial-supplement.md)

[Release 1.20 rapid-decompression cohorts and source crosswalk](chamber-rapid-decompression-supplement.md)

[Release 1.21 chamber programs and historical case reports](chamber-program-supplement.md)

[Release 1.22 chamber Doppler and operational flight surveillance](chamber-flight-surveillance-supplement.md)

[Release 1.23 archive follow-up and simulated zoom trials](chamber-archive-followup-supplement.md)

[Release 1.24 historical chamber surveillance and clinical outcomes](chamber-historical-outcomes-supplement.md)

[Release 1.25 hypobaric chamber case reports and training cluster](chamber-case-supplement.md)

[Release 1.26 participant-linked chamber trial timing](chamber-timing-supplement.md)

[Release 1.27 original journal archives and chamber outcome tables](chamber-archive-supplement.md)

[Release 1.28 chamber symptom counts and paired crossover outcomes](chamber-symptom-supplement.md)

[Release 1.29 chamber case series, symptom onset and diagnostic reports](chamber-case-series-supplement.md)

[Release 1.30 age-stratified chamber outcomes and archival crosswalks](chamber-age-strata-supplement.md)

[Release 1.31 historical chamber outcomes and cohort reconciliation](chamber-reconciliation-supplement.md)

[Release 1.32 NASA session and technician counts and FAA source verification](chamber-nasa-strata-supplement.md)

[Release 1.33 NASA case timing and Swedish paired chamber outcomes](chamber-nasa-cases-supplement.md)

[Release 1.34 Swedish post-dive chamber exposures and exercise crossover VGE grades](chamber-paired-exposures-supplement.md)

[Release 1.35 archived post-dive chamber flights and staged symptom records](chamber-staged-exposures-supplement.md)

[Release 1.36 USAF treated-case surveillance and commercial-flight observations](chamber-treated-case-supplement.md)

[Release 1.37 treated-case distribution, follow-up and individual bubble grades](chamber-case-detail-supplement.md)

[Release 1.38 Polaris Dawn ground test, chamber accident and historical table reconciliation](chamber-threshold-supplement.md)

[Release 1.39 historical Doppler outcomes and a chamber training case](chamber-bubble-outcomes-supplement.md)

[Release 1.40 NASA symptomatic noncases and diagnostic ratings](chamber-diagnosis-supplement.md)

[SharePoint books and papers, linked DCS/VGE observations and denominator reconciliation](chamber-sharepoint-review.md)

[Official Colombian Air Force case register, annual training activity and role counts](chamber-fac-official.md)

The SQLite database contains 16 source records, the observed NASA and AFRL protocol groups, the NEDU compilation, published aviation training counts and the public Grade IV VGE onset intervals. The external benchmark reserves four operational cohorts. Their observed outcomes can be queried today. All five primary strata fall outside the estimand of the frozen NASA group model, so expected events and external calibration are unavailable. The baseline is the repository tree at `93eab8ae728d2d18e9a3de0a196bff264d1f1b08`. [Source inventory](../data/chamber/v1/sources.csv) · [Frozen study design](../data/chamber/v1/design.json) · [Cohort overlap](../data/chamber/v1/source_overlap.csv)

## Build and query

Run from the repository root with Python 3.12. The database builder uses the standard library and SQLite 3.37 or later. Model evaluation uses the project's NumPy and SciPy dependencies. Both commands work offline from the versioned tables. The builder checks the input and model digests, reconciles denominators, checks foreign keys and publishes the database atomically. An existing different file requires a new output path.

```sh
python -m scripts.build_chamber_database
python -m scripts.evaluate_chamber_benchmark
python -m pytest -q tests/test_observed_benchmark.py
```

The commands generate `artifacts/chamber-v1/observed.sqlite` and `artifacts/chamber-v1/evaluation.json`. The evaluation includes model parameters, validation and the external cohort assessment. Pass `--output PATH` to choose another location. The release manifest identifies the portable source data. When the original acquisition cache is available, use `--verify-cache artifacts/chamber-sources-v1` to verify all 16 source hashes. Publisher watermarks can change the PDF bytes on later downloads. An independent build produced the same SQLite file byte for byte. All 216 repository tests passed. [Input checksums](../data/chamber/v1/manifest.json) · [Verification record and output digests](evidence/chamber-observations-v1.json)

```sql
SELECT source_id, stratum, endpoint, cases, denominator, denominator_unit, window
FROM locked_external ORDER BY source_id, stratum;

SELECT profile, test_id, agreement
FROM a1309_nasa_overlap WHERE agreement LIKE '%differ%';

SELECT finding_id, finding, action FROM source_finding ORDER BY finding_id;
```

## Evidence and denominators

| Source | Public observations included | Analysis decision |
| --- | --- | --- |
| NASA historical database | 548 exposures and 84 DCS cases across 31 tests. The poster gives 237 participants in its abstract and 238 in its body. | Historical summary with unresolved participant count. Individual linkage requires access from the custodian. [NASA poster](https://ntrs.nasa.gov/citations/20080013529) |
| NASA 2019 and 2020 | Table F1 has 49 test rows, 1,031 exposures, 1,030 DCS-evaluable exposures and 125 cases. The frozen development subset has 124 cases in 885 evaluable exposures across 41 groups. | A participant in Nuc-1 left early for left ventricular gas emboli. The seven long stages and the ambiguous ambulation assignment in test 10 are excluded from the development subset. The 2019 VGE cells sum to 371 any-grade and 168 Grade IV. The 2020 analysis reports 368 and 166 among 903 monitored exposures. Each version retains its own counts. [2019 Table F1](https://www.nasa.gov/wp-content/uploads/2023/03/abercromby-suited-chamber-testing-tp220343-2019.pdf) · [2020 Tables 1–3](https://ntrs.nasa.gov/citations/20200004317) |
| Conkin et al., AFRL | All 29 four-hour test groups, 340 DCS cases in 708 exposures. Table I gives sex, pressure, prebreathe including ascent and retrospectively assigned workload. | Standalone four-hour activity experiment. Tests 16 and 18 used a different gas mixture. Cross-test participant IDs are unavailable. [Original Table I and Appendix](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/84/7/article-p661.pdf) |
| NEDU A1309 | All 117 Appendix E profiles, totaling 2,594 exposures and 858.3 weighted outcomes. Four additional unassigned exposures each had DCS. Table 2 reports 2,598 exposures, 862 positives and three marginals weighted at 0.1. | All 35 named NASA rows map to NASA protocols. PRP IV has 69 exposures and 8.3 weighted events in NEDU versus 65 and 8 cases in F1. The compilation stays outside fitting. No individual ANS file was retrieved. [NEDU TR 18-01, Table 2 and Appendix E](https://apps.dtic.mil/sti/trecms/pdf/AD1101527.pdf) |
| Pilmanis et al., USAF | 24 published Kaplan–Meier estimates across two endpoints and three horizons. The three interruption arms include 40, 40 and 32 exposures. | Interruption began after 30 min of oxygen and was followed by 30 min of oxygen. At one and two hours the historical comparator includes 95 exposures. At four hours it includes the 28 assigned the longer protocol. Participants repeat across arms. Group size, horizon and percentage are retained. [Methods and Table II](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/81/10/article-p944.pdf) |
| thregI::hdsd | 238 original public IDs, 69 finite onset intervals and 169 right-censored observations of first Grade IV VGE. | Reproduces the existing VGE comparator. Missing right bounds in SQLite identify right censoring through the accompanying status. [Pinned data dictionary](https://raw.githubusercontent.com/cran/thregI/11919e13da5be6412dde3184c814ffd3fb4f1873/man/hdsd.Rd) |

The source register also includes the primary activity experiments, the supplied Webb–Miller preprint, the NASA interruption case review and the De Ridder gas-exchange study. Workload summaries distinguish the highest one-minute oxygen consumption from mean task oxygen consumption. Fitness, posture, ambulation and timing relative to decompression have separate meanings. In the 2016 nonambulatory chamber cohort, the authors explicitly report zero DCS cases and zero VGE observations among 20 men. They measured workload on the ground before chamber exposure. The late break in the NASA case and the physiological washout/VGE results inform data collection. Each has its own outcome and observation setting. [Webb 2010, Table II](https://www.nasa.gov/wp-content/uploads/2023/03/webb-exercise-oxygen-consumption-2010.pdf) · [Webb 2016, Table I](https://pubmed.ncbi.nlm.nih.gov/27208673/) · [NASA interruption review](https://ntrs.nasa.gov/citations/20240016139) · [De Ridder et al.](https://doi.org/10.3357/AMHP.6554.2025)

The 19 rounded Table III rows in the supplied preprint reproduce an ordinary least-squares R² of 0.9999813. At 22,500 ft, 120 min at altitude, workload 7.6 mL/kg/min and 30 min of prebreathe, the printed equation gives 32.98%. Changing only the prebreathe to 90 min gives 34.84%. Changing only the exposure duration to 180 min gives 30.22%. Those are arithmetic checks on constructed points. The observed-outcome database excludes these points from the clinical fits. The 3RUT prototype and its simulated grid also remain research comparators.

## Locked operational cohorts

The lock designates studies and strata separately from fitting and recalibration. Published outcomes were visible before this retrospective lock. Named institutions and study settings support separation of the operational series from the NASA development experiments. Cross-institution participant identifiers are unavailable. Each row retains its native case definition and follow-up.

| Cohort | Cases / published denominator | Interpretation |
| --- | ---: | --- |
| US Navy, Rice | 94 / 38,153 exposures | Confirmed DCS during exposure or within 48 h. Five Table I profile cells sum to 92. Table II is a nested calendar period, and Table III further stratifies by rank. The database retains all three sets of printed margins. [Tables I–III](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/74/1/article-p56.pdf) |
| Singapore, Cheok | 2 / 1,530 before and 2 / 1,729 after | Specialist-diagnosed DCI, a ten-minute plateau at 25,000 ft and staggered mask removal. Some personnel took part in both periods. [Methods and Results](https://asma.kglmeridian.com/downloadpdf/view/journals/amhp/92/5/article-p289.pdf) |
| Australia, Smart and Cable | 42 / 10,851 exposures | Definite or probable DCI in the denominator-available AVMED series. Both year and profile margins reproduce the overall count. Annual profile denominators are published, while the corresponding year-by-profile case cells are unavailable. [Boxes 4 and 6](https://jmvh.org/wp-content/uploads/2025/11/ADFHealth_5_1_03-10.pdf) |
| Israel, Ben-Ari | 11 / 2,279 trainees and instructors | 272 chamber sessions. The counting unit for repeated personnel remains unresolved. Four additional flight cases have a separate row with a null denominator. [Results and Table 1](https://www.ima.org.il/MedicineIMAJ/Article.aspx?aId=6788) |

The evaluator checks population, endpoint, ascertainment, denominator, duration and the joint protocol inputs before computing expected events. All five locked strata lack group mean arrival TR360 and source-compatible histories. Consequently, external observed-to-expected ratios, Brier score, log loss and calibration intercept/slope are null. No cohort is designated for recalibration. Clinical survival fitting requires exposure-linked onset and censoring records. Obtaining standardized follow-up in short aviation training remains the prerequisite for a clinical model release.

## Group model results

The two studies below use different populations and keep their observations separate. The interval is an approximate 95% delete-one-block jackknife interval for the change in log loss, with all folds refit on each deletion. A positive change favors the baseline. The blocks account for shared protocol settings or pressures. The underlying data cannot identify repeat-person uncertainty.

| Internal comparison | Holdout blocks | Baseline log loss | Challenger log loss | Change, approximate 95% interval |
| --- | ---: | ---: | ---: | --- |
| NASA pooled prevalence versus hierarchical beta-binomial protocol-family prevalence | 8 connected components of 12 families | 0.41093 | 0.41185 | +0.00091 [−0.00401, +0.00584] |
| AFRL grouped logistic regression with pressure, prebreathe, sex and gas versus the same model plus assigned workload | 9 nominal pressures | 0.65348 | 0.66337 | +0.00989 [−0.29307, +0.31284] |

For NASA, the hierarchical model predicted 137.32 events across held-out groups versus 124 observed, with Brier score 0.12220. For AFRL, adding workload changed expected events from 340.64 to 381.27 versus 340 observed, and Brier score from 0.22993 to 0.23287. The data do not establish an improvement from the assigned workload term. The versioned JSON contains refitted coefficients, every held-out prediction, calibration bins and the grouped sensitivity estimates. The frozen NASA ridge comparator also has a connected-holdout log-loss difference whose interval crosses zero. [Frozen NASA comparator](../tinydcs/studies/nasa-chamber-dcs-v1.json)

For the 60 held-out hdsd IDs, reconstruction from the public intervals yields mean interval negative log likelihood 1.191239 for the existing Grade IV model and 1.364174 for its intercept-only comparator. The calculation uses interval probability for finite bounds and survival through the last observation for right censoring. No future bubble measurement enters either clinical pre-exposure fit. [Frozen VGE comparator](../tinydcs/studies/grade-iv-vge-v1.json)

## Database dictionary

| Tables or views | Record unit and conventions |
| --- | --- |
| `cohort`, `source`, `source_overlap`, `source_finding`, `frozen_input` | Cohort partition, source edition, URL, acquisition digest, locator, extraction method, access notes, overlap evidence and discrepancies. Unlisted source pairs have no recorded overlap assessment. |
| `nasa_test`, `development_counts` | One published test group. Pressure is psia, duration hours and TR360 the computed group mean. DCS has its own evaluable denominator. Null VGE cells identify unmonitored stages. |
| `afrl_test`, `activity_summary` | Test-level sex coding, mmHg, minutes and assigned workload in mL/kg/min. Separate task reconstructions retain the measurement setting and published historical percentages. |
| `a1309_profile`, `a1309_nasa_overlap` | Protocol as printed, source page, exposure denominator and original event token. The fractional PRP IV token has a null integer case count. Crosswalks match named protocols and retain discrepancies. |
| `air_break_arm`, `air_break_estimate` | Scheduled oxygen segments, air interruption, posture, arm size, endpoint, horizon in hours and published Kaplan–Meier percentage. No exact case numerator is derived. |
| `aviation_count`, `adf_exposure_margin`, `external_lock`, `locked_external` | Published totals and projections, ascertainment, denominating unit and case count. The locked view contains one primary observation per disjoint exposure stratum within each published cohort. |
| `vge_interval` | Released ID, original age and sex coding, TR360, ambulation, hours since exposure origin, interval bounds and censoring type. |
| `source_statistic`, `endpoint` | Report-level quantities with units and locators, and definitions of clinical and Doppler endpoints. |

Firecrawl located the NEDU report and retrieved the NASA archive description. The live DTIC PDF endpoint returned a maintenance page. Tavily supplied the full report text, including Appendix E. Each NEDU row name and pair of numbers was matched in order against the repository transcription. Tavily also located the operational papers and extracted the Australian and AFRL tables. The original publisher PDFs, the frozen NASA companion CSV, the supplied preprint and the pinned R data were checked locally. The companion CSV digest matches the prior NASA model export. The hdsd CSV preserves the seven columns of the CRAN release, including the original `Inf` right boundary. thregI 1.0.4 credits Man-Hua Chen and declares GPL-2. [Pinned package description](https://raw.githubusercontent.com/cran/thregI/11919e13da5be6412dde3184c814ffd3fb4f1873/DESCRIPTION) · [Source data](https://raw.githubusercontent.com/cran/thregI/11919e13da5be6412dde3184c814ffd3fb4f1873/data/hdsd.RData) · [GPL-2](../data/chamber/LICENSE-hdsd.txt)

## Prospective FAC/CEMAE registry

The registry initializer creates an empty SQLite template for consecutive enrollment, including exposures awaiting follow-up. Use a separate institutionally controlled path for participant data. The proposed primary endpoint is adjudicated symptomatic DCS during exposure or through 48 hours after return to site pressure. The choice of return as the time origin for the proposed post-exposure window requires protocol agreement. All stored elapsed times use minutes from exposure start so another approved horizon can be evaluated. The template assigns no clinical labels automatically.

```sh
python -m scripts.fac_chamber_registry init PATH_TO_NEW_PRIVATE_DB
python -m scripts.fac_chamber_registry schema
python -m scripts.fac_chamber_registry append PATH_TO_PRIVATE_DB PATH_TO_SNAPSHOT_JSON
```

The snapshot requires a pseudonymous participant, exposure and chamber-session ID, protocol version, source version and digest, extraction method and timestamp. The first revision can register the exposure with clinical follow-up pending. Subsequent revisions retain the prior document, the submitted file digest and the canonical snapshot digest. The original participant, exposure origin, pre-exposure plan and its time-stamped segment evidence remain identifiable across revisions. Supply the complete current snapshot on each revision. A repeated submission with identical content is idempotent.

Planned and actual profiles use TinyDCS's existing validated history types. Split a pressure–gas segment at each observed interruption or mask transition, and record its mask state, delivery and workload basis. The register holds residence and previous-exposure history, measured absolute starting pressure and instrument, mechanical activity and posture, highest one-minute VO₂, task mean VO₂ and fitness in their respective fields. Document symptom onset bounds, termination, return, last assessment, confirmed event-free coverage and censoring separately. Clinical DCS/DCI assessments and time-stamped Doppler grades occupy distinct views. A partial follow-up remains partial at the proposed 48-hour horizon. [Synthetic enrollment example](examples/fac-chamber-enrollment.json)

The next data-access request is for pseudonymized exposure, participant, session and original protocol IDs, actual pressure–gas timelines, measurement methods, onset or censoring times and post-return ascertainment from the NASA and AFRL custodians. The same identifiers would allow the A1309 overlap decisions to be refined. No linked individual DCS file or designated recalibration cohort was available in this release.
