# TinyDCS

TinyDCS is an aerospace medicine research project on altitude decompression sickness (DCS). It began with equations and software to estimate DCS probability from pressure, breathing-gas and activity histories. The project now also conducts a systematic review of symptomatic DCS in hypobaric chamber training.

| Research area | Question | Start here |
| --- | --- | --- |
| Systematic review and planned meta-analysis | How often does symptomatic DCS occur among staff and trainees during hypobaric chamber training, and how does risk compare within the same program? | [Review protocol](docs/chamber-publication-review.md) · [Search strategies and pilot results](docs/chamber-review-search.md) |
| Probability models and scenario software | Under a defined exposure history, how likely is symptomatic DCS or the Doppler detection of venous gas emboli (VGE) within a stated observation window? | [Equations and assumptions](docs/hypobaric-probability.md) · [Worked chamber examples](docs/hypobaric-outcomes.md) · [Accuracy audit](docs/accuracy-audit.md) |

The evidence database supports both lines of research. It links publications to their study populations, reported outcomes and denominators so researchers can verify each estimate and identify overlapping cohorts. The software is for research use only. Independent clinical validation remains a research objective.

## Systematic review of hypobaric chamber training

**Working title** · *Risk of Altitude Decompression Sickness Among Staff and Trainees in Hypobaric Chamber Training: A Systematic Review and Meta-analysis*

The review compares staff working inside the chamber with trainees in the same operational training program. The primary outcome is clinically diagnosed symptomatic DCS per person-exposure, including cases detected during training and within the source's post-return follow-up window. The review will report cases, evaluable exposures and risk per 1,000 person-exposures for each role, with within-program risk ratios where the denominators are compatible. Secondary outcomes include neurological or serious DCS as defined by each study and DCS first presenting after return. [Eligibility criteria](docs/chamber-publication-review.md#eligibility-for-the-role-comparison) · [Analysis plan](docs/chamber-publication-review.md#analysis-and-appraisal)

