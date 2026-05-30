import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption, SeriesOption } from "echarts";
import { chartTheme, colorPalettes, getBaseChartOptions } from "./chartConfig";
import type { ADRACDecomposition } from "../../utils/models";

interface CovariateContributionProps {
  decomposition: ADRACDecomposition;
  height?: number;
}

/**
 * Tornado decomposition of the current ADRAC prediction on the LOG-ODDS scale.
 * Each bar is one additive term of ω; warm bars push risk up, cool bars pull it
 * down. Sorted by magnitude (largest on top). Contributions are additive on the
 * logit scale only — the running total ω maps to P(DCS) through the logistic.
 */
export function CovariateContribution({
  decomposition,
  height = 320,
}: CovariateContributionProps): React.ReactElement {
  const option: EChartsOption = useMemo(() => {
    const base = getBaseChartOptions();
    const up = colorPalettes.risk.high;
    const down = colorPalettes.scientific[0];
    const { contributions } = decomposition;
    // Category axis with inverse:true puts the first (largest) item on top.
    const labels = contributions.map((c) => c.label);
    const data = contributions.map((c) => ({
      value: +c.value.toFixed(3),
      itemStyle: {
        color: c.value >= 0 ? up : down,
        borderRadius: 3,
      },
    }));

    return {
      ...base,
      grid: { left: 8, right: 56, top: 16, bottom: 48, containLabel: true },
      tooltip: {
        ...base.tooltip,
        trigger: "item",
        formatter: (params: unknown) => {
          const p = params as { name: string; value: number };
          const dir = p.value >= 0 ? "raises" : "lowers";
          return `<div style="font-weight:500;margin-bottom:2px">${p.name}</div><div style="font-family:'JetBrains Mono',monospace;font-size:11px">${dir} log-odds by <b>${p.value >= 0 ? "+" : ""}${p.value.toFixed(
            2,
          )}</b></div>`;
        },
      },
      xAxis: {
        ...(base.xAxis as object),
        type: "value" as const,
        name: "Contribution to log-odds of P(DCS)",
        nameLocation: "middle" as const,
        nameGap: 30,
        axisLabel: {
          color: chartTheme.axisColor,
          fontSize: 11,
          fontFamily: "JetBrains Mono, monospace",
        },
      },
      yAxis: {
        ...(base.yAxis as object),
        type: "category" as const,
        inverse: true,
        data: labels,
        axisTick: { show: false },
        axisLine: { show: false },
        axisLabel: { color: chartTheme.textColor, fontSize: 11.5 },
        splitLine: { show: false },
      },
      series: [
        {
          type: "bar",
          data,
          barWidth: "56%",
          label: {
            show: true,
            position: "right",
            formatter: (p: { value: number }) =>
              `${p.value >= 0 ? "+" : ""}${p.value.toFixed(2)}`,
            fontSize: 10.5,
            fontFamily: "JetBrains Mono, monospace",
            color: chartTheme.axisColor,
          },
        } as unknown as SeriesOption,
      ],
    };
  }, [decomposition]);

  return (
    <ReactECharts
      option={option}
      notMerge
      style={{ height: `${height}px`, width: "100%" }}
      opts={{ renderer: "canvas" }}
    />
  );
}
