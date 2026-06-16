import type {
  EVAReportFormat,
  EVAReportResponse,
  EVAScenario,
  EVASimulationApiResponse,
  EVASimulationResult,
  EVATelemetrySample,
} from "../types";

const env = import.meta.env as Record<string, string | undefined>;

export const EVA_API_BASE_URL = env.VITE_TINYDCS_API_URL ?? "http://127.0.0.1:8180/api/v1";

async function postJson<T>(path: string, payload: unknown, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${EVA_API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`TinyDCS API ${response.status}: ${detail || response.statusText}`);
  }
  return (await response.json()) as T;
}

export function simulateEVAApi(
  scenario: EVAScenario,
  options: {
    missionRuleProfile?: string;
    telemetry?: EVATelemetrySample[];
    signal?: AbortSignal;
  } = {},
): Promise<EVASimulationApiResponse> {
  return postJson<EVASimulationApiResponse>(
    "/eva/simulate",
    {
      scenario,
      missionRuleProfile: options.missionRuleProfile ?? "default",
      telemetry: options.telemetry ?? [],
    },
    options.signal,
  );
}

export function createEVAReport(
  scenario: EVAScenario,
  result: EVASimulationResult,
  options: {
    missionRuleProfile?: string;
    telemetry?: EVATelemetrySample[];
    signal?: AbortSignal;
  } = {},
): Promise<EVAReportResponse> {
  return postJson<EVAReportResponse>(
    "/eva/report",
    {
      scenario,
      result,
      missionRuleProfile: options.missionRuleProfile ?? "default",
      telemetry: options.telemetry ?? [],
    },
    options.signal,
  );
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
  result: EVASimulationResult,
  missionRuleProfile: string,
): void {
  const payload = {
    generatedAt: new Date().toISOString(),
    scenarioId: scenario.id,
    missionRuleProfile,
    result,
    source: "browser-fallback",
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `eva-${scenario.id}-browser-fallback.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
