import React, { useState, useCallback } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/Card";
import { Input } from "../ui/Input";
import { Button } from "../ui/Button";
import { Slider } from "../ui/Slider";
import { Switch } from "../ui/Switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/Select";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "../ui/Accordion";
import { MetricCard } from "../ui/MetricCard";
import { TimeSeriesChart } from "../charts/TimeSeriesChart";
import { RiskGauge } from "../charts/RiskGauge";
import { runMechanisticSimulation } from "../../utils/models";
import { altitudeFtToPAmbAtm } from "../../lib/utils";
import { defaultMechanisticInputs, modelValidityCards } from "../../data/mockData";
import { ValidityPanel } from "./ValidityPanel";
import {
  Activity,
  Clock,
  Gauge,
  Mountain,
  Play,
  Download,
  Settings,
} from "lucide-react";
import type { ExerciseLevel, MechanisticInputs, ModelState } from "../../types";

export function Mechanistic3RUT(): React.ReactElement {
  const [inputs, setInputs] = useState<MechanisticInputs>(defaultMechanisticInputs);
  const [result, setResult] = useState<{
    history: ModelState[];
    finalPDcsPercent: number;
  } | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  const handleInputChange = useCallback(
    (field: keyof MechanisticInputs, value: number | string | boolean) => {
      setInputs((prev) => ({
        ...prev,
        [field]: value,
      }));
    },
    []
  );

  const handleRunSimulation = useCallback(() => {
    setIsSimulating(true);
    // Simulate async calculation
    setTimeout(() => {
      const simResult = runMechanisticSimulation(inputs);
      setResult(simResult);
      setIsSimulating(false);
    }, 800);
  }, [inputs]);

  const handleExportCSV = useCallback(() => {
    if (!result) return;

    const headers = [
      "t_min",
      "p_amb_atm",
      "pt_n2_atm",
      "pt_o2_atm",
      "n_b",
      "r_hat",
      "h_per_min",
      "p_dcs_percent",
    ];
    const rows = result.history.map((s) =>
      [
        s.tMin.toFixed(6),
        s.pAmbAtm.toFixed(9),
        s.ptN2Atm.toFixed(9),
        s.ptO2Atm.toFixed(9),
        s.nB.toExponential(9),
        s.rHat.toExponential(9),
        s.hPerMin.toExponential(9),
        (s.pDcs * 100).toFixed(9),
      ].join(",")
    );

    const csv = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "mechanistic_3rut_mbe1_results.csv";
    a.click();
    URL.revokeObjectURL(url);
  }, [result]);

  const targetPressure = altitudeFtToPAmbAtm(inputs.altitudeFt);

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">
          Mechanistic 3RUT‑MBe1 Simulation
        </h2>
        <p className="text-muted-foreground">
          Time-dependent bubble-evolution and survival/hazard recursion model based
          on NEDU TR 18‑01 (Appendix C/D). Supports time-varying covariates.
        </p>
      </div>

      {/* Main content grid */}
      <div className="grid lg:grid-cols-4 gap-6">
        {/* Input Panel */}
        <Card className="lg:col-span-1">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Settings className="h-5 w-5 text-primary" />
              Profile Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Altitude"
              type="number"
              value={inputs.altitudeFt}
              onChange={(e) =>
                handleInputChange("altitudeFt", parseFloat(e.target.value) || 0)
              }
              unit="ft"
              min={0}
              max={63000}
              step={1000}
            />

            <Input
              label="Time at Altitude"
              type="number"
              value={inputs.timeAtAltitudeMin}
              onChange={(e) =>
                handleInputChange(
                  "timeAtAltitudeMin",
                  parseFloat(e.target.value) || 0
                )
              }
              unit="min"
              min={0}
              max={600}
              step={10}
            />

            <Input
              label="Pre-breathe Time"
              type="number"
              value={inputs.prebreathingTimeMin}
              onChange={(e) =>
                handleInputChange(
                  "prebreathingTimeMin",
                  parseFloat(e.target.value) || 0
                )
              }
              unit="min"
              min={0}
              max={240}
              step={5}
            />

            <div className="space-y-2">
              <label className="block text-sm font-medium">
                Exercise at Altitude
              </label>
              <Select
                value={inputs.altitudeExerciseLevel}
                onValueChange={(value) =>
                  handleInputChange("altitudeExerciseLevel", value as ExerciseLevel)
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Rest">Rest</SelectItem>
                  <SelectItem value="Mild">Mild (I_ex = 0.41)</SelectItem>
                  <SelectItem value="Heavy">Heavy (I_ex = 0.55)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Advanced Options */}
            <Accordion type="single" collapsible>
              <AccordionItem value="advanced">
                <AccordionTrigger className="text-sm">
                  Advanced Options
                </AccordionTrigger>
                <AccordionContent className="space-y-4 pt-2">
                  <div className="space-y-2">
                    <label className="block text-sm font-medium">
                      Exercise During Prebreathe
                    </label>
                    <Select
                      value={inputs.prebreathingExerciseLevel}
                      onValueChange={(value) =>
                        handleInputChange(
                          "prebreathingExerciseLevel",
                          value as ExerciseLevel
                        )
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Rest">Rest</SelectItem>
                        <SelectItem value="Mild">Mild</SelectItem>
                        <SelectItem value="Heavy">Heavy</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Slider
                    label="Prebreathe FiO₂"
                    value={[inputs.prebreathFio2]}
                    onValueChange={([v]) => handleInputChange("prebreathFio2", v)}
                    min={0.21}
                    max={1.0}
                    step={0.01}
                    formatValue={(v) => (v * 100).toFixed(0) + "%"}
                  />

                  <Switch
                    label="Breathe O₂ at Altitude"
                    description="Use 100% O₂ during altitude exposure"
                    checked={inputs.breatheO2AtAltitude}
                    onCheckedChange={(v) =>
                      handleInputChange("breatheO2AtAltitude", v)
                    }
                  />

                  <Input
                    label="Ascent Duration"
                    type="number"
                    value={inputs.ascentDurationMin}
                    onChange={(e) =>
                      handleInputChange(
                        "ascentDurationMin",
                        parseFloat(e.target.value) || 0
                      )
                    }
                    unit="min"
                    min={0}
                    max={60}
                    step={1}
                  />

                  <Slider
                    label="Time Step (dt)"
                    value={[inputs.dtMin]}
                    onValueChange={([v]) => handleInputChange("dtMin", v)}
                    min={0.01}
                    max={0.5}
                    step={0.01}
                    unit="min"
                    formatValue={(v) => v.toFixed(2)}
                  />
                </AccordionContent>
              </AccordionItem>
            </Accordion>

            <Button
              onClick={handleRunSimulation}
              className="w-full"
              size="lg"
              isLoading={isSimulating}
            >
              <Play className="h-4 w-4 mr-2" />
              Run Simulation
            </Button>
          </CardContent>
        </Card>

        {/* Results Panel */}
        <div className="lg:col-span-3 space-y-6">
          {/* Summary Metrics */}
          <div className="grid sm:grid-cols-4 gap-4">
            <MetricCard
              label="Altitude"
              value={inputs.altitudeFt.toLocaleString()}
              unit="ft"
              icon={<Mountain className="h-4 w-4 text-blue-500" />}
            />
            <MetricCard
              label="Exposure Duration"
              value={inputs.timeAtAltitudeMin}
              unit="min"
              icon={<Clock className="h-4 w-4 text-amber-500" />}
            />
            <MetricCard
              label="Target Pressure"
              value={targetPressure.toFixed(4)}
              unit="atm"
              icon={<Gauge className="h-4 w-4 text-purple-500" />}
            />
            <MetricCard
              label="Final P(DCS)"
              value={result ? result.finalPDcsPercent.toFixed(3) : "—"}
              unit="%"
              isRisk
              riskValue={result?.finalPDcsPercent ?? 0}
              icon={<Activity className="h-4 w-4" />}
            />
          </div>

          {/* Simulation Results */}
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Simulation Results</CardTitle>
                  <CardDescription>
                    Time-resolved model state evolution
                  </CardDescription>
                </div>
                {result && (
                  <Button variant="outline" size="sm" onClick={handleExportCSV}>
                    <Download className="h-4 w-4 mr-2" />
                    Export CSV
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {result ? (
                <div className="space-y-6">
                  {/* Risk Gauge */}
                  <div className="flex justify-center">
                    <div className="w-72">
                      <RiskGauge
                        value={result.finalPDcsPercent}
                        title="Final DCS Risk"
                        height={220}
                      />
                    </div>
                  </div>

                  {/* Time Series Charts */}
                  <TimeSeriesChart
                    data={result.history}
                    height={700}
                    title="Time-Resolved Model Variables"
                  />
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-96 text-gray-400">
                  <Activity className="h-16 w-16 mb-4 opacity-50" />
                  <p className="text-lg">Configure profile and run simulation</p>
                  <p className="text-sm">
                    Results will show time-resolved model variables
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Validity Panel */}
      <ValidityPanel validity={modelValidityCards.mechanistic_3rut} />
    </div>
  );
}
