# Scientific background

This document anchors TinyDCS in the existing literature on altitude decompression sickness (DCS) modelling, so that every engineering decision in the codebase can be traced back to a primary source.

## 1. What causes altitude DCS

Altitude DCS is the in-situ growth of gas bubbles from dissolved tissue nitrogen when ambient pressure drops faster than the body can offload nitrogen. The classical necessary condition is **tissue supersaturation**: the sum of dissolved gas partial pressures in a region exceeds the local ambient pressure opposing phase separation (Conkin et al., NASA TP-2004-213158). Operationally, four covariates dominate the risk surface:

| Covariate | Mechanism |
|---|---|
| Altitude / ambient pressure | Determines the post-ascent ambient pressure $P_2$ and thus the supersaturation window |
| Time at altitude | Hazard accumulates; risk grows with exposure duration |
| Prebreathe duration (100% O₂) | Denitrogenates tissue before ascent; the dominant protective factor |
| Exercise during exposure | Elevates tissue N₂ washout *and* bubble nucleation/growth |

Secondary factors (age, sex, BMI, aerobic capacity, menstrual cycle, PFO, hydration) all modulate susceptibility but are typically excluded from operational models because their effects are smaller than the "big four" and harder to measure in the field (Webb et al. 2003, 2005).

## 2. ADRAC — the US Air Force operational model

The **Altitude DCS Risk Assessment Computer** (Pilmanis, Kannan, Petropoulos, Webb 1998–2004) is a **stratified accelerated-failure-time log-logistic survival model** built on the USAFSAM hypobaric-chamber database. Its core equation:

$$
P(\text{DCS by time } t) = 1 - S(t) = \frac{1}{1 + \exp\big((\ln t - \beta_2 - \beta \cdot \mathbf{x})/\beta_1\big)}
$$

Covariates $\mathbf{x}$ are ambient pressure (mmHg, non-linear in feet), prebreathe duration (entering via an exponential trendline), and a **three-level categorical exercise variable** (Rest / Mild / Heavy). The time-to-event $t$ is the failure time — exposure duration at altitude.

ADRAC was validated with 150 prospective hypobaric exposures (Pilmanis et al. 2004, ASEM 75:749–59) and has an altitude ceiling of 40,000 ft. It is the model underlying the shipped `DCS_Risk_DB_2025.csv` and the US Air Force operational risk-planning tool. **TinyDCS's primary training target is ADRAC's output on a dense grid.**

Limitations the literature itself acknowledges:

- Exercise is a 3-level categorical covariate. The ICASM 2017 slides explicitly call this out as a weakness and propose Webb et al. (2010)'s "highest 1-minute VO₂ per 16-minute window" as the operationally correct metric.
- The model is population-average; individual susceptibility is not modelled.
- Validity is bounded by the training envelope (altitude 18,000–40,000 ft; prebreathe 0–240 min; time 10–480 min).

## 3. Conkin NASA Research / NASA Models — continuous-VO₂ during prebreathe

Conkin & Gernhardt (2004, NASA TP-2004-213158) introduced the **Exercise Tissue Ratio**:

$$
\text{ETR} = \frac{P_1 N_2}{P_2}
$$

where $P_1 N_2$ is the computed tissue N₂ partial pressure after ascent, and $P_2$ is the post-ascent ambient pressure. Crucially, $P_1 N_2$ is computed with a **variable half-time compartment** whose half-time depends nonlinearly on VO₂ during prebreathe (normalized to peak, %VO₂ₚₖ). The ETR becomes the decompression-dose input to two logistic regressions:

- **RM (Research Model)**: $P(\text{DCS}) = \sigma(\beta_0 + \beta_1 \cdot \text{ETR} + \beta_2 \cdot \text{age})$ [Eq. 15 of TP-2004-213158]
- **NM (NASA Model)**: $P(\text{DCS}) = \sigma(\beta_0 + \beta_1 \cdot \text{ETR} + \beta_2 \cdot \text{sex})$ [Eq. 14 of TP-2004-213158]

The RM/NM distinction controls the demographic covariate. Both models are implemented in `mechanistic/conkin_nasa.py` (relocated from the original `NASA_model/DCS_NASA.py`).

