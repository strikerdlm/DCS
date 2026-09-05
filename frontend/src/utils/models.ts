/**
 * DCS risk model implementations (TypeScript ports of the published
 * mechanistic/ Python references).
 *
 * Closed-form ADRAC log-logistic AFT — Pilmanis et al. (ASEM 2004; 75:749-59),
 *   functional form from Kannan & Pilmanis (ASEM 1998).
 * Coefficients fitted on the frozen training partition in Python and exported
 *   to data/adrac_coefficients.json; validation rows are kept separate.
 *
 * NASA RM/NM logistic — NASA/TP-2004-213158, Eq. 6, 14 (RM), 15 (NM).
 *
 * Mechanistic 3RUT-MBe1 — absolute risk and bubble history are unavailable
 *   while source-equation reconciliation remains open. Pressure profiles work
 *   independently of the disabled risk model.
 */

import {
  altitudeFtToMmHg,
  altitudeFtToPAmbAtm,
  clamp,
  stableSigmoid,
} from "../lib/utils";
import type {
  ExerciseLevel,
  MLSurrogateInputs,
  MLSurrogatePrediction,
  MechanisticInputs,
  MechanisticSimulationResult,
  NASAInputs,
  NASAPrediction,
  ProfileSegment,
  RegressionMetrics,
  ValidationDataPoint,
} from "../types";
import adracCoefficients from "../data/adrac_coefficients.json";

const LN2 = Math.log(2);
const SEA_LEVEL_MMHG = 760.0;
const P_H2O_MMHG = 47.0;
const N2_FRACTION_AIR = 0.79;

const ADRAC = adracCoefficients;

// ---------------------------------------------------------------------------
// Audited primary-grid support. The coefficient metadata currently exports no
// training bounds, so these explicit bounds come from the cleaned-grid audit;
// held-out rows must not be used to infer training support. This rectangular
// check is not the deployed surrogate's server-side Mahalanobis gate.
// ---------------------------------------------------------------------------

export const VALIDITY_ENVELOPE = {
  altitudeFt: [18000, 40000] as [number, number],
  prebreatheMin: [0, 60] as [number, number],
  timeAtAltitudeMin: [10, 240] as [number, number],
  exercise: ["Rest", "Mild", "Heavy"] as ExerciseLevel[],
};

export interface EnvelopeVerdict {
  inEnvelope: boolean;
  reasons: string[];
}

/** Returns whether a scenario sits inside the audited grid support, and why not. */
export function checkEnvelope(
  altitudeFt: number,
  prebreatheMin: number,
  timeAtAltitudeMin: number,
  exercise: ExerciseLevel,
): EnvelopeVerdict {
  const reasons: string[] = [];
  const [aLo, aHi] = VALIDITY_ENVELOPE.altitudeFt;
  const [pLo, pHi] = VALIDITY_ENVELOPE.prebreatheMin;
  const [tLo, tHi] = VALIDITY_ENVELOPE.timeAtAltitudeMin;
  if (!Number.isFinite(altitudeFt) || altitudeFt < aLo || altitudeFt > aHi)
    reasons.push(
      `Altitude ${altitudeFt.toLocaleString()} ft is outside ${aLo.toLocaleString()}–${aHi.toLocaleString()} ft`,
    );
  if (!Number.isFinite(prebreatheMin) || prebreatheMin < pLo || prebreatheMin > pHi)
    reasons.push(`Prebreathe ${prebreatheMin} min is outside ${pLo}–${pHi} min`);
  if (!Number.isFinite(timeAtAltitudeMin) || timeAtAltitudeMin < tLo || timeAtAltitudeMin > tHi)
    reasons.push(`Time-at-altitude ${timeAtAltitudeMin} min is outside ${tLo}–${tHi} min`);
  if (!VALIDITY_ENVELOPE.exercise.includes(exercise))
    reasons.push(`Exercise level "${exercise}" is not Rest/Mild/Heavy`);
  return { inEnvelope: reasons.length === 0, reasons };
}

/** No calibrated interval is available for the bundled ADRAC baseline. */
export function illustrativeInterval(
  _riskFraction: number,
  _altitudeFt: number,
): null {
  void _riskFraction;
  void _altitudeFt;
  return null;
}

function requireNonnegative(value: number, name: string): void {
  if (!Number.isFinite(value) || value < 0)
    throw new Error(`${name} must be finite and ≥ 0`);
}

