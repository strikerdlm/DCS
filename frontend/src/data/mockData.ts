/**
 * Real ADRAC validation data + model validity cards.
 *
 * `validationData` is loaded from `adrac_validation.json`, which is a 1,500-row
 * stratified sample of the cleaned ADRAC grid (n = 15,908) with the closed-form
 * log-logistic AFT prediction included for residual analysis.
 *
 * Citations live in `citations` and the per-model validity blurbs in
 * `modelValidityCards`. The "Validation Dashboard" shows true ADRAC reference
 * values vs the closed-form fit — no synthetic noise.
 */

import type {
  Citation,
  MLSurrogateInputs,
  MechanisticInputs,
  ModelValidity,
  NASAInputs,
  ValidationDataPoint,
} from "../types";
import adracValidationRaw from "./adrac_validation.json";

interface AdracValidationPayload {
  metrics: { mae: number; rmse: number; r2: number; n_train: number; n_sample: number };
  rows: ValidationDataPoint[];
}

const ADRAC_VAL = adracValidationRaw as AdracValidationPayload;

export const validationData: ValidationDataPoint[] = ADRAC_VAL.rows;
export const validationMetrics = {
  mae: ADRAC_VAL.metrics.mae,
  rmse: ADRAC_VAL.metrics.rmse,
  r2: ADRAC_VAL.metrics.r2,
  nTrain: ADRAC_VAL.metrics.n_train,
  nSample: ADRAC_VAL.metrics.n_sample,
};

export const modelValidityCards: Record<string, ModelValidity> = {
  ml_surrogate: {
    name: "ADRAC closed-form (Pilmanis 2004 functional form)",
    sources: [
      "mechanistic/adrac.py",
      "legacy/Model_Rel_Candidate/DCS_Risk_DB_2025.csv (cleaned)",
    ],
    notesMd: `- **Model family**: log-logistic accelerated-failure-time survival model from Kannan & Pilmanis (1998), fitted to the cleaned ADRAC grid (15,908 rows after \`tinydcs.data_clean.clean_dcs_risk_db\`).
- **What this is**: the *real* closed-form ADRAC baseline. It is NOT the LightGBM/ONNX surrogate (95 KB ONNX, 2.4 µs/row) advertised in the repo README — that one runs server-side; the browser build uses the ADRAC functional form so it runs everywhere.
- **Validity envelope**: altitude 18,000 – 40,000 ft, prebreathe 0 – 180 min, time-at-altitude 10 – 240 min, exercise ∈ {Rest, Mild, Heavy}.
- **Limitations**: predictions outside this envelope are extrapolations. Risk values are upper-bounded at 100 %; below ≈1 % the closed form saturates and should not be over-interpreted.`,
    metrics: [
      { key: "MAE (pp)", value: ADRAC_VAL.metrics.mae.toFixed(3) },
      { key: "RMSE (pp)", value: ADRAC_VAL.metrics.rmse.toFixed(3) },
      { key: "R²", value: ADRAC_VAL.metrics.r2.toFixed(4) },
      { key: "Training rows", value: ADRAC_VAL.metrics.n_train.toLocaleString() },
      { key: "Validation sample", value: ADRAC_VAL.metrics.n_sample.toLocaleString() },
    ],
  },
  mechanistic_3rut: {
    name: "Mechanistic 3RUT‑MBe1 (schematic preview)",
    sources: ["mechanistic/rut_mbe1.py", "docs/methods.md §M7"],
    notesMd: `- **What this view is**: a *schematic* time-resolved preview computed in TypeScript. Tissue N₂/O₂ follow Conkin single-compartment dynamics (τ₁/₂ = 360 min for N₂, 30 min for O₂); the hazard channel is a supersaturation × exercise dose proxy; the final P(DCS) shown on the gauge is the **real ADRAC closed-form** prediction at the same exposure parameters.
- **What this view is NOT**: the full bubble-evolution recursion in \`mechanistic/rut_mbe1.py\` (29 KB). That model is too heavy for the browser bundle and is also under calibration reconciliation against NEDU TR 18‑01 Appendix C (\`docs/methods.md\` §M7).
- **Use for**: shape inspection of tissue / hazard trajectories under different prebreathe + altitude profiles. Do **not** read the absolute hazard or bubble-number values as quantitative.`,
    metrics: [
      { key: "Tissue N₂ τ₁/₂", value: "360 min (Conkin default)" },
      { key: "Final P(DCS) source", value: "ADRAC closed-form" },
      { key: "Full ODE recursion", value: "Python only (rut_mbe1.py)" },
    ],
  },
  nasa_rm_nm: {
    name: "NASA Conkin logistic (RM with age / NM with sex)",
    sources: [
      "mechanistic/conkin_nasa.py",
      "NASA/TM-2004-213093 (Conkin, 2004)",
    ],
    notesMd: `- **Model family**: logistic regression of P(DCS) from the Exercise Tissue Ratio (ETR), with either age (RM, Eq. 15) or sex (NM, Eq. 14).
- **Equations are the published forms verbatim**: NM is σ(-25.56 + 12.83·ETR - 1.037·SEX), RM is σ(-31.71 + 14.55·ETR + 0.053·AGE).
- **Limitations**: published coefficients were fitted on n = 159 (NM) / n = 229 (RM) chamber exposures. The single-interval prebreathe calculator here does not model multi-interval PB protocols. CIs are not carried.`,
    metrics: [
      { key: "Dataset size (NM)", value: "n = 159" },
      { key: "Dataset size (RM)", value: "n = 229" },
      { key: "ETR formula", value: "P1N₂ / P₂" },
      { key: "Default τ₁/₂", value: "360 min" },
    ],
  },
};

