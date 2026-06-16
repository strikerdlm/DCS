import React from "react";
import {
  ArrowRight,
  Boxes,
  Cpu,
  Gauge,
  Layers,
  Radio,
  Ruler,
  ShieldCheck,
  Sparkles,
  Target,
  Watch,
  Zap,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";

interface LayerSpec {
  index: string;
  icon: React.ReactNode;
  tint: string;
  title: string;
  subtitle: string;
  points: string[];
}

const LAYERS: LayerSpec[] = [
  {
    index: "01",
    icon: <Watch className="h-5 w-5" />,
    tint: "hsl(var(--primary))",
    title: "Wearable input layer",
    subtitle: "Telemetry → 13-feature vector",
    points: [
      "Altitude, time-at-altitude, prebreathe, exercise category in.",
      "Derived physiology out: ambient pressure, log-time, 360-min tissue-N₂ ratio, supersaturation, exercise dose.",
      "Continuous-VO₂ channel is wired but future-facing — see note below.",
    ],
  },
  {
    index: "02",
    icon: <Cpu className="h-5 w-5" />,
    tint: "hsl(var(--accent))",
    title: "LightGBM logit core + OOD gate",
    subtitle: "Monotone gradient boosting · Mahalanobis envelope check",
    points: [
      "Gradient-boosted trees with physiological monotonicity constraints (risk rises with altitude & time, falls with prebreathe).",
      "A Mahalanobis out-of-distribution gate flags inputs that fall outside the training manifold.",
      "Outside the validated envelope the model abstains rather than extrapolating.",
    ],
  },
  {
    index: "03",
    icon: <Ruler className="h-5 w-5" />,
    tint: "hsl(var(--signal))",
    title: "Zero-inflated conformal calibration",
    subtitle: "Two-stage split-conformal · the headline contribution",
    points: [
      "Turns the point logit into a point estimate + calibrated 95 % prediction interval.",
      "Zero-inflated two-stage design handles bands where ~40 % of targets are exactly zero.",
      "Closes a coverage shortfall (~0.58 → ≥0.95 in every 5 000-ft band; 0.960 overall).",
    ],
  },
];

const SPEC_TILES = [
  { icon: <Boxes className="h-4 w-4" />, label: "ONNX footprint", value: "95 KB", note: "compact variant" },
  { icon: <Zap className="h-4 w-4" />, label: "Latency", value: "2.44 µs", note: "/row, server-CPU p50" },
  { icon: <Target className="h-4 w-4" />, label: "Fidelity to ADRAC", value: "MAE 0.020", note: "R² 0.986 · Brier 0.0016" },
  { icon: <ShieldCheck className="h-4 w-4" />, label: "Interval coverage", value: "0.960", note: "≥0.95 per 5 kft band" },
];

export function Overview(): React.ReactElement {
  return (
    <div className="space-y-6">
      {/* Hero */}
      <section className="surface-elevated p-6 lg:p-10 relative overflow-hidden">
        <div className="absolute inset-0 grid-overlay opacity-[0.16] pointer-events-none" />
        <div className="absolute -top-40 -right-24 w-[28rem] h-[28rem] rounded-full bg-primary/15 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-44 -left-24 w-[24rem] h-[24rem] rounded-full bg-accent/10 blur-3xl pointer-events-none" />
        <div className="relative max-w-3xl">
          <span className="pill-primary mb-4">
            <Sparkles className="h-3 w-3" /> How TinyDCS works
          </span>
          <h2 className="display text-3xl lg:text-[2.6rem] font-bold tracking-tight leading-[1.08]">
            An edge-deployable surrogate of the USAF{" "}
            <span className="text-primary">ADRAC</span> altitude-DCS risk grid.
          </h2>
          <p className="text-muted-foreground mt-4 text-[15px] leading-relaxed">
            TinyDCS reproduces the ADRAC modelled risk surface in a 95 KB model that runs on a
            wearable, and wraps every prediction in a{" "}
            <strong className="text-foreground">calibrated 95 % interval</strong>. Its headline
            contribution is <strong className="text-foreground">calibration, not better
            prediction</strong> — honest uncertainty where earlier methods quietly under-covered.
          </p>
          <div className="flex flex-wrap items-center gap-2 mt-5">
            <span className="pill-accent">3-layer architecture</span>
            <span className="pill-muted">13-feature vector</span>
            <span className="pill-muted">zero-inflated conformal</span>
            <span className="pill-signal">OOD abstention</span>
          </div>
        </div>
      </section>

      {/* Honest-framing callout — must not be missed */}
      <Card variant="glass">
        <CardContent className="p-5 lg:p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="shrink-0">
              <div
                className="h-11 w-11 rounded-xl flex items-center justify-center"
                style={{ background: "hsl(var(--signal) / 0.14)", color: "hsl(var(--signal))" }}
              >
                <Target className="h-5 w-5" />
              </div>
            </div>
            <div className="space-y-2">
              <h3 className="display text-[15px] font-semibold">
                What the accuracy numbers actually measure
              </h3>
              <p className="text-[13.5px] text-muted-foreground leading-relaxed">
                Ground truth here is <strong className="text-foreground">ADRAC's modelled output,
                not observed DCS</strong>. Every accuracy figure — MAE 0.020, R² 0.986, Brier 0.0016
                — measures <strong className="text-foreground">fidelity to the ADRAC grid</strong>,
                i.e. how faithfully the surrogate reproduces that reference model. The closed-form
                ADRAC baseline reaches MAE 0.086; the surrogate reproduces the grid ~4× more
                faithfully as a function-approximation benchmark.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Spec tiles */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {SPEC_TILES.map((t) => (
          <div key={t.label} className="stat-tile">
            <div className="flex items-center gap-2 text-muted-foreground">
              <span className="text-primary">{t.icon}</span>
              <span className="text-[11px] font-medium uppercase tracking-wider">{t.label}</span>
            </div>
            <p className="display text-[24px] font-bold mt-2 leading-none text-num">{t.value}</p>
            <p className="text-[11.5px] text-muted-foreground mt-1.5">{t.note}</p>
          </div>
        ))}
      </div>

      {/* 3-layer architecture */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-primary" />
            The 3-layer architecture
          </CardTitle>
          <p className="text-[12.5px] text-muted-foreground mt-1">
            Telemetry enters on the left and leaves on the right as a point estimate, a calibrated
            interval, and an in/out-of-envelope verdict.
          </p>
        </CardHeader>
        <CardContent className="pt-1">
          <div className="grid lg:grid-cols-3 gap-4">
            {LAYERS.map((layer, i) => (
              <div key={layer.index} className="relative">
                <div className="surface h-full p-5 flex flex-col">
                  <div className="flex items-start justify-between">
                    <div
                      className="h-11 w-11 rounded-xl flex items-center justify-center"
                      style={{ background: `color-mix(in oklab, ${layer.tint} 14%, transparent)`, color: layer.tint }}
                    >
                      {layer.icon}
                    </div>
                    <span className="text-num text-[26px] font-bold text-muted-foreground/25 leading-none">
                      {layer.index}
                    </span>
                  </div>
                  <h4 className="display text-[15px] font-semibold mt-4">{layer.title}</h4>
                  <p className="text-[11.5px] text-muted-foreground mt-0.5">{layer.subtitle}</p>
                  <ul className="mt-3 space-y-2 text-[12.5px] text-muted-foreground leading-snug">
                    {layer.points.map((pt, j) => (
                      <li key={j} className="flex gap-2">
                        <span
                          className="mt-1.5 h-1.5 w-1.5 rounded-full shrink-0"
                          style={{ background: layer.tint }}
                        />
                        <span>{pt}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                {i < LAYERS.length - 1 && (
                  <div className="hidden lg:flex absolute top-1/2 -right-[14px] -translate-y-1/2 z-10 h-7 w-7 rounded-full bg-card border border-border items-center justify-center shadow-sm">
                    <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Rationale + VO2 note */}
      <div className="grid lg:grid-cols-[1.3fr_1fr] gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-[15px]">
              <Gauge className="h-4 w-4 text-primary" /> Why calibration is the contribution
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-[13px] text-muted-foreground leading-relaxed">
            <p>
              A point risk of "3 %" is only actionable if you know how much to trust it. On the ADRAC
              grid, the low-altitude band (18 000–23 000 ft) is dominated by near-zero risk: roughly{" "}
              <strong className="text-foreground">40 % of those rows have a target of exactly
              zero</strong>. Four conformal-only methods all under-covered there, with empirical
              coverage as low as <span className="text-num text-foreground">~0.58</span> against a
              nominal 0.95.
            </p>
            <p>
              The zero-inflated two-stage split-conformal model separates the "is it zero?" decision
              from the "how large if positive?" decision. That single change lifts coverage to{" "}
              <strong className="text-foreground">≥0.95 in every 5 000-ft band</strong> (0.960
              overall) without inflating intervals elsewhere. The intervals you see in the Use Cases
              tab illustrate that shape.
            </p>
          </CardContent>
        </Card>

        <Card variant="glass">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-[15px]">
              <Radio className="h-4 w-4 text-accent" /> Continuous-VO₂: future-facing
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-[12.5px] text-muted-foreground leading-relaxed">
            <p>
              The input schema carries a continuous oxygen-uptake (VO₂) channel so the model is{" "}
              <strong className="text-foreground">ready to ingest real wearable VO₂</strong> when
              that telemetry is available.
            </p>
            <p>
              On the current ADRAC grid those VO₂ features are{" "}
              <strong className="text-foreground">synthetic</strong> — derived from the 3-level
              exercise category — and add no accuracy. We do not claim continuous-VO₂ improves
              prediction today; it is plumbing for tomorrow's sensors.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
