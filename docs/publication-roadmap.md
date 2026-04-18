# Publication roadmap

Three-paper plan with explicit scope, dependencies, and timeline. The sequencing is chosen so each paper is publishable on its own and can stand if the next is delayed.

---

## Paper 1 — TinyDCS (methods paper)

**Working title**
> *TinyDCS: An edge-deployable machine-learning surrogate of the ADRAC altitude-decompression-sickness model with continuous-exposure VO₂ covariates and calibrated uncertainty*

**Journal targets**
1. **Aerospace Medicine and Human Performance (AMHP)** — primary. Aerospace-medicine audience; Diego's home journal.
2. **Diving and Hyperbaric Medicine (DHM)** — secondary; peer community.
3. **IEEE Journal of Biomedical and Health Informatics (JBHI)** — if the edge-ML angle carries the weight.

**Primary data source**
- `legacy/Model_Rel_Candidate/DCS_Risk_DB_2025.csv`, cleaned to 15,908 unique grid cells by `scripts/01_clean_data.py`.

**Secondary / ablation**
- Synthetic profiles from `mechanistic.rut_mbe1` (shape-only; not training target until reconciliation completes).

**Core contributions**
1. A **continuous-VO₂ extension** of the ADRAC covariate set using Conkin 2004's variable-half-time tissue ratio, validated against the ADRAC-on-a-dense-grid surrogate target.
2. A **lightweight surrogate model** (LightGBM on logit(P(DCS))) with target post-quantization size < 100 KB.
3. **Calibrated uncertainty** via split conformal prediction on the logit scale, with finite-sample marginal coverage guarantees.
4. **Principled out-of-distribution abstention** via Mahalanobis distance in feature space.
5. **Edge deployment** to ONNX/INT8 with a bit-exact Python reference runtime for development.
6. A **reproducible data-cleaning pipeline** that repairs the 1,221-row scale bug in the shipped dataset.

**Pre-specified acceptance criteria**
- MAE on held-out test ≤ 0.03 (absolute probability units);
- Calibration slope ∈ [0.9, 1.1], intercept magnitude < 0.05;
- Empirical conformal coverage ≥ 94% at nominal 95%;
- OOD detector abstains ≥ 90% on deliberately-out-of-envelope inputs;
- Post-quantization model size ≤ 100 KB, latency ≤ 1 ms on Cortex-M4 simulator.

**Timeline**
- Weeks 1–2: Close the 3RUT-MBe1 reconciliation issue (or formally park it) and finalize `mechanistic/adrac.py` log-logistic AFT fit to the cleaned grid.
- Weeks 3–4: Full-scale simulation/training campaign (≥ 20,000 profiles); leave-one-altitude-out ablation.
- Weeks 5–6: ONNX/INT8 export + TFLite Micro benchmarking.
- Weeks 7–9: Writing + internal review.
- Weeks 10–12: Submission; journal round trip.

**Risks and how they are mitigated**
- *Risk — surrogate is too accurate to be a compelling paper.* Mitigate by reporting against Han 2023 IEEE CACRE as a baseline and emphasizing the continuous-VO₂ extension + calibrated-uncertainty + edge-deployment trifecta, which no prior work combines.
- *Risk — reviewers conflate surrogate accuracy with clinical accuracy.* Mitigate by explicit "ground truth is a parametric model, not observed DCS" framing in the abstract, introduction, and limitations. Paper 3 addresses the clinical question.

---

## Paper 2 — Hierarchical Bayesian personalization

**Working title**
> *A hierarchical Bayesian personalization layer for wearable altitude-DCS risk prediction: integrating multimodal physiology and online posterior updates*

**Journal targets**
1. **PLOS Computational Biology** — methodology-leaning;
2. **Frontiers in Physiology (Aerospace Medicine)** — scope-aligned;
3. **AMHP** — clinically-leaning variant.

**Dependencies**
- Paper 1 published or in press.
- A representative **individual-variability simulator** (likely extending `mechanistic.rut_mbe1` with a subject-level susceptibility parameter $\lambda_i$; the USAFSAM database has enough resolution to bootstrap this).

