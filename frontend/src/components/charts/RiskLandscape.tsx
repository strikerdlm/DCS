import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
import { chartTheme, colorPalettes, getBaseChartOptions, withAlpha } from "./chartConfig";
import type { RiskLandscapePoint } from "../../utils/models";

interface RiskLandscapeProps {
  points: RiskLandscapePoint[];
  highlight?: { altitudeFt: number; timeAtAltitudeMin: number };
  height?: number;
  title?: string;
}

export function RiskLandscape({
  points,
  highlight,
  height = 380,
  title = "Risk Landscape — altitude × time-at-altitude",
}: RiskLandscapeProps): React.ReactElement {
  const { altitudes, times, matrix } = useMemo(() => {
    const altSet = new Set<number>();
    const timeSet = new Set<number>();
    for (const p of points) {
      altSet.add(Math.round(p.altitudeFt));
      timeSet.add(Math.round(p.timeAtAltitudeMin));
    }
    const altitudes = [...altSet].sort((a, b) => a - b);
    const times = [...timeSet].sort((a, b) => a - b);
    const altIdx = new Map(altitudes.map((v, i) => [v, i]));
    const timeIdx = new Map(times.map((v, i) => [v, i]));
    const matrix: [number, number, number][] = [];
    for (const p of points) {
      const xi = timeIdx.get(Math.round(p.timeAtAltitudeMin));
      const yi = altIdx.get(Math.round(p.altitudeFt));
      if (xi !== undefined && yi !== undefined) {
        matrix.push([xi, yi, +p.riskPercent.toFixed(2)]);
      }
    }
    return { altitudes, times, matrix };
  }, [points]);

  const palette = colorPalettes.sequential.ocean;

  const highlightCell = useMemo(() => {
    if (!highlight || altitudes.length === 0 || times.length === 0) return null;
    const altClosest = altitudes.reduce((p, c) =>
      Math.abs(c - highlight.altitudeFt) < Math.abs(p - highlight.altitudeFt) ? c : p,
    );
    const timeClosest = times.reduce((p, c) =>
      Math.abs(c - highlight.timeAtAltitudeMin) < Math.abs(p - highlight.timeAtAltitudeMin) ? c : p,
    );
    return [times.indexOf(timeClosest), altitudes.indexOf(altClosest)] as [number, number];
  }, [highlight, altitudes, times]);

  const option: EChartsOption = useMemo(() => {
    const base = getBaseChartOptions();
    return {
      ...base,
      title: {
        text: title,
        left: 20,
        top: 14,
        textStyle: {
          fontSize: 13,
          fontWeight: 600,
          color: chartTheme.textColor,
          fontFamily: "Space Grotesk, Inter, system-ui, sans-serif",
        },
      },
      tooltip: {
        ...base.tooltip,
        formatter: (params: unknown) => {
          const p = params as { value: [number, number, number]; seriesName: string };
          if (p.seriesName === "Current") {
            return `<span style="font-weight:500">Current scenario</span>`;
          }
          const x = times[p.value[0]];
          const y = altitudes[p.value[1]];
          const v = p.value[2];
          const level = v < 1 ? "Low" : v < 5 ? "Moderate" : v < 20 ? "Elevated" : "High";
          return `
            <div style="font-weight:500;margin-bottom:4px">${level} risk</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:11px;line-height:1.5">
              <div>Altitude: <b>${y.toLocaleString()} ft</b></div>
              <div>Time at altitude: <b>${x} min</b></div>
              <div>P(DCS): <b>${v.toFixed(2)}%</b></div>
            </div>
          `;
        },
      },
      grid: {
        left: 80,
        right: 24,
        top: 60,
        bottom: 56,
      },
      xAxis: {
        ...(base.xAxis as object),
        type: "category" as const,
        data: times.map((t) => `${t}`),
        name: "Time at altitude (min)",
        nameLocation: "middle" as const,
        nameGap: 32,
        boundaryGap: true,
        splitArea: { show: false },
        axisLabel: {
          color: chartTheme.axisColor,
          fontSize: 10,
          interval: Math.max(0, Math.floor(times.length / 8) - 1),
          fontFamily: "JetBrains Mono, monospace",
        },
      },
      yAxis: {
        ...(base.yAxis as object),
        type: "category" as const,
        data: altitudes.map((a) => `${a.toLocaleString()}`),
        name: "Altitude (ft)",
        nameLocation: "middle" as const,
        nameGap: 60,
        boundaryGap: true,
        splitArea: { show: false },
        axisLabel: {
          color: chartTheme.axisColor,
          fontSize: 10,
          interval: Math.max(0, Math.floor(altitudes.length / 8) - 1),
          fontFamily: "JetBrains Mono, monospace",
        },
      },
      visualMap: {
        min: 0,
        max: 100,
        calculable: true,
        orient: "vertical",
        right: 16,
        top: 56,
        itemWidth: 12,
        itemHeight: 180,
        text: ["100%", "0%"],
        textStyle: { fontSize: 10, color: chartTheme.axisColor },
        inRange: { color: palette },
      },
      series: [
        {
          name: "P(DCS)",
          type: "heatmap",
          data: matrix,
          progressive: 800,
          progressiveThreshold: 800,
          emphasis: {
            itemStyle: {
              borderColor: chartTheme.textColor,
              borderWidth: 1,
            },
          },
        },
        ...(highlightCell
          ? [
              {
                name: "Current",
                type: "scatter" as const,
                symbol: "circle",
                symbolSize: 16,
                z: 10,
                itemStyle: {
                  color: chartTheme.riskHighColor,
                  borderColor: "#fff",
                  borderWidth: 3,
                  shadowBlur: 10,
                  shadowColor: withAlpha(chartTheme.riskHighColor, 0.6),
                },
                data: [highlightCell],
              },
            ]
          : []),
      ],
    };
  }, [altitudes, times, matrix, palette, title, highlightCell]);

  return (
    <ReactECharts
      option={option}
      notMerge
      style={{ height: `${height}px`, width: "100%" }}
      opts={{ renderer: "canvas" }}
    />
  );
}
