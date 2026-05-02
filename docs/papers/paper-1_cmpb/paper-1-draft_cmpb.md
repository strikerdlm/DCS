---
title: 'TinyDCS: An edge-deployable machine-learning surrogate of the ADRAC altitude-decompression-sickness risk model with continuous-exposure covariates and calibrated uncertainty'

running-title: 'TinyDCS: edge surrogate of ADRAC'
running-authors: 'Malpica \& Farfán'

article-type: 'Full Length Article'
journal-line: '\textit{Computer Methods and Programs in Biomedicine} (Elsevier) --- under review'

author-line: 'Diego Malpica, MD\textsuperscript{1*}\enspace·\enspace Marian Farfán, MD\textsuperscript{1}'

affil-1: 'Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine, Colombian Aerospace Force, Bogotá DC, Colombia'

correspondence: 'diego.malpica@fac.mil.co'

pdf-author: 'Malpica D, Farfán M'

wordcount: 'approx. 2,800 (body) --- 320 (abstract) --- 16 references'
version: '1.0.0 --- 2026-05-01 (CMPB submission)'

repository: 'github.com/strikerdlm/DCS'

abstract-background-and-objectives: 'The US Air Force ADRAC altitude-decompression-sickness risk model [1] is the operational standard for planning hypobaric exposures, but its three-level exercise covariate cannot ingest continuous wearable-derived VO\textsubscript{2} trajectories and it returns point estimates without calibrated uncertainty. We aimed to build a wearable-grade machine-learning surrogate of the ADRAC grid that (i) accepts continuous-VO\textsubscript{2} covariates, (ii) ships calibrated 95\% prediction intervals with uniform altitude-band coverage, (iii) abstains outside the validated input envelope, and (iv) meets an edge-deployment footprint below 100 KB with per-inference latency below 10 \textmu{}s.'

abstract-methods: 'After cleaning a public 16,295-row ADRAC-output grid (15,908 unique cells; 7.5\% rescaled from fraction to percent), we trained a LightGBM regressor on the logit of P(DCS) using a 13-feature vector that augments the ADRAC covariates with a Conkin tissue-nitrogen ratio [6] and continuous-VO\textsubscript{2} summaries (Webb 2010 1-min peak [2]). Monotonicity constraints, Smithson--Verkuilen boundary shrinkage [8], and a two-stage zero-inflated split-conformal stack [9,10] with Mahalanobis-distance out-of-envelope abstention were applied. The surrogate was benchmarked against a closed-form log-logistic AFT and exported to ONNX.'

abstract-results: 'On the held-out random test fold (\textit{n} = 2,386), TinyDCS attained MAE = 0.020, R\textsuperscript{2} = 0.986, and Brier score = 0.0016 --- a 4-fold MAE reduction and 10-fold Brier reduction over the closed-form baseline (MAE = 0.086; Brier = 0.0150). Empirical 95\% coverage was 0.960 overall and at least 0.95 in each of the five 5,000-ft altitude bands, closing a low-band shortfall (coverage 0.58--0.59 at 18,000--23,000 ft) that was invariant under four conformal-only alternatives. A compact zero-inflated variant compiled to 95 KB of ONNX with CPU per-row latency of 2.44 \textmu{}s (p50). A conjugate-Gaussian hierarchical personalisation prototype recovered per-subject log-susceptibility at Pearson \textit{r} = 0.63 after twenty exposures per subject.'

abstract-conclusions: 'A continuous-VO\textsubscript{2} ADRAC surrogate with zero-inflated conformal calibration and out-of-envelope abstention outperforms the closed-form model on the same data at an edge-feasible memory and latency budget. External prospective validation on a hypobaric-chamber cohort with Doppler venous-gas-emboli ground truth, and replacement of the conjugate-Gaussian personalisation stub with a full hierarchical Bayesian model on real subjects, are the priority follow-ups.'

abstract-keywords: 'altitude decompression sickness; ADRAC; wearable computing; conformal prediction; zero-inflated models; edge AI; aerospace medicine; hierarchical Bayesian personalisation'

---

<!-- ============================================================
     Body begins. The YAML frontmatter above is consumed by the
     npj-pdf-export template; this body is $body$ in the PDF.
     ============================================================ -->

## 1. Introduction

