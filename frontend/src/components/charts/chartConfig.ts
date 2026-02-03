/**
 * ECharts Configuration for Publication-Quality Scientific Charts
 * 
 * Designed for Q1 science journal publication standards:
 * - Clear axis labels with proper scientific notation
 * - Professional color palette suitable for print
 * - High-contrast text for readability
 * - Proper grid spacing and margins
 * - Export-ready resolution settings
 * 
 * References:
 * - Nature/Science figure guidelines
 * - IEEE Visualization standards
 * - APA Publication Manual (7th edition)
 */

import type { EChartsOption } from "echarts";
import type { ChartTheme } from "../../types";

// ============================================================================
// Publication-Quality Color Palettes
// ============================================================================

export const colorPalettes = {
  // Primary palette for multi-series charts
  scientific: [
    "#2563eb", // Blue (primary)
    "#dc2626", // Red
    "#059669", // Green
    "#d97706", // Amber
    "#7c3aed", // Purple
    "#0891b2", // Cyan
    "#be185d", // Pink
    "#4b5563", // Gray
  ],
  
  // Sequential palette for continuous data
  sequential: {
    blue: ["#eff6ff", "#bfdbfe", "#93c5fd", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8", "#1e40af"],
    green: ["#f0fdf4", "#bbf7d0", "#86efac", "#4ade80", "#22c55e", "#16a34a", "#15803d", "#166534"],
    red: ["#fef2f2", "#fecaca", "#fca5a5", "#f87171", "#ef4444", "#dc2626", "#b91c1c", "#991b1b"],
  },
  
  // Diverging palette for bipolar data
  diverging: ["#1d4ed8", "#3b82f6", "#93c5fd", "#f3f4f6", "#fca5a5", "#ef4444", "#b91c1c"],
  
  // Risk-specific palette
  risk: {
    low: "#10b981",
    moderate: "#f59e0b",
    high: "#ef4444",
    veryHigh: "#991b1b",
  },
  
  // Grayscale for print compatibility
  grayscale: ["#1f2937", "#4b5563", "#6b7280", "#9ca3af", "#d1d5db", "#e5e7eb"],
};

// ============================================================================
// Chart Theme
// ============================================================================

export const chartTheme: ChartTheme = {
  backgroundColor: "#ffffff",
  textColor: "#1f2937",
  gridColor: "#e5e7eb",
  axisColor: "#4b5563",
  tooltipBg: "rgba(255, 255, 255, 0.95)",
  primaryColor: "#2563eb",
  secondaryColor: "#7c3aed",
  tertiaryColor: "#059669",
  riskLowColor: "#10b981",
  riskModerateColor: "#f59e0b",
  riskHighColor: "#ef4444",
};

// ============================================================================
// Base Chart Options (Publication-Quality Defaults)
// ============================================================================

export function getBaseChartOptions(): Partial<EChartsOption> {
  return {
    backgroundColor: "transparent",
    textStyle: {
      fontFamily: "Inter, system-ui, sans-serif",
      fontSize: 12,
      color: chartTheme.textColor,
    },
    title: {
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: chartTheme.textColor,
      },
      subtextStyle: {
        fontSize: 12,
        color: "#6b7280",
      },
    },
    tooltip: {
      backgroundColor: chartTheme.tooltipBg,
      borderColor: "#e5e7eb",
      borderWidth: 1,
      textStyle: {
        color: chartTheme.textColor,
        fontSize: 12,
      },
      padding: [12, 16],
      extraCssText: "box-shadow: 0 10px 25px -5px rgb(0 0 0 / 0.1); border-radius: 8px;",
    },
    legend: {
      textStyle: {
        fontSize: 12,
        color: chartTheme.textColor,
      },
      itemGap: 16,
      itemWidth: 16,
      itemHeight: 8,
    },
    grid: {
      left: "10%",
      right: "5%",
      top: "15%",
      bottom: "15%",
      containLabel: true,
    },
    xAxis: {
      axisLine: {
        lineStyle: {
          color: chartTheme.axisColor,
          width: 1,
        },
      },
      axisTick: {
        lineStyle: {
          color: chartTheme.axisColor,
        },
      },
      axisLabel: {
        color: chartTheme.textColor,
        fontSize: 11,
      },
      splitLine: {
        lineStyle: {
          color: chartTheme.gridColor,
          type: "dashed",
        },
      },
      nameTextStyle: {
        fontSize: 12,
        fontWeight: 500,
        color: chartTheme.textColor,
        padding: [10, 0, 0, 0],
      },
    },
    yAxis: {
      axisLine: {
        lineStyle: {
          color: chartTheme.axisColor,
          width: 1,
        },
      },
      axisTick: {
        lineStyle: {
          color: chartTheme.axisColor,
        },
      },
      axisLabel: {
        color: chartTheme.textColor,
        fontSize: 11,
      },
      splitLine: {
        lineStyle: {
          color: chartTheme.gridColor,
          type: "dashed",
        },
      },
      nameTextStyle: {
        fontSize: 12,
        fontWeight: 500,
        color: chartTheme.textColor,
        padding: [0, 0, 10, 0],
      },
    },
    animation: true,
    animationDuration: 800,
    animationEasing: "cubicOut",
  };
}

