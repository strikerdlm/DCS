# AGENTS.md — Continuation guide for AI agents

This document is the handoff for any AI coding or research agent who picks up TinyDCS. It is maintained alongside the code and updated at the end of each substantive contribution. Human collaborators are welcome to read it too; the framing is "what would I need to know to contribute correctly in the first 30 minutes."

Keep this file current. When an agent lands a change that alters the methods, repo layout, or open-problem list, append a `## Session log` entry at the bottom with the date, the commit range, and a one-line summary of what changed.

---

## 1. TL;DR

- **What this is**: a machine-learning surrogate of the USAF ADRAC altitude-DCS risk model, plus three published mechanistic comparators, designed to run on a wearable in under 1 ms.
- **Current headline**: MAE 0.020, R² 0.986, Brier 0.00156 against the closed-form ADRAC baseline's 0.086 / 0.869 / 0.0150; 47 KB compact ONNX variant; empirical 95% coverage uniform across all 5,000-ft altitude bands after the zero-inflated calibration landed in v0.4.0.
- **Where to start**: read this file, then `docs/runbook.md` (step-by-step reproduction), then `README.md`, then `docs/methods.md`, then the last two `CHANGELOG.md` entries.
- **Repo on origin**: `github.com/strikerdlm/DCS`, default branch `main`, latest tag `v0.5.0` (v0.6.0 is in progress: runbook, validation-hardware, Appendix-C checklist).
- **25 / 25 tests pass** at the current HEAD.

---

## 2. What the project actually targets

**Primary**: a continuous-VO₂ surrogate of the ADRAC log-logistic AFT model on a cleaned 15,908-row grid. This is what Paper 1 is about.

**Secondary (scaffolding)**: callable wrappers for the three published mechanistic models — `mechanistic.adrac`, `mechanistic.conkin_nasa`, `mechanistic.rut_mbe1` — used as baselines, ablations, and physics-informed feature sources.

**Non-targets**:
- TinyDCS is **not** trained on observed clinical DCS incidence. The ground truth is ADRAC's output. Any claim of clinical accuracy requires a prospective-validation study (Paper 3 scope). Do not let framing drift into "clinical DCS prediction."
- `mechanistic/rut_mbe1.py` has an open calibration discrepancy (~4–5 OoM under-prediction vs Gerth Figure 16). **Do not use it as a training target** until this is reconciled. See `docs/methods.md` §M7.

---

## 3. How to get set up

```bash
git clone https://github.com/strikerdlm/DCS
cd DCS
pip install -r requirements.txt         # or: pip install -e .
pytest tests/ -q                        # should print "21 passed"

# Reproduce the headline numbers end-to-end (~2 min on CPU):
python scripts/01_clean_data.py \
    --input legacy/Model_Rel_Candidate/DCS_Risk_DB_2025.csv \
    --output artifacts/DCS_Risk_DB_2025_clean.parquet \
    --report artifacts/data_quality_report.md

python scripts/04_train_adrac_surrogate.py \
    --training artifacts/DCS_Risk_DB_2025_clean.parquet \
    --output-surrogate artifacts/tinydcs_adrac_zi.joblib \
    --output-baseline artifacts/adrac_baseline_zi.joblib \
    --output-metrics artifacts/metrics_adrac_zi.json \
    --output-figures artifacts/figures_adrac_zi \
    --no-run-leave-one-altitude-out --zi
```

If any of the above fails on a clean checkout, **fix that first and document the fix here** before starting new work. Pipeline resilience is load-bearing for Paper 1's reproducibility claim.

---

## 4. Reading order

The repo has grown; these are the files worth reading in the first hour, in order:

