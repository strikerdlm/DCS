---
title: 'TinyDCS: An edge-deployable machine-learning surrogate of the ADRAC altitude-decompression-sickness risk model with continuous-exposure covariates and calibrated uncertainty'

running-title: 'TinyDCS: edge surrogate of ADRAC'
running-authors: 'Malpica \& Farfán'

article-type: 'Original Research --- Extended Abstract'
journal-line: '\textit{Aerospace Medicine and Human Performance} (AsMA) --- in preparation'

author-line: 'Diego Malpica, MD\textsuperscript{1*}\enspace·\enspace Marian Farfán, MD\textsuperscript{1}'

affil-1: 'Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine, Colombian Aerospace Force, Bogotá DC, Colombia'

correspondence: 'diego.malpica@fac.mil.co'

pdf-author: 'Malpica D, Farfán M'

wordcount: 'approx. 250 (abstract) --- full manuscript in preparation'
version: '0.5.0 --- 2026-04-18'

repository: 'github.com/strikerdlm/DCS'

abstract-background: 'The US Air Force Altitude DCS Risk Assessment Computer (ADRAC; Pilmanis 2004) is the operational standard for planning hypobaric exposures in aviation and extravehicular activity, but two limitations constrain modern use: its three-level exercise covariate cannot accommodate continuous wearable-derived VO\textsubscript{2} trajectories, and it returns point estimates without calibrated uncertainty.'

abstract-objective: 'To build and benchmark a wearable-grade machine-learning surrogate of the ADRAC grid that (i) accepts continuous-VO\textsubscript{2} exposure covariates, (ii) ships calibrated 95\% prediction intervals with uniform altitude-band coverage, (iii) abstains outside the validated input envelope, and (iv) meets an edge-deployment footprint below 100 KB and a per-inference latency below 10 \textmu{}s.'

abstract-methods: 'We audited and repaired a public ADRAC-output grid (16,295 rows; 1,221 rows, 7.5\%, were mis-entered on the fraction scale and were rescaled neighbour-consistently to percent), retaining 15,908 unique grid cells. We trained a LightGBM regressor on the logit of P(DCS) using a 13-feature vector that augments the ADRAC covariates with a Conkin 2004 single-compartment tissue-nitrogen ratio (360-min half-time) and continuous-VO\textsubscript{2} summaries consistent with Webb 2010''s 1-minute-peak metric. Smithson--Verkuilen boundary shrinkage handled exact-zero targets, physiological monotonicity constraints were imposed on altitude, prebreathe, time-at-altitude, and tissue-N\textsubscript{2} features, and a two-stage zero-inflated conformal stack was fitted: a binary classifier for the exact-zero mass combined with a split-conformal regressor for the positive support, with Mahalanobis-distance out-of-envelope abstention. We benchmarked against a closed-form log-logistic AFT fit to the same grid and exported the surrogate to ONNX. A conjugate-Gaussian hierarchical Bayesian personalization layer was prototyped on a synthetic 200-subject cohort.'

abstract-results: 'On the held-out random test fold (\textit{n} = 2,387), TinyDCS attained MAE = 0.020, R\textsuperscript{2} = 0.986, and Brier score = 0.0016 --- a 4-fold MAE reduction and 10-fold Brier reduction over the closed-form baseline (MAE = 0.086; Brier = 0.0150). Empirical 95\% coverage was 0.960 overall and at least 0.95 in each of the five 5,000-ft altitude bands, closing a low-band shortfall (coverage 0.58--0.59 at 18,000--23,000 ft) that was invariant under four conformal-only alternatives and was diagnosed as target-distribution pathology rather than residual-variance error. A compact zero-inflated variant compiled to 95 KB of ONNX with CPU per-row latency of 2.44 \textmu{}s (p50). The personalization prototype recovered per-subject log-susceptibility at Pearson \textit{r} = 0.63 after twenty exposures per subject, with population-vs-personalized Brier parity crossover near \textit{k} = 10.'

abstract-conclusions: 'A continuous-VO\textsubscript{2} ADRAC surrogate with zero-inflated conformal calibration and out-of-envelope abstention outperforms the closed-form model on the same data at an edge-feasible memory and latency budget. External prospective validation on a hypobaric-chamber cohort with Doppler venous-gas-emboli ground truth, and replacement of the conjugate-Gaussian personalization stub with a full hierarchical Bayesian model on real subjects, are the priority follow-ups. The full methods pipeline, trained weights, ONNX exports, and an AI-agent continuation guide (\texttt{AGENTS.md}) are released open-source at \texttt{github.com/strikerdlm/DCS}.'

abstract-keywords: 'altitude decompression sickness; ADRAC; wearable computing; conformal prediction; zero-inflated models; edge AI; aerospace medicine; hierarchical Bayesian personalization'

---

<!-- ============================================================
     Extended-abstract body. Brief significance statement,
     contributions list, and data availability only --- the full
     manuscript is in paper-1-draft.md.
     ============================================================ -->

## Significance

Unpressurized general aviation above FL180, military egress from pressurized cockpits, and EVA prebreathe scheduling all rely on ADRAC-class closed-form models for ground-side planning. None of the published operational models ingests the per-second VO\textsubscript{2}, heart-rate, SpO\textsubscript{2}, and barometric-altitude streams that modern wearables now produce. This work delivers a first-generation surrogate that is simultaneously (a) accurate on the ADRAC-grid reference target, (b) honestly uncertainty-quantified across the full altitude range of operational interest, and (c) small and fast enough to run on a flight-watch or smartphone background task --- three properties that no prior published altitude-DCS model has achieved together.

## Summary of contributions

1. **Data audit.** The shipped `DCS_Risk_DB_2025.csv` contains a systematic scale inconsistency affecting 7.5\% of rows; we document the defect and release a deterministic neighbour-median cleaner that restores the grid to 15,908 unique cells on a single scale.
2. **Hybrid feature vector.** A 13-feature descriptor that carries ADRAC's covariates forward while injecting a Conkin 2004 tissue-N\textsubscript{2} ratio and continuous-VO\textsubscript{2} summaries consistent with Webb 2010.
3. **Zero-inflated conformal calibration.** A two-stage calibration that routes the exact-zero mass through a dedicated binary classifier and closes a low-altitude coverage gap that four conformal-only alternatives could not.
4. **Edge-deployable ONNX ladder.** Model-size variants spanning 17 KB to 1.8 MB; the 95 KB compact variant retains R\textsuperscript{2} > 0.98 and still outperforms the closed-form ADRAC baseline by three-fold on MAE.
5. **Hierarchical personalization prototype.** A conjugate-Gaussian per-subject posterior on log susceptibility, with an explicit information-gain curve across *k* = 1--20 exposures (Paper 2 scope).
6. **Reproducibility package.** A command-by-command runbook, an honest validation-hardware inventory, an NEDU TR 18-01 Appendix-C audit checklist for the open 3RUT-MBe1 reconciliation, and an AI-agent continuation guide.

## Data and code availability

All code, cleaned data, trained model bundles (joblib), ONNX artifacts, metrics JSONs, and figure bundles are released under a research-use license at `github.com/strikerdlm/DCS`. Every headline number in this abstract is reproducible end-to-end in under three minutes on CPU via `docs/runbook.md`.

## Conflicts of interest and funding

The authors declare no conflicts of interest. This work received no external funding. AI coding assistance (Claude Opus 4.7 and Claude Sonnet 4.6) was used during implementation and is declared on every relevant commit; all modelling decisions, validation, and interpretation are the authors'.
