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

A modern web interface built with **Streamlit** (see `streamlit_app.py`) allows interactive exploration of any trained DCS model artefacts.

### Quick start
```bash
# (inside your virtual-env)
pip install -r requirements.txt  # ensures Streamlit & Plotly are available

# Launch the UI
streamlit run streamlit_app.py
```

### Features
1. **Single prediction** – enter exposure parameters and instantly obtain the predicted DCS risk.
2. **Parameter sweep** – vary altitude, time at altitude, or pre-breathing time to visualise how risk evolves.
3. **Feature importance** – bar-chart of `feature_importances_` when provided by the underlying estimator.
4. **Model-agnostic loading** – simply point the app to any directory containing matching `scaler_*.joblib`, `onehot_encoder_*.joblib`, and `simple_model_*` (or `trained_model_*`) artefacts; the latest timestamped versions are selected automatically.

> **Note:** These models are experimental and **must not** be used for clinical or operational decisions. See the repository disclaimer.

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