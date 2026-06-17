import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption, SeriesOption } from "echarts";
import { chartTheme, colorPalettes, getBaseChartOptions, withAlpha } from "./chartConfig";
import { generateDoseResponse, predictADRAC } from "../../utils/models";
import type { MLSurrogateInputs } from "../../types";

interface PrebreatheFrontierProps {
  inputs: MLSurrogateInputs;
  height?: number;
}

/**
 * The prebreathe cost–benefit frontier.
 *
 * P(DCS) vs 100 % O₂ prebreathe (0–180 min), holding altitude, time-at-altitude
 * and exercise at the current scenario. The curve is steep then flattens —
 * classic diminishing returns: the first 30 min buy the most safety, the last
 * 30 min buy almost none. The 5 % operational gate, the live point, 30-min tick
 * annotations, and a marginal-benefit callout make the trade legible to a
 * mission planner deciding how long to prebreathe.
 */
export function PrebreatheFrontier({
  inputs,
  height = 320,
}: PrebreatheFrontierProps): React.ReactElement {
  const { curve, ticks, currentRisk, nextRisk, maxRisk } = useMemo(() => {
    const pts = generateDoseResponse({
      base: inputs,
      variable: "prebreathe",
      exerciseLevel: inputs.exerciseLevel,
      steps: 181,
    });
    const curve: [number, number][] = pts.map((p) => [p.x, +p.riskPercent.toFixed(3)]);
    const maxRisk = Math.max(40, ...pts.map((p) => p.riskPercent));

    // Ticks every 30 min with their risk value as a label.
    const ticks: { x: number; y: number }[] = [];
    for (let x = 0; x <= 180; x += 30) {
      const pt = pts.find((p) => Math.abs(p.x - x) < 0.5);
      if (pt) ticks.push({ x, y: +pt.riskPercent.toFixed(2) });
    }

    const { riskFraction } = predictADRAC(
      inputs.altitude,
      inputs.prebreathingTime,
      inputs.exerciseLevel,
      inputs.timeAtAltitude,
    );
    const currentRisk = riskFraction * 100;
    const nextPb = Math.min(180, inputs.prebreathingTime + 30);
    const { riskFraction: nextFrac } = predictADRAC(
      inputs.altitude,
      nextPb,
      inputs.exerciseLevel,
      inputs.timeAtAltitude,
    );
    const nextRisk = nextFrac * 100;
    return { curve, ticks, currentRisk, nextRisk, maxRisk };
  }, [inputs]);

  const option: EChartsOption = useMemo(() => {
    const base = getBaseChartOptions();
    const cCurve = chartTheme.primaryColor;
    const cGate = colorPalettes.risk.moderate;
    const cTick = colorPalettes.scientific[6]; // sky

    // 5 % operational gate.
    const gate: SeriesOption = {
      name: "5% gate",
      type: "line",
      showSymbol: false,
      silent: true,
      lineStyle: { color: withAlpha(cGate, 0.8), type: "dashed", width: 1.5 },
      tooltip: { show: false },
      endLabel: {
        show: true,
        formatter: "5% gate",
        color: withAlpha(cGate, 0.9),
        fontSize: 10,
        fontFamily: "IBM Plex Mono, monospace",
        offset: [-8, -10],
      },
      data: [
        [0, 5],
        [180, 5],
      ],
    } as unknown as SeriesOption;

    // Current-prebreathe vertical drop line.
    const drop: SeriesOption = {
      name: "drop",
      type: "line",
      showSymbol: false,
      silent: true,
      lineStyle: { color: withAlpha(cCurve, 0.5), type: "dotted", width: 1.5 },
      tooltip: { show: false },
      data: [
        [inputs.prebreathingTime, 0],
        [inputs.prebreathingTime, currentRisk],
      ],
    } as unknown as SeriesOption;

    // 30-min tick dots with value labels.
    const tickScatter: SeriesOption = {
      name: "ticks",
      type: "scatter",
      symbol: "circle",
      symbolSize: 6,
      z: 5,
      itemStyle: { color: cTick, borderColor: chartTheme.tooltipBg, borderWidth: 1.5 },
      label: {
        show: true,
        position: "top",
        formatter: (p: { value: [number, number] }) => `${p.value[1].toFixed(1)}`,
        fontSize: 9.5,
        fontFamily: "IBM Plex Mono, monospace",
        color: chartTheme.axisColor,
      },
      data: ticks.map((t) => [t.x, t.y]),
    } as unknown as SeriesOption;

    // Live point.
    const live: SeriesOption = {
      name: "Current",
      type: "scatter",
      symbol: "circle",
      symbolSize: 15,
      z: 12,
      itemStyle: {
        color: cCurve,
        borderColor: chartTheme.tooltipBg,
        borderWidth: 3,
        shadowBlur: 12,
        shadowColor: withAlpha(cCurve, 0.5),
      },
      data: [[inputs.prebreathingTime, currentRisk]],
    } as unknown as SeriesOption;

    return {
      ...base,
      animationDuration: 900,
      grid: { left: 56, right: 52, top: 28, bottom: 52, containLabel: true },
      tooltip: {
        ...base.tooltip,
        trigger: "axis",
        axisPointer: { type: "line", lineStyle: { color: chartTheme.axisColor, type: "dashed" } },
        formatter: (params: unknown) => {
          const arr = params as Array<{ value: [number, number]; seriesName: string }>;
          const pt = arr.find((a) => a.seriesName === "P(DCS)");
          if (!pt) return "";
          return `<div style="font-family:'IBM Plex Mono',monospace;font-size:11px;line-height:1.6"><div>Prebreathe: <b>${Math.round(pt.value[0])} min</b></div><div>P(DCS): <b>${pt.value[1].toFixed(2)}%</b></div></div>`;
        },
      },
      xAxis: {
        ...(base.xAxis as object),
        type: "value" as const,
        min: 0,
        max: 180,
        name: "100% O₂ prebreathe (min)",
        nameLocation: "middle" as const,
        nameGap: 34,
        axisLabel: {
          color: chartTheme.axisColor,
          fontSize: 11,
          fontFamily: "IBM Plex Mono, monospace",
          formatter: (v: number) => `${Math.round(v)}`,
        },
      },
      yAxis: {
        ...(base.yAxis as object),
        type: "value" as const,
        min: 0,
        max: maxRisk,
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
          name: "P(DCS)",
          type: "line",
          showSymbol: false,
          smooth: 0.2,
          lineStyle: { width: 2.6, color: cCurve },
          itemStyle: { color: cCurve },
          areaStyle: {
            color: {
              type: "linear",
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: withAlpha(cCurve, 0.22) },
                { offset: 1, color: withAlpha(cCurve, 0.02) },
              ],
            },
          },
          z: 2,
          data: curve,
        } as unknown as SeriesOption,
        gate,
        drop,
        tickScatter,
        live,
      ],
    };
  }, [curve, ticks, currentRisk, maxRisk, inputs.prebreathingTime]);

  // Marginal-benefit callout (React-rendered, keeps the chart clean).
  const delta = nextRisk - currentRisk; // negative = reduction
  const reduction = Math.max(0, -delta);
  const nextPb = Math.min(180, inputs.prebreathingTime + 30);
  const marginal =
    inputs.prebreathingTime >= 180
      ? "Already at the 180 min ceiling — no further prebreathe to give."
      : `+30 min prebreathe (to ${nextPb} min) buys −${reduction.toFixed(2)} % P(DCS).`;

  return (
    <div>
      <ReactECharts
        option={option}
        notMerge
        style={{ height: `${height}px`, width: "100%" }}
        opts={{ renderer: "canvas" }}
      />
      <div className="mt-2 scientific-callout">
        <span className="font-medium">Marginal benefit. </span>
        <span className="text-muted-foreground">
          At <span className="text-num text-foreground">{inputs.prebreathingTime} min</span> the
          point risk is{" "}
          <span className="text-num text-foreground">{currentRisk.toFixed(2)}%</span>. {marginal} The
          curve flattens with every increment — the first 30 min are worth far more than the last.
        </span>
      </div>
    </div>
  );
}