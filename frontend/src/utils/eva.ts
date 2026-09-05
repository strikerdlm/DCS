/** Offline reference calculation. Kept in numerical parity with tinydcs/eva.py. */
import { stableSigmoid } from "../lib/utils";
import { missionRules, validateScenario } from "./evaContract";
import type { EVAOptions, MissionRules } from "./evaContract";
import { applyTelemetry } from "./evaTelemetry";
import type { EVADecisionImplication, EVAScenario, EVASimulationResult, EVATimelinePoint, RiskConsequenceLevel, RiskLikelihoodLevel, RiskMatrixHazard } from "../types";

export { missionRules } from "./evaContract";
export type { EVAOptions, MissionRules } from "./evaContract";
export const EVA_MODEL_VERSION = "eva-reference-v2";
export const NASA_SOURCE = "https://www.nasa.gov/wp-content/uploads/2023/03/conkin-dcs-exercise-tp-213158-2004.pdf";
const MMHG_PER_PSIA = 760 / 14.695948775513449;
export const psiaToKpa = (psia: number): number => psia * 6.894757293168;
export const psiaToMmHg = (psia: number): number => psia * MMHG_PER_PSIA;
export const inspiredGasPsia = (p: number, fraction: number): number => Math.max(p - 47 / MMHG_PER_PSIA, 0) * fraction;
const tissueToward = (initial: number, target: number, duration: number): number => target + (initial - target) * Math.exp(-duration * Math.LN2 / 360);
const tissueExercise = (initial: number, target: number, duration: number, vo2: number): number => target + (initial - target) * Math.exp(-duration * Math.exp(.025 * vo2) / 519.37);

export function likelihoodFromProbability(p: number | null, rules: MissionRules): RiskLikelihoodLevel | null {
  if (p === null) return null;
  if (!Number.isFinite(p) || p < 0 || p > 100) throw new Error("risk must be a finite percentage");
  const t = rules.lxc_probability_thresholds_percent;
  if (p < t.level_2_min) return 1;
  if (p < t.level_3_min) return 2;
  if (p < t.level_4_min) return 3;
  if (p < t.level_5_min) return 4;
  return 5;
}

export function posture(score: number | null, rules: MissionRules): RiskMatrixHazard["posture"] {
  if (score === null) return "unavailable";
  for (const color of ["green", "yellow", "orange"] as const) if (score <= rules.posture_score_max[color]) return color;
  return "red";
}

function hazard(id: string, name: string, p: number | null, consequence: RiskConsequenceLevel, driver: string, rules: MissionRules, indicator: RiskMatrixHazard["indicator"] = null): RiskMatrixHazard {
  const likelihood = likelihoodFromProbability(p, rules), score = likelihood === null ? null : likelihood * consequence;
  return { id, name, probabilityPercent: p, likelihood, consequence, score, posture: posture(score, rules), driver, indicator,
    evidenceStatus: p === null ? "indicator_only" : "reference_endpoint" };
}

function planningWarnings(s: EVAScenario, rules: MissionRules): string[] {
  const e = rules.envelope, out: string[] = [];
  if (s.suit.pressurePsia < e.suit_pressure_psia_min || s.suit.pressurePsia > e.suit_pressure_psia_max)
    out.push(`Suit pressure is outside the ${e.suit_pressure_psia_min.toFixed(1)}-${e.suit_pressure_psia_max.toFixed(1)} psia exploration comparison range.`);
  if (s.habitat.pressurePsia < e.habitat_pressure_psia_min || s.habitat.pressurePsia > e.habitat_pressure_psia_max)
    out.push(`Habitat pressure is outside the ${e.habitat_pressure_psia_min.toFixed(1)}-${e.habitat_pressure_psia_max.toFixed(1)} psia planning range.`);
  if (s.habitat.oxygenFraction < e.habitat_oxygen_fraction_min || s.habitat.oxygenFraction > e.habitat_oxygen_fraction_max) out.push("Habitat oxygen fraction is outside the configured planning range.");
  if (s.prebreatheOxygenFraction < e.prebreathe_oxygen_fraction_min || s.prebreatheOxygenFraction > e.prebreathe_oxygen_fraction_max) out.push("Prebreathe oxygen fraction is outside the configured planning range.");
  if (s.prebreatheMin < e.prebreathe_min_min || s.prebreatheMin > e.prebreathe_min_max) out.push("Prebreathe duration is outside the configured planning range.");
  if (s.evaDurationMin < e.eva_duration_min_min || s.evaDurationMin > e.eva_duration_min_max) out.push("EVA duration is outside the configured planning range.");
  if (s.prebreatheMin < e.short_prebreathe_high_pressure_min && s.habitat.pressurePsia > e.short_prebreathe_high_pressure_psia) out.push("Short prebreathe from a high-pressure habitat is an unsupported extrapolation.");
  return out;
}

