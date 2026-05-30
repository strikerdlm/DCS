import React, { useCallback, useState } from "react";
import {
  Activity,
  Clock,
  Download,
  Gauge,
  Mountain,
  Play,
  Settings,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
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
      setInputs((prev) => ({ ...prev, [field]: value }));
    },
    [],
  );

  const handleRunSimulation = useCallback(() => {
    setIsSimulating(true);
    setTimeout(() => {
      setResult(runMechanisticSimulation(inputs));
      setIsSimulating(false);
    }, 350);
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
      ].join(","),
    );
    const csv = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const ts = new Date().toISOString().replace(/[:.]/g, "-").replace(/Z$/, "");
    a.href = url;
    a.download = `tinydcs_3rut_preview_${ts}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [result]);

  const targetPressure = altitudeFtToPAmbAtm(inputs.altitudeFt);

  return (
    <div className="space-y-6">
      {/* Hero */}
      <section className="surface-elevated p-6 lg:p-8 relative overflow-hidden">
        <div className="absolute inset-0 grid-overlay opacity-[0.18] pointer-events-none" />
        <div className="absolute -top-32 -left-20 w-96 h-96 rounded-full bg-accent/15 blur-3xl pointer-events-none" />
        <div className="relative">
          <span className="pill-accent mb-3">
            <Settings className="h-3 w-3" /> 3RUT-MBe1 schematic preview
          </span>
          <h2 className="display text-3xl font-bold tracking-tight mt-2">
            Time-resolved tissue dynamics & hazard channel.
          </h2>
          <p className="text-muted-foreground mt-2 max-w-3xl text-[14px] leading-relaxed">
            Browser preview of the NEDU TR 18-01 / Gerth 3RUT-MBe1 model: Conkin single-
            compartment N₂ uptake/washout, supersaturation × exercise hazard proxy, and
            the published ADRAC closed-form anchor for the final P(DCS). The full bubble-
            evolution recursion is in <code className="text-num text-[12px]">mechanistic/rut_mbe1.py</code>.
          </p>
          <div className="flex flex-wrap items-center gap-2 mt-4">
            <span className="pill-accent">Conkin τ½ = 360 min</span>
            <span className="pill-muted">Hazard proxy</span>
            <span className="pill-signal">Bubble channel illustrative only</span>
          </div>
        </div>
      </section>

      <div className="grid xl:grid-cols-[360px_1fr] gap-6">
        <Card className="xl:sticky xl:top-24 xl:self-start">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-[15px]">
              <Settings className="h-4 w-4 text-primary" /> Profile configuration
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
              label="Time at altitude"
              type="number"
              value={inputs.timeAtAltitudeMin}
              onChange={(e) =>
                handleInputChange("timeAtAltitudeMin", parseFloat(e.target.value) || 0)
              }
              unit="min"
              min={0}
              max={600}
              step={10}
            />
            <Input
              label="Pre-breathe time"
              type="number"
              value={inputs.prebreathingTimeMin}
              onChange={(e) =>
                handleInputChange("prebreathingTimeMin", parseFloat(e.target.value) || 0)
              }
              unit="min"
              min={0}
              max={240}
              step={5}
            />
            <div className="space-y-2">
              <label className="block text-[13px] font-medium text-foreground">
                Exercise at altitude
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
                  <SelectItem value="Rest">Rest (I_ex = 0)</SelectItem>
                  <SelectItem value="Mild">Mild (I_ex = 0.41)</SelectItem>
                  <SelectItem value="Heavy">Heavy (I_ex = 0.55)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Accordion type="single" collapsible>
              <AccordionItem value="advanced">
                <AccordionTrigger className="text-[13px]">Advanced</AccordionTrigger>
                <AccordionContent className="space-y-4 pt-2">
                  <div className="space-y-2">
                    <label className="block text-[13px] font-medium">
                      Exercise during prebreathe
                    </label>
                    <Select
                      value={inputs.prebreathingExerciseLevel}
                      onValueChange={(value) =>
                        handleInputChange(
                          "prebreathingExerciseLevel",
                          value as ExerciseLevel,
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
                    formatValue={(v) => `${(v * 100).toFixed(0)} %`}
                  />
                  <Switch
                    label="Breathe O₂ at altitude"
                    description="100 % O₂ during altitude exposure"
                    checked={inputs.breatheO2AtAltitude}
                    onCheckedChange={(v) =>
                      handleInputChange("breatheO2AtAltitude", v)
                    }
                  />
                  <Input
                    label="Ascent duration"
                    type="number"
                    value={inputs.ascentDurationMin}
                    onChange={(e) =>
                      handleInputChange(
                        "ascentDurationMin",
                        parseFloat(e.target.value) || 0,
                      )
                    }
                    unit="min"
                    min={0}
                    max={60}
                    step={1}
                  />
                  <Slider
                    label="Time step Δt"
                    value={[inputs.dtMin]}
                    onValueChange={([v]) => handleInputChange("dtMin", v)}
                    min={0.1}
                    max={2.0}
                    step={0.1}
                    formatValue={(v) => `${v.toFixed(2)} min`}
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
              <Play className="h-4 w-4 mr-2" /> Run simulation
            </Button>
          </CardContent>
        </Card>

        <div className="space-y-6 min-w-0">
          <div className="grid sm:grid-cols-4 gap-3">
            <MetricCard
              label="Altitude"
              value={inputs.altitudeFt.toLocaleString()}
              unit="ft"
              icon={<Mountain className="h-4 w-4 text-primary" />}
            />
            <MetricCard
              label="Exposure"
              value={inputs.timeAtAltitudeMin}
              unit="min"
              icon={<Clock className="h-4 w-4 text-accent" />}
            />
            <MetricCard
              label="Pressure target"
              value={targetPressure.toFixed(3)}
              unit="atm"
              icon={<Gauge className="h-4 w-4 text-chart-2" />}
            />
            <MetricCard
              label="Final P(DCS)"
              value={result ? result.finalPDcsPercent.toFixed(2) : "—"}
              unit="%"
              isRisk
              riskValue={result?.finalPDcsPercent ?? 0}
              icon={<Activity className="h-4 w-4" />}
              description="Anchored to ADRAC closed-form"
            />
          </div>

          <Card>
            <CardHeader className="pb-2 flex-row items-center justify-between">
              <div>
                <CardTitle className="text-[15px]">Time-resolved trajectories</CardTitle>
                <p className="text-[12.5px] text-muted-foreground mt-0.5">
                  Tissue gas, hazard rate, bubble proxy, and survival probability
                  across the prebreathe → ascent → exposure profile.
                </p>
              </div>
              {result && (
                <Button variant="outline" size="sm" onClick={handleExportCSV}>
                  <Download className="h-4 w-4 mr-2" />
                  CSV
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {result ? (
                <div className="space-y-6">
                  <div className="flex justify-center">
                    <div className="w-72">
                      <RiskGauge
                        value={result.finalPDcsPercent}
                        title="Final risk · ADRAC anchor"
                        height={220}
                        max={40}
                      />
                    </div>
                  </div>
                  <TimeSeriesChart
                    data={result.history}
                    height={620}
                    title="Mechanistic 3RUT-MBe1 — schematic preview"
                  />
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-72 text-muted-foreground gap-2">
                  <Play className="h-10 w-10 opacity-40" />
                  <p className="text-[14px]">Configure profile and run the simulation.</p>
                  <p className="text-[12.5px]">Trajectories will animate in.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      <ValidityPanel validity={modelValidityCards.mechanistic_3rut} />
    </div>
  );
}
