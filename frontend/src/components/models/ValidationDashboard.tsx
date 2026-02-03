import React, { useState, useMemo } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/Card";
import { Button } from "../ui/Button";
import { MetricCard } from "../ui/MetricCard";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../ui/Tabs";
import { Slider } from "../ui/Slider";
import { ScatterPlot } from "../charts/ScatterPlot";
import { Histogram } from "../charts/Histogram";
import { Heatmap } from "../charts/Heatmap";
import { validationData as mockData } from "../../data/mockData";
import {
  BarChart3,
  TrendingUp,
  AlertCircle,
  Download,
  Filter,
} from "lucide-react";
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

  // Filter data
  const filteredData = useMemo(() => {
    return mockData.filter((d) => {
      const exerciseOk = filters.exerciseLevels.includes(
        d.exerciseLevel as ExerciseLevel
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

  // Calculate metrics
  const metrics = useMemo((): RegressionMetrics => {
    if (filteredData.length === 0) {
      return { r2: 0, mae: 0, rmse: 0, mse: 0 };
    }

    const n = filteredData.length;
    const yTrue = filteredData.map((d) => d.riskOfDcs);
    const yPred = filteredData.map((d) => d.predictedRisk ?? d.riskOfDcs);

    const meanTrue = yTrue.reduce((a, b) => a + b, 0) / n;

    let ssRes = 0;
    let ssTot = 0;
    let sumAbsError = 0;
    let sumSqError = 0;

    for (let i = 0; i < n; i++) {
      const residual = yPred[i] - yTrue[i];
      ssRes += residual * residual;
      ssTot += (yTrue[i] - meanTrue) * (yTrue[i] - meanTrue);
      sumAbsError += Math.abs(residual);
      sumSqError += residual * residual;
    }

    const r2 = ssTot > 0 ? 1 - ssRes / ssTot : 0;
    const mae = sumAbsError / n;
    const mse = sumSqError / n;
    const rmse = Math.sqrt(mse);

    return { r2, mae, rmse, mse };
  }, [filteredData]);

  // Get worst cases
  const worstCases = useMemo(() => {
    return [...filteredData]
      .sort((a, b) => (b.absError ?? 0) - (a.absError ?? 0))
      .slice(0, showWorstN);
  }, [filteredData, showWorstN]);

  const toggleExercise = (level: ExerciseLevel) => {
    setFilters((prev) => {
      const levels = prev.exerciseLevels.includes(level)
        ? prev.exerciseLevels.filter((l) => l !== level)
        : [...prev.exerciseLevels, level];
      return { ...prev, exerciseLevels: levels.length > 0 ? levels : [level] };
    });
  };

  const handleExportData = () => {
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
      ].join(",")
    );

    const csv = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "adrac_validation_data.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">
          ADRAC Validation Dashboard
        </h2>
        <p className="text-muted-foreground">
          ML surrogate validation against ADRAC-derived reference dataset. Interactive
          exploration of prediction accuracy across parameter space.
        </p>
      </div>

      {/* Metrics Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="R² Score"
          value={metrics.r2.toFixed(4)}
          description="Coefficient of determination"
          icon={<TrendingUp className="h-4 w-4 text-emerald-500" />}
        />
        <MetricCard
          label="MAE"
          value={metrics.mae.toFixed(3)}
          unit="pp"
          description="Mean absolute error"
          icon={<BarChart3 className="h-4 w-4 text-blue-500" />}
        />
        <MetricCard
          label="RMSE"
          value={metrics.rmse.toFixed(3)}
          unit="pp"
          description="Root mean squared error"
          icon={<BarChart3 className="h-4 w-4 text-purple-500" />}
        />
        <MetricCard
          label="Samples"
          value={filteredData.length.toLocaleString()}
          description={`of ${mockData.length.toLocaleString()} total`}
          icon={<Filter className="h-4 w-4 text-gray-500" />}
        />
      </div>

      {/* Filters */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Filter className="h-5 w-5 text-primary" />
                Filters
              </CardTitle>
              <CardDescription>
                Filter validation data by exercise level and parameter ranges
              </CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={handleExportData}>
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            {/* Exercise Filter */}
            <div className="space-y-3">
              <label className="text-sm font-medium">Exercise Level</label>
              <div className="flex flex-wrap gap-2">
                {(["Rest", "Mild", "Heavy"] as ExerciseLevel[]).map((level) => (
                  <button
                    key={level}
                    onClick={() => toggleExercise(level)}
                    className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                      filters.exerciseLevels.includes(level)
                        ? "bg-primary text-primary-foreground"
                        : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>

            {/* Altitude Filter */}
            <Slider
              label="Altitude Range"
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

            {/* Time Filter */}
            <Slider
              label="Time at Altitude"
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

      {/* Charts Tabs */}
      <Card>
        <CardContent className="pt-6">
          <Tabs defaultValue="scatter">
            <TabsList className="mb-4">
              <TabsTrigger value="scatter">Predicted vs Reference</TabsTrigger>
              <TabsTrigger value="residuals">Residuals</TabsTrigger>
              <TabsTrigger value="heatmap">Error Heatmap</TabsTrigger>
              <TabsTrigger value="worst">Worst Cases</TabsTrigger>
            </TabsList>

            <TabsContent value="scatter">
              <ScatterPlot
                data={filteredData}
                xKey="riskOfDcs"
                yKey="predictedRisk"
                colorKey="exerciseLevel"
                title="ML Prediction vs ADRAC Reference"
                xLabel="ADRAC Reference Risk (%)"
                yLabel="ML Predicted Risk (%)"
                height={550}
                showDiagonal
              />
            </TabsContent>

            <TabsContent value="residuals" className="space-y-6">
              <Histogram
                data={filteredData}
                dataKey="residual"
                groupKey="exerciseLevel"
                title="Residual Distribution (Predicted - Reference)"
                xLabel="Residual (percentage points)"
                height={400}
                bins={50}
              />

              <ScatterPlot
                data={filteredData}
                xKey="timeAtAltitude"
                yKey="residual"
                colorKey="exerciseLevel"
                title="Residuals vs Time at Altitude"
                xLabel="Time at Altitude (min)"
                yLabel="Residual (pp)"
                height={450}
              />
            </TabsContent>

            <TabsContent value="heatmap">
              <Heatmap
                data={filteredData}
                xKey="timeAtAltitude"
                yKey="altitude"
                valueKey="absError"
                title="Mean Absolute Error by Parameter Region"
                xLabel="Time at Altitude (min)"
                yLabel="Altitude (ft)"
                valueLabel="Mean |Error| (pp)"
                height={550}
                bins={12}
              />
            </TabsContent>

            <TabsContent value="worst">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-amber-500" />
                    Highest Error Cases
                  </h4>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500">Show top</span>
                    <select
                      value={showWorstN}
                      onChange={(e) => setShowWorstN(parseInt(e.target.value))}
                      className="px-2 py-1 rounded border text-sm"
                    >
                      <option value={10}>10</option>
                      <option value={25}>25</option>
                      <option value={50}>50</option>
                    </select>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-gray-50 dark:bg-gray-800">
                        <th className="text-left py-3 px-4">Altitude (ft)</th>
                        <th className="text-left py-3 px-4">Time (min)</th>
                        <th className="text-left py-3 px-4">PB Time (min)</th>
                        <th className="text-left py-3 px-4">Exercise</th>
                        <th className="text-right py-3 px-4">Reference (%)</th>
                        <th className="text-right py-3 px-4">Predicted (%)</th>
                        <th className="text-right py-3 px-4">|Error| (pp)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {worstCases.map((row, idx) => (
                        <tr
                          key={idx}
                          className="border-b hover:bg-gray-50 dark:hover:bg-gray-800/50"
                        >
                          <td className="py-2 px-4 font-mono">
                            {row.altitude.toLocaleString()}
                          </td>
                          <td className="py-2 px-4 font-mono">
                            {row.timeAtAltitude.toFixed(1)}
                          </td>
                          <td className="py-2 px-4 font-mono">
                            {row.prebreathingTime.toFixed(1)}
                          </td>
                          <td className="py-2 px-4">
                            <span
                              className={`px-2 py-0.5 rounded text-xs ${
                                row.exerciseLevel === "Rest"
                                  ? "bg-blue-100 text-blue-700"
                                  : row.exerciseLevel === "Mild"
                                    ? "bg-amber-100 text-amber-700"
                                    : "bg-red-100 text-red-700"
                              }`}
                            >
                              {row.exerciseLevel}
                            </span>
                          </td>
                          <td className="py-2 px-4 text-right font-mono">
                            {row.riskOfDcs.toFixed(2)}
                          </td>
                          <td className="py-2 px-4 text-right font-mono">
                            {row.predictedRisk?.toFixed(2) ?? "—"}
                          </td>
                          <td className="py-2 px-4 text-right font-mono text-red-600">
                            {row.absError?.toFixed(3) ?? "—"}
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
