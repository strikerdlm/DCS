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
 * `tissue_n2_ratio_360` feature). Below 1.0 the tissue is undersaturated; the
 * line warms and crosses the dashed reference as it becomes supersaturated at
 * altitude. A vertical marker shows the (instantaneous) ascent.
 */
export function TissueN2Chart({
  inputs,
  height = 320,
}: TissueN2ChartProps): React.ReactElement {
  const option: EChartsOption = useMemo(() => {
    const base = getBaseChartOptions();
    const traj = tissueN2Trajectory(inputs);
    const data = traj.map((p) => [+p.tMin.toFixed(2), +p.ratio.toFixed(4)]);
    const maxRatio = traj.reduce((m, p) => Math.max(m, p.ratio), 0);
    const yMax = Math.max(1.2, Math.ceil(maxRatio * 10) / 10 + 0.1);
    const safe = colorPalettes.scientific[1];
    const supersat = colorPalettes.risk.high;

    const lineSeries = {
      name: "Supersaturation ratio",
      type: "line",
      showSymbol: false,
      smooth: 0.15,
      lineStyle: { width: 2.5 },
      areaStyle: {
        color: {
          type: "linear",
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: withAlpha(supersat, 0.18) },
            { offset: 1, color: withAlpha(safe, 0.02) },
          ],
        },
      },
      data,
    } as unknown as SeriesOption;

    return {
      ...base,
      grid: { left: 60, right: 20, top: 24, bottom: 56, containLabel: true },
      tooltip: {
        ...base.tooltip,
        trigger: "axis",
        axisPointer: { type: "line", lineStyle: { color: chartTheme.axisColor, type: "dashed" } },
        formatter: (params: unknown) => {
          const arr = params as Array<{ value: [number, number] }>;
          if (!Array.isArray(arr) || arr.length === 0) return "";
          const [t, r] = arr[0].value;
          const state = r >= 1 ? "supersaturated" : "undersaturated";
          return `<div style="font-family:'JetBrains Mono',monospace;font-size:11px;line-height:1.6"><div>t = <b>${t.toFixed(
            0,
          )} min</b></div><div>ratio = <b>${r.toFixed(2)}</b> (${state})</div></div>`;
        },
      },
      visualMap: {
        show: false,
        type: "piecewise",
        dimension: 1,
        seriesIndex: 0,
        pieces: [
          { lt: 1, color: safe },
          { gte: 1, color: supersat },
        ],
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
      series: [lineSeries],
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
