import React, { useState, useCallback, useMemo } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/Card";
import { Input } from "../ui/Input";
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
import { RiskGauge } from "../charts/RiskGauge";
import { predictNASA } from "../../utils/models";
import { defaultNASAInputs, modelValidityCards } from "../../data/mockData";
import { ValidityPanel } from "./ValidityPanel";
import {
  Calculator,
  User,
  Activity,
  BookOpen,
  Settings,
} from "lucide-react";
import type { NASAInputs, NASAPrediction, NASAVariant } from "../../types";

export function NASALogistic(): React.ReactElement {
  const [inputs, setInputs] = useState<NASAInputs>(defaultNASAInputs);
  const [prediction, setPrediction] = useState<NASAPrediction | null>(null);

  const handleInputChange = useCallback(
    (
      field: keyof NASAInputs,
      value: number | string | "Male" | "Female" | "NM" | "RM"
    ) => {
      setInputs((prev) => ({
        ...prev,
        [field]: value,
      }));
    },
    []
  );

  // Auto-calculate on input change
  useMemo(() => {
    try {
      const result = predictNASA(inputs);
      setPrediction(result);
    } catch {
      setPrediction(null);
    }
  }, [inputs]);

  const showAge = inputs.variant === "RM";
  const showSex = inputs.variant === "NM";

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">
          NASA ETR Logistic Calculator
        </h2>
        <p className="text-muted-foreground">
          Implements published equations from NASA/TM-2004-213093. NM (Eq. 14) uses
          ETR + sex; RM (Eq. 15) uses ETR + age.
        </p>
      </div>

      {/* Main content grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Input Panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5 text-primary" />
              Model Parameters
            </CardTitle>
            <CardDescription>
              Configure prebreathe and exposure parameters
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Model Variant Selection */}
            <div className="space-y-2">
              <label className="block text-sm font-medium">Model Variant</label>
              <Select
                value={inputs.variant}
                onValueChange={(value) =>
                  handleInputChange("variant", value as NASAVariant)
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="NM">NM (ETR + Sex) - Eq. 14</SelectItem>
                  <SelectItem value="RM">RM (ETR + Age) - Eq. 15</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-gray-500">
                {inputs.variant === "NM"
                  ? "NASA Model with sex covariate"
                  : "Research Model with age covariate"}
              </p>
            </div>

            {/* Conditional inputs */}
            {showSex && (
              <div className="space-y-2">
                <label className="block text-sm font-medium">Sex</label>
                <Select
                  value={inputs.sex}
                  onValueChange={(value) =>
                    handleInputChange("sex", value as "Male" | "Female")
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Male">Male (SEX = 1)</SelectItem>
                    <SelectItem value="Female">Female (SEX = 0)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}

            {showAge && (
              <Input
                label="Age"
                type="number"
                value={inputs.ageYears}
                onChange={(e) =>
                  handleInputChange("ageYears", parseFloat(e.target.value) || 0)
                }
                unit="years"
                min={1}
                max={100}
                step={1}
              />
            )}

            <div className="border-t pt-4 mt-4">
              <h4 className="text-sm font-medium mb-3">
                Prebreathe Parameters (Single Interval)
              </h4>

              <div className="space-y-3">
                <Input
                  label="Initial Tissue ppN₂ (P0)"
                  type="number"
                  value={inputs.p0Psia}
                  onChange={(e) =>
                    handleInputChange("p0Psia", parseFloat(e.target.value) || 0)
                  }
                  unit="psia"
                  min={0}
                  max={20}
                  step={0.1}
                  description="Report example: 8.0 psia"
                />

                <Input
                  label="Ambient ppN₂ During PB (Pa)"
                  type="number"
                  value={inputs.paPsia}
                  onChange={(e) =>
                    handleInputChange("paPsia", parseFloat(e.target.value) || 0)
                  }
                  unit="psia"
                  min={0}
                  max={20}
                  step={0.1}
                  description="100% O₂ PB → Pa ≈ 0 psia"
                />

                <Input
                  label="PB Duration"
                  type="number"
                  value={inputs.pbTimeMin}
                  onChange={(e) =>
                    handleInputChange("pbTimeMin", parseFloat(e.target.value) || 0)
                  }
                  unit="min"
                  min={0}
                  max={240}
                  step={5}
                />

                <Input
                  label="VO₂ During PB"
                  type="number"
                  value={inputs.vo2MlKgMin}
                  onChange={(e) =>
                    handleInputChange("vo2MlKgMin", parseFloat(e.target.value) || 0)
                  }
                  unit="mL/kg/min"
                  min={0}
                  max={120}
                  step={0.5}
                  description="Reflects exercise intensity"
                />
              </div>
            </div>

            <div className="border-t pt-4 mt-4">
              <h4 className="text-sm font-medium mb-3">Exposure Parameters</h4>

              <Input
                label="Ambient Pressure (P2)"
                type="number"
                value={inputs.p2Psia}
                onChange={(e) =>
                  handleInputChange("p2Psia", parseFloat(e.target.value) || 0)
                }
                unit="psia"
                min={1}
                max={14.7}
                step={0.1}
                description="Post-depressurization pressure"
              />
            </div>

            {/* Advanced Parameters */}
            <Accordion type="single" collapsible>
              <AccordionItem value="advanced">
                <AccordionTrigger className="text-sm">
                  <div className="flex items-center gap-2">
                    <Settings className="h-4 w-4" />
                    Model Parameters
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pt-2">
                  <Input
                    label="λ₂ (Lambda)"
                    type="number"
                    value={inputs.lambda2}
                    onChange={(e) =>
                      handleInputChange("lambda2", parseFloat(e.target.value) || 0)
                    }
                    min={0.0001}
                    max={0.2}
                    step={0.0005}
                    description={`Report examples: NM λ₂=0.030, RM λ₂=0.025`}
                  />
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>

        {/* Results Panel */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Calculation Results
            </CardTitle>
            <CardDescription>
              Real-time computation using {inputs.variant === "NM" ? "Eq. 14" : "Eq. 15"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {prediction ? (
              <div className="grid md:grid-cols-2 gap-6">
                {/* Gauge */}
                <div className="flex flex-col items-center justify-center">
                  <RiskGauge
                    value={prediction.pDcsPercent}
                    title="P(DCS)"
                    height={280}
                  />
                </div>

                {/* Metrics */}
                <div className="space-y-4">
                  <MetricCard
                    label="P1N2 After Prebreathe"
                    value={prediction.p1n2Psia.toFixed(3)}
                    unit="psia"
                    description="Tissue N₂ tension after PB interval"
                  />

                  <MetricCard
                    label="Exercise Tissue Ratio (ETR)"
                    value={prediction.etr.toFixed(3)}
                    description="ETR = P1N2 / P2"
                  />

                  <MetricCard
                    label="Predicted P(DCS)"
                    value={prediction.pDcsPercent.toFixed(2)}
                    unit="%"
                    isRisk
                    riskValue={prediction.pDcsPercent}
                    icon={<User className="h-5 w-5" />}
                  />

                  {/* Equation Display */}
                  <Card variant="glass" className="p-4">
                    <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                      <BookOpen className="h-4 w-4" />
                      Equation Used
                    </h4>
                    <pre className="text-xs font-mono bg-gray-50 dark:bg-gray-800 p-3 rounded-lg whitespace-pre-wrap">
                      {prediction.equation}
                    </pre>
                    <p className="text-xs text-gray-500 mt-2">
                      Source: NASA/TM-2004-213093 (conkin-dcs-exercise_2004.md)
                    </p>
                  </Card>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                <Calculator className="h-16 w-16 mb-4 opacity-50" />
                <p className="text-lg">Adjust parameters to calculate</p>
                <p className="text-sm">Results update automatically</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Full Equation Reference */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-primary" />
            Published Equations Reference
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            {/* NM Equation */}
            <div className="space-y-3">
              <h4 className="font-medium">NM Model (Eq. 14)</h4>
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <pre className="text-sm font-mono overflow-x-auto">
{`P(DCS) = exp(z) / (1 + exp(z))

where:
  z = -25.56 + 12.83×ETR - 1.037×SEX
  
  SEX = 1 (male), 0 (female)
  
Dataset: n = 159 exposures`}
                </pre>
              </div>
            </div>

            {/* RM Equation */}
            <div className="space-y-3">
              <h4 className="font-medium">RM Model (Eq. 15)</h4>
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <pre className="text-sm font-mono overflow-x-auto">
{`P(DCS) = exp(z) / (1 + exp(z))

where:
  z = -31.71 + 14.55×ETR + 0.053×AGE
  
  AGE in years
  
Dataset: n = 229 exposures`}
                </pre>
              </div>
            </div>
          </div>

          <div className="mt-4 text-xs text-gray-500">
            <strong>Citation:</strong> Conkin J. (2004). "Likelihood and Severity of
            Decompression Sickness with Exercise During EVA." NASA/TM-2004-213093.
          </div>
        </CardContent>
      </Card>

      {/* Validity Panel */}
      <ValidityPanel validity={modelValidityCards.nasa_rm_nm} />
    </div>
  );
}
