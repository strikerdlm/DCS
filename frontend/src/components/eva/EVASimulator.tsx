import React, { useEffect, useMemo, useState } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
import {
  Activity,
  AlertTriangle,
  BatteryCharging,
  Clock,
  Download,
  Gauge,
  GitCompare,
  Link2,
  Moon,
  Radio,
  Server,
  ShieldAlert,
  Thermometer,
  UserRound,
  Wind,
} from "lucide-react";
import { RiskGauge } from "../charts/RiskGauge";
import { chartTheme, colorPalettes, getBaseChartOptions, withAlpha } from "../charts/chartConfig";
import { Button } from "../ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/Select";
import { Slider } from "../ui/Slider";
import { Switch } from "../ui/Switch";
import { EVA_EVIDENCE_LINKS, EVA_SCENARIOS } from "../../data/evaScenarios";
import { cn, formatNumber } from "../../lib/utils";
import {
  cloneScenario,
  psiaToKpa,
  simulateEVA,
} from "../../utils/eva";
import {
  createEVAReport,
  downloadLocalScenarioJson,
  downloadReportArtifact,
  EVA_API_BASE_URL,
  simulateEVAApi,
} from "../../utils/evaApi";
import type {
  EVADecisionImplication,
  EVAReportFormat,
  EVAScenario,
  EVASimulationApiResponse,
  EVASimulationResult,
  EVATelemetrySample,
  EVATimelinePoint,
  RadiationWeather,
  RiskConsequenceLevel,
  RiskLikelihoodLevel,
  RiskMatrixHazard,
} from "../../types";

const LIKELIHOOD_LABELS: Record<RiskLikelihoodLevel, string> = {
  1: "Remote",
  2: "Unlikely",
  3: "Possible",
  4: "Likely",
  5: "Frequent",
};

const CONSEQUENCE_LABELS: Record<RiskConsequenceLevel, string> = {
  1: "Minimal",
  2: "Minor",
  3: "Moderate",
  4: "Critical",
  5: "Catastrophic",
};

const POSTURE_CLASS: Record<RiskMatrixHazard["posture"], string> = {
  green: "bg-emerald-500/12 text-emerald-700 dark:text-emerald-300 border-emerald-500/25",
  yellow: "bg-amber-500/12 text-amber-700 dark:text-amber-300 border-amber-500/25",
  orange: "bg-orange-500/12 text-orange-700 dark:text-orange-300 border-orange-500/25",
  red: "bg-red-500/12 text-red-700 dark:text-red-300 border-red-500/25",
};

const DECISION_CLASS: Record<EVADecisionImplication, string> = {
  proceed: "bg-emerald-500/12 text-emerald-700 dark:text-emerald-300 border-emerald-500/25",
  monitor: "bg-sky-500/12 text-sky-700 dark:text-sky-300 border-sky-500/25",
  modify: "bg-amber-500/12 text-amber-700 dark:text-amber-300 border-amber-500/25",
  delay: "bg-orange-500/12 text-orange-700 dark:text-orange-300 border-orange-500/25",
  abort: "bg-red-500/12 text-red-700 dark:text-red-300 border-red-500/25",
  abstain: "bg-zinc-500/12 text-zinc-700 dark:text-zinc-300 border-zinc-500/25",
};

function updateScenario(
  scenario: EVAScenario,
  mutator: (draft: EVAScenario) => void,
): EVAScenario {
  const next = cloneScenario(scenario);
  mutator(next);
  return next;
}

function pressureToAltitudeLabel(psia: number): string {
  const atm = psia / 14.7;
  if (atm >= 1) return "sea-level cabin";
  const altitudeFt = (1 - Math.pow(atm, 1 / 5.2559)) / 6.87535e-6;
  return `${Math.round(altitudeFt / 100) * 100} ft equiv.`;
}

function postureLabel(posture: RiskMatrixHazard["posture"]): string {
  if (posture === "green") return "Controlled";
  if (posture === "yellow") return "Watch";
  if (posture === "orange") return "Mitigate";
  return "No-go";
}

function decisionLabel(decision: EVADecisionImplication): string {
  return decision.charAt(0).toUpperCase() + decision.slice(1);
}

