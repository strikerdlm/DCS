import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
import { getBaseChartOptions, chartTheme } from "./chartConfig";
import { safeMax, safeMin } from "../../lib/utils";
import type { ValidationDataPoint } from "../../types";

interface HeatmapProps {
  data: ValidationDataPoint[];
  xKey: keyof ValidationDataPoint;
  yKey: keyof ValidationDataPoint;
  valueKey: keyof ValidationDataPoint;
  title: string;
  xLabel: string;
  yLabel: string;
  valueLabel: string;
  height?: number;
  bins?: number;
}

export function Heatmap({
  data,
  xKey,
  yKey,
  valueKey,
  title,
  xLabel,
  yLabel,
  valueLabel,
  height = 500,
  bins = 12,
}: HeatmapProps): React.ReactElement {
  const { heatmapData, xBins, yBins, minValue, maxValue } = useMemo(() => {
    // Calculate bin edges (reduce, not spread, to avoid stack overflow on large arrays)
    const xValues = data.map((d) => Number(d[xKey]));
    const yValues = data.map((d) => Number(d[yKey]));

    const xMin = safeMin(xValues);
    const xMaxRaw = safeMax(xValues);
    const yMin = safeMin(yValues);
    const yMaxRaw = safeMax(yValues);
    // Guard against degenerate (zero-range) axes
    const xMax = xMaxRaw === xMin ? xMin + 1 : xMaxRaw;
    const yMax = yMaxRaw === yMin ? yMin + 1 : yMaxRaw;

    const xStep = Math.max((xMax - xMin) / bins, 1e-12);
    const yStep = Math.max((yMax - yMin) / bins, 1e-12);

    const xBinEdges: number[] = [];
    const yBinEdges: number[] = [];
    for (let i = 0; i <= bins; i++) {
      xBinEdges.push(xMin + i * xStep);
      yBinEdges.push(yMin + i * yStep);
    }

    // Bin labels
    const xBinLabels = xBinEdges.slice(0, -1).map((v, i) => {
      const next = xBinEdges[i + 1];
      return `${Math.round(v)}-${Math.round(next)}`;
    });
    const yBinLabels = yBinEdges.slice(0, -1).map((v, i) => {
      const next = yBinEdges[i + 1];
      return `${Math.round(v)}-${Math.round(next)}`;
    });

    // Aggregate data into bins
    const binCounts: number[][] = Array.from({ length: bins }, () =>
      Array(bins).fill(0)
    );
    const binSums: number[][] = Array.from({ length: bins }, () =>
      Array(bins).fill(0)
    );

    for (const point of data) {
      const x = Number(point[xKey]);
      const y = Number(point[yKey]);
      const value = Number(point[valueKey]);

      if (!Number.isFinite(x) || !Number.isFinite(y) || !Number.isFinite(value)) {
        continue;
      }

      const xBinIdx = Math.min(
        Math.floor((x - xMin) / xStep),
        bins - 1
      );
      const yBinIdx = Math.min(
        Math.floor((y - yMin) / yStep),
        bins - 1
      );

      binCounts[yBinIdx][xBinIdx]++;
      binSums[yBinIdx][xBinIdx] += value;
    }

    // Calculate mean values
    const heatmapData: Array<[number, number, number | null]> = [];
    let minVal = Infinity;
    let maxVal = -Infinity;

    for (let y = 0; y < bins; y++) {
      for (let x = 0; x < bins; x++) {
        const count = binCounts[y][x];
        const mean = count > 0 ? binSums[y][x] / count : null;
        heatmapData.push([x, y, mean]);
        if (mean !== null) {
          minVal = Math.min(minVal, mean);
          maxVal = Math.max(maxVal, mean);
        }
      }
    }

    return {
      heatmapData,
      xBins: xBinLabels,
      yBins: yBinLabels,
      minValue: minVal === Infinity ? 0 : minVal,
      maxValue: maxVal === -Infinity ? 1 : maxVal,
    };
  }, [data, xKey, yKey, valueKey, bins]);

  const option: EChartsOption = {
    ...getBaseChartOptions(),
    title: {
      text: title,
      left: "center",
      top: 10,
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: chartTheme.textColor,
      },
    },
    tooltip: {
      position: "top",
      backgroundColor: chartTheme.tooltipBg,
      borderColor: "#e5e7eb",
      textStyle: {
        fontSize: 11,
        color: chartTheme.textColor,
      },
      formatter: (params: unknown) => {
        const p = params as { value: [number, number, number | null]; name: string };
        if (p.value[2] === null) {
          return "No data";
        }
        return `
          <div class="font-medium mb-1">${valueLabel}</div>
          <div class="text-xs">
            <div>${xLabel}: ${xBins[p.value[0]]}</div>
            <div>${yLabel}: ${yBins[p.value[1]]}</div>
            <div>Mean: <span class="font-mono">${p.value[2].toFixed(3)}</span></div>
          </div>
        `;
      },
    },
    grid: {
      left: "15%",
      right: "15%",
      top: "15%",
      bottom: "15%",
      containLabel: false,
    },
    xAxis: {
      type: "category",
      data: xBins,
      name: xLabel,
      nameLocation: "middle",
      nameGap: 40,
      nameTextStyle: {
        fontSize: 12,
        fontWeight: 500,
        color: chartTheme.textColor,
      },
      axisLabel: {
        fontSize: 9,
        rotate: 45,
        color: chartTheme.textColor,
      },
      splitArea: {
        show: true,
      },
    },
    yAxis: {
      type: "category",
      data: yBins,
      name: yLabel,
      nameLocation: "middle",
      nameGap: 60,
      nameTextStyle: {
        fontSize: 12,
        fontWeight: 500,
        color: chartTheme.textColor,
      },
      axisLabel: {
        fontSize: 9,
        color: chartTheme.textColor,
      },
      splitArea: {
        show: true,
      },
    },
    visualMap: {
      min: minValue,
      max: maxValue,
      calculable: true,
      orient: "vertical",
      right: 10,
      top: "middle",
      text: ["High", "Low"],
      textStyle: {
        fontSize: 11,
        color: chartTheme.textColor,
      },
      inRange: {
        color: [
          "#f0f9ff",
          "#bae6fd",
          "#7dd3fc",
          "#38bdf8",
          "#0ea5e9",
          "#0284c7",
          "#0369a1",
          "#075985",
        ],
      },
    },
    series: [
      {
        name: valueLabel,
        type: "heatmap",
        data: heatmapData.filter((d) => d[2] !== null),
        label: {
          show: false,
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: "rgba(0, 0, 0, 0.3)",
          },
        },
      },
    ],
    toolbox: {
      feature: {
        saveAsImage: {
          show: true,
          pixelRatio: 3,
          title: "Save as PNG",
        },
      },
      right: 20,
      top: 10,
    },
  };

  return (
    <ReactECharts
      option={option}
      style={{ height: `${height}px`, width: "100%" }}
      opts={{ renderer: "canvas" }}
    />
  );
}
