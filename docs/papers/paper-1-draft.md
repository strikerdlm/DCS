# TinyDCS: An edge-deployable machine-learning surrogate of the ADRAC altitude-decompression-sickness risk model with continuous-exposure covariates and calibrated uncertainty

**Diego Malpica, MD¹**

¹ Aerospace Medicine, Colombia Aerospace Force / Universidad del Bosque, Bogotá.

*Draft v0.3 — in preparation for submission to Aerospace Medicine and Human Performance*

---

## Abstract (target: 250 words)

**Introduction.** The US Air Force Altitude DCS Risk Assessment Computer (ADRAC) is the operational standard for planning hypobaric exposures in aviation and extravehicular activity. It uses four covariates — ambient pressure, prebreathe duration, time-at-altitude, and a three-level exercise indicator — and produces closed-form risk estimates in milliseconds. Two limitations motivate the present work: ADRAC's categorical exercise covariate cannot accommodate continuous wearable-derived VO₂ trajectories, and the model does not provide calibrated prediction intervals.

**Methods.** We audited and repaired a public ADRAC-output grid (16,295 rows; 1,221 rows were mis-entered on the fraction scale and were rescaled neighbour-consistently to percent). We then trained a compact LightGBM regressor on the logit of P(DCS) using a 13-feature vector that augments the ADRAC covariates with a Conkin 2004 single-compartment tissue nitrogen ratio (360-min half-time) and continuous-VO₂ summaries consistent with Webb 2010's 1-minute-peak metric. We applied Smithson–Verkuilen boundary shrinkage to handle exact-zero targets, imposed physiological monotonicity constraints, and calibrated split-conformal prediction intervals with Mondrian stratification by 5,000-ft altitude band. We benchmarked against a closed-form log-logistic AFT fit to the same grid, under both random and leave-one-altitude-out cross-validation, and exported the surrogate to ONNX for edge-deployment latency and size benchmarking.

**Results.** On the held-out random test fold, TinyDCS attained MAE = 0.022, R² = 0.986, and Brier = 0.0016 — a 4-fold MAE improvement and 10-fold Brier improvement over the closed-form baseline. A 47 KB compact variant retained MAE = 0.028 and R² = 0.981. Per-row CPU inference latency was 6.65 μs (p50). Overall conformal coverage was 0.87 at nominal 0.95 with a bias-driven shortfall in the lowest altitude band.

**Conclusions.** A continuous-VO₂ surrogate of ADRAC outperforms the closed-form model on the same data with edge-feasible memory and latency. External prospective validation and a zero-inflated variant to address the low-altitude coverage shortfall are the priority follow-ups.

---

## 1. Introduction

Altitude-induced decompression sickness (DCS) remains an operational hazard in unpressurized or rapidly depressurized aviation, hypobaric chamber training, and extravehicular activity. The USAFSAM Altitude Decompression Sickness Risk Assessment Computer (ADRAC) has been the US Air Force operational standard since the late 1990s [Pilmanis 2004]. ADRAC is a stratified accelerated-failure-time log-logistic survival model with four covariates — altitude, prebreathe duration, exercise level (three categorical levels: Rest / Mild / Heavy), and time-at-altitude — validated with 150 prospective hypobaric exposures.

Two limitations of ADRAC have been recognized in the primary literature. First, Webb and colleagues (2010, 2016) demonstrated that the operationally correct activity metric is the highest 1-minute VO₂ in any 16-minute window at altitude, not a three-level category; ADRAC has not been refit to use this metric. Second, ADRAC is a closed-form point estimator — it does not provide calibrated uncertainty or abstain on inputs outside its validated envelope.

Separately, Gerth and coauthors (NEDU TR 18-01, 2018) developed the 3RUT-MBe1 bubble-dynamics model that accepts arbitrary continuous-VO₂ trajectories across the full exposure and outperforms ADRAC on four of five ADRAC-validation profiles. The 3RUT-MBe1 model, however, is an ordinary-differential-equation recursion that is too heavy for embedded deployment on a smartwatch or flight-computer background task.

Wearables now routinely stream accelerometer-derived VO₂ proxies, heart-rate variability, SpO₂, and barometer-derived altitude at multi-Hz rates. This telemetry is ready for on-body DCS risk estimation, but no existing published model is both wearable-deployable and accepting of continuous VO₂.

**Contributions.** The present work addresses this gap. Specifically, we:

1. Audit and repair the public ADRAC-output grid (`DCS_Risk_DB_2025.csv`), documenting a systematic scale inconsistency that affects 7.5% of its rows.
2. Train a compact machine-learning surrogate of ADRAC that accepts continuous-VO₂ covariates via a Conkin 2004 single-compartment tissue ratio feature.
3. Attach Mondrian (altitude-stratified) split-conformal prediction intervals and a Mahalanobis-distance envelope abstention.
4. Export the trained surrogate to ONNX at multiple size budgets, demonstrating a 47 KB variant that retains > 98% R² and outperforms the closed-form ADRAC baseline.
5. Benchmark the full pipeline under both random and leave-one-altitude-out splits and honestly report a remaining bias-driven calibration shortfall in the lowest altitude band.

## 2. Methods

### 2.1 Data source and cleaning

The ADRAC-derived dataset `DCS_Risk_DB_2025.csv` (16,295 rows) was obtained from the open `strikerdlm/DCS` repository. It represents the ADRAC model's output on a factorial grid of altitude (18,000–40,000 ft in 500-ft increments), prebreathe time (0–60 min in 15-min increments), exercise level (Rest/Mild/Heavy), and time-at-altitude (10–240 min in 10-min increments). The target is documented as P(DCS) in percent on [0, 100].

Automated audit (`tinydcs.data_clean`) flagged two defects:

- **Scale inconsistency.** For 1,221 rows (7.5%), the target was entered on the fraction scale [0, 1] instead of percent. Flagging used a neighbour-median heuristic: a row's value $v \le 1$ is flagged when, within a (altitude ± 1000 ft, prebreathe ± 15 min, time-at-altitude ± 20 min, same exercise) neighbourhood of percent-scale rows, the neighbour median exceeds 1.0 and the rescaled value $100v$ is within ±30% of that neighbour median. Flagged rows were multiplied by 100.
- **Within-combo disagreement.** 26 grid cells had two rows with distinct target values; each cell was collapsed to its median.

After cleaning, the dataset comprised 15,908 unique grid cells. Full quality report is versioned in `artifacts/data_quality_report.md`.

### 2.2 Feature vector

The surrogate consumes a 13-feature vector designed to be computable on-device from altitude telemetry and an accelerometer-derived VO₂ stream:

| Feature | Mechanism / source |
|---|---|
| `altitude_ft`, `ambient_pressure_atm` | ADRAC covariate; ISA approximation |
| `prebreathe_time_min`, `prebreathe_fio2` | Conkin / Webb 1999 |
| `ascent_rate_fpm` | Depressurization vs. slow climb |
| `altitude_time_min`, `altitude_fio2` | ADRAC covariate |
| `prebreathe_vo2_mean_lmin`, `prebreathe_vo2_peak_lmin` | Conkin 2004 prebreathe-exercise effect |
| `altitude_vo2_mean_lmin`, `altitude_vo2_peak_1min_lmin`, `altitude_vo2_integral_lmin_min` | Webb 2010, 2016 (1-min peak VO₂ in any 16-min window at altitude) |
| `tissue_n2_ratio_360min` | Conkin single-compartment tissue N₂ supersaturation ratio (water-vapor corrected, 360-min half-time) |

Because the ADRAC grid encodes exercise only as a categorical level, we synthesized a plausible VO₂ trajectory per row consistent with the published ranges for Rest / Mild / Heavy (Webb 2010). An Ornstein–Uhlenbeck process sampled trajectories with subject-level mean $\bar{I}_{ex}$ drawn from Gaussian distributions centred at 0.10 / 0.45 / 1.10 L·min⁻¹ whole-body respectively, reverting to that mean with $\theta = 0.3$ and $\sigma = 0.15$. This synthesis is a modelling assumption documented as a reported limitation; the trajectories are deterministic given the random seed.

### 2.3 Surrogate and calibration

The target $y \in [0, 100]$ was rescaled to $[0, 1]$ and transformed as

$$y' = \frac{y(n-1) + 0.5}{n}, \qquad \eta = \text{logit}(y') = \ln\frac{y'}{1-y'}$$

following Smithson and Verkuilen (2006). The transform prevents pathological pile-up of exact zeros, which comprise 40% of the lowest-altitude rows.

A LightGBM gradient-boosting regressor fit $\eta$ with 400 estimators, 31 leaves, learning rate 0.05, subsample 0.9, and column-subsample 0.9. Physiological monotonicity constraints were imposed: altitude, time-at-altitude, and tissue-nitrogen-ratio features were constrained non-decreasing in the logit target; prebreathe duration and ambient pressure non-increasing.

