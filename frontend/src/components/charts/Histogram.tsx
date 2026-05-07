import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
import { getBaseChartOptions, colorPalettes, chartTheme } from "./chartConfig";
import { safeMax, safeMin } from "../../lib/utils";
import type { ValidationDataPoint } from "../../types";

interface HistogramProps {
  data: ValidationDataPoint[];
  dataKey: keyof ValidationDataPoint;
  groupKey?: keyof ValidationDataPoint;
  title: string;
  xLabel: string;
  height?: number;
  bins?: number;
}

export function Histogram({
  data,
  dataKey,
  groupKey,
  title,
  xLabel,
  height = 400,
  bins = 40,
}: HistogramProps): React.ReactElement {
  const { series, groups, binEdges } = useMemo(() => {
    // Extract values (use reduce-backed safeMin/safeMax — spread blows up on large arrays)
    const values = data.map((d) => Number(d[dataKey])).filter(Number.isFinite);
    const min = safeMin(values);
    const maxRaw = safeMax(values);
    const max = maxRaw === min ? min + 1 : maxRaw;
    const binWidth = Math.max((max - min) / bins, 1e-12);

    // Create bin edges
    const edges: number[] = [];
    for (let i = 0; i <= bins; i++) {
      edges.push(min + i * binWidth);
    }

    // Group data if groupKey is provided
    const grouped: Record<string, number[]> = {};
    if (groupKey) {
      for (const point of data) {
        const group = String(point[groupKey] ?? "default");
        const value = Number(point[dataKey]);
        if (!Number.isFinite(value)) continue;
        if (!grouped[group]) {
          grouped[group] = [];
        }
        grouped[group].push(value);
      }
    } else {
      grouped["All"] = values;
    }

    const groupNames = Object.keys(grouped);

    // Calculate histogram for each group
    const series = groupNames.map((group, idx) => {
      const groupValues = grouped[group];
      const counts = Array(bins).fill(0);

      for (const value of groupValues) {
        const binIdx = Math.min(Math.floor((value - min) / binWidth), bins - 1);
        counts[binIdx]++;
      }

      return {
        name: group,
        type: "bar" as const,
        barGap: "0%",
        barCategoryGap: "10%",
        data: counts.map((count) => ({
          value: count,
          itemStyle: {
            color: colorPalettes.scientific[idx % colorPalettes.scientific.length],
            opacity: 0.7,
          },
        })),
        emphasis: {
          itemStyle: {
            opacity: 1,
          },
        },
      };
    });

    return { series, groups: groupNames, binEdges: edges };
  }, [data, dataKey, groupKey, bins]);

  // Create x-axis labels
  const xAxisLabels = binEdges.slice(0, -1).map((edge, i) => {
    const next = binEdges[i + 1];
    const center = (edge + next) / 2;
    return center.toFixed(1);
  });

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
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
      backgroundColor: chartTheme.tooltipBg,
      borderColor: "#e5e7eb",
      textStyle: {
        fontSize: 11,
        color: chartTheme.textColor,
      },
      formatter: (params: unknown) => {
        const p = params as Array<{
          seriesName: string;
          value: number;
          axisValue: string;
          color: string;
        }>;
        if (!Array.isArray(p) || p.length === 0) return "";
        const binIdx = parseInt(p[0].axisValue);
        const binStart = binEdges[binIdx]?.toFixed(2) ?? "?";
        const binEnd = binEdges[binIdx + 1]?.toFixed(2) ?? "?";

        let html = `<div class="font-medium mb-1">${xLabel}: ${binStart} to ${binEnd}</div>`;
        p.forEach((item) => {
          html += `<div class="flex items-center gap-2 text-xs">
            <span style="background:${item.color};" class="w-2 h-2 rounded-full"></span>
            ${item.seriesName}: <span class="font-mono">${item.value}</span>
          </div>`;
        });
        return html;
      },
    },
    legend: groups.length > 1 ? {
      data: groups,
      bottom: 10,
      type: "scroll",
      textStyle: {
        fontSize: 11,
      },
    } : undefined,
    grid: {
      left: "10%",
      right: "5%",
      top: "15%",
      bottom: groups.length > 1 ? "18%" : "12%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: xAxisLabels,
      name: xLabel,
      nameLocation: "middle",
      nameGap: 35,
      nameTextStyle: {
        fontSize: 12,
        fontWeight: 500,
        color: chartTheme.textColor,
      },
      axisLabel: {
        fontSize: 9,
        color: chartTheme.textColor,
        rotate: 45,
        interval: Math.floor(bins / 10),
      },
      axisLine: {
        lineStyle: { color: chartTheme.axisColor },
      },
    },
    yAxis: {
      type: "value",
      name: "Frequency",
      nameLocation: "middle",
      nameGap: 45,
      nameTextStyle: {
        fontSize: 12,
        fontWeight: 500,
        color: chartTheme.textColor,
      },
      axisLabel: {
        fontSize: 10,
        color: chartTheme.textColor,
      },
      axisLine: {
        lineStyle: { color: chartTheme.axisColor },
      },
      splitLine: {
        lineStyle: { color: chartTheme.gridColor, type: "dashed" },
      },
    },
    series,
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
