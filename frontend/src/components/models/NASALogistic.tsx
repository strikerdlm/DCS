import React, { useMemo, useState } from "react";
import { Activity, BookOpen, Calculator, Settings, User } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
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
import type { NASAInputs, NASAPrediction, NASAVariant } from "../../types";

export function NASALogistic(): React.ReactElement {
  const [inputs, setInputs] = useState<NASAInputs>(defaultNASAInputs);

  const { prediction, error } = useMemo<{
    prediction: NASAPrediction | null;
    error: string | null;
  }>(() => {
    try {
      return { prediction: predictNASA(inputs), error: null };
    } catch (e) {
      return {
        prediction: null,
        error: e instanceof Error ? e.message : "Computation error",
      };
    }
  }, [inputs]);

  const handle = <K extends keyof NASAInputs>(field: K, value: NASAInputs[K]) =>
    setInputs((prev) => ({ ...prev, [field]: value }));

  const showAge = inputs.variant === "RM";
  const showSex = inputs.variant === "NM";

  return (
    <div className="space-y-6">
      {/* Hero */}
      <section className="surface-elevated p-6 lg:p-8 relative overflow-hidden">
        <div className="absolute inset-0 grid-overlay opacity-[0.18] pointer-events-none" />
        <div className="absolute -top-32 -right-20 w-96 h-96 rounded-full bg-chart-2/15 blur-3xl pointer-events-none" />
        <div className="relative">
          <span className="pill-primary mb-3">
            <Calculator className="h-3 w-3" /> NASA/TM-2004-213093 · Conkin
          </span>
          <h2 className="display text-3xl font-bold tracking-tight mt-2">
            Exercise Tissue Ratio logistic — single-interval prebreathe.
          </h2>
          <p className="text-muted-foreground mt-2 max-w-3xl text-[14px] leading-relaxed">
            Verbatim port of <code className="text-num text-[12px]">mechanistic/conkin_nasa.py</code>.
            NM (Eq. 14) uses ETR + sex on n = 159; RM (Eq. 15) uses ETR + age on
            n = 229. The variable τ½ depends on VO₂ during prebreathe via λ.
          </p>
        </div>
      </section>

      <div className="grid xl:grid-cols-[360px_1fr] gap-6">
        <Card className="xl:sticky xl:top-24 xl:self-start">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-[15px]">
              <Calculator className="h-4 w-4 text-primary" /> Model parameters
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="block text-[13px] font-medium">Model variant</label>
              <Select
                value={inputs.variant}
                onValueChange={(value) => handle("variant", value as NASAVariant)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="NM">NM · Eq. 14 · ETR + sex</SelectItem>
                  <SelectItem value="RM">RM · Eq. 15 · ETR + age</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-[11.5px] text-muted-foreground">
                {inputs.variant === "NM"
                  ? "NASA Model — sex covariate; n = 159 chamber exposures."
                  : "Research Model — age covariate; n = 229 chamber exposures."}
              </p>
            </div>

            {showSex && (
              <div className="space-y-2">
                <label className="block text-[13px] font-medium">Sex</label>
                <Select
                  value={inputs.sex}
                  onValueChange={(value) => handle("sex", value as "Male" | "Female")}
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
                onChange={(e) => handle("ageYears", parseFloat(e.target.value) || 0)}
                unit="years"
                min={1}
                max={100}
                step={1}
              />
            )}

            <div className="border-t border-border/60 pt-4">
              <h4 className="text-[12px] font-semibold uppercase tracking-wider text-muted-foreground mb-3">
                Prebreathe (single interval)
              </h4>
              <div className="space-y-3">
                <Input
                  label="Initial tissue ppN₂ · P0"
                  type="number"
                  value={inputs.p0Psia}
                  onChange={(e) => handle("p0Psia", parseFloat(e.target.value) || 0)}
                  unit="psia"
                  min={0}
                  max={20}
                  step={0.1}
                  description="Report example: 8.0 psia"
                />
                <Input
                  label="Ambient ppN₂ during PB · Pa"
                  type="number"
                  value={inputs.paPsia}
                  onChange={(e) => handle("paPsia", parseFloat(e.target.value) || 0)}
                  unit="psia"
                  min={0}
                  max={20}
                  step={0.1}
                  description="100 % O₂ PB → Pa ≈ 0"
                />
                <Input
                  label="PB duration"
                  type="number"
                  value={inputs.pbTimeMin}
                  onChange={(e) => handle("pbTimeMin", parseFloat(e.target.value) || 0)}
                  unit="min"
                  min={0}
                  max={240}
                  step={5}
                />
                <Input
                  label="VO₂ during PB"
                  type="number"
                  value={inputs.vo2MlKgMin}
                  onChange={(e) =>
                    handle("vo2MlKgMin", parseFloat(e.target.value) || 0)
                  }
                  unit="mL·kg⁻¹·min⁻¹"
                  min={0}
                  max={120}
                  step={0.5}
                  description="Reflects exercise intensity"
                />
              </div>
            </div>

            <div className="border-t border-border/60 pt-4">
              <h4 className="text-[12px] font-semibold uppercase tracking-wider text-muted-foreground mb-3">
                Exposure
              </h4>
              <Input
                label="Ambient pressure · P2"
                type="number"
                value={inputs.p2Psia}
                onChange={(e) => handle("p2Psia", parseFloat(e.target.value) || 0)}
                unit="psia"
                min={1}
                max={14.7}
                step={0.1}
                description="Post-depressurization (e.g., EMU at 4.3 psia)"
              />
            </div>

            <Accordion type="single" collapsible>
              <AccordionItem value="lambda">
                <AccordionTrigger className="text-[13px]">
                  <div className="flex items-center gap-2">
                    <Settings className="h-3.5 w-3.5" /> Model coefficients
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pt-2">
                  <Input
                    label="λ₂"
                    type="number"
                    value={inputs.lambda2}
                    onChange={(e) =>
                      handle("lambda2", parseFloat(e.target.value) || 0)
                    }
                    min={0.0001}
                    max={0.2}
                    step={0.0005}
                    description="NM example λ₂ = 0.030, RM example λ₂ = 0.025"
                  />
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>

        <div className="space-y-6 min-w-0">
          {/* Top row */}
          <div className="grid xl:grid-cols-[420px_1fr] gap-6">
            <Card variant="glass">
              <CardContent className="p-6">
                {prediction ? (
                  <RiskGauge
                    value={prediction.pDcsPercent}
                    title="P(DCS)"
                    height={300}
                    max={40}
                  />
                ) : (
                  <div className="h-[300px] flex flex-col items-center justify-center text-muted-foreground">
                    <Activity className="h-10 w-10 opacity-40 mb-2" />
                    <p className="text-[14px]">{error ?? "Adjust parameters"}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <div className="grid sm:grid-cols-2 gap-3">
              <MetricCard
                label="P1N₂ after prebreathe"
                value={prediction ? prediction.p1n2Psia.toFixed(3) : "—"}
                unit="psia"
                description="Tissue N₂ tension after PB interval"
              />
              <MetricCard
                label="ETR"
                value={prediction ? prediction.etr.toFixed(3) : "—"}
                description="ETR = P1N₂ / P2"
              />
              <MetricCard
                label="Variant"
                value={inputs.variant}
                description={inputs.variant === "NM" ? "ETR + sex" : "ETR + age"}
                icon={<User className="h-4 w-4 text-accent" />}
              />
              <MetricCard
                label="Predicted P(DCS)"
                value={prediction ? prediction.pDcsPercent.toFixed(2) : "—"}
                unit="%"
                isRisk
                riskValue={prediction?.pDcsPercent ?? 0}
                icon={<Activity className="h-4 w-4" />}
              />
            </div>
          </div>

          {/* Equation */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-[15px]">
                <BookOpen className="h-4 w-4 text-primary" /> Active equation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-num text-[12.5px] bg-muted/50 dark:bg-muted/30 p-4 rounded-lg whitespace-pre-wrap leading-relaxed">
                {prediction?.equation ?? "—"}
              </pre>
              <p className="text-[11.5px] text-muted-foreground mt-2">
                Source: NASA/TM-2004-213093 · Conkin (2004) · ported in <code className="text-num text-[11px]">mechanistic/conkin_nasa.py</code>.
              </p>
            </CardContent>
          </Card>

          {/* Reference equations */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-[15px]">Reference equations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h4 className="text-[12px] font-semibold uppercase tracking-wider text-muted-foreground">
                    NM · Eq. 14
                  </h4>
                  <pre className="text-num text-[12px] bg-muted/50 dark:bg-muted/30 p-4 rounded-lg whitespace-pre-wrap leading-relaxed">
{`P(DCS) = σ(z)
z = -25.56 + 12.83 · ETR − 1.037 · SEX
SEX = 1 (male), 0 (female)
n = 159 exposures`}
                  </pre>
                </div>
                <div className="space-y-2">
                  <h4 className="text-[12px] font-semibold uppercase tracking-wider text-muted-foreground">
                    RM · Eq. 15
                  </h4>
                  <pre className="text-num text-[12px] bg-muted/50 dark:bg-muted/30 p-4 rounded-lg whitespace-pre-wrap leading-relaxed">
{`P(DCS) = σ(z)
z = -31.71 + 14.55 · ETR + 0.053 · AGE
AGE in years
n = 229 exposures`}
                  </pre>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <ValidityPanel validity={modelValidityCards.nasa_rm_nm} />
    </div>
  );
}
