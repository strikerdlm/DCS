/** Construct an explicit planned timeline. The Python core owns all physics and inference. */
export type PressureUnit = "ft" | "m" | "psia" | "kPa";
export type Phase = "prebreathe" | "oxygen_break" | "recovery" | "ascent" | "plateau" | "return" | "post_exposure";
export type ActivityChoice = "rest" | "exercise" | "walking" | "unknown";
export type PhaseInput = { minutes: string; oxygen: string; activity: ActivityChoice; vo2: string; delivery: string };
export type Question = "complete" | "followup" | "male_reference" | "nasa_reference" | "physiology";
export type Form = {
  site: string; siteUnit: PressureUnit; target: string; targetUnit: PressureUnit;
  initialMethod: "assumed_equilibrium" | "unknown"; initialOxygen: string;
  recentDiving: "no" | "yes" | "unknown"; priorAltitude: "no" | "yes" | "unknown";
  breakStart: string; bmi: string; question: Question; phases: Record<Phase, PhaseInput>;
};

function phase(minutes: string, oxygen: string, activity: ActivityChoice = "rest"): PhaseInput {
  return { minutes, oxygen, activity, vo2: "", delivery: oxygen === "100" ? "mask" : "ambient" };
}

export function exampleForm(chamber = false): Form {
  return {
    site: chamber ? "14.7" : "0", siteUnit: chamber ? "psia" : "ft",
    target: chamber ? "6.5" : "25000", targetUnit: chamber ? "psia" : "ft",
    initialMethod: "assumed_equilibrium", initialOxygen: "21",
    recentDiving: "no", priorAltitude: "no", breakStart: "10", bmi: "24",
    question: chamber ? "male_reference" : "complete",
    phases: {
      prebreathe: phase(chamber ? "115" : "30", "100"), oxygen_break: phase("0", "21"),
      recovery: phase("0", "100"), ascent: phase(chamber ? "30" : "10", "100"),
      plateau: phase(chamber ? "240" : "10", chamber ? "100" : "21", chamber ? "walking" : "rest"),
      return: phase(chamber ? "0" : "10", "100"), post_exposure: phase("0", "21"),
    },
  };
}

function numberField(value: string, label: string) {
  const parsed = Number(value);
  if (!value.trim() || !Number.isFinite(parsed) || parsed < 0) throw Error("Enter a nonnegative value for " + label + ".");
  return parsed;
}

function pressure(value: string, unit: PressureUnit) {
  return { kind: unit === "ft" || unit === "m" ? "pressure_altitude" : "absolute", value: numberField(value, "body pressure or altitude"), unit };
}

function gas(oxygen: string, delivery: string) {
  if (!oxygen.trim()) return null;
  const percent = numberField(oxygen, "oxygen");
  if (percent > 100) throw Error("Oxygen must be between 0 and 100%.");
  return { oxygen_fraction: percent / 100, nitrogen_fraction: (100 - percent) / 100,
    basis: "dry", delivery_method: delivery };
}

function activity(row: PhaseInput) {
  if (row.activity === "unknown") return null;
  return {
    type: row.activity === "rest" ? "rest" : "exercise", ambulation: row.activity === "walking",
    ...(row.vo2.trim() ? { vo2_ml_kg_min: numberField(row.vo2, "oxygen consumption"), method: "estimated" } : {}),
  };
}

function historyFlag(flag: Form["recentDiving"]) {
  return flag === "unknown" ? null : flag === "yes";
}

type Pressure = ReturnType<typeof pressure>;
type Segment = {
  id: string; phase: Phase; start: number; end: number; start_pressure: Pressure; end_pressure: Pressure;
  interpolation: "constant" | "linear_pressure"; gas: ReturnType<typeof gas>; activity: ReturnType<typeof activity>;
  provenance: string; break_kind?: "breathing_gas";
};