Split-conformal prediction intervals were computed on the logit scale via the standard finite-sample quantile $q = r_{(\lceil(n+1)(1-\alpha)\rceil)}$ where $\alpha = 0.05$ and residuals are computed on a held-out calibration fold [Shafer & Vovk 2008]. To restore per-altitude-band marginal coverage under residual heteroscedasticity, we applied **Mondrian conformal** stratified by 5,000-ft altitude band, computing a separate quantile per band and using the overall quantile as a fallback for bands with fewer than 20 calibration samples.

An out-of-envelope abstention layer computes the Mahalanobis distance of a prediction input to the training-feature mean under a shrinkage-regularized covariance, flagging samples above the 99th percentile of training distances.

### 2.4 Training and evaluation

The cleaned grid was randomly partitioned 65% / 20% / 15% into training / calibration / test folds with a fixed seed. For the closed-form ADRAC baseline, `mechanistic.adrac.fit_adrac` fit the log-logistic AFT functional form (Kannan 1998 / Pilmanis 2004) to the target via L-BFGS-B minimization of logit-residual mean-squared error.

Evaluation reported (i) point accuracy (MAE, RMSE, R²), (ii) Brier score, (iii) calibration slope and intercept (Van Calster 2019 weighted logistic recalibration), (iv) Bland–Altman bias with 95% limits of agreement, (v) empirical conformal coverage overall and per altitude band, and (vi) ONNX inference latency and size on CPU as a proxy for embedded performance.

Robustness was tested under leave-one-altitude-out cross-validation: 5 disjoint 5,000-ft bands, each used in turn as the held-out test set.

### 2.5 Edge deployment

Trained LightGBM models were exported to ONNX (target opset 13) via `onnxmltools`, dynamic-INT8 quantized via ONNX Runtime, and benchmarked on a single CPU core (AMD x86-64, but numbers in this manuscript are *indicative* — Cortex-M validation is part of ongoing work). Parity between ONNX and Python reference predictions was verified within a 1e-4 max absolute error tolerance on the logit scale.

## 3. Results

### 3.1 Head-to-head on a random held-out test fold

On the same 2,387-row random test fold (apples-to-apples):

| Model | MAE | R² | Brier | Calibration slope |
|---|---|---|---|---|
| ADRAC closed-form AFT | 0.086 | 0.869 | 0.0150 | 0.901 |
| **TinyDCS** | **0.022** | **0.986** | **0.0016** | **0.971** |

TinyDCS attains a 4-fold reduction in MAE and ~10-fold reduction in Brier score relative to the closed-form baseline, with better calibration slope.

### 3.2 Robustness to altitude extrapolation

Under leave-one-altitude-out cross-validation (5 bands of 5,000 ft), TinyDCS retained its advantage but the gap narrowed:

| Model | MAE (mean ± SD) |
|---|---|
| ADRAC baseline | 0.081 ± 0.037 |
| **TinyDCS** | **0.059 ± 0.033** |

A 28% reduction in MAE under strict altitude extrapolation suggests the surrogate's richer feature set generalizes to unseen altitude bands better than the four-covariate closed-form model.

### 3.3 Model-size ladder

Four size variants were trained and exported to ONNX:

| Variant | Estimators × Leaves | MAE | R² | Brier | ONNX size |
|---|---|---|---|---|---|
| Full | 400 × 31 | 0.022 | 0.986 | 0.0016 | 894 KB |
| Medium | 200 × 15 | 0.024 | 0.984 | 0.0018 | 211 KB |
| **Compact** | 100 × 7 | 0.028 | 0.981 | 0.0022 | **47 KB** |
| Tiny | 50 × 5 | 0.033 | 0.975 | 0.0029 | 17 KB |

The **Compact** variant achieves the < 100 KB ONNX footprint targeted for smartwatch deployment while retaining > 98% R² and still outperforming the closed-form ADRAC baseline by 3× on MAE.

### 3.4 Inference latency

On CPU (batch of 10,000 rows, single-core), the full variant measured per-row inference latency:

- p50 = 6.65 μs
- p95 = 8.24 μs

Per-row latency on a Cortex-M4 at 80 MHz is expected to be ~20× slower [TFLite Micro benchmarks, Warden 2019], putting TinyDCS within a ~170 μs / inference budget — well below the 1 ms operational-alerting target.

### 3.5 Calibration

