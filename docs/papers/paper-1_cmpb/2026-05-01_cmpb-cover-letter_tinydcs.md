# Cover Letter — TinyDCS to Computer Methods and Programs in Biomedicine

> **Pre-submission notes for the corresponding author.** Copy the body below into your institutional letterhead. Verify each declaration once more on the day of submission. The letter is structured to address the 10 elements expected by CMPB (scope, what is known, what this study adds, originality, AI disclosure, suggested reviewers, data/code, COI, funding, software product). Total length ≈ 480 words.

---

[Institutional letterhead — Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine, Colombian Aerospace Force]

2026-05-01

Filippo Molinari, PhD
Editor-in-Chief, *Computer Methods and Programs in Biomedicine*
Department of Electronics and Telecommunications
Polytechnic of Turin, Turin, Italy

*Submitted via Editorial Manager (https://www.editorialmanager.com/cmpb/)*

Dear Prof. Molinari,

We are submitting our manuscript, *"TinyDCS: An edge-deployable machine-learning surrogate of the ADRAC altitude-decompression-sickness risk model with continuous-exposure covariates and calibrated uncertainty,"* for consideration as a Full Length Article in *Computer Methods and Programs in Biomedicine*.

**Scope and fit.** The manuscript is, at its core, a methodological and software contribution: a monotonicity-constrained gradient-boosting surrogate of a published survival-model probability grid, equipped with a two-stage zero-inflated split-conformal calibration, Mondrian altitude-band stratification, Mahalanobis-distance out-of-distribution abstention, and an ONNX export pipeline that compiles to 95 KB and runs at 2.44 μs per inference on commodity CPU. Altitude decompression sickness in unpressurised aviation and extravehicular activity is the demonstrating use case. The methodology — boundary-shrinkage logit regression with monotonicity constraints, Mondrian conformal calibration with a dedicated zero-inflation stage to repair coverage where the target distribution is degenerate, and OOD-aware abstention for safety-critical inference — generalises to any biomedical risk-grid surrogate with similar pathologies. CMPB's mandate to encourage formal computing methods and their application in biomedical research and medical practice is the natural home for this work.

**What is known.** The US Air Force ADRAC log-logistic accelerated-failure-time model (Pilmanis 2004) is the operational standard for altitude DCS risk planning, but it accepts only a three-level categorical exercise covariate and emits point estimates without calibrated uncertainty. The bubble-dynamics 3RUT-MBe1 model (NEDU TR 18-01, 2018) accepts continuous VO₂ trajectories but is too computationally heavy for embedded deployment.

**What this study adds.** TinyDCS is, to our knowledge, the first published model that simultaneously (i) reproduces the ADRAC grid with a 4-fold MAE reduction (0.020 vs 0.086) and 10-fold Brier reduction over a closed-form log-logistic AFT fit to the same data, (ii) accepts continuous wearable-derived VO₂ covariates, (iii) ships calibrated 95 % prediction intervals with uniform per-altitude-band coverage (closing a 0.58 → 0.96 shortfall in the 18–23 kft band that four conformal-only alternatives could not close), (iv) abstains principled outside its validated input envelope, and (v) compiles to a 95 KB ONNX artefact with 2.44 μs per-row inference latency. A reproducibility package (runbook, AI-agent continuation guide, trained weights, ONNX exports, metrics JSONs, TRIPOD+AI checklist) is publicly released at https://github.com/strikerdlm/DCS.

**Generalisability.** The two-stage zero-inflated conformal architecture and the Mahalanobis envelope abstention are agnostic to the aerospace domain and applicable to any survival-model surrogate with a degenerate target mass at one boundary — a common pathology in clinical risk modelling.

**Declarations.**

- **Originality.** The manuscript has not been previously published and is not under concurrent consideration at any other journal.
- **AI disclosure.** Generative AI tools (Claude Code, Anthropic) were used as a coding and prose-revision assistant under direct human supervision. AI did not generate scientific content, did not author the manuscript, and was not used to fabricate data, citations, figures, or analyses. All scientific claims and numerical results were derived from the released code base and verified by the authors. No AI-generated text was retained without manual review.
- **Conflicts of interest.** All authors declare no conflicts of interest.
- **Funding.** This work received no external funding.
- **Ethical approval.** Not applicable. The study uses a published computational grid (ADRAC) and synthetic VO₂ trajectories; no human or animal subjects were involved.
- **Data and code availability.** Repository: https://github.com/strikerdlm/DCS. License: research-use. Reproduction is end-to-end deterministic via `docs/runbook.md` (~3 minutes on CPU).
- **Suggested reviewers.** Five candidates with relevant expertise in conformal prediction in clinical contexts, ML surrogates of physiological/biomedical risk models, and TinyML for wearable physiological monitoring are listed in the accompanying suggested-reviewers file. None has co-authored with us in the past three years; none shares our institutional affiliation; none is a member of the CMPB editorial board to our knowledge.
- **Software product.** The TinyDCS Python library, its ONNX exports at four size tiers (17 KB / 47 KB / 211 KB / 891 KB regressor + paired classifier), and a `tinydcs.zi` API for the production zero-inflated configuration are released open-source as part of this submission. The release supports CPU and is positioned for Cortex-M validation in follow-up work.

We confirm that all authors have read and approved the submitted version, and that the manuscript reports our original work. We thank you and the reviewers for your time and consideration.

Sincerely,

**Diego Malpica, MD** *(corresponding author)*
Subdirectorate of Aerospace Sciences
Direction of Aerospace Medicine, Colombian Aerospace Force
Bogotá DC, Colombia
Email: diego.malpica@fac.mil.co

**Marian Farfán, MD**
Subdirectorate of Aerospace Sciences
Direction of Aerospace Medicine, Colombian Aerospace Force
Bogotá DC, Colombia
