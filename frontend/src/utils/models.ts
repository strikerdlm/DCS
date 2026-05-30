/**
 * DCS risk model implementations (TypeScript ports of the published
 * mechanistic/ Python references).
 *
 * Closed-form ADRAC log-logistic AFT — Pilmanis et al. (ASEM 2004; 75:749-59),
 *   functional form from Kannan & Pilmanis (ASEM 1998).
 * Coefficients fitted in Python (mechanistic.adrac.fit_adrac) on the cleaned
 *   ADRAC grid (15,908 rows) and exported to data/adrac_coefficients.json.
 *
 * NASA RM/NM logistic — Conkin (NASA/TM-2004-213093), Eq. 14 / Eq. 15,
 *   ported verbatim from mechanistic/conkin_nasa.py.
 *
 * Mechanistic 3RUT-MBe1 — schematic preview only. The full bubble-evolution
 *   recursion lives in mechanistic/rut_mbe1.py (29 KB) and is too heavy for
 *   client-side execution. The TS routine here emits ADRAC + Conkin time-
 *   sampled trajectories, badged as "schematic" in the UI.
 *
 * Research use only. Not validated for clinical or operational decisions.
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
  ModelState,
  NASAInputs,
  NASAPrediction,
  ProfileSegment,
} from "../types";
import adracCoefficients from "../data/adrac_coefficients.json";

const LN2 = Math.log(2);
const DEFAULT_T_HALF_MIN = 360.0;
const SEA_LEVEL_MMHG = 760.0;
const P_H2O_MMHG = 47.0;
const N2_FRACTION_AIR = 0.79;

const ADRAC = adracCoefficients as {
  beta_1: number;
  beta_2: number;
  beta: [number, number, number, number];
  feature_names: ["pressure_mmhg", "prebreathe_min", "exercise_mild", "exercise_heavy"];
};

// ---------------------------------------------------------------------------
// Validity envelope + out-of-distribution gate (mirrors the OOD layer of the
// trained TinyDCS stack — the browser bundle reproduces the *envelope check*
// only; the Mahalanobis gate itself runs server-side).
// ---------------------------------------------------------------------------

export const VALIDITY_ENVELOPE = {
  altitudeFt: [18000, 40000] as [number, number],
  prebreatheMin: [0, 180] as [number, number],
  timeAtAltitudeMin: [10, 240] as [number, number],
  exercise: ["Rest", "Mild", "Heavy"] as ExerciseLevel[],
};

export interface EnvelopeVerdict {
  inEnvelope: boolean;
  reasons: string[];
}

/** Returns whether a scenario sits inside the validated envelope, and why not. */
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
  if (altitudeFt < aLo || altitudeFt > aHi)
    reasons.push(
      `Altitude ${altitudeFt.toLocaleString()} ft is outside ${aLo.toLocaleString()}–${aHi.toLocaleString()} ft`,
    );
  if (prebreatheMin < pLo || prebreatheMin > pHi)
    reasons.push(`Prebreathe ${prebreatheMin} min is outside ${pLo}–${pHi} min`);
  if (timeAtAltitudeMin < tLo || timeAtAltitudeMin > tHi)
    reasons.push(`Time-at-altitude ${timeAtAltitudeMin} min is outside ${tLo}–${tHi} min`);
  if (!VALIDITY_ENVELOPE.exercise.includes(exercise))
    reasons.push(`Exercise level "${exercise}" is not Rest/Mild/Heavy`);
  return { inEnvelope: reasons.length === 0, reasons };
}

/**
 * ILLUSTRATIVE calibrated 95 % prediction interval.
 *
 * The real TinyDCS interval is produced by a zero-inflated two-stage
 * split-conformal calibrator fitted on a held-out set (≥0.95 band coverage,
 * 0.960 overall). That calibrator is NOT shipped in the browser bundle. To
 * demonstrate the *shape* of the contribution, this routine forms a symmetric
 * band on the logit scale around the ADRAC point estimate — band width grows
 * in the low-altitude / near-zero region where the published method showed its
 * coverage gain. It is a teaching device, clearly labelled "illustrative"
 * everywhere it is rendered, and is NOT the conformal interval from the paper.
 */