export function buildProfile(form: Form) {
  const site = pressure(form.site, form.siteUnit);
  const target = pressure(form.target, form.targetUnit);
  const segments: Segment[] = [];
  const rows = form.phases;
  const duration = (key: Phase) => numberField(rows[key].minutes, key + " minutes");
  const add = (key: Phase, minutes: number, start: Pressure, end: Pressure = start, id: string = key) => {
    if (minutes === 0) return;
    const t = segments.at(-1)?.end ?? 0;
    segments.push({
      id, phase: key, start: t, end: t + minutes, start_pressure: start, end_pressure: end,
      interpolation: start === end ? "constant" : "linear_pressure", gas: gas(rows[key].oxygen, rows[key].delivery),
      activity: activity(rows[key]), provenance: "user-entered plan",
      ...(key === "oxygen_break" ? { break_kind: "breathing_gas" } : {}),
    });
  };
  const pre = duration("prebreathe");
  const interruption = duration("oxygen_break");
  if (interruption > 0) {
    const at = numberField(form.breakStart, "interruption start");
    if (at + interruption > pre) throw Error("The interruption must fit inside the entered preoxygenation period.");
    add("prebreathe", at, site);
    add("oxygen_break", interruption, site);
    add("prebreathe", pre - at - interruption, site, site, "resumed-prebreathe");
  } else add("prebreathe", pre, site);
  add("recovery", duration("recovery"), site);
  if (duration("ascent") === 0 || duration("plateau") === 0) throw Error("Enter positive ascent and plateau durations.");
  add("ascent", duration("ascent"), site, target);
  add("plateau", duration("plateau"), target);
  add("return", duration("return"), target, site);
  if (duration("post_exposure") && !duration("return")) throw Error("Enter a return segment before post-return follow-up.");
  add("post_exposure", duration("post_exposure"), site);
  const source = form.question === "male_reference" || form.question === "nasa_reference";
  const isFollowup = form.question === "followup";
  if ((isFollowup || form.question === "complete") && duration("return") === 0)
    throw Error("Enter the return duration for a complete exposure.");
  if (isFollowup && duration("post_exposure") === 0) throw Error("Enter the duration of post-return follow-up.");
  const endOfReturn = segments.find(s => s.phase === "return")?.end;
  const horizon = source ? duration("plateau") : (form.question === "complete" ? endOfReturn! : segments.at(-1)!.end);
  return {
    schema_version: "1.0.0", profile_id: "aviation-plan", purpose: "research",
    provenance: "user-entered plan", time_unit: "min",
    initial_state: { method: form.initialMethod, body_pressure: site, gas: gas(form.initialOxygen, "ambient"),
      provenance: form.initialMethod === "unknown" ? "starting nitrogen unknown" : "declared equilibrium at starting pressure" },
    history: { recent_diving: historyFlag(form.recentDiving), previous_altitude_exposure: historyFlag(form.priorAltitude) },
    person_covariates: form.question === "nasa_reference" && form.bmi.trim() ? { bmi_kg_m2: numberField(form.bmi, "BMI") } : {},
    segments,
    prediction_request: {
      model_id: form.question === "physiology" ? "physiology" : "auto",
      endpoint: source ? "symptomatic_dcs" : form.question === "physiology" ? "physiology" : "clinically_adjudicated_dcs",
      prediction_origin: source ? "plateau_arrival" : "profile_start", horizon_minutes: horizon,
      window: source ? "during_plateau" : isFollowup ? "post_return" : "complete_exposure",
      reference_population: source ? (form.question === "male_reference" ? "male_hypobaric_chamber" : "nasa_hypobaric_chamber") : "aviation",
      ...(source ? { source_protocol: "nasa_2020_table5" } : {}),
    },
  };
}

export const PHASE_LABELS: Record<Phase, string> = {
  prebreathe: "Preoxygenation", oxygen_break: "Oxygen interruption", recovery: "Recovery before ascent",
  ascent: "Ascent", plateau: "At altitude", return: "Return", post_exposure: "After return",
};
