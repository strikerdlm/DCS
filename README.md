# TinyDCS

Research software for decompression-model calculations, model-grid emulation and EVA scenario exploration. Version 0.7.0.

Not clinically validated, flight-certified, or suitable for operational clearance. Software agreement with a published equation or a model-derived grid is not evidence of accuracy in people.

[Reproduction runbook](docs/runbook.md) · [Accuracy audit](docs/accuracy-audit.md) · [Methods](docs/accuracy-methods.md) · [Scientific sources](docs/accuracy-sources.md) · [Architecture](docs/accuracy-architecture.md)

## What is available

| Surface | Supported calculation | Important limit |
|---|---|---|
| Browser ADRAC baseline | Train-only re-fit of a log-logistic model to the audited grid | Not original ADRAC coefficients, not the trained ML surrogate; no interval |
| Python LightGBM surrogate | Eleven-feature emulation of model-valued grid targets, calibrated mixture intervals and input-support flags | Synthetic exercise augmentation; no clinical outcomes or independently measured continuous VO2 |
| NASA RM / NM | Source Eq. 6 nitrogen kinetics and Eq. 14 / 15 reference endpoint | Four-hour, 4.3-psia oxygen, adynamic source conditions; cohort transportability unestablished |
| EVA dashboard / API | Sequential PB and EVA compartment calculations; exact pressure/workload schedules; raw indicators and consumables arithmetic | EVA kinetics are an exploratory extension, not a validated risk-time curve |
| 3RUT-MBe1 | Experimental source-equation implementation and pressure-profile exploration | Quantitative output disabled pending gain/volume and benchmark reconciliation |

The EVA dashboard preserves the model explorer layout. It shows unsupported probabilities, risk integrals, time-risk curves, confidence bands and non-DCS event probabilities as unavailable, never zero or a green risk category. A source-reference endpoint appears only when its assumptions are explicitly declared and its pressure/gas/duration conditions match.

PB exercise is separate from EVA workload. Duration edits in the UI explicitly rescale schedule durations; the calculation API instead rejects inconsistent schedules. Oxygen reserve is separate from the PLSS duration margin.

Mission-rule classifications are configurable planning conventions, not measured likelihoods. Configured stop conditions (symptoms, radiation storm or negative PLSS margin) remain visible even when the DCS model abstains.

## Current model-agreement evidence

Primary cleaning retains 14,683 unambiguous cells from 16,295 raw rows. Suspected scaling errors and all disagreeing duplicate cells are excluded from the primary analysis; their raw values and alternative policies are retained for sensitivity analysis.

The frozen split has 9,544 training, 2,937 calibration and 2,202 test cells (seed 42). No baseline is fitted on calibration or test rows.

| Evaluation | Surrogate MAE, probability units | Empirical interval coverage |
|---|---:|---:|
| Primary random holdout | 0.021932 (2.1932 percentage points) | 2095/2202 = 95.14% |
| Profile-grouped holdout | 0.026344 | 97.21% |

Nominal coverage is 95%. These are model-agreement intervals, not clinical confidence intervals. Neighboring grid cells are dependent; Wilson intervals are descriptive, and finite-sample conformal guarantees require exchangeability.

The global ADRAC-form baseline MAE is 0.084972; the stronger altitude-stratified baseline is 0.033773. An ordinal-exercise ablation outperforms synthetic-VO2 augmentation, so the grid does not establish added predictive value from continuously measured exercise.

See [tracked evidence](docs/evidence/accuracy-v3.json) for exact values, stronger baselines, held-out altitude results, cleaning sensitivity, export parity, environment and artifact hashes. A duration sweep found no decreases in 25,875 adjacent comparisons across 1,125 constant-workload profiles; this is not a proof for arbitrary changing workloads.

## Run locally

Python 3.12 and Node 22 were used for the correction checks.

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

Remaining research work: reconcile 3RUT, collect independent outcome/telemetry validation, test hardware deployment and review mission rules with responsible authorities. See [LICENSE](LICENSE) for repository terms.
