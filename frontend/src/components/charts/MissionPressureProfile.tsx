import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption, SeriesOption } from "echarts";
import { chartTheme, colorPalettes, getBaseChartOptions, withAlpha } from "./chartConfig";
import { missionPressureProfile } from "../../utils/models";
import type { MLSurrogateInputs } from "../../types";

interface MissionPressureProfileProps {
  inputs: MLSurrogateInputs;
  height?: number;
  ascentDurationMin?: number;
}

/**
 * The core DCS physics, drawn as a pressure "valley".
 *
 * Ambient pressure (indigo) starts at 760 mmHg on the ground, holds through
 * prebreathe, ramps down through ascent, and bottoms out at the low altitude
 * pressure. Tissue N₂ tension (amber) lags it: it can only fall so fast in the
 * prebreathe/ascent window, so when the ambient line plunges below the tissue
 * line the gap between them — shaded vermillion — is the supersaturation that
 * drives bubbles. That gap is the whole reason this model exists.
 *
 * Stacked area trick: `ambient` is the stack base (its area is the air-pressure
 * mass 0 → ambient); `gap = max(0, tissue − ambient)` stacks on top, so the
 * stacked top equals tissue exactly where the tissue rides above ambient and
 * equals ambient elsewhere. The `tissue` line is drawn unstacked on top so its
 * full trajectory stays visible even where it sits below ambient (prebreathe).
 */