**What Conkin's model gives TinyDCS.** It gives us a physiologically-grounded way to inject *continuous* VO₂ into ADRAC's categorical exercise covariate. By computing a Conkin-style tissue ratio using a VO₂(t) trajectory (see `tinydcs/features.py`) we can condition the surrogate on real wearable telemetry.

**What Conkin's model does not give us.** Conkin RM/NM only models exercise during *prebreathe*. Exercise during altitude exposure is treated as a categorical indicator only. This is precisely why we need the extension.

## 4. Webb 2010 & 2016 — continuous exercise during altitude exposure

Webb, Krock & Gernhardt (2010, ASEM 81:987–92) and Webb, Morgan & Sarsfield (2016, AMHP 87:516–20) analyzed the USAFSAM DCS database and defined the operationally correct activity metric:

> "Level of activity is the highest 1-minute of VO₂ during each 16-minute window of testing, in mL·kg⁻¹·min⁻¹."

This is the metric TinyDCS's `tinydcs.features._peak_1min` computes. Webb's papers established the dose-response but **did not formally refit ADRAC or Conkin to use it**. That formal extension is one of the publishable contributions of TinyDCS.

## 5. Gerth 3RUT-MBe1 — the mechanistic bubble-dynamics frontier

Gerth, Doolette & Gault (2018, NEDU TR 18-01, DTIC AD1101527) developed the **three-region unified tissue bubble-evolution model** (3RUT-MBe1). It is a deterministic ODE recursion that accepts an arbitrary piecewise-VO₂ trajectory and evolves:

- Tissue gas tensions (N₂, O₂) with exercise-dependent perfusion;
- Bubble number density via a crush-pressure + surface-tension recruitment model;
- Bubble radius growth via gas transport;
- Hazard via a gas-volume-to-hazard map, accumulated to P(DCS).

