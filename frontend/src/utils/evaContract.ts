import Ajv2020 from "ajv/dist/2020";
import schema from "../data/eva-schema.json";
import profiles from "../data/eva-rules.json";
import type { EVAScenario, EVATelemetrySample } from "../types";

export type MissionRules = Omit<typeof profiles.default, "uncertainty">;
export interface EVAOptions {
  missionRuleProfile?: string;
  telemetry?: EVATelemetrySample[];
  telemetryNowSec?: number;
}

const validate = new Ajv2020({ allErrors: true, useDefaults: true, strictNumbers: true }).compile(schema);

export function validateScenario(input: EVAScenario): Required<EVAScenario> {
  // Pydantic default_factory arrays are not emitted as JSON Schema defaults.
  const scenario = { prebreatheSegments: [], pressureSegments: [], ...structuredClone(input) };
  if (!validate(scenario)) throw new Error(`Invalid scenario: ${validate.errors?.map(e => `${e.instancePath} ${e.message}`).join("; ")}`);
  const s = scenario as Required<EVAScenario>;
  for (const [label, blocks, duration] of [
    ["workload", s.workload, s.evaDurationMin], ["pressure", s.pressureSegments, s.evaDurationMin],
    ["prebreathe", s.prebreatheSegments, s.prebreatheMin],
  ] as const) {
    if (blocks.length && Math.abs(blocks.reduce((sum, b) => sum + b.durationMin, 0) - duration) > 1e-6)
      throw new Error(`${label} segment durations must sum to the phase duration`);
    if (blocks.length) {
      const remaining = duration - blocks.slice(0, -1).reduce((sum,b) => sum+b.durationMin,0);
      if (remaining <= 0) throw new Error(`${label} final segment must have positive duration`);
      blocks[blocks.length - 1].durationMin = remaining;
    }
  }
  if (s.suit.variablePressure && !s.pressureSegments.length) throw new Error("variable pressure requires an explicit pressure schedule");
  if (s.peakVo2MlKgMin < s.meanVo2MlKgMin) throw new Error("peak VO2 must be at least mean VO2");
  return s;
}

export function missionRules(profile = "default"): MissionRules {
  if (!Object.hasOwn(profiles, profile)) throw new Error(`Unknown mission-rule profile: ${profile}`);
  return profiles[profile as keyof typeof profiles];
}
