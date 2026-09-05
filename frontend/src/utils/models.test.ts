import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import {
  altitudeFtToMmHg,
  altitudeFtToPAmbAtm,
  formatNumber,
  getRiskColor,
  getRiskLevel,
  pressureAtmToAltitudeFt,
  stableSigmoid,
} from "../lib/utils";
import { RiskGauge } from "../components/charts/RiskGauge";
import { Anatomy } from "../components/models/Anatomy";
import type { ExerciseLevel, MechanisticInputs, NASAInputs } from "../types";
import {
  checkEnvelope,
  decomposeADRAC,
  generateAltitudePrebreatheGrid,
  generateDoseResponse,
  generateRiskLandscape,
  illustrativeInterval,
  missionPressureProfile,
  predictADRAC,
  predictNASA,
  runMechanisticSimulation,
  summarizeValidation,
} from "./models";

const nasaInputs: NASAInputs = {
  variant: "RM", p0Psia: 8, paPsia: 0, pbTimeMin: 90,
  vo2MlKgMin: 25, lambda2: 0.025, p2Psia: 4.3,
  sex: "Male", ageYears: 35,
};

const profileInputs: MechanisticInputs = {
  altitudeFt: 30000, timeAtAltitudeMin: 60, prebreathingTimeMin: 30,
  prebreathingExerciseLevel: "Rest", altitudeExerciseLevel: "Rest",
  prebreathFio2: 1, breatheO2AtAltitude: false, ascentDurationMin: 6, dtMin: 0.5,
};

describe("NASA TP-2004-213158 reference equations", () => {
  it.each([
    ["RM", 0.025, 6.69], ["NM", 0.030, 6.62],
  ] as const)("reproduces Table 17 nitrogen transitions for %s", (variant, lambda2, expected) => {
    // Table 17 includes a 20-minute air break. Omitting the exponential rate
    // or treating that interval as oxygen fails this independent source case.
    let p0Psia = 8;
    for (const [pbTimeMin, vo2MlKgMin, paPsia] of [
      [3, 12.5, 0], [17, 25, 0], [3, 12.5, 0],
      [17, 10, 0], [20, 10, 8], [30, 4.7, 0],
    ]) {
      p0Psia = predictNASA({ ...nasaInputs, variant, lambda2, p0Psia,
        pbTimeMin, vo2MlKgMin, paPsia }).p1n2Psia;
    }
    expect(Math.abs(p0Psia - expected)).toBeLessThan(0.02);
  });

  it("uses the Eq. 6 rate at zero VO2", () => {
    const result = predictNASA({ ...nasaInputs, p0Psia: 1, pbTimeMin: 519.37, vo2MlKgMin: 0 });
    expect(result.p1n2Psia).toBeCloseTo(0.36787944117144233, 12);
  });

  it("uses the fitted rate belonging to the selected variant", () => {
    // A stale caller-supplied lambda must not change the published variant.
    const result = predictNASA({ ...nasaInputs, variant: "NM", lambda2: 0.025 });
    expect(result.p1n2Psia).toBeCloseTo(5.543318018727451, 10);
  });

  it.each([["RM", 31.9732803301], ["NM", 28.1506726725],] as const)(
    "evaluates the %s endpoint with its published covariate", (variant, expected) => {
      const result = predictNASA({ ...nasaInputs, variant, p0Psia: 8.6, pbTimeMin: 0 });
      expect(result.pDcsPercent).toBeCloseTo(expected, 2);
    },
  );

  it("keeps nitrogen and ETR available but withholds risk at other pressures", () => {
    const result = predictNASA({ ...nasaInputs, p2Psia: 6 });
    expect(Number.isFinite(result.p1n2Psia)).toBe(true);
    expect(Number.isFinite(result.etr)).toBe(true);
    expect(result.pDcsPercent).toBeNull();
  });

  it.each([
    { p0Psia: Number.NaN }, { paPsia: -1 }, { pbTimeMin: Number.NaN },
    { vo2MlKgMin: Number.POSITIVE_INFINITY }, { pbTimeMin: -1 },
  ])("rejects invalid physical inputs %j", (patch) => {
    expect(() => predictNASA({ ...nasaInputs, ...patch })).toThrow();
  });
});

