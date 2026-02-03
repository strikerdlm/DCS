import React from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
import { getBaseChartOptions, chartTheme } from "./chartConfig";
import { formatNumber, getRiskLevel, getRiskColor } from "../../lib/utils";

interface RiskGaugeProps {
  value: number;
  title?: string;
  height?: number;
  showLabel?: boolean;
}

export function RiskGauge({
  value,
  title = "DCS Risk",
  height = 300,
  showLabel = true,
}: RiskGaugeProps): React.ReactElement {
  const riskLevel = getRiskLevel(value);
  const riskColor = getRiskColor(value);

  const option: EChartsOption = {
    ...getBaseChartOptions(),
    series: [
      {
        type: "gauge",
        startAngle: 200,
        endAngle: -20,
        center: ["50%", "60%"],
        radius: "85%",
        min: 0,
        max: 100,
        splitNumber: 10,
        axisLine: {
          lineStyle: {
            width: 25,
            color: [
              [0.05, chartTheme.riskLowColor],
              [0.15, chartTheme.riskModerateColor],
              [1, chartTheme.riskHighColor],
            ],
          },
        },
        pointer: {
          icon: "path://M12.8,0.7l12,40.1H0.7L12.8,0.7z",
          length: "55%",
          width: 12,
          offsetCenter: [0, "-15%"],
          itemStyle: {
            color: "auto",
          },
        },
        axisTick: {
          length: 10,
          distance: 5,
          lineStyle: {
            color: "auto",
            width: 1.5,
          },
        },
        splitLine: {
          length: 18,
          distance: 5,
          lineStyle: {
            color: "auto",
            width: 2.5,
          },
        },
        axisLabel: {
          color: chartTheme.textColor,
          fontSize: 12,
          fontWeight: 500,
          distance: 30,
          formatter: (val: number) => {
            if (val === 0) return "0%";
            if (val === 50) return "50%";
            if (val === 100) return "100%";
            return "";
          },
        },
        title: {
          show: showLabel,
          offsetCenter: [0, "80%"],
          fontSize: 14,
          fontWeight: 500,
          color: chartTheme.textColor,
        },
        detail: {
          valueAnimation: true,
          formatter: (val: number) => `${formatNumber(val, 2)}%`,
          fontSize: 32,
          fontWeight: 700,
          offsetCenter: [0, "30%"],
          color: riskColor,
        },
        data: [{ value: Math.round(value * 100) / 100, name: title }],
      },
      // Background ring
      {
        type: "gauge",
        startAngle: 200,
        endAngle: -20,
        center: ["50%", "60%"],
        radius: "70%",
        min: 0,
        max: 100,
        itemStyle: {
          color: "#f3f4f6",
        },
        progress: {
          show: true,
          width: 8,
          itemStyle: {
            color: riskColor,
          },
        },
        pointer: {
          show: false,
        },
        axisLine: {
          lineStyle: {
            width: 8,
            color: [[1, "#f3f4f6"]],
          },
        },
        axisTick: {
          show: false,
        },
        splitLine: {
          show: false,
        },
        axisLabel: {
          show: false,
        },
        detail: {
          show: false,
        },
        data: [{ value: value }],
      },
    ],
  };

  return (
    <div className="relative">
      <ReactECharts
        option={option}
        style={{ height: `${height}px`, width: "100%" }}
        opts={{ renderer: "canvas" }}
      />
      {/* Risk level badge */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium ${
            riskLevel === "low"
              ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300"
              : riskLevel === "moderate"
                ? "bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300"
                : "bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300"
          }`}
        >
          {riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)} Risk
        </span>
      </div>
    </div>
  );
}
