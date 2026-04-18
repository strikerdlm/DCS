# Paper 2 scope — hierarchical Bayesian personalization of TinyDCS

*Scoping note v0.1 — drafted alongside the code in `tinydcs/personalization.py`.*

---

## Working title

> *A hierarchical Bayesian personalization layer for wearable altitude-DCS risk prediction: per-subject susceptibility from sparse exposure histories*

## Journal targets

1. **PLOS Computational Biology** — primary. Methods-forward; accepts hierarchical Bayesian methodology with synthetic-cohort validation.
2. **Frontiers in Physiology (Aerospace Medicine)** — secondary. Same audience, open access.
3. **Aerospace Medicine and Human Performance (AMHP)** — if we want to stay in Diego's home venue.

## Scientific framing

Every published altitude-DCS model — ADRAC, Conkin RM/NM, Gerth 3RUT-MBe1, and our own TinyDCS surrogate — is a **population-average** predictor. Documented inter-subject variability in DCS susceptibility is 10–100× across published chamber cohorts (Webb et al. 2003, 2005; Balldin et al. 2004). No existing operational tool represents this variability as a first-class parameter.

Wearables make the personalized-prediction regime newly tractable: a single device accumulates a subject's exposure history, activity trajectories, and (via periodic symptom checks) ground-truth outcome labels. The question this paper asks is: **given the base surrogate TinyDCS and a few exposures per subject, how well can we infer that subject's susceptibility and improve their personal calibration?**

## The hierarchical model

We place a per-subject log-susceptibility $\log \lambda_i$ on a log-odds scale above the base surrogate's prediction:

$$
\text{logit}\big(P(\text{DCS}_{ij} \mid x_{ij}, \lambda_i)\big) = \hat\eta(x_{ij}) + \log \lambda_i
$$

with the hierarchical prior

$$
\log \lambda_i \sim \mathcal{N}(\mu_\lambda,\, \sigma_\lambda^2)
$$

where $\hat\eta(x)$ is the TinyDCS base surrogate's logit output, $i$ indexes subjects, $j$ indexes their exposures, and $y_{ij} \in \{0, 1\}$ is the observed outcome (ideally DCS; VGE as a secondary stronger-signal proxy).

**Why this parameterization.** Adding $\log \lambda_i$ to the logit is the natural hazard-multiplier form: $\lambda_i > 1$ means the subject is more susceptible than the population average; $\lambda_i < 1$ less. On the probability scale it is a monotone, dose-response-preserving shift. It does not require refitting the base surrogate and so cleanly separates Paper 1 (base model) from Paper 2 (personalization).

## Inference: two implementations, one paper

### Implementation A — conjugate Gaussian update (closed form, on-device)

When the likelihood is approximated as Gaussian around the base surrogate's logit (valid whenever the base prediction is away from 0 or 1), the posterior over $\log \lambda_i$ is conjugate:

$$
\mu_{\text{post}, i} = \frac{\sigma_{\text{lik}}^2 \mu_\lambda + \sigma_\lambda^2 \sum_j (y_{ij}^\text{logit} - \hat\eta(x_{ij}))}{\sigma_{\text{lik}}^2 + n_i \sigma_\lambda^2}, \quad
\sigma_{\text{post}, i}^2 = \frac{\sigma_{\text{lik}}^2 \sigma_\lambda^2}{\sigma_{\text{lik}}^2 + n_i \sigma_\lambda^2}
$$

This is **tiny, fast, and on-device-friendly** — no MCMC required. Population hyperparameters $\mu_\lambda, \sigma_\lambda^2$ are fit by empirical Bayes on the aggregated cohort. Per-subject updates are O(1) per new observation.

Prototype lives in `tinydcs.personalization.PersonalizedSurrogate`. This is the version that would actually run on a watch.

### Implementation B — full hierarchical Bayesian (PyMC, off-device)

A full No-U-Turn-Sampler posterior over $(\mu_\lambda, \sigma_\lambda, \{\log \lambda_i\})$ lets us:

- Propagate population-level uncertainty.
- Handle binary outcomes exactly (no Gaussian approximation).
- Run simulation-based calibration (SBC, Talts et al. 2018) to verify the algorithm.

This is for the paper's validation and for reviewers who expect a full Bayesian treatment. Not deployed on-device.

