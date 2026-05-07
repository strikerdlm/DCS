import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

import type { RiskLevel } from "../types";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatNumber(value: number, digits: number = 2): string {
  if (!Number.isFinite(value)) return "—";
  if (value === 0) return "0";
  const abs = Math.abs(value);
  if (abs < 1e-4) return "<0.0001";
  if (abs < 1e-2) return value.toFixed(4);
  if (abs >= 1e6) return value.toExponential(2);
  return value.toFixed(digits);
}

const RISK_THRESHOLDS = {
  low: 1,
  moderate: 10,
} as const;

export function getRiskLevel(percent: number): RiskLevel {
  if (!Number.isFinite(percent) || percent < RISK_THRESHOLDS.low) return "low";
  if (percent < RISK_THRESHOLDS.moderate) return "moderate";
  return "high";
}

export function getRiskColor(percent: number): string {
  const level = getRiskLevel(percent);
  if (level === "low") return "#10b981";
  if (level === "moderate") return "#f59e0b";
  return "#ef4444";
}

const SEA_LEVEL_PRESSURE_ATM = 1.0;

export function altitudeFtToPAmbAtm(altitudeFt: number): number {
  if (!Number.isFinite(altitudeFt) || altitudeFt <= 0) return SEA_LEVEL_PRESSURE_ATM;
  return Math.pow(1 - 6.87535e-6 * altitudeFt, 5.2559);
}

export function altitudeFtToMmHg(altitudeFt: number): number {
  return altitudeFtToPAmbAtm(altitudeFt) * 760.0;
}

export function stableSigmoid(x: number): number {
  if (!Number.isFinite(x)) return x > 0 ? 1 : 0;
  if (x >= 0) {
    const z = Math.exp(-x);
    return 1 / (1 + z);
  }
  const z = Math.exp(x);
  return z / (1 + z);
}

export function clamp(value: number, lo: number, hi: number): number {
  return Math.min(Math.max(value, lo), hi);
}

export function safeMin(values: ArrayLike<number>): number {
  let m = Infinity;
  for (let i = 0; i < values.length; i++) {
    const v = values[i];
    if (Number.isFinite(v) && v < m) m = v;
  }
  return m === Infinity ? NaN : m;
}

export function safeMax(values: ArrayLike<number>): number {
  let m = -Infinity;
  for (let i = 0; i < values.length; i++) {
    const v = values[i];
    if (Number.isFinite(v) && v > m) m = v;
  }
  return m === -Infinity ? NaN : m;
}