describe("layered standard atmosphere", () => {
  it.each([
    [0, 101325], [11000 / 0.3048, 22632.06], [20000 / 0.3048, 5474.89],
  ])("matches the reference pressure at %s ft", (altitude, pressurePa) => {
    expect(altitudeFtToMmHg(altitude)).toBeCloseTo(pressurePa * 760 / 101325, 2);
  });
  it.each([Number.NaN, Infinity, -100, 70000])("rejects unsupported altitude %s", (altitude) => {
    expect(() => altitudeFtToPAmbAtm(altitude)).toThrow();
  });
  it.each([0, 30000, 11000 / 0.3048, 40000, 20000 / 0.3048])(
    "round trips pressure altitude through both atmosphere layers at %s ft", (altitude) => {
      expect(pressureAtmToAltitudeFt(altitudeFtToPAmbAtm(altitude))).toBeCloseTo(altitude, 6);
    },
  );
  it.each([Number.NaN, Infinity, 0, -1, 1.1, 0.01])("rejects unsupported pressure %s", (pressure) => {
    expect(() => pressureAtmToAltitudeFt(pressure)).toThrow();
  });
});

describe("ADRAC physical limits", () => {
  it("returns exactly zero at zero exposure duration", () => {
    expect(predictADRAC(30000, 60, "Rest", 0).riskFraction).toBe(0);
    expect(decomposeADRAC({ altitude: 30000, prebreathingTime: 60,
      exerciseLevel: "Rest", timeAtAltitude: 0 }).riskPercent).toBe(0);
  });
  it.each([Number.NaN, -1, Infinity])("rejects invalid duration %s", (duration) => {
    expect(() => predictADRAC(30000, 60, "Rest", duration)).toThrow();
  });
  it("rejects unknown exercise instead of interpreting it as rest", () => {
    expect(() => predictADRAC(30000, 60, "unknown" as ExerciseLevel, 60)).toThrow();
  });
  it.each([
    [Number.NaN, 60, 120], [30000, Number.NaN, 120], [30000, 60, Number.NaN],
  ])("does not certify nonfinite inputs as in-envelope", (altitude, prebreathe, time) => {
    expect(checkEnvelope(altitude, prebreathe, time, "Rest").inEnvelope).toBe(false);
  });
  it("withholds positive-duration estimates beyond the audited 60-minute prebreathe support", () => {
    expect(checkEnvelope(25000, 60, 60, "Rest").inEnvelope).toBe(true);
    expect(checkEnvelope(25000, 61, 60, "Rest").inEnvelope).toBe(false);
  });
  it("does not plot a risk landscape with unsupported fixed prebreathe", () => {
    expect(generateRiskLandscape({ prebreatheMin: 61, exerciseLevel: "Rest" })).toEqual([]);
  });
  it("does not plot dose-response estimates with unsupported fixed inputs", () => {
    const base = { altitude: 25000, prebreathingTime: 61, timeAtAltitude: 60,
      exerciseLevel: "Rest" as const };
    expect(generateDoseResponse({ base, variable: "time", exerciseLevel: "Rest" })).toEqual([]);
  });
  it("ends the supported prebreathe response at 60 minutes", () => {
    const base = { altitude: 25000, prebreathingTime: 30, timeAtAltitude: 60,
      exerciseLevel: "Rest" as const };
    const points = generateDoseResponse({ base, variable: "prebreathe", exerciseLevel: "Rest" });
    expect(points.at(-1)?.x).toBe(60);
    expect(points.every((point) => point.x >= 0 && point.x <= 60)).toBe(true);
  });
  it("omits unsupported requested grid cells instead of extrapolating probabilities", () => {
    const points = generateAltitudePrebreatheGrid({ timeAtAltitudeMin: 60,
      exerciseLevel: "Rest", altitudeRange: [25000, 30000], altitudeSteps: 2,
      prebreatheRange: [0, 120], prebreatheSteps: 3 });
    expect(points.map((point) => point.prebreatheMin)).toEqual([0, 60, 0, 60]);
    expect(generateAltitudePrebreatheGrid({ timeAtAltitudeMin: 241,
      exerciseLevel: "Rest" })).toEqual([]);
  });
  it("limits Anatomy prebreathe interaction to the supported range", () => {
    const html = renderToStaticMarkup(createElement(Anatomy));
    const prebreatheControl = html.match(/<[^>]*aria-label="100% O₂ prebreathe"[^>]*>/)?.[0];
    expect(prebreatheControl).toContain('aria-valuemax="60"');
  });
});

