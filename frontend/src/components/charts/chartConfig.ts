/**
 * ECharts 6.x configuration for the DCS Safety Dashboard.
 *
 * Mirrors the publication-figure style produced by
 * scripts/09_make_paper_figures.py and artifacts/paper_figures/* so
 * the in-browser dashboard reads as the same visual language as the
 * exported research figures.
 *
 * Palette: Okabe-Ito-derived colorblind-safe ramp resolved at runtime
 * from CSS custom properties so light / dark themes stay in sync with
 * the rest of the design system. All chart series colors are 8-stop
 * deterministic; sequential and diverging ramps are listed below.
 */

import type { EChartsOption } from "echarts";
import type { ChartTheme } from "../../types";

type SchemeName =
  | "background"
  | "foreground"
  | "muted"
  | "border"
  | "grid"
  | "primary"
  | "accent"
  | "card"
  | "risk-low"
  | "risk-moderate"
  | "risk-high"
  | "risk-very-high";

let cssScheme: Record<SchemeName, string> | null = null;
let chartSeriesPalette: string[] | null = null;

function readVar(name: string): string {
  if (typeof window === "undefined") return "0 0% 0%";
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || "0 0% 0%";
}

function hsl(name: string, alpha: number = 1): string {
  const v = readVar(name);
  return alpha < 1 ? `hsl(${v} / ${alpha})` : `hsl(${v})`;
}

export function refreshChartTheme(): void {
  cssScheme = {
    background: hsl("--card"),
    foreground: hsl("--foreground"),
    muted: hsl("--muted-foreground"),
    border: hsl("--border"),
    grid: hsl("--grid"),
    primary: hsl("--primary"),
    accent: hsl("--accent"),
    card: hsl("--card"),
    "risk-low": hsl("--risk-low"),
    "risk-moderate": hsl("--risk-moderate"),
    "risk-high": hsl("--risk-high"),
    "risk-very-high": hsl("--risk-very-high"),
  };
  chartSeriesPalette = [
    hsl("--chart-1"),
    hsl("--chart-2"),
    hsl("--chart-3"),
    hsl("--chart-4"),
    hsl("--chart-5"),
    hsl("--chart-6"),
    hsl("--chart-7"),
    hsl("--chart-8"),
  ];
}

if (typeof window !== "undefined") {
  refreshChartTheme();
  const observer = new MutationObserver(() => refreshChartTheme());
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
}

function ensureScheme(): Record<SchemeName, string> {
  if (!cssScheme) refreshChartTheme();
  return cssScheme!;
}

function ensurePalette(): string[] {
  if (!chartSeriesPalette) refreshChartTheme();
  return chartSeriesPalette!;
}

/**
 * Apply an alpha to any color string the rest of the chart code might emit.
 * Handles hsl(H S% L%), hsl(H S% L% / α), #rrggbb, and pass-through.
 */
export function withAlpha(color: string, alpha: number): string {
  if (color.startsWith("hsl(")) {
    const inner = color.slice(4, -1).split("/")[0].trim();
    return `hsl(${inner} / ${alpha})`;
  }
  if (color.startsWith("#")) {
    const hex = Math.round(alpha * 255).toString(16).padStart(2, "0");
    return color.length === 7 ? `${color}${hex}` : color;
  }
  if (color.startsWith("rgb(")) {
    const inner = color.slice(4, -1).trim();
    return `rgba(${inner}, ${alpha})`;
  }
  return color;
}

// -----------------------------------------------------------------------
// Public theme accessors
// -----------------------------------------------------------------------

export const colorPalettes = {
  get scientific(): string[] {
    return ensurePalette();
  },
  get sequential() {
    return {
      ocean: ["#eef6ff", "#cfe6ff", "#9bcdff", "#5cabf3", "#2e8be0", "#196dbf", "#0f5499", "#0a3d75"],
      teal: ["#ecf9f7", "#c2efe7", "#8edcd0", "#52c2b1", "#28a08b", "#177864", "#0f5b4c", "#0a4338"],
      amber: ["#fef6e7", "#fde6b3", "#fbcd6a", "#f7ae2a", "#e58a09", "#b46b06", "#7f4904", "#502c02"],
      magma: ["#fff4ec", "#fbd5b1", "#f5a274", "#e9714a", "#c64731", "#8e2c20", "#581b13", "#2e0d09"],
    };
  },
  get diverging(): string[] {
    return [
      "#0a3d75", "#196dbf", "#5cabf3", "#dde8f1", "#f7ae2a", "#c64731", "#8e2c20",
    ];
  },
  get risk() {
    const s = ensureScheme();
    return {
      low: s["risk-low"],
      moderate: s["risk-moderate"],
      high: s["risk-high"],
      veryHigh: s["risk-very-high"],
    };
  },
};

export const chartTheme: ChartTheme = new Proxy({} as ChartTheme, {
  get(_t, key: string) {
    const s = ensureScheme();
    switch (key) {
      case "backgroundColor":
        return "transparent";
      case "textColor":
        return s.foreground;
      case "gridColor":
        return s.grid;
      case "axisColor":
        return s.muted;
      case "tooltipBg":
        return s.card;
      case "primaryColor":
        return s.primary;
      case "secondaryColor":
        return s.accent;
      case "tertiaryColor":
        return s["risk-low"];
      case "riskLowColor":
        return s["risk-low"];
      case "riskModerateColor":
        return s["risk-moderate"];
      case "riskHighColor":
        return s["risk-high"];
      default:
        return "";
    }
  },
});

