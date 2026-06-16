import { clamp, stableSigmoid } from "../lib/utils";
import type {
  EVADecisionImplication,
  EVAScenario,
  EVASimulationResult,
  EVATimelinePoint,
  RiskConsequenceLevel,
  RiskLikelihoodLevel,
  RiskMatrixHazard,
} from "../types";

const LN2 = Math.log(2);
const SEA_LEVEL_PSIA = 14.7;
const WATER_VAPOR_PSIA = 0.91;
const N2_AIR_FRACTION = 0.79;
const TISSUE_HALF_TIME_MIN = 360;
const TISSUE_TAU_MIN = TISSUE_HALF_TIME_MIN / LN2;

export function psiaToKpa(psia: number): number {
  return psia * 6.894757;
}

export function psiaToMmHg(psia: number): number {
  return psia * 51.7149;
}

export function inspiredGasPsia(totalPressurePsia: number, fraction: number): number {
  return Math.max(totalPressurePsia - WATER_VAPOR_PSIA, 0) * clamp(fraction, 0, 1);
}

function tissueToward(initialPsia: number, targetPsia: number, durationMin: number): number {
  if (durationMin <= 0) return initialPsia;
  return targetPsia + (initialPsia - targetPsia) * Math.exp(-durationMin / TISSUE_TAU_MIN);
}

function exerciseAdjustedK(vo2MlKgMin: number): number {
  const lambda = 0.03;
  return (1 - Math.exp(-lambda * Math.max(vo2MlKgMin, 0))) / 51.937 + LN2 / TISSUE_HALF_TIME_MIN;
}

function tissueTowardWithExercise(
  initialPsia: number,
  targetPsia: number,
  durationMin: number,
  vo2MlKgMin: number,
): number {
  if (durationMin <= 0) return initialPsia;
  const k = exerciseAdjustedK(vo2MlKgMin);
  return targetPsia + (initialPsia - targetPsia) * Math.exp(-k * durationMin);
}

function conkinResearchPDcs(etr: number, ageYears: number): number {
  return stableSigmoid(-31.71 + 14.55 * etr + 0.053 * ageYears) * 100;
}

function intervalForRiskPercent(
  riskPercent: number,
  scenario: EVAScenario,
): { low: number; high: number } {
  const p = clamp(riskPercent / 100, 1e-6, 1 - 1e-6);
  const logit = Math.log(p / (1 - p));
  const novelProfile =
    scenario.kind === "scenario_c_habitat_pressure_decision" ||
    scenario.habitat.pressurePsia < 11 ||
    scenario.suit.variablePressure;
  const workloadWidth = clamp((scenario.peakVo2MlKgMin - 20) / 30, 0, 1);
  const halfWidth = 0.72 + (novelProfile ? 0.32 : 0) + workloadWidth * 0.22;
  return {
    low: stableSigmoid(logit - halfWidth) * 100,
    high: stableSigmoid(logit + halfWidth) * 100,
  };
}

function likelihoodFromProbability(percent: number): RiskLikelihoodLevel {
  if (percent < 1) return 1;
  if (percent < 5) return 2;
  if (percent < 15) return 3;
  if (percent < 35) return 4;
  return 5;
}

function posture(score: number): RiskMatrixHazard["posture"] {
  if (score <= 4) return "green";
  if (score <= 9) return "yellow";
  if (score <= 15) return "orange";
  return "red";
}

function hazard(
  id: string,
  name: string,
  probabilityPercent: number,
  consequence: RiskConsequenceLevel,
  driver: string,
): RiskMatrixHazard {
  const likelihood = likelihoodFromProbability(probabilityPercent);
  const score = likelihood * consequence;
  return {
    id,
    name,
    probabilityPercent: clamp(probabilityPercent, 0, 100),
    likelihood,
    consequence,
    score,
    posture: posture(score),
    driver,
  };
}

