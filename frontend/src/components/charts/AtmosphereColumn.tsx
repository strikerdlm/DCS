import React from "react";
import { Mountain, Wind, Gauge, Activity } from "lucide-react";
import {
  altitudeFtToMmHg,
  altitudeFtToPAmbAtm,
  formatNumber,
  getRiskLevel,
} from "../../lib/utils";
import { predictMLSurrogate } from "../../utils/models";
import type { MLSurrogateInputs } from "../../types";

interface AtmosphereColumnProps {
  inputs: MLSurrogateInputs;
}

/**
 * The signature "looking up through the atmosphere" visual.
 *
 * A vertical pressure column from sea level (bottom) to ~45 kft (top),
 * stratified into troposphere / tropopause / stratosphere, with an ambient
 * pressure scale on the left, the validated 18–40 kft operational envelope
 * marked, faint isobar ticks, and the current scenario as a glowing marker on
 * the column. To its right, an avionics "flight strip" of derived readouts.
 *
 * Pure SVG + CSS — no chart library, so it scales crisply and stays in the
 * atmospheric design language (isobars, stratification, signal-amber
 * tropopause band). The marker breathes to read as a living reading.
 */

const TOP_FT = 45_000;
// SVG geometry — portrait column.
const VB_W = 360;
const VB_H = 540;
const COL_L = 70; // column left
const COL_R = 300; // column right
const COL_W = COL_R - COL_L;
const TOP_Y = 28; // y at TOP_FT
const BOT_Y = 496; // y at 0 ft
const PLOT_H = BOT_Y - TOP_Y;

function altToY(altFt: number): number {
  return BOT_Y - (Math.min(Math.max(altFt, 0), TOP_FT) / TOP_FT) * PLOT_H;
}

