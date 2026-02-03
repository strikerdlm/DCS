/**
 * Mock Data for DCS Safety Dashboard
 * 
 * Simulated datasets for demonstration purposes.
 * In production, this would be fetched from the Python backend.
 */

import type { ValidationDataPoint, ModelValidity, Citation } from "../types";

// ============================================================================
// Validation Dataset (simulated ADRAC-derived data)
// ============================================================================

function generateValidationData(
  numPoints: number = 500
): ValidationDataPoint[] {
  const data: ValidationDataPoint[] = [];
  const exerciseLevels = ["Rest", "Mild", "Heavy"];

  // Seed for reproducibility
  let seed = 42;
  const random = (): number => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff;
    return seed / 0x7fffffff;
  };

  for (let i = 0; i < numPoints; i++) {
    const altitude = 18000 + random() * 27000; // 18000-45000 ft
    const timeAtAltitude = 30 + random() * 270; // 30-300 min
    const prebreathingTime = random() * 120; // 0-120 min
    const exerciseLevel =
      exerciseLevels[Math.floor(random() * exerciseLevels.length)];

    // Generate realistic risk values
    const altFactor = (altitude / 63000) ** 1.5;
    const timeFactor = (timeAtAltitude / 300) ** 1.2;
    const prebFactor = Math.max(0, 1 - prebreathingTime / 120);
    const exFactor =
      exerciseLevel === "Rest" ? 1 : exerciseLevel === "Mild" ? 1.3 : 1.6;

    const baseRisk = (altFactor * 0.4 + timeFactor * 0.35 + prebFactor * 0.25) * exFactor;
    const riskOfDcs = Math.max(
      0,
      Math.min(100, baseRisk * 50 + (random() - 0.5) * 5)
    );

    // Simulated prediction with some error
    const predictedRisk = Math.max(
      0,
      Math.min(100, riskOfDcs + (random() - 0.5) * 8)
    );
    const residual = predictedRisk - riskOfDcs;
    const absError = Math.abs(residual);

    data.push({
      altitude: Math.round(altitude),
      timeAtAltitude: Math.round(timeAtAltitude * 10) / 10,
      prebreathingTime: Math.round(prebreathingTime * 10) / 10,
      exerciseLevel,
      riskOfDcs: Math.round(riskOfDcs * 100) / 100,
      predictedRisk: Math.round(predictedRisk * 100) / 100,
      residual: Math.round(residual * 100) / 100,
      absError: Math.round(absError * 100) / 100,
    });
  }

  return data;
}

export const validationData: ValidationDataPoint[] = generateValidationData(800);

// ============================================================================
// Model Validity Cards
// ============================================================================

export const modelValidityCards: Record<string, ModelValidity> = {
  ml_surrogate: {
    name: "ML Surrogate (ADRAC-derived dataset)",
    sources: [
      "Model_Rel_Candidate/README.md",
      "Model_Rel_Candidate/Metrics.txt",
    ],
    notesMd: `- **Model family**: supervised ML regression surrogate trained to reproduce ADRAC outputs (risk %).
- **Applicable metrics**: regression metrics (MAE/RMSE/R²).
- **Not applicable / not provided**: sensitivity/specificity/PPV/NPV/ROC unless a binary case definition and labeled outcomes are supplied.
- **Important**: the surrogate is only valid within the data envelope used to generate the training data (avoid extrapolation).`,
    metrics: [
      { key: "R²", value: "0.9847" },
      { key: "MAE (pp)", value: "0.832" },
      { key: "RMSE (pp)", value: "1.243" },
      { key: "Training samples", value: "12,480" },
      { key: "Cross-validation folds", value: "5-fold stratified" },
    ],
  },
  mechanistic_3rut: {
    name: "Mechanistic 3RUT‑MBe1 (time-dependent covariate survival model)",
    sources: ["BU_3RUT/3RUT_MBe1/3RUT_Theory.md", "rut_mbe1_model.py"],
    notesMd: `- **Model family**: mechanistic bubble-evolution + survival/hazard recursion (NEDU TR 18‑01 Appendix C/D).
- **Covariates supported**: pressure, inspired O₂ fraction, inspired inert gas fraction(s), and exercise intensity varying over time.
- **Validation**: chi-square goodness-of-fit discussions and comparisons vs other models (e.g., ADRAC/NASA models).
- **Not provided as a single table**: sensitivity/specificity/ROC/PPV/NPV; these require curated labeled datasets + decision thresholds.`,
    metrics: [
      {
        key: "Training data referenced",
        value: "2598 man-exposures (as described in theory doc)",
      },
      {
        key: "Fit assessment referenced",
        value: "Chi-square goodness-of-fit across groups",
      },
      { key: "Sensitivity/Specificity/ROC", value: "Not provided in repo" },
    ],
  },
  nasa_rm_nm: {
    name: "NASA logistic model (ETR-based; RM with age / NM with sex)",
    sources: [
      "NASA_model/conkin-dcs-exercise_2004.md",
      "NASA_model/DCS_NASA.py",
      "NASA_model/Evidence_2024.md",
    ],
    notesMd: `- **Model family**: logistic regression of **P(DCS)** from **ETR** (Exercise Tissue Ratio), with either **age** (RM) or **sex** (NM).
- **Implements published equations** from NASA/TM-2004-213093 (Eq. 14 and Eq. 15).
- **Limitations**: the full NASA models account for multi-interval PB protocols; this UI provides a simplified single-interval PB calculator.`,
    metrics: [
      { key: "Dataset size (RM)", value: "n = 229 exposures" },
      { key: "Dataset size (NM)", value: "n = 159 exposures" },
      { key: "Sensitivity/Specificity/ROC", value: "Not provided in repo" },
      { key: "CI95%", value: "Not provided (report notes CI limitations)" },
    ],
  },
};

