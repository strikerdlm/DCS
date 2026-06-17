import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption, SeriesOption } from "echarts";
import { chartTheme, colorPalettes, getBaseChartOptions, withAlpha } from "./chartConfig";
import { DOSE_RANGE, generateDoseResponse, predictADRAC } from "../../utils/models";
import type { DoseVariable } from "../../utils/models";
import type { ExerciseLevel, MLSurrogateInputs } from "../../types";

interface DoseResponseChartProps {
  base: MLSurrogateInputs;
  variable: DoseVariable;
  height?: number;
}

const EXERCISE_LEVELS: ExerciseLevel[] = ["Rest", "Mild", "Heavy"];

const AXIS: Record<
  DoseVariable,
  { name: string; unit: string; current: (i: MLSurrogateInputs) => number; fmt: (v: number) => string }
> = {
  time: {
    name: "Time at altitude",
    unit: "min",
    current: (i) => i.timeAtAltitude,
    fmt: (v) => `${Math.round(v)}`,
  },
  altitude: {
    name: "Altitude",
    unit: "ft",
    current: (i) => i.altitude,
    fmt: (v) => `${(v / 1000).toFixed(0)}k`,
  },
  prebreathe: {
    name: "Prebreathe",
    unit: "min",
    current: (i) => i.prebreathingTime,
    fmt: (v) => `${Math.round(v)}`,
  },
};

/**
 * ADRAC dose–response: P(DCS) vs one swept exposure variable, with the three
 * exercise levels overlaid. The currently-selected exercise is emphasised; the
 * live scenario is marked. Pure closed-form, recomputed on every input change.
 */
export function DoseResponseChart({
  base,
  variable,
  height = 360,
}: DoseResponseChartProps): React.ReactElement {
  const axis = AXIS[variable];
  const [lo, hi] = DOSE_RANGE[variable];
  const currentX = axis.current(base);
  const inRange = currentX >= lo && currentX <= hi;

  const option: EChartsOption = useMemo(() => {
    const base0 = getBaseChartOptions();
    const palette = [
      colorPalettes.scientific[0],
      colorPalettes.scientific[2],
      colorPalettes.risk.high,
    ];

    const series: SeriesOption[] = EXERCISE_LEVELS.map((level, idx) => {
      const isActive = level === base.exerciseLevel;
      const color = palette[idx];
      const data = generateDoseResponse({ base, variable, exerciseLevel: level }).map(
        (p) => [p.x, +p.riskPercent.toFixed(3)],
      );
      return {
        name: level,
        type: "line",
        showSymbol: false,
        smooth: 0.2,
        z: isActive ? 5 : 2,
        lineStyle: { width: isActive ? 3 : 1.5, color, opacity: isActive ? 1 : 0.4 },
        itemStyle: { color },
        emphasis: { focus: "series" },
        data,
      } as SeriesOption;
    });

    // Live scenario marker on the active exercise curve. Rendered as a single
    // styled symbol on the active LINE series (showSymbol stays off elsewhere)
    // rather than a separate scatter series: a 1-point scatter mixed with the
    // line series tripped an internal ECharts 6 `coord` error in the progressive
    // render path. Marking the point on the line avoids that path entirely.
    if (inRange) {
      const { riskFraction } = predictADRAC(
        base.altitude,
        base.prebreathingTime,
        base.exerciseLevel,
        base.timeAtAltitude,
      );
      const activeIdx = EXERCISE_LEVELS.indexOf(base.exerciseLevel);
      const active = series[activeIdx] as unknown as {
        markPoint?: unknown;
      };
      if (active) {
        active.markPoint = {
          symbol: "circle",
          symbolSize: 13,
          silent: true,
          itemStyle: {
            color: chartTheme.primaryColor,
            borderColor: chartTheme.tooltipBg,
            borderWidth: 2.5,
            shadowBlur: 10,
            shadowColor: withAlpha(chartTheme.primaryColor, 0.5),
          },
          label: { show: false },
          data: [{ coord: [currentX, +(riskFraction * 100).toFixed(2)] }],
        };
      }
    }

    return {
      ...base0,
      grid: { left: 64, right: 24, top: 40, bottom: 64, containLabel: true },
      legend: {
        ...base0.legend,
        top: 6,
        right: 8,
        data: EXERCISE_LEVELS.map((l) => String(l)),
      },
      tooltip: {
        ...base0.tooltip,
        trigger: "axis",
        axisPointer: { type: "line", lineStyle: { color: chartTheme.axisColor, type: "dashed" } },
        formatter: (params: unknown) => {
          const arr = params as Array<{ seriesName: string; value: [number, number]; color: string }>;
          const pts = arr.filter((p) => p.seriesName !== "Current");
          if (pts.length === 0) return "";
          const x = pts[0].value[0];
          let html = `<div style="font-weight:500;margin-bottom:4px">${axis.name} ${axis.fmt(
            x,
          )} ${axis.unit}</div><div style="font-family:'IBM Plex Mono',monospace;font-size:11px;line-height:1.6">`;
          pts.forEach((p) => {
            html += `<div><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${p.color};margin-right:6px"></span>${p.seriesName}: <b>${p.value[1].toFixed(
              2,
            )}%</b></div>`;
          });
          return html + "</div>";
        },
      },
      xAxis: {
        ...(base0.xAxis as object),
        type: "value" as const,
        min: lo,
        max: hi,
        name: `${axis.name} (${axis.unit})`,
        nameLocation: "middle" as const,
        nameGap: 34,
        axisLabel: {
          color: chartTheme.axisColor,
          fontSize: 11,
          fontFamily: "IBM Plex Mono, monospace",
          formatter: (v: number) => axis.fmt(v),
        },
      },
      yAxis: {
        ...(base0.yAxis as object),
        type: "value" as const,
        min: 0,
        name: "P(DCS) (%)",
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
  }, [base, variable, axis, lo, hi, currentX, inRange]);

  return (
    <ReactECharts
      option={option}
      notMerge
      style={{ height: `${height}px`, width: "100%" }}
      opts={{ renderer: "canvas" }}
    />
  );
}