// ============================================================================
// Specialized Chart Configurations
// ============================================================================

export function getScatterChartOptions(
  title: string,
  xLabel: string,
  yLabel: string
): Partial<EChartsOption> {
  return {
    ...getBaseChartOptions(),
    title: {
      text: title,
      left: "center",
      top: 10,
    },
    xAxis: {
      type: "value" as const,
      name: xLabel,
      nameLocation: "middle" as const,
      nameGap: 35,
    },
    yAxis: {
      type: "value" as const,
      name: yLabel,
      nameLocation: "middle" as const,
      nameGap: 45,
    },
    toolbox: {
      feature: {
        dataZoom: { show: true },
        saveAsImage: { 
          show: true, 
          pixelRatio: 3,
          title: "Save as PNG",
        },
        dataView: { show: true },
      },
      right: 20,
      top: 10,
    },
  };
}

export function getTimeSeriesOptions(
  _title: string,
  _yLabels: string[]
): Partial<EChartsOption> {
  return {
    ...getBaseChartOptions(),
    dataZoom: [
      {
        type: "inside",
        start: 0,
        end: 100,
      },
      {
        type: "slider",
        start: 0,
        end: 100,
        bottom: 40,
      },
    ],
    toolbox: {
      feature: {
        saveAsImage: { 
          show: true, 
          pixelRatio: 3,
          title: "Save as PNG",
        },
        dataZoom: { show: true },
        restore: { show: true },
      },
      right: 20,
      top: 10,
    },
  };
}

export function getHeatmapOptions(
  _title: string,
  _xLabel: string,
  _yLabel: string
): Partial<EChartsOption> {
  return {
    ...getBaseChartOptions(),
  };
}

export function getHistogramOptions(
  _title: string,
  _xLabel: string
): Partial<EChartsOption> {
  return {
    ...getBaseChartOptions(),
  };
}

// ============================================================================
// Risk Gradient for Gauges
// ============================================================================

export function getRiskGradientColors(value: number): string[] {
  if (value < 5) return [chartTheme.riskLowColor, "#34d399"];
  if (value < 15) return [chartTheme.riskModerateColor, "#fbbf24"];
  return [chartTheme.riskHighColor, "#f87171"];
}

export function getGaugeChartOptions(
  title: string,
  value: number,
  maxValue: number = 100
): Partial<EChartsOption> {
  const colors = getRiskGradientColors(value);
  
  return {
    ...getBaseChartOptions(),
    title: {
      text: title,
      left: "center",
      top: 10,
    },
    series: [
      {
        type: "gauge",
        startAngle: 200,
        endAngle: -20,
        center: ["50%", "60%"],
        radius: "80%",
        min: 0,
        max: maxValue,
        splitNumber: 10,
        axisLine: {
          lineStyle: {
            width: 20,
            color: [
              [0.05, chartTheme.riskLowColor],
              [0.15, chartTheme.riskModerateColor],
              [1, chartTheme.riskHighColor],
            ],
          },
        },
        pointer: {
          length: "70%",
          width: 6,
          itemStyle: {
            color: "auto",
          },
        },
        axisTick: {
          length: 8,
          lineStyle: {
            color: "auto",
            width: 1.5,
          },
        },
        splitLine: {
          length: 15,
          lineStyle: {
            color: "auto",
            width: 2,
          },
        },
        axisLabel: {
          color: chartTheme.textColor,
          fontSize: 11,
          distance: 25,
        },
        title: {
          show: true,
          offsetCenter: [0, "85%"],
          fontSize: 14,
          color: chartTheme.textColor,
        },
        detail: {
          valueAnimation: true,
          formatter: "{value}%",
          fontSize: 28,
          fontWeight: 700,
          offsetCenter: [0, "40%"],
          color: colors[0],
        },
        data: [{ value, name: "DCS Risk" }],
      },
    ],
  };
}