/** Percent inputs produce percentage-point MAE/RMSE and squared-pp MSE. */
export function summarizeValidation(data: ValidationDataPoint[]): {
  metrics: RegressionMetrics;
  rows: Array<ValidationDataPoint & { predictedRisk: number; residual: number; absError: number }>;
  excludedCount: number;
} {
  const rows = data.flatMap((row) => {
    if (!Number.isFinite(row.riskOfDcs) || row.riskOfDcs < 0 || row.riskOfDcs > 100 ||
      typeof row.predictedRisk !== "number" || !Number.isFinite(row.predictedRisk) ||
      row.predictedRisk < 0 || row.predictedRisk > 100) return [];
    const residual = row.predictedRisk - row.riskOfDcs;
    return [{ ...row, predictedRisk: row.predictedRisk, residual, absError: Math.abs(residual) }];
  });
  const excludedCount = data.length - rows.length;
  if (rows.length === 0)
    return { rows, excludedCount, metrics: { r2: null, mae: null, rmse: null, mse: null } };
  const mean = rows.reduce((sum, row) => sum + row.riskOfDcs, 0) / rows.length;
  const ssRes = rows.reduce((sum, row) => sum + row.residual ** 2, 0);
  const ssTot = rows.reduce((sum, row) => sum + (row.riskOfDcs - mean) ** 2, 0);
  const mse = ssRes / rows.length;
  return {
    rows, excludedCount,
    metrics: {
      r2: rows.length >= 2 && ssTot > 0 ? 1 - ssRes / ssTot : null,
      mae: rows.reduce((sum, row) => sum + row.absError, 0) / rows.length,
      rmse: Math.sqrt(mse), mse,
    },
  };
}

// ---------------------------------------------------------------------------
// ADRAC closed-form log-logistic AFT
// ---------------------------------------------------------------------------

/**
 * P(DCS) = σ((ln t - β₂ - β·x) / β₁), with P(0) = 0.
 *
 * x = [ambient pressure (mmHg), prebreathing time (min),
 *      mildIndicator (0/1), heavyIndicator (0/1)].
 * Coefficients in adrac_coefficients.json are fitted on the training partition.
 */
export function predictADRAC(
  altitudeFt: number,
  prebreatheMin: number,
  exerciseLevel: ExerciseLevel,
  timeAtAltitudeMin: number,
): { riskFraction: number; logT: number; covariateTerm: number; pressureMmHg: number } {
  requireNonnegative(prebreatheMin, "Prebreathe duration");
  requireNonnegative(timeAtAltitudeMin, "Exposure duration");
  if (!VALIDITY_ENVELOPE.exercise.includes(exerciseLevel))
    throw new Error("Exercise level must be Rest, Mild, or Heavy");
  const pressureMmHg = altitudeFtToMmHg(altitudeFt);
  const mild = exerciseLevel === "Mild" ? 1 : 0;
  const heavy = exerciseLevel === "Heavy" ? 1 : 0;
  const x = [pressureMmHg, prebreatheMin, mild, heavy];

  const covariateTerm =
    ADRAC.beta[0] * x[0] +
    ADRAC.beta[1] * x[1] +
    ADRAC.beta[2] * x[2] +
    ADRAC.beta[3] * x[3];

  const logT = Math.log(timeAtAltitudeMin);
  const omega = (logT - ADRAC.beta_2 - covariateTerm) / ADRAC.beta_1;
  const riskFraction = clamp(stableSigmoid(omega), 0, 1);
  return { riskFraction, logT, covariateTerm, pressureMmHg };
}

/**
 * Conkin single-compartment tissue-N₂ supersaturation ratio at exit.
 * Mirrors tinydcs.features._tissue_n2_ratio_360 (no exercise).
 */
function tissueN2Ratio360(
  altitudeFt: number,
  prebreatheTimeMin: number,
  prebreatheFio2: number,
  altitudeTimeMin: number,
  altitudeFio2: number,
  halfTimeMin: number = 360.0,
): number {
  const pAmbAltMmHg = Math.max(altitudeFtToMmHg(altitudeFt), 1e-6);
  const pAmbGround = SEA_LEVEL_MMHG;

  const fn2Pre = 1.0 - prebreatheFio2;
  const fn2Alt = 1.0 - altitudeFio2;

  const pInspN2GroundAir = Math.max(pAmbGround - P_H2O_MMHG, 0) * N2_FRACTION_AIR;
  const pInspN2Pre = Math.max(pAmbGround - P_H2O_MMHG, 0) * fn2Pre;
  const pInspN2Alt = Math.max(pAmbAltMmHg - P_H2O_MMHG, 0) * fn2Alt;

  const tau = halfTimeMin / LN2;
  const pAfterPre = pInspN2Pre - (pInspN2Pre - pInspN2GroundAir) * Math.exp(-prebreatheTimeMin / tau);
  const pEnd = pInspN2Alt - (pInspN2Alt - pAfterPre) * Math.exp(-altitudeTimeMin / tau);
  return pEnd / pAmbAltMmHg;
}

