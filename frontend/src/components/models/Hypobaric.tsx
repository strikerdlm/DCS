import { useEffect, useRef, useState } from "react";
import { buildProfile, exampleForm, PHASE_LABELS } from "../../utils/aviationProfile";
import type { ActivityChoice, Form, Phase, PhaseInput, PressureUnit, Question } from "../../utils/aviationProfile";
import { EVA_API_BASE_URL } from "../../utils/evaApi";

const api = import.meta.env.VITE_TINYDCS_V3_API_URL ?? EVA_API_BASE_URL.replace(/\/v2\/?$/, "/v3");
const control = "mt-1 block w-full rounded-md border bg-background px-3 py-2 text-sm";
const button = "rounded-md border px-3 py-2 text-sm font-medium hover:bg-muted";
const phases = Object.keys(PHASE_LABELS) as Phase[];

type Result = {
  input_fingerprint: string; profile_id: string; probability_fraction: number | null;
  quantitative_output_enabled: boolean; evidence_class: string; model_id: string | null;
  model_version: string | null; core_version: string; endpoint: string; horizon_minutes: number;
  source: string; outcome_ascertainment: string; reference_population: string;
  outcome_window: string; applicability: { status: string; reasons: string[] };
  uncertainty: { status: string }; assumptions: string[]; included_factors: string[]; unused_factors: string[];
  physiology: { status: string; arrival_nitrogen_pa: number | null; plateau_exit_nitrogen_pa: number | null;
    maximum_tissue_ratio: number | null; supersaturation_dose_pa_s: number | null };
};

function human(value: string) { return value.toLowerCase().replaceAll("_", " "); }
function numeric(value: number | null, divisor = 1) {
  return value == null ? "Unavailable" : (value / divisor).toLocaleString(undefined, { maximumFractionDigits: 3 });
}

function Choice({ label, value, values, change }: {
  label: string; value: string; values: readonly (readonly [string, string])[]; change: (value: string) => void;
}) {
  return <label className="block text-sm">{label}<select className={control} value={value} onChange={e => change(e.target.value)}>
    {values.map(([id, text]) => <option key={id} value={id}>{text}</option>)}
  </select></label>;
}

function NumberField({ label, value, change }: { label: string; value: string; change: (value: string) => void }) {
  return <label className="block text-sm">{label}<input className={control} type="number" min="0" step="any" value={value} onChange={e => change(e.target.value)} /></label>;
}

function ProfileForm({ form, setForm }: { form: Form; setForm: (form: Form) => void }) {
  function set<K extends keyof Form>(key: K, value: Form[K]) { setForm({ ...form, [key]: value }); }
  function editPhase<K extends keyof PhaseInput>(name: Phase, key: K, value: PhaseInput[K]) {
    set("phases", { ...form.phases, [name]: { ...form.phases[name], [key]: value } });
  }
  const units = [["ft", "Pressure altitude (ft)"], ["m", "Pressure altitude (m)"], ["psia", "Absolute pressure (psia)"], ["kPa", "Absolute pressure (kPa)"]] as const;
  const yesNo = [["no", "No"], ["yes", "Yes"], ["unknown", "Unknown"]] as const;
  return <>
    <fieldset className="surface-elevated space-y-4 p-5">
      <legend className="px-1 text-lg font-semibold">Starting state and exposure pressure</legend>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <NumberField label="Starting value" value={form.site} change={v => set("site", v)} />
        <Choice label="Starting pressure basis" value={form.siteUnit} values={units} change={v => set("siteUnit", v as PressureUnit)} />
        <NumberField label="At-altitude value" value={form.target} change={v => set("target", v)} />
        <Choice label="At-altitude pressure basis" value={form.targetUnit} values={units} change={v => set("targetUnit", v as PressureUnit)} />
        <Choice label="Initial tissue nitrogen" value={form.initialMethod} values={[["assumed_equilibrium", "Assume equilibrium at starting pressure"], ["unknown", "Unknown"]]} change={v => set("initialMethod", v as Form["initialMethod"])} />
        <NumberField label="Starting gas O₂ (%)" value={form.initialOxygen} change={v => set("initialOxygen", v)} />
        <Choice label="Recent diving / hyperbaric exposure" value={form.recentDiving} values={yesNo} change={v => set("recentDiving", v as Form["recentDiving"])} />
        <Choice label="Previous altitude exposure" value={form.priorAltitude} values={yesNo} change={v => set("priorAltitude", v as Form["priorAltitude"])} />
      </div>
    </fieldset>
    <section className="surface-elevated space-y-3 p-5">
      <h3 className="text-lg font-semibold">Planned phases</h3>
      <p className="text-sm text-muted-foreground">Enter body-experienced pressure and dry breathing gas. This form assigns the balance of oxygen to nitrogen, including argon. Leave oxygen or VO₂ blank when unknown. Preoxygenation time includes any interruption.</p>
      <div className="overflow-x-auto"><table className="w-full min-w-[660px] text-left text-sm">
        <thead><tr className="border-b"><th>Phase</th><th>Minutes</th><th>O₂ (%)</th><th>Delivery</th><th>Activity</th><th>VO₂ (mL/kg/min)</th></tr></thead>
        <tbody>{phases.map(key => {
          const row = form.phases[key];
          return <tr key={key} className="border-b"><th scope="row" className="py-2 pr-3 font-medium">{PHASE_LABELS[key]}</th>
            {(["minutes", "oxygen"] as const).map(k => <td key={k} className="pr-2"><input className={control + " w-20"} aria-label={PHASE_LABELS[key] + " " + k} type="number" step="any" min="0" value={row[k]} onChange={e => editPhase(key, k, e.target.value)} /></td>)}
            <td className="pr-2"><select className={control} aria-label={PHASE_LABELS[key] + " delivery"} value={row.delivery} onChange={e => editPhase(key, "delivery", e.target.value)}>
              {["ambient", "mask", "suit", "unknown"].map(x => <option key={x}>{x}</option>)}</select></td>
            <td className="pr-2"><select className={control} aria-label={PHASE_LABELS[key] + " activity"} value={row.activity} onChange={e => editPhase(key, "activity", e.target.value as ActivityChoice)}>
              {["rest", "exercise", "walking", "unknown"].map(x => <option key={x}>{x}</option>)}</select></td>
            <td><input className={control + " w-24"} aria-label={PHASE_LABELS[key] + " estimated VO2"} type="number" min="0" step="any" value={row.vo2} onChange={e => editPhase(key, "vo2", e.target.value)} /></td>
          </tr>;
        })}</tbody></table></div>
      {Number(form.phases.oxygen_break.minutes) > 0 && <NumberField label="Interruption start (minutes after preoxygenation begins)" value={form.breakStart} change={v => set("breakStart", v)} />}
    </section>
    <section className="surface-elevated grid gap-4 p-5 sm:grid-cols-2">
      <Choice label="Outcome and reference population" value={form.question} change={v => set("question", v as Question)} values={[
        ["complete", "Aviation DCS through return"], ["followup", "Aviation DCS through post-return follow-up"],
        ["male_reference", "NASA Table 5, male reference group above 5 psia"],
        ["nasa_reference", "NASA Table 5, chamber reference group at or below 5 psia"], ["physiology", "Physiological calculation"],
      ]} />
      {form.question === "nasa_reference" && <NumberField label="BMI for Eq. 4 (kg/m²)" value={form.bmi} change={v => set("bmi", v)} />}
    </section>
  </>;
}

