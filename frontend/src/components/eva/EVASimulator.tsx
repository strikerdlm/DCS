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
import { cn, formatNumber, pressureAtmToAltitudeFt } from "../../lib/utils";
import { updateScenario, normalizePreset, scenarioAlternatives } from "../../utils/evaScenario";
import {
  missionRules,
  EVA_MODEL_VERSION,
  posture,
  psiaToKpa,
  simulateEVA,
} from "../../utils/eva";
import {
  createEVAReport,
  canUseOffline,
  responseForInputs,
  downloadLocalScenarioJson,
  downloadReportArtifact,
  EVA_API_BASE_URL,
  simulateEVAApi,
} from "../../utils/evaApi";
import type { EVAOptions, MissionRules } from "../../utils/eva";
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
  unavailable: "bg-zinc-500/10 text-zinc-700 dark:text-zinc-300 border-zinc-500/25",
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

const RISK_CELL_TONE: Record<RiskMatrixHazard["posture"], string> = {
  unavailable: "bg-zinc-500/10 border-zinc-500/25 text-muted-foreground",
  green:
    "bg-emerald-100/90 dark:bg-emerald-950/55 border-emerald-500/45 text-emerald-950 dark:text-emerald-100 shadow-[inset_0_0_0_1px_rgba(16,185,129,0.16)]",
  yellow:
    "bg-amber-200/95 dark:bg-amber-900/60 border-amber-500/65 text-amber-950 dark:text-amber-50 shadow-[inset_0_0_0_1px_rgba(245,158,11,0.24)]",
  orange:
    "bg-orange-200/95 dark:bg-orange-900/65 border-orange-500/70 text-orange-950 dark:text-orange-50 shadow-[inset_0_0_0_1px_rgba(249,115,22,0.28)]",
  red:
    "bg-red-200/95 dark:bg-red-950/70 border-red-500/80 text-red-950 dark:text-red-50 shadow-[inset_0_0_0_1px_rgba(239,68,68,0.34)]",
};

function likelihoodBands(rules: MissionRules): Record<RiskLikelihoodLevel, string> {
  const t = rules.lxc_probability_thresholds_percent;
  return { 1: `<${t.level_2_min}%`, 2: `${t.level_2_min}-<${t.level_3_min}%`, 3: `${t.level_3_min}-<${t.level_4_min}%`, 4: `${t.level_4_min}-<${t.level_5_min}%`, 5: `≥${t.level_5_min}%` };
}
const probabilityLabel = (value: number | null) => value === null ? "Unavailable" : `${value.toFixed(2)}%`;

type PressureUnit = "psi" | "mmHg" | "inHg" | "bar" | "hPa";

const PRESSURE_UNITS: PressureUnit[] = ["psi", "mmHg", "inHg", "bar", "hPa"];

const PRESSURE_UNIT_META: Record<
  PressureUnit,
  { label: string; factorFromPsia: number; digits: number }
> = {
  psi: { label: "psia", factorFromPsia: 1, digits: 2 },
  mmHg: { label: "mmHg", factorFromPsia: 760 / 14.695948775513449, digits: 0 },
  inHg: { label: "inHg", factorFromPsia: 29.921259842519685 / 14.695948775513449, digits: 2 },
  bar: { label: "bar", factorFromPsia: 0.06894757293168, digits: 3 },
  hPa: { label: "hPa", factorFromPsia: 68.94757293168, digits: 0 },
};

function pressureToAltitudeLabel(psia: number): string {
  const atm = psia / 14.695948775513449;
  if (atm >= 1) return "sea-level cabin";
  const altitudeFt = pressureAtmToAltitudeFt(atm);
  return `${Math.round(altitudeFt / 100) * 100} ft equiv.`;
}

function postureLabel(posture: RiskMatrixHazard["posture"]): string {
  if (posture === "unavailable") return "Unavailable";
  if (posture === "green") return "Below rule threshold";
  if (posture === "yellow") return "Watch";
  if (posture === "orange") return "Mitigate";
  return "No-go";
}

function decisionLabel(decision: EVADecisionImplication): string {
  return decision.charAt(0).toUpperCase() + decision.slice(1);
}

function pressureValue(psia: number, unit: PressureUnit): number {
  return psia * PRESSURE_UNIT_META[unit].factorFromPsia;
}

function formatPressure(psia: number, unit: PressureUnit): string {
  const meta = PRESSURE_UNIT_META[unit];
  return `${pressureValue(psia, unit).toFixed(meta.digits)} ${meta.label}`;
}