function PressureTimelineChart({
  data,
}: {
  data: EVATimelinePoint[];
}): React.ReactElement {
  const option: EChartsOption = useMemo(
    () => ({
      ...getBaseChartOptions(),
      grid: { left: 54, right: 48, top: 36, bottom: 46, containLabel: true },
      tooltip: {
        ...getBaseChartOptions().tooltip,
        trigger: "axis",
        formatter: (params: unknown) => {
          const rows = params as Array<{ marker: string; seriesName: string; value: [number, number] }>;
          if (!Array.isArray(rows) || rows.length === 0) return "";
          const t = rows[0].value[0];
          return [
            `<strong>${t.toFixed(0)} min</strong>`,
            ...rows.map(
              (row) =>
                `${row.marker}${row.seriesName}: <span class="font-mono">${formatNumber(row.value[1], 2)}</span>`,
            ),
          ].join("<br/>");
        },
      },
      legend: {
        top: 0,
        right: 0,
        textStyle: { color: chartTheme.textColor, fontSize: 11 },
      },
      xAxis: {
        type: "value",
        name: "Mission time (min)",
        axisLabel: { color: chartTheme.axisColor, fontSize: 11 },
        splitLine: { lineStyle: { color: chartTheme.gridColor, type: "dashed" } },
      },
      yAxis: [
        {
          type: "value",
          name: "Pressure (psia)",
          axisLabel: { color: chartTheme.axisColor, fontSize: 11 },
          splitLine: { lineStyle: { color: chartTheme.gridColor, type: "dashed" } },
        },
        {
          type: "value",
          name: "P(DCS) %",
          axisLabel: { color: chartTheme.axisColor, fontSize: 11 },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: "Ambient",
          type: "line",
          step: "end",
          symbol: "none",
          data: data.map((p) => [p.timeMin, p.ambientPressurePsia]),
          lineStyle: { width: 3, color: chartTheme.primaryColor },
          areaStyle: { color: withAlpha(chartTheme.primaryColor, 0.1) },
        },
        {
          name: "Tissue N2",
          type: "line",
          smooth: 0.25,
          symbol: "none",
          data: data.map((p) => [p.timeMin, p.tissueN2Psia]),
          lineStyle: { width: 2, color: colorPalettes.scientific[2] },
        },
        {
          name: "95% low",
          type: "line",
          yAxisIndex: 1,
          smooth: 0.25,
          symbol: "none",
          data: data.map((p) => [p.timeMin, p.intervalLowPercent]),
          lineStyle: {
            width: 1.5,
            type: "dashed",
            color: withAlpha(chartTheme.riskModerateColor, 0.72),
          },
        },
        {
          name: "P(DCS)",
          type: "line",
          yAxisIndex: 1,
          smooth: 0.25,
          symbol: "none",
          data: data.map((p) => [p.timeMin, p.cumulativePDcsPercent]),
          lineStyle: { width: 2, color: chartTheme.riskHighColor },
        },
        {
          name: "95% high",
          type: "line",
          yAxisIndex: 1,
          smooth: 0.25,
          symbol: "none",
          data: data.map((p) => [p.timeMin, p.intervalHighPercent]),
          lineStyle: {
            width: 1.5,
            type: "dashed",
            color: withAlpha(chartTheme.riskHighColor, 0.72),
          },
          areaStyle: { color: withAlpha(chartTheme.riskHighColor, 0.07) },
        },
      ],
    }),
    [data],
  );

  return (
    <ReactECharts
      option={option}
      notMerge
      style={{ height: 320, width: "100%" }}
      opts={{ renderer: "canvas" }}
    />
  );
}

function WorkloadStrip({ scenario }: { scenario: EVAScenario }): React.ReactElement {
  const total = Math.max(
    1,
    scenario.workload.reduce((sum, block) => sum + block.durationMin, 0),
  );
  return (
    <div className="space-y-3">
      <div className="h-14 rounded-lg overflow-hidden border border-border/70 bg-muted flex">
        {scenario.workload.map((block, i) => {
          const width = `${(block.durationMin / total) * 100}%`;
          const intensity = Math.min(1, block.vo2MlKgMin / Math.max(scenario.peakVo2MlKgMin, 1));
          return (
            <div
              key={`${block.name}-${i}`}
              className="relative min-w-[48px] border-r last:border-r-0 border-background/60"
              style={{
                width,
                background: `linear-gradient(180deg, ${withAlpha(
                  colorPalettes.scientific[i % colorPalettes.scientific.length],
                  0.22 + intensity * 0.42,
                )}, ${withAlpha(colorPalettes.scientific[i % colorPalettes.scientific.length], 0.08)})`,
              }}
            >
              <div className="absolute inset-x-2 top-2">
                <p className="text-[10px] font-semibold leading-tight truncate">{block.name}</p>
                <p className="text-num text-[10px] text-muted-foreground">
                  {block.durationMin}m / {block.vo2MlKgMin}
                </p>
              </div>
            </div>
          );
        })}
      </div>
      <div className="grid grid-cols-3 gap-2 text-[11px] text-muted-foreground">
        <span>Mean {scenario.meanVo2MlKgMin.toFixed(0)} mL/kg/min</span>
        <span className="text-center">Peak {scenario.peakVo2MlKgMin.toFixed(0)} mL/kg/min</span>
        <span className="text-right">{scenario.evaDurationMin} min EVA</span>
      </div>
    </div>
  );
}