export function AtmosphereColumn({ inputs }: AtmosphereColumnProps): React.ReactElement {
  const { altitude } = inputs;

  const pAtm = altitudeFtToPAmbAtm(altitude);
  const pMmHg = altitudeFtToMmHg(altitude);
  const pred = predictMLSurrogate(inputs);
  const ratio =
    pred.features.find((f) => f.name === "tissue_n2_ratio_360")?.value ?? 0;
  const gapMmHg = Math.max(0, (ratio - 1) * pMmHg);
  const risk = pred.riskPercent;
  const level = getRiskLevel(risk);
  const read = { pAtm, pMmHg, ratio, gapMmHg, risk, level };

  const markerY = altToY(altitude);

  // Pressure-axis ticks: altitude (ft) → mmHg, placed at the matching y.
  const pTicks = [
    { alt: 0, label: "760" },
    { alt: 18_000, label: `${Math.round(altitudeFtToMmHg(18_000))}` },
    { alt: 30_000, label: `${Math.round(altitudeFtToMmHg(30_000))}` },
    { alt: 40_000, label: `${Math.round(altitudeFtToMmHg(40_000))}` },
    { alt: TOP_FT, label: `${Math.round(altitudeFtToMmHg(TOP_FT))}` },
  ];

  // Altitude-axis ticks every 10 kft.
  const altTicks = [0, 10_000, 20_000, 30_000, 40_000, TOP_FT];

  const ratioColor =
    read.level === "low" ? "hsl(var(--risk-low))" :
    read.level === "moderate" ? "hsl(var(--signal))" : "hsl(var(--risk-high))";

  // Flight-strip readouts.
  const strips = [
    {
      icon: <Mountain className="h-3.5 w-3.5" />,
      label: "Altitude",
      value: altitude.toLocaleString(),
      unit: "ft",
      edge: "hsl(var(--primary))",
    },
    {
      icon: <Gauge className="h-3.5 w-3.5" />,
      label: "Ambient P",
      value: read.pAtm.toFixed(3),
      unit: `atm · ${read.pMmHg.toFixed(0)} mmHg`,
      edge: "hsl(var(--accent))",
    },
    {
      icon: <Wind className="h-3.5 w-3.5" />,
      label: "Tissue N₂ ratio",
      value: formatNumber(read.ratio, 2),
      unit: read.ratio >= 1 ? "supersaturated" : "undersaturated",
      edge: ratioColor,
      valueColor: ratioColor,
    },
    {
      icon: <Activity className="h-3.5 w-3.5" />,
      label: "P(DCS)",
      value: read.risk.toFixed(2),
      unit: "%",
      edge: ratioColor,
      valueColor: ratioColor,
    },
  ];

  return (
    <div className="grid lg:grid-cols-[minmax(0,420px)_1fr] gap-6 items-stretch">
      {/* SVG column */}
      <div className="relative surface p-2 grain">
        <svg
          viewBox={`0 0 ${VB_W} ${VB_H}`}
          preserveAspectRatio="xMidYMid meet"
          className="w-full h-auto block"
          role="img"
          aria-label={`Atmospheric column, scenario at ${altitude.toLocaleString()} feet`}
        >
          <defs>
            <linearGradient id="atmCol" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" style={{ stopColor: "hsl(var(--accent))", stopOpacity: 0.06 }} />
              <stop offset="42%" style={{ stopColor: "hsl(var(--primary))", stopOpacity: 0.14 }} />
              <stop offset="100%" style={{ stopColor: "hsl(var(--accent))", stopOpacity: 0.4 }} />
            </linearGradient>
            <linearGradient id="tropoBand" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" style={{ stopColor: "hsl(var(--signal))", stopOpacity: 0.22 }} />
              <stop offset="100%" style={{ stopColor: "hsl(var(--signal))", stopOpacity: 0.04 }} />
            </linearGradient>
            <filter id="markerGlow" x="-60%" y="-60%" width="220%" height="220%">
              <feGaussianBlur stdDeviation="3.4" result="b" />
              <feMerge>
                <feMergeNode in="b" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <clipPath id="colClip">
              <rect x={COL_L} y={TOP_Y} width={COL_W} height={PLOT_H} rx={10} />
            </clipPath>
          </defs>

          {/* Column body */}
          <rect
            x={COL_L}
            y={TOP_Y}
            width={COL_W}
            height={PLOT_H}
            rx={10}
            fill="url(#atmCol)"
            style={{ stroke: "hsl(var(--border))", strokeWidth: 1 }}
          />

          {/* Isobar ticks (every 5 kft) inside the column, clipped */}
          <g clipPath="url(#colClip)">
            {Array.from({ length: 10 }, (_, i) => (i + 1) * 5_000).map((a) => (
              <line
                key={`iso-${a}`}
                x1={COL_L}
                x2={COL_R}
                y1={altToY(a)}
                y2={altToY(a)}
                style={{ stroke: "hsl(var(--foreground))", strokeOpacity: 0.05, strokeWidth: 1 }}
              />
            ))}
            {/* Tropopause band (36–40 kft) — the signal-amber horizon */}
            <rect
              x={COL_L}
              y={altToY(40_000)}
              width={COL_W}
              height={altToY(36_000) - altToY(40_000)}
              fill="url(#tropoBand)"
            />
            <line
              x1={COL_L}
              x2={COL_R}
              y1={altToY(36_000)}
              y2={altToY(36_000)}
              style={{ stroke: "hsl(var(--signal))", strokeOpacity: 0.35, strokeWidth: 1, strokeDasharray: "2 4" }}
            />
          </g>

          {/* Validity envelope 18–40 kft */}
          <rect
            x={COL_L - 1}
            y={altToY(40_000)}
            width={COL_W + 2}
            height={altToY(18_000) - altToY(40_000)}
            rx={4}
            style={{
              fill: "hsl(var(--primary))",
              fillOpacity: 0.05,
              stroke: "hsl(var(--primary))",
              strokeOpacity: 0.45,
              strokeWidth: 1,
              strokeDasharray: "5 4",
            }}
          />
          <text
            x={COL_L + 8}
            y={altToY(40_000) - 6}
            style={{
              fill: "hsl(var(--primary))",
              fillOpacity: 0.85,
              fontSize: 9.5,
              fontWeight: 600,
              fontFamily: "IBM Plex Mono, monospace",
              letterSpacing: "0.08em",
            }}
          >
            VALIDITY 18–40 KFT
          </text>

          {/* Phase labels (inside column) */}
          <text x={COL_L + COL_W / 2} y={altToY(42_500)} textAnchor="middle" style={{ fill: "hsl(var(--muted-foreground))", fillOpacity: 0.6, fontSize: 9, fontWeight: 600, letterSpacing: "0.22em", fontFamily: "Inter, sans-serif" }}>STRATOSPHERE</text>
          <text x={COL_L + COL_W / 2} y={altToY(38_000) + 3} textAnchor="middle" style={{ fill: "hsl(var(--signal))", fillOpacity: 0.7, fontSize: 8.5, fontWeight: 600, letterSpacing: "0.18em", fontFamily: "Inter, sans-serif" }}>TROPOPAUSE</text>
          <text x={COL_L + COL_W / 2} y={altToY(18_000)} textAnchor="middle" style={{ fill: "hsl(var(--muted-foreground))", fillOpacity: 0.6, fontSize: 9, fontWeight: 600, letterSpacing: "0.22em", fontFamily: "Inter, sans-serif" }}>TROPOSPHERE</text>

          {/* Pressure axis (left) */}
          {pTicks.map((t) => (
            <g key={`p-${t.alt}`}>
              <line x1={COL_L - 6} x2={COL_L} y1={altToY(t.alt)} y2={altToY(t.alt)} style={{ stroke: "hsl(var(--muted-foreground))", strokeOpacity: 0.5 }} />
              <text x={COL_L - 10} y={altToY(t.alt) + 3} textAnchor="end" style={{ fill: "hsl(var(--muted-foreground))", fontSize: 9.5, fontFamily: "IBM Plex Mono, monospace" }}>{t.label}</text>
            </g>
          ))}
          <text x={COL_L - 10} y={TOP_Y - 8} textAnchor="end" style={{ fill: "hsl(var(--muted-foreground))", fontSize: 9, fontWeight: 600, letterSpacing: "0.12em" }}>mmHg</text>

          {/* Altitude axis (right) */}
          {altTicks.map((a) => (
            <g key={`a-${a}`}>
              <line x1={COL_R} x2={COL_R + 6} y1={altToY(a)} y2={altToY(a)} style={{ stroke: "hsl(var(--muted-foreground))", strokeOpacity: 0.5 }} />
              <text x={COL_R + 10} y={altToY(a) + 3} style={{ fill: "hsl(var(--muted-foreground))", fontSize: 9.5, fontFamily: "IBM Plex Mono, monospace" }}>{a >= 1000 ? `${Math.round(a / 1000)}k` : "0"}</text>
            </g>
          ))}
          <text x={COL_R + 10} y={TOP_Y - 8} style={{ fill: "hsl(var(--muted-foreground))", fontSize: 9, fontWeight: 600, letterSpacing: "0.12em" }}>kft</text>

          {/* Scenario marker — glowing line + breathing dot + callout */}
          <g filter="url(#markerGlow)">
            <line
              x1={COL_L}
              x2={COL_R}
              y1={markerY}
              y2={markerY}
              style={{ stroke: "hsl(var(--primary))", strokeWidth: 1.6, strokeOpacity: 0.9 }}
            />
            <circle cx={COL_R} cy={markerY} r={5.5} style={{ fill: "hsl(var(--primary))" }} className="animate-breathe" />
            <circle cx={COL_R} cy={markerY} r={3} style={{ fill: "hsl(var(--card))" }} />
            <circle cx={COL_R} cy={markerY} r={1.6} style={{ fill: "hsl(var(--primary))" }} />
          </g>
          {/* Callout to the right of the column */}
          <g>
            <line x1={COL_R + 22} x2={COL_R + 30} y1={markerY} y2={markerY} style={{ stroke: "hsl(var(--primary))", strokeOpacity: 0.6 }} />
            <text x={COL_R + 34} y={markerY - 2} style={{ fill: "hsl(var(--foreground))", fontSize: 11, fontWeight: 700, fontFamily: "Archivo, sans-serif" }}>
              {altitude.toLocaleString()} ft
            </text>
            <text x={COL_R + 34} y={markerY + 11} style={{ fill: "hsl(var(--muted-foreground))", fontSize: 9.5, fontFamily: "IBM Plex Mono, monospace" }}>
              {read.pMmHg.toFixed(0)} mmHg · {read.pAtm.toFixed(2)} atm
            </text>
          </g>
        </svg>
      </div>

      {/* Avionics flight-strip readouts */}
      <div className="flex flex-col gap-3 min-w-0">
        <div className="grid grid-cols-2 gap-3 flex-1">
          {strips.map((s) => (
            <div key={s.label} className="relative surface px-4 py-3 overflow-hidden">
              <div className="absolute left-0 top-0 bottom-0 w-1" style={{ background: s.edge }} />
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <span style={{ color: s.edge }}>{s.icon}</span>
                <span className="text-[9.5px] font-semibold uppercase tracking-[0.14em]">{s.label}</span>
              </div>
              <div className="mt-1.5 flex items-baseline gap-1.5">
                <span
                  className="display text-[22px] font-bold leading-none text-num"
                  style={s.valueColor ? { color: s.valueColor } : undefined}
                >
                  {s.value}
                </span>
                <span className="text-[10.5px] text-muted-foreground">{s.unit}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Supersaturation ribbon — visualizes the tissue load that drives DCS */}
        <div className="surface px-4 py-3">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[9.5px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
              Tissue N₂ supersaturation
            </span>
            <span className="text-num text-[11px]" style={{ color: ratioColor }}>
              {read.ratio >= 1 ? `+${read.gapMmHg.toFixed(0)} mmHg over ambient` : "below ambient"}
            </span>
          </div>
          <div className="relative h-2.5 rounded-full bg-muted overflow-hidden">
            {/* scale 0 → 2.5 ratio */}
            <div
              className="absolute top-0 bottom-0 left-0 rounded-full transition-all duration-500"
              style={{
                width: `${Math.min(100, (Math.min(read.ratio, 2.5) / 2.5) * 100)}%`,
                background: `linear-gradient(90deg, hsl(var(--risk-low)), ${ratioColor})`,
              }}
            />
            {/* threshold tick at ratio = 1 */}
            <div
              className="absolute top-0 bottom-0 w-px"
              style={{ left: `${(1 / 2.5) * 100}%`, background: "hsl(var(--foreground))", opacity: 0.55 }}
            />
          </div>
          <div className="flex justify-between mt-1 text-[9px] text-muted-foreground text-num">
            <span>0</span>
            <span style={{ marginLeft: "38%" }}>1.0 · equilibrium</span>
            <span>2.5</span>
          </div>
        </div>
      </div>
    </div>
  );
}
