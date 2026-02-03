import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
import { getScatterChartOptions, colorPalettes } from "./chartConfig";
import type { ValidationDataPoint } from "../../types";

interface ScatterPlotProps {
  data: ValidationDataPoint[];
  xKey: keyof ValidationDataPoint;
  yKey: keyof ValidationDataPoint;
  colorKey?: keyof ValidationDataPoint;
  title: string;
  xLabel: string;
  yLabel: string;
  height?: number;
  showDiagonal?: boolean;
}

export function ScatterPlot({
  data,
  xKey,
  yKey,
  colorKey = "exerciseLevel",
  title,
  xLabel,
  yLabel,
  height = 500,
  showDiagonal = false,
}: ScatterPlotProps): React.ReactElement {
  const { seriesData, groups, minMax } = useMemo(() => {
    const grouped: Record<string, Array<[number, number, ValidationDataPoint]>> = {};
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;

    for (const point of data) {
      const x = Number(point[xKey]);
      const y = Number(point[yKey]);
      const group = String(point[colorKey] ?? "default");

      if (!grouped[group]) {
        grouped[group] = [];
      }
      grouped[group].push([x, y, point]);

      minX = Math.min(minX, x);
      maxX = Math.max(maxX, x);
      minY = Math.min(minY, y);
      maxY = Math.max(maxY, y);
    }

    return {
      seriesData: grouped,
      groups: Object.keys(grouped),
      minMax: { minX, maxX, minY, maxY },
    };
  }, [data, xKey, yKey, colorKey]);

  const series: EChartsOption["series"] = groups.map((group, index) => ({
    name: group,
    type: "scatter" as const,
    symbolSize: 8,
    itemStyle: {
      color: colorPalettes.scientific[index % colorPalettes.scientific.length],
      opacity: 0.7,
    },
    emphasis: {
      scale: 1.5,
      itemStyle: {
        opacity: 1,
        shadowBlur: 10,
        shadowColor: "rgba(0,0,0,0.2)",
      },
    },
    data: seriesData[group].map(([x, y, point]) => ({
      value: [x, y],
      name: point.exerciseLevel,
    })),
  }));

  // Add diagonal y=x line if requested
  if (showDiagonal) {
    const diagonalMin = Math.min(minMax.minX, minMax.minY);
    const diagonalMax = Math.max(minMax.maxX, minMax.maxY);
    (series as unknown[]).push({
      name: "y = x",
      type: "line",
      symbolSize: 0,
      lineStyle: {
        color: "#374151",
        width: 2,
        type: "dashed",
      },
      itemStyle: {
        color: "#374151",
        opacity: 1,
      },
      data: [
        [diagonalMin, diagonalMin],
        [diagonalMax, diagonalMax],
      ],
    });
  }

  const option: EChartsOption = {
    ...getScatterChartOptions(title, xLabel, yLabel),
    legend: {
      data: groups,
      bottom: 10,
      type: "scroll",
      textStyle: {
        fontSize: 11,
      },
    },
    grid: {
      left: "10%",
      right: "5%",
      top: "12%",
      bottom: "18%",
    },
    tooltip: {
      ...getScatterChartOptions(title, xLabel, yLabel).tooltip,
      formatter: (params: unknown) => {
        const p = params as { value: [number, number]; data?: { point?: ValidationDataPoint } };
        const point = p.data?.point;
        if (!point) {
          return `${xLabel}: ${p.value[0].toFixed(2)}<br/>${yLabel}: ${p.value[1].toFixed(2)}`;
        }
        return `
          <div class="font-medium mb-1">${point.exerciseLevel}</div>
          <div class="text-xs space-y-0.5">
            <div>${xLabel}: <span class="font-mono">${p.value[0].toFixed(2)}</span></div>
            <div>${yLabel}: <span class="font-mono">${p.value[1].toFixed(2)}</span></div>
            ${point.altitude !== undefined ? `<div>Altitude: <span class="font-mono">${point.altitude.toLocaleString()} ft</span></div>` : ""}
            ${point.absError !== undefined ? `<div>Abs Error: <span class="font-mono">${point.absError.toFixed(3)} pp</span></div>` : ""}
          </div>
        `;
      },
    },
    series,
  };

  return (
    <ReactECharts
      option={option}
      style={{ height: `${height}px`, width: "100%" }}
      opts={{ renderer: "canvas" }}
    />
  );
}
