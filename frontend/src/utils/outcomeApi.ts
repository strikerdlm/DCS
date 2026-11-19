/** Transport contract for the paired research outcomes from the DCS service. */
export interface OutcomeInputs {
  protocol_id: string; altitude_ft: number | null; plateau_pressure_psia: number | null;
  time_at_altitude_min: number; prebreathing_min: number; ascent_min: number; starting_pressure_psia: number;
  activity: 'ambulatory' | 'adynamic'; age_years: number | null; bmi_kg_m2: number | null;
  source_sex: 'male' | 'female' | null; oxygen_interrupted: boolean;
}
export interface Protocol { id: string; label: string; description: string; defaults: OutcomeInputs }
export interface Outcome {
  id: string; label: string; model_id: string; probability_fraction: number | null;
  applicability: { status: 'supported' | 'unsupported'; reasons: string[] }; endpoint: string; window: string;
  population: string; source_url: string; uncertainty: { status: string; detail: string }; evidence_class: string;
  coefficient_version?: string; model_digest?: string;
  group_dose_at_published_precision?: number | null; matched_test_ids?: string[] | null;
  observed_cases?: number | null; dcs_denominator?: number | null;
}
export interface OutcomeResult {
  version: string; inputs: OutcomeInputs; input_fingerprint: string;
  physiology: { plateau_pressure_psia: number; arrival_tissue_n2_psia: number | null; arrival_tissue_ratio: number | null };
  assumptions: string[]; outcomes: Outcome[]; clinical_individual_probability_available: false;
}

const invalid = 'The outcome service returned an incompatible record.';
const object = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null && !Array.isArray(value);
const str = (x: unknown): x is string => typeof x === 'string' && x.trim().length > 0;
const finite = (x: unknown): x is number => typeof x === 'number' && Number.isFinite(x);
const strings = (x: unknown): x is string[] => Array.isArray(x) && x.every(str);
const uri = (x: unknown): x is string => str(x) && /^https?:\/\//i.test(x);

export function isOutcomeInputs(value: unknown): value is OutcomeInputs {
  if (!object(value) || !str(value.protocol_id) || !['ambulatory','adynamic'].includes(String(value.activity)) ||
      ![null,'male','female'].some(v=>v===value.source_sex) || typeof value.oxygen_interrupted !== 'boolean') return false;
  if ((value.altitude_ft === null) === (value.plateau_pressure_psia === null)) return false;
  return ['altitude_ft','plateau_pressure_psia','bmi_kg_m2','age_years'].every(k=>value[k] === null || finite(value[k])) &&
    ['time_at_altitude_min','prebreathing_min','ascent_min','starting_pressure_psia'].every(k=>finite(value[k]));
}

async function exchange(base: string, path: string, signal: AbortSignal, inputs?: OutcomeInputs): Promise<unknown> {
  const response = await fetch(base.replace(/\/$/, '') + '/hypobaric/outcomes/' + path, {
    method: inputs ? 'POST' : 'GET', signal, cache: 'no-store',
    headers: inputs ? {'Content-Type':'application/json'} : undefined, body: inputs ? JSON.stringify(inputs) : undefined,
  });
  if (!response.ok) throw Error(response.status === 422 ? 'The service rejected the exposure inputs. Check the units and required fields.' : 'The research outcome service is unavailable.');
  return response.json();
}

export async function getProtocols(base: string, signal: AbortSignal): Promise<Protocol[]> {
  const raw = await exchange(base, 'models', signal);
  if (!object(raw) || !str(raw.version) || !uri(raw.source_url) || !Array.isArray(raw.protocols) || !raw.protocols.length) throw Error(invalid);
  const protocols = raw.protocols.map((p: unknown) => {
    if (!object(p) || !str(p.id) || !str(p.label) || !str(p.description) || !isOutcomeInputs(p.defaults) || p.id !== p.defaults.protocol_id) throw Error(invalid);
    return {id:p.id, label:p.label, description:p.description, defaults:p.defaults};
  });
  if (new Set(protocols.map(p=>p.id)).size !== protocols.length) throw Error(invalid);
  return protocols;
}

function outcome(value: unknown): Outcome {
  if (!object(value) || !['id','label','model_id','endpoint','window','population','evidence_class'].every(k=>str(value[k])) ||
      !uri(value.source_url) || !object(value.uncertainty) || !str(value.uncertainty.status) || !str(value.uncertainty.detail) ||
      !object(value.applicability) || !strings(value.applicability.reasons)) throw Error(invalid);
  const p = value.probability_fraction;
  if (value.applicability.status === 'supported') {
    if (!['published_reference','protocol_group_benchmark','interval_censored_benchmark'].includes(String(value.evidence_class)) ||
        !finite(p) || p < 0 || p > 1 || value.applicability.reasons.length) throw Error(invalid);
  } else if (value.applicability.status !== 'unsupported' || p !== null || !value.applicability.reasons.length) throw Error(invalid);
  if (value.model_digest != null && (!str(value.model_digest) || !/^[a-f0-9]{64}$/.test(value.model_digest))) throw Error(invalid);
  if (value.coefficient_version != null && !str(value.coefficient_version)) throw Error(invalid);
  if (value.group_dose_at_published_precision != null && !finite(value.group_dose_at_published_precision)) throw Error(invalid);
  if (value.matched_test_ids != null && !strings(value.matched_test_ids)) throw Error(invalid);
  const cases = value.observed_cases, total = value.dcs_denominator;
  if ((cases != null || total != null) && (!finite(cases) || !Number.isInteger(cases) || cases < 0 ||
      !finite(total) || !Number.isInteger(total) || total < 1 || cases > total)) throw Error(invalid);
  return value as unknown as Outcome;
}

export async function getOutcomes(base: string, inputs: OutcomeInputs, signal: AbortSignal): Promise<OutcomeResult> {
  const raw = await exchange(base, 'predict', signal, inputs);
  if (!object(raw) || !str(raw.version) || !str(raw.input_fingerprint) || !/^[0-9a-f]{64}$/.test(raw.input_fingerprint) ||
      raw.clinical_individual_probability_available !== false || !isOutcomeInputs(raw.inputs) ||
      !object(raw.physiology) || !finite(raw.physiology.plateau_pressure_psia) ||
      ![raw.physiology.arrival_tissue_n2_psia,raw.physiology.arrival_tissue_ratio].every(x=>x === null || finite(x)) ||
      !strings(raw.assumptions) || !Array.isArray(raw.outcomes) || !raw.outcomes.length) throw Error(invalid);
  const echo=raw.inputs;
  if ((Object.keys(inputs) as (keyof OutcomeInputs)[]).some(k=>echo[k]!==inputs[k])) throw Error(invalid);
  const outcomes=raw.outcomes.map(outcome);
  if (new Set(outcomes.map(o=>o.id)).size !== outcomes.length) throw Error(invalid);
  return {...raw, outcomes} as OutcomeResult;
}
