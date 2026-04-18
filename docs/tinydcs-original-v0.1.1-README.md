# TinyDCS

**An edge-deployable machine-learning surrogate of the 3RUT-MBe1 bubble-dynamics model for real-time altitude decompression-sickness risk estimation.**

> ⚠️ **Research-only disclaimer.** TinyDCS is an experimental research artifact. It is **not** a clinical device, not certified for operational or flight use, and must not be used as the sole basis for any aeromedical decision. It approximates a published mechanistic model (Gerth et al., NEDU TR 18-01) and inherits the limits of that model's validation envelope.

---

## Why this exists

Altitude decompression sickness (DCS) in unpressurized aviation and extravehicular activity is a well-studied risk with three dominant families of published predictive models:

| Model family | Paradigm | Validated for | Computational footprint |
|---|---|---|---|
| **ADRAC** (USAFSAM, Pilmanis/Kannan 1998–2004) | Log-logistic accelerated failure time on 4 covariates | 18,000–40,000 ft, 150 validation profiles | Closed-form, trivial |
| **Conkin NASA RM/NM** (NASA TP-2004-213158) | Logistic regression on Exercise Tissue Ratio (ETR) + age/sex | 4.3–9.5 psia, NASA chamber tests | Closed-form, trivial |
| **3RUT-MBe1** (Gerth et al., NEDU TR 18-01, 2018) | Mechanistic three-region tissue model with bubble-evolution ODE | Outperforms ADRAC on 4/5 validation profiles | ODE recursion, ~300+ steps/profile |

All three were fit on overlapping USAFSAM / NASA hypobaric chamber data. ADRAC and Conkin-RM/NM are fast enough for a watch but **cannot accept continuous time-varying activity** — ADRAC uses three coarse levels (Rest/Mild/Heavy) and Conkin-RM integrates VO₂ only during prebreathe. 3RUT-MBe1 accepts arbitrary piecewise VO₂(t) trajectories and is the published state-of-the-art for continuous-exposure modelling, but its ODE recursion is too heavy for a smartwatch or a flight computer's background task.

TinyDCS targets this specific, well-defined gap: **a compact ML surrogate that reproduces 3RUT-MBe1 risk predictions to within a documented tolerance, runs in < 1 ms on an ARM Cortex-M4, and provides calibrated uncertainty with principled abstention outside the mechanistic model's validated envelope.**

---

## Objectives

### Primary

1. **O1 — Surrogate fidelity.** Train an ML surrogate (LightGBM baseline; small MLP as comparator) that reproduces 3RUT-MBe1 final P(DCS) on held-out altitude/prebreathe/exercise profiles with mean absolute error ≤ 3 percentage points and calibration slope within [0.9, 1.1].
2. **O2 — Calibrated uncertainty.** Attach split-conformal prediction intervals with finite-sample marginal coverage ≥ 95% on held-out profiles, calibrated on the logit scale so intervals respect `[0, 1]`.
3. **O3 — Validity-envelope abstention.** Implement Mahalanobis-distance OOD detection in the feature space of 3RUT-MBe1's training envelope; abstain (return "out of envelope") rather than extrapolate silently.
4. **O4 — Edge deployment.** Export to ONNX, quantize to INT8, report inference latency and memory on CPU + simulated Cortex-M4 via TFLite Micro. Target: < 1 ms latency, < 100 KB model, < 32 KB RAM.

### Secondary

5. **O5 — Dataset audit & cleanup.** Fix the documented scale inconsistency in `Model_Rel_Candidate/DCS_Risk_DB_2025.csv` (some rows entered as fractions, others as percent) and publish a reproducible cleaner + quality report.
6. **O6 — Continuous-VO₂ demonstration.** Show that feeding a realistic accelerometer-derived VO₂(t) trajectory (vs. a single scalar like "Mild") produces materially different risk estimates — i.e. demonstrate the operational relevance of continuous activity input.
7. **O7 — Manuscript-ready outputs.** Auto-generate publication figures (calibration plot, reliability curve, Bland–Altman surrogate-vs-mechanistic, inference latency histogram) and a TRIPOD-AI-style reporting checklist.

### Non-objectives (explicit)

- We are **not** proposing a new mechanistic DCS model. TinyDCS is strictly a surrogate of a published one.
- We are **not** claiming clinical predictive accuracy. The "ground truth" is 3RUT-MBe1's own output, not observed DCS incidence. Any clinical claim requires a separate prospective validation (see *Roadmap → Paper 2*).
- We are **not** replacing ADRAC, Conkin, or 3RUT-MBe1. All three remain authoritative in their respective published envelopes; TinyDCS only makes 3RUT-MBe1 deployable at the edge.

