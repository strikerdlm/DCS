# Chamber databases for the review and DCS model

The two SQLite files can be queried independently. Each contains the same evidence release ID. The accompanying `release.json` identifies the exact bytes of both files. Version-controlled inputs are the shared editing surface on both computers.

| File | Start here | Unit |
| --- | --- | --- |
| `systematic-review.sqlite` | `review_record`, `review_publication_catalog`, `review_study_report`, `review_current_screening` | Retrieved occurrence, published report, study and reviewer decision |
| `systematic-review.sqlite` | `review_seed_role_cell`, `review_supplementary_role_cell`, `review_secondary_role_cell` | Original and secondary role-specific counts for eligibility assessment |
| `dcs-model.sqlite` | `development_counts`, `afrl_test`, `vge_interval`, `locked_external` | Frozen NASA DCS groups, separate AFRL test groups, Grade IV VGE intervals and external strata |
| `dcs-model.sqlite` | `historical_case_catalog`, `dcs_case`, `publication_observation_revision` | Selected historical case histories and source corrections |
| `dcs-model.sqlite` | `publication_aircraft_incident`, `publication_aircraft_incident_count` | Aircraft incident profiles and source-reported outcomes |
| `dcs-model.sqlite` | `publication_aviation_group`, `publication_meader_reported_flight` | Descriptive historical flight groups and case-selected affected flights |
| `dcs-model.sqlite` | `publication_liske_case_profile`, `publication_case_milestone` | Selected neurological case profiles and source-reported chronology |
| `dcs-model.sqlite` | `publication_lewis_case_profile`, `publication_overlap` | Selected aviation surveillance cases and source differences |
| Both files | `shared_case_evidence`, `dataset_release`, `frozen_input` | Case-to-occurrence evidence, release and input provenance |

## Build and use a release

From the repository root in the project Python environment, choose a new output directory for a changed release. Rebuilding identical contents in the same directory is supported.

```sh
python -m scripts.chamber_products --output-dir artifacts/chamber-products/2026-11-20-r2
python -m scripts.evaluate_chamber_benchmark --database artifacts/chamber-products/2026-11-20-r2/dcs-model.sqlite --output artifacts/chamber-products/evaluation-v1.40-r2.json
python -m pytest -q tests/test_chamber_products.py tests/test_publication_review.py tests/test_review_identity.py tests/test_observed_benchmark.py
```

The benchmark reads only the model file, its adjacent checksum manifest and the frozen comparators in the checkout. To trace a case back to a paper, open the pair read-only. The following prints each enriched case, the source title and both extraction locators.

```python
from scripts.chamber_products import connect_pair

with connect_pair("artifacts/chamber-products/2026-11-20-r2") as db:
    for row in db.execute("""
        SELECT c.case_id, r.title, e.review_locator, e.extraction_locator
        FROM historical_case_catalog c
        JOIN shared_case_evidence e USING (source_id, endpoint)
        JOIN review.review_record r ON r.record_key=e.record_key AND r.report_id=e.report_id
        WHERE c.case_id = e.source_id || ':' || e.stratum
        ORDER BY c.case_id, e.record_key
    """):
        print(row)
```

`model_report_link` resolves a source table and its local source ID to a review occurrence and canonical report. `chamber_group_evidence` carries original staff and trainee counts with their study ID, stratum and locator. For example, Howard's observer and trainee counts each have one row. The review records later summaries as secondary evidence. Assess cohort overlap and the denominator definition before combining any groups.

## How the crosswalk changes an older case

