import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

import type { RiskLevel } from "../types";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatNumber(value: number | null | undefined, digits: number = 2): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return "—";
  if (value === 0) return "0";
  const abs = Math.abs(value);
  if (abs < 1e-4) return value.toExponential(2);
  if (abs < 1e-2) return value.toFixed(4);
  if (abs >= 1e6) return value.toExponential(2);
  return value.toFixed(digits);
}

const RISK_THRESHOLDS = {
  low: 1,
  moderate: 10,
} as const;

export function getRiskLevel(percent: number | null | undefined): RiskLevel {
  if (typeof percent !== "number" || !Number.isFinite(percent) || percent < 0 || percent > 100)
    return "unavailable";
  if (percent < RISK_THRESHOLDS.low) return "low";
  if (percent < RISK_THRESHOLDS.moderate) return "moderate";
  return "high";
}

export function getRiskColor(percent: number | null | undefined): string {
  const level = getRiskLevel(percent);
  if (level === "unavailable") return "#64748b";
  if (level === "low") return "#10b981";
  if (level === "moderate") return "#f59e0b";
  return "#ef4444";
}

/** US Standard Atmosphere (1976), pressure/geopotential altitude 0–20 km. */
export function altitudeFtToPAmbAtm(altitudeFt: number): number {
  const heightM = altitudeFt * 0.3048;
  if (!Number.isFinite(heightM) || heightM < 0 || heightM > 20000 + 1e-9)
    throw new Error("Pressure altitude must be finite and within 0–20 km");
  const g0 = 9.80665;
  const rAir = 287.05287;
  const t0 = 288.15;
  const lapse = 0.0065;
  const t11 = 216.65;
  const exponent = g0 / (rAir * lapse);
  if (heightM <= 11000) return Math.pow(1 - lapse * heightM / t0, exponent);
  const p11 = Math.pow(t11 / t0, exponent);
  return p11 * Math.exp(-g0 * (heightM - 11000) / (rAir * t11));
}

export function altitudeFtToMmHg(altitudeFt: number): number {
  return altitudeFtToPAmbAtm(altitudeFt) * 760.0;
}

/** Inverse of the 0–20 km layered pressure-altitude conversion. */
export function pressureAtmToAltitudeFt(pressureAtm: number): number {
  const g0 = 9.80665;
  const rAir = 287.05287;
  const t0 = 288.15;
  const lapse = 0.0065;
  const t11 = 216.65;
  const p11 = Math.pow(t11 / t0, g0 / (rAir * lapse));
  const p20 = p11 * Math.exp(-g0 * 9000 / (rAir * t11));
  if (!Number.isFinite(pressureAtm) || pressureAtm < p20 || pressureAtm > 1)
    throw new Error("Pressure is outside the implemented 0–20 km atmosphere");
  const heightM = pressureAtm >= p11
    ? t0 / lapse * (1 - Math.pow(pressureAtm, rAir * lapse / g0))
    : 11000 - rAir * t11 / g0 * Math.log(pressureAtm / p11);
  return heightM / 0.3048;
}

export function stableSigmoid(x: number): number {
  if (Number.isNaN(x)) return Number.NaN;
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
