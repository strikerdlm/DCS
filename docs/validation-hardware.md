# Measurement and validation in a hypobaric chamber

Clinical DCS validation requires a defined population and exposure, an independently adjudicated clinical outcome, and follow-up through the stated horizon. Validation of a VGE model requires appropriately timed and graded bubble observations. Agreement with a published equation or with a frozen surrogate can be checked using its declared inputs without observing either endpoint. [NASA chamber outcome and ascertainment methods, §§2.2–2.4](https://ntrs.nasa.gov/api/citations/20200004317/downloads/20200004317.pdf)

## 1. Equipment already available

| Device | Measurement or development role | Evidence to record |
|---|---|---|
| Seeed Studio XIAO nRF52840 Sense | Bluetooth logger with an inertial sensor and microphone. An external transducer or the chamber log supplies pressure. | Record the pressure source, calibration and synchronization, including any clock resets. [Manufacturer specifications](https://wiki.seeedstudio.com/XIAO_BLE/) |
| Polar H10 | Heart rate, R–R and raw ECG for an optional cardiac or wearable substudy. | Record sensor placement, raw data completeness, motion artifacts and agreement with the reference selected for that substudy. [Polar sensor SDK](https://github.com/polarofficial/polar-ble-sdk) |
| Garmin vívosmart 5 | Wrist heart rate and pulse-oximetry estimates for exploratory measurement. | Record wear conditions and motion. The manufacturer describes its pulse-oximetry measurements during stillness. [Garmin owner's manual](https://www8.garmin.com/manuals/webhelp/GUID-8674F17E-62B2-48DE-927A-251611664658/EN-GB/vivosmart_5_OM_EN-US.pdf) |

## 2. Measures for each study endpoint

| Study variable | Measurement record |
|---|---|
| Clinical DCS | Timestamp participant symptoms, physical findings, the clinical assessment, first and last possible onset, treatment, follow-up and censoring. Prespecify diagnostic criteria and the review process. Include assessments during ascent, at plateau and after return when the study endpoint includes those periods. |
| Any VGE or Grade IV VGE | Record modality, anatomical site, scan times relative to ascent and return, rest or provocation, grading scale, reader and missing observations. The last negative and first positive scan bracket the time of first detection. A Doppler grade and an echocardiographic grade require an explicit mapping before outcomes can be pooled. |
| Body-experienced pressure, time and breathing gas | Record the calibrated chamber or suit absolute pressure, clock, gas fractions and delivery, phase changes, interruptions and return. Document whether each value was measured, prescribed or assumed. |
| Prebreathe workload and activity at altitude | Record posture, ambulation, activity and timing by phase. If the model requires oxygen consumption, identify the calibrated gas-exchange system or other validated measurement method, units and test conditions. Label an equation-based oxygen-consumption estimate and a published workload assignment separately. |
| Secondary measurements | Select ECG, SpO₂, skin or core temperature, or other signals for a prespecified endpoint or measurement study. Their completeness and accuracy can be assessed alongside the exposure record. |

Connolly and colleagues studied 15 healthy men during repeated chamber ascents. At 25,000 ft five exposures produced diagnosed limb-pain DCS. Grade 4 VGE preceded all five events and also occurred in 18 of the 37 other exposures in that comparison. The positive predictive value was 5/23 (21.7%). Clinical assessment and serial precordial imaging therefore supplied different outcomes in the same participants. The counts refer to exposures, including repeat observations. [Connolly et al., 2023, pp. 670–671 and Table III](https://tgsmith.com/PDFs/DCS_2023.pdf)

### Equipment and study size

A synchronized chamber log, gas-delivery record and standardized clinical assessment can support a study of symptomatic DCS. Ultrasound is part of a VGE substudy when the chosen endpoint requires bubble detection. A metabolic cart is one way to obtain measured VO₂. Select equipment by its validated performance for the intended signal and exposure conditions. A clinical prediction study also needs enough independently assessed events and follow-up for the precision claimed, with repeated exposures grouped by participant.

## 3. Chamber governance

For a FAC CEMAE study, document the facility's current authorized monitoring and stopping procedures, medical oversight, ethics review, consent, and data handling. Record approval for any added device and test its compatibility and clock synchronization before participant measurements. Safety monitoring follows the facility's controlled procedure. Maintain the research record of clinical outcomes separately from telemetry and from contemporaneous operational decisions.

## 4. Training-hardware reality check

Diego has two options for model training and evaluation:

### 4.1 Current OpenClaw server (default)

Every headline number in this repo through v0.5.0 was produced on this machine:

- LightGBM training (zero-inflated, 3×models @ 300 trees): seconds on CPU.
- Conformal calibration: seconds.
- Synthetic personalization demo (200 subjects × 20 exposures × 5 k-values): minutes on CPU.
- ONNX export + 10 k-row benchmark: seconds.
- Full `pytest tests/ -q`: ~3 seconds.

**No GPU is required for anything currently in the repo.** The model family (gradient-boosted decision trees) is CPU-native and GPU ports of LightGBM are not meaningfully faster on this workload size (< 20 k training rows, < 20 features).

### 4.2 Home PC (Ubuntu, i5-12th, 64 GB RAM, RTX 5070)

The RTX 5070 only becomes materially useful in one of these future scenarios, and none of them is blocking Paper 1:

1. **NumPyro / PyMC MCMC for the full hierarchical Bayesian model** (Paper 2, Implementation C as sketched in `docs/papers/paper-2-scope.md`). Once the cohort grows to ≳ 500 subjects × ≳ 20 exposures with a partial-pooling covariance model, CPU NUTS may take hours-to-days. NumPyro on GPU (JAX backend) is typically 10–50× faster on that workload. **This is the first actually-justified use of the 5070.**
2. **Neural quantile regression / monotonic normalising flows** as an alternative to LightGBM-CQR (see AGENTS.md §4 "speculative directions"). Training times in the 10-minute range on GPU vs tens-of-minutes on CPU; useful for iteration speed, not a blocker.
3. **Large-scale synthetic cohort generation** if you ever run 10 k+ subject-exposure simulations via `ornstein_uhlenbeck_vo2`. That particular loop is CPU-bound and embarrassingly parallel; a GPU does not help — a workstation with 12+ cores does. The i5-12th has 16 threads, so even this is a win over the server, without needing the GPU.

### 4.3 When to migrate work to the home PC

Switch only when one of the following is true:

- A training job now takes > 30 minutes on the server and iteration pace is suffering.
- You are about to run a NumPyro MCMC sweep > 1 h CPU budget.
- You need to ship a reproducibility environment that will outlive this server.

Otherwise the server is the right surface because:

- All repo paths, artifacts, and git state are here.
- Cron-scheduled TinyDCS jobs (if any) would need to be ported.
- Data-provenance gets muddier when there are two training machines.

### 4.4 Exact migration steps (if and when it happens)

```bash
# On the home PC (Ubuntu 22.04 or 24.04 assumed)
git clone https://github.com/strikerdlm/DCS
cd DCS
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install onnx onnxruntime onnxmltools skl2onnx onnxconverter_common
pytest tests/ -q
# Then follow docs/runbook.md steps 1–5.
```

For NumPyro GPU work (when needed):

```bash
pip install --upgrade "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
pip install numpyro
```

`jax[cuda12_pip]` is the CUDA 12 wheel. For a 5070 (Blackwell, compute capability 12.x), verify the installed CUDA toolkit is ≥ 12.4 and that `jax.devices()` reports the GPU before running MCMC.

---

## 5. Study records

A wearable replay tests data transfer and timing logic. Physical-device accuracy, dropout and agreement with a reference require observations under the intended conditions. The existing replay test exercises the tablet/wearable telemetry contract.

Clinical DCS and VGE analyses retain their own definitions, observation times and missingness. For clinical DCS, follow-up after return determines which delayed events can be counted. For VGE, the scan schedule and grading method determine which events can be detected. [NASA chamber study](https://ntrs.nasa.gov/api/citations/20200004317/downloads/20200004317.pdf) · [Connolly et al., 2023](https://tgsmith.com/PDFs/DCS_2023.pdf)