function buildTimeline(
  scenario: EVAScenario,
  tissueN2StartPsia: number,
  tissueN2AfterPrebreathePsia: number,
  pDcsPercent: number,
): EVATimelinePoint[] {
  const timeline: EVATimelinePoint[] = [];
  const habitatN2Psia = inspiredGasPsia(
    scenario.habitat.pressurePsia,
    1 - scenario.habitat.oxygenFraction,
  );
  const prebreatheN2Psia = inspiredGasPsia(
    scenario.habitat.pressurePsia,
    1 - scenario.prebreatheOxygenFraction,
  );
  const suitN2Psia = inspiredGasPsia(scenario.suit.pressurePsia, 1 - scenario.suit.oxygenFraction);
  const duration = Math.max(scenario.evaDurationMin, 1);
  const step = Math.max(5, Math.round(duration / 48));

  timeline.push({
    timeMin: -scenario.prebreatheMin,
    phase: "habitat",
    ambientPressurePsia: scenario.habitat.pressurePsia,
    inspiredN2Psia: habitatN2Psia,
    tissueN2Psia: tissueN2StartPsia,
    vo2MlKgMin: 3.5,
    cumulativePDcsPercent: 0,
    intervalLowPercent: 0,
    intervalHighPercent: 0,
  });
  timeline.push({
    timeMin: 0,
    phase: "prebreathe",
    ambientPressurePsia: scenario.habitat.pressurePsia,
    inspiredN2Psia: prebreatheN2Psia,
    tissueN2Psia: tissueN2AfterPrebreathePsia,
    vo2MlKgMin: scenario.meanVo2MlKgMin,
    cumulativePDcsPercent: 0,
    intervalLowPercent: 0,
    intervalHighPercent: 0,
  });

  for (let t = step; t <= duration; t += step) {
    const frac = clamp(t / duration, 0, 1);
    const workloadPulse =
      scenario.meanVo2MlKgMin +
      Math.sin(frac * Math.PI * 2) * Math.max(0, scenario.peakVo2MlKgMin - scenario.meanVo2MlKgMin) * 0.35;
    const tissueN2 = tissueTowardWithExercise(
      tissueN2AfterPrebreathePsia,
      suitN2Psia,
      t,
      workloadPulse,
    );
    const cumulativePDcsPercent = pDcsPercent * Math.pow(frac, 1.22);
    const interval = intervalForRiskPercent(cumulativePDcsPercent, scenario);
    timeline.push({
      timeMin: t,
      phase: "eva",
      ambientPressurePsia: scenario.suit.pressurePsia,
      inspiredN2Psia: suitN2Psia,
      tissueN2Psia: tissueN2,
      vo2MlKgMin: workloadPulse,
      cumulativePDcsPercent,
      intervalLowPercent: interval.low,
      intervalHighPercent: interval.high,
    });
  }

  return timeline;
}

function integrateRiskPercentHours(timeline: EVATimelinePoint[]): number {
  let areaPercentMin = 0;
  const evaPoints = timeline.filter((point) => point.timeMin >= 0);
  for (let i = 1; i < evaPoints.length; i++) {
    const a = evaPoints[i - 1];
    const b = evaPoints[i];
    const dt = Math.max(0, b.timeMin - a.timeMin);
    areaPercentMin += ((a.cumulativePDcsPercent + b.cumulativePDcsPercent) / 2) * dt;
  }
  return areaPercentMin / 60;
}

function maxRisk(timeline: EVATimelinePoint[]): { percent: number; timeMin: number } {
  return timeline.reduce(
    (best, point) =>
      point.cumulativePDcsPercent > best.percent
        ? { percent: point.cumulativePDcsPercent, timeMin: point.timeMin }
        : best,
    { percent: 0, timeMin: 0 },
  );
}

function scenarioEnvelopeWarnings(scenario: EVAScenario): string[] {
  const warnings: string[] = [];
  if (scenario.suit.pressurePsia < 3.7 || scenario.suit.pressurePsia > 8.2) {
    warnings.push("Suit pressure is outside the 3.7-8.2 psia exploration comparison range.");
  }
  if (scenario.habitat.pressurePsia < 5 || scenario.habitat.pressurePsia > 14.7) {
    warnings.push("Habitat pressure is outside the 5.0-14.7 psia planning range.");
  }
  if (scenario.habitat.oxygenFraction < 0.2 || scenario.habitat.oxygenFraction > 0.4) {
    warnings.push("Habitat oxygen fraction is outside the 20-40% planning range.");
  }
  if (scenario.prebreatheOxygenFraction < 0.21 || scenario.prebreatheOxygenFraction > 1) {
    warnings.push("Prebreathe oxygen fraction is outside the 21-100% range.");
  }
  if (scenario.prebreatheMin < 0 || scenario.prebreatheMin > 300) {
    warnings.push("Prebreathe duration is outside the 0-300 min planning range.");
  }
  if (scenario.evaDurationMin < 30 || scenario.evaDurationMin > 540) {
    warnings.push("EVA duration is outside the 30-540 min planning range.");
  }
  if (scenario.prebreatheMin < 15 && scenario.habitat.pressurePsia > 8.2) {
    warnings.push("Short prebreathe from a high-pressure habitat is an unsupported extrapolation.");
  }
  return warnings;
}

