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
import { validationMetrics } from "../../data/mockData";
import { formatNumber } from "../../lib/utils";

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
    title: "Exposure inputs",
    subtitle: "Entered parameters → model covariates",
    points: [
      "Altitude, time-at-altitude, prebreathe, exercise category in.",
      "Layered standard-atmosphere pressure, log-time, and exercise indicators enter the baseline.",
      "The separate tissue-N₂ panel illustrates a 360-min compartment. It is not a fitted ADRAC covariate.",
    ],
  },
  {
    index: "02",
    icon: <Cpu className="h-5 w-5" />,
    tint: "hsl(var(--accent))",
    title: "Browser ADRAC baseline",
    subtitle: "Closed-form calculation · explicit input range",
    points: [
      "The log-logistic AFT form uses coefficients fitted on the frozen training partition.",
      "Browser calculations run offline from the bundled coefficients. A trained ML surrogate is a separate artifact.",
      "A range check identifies unsupported inputs; it is not a learned Mahalanobis gate.",
    ],
  },
  {
    index: "03",
    icon: <Ruler className="h-5 w-5" />,
    tint: "hsl(var(--signal))",
    title: "Evidence and availability",
    subtitle: "Held-out comparisons · explicit unavailable outputs",
    points: [
      "Held-out grid cells quantify agreement with ADRAC model targets, not observed DCS outcomes.",
      "No validated prediction-interval artifact is bundled for the baseline.",
      "NASA endpoints retain their 240-min, 4.3-psia reference conditions; 3RUT absolute risk remains disabled.",
    ],
  },
];

const SPEC_TILES = [
  { icon: <Boxes className="h-4 w-4" />, label: "Browser model", value: "ADRAC", note: "closed-form baseline" },
  { icon: <Zap className="h-4 w-4" />, label: "Held-out grid cells", value: validationMetrics.nSample.toLocaleString(), note: "separate from training" },
  { icon: <Target className="h-4 w-4" />, label: "Baseline MAE", value: `${formatNumber(validationMetrics.mae)} pp`, note: `Held-out R² ${formatNumber(validationMetrics.r2, 3)}` },
  { icon: <ShieldCheck className="h-4 w-4" />, label: "Baseline interval", value: "Unavailable", note: "no calibrated artifact bundled" },
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
            DCS model exploration for{" "}
            <span className="text-primary">altitude and space research</span>.
          </h2>
          <p className="text-muted-foreground mt-4 text-[15px] leading-relaxed">
            Explore atmosphere, prebreathe, suit pressure, workload, and model applicability.
            Supported browser calculations work offline; the EVA interface can also use the
            Python API. Model-specific limits determine which outputs are available.
          </p>
          <div className="flex flex-wrap items-center gap-2 mt-5">
            <span className="pill-accent">EVA scenario API</span>
            <span className="pill-muted">5x5 LxC decisions</span>
            <span className="pill-muted">mission-rule profiles</span>
            <span className="pill-signal">telemetry adapters</span>
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
                Reference targets are <strong className="text-foreground">ADRAC model outputs</strong>.
                The baseline was fitted on {validationMetrics.nTrain.toLocaleString()} training cells
                and evaluated on {validationMetrics.nSample.toLocaleString()} separate held-out cells.
                MAE and RMSE use percentage points; R² is dimensionless. These statistics measure
                function approximation and cannot establish clinical prediction accuracy.
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
            Exposure inputs lead to a supported model calculation and explicit availability status.
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
              <Gauge className="h-4 w-4 text-primary" /> What uncertainty requires
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-[13px] text-muted-foreground leading-relaxed">
            <p>
              A point estimate alone does not establish its uncertainty. A prediction interval needs
              a calibration artifact fitted separately from training and evaluated on untouched data.
              Coverage and interval width must use the same target, units, and evaluation population.
            </p>
            <p>
              The Python pipeline supports separate surrogate and calibration artifacts. Their
              coverage cannot be transferred to the browser ADRAC baseline or to unsupported EVA
              profiles. Baseline intervals therefore remain unavailable in these views.
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
              <strong className="text-foreground">able to represent VO₂ inputs</strong>.
              Mapping wearable measurements to this quantity requires separate validation.
            </p>
            <p>
              On the current ADRAC grid those VO₂ features are{" "}
              <strong className="text-foreground">synthetic</strong> — derived from the 3-level
              exercise category. These proxies do not demonstrate performance with measured
              continuous-VO₂ data.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
