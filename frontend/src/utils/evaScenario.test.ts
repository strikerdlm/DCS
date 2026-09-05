import { expect, it } from "vitest";
import { EVA_SCENARIOS } from "../data/evaScenarios";
import { updateScenario, normalizePreset, scenarioAlternatives } from "./evaScenario";
import { simulateEVA } from "./eva";
it("every dashboard preset has a valid explicit or constant pressure schedule", () => {
  for (const preset of EVA_SCENARIOS) expect(() => simulateEVA(normalizePreset(preset))).not.toThrow();
});
it("duration edits preserve workload duration fractions and exact endpoint", () => {
  const before = normalizePreset(EVA_SCENARIOS[1]);
  const after = updateScenario(before, d => { d.evaDurationMin = 83; });
  expect(after.workload.reduce((sum,b) => sum+b.durationMin,0)).toBeCloseTo(83, 10);
  expect(after.workload[0].durationMin / after.evaDurationMin).toBeCloseTo(before.workload[0].durationMin / before.evaDurationMin,10);
  expect(simulateEVA(after).timeline.at(-1)?.timeMin).toBeCloseTo(83,10);
});
it("mean workload edits scale the schedule without changing PB dose", () => {
  const before = normalizePreset(EVA_SCENARIOS[1]);
  const after = updateScenario(before, d => { d.meanVo2MlKgMin = 30; });
  expect(simulateEVA(after).workloadMeanVo2MlKgMin).toBeCloseTo(30,10);
  expect(simulateEVA(after).p1n2Psia).toBe(simulateEVA(before).p1n2Psia);
});
it.each([0, 30, 45, 60, 75, 240])("shortening cannot lengthen a %s-minute EVA", duration => {
  const scenario = updateScenario(normalizePreset(EVA_SCENARIOS[0]), d => {d.evaDurationMin=duration;});
  const shortened = scenarioAlternatives(scenario, {}).find(a => a.id === "shorten")!;
  expect(shortened.scenario.evaDurationMin).toBeLessThanOrEqual(duration);
  expect(() => simulateEVA(shortened.scenario)).not.toThrow();
});
it("applies observations once before a future pressure counterfactual", () => {
  const options = {telemetry:[{kind:"suit_pressure" as const,value:4.3,unit:"psia",timestampSec:995}],telemetryNowSec:1000};
  const scenario = normalizePreset(EVA_SCENARIOS[2]);
  scenario.nasaAdynamicReference = true;
  const alternatives = scenarioAlternatives(scenario, options);
  expect(simulateEVA(alternatives[0].scenario).pDcsPercent).toBe(simulateEVA(scenario, options).pDcsPercent);
  const higher = alternatives.find(a => a.id === "pressure")!.scenario;
  expect(higher.suit.pressurePsia).toBe(5.3);
  expect(simulateEVA(higher).pDcsPercent).toBeNull();
});
