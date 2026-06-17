import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
import { chartTheme, colorPalettes, withAlpha } from "./chartConfig";
import { formatNumber, getRiskLevel } from "../../lib/utils";

interface RiskGaugeProps {
  value: number;
  title?: string;
  height?: number;
  showLabel?: boolean;
  /** Preferred upper bound of the dial (%). Default 100. Pass a smaller value
   *  (e.g. 40) on cards whose readings usually live in a narrow operational
   *  window so the low / moderate bands render legibly. The dial auto-expands
   *  above this if a reading would otherwise be clipped, so the value arc is
   *  never pinned while the number keeps climbing. */
  max?: number;
}

// Risk-band boundaries (percent) for the decorative track. These match the
// 1 / 5 / 20 four-zone convention used by the rest of the dashboard's figures —
// the RiskLandscape tooltip and the four-stop risk ramp in chartConfig
// (getRiskGradientStops) — and map onto the four deep-ocean risk tokens
// (low / moderate / high / very-high). Note this is a finer-grained scale than
// the three-level getRiskLevel() in lib/utils (1 / 10 %) that drives the
// caption pill: the band track gives visual severity context while the pill
// remains the single authoritative low/moderate/elevated call.
const RISK_LOW_MAX = 1;
const RISK_MODERATE_MAX = 5;
const RISK_HIGH_MAX = 20;

/**
 * Arc + colored risk-band gauge.
 *
 * Two layers, cleanly decoupled:
 *   1. A muted low / moderate / high / very-high colored band TRACK whose
 *      boundaries sit at the dashboard-wide 1 / 5 / 20 % thresholds, so the
 *      zones convey severity at a glance and stay coherent with the
 *      RiskLandscape tooltip and the chartConfig risk ramp.
 *   2. A single value (progress) ARC, drawn in the deep-ocean accent, that
 *      shows where the current reading sits on the track.
 *
 * Intentionally uncluttered: no needle / pointer, no anchor, no axis ticks,
 * no split lines, no crowded numeric axis labels — just the band track, the
 * value arc, a big centered value, and an optional small caption. All colors
 * come from the shared deep-ocean chartTheme so it matches the rest of the UI.
 */
export function RiskGauge({
  value,
  title = "DCS Risk",
  height = 280,
  showLabel = true,
  max = 100,
}: RiskGaugeProps): React.ReactElement {
  const safe = Math.max(0, value);
  // Auto-expand the dial so a reading above the preferred window is shown in
  // full (arc + number agree) instead of pinning the arc at the rim. Snaps to
  // a clean 10-% step and never exceeds 100 %.
  const dialMax = Math.min(100, Math.max(max, Math.ceil(safe / 10) * 10));
  const clamped = Math.min(dialMax, safe);
  const riskLevel = getRiskLevel(value);
  // Caption-dot color drawn from the same deep-ocean risk tokens as the band
  // track, so the dot, the band, and the pill never diverge in hue.
  const risk = colorPalettes.risk;
  const riskColor =
    riskLevel === "low"
      ? risk.low
      : riskLevel === "moderate"
        ? risk.moderate
        : risk.high;

  const option: EChartsOption = useMemo(() => {
    // Risk-band track anchored to the 1 / 5 / 20 % thresholds. Boundaries are
    // clamped into [0, 1] so the track is always valid even when `dialMax`
    // sits below a threshold (e.g. a low-range dial that never reaches the
    // very-high band). Alpha 0.42 keeps the zones perceptible-but-muted
    // against deep-ocean. Each successive stop is only emitted if it advances
    // past the previous one, so no zero-width slivers are drawn.
    const BAND_ALPHA = 0.42;
    const lowStop = Math.min(RISK_LOW_MAX / dialMax, 1);
    const modStop = Math.min(RISK_MODERATE_MAX / dialMax, 1);
    const highStop = Math.min(RISK_HIGH_MAX / dialMax, 1);
    const bandTrack: [number, string][] = [];
    if (lowStop > 0) bandTrack.push([lowStop, withAlpha(risk.low, BAND_ALPHA)]);
    if (modStop > lowStop) bandTrack.push([modStop, withAlpha(risk.moderate, BAND_ALPHA)]);
    if (highStop > modStop) bandTrack.push([highStop, withAlpha(risk.high, BAND_ALPHA)]);
    if (highStop < 1) bandTrack.push([1.0, withAlpha(risk.veryHigh, BAND_ALPHA)]);

    return {
      backgroundColor: "transparent",
      grid: undefined,
      tooltip: undefined,
      series: [
        {
          type: "gauge",
          startAngle: 220,
          endAngle: -40,
          center: ["50%", "56%"],
          radius: "92%",
          min: 0,
          max: dialMax,
          // Value arc — single deep-ocean accent so it reads purely as
          // "where the reading sits", letting the band track carry severity.
          progress: {
            show: true,
            width: 13,
            roundCap: true,
            itemStyle: {
              color: chartTheme.primaryColor,
              shadowBlur: 8,
              shadowColor: withAlpha(chartTheme.primaryColor, 0.35),
            },
          },
          // Muted low/moderate/high band track behind the value arc.
          axisLine: {
            lineStyle: {
              width: 13,
              color: bandTrack,
            },
          },
          // Decluttered: no needle, anchor, ticks, split lines or axis labels.
          pointer: { show: false },
          anchor: { show: false },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          title: {
            show: showLabel,
            offsetCenter: [0, "34%"],
            fontSize: 12,
            fontWeight: 500,
            color: chartTheme.axisColor,
            fontFamily: "Inter, system-ui, sans-serif",
          },
          detail: {
            valueAnimation: true,
            formatter: (val: number) => `${formatNumber(val, 2)}%`,
            fontSize: 30,
            fontWeight: 700,
            offsetCenter: [0, showLabel ? "4%" : "10%"],
            color: chartTheme.textColor,
            fontFamily: "Archivo, Inter, system-ui, sans-serif",
          },
          data: [{ value: clamped, name: title }],
        },
      ],
    };
    // `risk.*` are resolved strings (not the fresh getter object) so the memo
    // is stable across renders and only recomputes when an input truly changes.
  }, [clamped, dialMax, showLabel, title, risk.low, risk.moderate, risk.high, risk.veryHigh]);

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