Altitude-induced decompression sickness (DCS) remains an operational hazard in unpressurised or rapidly depressurised aviation, hypobaric chamber training, and extravehicular activity. The USAFSAM Altitude Decompression Sickness Risk Assessment Computer (ADRAC) has been the US Air Force operational standard since the late 1990s [1]. ADRAC is a stratified accelerated-failure-time log-logistic survival model with four covariates — altitude, prebreathe duration, exercise level (three categorical levels: Rest / Mild / Heavy), and time-at-altitude — validated with 150 prospective hypobaric exposures.

Two limitations of ADRAC have been recognised in the primary literature. First, Webb and colleagues [2,3] demonstrated that the operationally correct activity metric is the highest 1-minute VO\textsubscript{2} in any 16-minute window at altitude, not a three-level category; ADRAC has not been refit to use this metric. Second, ADRAC is a closed-form point estimator — it does not provide calibrated uncertainty or abstain on inputs outside its validated envelope.

Separately, Gerth and coauthors [4] developed the 3RUT-MBe1 bubble-dynamics model that accepts arbitrary continuous-VO\textsubscript{2} trajectories across the full exposure and outperforms ADRAC on four of five ADRAC-validation profiles. The 3RUT-MBe1 model, however, is an ordinary-differential-equation recursion that is too heavy for embedded deployment on a smartwatch or flight-computer background task. A recent random-forest study by Han and colleagues [5] applied general-purpose ML to ADRAC-derived data but did not address calibrated uncertainty or edge deployment.

Wearables now routinely stream accelerometer-derived VO\textsubscript{2} proxies, heart-rate variability, SpO\textsubscript{2}, and barometer-derived altitude at multi-Hz rates. This telemetry is ready for on-body DCS risk estimation, but no existing published model is both wearable-deployable and accepting of continuous VO\textsubscript{2}.

**Contributions.** The present work addresses this gap. Specifically, we:

1. Audit and repair the public ADRAC-output grid (`DCS_Risk_DB_2025.csv`), documenting a systematic scale inconsistency that affects 7.5% of its rows.
2. Train a compact machine-learning surrogate of ADRAC that accepts continuous-VO\textsubscript{2} covariates via a Conkin 2004 single-compartment tissue ratio feature.
3. Attach Mondrian (altitude-stratified) split-conformal prediction intervals [9,10], a two-stage zero-inflated calibration that closes a low-altitude-band coverage shortfall, and a Mahalanobis-distance envelope abstention.
4. Export the trained zero-inflated surrogate to ONNX at multiple size budgets, demonstrating a 95 KB combined variant that retains R² > 0.98 and outperforms the closed-form ADRAC baseline by 3× on MAE.
5. Benchmark the full pipeline under both random and leave-one-altitude-out splits; release a reproducibility package (runbook, AGENTS.md continuation guide, trained weights, ONNX artifacts, metrics JSONs, paper figures, TRIPOD+AI checklist).
6. Prototype a conjugate-Gaussian hierarchical personalisation layer on a synthetic cohort, quantifying the number of per-subject exposures required to reach Brier parity with the population model.

## 2. Methods

### 2.1 Data source and cleaning

The ADRAC-derived dataset `DCS_Risk_DB_2025.csv` (16,295 rows) was obtained from the open `strikerdlm/DCS` repository. It represents the ADRAC model's output on a factorial grid of altitude (18,000–40,000 ft in 500-ft increments), prebreathe time (0–60 min in 15-min increments), exercise level (Rest/Mild/Heavy), and time-at-altitude (10–240 min in 10-min increments). The target is documented as P(DCS) in percent on [0, 100].

Automated audit (`tinydcs.data_clean`) flagged two defects:

- **Scale inconsistency.** For 1,221 rows (7.5%), the target was entered on the fraction scale [0, 1] instead of percent. Flagging used a neighbour-median heuristic: a row's value $v \le 1$ is flagged when, within a (altitude ± 1000 ft, prebreathe ± 15 min, time-at-altitude ± 20 min, same exercise) neighbourhood of percent-scale rows, the neighbour median exceeds 1.0 and the rescaled value $100v$ is within ±30% of that neighbour median. Flagged rows were multiplied by 100.
- **Within-combo disagreement.** 26 grid cells had two rows with distinct target values; each cell was collapsed to its median.

After cleaning, the dataset comprised 15,908 unique grid cells. Full quality report is versioned in `artifacts/data_quality_report.md`.

### 2.2 Feature vector

The surrogate consumes a 13-feature vector designed to be computable on-device from altitude telemetry and an accelerometer-derived VO\textsubscript{2} stream:

