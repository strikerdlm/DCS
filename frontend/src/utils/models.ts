/**
 * DCS Risk Model Calculations
 * 
 * Implements the mathematical models for DCS risk prediction.
 * Based on published research equations from:
 * - NEDU TR 18-01 (3RUT-MBe1 model)
 * - NASA/TM-2004-213093 (ETR logistic models)
 * 
 * DISCLAIMER: These calculations are for research/educational purposes only.
 * NOT validated for clinical or operational decision-making.
 */

import { stableSigmoid, altitudeFtToPAmbAtm } from "../lib/utils";
import type {
  ExerciseLevel,
  MLSurrogateInputs,
  MLSurrogatePrediction,
  NASAInputs,
  NASAPrediction,
  MechanisticInputs,
  ModelState,
  ProfileSegment,
} from "../types";

// ============================================================================
// Constants
// ============================================================================

const LN2 = Math.log(2);
const DEFAULT_T_HALF_MIN = 360.0;

// Model parameters from Table 3 in 3RUT-MBe1 theory documentation
const MODEL_PARAMS = {
  pH2oMmhg: 47.0,
  rq: 1.0,
  ptCo2Mmhg: 45.0,
  alphaBo2MlPerMlPerAtm: 2.356e-2,
  alphaBn2MlPerMlPerAtm: 1.41e-2,
  kAlphaN2: 0.5985,
  kDn2: 0.9091,
  sigmaSurfaceTensionDynePerCm: 30.0,
  gainGHazard: 6.188e-2,
  n0BTotalNuclei: 1.198,
  beta0Cm: 4.868e-5,
  mElasticModulusAtmPerMl: 1.341e-7,
  nVgeGasLossRateMlInvMinInv: 4.758,
  sigmaCFactor: 19.64,
  alphaToCMlPerMlPerAtm: 4.536e-2,
  vTml: 5.279e-2,
  qTotalRestMlPerMin: 4.698e-3,
  dTo2Cm2PerMin: 1.414e-3,
  bnBubbleNumberPowerFactor: 2.172,
  tauPcrushMin: 201.4,
  mBetaEx: 0.6162,
  vdotO2RestMlPerMlPerMin: 4.401e-5,
  mVdotO2PerIEx: 1.677e-3,
  mQdotPerVdotO2: 6.997,
  lambdaCmInv: 100.0,
  nMinB: 1e-6,
};

// ============================================================================
// ML Surrogate Model (Simplified demonstration)
// ============================================================================

/**
 * Simplified ML surrogate prediction for demonstration
 * In production, this would call a backend API with actual ML models
 */
export function predictMLSurrogate(
  inputs: MLSurrogateInputs
): MLSurrogatePrediction {
  // Simplified risk estimation based on key factors
  // This is a demonstration approximation - actual model uses trained ML artefacts
  const { altitude, timeAtAltitude, prebreathingTime, exerciseLevel } = inputs;

  // Base risk factors (simplified demonstration)
  const altitudeFactor = Math.min(altitude / 63000, 1) * 0.4;
  const timeFactor = Math.min(timeAtAltitude / 300, 1) * 0.3;
  const prebreatheFactor = Math.max(0, 1 - prebreathingTime / 120) * 0.2;

  const exerciseMultiplier =
    exerciseLevel === "Rest" ? 1.0 : exerciseLevel === "Mild" ? 1.3 : 1.6;

  // Combine factors with sigmoid transformation
  const rawRisk =
    (altitudeFactor + timeFactor + prebreatheFactor) * exerciseMultiplier;
  const riskPercent = stableSigmoid(rawRisk * 6 - 3) * 100;

  return {
    riskPercent: Math.max(0, Math.min(100, riskPercent)),
    features: [
      { name: "altitude", value: altitude },
      { name: "time_at_altitude", value: timeAtAltitude },
      { name: "prebreathing_time", value: prebreathingTime },
      { name: `exercise_level_${exerciseLevel}`, value: 1.0 },
    ],
    modelMetadata: {
      applyV11Transforms: true,
    },
  };
}

