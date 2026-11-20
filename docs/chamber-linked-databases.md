# Chamber databases for the review and DCS model

The two SQLite files can be queried independently. Each contains the same evidence release ID. The accompanying `release.json` identifies the exact bytes of both files. Version-controlled inputs are the shared editing surface on both computers.

| File | Start here | Unit |
| --- | --- | --- |
| `systematic-review.sqlite` | `review_record`, `review_publication_catalog`, `review_study_report`, `review_current_screening` | Retrieved occurrence, published report, study and reviewer decision |
| `systematic-review.sqlite` | `review_seed_role_cell`, `review_supplementary_role_cell`, `review_secondary_role_cell` | Original and secondary role-specific counts for eligibility assessment |
| `dcs-model.sqlite` | `development_counts`, `afrl_test`, `vge_interval`, `locked_external` | Frozen NASA DCS groups, separate AFRL test groups, Grade IV VGE intervals and external strata |
| `dcs-model.sqlite` | `historical_case_catalog`, `dcs_case`, `publication_observation_revision` | Selected historical case histories and source corrections |
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

The historical catalog covers 103 numbered NASA cases and five explicitly cross-linked published cases in this release. Additional case reports and aggregate outcomes remain in the original extraction tables. The fitting dataset contains 41 NASA groups with 124 DCS events in 885 exposures. A separate table contains 238 Grade IV VGE intervals. Clinical risk for an individual routine chamber trainee still requires linked clinical outcomes and validation in that population.

Ferris and Engel supply seven case-conditional margins for the previously catalogued Cincinnati and Halifax series. Their clinical chapter also corroborates one Berkeley case from the 1944 meeting minutes and preserves both reported times to postdescent worsening. [Neurological timing supplement](chamber-ferris-engel-neurological-supplement.md)

The 1946 Operation Everest diary supplies two dated staff cerebral bends reports. Eleven contextual entries retain the lock activity, staffing, recorded symptoms and resident follow-up. The study register links the investigator and diary reports to one experiment. [Operation Everest I supplement](chamber-operation-everest-i-supplement.md)

The 2026 AsMA familiarization case adds six source-reported milestones. The study register also links the EA-6 meeting abstract and original NASA slides to their shared cohort. [AsMA chamber case supplement](chamber-asma-chamber-case-supplement.md)

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