| Feature | Mechanism / source |
|---|---|
| `altitude_ft`, `ambient_pressure_atm` | ADRAC covariate; ISA approximation |
| `prebreathe_time_min`, `prebreathe_fio2` | Conkin / Webb [6] |
| `ascent_rate_fpm` | Depressurisation vs. slow climb |
| `altitude_time_min`, `altitude_fio2` | ADRAC covariate |
| `prebreathe_vo2_mean_lmin`, `prebreathe_vo2_peak_lmin` | Conkin [6] prebreathe-exercise effect |
| `altitude_vo2_mean_lmin`, `altitude_vo2_peak_1min_lmin`, `altitude_vo2_integral_lmin_min` | Webb [2,3] (1-min peak VO\textsubscript{2} in any 16-min window at altitude) |
| `tissue_n2_ratio_360min` | Conkin single-compartment tissue N\textsubscript{2} supersaturation ratio [6] (water-vapour corrected, 360-min half-time) |

Because the ADRAC grid encodes exercise only as a categorical level, we synthesised a plausible VO\textsubscript{2} trajectory per row consistent with the published ranges for Rest / Mild / Heavy [2]. An Ornstein–Uhlenbeck process sampled trajectories with subject-level mean $\bar{I}_{ex}$ drawn from Gaussian distributions centred at 0.10 / 0.45 / 1.10 L\textperiodcentered{}min\textsuperscript{-1} whole-body respectively, reverting to that mean with $\theta = 0.3$ and $\sigma = 0.15$. This synthesis is a modelling assumption documented as a reported limitation; the trajectories are deterministic given the random seed.

### 2.3 Surrogate and calibration

The target $y \in [0, 100]$ was rescaled to $[0, 1]$ and transformed as

$$y' = \frac{y(n-1) + 0.5}{n}, \qquad \eta = \text{logit}(y') = \ln\frac{y'}{1-y'}$$

following Smithson and Verkuilen [8]. The transform prevents pathological pile-up of exact zeros, which comprise 40% of the lowest-altitude rows.

A LightGBM gradient-boosting regressor [7] fit $\eta$ with 400 estimators, 31 leaves, learning rate 0.05, subsample 0.9, and column-subsample 0.9. Physiological monotonicity constraints were imposed: altitude, time-at-altitude, and tissue-nitrogen-ratio features were constrained non-decreasing in the logit target; prebreathe duration and ambient pressure non-increasing.

Split-conformal prediction intervals were computed on the logit scale via the standard finite-sample quantile $q = r_{(\lceil(n+1)(1-\alpha)\rceil)}$ where $\alpha = 0.05$ and residuals are computed on a held-out calibration fold [9]. To restore per-altitude-band marginal coverage under residual heteroscedasticity, we applied **Mondrian conformal** [10] stratified by 5,000-ft altitude band, computing a separate quantile per band and using the overall quantile as a fallback for bands with fewer than 20 calibration samples. We also evaluated conformalised quantile regression (CQR) [11] as an ablation calibration mode.

An out-of-envelope abstention layer computes the Mahalanobis distance of a prediction input to the training-feature mean under a shrinkage-regularized covariance, flagging samples above the 99th percentile of training distances. The three-layer stack — wearable input / LightGBM logit core / conformal calibration — is schematised in Figure 1.

```{=latex}
\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\linewidth]{artifacts/paper_figures/fig5_architecture.pdf}
\caption{\textbf{TinyDCS system architecture.} Block diagram of the three-layer inference stack: (1) wearable sensor input layer producing a 13-feature vector from altitude telemetry and accelerometer-derived VO\textsubscript{2}; (2) LightGBM logit core with monotonicity constraints and Mahalanobis OOD gate; (3) zero-inflated conformal calibration layer returning a point estimate plus a calibrated 95\% interval. ONNX artifacts are shown at the edge-deployment node.}
\label{fig:architecture}
\end{figure}
```

### 2.4 Training and evaluation

The cleaned grid was randomly partitioned 65% / 20% / 15% into training / calibration / test folds with a fixed seed. For the closed-form ADRAC baseline, `mechanistic.adrac.fit_adrac` fit the log-logistic AFT functional form [12,1] to the target via L-BFGS-B minimisation of logit-residual mean-squared error.

Evaluation reported (i) point accuracy (MAE, RMSE, R²), (ii) Brier score, (iii) calibration slope and intercept [13] (weighted logistic recalibration), (iv) Bland–Altman bias with 95% limits of agreement, (v) empirical conformal coverage overall and per altitude band, and (vi) ONNX inference latency and size on CPU as a proxy for embedded performance. Reporting follows the TRIPOD+AI guidance [16] (Appendix A).

