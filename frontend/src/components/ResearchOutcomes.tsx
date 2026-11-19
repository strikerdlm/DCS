import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { getOutcomes, getProtocols } from '../utils/outcomeApi';
import type { Outcome, OutcomeInputs, OutcomeResult, Protocol } from '../utils/outcomeApi';
import './researchOutcomes.css';

type Catalog = { state: 'loading' | 'error' } | { state: 'ready'; protocols: Protocol[] };
type Reply = { state: 'idle' | 'loading' } | { state: 'error'; message: string } | { state: 'ready'; result: OutcomeResult };
const human = (text: string) => text.replaceAll('_', ' ');
const pct = (p: number) => (p * 100).toLocaleString(undefined,{maximumSignificantDigits:4}) + '%';
const isBenchmark = (row: Outcome) => ['protocol_group_benchmark', 'interval_censored_benchmark'].includes(row.evidence_class);
type NumberKey = 'altitude_ft' | 'plateau_pressure_psia' | 'time_at_altitude_min' | 'prebreathing_min' | 'ascent_min' | 'starting_pressure_psia' | 'age_years' | 'bmi_kg_m2';

function Numeric({name,label,initial,optional=false}: {name:NumberKey; label:string; initial:number|null; optional?:boolean}) {
  return <label>{label}<input type="number" name={name} step="any" defaultValue={initial ?? ''} required={!optional}/></label>;
}

function OutcomeCard({row}: {row: Outcome}) {
  return <article className="outcome-card"><h3>{row.label}</h3>
    <strong className="outcome-value">{row.probability_fraction === null ? 'Unavailable' : pct(row.probability_fraction)}</strong>
    <p>{row.evidence_class === "protocol_group_benchmark" ? "Fitted protocol-group estimate" : human(row.evidence_class)} · {human(row.applicability.status)}</p>
    {row.applicability.reasons.length > 0 && <ul>{row.applicability.reasons.map(reason=><li key={reason}>{human(reason)}</li>)}</ul>}
    <dl><dt>Endpoint</dt><dd>{human(row.endpoint)}</dd><dt>Observation window</dt><dd>{human(row.window)}</dd>
      <dt>Reference cohort</dt><dd>{human(row.population)}</dd><dt>Uncertainty · {human(row.uncertainty.status)}</dt><dd>{row.uncertainty.detail}</dd>
      {row.group_dose_at_published_precision != null && <><dt>Mean TR360 at study precision</dt><dd>{row.group_dose_at_published_precision.toFixed(2)}</dd></>}
      {Boolean(row.matched_test_ids?.length) && <><dt>Matched study test IDs</dt><dd>{row.matched_test_ids?.join(", ")}</dd></>}
      {row.observed_cases != null && row.dcs_denominator != null && <><dt>Observed cases in matched tests</dt><dd>{row.observed_cases} of {row.dcs_denominator} exposures</dd></>}
      <dt>Model</dt><dd>{row.model_id}{row.coefficient_version && " · " + row.coefficient_version}</dd></dl>
    {row.model_digest && <details><summary>Model SHA-256</summary><code>{row.model_digest}</code></details>}
    <a href={row.source_url} target="_blank" rel="noreferrer">Primary source</a>
  </article>;
}

function Cards({ rows }: { rows: Outcome[] }) {
  const benchmarks = rows.filter(isBenchmark);
  return <><div className="outcome-cards">{rows.filter(row => !isBenchmark(row)).map(row => <OutcomeCard key={row.id} row={row}/>)}</div>
    {benchmarks.length > 0 && <details className="outcome-record"><summary>Compare with observed-outcome studies</summary>
      <p>These historical studies were evaluated internally. The DCS benchmark estimates a protocol group’s event frequency. The Grade IV VGE benchmark conditions on age, source sex, tissue ratio and ambulation. Cross-site validation is unavailable.</p>
      <div className="outcome-cards">{benchmarks.map(row => <OutcomeCard key={row.id} row={row}/>)}</div>
    </details>}</>;
}