The workflow records database queries, retrieval dates and source locations for extracted counts. Two reviewers will screen reports independently and record their decisions. The decision to pool will account for differences in diagnostic definitions and surveillance windows, repeated attendance and cohort overlap across reports. [Review and appraisal methods](docs/chamber-publication-review.md#identification-and-review-decisions)

**The protocol is approved and the search strategies have been pilot tested.** The initial source audit documents six study periods across four programs with role-specific cases and exposure counts, plus three periods for further eligibility assessment. Formal retrieval awaits search-strategy approval. [Publication inventory](docs/chamber-publication-review.md#publication-inventory) · [Search strategies and pilot results](docs/chamber-review-search.md) · [Review status record](data/chamber/publication-review/prisma-flow.json)

## Evidence database

Build the two study databases with `python -m scripts.chamber_products --output-dir artifacts/chamber-products/v1.40-reconciled`. Use `systematic-review.sqlite` for screening and meta-analysis and `dcs-model.sqlite` for the chamber benchmark and historical case catalog. Both files share source identifiers and a verified release. [Build, query and link the two databases](docs/chamber-linked-databases.md) · [Agent intake rules](AGENTS.md)

The SQLite build includes the publication register and the observed-outcome benchmark. The register connects search records to reports and study cohorts, and tracks editorial checks, unresolved identity matches and reviewer decisions. The benchmark preserves each observation's population, counting unit and source locator. A person-exposure, a diagnosed case and a limb Doppler reading are distinct units. [Publication database schema](data/chamber/publication-review/schema.sql) · [Observed-outcome database dictionary](docs/chamber-benchmark.md)

The SharePoint library review adds 208 aggregate observations and 26 published VGE-positive subject records. Its source register also identifies textbook definitions, reprinted cohorts and conflicting denominators. [SharePoint extractions and reconciliation notes](docs/chamber-sharepoint-review.md)

For the Colombian Air Force chamber program, the official FAC registers are the primary sources for 2010–2020. They record **54 DCS events**, with **35 student events and 19 instructor events** identified under `POSICION`. The training workbook records **5,030 hypoxia and 1,715 rapid-decompression activities**. The annual view includes each role's case count. Estimating risk by role requires a roster covering all occupants and follow-up for each exposure. The workbooks contain no VGE scans. [FAC source reconciliation and annual counts](docs/chamber-fac-official.md)

The FAC flight-date analysis places the case series under the historical Bogotá schedule. In 2022 the program changed to one combined RD and 25,000-ft session per week with a one-flight-per-person limit. The protocol tables preserve both schedules and the altitude profile. [Instructor flight dates and the 2022 schedule change](docs/chamber-fac-official.md#instructor-flight-dates-and-the-2022-schedule-change)

The Rojas USAF case-control supplement adds occupation, tobacco and alcohol counts from the original tables. Its denominators are sampled cases and controls. [Rojas extraction and database build](docs/chamber-rojas-2015.md)

The six-PDF intake adds a self-reported U-2 flight history, new ADF and Shaw AFB case detail, NASA ground versus operational EVA summaries, and an FAA profile comparison. The source crosswalk records matching and alternate versions of observations. [Six-PDF extraction and database build](docs/chamber-six-pdfs.md)

The Zotero DCS collection adds NASA extravehicular activity (EVA) follow-up, symptom-resolution data, prospective chamber validation estimates, and AC-130 case timelines. Its attachment register links exact copies, alternate PDFs, and repeated cohorts to their prior database sources. [Zotero DCS collection and build](docs/chamber-zotero-dcs.md)

### Build and inspect the data

Run from the repository root. The legacy combined publication-review build includes the benchmark, releases through v1.40, the SharePoint intake, the official Colombian aggregates and the Rojas, six-PDF and Zotero DCS supplements. It works offline. The evaluation command reproduces the frozen benchmark from its original inputs.

```sh
python -m scripts.build_chamber_database --publication-review
python -m scripts.build_chamber_database --fac-official
python -m scripts.build_chamber_database
python -m scripts.evaluate_chamber_benchmark
```

Open `artifacts/chamber-publication-review/observed.sqlite` for the publication register and combined public outcome tables. The aggregate-only FAC build remains available at `artifacts/chamber-fac-official/observed.sqlite`. Use `fac_official_chamber_year` for FAC case and activity counts and `fac_celis_annual_reconciliation` to compare the thesis. The original workbooks also support a local build with one row per case. For literature observations, query the unit and locator alongside the values. [FAC build and queries](docs/chamber-fac-official.md#build-and-query) · [Literature deduplication rules](docs/chamber-sharepoint-review.md#deduplicated-database)

```sql
-- Inspect the original role-specific counts used to develop the review.
SELECT study_id, chamber_role, cases, exposures, locator
FROM review_seed_role_cell
ORDER BY study_id, chamber_role, source_cell;

-- Verify the counting unit and source locator for an extracted outcome.
SELECT stratum, endpoint, events, denominator, denominator_unit,
       reported_percent, analysis_role, locator
FROM sharepoint_deduplicated_observation
WHERE source_id = 'balldin04' AND stratum = 'cns_subset'
ORDER BY endpoint;
```

## Probability models and validation

TinyDCS implements published reference equations, fits models to observed chamber outcomes and evaluates surrogates of historical calculator outputs. Each probability has a defined endpoint, observation window and supported exposure range. The software also supports analysis of aviation and EVA scenarios. [Modeling methods](docs/accuracy-methods.md) · [Scientific sources](docs/accuracy-sources.md) · [Architecture](docs/accuracy-architecture.md)

### Fitting and evaluation with observed outcomes

| Prediction target | Available evidence | Data needed for further fitting |
| --- | --- | --- |
| Symptomatic DCS by a specified time | The current group fit uses 124 cases in 885 evaluable exposures from 41 NASA tests. A separate AFRL table contains 340 cases in 708 exposures. | For a grouped binomial fit, use exact events and evaluable exposures with comparable clinical definitions and windows. Individual time-to-DCS modeling also needs symptom onset or last documented event-free time for each exposure. |
| First detection of any VGE | Published NASA reference equations, monitored group counts and selected first-detection times are available. The exercise-order report gives 13 detections among 27 subjects in each group. | Obtain the last negative and first positive scan, or the last negative scan at end of monitoring. Record ultrasound method, scale, observation schedule, posture and provocation. |
| First Grade IV VGE | The interval-censored study used 178 records for fitting and 60 for held-out evaluation. Across all 238 records, 69 contain a detection interval and 169 are right-censored. | Preserve the original grading scale and the first qualifying grade interval. A maximum grade and a time to the first bubble identify different observations. |
| Clinical subtype, severity and joint DCS/VGE outcomes | Some reports supply subtype counts, case timelines or joint clinical and ultrasound outcomes. One NASA series enumerates all four DCS/VGE combinations. | For subtype incidence, collect a consistent case definition and all eligible exposures. For joint models, both endpoints need ascertainment in the same exposures. Case-only series can describe presentation and timing. |

1. **Capture the exposure.** Link study, site, protocol and revision. Preserve cohort, person and session identifiers where the source supplies them. Record starting pressure, prior diving or altitude, oxygen and air breaks, ascent, body-experienced pressure, time at plateau, workload, posture and return. Retain the measured or assigned basis and the time each predictor became available.
2. **Capture onset and follow-up.** Record adjudication, onset bounds, follow-up after return and event-free coverage for DCS. Link timestamped Doppler scans to that exposure and retain the original grades. Store unmonitored, indeterminate and lost-to-follow-up observations explicitly. The FAC/CEMAE registry supports prospective exposure histories and adjudicated follow-up. [Registry schema and commands](docs/chamber-benchmark.md#prospective-faccemae-registry)
3. **Freeze the eligible cohorts before fitting.** Reconcile duplicate publications, repeat subjects, overlapping totals, incompatible grading scales and conflicting counts. Select one risk set per endpoint and horizon. Keep connected people, protocols and publications together across splits. Reserve independent sites or cohorts for external evaluation. [Frozen design](data/chamber/v1/design.json) · [Library overlap register](data/chamber/sharepoint-2026-11-19/overlap.csv)
4. **Fit and evaluate at the available level of detail.** Compare grouped incidence with a training-prevalence baseline. Fit time-to-event models where onset and censoring are observed, using interval likelihoods for intermittently sampled VGE. Limit pre-exposure predictors to information available when the prediction is made. Evaluate held-out calibration, observed versus expected counts, Brier score and log loss at supported horizons, or interval likelihood for censored records. Publish the data cut, coefficients, uncertainty and supported range with each fit.

The benchmark includes two grouped model comparisons and a locked set of four operational aviation cohorts for external evaluation. Their five strata lack matched pressure histories and group mean arrival tissue ratios. External calibration of the current group DCS model remains open. Short aviation profiles need linked exposure histories, adjudicated post-return surveillance and serial Doppler observations where VGE is a target. [Fitted chamber studies](docs/hypobaric-outcomes.md) · [Benchmark and external cohort assessment](docs/chamber-benchmark.md)

### Scenario software

**Chamber research outcomes** evaluates symptomatic DCS, any VGE and Grade IV VGE from one pressure and oxygen history. It also compares an eligible scenario with a group DCS model fitted to 124 cases in 885 evaluable chamber exposures and a Grade IV VGE model fitted to monitored onset intervals. The browser and both repositories' Python services use the same reviewed coefficients and data digests. [Run a worked example and read the study results](docs/hypobaric-outcomes.md)

**Aviation pressure history** accepts starting pressure, preoxygenation, changes of breathing gas, activity, ascent, time at altitude and return. The backend derives tissue nitrogen at arrival and checks the protocol, population and outcome window before displaying a published reference probability. The clinical outcome field for complete short aviation profiles is unavailable. [API, examples and migration](docs/aviation-profile.md)

| Surface | Supported calculation | Important limit |
|---|---|---|
| Aviation history | Dry nitrogen trajectory, arrival and exit state, maximum tissue ratio, integrated supersaturation and applicable chamber reference equations | An identified initial state, gas history and source protocol govern each output |
| Workbook experiment API | Fitted pipeline, calibration and evaluation from the companion ML repository, loaded by SHA-256 | Agreement with workbook labels of unverified lineage |
| Browser ADRAC baseline | Train-only re-fit of a log-logistic model to the audited grid | Not original ADRAC coefficients, not the trained ML surrogate; no interval |
| Python LightGBM surrogate | Eleven-feature emulation of model-valued grid targets, calibrated mixture intervals and input-support flags | Synthetic exercise augmentation; no clinical outcomes or independently measured continuous VO2 |
| NASA RM / NM | Source Eq. 6 nitrogen kinetics and Eq. 14 / 15 reference endpoint | Four-hour, 4.3-psia oxygen, adynamic source conditions; cohort transportability unestablished |
| EVA dashboard / API | Sequential PB and EVA compartment calculations; exact pressure/workload schedules; raw indicators and consumables arithmetic | EVA kinetics are an exploratory extension, not a validated risk-time curve |
| 3RUT-MBe1 | Experimental source-equation implementation and pressure-profile exploration | Quantitative output disabled pending gain/volume and benchmark reconciliation |

The EVA dashboard displays the compartment trajectory, workload, consumables and configured mission conditions. Its compact scenario lacks the phase-specific data required to qualify a NASA reference probability. The full aviation editor checks those inputs and gives the applicable reference endpoint.

PB exercise is separate from EVA workload. Duration edits in the UI explicitly rescale schedule durations; the calculation API instead rejects inconsistent schedules. Oxygen reserve is separate from the PLSS duration margin.

Mission-rule classifications are configurable planning conventions, not measured likelihoods. Configured stop conditions (symptoms, radiation storm or negative PLSS margin) remain visible even when the DCS model abstains.

### Agreement with the ADRAC-derived model grid

Primary cleaning retains 14,683 unambiguous cells from 16,295 raw rows. The project preserves suspected scaling errors and disagreeing duplicate cells in a raw ledger for sensitivity analysis. [ADRAC and workbook provenance](docs/chamber-source-search-2026-11-19.md)

The frozen split has 9,544 training, 2,937 calibration and 2,202 test cells (seed 42). No baseline is fitted on calibration or test rows.

| Evaluation | Surrogate MAE, probability units | Empirical interval coverage |
|---|---:|---:|
| Primary random holdout | 0.021932 (2.1932 percentage points) | 2095/2202 = 95.14% |
| Profile-grouped holdout | 0.026344 | 97.21% |

Nominal coverage is 95%. These intervals quantify agreement with the model-derived targets. Neighboring grid cells are dependent, Wilson intervals are descriptive, and finite-sample conformal guarantees require exchangeability.

The global ADRAC-form baseline MAE is 0.084972; the stronger altitude-stratified baseline is 0.033773. An ordinal-exercise ablation outperforms synthetic-VO2 augmentation, so the grid does not establish added predictive value from continuously measured exercise.

See [tracked evidence](docs/evidence/accuracy-v3.json) for exact values, stronger baselines, held-out altitude results, cleaning sensitivity, export parity, environment and artifact hashes. A duration sweep found no decreases in 25,875 adjacent comparisons across 1,125 constant-workload profiles; this is not a proof for arbitrary changing workloads.

## Run locally

The software is at version 0.9.0. Verification used Python 3.12 and Node 22.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[dev,edge]'
.venv/bin/pytest -q
.venv/bin/uvicorn tinydcs.api:app --host 127.0.0.1 --port 8180
```

In another terminal:

```bash
cd frontend
npm ci
npm test
npm run build
npm run dev -- --host 127.0.0.1
```

The browser uses `http://127.0.0.1:8180/api/v2` by default; override `VITE_TINYDCS_API_URL` if required. A transport failure allows the parity-tested offline calculation. Rejected inputs, incompatible API versions and server calculation errors do not silently fall back. Results are keyed to all scenario, mission-rule and telemetry inputs to prevent stale displays.

## EVA API and exports

- `POST /api/v2/eva/simulate`: validated scenario, rule profile, optional timestamped telemetry and explicit replay evaluation time.
- `POST /api/v2/eva/report`: recomputes from inputs and returns JSON, HTML and PDF. Client-supplied displayed results are ignored.
- `GET /api/v2/eva/mission-rules/{profile}` and `GET /api/v2/eva/model-metadata`: assumptions and configuration.
- Legacy v1 routes are deprecated aliases returning the version-2 nullable contract; clients must migrate.

JSON reports retain actual inputs, rules, telemetry, evaluation time and a server input fingerprint. Offline JSON exports recompute with the same context and identify the browser reference engine. PDF/HTML exports require the API.

Telemetry must have recognized units, a finite timestamp, acceptable confidence and freshness. Habitat and suit pressure are distinct. Accelerometer magnitude, activity counts, HR/HRV and skin temperature remain indicators; there is no unvalidated acceleration-to-VO2 or temperature-to-cooling conversion. The UI replay is synthetic, not hardware validation.

## Reproduce artifacts

Follow [the runbook](docs/runbook.md). Generated models, ONNX graphs, figures, ledgers and detailed metrics live in the ignored `artifacts/accuracy-v3/` directory. Reproducible code, bundled browser baseline/held-out data and compact evidence with SHA-256 hashes are versioned. Legacy artifacts and manuscript claims are retained as historical material, not current evidence.

Personalization uses a Bernoulli likelihood for actual binary outcomes and a Normal susceptibility prior. Its uncertainty is a posterior credible interval, not a preserved conformal coverage guarantee.

Ongoing modeling work includes reconciling 3RUT, collecting independent outcomes and telemetry for validation, testing hardware deployment and reviewing mission rules with responsible authorities. [Repository terms](LICENSE)
