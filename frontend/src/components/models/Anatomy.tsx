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
import { decomposeADRAC, predictADRAC } from "../../utils/models";
import { altitudeFtToMmHg, altitudeFtToPAmbAtm, getRiskLevel } from "../../lib/utils";
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
    const { riskFraction } = predictADRAC(
      inputs.altitude,
      inputs.prebreathingTime,
      inputs.exerciseLevel,
      inputs.timeAtAltitude,
    );
    const decomp = decomposeADRAC(inputs);
    return {
      risk: riskFraction * 100,
      omega: decomp.omega,
      level: getRiskLevel(riskFraction * 100),
      pAtm: altitudeFtToPAmbAtm(inputs.altitude),
      pMmHg: altitudeFtToMmHg(inputs.altitude),
    };
  }, [inputs]);

  const levelPill =
    read.level === "low" ? "pill-low" : read.level === "moderate" ? "pill-signal" : "pill-high";

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
            TinyDCS turns four flight-schedule numbers into a calibrated risk. This page follows that
            single transformation end to end — the pressure differential that causes bubbles, the
            log-logistic that turns it into a probability, the altitude × prebreathe map you plan
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
              min={18000}
              max={40000}
              step={500}
              unit="ft"
              formatValue={(v) => v.toLocaleString()}
            />
            <Slider
              label="Time at altitude"
              value={[inputs.timeAtAltitude]}
              onValueChange={([v]) => set({ timeAtAltitude: v })}
              min={10}
              max={240}
              step={5}
              unit="min"
            />
            <Slider
              label="100% O₂ prebreathe"
              value={[inputs.prebreathingTime]}
              onValueChange={([v]) => set({ prebreathingTime: v })}
              min={0}
              max={180}
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
              P(DCS) {read.risk.toFixed(2)}% · {read.level}
            </span>
            <span className="pill-muted text-num">
              ω = {read.omega.toFixed(2)}
            </span>
            <span className="pill-muted text-num">
              {inputs.altitude.toLocaleString()} ft · {read.pMmHg.toFixed(0)} mmHg ({read.pAtm.toFixed(2)} atm)
            </span>
            <span className="pill-muted text-num">
              {inputs.timeAtAltitude} min @ alt · {inputs.prebreathingTime} min PB · {inputs.exerciseLevel}
            </span>
          </div>
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
            tissue can hold. The validated 18–40 kft envelope is the operational band; the glowing
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
            DCS is a race between ambient pressure dropping and tissue nitrogen washing out. The
            indigo line is the air; the amber line is the tissue. Where the tissue rides above the
            air — the vermillion gap — gas can come out of solution. That gap is the entire reason
            this model exists.
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
              single 360-min compartment (Conkin). Supersaturation ratio <em>R</em> = <em>P</em><sub>tN₂</sub> / <em>P</em><sub>amb</sub>; <em>R</em> &gt; 1 is the hazard.
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
          <LogitProbabilityBridge inputs={inputs} height={320} />
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
            1 / 5 / 20 % risk thresholds drawn as contour isobars. Stay below the 5 % isobar and the
            profile is operationally safe; the dashed frame is the validity envelope, beyond which
            the model abstains rather than extrapolate.
          </p>
        </CardHeader>
        <CardContent>
          <RiskIsobars inputs={inputs} height={420} />
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
                core</strong> evaluated in your browser — deterministic and ~0.1 ms. The trained
                TinyDCS stack (monotone LightGBM logit, Mahalanobis out-of-distribution gate, and the
                zero-inflated two-stage conformal calibrator that produces the real 95 % intervals)
                runs server-side and ships as a 95 KB ONNX for the edge; the browser build uses the
                ADRAC functional form so the explainer is reproducible from the coefficient JSON the
                repo ships. The pressure-profile integration is a single 360-min compartment
                schematic consistent with the <code className="text-num text-[11px]">tissue_n2_ratio_360</code> feature, not the full 3RUT bubble-evolution recursion.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}