function RiskMatrix({
  hazards,
  selectedId,
  onSelect,
}: {
  hazards: RiskMatrixHazard[];
  selectedId: string;
  onSelect: (id: string) => void;
}): React.ReactElement {
  const rows: RiskLikelihoodLevel[] = [5, 4, 3, 2, 1];
  const cols: RiskConsequenceLevel[] = [1, 2, 3, 4, 5];
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-[78px_repeat(5,minmax(46px,1fr))] gap-1 text-[10px]">
        <div />
        {cols.map((col) => (
          <div key={col} className="text-center text-muted-foreground truncate">
            {CONSEQUENCE_LABELS[col]}
          </div>
        ))}
        {rows.map((row) => (
          <React.Fragment key={row}>
            <div className="h-16 flex items-center text-muted-foreground">
              {LIKELIHOOD_LABELS[row]}
            </div>
            {cols.map((col) => {
              const cellHazards = hazards.filter(
                (hazard) => hazard.likelihood === row && hazard.consequence === col,
              );
              const score = row * col;
              const tone =
                score <= 4
                  ? "bg-emerald-500/10 border-emerald-500/25"
                  : score <= 9
                    ? "bg-amber-500/12 border-amber-500/25"
                    : score <= 15
                      ? "bg-orange-500/14 border-orange-500/30"
                      : "bg-red-500/14 border-red-500/35";
              return (
                <button
                  key={`${row}-${col}`}
                  className={cn(
                    "h-16 rounded-md border p-1.5 transition-all hover:ring-2 hover:ring-primary/30",
                    tone,
                    cellHazards.some((h) => h.id === selectedId) && "ring-2 ring-primary/60",
                  )}
                  onClick={() => cellHazards[0] && onSelect(cellHazards[0].id)}
                  type="button"
                >
                  <div className="h-full flex flex-wrap content-start gap-1">
                    {cellHazards.map((hazard) => (
                      <span
                        key={hazard.id}
                        className={cn(
                          "h-5 min-w-5 px-1 rounded text-[9px] font-semibold flex items-center justify-center border",
                          POSTURE_CLASS[hazard.posture],
                        )}
                        title={hazard.name}
                      >
                        {hazard.name
                          .split(" ")
                          .map((part) => part[0])
                          .join("")
                          .slice(0, 3)}
                      </span>
                    ))}
                  </div>
                </button>
              );
            })}
          </React.Fragment>
        ))}
      </div>
      <div className="grid grid-cols-5 gap-1 pl-[82px] text-[10px] text-muted-foreground">
        <span className="col-span-5 text-center">Consequence</span>
      </div>
    </div>
  );
}

