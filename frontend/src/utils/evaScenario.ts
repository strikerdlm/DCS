import type { EVAScenario } from "../types";
import { applyTelemetry } from "./evaTelemetry";
import { missionRules, validateScenario } from "./evaContract";
import type { EVAOptions } from "./evaContract";

function rescale<T extends { durationMin: number }>(blocks: T[], duration: number): void {
  if (!blocks.length) return;
  const total = blocks.reduce((sum, b) => sum + b.durationMin, 0);
  let elapsed = 0;
  blocks.forEach((block, index) => {
    block.durationMin = index === blocks.length - 1 ? duration - elapsed : block.durationMin / total * duration;
    elapsed += block.durationMin;
  });
}

export function normalizePreset(input: EVAScenario): EVAScenario {
  const s = structuredClone(input);
  if (s.workload.length && s.evaDurationMin) s.meanVo2MlKgMin = s.workload.reduce((sum,b) => sum+b.durationMin*b.vo2MlKgMin,0) / s.evaDurationMin;
  s.peakVo2MlKgMin = Math.max(s.peakVo2MlKgMin, s.meanVo2MlKgMin, ...s.workload.map(b => b.vo2MlKgMin));
  return s;
}

/** UI edits explicitly rescale schedules; the scientific calculator never does. */
export function updateScenario(input: EVAScenario, mutator: (draft: EVAScenario) => void): EVAScenario {
  const s = structuredClone(input);
  mutator(s);
  if (s.evaDurationMin !== input.evaDurationMin) {
    if (s.evaDurationMin === 0) { s.workload = []; s.pressureSegments = []; s.suit.variablePressure = false; }
    else { rescale(s.workload, s.evaDurationMin); rescale(s.pressureSegments ?? [], s.evaDurationMin); }
  }
  if (s.prebreatheMin !== input.prebreatheMin) {
    if (s.prebreatheMin === 0) s.prebreatheSegments = [];
    else rescale(s.prebreatheSegments ?? [], s.prebreatheMin);
  }
  if (s.meanVo2MlKgMin !== input.meanVo2MlKgMin && s.workload.length) {
    const mean = s.workload.reduce((sum, b) => sum+b.durationMin*b.vo2MlKgMin,0) / s.evaDurationMin;
    s.workload.forEach(b => { b.vo2MlKgMin = mean ? b.vo2MlKgMin*s.meanVo2MlKgMin/mean : s.meanVo2MlKgMin; });
  }
  if (s.suit.pressurePsia !== input.suit.pressurePsia && s.pressureSegments?.length) s.pressureSegments[0].pressurePsia = s.suit.pressurePsia;
  return normalizePreset(s);
}

/** Apply the common observation context once, then change future hypotheses.
 * Do not reapply a current pressure snapshot over a proposed future pressure.
 */
export function scenarioAlternatives(input: EVAScenario, options: EVAOptions) {
  const observed = validateScenario(input);
  applyTelemetry(observed, options.telemetry ?? [], missionRules(options.missionRuleProfile), options.telemetryNowSec);
  const shorter = Math.min(observed.evaDurationMin, Math.max(30, observed.evaDurationMin - 60));
  const higher = Math.min(8.2, observed.suit.pressurePsia + 1);
  return [
    { id: "baseline", label: "Scheduled now", scenario: observed },
    { id: "delay", label: "Delay: +120 min PB", scenario: updateScenario(observed, d => { d.prebreatheMin += 120; }) },
    { id: "habitat", label: "Alter habitat 8.2/34%", scenario: updateScenario(observed, d => {
      d.habitat.pressurePsia = 8.2; d.habitat.oxygenFraction = .34;
      d.habitat.equilibrationHours = Math.max(d.habitat.equilibrationHours, 24); d.prebreatheMin = Math.max(d.prebreatheMin,30);
    }) },
    { id: "pressure", label: `Suit stage 1: ${higher.toFixed(1)} psia`, scenario: updateScenario(observed, d => { d.suit.pressurePsia = higher; }) },
    { id: "shorten", label: `EVA: −${observed.evaDurationMin - shorter} min`, scenario: updateScenario(observed, d => { d.evaDurationMin = shorter; }) },
    { id: "workload", label: "20% lower workload", scenario: updateScenario(observed, d => { d.meanVo2MlKgMin *= .8; d.peakVo2MlKgMin *= .8; }) },
  ];
}
