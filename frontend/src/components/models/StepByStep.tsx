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
    title: "Wearable telemetry",
    lede: "Capture the exposure profile.",
    detail:
      "Altitude, time-at-altitude, prebreathe duration and exercise category are read from the device (or entered by an instructor). This is the raw exposure the airman will fly.",
    io: { in: "raw exposure profile", out: "4 primary inputs" },
  },
  {
    n: 2,
    icon: <Binary className="h-5 w-5" />,
    title: "13-feature vector",
    lede: "Engineer the physiology.",
    detail:
      "The primary inputs expand into a fixed 13-element vector: ambient pressure (mmHg & atm), log-time, one-hot exercise, 360-min tissue-N₂ ratio, supersaturation and exercise dose. Identical structure to the trained surrogate's input tensor.",
    io: { in: "4 inputs", out: "13-feature vector" },
  },
  {
    n: 3,
    icon: <GitBranch className="h-5 w-5" />,
    title: "LightGBM logit core + OOD gate",
    lede: "Score, with guardrails.",
    detail:
      "Monotone gradient-boosted trees emit a risk logit. In parallel, a Mahalanobis out-of-distribution gate checks whether the feature vector sits inside the training manifold and the validated envelope.",
    io: { in: "13-feature vector", out: "risk logit + OOD flag" },
  },
  {
    n: 4,
    icon: <Ruler className="h-5 w-5" />,
    title: "Zero-inflated conformal calibration",
    lede: "Turn a score into an interval.",
    detail:
      "A two-stage split-conformal calibrator maps the logit to a point estimate and a calibrated 95 % prediction interval. The zero-inflated stage keeps coverage ≥0.95 even in near-zero low-altitude bands.",
    io: { in: "risk logit", out: "point + 95 % interval" },
  },
  {
    n: 5,
    icon: <CheckCircle2 className="h-5 w-5" />,
    title: "Verdict",
    lede: "Deliver an honest answer.",
    detail:
      "The output is a point P(DCS), a 95 % interval, and an in/out-of-envelope verdict. If the OOD gate fired, the model abstains instead of returning a number it cannot stand behind.",
    io: { in: "point + interval + flag", out: "point · interval · verdict" },
  },
];

const REPRODUCE: { label: string; cmd: string; note: string }[] = [
  { label: "Clean the grid", cmd: "tinydcs.data_clean.clean_dcs_risk_db", note: "ADRAC DB → 15,908 rows" },
  { label: "Build features", cmd: "tinydcs/features.py", note: "13-feature vector" },
  { label: "Fit the core", cmd: "train LightGBM (monotone)", note: "logit core" },
  { label: "Calibrate", cmd: "zero-inflated two-stage conformal", note: "95 % intervals" },
  { label: "Export", cmd: "ONNX (compact 95 KB)", note: "edge target" },
  { label: "Validate", cmd: "scripts/…_validate", note: "fidelity + coverage" },
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
            From wearable telemetry to a calibrated verdict.
          </h2>
          <p className="text-muted-foreground mt-3 text-[14px] leading-relaxed max-w-xl">
            The same five stages run on every prediction. The browser build executes the closed-form
            ADRAC core; the trained LightGBM + conformal stack runs in the Python pipeline and ships
            as a 95 KB ONNX model for the edge.
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
              At step 3 the OOD gate can halt the pipeline. If the exposure falls outside the
              validated envelope — altitude{" "}
              <span className="text-num text-foreground">18 000–40 000 ft</span>, prebreathe{" "}
              <span className="text-num text-foreground">0–180 min</span>, time-at-altitude{" "}
              <span className="text-num text-foreground">10–240 min</span>, exercise Rest/Mild/Heavy —
              the model returns <strong className="text-foreground">no prediction</strong>.
            </p>
            <p>
              Abstention is a feature, not a failure: it is the honest response when the airman's
              profile is one the model was never validated on (e.g. an unpressurised excursion above
              40 000 ft).
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
