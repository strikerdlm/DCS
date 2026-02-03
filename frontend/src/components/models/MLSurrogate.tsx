import React, { useState, useCallback } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/Card";
import { Input } from "../ui/Input";
import { Button } from "../ui/Button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/Select";
import { MetricCard } from "../ui/MetricCard";
import { RiskGauge } from "../charts/RiskGauge";
import { predictMLSurrogate } from "../../utils/models";
import { defaultMLInputs, modelValidityCards } from "../../data/mockData";
import { ValidityPanel } from "./ValidityPanel";
import { Activity, Clock, Wind, Gauge } from "lucide-react";
import type { ExerciseLevel, MLSurrogateInputs, MLSurrogatePrediction } from "../../types";

export function MLSurrogate(): React.ReactElement {
  const [inputs, setInputs] = useState<MLSurrogateInputs>(defaultMLInputs);
  const [prediction, setPrediction] = useState<MLSurrogatePrediction | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  const handleInputChange = useCallback(
    (field: keyof MLSurrogateInputs, value: number | string) => {
      setInputs((prev) => ({
        ...prev,
        [field]: value,
      }));
    },
    []
  );

  const handleCalculate = useCallback(() => {
    setIsCalculating(true);
    // Simulate async calculation
    setTimeout(() => {
      const result = predictMLSurrogate(inputs);
      setPrediction(result);
      setIsCalculating(false);
    }, 500);
  }, [inputs]);

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">ML Surrogate Prediction</h2>
        <p className="text-muted-foreground">
          Supervised ML regression surrogate trained on ADRAC-derived risk outputs.
          Enter exposure parameters to predict DCS risk.
        </p>
      </div>

      {/* Main content grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Input Panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Gauge className="h-5 w-5 text-primary" />
              Exposure Parameters
            </CardTitle>
            <CardDescription>
              Configure altitude, time, and exercise conditions
            </CardDescription>
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
              description="Target altitude for exposure (0-63,000 ft)"
            />

            <Input
              label="Time at Altitude"
              type="number"
              value={inputs.timeAtAltitude}
              onChange={(e) =>
                handleInputChange("timeAtAltitude", parseFloat(e.target.value) || 0)
              }
              unit="min"
              min={0}
              max={600}
              step={5}
              description="Duration of altitude exposure"
            />

            <Input
              label="Pre-breathe Time"
              type="number"
              value={inputs.prebreathingTime}
              onChange={(e) =>
                handleInputChange(
                  "prebreathingTime",
                  parseFloat(e.target.value) || 0
                )
              }
              unit="min"
              min={0}
              max={240}
              step={5}
              description="100% O₂ prebreathe duration"
            />

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Exercise Level
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
                  <SelectItem value="Rest">Rest</SelectItem>
                  <SelectItem value="Mild">Mild</SelectItem>
                  <SelectItem value="Heavy">Heavy</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Physical activity level during exposure
              </p>
            </div>

            <Button
              onClick={handleCalculate}
              className="w-full mt-6"
              size="lg"
              isLoading={isCalculating}
            >
              Calculate Risk
            </Button>
          </CardContent>
        </Card>

        {/* Results Panel */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Prediction Results</CardTitle>
            <CardDescription>
              ML surrogate prediction based on input parameters
            </CardDescription>
          </CardHeader>
          <CardContent>
            {prediction ? (
              <div className="grid md:grid-cols-2 gap-6">
                {/* Gauge */}
                <div className="flex flex-col items-center justify-center">
                  <RiskGauge
                    value={prediction.riskPercent}
                    title="DCS Risk"
                    height={280}
                  />
                </div>

                {/* Metrics */}
                <div className="space-y-4">
                  <MetricCard
                    label="Predicted DCS Risk"
                    value={prediction.riskPercent.toFixed(2)}
                    unit="%"
                    isRisk
                    riskValue={prediction.riskPercent}
                    icon={<Activity className="h-5 w-5" />}
                  />

                  <div className="grid grid-cols-2 gap-3">
                    <MetricCard
                      label="Altitude"
                      value={inputs.altitude.toLocaleString()}
                      unit="ft"
                      icon={<Wind className="h-4 w-4 text-blue-500" />}
                    />
                    <MetricCard
                      label="Exposure Time"
                      value={inputs.timeAtAltitude}
                      unit="min"
                      icon={<Clock className="h-4 w-4 text-amber-500" />}
                    />
                  </div>

                  {/* Feature vector display */}
                  <Card variant="glass" className="p-4">
                    <h4 className="text-sm font-medium mb-2">Feature Vector</h4>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {prediction.features.map((f) => (
                        <div
                          key={f.name}
                          className="flex justify-between bg-gray-50 dark:bg-gray-800 rounded px-2 py-1"
                        >
                          <span className="text-gray-600 dark:text-gray-400">
                            {f.name}
                          </span>
                          <span className="font-mono">{f.value.toFixed(2)}</span>
                        </div>
                      ))}
                    </div>
                  </Card>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                <Gauge className="h-16 w-16 mb-4 opacity-50" />
                <p className="text-lg">Enter parameters and calculate risk</p>
                <p className="text-sm">Results will appear here</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Validity Panel */}
      <ValidityPanel validity={modelValidityCards.ml_surrogate} />
    </div>
  );
}