1. `docs/runbook.md` — **the first file you open**. Command-by-command reproduction from clean checkout. If a session disconnects mid-work, this is how to resume.
2. `README.md` — user-facing overview, repo layout, status table.
3. `docs/scientific-background.md` — ADRAC, Conkin, Webb, Gerth lineages; primary citations.
4. `docs/methods.md` — TRIPOD+AI-aligned methods (M1–M8). **This is the spec the code implements.** §M7 is the open 3RUT-MBe1 reconciliation task with its Appendix-C audit checklist.
5. `docs/architecture.md` — three-layer diagram (mechanistic / ML surrogate / personalization+fusion).
6. `docs/validation-hardware.md` — honest device inventory for the planned Paper-1 / Paper-3 validation cohort; also the training-hardware scoping note (CPU sufficient through v0.5.0).
7. `docs/publication-roadmap.md` — Papers 1, 2, 3 with journals, data sources, timelines.
8. `docs/papers/paper-1-draft.md` — the draft manuscript. All headline numbers live here.
9. `CHANGELOG.md` — tagged releases; read v0.4.0 and v0.5.0 at minimum.
10. `tinydcs/surrogate.py` — the single most important code file. Four calibration classes, four `fit_*` helpers, one `train_surrogate` orchestrator, one self-contained `TinyDcsSurrogate` bundle.
11. `tinydcs/personalization.py` — Paper-2 prototype: conjugate-Gaussian hierarchical personalization on top of any trained base surrogate.
12. `mechanistic/adrac.py` — closed-form ADRAC log-logistic baseline (the honest comparator).
13. `scripts/04_train_adrac_surrogate.py` — the primary training pipeline CLI.
14. `scripts/08_personalization_demo.py` — the Paper 2 synthetic-cohort demo.

Don't skim `legacy/`. Treat it as frozen history. Nothing there is imported by current code.

---

## 5. The three-layer architecture

```
Layer 1 — published mechanistic models (mechanistic/)
    rut_mbe1.py        Gerth 3RUT-MBe1 (calibration WIP; do not train against)
    conkin_nasa.py     Conkin RM/NM logistic (Eq 14/15, TP-2004-213158)
    adrac.py           Closed-form log-logistic AFT (Kannan 1998 / Pilmanis 2004)

Layer 2 — ML surrogate core (tinydcs/)                          ← primary focus
    simulator.py       Continuous-VO2(t) wrapper
    features.py        13-feature vector (incl. Conkin TR_360)
    surrogate.py       LightGBM + 4 calibration modes + OOD + joblib bundle
    metrics.py         Brier, reliability, Bland-Altman, coverage
    data_clean.py      ADRAC CSV scale-fix + dedup
    cli.py             Console entry points

Layer 3 — personalization and multimodal fusion                  ← Paper 2 scope
    (not implemented yet; see docs/publication-roadmap.md Paper 2)
```

Changes that span layers should update `docs/architecture.md` in the same commit.

---

## 6. Methods currently in use

### 6.1 Data cleaning (`tinydcs.data_clean`)

The shipped `DCS_Risk_DB_2025.csv` has two documented defects:

1. **Scale inconsistency** — 1,221 rows (7.5%) entered on the fraction scale [0, 1] instead of percent [0, 100]. Detected via a neighbour-median heuristic: value ≤ 1.0 AND neighbour-median (same exercise, altitude ± 1000 ft, PB ± 15 min, time ± 20 min) > 1.0 AND rescaled (×100) within ±30% of neighbour median.
2. **Within-combo disagreements** — 26 grid cells with two distinct values; collapsed to the median.

Never train on the raw CSV. Always run `scripts/01_clean_data.py` first.

### 6.2 Feature vector (`tinydcs.features.FEATURE_COLUMNS`, 13 features)

Every feature is justified by a primary-source citation. Don't add features without a citation and a physiological hypothesis.

| Feature | Source |
|---|---|
| `altitude_ft`, `ambient_pressure_atm` | ADRAC + ISA |
| `prebreathe_time_min`, `prebreathe_fio2` | Webb 1999 + Conkin 2004 |
| `ascent_rate_fpm` | Depressurization profile input |
| `altitude_time_min`, `altitude_fio2` | ADRAC failure time + inspired gas |
| `prebreathe_vo2_mean_lmin`, `prebreathe_vo2_peak_lmin` | Conkin 2004 exercise-prebreathe effect |
| `altitude_vo2_mean_lmin`, `altitude_vo2_peak_1min_lmin`, `altitude_vo2_integral_lmin_min` | Webb 2010, 2016 (1-min peak VO₂ per 16-min window) |
| `tissue_n2_ratio_360min` | Conkin single-compartment supersaturation ratio, water-vapor corrected |

### 6.3 Target transform

```
y_pct → y_frac = y/100 → Smithson-Verkuilen (y*(n-1)+0.5)/n → logit
```

Smithson-Verkuilen is essential because ~40% of low-altitude rows have exact-zero targets, which create a logit-space pile-up.

