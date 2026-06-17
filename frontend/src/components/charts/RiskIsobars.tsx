import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption, SeriesOption } from "echarts";
import { chartTheme, classicHsl, colorPalettes, getBaseChartOptions, withAlpha } from "./chartConfig";
import { generateAltitudePrebreatheGrid } from "../../utils/models";
import { altitudeFtToMmHg, clamp } from "../../lib/utils";
import type { MLSurrogateInputs } from "../../types";

interface RiskIsobarsProps {
  inputs: MLSurrogateInputs;
  height?: number;
  steps?: number;
}

type Edge = "bottom" | "right" | "top" | "left";

/**
 * Marching-squares isoline extractor. Given a regular grid of P(DCS) over
 * altitude (rows, ascending) × prebreathe (cols, ascending), returns the set
 * of crossing segments where the field passes through `threshold`. Each
 * segment is a pair of [prebreathe, altitude] points; adjacent cells share
 * edge crossings so the segments tile into continuous contour polylines.
 */
function isolineSegments(
  grid: number[][],
  prebreathe: number[],
  altitude: number[],
  threshold: number,
): Array<[number, number][]> {
  const nAlt = altitude.length;
  const nPb = prebreathe.length;
  const lerp = (v0: number, v1: number, p0: number, p1: number): number => {
    if (v1 === v0) return p0;
    const f = clamp((threshold - v0) / (v1 - v0), 0, 1);
    return p0 + f * (p1 - p0);
  };
  const ep = (i: number, j: number, edge: Edge): [number, number] => {
    const a = grid[i][j], b = grid[i][j + 1], c = grid[i + 1][j + 1], d = grid[i + 1][j];
    const x0 = prebreathe[j], x1 = prebreathe[j + 1], y0 = altitude[i], y1 = altitude[i + 1];
    switch (edge) {
      case "bottom": return [lerp(a, b, x0, x1), y0];
      case "right": return [x1, lerp(b, c, y0, y1)];
      case "top": return [lerp(c, d, x1, x0), y1];
      case "left": return [x0, lerp(d, a, y1, y0)];
    }
  };
  const segs: Array<[number, number][]> = [];
  for (let i = 0; i < nAlt - 1; i++) {
    for (let j = 0; j < nPb - 1; j++) {
      const a = grid[i][j], b = grid[i][j + 1], c = grid[i + 1][j + 1], d = grid[i + 1][j];
      const code = (a >= threshold ? 1 : 0) | (b >= threshold ? 2 : 0) | (c >= threshold ? 4 : 0) | (d >= threshold ? 8 : 0);
      const pairs: [Edge, Edge][] = [];
      switch (code) {
        case 1: pairs.push(["left", "bottom"]); break;
        case 2: pairs.push(["bottom", "right"]); break;
        case 3: pairs.push(["left", "right"]); break;
        case 4: pairs.push(["right", "top"]); break;
        case 5: pairs.push(["left", "bottom"], ["right", "top"]); break;
        case 6: pairs.push(["bottom", "top"]); break;
        case 7: pairs.push(["left", "top"]); break;
        case 8: pairs.push(["top", "left"]); break;
        case 9: pairs.push(["bottom", "top"]); break;
        case 10: pairs.push(["bottom", "right"], ["top", "left"]); break;
        case 11: pairs.push(["right", "top"]); break;
        case 12: pairs.push(["right", "left"]); break;
        case 13: pairs.push(["bottom", "right"]); break;
        case 14: pairs.push(["bottom", "left"]); break;
        default: break; // 0 / 15 — fully inside or outside, no crossing
      }
      for (const [e1, e2] of pairs) segs.push([ep(i, j, e1), ep(i, j, e2)]);
    }
  }
  return segs;
}

/**
 * The altitude × prebreathe trade-space with risk isobars.
 *
 * The two mission-planning levers on the axes; P(DCS) as a faint ocean field
 * behind crisp marching-squares contour "isobars" at the 1 / 5 / 20 % four-zone
 * thresholds. The area below the 5 % isobar is the safe operating space for the
 * current time-at-altitude and workload; the dashed frame is the validity
 * envelope (the model abstains beyond it); the marker is the live scenario.
 *
 * Value axes throughout so the contour polylines land on real coordinates.
 */
