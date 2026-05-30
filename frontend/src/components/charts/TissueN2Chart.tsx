import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption, SeriesOption } from "echarts";
import { chartTheme, colorPalettes, getBaseChartOptions, withAlpha } from "./chartConfig";
import { tissueN2Trajectory } from "../../utils/models";
import type { MLSurrogateInputs } from "../../types";

interface TissueN2ChartProps {
  inputs: MLSurrogateInputs;
  height?: number;
}

/**
 * Tissue N₂ supersaturation ratio over the exposure (the trajectory behind the
 * `tissue_n2_ratio_360` feature). The trace is split at the ratio = 1 line: the
 * undersaturated portion is cool, the supersaturated portion warm. A dashed
 * reference marks the supersaturation threshold.
 *
 * Important: a line series whose y-values are *entirely* null (e.g. an exposure
 * that is supersaturated for its whole duration, so the "undersaturated" series
 * has no points) crashes ECharts 6's progressive render path with an internal
 * `coord` TypeError. So each colour band is only emitted when it actually has a
 * data point — never an all-null series. visualMap / markLine are avoided for
 * the same family of reasons.
 */
export function TissueN2Chart({
  inputs,
  height = 320,
}: TissueN2ChartProps): React.ReactElement {
  const option: EChartsOption = useMemo(() => {
    const base = getBaseChartOptions();
    const traj = tissueN2Trajectory(inputs);
    const safe = colorPalettes.scientific[1];
    const supersat = colorPalettes.risk.high;

    // One value per series per x; the inactive band is null so the two colours
    // never overlap. Points at/over 1 belong to the warm "supersaturated" band
    // so it owns the threshold crossing.
    const undersat: (number | null)[][] = [];
    const over: (number | null)[][] = [];
    let nUnder = 0;
    let nOver = 0;
    for (const p of traj) {
      const x = +p.tMin.toFixed(2);
      const r = +p.ratio.toFixed(4);
      if (r < 1) {
        undersat.push([x, r]);
        over.push([x, null]);
        nUnder++;
      } else {
        undersat.push([x, null]);
        over.push([x, r]);
        nOver++;
      }
    }
    const maxRatio = traj.reduce((m, p) => Math.max(m, p.ratio), 0);
    const yMax = Math.max(1.2, Math.ceil(maxRatio * 10) / 10 + 0.1);

    const mkLine = (name: string, color: string, data: (number | null)[][], withArea: boolean) =>
      ({
        name,
        type: "line",
        showSymbol: false,
        smooth: 0.15,
        connectNulls: false,
        lineStyle: { width: 2.5, color },
        itemStyle: { color },
        ...(withArea
          ? {
              areaStyle: {
                color: {
                  type: "linear",
                  x: 0,
                  y: 0,
                  x2: 0,
                  y2: 1,
                  colorStops: [
                    { offset: 0, color: withAlpha(color, 0.18) },
                    { offset: 1, color: withAlpha(color, 0.01) },
                  ],
                },
              },
            }
          : {}),
        data,
      }) as unknown as SeriesOption;

    // Threshold reference (ratio = 1) as a plain 2-point line spanning the axis.
    const tEnd = traj.length ? traj[traj.length - 1].tMin : 1;
    const refLine = {
      name: "threshold",
      type: "line",
      showSymbol: false,
      silent: true,
      lineStyle: { color: withAlpha(chartTheme.axisColor, 0.55), type: "dashed", width: 1 },
      tooltip: { show: false },
      data: [
        [0, 1],
        [+tEnd.toFixed(2), 1],
      ],
    } as unknown as SeriesOption;

    // Only include a band series when it has real points — never an all-null
    // series (that is what trips the progressive-render `coord` crash).
    const series: SeriesOption[] = [];
    if (nUnder > 0) series.push(mkLine("undersaturated", safe, undersat, false));
    if (nOver > 0) series.push(mkLine("supersaturated", supersat, over, true));
    series.push(refLine);

    return {
      ...base,
      grid: { left: 60, right: 20, top: 24, bottom: 56, containLabel: true },
      tooltip: {
        ...base.tooltip,
        trigger: "axis",
        axisPointer: { type: "line", lineStyle: { color: chartTheme.axisColor, type: "dashed" } },
        formatter: (params: unknown) => {
          const arr = (params as Array<{ value: [number, number] }>).filter(
            (p) => Array.isArray(p.value) && p.value[1] != null,
          );
          if (arr.length === 0) return "";
          const [t, r] = arr[0].value;
          const stateText = r >= 1 ? "supersaturated" : "undersaturated";
          return `<div style="font-family:'JetBrains Mono',monospace;font-size:11px;line-height:1.6"><div>t = <b>${t.toFixed(
            0,
          )} min</b></div><div>ratio = <b>${r.toFixed(2)}</b> (${stateText})</div></div>`;
        },
      },
      xAxis: {
        ...(base.xAxis as object),
        type: "value" as const,
        min: 0,
        name: "Time (min)",
        nameLocation: "middle" as const,
        nameGap: 32,
        axisLabel: {
          color: chartTheme.axisColor,
          fontSize: 11,
          fontFamily: "JetBrains Mono, monospace",
        },
      },
      yAxis: {
        ...(base.yAxis as object),
        type: "value" as const,
        min: 0,
        max: yMax,
        name: "Tissue N₂ / ambient",
        nameLocation: "middle" as const,
        nameGap: 40,
        axisLabel: {
          color: chartTheme.axisColor,
          fontSize: 11,
          fontFamily: "JetBrains Mono, monospace",
        },
      },
      series,
    };
  }, [inputs]);

  return (
    <ReactECharts
      option={option}
      notMerge
      style={{ height: `${height}px`, width: "100%" }}
      opts={{ renderer: "canvas" }}
    />
  );
}
