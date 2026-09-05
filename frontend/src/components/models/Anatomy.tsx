import React, { useMemo, useState } from "react";
import {
  Activity,
  Brain,
  Compass,
  Gauge,
  Layers,
  Map as MapIcon,
  Mountain,
  Wind,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
import { Slider } from "../ui/Slider";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/Select";
import { AtmosphereColumn } from "../charts/AtmosphereColumn";
import { MissionPressureProfile } from "../charts/MissionPressureProfile";
import { LogitProbabilityBridge } from "../charts/LogitProbabilityBridge";
import { RiskIsobars } from "../charts/RiskIsobars";
import { checkEnvelope, decomposeADRAC, VALIDITY_ENVELOPE } from "../../utils/models";
import { altitudeFtToMmHg, altitudeFtToPAmbAtm, formatNumber, getRiskLevel } from "../../lib/utils";
import { defaultMLInputs } from "../../data/mockData";
import type { ExerciseLevel, MLSurrogateInputs } from "../../types";

const EXERCISE: ExerciseLevel[] = ["Rest", "Mild", "Heavy"];

/**
 * Anatomy of an altitude-DCS prediction — a visual explainer.
 *
 * Four charts, one scenario. Move the levers and watch the same exposure
 * propagate through the physics (pressure vs tissue N₂), the math (log-odds →
 * probability), the geography (altitude × prebreathe isobars), and the
 * position (where you sit in the atmospheric column). All four are driven by
 * the closed-form ADRAC core, so they stay mutually consistent in real time.
 */
export function Anatomy(): React.ReactElement {
  const [inputs, setInputs] = useState<MLSurrogateInputs>(defaultMLInputs);
  const set = (patch: Partial<MLSurrogateInputs>) =>
    setInputs((s) => ({ ...s, ...patch }));

  const read = useMemo(() => {
    const envelope = checkEnvelope(
      inputs.altitude,
      inputs.prebreathingTime,
      inputs.timeAtAltitude,
      inputs.exerciseLevel,
    );
    const decomp = envelope.inEnvelope ? decomposeADRAC(inputs) : null;
    const risk = decomp?.riskPercent ?? null;
    return {
      envelope,
      risk,
      omega: decomp?.omega ?? null,
      level: getRiskLevel(risk),
      pAtm: altitudeFtToPAmbAtm(inputs.altitude),
      pMmHg: altitudeFtToMmHg(inputs.altitude),
    };
  }, [inputs]);

  const levelPill =
    read.level === "unavailable" ? "pill-muted" : read.level === "low" ? "pill-low" : read.level === "moderate" ? "pill-signal" : "pill-high";

  return (
    <div className="space-y-6">
      {/* Hero */}
      <section className="surface-elevated p-6 lg:p-10 relative overflow-hidden grain">
        <div className="absolute inset-0 grid-overlay opacity-[0.16] pointer-events-none" />
        <div className="absolute -top-40 -right-24 w-[28rem] h-[28rem] rounded-full bg-primary/15 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-44 -left-24 w-[24rem] h-[24rem] rounded-full bg-accent/10 blur-3xl pointer-events-none" />
        <div className="relative max-w-3xl">
          <span className="pill-primary mb-4">
            <Layers className="h-3 w-3" /> Anatomy of a prediction
          </span>
          <h2 className="display text-3xl lg:text-[2.6rem] font-bold tracking-tight leading-[1.08]">
            One exposure, followed through{" "}
            <span className="text-primary">physics, math, geography, and position</span>.
          </h2>
          <p className="text-muted-foreground mt-4 text-[15px] leading-relaxed">
            TinyDCS turns four exposure inputs into an ADRAC baseline estimate. This page shows
            related pressure and tissue diagnostics, the
            log-logistic probability calculation, the altitude × prebreathe map you inspect
            against, and the column of air you are sitting in. Move the levers once; every panel
            recomputes from the same closed-form core.
          </p>
        </div>
      </section>

      {/* Shared scenario control */}
      <Card className="lg:sticky lg:top-24 lg:z-20">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-[15px]">
            <Compass className="h-4 w-4 text-primary" /> Scenario — drives every panel below
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5">
            <Slider
              label="Altitude"
              value={[inputs.altitude]}
              onValueChange={([v]) => set({ altitude: v })}
              min={VALIDITY_ENVELOPE.altitudeFt[0]}
              max={VALIDITY_ENVELOPE.altitudeFt[1]}
              step={500}
              unit="ft"
              formatValue={(v) => v.toLocaleString()}
            />
            <Slider
              label="Time at altitude"
              value={[inputs.timeAtAltitude]}
              onValueChange={([v]) => set({ timeAtAltitude: v })}
              min={VALIDITY_ENVELOPE.timeAtAltitudeMin[0]}
              max={VALIDITY_ENVELOPE.timeAtAltitudeMin[1]}
              step={5}
              unit="min"
            />
            <Slider
              label="100% O₂ prebreathe"
              value={[inputs.prebreathingTime]}
              onValueChange={([v]) => set({ prebreathingTime: v })}
              min={VALIDITY_ENVELOPE.prebreatheMin[0]}
              max={VALIDITY_ENVELOPE.prebreatheMin[1]}
              step={5}
              unit="min"
            />
            <div className="space-y-2">
              <label className="block text-sm font-medium">Exercise</label>
              <Select
                value={inputs.exerciseLevel}
                onValueChange={(v) => set({ exerciseLevel: v as ExerciseLevel })}
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
          </div>
          <div className="flex flex-wrap items-center gap-2 mt-5 pt-4 border-t border-border/60">
            <span className={levelPill}>
              <Activity className="h-3 w-3" />
              P(DCS) {read.risk === null ? "unavailable" : `${formatNumber(read.risk)}% · ${read.level}`}
            </span>
            <span className="pill-muted text-num">
              ω = {formatNumber(read.omega)}
            </span>
            <span className="pill-muted text-num">
              {inputs.altitude.toLocaleString()} ft · {read.pMmHg.toFixed(0)} mmHg ({read.pAtm.toFixed(2)} atm)
            </span>
            <span className="pill-muted text-num">
              {inputs.timeAtAltitude} min @ alt · {inputs.prebreathingTime} min PB · {inputs.exerciseLevel}
            </span>
          </div>
          {!read.envelope.inEnvelope && (
            <p role="status" className="scientific-callout mt-4 text-[13px]">
              Prediction unavailable: {read.envelope.reasons.join(". ")}. Pressure and tissue diagnostics remain available.
            </p>
          )}
        </CardContent>
      </Card>

      {/* 1. Position — atmosphere column */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-[15px]">
            <Mountain className="h-4 w-4 text-primary" /> 01 · Position — where you are in the sky
          </CardTitle>
          <p className="text-[12.5px] text-muted-foreground mt-1 max-w-3xl">
            Altitude sets ambient pressure, and ambient pressure sets how much dissolved nitrogen
            tissue can hold at equilibrium. The 18–40 kft region is the supported model range; the glowing
            marker is the live scenario riding that column.
          </p>
        </CardHeader>
        <CardContent>
          <AtmosphereColumn inputs={inputs} />
        </CardContent>
      </Card>

      {/* 2. Physics — pressure vs tissue N2 */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-[15px]">
            <Wind className="h-4 w-4 text-accent" /> 02 · Physics — the pressure differential
          </CardTitle>
          <p className="text-[12.5px] text-muted-foreground mt-1 max-w-3xl">
            The indigo line is total ambient pressure; the amber line is the nitrogen tension in a
            fixed 360-min tissue compartment. The shaded positive difference is a simplified
            supersaturation diagnostic, not a bubble calculation or a quantified DCS hazard.
          </p>
        </CardHeader>
        <CardContent className="space-y-2">
          <MissionPressureProfile inputs={inputs} height={340} />
          <div className="equation-block">
            <div className="eq">
              <span className="eq-var">P</span><sub>tN₂</sub>(<span className="eq-var">t</span>) = <span className="eq-var">P</span><sub>insp,N₂</sub> − (<span className="eq-var">P</span><sub>insp,N₂</sub> − <span className="eq-var">P</span><sub>tN₂</sub>(0)) · e<sup>−<span className="eq-var">t</span>/<span className="eq-var">τ</span></sup>
              <span className="eq-op">,</span>
              <span className="eq-var">τ</span> = <span className="eq-var">t</span><sub>½</sub> / ln 2
            </div>
            <div className="eq-caption">
              single 360-min compartment. Ratio <em>R</em> = <em>P</em><sub>tN₂</sub> / <em>P</em><sub>amb</sub>; <em>R</em> &gt; 1 means nitrogen tension exceeds ambient pressure.
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 3. Math — logit to probability */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-[15px]">
            <Brain className="h-4 w-4 text-primary" /> 03 · Math — log-odds to probability
          </CardTitle>
          <p className="text-[12.5px] text-muted-foreground mt-1 max-w-3xl">
            The exposure becomes a single log-odds ω, then the logistic curve bends it into a
            probability. The covariate tornado builds ω term by term; this curve is the non-linear
            step that turns that sum into the number on the gauge. It is painted with the four-zone
            risk ramp so colour itself reads as severity.
          </p>
        </CardHeader>
        <CardContent className="space-y-2">
          {read.envelope.inEnvelope ? <LogitProbabilityBridge inputs={inputs} height={320} /> : (
            <p className="text-sm text-muted-foreground">Probability plot unavailable outside the supported input range.</p>
          )}
          <div className="equation-block">
            <div className="eq">
              <span className="eq-var">ω</span> = (ln <span className="eq-var">t</span> − <span className="eq-var">β</span><sub>2</sub> − <span className="eq-var">β</span>·<span className="eq-var">x</span>) / <span className="eq-var">β</span><sub>1</sub>
              <span className="eq-op">,</span>
              <span className="eq-fn">P</span>(DCS) = <span className="eq-fn">σ</span>(<span className="eq-var">ω</span>) = 1 / (1 + e<sup>−<span className="eq-var">ω</span></sup>)
            </div>
            <div className="eq-caption">
              log-logistic accelerated-failure-time form (Kannan &amp; Pilmanis 1998); <em>x</em> = [<em>P</em><sub>amb</sub>, prebreathe, 1<sub>mild</sub>, 1<sub>heavy</sub>].
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 4. Geography — risk isobars */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-[15px]">
            <MapIcon className="h-4 w-4 text-accent" /> 04 · Geography — the operating map
          </CardTitle>
          <p className="text-[12.5px] text-muted-foreground mt-1 max-w-3xl">
            The two mission-planning levers — altitude and prebreathe — against each other, with the
            1 / 5 / 20 % contours drawn as model comparisons. These illustrative thresholds do not
            certify operational safety; the dashed frame marks the supported input range.
          </p>
        </CardHeader>
        <CardContent>
          {read.envelope.inEnvelope ? <RiskIsobars inputs={inputs} height={420} /> : (
            <p className="text-sm text-muted-foreground">Probability map unavailable outside the supported input range.</p>
          )}
        </CardContent>
      </Card>

      {/* Honest framing */}
      <Card variant="glass">
        <CardContent className="p-5 lg:p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="shrink-0">
              <div
                className="h-11 w-11 rounded-xl flex items-center justify-center"
                style={{ background: "hsl(var(--signal) / 0.14)", color: "hsl(var(--signal))" }}
              >
                <Gauge className="h-5 w-5" />
              </div>
            </div>
            <div className="space-y-2">
              <h3 className="display text-[15px] font-semibold">What these panels compute</h3>
              <p className="text-[13px] text-muted-foreground leading-relaxed">
                Every figure on this page is the <strong className="text-foreground">closed-form ADRAC
                core</strong> or a separately labelled physical diagnostic. The browser baseline
                uses bundled coefficients and has no validated prediction interval. The pressure
                profile follows a single 360-min nitrogen compartment with a finite ascent; its
                longer washout differs from the instantaneous-ascent tissue feature. No 3RUT
                bubble or hazard model is executed here.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