export function RiskIsobars({
  inputs,
  height = 400,
  steps = 26,
}: RiskIsobarsProps): React.ReactElement {
  const { prebreathe, altitude, matrix, maxRisk } = useMemo(() => {
    const pts = generateAltitudePrebreatheGrid({
      timeAtAltitudeMin: inputs.timeAtAltitude,
      exerciseLevel: inputs.exerciseLevel,
      altitudeSteps: steps,
      prebreatheSteps: steps,
    });
    const altSet = new Set<number>();
    const pbSet = new Set<number>();
    for (const p of pts) {
      altSet.add(Math.round(p.altitudeFt));
      pbSet.add(Math.round(p.prebreatheMin));
    }
    const altitude = [...altSet].sort((a, b) => a - b);
    const prebreathe = [...pbSet].sort((a, b) => a - b);
    const altIdx = new Map(altitude.map((v, i) => [v, i]));
    const pbIdx = new Map(prebreathe.map((v, i) => [v, i]));
    const matrix: number[][] = altitude.map(() => new Array(prebreathe.length).fill(0));
    let mx = 0;
    for (const p of pts) {
      const yi = altIdx.get(Math.round(p.altitudeFt));
      const xi = pbIdx.get(Math.round(p.prebreatheMin));
      if (yi !== undefined && xi !== undefined) {
        matrix[yi][xi] = p.riskPercent;
        if (p.riskPercent > mx) mx = p.riskPercent;
      }
    }
    return { prebreathe, altitude, matrix, maxRisk: mx };
  }, [inputs.timeAtAltitude, inputs.exerciseLevel, steps]);

  const option: EChartsOption = useMemo(() => {
    const base = getBaseChartOptions();
    const risk = colorPalettes.risk;
    const ocean = colorPalettes.sequential.ocean;
    // Contour colours are pre-converted to classic comma-hsl: ECharts' colour
    // parser rejects the modern space-separated hsl() form on some paths.
    const thresholds: { t: number; color: string; label: string }[] = [
      { t: 1, color: classicHsl(risk.low), label: "1% isobar" },
      { t: 5, color: classicHsl(risk.moderate), label: "5% isobar" },
      { t: 20, color: classicHsl(risk.high), label: "20% isobar" },
    ];

    // ECharts 6 heatmap requires two CATEGORY axes, so the field is gridded
    // by index and the contour/frame/marker overlays are expressed in the same
    // category-index space (fractional indices interpolate smoothly for line
    // series, so the marching-squares polylines still land on real coordinates).
    const nPb = prebreathe.length;
    const nAlt = altitude.length;
    const pbMin = prebreathe[0];
    const pbMax = prebreathe[nPb - 1];
    const altMin = altitude[0];
    const altMax = altitude[nAlt - 1];
    const pbToIdx = (v: number) =>
      nPb <= 1 ? 0 : ((v - pbMin) / (pbMax - pbMin)) * (nPb - 1);
    const altToIdx = (v: number) =>
      nAlt <= 1 ? 0 : ((v - altMin) / (altMax - altMin)) * (nAlt - 1);

    // Heatmap field, indexed by [prebreatheIndex, altitudeIndex].
    const fieldData: [number, number, number][] = [];
    for (let yi = 0; yi < nAlt; yi++) {
      for (let xi = 0; xi < nPb; xi++) {
        fieldData.push([xi, yi, +matrix[yi][xi].toFixed(2)]);
      }
    }

    // Contour line series (null-separated segments → continuous polylines),
    // converted from value space to category-index space.
    const contourSeries: SeriesOption[] = thresholds.map((th) => {
      const segs = isolineSegments(matrix, prebreathe, altitude, th.t);
      const data: Array<[number, number] | null> = [];
      for (const [p1, p2] of segs) {
        data.push(
          [pbToIdx(p1[0]), altToIdx(p1[1])],
          [pbToIdx(p2[0]), altToIdx(p2[1])],
          null,
        );
      }
      return {
        name: th.label,
        type: "line",
        showSymbol: false,
        smooth: false,
        connectNulls: false,
        lineStyle: { color: th.color, width: 2.2, opacity: 0.92 },
        itemStyle: { color: th.color },
        z: 6,
        emphasis: { disabled: true },
        tooltip: { show: false },
        data,
      } as unknown as SeriesOption;
    });

    // Validity frame (the model abstains beyond it) — index-space rectangle.
    const frame: SeriesOption = {
      name: "Validity envelope",
      type: "line",
      showSymbol: false,
      silent: true,
      lineStyle: { color: withAlpha(chartTheme.axisColor, 0.7), type: "dashed", width: 1.5 },
      tooltip: { show: false },
      data: [
        [0, 0],
        [nPb - 1, 0],
        [nPb - 1, nAlt - 1],
        [0, nAlt - 1],
        [0, 0],
      ],
    } as unknown as SeriesOption;

    // Live scenario marker (index space).
    const marker: SeriesOption = {
      name: "Current scenario",
      type: "scatter",
      symbol: "circle",
      symbolSize: 16,
      z: 12,
      itemStyle: {
        color: chartTheme.primaryColor,
        borderColor: chartTheme.tooltipBg,
        borderWidth: 3,
        shadowBlur: 12,
        shadowColor: withAlpha(chartTheme.primaryColor, 0.5),
      },
      data: [[pbToIdx(inputs.prebreathingTime), altToIdx(inputs.altitude)]],
    } as unknown as SeriesOption;

    const visualMax = Math.max(40, Math.ceil(maxRisk / 10) * 10);

    return {
      ...base,
      animationDuration: 700,
      grid: { left: 72, right: 70, top: 40, bottom: 56, containLabel: true },
      legend: {
        ...base.legend,
        top: 6,
        right: 10,
        data: ["1% isobar", "5% isobar", "20% isobar"],
        textStyle: { fontSize: 10.5, color: chartTheme.textColor },
        itemWidth: 12,
        itemHeight: 8,
      },
      tooltip: {
        ...base.tooltip,
        formatter: (params: unknown) => {
          const p = params as { value: number[]; seriesName: string };
          if (p.seriesName === "Current scenario") {
            return `<div style="font-weight:500">Current scenario</div><div style="font-family:'IBM Plex Mono',monospace;font-size:11px;line-height:1.6">${inputs.altitude.toLocaleString()} ft · ${inputs.prebreathingTime} min prebreathe</div>`;
          }
          if (p.seriesName === "Validity envelope") return "";
          // Heatmap value is [prebreatheIndex, altitudeIndex, riskPercent].
          if (Array.isArray(p.value) && p.value.length >= 3) {
            const [xi, yi, v] = p.value;
            const pb = prebreathe[Math.round(xi)] ?? xi;
            const alt = altitude[Math.round(yi)] ?? yi;
            const level = v < 1 ? "Low" : v < 5 ? "Moderate" : v < 20 ? "Elevated" : "High";
            return `<div style="font-weight:500;margin-bottom:3px">${level} risk</div><div style="font-family:'IBM Plex Mono',monospace;font-size:11px;line-height:1.6"><div>Altitude: <b>${alt.toLocaleString()} ft</b></div><div>Prebreathe: <b>${pb} min</b></div><div>P(DCS): <b>${v.toFixed(2)}%</b></div></div>`;
          }
          return "";
        },
      },
      visualMap: {
        show: true,
        type: "continuous",
        seriesIndex: 0,
        min: 0,
        max: visualMax,
        calculable: false,
        orient: "vertical",
        right: 10,
        top: "middle",
        itemWidth: 10,
        itemHeight: 160,
        text: [`${visualMax}%`, "0%"],
        textStyle: { fontSize: 9.5, color: chartTheme.axisColor, fontFamily: "IBM Plex Mono, monospace" },
        inRange: { color: ocean },
      },
      xAxis: {
        ...(base.xAxis as object),
        type: "category" as const,
        data: prebreathe.map((v) => `${v}`),
        name: "Prebreathe (min)",
        nameLocation: "middle" as const,
        nameGap: 34,
        boundaryGap: true,
        splitArea: { show: false },
        axisLabel: {
          color: chartTheme.axisColor,
          fontSize: 10.5,
          fontFamily: "IBM Plex Mono, monospace",
          interval: Math.max(0, Math.floor(prebreathe.length / 8) - 1),
          formatter: (v: string) => `${Math.round(Number(v))}`,
        },
      },
      yAxis: {
        ...(base.yAxis as object),
        type: "category" as const,
        data: altitude.map((v) => `${v}`),
        name: "Altitude (ft)",
        nameLocation: "middle" as const,
        nameGap: 56,
        boundaryGap: true,
        splitArea: { show: false },
        axisLabel: {
          color: chartTheme.axisColor,
          fontSize: 10.5,
          fontFamily: "IBM Plex Mono, monospace",
          interval: Math.max(0, Math.floor(altitude.length / 8) - 1),
          formatter: (v: string) => `${(Number(v) / 1000).toFixed(0)}k`,
        },
      },
      series: [
        {
          name: "P(DCS) field",
          type: "heatmap",
          data: fieldData,
          progressive: 800,
          progressiveThreshold: 800,
          itemStyle: { borderColor: "transparent" },
          emphasis: { disabled: true },
        } as unknown as SeriesOption,
        ...contourSeries,
        frame,
        marker,
      ],
    };
  }, [matrix, prebreathe, altitude, maxRisk, inputs.altitude, inputs.prebreathingTime]);

  // Derived readouts for the caption.
  const pMmHg = altitudeFtToMmHg(inputs.altitude);

  return (
    <div>
      <ReactECharts
        option={option}
        notMerge
        style={{ height: `${height}px`, width: "100%" }}
        opts={{ renderer: "canvas" }}
      />
      <p className="mt-2 text-[11.5px] text-muted-foreground leading-relaxed">
        Field and isobars hold time-at-altitude at{" "}
        <span className="text-num text-foreground">{inputs.timeAtAltitude} min</span> and workload at{" "}
        <span className="text-num text-foreground">{inputs.exerciseLevel}</span>. Stay below the{" "}
        <span style={{ color: colorPalettes.risk.moderate }}>5 % isobar</span> for an operationally
        safe profile; the dashed frame is the validity envelope — the model abstains beyond it. Current
        point at <span className="text-num text-foreground">{inputs.altitude.toLocaleString()} ft</span> /{" "}
        <span className="text-num text-foreground">{pMmHg.toFixed(0)} mmHg</span>.
      </p>
    </div>
  );
}