Robustness was tested under leave-one-altitude-out cross-validation: 5 disjoint 5,000-ft bands, each used in turn as the held-out test set.

### 2.5 Edge deployment

Trained LightGBM models were exported to ONNX (target opset 13) via `onnxmltools`, dynamic-INT8 quantised via ONNX Runtime, and benchmarked on a single CPU core (AMD x86-64, but numbers in this manuscript are *indicative* — Cortex-M validation is part of ongoing work). Parity between ONNX and Python reference predictions was verified within a 1e-4 max absolute error tolerance on the logit scale.

## 3. Results

### 3.1 Head-to-head on a random held-out test fold

On the same 2,386-row random test fold (apples-to-apples):

| Model | MAE | R² | Brier | Calibration slope |
|---|---|---|---|---|
| ADRAC closed-form AFT | 0.086 | 0.869 | 0.0150 | 0.613 |
| **TinyDCS (zero-inflated)** | **0.020** | **0.986** | **0.0016** | **0.970** |

TinyDCS attains a 4-fold reduction in MAE and ~10-fold reduction in Brier score relative to the closed-form baseline, with a calibration slope (0.970) much closer to the ideal of 1.0 than the baseline's 0.613. Reliability across the full probability range is shown in Figure 2.

```{=latex}
\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\linewidth]{artifacts/paper_figures/fig1_reliability_diagram.pdf}
\caption{\textbf{Reliability diagram --- TinyDCS vs. closed-form ADRAC baseline.} Predicted P(DCS) bins (x-axis) versus empirical observed fraction (y-axis) on the held-out test fold (\textit{n} = 2,386). Perfect calibration lies on the diagonal. TinyDCS (zero-inflated two-stage) tracks the diagonal closely across the full probability range; the closed-form AFT baseline shows systematic overestimation at low probabilities.}
\label{fig:reliability}
\end{figure}
```

### 3.2 Robustness to altitude extrapolation

Under leave-one-altitude-out cross-validation (5 bands of 5,000 ft), TinyDCS retained its advantage but the gap narrowed:

| Model | MAE (mean ± SD) |
|---|---|
| ADRAC baseline | 0.081 ± 0.037 |
| **TinyDCS** | **0.059 ± 0.033** |

A 28% reduction in MAE under strict altitude extrapolation suggests the surrogate's richer feature set generalizes to unseen altitude bands better than the four-covariate closed-form model.

### 3.3 Model-size ladder and edge deployment

Because the zero-inflated surrogate is the production default, each deployable variant consists of a matched pair of LightGBM models (binary classifier + continuous regressor). We trained four size variants of the pair and exported both stages to ONNX:

| Variant | Estimators × Leaves | MAE | R² | Coverage | Classifier | Regressor | **Combined** | p50 latency |
|---|---|---|---|---|---|---|---|---|
| Full | 400 × 31 | 0.020 | 0.986 | 0.960 | 896 KB | 891 KB | 1,787 KB | 16.5 μs |
| Medium | 200 × 15 | 0.023 | 0.984 | 0.956 | 212 KB | 211 KB | 423 KB | 6.1 μs |
| **Compact** | 100 × 7 | 0.028 | 0.981 | 0.953 | 47 KB | 47 KB | **95 KB** | **2.44 μs** |
| Tiny | 50 × 5 | 0.033 | 0.975 | 0.948 | 17 KB | 17 KB | 34 KB | 1.9 μs |

The **Compact** variant is the headline: it achieves the 100 KB combined ONNX footprint targeted for smartwatch and flight-watch deployment while retaining R² > 0.98, closing the low-band coverage shortfall (see §3.5), and still outperforming the closed-form ADRAC baseline by 3× on MAE. The Pareto frontier of ONNX size versus MAE is shown in Figure 3.

```{=latex}
\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\linewidth]{artifacts/paper_figures/fig3_size_vs_accuracy.pdf}
\caption{\textbf{ONNX model size versus MAE --- Pareto frontier across the size ladder.} Log-scale x-axis (ONNX file size in KB) versus MAE on the held-out test fold. Four TinyDCS variants (Tiny, Compact, Medium, Full) and the closed-form ADRAC baseline are plotted. The Compact variant achieves the target edge-deployment footprint while dominating the baseline by 3\texttimes{} on MAE.}
\label{fig:size-accuracy}
\end{figure}
```

### 3.4 Inference latency and embedded feasibility

