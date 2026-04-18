import time
from typing import List, Dict, Any
import csv
import dataclasses
import os

# Define the output directory for CSV files
OUTPUT_DIR = r"C:/Users/User/OneDrive/FAC/Research/Altitude Chamber/DCS FAC/DCS models/DCS/3RUT_MBe1"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Attempt to import from local files; ensure these are in the same directory or PYTHONPATH
try:
    from rut_mbe1_model import RutMbe1Model, ModelParameters, ProfileSegment as ModelProfileSegment, ModelState
    from simulation_utils import generate_altitude_exposure_profile, altitude_to_pressure_atm
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure rut_mbe1_model.py and simulation_utils.py are accessible.")
    # As a fallback for the ProfileSegment, if rut_mbe1_model cannot be imported for some reason
    # we might need to redefine ProfileSegment here or ensure simulation_utils.ProfileSegment is used everywhere.
    # For now, the ProfileSegment in simulation_utils is designed to be compatible.
    from simulation_utils import ProfileSegment as UtilsProfileSegment # Use this if main model import fails for segment type hints
    # This script primarily uses ProfileSegment from simulation_utils for generation,
    # and RutMbe1Model expects a compatible structure.
    ModelProfileSegment = UtilsProfileSegment # Alias for clarity if main import fails
    # Basic placeholder for ModelState if rut_mbe1_model fails, for type hinting.
    # Actual execution will fail if RutMbe1Model is not importable.
    class ModelState: pass 


def run_single_profile(
    model_params: ModelParameters,
    profile_segments: List[ModelProfileSegment], 
    initial_conditions: dict,
    delta_t_min: float = 0.1
) -> Dict[str, Any]:
    """
    Runs a single simulation profile and returns key results including history.
    """
    model = RutMbe1Model(model_params)
    model.initialize_state(
        initial_P_amb_atm=initial_conditions['P_amb_atm'],
        initial_FIO2=initial_conditions['FIO2'],
        initial_FIN2=initial_conditions['FIN2'],
        initial_I_ex=initial_conditions['I_ex_L_min_wb']
    )

    if not model.current_state:
        print("Error: Model state not initialized after call to initialize_state.")
        return {"error": "Initialization failed", "history": [], "end_segment_states": []}

    # print(f"Initial State (t=0 min, Pamb={model.current_state.P_amb_atm:.3f} atm): ")
    # print(f"  ptN2={model.current_state.pt_N2_atm:.4f}, ptO2={model.current_state.pt_O2_atm:.4f}, Pcrush={model.current_state.P_crush_atm:.4f}")
    # print(f"  n_b={model.current_state.n_b:.3e}, r_hat={model.current_state.r_hat_dimensionless:.3e}, P_DCS={model.current_state.P_DCS:.4e}\n")

    full_history: List[ModelState] = model.run_profile(profile_segments=profile_segments, delta_t_min=delta_t_min)

    if not full_history:
        return {"error": "Simulation produced no history.", "history": [], "end_segment_states": []}

    final_state = full_history[-1]
    
    # Extract end-of-segment states
    end_segment_states: List[ModelState] = []
    current_time_marker = 0.0
    # Adjust history indexing if initialize_state adds the first state to history
    # The current rut_mbe1_model.run_profile likely starts history with current_state *after* initialize_state
    
    # Find the index in full_history that corresponds to the end of each segment
    # This logic assumes t_min in ModelState is cumulative and accurate.
    history_idx = 0
    for segment in profile_segments:
        current_time_marker += segment.duration_min
        # Find the state in history closest to or just past current_time_marker
        found_segment_end_state = None
        while history_idx < len(full_history):
            if full_history[history_idx].t_min >= current_time_marker - (delta_t_min / 2): # Allow for small float inaccuracies
                found_segment_end_state = full_history[history_idx]
                # To ensure we get the state *at* the end, if multiple steps end exactly at current_time_marker,
                # we might want the last one. The loop structure naturally handles this if we break after finding.
                # However, to be robust if a step slightly overshoots:
                if history_idx > 0 and abs(full_history[history_idx-1].t_min - current_time_marker) < abs(full_history[history_idx].t_min - current_time_marker):
                     found_segment_end_state = full_history[history_idx-1] # previous step was closer
                
                # If the exact time isn't hit, but we are within a step, we might need to check which is best.
                # For simplicity now, take the first state at or just past the marker.
                break 
            history_idx += 1
        
        if found_segment_end_state:
            end_segment_states.append(found_segment_end_state)
        elif full_history: # If segment end time is beyond last history point, take last history point
            end_segment_states.append(full_history[-1])


    results = {
        "profile_segments_count": len(profile_segments),
        "total_duration_simulated_min": final_state.t_min,
        "final_P_DCS": final_state.P_DCS,
        "final_ptN2_atm": final_state.pt_N2_atm,
        "final_ptO2_atm": final_state.pt_O2_atm,
        "final_P_amb_atm": final_state.P_amb_atm,
        "final_n_b": final_state.n_b,
        "final_r_hat": final_state.r_hat_dimensionless,
        "final_Pcrush_atm": final_state.P_crush_atm,
        "max_P_DCS_observed": max(s.P_DCS for s in full_history) if full_history else 0,
        "time_at_max_P_DCS_min": full_history[[s.P_DCS for s in full_history].index(max(s.P_DCS for s in full_history))].t_min if full_history and any(s.P_DCS > 0 for s in full_history) else 0,
        "steps_in_history": len(full_history),
        "full_history": full_history,
        "end_segment_states": end_segment_states
    }
    return results