The full recursion is in Appendix C of NEDU TR 18-01 and is implemented in `mechanistic/rut_mbe1.py` (1,255 lines, preserved from the user's prior work). 3RUT-MBe1 outperforms ADRAC on 4/5 of Gerth's own validation profiles (Figure 16 of the report).

### 3RUT-MBe1 reconciliation — open issue

The current `mechanistic/rut_mbe1.py` implementation **under-reports P(DCS) by ~4–5 orders of magnitude** on Gerth's five ADRAC-validation profiles:

| Profile | Our implementation | Gerth Figure 16 (approx.) |
|---|---|---|
| A: 90 min PB, 35K ft, light ex, 180 min | 1.2e-5 | ~20–30% |
| B: 30 min PB, 25K ft, heavy ex, 240 min | 2.2e-5 | ~40–60% |
| C: 15 min PB, 22.5K ft, heavy ex, 240 min | 2.3e-5 | ~50–70% |
| D: 0 PB, 18K ft, heavy ex, 360 min | 3.7e-5 | ~30–50% |
| E: 75 min PB, 30K ft, rest, 240 min | 1.8e-5 | ~10–20% |

This is a **parameter or scaling bug** in the vendored implementation, not a property of 3RUT-MBe1 itself. The most likely suspects are:
1. The Λ scaling factor in Appendix C (`lambda_cm_inv = 100.0` default) may not match Gerth's fitted value.
2. The hazard gain (`gain_g_hazard`) or the bubble-number multiplier (`n0_b_total_nuclei`) may need recalibration.
3. The recursion may accumulate numerical damping over thousands of 0.5-min steps.

**Practical consequence for TinyDCS.** Until reconciliation is complete, the primary training target is ADRAC's output, not 3RUT-MBe1. 3RUT-MBe1 remains in the repo as (a) a mechanistic comparator once reconciled, (b) a shape-study tool (monotonicity, trajectory effects), and (c) the forward path to published-state-of-the-art mechanistic predictions.

## 6. What nobody has yet published

A literature pull (PubMed + Europe PMC + DTIC + NASA NTRS + Google Scholar, through April 2026) finds:

- **Han et al. 2023 (IEEE CACRE)** — an ML surrogate (random forest + NN) of ADRAC output. Demonstrated ≥ 0.99 explained variance but categorical-exercise inputs only, no uncertainty quantification, no edge deployment, and no OOD handling.
- **Aselisewine & Pal (2023–2026, Stat Comput, AStA)** — SVM-based mixture cure-rate models on the NASA hypobaric DCS database. Methodologically interesting (interval-censored targets) but not wearable-focused.
- **Fichtner et al. 2025 (Sports Med Open)** — ML prediction of post-dive bubble grades in *diving* (hyperbaric) DCS. Diving, not altitude.
- **Posada-Quintero et al. 2024 (Communications Medicine)** — EDA-spectrum prediction of CNS-O₂ toxicity in divers. Hyperbaric, not hypobaric.
- **Jia et al. 2026 (Scientific Data)** — descriptive pilot SpO₂/respiratory dataset at simulated altitude. No predictive model.

**What remains unpublished as of April 2026:**

1. A wearable-grade, edge-deployable surrogate of ADRAC that accepts **continuous VO₂ trajectories** (both during prebreathe and during altitude).
2. **Calibrated uncertainty** with finite-sample conformal guarantees and **principled OOD abstention** outside the validated envelope.
3. **Hierarchical Bayesian personalization** from multimodal wearable telemetry (HR/HRV/SpO₂/skin-temp), with per-subject posterior updates.
4. Prospective **external validation** in a Latin American aerospace cohort with continuous wearable physiology.

Items 1 + 2 are the scope of **Paper 1** (this repo's v0.x–v1.0 target). Item 3 is **Paper 2**. Item 4 is **Paper 3**. See `docs/publication-roadmap.md`.

## 7. Full bibliography

The comprehensive primary-source list is maintained in `docs/nasa_model_references/` (vendored markdowns of the Conkin 2004 ETR paper, NASA BiP 2024 report, and the NASA evidence reviews). The list below is the load-bearing set.

### USAFSAM / ADRAC lineage
- Kannan N, Raychaudhuri A, Pilmanis AA (1998). *A loglogistic model for altitude decompression sickness.* Aviat Space Environ Med 69:965–70.
- Pilmanis AA, Petropoulos LJ, Kannan N, Webb JT (2004). *Decompression sickness risk model: development and validation by 150 prospective hypobaric exposures.* ASEM 75:749–59.
- Webb JT, Pilmanis AA (1999, 2005, 2016). Series on preoxygenation and exposure dose-response.

### NASA / Conkin lineage
- Conkin J, Kumar KV, Powell MR, Foster PP, Waligora JM (1996). *A probability model of hypobaric decompression sickness based on 66 chamber tests.* ASEM 67:176–83.
- Conkin J (2001). *A Log Logistic Survival Model Applied to Hypobaric Decompression Sickness.* NASA TP-2001-210775.
- Conkin J, Gernhardt ML (2004). *A probability model of decompression sickness at 4.3 psia after exercise prebreathe.* NASA TP-2004-213158.
- Conkin J (2011). *Decompression sickness after air break in prebreathe described with a survival model.* ASEM 82:589–98.

### Mechanistic / bubble-dynamics lineage
- Van Liew HD, Hlastala MP (1969). *Influence of bubble resorption on the determination of the effective surface area of the alveolar membrane.* Respir Physiol 7:111–21 (foundational).
- Gernhardt ML (1991). Tissue Bubble Dynamics Model (TBDM).
- Gerth WA, Doolette DJ, Gault KA (2018). *A Probabilistic Model of Altitude Decompression Sickness Based on the 3RUT-MB Model.* NEDU TR 18-01 (DTIC AD1101527).

### Methodology
- Shafer G, Vovk V (2008). *A tutorial on conformal prediction.* JMLR 9:371–421.
- Van Calster B et al. (2019). *Calibration: the Achilles heel of predictive analytics.* BMC Med 17:230.
- Collins GS, Moons KGM, et al. (2024). *TRIPOD+AI statement.* BMJ 385:e078378.

### Operational / clinical context
- Stepanek J et al. (2024). *Decompression sickness risk assessment and awareness in general aviation.* AMHP (Mayo analysis of FL180+ unpressurized flights in the US).