export function illustrativeInterval(
  riskFraction: number,
  altitudeFt: number,
): { lowPercent: number; highPercent: number; widthPercent: number } {
  const p = clamp(riskFraction, 1e-6, 1 - 1e-6);
  const logit = Math.log(p / (1 - p));
  // Base logit half-width ~ moderate; widened toward the low-altitude band
  // (18–23 kft) where the zero-inflated stage matters most.
  const lowBandFactor =
    altitudeFt <= 23000 ? 1.0 + (23000 - Math.max(altitudeFt, 18000)) / 5000 : 1.0;
  const halfWidth = 0.9 * lowBandFactor;
  const low = stableSigmoid(logit - halfWidth);
  const high = stableSigmoid(logit + halfWidth);
  return {
    lowPercent: low * 100,
    highPercent: high * 100,
    widthPercent: (high - low) * 100,
  };
}

// ---------------------------------------------------------------------------
// ADRAC closed-form log-logistic AFT
// ---------------------------------------------------------------------------

/**
 * P(DCS) = 1 / (1 + exp((ln t - β₂ - β·x) / β₁))
 *
 * x = [ambient pressure (mmHg), prebreathing time (min),
 *      mildIndicator (0/1), heavyIndicator (0/1)].
 * Coefficients in adrac_coefficients.json fitted on the cleaned ADRAC
 * grid; reference fit metrics MAE = 8.74 pp, R² = 0.864 (n = 15,908).
 */
export function predictADRAC(
  altitudeFt: number,
  prebreatheMin: number,
  exerciseLevel: ExerciseLevel,
  timeAtAltitudeMin: number,
): { riskFraction: number; logT: number; covariateTerm: number; pressureMmHg: number } {
  const pressureMmHg = altitudeFtToMmHg(altitudeFt);
  const mild = exerciseLevel === "Mild" ? 1 : 0;
  const heavy = exerciseLevel === "Heavy" ? 1 : 0;
  const x = [pressureMmHg, prebreatheMin, mild, heavy];

  const covariateTerm =
    ADRAC.beta[0] * x[0] +
    ADRAC.beta[1] * x[1] +
    ADRAC.beta[2] * x[2] +
    ADRAC.beta[3] * x[3];

  const logT = Math.log(Math.max(timeAtAltitudeMin, 1e-6));
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
      { name: "supersaturation_atm", value: supersaturation },
      { name: "exercise_dose", value: exerciseDose },
      { name: "covariate_term", value: covariateTerm },
    ],
    modelMetadata: {
      modelPath: "mechanistic/adrac.py (closed-form log-logistic AFT)",
      applyV11Transforms: true,
    },
  };
}

// ---------------------------------------------------------------------------
// NASA Conkin RM/NM logistic
// ---------------------------------------------------------------------------

function nasaKFromVo2(vo2MlKgMin: number, lambda2: number): number {
  if (!Number.isFinite(vo2MlKgMin) || vo2MlKgMin < 0)
    throw new Error("vo2MlKgMin must be finite and ≥ 0");
  if (!Number.isFinite(lambda2) || lambda2 <= 0)
    throw new Error("lambda2 must be finite and > 0");
  return (1 - Math.exp(-lambda2 * vo2MlKgMin)) / 51.937 + LN2 / DEFAULT_T_HALF_MIN;
}

function nasaP1n2AfterPb(
  p0Psia: number,
  paPsia: number,
  vo2MlKgMin: number,
  pbTimeMin: number,
  lambda2: number,
): number {
  if (pbTimeMin < 0) throw new Error("pbTimeMin must be ≥ 0");
  const k = nasaKFromVo2(vo2MlKgMin, lambda2);
  return p0Psia + (paPsia - p0Psia) * (1 - Math.exp(-k * pbTimeMin));
}

function nasaEtr(p1n2Psia: number, p2Psia: number): number {
  if (!Number.isFinite(p1n2Psia) || !Number.isFinite(p2Psia))
    throw new Error("Pressures must be finite");
  if (p2Psia <= 0) throw new Error("p2Psia must be > 0");
  return p1n2Psia / p2Psia;
}

function nasaPDcsNm(etr: number, sex: "Male" | "Female"): number {
  if (!Number.isFinite(etr) || etr <= 0)
    throw new Error("ETR must be finite and > 0");
  const sexCode = sex === "Male" ? 1.0 : 0.0;
  return stableSigmoid(-25.56 + 12.83 * etr - 1.037 * sexCode);
}