function MitigationTable({ scenario }: { scenario: EVAScenario }): React.ReactElement {
  const rows = useMemo(() => {
    const options: Array<{ label: string; scenario: EVAScenario }> = [
      { label: "Scheduled now", scenario },
      {
        label: "Delay: +120 min PB",
        scenario: updateScenario(scenario, (d) => {
          d.prebreatheMin += 120;
        }),
      },
      {
        label: "Alter habitat 8.2/34%",
        scenario: updateScenario(scenario, (d) => {
          d.habitat.pressurePsia = 8.2;
          d.habitat.oxygenFraction = 0.34;
          d.habitat.equilibrationHours = Math.max(d.habitat.equilibrationHours, 24);
          d.prebreatheMin = Math.max(d.prebreatheMin, 30);
        }),
      },
      {
        label: "+1 psia suit",
        scenario: updateScenario(scenario, (d) => {
          d.suit.pressurePsia = Math.min(8.2, d.suit.pressurePsia + 1);
        }),
      },
      {
        label: "Shorten EVA -60",
        scenario: updateScenario(scenario, (d) => {
          d.evaDurationMin = Math.max(60, d.evaDurationMin - 60);
        }),
      },
      {
        label: "-20% peak VO2",
        scenario: updateScenario(scenario, (d) => {
          d.peakVo2MlKgMin = Math.max(d.meanVo2MlKgMin, d.peakVo2MlKgMin * 0.8);
        }),
      },
    ];
    return options.map((option) => ({
      label: option.label,
      result: simulateEVA(option.scenario),
    }));
  }, [scenario]);
  const baseline = rows[0].result.pDcsPercent;

  return (
    <div className="space-y-2">
      {rows.map((row) => {
        const delta = row.result.pDcsPercent - baseline;
        return (
          <div
            key={row.label}
            className="grid grid-cols-[1fr_70px_62px_72px] gap-3 items-center rounded-lg border border-border/70 bg-background/45 px-3 py-2"
          >
            <span className="text-[12px] font-medium truncate">{row.label}</span>
            <span className="text-num text-[12px] text-right">{row.result.pDcsPercent.toFixed(2)}%</span>
            <span
              className={cn(
                "text-num text-[12px] text-right",
                delta <= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400",
              )}
            >
              {delta > 0 ? "+" : ""}
              {delta.toFixed(2)}
            </span>
            <span
              className={cn(
                "text-[10px] uppercase tracking-[0.12em] text-center rounded border px-1.5 py-1",
                DECISION_CLASS[row.result.decision],
              )}
            >
              {row.result.decision}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function EvidencePanel({ scenario }: { scenario: EVAScenario }): React.ReactElement {
  return (
    <Card variant="glass">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Link2 className="h-4 w-4 text-primary" />
          Evidence Trace
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          {scenario.evidence.map((item) => (
            <div key={item} className="flex items-start gap-2 text-[12px] text-muted-foreground">
              <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
              <span>{item}</span>
            </div>
          ))}
        </div>
        <div className="flex flex-wrap gap-2 pt-2 border-t border-border/60">
          {EVA_EVIDENCE_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              target="_blank"
              rel="noreferrer"
              className="pill-muted hover:text-primary transition-colors"
            >
              {link.label}
            </a>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function NumberTile({
  icon,
  label,
  value,
  detail,
  tone = "default",
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  detail: string;
  tone?: "default" | "amber" | "red" | "green";
}): React.ReactElement {
  const toneClass =
    tone === "amber"
      ? "text-amber-600 bg-amber-500/12"
      : tone === "red"
        ? "text-red-600 bg-red-500/12"
        : tone === "green"
          ? "text-emerald-600 bg-emerald-500/12"
          : "text-primary bg-primary/12";
  return (
    <div className="surface p-4 min-w-0">
      <div className="flex items-center gap-3">
        <div className={cn("h-9 w-9 rounded-lg flex items-center justify-center shrink-0", toneClass)}>
          {icon}
        </div>
        <div className="min-w-0">
          <p className="text-[10px] uppercase tracking-[0.14em] text-muted-foreground truncate">
            {label}
          </p>
          <p className="text-num text-[18px] font-semibold leading-tight truncate">{value}</p>
        </div>
      </div>
      <p className="text-[11px] text-muted-foreground mt-3 leading-snug">{detail}</p>
    </div>
  );
}

function DecisionPanel({
  result,
}: {
  result: EVASimulationResult;
}): React.ReactElement {
  return (
    <div className={cn("rounded-xl border p-4", DECISION_CLASS[result.decision])}>
      <div className="grid lg:grid-cols-[180px_1fr] gap-4 items-start">
        <div>
          <p className="text-[10px] uppercase tracking-[0.16em] opacity-75">
            Decision implication
          </p>
          <p className="display text-2xl font-bold mt-1">{decisionLabel(result.decision)}</p>
        </div>
        <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-3">
          <div>
            <p className="text-[10px] uppercase tracking-[0.14em] opacity-75">Envelope</p>
            <p className="text-sm font-semibold">
              {result.inEnvelope ? "In-envelope" : "Abstain"}
            </p>
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-[0.14em] opacity-75">Max risk</p>
            <p className="text-num text-sm font-semibold">
              {result.maxRiskPercent.toFixed(2)}% @ {result.maxRiskTimeMin.toFixed(0)} min
            </p>
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-[0.14em] opacity-75">Integrated risk</p>
            <p className="text-num text-sm font-semibold">
              {result.integratedRiskPercentHours.toFixed(2)} %-h
            </p>
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-[0.14em] opacity-75">LxC</p>
            <p className="text-num text-sm font-semibold">
              {result.lxcLikelihood} x {result.lxcConsequence} = {result.lxcScore}
            </p>
          </div>
        </div>
      </div>
      <p className="text-[12px] mt-3 leading-relaxed">{result.decisionRationale}</p>
    </div>
  );
}

export function EVASimulator(): React.ReactElement {
  const [scenario, setScenario] = useState<EVAScenario>(() => cloneScenario(EVA_SCENARIOS[1]));
  const [missionRuleProfile, setMissionRuleProfile] = useState("artemis_lunar");
  const [telemetryReplay, setTelemetryReplay] = useState(false);
  const telemetrySamples = useMemo<EVATelemetrySample[]>(
    () =>
      telemetryReplay
        ? [
            {
              kind: "pressure",
              value: scenario.suit.pressurePsia,
              unit: "psia",
              source: "tablet-replay-pressure",
              confidence: 0.96,
            },
            {
              kind: "workload",
              value: scenario.peakVo2MlKgMin,
              unit: "vo2_ml_kg_min",
              source: "tablet-replay-accelerometer",
              confidence: 0.88,
            },
            {
              kind: "heart_rate",
              value: Math.round(72 + scenario.meanVo2MlKgMin * 2.1),
              unit: "bpm",
              source: "tablet-replay-hr",
              confidence: 0.86,
            },
            {
              kind: "hrv",
              value: Math.max(18, 62 - scenario.meanVo2MlKgMin),
              unit: "rmssd_ms",
              source: "tablet-replay-hrv",
              confidence: 0.82,
            },
            {
              kind: "spo2",
              value: scenario.crew.spo2Percent,
              unit: "%",
              source: "tablet-replay-spo2",
              confidence: 0.92,
            },
            {
              kind: "skin_temperature",
              value: 33.5 + scenario.environment.sunExposure * 2,
              unit: "c",
              source: "tablet-replay-skin-temp",
              confidence: 0.84,
            },
          ]
        : [],
    [scenario, telemetryReplay],
  );
  const localResult = useMemo(() => simulateEVA(scenario), [scenario]);
  const [apiResponse, setApiResponse] = useState<EVASimulationApiResponse | null>(null);
  const [apiStatus, setApiStatus] = useState<"idle" | "loading" | "online" | "fallback">("idle");
  const [apiError, setApiError] = useState<string | null>(null);
  const [reportFormat, setReportFormat] = useState<EVAReportFormat | null>(null);
  const result = apiResponse?.result ?? localResult;
  const [selectedHazardId, setSelectedHazardId] = useState("dcs");
  const selectedHazard =
    result.hazards.find((hazard) => hazard.id === selectedHazardId) ?? result.hazards[0];

  useEffect(() => {
    const controller = new AbortController();
    const handle = window.setTimeout(() => {
      setApiStatus("loading");
      simulateEVAApi(scenario, {
        missionRuleProfile,
        telemetry: telemetrySamples,
        signal: controller.signal,
      })
        .then((response) => {
          setApiResponse(response);
          setApiStatus("online");
          setApiError(null);
        })
        .catch((error: unknown) => {
          if (controller.signal.aborted) return;
          setApiResponse(null);
          setApiStatus("fallback");
          setApiError(error instanceof Error ? error.message : "TinyDCS API unavailable");
        });
    }, 250);
    return () => {
      controller.abort();
      window.clearTimeout(handle);
    };
  }, [missionRuleProfile, scenario, telemetrySamples]);

  const setPreset = (id: string) => {
    const preset = EVA_SCENARIOS.find((item) => item.id === id);
    if (!preset) return;
    setScenario(cloneScenario(preset));
    setSelectedHazardId("dcs");
  };

  const patch = (mutator: (draft: EVAScenario) => void) => {
    setScenario((current) => updateScenario(current, mutator));
  };

  const exportReport = async (format: EVAReportFormat) => {
    setReportFormat(format);
    try {
      const report = await createEVAReport(scenario, result, {
        missionRuleProfile,
        telemetry: telemetrySamples,
      });
      downloadReportArtifact(report, format);
    } catch (error) {
      if (format === "json") {
        downloadLocalScenarioJson(scenario, result, missionRuleProfile);
      } else {
        setApiError(error instanceof Error ? error.message : "Report export requires the TinyDCS API");
      }
    } finally {
      setReportFormat(null);
    }
  };

  return (
    <div className="space-y-6">
      <section className="surface-elevated overflow-hidden">
        <div className="grid xl:grid-cols-[1.25fr_0.75fr] gap-0">
          <div className="p-6 lg:p-7 border-b xl:border-b-0 xl:border-r border-border/70">
            <div className="flex flex-wrap items-center gap-2 mb-4">
              <span className="pill-primary">
                <Moon className="h-3.5 w-3.5" />
                EVA Mission Simulator
              </span>
              <span className={cn("pill border", DECISION_CLASS[result.decision])}>
                {decisionLabel(result.decision)}
              </span>
              <span className={cn("pill border", POSTURE_CLASS[result.lxcCategory])}>
                DCS LxC {postureLabel(result.lxcCategory)}
              </span>
              <span className="pill-muted">{scenario.shortName}</span>
              <span
                className={cn(
                  "pill border",
                  apiStatus === "online"
                    ? "bg-emerald-500/12 text-emerald-700 dark:text-emerald-300 border-emerald-500/25"
                    : apiStatus === "loading"
                      ? "bg-sky-500/12 text-sky-700 dark:text-sky-300 border-sky-500/25"
                      : "bg-amber-500/12 text-amber-700 dark:text-amber-300 border-amber-500/25",
                )}
                title={apiError ?? EVA_API_BASE_URL}
              >
                <Server className="h-3.5 w-3.5" />
                {apiStatus === "online" ? "Python API" : apiStatus === "loading" ? "Syncing" : "Browser fallback"}
              </span>
            </div>
            <div className="max-w-3xl">
              <h2 className="display text-3xl lg:text-4xl font-bold tracking-tight">
                DCS-informed EVA risk planning
              </h2>
              <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
                {scenario.summary}
              </p>
            </div>
            <div className="grid sm:grid-cols-2 2xl:grid-cols-4 gap-3 mt-6">
              <NumberTile
                icon={<Gauge className="h-4 w-4" />}
                label="ETR"
                value={result.etr.toFixed(2)}
                detail={`${result.p1n2Psia.toFixed(2)} psia tissue N2 after prebreathe`}
                tone={result.etr > 1.4 ? "red" : result.etr > 1.1 ? "amber" : "green"}
              />
              <NumberTile
                icon={<Wind className="h-4 w-4" />}
                label="95% CI"
                value={`${result.intervalLowPercent.toFixed(2)}-${result.intervalHighPercent.toFixed(2)}%`}
                detail="Final timepoint interval around DCS point estimate"
              />
              <NumberTile
                icon={<BatteryCharging className="h-4 w-4" />}
                label="Max risk"
                value={`${result.maxRiskPercent.toFixed(2)}%`}
                detail={`Peak point risk at T+${result.maxRiskTimeMin.toFixed(0)} min`}
                tone={result.maxRiskPercent >= 10 ? "red" : result.maxRiskPercent >= 1 ? "amber" : "green"}
              />
              <NumberTile
                icon={<Activity className="h-4 w-4" />}
                label="Risk integral"
                value={`${result.integratedRiskPercentHours.toFixed(2)} %-h`}
                detail="Area under the point-risk trajectory"
              />
            </div>
            <div className="flex flex-wrap items-center gap-2 mt-5">
              <Button
                size="sm"
                variant="outline"
                onClick={() => void exportReport("pdf")}
                disabled={reportFormat !== null}
              >
                <Download className="h-4 w-4" />
                PDF
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => void exportReport("html")}
                disabled={reportFormat !== null}
              >
                <Download className="h-4 w-4" />
                HTML
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => void exportReport("json")}
                disabled={reportFormat !== null}
              >
                <Download className="h-4 w-4" />
                JSON
              </Button>
              <span className="text-[11px] text-muted-foreground">
                {apiResponse?.modelMetadata.modelVersion ?? "local browser model"}
                {result.telemetryStatus ? ` · telemetry ${result.telemetryStatus.accepted}/${telemetrySamples.length}` : ""}
              </span>
            </div>
          </div>
          <div className="p-5 lg:p-6 bg-background/35">
            <RiskGauge value={result.pDcsPercent} title="Conkin-style P(DCS)" height={250} max={40} />
            <div className="grid grid-cols-2 gap-2 mt-3 text-[11px]">
              <div className="rounded-lg border border-border/70 bg-card/70 p-3">
                <p className="text-muted-foreground">Suit pressure</p>
                <p className="text-num font-semibold">
                  {scenario.suit.pressurePsia.toFixed(1)} psia
                </p>
                <p className="text-muted-foreground">{psiaToKpa(scenario.suit.pressurePsia).toFixed(0)} kPa</p>
              </div>
              <div className="rounded-lg border border-border/70 bg-card/70 p-3">
                <p className="text-muted-foreground">Pressure altitude</p>
                <p className="text-num font-semibold">
                  {pressureToAltitudeLabel(scenario.suit.pressurePsia)}
                </p>
                <p className="text-muted-foreground">suit equivalent</p>
              </div>
              <div className="rounded-lg border border-border/70 bg-card/70 p-3">
                <p className="text-muted-foreground">Habitat O2</p>
                <p className="text-num font-semibold">
                  {Math.round(result.habitatInspiredO2MmHg)} mmHg
                </p>
                <p className="text-muted-foreground">
                  {scenario.habitat.pressurePsia.toFixed(1)} psia /{" "}
                  {Math.round(scenario.habitat.oxygenFraction * 100)}%
                </p>
              </div>
              <div className="rounded-lg border border-border/70 bg-card/70 p-3">
                <p className="text-muted-foreground">Envelope</p>
                <p className="text-num font-semibold">
                  {result.inEnvelope ? "in" : "abstain"}
                </p>
                <p className="text-muted-foreground">DCS model flag</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <DecisionPanel result={result} />

      {result.envelopeWarnings.length > 0 && (
        <div className="rounded-xl border-l-2 border-amber-500 bg-amber-500/8 pl-4 pr-3 py-3 flex items-start gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
          <div className="text-[12.5px] text-amber-800 dark:text-amber-200 space-y-1">
            {result.envelopeWarnings.map((warning) => (
              <p key={warning}>{warning}</p>
            ))}
          </div>
        </div>
      )}

      <div className="grid 2xl:grid-cols-[360px_minmax(0,1fr)] gap-6">
        <aside className="space-y-4">
          <Card variant="glass">
            <CardHeader>
              <CardTitle>Scenario</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Select value={scenario.id} onValueChange={setPreset}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {EVA_SCENARIOS.map((preset) => (
                    <SelectItem key={preset.id} value={preset.id}>
                      {preset.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <div className="grid grid-cols-2 gap-2">
                {EVA_SCENARIOS.map((preset) => (
                  <Button
                    key={preset.id}
                    variant={scenario.id === preset.id ? "default" : "outline"}
                    size="sm"
                    onClick={() => setPreset(preset.id)}
                    className="justify-start text-left h-auto py-2 whitespace-normal"
                  >
                    {preset.shortName}
                  </Button>
                ))}
              </div>
              <div className="space-y-1.5 border-t border-border/60 pt-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Mission-rule profile
                </label>
                <Select value={missionRuleProfile} onValueChange={setMissionRuleProfile}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">default</SelectItem>
                    <SelectItem value="commercial_standup">commercial_standup</SelectItem>
                    <SelectItem value="artemis_lunar">artemis_lunar</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Wind className="h-4 w-4 text-primary" />
                Atmosphere
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <Slider
                label="Habitat pressure"
                value={[scenario.habitat.pressurePsia]}
                onValueChange={([v]) => patch((d) => void (d.habitat.pressurePsia = v))}
                min={5}
                max={14.7}
                step={0.1}
                unit="psia"
                formatValue={(v) => v.toFixed(1)}
              />
              <Slider
                label="Habitat oxygen"
                value={[scenario.habitat.oxygenFraction * 100]}
                onValueChange={([v]) => patch((d) => void (d.habitat.oxygenFraction = v / 100))}
                min={20}
                max={40}
                step={1}
                unit="%"
              />
              <Slider
                label="Equilibration"
                value={[scenario.habitat.equilibrationHours]}
                onValueChange={([v]) => patch((d) => void (d.habitat.equilibrationHours = v))}
                min={1}
                max={72}
                step={1}
                unit="h"
              />
              <Slider
                label="Prebreathe"
                value={[scenario.prebreatheMin]}
                onValueChange={([v]) => patch((d) => void (d.prebreatheMin = v))}
                min={0}
                max={300}
                step={5}
                unit="min"
              />
              <Slider
                label="Prebreathe O2"
                value={[scenario.prebreatheOxygenFraction * 100]}
                onValueChange={([v]) => patch((d) => void (d.prebreatheOxygenFraction = v / 100))}
                min={21}
                max={100}
                step={1}
                unit="%"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 text-primary" />
                Suit and PLSS
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <Slider
                label="Suit pressure"
                value={[scenario.suit.pressurePsia]}
                onValueChange={([v]) => patch((d) => void (d.suit.pressurePsia = v))}
                min={3.7}
                max={8.2}
                step={0.1}
                unit="psia"
                formatValue={(v) => v.toFixed(1)}
              />
              <Slider
                label="PLSS duration"
                value={[scenario.suit.plssDurationMin]}
                onValueChange={([v]) => patch((d) => void (d.suit.plssDurationMin = v))}
                min={180}
                max={540}
                step={15}
                unit="min"
              />
              <Slider
                label="O2 reserve"
                value={[scenario.suit.oxygenReserveMin]}
                onValueChange={([v]) => patch((d) => void (d.suit.oxygenReserveMin = v))}
                min={0}
                max={90}
                step={5}
                unit="min"
              />
              <Slider
                label="CO2 scrubber margin"
                value={[scenario.suit.co2ScrubberMargin * 100]}
                onValueChange={([v]) => patch((d) => void (d.suit.co2ScrubberMargin = v / 100))}
                min={40}
                max={100}
                step={1}
                unit="%"
              />
              <Slider
                label="Cooling margin"
                value={[scenario.suit.coolingMargin * 100]}
                onValueChange={([v]) => patch((d) => void (d.suit.coolingMargin = v / 100))}
                min={40}
                max={100}
                step={1}
                unit="%"
              />
              <div className="space-y-3 border-t border-border/60 pt-4">
                <Switch
                  checked={scenario.suit.variablePressure}
                  onCheckedChange={(checked) =>
                    patch((d) => void (d.suit.variablePressure = checked))
                  }
                  label="Variable pressure"
                />
                <Switch
                  checked={scenario.suit.suitPort}
                  onCheckedChange={(checked) => patch((d) => void (d.suit.suitPort = checked))}
                  label="Suitport / rear entry"
                />
              </div>
            </CardContent>
          </Card>
        </aside>

        <main className="space-y-6 min-w-0">
          <div className="grid 2xl:grid-cols-[minmax(0,1fr)_360px] gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Gauge className="h-4 w-4 text-primary" />
                  Pressure and Tissue N2 Timeline
                </CardTitle>
              </CardHeader>
              <CardContent>
                <PressureTimelineChart data={result.timeline} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Thermometer className="h-4 w-4 text-primary" />
                  Surface Environment
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-5">
                <Slider
                  label="EVA duration"
                  value={[scenario.evaDurationMin]}
                  onValueChange={([v]) => patch((d) => void (d.evaDurationMin = v))}
                  min={30}
                  max={540}
                  step={15}
                  unit="min"
                />
                <Slider
                  label="Mean VO2"
                  value={[scenario.meanVo2MlKgMin]}
                  onValueChange={([v]) =>
                    patch((d) => {
                      d.meanVo2MlKgMin = v;
                      d.peakVo2MlKgMin = Math.max(d.peakVo2MlKgMin, v);
                    })
                  }
                  min={8}
                  max={35}
                  step={1}
                  unit="mL/kg/min"
                />
                <Slider
                  label="Peak VO2"
                  value={[scenario.peakVo2MlKgMin]}
                  onValueChange={([v]) =>
                    patch((d) => void (d.peakVo2MlKgMin = Math.max(v, d.meanVo2MlKgMin)))
                  }
                  min={10}
                  max={50}
                  step={1}
                  unit="mL/kg/min"
                />
                <Slider
                  label="Dust load"
                  value={[scenario.environment.dustLevel * 100]}
                  onValueChange={([v]) => patch((d) => void (d.environment.dustLevel = v / 100))}
                  min={0}
                  max={100}
                  step={1}
                  unit="%"
                />
                <Slider
                  label="Sun exposure"
                  value={[scenario.environment.sunExposure * 100]}
                  onValueChange={([v]) => patch((d) => void (d.environment.sunExposure = v / 100))}
                  min={0}
                  max={100}
                  step={1}
                  unit="%"
                />
                <div className="space-y-1.5">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Radiation weather
                  </label>
                  <Select
                    value={scenario.environment.radiationWeather}
                    onValueChange={(value) =>
                      patch((d) => void (d.environment.radiationWeather = value as RadiationWeather))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="quiet">quiet</SelectItem>
                      <SelectItem value="elevated">elevated</SelectItem>
                      <SelectItem value="storm">storm</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Slider
                  label="Shelter return"
                  value={[scenario.environment.shelterReturnMin]}
                  onValueChange={([v]) =>
                    patch((d) => void (d.environment.shelterReturnMin = v))
                  }
                  min={2}
                  max={60}
                  step={1}
                  unit="min"
                />
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-primary" />
                Workload Blocks
              </CardTitle>
            </CardHeader>
            <CardContent>
              <WorkloadStrip scenario={scenario} />
            </CardContent>
          </Card>

          <div className="grid 2xl:grid-cols-[minmax(0,1fr)_360px] gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShieldAlert className="h-4 w-4 text-primary" />
                  5x5 Likelihood x Consequence Matrix
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <RiskMatrix
                  hazards={result.hazards}
                  selectedId={selectedHazard.id}
                  onSelect={setSelectedHazardId}
                />
                <div className={cn("rounded-lg border p-4", POSTURE_CLASS[selectedHazard.posture])}>
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="display text-base font-semibold">{selectedHazard.name}</p>
                      <p className="text-[12px] mt-1">{selectedHazard.driver}</p>
                    </div>
                    <div className="text-right shrink-0">
                      <p className="text-num text-lg font-bold">
                        {selectedHazard.probabilityPercent.toFixed(1)}%
                      </p>
                      <p className="text-[10px] uppercase tracking-[0.14em]">
                        score {selectedHazard.score}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GitCompare className="h-4 w-4 text-primary" />
                  Decision Alternatives
                </CardTitle>
              </CardHeader>
              <CardContent>
                <MitigationTable scenario={scenario} />
              </CardContent>
            </Card>
          </div>

          <div className="grid 2xl:grid-cols-[minmax(0,1fr)_360px] gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <UserRound className="h-4 w-4 text-primary" />
                  Crew and Telemetry
                </CardTitle>
              </CardHeader>
              <CardContent className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
                <Slider
                  label="Age"
                  value={[scenario.crew.ageYears]}
                  onValueChange={([v]) => patch((d) => void (d.crew.ageYears = v))}
                  min={25}
                  max={65}
                  step={1}
                  unit="yr"
                />
                <Slider
                  label="Mass"
                  value={[scenario.crew.massKg]}
                  onValueChange={([v]) => patch((d) => void (d.crew.massKg = v))}
                  min={45}
                  max={110}
                  step={1}
                  unit="kg"
                />
                <Slider
                  label="SpO2"
                  value={[scenario.crew.spo2Percent]}
                  onValueChange={([v]) => patch((d) => void (d.crew.spo2Percent = v))}
                  min={88}
                  max={100}
                  step={1}
                  unit="%"
                />
                <Slider
                  label="Hydration"
                  value={[scenario.crew.hydration * 100]}
                  onValueChange={([v]) => patch((d) => void (d.crew.hydration = v / 100))}
                  min={30}
                  max={100}
                  step={1}
                  unit="%"
                />
                <div className="space-y-1.5">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Sex covariate
                  </label>
                  <Select
                    value={scenario.crew.sex}
                    onValueChange={(value) =>
                      patch((d) => void (d.crew.sex = value as EVAScenario["crew"]["sex"]))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Male">Male</SelectItem>
                      <SelectItem value="Female">Female</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end pb-2">
                  <Switch
                    checked={scenario.crew.symptomFlag}
                    onCheckedChange={(checked) =>
                      patch((d) => void (d.crew.symptomFlag = checked))
                    }
                    label="Symptom flag"
                  />
                </div>
                <div className="flex items-end pb-2">
                  <Switch
                    checked={telemetryReplay}
                    onCheckedChange={setTelemetryReplay}
                    label="Telemetry replay"
                  />
                </div>
              </CardContent>
            </Card>

            <EvidencePanel scenario={scenario} />
          </div>

          <Card variant="glass">
            <CardContent className="pt-6">
              <div className="grid md:grid-cols-3 gap-4 text-[12px] text-muted-foreground">
                <div className="flex items-start gap-2">
                  <Radio className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                  <span>Commercial EVA service assumptions follow NASA xEVAS public framing.</span>
                </div>
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
                  <span>DCS probability is Conkin-style ETR logic, not flight-certified mission software.</span>
                </div>
                <div className="flex items-start gap-2">
                  <Moon className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                  <span>Lunar dust, thermal, CO2, and radiation rows are decision aids, not validated medical endpoints.</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}