// ---------------------------------------------------------------------------
// "ML Surrogate" tab — uses real ADRAC closed-form (the LightGBM ONNX is
// shipped in the Python pipeline, not yet in the browser bundle).
// ---------------------------------------------------------------------------

export function predictMLSurrogate(inputs: MLSurrogateInputs): MLSurrogatePrediction {
  const { altitude, timeAtAltitude, prebreathingTime, exerciseLevel } = inputs;
  const { riskFraction, pressureMmHg, covariateTerm, logT } = predictADRAC(
    altitude,
    prebreathingTime,
    exerciseLevel,
    timeAtAltitude,
  );

  const tr360 = tissueN2Ratio360(
    altitude,
    prebreathingTime,
    1.0,
    timeAtAltitude,
    0.21,
  );

  const pAmbAtm = altitudeFtToPAmbAtm(altitude);
  const exerciseRest = exerciseLevel === "Rest" ? 1 : 0;
  const exerciseMild = exerciseLevel === "Mild" ? 1 : 0;
  const exerciseHeavy = exerciseLevel === "Heavy" ? 1 : 0;
  const supersaturation = Math.max(0, (1 - pAmbAtm) * N2_FRACTION_AIR);
  const exerciseDose =
    timeAtAltitude * (exerciseRest * 0 + exerciseMild * 0.41 + exerciseHeavy * 0.55);

  return {
    riskPercent: riskFraction * 100,
    features: [
      { name: "altitude_ft", value: altitude },
      { name: "pressure_mmhg", value: pressureMmHg },
      { name: "pressure_atm", value: pAmbAtm },
      { name: "time_at_altitude_min", value: timeAtAltitude },
      { name: "log_time", value: logT },
      { name: "prebreathe_min", value: prebreathingTime },
      { name: "exercise_rest", value: exerciseRest },
      { name: "exercise_mild", value: exerciseMild },
      { name: "exercise_heavy", value: exerciseHeavy },
      { name: "tissue_n2_ratio_360", value: tr360 },
      { name: "dry_ambient_n2_pressure_drop_atm", value: supersaturation },
      { name: "category_exercise_proxy_l", value: exerciseDose },
      { name: "covariate_term", value: covariateTerm },
    ],
    modelMetadata: {
      modelPath: "mechanistic/adrac.py (closed-form log-logistic AFT)",
      applyV11Transforms: false,
    },
  };
}

// ---------------------------------------------------------------------------
// NASA Conkin RM/NM logistic
// ---------------------------------------------------------------------------

export const NASA_VARIANT_LAMBDA = { RM: 0.025, NM: 0.030 } as const;

function nasaKFromVo2(vo2MlKgMin: number, lambda2: number): number {
  if (!Number.isFinite(vo2MlKgMin) || vo2MlKgMin < 0)
    throw new Error("vo2MlKgMin must be finite and ≥ 0");
  if (!Number.isFinite(lambda2) || lambda2 <= 0)
    throw new Error("lambda2 must be finite and > 0");
  if (lambda2 * vo2MlKgMin > 700) throw new Error("lambda × VO2 exceeds the numerical range");
  return Math.exp(lambda2 * vo2MlKgMin) / 519.37;
}

function nasaP1n2AfterPb(
  p0Psia: number,
  paPsia: number,
  vo2MlKgMin: number,
  pbTimeMin: number,
  lambda2: number,
): number {
  requireNonnegative(p0Psia, "Initial nitrogen pressure");
  requireNonnegative(paPsia, "Ambient nitrogen pressure");
  requireNonnegative(pbTimeMin, "Prebreathe duration");
  const k = nasaKFromVo2(vo2MlKgMin, lambda2);
  return paPsia + (p0Psia - paPsia) * Math.exp(-k * pbTimeMin);
}

function nasaEtr(p1n2Psia: number, p2Psia: number): number {
  if (!Number.isFinite(p1n2Psia) || !Number.isFinite(p2Psia))
    throw new Error("Pressures must be finite");
  if (p2Psia <= 0) throw new Error("p2Psia must be > 0");
  return p1n2Psia / p2Psia;
}

function nasaPDcsNm(etr: number, sex: "Male" | "Female"): number {
  requireNonnegative(etr, "ETR");
  if (sex !== "Male" && sex !== "Female") throw new Error("Sex must be Male or Female");
  const sexCode = sex === "Male" ? 1.0 : 0.0;
  return stableSigmoid(-25.56 + 12.83 * etr - 1.037 * sexCode);
}

