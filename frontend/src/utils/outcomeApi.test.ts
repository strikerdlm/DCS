import { afterEach, assert, expect, test } from 'vitest';
import { getOutcomes, getProtocols } from './outcomeApi';

const signal = new AbortController().signal;
const original = globalThis.fetch;
afterEach(() => { globalThis.fetch = original; });
const input = { protocol_id:'fixture', altitude_ft:null, plateau_pressure_psia:4.3, starting_pressure_psia:14.7,
  time_at_altitude_min:240, prebreathing_min:225, ascent_min:15, activity:'ambulatory' as const,
  age_years:32, bmi_kg_m2:24, source_sex:'male' as const, oxygen_interrupted:false };
const row = { id:'symptomatic_dcs', label:'Test DCS', model_id:'fixture', probability_fraction:.2,
  endpoint:'Test DCS endpoint', window:'During the test plateau', population:'Test chamber group',
  evidence_class:'published_reference', source_url:'https://example.org/fixture', applicability:{status:'supported',reasons:[]},
  uncertainty:{status:'unavailable',detail:'No interval in fixture'} };
const held = { ...row, id:'vge', label:'Test VGE', probability_fraction:null, applicability:{status:'unsupported',reasons:['SOURCE_WINDOW']} };
const result = {version:'fixture', input_fingerprint:'c'.repeat(64), inputs:input, clinical_individual_probability_available:false,
  assumptions:['Fixture'], physiology:{plateau_pressure_psia:4.3,arrival_tissue_n2_psia:null,arrival_tissue_ratio:null}, outcomes:[row,held]};
function serve(payload: unknown) { globalThis.fetch = async () => Response.json(payload); }

test('uses each published protocol’s actual defaults, and enforces one pressure basis', async () => {
  const protocol = {id:'fixture',label:'Test protocol',description:'Example exposure',defaults:input};
  const data = {version:'test',source_url:row.source_url,protocols:[protocol]};
  serve(data);
  assert.deepEqual((await getProtocols('/api/v3',signal))[0].defaults,input);
  serve({...data,protocols:[{...protocol,defaults:{...input,altitude_ft:25000}}]});
  await expect(getProtocols('/api/v3',signal)).rejects.toThrow();
});

test('retains endpoint-specific eligibility, unavailable uncertainty and independent study evidence', async () => {
  const observed = {...row,id:'test-group',evidence_class:'protocol_group_benchmark'};
  globalThis.fetch=async (url,init) => {
    assert.equal(url,'/api/v3/hypobaric/outcomes/predict');
    assert.equal(init?.method,'POST');
    assert.deepEqual(JSON.parse(String(init?.body)),input);
    return Response.json({...result,outcomes:[row,held,observed]});
  };
  const response = await getOutcomes('/api/v3',input,signal);
  assert.equal(response.outcomes[0].probability_fraction,.2);
  assert.equal(response.outcomes[1].probability_fraction,null);
  assert.equal(response.outcomes[2].evidence_class,'protocol_group_benchmark');
  assert.equal(response.physiology.arrival_tissue_n2_psia,null);
});

test('rejects stale echoes, unverified releases, invalid identifiers and inconsistent nulls', async () => {
  for(const bad of [
    {...result,inputs:{...input,ascent_min:14}}, {...result,input_fingerprint:'missing'},
    {...result,clinical_individual_probability_available:true}, {...result,outcomes:[row,row]},
    {...result,outcomes:[{...row,evidence_class:'workbook_label'}]},
    {...result,outcomes:[{...held,probability_fraction:0}]},
    {...result,outcomes:[{...row,probability_fraction:null}]},
    {...result,outcomes:[{...row,probability_fraction:1.01}]},
    {...result,outcomes:[{...row,applicability:{status:'supported',reasons:['VETO']}}]},
    {...result,outcomes:[{...row,source_url:'about:blank'}]},
    {...result,outcomes:[{...row,observed_cases:24,dcs_denominator:23}]},
  ]) {
    serve(bad); await expect(getOutcomes('/api/v3',input,signal)).rejects.toThrow();
  }
});
