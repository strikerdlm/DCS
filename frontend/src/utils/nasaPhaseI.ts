import type { NASAVariant } from '../types';

/** Planned inputs from the NASA/TP-2004-213158 Phase I reference schedule.
 * The service evaluates the complete schedule and its applicability. */
export function nasaPhaseI(variant: NASAVariant) {
  const pressure = (value: number) => ({ kind: 'absolute', value, unit: 'psia' });
  const gas = (oxygen: number) => ({ basis: 'dry', oxygen_fraction: oxygen, nitrogen_fraction: 1 - oxygen });
  function stage(phase: string, start: number, end: number, from: number, to: number, oxygen = 1,
                 type = 'rest', extra: Record<string, string | number> = {}) {
    return {
      id: phase + '-' + start, phase, start, end, start_pressure: pressure(from), end_pressure: pressure(to),
      interpolation: from === to ? 'constant' : 'linear_pressure', gas: gas(oxygen),
      activity: { type, ambulation: false, posture: 'semi_recumbent', ...extra },
      provenance: 'NASA Phase I reference schedule',
    };
  }
  return {
    schema_version: '1.0.0', profile_id: 'NASA-2004-Phase-I-' + variant, purpose: 'research',
    provenance: 'NASA/TP-2004-213158 Phase I reference', time_unit: 'min',
    initial_state: {method: 'assumed_equilibrium', body_pressure: pressure(14.7), gas: gas(.21), provenance: 'Reference sea-level air'},
    history: {recent_diving: false, previous_altitude_exposure: false,
      segments: [stage('residence', -100, 0, 14.7, 14.7, .21, 'rest', {posture: 'recumbent'})]},
    segments: [
      stage('prebreathe', 0, 3, 14.7, 14.7, 1, 'warmup', {exercise_mode: 'dual_cycle', percent_vo2_peak: 37.5}),
      stage('prebreathe', 3, 10, 14.7, 14.7, 1, 'exercise', {exercise_mode: 'dual_cycle', percent_vo2_peak: 75}),
      stage('recovery', 10, 13, 14.7, 14.7, 1, 'recovery', {percent_vo2_peak: 37.5}),
      stage('recovery', 13, 30, 14.7, 14.7, 1, 'recovery', {percent_vo2_peak: 25}),
      stage('prebreathe', 30, 50, 14.7, 14.7), stage('prebreathe', 50, 70, 14.7, 9.6),
      stage('prebreathe', 70, 80, 9.6, 10.2), stage('prebreathe', 80, 110, 10.2, 10.2, .265),
      stage('prebreathe', 110, 115, 10.2, 14.7), stage('prebreathe', 115, 150, 14.7, 14.7),
      stage('ascent', 150, 180, 14.7, 4.3),
      stage('plateau', 180, 420, 4.3, 4.3, 1, 'simulated_eva', {exercise_mode: 'crank_and_yank'}),
    ],
    person_covariates: {source_sex: 'male', age_years: 43, vo2_peak_ml_kg_min: 50, vo2_peak_method: 'measured', bmi_kg_m2: 24},
    prediction_request: {
      model_id: variant === 'NM' ? 'nasa_2004_nm' : 'nasa_2004_rm', endpoint: 'symptomatic_dcs',
      prediction_origin: 'plateau_arrival', source_protocol: 'nasa_2004_phase_i', horizon_minutes: 240,
      reference_population: 'nasa_2004_adynamic_chamber', window: variant === 'NM' ? 'source_post_test' : 'during_plateau',
      ...(variant === 'NM' && {post_test_course: 'published_source_ascertainment'}),
    },
  };
}