function nasaPDcsRm(etr: number, ageYears: number): number {
  requireNonnegative(etr, "ETR");
  if (!Number.isFinite(ageYears) || ageYears <= 0)
    throw new Error("age must be finite and > 0");
  return stableSigmoid(-31.71 + 14.55 * etr + 0.053 * ageYears);
}

export function predictNASA(inputs: NASAInputs): NASAPrediction {
  if (inputs.variant !== "RM" && inputs.variant !== "NM") throw new Error("Variant must be RM or NM");
  const lambda2 = NASA_VARIANT_LAMBDA[inputs.variant];
  const p1n2 = nasaP1n2AfterPb(
    inputs.p0Psia,
    inputs.paPsia,
    inputs.vo2MlKgMin,
    inputs.pbTimeMin,
    lambda2,
  );
  const etr = nasaEtr(p1n2, inputs.p2Psia);

  let pDcs: number;
  let equation: string;
  if (inputs.variant === "NM") {
    pDcs = nasaPDcsNm(etr, inputs.sex);
    equation = `P(DCS) = σ(-25.56 + 12.83·ETR - 1.037·SEX)\nSEX = ${inputs.sex === "Male" ? 1 : 0} (${inputs.sex})`;
  } else {
    pDcs = nasaPDcsRm(etr, inputs.ageYears);
    equation = `P(DCS) = σ(-31.71 + 14.55·ETR + 0.053·AGE)\nAGE = ${inputs.ageYears}`;
  }

  const unavailableReason = Math.abs(inputs.p2Psia - 4.3) > 1e-9
    ? "The published endpoint applies to 240 min at 4.3 psia with adynamic light exercise. Other exposure pressures have no supported probability endpoint."
    : null;
  return {
    p1n2Psia: p1n2,
    etr,
    pDcsPercent: unavailableReason === null ? pDcs * 100 : null,
    equation,
    lambda2,
    predictionHorizonMin: 240,
    referencePressurePsia: 4.3,
    unavailableReason,
  };
}

// ---------------------------------------------------------------------------
// Mechanistic 3RUT-MBe1 availability and configured exposure profile.
// ---------------------------------------------------------------------------

function exerciseLevelToIEx(level: ExerciseLevel): number {
  return level === "Rest" ? 0.0 : level === "Mild" ? 0.41 : 0.55;
}

export function buildMechanisticProfile(inputs: MechanisticInputs): ProfileSegment[] {
  const {
    altitudeFt,
    timeAtAltitudeMin,
    prebreathingTimeMin,
    prebreathingExerciseLevel,
    altitudeExerciseLevel,
    prebreathFio2,
    breatheO2AtAltitude,
    ascentDurationMin,
    dtMin,
  } = inputs;

  requireNonnegative(timeAtAltitudeMin, "Exposure duration");
  requireNonnegative(prebreathingTimeMin, "Prebreathe duration");
  requireNonnegative(ascentDurationMin, "Ascent duration");
  if (!Number.isFinite(dtMin) || dtMin <= 0) throw new Error("Time step must be finite and > 0");
  if (!Number.isFinite(prebreathFio2) || prebreathFio2 < 0 || prebreathFio2 > 1)
    throw new Error("Prebreathe oxygen fraction must lie between 0 and 1");

  const pFinal = altitudeFtToPAmbAtm(altitudeFt);
  const fio2Alt = breatheO2AtAltitude ? 1.0 : 0.21;
  const fin2Alt = breatheO2AtAltitude ? 0.0 : 0.79;
  const iExPre = exerciseLevelToIEx(prebreathingExerciseLevel);
  const iExAlt = exerciseLevelToIEx(altitudeExerciseLevel);

  const segments: ProfileSegment[] = [];
  if (prebreathingTimeMin > 0) {
    segments.push({
      durationMin: prebreathingTimeMin,
      pAmbAtm: 1.0,
      fio2: prebreathFio2,
      fin2: Math.max(0, 1 - prebreathFio2),
      iExLMinWb: iExPre,
    });
  }
  if (ascentDurationMin > 0) {
    const nSteps = Math.max(1, Math.ceil(ascentDurationMin / dtMin));
    const stepDt = ascentDurationMin / nSteps;
    for (let i = 0; i < nSteps; i++) {
      const frac = (i + 1) / nSteps;
      const pStep = 1.0 + (pFinal - 1.0) * frac;
      segments.push({
        durationMin: stepDt,
        pAmbAtm: pStep,
        fio2: fio2Alt,
        fin2: fin2Alt,
        iExLMinWb: 0,
      });
    }
  }
  if (timeAtAltitudeMin > 0) {
    segments.push({
      durationMin: timeAtAltitudeMin,
      pAmbAtm: pFinal,
      fio2: fio2Alt,
      fin2: fin2Alt,
      iExLMinWb: iExAlt,
    });
  }
  return segments;
}