---

## Scientific background (one page)

### What ADRAC is, exactly

The USAF Altitude Decompression Sickness Risk Assessment Computer is a **stratified accelerated-failure-time log-logistic survival model** with four covariates: ambient pressure (mmHg), prebreathe time, time at altitude (the failure time), and exercise level (categorical Rest/Mild/Heavy). Core equation:

$$P(\text{DCS by time } t) = 1 - S(t) = \frac{1}{1 + \exp\big((\ln t - \beta_2 - \beta \cdot x)/\beta_1\big)}$$

Validation: 150 prospective hypobaric exposures (Pilmanis et al. 2004, ASEM 75:749–59). Ceiling 40,000 ft.

### What Conkin RM/NM add

Conkin's **Exercise Tissue Ratio** model (NASA TP-2004-213158) replaces the categorical exercise input with a physiologically grounded **variable half-time** that depends on VO₂ during prebreathe:

$$\text{ETR} = \frac{P_1N_2}{P_2}, \qquad P(\text{DCS}) = \sigma(\beta_0 + \beta_1 \cdot \text{ETR} + \beta_2 \cdot \text{covariate})$$

where the covariate is age (RM) or sex (NM) and P₁N₂ integrates N₂ kinetics with a VO₂-dependent half-time. Exercise at altitude is **not** modelled — only during prebreathe.

### What 3RUT-MBe1 adds

Gerth et al. (NEDU TR 18-01, 2018) implement a **three-region unified tissue bubble-evolution model** that accepts arbitrary piecewise VO₂(t) trajectories across the full exposure (prebreathe + ascent + altitude + descent). It is the first altitude-DCS model with **time-dependent covariates** for exercise at altitude. It outperforms ADRAC on 4/5 validation profiles. Cost: an ODE recursion (Appendix C of the report) with ~300 steps per profile for ms-resolution.

### The published gap

Webb et al. (ASEM 2010; AMHP 2016) defined the operationally correct activity metric — **highest 1-min VO₂ per 16-min window at altitude** — but ADRAC has not been refit to use it. 3RUT-MBe1 can use it but cannot run on a watch. No one has published an edge-deployable surrogate of 3RUT-MBe1 with calibrated uncertainty and OOD abstention. That is TinyDCS.

---

## Methods

### M1 — Data audit

Three dataset sources are relevant:

- `DCS-model-with-Machine-Learning/output_data_setV10.xlsx` (2,328 rows, target in fraction [0, 0.98], 4 inputs). Used for replication of prior surrogate work.
- `DCS-other/Model_Rel_Candidate/DCS_Risk_DB_2025.csv` (16,295 rows, target labelled as risk_of_decompression_sickness in percent 0–100, but with **documented within-row scale inconsistencies**: some rows entered as fractions 0.01–0.90, others as percent 1–98). Must be cleaned before use.
- Synthetic: profiles generated by running 3RUT-MBe1 on randomized inputs (this is TinyDCS's primary training data).

`tinydcs.data.clean` audits and repairs the scale inconsistency and produces `DCS_Risk_DB_2025_clean.parquet` + a markdown quality report. See `scripts/01_clean_data.py`.

### M2 — Simulation campaign

We use the existing `rut_mbe1_model.py` (no modifications) to generate training data. Inputs are sampled as:

| Input | Distribution |
|---|---|
| Target altitude | Uniform(18,000, 40,000) ft |
| Prebreathe FiO₂ | `{1.0: 0.8, 0.95: 0.1, 0.85: 0.1}` |
| Prebreathe duration | Uniform(0, 180) min |
| Prebreathe VO₂ profile | Constant or piecewise with I_ex∈[0, 1.5] L·min⁻¹ |
| Ascent rate | `{5000 fpm: 0.9, 1000 fpm: 0.1}` (cabin depressurization vs. slow climb) |
| Altitude duration | Uniform(10, 480) min |
| Altitude FiO₂ | `{0.21: 0.8, 1.0: 0.15, 0.95: 0.05}` (air vs. chamber O₂) |
| Altitude VO₂ trajectory | Ornstein–Uhlenbeck on I_ex with bounds [0, 1.0] L·min⁻¹ whole-body, reverting to subject-specific mean |

For each profile we extract the final `ModelState.p_dcs` from 3RUT-MBe1 and also tabulate intermediate summary features (see M3). See `scripts/02_simulate_training.py`. A pilot campaign of 200 profiles runs in minutes for end-to-end sanity checks; the full campaign (target 20,000+ profiles) runs overnight on a single core and scales embarrassingly parallel.

### M3 — Features

The surrogate consumes a compact feature vector computable on-device from an accelerometer-derived VO₂ proxy and an altitude stream:

- `altitude_ft` (max sustained altitude) and `ambient_pressure_atm` (derived).
- `prebreathe_time_min`, `prebreathe_fio2`, `prebreathe_vo2_mean_lmin`, `prebreathe_vo2_peak_lmin`.
- `ascent_rate_fpm` (derived from altitude stream gradient).
- `altitude_time_min`, `altitude_fio2`.
- `altitude_vo2_mean_lmin`, `altitude_vo2_peak_1min_lmin` (matches Webb 2010 metric), `altitude_vo2_integral`.
- `tissue_n2_ratio_360min` — the classic Conkin TR with a single 360-min half-time compartment, computed closed-form on the altitude/PB/FiO₂ trajectory. Serves as a physics-informed prior feature.

Feature set is intentionally **small** (≤ 12 features) so the trained model stays under 100 KB after quantization.

### M4 — Surrogate

- **Baseline**: LightGBM regressor on logit(P(DCS)), trained with monotonic constraints where physiology mandates monotonicity (e.g. increasing altitude ⇒ non-decreasing risk at fixed other covariates).
- **Comparator**: 2–3-layer MLP (≤ 8k parameters), INT8-quantized post-training.
- **Residual-on-physics mode (optional)**: LightGBM on the *residual* between 3RUT-MBe1 and a cheap closed-form predictor (log-logistic fit to Conkin ETR) — this is hybrid physics+ML, often better-behaved at the envelope edge.

### M5 — Uncertainty and abstention

- **Split conformal** on a held-out calibration fold, residuals computed on the logit scale so intervals respect [0, 1].
- **Validity envelope**: Mahalanobis distance in feature space to the 3RUT-MBe1 training-input distribution; threshold chosen to give < 5% false-abstention on in-envelope calibration data.
- Output API returns `{point_estimate, lower_95, upper_95, in_envelope: bool, envelope_distance: float}`.

### M6 — Evaluation

- **Discrimination**: ROC-AUC (thresholded P(DCS) > 10% as positive), Brier score.
- **Calibration**: reliability diagram, calibration slope/intercept (Van Calster et al. 2019).
- **Conformal coverage**: empirical coverage at nominal 95% on an out-of-distribution altitude-stratified hold-out.
- **Fidelity to mechanistic model**: Bland–Altman surrogate-vs-3RUT-MBe1, MAE, RMSE, and worst-case error.
- **Efficiency**: inference latency (CPU, simulated Cortex-M4), model size, RAM footprint.

### M7 — Deployment

- Export best model to ONNX; verify outputs match PyTorch/LightGBM reference to 1e-5.
- Quantize to INT8 (ONNX Runtime or TFLite Micro pipeline).
- Generate a header-only C file with weights for direct flashing.
- Provide a minimal Python reference runtime (`tinydcs.runtime`) that matches the quantized edge output bit-exact.

---

## Repository layout

```
TinyDCS/
├── README.md                ← this file
├── CHANGELOG.md             ← versioned change log
├── requirements.txt         ← pinned Python deps
├── pyproject.toml           ← package metadata
├── tinydcs/                 ← installable package
│   ├── __init__.py
│   ├── simulator.py         ← 3RUT-MBe1 wrapper with continuous VO2(t)
│   ├── features.py          ← feature extraction
│   ├── surrogate.py         ← LightGBM + conformal + OOD
│   ├── metrics.py           ← Brier, reliability, coverage
│   ├── data_clean.py        ← DCS_Risk_DB_2025.csv cleaner
│   └── cli.py               ← CLI entrypoints
├── scripts/
│   ├── 01_clean_data.py     ← audit + clean the shipped CSV
│   ├── 02_simulate_training.py  ← build synthetic training set
│   ├── 03_train_surrogate.py    ← train + calibrate + evaluate
│   └── 04_export_onnx.py        ← quantize + export edge artifact
├── tests/
│   ├── test_simulator.py
│   ├── test_data_clean.py
│   └── test_surrogate.py
├── artifacts/               ← (git-ignored) models, CSVs, figures
└── data/                    ← derived data products (small, versioned)
```

---

## Installation

Requires Python 3.10+.

```bash
cd DCS-other/TinyDCS
pip install -r requirements.txt          # or: pip install -e .
```

Verify 3RUT-MBe1 is reachable (TinyDCS imports it from `DCS-other/rut_mbe1_model.py`):

```bash
python -c "from tinydcs.simulator import smoke_test; smoke_test()"
```

---

## Step-by-step usage

### Step 1 — Audit and clean the shipped dataset

```bash
python scripts/01_clean_data.py \
    --input ../Model_Rel_Candidate/DCS_Risk_DB_2025.csv \
    --output artifacts/DCS_Risk_DB_2025_clean.parquet \
    --report artifacts/data_quality_report.md
```

Detects rows where the target appears to be on the fraction scale (e.g. `0.47` instead of `47`), rescales, deduplicates within-combo disagreements by keeping the median, and produces a markdown quality report summarizing what was changed and why.

### Step 2 — Generate surrogate training data from 3RUT-MBe1

Pilot (a few hundred profiles, minutes):

```bash
python scripts/02_simulate_training.py --n-profiles 200 --seed 42 \
    --output artifacts/training_pilot.parquet
```

Full campaign (target ≥ 20,000 profiles, overnight; trivially parallelizable):

```bash
python scripts/02_simulate_training.py --n-profiles 20000 --seed 42 --workers 8 \
    --output artifacts/training_full.parquet
```

Each row in the output parquet contains the input profile parameters, the derived feature vector, and the final 3RUT-MBe1 P(DCS).

### Step 3 — Train + calibrate the surrogate

```bash
python scripts/03_train_surrogate.py \
    --training artifacts/training_full.parquet \
    --test-fraction 0.15 --calibration-fraction 0.15 \
    --model-type lightgbm \
    --output-model artifacts/tinydcs_v0.1.joblib \
    --output-metrics artifacts/metrics_v0.1.json \
    --output-figures artifacts/figures_v0.1/
```

Produces:
- The trained surrogate + conformal quantile + OOD detector as a single joblib.
- A metrics JSON (R², Brier, calibration slope/intercept, conformal coverage, latency).
- Publication-ready figures: reliability diagram, Bland–Altman, ROC, latency histogram.

### Step 4 — Export to ONNX + quantize for edge

```bash
python scripts/04_export_onnx.py \
    --input-model artifacts/tinydcs_v0.1.joblib \
    --output-onnx artifacts/tinydcs_v0.1.onnx \
    --quantize int8 \
    --benchmark-tflm
```

Verifies that the quantized model matches the floating-point reference within a configurable tolerance, and emits a benchmark report (inference latency, flash footprint, RAM).

---

## Expected results

### Fidelity (primary)

- **Surrogate vs 3RUT-MBe1 MAE** ≤ 0.03 on the final P(DCS). Target R² ≥ 0.98 on held-out profiles drawn from the same input distribution.
- **Bland–Altman**: systematic bias |Δ| < 0.01 across the 0–1 range; 95% limits of agreement within ± 0.06.

### Calibration

- **Calibration slope** in [0.9, 1.1], **calibration intercept** |β₀| < 0.05 on held-out data (Van Calster et al. 2019 reporting).
- **Brier score** ≤ 0.05 (binarizing at P(DCS) > 10%).

### Uncertainty

- **Empirical conformal coverage** ≥ 94% at nominal 95% on the in-envelope test fold.
- On **deliberately out-of-envelope** inputs (altitude 45,000 ft, or prebreathe > 240 min), the OOD detector abstains on ≥ 90% of samples.

### Efficiency

- **Model size** < 100 KB after INT8 quantization.
- **Inference latency** < 1 ms on Cortex-M4 at 80 MHz (simulated via TFLite Micro benchmark).
- **Peak RAM** < 32 KB.

### Operational demonstration

- A worked example where a realistic accelerometer-derived VO₂(t) trajectory (e.g., aircrew running a fitness drill during a hypobaric chamber sortie) produces a **≥ 5-percentage-point** different P(DCS) from a naïve "Mild" categorical input at the same altitude/PB/time. This is the core "why continuous matters" figure for the paper.

---

## Roadmap to publication

### Paper 1 — Methods paper (3–6 months, uses only existing artifacts + simulation)

**Title (tentative)**: *"TinyDCS: An edge-deployable surrogate of the 3RUT-MBe1 bubble-dynamics model for real-time altitude decompression-sickness risk monitoring in unpressurized aviation."*

**Journal targets**: primary — *Aerospace Medicine and Human Performance* (AMHP); secondary — *Diving and Hyperbaric Medicine*, *IEEE Journal of Biomedical and Health Informatics*.

**Contents**:
1. Motivation (unpressurized GA above FL180 post-Stepanek 2024; limitations of ADRAC's categorical activity input).
2. Methods as summarized in *Methods* above, with the full TRIPOD-AI checklist.
3. Results: fidelity, calibration, coverage, efficiency, and the continuous-VO₂ worked example.
4. Limitations: surrogate inherits 3RUT-MBe1's envelope; target is a mechanistic output, not observed DCS incidence; external clinical validation deferred to Paper 2.
5. Open source + reproducibility statement.

### Paper 2 — Clinical validation (12–18 months, requires new data collection)

**Title (tentative)**: *"Prospective evaluation of a wearable continuous DCS risk monitor during hypobaric chamber training: an external-validation study in a Latin American aerospace cohort."*

**Journal targets**: primary — *npj Digital Medicine*, *AMHP*; secondary — *Frontiers in Physiology*.

**Requirements**:
- IRB protocol (CIAF / Universidad del Bosque).
- Chamber training cohort with wearable-derived VO₂(t), altitude log, and prospective DCS/VGE outcome ascertainment.
- Sample-size calculation targeting calibration slope precision (Riley et al. 2019).

### Paper 3 — (stretch, 18+ months) Integration study

ADS-B altitude stream + wearable VO₂ + TinyDCS inference + in-cockpit advisory, deployed on a small fleet. Evaluation focuses on compliance, workload, and false-alarm rate rather than DCS incidence.

---

## TRIPOD-AI reporting checklist coverage (target)

| Section | Target coverage |
|---|---|
| Title, abstract, background | §Why this exists, Scientific background |
| Methods (data, features, model, validation) | §Methods M1–M7 |
| Results (performance, calibration, uncertainty, efficiency) | §Expected results |
| Discussion (limitations, envelope) | §Non-objectives, §Limitations below |
| Open science (code, data, artefacts) | This repo + release tags |

---

## Limitations

1. **Ground truth is a mechanistic model's output**, not observed DCS. External prospective validation is the single biggest gap and is deferred to Paper 2.
2. **3RUT-MBe1's validation envelope is the hard ceiling.** TinyDCS abstains outside it (by design); it does not extrapolate.
3. **Individual variability.** Neither 3RUT-MBe1 nor TinyDCS represents inter-subject differences in susceptibility, PFO, hydration status, prior DCS history, or fatigue. A per-subject calibration layer is an obvious future extension.
4. **Wearable VO₂ accuracy.** Accelerometer-derived VO₂ proxies (Firstbeat, Keytel) carry 10–20% error in absolute VO₂ and are not validated at altitude. TinyDCS sensitivity to this error must be reported in Paper 1.
5. **Regulatory status.** TinyDCS is research software. Use for operational or clinical decision-making would require an entirely separate regulatory pathway (e.g. FDA SaMD, EU MDR).

---

## Citations (primary sources)

- Kannan N, Raychaudhuri A, Pilmanis AA. *A loglogistic model for altitude decompression sickness.* Aviat Space Environ Med 1998; 69:965–70. PMID: 9773897.
- Pilmanis AA, Petropoulos L, Kannan N, Webb JT. *Decompression sickness risk model: development and validation by 150 prospective hypobaric exposures.* Aviat Space Environ Med 2004; 75:749–59.
- Conkin J. *A Log Logistic Survival Model Applied to Hypobaric Decompression Sickness.* NASA TP-2001-210775, 2001.
- Conkin J, et al. *A probability model of decompression sickness at 4.3 psia after exercise prebreathe.* NASA TP-2004-213158, 2004.
- Webb JT, Krock LP, Gernhardt ML. *Oxygen consumption at altitude as a risk factor for altitude decompression sickness.* Aviat Space Environ Med 2010; 81:987–92.
- Webb JT, Morgan TR, Sarsfield SD. *Altitude decompression sickness risk and physical activity during exposure.* Aerosp Med Hum Perform 2016; 87:516–20.
- Gerth WA et al. *A Probabilistic Model of Altitude Decompression Sickness Based on the 3RUT-MB Model.* NEDU TR 18-01, 2018. DTIC AD1101527.
- Collins GS, Moons KGM, et al. *TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods.* BMJ 2024; 385:e078378.
- Van Calster B, McLernon DJ, van Smeden M, et al. *Calibration: the Achilles heel of predictive analytics.* BMC Med 2019; 17:230.

---

## License

See the parent repository. Code is research-use-only; see the top-of-file disclaimer on every module.