### 6.4 Base surrogate (`tinydcs.surrogate.train_surrogate`)

- LightGBM regressor on logit target.
- 400 estimators, 31 leaves, learning rate 0.05, subsample 0.9, col-subsample 0.9 (default).
- **Physiological monotonicity constraints**: altitude / time / tissue-ratio ↑ ⇒ risk ↑; prebreathe / ambient pressure ↑ ⇒ risk ↓.
- Fixed random state (default 42) for reproducibility.

### 6.5 Calibration — four modes

1. **Global split-conformal** — simplest; constant half-width.
2. **Mondrian conformal** — per-altitude-band quantile with a global fallback; handles heteroscedastic residuals.
3. **Conformalized Quantile Regression (CQR)** — two quantile regressors + a single correction; handles asymmetric intervals. Optional Mondrian correction stratifies per band.
4. **Zero-inflated two-stage** (default for headline numbers) — binary classifier for P(y=0) gating a continuous regressor on non-zero rows. Closes the low-altitude coverage shortfall that all three conformal-only methods leave open.

The zero-inflated mode should be your default for new work unless you have a specific reason to use another.

### 6.6 Out-of-envelope abstention

Mahalanobis distance in feature space to the training mean under a Ledoit–Wolf-shrunk covariance. Threshold = 99th percentile of training distances. Not a probability; returns a boolean flag alongside the prediction.

### 6.7 Edge export (`scripts/05_export_onnx.py`, `scripts/06_train_compact_surrogate.py`)

FP32 ONNX via `onnxmltools.convert_lightgbm`; dynamic INT8 via `onnxruntime.quantization.quantize_dynamic` (does NOT shrink tree ensembles; expected). Compact variant (100 × 7) hits 47 KB at MAE 0.028, R² 0.981 — this is the current wearable-target model.

---

## 7. Open problems, ranked

### P0 — Ship the zero-inflated surrogate to edge

The current `scripts/05_export_onnx.py` only exports single-model surrogates. The zero-inflated two-stage model needs a variant that emits both sub-graphs (classifier + continuous regressor) plus a tiny runtime that implements the gate + mixture aggregation. Estimated effort: 1–2 hours.

Acceptance: a single ONNX-ish artifact (either two ONNX files + a Python gluer, or one ONNX with a dispatch node) that reproduces `TinyDcsSurrogate.predict()` bit-exact on a 10,000-row batch. Paper-1 "runs on wearables" claim is incomplete without this.

### P1 — Real hardware benchmark

Current latency numbers (6.65 μs/row p50 on CPU) are extrapolated to Cortex-M4 with a ~20× multiplier from Warden & Situnayake 2019. This is indicative, not empirical. A real measurement on a STM32F7, Apple Watch, or Arduino Portenta would upgrade the claim from "expected" to "measured". Needs hardware access.

### P2 — Paper 2: hierarchical Bayesian personalization

The single most defensible novel scientific contribution after Paper 1. Key components:

- Per-subject susceptibility $\lambda_i \sim \mathrm{LogNormal}(\mu_\lambda, \sigma_\lambda)$ as a multiplier on the base hazard.
- Online posterior updates from user-reported symptom checks.
- Multimodal state-dependent modulation (HR, HRV, SpO₂, skin temp).

PyMC is already a dependency in the broader workspace. A scoping note should live in `docs/papers/paper-2-scope.md` (does not yet exist — create it when you pick this up).

### P3 — Paper 3: prospective clinical validation

Requires IRB + chamber access + wearable logistics. The only way to move the surrogate-vs-clinical framing from "claimed" to "demonstrated". See `docs/publication-roadmap.md`.

### P4 — Reconcile 3RUT-MBe1

`mechanistic/rut_mbe1.py` under-predicts P(DCS) by 4–5 orders of magnitude on Gerth's own validation profiles. Likely suspects: Λ scaling factor (`lambda_cm_inv = 100.0` default), `n0_b_total_nuclei` (1.198), `gain_g_hazard` (6.188e-2), or numerical damping. Approach (listed in `docs/methods.md` §M7): step-by-step Appendix C audit + Bayesian-optimization parameter scan on the five validation profiles. Once reconciled, 3RUT-MBe1 becomes a third ground-truth source alongside ADRAC.