function modelApplicability(s: Required<EVAScenario>): EVASimulationResult["modelApplicability"] {
  const reasons: string[] = [];
  if (Math.abs(s.evaDurationMin - 240) > 1e-8) reasons.push("The NASA endpoint is four hours; no duration scaling is validated.");
  if (s.suit.variablePressure || s.pressureSegments.length > 1) reasons.push("Variable-pressure EVA is outside the NASA reference endpoint.");
  const pressures = s.pressureSegments.length ? s.pressureSegments : [s.suit];
  if (pressures.some(p => Math.abs(p.pressurePsia - 4.3) > 1e-8 || Math.abs(p.oxygenFraction - 1) > 1e-8)) reasons.push("Reference exposure requires constant 4.3 psia and oxygen breathing.");
  if (!s.nasaAdynamicReference) reasons.push("Adynamic source-reference assumptions have not been declared.");
  return { applicable: reasons.length === 0, reasons, modelId: "conkin-RM-equation-14", horizonMin: 240, referencePressurePsia: 4.3, source: NASA_SOURCE, intervalKind: "unavailable", clinicalValidation: false,
    evidenceStatus: reasons.length ? "outside_reference" : "reference_calculation",
    assumptions: ["Source-cohort transportability is not established.", "NASA dry ambient nitrogen convention; lambda=0.025.", "Exercise-dependent kinetics outside prebreathe are an exploratory compartment extension."] };
}

function pbSegments(s: Required<EVAScenario>) {
  return s.prebreatheSegments.length ? s.prebreatheSegments : s.prebreatheMin ? [{ durationMin: s.prebreatheMin, pressurePsia: s.habitat.pressurePsia, oxygenFraction: s.prebreatheOxygenFraction, vo2MlKgMin: s.prebreatheVo2MlKgMin }] : [];
}

function point(timeMin: number, phase: EVATimelinePoint["phase"], pressure: number, oxygen: number, tissue: number, vo2: number): EVATimelinePoint {
  return { timeMin, phase, ambientPressurePsia: pressure, ambientN2Psia: pressure * (1 - oxygen), inspiredN2Psia: pressure * (1 - oxygen), tissueN2Psia: tissue, vo2MlKgMin: vo2, cumulativePDcsPercent: null, intervalLowPercent: null, intervalHighPercent: null };
}

