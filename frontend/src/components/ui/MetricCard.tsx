import * as React from "react";
import { AlertTriangle, Minus, TrendingDown, TrendingUp } from "lucide-react";
import { cn, getRiskColor, getRiskLevel } from "../../lib/utils";

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  description?: string;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  isRisk?: boolean;
  riskValue?: number;
  className?: string;
  icon?: React.ReactNode;
}

export function MetricCard({
  label,
  value,
  unit,
  description,
  trend,
  trendValue,
  isRisk,
  riskValue,
  className,
  icon,
}: MetricCardProps): React.ReactElement {
  const riskLevel =
    isRisk && typeof riskValue === "number" ? getRiskLevel(riskValue) : null;
  const accent =
    isRisk && typeof riskValue === "number" ? getRiskColor(riskValue) : undefined;
  const TrendIcon = trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus;

  return (
    <div
      className={cn(
        "surface relative overflow-hidden p-5 transition-all duration-300 hover:-translate-y-0.5",
        riskLevel === "high" && "ring-1 ring-red-500/30",
        className,
      )}
      style={
        accent
          ? ({
              ["--accent-edge" as string]: accent,
            } as React.CSSProperties)
          : undefined
      }
    >
      <div
        className="absolute left-0 top-0 bottom-0 w-1"
        style={{ background: accent ?? "hsl(var(--primary) / 0.7)" }}
      />
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1.5 min-w-0">
          <p className="text-[11.5px] font-medium uppercase tracking-wider text-muted-foreground truncate">
            {label}
          </p>
          <div className="flex items-baseline gap-1.5 flex-wrap">
            <span
              className="display text-[26px] font-bold leading-none tabular-nums"
              style={accent ? { color: accent } : undefined}
            >
              {value}
            </span>
            {unit && (
              <span className="text-[12px] font-medium text-muted-foreground">
                {unit}
              </span>
            )}
          </div>
          {description && (
            <p className="text-[11.5px] text-muted-foreground leading-snug">
              {description}
            </p>
          )}
          {trend && trendValue && (
            <div className="flex items-center gap-1 text-[11.5px] pt-1">
              <TrendIcon
                className={cn(
                  "h-3 w-3",
                  trend === "up"
                    ? "text-emerald-500"
                    : trend === "down"
                      ? "text-red-500"
                      : "text-muted-foreground",
                )}
              />
              <span
                className={cn(
                  trend === "up"
                    ? "text-emerald-600 dark:text-emerald-400"
                    : trend === "down"
                      ? "text-red-600 dark:text-red-400"
                      : "text-muted-foreground",
                )}
              >
                {trendValue}
              </span>
            </div>
          )}
        </div>
        <div className="flex flex-col items-end gap-1.5">
          {icon && (
            <div
              className="p-2 rounded-lg"
              style={{
                background: accent
                  ? `${accent}1f`
                  : "hsl(var(--primary) / 0.10)",
                color: accent ?? "hsl(var(--primary))",
              }}
            >
              {icon}
            </div>
          )}
          {isRisk && riskLevel === "high" && (
            <AlertTriangle className="h-4 w-4 text-red-500 animate-pulse-soft" />
          )}
        </div>
      </div>
    </div>
  );
}