// ============================================================================
// NASA ETR Logistic Models
// ============================================================================

/**
 * Calculate nitrogen elimination rate constant k
 * Based on Conkin et al. 2004 methodology
 * 
 * Reference: NASA/TM-2004-213093, DCS_NASA.py
 */
function nasaKFromVo2(vo2MlKgMin: number, lambda2: number): number {
  if (!Number.isFinite(vo2MlKgMin) || vo2MlKgMin < 0) {
    throw new Error("vo2MlKgMin must be finite and >= 0");
  }
  if (!Number.isFinite(lambda2) || lambda2 <= 0) {
    throw new Error("lambda2 must be finite and > 0");
  }
  return (
    (1 - Math.exp(-lambda2 * vo2MlKgMin)) / 51.937 + LN2 / DEFAULT_T_HALF_MIN
  );
}

/**
 * Compute tissue nitrogen pressure P1N2 after a single PB interval
 */
function nasaP1n2AfterPb(
  p0Psia: number,
  paPsia: number,
  vo2MlKgMin: number,
  pbTimeMin: number,
  lambda2: number
): number {
  if (pbTimeMin < 0) {
    throw new Error("pbTimeMin must be >= 0");
  }
  const k = nasaKFromVo2(vo2MlKgMin, lambda2);
  return p0Psia + (paPsia - p0Psia) * (1 - Math.exp(-k * pbTimeMin));
}

/**
 * Calculate Exercise Tissue Ratio (ETR)
 */
function nasaEtr(p1n2Psia: number, p2Psia: number): number {
  if (!Number.isFinite(p1n2Psia) || !Number.isFinite(p2Psia)) {
    throw new Error("Pressures must be finite");
  }
  if (p2Psia <= 0) {
    throw new Error("p2Psia must be > 0");
  }
  return p1n2Psia / p2Psia;
}

/**
 * NASA Model (NM): Eq. 14 from conkin-dcs-exercise_2004.md
 * P(DCS) = exp(-25.56 + 12.83*ETR - 1.037*SEX) / (1 + exp(...))
 * SEX coding: male = 1, female = 0
 */
function nasaPDcsNm(etrVal: number, sex: "Male" | "Female"): number {
  if (!Number.isFinite(etrVal) || etrVal <= 0) {
    throw new Error("etrVal must be finite and > 0");
  }
  const sexCode = sex === "Male" ? 1.0 : 0.0;
  const z = -25.56 + 12.83 * etrVal - 1.037 * sexCode;
  return stableSigmoid(z);
}

/**
 * Research Model (RM): Eq. 15 from conkin-dcs-exercise_2004.md
 * P(DCS) = exp(-31.71 + 14.55*ETR + 0.053*AGE) / (1 + exp(...))
 */
function nasaPDcsRm(etrVal: number, ageYears: number): number {
  if (!Number.isFinite(etrVal) || etrVal <= 0) {
    throw new Error("etrVal must be finite and > 0");
  }
  if (!Number.isFinite(ageYears) || ageYears <= 0) {
    throw new Error("ageYears must be finite and > 0");
  }
  const z = -31.71 + 14.55 * etrVal + 0.053 * ageYears;
  return stableSigmoid(z);
}

/**
 * Calculate NASA ETR prediction
 */
export function predictNASA(inputs: NASAInputs): NASAPrediction {
  const p1n2 = nasaP1n2AfterPb(
    inputs.p0Psia,
    inputs.paPsia,
    inputs.vo2MlKgMin,
    inputs.pbTimeMin,
    inputs.lambda2
  );

  const etr = nasaEtr(p1n2, inputs.p2Psia);

  let pDcs: number;
  let equation: string;

  if (inputs.variant === "NM") {
    pDcs = nasaPDcsNm(etr, inputs.sex);
    equation = `P(DCS) = σ(-25.56 + 12.83×ETR - 1.037×SEX)\nwhere SEX = ${inputs.sex === "Male" ? 1 : 0} (${inputs.sex})`;
  } else {
    pDcs = nasaPDcsRm(etr, inputs.ageYears);
    equation = `P(DCS) = σ(-31.71 + 14.55×ETR + 0.053×AGE)\nwhere AGE = ${inputs.ageYears}`;
  }

  return {
    p1n2Psia: p1n2,
    etr,
    pDcsPercent: pDcs * 100,
    equation,
  };
}