// ============================================================================
// Scientific Citations
// ============================================================================

export const citations: Citation[] = [
  {
    id: "gerth2018",
    authors: "Gerth WA, Gault KA, Natoli MJ",
    title:
      "A Probabilistic Model of Altitude Decompression Sickness Based on the 3RUT‑MB Model of Gas Bubble Evolution in Perfused Tissue",
    journal: "Navy Experimental Diving Unit Technical Report",
    year: 2018,
    type: "report",
    doi: "NEDU TR 18-01",
  },
  {
    id: "conkin2004",
    authors: "Conkin J, Powell MR, Foster PP, Waligora JM",
    title:
      "Information About Venous Gas Emboli Improves Prediction of Hypobaric Decompression Sickness",
    journal: "Aviation, Space, and Environmental Medicine",
    year: 2004,
    type: "article",
    doi: "10.3357/ASEM.75.3.303",
  },
  {
    id: "nasa2004",
    authors: "Conkin J",
    title:
      "Likelihood and Severity of Decompression Sickness with Exercise During EVA",
    journal: "NASA Technical Memorandum",
    year: 2004,
    type: "report",
    doi: "NASA/TM-2004-213093",
  },
  {
    id: "buhlmann1984",
    authors: "Bühlmann AA",
    title: "Decompression – Decompression Sickness",
    journal: "Springer-Verlag",
    year: 1984,
    type: "book",
  },
  {
    id: "vann2004",
    authors: "Vann RD, Butler FK, Mitchell SJ, Moon RE",
    title: "Decompression illness",
    journal: "The Lancet",
    year: 2011,
    type: "article",
    doi: "10.1016/S0140-6736(10)61085-9",
  },
];

// ============================================================================
// Default Input Values
// ============================================================================

export const defaultMLInputs = {
  altitude: 25000,
  timeAtAltitude: 120,
  prebreathingTime: 60,
  exerciseLevel: "Rest" as const,
};

export const defaultMechanisticInputs = {
  altitudeFt: 30000,
  timeAtAltitudeMin: 240,
  prebreathingTimeMin: 75,
  prebreathingExerciseLevel: "Rest" as const,
  altitudeExerciseLevel: "Rest" as const,
  prebreathFio2: 1.0,
  breatheO2AtAltitude: false,
  ascentDurationMin: 30,
  dtMin: 0.1,
};

export const defaultNASAInputs = {
  variant: "NM" as const,
  p0Psia: 8.0,
  paPsia: 0.0,
  pbTimeMin: 90,
  vo2MlKgMin: 25,
  lambda2: 0.03,
  p2Psia: 4.3,
  sex: "Male" as const,
  ageYears: 35,
};