def main():
    print("Starting DCS Model Simulations...")
    start_time = time.time()

    model_params = ModelParameters() # Load default parameters
    # You can adjust specific parameters here if needed, e.g.:
    # model_params.Lambda_scale_factor_cm_neg1 = 100.0 
    # model_params.__post_init__() # Recalculate derived params if base ones changed

    # Standard initial conditions for most profiles (sea level, air, rest)
    initial_conditions_std = {
        'P_amb_atm': 1.0,
        'FIO2': 0.21,
        'FIN2': 0.79,
        'I_ex_L_min_wb': 0.0 
    }
    
    simulation_dt_min = 0.1 # Time step for simulation

    print(f"Using simulation time step: {simulation_dt_min} min")
    print("\n--- Altitude Sweep Simulation (15,000 ft to 50,000 ft, 1000 ft increments) ---")
    print("Profile: 5 min air acclimatization at 1 ATA, ascent at 5000 ft/min on air, 60 min at altitude on air, rest throughout.")
    print("-" * 80)
    print(f"{'Target Altitude (ft)':<20} | {'Target Pressure (atm)':<22} | {'Final P(DCS)':<15} | {'Max P(DCS)':<15} | {'Steps'}")
    print("-" * 80)

    all_simulation_results: Dict[str, Dict[str, Any]] = {} # Store all detailed results

    for alt_ft in range(15000, 50000 + 1000, 1000):
        profile_name = f"profile_{alt_ft}ft_air_rest"
        profile_segments = generate_altitude_exposure_profile(
            target_altitude_ft=float(alt_ft),
            acclimatization_duration_min=5.0,
            acclimatization_i_ex_l_min_wb=0.0,
            prebreathe_duration_min=0.0,
            ascent_fio2=0.21, # Air for ascent
            ascent_fin2=0.79,
            ascent_i_ex_l_min_wb=0.0,
            altitude_exposure_duration_min=60.0,
            altitude_fio2=0.21, # Air at altitude
            altitude_fin2=0.79,
            altitude_i_ex_l_min_wb=0.0
        )
        
        # print(f"\nSimulating for {alt_ft} ft...")
        # for i, seg in enumerate(profile_segments):
        #     print(f"  Segment {i+1}: Duration={seg.duration_min:.1f}min, Pamb={seg.P_amb_atm:.3f}atm, FIO2={seg.FIO2:.2f}, I_ex={seg.I_ex_L_min_wb:.2f}")

        sim_result = run_single_profile(
            model_params=model_params,
            profile_segments=profile_segments,
            initial_conditions=initial_conditions_std,
            delta_t_min=simulation_dt_min
        )
        
        all_simulation_results[profile_name] = sim_result # Store detailed result
        target_pressure_display = altitude_to_pressure_atm(float(alt_ft))
        
        if "error" in sim_result:
            print(f"{alt_ft:<20} | {target_pressure_display:<22.3f} | Error: {sim_result['error']:<15}")
        else:
            print(f"{alt_ft:<20} | {target_pressure_display:<22.3f} | {sim_result['final_P_DCS']:<15.3e} | {sim_result['max_P_DCS_observed']:<15.3e} | {sim_result['steps_in_history']}")

    # Example of a more complex profile simulation (e.g., with O2 prebreathe)
    print("\n--- Example O2 Prebreathe Scenario (25,000 ft) ---")
    profile_name_o2pb = "profile_25000ft_o2pb_rest"
    o2_prebreathe_profile_segments = generate_altitude_exposure_profile(
        target_altitude_ft=25000.0,
        acclimatization_duration_min=5.0, # 5 min air at 1 ATA
        prebreathe_duration_min=60.0,    # 60 min O2 prebreathe at 1 ATA, rest
        prebreathe_fio2=1.0,
        prebreathe_fin2=0.0,
        prebreathe_i_ex_l_min_wb=0.0,
        ascent_fio2=1.0,                 # Continue O2 during ascent
        ascent_fin2=0.0,
        altitude_exposure_duration_min=120.0, # 120 min at 25k ft
        altitude_fio2=1.0,               # O2 at altitude
        altitude_fin2=0.0,
        altitude_i_ex_l_min_wb=0.0       # Rest at altitude
    )
    print(f"\n--- {profile_name_o2pb} ---")
    sim_result_o2pb = run_single_profile(
        model_params=model_params,
        profile_segments=o2_prebreathe_profile_segments,
        initial_conditions=initial_conditions_std,
        delta_t_min=simulation_dt_min
    )
    all_simulation_results[profile_name_o2pb] = sim_result_o2pb
    if "error" not in sim_result_o2pb:
        print(f"  End of O2 Prebreathe (25k ft): Final P(DCS) = {sim_result_o2pb['final_P_DCS']:.3e}, Max P(DCS) = {sim_result_o2pb['max_P_DCS_observed']:.3e}")
        print(f"    Final ptN2={sim_result_o2pb['final_ptN2_atm']:.4f}, ptO2={sim_result_o2pb['final_ptO2_atm']:.4f}, n_b={sim_result_o2pb['final_n_b']:.2e}, Pcrush={sim_result_o2pb['final_Pcrush_atm']:.3f}")
    else:
        print(f"  Error in O2 prebreathe simulation: {sim_result_o2pb['error']}")


    # Example of a profile with exercise during prebreathe
    print("\n--- Example Exercise + O2 Prebreathe Scenario (NASA Test Profile like SCEN2 output) ---")
    # Simulating conditions roughly like Scenario 2 from your output: 120 min O2 PB with I_ex, then ascent to 0.3 atm.
    # For I_ex_L_min_wb=0.695, it implies V_O2_wb_total = 0.695 + 0.305 = 1.0 L/min.
    # This corresponds to the "I_ex_moderate = 1.0" used in your model's own __main__ for SCEN2 if I_ex_L_min_wb is defined as (Total - Rest).
    # Let's use I_ex_L_min_wb directly.
    exercise_prebreathe_i_ex = 0.695 # This means total VO2_wb = 0.695 + 0.305 = 1.0 L/min
    target_alt_for_scen2_equiv_ft = altitude_to_ft(0.3) # Convert 0.3 atm to feet for generator

    profile_name_ex_pb = "profile_29777ft_ex_o2pb_rest_at_alt" # Approx 0.3 atm
    ex_o2_prebreathe_profile_segments = generate_altitude_exposure_profile(
        target_altitude_ft=target_alt_for_scen2_equiv_ft, # Equivalent to 0.3 atm
        acclimatization_duration_min=0, # Start direct with prebreathe for this test
        prebreathe_duration_min=120.0,   
        prebreathe_pressure_atm=1.0,
        prebreathe_fio2=1.0,
        prebreathe_fin2=0.0,
        prebreathe_i_ex_l_min_wb=exercise_prebreathe_i_ex, # Exercise during PB
        
        ascent_rate_ft_per_min=30000, # Fast ascent (e.g. 1 min to reach high alt, needs P_amb_start for duration)
                                     # The generate_altitude_exposure_profile calculates ascent duration based on ft from sea level.
                                     # For 0.3 atm (~30300 ft), this would be ~1 min.
        ascent_fio2=1.0,            
        ascent_fin2=0.0,
        ascent_i_ex_l_min_wb=0.0, # Rest during ascent

        altitude_exposure_duration_min=180.0, 
        altitude_fio2=1.0,             
        altitude_fin2=0.0,
        altitude_i_ex_l_min_wb=0.0      # Rest at altitude
    )
    print(f"\n--- {profile_name_ex_pb} ({target_alt_for_scen2_equiv_ft:.0f} ft) ---")
    sim_result_ex_pb = run_single_profile(
        model_params=model_params,
        profile_segments=ex_o2_prebreathe_profile_segments,
        initial_conditions=initial_conditions_std, # Start saturated to air at rest
        delta_t_min=simulation_dt_min
    )
    all_simulation_results[profile_name_ex_pb] = sim_result_ex_pb
    if "error" not in sim_result_ex_pb:
        print(f"  End of Exercise + O2 PB ({target_alt_for_scen2_equiv_ft:.0f} ft): Final P(DCS) = {sim_result_ex_pb['final_P_DCS']:.3e}, Max P(DCS) = {sim_result_ex_pb['max_P_DCS_observed']:.3e}")
        print(f"    Final ptN2={sim_result_ex_pb['final_ptN2_atm']:.4f}, ptO2={sim_result_ex_pb['final_ptO2_atm']:.4f}, n_b={sim_result_ex_pb['final_n_b']:.2e}, Pcrush={sim_result_ex_pb['final_Pcrush_atm']:.3f}")
    else:
        print(f"  Error in exercise + O2 prebreathe simulation: {sim_result_ex_pb['error']}")

    end_time = time.time()
    print(f"\nTotal simulation run time: {end_time - start_time:.2f} seconds.")

    # --- Post-simulation analysis example ---
    # Example: Print end-segment states for the 15000ft profile
    print("\n--- Detailed Analysis Example for profile_35000ft_air_rest ---")
    example_profile_key = "profile_35000ft_air_rest" # Changed to target 35000ft profile
    if example_profile_key in all_simulation_results and "error" not in all_simulation_results[example_profile_key]:
        print(f"End-segment states for {example_profile_key}:")
        # Regenerate to get segment details for printing context
        original_segments = generate_altitude_exposure_profile(
            target_altitude_ft=35000.0, # Altitude for the key
            acclimatization_duration_min=5.0, 
            altitude_exposure_duration_min=60.0
        ) 
        
        for i, state in enumerate(all_simulation_results[example_profile_key].get("end_segment_states", [])):
            # Try to get corresponding original segment for context, if lists align
            original_segment_info = ""
            if i < len(original_segments):
                 orig_seg = original_segments[i]
                 original_segment_info = f"(Target Pamb: {orig_seg.P_amb_atm:.3f}, Dur: {orig_seg.duration_min:.1f} min, FIO2: {orig_seg.FIO2:.2f}, I_ex: {orig_seg.I_ex_L_min_wb:.2f})"

            print(f"  End of Segment {i+1} {original_segment_info}:")
            print(f"    t={state.t_min:.2f} min, Pamb={state.P_amb_atm:.3f} atm, P(DCS)={state.P_DCS:.3e}")
            print(f"    ptN2={state.pt_N2_atm:.4f}, ptO2={state.pt_O2_atm:.4f}, Pcrush={state.P_crush_atm:.3f}")
            print(f"    n_b={state.n_b:.2e}, r_hat={state.r_hat_dimensionless:.2e}")
            
        # To get the full history for plotting or detailed CSV export for one profile:
        specific_history = all_simulation_results[example_profile_key].get("full_history", [])
        if specific_history:
            print(f"\nFull history for {example_profile_key} has {len(specific_history)} steps.")
            # Save the full history for the example profile to the specified output directory
            csv_path = os.path.join(OUTPUT_DIR, f'{example_profile_key}_history.csv')
            with open(csv_path, 'w', newline='') as csvfile:
                fieldnames = [f.name for f in dataclasses.fields(specific_history[0])]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for step_state in specific_history:
                    writer.writerow(dataclasses.asdict(step_state))
            print(f"Full history for {example_profile_key} saved to {csv_path}")

    else:
        print(f"No detailed results or error found for {example_profile_key}.")


def altitude_to_ft(pressure_atm: float) -> float:
    """Roughly converts pressure in atm back to altitude in feet. Inverse of standard formula."""
    if pressure_atm <= 0.001: return 80000 # Arbitrary high altitude for very low pressure
    if pressure_atm >= 1.0: return 0
    # P = (1 - k*h)^n  => P^(1/n) = 1 - k*h => k*h = 1 - P^(1/n) => h = (1 - P^(1/n))/k
    k = 6.87535e-6
    n_inv = 1.0/5.2559
    try:
        h = (1.0 - pressure_atm**n_inv) / k
    except ValueError: # e.g. pressure_atm too low leads to negative in power
        h = 80000 # Assign high altitude if math error
    return max(0,h)

if __name__ == "__main__":
    main() 