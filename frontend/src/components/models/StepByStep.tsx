import React from "react";
import {
  Activity,
  Binary,
  CheckCircle2,
  FlaskConical,
  GitBranch,
  ListChecks,
  Ruler,
  ShieldAlert,
  Watch,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
import { VALIDITY_ENVELOPE } from "../../utils/models";

interface Step {
  n: number;
  icon: React.ReactNode;
  title: string;
  lede: string;
  detail: string;
  io?: { in: string; out: string };
}

const PIPELINE: Step[] = [
  {
    n: 1,
    icon: <Watch className="h-5 w-5" />,
    title: "Exposure inputs",
    lede: "Capture the exposure profile.",
    detail:
      "Enter pressure altitude, time at altitude, prebreathe duration, and exercise category. These define the altitude model example; wearable measurements require their own validated mapping.",
    io: { in: "raw exposure profile", out: "4 primary inputs" },
  },
  {
    n: 2,
    icon: <Binary className="h-5 w-5" />,
    title: "Model covariates",
    lede: "Engineer the physiology.",
    detail:
      "The baseline uses standard-atmosphere pressure, prebreathe duration, mild/heavy exercise indicators, and log exposure time. Tissue nitrogen and exercise-dose displays are separate diagnostics, not additional fitted ADRAC predictors.",
    io: { in: "4 inputs", out: "baseline covariates + diagnostics" },
  },
  {
    n: 3,
    icon: <GitBranch className="h-5 w-5" />,
    title: "ADRAC baseline and input range",
    lede: "Evaluate the supported equation.",
    detail:
      "The browser evaluates the log-logistic AFT form with bundled coefficients fitted on training cells. A deterministic range check identifies unsupported inputs. It does not execute the separately trained LightGBM surrogate or its Mahalanobis gate.",
    io: { in: "model covariates", out: "baseline estimate + range status" },
  },
  {
    n: 4,
    icon: <Ruler className="h-5 w-5" />,
    title: "Interval availability",
    lede: "Check the available evidence.",
    detail:
      "No validated calibration artifact is bundled for this baseline, so the prediction interval is unavailable. A separately trained surrogate's empirical coverage does not establish coverage for this model or an unsupported EVA profile.",
    io: { in: "baseline artifact", out: "interval unavailable" },
  },
  {
    n: 5,
    icon: <CheckCircle2 className="h-5 w-5" />,
    title: "Verdict",
    lede: "Deliver an honest answer.",
    detail:
      "A supported ADRAC estimate is shown with its input-range status and unavailable interval. Outside the supported range, the example withholds risk. The exact zero-duration limit is labelled separately from positive-duration validation.",
    io: { in: "estimate + availability", out: "research model result" },
  },
];

const REPRODUCE: { label: string; cmd: string; note: string }[] = [
  { label: "Clean the grid", cmd: "tinydcs.data_clean.clean_dcs_risk_db", note: "deduplicate and validate cells" },
  { label: "Freeze partitions", cmd: "training / calibration / test", note: "disjoint grid cells" },
  { label: "Fit the baseline", cmd: "mechanistic.adrac.fit_adrac", note: "training cells only" },
  { label: "Evaluate", cmd: "untouched held-out test cells", note: "MAE/RMSE in percentage points" },
  { label: "Export", cmd: "adrac_coefficients.json", note: "offline baseline coefficients" },
  { label: "Audit", cmd: "adrac_validation.json metadata", note: "partition IDs, hashes, and provenance" },
];

export function StepByStep(): React.ReactElement {
  return (
    <div className="space-y-6">
      {/* Hero */}
      <section className="surface-elevated p-6 lg:p-8 relative overflow-hidden">
        <div className="absolute inset-0 grid-overlay opacity-[0.16] pointer-events-none" />
        <div className="absolute -top-32 -right-24 w-96 h-96 rounded-full bg-accent/12 blur-3xl pointer-events-none" />
        <div className="relative max-w-2xl">
          <span className="pill-accent mb-3">
            <Activity className="h-3 w-3" /> Inference pipeline
          </span>
          <h2 className="display text-3xl font-bold tracking-tight mt-1">
            From exposure inputs to an auditable model result.
          </h2>
          <p className="text-muted-foreground mt-3 text-[14px] leading-relaxed max-w-xl">
            These stages describe the standalone browser ADRAC baseline. The trained LightGBM and
            calibration pipeline is a separate implementation with its own artifacts and evaluation.
          </p>
        </div>
      </section>

      {/* Vertical stepper */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle>End-to-end inference</CardTitle>
        </CardHeader>
        <CardContent className="pt-1">
          <ol className="relative">
            {PIPELINE.map((s, i) => (
              <li key={s.n} className="relative pl-16 pb-7 last:pb-0">
                {/* connector */}
                {i < PIPELINE.length - 1 && (
                  <span className="absolute left-[27px] top-12 bottom-0 w-px bg-gradient-to-b from-primary/40 to-border" />
                )}
                {/* node */}
                <span className="absolute left-0 top-0 h-14 w-14 rounded-2xl bg-primary/10 ring-1 ring-primary/20 text-primary flex items-center justify-center">
                  {s.icon}
                  <span className="absolute -top-1.5 -right-1.5 h-5 w-5 rounded-full bg-primary text-primary-foreground text-[11px] font-bold flex items-center justify-center text-num">
                    {s.n}
                  </span>
                </span>
                <div className="surface p-4">
                  <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
                    <h4 className="display text-[15px] font-semibold">{s.title}</h4>
                    <span className="text-[12px] text-muted-foreground">— {s.lede}</span>
                  </div>
                  <p className="text-[12.5px] text-muted-foreground mt-1.5 leading-relaxed">
                    {s.detail}
                  </p>
                  {s.io && (
                    <div className="flex items-center gap-2 mt-3 flex-wrap">
                      <span className="pill-muted text-num">{s.io.in}</span>
                      <span className="text-muted-foreground/60">→</span>
                      <span className="pill-primary text-num">{s.io.out}</span>
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ol>
        </CardContent>
      </Card>

      {/* Abstention note + reproduce */}
      <div className="grid lg:grid-cols-[1fr_1fr] gap-6">
        <Card variant="glass">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-[15px]">
              <ShieldAlert className="h-4 w-4 text-amber-500" /> When the pipeline abstains
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-[12.5px] text-muted-foreground leading-relaxed">
            <p>
              At step 3 the browser checks the supported range. If the exposure falls outside
              that range — altitude{" "}
              <span className="text-num text-foreground">{VALIDITY_ENVELOPE.altitudeFt.map((value) => value.toLocaleString()).join("–")} ft</span>, prebreathe{" "}
              <span className="text-num text-foreground">{VALIDITY_ENVELOPE.prebreatheMin.join("–")} min</span>, time-at-altitude{" "}
              <span className="text-num text-foreground">{VALIDITY_ENVELOPE.timeAtAltitudeMin.join("–")} min</span>, exercise Rest/Mild/Heavy —
              the model returns <strong className="text-foreground">no prediction</strong>.
            </p>
            <p>
              The displayed range describes model applicability, not permission to use a profile
              in flight or a chamber. An out-of-range example retains its inputs and a reason for
              withholding the estimate.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-[15px]">
              <ListChecks className="h-4 w-4 text-primary" /> Reproduce the science
            </CardTitle>
            <p className="text-[12px] text-muted-foreground mt-0.5">
              The full pipeline, end to end, from the public repo.
            </p>
          </CardHeader>
          <CardContent className="pt-1">
            <ol className="space-y-2">
              {REPRODUCE.map((r, i) => (
                <li
                  key={r.label}
                  className="flex items-center gap-3 px-3 py-2 rounded-lg bg-muted/40 border border-border/40"
                >
                  <span className="text-num text-[11px] font-bold h-6 w-6 shrink-0 rounded-md bg-primary/10 text-primary flex items-center justify-center">
                    {i + 1}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-[13px] font-medium leading-tight">{r.label}</p>
                    <code className="text-num text-[11px] text-muted-foreground">{r.cmd}</code>
                  </div>
                  <span className="text-[11px] text-muted-foreground/80 text-right shrink-0 hidden sm:block">
                    {r.note}
                  </span>
                </li>
              ))}
            </ol>
            <div className="flex items-center gap-2 mt-4 text-[11.5px] text-muted-foreground">
              <FlaskConical className="h-3.5 w-3.5" />
              See <code className="text-num text-[11px] text-foreground">docs/methods.md</code> (TRIPOD+AI
              M1–M8) and <code className="text-num text-[11px] text-foreground">docs/runbook.md</code>.
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