**Core contributions**
1. A **hierarchical prior** over per-subject susceptibility $\lambda_i \sim \mathrm{LogNormal}(\mu_\lambda, \sigma_\lambda)$ that multiplies the base hazard.
2. **Online posterior updates** from user-reported symptom checks and optional wearable biomarkers.
3. **Multimodal fusion** of HR, HRV, SpO₂, and skin temperature as state-dependent modulators of the base risk.
4. Simulation-based calibration (Talts et al. 2018) on the hierarchical model.
5. Quantitative comparison against the Paper 1 population-average surrogate.

**Open scientific questions this paper tackles**
- How many symptom-check + exposure pairs are needed to drive a subject's posterior to practical precision?
- Which wearable biomarker carries the most per-bit information about $\lambda_i$?
- Does HRV during the first 30 minutes at altitude predict subsequent DCS? (Pre-registered hypothesis.)

---

## Paper 3 — Prospective clinical validation

**Working title**
> *Prospective external validation of a wearable hybrid DCS risk monitor during hypobaric chamber training in a Latin American aerospace cohort*

**Journal targets**
1. **npj Digital Medicine** — primary; wearable-ML-clinical audience.
2. **AMHP** — aerospace-medicine home venue.
3. **Frontiers in Physiology** — backup OA option.

**Dependencies**
- Papers 1 and 2 in hand (at least as preprints).
- IRB approval (CIAF / Universidad del Bosque or equivalent).
- Chamber access (CIAF chamber in Bogotá or equivalent).
- Wearable logistics (compatible device, VO₂ calibration procedure, data-capture pipeline).

**Core contributions**
1. Prospective chamber cohort with continuous wearable physiology + exposure logging + blinded DCS/VGE outcome ascertainment.
2. **External validation** of TinyDCS v1.0 (Paper 1 surrogate) and of the hierarchical personalization layer (Paper 2).
3. **Calibration and discrimination** on real clinical outcomes, not parametric-model output.
4. Sensitivity analyses: wearable-VO₂ error propagation, missing-biomarker scenarios, symptom-underreporting scenarios.

**Sample-size calculation (targeting calibration slope precision, Riley et al. 2019)**: ~150–300 subject-exposures, depending on event rate and baseline risk distribution.

**Ethical and operational framing**
- This is a prospective observational + decision-support study, **not** an interventional trial. TinyDCS predictions are logged but not used to change exposure protocols.
- Underreporting of mild DCS is a known failure mode; the protocol must include standardized symptom-check prompts (e.g., 15-minute intervals) and Doppler VGE monitoring where feasible.
- Cultural/linguistic calibration of the symptom-check instrument (Spanish-language aerospace population) is a non-trivial sub-contribution.

---

## Cross-paper considerations

**Reporting standards.** All three papers adopt [TRIPOD+AI (BMJ 2024)](https://doi.org/10.1136/bmj.e078378) for predictive-model reporting and [STARD 2015](https://doi.org/10.1136/bmj.h5527) for the clinical validation (Paper 3). The reporting checklist coverage is documented per paper in `docs/` at submission time.

**Open science.**
- Paper 1 code + cleaned data + trained joblib → GitHub + Zenodo DOI on acceptance.
- Paper 2 posterior samples and simulation code → same.
- Paper 3 anonymized dataset → per IRB; aggregate results + per-subject model cards published.

**Authorship and attribution.** Diego Malpica as first author and PI across all three papers. Paper-specific collaborators to be added for: ML methodology (Paper 1), Bayesian hierarchical modelling (Paper 2), chamber and clinical operations (Paper 3).

**Risks to the roadmap.**
- If the 3RUT-MBe1 reconciliation in Paper 1 cannot be completed, Paper 1 is re-scoped to "surrogate of ADRAC with continuous-VO₂ extension" and 3RUT-MBe1 is relegated to Paper 1b as a short methods note.
- If IRB or chamber access for Paper 3 slips, the intermediate **digital twin** — a high-fidelity simulator built from the cleaned USAFSAM data — becomes a viable Paper 2.5 that maintains publication cadence.
