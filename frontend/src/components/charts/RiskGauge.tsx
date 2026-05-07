import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
import { chartTheme, getBaseChartOptions, getRiskGradientStops, withAlpha } from "./chartConfig";
import { formatNumber, getRiskColor, getRiskLevel } from "../../lib/utils";

interface RiskGaugeProps {
  value: number;
  title?: string;
  height?: number;
  showLabel?: boolean;
}

export function RiskGauge({
  value,
  title = "DCS Risk",
  height = 280,
  showLabel = true,
}: RiskGaugeProps): React.ReactElement {
  const riskLevel = getRiskLevel(value);
  const riskColor = getRiskColor(value);
  const stops = getRiskGradientStops();

  const option: EChartsOption = useMemo(
    () => ({
      ...getBaseChartOptions(),
      series: [
        {
          type: "gauge",
          startAngle: 210,
          endAngle: -30,
          center: ["50%", "62%"],
          radius: "82%",
          min: 0,
          max: 100,
          splitNumber: 10,
          progress: {
            show: false,
          },
          axisLine: {
            lineStyle: {
              width: 22,
              color: stops,
            },
          },
          pointer: {
            length: "62%",
            width: 4,
            offsetCenter: [0, "8%"],
            itemStyle: {
              color: riskColor,
              shadowBlur: 10,
              shadowColor: withAlpha(riskColor, 0.6),
            },
          },
          anchor: {
            show: true,
            size: 12,
            showAbove: true,
            itemStyle: {
              color: chartTheme.tooltipBg,
              borderColor: riskColor,
              borderWidth: 2,
            },
          },
          axisTick: {
            length: 6,
            distance: -22,
            lineStyle: { color: "#fff", width: 1.5 },
          },
          splitLine: {
            length: 12,
            distance: -22,
            lineStyle: { color: "#fff", width: 2 },
          },
          axisLabel: {
            color: chartTheme.textColor,
            fontSize: 10,
            fontFamily: "JetBrains Mono, monospace",
            distance: -34,
            formatter: (val: number) => {
              if (val === 0) return "0";
              if (val === 50) return "50";
              if (val === 100) return "100";
              return "";
            },
          },
          title: {
            show: showLabel,
            offsetCenter: [0, "82%"],
            fontSize: 12,
            fontWeight: 500,
            color: chartTheme.textColor,
            fontFamily: "Inter, system-ui, sans-serif",
          },
          detail: {
            valueAnimation: true,
            formatter: (val: number) => `${formatNumber(val, 2)}%`,
            fontSize: 32,
            fontWeight: 700,
            offsetCenter: [0, "32%"],
            color: riskColor,
            fontFamily: "Space Grotesk, Inter, system-ui, sans-serif",
          },
          data: [{ value: Math.max(0, Math.min(100, value)), name: title }],
        },
      ],
    }),
    [value, riskColor, showLabel, stops, title],
  );

  return (
    <div className="relative">
      <ReactECharts
        option={option}
        notMerge
        style={{ height: `${height}px`, width: "100%" }}
        opts={{ renderer: "canvas" }}
      />
      <div className="absolute bottom-1 left-1/2 -translate-x-1/2">
        <span
          className={
            riskLevel === "low"
              ? "pill-low"
              : riskLevel === "moderate"
                ? "pill-signal"
                : "pill-high"
          }
        >
          <span
            className="inline-block w-1.5 h-1.5 rounded-full animate-pulse-soft"
            style={{ background: riskColor }}
          />
          {riskLevel === "low"
            ? "Low Risk"
            : riskLevel === "moderate"
              ? "Moderate Risk"
              : "Elevated Risk"}
        </span>
      </div>
    </div>
  );
}