function Exposure({base,protocol}: {base:string;protocol:Protocol}) {
  const def=protocol.defaults;
  const [pressure,setPressure]=useState<'altitude_ft'|'plateau_pressure_psia'>(def.altitude_ft === null ? 'plateau_pressure_psia' : 'altitude_ft');
  const [reply,setReply]=useState<Reply>({state:'idle'});
  const active=useRef<AbortController|null>(null);
  useEffect(()=>()=>active.current?.abort(), []);
  function clear() { active.current?.abort(); active.current=null; setReply({state:'idle'}); }
  async function submit(e:FormEvent<HTMLFormElement>) {
    e.preventDefault(); clear();
    const data=new FormData(e.currentTarget);
    const number=(key:NumberKey) => { const s=String(data.get(key) ?? '').trim(); return s ? Number(s) : null; };
    const inputs:OutcomeInputs = {
      protocol_id:protocol.id, altitude_ft:number('altitude_ft'), plateau_pressure_psia:number('plateau_pressure_psia'),
      time_at_altitude_min:number('time_at_altitude_min')!, prebreathing_min:number('prebreathing_min')!,
      ascent_min:number('ascent_min')!, starting_pressure_psia:number('starting_pressure_psia')!,
      activity:data.get('activity') as OutcomeInputs['activity'], age_years:number('age_years'), bmi_kg_m2:number('bmi_kg_m2'),
      source_sex:(data.get('source_sex') || null) as OutcomeInputs['source_sex'], oxygen_interrupted:data.has('oxygen_interrupted'),
    };
    const controller=new AbortController(); active.current=controller; setReply({state:'loading'});
    try { const result=await getOutcomes(base,inputs,controller.signal);
      if (!controller.signal.aborted && active.current===controller) setReply({state:'ready',result});
    } catch (error) { if (!controller.signal.aborted && active.current===controller)
      setReply({state:'error',message:error instanceof Error && !(error instanceof TypeError || error instanceof SyntaxError) ? error.message : 'The DCS service did not return a compatible result.'}); }
  }
  return <><p>{protocol.description}</p><form onSubmit={submit} onChange={clear}>
    <div className="outcome-fields">
      <label>Exposure pressure basis<select aria-label="Exposure pressure basis" value={pressure} onChange={e=>setPressure(e.target.value as typeof pressure)}>
        <option value="plateau_pressure_psia">Absolute plateau pressure</option><option value="altitude_ft">Pressure altitude</option></select></label>
      <Numeric key={pressure} name={pressure} label={pressure==='altitude_ft'?'Pressure altitude (ft)':'Plateau pressure (psia)'} initial={def[pressure]}/>
      <Numeric name="starting_pressure_psia" label="Starting pressure (psia)" initial={def.starting_pressure_psia}/>
      <Numeric name="prebreathing_min" label="Prebreathing time (min)" initial={def.prebreathing_min}/>
      <Numeric name="ascent_min" label="Ascent duration (min)" initial={def.ascent_min}/>
      <Numeric name="time_at_altitude_min" label="Time at altitude (min)" initial={def.time_at_altitude_min}/>
      <label>Activity at altitude<select aria-label="Activity at altitude" name="activity" defaultValue={def.activity}>
        <option value="ambulatory">Ambulatory</option><option value="adynamic">Adynamic</option></select></label>
      <Numeric name="age_years" label="Age (years, if known)" initial={def.age_years} optional/>
      <Numeric name="bmi_kg_m2" label="BMI (kg/m², if known)" initial={def.bmi_kg_m2} optional/>
      <label>Sex as coded by the source<select aria-label="Sex as coded by the source" name="source_sex" defaultValue={def.source_sex ?? ''}>
        <option value="">Unknown</option><option value="male">Male</option><option value="female">Female</option></select></label>
    </div><label className="outcome-check"><input name="oxygen_interrupted" type="checkbox" defaultChecked={def.oxygen_interrupted}/> Oxygen was interrupted</label>
    <button className="outcome-button" disabled={reply.state==='loading'}>{reply.state==='loading'?'Evaluating…':'Evaluate research outcomes'}</button>
  </form><div aria-live="polite">
    {reply.state==='error' && <p role="alert">{reply.message}</p>}
    {reply.state==='ready' && <><Cards rows={reply.result.outcomes}/>
      <details className="outcome-record"><summary>Pressure, assumptions and input record</summary>
        <dl><dt>Plateau pressure</dt><dd>{reply.result.physiology.plateau_pressure_psia.toFixed(3)} psia</dd>
        <dt>Arrival tissue nitrogen</dt><dd>{reply.result.physiology.arrival_tissue_n2_psia?.toFixed(3) ?? 'Unavailable'}{reply.result.physiology.arrival_tissue_n2_psia !== null && ' psia'}</dd>
        <dt>Arrival tissue ratio</dt><dd>{reply.result.physiology.arrival_tissue_ratio?.toFixed(3) ?? 'Unavailable'}</dd>
        <dt>Version</dt><dd>{reply.result.version}</dd><dt>Input SHA-256</dt><dd><code>{reply.result.input_fingerprint}</code></dd></dl>
        {reply.result.assumptions.length>0 && <ul>{reply.result.assumptions.map(a=><li key={a}>{a}</li>)}</ul>}</details></>}
  </div></>;
}

export function ResearchOutcomes({base}: {base:string}) {
  const [catalog,setCatalog]=useState<Catalog>({state:'loading'});
  const [selected,setSelected]=useState('');
  const [attempt,setAttempt]=useState(0);
  useEffect(()=>{
    const controller=new AbortController();
    getProtocols(base,controller.signal).then(protocols=>{if(!controller.signal.aborted)setCatalog({state:'ready',protocols});},
      ()=>{if(!controller.signal.aborted)setCatalog({state:'error'});});
    return ()=>controller.abort();
  },[base,attempt]);
  const protocol=catalog.state==='ready' ? (catalog.protocols.find(p=>p.id===selected) ?? catalog.protocols[0]) : null;
  return <section className="paired-outcomes"><h2>Chamber research outcomes</h2>
    <p className="outcome-lede">Compare symptomatic decompression sickness (DCS) and ultrasound-detected venous gas emboli (VGE) for the same exposure. Each result applies to its stated cohort and observation window. Individual clinical probability is unavailable.</p>
    {catalog.state==='loading' && <p role="status">Loading reference protocols…</p>}
    {catalog.state==='error' && <><p role="alert">Reference protocols unavailable. Connect the DCS service to evaluate outcomes.</p>
      <button className="outcome-button" onClick={()=>{setCatalog({state:'loading'});setAttempt(n=>n+1);}}>Retry protocols</button></>}
    {catalog.state==='ready' && protocol && <div className="outcome-panel"><label>Reference protocol<select aria-label="Reference protocol" value={protocol.id} onChange={e=>setSelected(e.target.value)}>
      {catalog.protocols.map(p=><option value={p.id} key={p.id}>{p.label}</option>)}</select></label>
      <Exposure key={protocol.id} base={base} protocol={protocol}/></div>}
  </section>;
}
