# Highlights — TinyDCS

**Manuscript:** *TinyDCS: An edge-deployable machine-learning surrogate of the ADRAC altitude-decompression-sickness risk model with continuous-exposure covariates and calibrated uncertainty*
**Target journal:** Computer Methods and Programs in Biomedicine (Elsevier)
**Format:** 3–5 bullets, each ≤ 85 characters including spaces (CMPB Guide for Authors).

---

- TinyDCS surrogate of ADRAC reaches MAE 0.020 vs 0.086 for closed-form baseline.
- Compact 95 KB ONNX model with 2.44 μs/row CPU latency for wearable deployment.
- Zero-inflated two-stage calibration restores 95% coverage at low altitudes.
- Continuous-VO2 covariates with monotonicity constraints and OOD abstention.
- Bayesian personalisation prototype reaches r = 0.63 after 20 per-subject runs.

---

**Character-count verification (UTF-8 visible characters including spaces):**

| # | len | bullet |
|---|---|---|
| 1 | 79 | TinyDCS surrogate of ADRAC reaches MAE 0.020 vs 0.086 for closed-form baseline. |
| 2 | 78 | Compact 95 KB ONNX model with 2.44 μs/row CPU latency for wearable deployment. |
| 3 | 75 | Zero-inflated two-stage calibration restores 95% coverage at low altitudes. |
| 4 | 75 | Continuous-VO2 covariates with monotonicity constraints and OOD abstention. |
| 5 | 78 | Bayesian personalisation prototype reaches r = 0.63 after 20 per-subject runs. |

All bullets ≤ 85 characters. Verified via `python3 -c "len(s)"` on 2026-05-01.

**Portal note.** Some Editorial Manager portals accept Highlights as a free-text field rather than a file upload — copy the bullets verbatim. Others require a separate `.docx` or `.txt` file labelled `Highlights`. Have both forms ready.

**Notes on style:**

- Bullet 2 uses Greek lowercase mu (μ); some portals strip non-ASCII. If the portal mangles it, the ASCII fallback is `2.44 us/row` (one character shorter, still well under cap).
- Bullet 4 spells `VO2` without subscript for portal-text compatibility; the manuscript uses `VO\textsubscript{2}`.
- UK English: `personalisation` (bullet 5) consistent with manuscript convention (e.g. `neighbour-median` in §2.1).