function chooseDecision({
  abstain,
  lxcScore,
  maxRiskPercent,
  integratedRiskPercentHours,
  consumablesMarginMin,
  radiationWeather,
  symptomFlag,
}: {
  abstain: boolean;
  lxcScore: number;
  maxRiskPercent: number;
  integratedRiskPercentHours: number;
  consumablesMarginMin: number;
  radiationWeather: EVAScenario["environment"]["radiationWeather"];
  symptomFlag: boolean;
}): { decision: EVADecisionImplication; rationale: string } {
  if (abstain) {
    return {
      decision: "abstain",
      rationale: "Model inputs are outside the supported planning envelope.",
    };
  }
  if (radiationWeather === "storm" || consumablesMarginMin < 0 || symptomFlag) {
    return {
      decision: "abort",
      rationale: "A hard operational stop is present: radiation storm, negative consumables margin, or active symptoms.",
    };
  }
  if (lxcScore >= 16 || maxRiskPercent >= 20) {
    return {
      decision: "delay",
      rationale: "LxC is red or DCS point risk exceeds the high-risk planning threshold.",
    };
  }
  if (lxcScore >= 10 || maxRiskPercent >= 10 || integratedRiskPercentHours >= 30) {
    return {
      decision: "modify",
      rationale: "Risk is elevated; modify prebreathe, suit pressure, workload, or EVA duration.",
    };
  }
  if (lxcScore >= 5 || maxRiskPercent >= 1 || integratedRiskPercentHours >= 5) {
    return {
      decision: "monitor",
      rationale: "Risk remains manageable but requires telemetry and symptom surveillance.",
    };
  }
  return {
    decision: "proceed",
    rationale: "Risk is low and inside the model envelope with positive operational margins.",
  };
}

function buildHazards(
  scenario: EVAScenario,
  pDcsPercent: number,
  etr: number,
  suitInspiredO2MmHg: number,
  habitatInspiredO2MmHg: number,
  consumablesMarginMin: number,
): RiskMatrixHazard[] {
  const durationFactor = clamp(scenario.evaDurationMin / 480, 0, 1.5);
  const workloadFactor = clamp((scenario.peakVo2MlKgMin - 15) / 25, 0, 1.5);
  const lowO2Factor = clamp((120 - Math.min(suitInspiredO2MmHg, habitatInspiredO2MmHg)) / 60, 0, 2);
  const co2Probability = clamp(
    (1 - scenario.suit.co2ScrubberMargin) * 34 + workloadFactor * 18 + durationFactor * 8,
    0,
    80,
  );
  const thermalProbability = clamp(
    (1 - scenario.suit.coolingMargin) * 32 +
      scenario.environment.sunExposure * 17 +
      workloadFactor * 20,
    0,
    85,
  );
  const dustProbability = clamp(
    scenario.environment.dustLevel * 42 +
      (scenario.suit.suitPort ? -10 : 10) +
      durationFactor * 8,
    0,
    90,
  );
  const fatigueProbability = clamp(
    durationFactor * 24 +
      workloadFactor * 26 +
      (scenario.suit.pressurePsia > 5.5 ? 10 : 0) +
      (scenario.crew.hydration < 0.65 ? 12 : 0),
    0,
    90,
  );
  const radiationBase =
    scenario.environment.radiationWeather === "quiet"
      ? 0.8
      : scenario.environment.radiationWeather === "elevated"
        ? 8
        : 45;
  const radiationProbability = clamp(
    radiationBase + durationFactor * 3 + Math.max(0, scenario.environment.shelterReturnMin - 20) * 0.7,
    0,
    95,
  );
  const consumablesProbability = clamp(
    consumablesMarginMin < 0 ? 55 + Math.abs(consumablesMarginMin) * 0.5 : Math.max(0, 12 - consumablesMarginMin) * 2,
    0,
    95,
  );

  const dcsConsequence = clamp(
    3 + (etr > 1.4 ? 1 : 0) + (scenario.environment.shelterReturnMin > 20 ? 1 : 0),
    1,
    5,
  ) as RiskConsequenceLevel;

  return [
    hazard("dcs", "DCS", pDcsPercent, dcsConsequence, `ETR ${etr.toFixed(2)} with ${scenario.prebreatheMin} min prebreathe`),
    hazard("hypoxia", "Hypoxia", lowO2Factor * 18, 4, `${Math.round(Math.min(suitInspiredO2MmHg, habitatInspiredO2MmHg))} mmHg lowest inspired O2`),
    hazard("co2", "CO2 retention", co2Probability, 4, `${Math.round(scenario.suit.co2ScrubberMargin * 100)}% scrubber margin`),
    hazard("thermal", "Thermal strain", thermalProbability, 3, `${Math.round(scenario.suit.coolingMargin * 100)}% cooling margin`),
    hazard("dust", "Dust contamination", dustProbability, 3, `${Math.round(scenario.environment.dustLevel * 100)}% dust load`),
    hazard("fatigue", "Fatigue / injury", fatigueProbability, 3, `${scenario.peakVo2MlKgMin.toFixed(0)} mL/kg/min peak VO2`),
    hazard("radiation", "Radiation event", radiationProbability, 5, scenario.environment.radiationWeather),
    hazard("consumables", "Consumables margin", consumablesProbability, 4, `${Math.round(consumablesMarginMin)} min remaining`),
  ];
}