function ResultPanel({ result, body }: { result: Result; body: string }) {
  const p = result.physiology;
  function download() {
    const report = { profile: JSON.parse(body), result };
    const url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: "application/json" }));
    const link = document.createElement("a");
    link.href = url; link.download = "aviation-profile-" + result.input_fingerprint.slice(0, 12) + ".json";
    link.click(); window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return <section className="surface-elevated space-y-4 p-5" aria-live="polite">
    <div className="flex flex-wrap items-center justify-between gap-3"><h3 className="text-lg font-semibold">Calculation result</h3>
      <button className={button} onClick={download}>Download profile and result</button></div>
    <p className="text-sm">{human(result.evidence_class)} · {result.model_id ?? "No eligible model"} · {human(result.endpoint)} · {result.horizon_minutes} min</p>
    {result.endpoint === "physiology" ? <p className="text-sm">Physiological calculation · {human(p.status)}</p>
      : <p className="display text-3xl font-semibold">{result.quantitative_output_enabled && result.probability_fraction != null
        ? numeric(result.probability_fraction * 100) + "%" : "Probability unavailable"}</p>}
    {!!result.applicability.reasons.length && <ul className="list-disc pl-5 text-sm">{result.applicability.reasons.map(x => <li key={x}>{human(x)}</li>)}</ul>}
    <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{[
      ["Arrival tissue N₂ (kPa)", numeric(p.arrival_nitrogen_pa, 1000)], ["Plateau-exit tissue N₂ (kPa)", numeric(p.plateau_exit_nitrogen_pa, 1000)],
      ["Maximum tissue ratio", numeric(p.maximum_tissue_ratio)], ["Supersaturation dose (kPa·min)", numeric(p.supersaturation_dose_pa_s, 60000)],
    ].map(([label, value]) => <div className="rounded-md bg-muted p-3" key={label}><dt className="text-xs">{label}</dt><dd className="mt-1 text-xl">{value}</dd></div>)}</dl>
    <p className="text-sm">Outcome window · {human(result.outcome_window)}. Probability interval · {human(result.uncertainty.status)}.</p>
    {result.evidence_class === "published_reference" && <p className="text-sm">
      {result.outcome_ascertainment} Reference population · {human(result.reference_population)}.{" "}
      <a href={result.source} className="underline">Source report</a>
    </p>}
    <details><summary className="cursor-pointer text-sm">Assumptions, factors and calculation record</summary>
      <p className="mt-2 text-sm">{result.assumptions.join(" · ")}</p>
      <p className="text-sm">Included factors · {result.included_factors.join(", ") || "None"}</p>
      <p className="text-sm">Unused factors · {result.unused_factors.join(", ") || "None"}</p>
      <pre className="mt-2 max-h-80 overflow-auto rounded bg-muted p-3 text-xs">{JSON.stringify(result, null, 2)}</pre></details>
    <p className="break-all font-mono text-xs text-muted-foreground">Core {result.core_version} · Input SHA-256 {result.input_fingerprint}</p>
  </section>;
}