export const RUT_UNAVAILABLE_REASON =
  "3RUT-MBe1 source-equation and benchmark reconciliation is incomplete. Absolute DCS risk, bubble trajectories, and hazard histories are unavailable.";

/** Returns the supported exposure profile and the explicit 3RUT availability gate. */
export function runMechanisticSimulation(
  inputs: MechanisticInputs,
): MechanisticSimulationResult {
  return {
    history: [],
    finalPDcsPercent: null,
    segments: buildMechanisticProfile(inputs),
    absoluteRiskEnabled: false,
    reason: RUT_UNAVAILABLE_REASON,
  };
}

// ---------------------------------------------------------------------------
// Risk landscape (altitude × time-at-altitude → P(DCS) %)
// ---------------------------------------------------------------------------

export interface RiskLandscapePoint {
  altitudeFt: number;
  timeAtAltitudeMin: number;
  riskPercent: number;
}

export function generateRiskLandscape({
  prebreatheMin,
  exerciseLevel,
  altitudeRange = VALIDITY_ENVELOPE.altitudeFt,
  timeRange = VALIDITY_ENVELOPE.timeAtAltitudeMin,
  altitudeSteps = 24,
  timeSteps = 24,
}: {
  prebreatheMin: number;
  exerciseLevel: ExerciseLevel;
  altitudeRange?: [number, number];
  timeRange?: [number, number];
  altitudeSteps?: number;
  timeSteps?: number;
}): RiskLandscapePoint[] {
  const out: RiskLandscapePoint[] = [];
  const dAlt = (altitudeRange[1] - altitudeRange[0]) / (altitudeSteps - 1);
  const dT = (timeRange[1] - timeRange[0]) / (timeSteps - 1);
  for (let i = 0; i < altitudeSteps; i++) {
    const alt = altitudeRange[0] + i * dAlt;
    for (let j = 0; j < timeSteps; j++) {
      const t = timeRange[0] + j * dT;
      if (!checkEnvelope(alt, prebreatheMin, t, exerciseLevel).inEnvelope) continue;
      const { riskFraction } = predictADRAC(alt, prebreatheMin, exerciseLevel, t);
      out.push({ altitudeFt: alt, timeAtAltitudeMin: t, riskPercent: riskFraction * 100 });
    }
  }
  return out;
}

// ---------------------------------------------------------------------------
// Dose–response sweep (one input varied across its validity range, others held)
// ---------------------------------------------------------------------------

export type DoseVariable = "time" | "altitude" | "prebreathe";

export interface DoseResponsePoint {
  x: number;
  riskPercent: number;
}

/** Validity-envelope sweep range for each dose-response variable. */
export const DOSE_RANGE: Record<DoseVariable, [number, number]> = {
  time: [VALIDITY_ENVELOPE.timeAtAltitudeMin[0], VALIDITY_ENVELOPE.timeAtAltitudeMin[1]],
  altitude: [VALIDITY_ENVELOPE.altitudeFt[0], VALIDITY_ENVELOPE.altitudeFt[1]],
  prebreathe: [VALIDITY_ENVELOPE.prebreatheMin[0], VALIDITY_ENVELOPE.prebreatheMin[1]],
};

/**
 * Sweeps a single exposure variable across its validity range while holding the
 * others at the supplied scenario, returning the ADRAC P(DCS) response curve for
 * one exercise level. Pure closed-form, so a 60-point curve is essentially free.
 */
export function generateDoseResponse({
  base,
  variable,
  exerciseLevel,
  steps = 61,
}: {
  base: MLSurrogateInputs;
  variable: DoseVariable;
  exerciseLevel: ExerciseLevel;
  steps?: number;
}): DoseResponsePoint[] {
  const [lo, hi] = DOSE_RANGE[variable];
  const out: DoseResponsePoint[] = [];
  for (let i = 0; i < steps; i++) {
    const x = lo + ((hi - lo) * i) / (steps - 1);
    const alt = variable === "altitude" ? x : base.altitude;
    const t = variable === "time" ? x : base.timeAtAltitude;
    const pb = variable === "prebreathe" ? x : base.prebreathingTime;
    if (!checkEnvelope(alt, pb, t, exerciseLevel).inEnvelope) continue;
    const { riskFraction } = predictADRAC(alt, pb, exerciseLevel, t);
    out.push({ x, riskPercent: riskFraction * 100 });
  }
  return out;
}

