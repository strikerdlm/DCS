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
python -m scripts.chamber_products --output-dir artifacts/chamber-products/v1.40-reconciled
python -m scripts.evaluate_chamber_benchmark --database artifacts/chamber-products/v1.40-reconciled/dcs-model.sqlite --output artifacts/chamber-products/evaluation-v1.40.json
python -m pytest -q tests/test_chamber_products.py tests/test_publication_review.py tests/test_review_identity.py tests/test_observed_benchmark.py
```

The benchmark reads only the model file, its adjacent checksum manifest and the frozen comparators in the checkout. To trace a case back to a paper, open the pair read-only. The following prints each enriched case, the source title and both extraction locators.

```python
from scripts.chamber_products import connect_pair

with connect_pair("artifacts/chamber-products/v1.40-reconciled") as db:
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

The historical catalog covers 103 numbered NASA cases and two explicitly cross-linked published cases in this release. Additional case reports and aggregate outcomes remain in the original extraction tables. The fitting dataset contains 41 NASA groups with 124 DCS events in 885 exposures. A separate table contains 238 Grade IV VGE intervals. Clinical risk for an individual routine chamber trainee still requires linked clinical outcomes and validation in that population.

The diagnostic supplement also includes 32 selected symptomatic NASA exposures classified as no DCS. They remain in `literature_symptomatic_noncase` with their original selection criteria. [Diagnostic extraction and interpretation](chamber-diagnosis-supplement.md)

One example of deduplication is the Ata and Karaca chamber report. All 120 full- or truncated-title search occurrences in this release resolve to the same publication. The candidate queue preserves uncertain matches for adjudication. Use `review_identity_candidate` to inspect them and follow the agent rules when recording a decision on either computer. [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC8313775/) · [Agent rules](../AGENTS.md)