function buildTimeline(s: Required<EVAScenario>, initial: number): EVATimelinePoint[] {
  let tissue = initial, time = -s.prebreatheMin;
  const timeline = [point(time, "habitat", s.habitat.pressurePsia, s.habitat.oxygenFraction, tissue, 0)];
  for (const segment of pbSegments(s)) {
    const count = Math.max(1, Math.ceil(segment.durationMin / 5)), duration = segment.durationMin / count;
    for (let i = 0; i < count; i++) {
      tissue = tissueExercise(tissue, segment.pressurePsia * (1 - segment.oxygenFraction), duration, segment.vo2MlKgMin);
      time += duration;
      timeline.push(point(Math.min(time, 0), "prebreathe", segment.pressurePsia, segment.oxygenFraction, tissue, segment.vo2MlKgMin));
    }
  }
  timeline[timeline.length - 1].timeMin = 0;
  const duration = s.evaDurationMin;
  if (!duration) return timeline;
  const workload = s.workload.length ? s.workload : [{ durationMin: duration, vo2MlKgMin: s.meanVo2MlKgMin }];
  const pressure = s.pressureSegments.length ? s.pressureSegments : [{ durationMin: duration, ...s.suit }];
  const endpoints = (blocks: {durationMin: number}[]) => { let t = 0; return blocks.map(b => t += b.durationMin); };
  const workEnds = endpoints(workload), pressureEnds = endpoints(pressure), step = Math.max(1, Math.ceil(duration / 48));
  workEnds[workEnds.length - 1] = pressureEnds[pressureEnds.length - 1] = duration;
  const allCuts = [0, duration, ...workEnds, ...pressureEnds];
  for (let t = step; t < Math.ceil(duration); t += step) allCuts.push(t);
  const cuts = [...new Set(allCuts)].sort((a, b) => a - b);
  for (let i = 1; i < cuts.length; i++) {
    const start = cuts[i - 1], end = cuts[i], middle = (start + end) / 2;
    if (end - start <= 1e-10) continue;
    const work = workload[workEnds.findIndex(t => middle < t)], gas = pressure[pressureEnds.findIndex(t => middle < t)];
    tissue = tissueExercise(tissue, gas.pressurePsia * (1 - gas.oxygenFraction), end - start, work.vo2MlKgMin);
    timeline.push(point(end, "eva", gas.pressurePsia, gas.oxygenFraction, tissue, work.vo2MlKgMin));
  }
  return timeline;
}

function chooseDecision(abstain: boolean, score: number | null, p: number | null, stops: string[], rules: MissionRules): { decision: EVADecisionImplication; rationale: string } {
  if (stops.length) return { decision: "abort", rationale: "A configured stop condition is present, independently of model availability." };
  if (abstain || p === null || score === null) return { decision: "abstain", rationale: "No applicable DCS endpoint estimate; indicators do not establish a safe operating decision." };
  const t = rules.decision_thresholds;
  for (const action of ["delay", "modify", "monitor"] as const)
    if (score >= t[`${action}_lxc_score_min`] || p >= t[`${action}_risk_percent_min`])
      return { decision: action, rationale: `Reference endpoint meets the configured ${action} threshold; this is a planning classification.` };
  return { decision: "proceed", rationale: "Below configured reference-model thresholds; this is not operational clearance." };
}

