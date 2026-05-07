import React, { useMemo, useState } from "react";
import {
  AlertCircle,
  BarChart3,
  Database,
  Download,
  Filter,
  TrendingUp,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
import { Button } from "../ui/Button";
import { MetricCard } from "../ui/MetricCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/Tabs";
import { Slider } from "../ui/Slider";
import { Heatmap } from "../charts/Heatmap";
import { Histogram } from "../charts/Histogram";
import { ScatterPlot } from "../charts/ScatterPlot";
import { validationData, validationMetrics } from "../../data/mockData";
import type { ExerciseLevel, RegressionMetrics } from "../../types";

interface FilterState {
  exerciseLevels: ExerciseLevel[];
  altitudeRange: [number, number];
  timeRange: [number, number];
}

export function ValidationDashboard(): React.ReactElement {
  const [filters, setFilters] = useState<FilterState>({
    exerciseLevels: ["Rest", "Mild", "Heavy"],
    altitudeRange: [0, 63000],
    timeRange: [0, 600],
  });
  const [showWorstN, setShowWorstN] = useState(10);

  const filteredData = useMemo(() => {
    return validationData.filter((d) => {
      const exerciseOk = filters.exerciseLevels.includes(
        d.exerciseLevel as ExerciseLevel,
      );
      const altOk =
        d.altitude >= filters.altitudeRange[0] &&
        d.altitude <= filters.altitudeRange[1];
      const timeOk =
        d.timeAtAltitude >= filters.timeRange[0] &&
        d.timeAtAltitude <= filters.timeRange[1];
      return exerciseOk && altOk && timeOk;
    });
  }, [filters]);

  const metrics = useMemo((): RegressionMetrics => {
    if (filteredData.length === 0)
      return { r2: 0, mae: 0, rmse: 0, mse: 0 };
    const n = filteredData.length;
    const yTrue = filteredData.map((d) => d.riskOfDcs);
    const yPred = filteredData.map((d) => d.predictedRisk ?? d.riskOfDcs);
    const mean = yTrue.reduce((a, b) => a + b, 0) / n;
    let ssRes = 0,
      ssTot = 0,
      sumAbs = 0,
      sumSq = 0;
    for (let i = 0; i < n; i++) {
      const r = yPred[i] - yTrue[i];
      ssRes += r * r;
      ssTot += (yTrue[i] - mean) * (yTrue[i] - mean);
      sumAbs += Math.abs(r);
      sumSq += r * r;
    }
    return {
      r2: ssTot > 0 ? 1 - ssRes / ssTot : 0,
      mae: sumAbs / n,
      rmse: Math.sqrt(sumSq / n),
      mse: sumSq / n,
    };
  }, [filteredData]);

  const worstCases = useMemo(
    () =>
      [...filteredData]
        .sort((a, b) => (b.absError ?? 0) - (a.absError ?? 0))
        .slice(0, showWorstN),
    [filteredData, showWorstN],
  );

  const toggleExercise = (level: ExerciseLevel) =>
    setFilters((p) => {
      const next = p.exerciseLevels.includes(level)
        ? p.exerciseLevels.filter((l) => l !== level)
        : [...p.exerciseLevels, level];
      return { ...p, exerciseLevels: next.length > 0 ? next : [level] };
    });

  const exportCsv = () => {
    const headers = [
      "altitude",
      "time_at_altitude",
      "prebreathing_time",
      "exercise_level",
      "risk_of_dcs",
      "predicted_risk",
      "residual",
      "abs_error",
    ];
    const rows = filteredData.map((d) =>
      [
        d.altitude,
        d.timeAtAltitude,
        d.prebreathingTime,
        d.exerciseLevel,
        d.riskOfDcs,
        d.predictedRisk ?? "",
        d.residual ?? "",
        d.absError ?? "",
      ].join(","),
    );
    const csv = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const ts = new Date().toISOString().replace(/[:.]/g, "-").replace(/Z$/, "");
    a.href = url;
    a.download = `adrac_validation_${ts}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Hero */}
      <section className="surface-elevated p-6 lg:p-8 relative overflow-hidden">
        <div className="absolute inset-0 grid-overlay opacity-[0.18] pointer-events-none" />
        <div className="absolute -top-32 -right-32 w-96 h-96 rounded-full bg-chart-3/15 blur-3xl pointer-events-none" />
        <div className="relative grid lg:grid-cols-[1fr_auto] gap-6 items-end">
          <div>
            <span className="pill-signal mb-3">
              <Database className="h-3 w-3" /> ADRAC validation
            </span>
            <h2 className="display text-3xl font-bold tracking-tight mt-2">
              Closed-form fit vs ADRAC reference grid.
            </h2>
            <p className="text-muted-foreground mt-2 max-w-3xl text-[14px] leading-relaxed">
              Stratified sample of {validationMetrics.nSample.toLocaleString()} rows
              from the cleaned ADRAC grid (n = {validationMetrics.nTrain.toLocaleString()}).
              The Pilmanis 2004 functional form was refit in <code className="text-num text-[12px]">mechanistic/adrac.py</code> and
              applied to the full grid; this tab shows residuals against that fit.
            </p>
          </div>
          <div className="flex flex-wrap gap-2 justify-end">
            <span className="pill-primary">
              <TrendingUp className="h-3 w-3" /> R² {validationMetrics.r2.toFixed(3)}
            </span>
            <span className="pill-accent">MAE {validationMetrics.mae.toFixed(2)} pp</span>
            <span className="pill-muted">RMSE {validationMetrics.rmse.toFixed(2)} pp</span>
          </div>
        </div>
      </section>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          label="R² · sample"
          value={metrics.r2.toFixed(4)}
          description="Filtered subset"
          icon={<TrendingUp className="h-4 w-4 text-emerald-500" />}
        />
        <MetricCard
          label="MAE"
          value={metrics.mae.toFixed(2)}
          unit="pp"
          description="Mean absolute error"
          icon={<BarChart3 className="h-4 w-4 text-primary" />}
        />
        <MetricCard
          label="RMSE"
          value={metrics.rmse.toFixed(2)}
          unit="pp"
          description="Root mean squared error"
          icon={<BarChart3 className="h-4 w-4 text-accent" />}
        />
        <MetricCard
          label="Samples"
          value={filteredData.length.toLocaleString()}
          description={`of ${validationData.length.toLocaleString()} (sample) · ${validationMetrics.nTrain.toLocaleString()} (full grid)`}
          icon={<Filter className="h-4 w-4 text-muted-foreground" />}
        />
      </div>

      {/* Filters */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between gap-3">
            <CardTitle className="flex items-center gap-2 text-[15px]">
              <Filter className="h-4 w-4 text-primary" /> Filters
            </CardTitle>
            <Button variant="outline" size="sm" onClick={exportCsv}>
              <Download className="h-4 w-4 mr-2" /> Export CSV
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="space-y-3">
              <label className="text-[13px] font-medium">Exercise level</label>
              <div className="flex flex-wrap gap-2">
                {(["Rest", "Mild", "Heavy"] as ExerciseLevel[]).map((level) => {
                  const active = filters.exerciseLevels.includes(level);
                  return (
                    <button
                      key={level}
                      onClick={() => toggleExercise(level)}
                      className={`px-3 py-1.5 rounded-full text-[12.5px] font-medium border transition-colors ${
                        active
                          ? "bg-primary text-primary-foreground border-primary"
                          : "bg-muted/40 text-muted-foreground border-border/60 hover:text-foreground"
                      }`}
                    >
                      {level}
                    </button>
                  );
                })}
              </div>
            </div>
            <Slider
              label="Altitude range"
              value={filters.altitudeRange}
              onValueChange={(v) =>
                setFilters((p) => ({
                  ...p,
                  altitudeRange: [v[0], v[1]] as [number, number],
                }))
              }
              min={0}
              max={63000}
              step={1000}
              unit="ft"
              formatValue={(v) => v.toLocaleString()}
            />
            <Slider
              label="Time at altitude"
              value={filters.timeRange}
              onValueChange={(v) =>
                setFilters((p) => ({
                  ...p,
                  timeRange: [v[0], v[1]] as [number, number],
                }))
              }
              min={0}
              max={600}
              step={10}
              unit="min"
              formatValue={(v) => v.toString()}
            />
          </div>
        </CardContent>
      </Card>

      {/* Charts */}
      <Card>
        <CardContent className="pt-6">
          <Tabs defaultValue="scatter">
            <TabsList className="mb-4">
              <TabsTrigger value="scatter">Predicted vs reference</TabsTrigger>
              <TabsTrigger value="residuals">Residuals</TabsTrigger>
              <TabsTrigger value="heatmap">Error heatmap</TabsTrigger>
              <TabsTrigger value="worst">Worst cases</TabsTrigger>
            </TabsList>

            <TabsContent value="scatter">
              <ScatterPlot
                data={filteredData}
                xKey="riskOfDcs"
                yKey="predictedRisk"
                colorKey="exerciseLevel"
                title="ADRAC closed-form prediction vs reference"
                xLabel="ADRAC reference risk (%)"
                yLabel="Closed-form prediction (%)"
                height={520}
                showDiagonal
              />
            </TabsContent>

            <TabsContent value="residuals" className="space-y-6">
              <Histogram
                data={filteredData}
                dataKey="residual"
                groupKey="exerciseLevel"
                title="Residual distribution (predicted − reference)"
                xLabel="Residual (percentage points)"
                height={380}
                bins={50}
              />
              <ScatterPlot
                data={filteredData}
                xKey="timeAtAltitude"
                yKey="residual"
                colorKey="exerciseLevel"
                title="Residuals vs time-at-altitude"
                xLabel="Time at altitude (min)"
                yLabel="Residual (pp)"
                height={420}
              />
            </TabsContent>

            <TabsContent value="heatmap">
              <Heatmap
                data={filteredData}
                xKey="timeAtAltitude"
                yKey="altitude"
                valueKey="absError"
                title="Mean |error| by parameter region"
                xLabel="Time at altitude (min)"
                yLabel="Altitude (ft)"
                valueLabel="Mean |Error| (pp)"
                height={520}
                bins={12}
              />
            </TabsContent>

            <TabsContent value="worst">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium flex items-center gap-2 text-[14px]">
                    <AlertCircle className="h-4 w-4 text-amber-500" />
                    Highest absolute error
                  </h4>
                  <div className="flex items-center gap-2 text-[12.5px] text-muted-foreground">
                    Show top
                    <select
                      value={showWorstN}
                      onChange={(e) => setShowWorstN(parseInt(e.target.value))}
                      className="px-2 py-1 rounded border border-input text-[12.5px] bg-background"
                    >
                      <option value={10}>10</option>
                      <option value={25}>25</option>
                      <option value={50}>50</option>
                    </select>
                  </div>
                </div>
                <div className="overflow-x-auto rounded-xl border border-border/60">
                  <table className="w-full text-[12.5px]">
                    <thead className="bg-muted/40 text-muted-foreground">
                      <tr>
                        <th className="text-left py-2.5 px-4 font-medium">Altitude (ft)</th>
                        <th className="text-left py-2.5 px-4 font-medium">Time (min)</th>
                        <th className="text-left py-2.5 px-4 font-medium">PB (min)</th>
                        <th className="text-left py-2.5 px-4 font-medium">Exercise</th>
                        <th className="text-right py-2.5 px-4 font-medium">Reference (%)</th>
                        <th className="text-right py-2.5 px-4 font-medium">Predicted (%)</th>
                        <th className="text-right py-2.5 px-4 font-medium">|Error| (pp)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {worstCases.map((row, idx) => (
                        <tr
                          key={idx}
                          className="border-t border-border/60 hover:bg-muted/30 transition-colors"
                        >
                          <td className="py-2 px-4 text-num">{row.altitude.toLocaleString()}</td>
                          <td className="py-2 px-4 text-num">{row.timeAtAltitude.toFixed(0)}</td>
                          <td className="py-2 px-4 text-num">{row.prebreathingTime.toFixed(0)}</td>
                          <td className="py-2 px-4">
                            <span
                              className={
                                row.exerciseLevel === "Rest"
                                  ? "pill-primary"
                                  : row.exerciseLevel === "Mild"
                                    ? "pill-signal"
                                    : "pill-high"
                              }
                            >
                              {row.exerciseLevel}
                            </span>
                          </td>
                          <td className="py-2 px-4 text-right text-num">
                            {row.riskOfDcs.toFixed(2)}
                          </td>
                          <td className="py-2 px-4 text-right text-num">
                            {row.predictedRisk?.toFixed(2) ?? "—"}
                          </td>
                          <td className="py-2 px-4 text-right text-num text-red-600 dark:text-red-400">
                            {row.absError?.toFixed(2) ?? "—"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