CPU per-row inference latency (single AMD x86-64 core, batch 10,000 rows) for the Compact zero-inflated pair:

- p50 = 2.44 μs / row
- p95 = 3.31 μs / row

The Full variant measured 16.5 μs p50. ONNX-to-Python parity was verified within 6.4 × $10^{-7}$ max absolute error on P(y = 0) and 4.9 × $10^{-6}$ on the continuous logit — well below the $10^{-4}$ target. Per-row latency on a Cortex-M4 at 80 MHz is expected to be ~20× slower than server CPU under TFLite Micro-style quantised kernels [14], giving the Compact variant an operational budget of ~50 μs / inference on bare metal — two orders of magnitude below the 1 ms wearable-alerting target. Direct Cortex-M validation remains part of ongoing work.

### 3.5 Calibration

We compared five calibration strategies on the same random test fold. Per-altitude-band coverage is the diagnostic:

| Calibration | Overall | 18–23K ft | 23–28K ft | 28–33K ft | 33–38K ft | 38–43K ft |
|---|---|---|---|---|---|---|
| Global conformal | 0.869 | 0.591 | 0.933 | 0.944 | 0.967 | 0.948 |
| Mondrian | 0.869 | 0.583 | 0.949 | 0.945 | 0.954 | 0.955 |
| CQR (global q) | 0.864 | 0.589 | 0.937 | 0.945 | 0.945 | 0.937 |
| Mondrian-CQR | 0.865 | 0.589 | 0.924 | 0.959 | 0.951 | 0.937 |
| **Zero-inflated two-stage** | **0.960** | **0.964** | **0.953** | **0.951** | **0.967** | **0.966** |

Four conformal-only methods produce near-nominal coverage in the four upper bands (0.92–0.97) but are invariant at 0.58–0.59 in the lowest altitude band. The invariance across methods is diagnostic: the shortfall is target-distribution pathology rather than residual variance. Routing the ~40% exact-zero mass through a dedicated binary classifier (stage 1), with the continuous regressor (stage 2) trained only on non-zero rows, closes the gap entirely — the 18,000–23,000 ft band reaches 0.964 and overall coverage is 0.960. The zero-inflated model is therefore adopted as the default calibration for all headline numbers; the three conformal-only modes remain available as ablations. Per-altitude-band coverage profiles for all five strategies are shown in Figure 4.

```{=latex}
\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\linewidth]{artifacts/paper_figures/fig2_per_band_coverage.pdf}
\caption{\textbf{Per-altitude-band 95\% conformal coverage --- five calibration strategies.} Grouped bars showing empirical coverage in each 5,000-ft altitude band for five calibration methods on the same test fold. Four conformal-only methods (global, Mondrian, CQR, Mondrian-CQR) are invariant at 0.58--0.59 in the 18,000--23,000 ft band. The zero-inflated two-stage method achieves $\geq$ 0.95 coverage in all five bands.}
\label{fig:coverage}
\end{figure}
```

### 3.6 Personalisation prototype

A conjugate-Gaussian hierarchical model placed a Gaussian prior on per-subject log-susceptibility (prior mean and variance fit to the population distribution) and updated it via Bayes' rule after each observed exposure. On a synthetic 200-subject cohort (true susceptibilities drawn from the prior, DCS outcomes simulated with the TinyDCS point estimate as the population rate), the model recovered per-subject log-susceptibility at Pearson *r* = 0.63 after twenty exposures per subject. Population-level versus personalized Brier parity crossover occurred near *k* = 10 exposures. These results establish feasibility and scope for Paper 2 (full hierarchical Bayesian model on real chamber cohort data). The information-gain curve is shown in Figure 5.

```{=latex}
\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\linewidth]{artifacts/paper_figures/fig4_personalization_info_gain.pdf}
\caption{\textbf{Personalisation information gain --- per-subject susceptibility recovery.} Left y-axis: Pearson \textit{r} between true and posterior-mean log-susceptibility (synthetic 200-subject cohort) as a function of observed exposures \textit{k} per subject. Right y-axis: Brier score for population-level (flat prior) versus personalised predictions. Crossover near \textit{k} = 10 indicates the exposure count at which personalisation begins to outperform the population model.}
\label{fig:personalisation}
\end{figure}
```

### 3.7 Dataset quality