### P5 — Manuscript polish

`docs/papers/paper-1-draft.md` is substantively complete. What remains: journal-specific formatting (AMHP primary; DHM backup), figure embedding (PNGs in `artifacts/figures_adrac_zi/`), acknowledgements, declared COIs, final reference formatting. This is largely non-technical and can be done late.

### P6 — ONNX for CQR

Lower priority than P0 but same shape: CQR ships two quantile regressors + a scalar correction. An ONNX version would let callers deploy CQR-calibrated surrogates, not just the default zero-inflated one. Matters mostly for ablation studies.

---

## 8. Promising research directions (less ranked, more speculative)

These are ideas to explore when you're looking for something novel rather than completing the v1.0 checklist.

- **Monotonic quantile network** — a small neural network with constrained weights that handles the quantile objective + monotonicity *at the same time* (LightGBM refuses this combination). If trained end-to-end with a pinball loss, this would give CQR its monotonicity back without giving up quantile-level coverage guarantees.
- **Continuous-time hazard model** — instead of predicting final P(DCS) for a given (altitude, duration), emit a hazard function h(t | altitude, VO₂(t)) so a wearable can compute running risk along any exposure curve. Connects nicely to Conkin's log-logistic survival framework.
- **Physics-informed regularization** — add a loss term that penalizes violations of the supersaturation condition (ΔP < 0 ⇒ P(DCS) small). Might tighten the low-altitude predictions without the zero-inflated split.
- **Counterfactual advisory API** — given a current prediction, answer "what prebreathe duration would drop risk below 5%?" Implement by scanning the input along one dimension at a time and returning thresholds. Operationally valuable, trivial to build once the surrogate exists.
- **Federated personalization** — per-device posterior updates of the susceptibility parameter aggregated via differential privacy. Avoids centralizing patient-level physiology data. Connects to Paper 2 but is mostly a separate systems contribution.
- **VGE (venous gas emboli) as a secondary target** — VGE appears earlier than clinical DCS and has more labels in chamber data. A multi-task surrogate that predicts both P(DCS) and P(VGE≥3) might be more useful operationally and supply richer calibration data.
- **Active learning for chamber trials** — once Paper 3 data collection starts, use surrogate uncertainty to pick the most informative exposure profiles to measure. Reduces the study's chamber-hour budget.

Each of these is at least a weekend of work; several are independent-paper candidates.

---

## 9. Pitfalls and guardrails

- **Don't modify `mechanistic/rut_mbe1.py` without running the DTIC validation check.** `docs/methods.md` §M7 has the exact five profiles and expected-range table. Any "fix" that moves predictions further from those values is regression.
- **Don't commit `artifacts/`.** It's `.gitignore`d. Headline numbers are reproducible from raw inputs; artifacts are outputs.
- **Don't skip `01_clean_data.py`.** Training on the raw CSV with 1,221 mis-scaled rows will silently ruin every downstream metric.
- **Don't claim clinical accuracy.** The target is ADRAC's output. Every external-facing surface (abstract, limitations, README) already enforces this framing — don't weaken it.
- **LightGBM's "X does not have valid feature names" warning is benign.** It fires when `predict()` receives a numpy array without column names. We wrap inputs in a `pandas.DataFrame` internally; the warning survives in some edge cases. Leave it.
- **LightGBM rejects monotone constraints on the quantile objective.** This is a hard upstream limitation. Our CQR quantile regressors therefore don't carry monotonicity; the base model does. If you're replacing CQR with a neural quantile regressor, re-add the constraint.
- **Don't add features without a primary-source citation.** Reviewer first question is always "why this feature?". Paper 1 answers it with Conkin / Webb / ADRAC references. A novel feature needs a novel mechanism.
- **Always use `git mv` for renames.** Preserving blame/log history is load-bearing for the project's provenance claim.

---

## 10. Validation checklist for new contributions

Before opening a PR or pushing to `main`, verify:

- [ ] `pytest tests/ -q` — all tests pass, no new flakes.
- [ ] If you changed calibration, `scripts/04_train_adrac_surrogate.py` still runs end-to-end with all three `--cqr`, `--zi`, and default modes.
- [ ] If you changed the surrogate or ONNX path, `scripts/05_export_onnx.py` still produces a valid FP32 ONNX with ≤ 1e-4 max-abs parity vs Python.
- [ ] `CHANGELOG.md` gets a `## [Unreleased]` → `## [0.X.Y] — ...` entry with before/after numbers.
- [ ] `docs/methods.md` or `docs/architecture.md` updated if the method or layout changed.
- [ ] `docs/papers/paper-1-draft.md` numbers updated if headline metrics moved.
- [ ] A per-file commit message explaining the *why* (not just the what). Template in `docs/papers/paper-1-draft.md`'s git log.

If you added a new calibration mode or a whole new class of model, also:

- [ ] Add at least one test covering fit / predict / save / load.
- [ ] Add a per-band coverage table to the CHANGELOG entry.

---

## 11. How to document new work

Every substantive commit should answer three questions in its body (not just subject line):

1. **What changed** — concrete list of files / functions / behaviour.
2. **Why** — the motivating observation, citation, or failure mode.
3. **What this does to the headline numbers** — before/after MAE, R², Brier, coverage, size, latency if relevant.

For multi-commit changes, end with a CHANGELOG update and a tag bump (`vX.Y.Z`). Tags are the external API; users who consume this repo for Paper 2 / 3 experiments should be able to check out a tag and get reproducible results.

---

## 12. Attribution

Project is maintained by Diego Malpica, MD. AI agent co-authorship is declared in each commit's `Co-Authored-By:` line per the project's transparency policy. Major releases tag the specific model family (e.g. `Claude Sonnet 4.6`, `Opus 4.7`) that produced the session's code.

If you fork or build on this, please include the `AGENTS.md` and preserve the continuation-log format — it is part of the reproducibility contract.

---

## Session log

A dated record of substantive agent sessions. Each entry is one line: date, git range, one-phrase summary.

- `2026-04-18` · `50a4eaf..f1f80a5` · repo restructure, ADRAC closed-form baseline, LightGBM surrogate with Mondrian / CQR / zero-inflated calibration, ONNX export + compact ladder, Paper 1 manuscript draft; v0.2.0 → v0.4.0.
- `2026-04-18` · `1c8707a..4447f77` · AGENTS.md continuation guide; zero-inflated ONNX edge export (compact: 95 KB total, 2.4 μs/row, R²=0.98, coverage=0.95); Paper 2 scope doc; conjugate-Gaussian personalization prototype with synthetic-cohort sweep; v0.4.1, v0.5.0.
- `2026-04-18` · `cf9826f..9d55180` · docs/runbook.md (command-by-command reproduction); docs/validation-hardware.md (honest device inventory + training-hardware scoping); docs/methods.md §M7 replaced scalar-fit reconciliation with NEDU-TR-18-01 Appendix-C audit checklist; AGENTS.md continuity updates (reading order, TL;DR, resume pointer below). v0.6.0 in progress.
- *(next session: add your entry here before your last push.)*

### If this session disconnects — resume here

1. Open `docs/runbook.md`. Follow §0 → §2 to regenerate `artifacts/DCS_Risk_DB_2025_clean.parquet` and `artifacts/tinydcs_adrac_zi.joblib` from a clean checkout. If the printed headline numbers do not match §2 of the runbook, stop and report the divergence — something has drifted.
2. Open this file's §7 (Open problems, ranked). P0, P1, P2 are the active Paper 1 / Paper 2 items. P4 (3RUT-MBe1) is the long-tail task whose checklist now lives in `docs/methods.md` §M7; do not start it casually — it requires access to NEDU TR 18-01.
3. The immediate next deliverable after v0.5.0 is `scripts/09_make_paper_figures.py` — generate the five AMHP IMRAD figures (reliability diagram, per-band coverage, size-vs-accuracy Pareto, info-gain curve, architecture). Read `docs/papers/paper-1-draft.md` first to confirm which figures the manuscript references.
4. After the figures script, tag `v0.6.0` and push.
5. Do **not** reformat the manuscript to Nature / *Science* Results-before-Methods style. Primary target journal is *Aerospace Medicine and Human Performance* (AMHP), IMRAD. This is a settled call.
6. Do **not** apply a scalar-fit patch to `mechanistic/rut_mbe1.py` to make its output match Gerth Fig. 16. That is explicitly rejected in `docs/methods.md` §M7 — the reconciliation must go through the Appendix-C equation audit.
