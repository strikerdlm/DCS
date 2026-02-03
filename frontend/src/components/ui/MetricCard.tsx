import * as React from "react";
import { cn, getRiskLevel } from "../../lib/utils";
import { TrendingUp, TrendingDown, Minus, AlertTriangle } from "lucide-react";

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
  const riskLevel = isRisk && typeof riskValue === "number" 
    ? getRiskLevel(riskValue) 
    : null;

  const riskStyles = {
    low: "border-l-emerald-500 bg-emerald-50 dark:bg-emerald-950/20",
    moderate: "border-l-amber-500 bg-amber-50 dark:bg-amber-950/20",
    high: "border-l-red-500 bg-red-50 dark:bg-red-950/20",
  };

  const riskTextStyles = {
    low: "text-emerald-700 dark:text-emerald-400",
    moderate: "text-amber-700 dark:text-amber-400",
    high: "text-red-700 dark:text-red-400",
  };

  const TrendIcon = trend === "up" 
    ? TrendingUp 
    : trend === "down" 
      ? TrendingDown 
      : Minus;

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border-l-4 p-5 transition-all duration-300 hover:shadow-lg",
        riskLevel ? riskStyles[riskLevel] : "border-l-primary bg-white dark:bg-gray-900",
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
            {label}
          </p>
          <div className="flex items-baseline gap-2">
            <span
              className={cn(
                "text-3xl font-bold tracking-tight",
                riskLevel ? riskTextStyles[riskLevel] : "text-gray-900 dark:text-white"
              )}
            >
              {value}
            </span>
            {unit && (
              <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                {unit}
              </span>
            )}
          </div>
          {description && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {description}
            </p>
          )}
        </div>
        <div className="flex flex-col items-end gap-2">
          {icon && (
            <div className={cn(
              "p-2 rounded-lg",
              riskLevel 
                ? `bg-${riskLevel === 'low' ? 'emerald' : riskLevel === 'moderate' ? 'amber' : 'red'}-100 dark:bg-${riskLevel === 'low' ? 'emerald' : riskLevel === 'moderate' ? 'amber' : 'red'}-900/30`
                : "bg-primary/10"
            )}>
              {icon}
            </div>
          )}
          {isRisk && riskLevel === "high" && (
            <AlertTriangle className="h-5 w-5 text-red-500 animate-pulse" />
          )}
        </div>
      </div>
      {trend && trendValue && (
        <div className="mt-3 flex items-center gap-1 text-xs">
          <TrendIcon
            className={cn(
              "h-3 w-3",
              trend === "up"
                ? "text-emerald-500"
                : trend === "down"
                  ? "text-red-500"
                  : "text-gray-400"
            )}
          />
          <span
            className={cn(
              trend === "up"
                ? "text-emerald-600 dark:text-emerald-400"
                : trend === "down"
                  ? "text-red-600 dark:text-red-400"
                  : "text-gray-500"
            )}
          >
            {trendValue}
          </span>
        </div>
      )}
    </div>
  );
}