The cleaner repaired 1,221 rows (7.5% of the raw dataset) with a systematic fraction-vs-percent scale inconsistency. Before cleaning, the target variable had max 98 but 2,348 rows with values in (0, 1], indicating the mixed-scale pathology. After cleaning, all targets were in the expected [0, 100] range with sensible gradients across the factorial grid. 26 within-combo disagreements were resolved to the median. Full report versioned as `artifacts/data_quality_report.md`.

## 4. Discussion

### 4.1 What the numbers mean

A MAE of 0.020 on held-out ADRAC-output probability is approximately one order of magnitude below the typical resolution of operational aeromedical decisions (which are made in coarse increments of perhaps 5%). The R² of 0.986 on a factorial grid reflects that the surrogate is doing what it should — recovering a known function — but the leave-one-altitude-out MAE of 0.059 is the more honest measure of generalization, and even there TinyDCS reduces the ADRAC baseline's error by 28%.

A 95 KB combined ONNX footprint with 2.44 μs p50 inference fits comfortably on every major wearable platform — a smartwatch main processor executes more than a million such inferences per second while still meeting its display and notification duties. The calibrated zero-inflated interval plus Mahalanobis envelope abstention provides the kind of uncertainty-aware output that a pilot or chamber medic can reason about operationally: a predicted 12% DCS risk accompanied by "[3%, 28%] 95% CI, in-envelope" is actionable in a way that a point estimate alone is not.

### 4.2 Why the surrogate beats the closed-form baseline

The closed-form ADRAC baseline is a four-covariate log-logistic AFT fit to a factorial grid. Its functional form bakes in a specific interaction structure between log-time and covariates. The LightGBM surrogate relaxes that structure while remaining physiologically well-behaved via monotonicity constraints, and its 13-feature input captures mechanism (tissue nitrogen ratio) and exposure detail (continuous VO\textsubscript{2} trajectory summaries) that the closed-form model cannot. The improvement is expected and, importantly, does not come at the cost of deployment complexity: the combined ONNX pair is under 100 KB.

### 4.3 Limitations

*Ground truth is a mechanistic model's output, not observed DCS incidence.* TinyDCS is a surrogate of ADRAC; any claim beyond "reproduces ADRAC with richer covariates and calibrated uncertainty" requires prospective validation against chamber-observed symptoms. That work is the subject of a planned external-validation study in the Colombian CEMAE hypobaric chamber with Doppler venous-gas-emboli ground truth (Paper 3 scope).

*Zero-inflated calibration was necessary; mean-only calibration would not have sufficed.* Early variants produced an invariant 0.583 coverage in the 18,000–23,000 ft band across four conformal-only calibration modes (global, Mondrian, CQR, Mondrian-CQR). The invariance of the shortfall across methods was diagnostic: it reflected target-distribution pathology, not residual-variance error. Because ~40% of rows in the low-altitude band have target exactly zero, a mean regressor trained on the whole grid cannot represent that mass cleanly. The two-stage zero-inflated architecture — a LightGBM classifier for P(y = 0 $\mid$ x) gating a continuous regressor trained only on non-zero rows — closes the gap entirely and is adopted as the production default. The three conformal-only calibration modes remain available in the public API as ablations; Mondrian-CQR in particular produces intervals ~50% narrower than Mondrian conformal in the four upper altitude bands while maintaining coverage, which is a genuine efficiency advantage when a calibrated-but-narrow interval is preferred to the zero-inflated default.

*Continuous-VO\textsubscript{2} trajectories are synthesised, not measured.* Because the ADRAC grid encodes exercise categorically, this work's continuous-VO\textsubscript{2} features are plausibility-grounded synthesis consistent with Webb 2010 ranges, not real wearable data. The inference-time API accepts real accelerometer-derived VO\textsubscript{2}; external validation in a wearable-instrumented chamber cohort is required to demonstrate operational accuracy under real VO\textsubscript{2} signal.

*Fixed validity envelope.* The surrogate abstains outside the training envelope (altitude 18,000–40,000 ft; prebreathe 0–180 min; time-at-altitude 10–240 min). It does not extrapolate.

*No individual variability.* Neither TinyDCS nor the ADRAC baseline represents inter-subject differences in DCS susceptibility. Hierarchical Bayesian personalisation from multimodal wearable telemetry is the subject of a companion manuscript in preparation.

### 4.4 Operational implications

For unpressurised general-aviation operations above FL180 — a population with documented but under-monitored DCS risk [15] — TinyDCS offers a practical on-board monitor: a smartwatch or flight computer can compute altitude-informed, activity-aware risk estimates in real time, log the exposure, and alert before a predicted risk threshold is crossed. The model's refusal to predict outside its validated envelope is as important as its predictions within it — a flight exceeding the model's tested altitudes will be flagged rather than extrapolated against.

