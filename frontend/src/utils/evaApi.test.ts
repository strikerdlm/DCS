import { expect, it, vi, afterEach } from "vitest";
import { canUseOffline, EVAApiError, responseForInputs, createEVAReport, localScenarioReport, simulateEVAApi } from "./evaApi";
import fixtures from "../data/eva-golden.json";
import type { EVAScenario } from "../types";
import { missionRules } from "./eva";
const scenario = fixtures[2].scenario as EVAScenario;
const validResponse = () => ({schemaVersion:2,result:{schemaVersion:2},modelMetadata:{modelVersion:"eva-reference-v2"},missionRules:missionRules()});
afterEach(() => vi.unstubAllGlobals());
it("never exposes a previous input's response during debounce or out-of-order completion", () => {
  const state = { key: "old", response: { pDcsPercent: 25 } };
  expect(responseForInputs("changed", state)).toBeUndefined();
  expect(responseForInputs("old", state)).toBe(state.response);
});
it("allows only transport errors to fall back offline", () => {
  expect(canUseOffline(new TypeError("Failed to fetch"))).toBe(true);
  expect(canUseOffline(new EVAApiError(422, "bad inputs"))).toBe(false);
  expect(canUseOffline(new EVAApiError(500, "failed calculation"))).toBe(false);
});
it("does not send displayed or client-authored results to report API", async () => {
  const fetch = vi.fn().mockResolvedValue({ok: true, json: async () => ({artifacts:{json:{content:JSON.stringify(validResponse())}}})});
  vi.stubGlobal("fetch", fetch);
  await createEVAReport(scenario, {missionRuleProfile: "default", telemetryNowSec: 1000});
  const payload = JSON.parse(fetch.mock.calls[0][1].body);
  expect(payload).not.toHaveProperty("result");
  expect(payload.telemetryNowSec).toBe(1000);
});
it("preserves input/rules/telemetry context in an offline export and recalculates", () => {
  const report = localScenarioReport(scenario, {missionRuleProfile: "artemis_lunar", telemetryNowSec:1000});
  expect(report.scenario).toEqual(scenario);
  expect(report.missionRules.profile_id).toBe("artemis_lunar");
  expect(report.result.intervalLowPercent).toBeNull();
});
it("rejects obsolete API contracts", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ok:true, json:async () => ({ schemaVersion:1 })}));
  await expect(simulateEVAApi(scenario)).rejects.toThrow(/contract/);
});
it("refuses to mix server-customized rules with bundled browser alternatives", async () => {
  const rules = structuredClone(missionRules());
  rules.decision_thresholds.delay_risk_percent_min = 0.1;
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ok:true, json:async () => ({schemaVersion:2,result:{schemaVersion:2},modelMetadata:{modelVersion:"eva-reference-v2"},missionRules:rules})}));
  await expect(simulateEVAApi(scenario)).rejects.toThrow(/rule/i);
});
it("rejects report artifacts with different rules or an incompatible model", async () => {
  const payload = validResponse();
  payload.missionRules = structuredClone(payload.missionRules);
  payload.missionRules.decision_thresholds.delay_risk_percent_min = 0.1;
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ok:true,json:async () => ({artifacts:{json:{content:JSON.stringify(payload)}}})}));
  await expect(createEVAReport(scenario)).rejects.toThrow(/rule/i);
  payload.missionRules = missionRules();
  payload.modelMetadata.modelVersion = "obsolete";
  await expect(createEVAReport(scenario)).rejects.toThrow(/contract/i);
});