// ---------------------------------------------------------------------------
// Covariate contribution decomposition (log-odds scale)
// ---------------------------------------------------------------------------

export interface Contribution {
  /** Human label for the term. */
  label: string;
  /** Signed contribution to the log-odds (logit) ω. Positive raises risk. */
  value: number;
}

export interface ADRACDecomposition {
  /** Additive terms of ω, sorted by descending |value| (tornado order). */
  contributions: Contribution[];
  /** ω = Σ contributions (the AFT linear predictor on the logit scale). */
  omega: number;
  /** P(DCS) = σ(ω), as a percentage. */
  riskPercent: number;
}

/**
 * Exact additive decomposition of the ADRAC prediction on the LOG-ODDS scale.
 *
 *   ω = (ln t − β₂ − β·x) / β₁
 *     = (ln t)/β₁  −  β₂/β₁  −  β₀·P/β₁  −  β₁ₚ·prebreathe/β₁  −  βₑₓ·1/β₁
 *
 * Each bracketed term is one bar. Contributions are additive on the logit
 * scale only — the sum ω maps to probability through the logistic σ(·), so the
 * bars do NOT add up in percentage space. This is the linear-model analogue of
 * a SHAP decomposition; the UI labels the axis as log-odds and shows σ(ω).
 */
export function decomposeADRAC(inputs: MLSurrogateInputs): ADRACDecomposition {
  const { altitude, timeAtAltitude, prebreathingTime, exerciseLevel } = inputs;
  const { pressureMmHg, logT } = predictADRAC(altitude, prebreathingTime, exerciseLevel, timeAtAltitude);
  const mild = exerciseLevel === "Mild" ? 1 : 0;
  const heavy = exerciseLevel === "Heavy" ? 1 : 0;
  const invB1 = 1 / ADRAC.beta_1;

  const cTime = logT * invB1;
  const cBaseline = -ADRAC.beta_2 * invB1;
  const cPressure = -ADRAC.beta[0] * pressureMmHg * invB1;
  const cPrebreathe = -ADRAC.beta[1] * prebreathingTime * invB1;
  const cExercise = -(ADRAC.beta[2] * mild + ADRAC.beta[3] * heavy) * invB1;

  const contributions: Contribution[] = [
    { label: "Time at altitude", value: cTime },
    { label: "Baseline (intercept)", value: cBaseline },
    { label: "Ambient pressure", value: cPressure },
    { label: "Prebreathe", value: cPrebreathe },
    { label: `Exercise (${exerciseLevel})`, value: cExercise },
  ];

  const omega = cTime + cBaseline + cPressure + cPrebreathe + cExercise;
  const riskPercent = stableSigmoid(omega) * 100;
  contributions.sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
  return { contributions, omega, riskPercent };
}

// ---------------------------------------------------------------------------
// Tissue N₂ uptake / washout trajectory (single-compartment Conkin, τ½ = 360)
// ---------------------------------------------------------------------------

export interface TissueN2Point {
  tMin: number;
  /** Tissue N₂ tension (mmHg). */
  tensionMmHg: number;
  /** Ambient pressure at this instant (mmHg) — ground during prebreathe. */
  ambientMmHg: number;
  /** Supersaturation ratio = tissue tension / ambient pressure. */
  ratio: number;
  phase: "prebreathe" | "altitude";
}

/**
 * Time-resolved tissue N₂ trajectory behind the `tissue_n2_ratio_360` feature.
 *
 * Single 360-min compartment (Conkin): the tissue denitrogenates during 100 % O₂
 * prebreathe at ground, then on-gasses/holds at altitude. Ascent is treated as
 * instantaneous (matching the feature definition), so the supersaturation ratio
 * steps up the moment ambient pressure drops. The final point equals the scalar
 * `tissueN2Ratio360` used in the feature vector.
 */
