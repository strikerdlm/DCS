import { useState } from "react";
import { checkEnvelope, predictADRAC } from "../../utils/models";
import type { ExerciseLevel } from "../../types";

function Example({ title, altitude, duration, pre, activity }: {
  title: string; altitude: number; duration: number; pre: number; activity: ExerciseLevel;
}) {
  const [form, setForm] = useState({ altitude: String(altitude), duration: String(duration), pre: String(pre), activity });
  const values = [form.altitude, form.pre, form.duration].map(Number);
  const valid = [form.altitude, form.pre, form.duration].every(s => s.trim() !== "") && values.every(Number.isFinite);
  const env = valid ? checkEnvelope(values[0], values[1], values[2], form.activity) : null;
  const value = env?.inEnvelope ? predictADRAC(values[0], values[1], form.activity, values[2]).riskFraction * 100 : null;
  return <section className="surface-elevated p-5 space-y-4"><h3 className="display text-xl font-semibold">{title}</h3>
    <div className="grid gap-3 sm:grid-cols-2">{([["altitude","Altitude (ft)"],["duration","Time at altitude (min)"],["pre","Prebreathing time (min)"]] as const).map(([key,label]) =>
      <label key={key} className="text-sm">{label}<input className="mt-1 block w-full rounded border bg-background p-2" type="number" min="0" value={form[key]} onChange={e=>setForm({...form,[key]:e.target.value})}/></label>)}
      <label className="text-sm">Grid activity<select className="mt-1 block w-full rounded border bg-background p-2" value={form.activity} onChange={e=>setForm({...form,activity:e.target.value as ExerciseLevel})}>
        {["Rest","Mild","Heavy"].map(a=><option key={a}>{a}</option>)}</select></label></div>
    <p aria-live="polite">{value === null ? "Equation projection unavailable for these inputs." : "ADRAC-form grid projection · " + value.toFixed(2) + "%"}</p>
  </section>;
}

export function UseCases() {
  return <div className="space-y-5"><header className="surface-elevated p-6"><h2 className="display text-3xl font-semibold">Worked mathematical examples</h2>
    <p className="mt-3 text-muted-foreground">These examples evaluate the browser’s refitted grid equation. The percentages describe its mathematical response. Cohort-specific DCS and VGE results are available in the chamber outcomes view.</p></header>
    <Example title="Altitude and time" altitude={25000} duration={60} pre={0} activity="Mild"/>
    <Example title="Prebreathing and activity" altitude={35000} duration={30} pre={30} activity="Rest"/>
  </div>;
}