// ============================================================================
// Mechanistic 3RUT-MBe1 Model (Simplified demonstration)
// ============================================================================

/**
 * Map exercise level to I_ex (L/min whole-body O2 above rest)
 * Values from rut_mbe1_model.py
 */
function exerciseLevelToIEx(exerciseLevel: ExerciseLevel): number {
  const mapping: Record<ExerciseLevel, number> = {
    Rest: 0.0,
    Mild: 0.41,
    Heavy: 0.55,
  };
  return mapping[exerciseLevel];
}

/**
 * Build profile segments for mechanistic model
 */
export function buildMechanisticProfile(
  inputs: MechanisticInputs
): ProfileSegment[] {
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

  // Prebreathe segment
  if (prebreathingTimeMin > 0) {
    segments.push({
      durationMin: prebreathingTimeMin,
      pAmbAtm: 1.0,
      fio2: prebreathFio2,
      fin2: Math.max(0, 1 - prebreathFio2),
      iExLMinWb: iExPre,
    });
  }

  // Ascent segments
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
        iExLMinWb: 0.0,
      });
    }
  }

  // Altitude exposure segment
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
 * Simplified mechanistic simulation for demonstration
 * In production, this would call the Python backend for full recursion
 */
export function runMechanisticSimulation(
  inputs: MechanisticInputs
): { history: ModelState[]; finalPDcsPercent: number } {
  const segments = buildMechanisticProfile(inputs);
  const dtMin = inputs.dtMin;

  // Simplified simulation for demonstration
  // Generate time series based on profile
  const history: ModelState[] = [];
  let t = 0;
  let pSurvival = 1.0;

  for (const seg of segments) {
    const nSteps = Math.max(1, Math.ceil(seg.durationMin / dtMin));
    const stepDt = seg.durationMin / nSteps;

    for (let i = 0; i < nSteps; i++) {
      // Simplified risk accumulation model
      const supersaturation = Math.max(
        0,
        (1 - seg.pAmbAtm) * (1 - seg.fio2) * 0.79
      );
      const hazardRate =
        MODEL_PARAMS.gainGHazard *
        supersaturation *
        (1 + seg.iExLMinWb * MODEL_PARAMS.mBetaEx);

      pSurvival *= Math.exp(-hazardRate * stepDt);

      // Generate realistic-looking state variables
      const ptN2 = 0.79 * seg.pAmbAtm * (1 - seg.fio2 / (seg.fio2 + 0.001));
      const ptO2 = seg.fio2 * seg.pAmbAtm * 0.9;

      history.push({
        tMin: t,
        pAmbAtm: seg.pAmbAtm,
        fio2: seg.fio2,
        fin2: seg.fin2,
        iExLMinWb: seg.iExLMinWb,
        ptN2Atm: ptN2,
        ptO2Atm: ptO2,
        rHat: 1e-4 * (1 - pSurvival) * 10,
        pbN2Atm: ptN2 * 0.95,
        pbO2Atm: ptO2 * 1.05,
        xHatN2: 0,
        xHatO2: 0,
        nB: Math.max(0, (1 - pSurvival) * MODEL_PARAMS.n0BTotalNuclei),
        nBMax: (1 - pSurvival) * MODEL_PARAMS.n0BTotalNuclei,
        pCrushAtm: Math.max(0, seg.pAmbAtm - ptN2 - ptO2 - 0.06),
        betaFHat: 0,
        rHatMin: MODEL_PARAMS.beta0Cm * MODEL_PARAMS.lambdaCmInv,
        hPerMin: hazardRate,
        pSurvival,
        pDcs: 1 - pSurvival,
      });

      t += stepDt;
    }
  }

  return {
    history,
    finalPDcsPercent: (1 - pSurvival) * 100,
  };
}