export function tissueN2Trajectory(
  inputs: MLSurrogateInputs,
  {
    prebreatheFio2 = 1.0,
    altitudeFio2 = 0.21,
    halfTimeMin = 360.0,
    steps = 140,
  }: {
    prebreatheFio2?: number;
    altitudeFio2?: number;
    halfTimeMin?: number;
    steps?: number;
  } = {},
): TissueN2Point[] {
  const { altitude, timeAtAltitude, prebreathingTime } = inputs;
  const pAmbGround = SEA_LEVEL_MMHG;
  const pAmbAlt = Math.max(altitudeFtToMmHg(altitude), 1e-6);
  const tau = halfTimeMin / LN2;

  const fn2Pre = 1.0 - prebreatheFio2;
  const fn2Alt = 1.0 - altitudeFio2;
  const startTension = Math.max(pAmbGround - P_H2O_MMHG, 0) * N2_FRACTION_AIR;
  const pInspN2Pre = Math.max(pAmbGround - P_H2O_MMHG, 0) * fn2Pre;
  const pInspN2Alt = Math.max(pAmbAlt - P_H2O_MMHG, 0) * fn2Alt;
  // Tissue tension at the end of the prebreathe phase (start of altitude phase).
  const pAfterPre =
    pInspN2Pre - (pInspN2Pre - startTension) * Math.exp(-Math.max(prebreathingTime, 0) / tau);

  const total = Math.max(prebreathingTime + timeAtAltitude, 1e-6);
  const out: TissueN2Point[] = [];
  for (let i = 0; i < steps; i++) {
    const t = (total * i) / (steps - 1);
    if (prebreathingTime > 0 && t <= prebreathingTime) {
      const tension = pInspN2Pre - (pInspN2Pre - startTension) * Math.exp(-t / tau);
      out.push({
        tMin: t,
        tensionMmHg: tension,
        ambientMmHg: pAmbGround,
        ratio: tension / pAmbGround,
        phase: "prebreathe",
      });
    } else {
      const ta = t - prebreathingTime;
      const tension = pInspN2Alt - (pInspN2Alt - pAfterPre) * Math.exp(-ta / tau);
      out.push({
        tMin: t,
        tensionMmHg: tension,
        ambientMmHg: pAmbAlt,
        ratio: tension / pAmbAlt,
        phase: "altitude",
      });
    }
  }
  return out;
}

// ---------------------------------------------------------------------------
// Altitude × prebreathe risk grid (mission-planning trade-space for isobars)
// ---------------------------------------------------------------------------

export interface RiskGridPoint {
  altitudeFt: number;
  prebreatheMin: number;
  riskPercent: number;
}

/**
 * P(DCS) over the two mission-planning levers — altitude and prebreathe — with
 * time-at-altitude and exercise held at the current scenario. The 1 / 5 / 20 %
 * contours of this field are the "isobars of equal risk" rendered by RiskIsobars;
 * together with the supported input range they describe the model response.
 *
 * Pure closed-form ADRAC, so a 24 × 24 grid (576 evaluations) is essentially free.
 */
export function generateAltitudePrebreatheGrid({
  timeAtAltitudeMin,
  exerciseLevel,
  altitudeRange = VALIDITY_ENVELOPE.altitudeFt,
  prebreatheRange = VALIDITY_ENVELOPE.prebreatheMin,
  altitudeSteps = 24,
  prebreatheSteps = 24,
}: {
  timeAtAltitudeMin: number;
  exerciseLevel: ExerciseLevel;
  altitudeRange?: [number, number];
  prebreatheRange?: [number, number];
  altitudeSteps?: number;
  prebreatheSteps?: number;
}): RiskGridPoint[] {
  const out: RiskGridPoint[] = [];
  const dAlt = (altitudeRange[1] - altitudeRange[0]) / (altitudeSteps - 1);
  const dPb = (prebreatheRange[1] - prebreatheRange[0]) / (prebreatheSteps - 1);
  for (let i = 0; i < altitudeSteps; i++) {
    const alt = altitudeRange[0] + i * dAlt;
    for (let j = 0; j < prebreatheSteps; j++) {
      const pb = prebreatheRange[0] + j * dPb;
      if (!checkEnvelope(alt, pb, timeAtAltitudeMin, exerciseLevel).inEnvelope) continue;
      const { riskFraction } = predictADRAC(alt, pb, exerciseLevel, timeAtAltitudeMin);
      out.push({ altitudeFt: alt, prebreatheMin: pb, riskPercent: riskFraction * 100 });
    }
  }
  return out;
}

// ---------------------------------------------------------------------------
// Mission pressure profile (ambient pressure vs tissue N₂ over the exposure)
// ---------------------------------------------------------------------------

export interface MissionProfilePoint {
  tMin: number;
  /** Ambient total pressure (mmHg). */
  pAmbMmHg: number;
  /** Tissue N₂ tension (mmHg), single 360-min compartment. */
  tissueN2MmHg: number;
  /** Nitrogen excess = max(0, tissue N₂ − ambient total pressure).
   *  This one-gas diagnostic is not a full gas-tension sum or a hazard rate. */
  gapMmHg: number;
  phase: "prebreathe" | "ascent" | "altitude";
}