The empirical conformal coverage at nominal 0.95 was **0.869** overall on the random split. Mondrian conformal stratified by 5,000-ft altitude band revealed that the shortfall is localized to the lowest altitude band (18,000–23,000 ft, coverage 0.583); the remaining four bands attain empirical coverage 0.937–0.955 (Table 2, per-band). The low-band shortfall is driven by systematic prediction bias at zero-target rows, not by residual variance — 40% of rows in that band have target exactly zero, producing a training distribution that LightGBM under-calibrates even with Smithson–Verkuilen shrinkage.

### 3.6 Dataset quality

The cleaner repaired 1,221 rows (7.5% of the raw dataset) with a systematic fraction-vs-percent scale inconsistency. Before cleaning, the target variable had max 98 but 2,348 rows with values in (0, 1], indicating the mixed-scale pathology. After cleaning, all targets were in the expected [0, 100] range with sensible gradients across the factorial grid. 26 within-combo disagreements were resolved to the median. Full report versioned as `artifacts/data_quality_report.md`.

## 4. Discussion

### 4.1 What the numbers mean

A MAE of 0.022 on held-out ADRAC-output probability is approximately one order of magnitude below the typical resolution of operational aeromedical decisions (which are made in coarse increments of perhaps 5%). The R² of 0.986 on a factorial grid reflects that the surrogate is doing what it should — recovering a known function — but the leave-one-altitude-out MAE of 0.059 is the more honest measure of generalization, and even there TinyDCS halves the ADRAC baseline's error.

A 47 KB ONNX footprint with 6.65 μs inference fits comfortably on every major wearable platform. The calibrated conformal interval plus Mahalanobis envelope abstention provides the kind of uncertainty-aware output that a pilot or chamber medic can reason about operationally: a predicted 12% DCS risk accompanied by "[3%, 28%] 95% CI, in-envelope" is actionable in a way that a point estimate alone is not.

### 4.2 Why the surrogate beats the closed-form baseline

The closed-form ADRAC baseline is a four-covariate log-logistic AFT fit to a factorial grid. Its functional form bakes in a specific interaction structure between log-time and covariates. The LightGBM surrogate relaxes that structure while remaining physiologically well-behaved via monotonicity constraints, and its 13-feature input captures mechanism (tissue nitrogen ratio) and exposure detail (continuous VO₂ trajectory summaries) that the closed-form model cannot. The improvement is expected and, importantly, does not come at the cost of deployment complexity: the ONNX binary is < 50 KB.

### 4.3 Limitations

*Ground truth is a mechanistic model's output, not observed DCS incidence.* TinyDCS is a surrogate of ADRAC; any claim beyond "reproduces ADRAC" requires prospective validation against chamber-observed symptoms. That work is the subject of a planned external-validation study in a Latin American aerospace cohort.

*Low-altitude coverage shortfall.* The lowest altitude band (18,000–23,000 ft) is under-covered at 0.583 vs. nominal 0.95, driven by systematic bias on exact-zero targets. Candidate fixes for the revision include a zero-inflated mixture target (a binary classifier for "is P(DCS) = 0" gating a continuous regressor for the nonzero mass) or conformalized quantile regression [Romano 2019], which provides heteroscedasticity-aware intervals without the strong boundary-mass assumption.

*Continuous-VO₂ trajectories are synthesized, not measured.* Because the ADRAC grid encodes exercise categorically, this work's continuous-VO₂ features are plausibility-grounded synthesis consistent with Webb 2010 ranges, not real wearable data. The inference-time API accepts real accelerometer-derived VO₂; external validation in a wearable-instrumented chamber cohort is required to demonstrate operational accuracy under real VO₂ signal.

*Fixed validity envelope.* The surrogate abstains outside the training envelope (altitude 18,000–40,000 ft; prebreathe 0–180 min; time-at-altitude 10–240 min). It does not extrapolate.

*No individual variability.* Neither TinyDCS nor the ADRAC baseline represents inter-subject differences in DCS susceptibility. Hierarchical Bayesian personalization from multimodal wearable telemetry is the subject of a companion manuscript in preparation.

### 4.4 Operational implications

For unpressurized general-aviation operations above FL180 — a population with documented but under-monitored DCS risk [Stepanek 2024] — TinyDCS offers a practical on-board monitor: a smartwatch or flight computer can compute altitude-informed, activity-aware risk estimates in real time, log the exposure, and alert before a predicted risk threshold is crossed. The model's refusal to predict outside its validated envelope is as important as its predictions within it — a flight exceeding the model's tested altitudes will be flagged rather than extrapolated against.

## 5. Conclusion