## 5. Conclusion

We have developed a 95 KB combined, 2.44 μs/row edge-deployable machine-learning surrogate of the US Air Force ADRAC altitude-DCS risk model with continuous-VO\textsubscript{2} covariates, zero-inflated conformal prediction intervals with uniform altitude-band coverage, and principled Mahalanobis-distance out-of-envelope abstention. The surrogate reduces mean absolute error by 4× and Brier score by 10× relative to a closed-form log-logistic baseline on the same data, while preserving a calibration slope close to 1.0. A conjugate-Gaussian hierarchical personalisation prototype quantifies the per-subject exposure count at which individualisation matches the population model (k ≈ 10), setting the scope for a companion manuscript. The work is a prerequisite for wearable DCS monitoring in unpressurised aviation, chamber training, and extravehicular activity; prospective external validation in a Colombian chamber cohort is the immediate next step.

## Author contributions (CRediT)

**Diego Malpica:** Conceptualisation, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing — original draft, Writing — review and editing, Visualisation, Supervision, Project administration.

**Marian Farfán:** Conceptualisation, Methodology, Investigation, Writing — review and editing, Resources.

All authors read and approved the final version of the manuscript.

## Use of generative AI

During the preparation of this work, the authors used Claude Code (Anthropic Claude Opus 4.7) as a coding and prose-revision assistant under direct human supervision. AI tools were used to (i) accelerate boilerplate code (e.g. ONNX export wrappers and plotting scripts), (ii) suggest manuscript phrasing on non-scientific passages, and (iii) cross-check formatting against journal guidelines. AI tools were not used to generate scientific content, design experiments, fabricate or alter data, draft results or interpretation, or produce figures, tables, or citations without manual verification. All scientific claims and numerical results were derived from the released code base and verified by the authors. After using these tools, the authors reviewed and edited the content as needed and take full responsibility for the content of the publication.

## Declaration of competing interests

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Funding

This work received no external funding. The work was conducted as part of the authors' duties at the Colombian Aerospace Force, Direction of Aerospace Medicine.

## Data and code availability

All code, the cleaned ADRAC-derived dataset, trained model bundles (joblib), ONNX artefacts at four size tiers, metrics JSONs, paper figures, the TRIPOD+AI checklist, and a command-by-command reproduction guide are released under a research-use license at https://github.com/strikerdlm/DCS (default branch `main`, tagged release at the time of submission). All training runs are reproducible from the shipped raw CSV with `seed = 42` in under three minutes on CPU via `docs/runbook.md`. No restricted data are involved.

## Acknowledgements

The authors thank the Jefatura de Educación Aeronáutica y Espacial (Aeronautics and Space Education Directorate) and the Jefatura de Salud (Health Directorate) of the Colombian Aerospace Force for their institutional support of this research. We are grateful to CR Julio Blanco, MY Nindre Pico, MY Luis Eduardo Jerez, TS Bernabé Cardona, T1 Ever Buitrago, T1 Angie Alvarado, and T1 Rafael Salamanca for their thoughtful review, technical input, and the team effort that made this work possible.

## References

[1] Pilmanis AA, Petropoulos L, Kannan N, Webb JT. Decompression sickness risk model: development and validation by 150 prospective hypobaric exposures. Aviat Space Environ Med 2004;75:749–59.

[2] Webb JT, Krock LP, Gernhardt ML. Oxygen consumption at altitude as a risk factor for altitude decompression sickness. Aviat Space Environ Med 2010;81:987–92.

[3] Webb JT, Morgan TR, Sarsfield SD. Altitude decompression sickness risk and physical activity during exposure. Aerosp Med Hum Perform 2016;87:516–20. https://doi.org/10.3357/AMHP.4477.2016.

[4] Gerth WA, Doolette DJ, Gault KA. A probabilistic model of altitude decompression sickness based on the 3RUT-MB model. Navy Experimental Diving Unit Technical Report NEDU TR 18-01; 2018. DTIC accession AD1101527.

[5] Han Y, et al. Machine learning methods to predict incidence risk of altitude decompression sickness. Proc IEEE Int Conf Comput Aerosp Robot Eng (CACRE); 2023.

[6] Conkin J, Gernhardt ML. A probability model of decompression sickness at 4.3 psia after exercise prebreathe. NASA Technical Paper TP-2004-213158; 2004.