The Gentry report supplies symptom onset at three hours, a first presentation at approximately 48 hours and a later presentation on day 14. All three observations belong to the same episode. The Yoneda abstract and extraction support a probable cutaneous DCS case with 24 hours of recurrence-free follow-up. The records retain their original diagnosis and counting unit. Neither supplies a population denominator. NASA case 30 keeps the 86-minute printed table value alongside a preferred 68-minute first symptom report from the narrative. The source locator accompanies each value. [Gentry report](https://pubmed.ncbi.nlm.nih.gov/28518008/) · [Yoneda report](https://pubmed.ncbi.nlm.nih.gov/9681378/) · [NASA timing review](../data/chamber/v1.33/nasa_timing_review.csv)

The historical catalog covers 103 numbered NASA cases and eight explicitly cross-linked published cases in this release. Additional case reports and aggregate outcomes remain in the original extraction tables. The fitting dataset contains 41 NASA groups with 124 DCS events in 885 exposures. A separate table contains 238 Grade IV VGE intervals. Clinical risk for an individual routine chamber trainee still requires linked clinical outcomes and validation in that population.

Ferris and Engel supply seven case-conditional margins for the previously catalogued Cincinnati and Halifax series. Their clinical chapter also corroborates one Berkeley case from the 1944 meeting minutes and preserves both reported times to postdescent worsening. [Neurological timing supplement](chamber-ferris-engel-neurological-supplement.md)

The 1946 Operation Everest diary supplies two dated staff cerebral bends reports. Eleven contextual entries retain the lock activity, staffing, recorded symptoms and resident follow-up. The study register links the investigator and diary reports to one experiment. [Operation Everest I supplement](chamber-operation-everest-i-supplement.md)

The 2026 AsMA familiarization case adds six source-reported milestones. The study register also links the EA-6 meeting abstract and original NASA slides to their shared cohort. [AsMA chamber case supplement](chamber-asma-chamber-case-supplement.md)

The aircraft incident supplement links the original military depressurization reports from Johnston and Mancini to two distinct studies. It preserves passenger and occupant denominators, one presumptive diagnosis, and an unreconciled symptom count. These aircraft counts are descriptive aviation evidence. [v1.65 source extractions](../data/chamber/v1.65/counts.csv)

Bruneau and Hertz report 17 dysbarism cases across 6,048 aircraft flights and one episode across 271 reported decompressions. Keep both counting units and the overlap hold for the 1957–1960 U-2 surveillance. Meader's 36 flight rows describe the affected flights already counted in the 958-flight selected cohort. The original journal article and DTIC reprint use one report ID. Table II covers 809 flights, nine fewer than the Table I sum after excluding crew member I. Nine flights remain unallocated. [v1.66 flight strata](../data/chamber/v1.66/flight_groups.csv)

The neurological archive supplement captures thirteen selected focal cases from Liske's 37 surviving pilots, with six chamber and seven aircraft exposures. The case profiles retain the EEG table and discussion separately for patients 2 and 8. Höök's follow-up and the 1954 Swedish report cite the same chamber case. Rudolph's aircraft case supplies a separate chronology with possible overlap in the earlier USAFSAM archive. Chamber and aircraft exposure denominators remain unavailable for these case series. [v1.67 clinical profiles and locators](../data/chamber/v1.67/liske_cases.csv)

Lewis reports 14 cases from 1968–1971 USAF safety forms and gives profiles for the 13 evaluable cases. The case-series denominator counts reported cases, with total flight exposure unavailable. The NASA compilations are linked to the original Lewis, Meader, Berry and Furry reports. For Berry, the published 51,580 trainees or person-exposures and original symptom rates take precedence over the 51,530 figure in West and Parker. [v1.68 source reconciliation](../data/chamber/v1.68/overlap.csv)

Davis et al. (1971) supply 18 milestones for two neurological cases. The aircraft case extends Lewis's existing B-52 gunner record. The chamber case preserves symptoms during ascent, apparent recovery, and later neurological progression without a cohort denominator. Davis et al. (1977) provide 16 annual role-by-altitude cells totaling 70 hyperbaric-oxygen-treated DCS cases in 242,352 chamber exposures in 1973–1976. Table VIII gives 39 treatments in 194,204 student exposures and 31 in 48,148 observer exposures. The model export reuses the review's 16 existing risk-set IDs and retains the overlap hold with Bassett's broader reporting series. The 145 historical treated referrals form a separate case series. [v1.69 counts and case anchors](../data/chamber/v1.69/observations.csv) · [Overlap evidence](../data/chamber/v1.69/overlap.csv)

Hodgson et al. give 571 numerically reported episodes of decompression sickness among 107 of 164 responding operators in 1966. The 1966 age and cumulative chamber-hour tables describe the same respondents. The follow-up draws from the 1958 radiography archive. Tables I and V give different totals above 20,000 ft, so the release preserves both values with their source locators. Heimbach et al. record 11 altitude DCS treatment referrals among 127 patients treated for various conditions, plus a separate network count of 80 USAF-treated cases. These counts remain on overlap hold with the Davis archive. [v1.70 observations](../data/chamber/v1.70/observations.csv) · [Overlap evidence](../data/chamber/v1.70/overlap.csv)

Katuntsev's 1996 author summary reports DCS symptoms in 931 of 1,778 experimental chamber ascents. The published phase counts, 784 at the primary altitude and 147 during additional decompression, reconcile to 931. The 562 early terminations due to intense symptoms are another margin within the same affected ascents. The release preserves the existing report identity and records the program total on overlap hold with the component trials. In 228 selected experiments, 174 had lower-limb pain and 212 had detectable VGE. The source reports that VGE preceded pain in 164 of the 174 affected experiments, with a printed percentage of 95%. The counts imply 94.25%, and both values are traceable. [v1.71 observations](../data/chamber/v1.71/observations.csv) · [Source revision and nested risk sets](../data/chamber/publication-review/retrievals-2026-11-20-katuntsev-program-reconciliation.json)

The diagnostic supplement also includes 32 selected symptomatic NASA exposures classified as no DCS. They remain in `literature_symptomatic_noncase` with their original selection criteria. [Diagnostic extraction and interpretation](chamber-diagnosis-supplement.md)

The Armstrong archive supplement adds two reports of one chamber series, including the original 309 DCS cases in 1,163 exposures on overlap hold. The paired release also includes the Doppler reconciliation and Russian repeated-exposure supplements. [Armstrong archive](chamber-armstrong-archive-supplement.md) · [Doppler reconciliation](chamber-vge-reconciliation-supplement.md) · [Repeated exposures](chamber-repeated-eva-supplement.md)

The JPRS translation adds five strata from Kazakova and Poleshchuk's 38 chamber tests and the 25 reported symptomatic onset rows. The original article and its English translation share one study ID. [JPRS translation and extraction](chamber-jprs-translation-supplement.md)

The USAFSAM manual links the ADRAC development profile inventory and archive counts to their source denominators. The workshop rates and added 18,000-ft staging case detail can be traced to the prior cohort records. [USAFSAM archive and ADRAC profile reconciliation](chamber-usafsam-archive-supplement.md)

The Brooks supplement adds two VGE thresholds linked to one 2,077-exposure clinical margin, three related counts from the loglogistic development sample, and the original 1999 ADRAC validation percentages. [Joint DCS and Doppler evidence](chamber-brooks-joint-supplement.md)

The Armstrong survival report links its 1,426-exposure archive to the 975-exposure journal subset. The review holds both publications under one study. The model database preserves the archive outcome and four source breakdowns, with explicit discrepancies in the censoring and bubble-grade totals. [Armstrong survival report supplement](chamber-kannan-report-supplement.md)

The 2001 Air Force proceedings add five published ADRAC estimates and their printed uncertainty margins. The three reports describe one validation cohort, with differing model predictions and a documented discrepancy for the 35,000-ft observed estimate. [ADRAC proceedings crosswalk](chamber-adrac-proceedings-supplement.md)

Berry’s Stockholm manuscript and journal article corroborate 48 reported reactors in 1956 and symptom percentages for the 125 hospitalized reactors in the earlier period. The outcome count is recorded once, with the historical case definition and missing 1956 denominator. [Berry chamber surveillance supplement](chamber-berry-training-supplement.md)

The Halbouty and Heisler original report and Berry and King’s follow-up now share one existing 1954 chamber case. The follow-up’s earlier self-reported symptom and the original’s first observed signs retain distinct timing fields. [1954 case chronology](chamber-halbouty-case-supplement.md)

NASA TM-100472 adds the 150 profiles from its historical ascent-rate compilation and links 19 of its cited reports to existing source IDs. The historical rates and denominator totals are available for reconciliation. The clinical benchmark excludes these overlapping entries. [Ascent-rate compilation](chamber-nasa-ascent-compilation.md)

The 1992 HDSD article adds 27 historical group summaries for citation and outcome reconciliation. Four groups match existing Motley training strata and the rest remain on overlap hold. [HDSD Table III intake](chamber-hdsd-compilation.md)

Five source outcome margins and six additional bibliography links extend the NASA ascent-rate intake. The supplement preserves the conflicting 9.5-psia validation denominators and two phase-specific Navy bends counts with unavailable denominators. [Ascent source reconciliation](chamber-ascent-source-reconciliation.md)

The historical full-text supplement records 84 repeated chamber runs from Williams et al. and reconciles repeated publications about Houston’s chamber attendants. The crossover rows retain unresolved cells, historical symptom grades and within-person linkage. [Williams and Houston source tables](chamber-historical-crossover-supplement.md)

Henry’s 1947 classification study adds 129 published percentages with explicit identification of calculated controls and nested selections. The 1946 Berkeley series remain linked for cohort-overlap review. [Henry preselection tables](chamber-preselection-supplement.md)

The 1945 Berkeley preoxygenation supplement preserves repeated-flight summaries and their outcome time origins. The verified source crosswalk links the 1945 reference values to the calculated 1947 controls. [Henry and Cook preoxygenation tables](chamber-preoxygen-supplement.md)

The June 1944 CAM minutes provide the 132/719 source-defined chokes finding and distinguish it from a narrative rate and radiographic score totals. Related reports stay on overlap hold pending exposure-level linkage. [Wartime CAM minutes](chamber-cam-minutes-supplement.md)

The wartime bulletin adds linked Canadian repeat-flight tables and neurological program summaries. Flight-level counts, repeated classifications and archive discrepancies retain their printed scope. [Canadian and neurological chamber evidence](chamber-cam-repeat-flights-supplement.md)

The multicenter supplement adds the preliminary Randolph Field interval counts and the Berkson repeat-flight tables from four sites. The records preserve source-defined descents, changing denominators, incompatible printed values and crosswalks to related reports. [Multicenter repeat-flight evidence](chamber-cam-multicenter-supplement.md)

The paired-chamber supplement adds the Ferris time tables, Ivy's narrative rates and the Canadian pilot retest. A report crosswalk locates the existing RAF 610-person series at Kew. [Paired chamber outcomes and archive references](chamber-cam-paired-supplement.md)

The Gray and Motley supplement links historical age and weight-to-height strata to the original sources. It traces the Maxwell denominators to one underlying cohort and preserves conflicting Pensacola counts from two editions. [Historical age and weight-to-height strata](chamber-gray-motley-strata-supplement.md)

One example of deduplication is the Ata and Karaca chamber report. All 125 full- or truncated-title search occurrences in v1.48 resolve to the same publication. The candidate queue preserves uncertain matches for adjudication. Use `review_identity_candidate` to inspect them and follow the agent rules when recording a decision on either computer. [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC8313775/) · [Agent rules](../AGENTS.md)
