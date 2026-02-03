import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption, SeriesOption } from "echarts";
import { getBaseChartOptions, colorPalettes, chartTheme } from "./chartConfig";
import type { ModelState } from "../../types";

interface TimeSeriesChartProps {
  data: ModelState[];
  height?: number;
  title?: string;
}

interface SubplotConfig {
  key: keyof ModelState;
  name: string;
  unit: string;
  color: string;
  yAxisIndex: number;
}

export function TimeSeriesChart({
  data,
  height = 800,
  title = "Mechanistic 3RUT-MBe1 Simulation Results",
}: TimeSeriesChartProps): React.ReactElement {
  const subplots: SubplotConfig[] = [
    { key: "pAmbAtm", name: "Ambient Pressure", unit: "atm", color: colorPalettes.scientific[0], yAxisIndex: 0 },
    { key: "pDcs", name: "P(DCS)", unit: "%", color: colorPalettes.scientific[1], yAxisIndex: 1 },
    { key: "ptN2Atm", name: "Tissue N₂", unit: "atm", color: colorPalettes.scientific[2], yAxisIndex: 2 },
    { key: "ptO2Atm", name: "Tissue O₂", unit: "atm", color: colorPalettes.scientific[3], yAxisIndex: 3 },
    { key: "nB", name: "Bubble Number", unit: "", color: colorPalettes.scientific[4], yAxisIndex: 4 },
    { key: "hPerMin", name: "Hazard Rate", unit: "1/min", color: colorPalettes.scientific[5], yAxisIndex: 5 },
  ];

  const { series, gridConfigs, yAxisConfigs, xAxisConfigs } = useMemo(() => {
    const series: SeriesOption[] = [];
    const gridConfigs: EChartsOption["grid"] = [];
    const yAxisConfigs: EChartsOption["yAxis"] = [];
    const xAxisConfigs: EChartsOption["xAxis"] = [];

    const gridHeight = 12; // percentage
    const gridGap = 3;
    const rows = 3;
    const cols = 2;

    subplots.forEach((subplot, index) => {
      const row = Math.floor(index / cols);
      const col = index % cols;

      const left = col === 0 ? "8%" : "58%";
      const top = `${10 + row * (gridHeight + gridGap) * 2}%`;
      const width = "35%";
      const gridHeightStr = `${gridHeight * 1.5}%`;

      gridConfigs.push({
        left,
        top,
        width,
        height: gridHeightStr,
        containLabel: false,
      });

      xAxisConfigs.push({
        type: "value",
        gridIndex: index,
        axisLabel: {
          show: row === rows - 1,
          fontSize: 10,
          color: chartTheme.textColor,
        },
        axisLine: {
          lineStyle: { color: chartTheme.axisColor },
        },
        splitLine: {
          lineStyle: { color: chartTheme.gridColor, type: "dashed" },
        },
        name: row === rows - 1 ? "Time (min)" : "",
        nameLocation: "middle",
        nameGap: 25,
        nameTextStyle: {
          fontSize: 11,
          color: chartTheme.textColor,
        },
      });

      yAxisConfigs.push({
        type: "value",
        gridIndex: index,
        name: subplot.name,
        nameLocation: "middle",
        nameGap: 40,
        nameTextStyle: {
          fontSize: 11,
          fontWeight: 500,
          color: chartTheme.textColor,
        },
        axisLabel: {
          fontSize: 9,
          color: chartTheme.textColor,
          formatter: (value: number) => {
            if (Math.abs(value) < 0.001 && value !== 0) {
              return value.toExponential(1);
            }
            if (Math.abs(value) >= 1000) {
              return value.toExponential(1);
            }
            return value.toFixed(value < 1 ? 3 : 1);
          },
        },
        axisLine: {
          lineStyle: { color: chartTheme.axisColor },
        },
        splitLine: {
          lineStyle: { color: chartTheme.gridColor, type: "dashed" },
        },
      });

      const seriesData = data.map((state) => {
        const value = subplot.key === "pDcs" 
          ? (state[subplot.key] as number) * 100 
          : (state[subplot.key] as number);
        return [state.tMin, value];
      });

      series.push({
        name: subplot.name,
        type: "line",
        xAxisIndex: index,
        yAxisIndex: index,
        data: seriesData,
        smooth: 0.3,
        symbol: "none",
        lineStyle: {
          width: 2,
          color: subplot.color,
        },
        itemStyle: {
          color: subplot.color,
        },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: `${subplot.color}33` },
              { offset: 1, color: `${subplot.color}00` },
            ],
          },
        },
      });
    });

    return { series, gridConfigs, yAxisConfigs, xAxisConfigs };
  }, [data]);

  const option: EChartsOption = {
    ...getBaseChartOptions(),
    title: {
      text: title,
      left: "center",
      top: 5,
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: chartTheme.textColor,
      },
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
        lineStyle: {
          color: chartTheme.primaryColor,
          width: 1,
          type: "dashed",
        },
      },
      backgroundColor: chartTheme.tooltipBg,
      borderColor: "#e5e7eb",
      textStyle: {
        fontSize: 11,
        color: chartTheme.textColor,
      },
      formatter: (params: unknown) => {
        const p = params as Array<{ seriesName: string; value: [number, number]; color: string }>;
        if (!Array.isArray(p) || p.length === 0) return "";
        const time = p[0].value[0];
        let html = `<div class="font-medium mb-1">Time: ${time.toFixed(2)} min</div>`;
        p.forEach((item) => {
          html += `<div class="flex items-center gap-2 text-xs">
            <span style="background:${item.color};" class="w-2 h-2 rounded-full"></span>
            ${item.seriesName}: <span class="font-mono">${item.value[1].toPrecision(4)}</span>
          </div>`;
        });
        return html;
      },
    },
    legend: {
      data: subplots.map((s) => s.name),
      bottom: 5,
      type: "scroll",
      textStyle: {
        fontSize: 11,
      },
    },
    grid: gridConfigs,
    xAxis: xAxisConfigs,
    yAxis: yAxisConfigs,
    series,
    toolbox: {
      feature: {
        saveAsImage: {
          show: true,
          pixelRatio: 3,
          title: "Save as PNG",
        },
        dataZoom: {
          show: true,
          title: {
            zoom: "Area Zoom",
            back: "Reset Zoom",
          },
        },
        restore: {
          show: true,
          title: "Restore",
        },
      },
      right: 20,
      top: 10,
    },
    dataZoom: [
      {
        type: "inside",
        xAxisIndex: [0, 1, 2, 3, 4, 5],
        start: 0,
        end: 100,
      },
    ],
  };

  return (
    <ReactECharts
      option={option}
      style={{ height: `${height}px`, width: "100%" }}
      opts={{ renderer: "canvas" }}
    />
  );
}
