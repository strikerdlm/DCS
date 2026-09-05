import React, { useCallback, useMemo, useState } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
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
import { chartTheme, getBaseChartOptions } from "../charts/chartConfig";
import { RiskGauge } from "../charts/RiskGauge";
import { RUT_UNAVAILABLE_REASON, runMechanisticSimulation } from "../../utils/models";
import { altitudeFtToPAmbAtm, formatNumber } from "../../lib/utils";
import { defaultMechanisticInputs, modelValidityCards } from "../../data/mockData";
import { ValidityPanel } from "./ValidityPanel";
import type { ExerciseLevel, MechanisticInputs, MechanisticSimulationResult } from "../../types";

export function Mechanistic3RUT(): React.ReactElement {
  const [inputs, setInputs] = useState<MechanisticInputs>(defaultMechanisticInputs);
  const [result, setResult] = useState<MechanisticSimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = useCallback(
    (field: keyof MechanisticInputs, value: number | string | boolean) => {
      setInputs((prev) => ({ ...prev, [field]: value }));
      setResult(null);
      setError(null);
    },
    [],
  );

  const handleRunSimulation = useCallback(() => {
    try {
      setResult(runMechanisticSimulation(inputs));
      setError(null);
    } catch (caught) {
      setResult(null);
      setError(caught instanceof Error ? caught.message : "Invalid pressure profile");
    }
  }, [inputs]);

  const handleExportCSV = useCallback(() => {
    if (!result) return;
    const headers = ["duration_min", "p_amb_atm", "fio2", "fin2", "exercise_l_min_above_rest"];
    const rows = result.segments.map((s) =>
      [s.durationMin, s.pAmbAtm, s.fio2, s.fin2, s.iExLMinWb].join(","),
    );
    const csv = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const ts = new Date().toISOString().replace(/[:.]/g, "-").replace(/Z$/, "");
    a.href = url;
    a.download = `tinydcs_pressure_profile_${ts}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [result]);

  const targetPressure = useMemo(() => {
    try { return altitudeFtToPAmbAtm(inputs.altitudeFt); } catch { return null; }
  }, [inputs.altitudeFt]);
  const pressureOption = useMemo<EChartsOption>(() => {
    let t = 0;
    const data: number[][] = [[0, 1]];
    for (const segment of result?.segments ?? []) {
      data.push([t, segment.pAmbAtm]);
      t += segment.durationMin;
      data.push([t, segment.pAmbAtm]);
    }
    const base = getBaseChartOptions();
    return {
      ...base,
      xAxis: { ...(base.xAxis as object), type: "value", name: "Profile time (min)", min: 0 },
      yAxis: { ...(base.yAxis as object), type: "value", name: "Ambient pressure (atm)", min: 0 },
      series: [{ type: "line", name: "Ambient pressure", showSymbol: false,
        data, lineStyle: { color: chartTheme.primaryColor, width: 2 } }],
    };
  }, [result]);

  return (
    <div className="space-y-6">
      {/* Hero */}
      <section className="surface-elevated p-6 lg:p-8 relative overflow-hidden">
        <div className="absolute inset-0 grid-overlay opacity-[0.18] pointer-events-none" />
        <div className="absolute -top-32 -left-20 w-96 h-96 rounded-full bg-accent/15 blur-3xl pointer-events-none" />
        <div className="relative">
          <span className="pill-accent mb-3">
            <Settings className="h-3 w-3" /> 3RUT-MBe1 · reconciliation open
          </span>
          <h2 className="display text-3xl font-bold tracking-tight mt-2">
            Exposure profile & model availability.
          </h2>
          <p className="text-muted-foreground mt-2 max-w-3xl text-[14px] leading-relaxed">
            {RUT_UNAVAILABLE_REASON} The profile below retains pressure, gas fractions,
            and exercise inputs for inspection and export.
          </p>
          <div className="flex flex-wrap items-center gap-2 mt-4">
            <span className="pill-accent">Pressure profile available</span>
            <span className="pill-muted">Absolute risk unavailable</span>
            <span className="pill-signal">Source reconciliation required</span>
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
              value={Number.isFinite(inputs.altitudeFt) ? inputs.altitudeFt : ""}
              onChange={(e) =>
                handleInputChange("altitudeFt", e.target.valueAsNumber)
              }
              unit="ft"
              min={0}
              max={63000}
              step={1000}
            />
            <Input
              label="Time at altitude"
              type="number"
              value={Number.isFinite(inputs.timeAtAltitudeMin) ? inputs.timeAtAltitudeMin : ""}
              onChange={(e) =>
                handleInputChange("timeAtAltitudeMin", e.target.valueAsNumber)
              }
              unit="min"
              min={0}
              max={600}
              step={10}
            />
            <Input
              label="Pre-breathe time"
              type="number"
              value={Number.isFinite(inputs.prebreathingTimeMin) ? inputs.prebreathingTimeMin : ""}
              onChange={(e) =>
                handleInputChange("prebreathingTimeMin", e.target.valueAsNumber)
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
                    value={Number.isFinite(inputs.ascentDurationMin) ? inputs.ascentDurationMin : ""}
                    onChange={(e) =>
                      handleInputChange(
                        "ascentDurationMin",
                        e.target.valueAsNumber,
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
            >
              <Play className="h-4 w-4 mr-2" /> Build pressure profile
            </Button>
          </CardContent>
        </Card>

        <div className="space-y-6 min-w-0">
          <div className="grid sm:grid-cols-4 gap-3">
            <MetricCard
              label="Altitude"
              value={Number.isFinite(inputs.altitudeFt) ? inputs.altitudeFt.toLocaleString() : "—"}
              unit="ft"
              icon={<Mountain className="h-4 w-4 text-primary" />}
            />
            <MetricCard
              label="Exposure"
              value={formatNumber(inputs.timeAtAltitudeMin, 0)}
              unit="min"
              icon={<Clock className="h-4 w-4 text-accent" />}
            />
            <MetricCard
              label="Pressure target"
              value={formatNumber(targetPressure, 3)}
              unit="atm"
              icon={<Gauge className="h-4 w-4 text-chart-2" />}
            />
            <MetricCard
              label="Final P(DCS)"
              value="Unavailable"
              unit="%"
              isRisk
              icon={<Activity className="h-4 w-4" />}
              description="3RUT reconciliation incomplete"
            />
          </div>

          <Card>
            <CardHeader className="pb-2 flex-row items-center justify-between">
              <div>
                <CardTitle className="text-[15px]">Pressure profile</CardTitle>
                <p className="text-[12.5px] text-muted-foreground mt-0.5">
                  Ambient pressure across prebreathe → ascent → exposure.
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
                        value={null}
                        title="3RUT-MBe1 absolute risk"
                        height={220}
                        max={40}
                      />
                    </div>
                  </div>
                  <ReactECharts option={pressureOption} notMerge style={{ height: "400px" }} />
                  <p className="text-[12px] text-muted-foreground">{result.reason}</p>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-72 text-muted-foreground gap-2">
                  <Play className="h-10 w-10 opacity-40" />
                  <p className="text-[14px]">{error ?? "Configure and build the pressure profile."}</p>
                  <p className="text-[12.5px]">Absolute risk remains unavailable.</p>
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