// -----------------------------------------------------------------------
// Base options — pasted onto every chart so all charts share line widths,
// font, axis treatment, tooltip styling, toolbox etc.
// -----------------------------------------------------------------------

export function getBaseChartOptions(): Partial<EChartsOption> {
  const s = ensureScheme();
  return {
    backgroundColor: "transparent",
    textStyle: {
      fontFamily: "Inter, system-ui, sans-serif",
      fontSize: 12,
      color: s.foreground,
    },
    color: ensurePalette(),
    title: {
      textStyle: {
        fontSize: 14,
        fontWeight: 600,
        color: s.foreground,
        fontFamily: "Space Grotesk, Inter, system-ui, sans-serif",
      },
      subtextStyle: {
        fontSize: 11,
        color: s.muted,
      },
    },
    tooltip: {
      backgroundColor: s.card,
      borderColor: s.border,
      borderWidth: 1,
      textStyle: {
        color: s.foreground,
        fontSize: 12,
        fontFamily: "Inter, system-ui, sans-serif",
      },
      padding: [10, 14],
      extraCssText:
        "box-shadow: 0 16px 48px -16px hsl(220 50% 12% / 0.25); border-radius: 12px; backdrop-filter: blur(10px);",
    },
    legend: {
      textStyle: {
        fontSize: 12,
        color: s.foreground,
      },
      itemGap: 18,
      itemWidth: 14,
      itemHeight: 8,
      icon: "roundRect",
    },
    grid: {
      left: 64,
      right: 24,
      top: 56,
      bottom: 56,
      containLabel: true,
    },
    xAxis: {
      axisLine: {
        lineStyle: {
          color: s.border,
          width: 1,
        },
      },
      axisTick: {
        lineStyle: { color: s.muted },
        length: 4,
      },
      axisLabel: {
        color: s.muted,
        fontSize: 11,
        fontFamily: "JetBrains Mono, monospace",
      },
      splitLine: {
        lineStyle: {
          color: s.grid,
          type: "dashed",
        },
      },
      nameTextStyle: {
        fontSize: 12,
        fontWeight: 500,
        color: s.foreground,
        padding: [10, 0, 0, 0],
      },
    },
    yAxis: {
      axisLine: {
        lineStyle: {
          color: s.border,
          width: 1,
        },
      },
      axisTick: { lineStyle: { color: s.muted } },
      axisLabel: {
        color: s.muted,
        fontSize: 11,
        fontFamily: "JetBrains Mono, monospace",
      },
      splitLine: {
        lineStyle: {
          color: s.grid,
          type: "dashed",
        },
      },
      nameTextStyle: {
        fontSize: 12,
        fontWeight: 500,
        color: s.foreground,
        padding: [0, 0, 10, 0],
      },
    },
    animation: true,
    animationDuration: 700,
    animationDurationUpdate: 400,
    animationEasing: "cubicOut",
    animationEasingUpdate: "cubicOut",
  };
}

// -----------------------------------------------------------------------
// Chart-specific helpers
// -----------------------------------------------------------------------

export function getScatterChartOptions(
  title: string,
  xLabel: string,
  yLabel: string,
): Partial<EChartsOption> {
  const base = getBaseChartOptions();
  return {
    ...base,
    title: {
      text: title,
      left: "center",
      top: 10,
    },
    xAxis: {
      ...(base.xAxis as object),
      type: "value" as const,
      name: xLabel,
      nameLocation: "middle" as const,
      nameGap: 32,
    },
    yAxis: {
      ...(base.yAxis as object),
      type: "value" as const,
      name: yLabel,
      nameLocation: "middle" as const,
      nameGap: 48,
    },
    toolbox: {
      feature: {
        dataZoom: { show: true, title: { zoom: "Zoom", back: "Reset" } },
        saveAsImage: { show: true, pixelRatio: 3, title: "Save PNG" },
        dataView: { show: true, title: "Data" },
        restore: { show: true, title: "Restore" },
      },
      iconStyle: { borderColor: ensureScheme().muted },
      right: 16,
      top: 8,
    },
  };
}

export function getTimeSeriesOptions(): Partial<EChartsOption> {
  const base = getBaseChartOptions();
  return {
    ...base,
    dataZoom: [
      { type: "inside", start: 0, end: 100 },
      { type: "slider", start: 0, end: 100, bottom: 28, height: 16 },
    ],
    toolbox: {
      feature: {
        saveAsImage: { show: true, pixelRatio: 3, title: "Save PNG" },
        dataZoom: { show: true, title: { zoom: "Zoom", back: "Reset" } },
        restore: { show: true, title: "Restore" },
      },
      iconStyle: { borderColor: ensureScheme().muted },
      right: 16,
      top: 8,
    },
  };
}

export function getRiskGradientStops(): [number, string][] {
  const s = ensureScheme();
  return [
    [0.01, s["risk-low"]],
    [0.05, s["risk-moderate"]],
    [0.20, s["risk-high"]],
    [1.00, s["risk-very-high"]],
  ];
}

export function getRiskGradientColors(value: number): string[] {
  const s = ensureScheme();
  if (value < 1) return [s["risk-low"], s["risk-low"]];
  if (value < 5) return [s["risk-moderate"], s["risk-moderate"]];
  if (value < 20) return [s["risk-high"], s["risk-high"]];
  return [s["risk-very-high"], s["risk-very-high"]];
}