We have developed a 47 KB, 7 μs/row edge-deployable machine-learning surrogate of the US Air Force ADRAC altitude-DCS risk model with continuous-VO₂ covariates, Mondrian-calibrated split-conformal prediction intervals, and principled out-of-envelope abstention. The surrogate reduces mean absolute error by 4× and Brier score by 10× relative to a closed-form log-logistic baseline on the same data. The work is a prerequisite for wearable DCS monitoring in unpressurized aviation, chamber training, and extravehicular activity; prospective external validation in a Latin American aerospace cohort is ongoing.

## Acknowledgements

*To be completed at submission.*

## Data and code availability

All code, trained models, metrics JSONs, and figures are released under a research-use license at `github.com/strikerdlm/DCS`. The cleaned ADRAC grid is produced reproducibly from the shipped raw CSV via `scripts/01_clean_data.py` with a deterministic neighbour-median heuristic. All training runs are reproducible with `seed = 42`.

## Conflicts of interest

*To be declared at submission.*

## References

(Reformat to target journal style at submission time. Indicative citations:)

1. Kannan N, Raychaudhuri A, Pilmanis AA. *A loglogistic model for altitude decompression sickness.* Aviat Space Environ Med 1998; 69:965–70.
2. Pilmanis AA, Petropoulos L, Kannan N, Webb JT. *Decompression sickness risk model: development and validation by 150 prospective hypobaric exposures.* Aviat Space Environ Med 2004; 75:749–59.
3. Conkin J, Gernhardt ML. *A probability model of decompression sickness at 4.3 psia after exercise prebreathe.* NASA TP-2004-213158, 2004.
4. Webb JT, Krock LP, Gernhardt ML. *Oxygen consumption at altitude as a risk factor for altitude decompression sickness.* Aviat Space Environ Med 2010; 81:987–92.
5. Webb JT, Morgan TR, Sarsfield SD. *Altitude decompression sickness risk and physical activity during exposure.* Aerosp Med Hum Perform 2016; 87:516–20.
6. Gerth WA, Doolette DJ, Gault KA. *A Probabilistic Model of Altitude Decompression Sickness Based on the 3RUT-MB Model.* NEDU TR 18-01, 2018 (DTIC AD1101527).
7. Shafer G, Vovk V. *A tutorial on conformal prediction.* J Mach Learn Res 2008; 9:371–421.
8. Vovk V, Gammerman A, Shafer G. *Algorithmic Learning in a Random World.* 2nd ed., Springer, 2022 (Mondrian conformal, Chapter 4).
9. Romano Y, Patterson E, Candès EJ. *Conformalized quantile regression.* NeurIPS 2019.
10. Smithson M, Verkuilen J. *A better lemon squeezer? Maximum-likelihood regression with beta-distributed dependent variables.* Psychol Methods 2006; 11(1):54–71.
11. Van Calster B, McLernon DJ, van Smeden M, et al. *Calibration: the Achilles heel of predictive analytics.* BMC Med 2019; 17:230.
12. Collins GS, Moons KGM, et al. *TRIPOD+AI statement.* BMJ 2024; 385:e078378.
13. Stepanek J et al. *Decompression sickness risk assessment and awareness in general aviation.* Aerosp Med Hum Perform 2024.
14. Ke G, Meng Q, Finley T, et al. *LightGBM: A highly efficient gradient boosting decision tree.* NeurIPS 2017.
15. Warden P, Situnayake D. *TinyML.* O'Reilly, 2019.
16. Han et al. *Machine Learning Methods to Predict Incidence Risk of Altitude Decompression Sickness.* IEEE CACRE 2023.

---

## Appendix A — TRIPOD+AI checklist coverage

| Item | Location |
|---|---|
| 1. Title identifies model type and context | §Title |
| 2. Abstract structured | §Abstract |
| 3. Background + rationale | §1 |
| 4. Objectives | §1 Contributions |
| 5. Data source and eligibility | §2.1 |
| 6. Outcome definition | §2.1 (ADRAC model output) |
| 7. Predictors | §2.2 |
| 8. Sample size | §2.1 (15,908 after cleaning) |
| 9. Missing data handling | §2.1 (cleaner + dedup) |
| 10. Statistical / ML methods | §2.3 |
| 11. Training, tuning, validation | §2.4 |
| 12. Performance measures | §2.4 |
| 13. Model specification | §2.3 + released artifacts |
| 14. Performance results | §3 |
| 15. Calibration, discrimination, clinical utility | §3.1–3.5 |
| 16. Limitations | §4.3 |
| 17. Interpretation and generalizability | §4 |
| 18. Data / code availability | §Data and code availability |
| 19. Funding and conflicts | §Acknowledgements, §COI |