export function MissionPressureProfile({
  inputs,
  height = 340,
  ascentDurationMin = 6,
}: MissionPressureProfileProps): React.ReactElement {
  const { points, phases, total } = useMemo(() => {
    const pts = missionPressureProfile(inputs, { ascentDurationMin, dtMin: 2 });
    // Phase boundaries (minutes from mission start).
    const pbEnd = inputs.prebreathingTime;
    const tot = pts.length ? pts[pts.length - 1].tMin : 1;
    return {
      points: pts,
      phases: [
        { key: "prebreathe", label: "Prebreathe · 100% O₂", dur: Math.max(0, pbEnd), color: "hsl(var(--accent))" },
        { key: "ascent", label: "Ascent", dur: Math.max(0, ascentDurationMin), color: "hsl(var(--primary))" },
        { key: "altitude", label: "Altitude · air", dur: Math.max(0, inputs.timeAtAltitude), color: "hsl(var(--signal))" },
      ],
      total: Math.max(tot, 1),
    };
  }, [inputs, ascentDurationMin]);

  const option: EChartsOption = useMemo(() => {
    const base = getBaseChartOptions();
    const ambientColor = chartTheme.primaryColor;
    const cAmbient = colorPalettes.scientific[0];
    const cTissue = colorPalettes.scientific[2]; // amber
    const cGap = colorPalettes.risk.high;

    const ambient = points.map((p) => [p.tMin, +p.pAmbMmHg.toFixed(2)]);
    const gap = points.map((p) => [p.tMin, +p.gapMmHg.toFixed(2)]);
    const tissue = points.map((p) => [p.tMin, +p.tissueN2MmHg.toFixed(2)]);

    const yMax = Math.max(820, ...points.map((p) => Math.max(p.pAmbMmHg, p.tissueN2MmHg)) || 820);

    // Phase boundary verticals as silent 2-point lines (the safe pattern used
    // by TissueN2Chart — avoids markLine/coord pitfalls in ECharts 6).
    const boundary = (t: number): SeriesOption => ({
      name: "phase-boundary",
      type: "line",
      showSymbol: false,
      silent: true,
      lineStyle: { color: withAlpha(chartTheme.axisColor, 0.5), type: "dashed", width: 1 },
      tooltip: { show: false },
      data: [
        [t, 0],
        [t, yMax],
      ],
    } as unknown as SeriesOption);

    const boundaries: SeriesOption[] = [];
    if (inputs.prebreathingTime > 0 && ascentDurationMin > 0)
      boundaries.push(boundary(inputs.prebreathingTime + ascentDurationMin));
    else if (inputs.prebreathingTime > 0)
      boundaries.push(boundary(inputs.prebreathingTime));

    const series: SeriesOption[] = [
      {
        name: "Ambient pressure",
        type: "line",
        stack: "valley",
        showSymbol: false,
        smooth: 0.1,
        lineStyle: { width: 2.2, color: ambientColor },
        itemStyle: { color: ambientColor },
        areaStyle: {
          color: {
            type: "linear",
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: withAlpha(cAmbient, 0.22) },
              { offset: 1, color: withAlpha(cAmbient, 0.02) },
            ],
          },
        },
        data: ambient,
      } as unknown as SeriesOption,
      {
        name: "Supersaturation gap",
        type: "line",
        stack: "valley",
        showSymbol: false,
        smooth: 0.1,
        lineStyle: { width: 0 },
        areaStyle: {
          color: withAlpha(cGap, 0.42),
          shadowBlur: 12,
          shadowColor: withAlpha(cGap, 0.3),
        },
        emphasis: { disabled: true },
        data: gap,
      } as unknown as SeriesOption,
      {
        name: "Tissue N₂ tension",
        type: "line",
        showSymbol: false,
        smooth: 0.15,
        lineStyle: { width: 2.6, color: cTissue },
        itemStyle: { color: cTissue },
        z: 5,
        data: tissue,
      } as unknown as SeriesOption,
      ...boundaries,
    ];

    return {
      ...base,
      animationDuration: 900,
      grid: { left: 64, right: 16, top: 28, bottom: 52, containLabel: true },
      legend: {
        ...base.legend,
        top: 4,
        right: 8,
        data: ["Ambient pressure", "Supersaturation gap", "Tissue N₂ tension"],
        textStyle: { fontSize: 11, color: chartTheme.textColor },
      },
      tooltip: {
        ...base.tooltip,
        trigger: "axis",
        axisPointer: { type: "line", lineStyle: { color: chartTheme.axisColor, type: "dashed" } },
        formatter: (params: unknown) => {
          const arr = params as Array<{ seriesName: string; value: [number, number]; color: string }>;
          const t = arr[0]?.value[0] ?? 0;
          const p = points.find((q) => Math.abs(q.tMin - t) < 1.5);
          const rows = arr
            .filter((r) => r.seriesName !== "phase-boundary")
            .map((r) => {
              const v = r.value[1];
              if (v == null) return "";
              return `<div><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${r.color};margin-right:6px"></span>${r.seriesName}: <b>${v.toFixed(0)} mmHg</b></div>`;
            })
            .join("");
          const phase = p ? `<div style="font-weight:500;margin-bottom:3px;text-transform:capitalize">${p.phase} · t = ${t.toFixed(0)} min</div>` : "";
          return `<div style="font-family:'IBM Plex Mono',monospace;font-size:11px;line-height:1.6">${phase}${rows}</div>`;
        },
      },
      xAxis: {
        ...(base.xAxis as object),
        type: "value" as const,
        min: 0,
        max: total,
        name: "Mission time (min)",
        nameLocation: "middle" as const,
        nameGap: 32,
        axisLabel: {
          color: chartTheme.axisColor,
          fontSize: 11,
          fontFamily: "IBM Plex Mono, monospace",
          formatter: (v: number) => `${Math.round(v)}`,
        },
      },
      yAxis: {
        ...(base.yAxis as object),
        type: "value" as const,
        min: 0,
        max: yMax,
        name: "Pressure (mmHg)",
        nameLocation: "middle" as const,
        nameGap: 44,
        axisLabel: {
          color: chartTheme.axisColor,
          fontSize: 11,
          fontFamily: "IBM Plex Mono, monospace",
        },
      },
      series,
    };
  }, [points, total, inputs.prebreathingTime, ascentDurationMin]);

  // Phase ribbon — proportional segments rendered in React so the chart stays clean.
  return (
    <div>
      <ReactECharts
        option={option}
        notMerge
        style={{ height: `${height}px`, width: "100%" }}
        opts={{ renderer: "canvas" }}
      />
      <div className="mt-3 flex items-stretch gap-1 h-7 text-[10px]">
        {phases.map((ph) => {
          const w = total > 0 ? (ph.dur / total) * 100 : 0;
          if (w <= 0) return null;
          return (
            <div
              key={ph.key}
              className="flex items-center justify-center rounded-md px-2 overflow-hidden whitespace-nowrap"
              style={{
                width: `${w}%`,
                background: withAlpha(ph.color, 0.14),
                color: ph.color,
                border: `1px solid ${withAlpha(ph.color, 0.28)}`,
              }}
            >
              <span className="truncate">{ph.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}