export function simulateEVA(input: EVAScenario, options: EVAOptions = {}): EVASimulationResult {
  const rules = missionRules(options.missionRuleProfile), s = validateScenario(input);
  const telemetryStatus = applyTelemetry(s, options.telemetry ?? [], rules, options.telemetryNowSec);
  validateScenario(s);
  const initial = tissueToward(11.6, s.habitat.pressurePsia * (1 - s.habitat.oxygenFraction), s.habitat.equilibrationHours * 60);
  let p1 = initial;
  for (const segment of pbSegments(s)) p1 = tissueExercise(p1, segment.pressurePsia * (1 - segment.oxygenFraction), segment.durationMin, segment.vo2MlKgMin);
  const etr = p1 / (s.pressureSegments[0]?.pressurePsia ?? s.suit.pressurePsia);
  const applicability = modelApplicability(s), probability = applicability.applicable ? stableSigmoid(-31.71 + 14.55 * etr + .053 * s.crew.ageYears) * 100 : null;
  const suitO2 = Math.min(...(s.pressureSegments.length ? s.pressureSegments : [s.suit]).map(p => psiaToMmHg(inspiredGasPsia(p.pressurePsia, p.oxygenFraction))));
  const habitatO2 = psiaToMmHg(inspiredGasPsia(s.habitat.pressurePsia, s.habitat.oxygenFraction));
  const margin = s.suit.plssDurationMin - s.evaDurationMin, warnings = planningWarnings(s, rules);
  const abstain = !applicability.applicable || warnings.length > 0;
  const consequence = Math.min(5, Math.max(1, rules.hazards.dcs_base_consequence + Number(etr > rules.hazards.dcs_etr_consequence_trigger) + Number(s.environment.shelterReturnMin > rules.hazards.dcs_shelter_return_consequence_trigger_min))) as RiskConsequenceLevel;
  const dcs = hazard("dcs", "DCS", probability, consequence, `ETR ${etr.toFixed(2)}; source applicability required`, rules);
  const hazards = [dcs];
  const indicators: Array<[string, string, number | string, string, RiskConsequenceLevel, string]> = [
    ["hypoxia", "Inspired oxygen", Math.min(suitO2, habitatO2), "mmHg", 4, "Lowest humidified inspired O2; not an event probability"],
    ["co2", "CO2 scrubber", s.suit.co2ScrubberMargin, "fraction", 4, "Entered scrubber margin"],
    ["thermal", "Cooling", s.suit.coolingMargin, "fraction", 3, "Entered cooling margin"],
    ["dust", "Dust exposure", s.environment.dustLevel, "index 0–1", 3, "User-entered dust indicator"],
    ["fatigue", "Workload", s.peakVo2MlKgMin, "mL/kg/min", 3, "Declared peak VO2; no fatigue probability model"],
    ["radiation", "Radiation weather", s.environment.radiationWeather, "category", 5, "Declared weather state"],
    ["consumables", "PLSS margin", margin, "min", 4, "PLSS duration minus EVA duration; reserve is separate"],
  ];
  for (const [id, name, value, unit, severity, driver] of indicators) hazards.push(hazard(id, name, null, severity, driver, rules, { value, unit, source: "scenario_or_arithmetic" }));
  const stopReasons = [];
  if (s.crew.symptomFlag) stopReasons.push("active_symptoms");
  if (s.environment.radiationWeather === "storm") stopReasons.push("radiation_storm");
  if (margin < 0) stopReasons.push("negative_plss_margin");
  const decision = chooseDecision(abstain, dcs.score, probability, stopReasons, rules);
  const totalWork = s.workload.length ? s.workload.reduce((sum, b) => sum + b.durationMin * b.vo2MlKgMin, 0) : s.evaDurationMin * s.meanVo2MlKgMin;
  return {
    schemaVersion: 2, pDcsPercent: probability, intervalLowPercent: null, intervalHighPercent: null,
    modelApplicability: applicability, p1n2Psia: p1, etr, tissueN2StartPsia: initial, tissueN2AfterPrebreathePsia: p1,
    suitInspiredO2MmHg: suitO2, habitatInspiredO2MmHg: habitatO2, consumablesMarginMin: margin, oxygenReserveMin: s.suit.oxygenReserveMin,
    workloadMeanVo2MlKgMin: s.evaDurationMin ? totalWork / s.evaDurationMin : 0, workloadTotalO2Litres: totalWork * s.crew.massKg / 1000,
    inEnvelope: !abstain, planningEnvelope: !warnings.length, abstain, envelopeWarnings: [...applicability.reasons, ...warnings],
    maxRiskPercent: null, maxRiskTimeMin: null, integratedRiskPercentHours: null,
    lxcLikelihood: dcs.likelihood, lxcConsequence: dcs.consequence, lxcScore: dcs.score, lxcCategory: dcs.posture,
    decision: decision.decision, decisionRationale: decision.rationale, stopReasons, timeline: buildTimeline(s, initial), hazards, telemetryStatus,
  };
}

export const cloneScenario = (scenario: EVAScenario): EVAScenario => structuredClone(scenario);
export function summarizePosture(hazards: RiskMatrixHazard[]): RiskMatrixHazard["posture"] {
  if (!hazards.length || hazards.some(h => h.score === null)) return "unavailable";
  return posture(Math.max(...hazards.map(h => h.score!)), missionRules());
}