/**
 * Ambient-pressure "valley" with tissue-N₂ tension overlaid across the mission.
 *
 * Three segments, integrated with a single 360-min N₂ compartment (Conkin):
 *   1. Prebreathe — 100 % O₂ at ground (760 mmHg); tissue denitrogenates toward
 *      an inspired N₂ of ~0 but can only fall so far in the prebreathe window.
 *   2. Ascent — ambient pressure ramps from ground to the target altitude over
 *      `ascentDurationMin`; the crew stays on O₂ so the tissue keeps washing out
 *      while the ambient line drops away beneath it.
 *   3. Altitude — ambient holds at the (low) altitude pressure on air; the
 *      tissue on-gasses back toward the altitude inspired N₂. The gap between
 *      the tissue line and the ambient line is the supersaturation that drives
 *   DCS.
 *
 * A finite ascent changes total washout time relative to tissueN2Trajectory,
 * whose ascent is instantaneous. Its endpoint is therefore a distinct profile.
 */
export function missionPressureProfile(
  inputs: MLSurrogateInputs,
  {
    prebreatheFio2 = 1.0,
    altitudeFio2 = 0.21,
    halfTimeMin = 360.0,
    ascentDurationMin = 6,
    dtMin = 2,
  }: {
    prebreatheFio2?: number;
    altitudeFio2?: number;
    halfTimeMin?: number;
    ascentDurationMin?: number;
    dtMin?: number;
  } = {},
): MissionProfilePoint[] {
  const { altitude, timeAtAltitude, prebreathingTime } = inputs;
  requireNonnegative(prebreathingTime, "Prebreathe duration");
  requireNonnegative(timeAtAltitude, "Exposure duration");
  requireNonnegative(ascentDurationMin, "Ascent duration");
  if (!Number.isFinite(dtMin) || dtMin <= 0) throw new Error("Time step must be finite and > 0");
  const pAmbGround = SEA_LEVEL_MMHG;
  const pAmbAlt = Math.max(altitudeFtToMmHg(altitude), 1e-6);
  const tau = halfTimeMin / LN2;

  // Inspired N₂ (mmHg) for a given ambient + inspired O₂ fraction.
  const pInspN2 = (pAmbMmHg: number, fio2: number) =>
    Math.max(pAmbMmHg - P_H2O_MMHG, 0) * (1 - fio2);

  const startTension = pInspN2(pAmbGround, 1 - N2_FRACTION_AIR); // ground air

  // Segment definitions: [duration, pAmb start, pAmb end, fio2].
  const segs: Array<{
    dur: number;
    p0: number;
    p1: number;
    fio2: number;
    phase: MissionProfilePoint["phase"];
  }> = [];
  if (prebreathingTime > 0)
    segs.push({ dur: prebreathingTime, p0: pAmbGround, p1: pAmbGround, fio2: prebreatheFio2, phase: "prebreathe" });
  if (ascentDurationMin > 0)
    segs.push({ dur: ascentDurationMin, p0: pAmbGround, p1: pAmbAlt, fio2: prebreatheFio2, phase: "ascent" });
  if (timeAtAltitude > 0)
    segs.push({ dur: timeAtAltitude, p0: pAmbAlt, p1: pAmbAlt, fio2: altitudeFio2, phase: "altitude" });

  const out: MissionProfilePoint[] = [{
    tMin: 0, pAmbMmHg: pAmbGround, tissueN2MmHg: startTension,
    gapMmHg: Math.max(0, startTension - pAmbGround),
    phase: segs[0]?.phase ?? "altitude",
  }];
  let t = 0;
  let tension = startTension;
  for (const seg of segs) {
    const nSteps = Math.max(1, Math.ceil(seg.dur / dtMin));
    const stepDt = seg.dur / nSteps;
    for (let i = 0; i < nSteps; i++) {
      const frac = (i + 1) / nSteps;
      const pAmb = seg.p0 + (seg.p1 - seg.p0) * frac;
      const midPressure = seg.p0 + (seg.p1 - seg.p0) * (i + 0.5) / nSteps;
      const pInsp = pInspN2(midPressure, seg.fio2);
      // Single-compartment exponential update over this step.
      tension = pInsp - (pInsp - tension) * Math.exp(-stepDt / tau);
      const gap = Math.max(0, tension - pAmb);
      t += stepDt;
      out.push({
        tMin: +t.toFixed(3),
        pAmbMmHg: +pAmb.toFixed(3),
        tissueN2MmHg: +tension.toFixed(3),
        gapMmHg: +gap.toFixed(3),
        phase: seg.phase,
      });
    }
  }
  return out;
}
