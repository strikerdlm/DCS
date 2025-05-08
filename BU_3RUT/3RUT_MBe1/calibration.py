import pandas as pd
import numpy as np
from scipy.optimize import minimize
import logging
from dcs_risk_model import FlightProfile, complete_run_simulation_full, compute_risk_probability

# Assume that the following functions and classes are defined in your model:
# FlightProfile, complete_run_simulation_full, compute_risk_probability
# and that your current global configuration (test_params) contains the default parameters.
# Ensure that parameter names (e.g., "N_b0", "beta_N") are consistent.

# Mapping for excercise_level categorical values to numeric exercise intensity.
EXERCISE_INTENSITY_MAP = {
    "low": 1.0,
    "medium": 1.5,
    "high": 2.0
}

def calibrate_model_from_excel(excel_path: str, initial_params: dict):
    """
    Calibrate the 3RUT-MBe1 model using measured data from an Excel file.
    
    The Excel file is expected to have the following columns:
      - altitude (in feet)
      - prebreating_time (preoxygenation duration, in minutes)
      - excercise_level (categorical: "low", "medium", "high")
      - time_at_altitude (simulation time in minutes)
      - risk_of_decompression_sickness (measured DCS risk as a percentage)
    
    This function returns the calibrated parameters and the optimization result.
    """
    # Read the Excel file
    df = pd.read_excel(excel_path)
    
    # Standardize column names: convert to lowercase and replace spaces with underscores.
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    # Expected columns (one of):
    # altitude, prebreating_time OR prebreathing_time, excercise_level OR exercise_level, time_at_altitude, risk_of_decompression_sickness

    # Check for the exercise level column with alternate spellings.
    if "excercise_level" in df.columns:
        exercise_col = "excercise_level"
    elif "exercise_level" in df.columns:
        exercise_col = "exercise_level"
    else:
        raise KeyError("No column for exercise level found in the Excel file. Expected 'excercise_level' or 'exercise_level'.")

    logging.info("Using '%s' as the exercise level column", exercise_col)

    # Map the exercise level to a numeric exercise intensity.
    df["exercise_intensity"] = df[exercise_col].str.lower().map(EXERCISE_INTENSITY_MAP)
    df["exercise_intensity"] = df["exercise_intensity"].fillna(1.0)
    
    # Define the objective function to minimize: aggregated squared error over all exposures.
    def objective(x):
        # Update calibration parameters we wish to adjust.
        # For this example, we will calibrate "N_b0" and "beta_N".
        params = initial_params.copy()
        params["N_b0"] = x[0]
        params["beta_N"] = x[1]
        
        error_sum = 0.0
        
        # Set default ascent rate in ft/min; convert to m/s. 
        # For example, use 500 ft/min => 500 * 0.00508 = 2.54 m/s.
        default_ascent_rate_ft_min = 500
        ascent_rate_mps = default_ascent_rate_ft_min * 0.00508
        
        # Loop over each exposure (row) in the dataset.
        for idx, row in df.iterrows():
            # Convert altitude from feet (ft) to meters (m).
            altitude_m = row["altitude"] * 0.3048
            
            # Determine which column holds preoxygenation time.
            if "prebreating_time" in df.columns:
                preox_col = "prebreating_time"
            elif "prebreathing_time" in df.columns:
                preox_col = "prebreathing_time"
            else:
                raise KeyError("No column found for preoxygenation time. Expected 'prebreating_time' or 'prebreathing_time'.")
            logging.info("Using '%s' as the preoxygenation time column", preox_col)

            # Create a FlightProfile for this exposure.
            profile = FlightProfile(
                preox_duration=row[preox_col],
                ascent_rate=ascent_rate_mps,
                cruise_altitude=altitude_m,
                plateau_duration=0.0,  # assume zero if not provided
                exercise_intensity=row["exercise_intensity"]
            )
            # Use the provided "time_at_altitude" (in minutes) as the simulation time.
            sim_time = row["time_at_altitude"]
            # Run the simulation using your current model code.
            times, p_t_series, bubble_series, hazard_series = complete_run_simulation_full(
                profile, dt=0.1, simulation_time=sim_time, params_override=params
            )
            # Compute predicted risk (model output is dimensionless; convert to fraction, e.g., 0.2 for 20%).
            predicted_risk = compute_risk_probability(hazard_series[-1])
            # Convert measured risk from percentage to fraction.
            measured_risk = row["risk_of_decompression_sickness"] / 100.0
            error_sum += (predicted_risk - measured_risk)**2
        return error_sum
    
    # Initial guesses for calibration parameters.
    x0 = [initial_params.get("N_b0", 1.198), initial_params.get("beta_N", 2.0)]
    
    # Run the minimization.
    res = minimize(objective, x0, method='Nelder-Mead')
    calibrated_params = initial_params.copy()
    calibrated_params["N_b0"] = res.x[0]
    calibrated_params["beta_N"] = res.x[1]
    return calibrated_params, res

# Example usage:
if __name__ == "__main__":
    # File path to your measured data Excel file.
    excel_path = r"C:\Users\User\OneDrive\FAC\Research\Python Scripts\DCS\DCS_Risk_DB_2025.xlsx"
    
    # Use test_params or define your initial defaults. Note: "beta_N" must be used consistently in your model.
    initial_params = {
        "N_b0": 1.198,
        "beta_N": 2.0
    }
    
    calibrated_params, opt_result = calibrate_model_from_excel(excel_path, initial_params)
    logging.info("Calibrated parameters: %s", calibrated_params)
    print("Optimization Result:", opt_result)