## Data sources (synthetic first)

Paper 2 **does not require new clinical data**. The methodological contribution is validated on synthetic cohorts with known $\lambda_i$; Paper 3 will provide the real-data confirmation.

### Synthetic cohort generator (`tinydcs.personalization.generate_synthetic_cohort`)

1. Sample $n$ subjects, each with $\log \lambda_i \sim \mathcal{N}(0, \sigma_\lambda^2)$ (ground truth).
2. Generate $k$ exposures per subject from the ADRAC envelope. Exposures can be correlated within a subject (e.g. repeated chamber sorties at similar altitudes).
3. For each exposure, compute the base surrogate's $\hat\eta$ and draw an outcome $y_{ij} \sim \text{Bernoulli}(\sigma(\hat\eta + \log \lambda_i))$.
4. Return a long-format dataframe with `subject_id`, features, `y`, `log_lambda_true`.

### Validation protocol

- Fit the hierarchical model (Impl. A and Impl. B) on the synthetic cohort.
- Measure: Spearman correlation of posterior mean $\hat{\log \lambda_i}$ vs ground-truth $\log \lambda_i$; shrinkage plots; calibration on held-out exposures.
- Vary $k$ (exposures per subject, 1 → 20) and $\sigma_\lambda^2$ (cohort heterogeneity, 0.1 → 2.0) to produce the **information-gain curves** that tell a clinician "how many exposures until the personalization pays off?" This is a novel quantitative answer to a question the primary literature only discusses qualitatively.

## Core contributions

1. **Conjugate Gaussian per-subject susceptibility update** above the TinyDCS base surrogate — deployable on-device, closed-form posterior, no MCMC.
2. **Full hierarchical Bayesian counterpart** with simulation-based calibration and PyMC implementation for methodological rigor.
3. **Information-gain analysis**: how many exposures does a subject need before the personalized model beats the population-average baseline? How does this depend on cohort heterogeneity and exposure informativeness?
4. **Synthetic benchmark harness** (`tinydcs.personalization.generate_synthetic_cohort`) that other groups can use to evaluate their own personalization methods.
5. *(Optional, publication-grade figure):* Multimodal extension — HRV and SpO₂ trajectories as additional covariates modulating $\log \lambda_i$. Requires Paper 3 data unless replaced by a published dataset.

## Timeline

- **Weeks 1–2**: ship `tinydcs.personalization` prototype (Impl. A), synthetic-cohort generator, tests. *This session lands v0.5.0 with the prototype.*
- **Weeks 3–4**: PyMC reference implementation (Impl. B) + simulation-based calibration.
- **Weeks 5–7**: information-gain curves + cohort-heterogeneity sweep + publication figures.
- **Weeks 8–10**: manuscript drafting (methods section reuses Paper 1's TRIPOD+AI skeleton with a TRIPOD-Cluster addendum for the hierarchical element).
- **Weeks 11–12**: internal review + submission.

## Dependencies on Paper 1

The base surrogate $\hat\eta(x)$ is exactly the zero-inflated TinyDCS model from Paper 1. Paper 2 begins with "given Paper 1's base surrogate, …" and cites Paper 1 for the base-model validation. If Paper 1 slips, Paper 2 can cite a pre-print and proceed.

## What this paper is NOT

- **Not a clinical study.** Real human data enters in Paper 3.
- **Not a new mechanistic model.** The base surrogate is Paper 1's; Paper 2 is about personalization methodology.
- **Not reliant on PyMC for deployment.** Implementation A is the on-device path; Implementation B is the methodological scaffold.
- **Not the same as simple ridge regression.** The hierarchical prior explicitly regularizes subjects with few exposures toward the population mean — a shrinkage behaviour that improves small-n subjects' predictions.

## Ethical framing

Even under Paper 2's synthetic-cohort framing, it is worth pre-committing to:

- **Explicit uncertainty in personalized predictions.** A subject with 2 exposures should see a wider posterior than one with 20. The conjugate update makes this automatic; the UI must not hide it.
- **No closed-loop gating.** The personalized model advises; it does not disable training or flight clearance without a human in the loop. This framing is the same as Paper 1 and is restated in the Paper 2 discussion.
- **Subject-level opt-out.** Per-subject posteriors are subject-owned and deletable. This is a privacy design commitment that influences the API shape.