function nasaPDcsRm(etr: number, ageYears: number): number {
  if (!Number.isFinite(etr) || etr <= 0)
    throw new Error("ETR must be finite and > 0");
  if (!Number.isFinite(ageYears) || ageYears <= 0)
    throw new Error("age must be finite and > 0");
  return stableSigmoid(-31.71 + 14.55 * etr + 0.053 * ageYears);
}

export function predictNASA(inputs: NASAInputs): NASAPrediction {
  const p1n2 = nasaP1n2AfterPb(
    inputs.p0Psia,
    inputs.paPsia,
    inputs.vo2MlKgMin,
    inputs.pbTimeMin,
    inputs.lambda2,
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

  return {
    p1n2Psia: p1n2,
    etr,
    pDcsPercent: pDcs * 100,
    equation,
  };
}

// ---------------------------------------------------------------------------
// Mechanistic 3RUT-MBe1 (schematic preview).
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

/**
 * Schematic 3RUT-MBe1 preview — single-compartment Conkin tissue dynamics,
 * dose-driven hazard rate, and ADRAC closed-form for the final P(DCS).
 * The displayed hazard / bubble proxies are illustrative shapes only;
 * full ODE recursion is in mechanistic/rut_mbe1.py.
 */
export function runMechanisticSimulation(
  inputs: MechanisticInputs,
): { history: ModelState[]; finalPDcsPercent: number } {
  const segments = buildMechanisticProfile(inputs);
  const dtMin = inputs.dtMin;
  const tauN2 = DEFAULT_T_HALF_MIN / LN2;
  const tauO2 = 30 / LN2;

  const history: ModelState[] = [];
  let t = 0;
  let ptN2Atm = N2_FRACTION_AIR;
  let ptO2Atm = 0.21 * (1 - 47 / 760);
  let cumulativeHazard = 0;
  let bubbleProxy = 0;

  for (const seg of segments) {
    const nSteps = Math.max(1, Math.ceil(seg.durationMin / dtMin));
    const stepDt = seg.durationMin / nSteps;
    for (let i = 0; i < nSteps; i++) {
      const pInsp = Math.max(seg.pAmbAtm - 47 / 760, 0);
      const pInspN2 = pInsp * seg.fin2;
      const pInspO2 = pInsp * seg.fio2;

      ptN2Atm += (pInspN2 - ptN2Atm) * (1 - Math.exp(-stepDt / tauN2));
      ptO2Atm += (pInspO2 - ptO2Atm) * (1 - Math.exp(-stepDt / tauO2));

      const supersaturation = Math.max(0, ptN2Atm - seg.pAmbAtm * 0.79);
      const exerciseFactor = 1 + seg.iExLMinWb * 0.6162;
      const hazardRate = 6.188e-2 * supersaturation * exerciseFactor;
      cumulativeHazard += hazardRate * stepDt;
      const pSurvival = Math.exp(-cumulativeHazard);
      bubbleProxy = Math.max(0, supersaturation * exerciseFactor * 1.198);

      const pCrushAtm = Math.max(0, seg.pAmbAtm - ptN2Atm - ptO2Atm - 0.06);
      history.push({
        tMin: t,
        pAmbAtm: seg.pAmbAtm,
        fio2: seg.fio2,
        fin2: seg.fin2,
        iExLMinWb: seg.iExLMinWb,
        ptN2Atm,
        ptO2Atm,
        rHat: 4.868e-5 * (1 + supersaturation * 5),
        pbN2Atm: ptN2Atm * 0.95,
        pbO2Atm: ptO2Atm * 1.05,
        xHatN2: 0,
        xHatO2: 0,
        nB: bubbleProxy,
        nBMax: 1.198,
        pCrushAtm,
        betaFHat: 0,
        rHatMin: 4.868e-5 * 100,
        hPerMin: hazardRate,
        pSurvival,
        pDcs: 1 - pSurvival,
      });
      t += stepDt;
    }
  }

  const adrac = predictADRAC(
    inputs.altitudeFt,
    inputs.prebreathingTimeMin,
    inputs.altitudeExerciseLevel,
    inputs.timeAtAltitudeMin,
  );
  const finalPDcsPercent = adrac.riskFraction * 100;

  return { history, finalPDcsPercent };
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
  altitudeRange = [18000, 40000],
  timeRange = [10, 240],
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
      const { riskFraction } = predictADRAC(alt, prebreatheMin, exerciseLevel, t);
      out.push({ altitudeFt: alt, timeAtAltitudeMin: t, riskPercent: riskFraction * 100 });
    }
  }
  return out;
}