export function simulateEVA(scenario: EVAScenario): EVASimulationResult {
  const seaLevelN2Psia = inspiredGasPsia(SEA_LEVEL_PSIA, N2_AIR_FRACTION);
  const habitatN2Psia = inspiredGasPsia(
    scenario.habitat.pressurePsia,
    1 - scenario.habitat.oxygenFraction,
  );
  const tissueN2StartPsia = tissueToward(
    seaLevelN2Psia,
    habitatN2Psia,
    scenario.habitat.equilibrationHours * 60,
  );
  const prebreatheN2Psia = inspiredGasPsia(
    scenario.habitat.pressurePsia,
    1 - scenario.prebreatheOxygenFraction,
  );
  const tissueN2AfterPrebreathePsia = tissueTowardWithExercise(
    tissueN2StartPsia,
    prebreatheN2Psia,
    scenario.prebreatheMin,
    scenario.meanVo2MlKgMin,
  );
  const p1n2Psia = tissueN2AfterPrebreathePsia;
  const etr = p1n2Psia / Math.max(scenario.suit.pressurePsia, 0.1);
  const rawPDcs = conkinResearchPDcs(etr, scenario.crew.ageYears);
  const workloadPenalty = Math.max(0, scenario.peakVo2MlKgMin - 30) * 0.35;
  const hydrationPenalty = scenario.crew.hydration < 0.65 ? 2.5 : 0;
  const symptomPenalty = scenario.crew.symptomFlag ? 6 : 0;
  const pDcsPercent = clamp(rawPDcs + workloadPenalty + hydrationPenalty + symptomPenalty, 0, 100);
  const interval = intervalForRiskPercent(pDcsPercent, scenario);
  const suitInspiredO2MmHg = psiaToMmHg(inspiredGasPsia(scenario.suit.pressurePsia, scenario.suit.oxygenFraction));
  const habitatInspiredO2MmHg = psiaToMmHg(
    inspiredGasPsia(scenario.habitat.pressurePsia, scenario.habitat.oxygenFraction),
  );
  const consumablesMarginMin =
    scenario.suit.plssDurationMin + scenario.suit.oxygenReserveMin - scenario.evaDurationMin;
  const envelopeWarnings = scenarioEnvelopeWarnings(scenario);
  const inEnvelope = envelopeWarnings.length === 0;
  const abstain = !inEnvelope;

  const timeline = buildTimeline(scenario, tissueN2StartPsia, tissueN2AfterPrebreathePsia, pDcsPercent);
  const hazards = buildHazards(
    scenario,
    pDcsPercent,
    etr,
    suitInspiredO2MmHg,
    habitatInspiredO2MmHg,
    consumablesMarginMin,
  );
  const dcsHazard = hazards.find((item) => item.id === "dcs") ?? hazards[0];
  const max = maxRisk(timeline);
  const integratedRiskPercentHours = integrateRiskPercentHours(timeline);
  const lxcLikelihood = dcsHazard.likelihood;
  const lxcConsequence = dcsHazard.consequence;
  const lxcScore = dcsHazard.score;
  const lxcCategory = dcsHazard.posture;
  const decision = chooseDecision({
    abstain,
    lxcScore,
    maxRiskPercent: max.percent,
    integratedRiskPercentHours,
    consumablesMarginMin,
    radiationWeather: scenario.environment.radiationWeather,
    symptomFlag: scenario.crew.symptomFlag,
  });

  return {
    pDcsPercent,
    intervalLowPercent: interval.low,
    intervalHighPercent: interval.high,
    p1n2Psia,
    etr,
    tissueN2StartPsia,
    tissueN2AfterPrebreathePsia,
    suitInspiredO2MmHg,
    habitatInspiredO2MmHg,
    consumablesMarginMin,
    inEnvelope,
    abstain,
    envelopeWarnings,
    maxRiskPercent: max.percent,
    maxRiskTimeMin: max.timeMin,
    integratedRiskPercentHours,
    lxcLikelihood,
    lxcConsequence,
    lxcScore,
    lxcCategory,
    decision: decision.decision,
    decisionRationale: decision.rationale,
    timeline,
    hazards,
  };
}

export function cloneScenario(scenario: EVAScenario): EVAScenario {
  return JSON.parse(JSON.stringify(scenario)) as EVAScenario;
}

export function summarizePosture(hazards: RiskMatrixHazard[]): RiskMatrixHazard["posture"] {
  const maxScore = Math.max(...hazards.map((h) => h.score));
  return posture(maxScore);
}
