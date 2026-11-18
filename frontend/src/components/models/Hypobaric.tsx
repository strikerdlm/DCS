import { useEffect, useState } from "react";
import { EVA_API_BASE_URL } from "../../utils/evaApi";

const fields = [
  ["plateauPressurePsia", "Plateau pressure (psia)", "4.3"],
  ["arrivalTissueN2Psia", "Modeled tissue N₂ at plateau arrival (psia)", "5.289"],
  ["elapsedPlateauHours", "Time at constant pressure (hours)", "6"],
  ["depressurizationMinutes", "Time to reach the plateau (minutes)", "15"],
  ["bmiKgM2", "Body mass index (kg/m², Eq. 4)", "24"],
] as const;

type Result = { pDcsPercent: number | null; reason: string | null; model: string | null };

export default function Hypobaric() {
  const [values, setValues] = useState<Record<string, string>>(Object.fromEntries(fields.map(([key,, value]) => [key, value])));
  const [ambulatory, setAmbulatory] = useState(true);
  const [constant, setConstant] = useState(true);
  const [repress, setRepress] = useState(false);
  const [maleCohort, setMaleCohort] = useState(false);
  const [reply, setReply] = useState<{ key: string; result: Result } | null>(null);
  const valid = fields.every(([key]) => values[key].trim() !== "" && Number.isFinite(Number(values[key])));
  const body = JSON.stringify({ ...Object.fromEntries(fields.map(([key]) => [key, Number(values[key])])),
    singleConstantPlateau: constant, ambulationAtPlateau: ambulatory,
    sourceRepressurizationProtocol: repress, maleReferenceCohort: maleCohort });
  useEffect(() => {
    if (!valid) return;
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      try {
        const response = await fetch(EVA_API_BASE_URL + "/hypobaric/probability", {
          method: "POST", headers: { "Content-Type": "application/json" }, body, signal: controller.signal,
        });
        if (!response.ok) throw Error(response.status === 422 ? "Check the input units and values." : "DCS API unavailable.");
        const result: Result = await response.json();
        if (!controller.signal.aborted) setReply({ key: body, result });
      } catch (error) {
        if (!controller.signal.aborted) setReply({ key: body, result: { model: null, pDcsPercent: null,
          reason: error instanceof TypeError ? "Connect the DCS API to calculate." : String(error instanceof Error ? error.message : error) } });
      }
    }, 200);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [valid, body]);
  const current = valid && reply?.key === body ? reply.result : null;
  const status = !valid ? "Enter a number for each field." : current?.reason ?? (current ? current.model : "Calculating…");

  return <section className="space-y-5">
    <header className="surface-elevated p-6">
      <h2 className="display text-3xl font-bold">Hypobaric chamber probability</h2>
      <p className="mt-2 text-muted-foreground">Cumulative symptomatic DCS in a reference group by the selected time.
        The starting values reproduce the NASA six-hour exploration-atmosphere example.</p>
    </header>
    <div className="grid gap-5 lg:grid-cols-2">
      <div className="surface-elevated space-y-4 p-6">
        {fields.map(([key, label]) => <label key={key} className="block text-sm">{label}
          <input className="mt-1 block w-full rounded-md border bg-background p-2" type="number" step="any"
            value={values[key]} onChange={e => setValues({ ...values, [key]: e.target.value })} />
        </label>)}
        {([[constant, setConstant, "Single constant-pressure plateau"],
          [ambulatory, setAmbulatory, "Walking was part of exercise at altitude"],
          [repress, setRepress, "NASA 10.2 → 14.7 psia repressurization before a 4.3 psia exposure"],
          [maleCohort, setMaleCohort, "Use the male reference cohort for pressures above 5 psia"]] as const)
          .map(([checked, set, label]) => <label key={label} className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={checked} onChange={e => set(e.target.checked)} />{label}
          </label>)}
      </div>
      <div className="surface-elevated self-start p-6" aria-live="polite">
        <h3 className="text-sm text-muted-foreground">Modeled cumulative DCS</h3>
        <p className="display my-2 text-5xl font-bold">{current?.pDcsPercent != null ? current.pDcsPercent.toFixed(1) + "%" : "—"}</p>
        <p>{status}</p>
        <p className="mt-4 text-sm text-muted-foreground">Use an arrival nitrogen tension computed from a documented
          pressure and breathing-gas history. The model covers selected single-plateau chamber profiles.
          Individual and in-flight accuracy remain unestablished.</p>
        <a className="mt-4 inline-block underline" href="https://ntrs.nasa.gov/citations/20200004317">NASA report and applicability limits</a>
      </div>
    </div>
  </section>;
}
