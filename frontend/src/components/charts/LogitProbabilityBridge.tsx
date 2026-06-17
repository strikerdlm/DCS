import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption, SeriesOption } from "echarts";
import { chartTheme, colorPalettes, classicHsl, getBaseChartOptions, withAlpha } from "./chartConfig";
import { decomposeADRAC } from "../../utils/models";
import { stableSigmoid } from "../../lib/utils";
import type { MLSurrogateInputs } from "../../types";

interface LogitProbabilityBridgeProps {
  inputs: MLSurrogateInputs;
  height?: number;
}

/**
 * The bridge from log-odds to probability.
 *
 * The ADRAC predictor is ω = (ln t − β₂ − β·x) / β₁, then P(DCS) = σ(ω). The
 * CovariateContribution tornado shows the additive terms that build ω; this
 * chart shows the non-linear step that turns that sum into a probability. The
 * S-curve is painted with the four-zone risk ramp (low → very-high) so the
 * colour itself reads as severity, the 1 / 5 / 20 % operational thresholds are
 * drawn as horizontal isobars, and the live scenario is dropped from its ω on
 * the x-axis up onto the curve — the same number the gauge then displays.
 *
 * visualMap targets only the curve series (seriesIndex 0) so the threshold
 * lines and the live point keep their explicit colours.
 */
export function LogitProbabilityBridge({
  inputs,
  height = 340,
}: LogitProbabilityBridgeProps): React.ReactElement {
  const { omega, riskPercent } = useMemo(() => decomposeADRAC(inputs), [inputs]);

  const option: EChartsOption = useMemo(() => {
    const base = getBaseChartOptions();
    const risk = colorPalettes.risk;

    // Logistic curve σ(ω)·100 across the relevant logit window.
    const X_LO = -6;
    const X_HI = 3.2;
    const curve: [number, number][] = [];
    for (let i = 0; i <= 160; i++) {
      const w = X_LO + ((X_HI - X_LO) * i) / 160;
      curve.push([+w.toFixed(3), +(stableSigmoid(w) * 100).toFixed(3)]);
    }

    const yMax = Math.max(40, Math.ceil(riskPercent * 1.25));

    // Threshold "isobars" at 1 / 5 / 20 % — silent 2-point horizontal lines.
    const threshold = (y: number, color: string, label: string): SeriesOption =>
      ({
        name: label,
        type: "line",
        showSymbol: false,
        silent: true,
        lineStyle: { color: withAlpha(color, 0.7), type: "dashed", width: 1 },
        itemStyle: { color: classicHsl(color) },
        tooltip: { show: false },
        data: [
          [X_LO, y],
          [X_HI, y],
        ],
        // label at the right end
        endLabel: {
          show: true,
          formatter: label,
          color: withAlpha(color, 0.9),
          fontSize: 10,
          fontFamily: "IBM Plex Mono, monospace",
          offset: [-6, -10],
        },
      } as unknown as SeriesOption);

    // Live ω vertical drop-line from the axis up to the curve point.
    const dropLine: SeriesOption = {
      name: "drop",
      type: "line",
      showSymbol: false,
      silent: true,
      lineStyle: { color: withAlpha(chartTheme.primaryColor, 0.55), type: "dotted", width: 1.5 },
      tooltip: { show: false },
      data: [
        [omega, 0],
        [omega, riskPercent],
      ],
    } as unknown as SeriesOption;

    // Live point on the curve.
    const livePoint: SeriesOption = {
      name: "Live scenario",
      type: "scatter",
      symbol: "circle",
      symbolSize: 14,
      z: 10,
      itemStyle: {
        color: chartTheme.primaryColor,
        borderColor: chartTheme.tooltipBg,
        borderWidth: 2.5,
        shadowBlur: 12,
        shadowColor: withAlpha(chartTheme.primaryColor, 0.5),
      },
      data: [[omega, riskPercent]],
    } as unknown as SeriesOption;

    return {
      ...base,
      animationDuration: 900,
      grid: { left: 56, right: 44, top: 24, bottom: 52, containLabel: true },
      tooltip: {
        ...base.tooltip,
        trigger: "axis",
        axisPointer: { type: "line", lineStyle: { color: chartTheme.axisColor, type: "dashed" } },
        formatter: (params: unknown) => {
          const arr = params as Array<{ value: [number, number]; seriesName: string; color: string }>;
          const pt = arr.find((a) => a.seriesName === "P(DCS) = σ(ω)");
          if (!pt) return "";
          const w = pt.value[0];
          const p = pt.value[1];
          return `<div style="font-family:'IBM Plex Mono',monospace;font-size:11px;line-height:1.6"><div>ω = <b>${w.toFixed(2)}</b></div><div>P(DCS) = <b>${p.toFixed(2)}%</b></div></div>`;
        },
      },
      visualMap: {
        show: false,
        type: "continuous",
        seriesIndex: 0,
        min: 0,
        max: 40,
        inRange: { color: [classicHsl(risk.low), classicHsl(risk.moderate), classicHsl(risk.high), classicHsl(risk.veryHigh)] },
      },
      xAxis: {
        ...(base.xAxis as object),
        type: "value" as const,
        min: X_LO,
        max: X_HI,
        name: "ω  (log-odds of DCS)",
        nameLocation: "middle" as const,
        nameGap: 34,
        axisLabel: {
          color: chartTheme.axisColor,
          fontSize: 11,
          fontFamily: "IBM Plex Mono, monospace",
          formatter: (v: number) => (Number.isInteger(v) ? `${v > 0 ? "+" : ""}${v}` : ""),
        },
        splitLine: { show: false },
      },
      yAxis: {
        ...(base.yAxis as object),
        type: "value" as const,
        min: 0,
        max: yMax,
        name: "P(DCS) (%)",
        nameLocation: "middle" as const,
        nameGap: 40,
        axisLabel: {
          color: chartTheme.axisColor,
          fontSize: 11,
          fontFamily: "IBM Plex Mono, monospace",
        },
      },
      series: [
        {
          name: "P(DCS) = σ(ω)",
          type: "line",
          showSymbol: false,
          smooth: true,
          lineStyle: { width: 3 },
          z: 3,
          data: curve,
        } as unknown as SeriesOption,
        threshold(1, risk.low, "1%"),
        threshold(5, risk.moderate, "5%"),
        threshold(20, risk.high, "20%"),
        dropLine,
        livePoint,
      ],
    };
  }, [omega, riskPercent]);

  return (
    <div>
      <ReactECharts
        option={option}
        notMerge
        style={{ height: `${height}px`, width: "100%" }}
        opts={{ renderer: "canvas" }}
      />
      <div className="mt-2 flex items-center justify-center gap-4 text-[11px] text-muted-foreground">
        <span>
          ω = <span className="text-num text-foreground">{omega.toFixed(2)}</span>
        </span>
        <span className="text-muted-foreground/50">→</span>
        <span>
          σ(ω) = <span className="text-num text-foreground">{riskPercent.toFixed(2)}%</span>
        </span>
      </div>
    </div>
  );
}