import React from "react";
import { formatNumber } from "../../lib/utils";

interface RiskGaugeProps {
  value: number | null | undefined;
  title?: string;
  height?: number;
  showLabel?: boolean;
  max?: number;
}

/** Mathematical values carry a neutral scale. Clinical eligibility belongs to the service. */
export function RiskGauge({ value, title = "Model value", height = 220, showLabel = true, max = 100 }: RiskGaugeProps): React.ReactElement {
  const valid = typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= 100;
  return <div className="flex flex-col items-center justify-center gap-3 text-center" style={{minHeight: height}}>
    {showLabel && <span className="text-muted-foreground text-sm">{title}</span>}
    <strong className="display text-4xl">{valid ? formatNumber(value) + "%" : "Unavailable"}</strong>
    {valid && <meter aria-label={title} min={0} max={Math.max(max, value)} value={value} className="w-44" />}
  </div>;
}
