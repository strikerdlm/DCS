<div align="center">

# TinyDCS

**A wearable-grade decompression-sickness risk stack for aerospace and space operations.**

*Hybrid physiology + ML. Calibrated uncertainty. Edge-deployable. Mission-planning aware.*

<br>

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![Frontend](https://img.shields.io/badge/frontend-React%20%2B%20TypeScript-0ea5e9)
![Status](https://img.shields.io/badge/status-v0.6.0--in--progress-orange)
![License](https://img.shields.io/badge/license-research--use--only-lightgrey)
![Tests](https://img.shields.io/badge/tests-25%2F25%20passing-brightgreen)

[Runbook](docs/runbook.md) .
[Scientific background](docs/scientific-background.md) .
[Methods](docs/methods.md) .
[Architecture](docs/architecture.md) .
[Validation hardware](docs/validation-hardware.md) .
[Changelog](CHANGELOG.md)

</div>

---

> **Research-only.** TinyDCS is an experimental research artifact. It is not a clinical device, not certified flight software, not certified EVA software, and must not be used as the sole basis for any aeromedical or operational decision. It is intended for model exploration, scenario planning, and engineering trade studies inside clearly stated validity envelopes.

---

## What TinyDCS Is

TinyDCS combines established altitude decompression-sickness model families with a compact machine-learning surrogate and an interactive space-operations frontend. The core model estimates DCS-informed risk from exposure pressure, prebreathe, exposure time, and workload; the frontend turns that into mission-style planning displays for aviation, commercial EVA analogs, lunar EVA, and habitat pressure-management decisions.

The intended future form factor is a small worn computer or wearable companion that can ingest pressure, activity, and physiological telemetry, then return:

- DCS point risk and interval estimates;
- in-envelope or abstain status;
- risk trajectory over the exposure;
- NASA-style 5x5 likelihood x consequence categorization;
- decision implication: proceed, monitor, modify, delay, abort, or abstain.

---

## Space Operations Focus

TinyDCS is being adapted from altitude-DCS modeling toward space operations workflows where decompression risk is coupled to suit pressure, habitat atmosphere, prebreathe, workload, and return/repressurization options.

Current target use cases:

- **Commercial EVA operations:** private or commercial stand-up EVA analogs, short depressurization profiles, limited workload, suit oxygen, and rapid return/repressurization.
- **Artemis-relevant lunar EVA:** 4-6 h lunar surface task days with changing workload, suit pressure tradeoffs, prebreathe assumptions, dust, thermal strain, communications, and return-to-habitat/lander timing.
- **Habitat pressure management:** comparison of scheduled EVA now versus delayed EVA after extended prebreathe or altered oxygen/pressure profile.
- **Aviation and chamber operations:** hypobaric altitude exposures, prebreathe planning, wearable telemetry exploration, and model-envelope education.

The project remains deliberately conservative: unsupported profiles trigger abstention rather than silently extrapolating.

---

## Frontend Dashboard

The active interface is the React + TypeScript dashboard in `frontend/`.

### EVA Mission Simulator

The dashboard now includes an **EVA Simulator** under `Mission Planning` with three primary scenarios:

| Scenario | Purpose | Main controls |
|---|---|---|
| **A. Commercial stand-up EVA analog** | Short vehicle depressurization, suit oxygen, limited workload, return/repressurization | habitat pressure/O2, prebreathe, suit pressure, short EVA duration, workload blocks |
| **B. Artemis-relevant lunar EVA day** | Lunar surface day with 4-6 h activity and changing workload | exploration atmosphere, suit pressure, PLSS margins, dust, sun exposure, radiation weather, shelter return time |
| **C. Habitat pressure-management decision** | Compare EVA now vs delayed or altered pressure/O2 profile | habitat pressure/O2, equilibration, extended prebreathe, suit pressure, EVA duration, workload |

For each scenario, the frontend reports:

- point-risk trajectory over time;
- 95% interval trajectory over time;
- in-envelope or abstain flag;
- maximum risk and time of maximum risk;
- time-integrated risk;
- 5x5 likelihood x consequence category;
- decision implication: `proceed`, `monitor`, `modify`, `delay`, `abort`, or `abstain`;
- decision alternatives, including delayed prebreathe, altered habitat atmosphere, higher suit pressure, shorter EVA, and lower peak workload.

The EVA screen also includes a multi-hazard 5x5 matrix for DCS, hypoxia, CO2 retention, thermal strain, dust contamination, fatigue/injury, radiation event, and consumables margin.

### Model Explorer

The existing model views remain available:

- ADRAC-derived risk predictor;
- NASA Conkin ETR logistic model;
- mechanistic 3RUT-MBe1 schematic preview;
- validation dashboard for the ADRAC closed-form fit;
- dose-response, risk landscape, tissue N2, and uncertainty visualizations.

Run it locally:

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
npm run build      # production build in frontend/dist/
npm run preview
```

---

## Python Model Stack

TinyDCS keeps the model code separate from the frontend so the same model logic can support notebooks, command-line runs, server APIs, and future edge runtimes.

Core packages:

- `mechanistic/adrac.py` - closed-form ADRAC log-logistic accelerated-failure-time model.
- `mechanistic/conkin_nasa.py` - NASA Conkin RM/NM logistic model using Exercise Tissue Ratio.
- `mechanistic/rut_mbe1.py` - Gerth 3RUT-MBe1 bubble-dynamics implementation; currently used only for shape studies until calibration reconciliation is complete.
- `tinydcs/simulator.py` - continuous-VO2 exposure wrapper.
- `tinydcs/features.py` - feature extraction, including pressure/workload and Conkin-style tissue-ratio features.
- `tinydcs/surrogate.py` - LightGBM surrogate, conformal interval logic, and out-of-distribution handling.
- `tinydcs/personalization.py` - prototype subject-level personalization layer.

Install and test:

```bash
pip install -r requirements.txt
pytest tests/ -q
```

Rebuild the compact surrogate and ONNX artifact from a clean checkout:

```bash
python scripts/01_clean_data.py \
    --input legacy/Model_Rel_Candidate/DCS_Risk_DB_2025.csv \
    --output artifacts/DCS_Risk_DB_2025_clean.parquet \
    --report artifacts/data_quality_report.md

python scripts/04_train_adrac_surrogate.py \
    --training artifacts/DCS_Risk_DB_2025_clean.parquet \
    --output-surrogate artifacts/tinydcs_adrac_zi.joblib \
    --output-baseline artifacts/adrac_baseline_zi.joblib \
    --output-metrics artifacts/metrics_adrac_zi.json \
    --output-figures artifacts/figures_adrac_zi \
    --no-run-leave-one-altitude-out --zi

python scripts/06_train_compact_surrogate.py \
    --training artifacts/DCS_Risk_DB_2025_clean.parquet \
    --output-metrics artifacts/compact_vs_full.json

python scripts/07_export_zero_inflated_onnx.py \
    --input-model artifacts/tinydcs_adrac_zi.joblib \
    --output-dir artifacts/zi_onnx \
    --benchmark-n 10000 \
    --tolerance 1e-4
```

---

## Repository Layout

```text
DCS/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
│
├── frontend/                    # React + TypeScript operational dashboard
│   ├── src/components/eva/      # EVA mission simulator
│   ├── src/components/models/   # model explainer views
│   ├── src/components/charts/   # ECharts visualizations
│   ├── src/data/                # scenario presets and validation data
│   ├── src/types/               # TypeScript contracts
│   └── src/utils/               # browser-side calculation utilities
│
├── mechanistic/                 # physics-informed model implementations
├── tinydcs/                     # surrogate-model package
├── scripts/                     # reproducible training/export runners
├── tests/                       # Python test suite
├── docs/                        # technical documentation and source notes
├── artifacts/                   # git-ignored generated models/metrics
└── legacy/                      # historical material retained for provenance
```

---

## Model Families

| Model | Paradigm | Operational role | Status |
|---|---|---|---|
| ADRAC | Log-logistic altitude-DCS survival model | Primary surrogate training target and browser baseline | Implemented |
| NASA Conkin RM/NM | Logistic model using Exercise Tissue Ratio | DCS-informed prebreathe/suit-pressure trade studies | Implemented |
| Gerth 3RUT-MBe1 | Tissue bubble-dynamics recursion | Future high-fidelity continuous-workload comparator | Calibration reconciliation open |
| TinyDCS surrogate | ML surrogate + calibrated intervals + abstention | Edge and wearable-oriented risk estimation | Implemented |
| EVA frontend simulator | Scenario logic + 5x5 LxC + decision implication | Mission-planning and trade-study interface | Implemented |

---

## Validity and Safety Limits

TinyDCS is useful only when its inputs and assumptions are visible. Current limits:

- **Surrogate target:** the ML model reproduces an existing parametric model; it is not trained on new observed EVA outcomes.
- **Operational certification:** no part of this repository is certified for flight, EVA, clinical care, or real-time crew safety decisions.
- **OOD behavior:** unsupported profiles should abstain rather than extrapolate.
- **3RUT-MBe1:** the current implementation under-reports DCS risk against known validation profiles and is not used as a quantitative source until reconciled.
- **Wearable telemetry:** HR, HRV, SpO2, activity, and pressure inputs require device-specific validation before use in any real campaign.
- **LxC matrix:** the 5x5 matrix is a decision-support visualization. It does not replace mission rules, flight rules, medical authority, or program-level risk acceptance.

---

## Current Status

| Capability | Status |
|---|---|
| ADRAC data cleaning and closed-form baseline | Done |
| Continuous-VO2 feature extraction | Done |
| Zero-inflated calibrated surrogate | Done |
| Compact ONNX export path | Done |
| React dashboard for model exploration | Done |
| EVA scenario simulator A/B/C | Done |
| 5x5 LxC and decision implication logic | Done |
| Habitat pressure-management comparison | Done |
| Subject-level personalization prototype | Done |
| 3RUT-MBe1 calibration reconciliation | Open |
| Prospective chamber or analog validation | Open |
| Wearable hardware integration | Open |

---

## Development Roadmap

Near-term engineering priorities:

1. Connect the EVA frontend to the Python model stack through a stable API contract.
2. Add exportable scenario reports for EVA planning reviews.
3. Add unit tests for EVA scenario calculations, interval generation, LxC mapping, and decision implication logic.
4. Add telemetry adapters for pressure, accelerometer-derived workload, HR/HRV, SpO2, and skin temperature.
5. Reconcile 3RUT-MBe1 against its source equations before using it for absolute risk.
6. Add hardware-in-the-loop tests for a small wearable or tablet-class runtime.
7. Add mission-rule configuration files so operators can tune thresholds without changing source code.

---

## References

See `docs/scientific-background.md` for the broader bibliography. The main technical anchors are:

- Abercromby, A., Conkin, J., & Gernhardt, M. (2015). Modeling a 15-min extravehicular activity prebreathe protocol using NASA's exploration atmosphere.
- Belobrajdic, B., Melone, K., & Diaz-Artiles, A. (2021). Planetary extravehicular activity risk mitigation strategies for long-duration space missions. https://doi.org/10.1038/s41526-021-00144-w
- Chullen, C., & Westheimer, D. (2011). Extravehicular Activity Technology Development Status and Forecast. https://doi.org/10.2514/6.2011-5179
- Conkin, J., & Gernhardt, M. L. (2004). A probability model of decompression sickness at 4.3 psia after exercise prebreathe. NASA TP-2004-213158.
- Gerth, W. A., Doolette, D. J., & Gault, K. A. (2018). A probabilistic model of altitude decompression sickness based on the 3RUT-MB model. NEDU TR 18-01.
- Kluis, L., & Diaz-Artiles, A. (2021). Revisiting decompression sickness risk and mobility in the context of the SmartSuit, a hybrid planetary spacesuit. https://doi.org/10.1038/s41526-021-00175-3
- NASA. Life Support Baseline Values and Assumptions Document. https://ntrs.nasa.gov/citations/20180001338
- NASA. Moon Mission Spacesuit Nears Milestone. https://www.nasa.gov/missions/artemis/nasa-moon-mission-spacesuit-nears-milestone/

---

## License

Research-use-only. See `LICENSE` for repository terms. NASA, USAFSAM, NEDU, ESA, and other cited source documents retain their original terms.
