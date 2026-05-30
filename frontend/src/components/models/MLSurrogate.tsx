import React, { useCallback, useMemo, useState } from "react";
import {
  Activity,
  Clock,
  Compass,
  Gauge,
  Mountain,
  Wind,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
import { Input } from "../ui/Input";
import { Button } from "../ui/Button";
import { MetricCard } from "../ui/MetricCard";
import { RiskGauge } from "../charts/RiskGauge";
import { RiskLandscape } from "../charts/RiskLandscape";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/Select";
import {
  generateRiskLandscape,
  predictMLSurrogate,
} from "../../utils/models";
import { altitudeFtToMmHg, altitudeFtToPAmbAtm } from "../../lib/utils";
import { defaultMLInputs, modelValidityCards } from "../../data/mockData";
import { ValidityPanel } from "./ValidityPanel";
import type {
  ExerciseLevel,
  MLSurrogateInputs,
  MLSurrogatePrediction,
} from "../../types";

const EXERCISE_OPTIONS: { value: ExerciseLevel; label: string; vo2: string }[] = [
  { value: "Rest", label: "Rest", vo2: "≈ 0.0 L·min⁻¹" },
  { value: "Mild", label: "Mild", vo2: "≈ 0.41 L·min⁻¹" },
  { value: "Heavy", label: "Heavy", vo2: "≈ 0.55 L·min⁻¹" },
];

export function MLSurrogate(): React.ReactElement {
  const [inputs, setInputs] = useState<MLSurrogateInputs>(defaultMLInputs);
  const [prediction, setPrediction] = useState<MLSurrogatePrediction | null>(() =>
    predictMLSurrogate(defaultMLInputs),
  );
  const [isCalculating, setIsCalculating] = useState(false);

  const handleInputChange = useCallback(
    (field: keyof MLSurrogateInputs, value: number | string) => {
      setInputs((prev) => ({ ...prev, [field]: value }));
    },
    [],
  );

  const handleCalculate = useCallback(() => {
    setIsCalculating(true);
    setTimeout(() => {
      setPrediction(predictMLSurrogate(inputs));
      setIsCalculating(false);
    }, 280);
  }, [inputs]);

  const liveLandscape = useMemo(
    () =>
      generateRiskLandscape({
        prebreatheMin: inputs.prebreathingTime,
        exerciseLevel: inputs.exerciseLevel,
        altitudeRange: [18000, 40000],
        timeRange: [10, 240],
        altitudeSteps: 23,
        timeSteps: 24,
      }),
    [inputs.prebreathingTime, inputs.exerciseLevel],
  );

  const pAtm = altitudeFtToPAmbAtm(inputs.altitude);
  const pMmHg = altitudeFtToMmHg(inputs.altitude);

  return (
    <div className="space-y-6">
      {/* Hero */}
      <section className="surface-elevated p-6 lg:p-8 relative overflow-hidden">
        <div className="absolute inset-0 grid-overlay opacity-[0.18] pointer-events-none" />
        <div className="absolute -top-32 -right-32 w-96 h-96 rounded-full bg-primary/15 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-40 -left-20 w-80 h-80 rounded-full bg-accent/10 blur-3xl pointer-events-none" />
        <div className="relative grid lg:grid-cols-[1fr_auto] gap-8 items-center">
          <div>
            <span className="pill-primary mb-3">
              <Compass className="h-3 w-3" /> ADRAC closed-form
            </span>
            <h2 className="display text-3xl font-bold tracking-tight mt-2">
              Altitude-DCS risk, calibrated to the published log-logistic.
            </h2>
            <p className="text-muted-foreground mt-2 max-w-2xl text-[14px] leading-relaxed">
              Pilmanis (2004) functional form, fitted in <code className="text-num text-[12px]">mechanistic/adrac.py</code> on
              the cleaned ADRAC grid (n = 15,908). The browser bundle uses this closed
              form so predictions are deterministic, ~0.1 ms, and reproducible from the
              same coefficient JSON the repository ships.
            </p>
            <div className="flex flex-wrap items-center gap-2 mt-4">
              <span className="pill-muted">MAE 8.74 pp</span>
              <span className="pill-muted">RMSE 12.34 pp</span>
              <span className="pill-muted">R² 0.864</span>
              <span className="pill-accent">13-feature vector</span>
            </div>
          </div>
        </div>
      </section>

      <div className="grid lg:grid-cols-[360px_1fr] gap-6">
        {/* Inputs */}
        <Card className="lg:sticky lg:top-24 lg:self-start">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-[15px]">
              <Gauge className="h-4 w-4 text-primary" />
              Exposure parameters
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Altitude"
              type="number"
              value={inputs.altitude}
              onChange={(e) =>
                handleInputChange("altitude", parseFloat(e.target.value) || 0)
              }
              unit="ft"
              min={0}
              max={63000}
              step={500}
              description="Target altitude for exposure (validity 18 000 – 40 000 ft)"
            />
            <Input
              label="Time at altitude"
              type="number"
              value={inputs.timeAtAltitude}
              onChange={(e) =>
                handleInputChange("timeAtAltitude", parseFloat(e.target.value) || 0)
              }
              unit="min"
              min={0}
              max={600}
              step={5}
              description="Duration of altitude exposure (validity 10 – 240 min)"
            />
            <Input
              label="Pre-breathe time"
              type="number"
              value={inputs.prebreathingTime}
              onChange={(e) =>
                handleInputChange("prebreathingTime", parseFloat(e.target.value) || 0)
              }
              unit="min"
              min={0}
              max={240}
              step={5}
              description="100 % O₂ prebreathe before ascent"
            />
            <div className="space-y-2">
              <label className="block text-[13px] font-medium text-foreground">
                Exercise level
              </label>
              <Select
                value={inputs.exerciseLevel}
                onValueChange={(value) =>
                  handleInputChange("exerciseLevel", value as ExerciseLevel)
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select exercise level" />
                </SelectTrigger>
                <SelectContent>
                  {EXERCISE_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      <div className="flex items-baseline justify-between gap-3 w-full">
                        <span>{opt.label}</span>
                        <span className="text-num text-[11px] text-muted-foreground">
                          {opt.vo2}
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-[11.5px] text-muted-foreground">
                Whole-body O₂ consumption above rest (Webb 2010 metric).
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-border/60">
              <div>
                <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Pressure</p>
                <p className="text-num text-[15px] font-semibold">
                  {pAtm.toFixed(3)} <span className="text-[11px] text-muted-foreground">atm</span>
                </p>
                <p className="text-num text-[11px] text-muted-foreground">
                  {pMmHg.toFixed(0)} mmHg
                </p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Bench</p>
                <p className="text-num text-[15px] font-semibold">
                  {prediction ? prediction.riskPercent.toFixed(2) : "—"}<span className="text-[11px] text-muted-foreground"> %</span>
                </p>
                <p className="text-num text-[11px] text-muted-foreground">
                  P(DCS) instant
                </p>
              </div>
            </div>

            <Button
              onClick={handleCalculate}
              className="w-full"
              size="lg"
              isLoading={isCalculating}
            >
              Recompute prediction
            </Button>
          </CardContent>
        </Card>

        {/* Results */}
        <div className="space-y-6 min-w-0">
          {/* Top row — gauge + key metrics */}
          <div className="grid xl:grid-cols-[420px_1fr] gap-6">
            <Card variant="glass">
              <CardContent className="p-6">
                <RiskGauge
                  value={prediction?.riskPercent ?? 0}
                  title="P(DCS)"
                  height={300}
                  max={40}
                />
              </CardContent>
            </Card>

            <div className="grid sm:grid-cols-2 gap-3">
              <MetricCard
                label="Altitude"
                value={inputs.altitude.toLocaleString()}
                unit="ft"
                icon={<Mountain className="h-4 w-4 text-primary" />}
                description="Target exposure altitude"
              />
              <MetricCard
                label="Time at altitude"
                value={inputs.timeAtAltitude}
                unit="min"
                icon={<Clock className="h-4 w-4 text-accent" />}
                description="Exposure duration"
              />
              <MetricCard
                label="Prebreathe"
                value={inputs.prebreathingTime}
                unit="min"
                icon={<Wind className="h-4 w-4 text-chart-2" />}
                description="100 % O₂ window before ascent"
              />
              <MetricCard
                label="Predicted P(DCS)"
                value={prediction ? prediction.riskPercent.toFixed(2) : "—"}
                unit="%"
                isRisk
                riskValue={prediction?.riskPercent ?? 0}
                icon={<Activity className="h-4 w-4" />}
                description={prediction ? `Exercise ≈ ${inputs.exerciseLevel}` : ""}
              />
            </div>
          </div>

          {/* Risk landscape */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-[15px]">Risk landscape</CardTitle>
              <p className="text-[12.5px] text-muted-foreground mt-0.5">
                Predicted P(DCS) over altitude × time-at-altitude with the current
                prebreathe ({inputs.prebreathingTime} min) and exercise ({inputs.exerciseLevel}).
                The marker shows the current scenario.
              </p>
            </CardHeader>
            <CardContent className="pt-2">
              <RiskLandscape
                points={liveLandscape}
                highlight={{
                  altitudeFt: inputs.altitude,
                  timeAtAltitudeMin: inputs.timeAtAltitude,
                }}
                height={420}
              />
            </CardContent>
          </Card>

          {/* Feature vector */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-[15px]">Feature vector</CardTitle>
              <p className="text-[12.5px] text-muted-foreground mt-0.5">
                The 13-element feature vector that feeds the closed-form predictor —
                identical structure to the LightGBM/ONNX surrogate's input tensor
                (<code className="text-num text-[11px]">tinydcs/features.py</code>).
              </p>
            </CardHeader>
            <CardContent>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
                {(prediction?.features ?? []).map((f) => (
                  <div
                    key={f.name}
                    className="flex items-baseline justify-between gap-2 px-3 py-2 rounded-lg bg-muted/40 border border-border/40"
                  >
                    <span className="text-[12.5px] text-muted-foreground truncate">
                      {f.name}
                    </span>
                    <span className="text-num text-[12.5px] font-medium tabular-nums">
                      {Number.isFinite(f.value)
                        ? Math.abs(f.value) >= 1000
                          ? f.value.toExponential(2)
                          : f.value.toFixed(3)
                        : "—"}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <ValidityPanel validity={modelValidityCards.ml_surrogate} />
    </div>
  );
}
