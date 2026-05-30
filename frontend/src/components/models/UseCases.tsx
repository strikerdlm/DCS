import React, { useMemo, useState } from "react";
import {
  AlertTriangle,
  Ban,
  Gauge,
  Mountain,
  Plane,
  ShieldCheck,
  TestTube2,
  Wind,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
import { RiskGauge } from "../charts/RiskGauge";
import { Slider } from "../ui/Slider";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/Select";
import {
  checkEnvelope,
  illustrativeInterval,
  predictADRAC,
} from "../../utils/models";
import { altitudeFtToMmHg, altitudeFtToPAmbAtm, getRiskColor } from "../../lib/utils";
import type { ExerciseLevel } from "../../types";

const EXERCISE: ExerciseLevel[] = ["Rest", "Mild", "Heavy"];

interface ScenarioState {
  altitude: number;
  timeAtAltitude: number;
  prebreathe: number;
  exercise: ExerciseLevel;
}

/** A self-contained, live-computed use-case panel. */
function ScenarioPanel({
  initial,
  altitudeRange,
  prebreatheRange,
  timeRange,
  alertThresholdPct,
  interpret,
}: {
  initial: ScenarioState;
  altitudeRange: [number, number];
  prebreatheRange: [number, number];
  timeRange: [number, number];
  alertThresholdPct: number;
  interpret: (ctx: {
    risk: number;
    low: number;
    high: number;
    inEnvelope: boolean;
    state: ScenarioState;
    overThreshold: boolean;
  }) => React.ReactNode;
}): React.ReactElement {
  const [state, setState] = useState<ScenarioState>(initial);

  const result = useMemo(() => {
    const env = checkEnvelope(
      state.altitude,
      state.prebreathe,
      state.timeAtAltitude,
      state.exercise,
    );
    const { riskFraction } = predictADRAC(
      state.altitude,
      state.prebreathe,
      state.exercise,
      state.timeAtAltitude,
    );
    const risk = riskFraction * 100;
    const interval = illustrativeInterval(riskFraction, state.altitude);
    return { env, risk, interval };
  }, [state]);

  const abstains = !result.env.inEnvelope;
  const overThreshold = !abstains && result.risk >= alertThresholdPct;
  const pMmHg = altitudeFtToMmHg(state.altitude);
  const pAtm = altitudeFtToPAmbAtm(state.altitude);
  const riskColor = getRiskColor(result.risk);

  const set = (patch: Partial<ScenarioState>) =>
    setState((s) => ({ ...s, ...patch }));

  return (
    <div className="grid lg:grid-cols-[320px_1fr] gap-5">
      {/* Controls */}
      <div className="surface p-5 space-y-5 lg:self-start">
        <div className="flex items-center gap-2">
          <Gauge className="h-4 w-4 text-primary" />
          <span className="text-[13px] font-semibold display">Inputs</span>
        </div>

        <Slider
          label="Altitude"
          value={[state.altitude]}
          onValueChange={([v]) => set({ altitude: v })}
          min={altitudeRange[0]}
          max={altitudeRange[1]}
          step={500}
          unit="ft"
          formatValue={(v) => v.toLocaleString()}
        />
        <Slider
          label="Time at altitude"
          value={[state.timeAtAltitude]}
          onValueChange={([v]) => set({ timeAtAltitude: v })}
          min={timeRange[0]}
          max={timeRange[1]}
          step={5}
          unit="min"
        />
        <Slider
          label="100 % O₂ prebreathe"
          value={[state.prebreathe]}
          onValueChange={([v]) => set({ prebreathe: v })}
          min={prebreatheRange[0]}
          max={prebreatheRange[1]}
          step={5}
          unit="min"
        />
        <div className="space-y-1.5">
          <label className="block text-[13px] font-medium">Exercise level</label>
          <Select
            value={state.exercise}
            onValueChange={(v) => set({ exercise: v as ExerciseLevel })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {EXERCISE.map((e) => (
                <SelectItem key={e} value={e}>
                  {e}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="grid grid-cols-2 gap-3 pt-3 border-t border-border/60">
          <div>
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Pressure</p>
            <p className="text-num text-[15px] font-semibold">
              {pAtm.toFixed(3)} <span className="text-[11px] text-muted-foreground">atm</span>
            </p>
            <p className="text-num text-[11px] text-muted-foreground">{pMmHg.toFixed(0)} mmHg</p>
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Alert at</p>
            <p className="text-num text-[15px] font-semibold">
              ≥ {alertThresholdPct}
              <span className="text-[11px] text-muted-foreground"> %</span>
            </p>
            <p className="text-num text-[11px] text-muted-foreground">operational gate</p>
          </div>
        </div>
      </div>

      {/* Output */}
      <div className="space-y-4 min-w-0">
        {abstains ? (
          <div
            className="surface p-6 flex flex-col items-center text-center gap-3"
            style={{ borderColor: "hsl(var(--signal) / 0.4)" }}
          >
            <div
              className="h-14 w-14 rounded-2xl flex items-center justify-center"
              style={{ background: "hsl(var(--signal) / 0.14)", color: "hsl(var(--signal))" }}
            >
              <Ban className="h-7 w-7" />
            </div>
            <div>
              <h4 className="display text-lg font-bold">Model abstains — out of envelope</h4>
              <p className="text-[13px] text-muted-foreground mt-1 max-w-md">
                The OOD gate refuses to predict outside the validated envelope. Returning a number
                here would be an unsupported extrapolation.
              </p>
            </div>
            <ul className="text-[12.5px] text-amber-700 dark:text-amber-300 space-y-1 mt-1">
              {result.env.reasons.map((r, i) => (
                <li key={i} className="flex items-center gap-2 justify-center">
                  <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                  {r}
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <>
            <div className="grid sm:grid-cols-[260px_1fr] gap-4">
              <Card variant="glass">
                <CardContent className="p-4">
                  <RiskGauge value={result.risk} title="P(DCS)" height={210} />
                </CardContent>
              </Card>

              <div className="space-y-3">
                {/* Point + interval */}
                <div className="surface p-4">
                  <p className="text-[11px] uppercase tracking-wider text-muted-foreground">
                    Calibrated estimate
                  </p>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span
                      className="display text-[34px] font-bold leading-none text-num"
                      style={{ color: riskColor }}
                    >
                      {result.risk.toFixed(2)}
                    </span>
                    <span className="text-[13px] text-muted-foreground">% P(DCS)</span>
                  </div>
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-[11px] text-muted-foreground mb-1">
                      <span>95 % interval</span>
                      <span className="pill-muted">illustrative</span>
                    </div>
                    <IntervalBar
                      low={result.interval.lowPercent}
                      point={result.risk}
                      high={result.interval.highPercent}
                    />
                    <p className="text-num text-[12px] mt-1.5">
                      [{result.interval.lowPercent.toFixed(2)} —{" "}
                      {result.interval.highPercent.toFixed(2)}] %
                    </p>
                  </div>
                </div>

                {/* Envelope verdict */}
                <div className="surface p-4 flex items-center gap-3">
                  <div className="h-9 w-9 rounded-lg bg-emerald-500/12 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
                    <ShieldCheck className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-[13px] font-semibold">In-envelope</p>
                    <p className="text-[11.5px] text-muted-foreground">
                      Inside the validated grid — prediction is supported.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Threshold alert */}
            {overThreshold && (
              <div className="rounded-xl border-l-2 border-red-500 bg-red-500/5 pl-4 pr-3 py-3 flex items-start gap-2">
                <AlertTriangle className="h-4 w-4 text-red-500 shrink-0 mt-0.5 animate-pulse-soft" />
                <p className="text-[12.5px] text-red-700 dark:text-red-300">
                  <strong>Threshold alert.</strong> Estimated P(DCS) is at or above the{" "}
                  {alertThresholdPct}% operational gate for this scenario. Mitigation (more
                  prebreathe, lower altitude, shorter exposure) is indicated.
                </p>
              </div>
            )}

            {/* Operational interpretation */}
            <div className="scientific-callout">
              {interpret({
                risk: result.risk,
                low: result.interval.lowPercent,
                high: result.interval.highPercent,
                inEnvelope: result.env.inEnvelope,
                state,
                overThreshold,
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function IntervalBar({
  low,
  point,
  high,
}: {
  low: number;
  point: number;
  high: number;
}): React.ReactElement {
  // Scale to a fixed 0–40 % visual window (typical training/flight band).
  const scaleMax = Math.max(40, high * 1.15);
  const pct = (v: number) => `${Math.min(100, (v / scaleMax) * 100)}%`;
  return (
    <div className="relative h-2.5 rounded-full bg-muted overflow-hidden">
      <div
        className="absolute top-0 bottom-0 rounded-full"
        style={{
          left: pct(low),
          width: `calc(${pct(high)} - ${pct(low)})`,
          background: "hsl(var(--primary) / 0.30)",
        }}
      />
      <div
        className="absolute top-1/2 -translate-y-1/2 h-3.5 w-1 rounded-full"
        style={{ left: pct(point), background: getRiskColor(point) }}
      />
    </div>
  );
}

export function UseCases(): React.ReactElement {
  return (
    <div className="space-y-6">
      {/* Hero */}
      <section className="surface-elevated p-6 lg:p-8 relative overflow-hidden">
        <div className="absolute inset-0 grid-overlay opacity-[0.16] pointer-events-none" />
        <div className="absolute -top-32 -left-24 w-96 h-96 rounded-full bg-primary/12 blur-3xl pointer-events-none" />
        <div className="relative max-w-2xl">
          <span className="pill-primary mb-3">
            <Plane className="h-3 w-3" /> Worked examples
          </span>
          <h2 className="display text-3xl font-bold tracking-tight mt-1">
            Two real scenarios, computed live.
          </h2>
          <p className="text-muted-foreground mt-3 text-[14px] leading-relaxed max-w-xl">
            Each panel computes the point P(DCS) from the closed-form ADRAC core in your browser as
            you move the sliders. The 95 % interval and the abstention behaviour illustrate the
            TinyDCS calibration layer. Point estimates are exact; intervals are marked{" "}
            <span className="pill-muted">illustrative</span>.
          </p>
        </div>
      </section>

      {/* Use case A */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
              <Plane className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-[16px]">
                A · Unpressurised flight above 25,000 ft
              </CardTitle>
              <p className="text-[12.5px] text-muted-foreground mt-0.5">
                General aviation / FL250+ · pilot on supplemental O₂, no prebreathe, mild cockpit
                activity.
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-1">
          <ScenarioPanel
            initial={{ altitude: 25000, timeAtAltitude: 60, prebreathe: 0, exercise: "Mild" }}
            altitudeRange={[18000, 45000]}
            prebreatheRange={[0, 60]}
            timeRange={[10, 240]}
            alertThresholdPct={5}
            interpret={({ risk, low, high, state, overThreshold }) => (
              <>
                <p className="font-semibold text-foreground mb-1 flex items-center gap-2">
                  <Mountain className="h-3.5 w-3.5" /> Operational read
                </p>
                <p className="text-muted-foreground leading-relaxed">
                  At {state.altitude.toLocaleString()} ft for {state.timeAtAltitude} min with no
                  prebreathe ({state.exercise.toLowerCase()} activity), the calibrated estimate is{" "}
                  <strong className="text-foreground text-num">{risk.toFixed(2)}%</strong> P(DCS),
                  95 % interval{" "}
                  <span className="text-num">
                    [{low.toFixed(2)}–{high.toFixed(2)}]%
                  </span>{" "}
                  (illustrative). The in-envelope flag confirms this is a supported prediction.{" "}
                  {overThreshold
                    ? "It has crossed the 5% gate — the tool alerts before the airman commits to the profile."
                    : "It sits under the 5% alert gate, but climbs steeply with altitude and exposure time — push the altitude slider up to watch the alert fire."}{" "}
                  Drag altitude past <strong className="text-foreground">40,000 ft</strong> and the
                  tool <strong className="text-foreground">refuses to predict</strong> — an
                  unpressurised excursion there is outside anything the model was validated on.
                </p>
              </>
            )}
          />
        </CardContent>
      </Card>

      {/* Use case B */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-accent/10 text-accent flex items-center justify-center">
              <TestTube2 className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-[16px]">B · Hypobaric chamber training</CardTitle>
              <p className="text-[12.5px] text-muted-foreground mt-0.5">
                Instructor planning a 35,000 ft profile · 100 % O₂ prebreathe · resting trainees.
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-1">
          <ScenarioPanel
            initial={{ altitude: 35000, timeAtAltitude: 30, prebreathe: 30, exercise: "Rest" }}
            altitudeRange={[18000, 40000]}
            prebreatheRange={[0, 120]}
            timeRange={[10, 120]}
            alertThresholdPct={5}
            interpret={({ risk, low, high, state, overThreshold }) => (
              <>
                <p className="font-semibold text-foreground mb-1 flex items-center gap-2">
                  <Wind className="h-3.5 w-3.5" /> Prebreathe planning
                </p>
                <p className="text-muted-foreground leading-relaxed">
                  At {state.altitude.toLocaleString()} ft for {state.timeAtAltitude} min with a{" "}
                  {state.prebreathe}-min 100 % O₂ prebreathe (resting), the calibrated estimate is{" "}
                  <strong className="text-foreground text-num">{risk.toFixed(2)}%</strong> P(DCS),
                  95 % interval{" "}
                  <span className="text-num">
                    [{low.toFixed(2)}–{high.toFixed(2)}]%
                  </span>{" "}
                  (illustrative).{" "}
                  {state.prebreathe === 0
                    ? "With zero prebreathe the risk is markedly higher — slide prebreathe up and watch the estimate and its interval contract."
                    : "Pulling prebreathe to 0 min roughly doubles the point risk, which is exactly the trade the instructor needs to see before signing the profile."}{" "}
                  {overThreshold
                    ? "The current profile is over the 5% gate; either add prebreathe or trim exposure."
                    : "The current profile sits under the 5% gate — prebreathe is doing its job."}{" "}
                  The narrowing interval as prebreathe increases is the calibration layer rewarding a
                  better-characterised, lower-risk exposure.
                </p>
              </>
            )}
          />
        </CardContent>
      </Card>
    </div>
  );
}