export default function Hypobaric() {
  const [form, setForm] = useState(() => exampleForm());
  const [advanced, setAdvanced] = useState(false);
  const [editor, setEditor] = useState("");
  const [editorBase, setEditorBase] = useState("");
  const [reply, setReply] = useState<{ body: string; result?: Result; error?: string } | null>(null);
  const controller = useRef<AbortController | null>(null);
  let body = "", inputError = "";
  try { body = advanced ? JSON.stringify(JSON.parse(editor)) : JSON.stringify(buildProfile(form)); }
  catch (error) { inputError = advanced ? "Enter a valid JSON profile." : (error as Error).message; }
  useEffect(() => () => controller.current?.abort(), [body]);

  async function calculate() {
    controller.current?.abort();
    const current = new AbortController();
    controller.current = current;
    setReply({ body });
    try {
      const response = await fetch(api + "/aviation/evaluate", {
        method: "POST", body, headers: { "Content-Type": "application/json" }, signal: current.signal,
      });
      if (!response.ok) {
        if (response.status === 422) {
          const errors = (await response.json()).detail;
          throw Error(Array.isArray(errors) ? errors.map(e => e.loc.slice(1).join(".") + " " + e.msg).join(" / ") : "Check the profile inputs.");
        }
        throw Error("The DCS calculation service is unavailable.");
      }
      const result: Result = await response.json();
      if (result.profile_id !== JSON.parse(body)?.profile_id || !/^[a-f0-9]{64}$/.test(result.input_fingerprint)
          || !result.physiology || !result.applicability) throw Error("The server returned an incompatible calculation record.");
      if (!current.signal.aborted) setReply({ body, result });
    } catch (error) {
      if (!current.signal.aborted) setReply({ body, error: error instanceof TypeError ? "Connect the DCS API to calculate this profile." : (error as Error).message });
    }
  }
  const active = reply?.body === body ? reply : null;
  return <section className="space-y-5">
    <header className="surface-elevated space-y-3 p-6">
      <h2 className="display text-3xl font-semibold">Aviation pressure history</h2>
      <p className="text-sm text-muted-foreground">Follow nitrogen through preoxygenation, ascent, altitude exposure and return. The reference equations change at 5 psia. Eligibility depends on the breathing gas, population and observation window.</p>
      <div className="flex flex-wrap gap-2">
        <button className={button} onClick={() => { setForm(exampleForm()); setAdvanced(false); }}>Load ten-minute example</button>
        <button className={button} onClick={() => { setForm(exampleForm(true)); setAdvanced(false); }}>Load NASA chamber example</button>
        <button className={button} disabled={!advanced && !body} onClick={() => {
          if (!advanced && body !== editorBase) {
            setEditor(JSON.stringify(JSON.parse(body), null, 2));
            setEditorBase(body);
          }
          setAdvanced(!advanced);
        }}>{advanced ? "Return to simple form" : "Edit advanced timeline"}</button>
      </div>
    </header>
    {advanced ? <label className="surface-elevated block p-5">Versioned exposure profile (JSON)
      <textarea className={control + " font-mono text-xs"} rows={20} value={editor} spellCheck={false} onChange={e => setEditor(e.target.value)} /></label>
      : <ProfileForm form={form} setForm={setForm} />}
    {body && !advanced && <details open className="surface-elevated p-5"><summary className="cursor-pointer font-semibold">Review the generated timeline</summary>
      <ol className="mt-3 space-y-1 text-sm">{buildProfile(form).segments.map(s => <li key={s.id}>
        <span className="font-mono">{s.start}–{s.end} min</span> · {PHASE_LABELS[s.phase]} · {s.start_pressure.value} {s.start_pressure.unit} → {s.end_pressure.value} {s.end_pressure.unit} · {s.gas ? numeric(s.gas.oxygen_fraction * 100) + "% O₂" : "Gas unknown"}
      </li>)}</ol>
      <p className="mt-3 text-sm text-muted-foreground">Initial state · {human(form.initialMethod)}. Pressure changes linearly during ascent and return. Each phase has constant gas composition.</p>
    </details>}
    {inputError && <p role="alert">{inputError}</p>}
    <button className="rounded-md bg-primary px-5 py-2 font-medium text-primary-foreground disabled:opacity-50" disabled={!body}
      onClick={calculate}>Calculate profile</button>
    {active?.result ? <ResultPanel result={active.result} body={body} /> : active && <p role="status">{active.error ?? "Calculating…"}</p>}
  </section>;
}
