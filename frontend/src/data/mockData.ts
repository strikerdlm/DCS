/**
 * Real ADRAC validation data + model validity cards.
 *
 * `validationData` loads the frozen held-out partition and train-only baseline
 * predictions from the reproducible ADRAC export.
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
import { formatNumber } from "../lib/utils";
import { VALIDITY_ENVELOPE } from "../utils/models";

interface AdracValidationPayload {
  metrics: {
    mae: number | null; rmse: number | null; r2: number | null;
    n_train: number; n_sample: number; n_total?: number; n_calibration?: number;
  };
  rows: ValidationDataPoint[];
}

const ADRAC_VAL = adracValidationRaw as AdracValidationPayload;

export const validationData: ValidationDataPoint[] = ADRAC_VAL.rows;
export const validationMetrics = {
  mae: ADRAC_VAL.metrics.mae,
  rmse: ADRAC_VAL.metrics.rmse,
  r2: ADRAC_VAL.metrics.r2,
  nTrain: ADRAC_VAL.metrics.n_train,
  nSample: ADRAC_VAL.rows.length,
  nTotal: ADRAC_VAL.metrics.n_total ?? null,
  nCalibration: ADRAC_VAL.metrics.n_calibration ?? null,
};

export const modelValidityCards: Record<string, ModelValidity> = {
  ml_surrogate: {
    name: "ADRAC closed-form (Pilmanis 2004 functional form)",
    sources: [
      "mechanistic/adrac.py",
      "legacy/Model_Rel_Candidate/DCS_Risk_DB_2025.csv (cleaned)",
    ],
    notesMd: `- **Model family**: log-logistic accelerated-failure-time survival model from Kannan & Pilmanis (1998), fitted using only ${ADRAC_VAL.metrics.n_train.toLocaleString()} frozen training rows.
- **Browser implementation**: the deterministic ADRAC baseline uses bundled coefficients. A trained LightGBM/ONNX surrogate is a separate artifact and is not executed by this panel.
- **Supported input range**: altitude ${VALIDITY_ENVELOPE.altitudeFt.map((value) => value.toLocaleString()).join(" – ")} ft, prebreathe ${VALIDITY_ENVELOPE.prebreatheMin.join(" – ")} min, time-at-altitude ${VALIDITY_ENVELOPE.timeAtAltitudeMin.join(" – ")} min, exercise ∈ {Rest, Mild, Heavy}.
- **Evaluation**: held-out ADRAC grid cells measure agreement with model-generated targets, not observed clinical outcomes. MAE and RMSE are percentage points. A prediction interval is unavailable for this baseline.`,
    metrics: [
      { key: "Held-out MAE (pp)", value: formatNumber(ADRAC_VAL.metrics.mae, 3) },
      { key: "Held-out RMSE (pp)", value: formatNumber(ADRAC_VAL.metrics.rmse, 3) },
      { key: "Held-out R²", value: formatNumber(ADRAC_VAL.metrics.r2, 4) },
      { key: "Training rows", value: ADRAC_VAL.metrics.n_train.toLocaleString() },
      { key: "Held-out rows", value: ADRAC_VAL.rows.length.toLocaleString() },
    ],
  },
  mechanistic_3rut: {
    name: "Mechanistic 3RUT‑MBe1 (reconciliation open)",
    sources: ["mechanistic/rut_mbe1.py", "docs/methods.md §M7"],
    notesMd: `- **Available**: the configured ambient-pressure profile, gas fractions, and exercise inputs can be inspected and exported offline.
- **Unavailable**: absolute DCS probability, bubble dynamics, survival, and hazard histories. No other model's endpoint is substituted for 3RUT.
- **Reason**: source-equation and benchmark reconciliation of \`mechanistic/rut_mbe1.py\` against NEDU TR 18‑01 remains incomplete.`,
    metrics: [
      { key: "Absolute risk", value: "Disabled" },
      { key: "Pressure profile", value: "Available offline" },
      { key: "Source reconciliation", value: "Open" },
    ],
  },
  nasa_rm_nm: {
    name: "NASA Conkin logistic (RM with age / NM with sex)",
    sources: [
      "mechanistic/conkin_nasa.py",
      "https://www.nasa.gov/wp-content/uploads/2023/03/conkin-dcs-exercise-tp-213158-2004.pdf",
    ],
    notesMd: `- **Model family**: NASA/TP-2004-213158 logistic regression using Exercise Tissue Ratio, with age (RM, Eq. 14) or sex (NM, Eq. 15).
- **Washout**: Eq. 6 uses k = exp(λ·VO₂)/519.37 min⁻¹, with λ = 0.025 (RM) or 0.030 (NM). Eq. 4 equilibrates toward dry ambient nitrogen partial pressure.
- **Endpoint**: 240 min at 4.3 psia with adynamic light exercise. Other pressures retain nitrogen tension and ETR calculations but have no supported probability endpoint.
- **Limitations**: fits used n = 159 (NM) / n = 229 (RM) chamber exposures. This view uses a single prebreathe interval; actual source protocols comprise multiple intervals. Prediction intervals are unavailable.`,
    metrics: [
      { key: "Dataset size (NM)", value: "n = 159" },
      { key: "Dataset size (RM)", value: "n = 229" },
      { key: "ETR formula", value: "P1N₂ / P₂" },
      { key: "Reference exposure", value: "240 min at 4.3 psia" },
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
    authors: "Conkin J, Gernhardt ML, Powell MR, Pollock N",
    title:
      "A Probability Model of Decompression Sickness at 4.3 psia After Exercise Prebreathe",
    year: 2004,
    type: "report",
    url: "https://www.nasa.gov/wp-content/uploads/2023/03/conkin-dcs-exercise-tp-213158-2004.pdf",
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
