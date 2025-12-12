**Disclaimer:**
> This repository and all associated models, scripts, and data are provided strictly for academic and research purposes. The models herein are based on published theory and experimental data, but they are not validated for clinical, operational, or real-world risk prediction.  
> **These tools do not predict, diagnose, or guarantee the risk of decompression sickness (DCS) for any individual or exposure scenario.**  
> No part of this project should be used as a substitute for professional medical advice, operational safety protocols, or regulatory guidance.  
> The authors and contributors accept no liability for any use, misuse, or interpretation of the information or code provided in this repository.

# DCS (Decompression Sickness) Models and Analysis

## Overview
This repository contains a comprehensive suite of models, scripts, and data for the analysis and simulation of decompression sickness (DCS) in various environments. The project integrates legacy code, machine learning models, NASA models, and supporting documentation for research and operational use.

## Directory Structure
- **3RTU_BU_2025_02_02/**: Documentation and theory for 3RTU models.
- **3RUT_MBe1/**: Markdown documentation and theory for 3RUT models.
- **BU_3RUT/**: Contains 3RUT_MBe1 with calibration scripts, risk models, configs, and results.
- **BU_Model_2025/**: Main Python scripts for DCS simulation, CLI, and outputs (models, predictions).
- **DCS Python Project_old/**: Legacy code and previous BU projects.
- **Dive_DCS/libbuhlmann-master/**: Buhlmann decompression model implementation (with its own README).
- **ML model/**: Machine learning scripts, results, and visualizations.
- **Model_Rel_Candidate/**: Candidate models and metrics for release.
- **NASA_model/**: NASA-specific DCS model.
- **output/**: Model outputs and predictions.
- **.vscode/**: Editor settings.
- **__pycache__/**: Python bytecode cache (can be ignored).

## Getting Started
### Prerequisites
- Python 3.8+
- Recommended: Create a virtual environment

### Installation
```sh
git clone <repo-url>
cd DCS
pip install -r requirements.txt  # (if requirements.txt exists)
```

### Running Models
- **BU_Model_2025:**
  ```sh
  python BU_Model_2025/dcs_cli.py --help
  ```
- **ML model:**
  ```sh
  python "ML model/dcs_cli.py" --help
  ```

### Outputs
- Model outputs (predictions, parameters, encoders, scalers) are stored in the `output/` directories of respective modules.
- Example output files: `.xlsx` (predictions), `.joblib` (models, encoders, scalers).

## Directory Details
### BU_Model_2025/
- `dcs_cli.py`, `dcs_app.py`, `DCSv10.py`, `DCSv11.py`: Main simulation and CLI scripts.
- `output/`: Contains `.joblib` model files and `.xlsx` prediction outputs.

### Dive_DCS/libbuhlmann-master/
- Contains its own documentation and source for the Buhlmann model.

### BU_3RUT/3RUT_MBe1/
- Calibration, risk analysis, and test scripts for 3RUT models.

### ML model/
- `dcs_simulation.py`, `dcs_cli.py`, `dcs_app.py`: ML-based DCS simulation and analysis.

## 🖥️ Streamlit Risk Explorer

A modern web interface built with **Streamlit** (see `streamlit_app.py`) allows interactive exploration of multiple DCS risk model families. The UI is **model-aware**: it shows **only** the inputs that a selected model actually uses, and it displays **scientific validity + limitations** from artefacts already present in this repository.

Supported model families in the UI:

1) **ML surrogate (loaded artefacts)**: load a trained estimator + preprocessing artefacts (`.joblib`).  
2) **Mechanistic 3RUT‑MBe1**: recursion from NEDU TR 18‑01 (Appendix C/D) as implemented in `rut_mbe1_model.py`.  
3) **NASA ETR logistic (RM/NM)**: implements published equations from `NASA_model/conkin-dcs-exercise_2004.md`:
   - **NM (Eq. 14)**: \(P(DCS)\) from ETR + **sex**
   - **RM (Eq. 15)**: \(P(DCS)\) from ETR + **age**

### Quick start
```bash
# (inside your virtual-env)
pip install -r requirements.txt  # ensures Streamlit & Plotly are available

# Launch the UI
streamlit run streamlit_app.py
```

### Features
1. **Model-aware input forms** – the UI only shows variables used by the currently selected model.
2. **Accuracy & safety disclaimers** – explicit research-use-only language in the UI.
3. **Scientific validity panel** – per model, shows whatever metrics exist in-repo (and clearly marks missing ones as “not provided”).
4. **ML artefact loading** – point the app at a directory containing `scaler_*.joblib`, `onehot_encoder_*.joblib` (or `encoder_*.joblib`), and `model_*.joblib` / `simple_model_*.joblib` / `trained_model_*.joblib`.
5. **Mechanistic 3RUT‑MBe1 simulation** – time-resolved outputs + publication-style plots + CSV/HTML export.
6. **NASA ETR logistic calculator** – computes \(P1N2\), ETR, and \(P(DCS)\) using Eq. 14/15; exposes age/sex only when relevant.

> **Note:** These models are experimental and **must not** be used for clinical or operational decisions. See the repository disclaimer.

## Model input support matrix (UI)

The UI shows only the variables each model uses.

| Variable | ML surrogate (artefacts) | 3RUT‑MBe1 (mechanistic) | NASA ETR logistic (RM/NM) |
|---|---:|---:|---:|
| Altitude (ft) | ✅ | ✅ | ❌ |
| Time at altitude (min) | ✅ | ✅ | ❌ |
| Prebreathe time (min) | ✅ | ✅ | ✅ (PB duration) |
| Exercise level at altitude | ✅ (categorical) | ✅ (mapped to \(I_{ex}\)) | ❌ (assumed by study protocol) |
| Exercise during prebreathe | ⚠️ only if artefacts expect it | ✅ | ✅ via VO₂ input (simplified single-interval) |
| Prebreathe FiO₂ | ❌ | ✅ | ❌ (represented via Pa≈0 for 100% O₂ PB) |
| Breathe O₂ at altitude | ❌ | ✅ | ❌ |
| Ascent / decompression duration | ❌ | ✅ | ❌ (study profile assumption) |
| Age | ⚠️ only if artefacts expect it | ❌ | ✅ (RM) |
| Sex / gender | ⚠️ only if artefacts expect it | ❌ | ✅ (NM) |
| VO₂ during PB (mL/kg/min) | ❌ | ❌ | ✅ |
| P0 (initial tissue ppN₂, psia) | ❌ | ❌ | ✅ |
| Pa (ambient ppN₂ during PB, psia) | ❌ | ❌ | ✅ |
| P2 (ambient/suit pressure after depressurization, psia) | ❌ | ❌ | ✅ |
| λ₂ (lambda) | ❌ | ❌ | ✅ |

Legend:
- ✅ supported as a first-class input in the UI for that model
- ⚠️ shown only if detected/required by loaded ML artefacts
- ❌ not used by that model in this repository implementation

## Scientific validity (what is currently available in this repo)

This repository contains multiple model families with different validation styles. Not every model has a complete, publication-ready set of metrics (e.g., sensitivity/specificity/PPV/NPV/ROC/AUC/CI95%) bundled in one place.

- **ML surrogate (ADRAC-derived dataset)**:
  - Metrics are reported in `Model_Rel_Candidate/Metrics.txt` (e.g., R²/MAE/RMSE for a January 2025 run).
  - These are regression-style metrics against ADRAC-derived labels (risk %), not clinical outcomes.
- **Mechanistic 3RUT‑MBe1**:
  - The theory doc `BU_3RUT/3RUT_MBe1/3RUT_Theory.md` discusses chi-square goodness-of-fit and comparisons versus other models (e.g., ADRAC / NASA-RM2004).
  - A consolidated ROC/sensitivity/specificity table is **not** currently included in this repo.
- **NASA ETR logistic (RM/NM)**:
  - The UI implements Eq. 14/15 from `NASA_model/conkin-dcs-exercise_2004.md` and is intended as a transparent calculator.
  - The repo does not currently bundle a ready-to-run evaluation set that outputs ROC/AUC/sensitivity/specificity/PPV/NPV for this implementation.
- **Legacy ASEM metrics snapshot**:
  - A text metrics snapshot is present at `DCS Python Project_old/BU_2024/model_validation_metrics_20250128_1245.txt`.

## Roadmap: publishable, Q1 journal-grade app (step-by-step)

The path to a publishable scientific application is primarily about **traceability, verification/validation, uncertainty quantification, and reproducibility**. A suggested iteration roadmap (aligned with best scientific software practices and publishable methods reporting):

1) **Model registry + contracts (v0.1)**
   - Define a single “model interface” in code: required inputs, units, valid ranges, and outputs.
   - Ensure each model declares its supported covariates (age/sex/altitude/exercise/O₂ breathing/etc.).
   - Require explicit **unit conventions** (atm vs mmHg, ft vs m) and an automated unit/shape validation layer.

2) **Data curation + ground-truth definition (v0.2)**
   - For each model family, define what “ground truth” means (ADRAC-derived risk %, observed DCS outcomes, VGE grades, etc.).
   - Create a versioned dataset manifest: source, inclusion criteria, missingness handling, and licensing constraints.
   - Pre-specify a **case definition** (binary DCS / ordinal severity / time-to-event), censoring rules, and what constitutes an “exposure”.

3) **Verification-first evaluation suite (v0.3)**
   - Add **model verification** tests that check the implementation against the published recursion/identities (e.g., Appendix C/D invariants), not just outcome metrics.
   - Add **numerical stability** tests (step-size sensitivity, extreme-but-valid inputs, monotonicity where theoretically required).
   - Ensure deterministic runs (fixed seeds where applicable; avoid non-deterministic ordering).

4) **Validation suite with publishable metrics (v0.4)**
   - Add a standardized evaluation harness that can compute:
     - **Sensitivity, specificity, PPV, NPV**
     - **ROC/AUC** (with confidence intervals)
     - **Calibration** (reliability curves, Brier score, calibration intercept/slope)
     - **Uncertainty** (CI95% / prediction intervals / bootstrap CIs)
   - Make the “decision threshold” explicit and justified (not arbitrary).
   - Separate **discrimination** from **calibration**; report both.
   - Report uncertainty with a documented procedure (e.g., bootstrap by study/protocol to respect clustering).

5) **External validation + robustness (v0.5)**
   - Perform strict train/validation/test separation by **study/protocol/group** (avoid leakage).
   - Validate on out-of-sample profiles (altitudes, prebreathe durations, exercise regimens) where possible.
   - Include subgroup analyses and prespecified robustness checks.

6) **Mechanistic vs ML reconciliation (v0.6)**
   - Document which covariates are mechanistically modeled vs purely statistical.
   - Add model comparison plots: risk vs time, hazard vs time, subgroup analyses.
   - Explicitly report the **validity envelope** (input ranges and protocols supported) for each model family.

7) **Reproducible builds + auditability (v0.7)**
   - Pin dependencies, log model versions, hash artefacts, and store run metadata.
   - Add deterministic evaluation runs and artifact provenance (dataset version → model version → metrics).
   - Publish a reproducible “methods run” that regenerates key tables/figures from raw inputs.

8) **Scientific & safety framing (v0.8)**
   - Strengthen disclaimers, intended-use statements, and “not for operational use” guardrails.
   - Add clear “validity envelope” constraints in UI (warn/disable extrapolation beyond training range).
   - Adopt a reporting checklist (e.g., TRIPOD/TRIPOD-AI style) for any predictive claims.

9) **Manuscript-ready outputs (v1.0)**
   - Auto-generate publication-quality figures and tables (metrics, subgroup performance, calibration).
   - Provide a transparent methods section mapping each code path to the underlying theory documents.
   - Produce a “model card” style summary per model family (intended use, limitations, data, metrics, uncertainty).

## Contributing
1. Fork the repo and create your branch (`git checkout -b feature/fooBar`)
2. Commit your changes (`git commit -am 'Add some fooBar'`)
3. Push to the branch (`git push origin feature/fooBar`)
4. Create a new Pull Request

## License
- See `Dive_DCS/libbuhlmann-master/LICENSE` for Buhlmann model.
- Other code: Specify your license here (e.g., MIT, GPL, etc.).

## Acknowledgments
- NASA, Buhlmann model authors, and all contributors.
- Special thanks to all researchers and developers who contributed to the DCS modeling efforts. 