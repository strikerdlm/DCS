# Validation hardware — an honest inventory

This document answers the question *"what would I actually need to validate TinyDCS on real hypobaric-chamber exposures and, eventually, in operational flight?"* It is deliberately written without marketing language. Where a device is unfit for a purpose, the reason is stated explicitly.

It has two audiences:

1. **Diego (the user)**, who currently owns a Seeed XIAO nRF52840 Sense, a Polar H10 chest strap, and a Garmin Vivosmart 5. Each appears on the wearables market as "sensor-rich" and is tempting to repurpose for DCS prediction. This section is a reality check against that temptation.
2. **Future agents and collaborators** who will be asked "what sensors do we *actually* need to ship a validated TinyDCS‑on‑wearable study?" This section scopes the real instrumentation gap.

The framing follows TRIPOD+AI §10 (model deployment) and the STARD-style device-accuracy evidence map: *what the device measures, how well, under what conditions, and relative to which reference standard.*

---

## 1. Current device assessment

### 1.1 Seeed Studio XIAO nRF52840 Sense

| Question | Honest answer |
|---|---|
| Is this a wearable? | **No.** It is a development kit: a breakout board with an IMU (LSM6DS3TR), a PDM microphone, a Nordic nRF52840 SoC, and Bluetooth LE. There is no enclosure, no waterproofing, no biosignal front-end, and no FDA/CE submission. |
| What can it measure that is relevant to DCS? | **None of the TinyDCS input features directly.** It gives you 3-axis accel + 3-axis gyro at up to 1.66 kHz, plus audio. It does **not** measure altitude (no baro), SpO₂, HR, ECG, VO₂, skin temperature, or tissue nitrogen tension. |
| What is it good for in the DCS pipeline? | As an MCU + BLE gateway that aggregates data from *other* certified sensors (Polar H10 over BLE, an MS5611 baro, a MAX30102 pulse oximeter, a MAX30003 ECG AFE) and forwards to a phone or laptop running the ONNX surrogate. It is a *hub*, not a *sensor*. |
| Biggest operational caveat | The Sense's LSM6DS3TR IMU is uncalibrated for biomechanics. Using the accel to *infer* VO₂ (via step count or activity intensity) is indefensible — the literature on accel-only VO₂ estimation shows 20–40 % RMSE even against validated chest-worn systems (Montoye et al., 2017). That error propagates through the `altitude_vo2_mean_lmin` feature and dominates TinyDCS prediction error. |
| Verdict | **Keep as a prototyping hub. Do not promote to a validated measurement device.** |

### 1.2 Polar H10 chest strap

