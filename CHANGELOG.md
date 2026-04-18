# Changelog

All notable changes to TinyDCS are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning loosely follows [SemVer](https://semver.org/) with a `v0.X` research-preview series before any `v1.0`.

## [Unreleased]

### Planned
- ONNX export + INT8 quantization + TFLite Micro benchmark (`scripts/05_export_onnx.py`).
- Residual-on-physics hybrid variant (LightGBM on ADRAC − Conkin-ETR residual).
- Paper 1 manuscript draft alongside the code in `docs/`.
- Conformal-coverage investigation: random split hits 0.95 but LOAO folds drop to ~0.88. Likely fixed by (a) larger calibration fold per LOAO fold, or (b) Mondrian conformal stratified by altitude band.

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
