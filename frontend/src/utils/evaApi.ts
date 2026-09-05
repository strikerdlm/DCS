import type {
  EVAReportFormat,
  EVAReportResponse,
  EVAScenario,
  EVASimulationApiResponse,
  EVATelemetrySample,
} from "../types";
import { simulateEVA, EVA_MODEL_VERSION, missionRules } from "./eva";
import type { EVAOptions } from "./eva";

const env = import.meta.env as Record<string, string | undefined>;

export const EVA_API_BASE_URL = env.VITE_TINYDCS_API_URL ?? "http://127.0.0.1:8180/api/v2";

export class EVAApiError extends Error {
  readonly status: number;
  constructor(status: number, detail: string) { super(`TinyDCS API ${status}: ${detail}`); this.status = status; }
}

/** A transport failure permits offline use. HTTP/schema errors must not be masked. */
export function canUseOffline(error: unknown): boolean {
  return error instanceof TypeError;
}

export function responseForInputs<T>(inputKey: string, state: { key: string; response?: T } | null): T | undefined {
  return state?.key === inputKey ? state.response : undefined;
}

function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value !== null && typeof value === "object") return `{${Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([k,v]) => `${JSON.stringify(k)}:${canonical(v)}`).join(",")}}`;
  return JSON.stringify(value);
}

function validateServerContext(response: EVASimulationApiResponse, profile?: string): void {
  if (!response || response.schemaVersion !== 2 || response.result?.schemaVersion !== 2 || response.modelMetadata?.modelVersion !== EVA_MODEL_VERSION)
    throw new EVAApiError(502, "Incompatible scientific contract; update the API.");
  if (canonical(response.missionRules) !== canonical(missionRules(profile)))
    throw new EVAApiError(409, "Server mission rules differ from the browser bundle. Regenerate the browser rules before comparing results.");
}

async function postJson<T>(path: string, payload: unknown, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${EVA_API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new EVAApiError(response.status, detail || response.statusText);
  }
  return (await response.json()) as T;
}

export async function simulateEVAApi(
  scenario: EVAScenario,
  options: {
    missionRuleProfile?: string;
    telemetry?: EVATelemetrySample[];
    telemetryNowSec?: number;
    signal?: AbortSignal;
  } = {},
): Promise<EVASimulationApiResponse> {
  const response = await postJson<EVASimulationApiResponse>(
    "/eva/simulate",
    {
      scenario,
      missionRuleProfile: options.missionRuleProfile ?? "default",
      telemetry: options.telemetry ?? [],
      telemetryNowSec: options.telemetryNowSec,
    },
    options.signal,
  );
  validateServerContext(response, options.missionRuleProfile);
  return response;
}

export async function createEVAReport(
  scenario: EVAScenario,
  options: {
    missionRuleProfile?: string;
    telemetry?: EVATelemetrySample[];
    telemetryNowSec?: number;
    signal?: AbortSignal;
  } = {},
): Promise<EVAReportResponse> {
  const report = await postJson<EVAReportResponse>(
    "/eva/report",
    {
      scenario,
      missionRuleProfile: options.missionRuleProfile ?? "default",
      telemetry: options.telemetry ?? [],
      telemetryNowSec: options.telemetryNowSec,
    },
    options.signal,
  );
  let payload: EVASimulationApiResponse;
  try {
    payload = JSON.parse(report.artifacts.json.content ?? "");
  } catch {
    throw new EVAApiError(502, "Incompatible report contract; missing JSON provenance.");
  }
  validateServerContext(payload, options.missionRuleProfile);
  return report;
}

function base64ToBlob(base64: string, mimeType: string): Blob {
  const byteCharacters = atob(base64);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i += 1) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  return new Blob([new Uint8Array(byteNumbers)], { type: mimeType });
}

export function downloadReportArtifact(report: EVAReportResponse, format: EVAReportFormat): void {
  const artifact = report.artifacts[format];
  if (!artifact) {
    throw new Error(`Report artifact missing: ${format}`);
  }
  const blob =
    artifact.contentBase64 !== undefined
      ? base64ToBlob(artifact.contentBase64, artifact.mimeType)
      : new Blob([artifact.content ?? ""], { type: artifact.mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = artifact.filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function downloadLocalScenarioJson(
  scenario: EVAScenario,
  options: EVAOptions,
): void {
  const payload = localScenarioReport(scenario, options);
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `eva-${scenario.id}-browser-reference.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function localScenarioReport(scenario: EVAScenario, options: EVAOptions) {
  const telemetryNowSec = options.telemetryNowSec ?? Date.now() / 1000;
  return {
    schemaVersion: 2,
    modelVersion: EVA_MODEL_VERSION,
    generatedAt: new Date().toISOString(),
    scenarioId: scenario.id,
    scenario,
    missionRuleProfile: options.missionRuleProfile ?? "default",
    missionRules: missionRules(options.missionRuleProfile),
    telemetry: options.telemetry ?? [],
    telemetryNowSec,
    result: simulateEVA(scenario, { ...options, telemetryNowSec }),
    source: "browser-reference",
    researchUseOnly: true,
  };
}