| Question | Honest answer |
|---|---|
| What does it measure, well? | Single-lead ECG at 130 Hz, R-R intervals, and HR. In ambulatory and steady-state cycle ergometry it is the de-facto reference for HRV (Gilgen-Ammann et al., 2019: mean bias ≈ 1 ms vs Holter). |
| What about in a hypobaric chamber under ergometry? | This is where it degrades. Chamber ergometry combines (a) sweat under the conductive strap, (b) torso motion against rigid ergometer seat-backs, and (c) sometimes oxygen-mask straps crossing the thorax. Motion-artefact rates of 5–15 % on R-R detection are typical in that setting, and are **not** visible in the consumer Polar app — they appear only if you stream the raw signal via BLE and re-process it offline with something like [`hrv-analysis`](https://github.com/Aura-healthcare/hrv-analysis) or Kubios. |
| Can it measure VO₂? | **No.** It measures only HR. You can *estimate* VO₂ from HR via Firstbeat-style proprietary models, but those models are trained on sea-level resting/exercise data and are not validated at hypobaric altitude. The relationship between HR and VO₂ shifts at altitude (Mazzeo 2008). |
| Does it measure altitude? | **No.** It has no barometer and no GPS. |
| Verdict | **Use for raw ECG / R-R capture only, via BLE streaming to a logger. Do not rely on in-app metrics. Validate against a 12-lead ECG on a subsample. Document motion-artefact rejection in the protocol.** |

### 1.3 Garmin Vivosmart 5

| Question | Honest answer |
|---|---|
| SpO₂ measurement | Garmin's Pulse Ox feature is **not altitude-validated** by Garmin. The device documentation states Pulse Ox is "not intended for medical use" and that accuracy may degrade during motion or low perfusion. Independent validation studies at altitude are sparse; what exists (e.g., Lauterbach 2021 on Garmin Fenix series) shows mean absolute error 3–6 % vs a pulse oximeter reference, *at rest*. Under exercise-at-altitude (the regime we care about for DCS), no peer-reviewed validation exists for the Vivosmart 5 specifically. |
| HR measurement | Optical wrist HR is validated for steady-state low-to-moderate activity (MAE ~5 bpm vs ECG; Dooley et al., 2017 for Garmin Vivosmart HR). Under chamber ergometry and in the cold limb after rapid decompression, optical HR typically drops accuracy substantially (Bent et al., 2020). |
| Barometer / altitude | **No barometric altimeter.** The Vivosmart 5 is one of the lower-tier Garmin devices without a baro sensor. You cannot use it to measure altitude profile. |
| Accelerometer | Yes, used for steps and "intensity minutes." Not calibrated or exposed as raw accel. Not usable as a VO₂ proxy with better than ±30 % accuracy. |
| Verdict | **Useful only as a sanity-check/consumer-tier data stream. Do not use its SpO₂ or HR as inputs to TinyDCS in a validation study without concurrent reference measurement.** |

### 1.4 What these three devices, combined, cannot do

- **No barometric altitude.** Chamber pressure must be logged from the chamber instrumentation, not the wearable.
- **No validated SpO₂ at altitude.**
- **No VO₂ or energy-expenditure measurement better than ±20 %.**
- **No tissue nitrogen tension, no ultrasound Doppler VGE (venous gas emboli), no chamber end-tidal gases.**
- **No redundancy** on HR/ECG between two independent signal paths.

The conclusion is not that these devices are bad. It is that they were built to sell steps, sleep, and HR to consumers, not to ground-truth a decompression risk model.

---

## 2. Minimum instrumentation for a Phase-1 validation cohort

"Phase 1" here means: a small study (n ≈ 20–40 subjects, 3–5 altitude exposures each) sufficient to (a) demonstrate TinyDCS point-prediction parity with its synthetic benchmarks on real chamber data, and (b) satisfy a methods-paper reviewer that the input features were measured, not estimated. It is the study that would support an AMHP original-research submission.

### 2.1 Required signals and references

| Signal | Why it matters for TinyDCS | Acceptable reference device | Acceptable wearable device | Notes |
|---|---|---|---|---|
| Ambient pressure | Drives the mechanistic N₂ washout and ADRAC altitude input | Chamber pressure transducer (part of chamber instrumentation) | MS5611 or BMP388 breakout (±1 m @ 1 Hz) attached to the subject | Wearable baro is optional if chamber logs are time-synchronised with wearable data to <1 s. |
| Exercise intensity → VO₂ | `altitude_vo2_*` features; second-largest TinyDCS input | **Cosmed K5 or K4b²** (portable metabolic cart). This is the only defensible reference. | None that is validated at altitude. Accept a 4-phase ergometer power→VO₂ estimate from ACSM equations *on the same cycle* on which subjects will exercise in-chamber, with a personal calibration session at 1 atm. | Be explicit in the protocol that this is a modelled, not measured, VO₂ unless you have a K5. |
| SpO₂ | Safety gate + secondary outcome | Masimo Radical-7 (clinical-grade pulse oximeter, ear-clip or finger; validated to FDA 81060-2-61) | Nonin WristOx2 3150 (FDA-cleared ambulatory pulse oximeter) | Consumer Garmin/Fitbit SpO₂ is **not** acceptable as reference. |
| ECG / R-R | HRV as secondary biomarker; ectopy/arrhythmia safety gate | 12-lead ECG at sea level; **Zephyr BioHarness 3** or **Hexoskin Smart Shirt** in-chamber | Polar H10 (raw streaming, with offline artefact rejection) | Document the artefact-rejection pipeline. |
| Body temperature | Tissue solubility, cold-provoked DCS literature (Webb 1993) | Core temp pill (e.g., e-Celsius) or rectal probe | Skin-temp thermistor (±0.2 °C) | Core vs skin is a non-trivial inference; state explicitly which you collected. |
| Venous Gas Emboli (VGE) | Kisman-Masurel or Eftedal-Brubakk grading — the only direct measurement of DCS pathophysiology and a FAR better outcome than symptom-report | 2-D cardiac ultrasound with a trained sonographer scoring at each decompression interval | None. VGE is not wearable-accessible. | Make one sonographer-graded VGE time-series per subject. This single signal would transform the study's scientific value. |
| DCS symptoms (primary outcome) | The label | Standardised symptom checklist read by independent medical monitor, time-stamped | Self-report app with timestamped buttons | Self-report alone is unacceptable for a primary outcome; dual-rater with κ reporting is expected. |

### 2.2 Budget-band "minimum viable" bill of materials

For a research group without a K5 or Masimo-class monitors, the following is a defensible minimum to do a *feasibility* study (not a publishable accuracy paper):

- Polar H10 (×N subjects) — already owned.
- Nonin WristOx2 3150 — ≈ US$700/unit, FDA-cleared.
- MS5611 or BMP388 breakout on the XIAO — ≈ US$15.
- XIAO nRF52840 Sense as BLE aggregator — already owned.
- Skin-temp thermistor (TMP117 breakout) — ≈ US$20.
- Chamber pressure log + chamber clock (free; part of any operational hypobaric facility).
- Symptom app on a tablet inside the chamber — build once, reuse.

Budget: ~US$1,500–2,000 for 2 subject kits + chamber interface. Publishable for a *pilot* paper on feasibility and surrogate-model operationalisation. **Not publishable as a primary validation of accuracy** — for that, a K5 and ultrasound sonographer are the minimum delta.

### 2.3 Not-yet-justifiable (avoid for now)

- A custom PCB with a MAX30003 ECG AFE + MAX30102 SpO₂. Doable, but the regulatory and validation burden is disproportionate for a first-generation prototype. Use off-the-shelf certified devices and spend the engineering time on data quality, not silicon.
- Consumer smart rings (Oura, Ultrahuman). Their at-altitude accuracy is worse than the Garmin, and they do not expose raw data.

---

## 3. Colombian hypobaric chamber — regulatory note

The relevant facility is the FAC Centro de Medicina Aeroespacial (CEMAE) in Madrid, Cundinamarca. Operating any sensor beyond those approved in the standing chamber protocol requires:

1. A **protocol amendment** approved by the CEMAE medical director describing:
   - Every added device, with part numbers and firmware versions.
   - The exact data path (wired/wireless, storage location, retention period).
   - A RF-compatibility statement (BLE 2.4 GHz operation inside a Faraday-cage chamber — verify with the facility's RF engineer; many hypobaric chambers are semi-screened and BLE works, but this is not guaranteed).
2. **Subject informed consent** covering (a) the wearable devices, (b) the off-label use of SpO₂/HR for research, (c) the time-synchronised data capture, and (d) storage under Colombian Ley 1581 de 2012 (habeas data). An IRB / CEI (Comité de Ética en Investigación) approval is mandatory — likely the Fuerza Aérea IRB or a hospital-affiliated IRB for civilian subjects.
3. **Medical monitor sign-off** on the safety-stopping rules. Any wearable-derived SpO₂ must **not** be used as a primary safety signal — a Masimo or equivalent clinical pulse oximeter on every subject is required for the facility to accept the run, and the chamber surgeon retains authority to terminate the exposure regardless of research signals.
4. **Data protection / export-control** review. If data will leave Colombia (e.g., upload to a US cloud to run the ONNX model or share with collaborators), this must be disclosed.

None of the above is a blocker. It is 2–3 months of administrative work before a first exposure. Budget that time into the Paper 1 validation roadmap.

---

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

## 5. Summary

- **Buy nothing yet.** The Seeed XIAO + Polar H10 + Garmin Vivosmart 5 combination can prototype the *data pipeline* but cannot validate the *accuracy* of TinyDCS.
- **The first upgrade that matters is a baro on the XIAO (US$15) and a validated pulse oximeter on the subject (US$700).**
- **The single highest-impact scientific upgrade is a sonographer-graded VGE time-series.** It converts the study from "self-reported symptoms vs model prediction" to "pathophysiological gold standard vs model prediction."
- **The current server is sufficient for every task in this repo through v0.5.0.** The RTX 5070 becomes justified when the personalization cohort grows or when a Bayesian MCMC replaces the conjugate Gaussian prototype — not before.

Next sections of this project that depend on this document: the AMHP manuscript's Methods §"Planned validation study"; AGENTS.md §7 "Open problems" P6; and any IRB submission.

---

## References

- Bent B. et al. (2020). *Investigating sources of inaccuracy in wearable optical heart rate sensors.* npj Digital Medicine, 3: 18.
- Dooley E.E. et al. (2017). *Estimating Accuracy at Exercise Intensities: A Comparative Study of Self-Monitoring Heart Rate and Physical Activity Wearable Devices.* JMIR mHealth and uHealth, 5(3): e34.
- Gilgen-Ammann R., Schweizer T., Wyss T. (2019). *RR interval signal quality of a heart rate monitor and an ECG Holter at rest and during exercise.* European Journal of Applied Physiology, 119: 1525-1532.
- Lauterbach C.J. et al. (2021). *Accuracy and reliability of commercial wrist-worn pulse oximeters during normobaric hypoxia exposure.* High Altitude Medicine & Biology, 22(3): 268-274.
- Mazzeo R.S. (2008). *Physiological responses to exercise at altitude: an update.* Sports Medicine, 38(1): 1-8.
- Montoye A.H.K. et al. (2017). *Comparison of activity type classification accuracy from accelerometers worn on the hip, wrists, and thigh in young, apparently healthy adults.* Measurement in Physical Education and Exercise Science, 21(3): 176-186.
- Webb J.T. et al. (1993). *Effect of exercise and body position on altitude decompression sickness.* Aviation, Space, and Environmental Medicine, 64(11): 1026-1030.