export const citations: Citation[] = [
  {
    id: "pilmanis2004",
    authors: "Pilmanis AA, Petropoulos L, Kannan N, Webb JT",
    title:
      "Decompression sickness risk model: development and validation by 150 prospective hypobaric exposures",
    year: 2004,
    type: "article",
  },
  {
    id: "kannan1998",
    authors: "Kannan N, Raychaudhuri A, Pilmanis AA",
    title: "A loglogistic model for altitude decompression sickness",
    year: 1998,
    type: "article",
  },
  {
    id: "conkin2004",
    authors: "Conkin J",
    title:
      "Likelihood and Severity of Decompression Sickness with Exercise During EVA",
    year: 2004,
    type: "report",
    doi: "NASA/TM-2004-213093",
  },
  {
    id: "gerth2018",
    authors: "Gerth WA, Gault KA, Natoli MJ",
    title:
      "A Probabilistic Model of Altitude Decompression Sickness Based on the 3RUT‑MB Model of Gas Bubble Evolution in Perfused Tissue",
    year: 2018,
    type: "report",
    doi: "NEDU TR 18-01",
  },
  {
    id: "vann2011",
    authors: "Vann RD, Butler FK, Mitchell SJ, Moon RE",
    title: "Decompression illness",
    year: 2011,
    type: "article",
    doi: "10.1016/S0140-6736(10)61085-9",
  },
];

export const defaultMLInputs: MLSurrogateInputs = {
  altitude: 30000,
  timeAtAltitude: 120,
  prebreathingTime: 60,
  exerciseLevel: "Rest",
};

export const defaultMechanisticInputs: MechanisticInputs = {
  altitudeFt: 30000,
  timeAtAltitudeMin: 240,
  prebreathingTimeMin: 75,
  prebreathingExerciseLevel: "Rest",
  altitudeExerciseLevel: "Rest",
  prebreathFio2: 1.0,
  breatheO2AtAltitude: false,
  ascentDurationMin: 30,
  dtMin: 0.5,
};

export const defaultNASAInputs: NASAInputs = {
  variant: "NM",
  p0Psia: 8.0,
  paPsia: 0.0,
  pbTimeMin: 90,
  vo2MlKgMin: 25,
  lambda2: 0.03,
  p2Psia: 4.3,
  sex: "Male",
  ageYears: 35,
};