describe("unavailable scientific outputs", () => {
  it("does not manufacture an interval when calibration is absent", () => {
    expect(illustrativeInterval(0.05, 25000)).toBeNull();
  });
  it("does not substitute an ADRAC endpoint or fabricated history for 3RUT", () => {
    const result = runMechanisticSimulation(profileInputs);
    expect(result.finalPDcsPercent).toBeNull();
    expect(result.history).toEqual([]);
  });
  it("retains the physical initial point and final time in pressure profiles", () => {
    const result = missionPressureProfile({ altitude: 30000, timeAtAltitude: 60,
      prebreathingTime: 30, exerciseLevel: "Rest" }, { ascentDurationMin: 6, dtMin: 2 });
    expect(result[0].tMin).toBe(0);
    expect(result[0].tissueN2MmHg).toBeCloseTo(563.27, 6);
    expect(result.at(-1)?.tMin).toBe(96);
  });
});

describe("missing risks and signed formatting", () => {
  it("does not map NaN logits to a zero probability", () => {
    expect(stableSigmoid(Number.NaN)).toBeNaN();
    expect(stableSigmoid(Infinity)).toBe(1);
    expect(stableSigmoid(-Infinity)).toBe(0);
  });
  it.each([Number.NaN, Infinity, -1, 101, null])("does not label missing or invalid risk %s low", (value) => {
    expect(getRiskLevel(value as number)).toBe("unavailable");
    expect(getRiskColor(value as number)).not.toBe(getRiskColor(0));
  });
  it("renders an unavailable gauge without a low-risk label", () => {
    const html = renderToStaticMarkup(createElement(RiskGauge, { value: Number.NaN }));
    expect(html).toMatch(/unavailable/i);
    expect(html).not.toContain("Low Risk");
  });
  it("preserves negative signs below the ordinary display precision", () => {
    expect(formatNumber(-0.00001)).toBe("-1.00e-5");
  });
});

describe("paired validation statistics", () => {
  const base = { altitude: 30000, timeAtAltitude: 60, prebreathingTime: 30, exerciseLevel: "Rest" };
  it("excludes missing predictions and recomputes residuals from each observed pair", () => {
    const result = summarizeValidation([
      { ...base, riskOfDcs: 10, predictedRisk: 12, residual: 0, absError: 0 },
      { ...base, riskOfDcs: 20, predictedRisk: 16 },
      { ...base, riskOfDcs: 30 },
      { ...base, riskOfDcs: 40, predictedRisk: null },
      { ...base, riskOfDcs: Number.NaN, predictedRisk: 0 },
    ]);
    expect(result.rows).toHaveLength(2);
    expect(result.excludedCount).toBe(3);
    expect(result.metrics).toEqual({ mae: 3, mse: 10, rmse: Math.sqrt(10), r2: 0.6 });
    expect(result.rows.map((row) => row.residual)).toEqual([2, -4]);
  });
  it("leaves empty and constant-target R squared unavailable", () => {
    expect(summarizeValidation([]).metrics).toEqual({ r2: null, mae: null, rmse: null, mse: null });
    expect(summarizeValidation([{ ...base, riskOfDcs: 10, predictedRisk: 12 }]).metrics.r2).toBeNull();
    expect(summarizeValidation([
      { ...base, riskOfDcs: 10, predictedRisk: 12 },
      { ...base, riskOfDcs: 10, predictedRisk: 8 },
    ]).metrics).toEqual({ r2: null, mae: 2, rmse: 2, mse: 4 });
  });
});