[7] Ke G, Meng Q, Finley T, Wang T, Chen W, Ma W, et al. LightGBM: a highly efficient gradient boosting decision tree. Adv Neural Inf Process Syst (NeurIPS) 2017;30:3146–54.

[8] Smithson M, Verkuilen J. A better lemon squeezer? Maximum-likelihood regression with beta-distributed dependent variables. Psychol Methods 2006;11(1):54–71. https://doi.org/10.1037/1082-989X.11.1.54.

[9] Shafer G, Vovk V. A tutorial on conformal prediction. J Mach Learn Res 2008;9:371–421.

[10] Vovk V, Gammerman A, Shafer G. Algorithmic learning in a random world. 2nd ed. Springer; 2022 (Mondrian conformal, Chapter 4). https://doi.org/10.1007/978-3-031-06649-8.

[11] Romano Y, Patterson E, Candès EJ. Conformalized quantile regression. Adv Neural Inf Process Syst (NeurIPS) 2019;32:3543–53.

[12] Kannan N, Raychaudhuri A, Pilmanis AA. A loglogistic model for altitude decompression sickness. Aviat Space Environ Med 1998;69:965–70.

[13] Van Calster B, McLernon DJ, van Smeden M, Wynants L, Steyerberg EW; Topic Group 'Evaluating diagnostic tests and prediction models' of the STRATOS initiative. Calibration: the Achilles heel of predictive analytics. BMC Med 2019;17:230. https://doi.org/10.1186/s12916-019-1466-7.

[14] Warden P, Situnayake D. TinyML: machine learning with TensorFlow Lite on Arduino and ultra-low-power microcontrollers. Sebastopol (CA): O'Reilly Media; 2019.

[15] Stepanek J, et al. Decompression sickness risk assessment and awareness in general aviation. Aerosp Med Hum Perform 2024.

[16] Collins GS, Moons KGM, Dhiman P, Riley RD, Beam AL, Van Calster B, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ 2024;385:e078378. https://doi.org/10.1136/bmj-2023-078378.

---

## Appendix A — TRIPOD+AI [16] checklist coverage

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
| 15. Calibration, discrimination, clinical utility | §3.1–3.5, Fig. 1–3 |
| 16. Limitations | §4.3 |
| 17. Interpretation and generalisability | §4 |
| 18. Data / code availability | §Data and code availability |
| 19. Funding and conflicts | §Funding, §Declaration of competing interests |

---

## Figure captions

**Figure 1. TinyDCS system architecture.** Block diagram of the three-layer inference stack: (1) wearable sensor input layer producing a 13-feature vector from altitude telemetry and accelerometer-derived VO₂; (2) LightGBM logit core with monotonicity constraints and Mahalanobis OOD gate; (3) zero-inflated conformal calibration layer returning a point estimate plus a calibrated 95 % interval. ONNX artefacts are shown at the edge-deployment node.

**Figure 2. Reliability diagram — TinyDCS vs. closed-form ADRAC baseline.** Predicted P(DCS) bins (x-axis) versus empirical observed fraction (y-axis) on the held-out test fold (*n* = 2,386). Perfect calibration lies on the diagonal. TinyDCS (zero-inflated two-stage) tracks the diagonal closely across the full probability range; the closed-form AFT baseline shows systematic overestimation at low probabilities.

**Figure 3. ONNX model size versus MAE — Pareto frontier across the size ladder.** Log-scale x-axis (ONNX file size in KB) versus MAE on the held-out test fold. Four TinyDCS variants (Tiny, Compact, Medium, Full) and the closed-form ADRAC baseline are plotted. The Compact variant achieves the target edge-deployment footprint while dominating the baseline by 3× on MAE.

**Figure 4. Per-altitude-band 95 % conformal coverage — five calibration strategies.** Grouped bars showing empirical coverage in each 5,000-ft altitude band for five calibration methods on the same test fold. Four conformal-only methods (global, Mondrian, CQR, Mondrian-CQR) are invariant at 0.58–0.59 in the 18,000–23,000 ft band. The zero-inflated two-stage method achieves ≥ 0.95 coverage in all five bands.

**Figure 5. Personalisation information gain — per-subject susceptibility recovery.** Left y-axis: Pearson *r* between true and posterior-mean log-susceptibility (synthetic 200-subject cohort) as a function of observed exposures *k* per subject. Right y-axis: Brier score for population-level (flat prior) versus personalised predictions. Crossover near *k* = 10 indicates the exposure count at which personalisation begins to outperform the population model.
