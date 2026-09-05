import type { EVAScenario, EVASimulationResult, EVATelemetrySample } from "../types";
import type { MissionRules } from "./evaContract";

const PSIA_PER_ATM = 14.695948775513449;
const KPA_PER_PSIA = 6.894757293168;
const MMHG_PER_PSIA = 760 / PSIA_PER_ATM;
type Normalized = {kind: string; value: number; unit: string; source: string; confidence: number; timestampSec: number | null};
const numeric = (v: unknown): number | null => typeof v === "number" && Number.isFinite(v) ? v : null;

export function normalizeSample(s: EVATelemetrySample): Normalized | null {
  let kind: string = s.kind.toLowerCase(), unit = (s.unit ?? "").toLowerCase(), value = numeric(s.value);
  const confidence = numeric(s.confidence ?? 1), timestampSec = numeric(s.timestampSec);
  if (confidence === null || confidence < 0 || confidence > 1) return null;
  if (["pressure", "suit_pressure", "habitat_pressure"].includes(kind)) {
    const factors: Record<string, number> = { psia: 1, kpa: 1 / KPA_PER_PSIA, mmhg: 1 / MMHG_PER_PSIA, torr: 1 / MMHG_PER_PSIA, atm: PSIA_PER_ATM };
    if (value === null || !Object.hasOwn(factors, unit)) return null;
    value *= factors[unit]; unit = "psia";
    if (!(value > 0 && value <= 30)) return null;
  } else if (kind === "workload") {
    if (value === null || !["vo2_ml_kg_min", "ml/kg/min", "vo2"].includes(unit) || value < 0 || value > 120) return null;
    unit = "mL/kg/min";
  } else if (["activity", "accelerometer"].includes(kind)) {
    if (["cpm", "counts_per_min"].includes(unit) && value !== null && value >= 0) { kind = "activity_counts"; unit = "counts/min"; }
    else if (["g", "mg", "milli-g", "millig"].includes(unit)) {
      const xyz = [numeric(s.x), numeric(s.y), numeric(s.z)];
      if (xyz.some(x => x === null)) return null;
      value = Math.hypot(...xyz as number[]) / (unit === "g" ? 1 : 1000); kind = "acceleration_magnitude"; unit = "g";
    } else return null;
  } else if (["hr", "heart_rate"].includes(kind)) {
    if (value === null || unit !== "bpm" || value <= 0 || value > 300) return null;
    kind = "heart_rate";
  } else if (kind === "hrv") {
    if (value === null || !["rmssd_ms", "ms"].includes(unit) || value < 0 || value > 1000) return null;
    unit = "rmssd_ms";
  } else if (kind === "spo2") {
    if (value === null || !["%", "percent", "fraction"].includes(unit)) return null;
    if (unit === "fraction") value *= 100;
    if (value < 0 || value > 100) return null;
    unit = "percent";
  } else if (["skin_temperature", "skin_temp", "temperature"].includes(kind)) {
    if (value === null) return null;
    if (["f", "fahrenheit", "degf"].includes(unit)) value = (value - 32) * 5 / 9;
    else if (!["c", "celsius", "degc"].includes(unit)) return null;
    if (value < 0 || value > 60) return null;
    kind = "skin_temperature"; unit = "celsius";
  } else return null;
  if (value === null || !Number.isFinite(value)) return null;
  return { kind, value, unit, source: s.source || "unspecified", confidence, timestampSec };
}

export function applyTelemetry(s: EVAScenario, samples: EVATelemetrySample[], rules: MissionRules, now = Date.now() / 1000): NonNullable<EVASimulationResult["telemetryStatus"]> {
  if (!Number.isFinite(now)) throw new Error("finite telemetry reference time required");
  if (samples.length > 5000) throw new Error("too many telemetry samples");
  const status: NonNullable<EVASimulationResult["telemetryStatus"]> = { accepted: 0, rejected: 0, warnings: [], suitPressurePsia: null, habitatPressurePsia: null, meanVo2MlKgMin: null, peakVo2MlKgMin: null, spo2Percent: null, heartRateBpm: null, hrvRmssdMs: null, skinTempC: null, rawIndicators: [] };
  const latest: Record<string, Normalized> = {}, workloads: number[] = [];
  for (const raw of samples) {
    const n = normalizeSample(raw);
    let warning: string | undefined;
    if (!n) warning = `Unsupported or malformed telemetry sample: ${raw.kind ?? "unknown"}`;
    else if (n.confidence < rules.telemetry.min_confidence) warning = `Low-confidence telemetry sample ignored: ${n.kind}`;
    else if (n.timestampSec === null || now - n.timestampSec < 0 || now - n.timestampSec > rules.telemetry.max_sample_age_sec) warning = `Unverified timestamp, stale or future telemetry ignored: ${n.kind}`;
    if (warning) { status.rejected++; status.warnings.push(warning); continue; }
    if (!n || n.timestampSec === null) continue;
    status.accepted++;
    const kind = n.kind === "pressure" ? `${rules.telemetry.pressure_source}_pressure` : n.kind;
    if (!latest[kind] || n.timestampSec >= latest[kind].timestampSec!) latest[kind] = n;
    status.rawIndicators!.push({ kind, value: n.value, unit: n.unit, source: n.source, timestampSec: n.timestampSec });
    if (kind === "workload") workloads.push(n.value);
  }
  status.suitPressurePsia = latest.suit_pressure?.value ?? null;
  status.habitatPressurePsia = latest.habitat_pressure?.value ?? null;
  status.spo2Percent = latest.spo2?.value ?? null;
  status.heartRateBpm = latest.heart_rate?.value ?? null;
  status.hrvRmssdMs = latest.hrv?.value ?? null;
  status.skinTempC = latest.skin_temperature?.value ?? null;
  if (status.suitPressurePsia !== null) {
    if (s.pressureSegments?.length) status.warnings.push("Pressure snapshot displayed; explicit mission pressure schedule retained.");
    else s.suit.pressurePsia = status.suitPressurePsia;
  }
  if (status.habitatPressurePsia !== null) s.habitat.pressurePsia = status.habitatPressurePsia;
  if (status.spo2Percent !== null) s.crew.spo2Percent = status.spo2Percent;
  if (workloads.length) {
    status.meanVo2MlKgMin = workloads.reduce((a, b) => a + b, 0) / workloads.length;
    status.peakVo2MlKgMin = Math.max(...workloads);
    status.warnings.push("Measured VO2 samples displayed; a snapshot does not replace the mission workload schedule.");
  }
  if (latest.acceleration_magnitude || latest.activity_counts) status.warnings.push("Acceleration/activity remains a raw indicator; no validated VO2 conversion supplied.");
  return status;
}