function PressureUnitSelector({
  value,
  onChange,
}: {
  value: PressureUnit;
  onChange: (unit: PressureUnit) => void;
}): React.ReactElement {
  return (
    <div className="flex items-center gap-1 rounded-lg border border-border/70 bg-background/55 p-1">
      {PRESSURE_UNITS.map((unit) => (
        <button
          key={unit}
          type="button"
          onClick={() => onChange(unit)}
          className={cn(
            "text-num rounded-md px-2.5 py-1.5 text-[11px] font-semibold transition-colors",
            value === unit
              ? "bg-primary text-primary-foreground shadow-sm"
              : "text-muted-foreground hover:bg-muted hover:text-foreground",
          )}
          aria-pressed={value === unit}
        >
          {PRESSURE_UNIT_META[unit].label}
        </button>
      ))}
    </div>
  );
}

function hazardCode(name: string): string {
  const code = name
    .replace("/", " ")
    .split(" ")
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .slice(0, 3)
    .toUpperCase();
  return code || name.slice(0, 3).toUpperCase();
}

function PressureTimelineChart({
  data,
  pressureUnit,
}: {
  data: EVATimelinePoint[];
  pressureUnit: PressureUnit;
}): React.ReactElement {
  const pressureLabel = `Pressure (${PRESSURE_UNIT_META[pressureUnit].label})`;
  const option: EChartsOption = useMemo(
    () => ({
      ...getBaseChartOptions(),
      grid: { left: 40, right: 40, top: 58, bottom: 54, containLabel: true },
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
                `${row.marker}${row.seriesName}: <span class="font-mono">${formatNumber(row.value[1], row.seriesName.includes("VO2") ? 1 : PRESSURE_UNIT_META[pressureUnit].digits)}</span>`,
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
        nameLocation: "middle",
        nameGap: 30,
        min: "dataMin",
        max: "dataMax",
        splitNumber: 3,
        axisLabel: { color: chartTheme.axisColor, fontSize: 11, hideOverlap: true },
        splitLine: { lineStyle: { color: chartTheme.gridColor, type: "dashed" } },
      },
      yAxis: [
        {
          type: "value",
          name: pressureLabel,
          nameLocation: "middle",
          nameGap: 32,
          nameRotate: 90,
          nameTextStyle: { color: chartTheme.textColor, fontSize: 12, fontWeight: 600 },
          axisLabel: { color: chartTheme.axisColor, fontSize: 11 },
          splitLine: { lineStyle: { color: chartTheme.gridColor, type: "dashed" } },
        },
        {
          type: "value",
          name: "VO2 (mL/kg/min)",
          nameLocation: "middle",
          nameGap: 32,
          nameRotate: -90,
          nameTextStyle: { color: chartTheme.textColor, fontSize: 12, fontWeight: 600 },
          axisLabel: { color: chartTheme.axisColor, fontSize: 11 },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: "Ambient",
          type: "line",
          step: "start",
          symbol: "none",
          data: data.map((p) => [p.timeMin, pressureValue(p.ambientPressurePsia, pressureUnit)]),
          lineStyle: { width: 3, color: chartTheme.primaryColor },
          areaStyle: { color: withAlpha(chartTheme.primaryColor, 0.1) },
        },
        {
          name: "Tissue N2",
          type: "line",
          smooth: false,
          symbol: "none",
          data: data.map((p) => [p.timeMin, pressureValue(p.tissueN2Psia, pressureUnit)]),
          lineStyle: { width: 2, color: colorPalettes.scientific[2] },
        },
        {
          name: "Ambient N2 (dry)", type: "line", step: "start", symbol: "none",
          data: data.map(p => [p.timeMin, pressureValue(p.ambientN2Psia, pressureUnit)]),
          lineStyle: { width: 1.5, type: "dashed", color: chartTheme.secondaryColor },
        },
        {
          name: "VO2 (mL/kg/min)", type: "line", step: "start", yAxisIndex: 1, symbol: "none",
          data: data.map(p => [p.timeMin, p.vo2MlKgMin]),
          lineStyle: { width: 1.5, color: chartTheme.riskModerateColor },
        },
      ],
    }),
    [data, pressureLabel, pressureUnit],
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
  const maxVo2 = Math.max(...scenario.workload.map((block) => block.vo2MlKgMin), scenario.peakVo2MlKgMin, 1);
  return (
    <div className="space-y-5">
      <div className="space-y-3">
        {scenario.workload.map((block, i) => {
          const intensity = Math.min(1, block.vo2MlKgMin / Math.max(scenario.peakVo2MlKgMin, 1));
          const share = Math.round((block.durationMin / total) * 100);
          const barWidth = `${Math.max(12, (block.vo2MlKgMin / maxVo2) * 100)}%`;
          const color = colorPalettes.scientific[i % colorPalettes.scientific.length];
          return (
            <div
              key={`${block.name}-${i}`}
              className="relative overflow-hidden rounded-lg border border-border/75 bg-card/70 p-4"
              style={{
                background: `linear-gradient(135deg, ${withAlpha(color, 0.12 + intensity * 0.22)}, ${withAlpha(color, 0.05)})`,
              }}
            >
              <div
                className="absolute inset-y-0 left-0 opacity-35"
                style={{
                  width: barWidth,
                  background: `linear-gradient(90deg, ${withAlpha(color, 0.72)}, ${withAlpha(color, 0.08)})`,
                }}
              />
              <div className="relative z-10 grid gap-4 lg:grid-cols-[minmax(180px,0.9fr)_minmax(260px,1.4fr)_210px] lg:items-center">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-num flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-border/70 bg-background/70 text-[11px] font-bold">
                      {i + 1}
                    </span>
                    <p className="text-[14px] font-semibold leading-snug">{block.name}</p>
                  </div>
                  <p className="mt-2 text-[12px] text-muted-foreground">
                    {share}% of the planned EVA timeline
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="h-4 overflow-hidden rounded-full border border-border/70 bg-background/70">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: barWidth,
                        background: `linear-gradient(90deg, ${withAlpha(color, 0.95)}, ${withAlpha(color, 0.44)})`,
                      }}
                    />
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-[11px] text-muted-foreground">
                    <span>Rest</span>
                    <span className="text-center">Working</span>
                    <span className="text-right">Peak</span>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2 text-[11px]">
                  <div className="rounded-md bg-background/65 border border-border/60 px-2 py-1">
                    <p className="text-muted-foreground">Duration</p>
                    <p className="text-num font-semibold">{formatNumber(block.durationMin, 1)} min</p>
                  </div>
                  <div className="rounded-md bg-background/65 border border-border/60 px-2 py-1">
                    <p className="text-muted-foreground">VO2</p>
                    <p className="text-num font-semibold">{formatNumber(block.vo2MlKgMin, 1)}</p>
                  </div>
                  <div className="rounded-md bg-background/65 border border-border/60 px-2 py-1">
                    <p className="text-muted-foreground">Share</p>
                    <p className="text-num font-semibold">{share}%</p>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="grid grid-cols-3 gap-3 text-[12px]">
        <div className="rounded-lg border border-border/70 bg-background/55 px-3 py-2">
          <p className="text-muted-foreground">Mean workload</p>
          <p className="text-num font-semibold">{scenario.meanVo2MlKgMin.toFixed(0)} mL/kg/min</p>
        </div>
        <div className="rounded-lg border border-border/70 bg-background/55 px-3 py-2 text-center">
          <p className="text-muted-foreground">Peak workload</p>
          <p className="text-num font-semibold">{scenario.peakVo2MlKgMin.toFixed(0)} mL/kg/min</p>
        </div>
        <div className="rounded-lg border border-border/70 bg-background/55 px-3 py-2 text-right">
          <p className="text-muted-foreground">EVA duration</p>
          <p className="text-num font-semibold">{scenario.evaDurationMin} min</p>
        </div>
      </div>
    </div>
  );
}

function RiskMatrix({
  hazards,
  selectedId,
  onSelect,
  rules,
}: {
  rules: MissionRules;
  hazards: RiskMatrixHazard[];
  selectedId: string;
  onSelect: (id: string) => void;
}): React.ReactElement {
  const bands = likelihoodBands(rules);
  const rows: RiskLikelihoodLevel[] = [5, 4, 3, 2, 1];
  const cols: RiskConsequenceLevel[] = [1, 2, 3, 4, 5];
  return (
    <div className="space-y-4">
      <p className="text-xs text-muted-foreground">Configured planning bands, not calibrated event probabilities. Indicators without estimates are not placed in the matrix.</p>
      <div className="flex flex-wrap gap-2">
        {hazards.map(h => <button key={h.id} type="button" onClick={() => onSelect(h.id)} className={cn("rounded-md border px-3 py-2 text-xs", POSTURE_CLASS[h.posture], h.id === selectedId && "ring-2 ring-primary/50")}>{h.name}{h.indicator ? `: ${typeof h.indicator.value === "number" ? formatNumber(h.indicator.value, 2) : h.indicator.value} ${h.indicator.unit}` : `: ${probabilityLabel(h.probabilityPercent)}`}</button>)}
      </div>
      {hazards.some(h => h.likelihood !== null) && <>
      <div className="overflow-x-auto">
      <div className="grid min-w-[430px] grid-cols-[92px_repeat(5,minmax(58px,1fr))] gap-1.5 text-[10px]">
        <div />
        {cols.map((col) => (
          <div key={col} className="text-center text-muted-foreground">
            <span className="block text-num text-[11px] text-foreground">C{col}</span>
            <span className="block truncate">{CONSEQUENCE_LABELS[col]}</span>
          </div>
        ))}
        {rows.map((row) => (
          <React.Fragment key={row}>
            <div className="h-20 flex flex-col justify-center text-muted-foreground">
              <span className="text-num text-[11px] text-foreground">L{row}</span>
              <span>{LIKELIHOOD_LABELS[row]}</span>
              <span className="text-num text-[10px]">{bands[row]}</span>
            </div>
            {cols.map((col) => {
              const cellHazards = hazards.filter(
                (hazard) => hazard.likelihood === row && hazard.consequence === col,
              );
              const score = row * col;
              const cellPosture = posture(score, rules);
              const label =
                cellHazards.length > 0
                  ? cellHazards.map((hazard) => `${hazard.name}: ${probabilityLabel(hazard.probabilityPercent)}, score ${hazard.score}`).join("; ")
                  : `L${row} x C${col}, score ${score}`;
              return (
                <button
                  key={`${row}-${col}`}
                  className={cn(
                    "relative h-20 rounded-md border p-2 text-left transition-all hover:ring-2 hover:ring-primary/35",
                    RISK_CELL_TONE[cellPosture],
                    cellHazards.length === 0 && "opacity-80",
                    cellHazards.some((h) => h.id === selectedId) && "ring-2 ring-primary/60",
                  )}
                  aria-label={label}
                  onClick={() => cellHazards[0] && onSelect(cellHazards[0].id)}
                  title={label}
                  type="button"
                >
                  <span className="absolute bottom-1.5 right-2 text-num text-[10px] font-semibold opacity-65">
                    {score}
                  </span>
                  <div className="h-full flex flex-wrap content-start gap-1.5 pr-4">
                    {cellHazards.map((hazard) => (
                      <span
                        key={hazard.id}
                        className={cn(
                          "min-h-6 min-w-7 px-1.5 rounded text-[10px] font-bold flex items-center justify-center border bg-background/70 shadow-sm",
                          POSTURE_CLASS[hazard.posture],
                        )}
                        title={`${hazard.name}: ${probabilityLabel(hazard.probabilityPercent)}, L${hazard.likelihood} x C${hazard.consequence}`}
                      >
                        {hazardCode(hazard.name)}
                      </span>
                    ))}
                  </div>
                </button>
              );
            })}
          </React.Fragment>
        ))}
      </div>
      </div>
      <div className="grid grid-cols-5 gap-1 pl-[98px] text-[10px] text-muted-foreground">
        <span className="col-span-5 text-center">Consequence</span>
      </div>
      <div className="grid sm:grid-cols-4 gap-2 text-[11px]">
        <div className="rounded-md border border-emerald-500/45 bg-emerald-100/80 dark:bg-emerald-950/45 px-2 py-1.5">
          <span className="font-semibold text-emerald-800 dark:text-emerald-200">Green</span> score 1-{rules.posture_score_max.green}
        </div>
        <div className="rounded-md border border-amber-500/60 bg-amber-200/90 dark:bg-amber-900/55 px-2 py-1.5">
          <span className="font-semibold text-amber-900 dark:text-amber-100">Yellow</span> score {rules.posture_score_max.green + 1}-{rules.posture_score_max.yellow}
        </div>
        <div className="rounded-md border border-orange-500/65 bg-orange-200/90 dark:bg-orange-900/60 px-2 py-1.5">
          <span className="font-semibold text-orange-900 dark:text-orange-100">Orange</span> score {rules.posture_score_max.yellow + 1}-{rules.posture_score_max.orange}
        </div>
        <div className="rounded-md border border-red-500/75 bg-red-200/90 dark:bg-red-950/65 px-2 py-1.5">
          <span className="font-semibold text-red-900 dark:text-red-100">Red</span> score {rules.posture_score_max.orange + 1}-25
        </div>
      </div>
      </>}
    </div>
  );
}

function MitigationTable({ scenario, options }: { scenario: EVAScenario; options: EVAOptions }): React.ReactElement {
  const rows = useMemo(() => scenarioAlternatives(scenario, options).map(option => ({
    label: option.label,
    result: simulateEVA(option.scenario, { missionRuleProfile: options.missionRuleProfile, telemetryNowSec: options.telemetryNowSec }),
  })), [scenario, options]);
  const baseline = rows[0].result.timeline.at(-1)!.tissueN2Psia;

  return (
    <div className="space-y-2">
      <p className="text-xs text-muted-foreground">Final tissue N2 (psia) and change from baseline. All alternatives start from the same telemetry-adjusted state and use the same browser equation and rules. Future pressure hypotheses are not overwritten by a current snapshot; lower N2 is not a validated risk reduction.</p>
      {rows.map((row) => {
        const finalN2 = row.result.timeline.at(-1)!.tissueN2Psia;
        const delta = finalN2 - baseline;
        return (
          <div
            key={row.label}
            className="grid grid-cols-[1fr_70px_62px_72px] gap-3 items-center rounded-lg border border-border/70 bg-background/45 px-3 py-2"
          >
            <span className="text-[12px] font-medium truncate">{row.label}</span>
            <span className="text-num text-[12px] text-right">{finalN2.toFixed(2)}</span>
            <span
              className={cn(
                "text-num text-[12px] text-right",
                "text-muted-foreground",
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
        <p className="text-xs text-muted-foreground">Planning context only. These are illustrative presets, not validated mission protocols.</p>
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
              Unavailable
            </p>
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-[0.14em] opacity-75">Integrated risk</p>
            <p className="text-num text-sm font-semibold">
              Unavailable
            </p>
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-[0.14em] opacity-75">LxC</p>
            <p className="text-num text-sm font-semibold">
              {result.lxcScore === null ? "Unavailable" : `${result.lxcLikelihood} × ${result.lxcConsequence} = ${result.lxcScore}`}
            </p>
          </div>
        </div>
      </div>
      <p className="text-[12px] mt-3 leading-relaxed">{result.decisionRationale}</p>
      {result.stopReasons.length > 0 && <p className="mt-2 text-sm font-semibold" role="alert">Stop conditions: {result.stopReasons.join(", ").replaceAll("_", " ")}</p>}
    </div>
  );
}

export function EVASimulator(): React.ReactElement {
  const [scenario, setScenario] = useState<EVAScenario>(() => normalizePreset(EVA_SCENARIOS[1]));
  const [missionRuleProfile, setMissionRuleProfile] = useState("artemis_lunar");
  const [pressureUnit, setPressureUnit] = useState<PressureUnit>("psi");
  const [telemetryReplay, setTelemetryReplay] = useState(false);
  const telemetrySamples = useMemo<EVATelemetrySample[]>(
    () =>
      telemetryReplay
        ? [
            {
              kind: "pressure",
              value: scenario.suit.pressurePsia,
              unit: "psia",
              source: "synthetic-replay-pressure",
              confidence: 0.96,
            },
            {
              kind: "workload",
              value: scenario.peakVo2MlKgMin,
              unit: "vo2_ml_kg_min",
              source: "synthetic-replay-VO2",
              confidence: 0.88,
            },
            {
              kind: "heart_rate",
              value: 128,
              unit: "bpm",
              source: "synthetic-replay-hr",
              confidence: 0.86,
            },
            {
              kind: "hrv",
              value: 36,
              unit: "rmssd_ms",
              source: "synthetic-replay-hrv",
              confidence: 0.82,
            },
            {
              kind: "spo2",
              value: scenario.crew.spo2Percent,
              unit: "%",
              source: "synthetic-replay-spo2",
              confidence: 0.92,
            },
            {
              kind: "skin_temperature",
              value: 34.8,
              unit: "c",
              source: "synthetic-replay-skin-temp",
              confidence: 0.84,
            },
          ].map(sample => ({ ...sample, timestampSec: 995 })) as EVATelemetrySample[]
        : [],
    [scenario, telemetryReplay],
  );
  // Fixed replay clock makes synthetic telemetry reproducible in both runtimes.
  const options = useMemo<EVAOptions>(() => ({ missionRuleProfile, telemetry: telemetrySamples, telemetryNowSec: 1000 }), [missionRuleProfile, telemetrySamples]);
  const rules = useMemo(() => missionRules(missionRuleProfile), [missionRuleProfile]);
  const calculation = useMemo(() => {
    try { return { result: simulateEVA(scenario, options), error: null }; }
    catch (error) { return { result: null, error: error instanceof Error ? error.message : "Invalid scenario" }; }
  }, [scenario, options]);
  const inputKey = useMemo(() => JSON.stringify({ scenario, options }), [scenario, options]);
  const [apiState, setApiState] = useState<{ key: string; response?: EVASimulationApiResponse; error?: string; fallback?: boolean } | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);
  const [reportFormat, setReportFormat] = useState<EVAReportFormat | null>(null);
  const [selectedHazardId, setSelectedHazardId] = useState("dcs");
  const apiResponse = responseForInputs(inputKey, apiState);
  const activeState = apiState?.key === inputKey ? apiState : null;
  const apiStatus = apiResponse ? "online" : activeState?.error ? activeState.fallback ? "fallback" : "invalid" : "loading";
  const apiError = reportError ?? activeState?.error;
  const result = apiResponse?.result ?? calculation.result;

  useEffect(() => {
    if (calculation.error) return;
    const controller = new AbortController();
    const handle = window.setTimeout(() => {
      simulateEVAApi(scenario, { ...options, signal: controller.signal })
        .then(response => {
          if (!controller.signal.aborted) setApiState({ key: inputKey, response });
        })
        .catch((error: unknown) => {
          if (!controller.signal.aborted) setApiState({ key: inputKey, error: error instanceof Error ? error.message : "TinyDCS API error", fallback: canUseOffline(error) });
        });
    }, 250);
    return () => { controller.abort(); window.clearTimeout(handle); };
  }, [inputKey, scenario, options, calculation.error]);

  const setPreset = (id: string) => {
    const preset = EVA_SCENARIOS.find((item) => item.id === id);
    if (!preset) return;
    setScenario(normalizePreset(preset));
    setSelectedHazardId("dcs");
  };

  const patch = (mutator: (draft: EVAScenario) => void) => {
    setScenario((current) => updateScenario(current, mutator));
  };

  const exportReport = async (format: EVAReportFormat) => {
    setReportFormat(format);
    try {
      const report = await createEVAReport(scenario, options);
      downloadReportArtifact(report, format);
    } catch (error) {
      if (format === "json" && canUseOffline(error)) {
        downloadLocalScenarioJson(scenario, options);
      } else {
        setReportError(error instanceof Error ? error.message : "Report export requires the TinyDCS API");
      }
    } finally {
      setReportFormat(null);
    }
  };

  if (!result || calculation.error || apiStatus === "invalid") return (
    <div className="surface space-y-4 p-6" role="alert">
      <h2 className="text-xl font-semibold">Calculation unavailable</h2>
      <p>{calculation.error ?? apiError}</p>
      <p>No browser fallback is used for rejected inputs or an incompatible API contract.</p>
      <div className="flex flex-wrap gap-2">{EVA_SCENARIOS.map(p => <Button key={p.id} onClick={() => setPreset(p.id)}>{p.shortName}</Button>)}</div>
    </div>
  );
  const selectedHazard = result.hazards.find(h => h.id === selectedHazardId) ?? result.hazards[0];
  const bands = likelihoodBands(rules);

  return (
    <div className="space-y-6">
      <section className="surface-elevated overflow-hidden">
        <div className="p-6 lg:p-7 border-b border-border/70">
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
              {apiStatus === "online" ? "Python API" : apiStatus === "loading" ? "Syncing" : "Offline reference"}
            </span>
          </div>
          <div className="max-w-5xl">
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
              detail={`${formatPressure(result.p1n2Psia, pressureUnit)} tissue N2 after prebreathe`}
              tone="default"
            />
            <NumberTile
              icon={<Wind className="h-4 w-4" />}
              label="Uncertainty interval"
              value="Unavailable"
              detail="No calibrated EVA interval exists"
            />
            <NumberTile
              icon={<BatteryCharging className="h-4 w-4" />}
              label="PLSS margin"
              value={`${result.consumablesMarginMin.toFixed(0)} min`}
              detail={`Oxygen reserve separate: ${result.oxygenReserveMin} min`}
              tone={result.consumablesMarginMin < 0 ? "red" : "default"}
            />
            <NumberTile
              icon={<Activity className="h-4 w-4" />}
              label="Mean workload"
              value={`${result.workloadMeanVo2MlKgMin.toFixed(1)} mL/kg/min`}
              detail="Duration-weighted across the workload schedule"
            />
          </div>
          <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2">
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
                {apiResponse?.modelMetadata.modelVersion ?? EVA_MODEL_VERSION}
                {result.telemetryStatus ? ` · telemetry ${result.telemetryStatus.accepted}/${telemetrySamples.length}` : ""}
              </span>
            </div>
            <PressureUnitSelector value={pressureUnit} onChange={setPressureUnit} />
          </div>
        </div>
        <div className="p-5 lg:p-6 bg-background/35">
          <div className="grid gap-5 xl:grid-cols-[320px_minmax(0,1fr)] xl:items-center">
            <RiskGauge value={result.pDcsPercent} title="NASA reference endpoint (4 h)" height={250} max={40} />
            <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-3 text-[11px]">
              <div className="rounded-lg border border-border/70 bg-card/70 p-3">
                <p className="text-muted-foreground">Suit pressure</p>
                <p className="text-num font-semibold">
                  {formatPressure(scenario.suit.pressurePsia, pressureUnit)}
                </p>
                <p className="text-muted-foreground">{psiaToKpa(scenario.suit.pressurePsia).toFixed(0)} kPa reference</p>
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
                  {formatPressure(scenario.habitat.pressurePsia, pressureUnit)} /{" "}
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

      {reportError && <p role="alert" className="text-sm text-red-600">{reportError}</p>}
      <p className="text-sm text-muted-foreground">Research software, not operational clearance. The NASA endpoint requires declared adynamic, 240-minute, constant 4.3 psia oxygen exposure. Source-cohort transportability and clinical validation are not established.</p>
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

      <div className="grid grid-cols-1 2xl:grid-cols-[360px_minmax(0,1fr)] gap-6">
        <aside className="space-y-4">
          <Card variant="glass">
            <CardHeader>
              <CardTitle>Scenario</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Select value={scenario.id} onValueChange={setPreset}>
                <SelectTrigger aria-label="Scenario">
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
                  <SelectTrigger aria-label="Mission-rule profile">
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
                label="Prebreathe exercise"
                value={[scenario.prebreatheVo2MlKgMin ?? 3.5]}
                onValueChange={([v]) => patch(d => { d.prebreatheVo2MlKgMin = v; })}
                min={0} max={40} step={0.5} unit="mL/kg/min"
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
                    patch(d => {
                      d.suit.variablePressure = checked;
                      d.pressureSegments = checked ? [
                        { durationMin: d.evaDurationMin / 2, pressurePsia: d.suit.pressurePsia, oxygenFraction: d.suit.oxygenFraction },
                        { durationMin: d.evaDurationMin / 2, pressurePsia: d.suit.pressurePsia, oxygenFraction: d.suit.oxygenFraction },
                      ] : [];
                    })
                  }
                  label="Explicit two-stage pressure schedule"
                />
                {scenario.pressureSegments?.length === 2 && <div className="space-y-3">
                  <p className="text-xs text-muted-foreground">Two equal-duration stages ({formatNumber(scenario.evaDurationMin / 2, 1)} min each). The suit-pressure control sets stage 1; stage 2 is specified below.</p>
                  <Slider label="Second-stage pressure" value={[scenario.pressureSegments[1].pressurePsia]} onValueChange={([v]) => patch(d => { d.pressureSegments![1].pressurePsia = v; })} min={3.7} max={8.2} step={0.1} unit="psia" />
                </div>}
                <Switch checked={scenario.nasaAdynamicReference ?? false} onCheckedChange={checked => patch(d => { d.nasaAdynamicReference = checked; })} label="Declare adynamic source-reference assumptions" />
                <p className="text-xs text-muted-foreground">This declaration does not validate a moving EVA or a novel protocol.</p>
                <Switch
                  checked={scenario.suit.suitPort}
                  onCheckedChange={(checked) => patch((d) => void (d.suit.suitPort = checked))}
                  label="Suitport / rear entry"
                />
              </div>
            </CardContent>
          </Card>
        </aside>

        <section aria-label="EVA results and crew inputs" className="space-y-6 min-w-0">
          <div className="grid grid-cols-1 2xl:grid-cols-[minmax(0,1fr)_360px] gap-6">
            <Card>
              <CardHeader className="flex-row flex-wrap items-center justify-between gap-3 space-y-0">
                <CardTitle className="flex items-center gap-2">
                  <Gauge className="h-4 w-4 text-primary" />
                  Pressure and Tissue N2 Timeline
                </CardTitle>
                <PressureUnitSelector value={pressureUnit} onChange={setPressureUnit} />
              </CardHeader>
              <CardContent>
                <PressureTimelineChart data={result.timeline} pressureUnit={pressureUnit} />
                <p className="text-xs text-muted-foreground">Dry ambient N2; NASA Eq. 6 prebreathe kinetics. EVA kinetics are an exploratory compartment extension, not a validated risk trajectory. Pressure and workload changes are explicit steps.</p>
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
                  label="Schedule mean VO2"
                  formatValue={value => value.toFixed(1)}
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
                  label="Declared peak VO2"
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
                    <SelectTrigger aria-label="Radiation weather">
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
              <p className="mb-4 text-xs text-muted-foreground">Duration edits rescale block durations proportionally; the mean control scales block VO2. PB exercise is separate.</p>
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
                  rules={rules}
                  hazards={result.hazards}
                  selectedId={selectedHazard.id}
                  onSelect={setSelectedHazardId}
                />
                <div className={cn("rounded-lg border p-4", POSTURE_CLASS[selectedHazard.posture])}>
                  <div className="space-y-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="display text-base font-semibold">{selectedHazard.name}</p>
                        <p className="text-[12px] mt-1">{selectedHazard.driver}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <p className="text-num text-lg font-bold">
                          {probabilityLabel(selectedHazard.probabilityPercent)}
                        </p>
                        <p className="text-[10px] uppercase tracking-[0.14em]">
                          {hazardCode(selectedHazard.name)}
                        </p>
                      </div>
                    </div>
                    <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-2 text-[11px]">
                      <div className="rounded-md border border-current/20 bg-background/55 px-2.5 py-2">
                        <p className="font-semibold">Probability</p>
                        <p className="text-muted-foreground">Point estimate used for likelihood band.</p>
                        <p className="text-num font-semibold mt-1">{probabilityLabel(selectedHazard.probabilityPercent)}</p>
                      </div>
                      <div className="rounded-md border border-current/20 bg-background/55 px-2.5 py-2">
                        <p className="font-semibold">Likelihood</p>
                        <p className="text-muted-foreground">{selectedHazard.likelihood === null ? "Unavailable" : `L${selectedHazard.likelihood}: ${LIKELIHOOD_LABELS[selectedHazard.likelihood]}`}.</p>
                        <p className="text-num font-semibold mt-1">{selectedHazard.likelihood === null ? "No probability model" : bands[selectedHazard.likelihood]}</p>
                      </div>
                      <div className="rounded-md border border-current/20 bg-background/55 px-2.5 py-2">
                        <p className="font-semibold">Consequence</p>
                        <p className="text-muted-foreground">C{selectedHazard.consequence}: {CONSEQUENCE_LABELS[selectedHazard.consequence]} severity.</p>
                        <p className="text-num font-semibold mt-1">{selectedHazard.consequence} / 5</p>
                      </div>
                      <div className="rounded-md border border-current/20 bg-background/55 px-2.5 py-2">
                        <p className="font-semibold">LxC Score</p>
                        <p className="text-muted-foreground">Likelihood multiplied by consequence.</p>
                        <p className="text-num font-semibold mt-1">
                          {selectedHazard.score === null ? "Unavailable" : `${selectedHazard.likelihood} × ${selectedHazard.consequence} = ${selectedHazard.score}`}
                        </p>
                      </div>
                      <div className="rounded-md border border-current/20 bg-background/55 px-2.5 py-2">
                        <p className="font-semibold">Posture</p>
                        <p className="text-muted-foreground">Matrix color assigned from score.</p>
                        <p className="font-semibold mt-1">{postureLabel(selectedHazard.posture)}</p>
                      </div>
                      <div className="rounded-md border border-current/20 bg-background/55 px-2.5 py-2">
                        <p className="font-semibold">Driver</p>
                        <p className="text-muted-foreground">Dominant input behind this hazard.</p>
                        <p className="font-semibold mt-1">{selectedHazard.driver}</p>
                      </div>
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
                <MitigationTable scenario={scenario} options={options} />
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
                  label="Hydration indicator (entered)"
                  value={[scenario.crew.hydration * 100]}
                  onValueChange={([v]) => patch((d) => void (d.crew.hydration = v / 100))}
                  min={30}
                  max={100}
                  step={1}
                  unit="%"
                />
                <div className="space-y-1.5">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Recorded sex (not used in RM equation)
                  </label>
                  <Select
                    value={scenario.crew.sex}
                    onValueChange={(value) =>
                      patch((d) => void (d.crew.sex = value as EVAScenario["crew"]["sex"]))
                    }
                  >
                    <SelectTrigger aria-label="Recorded sex">
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
                    label="Synthetic telemetry replay"
                  />
                </div>
                {telemetryReplay && <div className="md:col-span-2 lg:col-span-3 space-y-2 text-xs text-muted-foreground">
                  <p>Synthetic samples at replay time 995 s, evaluated at 1000 s; not live wearable measurements.</p>
                  {result.telemetryStatus?.rawIndicators?.map((sample, index) => <p key={index}>{sample.kind}: {formatNumber(sample.value, 2)} {sample.unit} · {sample.source}</p>)}
                  {result.telemetryStatus?.warnings.map(warning => <p key={warning}>{warning}</p>)}
                </div>}
              </CardContent>
            </Card>

            <EvidencePanel scenario={scenario} />
          </div>
        </section>
      </div>
    </div>
  );
}
