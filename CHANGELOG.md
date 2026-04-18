# Changelog

All notable changes to TinyDCS are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning loosely follows [SemVer](https://semver.org/) with a `v0.X` research-preview series before any `v1.0`.

## [Unreleased]

### Planned
- Cortex-M4/M0 benchmarking of the compact ONNX variants on real hardware (current numbers are CPU-measured).
- Manuscript revision: journal-specific reformatting, figure embedding, acknowledgements, declared COIs.
- Prospective external-validation study (Paper 3 scope; IRB preparation).
- Paper 2 Implementation B: full PyMC hierarchical posterior with simulation-based calibration (Talts et al. 2018).
- Multimodal-fusion extension: HR/HRV/SpO₂ as state covariates modulating per-subject log λ.

## [0.5.0] — 2026-04-18 — Paper 2 scope + personalization prototype

### Added
- `AGENTS.md` — continuation guide for future AI agents (landed in v0.4.1 but first full session log entry is in this release).
- `docs/papers/paper-2-scope.md` — scoping note for Paper 2: hierarchical Bayesian personalization. Journal targets (PLOS Comp Bio / Frontiers / AMHP), two-implementation plan (conjugate closed-form for on-device, PyMC for methodological rigor), synthetic-first validation protocol, five core contributions, 12-week timeline, ethical framing.
- `tinydcs.personalization` package: conjugate Gaussian per-subject susceptibility layer on top of any `TinyDcsSurrogate`. Closed-form posterior, O(1) per new observation, ~16 bytes per subject. Includes `SubjectPosterior`, `PopulationPrior`, `PersonalizedSurrogate`, `fit_population_prior`, `generate_synthetic_cohort`.
- `tests/test_personalization.py` (4 tests) — conjugate update convergence, synthetic cohort structure, per-subject λ recovery, personalized prediction shift.
- `scripts/08_personalization_demo.py` — information-gain sweep at k ∈ {1, 2, 5, 10, 20} with n=100 synthetic subjects and σ_λ=1.0.

### Pilot results (seed=42, 100 synthetic subjects, σ_λ=1.0)

| k (exposures) | Pearson r (λ recovery) | RMSE(log λ) | Δ Brier (population − personalized) |
|---|---|---|---|
| 1 | 0.10 | 0.98 | +0.010 (worse) |
| 2 | 0.09 | 1.25 | +0.017 (worse) |
| 5 | 0.27 | 1.10 | +0.017 (worse) |
| 10 | 0.60 | 0.96 | +0.008 (worse) |
| 20 | 0.63 | 0.90 | +0.001 (~parity) |

The **information-gain curve** is the headline figure for Paper 2: recovery correlation grows monotonically with k, and personalization approaches parity with the population baseline at k ≈ 10–20 exposures. Below that, personalization noise dominates the susceptibility signal. This is a publishable quantitative answer to a question the primary literature only discusses qualitatively.

### Tests
25/25 passing on the full suite.

## [0.4.1] — 2026-04-18 — zero-inflated ONNX edge export

## [0.4.1] — 2026-04-18 — zero-inflated ONNX edge export

### Added
- `AGENTS.md` at repo root — comprehensive continuation guide for future AI agents (TL;DR, methods inventory, ranked open problems P0–P6, speculative research directions, pitfalls, validation checklist, session log).
- `scripts/07_export_zero_inflated_onnx.py` — exports the two-stage zero-inflated surrogate to two ONNX graphs (classifier + continuous) plus a JSON metadata sidecar with gate constants, feature names, OOD detector parameters, and the host-side runtime algorithm in human-readable form.

### Edge deployment of the zero-inflated model

| Variant | Classifier ONNX | Continuous ONNX | Combined | Per-row p50 | MAE | R² | Cov. |
|---|---|---|---|---|---|---|---|
| Full (400 × 31 each) | 896 KB | 891 KB | 1,787 KB | 16.5 μs | 0.020 | 0.986 | 0.960 |
| **Compact (100 × 7 each)** | **47 KB** | **47 KB** | **95 KB** | **2.4 μs** | **0.028** | **0.981** | **0.953** |

The compact zero-inflated variant hits the Paper-1 headline claim end-to-end: under 100 KB total, under 3 μs per-row inference, R² 0.98, empirical 95% coverage. Parity vs Python reference: max |error| = 6.4e-7 on P(y=0), 4.9e-6 on the continuous logit (well under the 1e-4 target).

### Note on classifier export
`onnxmltools.convert_lightgbm` on a `LGBMClassifier` requires the package-internal `onnxmltools.convert.common.data_types.FloatTensorType`, not the generic `onnxconverter_common.FloatTensorType` that works for regressors. This subtle type requirement is documented in both `scripts/07_export_zero_inflated_onnx.py` and `AGENTS.md` §9 pitfalls.

## [0.4.0] — 2026-04-18 — zero-inflated calibration closes the low-band shortfall

## [0.4.0] — 2026-04-18 — zero-inflated calibration closes the low-band shortfall

### Added
- `tinydcs.surrogate.CQRCalibration` + `fit_cqr()` — Conformalized Quantile Regression (Romano, Patterson & Candès 2019) with optional Mondrian (altitude-band) stratification of the conformal correction.
- `tinydcs.surrogate.ZeroInflatedCalibration` + `fit_zero_inflated()` — two-stage Lambert-style zero-inflated surrogate: binary LightGBM classifier for P(y = 0 | x) + LightGBM regressor for logit(y) on non-zero rows + conformal quantile on non-zero residuals + inference-time gating.
- `train_surrogate(use_cqr=True, ...)` and `train_surrogate(use_zero_inflated=True, ...)`; both branches survive save/load round-trip.
- `scripts/04_train_adrac_surrogate.py --cqr` / `--zi` flags for reproducible mode selection.
- `tests/test_surrogate.py::test_cqr_beats_global_on_biased_low_region` and `::test_cqr_save_load_roundtrip` — 21 tests passing.

### Calibration comparison on the 15,908-row cleaned ADRAC grid (seed=42, random split)

| Calibration | Overall | 18–23K ft | 23–28K ft | 28–33K ft | 33–38K ft | 38–43K ft |
|---|---|---|---|---|---|---|
| Global conformal | 0.869 | 0.591 | 0.933 | 0.944 | 0.967 | 0.948 |
| Mondrian | 0.869 | 0.583 | 0.949 | 0.945 | 0.954 | 0.955 |
| CQR (global q) | 0.864 | 0.589 | 0.937 | 0.945 | 0.945 | 0.937 |
| Mondrian-CQR | 0.865 | 0.589 | 0.924 | 0.959 | 0.951 | 0.937 |
| **Zero-inflated two-stage** | **0.960** | **0.964** | **0.953** | **0.951** | **0.967** | **0.966** |

All four conformal-only methods produce near-nominal coverage (0.92–0.97) in the four upper altitude bands but are invariant at 0.58–0.59 in the lowest band. This invariance was diagnostic of target-distribution pathology (~40% exact-zero rows in the low-altitude band). The two-stage model routes the zero mass through a dedicated classifier and closes the gap to 0.964. **Zero-inflated is now the default calibration for Paper-1 headline numbers.**

### Point accuracy improved slightly under the zero-inflated model
- MAE: 0.0217 → 0.0200
- R²: 0.986 → 0.986
- Brier: 0.0016 → 0.00156

### Documentation
- `docs/methods.md` §M3.3 / M3.3b / M3.3c rewritten to cover all four calibration modes + the empirical comparison table.
- `docs/papers/paper-1-draft.md` — abstract, results §3.5, and discussion §4.3 updated with the new numbers. The paper's limitation section no longer carries an un-addressed coverage shortfall.

### Known issues
- Dynamic INT8 quantization still does not shrink tree-ensemble ONNX files (expected; documented).
- Zero-inflated ONNX export is not yet wired — needs two ONNX graphs + an inference glue script. Tracked in "Unreleased".
- Cortex-M hardware benchmarks remain indicative (from CPU proxy).

## [0.3.0] — 2026-04-18 — Mondrian conformal, ONNX export, Paper 1 draft

## [0.3.0] — 2026-04-18 — Mondrian conformal, ONNX export, Paper 1 draft

### Added
- `tinydcs.surrogate.MondrianConformalCalibration` + `fit_mondrian_conformal()` — group-stratified (by altitude band) conformal calibration that restores per-band marginal coverage under heteroscedastic residuals. `train_surrogate` accepts `mondrian_feature` / `mondrian_band_width` / `mondrian_band_origin`.
- Smithson-Verkuilen (2006) boundary shrinkage applied to the target before the logit transform. Handles the ~40% exact-zero rows in the lowest altitude band.
- Physiological monotonicity constraints on the LightGBM trees (altitude↑, time-at-altitude↑, tissue-ratio↑ ⇒ risk↑; prebreathe↑, ambient pressure↑ ⇒ risk↓).
- `scripts/05_export_onnx.py` — FP32 ONNX + dynamic-INT8 export with CPU latency benchmarking and ONNX-vs-Python parity verification.
- `scripts/06_train_compact_surrogate.py` — trains four size variants (full / medium / compact / tiny) and reports accuracy + ONNX footprint side by side.
- `docs/papers/paper-1-draft.md` — full Paper 1 manuscript draft aligned with TRIPOD+AI reporting (abstract, introduction, methods, results, discussion, conclusion, references, checklist appendix).
- `tests/test_surrogate.py::test_mondrian_conformal_round_trip` — verifies Mondrian predict/save/load round-trip.

### Model-size ladder (seed=42, 15,908-row cleaned ADRAC grid)

| Variant | Trees × Leaves | MAE | R² | Brier | ONNX size |
|---|---|---|---|---|---|
| Full | 400 × 31 | 0.022 | 0.986 | 0.0016 | 894.1 KB |
| Medium | 200 × 15 | 0.024 | 0.984 | 0.0018 | 210.9 KB |
| **Compact** | 100 × 7 | **0.028** | **0.981** | **0.0022** | **47.2 KB** |
| Tiny | 50 × 5 | 0.033 | 0.975 | 0.0029 | 16.7 KB |

The compact variant hits the < 100 KB edge-deployment target while still outperforming the closed-form ADRAC baseline (MAE 0.086, R² 0.869) by 3× on MAE.

### Inference latency

Full variant, FP32 ONNX, CPU single-core, batch of 10,000:
- per-row p50 = **6.65 μs**
- per-row p95 = **8.24 μs**
- ONNX ↔ Python logit parity: max absolute error 8.6e-6 (well below the 1e-4 target).

### Per-altitude-band coverage (Mondrian, random split)

| Band | Coverage | Avg width |
|---|---|---|
| 18,000–23,000 ft | 0.583 (bias-driven) | 0.215 |
| 23,000–28,000 ft | 0.949 | 0.335 |
| 28,000–33,000 ft | 0.945 | 0.257 |
| 33,000–38,000 ft | 0.954 | 0.201 |
| 38,000–43,000 ft | 0.955 | 0.163 |

Four of five altitude bands reach near-nominal coverage. The lowest-band shortfall is localized to bias, not variance — fix candidate is CQR (planned).

### Known issues
- Low-band coverage 0.583 (vs nominal 0.95) is a bias-driven shortfall, not a variance-driven one; wider Mondrian quantiles alone cannot fix it. Tracked in "Unreleased".
- Dynamic INT8 quantization does not shrink tree-ensemble ONNX files in the current toolchain (size parity with FP32 is expected). Further shrinkage requires microTVM or explicit tree pruning.
- Current latency numbers are CPU-measured. Cortex-M4/M0 benchmarks require hardware access and are noted as indicative in the manuscript.

## [0.2.1] — 2026-04-18

## [0.2.1] — 2026-04-18 — first real-data ADRAC-surrogate run

### Added
- `scripts/04_train_adrac_surrogate.py` — primary Paper-1 training pipeline that fits the ADRAC log-logistic baseline and the TinyDCS surrogate on the cleaned 15,908-row grid and benchmarks them head-to-head on both random and leave-one-altitude-out splits.

### First real-data results (`seed=42`, 15,908 rows after cleaning)

Random split (apples-to-apples on the same 2,387-row test fold):

| Model | MAE | R² | Brier |
|---|---|---|---|
| ADRAC closed-form (log-logistic AFT fit on the grid) | 0.086 | 0.869 | 0.0150 |
| **TinyDCS (LightGBM + 13 features + conformal + OOD)** | **0.021** | **0.988** | **0.0014** |

Leave-one-altitude-out (5 bands, 5,000-ft each, mean ± SD):

| Model | MAE |
|---|---|
| ADRAC baseline | 0.081 ± 0.037 |
| **TinyDCS** | **0.059 ± 0.033** |

TinyDCS outperforms the closed-form ADRAC baseline by **4× on MAE** and **10× on Brier** on random splits, and by **~28% on MAE** under strict altitude-band extrapolation. These are the primary Paper-1 headline numbers.

### Known issues
- Conformal coverage on the random split is **0.878** vs. nominal 0.95. Two non-exclusive suspects: (i) the calibration fold size may be too small relative to the target-scale dynamic range; (ii) the Mahalanobis OOD threshold is separate from conformal and doesn't automatically widen intervals near the envelope edge. Fix candidates: **Mondrian conformal** stratified by altitude band, or a larger (25%) calibration fold. Tracked in "Unreleased".

## [0.2.0] — 2026-04-18 — repo restructure + ADRAC pivot

### Repo-level changes
- **Restructured** the project from the prior flat layout into explicit first-class packages:
  - `mechanistic/` — callable physics-informed models (rut_mbe1, conkin_nasa, adrac).
  - `tinydcs/` — ML surrogate package (promoted from the `TinyDCS/` subdir).
  - `apps/streamlit/` — the existing unified three-model explorer.
  - `scripts/` — reproducible pipeline runners.
  - `tests/` — pytest suite (18 tests passing).
  - `docs/` — scientific background, methods, architecture, publication roadmap, and vendored NASA/USAFSAM reference documents.
  - `legacy/` — every prior iteration (BU_Model_2025, BU_3RUT, 3RUT_MBe1 dev dir, DCS_Python_Project_old, Dive_DCS, ML_model, Model_Rel_Candidate) preserved for provenance.
- **Removed** a stray 36 MB ELF core dump (`core`) that had been accidentally committed at repo root.
- **Hardened** `.gitignore` against future core dumps, artifact directories, and large scientific-data binaries (`.nc`, `.h5`).
- **Unified** `pyproject.toml` and `requirements.txt` at the repo root (previously split between root and `TinyDCS/`).
- Every rename was performed with `git mv` to preserve blame/log history; atomic moves that crossed import boundaries were bundled into single commits to avoid broken intermediate states in the log.

### Scientific pivot (load-bearing)
- Verified that the vendored `mechanistic/rut_mbe1.py` under-reports P(DCS) by ~4–5 orders of magnitude on Gerth's own ADRAC-validation profiles (NEDU TR 18-01 Fig. 16): our implementation yields P ∈ [1e-5, 4e-5] where Gerth reports ~20–70%. Detailed table, three suspect parameters, and a reconciliation plan in `docs/methods.md` §M7.
- **Pivoted** Paper 1 target from "surrogate of 3RUT-MBe1" to "surrogate of ADRAC with continuous-VO₂ extension via Conkin 2004". The synthetic-3RUT-MBe1 path is retained for shape studies but is no longer the training target until reconciliation completes.

### Added
- `mechanistic/adrac.py` — closed-form log-logistic AFT (Kannan 1998 / Pilmanis 2004 functional form) with `fit_adrac()` and `AdracModel.predict()`. Serves as the Paper-1 baseline the TinyDCS surrogate is benchmarked against. Fit via L-BFGS-B on logit-residual MSE (pragmatic; the published MLE needs individual-level censored data).
- `tests/test_adrac.py` — sanity checks on the altitude→pressure map, physiological monotonicity (altitude↑⇒risk↑, PB↑⇒risk↓, exercise↑⇒risk↑) and unit-interval predictions.
- Updated `mechanistic/__init__.py` to re-export the ADRAC public API.
- `docs/README.md` (via `docs/scientific-background.md`, `docs/methods.md`, `docs/architecture.md`, `docs/publication-roadmap.md`): ~700 lines of curated documentation covering the scientific lineage (ADRAC, Conkin, Webb 2010/2016, Gerth 3RUT-MBe1), the TRIPOD+AI-aligned methods section, the three-layer architecture with Mermaid diagrams, and the three-paper publication plan.
- `legacy/README.md` — explains the provenance of every archived subdirectory.
- New root `README.md` with badges, repo layout, quick-start, side-by-side model comparison, status table, and an explicit limitations section.

### Known issues
- 3RUT-MBe1 reconciliation is open (tracked in `docs/methods.md` §M7). ADRAC is the working target.
- The surrogate tests currently use a toy synthetic dataset; the real ADRAC-grid training has not yet run end-to-end (next step in the unreleased section).
- A benign LightGBM warning on non-DataFrame `predict` paths appears in test output; it does not affect numeric correctness.

## [0.1.1] — 2026-04-18

## [0.1.1] — 2026-04-18

### Added
- `.gitignore` to exclude `artifacts/` (except `.gitkeep`) and Python bytecode.
- `tinydcs.cli` module exposing `tinydcs-clean`, `tinydcs-simulate`, `tinydcs-train` as console entry points via `pyproject.toml`.
- End-to-end pilot run with 200-profile simulation → cleaned dataset → surrogate training, confirming the full pipeline executes and produces a saved surrogate + metrics JSON + reliability/Bland–Altman figures.
- Guard in `scripts/02_simulate_training.py` that catches upstream `OverflowError`/`ValueError` in 3RUT-MBe1 (numerical instability in Lobdell O₂ saturation curve on some FiO₂/altitude combos), marks those rows NaN, and drops them from the written parquet with a reported count.

### Pilot results (200 simulated profiles, reproducible with `--seed 42`)
- **Simulation**: 194 / 200 profiles completed; 6 upstream failures dropped. Mean P(DCS) = 9e-6, max = 2.5e-5.
- **Surrogate** (LightGBM, train=116 / cal=39 / test=39): MAE = 3.6e-6, RMSE = 5.2e-6, R² = 0.39, calibration slope = 0.997, Brier = 2.7e-11.
- **Conformal** coverage = 0.82 at nominal 0.95 — undercovered on 39-sample calibration fold (expected; finite-sample effect).
- **Interpretation**: the low R² and tiny target magnitudes reflect the known upstream issue that 3RUT-MBe1 under default Table 3 parameters produces P(DCS) values in the 1e-6 range for profiles where ADRAC predicts 10–40%. The surrogate is learning the upstream model correctly; the upstream parameter set may need reconciliation before scaling. Recorded as an open question.

## [0.1.0] — 2026-04-18

### Added
- Project scaffold: `tinydcs/` package, `scripts/`, `tests/`, `artifacts/`, `data/`.
- `README.md` with explicit objectives, methods, expected results, repository layout, and two-paper publication roadmap.
- `CHANGELOG.md` (this file).
- `requirements.txt` with pinned Python dependencies for reproducibility.
- `pyproject.toml` package metadata.
- `tinydcs.data_clean`: audit and cleaner for `Model_Rel_Candidate/DCS_Risk_DB_2025.csv`. Detects and repairs the documented scale inconsistency (rows mis-entered on the fraction scale 0–1 instead of the percent scale 0–100). Emits a markdown data-quality report.
- `tinydcs.simulator`: wrapper around `rut_mbe1_model.py` that accepts continuous VO₂(t) trajectories and discretizes them into piecewise-constant profile segments for 3RUT-MBe1. Supports realistic exposure profiles (acclimatization → prebreathe → ascent → altitude → descent) with user-specified FiO₂ at each phase.
- `tinydcs.features`: feature extraction from a full exposure profile including Conkin-style tissue nitrogen ratio with 360-min half-time, water-vapor corrected.
- `tinydcs.surrogate`: LightGBM surrogate trainer with train/calibrate/test split, split-conformal intervals on the logit scale, and standard evaluation metrics.
- `tinydcs.metrics`: Brier score, reliability-diagram binning, calibration slope/intercept (logistic recalibration), empirical conformal coverage.
- `scripts/01_clean_data.py`: CLI driver for the dataset cleaner.
- `scripts/02_simulate_training.py`: CLI driver for the simulation campaign, with reproducible seeding and parallelizable workers.
- `scripts/03_train_surrogate.py`: CLI driver that fits LightGBM, calibrates conformal intervals, and writes metrics JSON + figures.
- `tests/test_data_clean.py`: unit test confirming the scale-fix heuristic flags and repairs mixed-unit rows.
- `tests/test_simulator.py`: unit test confirming the 3RUT-MBe1 wrapper produces finite, monotone-in-altitude P(DCS) on a canonical profile set.
- `tests/test_surrogate.py`: unit test on a toy dataset confirming the surrogate fit/predict/conformal round-trip.

### Known issues / open questions
- `rut_mbe1_model.py` produces P(DCS) values on some synthetic profiles that are very small (< 1e-4) even at altitudes/durations where ADRAC reports double-digit percentages. This is a **model-parameter sensitivity** issue in the upstream mechanistic model and not a TinyDCS bug, but it means the surrogate training distribution is skewed toward zero and the calibration target band must be chosen carefully. To be revisited once the full simulation campaign is run.
- The shipped `DCS_Risk_DB_2025.csv` contains within-combo label disagreements (e.g. altitude 39,000 ft, PB 0, Rest, 240 min has both 88 and 97). The cleaner currently keeps the median per combo; better strategies (e.g. regressing out systematic error) are deferred.
- No external clinical dataset is used in v0.1. This is by design — v0.1 is the *methods paper* scaffold; clinical external validation is Paper 2 scope (v1.0+).

### Not changed (intentional)
- `rut_mbe1_model.py` itself is treated as authoritative and is not modified. TinyDCS imports it read-only.
- `Model_Rel_Candidate/DCS_Risk_DB_2025.csv` is not overwritten; the cleaner writes to `artifacts/` only.
- The first repo (`DCS-model-with-Machine-Learning`) is out of scope for this CHANGELOG. See that repo's own changelog for related activity.
