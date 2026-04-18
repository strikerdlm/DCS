#!/usr/bin/env python
import os
import logging
import pandas as pd
import numpy as np
from scipy.optimize import minimize

# Import key model functions and variables from your model file.
# Adjust the import path if needed.
from dcs_risk_model import (
    complete_run_simulation_full,
    compute_risk_probability,
    test_params,
    FlightProfile
)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def create_profile_from_experiment(altitude, prebreathing_time, time_at_altitude, exercise_intensity):
    """
    Create a FlightProfile instance from experimental conditions.
    Assumes the FlightProfile has attributes: altitude, preox_duration, total_duration, exercise_intensity.
    """
    # Provide a default ascent_rate (example value) and map experimental inputs to the required parameters.
    ascent_rate = 300  # default ascent rate (e.g., in ft/min or appropriate units)
    # Map:
    #   preox_duration = prebreathing_time (in minutes)
    #   cruise_altitude = altitude
    #   plateau_duration = time_at_altitude (in minutes)
    #   exercise_intensity as determined from exercise_level mapping
    profile = FlightProfile(
         preox_duration=prebreathing_time,
         ascent_rate=ascent_rate,
         cruise_altitude=altitude,
         plateau_duration=time_at_altitude,
         exercise_intensity=exercise_intensity
    )
    return profile

def simulate_risk(x, row):
    """
    Run the simulation for an experimental row with a given parameter vector x = [N_b0, beta_N].
    Returns the predicted risk as a percentage.
    """
    # Extract experimental conditions from the row
    altitude = row['altitude']
    prebreathing_time = row['prebreathing_time']   # in minutes
    time_at_altitude = row['time_at_altitude']       # in minutes

    # Map exercise level ("Rest", "Mild", "Heavy") to a numerical intensity.
    exercise_map = {'Rest': 0.5, 'Mild': 1.0, 'Heavy': 1.5}
    exercise_intensity = exercise_map.get(row['exercise_level'], 1.0)
    
    # Create the flight profile based on experimental inputs.
    profile = create_profile_from_experiment(altitude, prebreathing_time, time_at_altitude, exercise_intensity)
    
    # Update the model parameters using the current calibration vector.
    current_params = test_params.copy()
    current_params.update({
        "N_b0": x[0],
        "beta_N": x[1]
    })
    
    # Run the simulation for the scenario.
    # dt is set to 0.1 minutes; simulation_time equals the time at altitude.
    times, p_t_series, bubble_series, hazard_series = complete_run_simulation_full(
        profile, dt=0.1, simulation_time=time_at_altitude, params_override=current_params)
    
    risk_pred = compute_risk_probability(hazard_series[-1])
    result = risk_pred * 100
    logging.debug("Simulated risk for row with altitude=%.1f, prebreathing=%.1f, time_at_alt=%.1f, exercise_intensity=%.2f: Predicted risk = %.2f%%",
                  row['altitude'], row['prebreathing_time'], row['time_at_altitude'], exercise_intensity, result)
    return result

def calibration_objective(x, data):
    """
    The objective function calculates the RMSE between the model predictions and experimental risk.
    """
    errors = []
    for index, row in data.iterrows():
        predicted_risk = simulate_risk(x, row)
        experimental = row['risk_of_decompression_sickness']
        error = predicted_risk - experimental
        errors.append(error ** 2)
        logging.debug("Row %d: Predicted risk = %.2f%%, Experimental risk = %.2f%%, Error = %.2f%%",
                      index, predicted_risk, experimental, error)
    rmse = np.sqrt(np.mean(errors))
    logging.info("Calibration objective for parameters %s: RMSE = %.2f%%", x, rmse)
    return rmse

def main():
    # Filepath for experimental data.
    excel_path = r"C:\Users\User\OneDrive\FAC\Research\Python Scripts\DCS\DCS_Risk_DB_2025.xlsx"
    
    # Load the experimental data.
    data = pd.read_excel(excel_path)
    logging.info("Loaded experimental data with %d rows from %s", len(data), excel_path)
    
    # Ensure the Excel file has the needed columns.
    required_columns = ['altitude', 'prebreathing_time', 'exercise_level', 'time_at_altitude', 'risk_of_decompression_sickness']
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        logging.error("Missing columns in Excel file: %s", missing)
        return

    # Calibrate the model parameters.
    logging.info("Starting parameter calibration using Nelder-Mead optimization...")
    result = minimize(lambda x: calibration_objective(x, data), x0=[1.0, 2.0], method='Nelder-Mead')
    calibrated_params = {"N_b0": result.x[0], "beta_N": result.x[1]}
    logging.info("Optimization complete. Calibrated Parameters: %s", calibrated_params)
    print("Calibrated Parameters:", calibrated_params)
    
    # Compute predictions and error metrics.
    data['predicted_risk'] = data.apply(lambda row: simulate_risk(result.x, row), axis=1)
    data['error'] = data['predicted_risk'] - data['risk_of_decompression_sickness']
    mean_abs_error = np.mean(np.abs(data['error']))
    logging.info("Mean Absolute Error (percentage): %.2f", mean_abs_error)
    print("Mean Absolute Error (percentage):", mean_abs_error)
    
    # Optionally, save the calibration results and predictions to a new Excel file.
    output_path = os.path.join(os.path.dirname(excel_path), "calibrated_predictions.xlsx")
    data.to_excel(output_path, index=False)
    logging.info("Calibrated predictions saved to: %s", output_path)
    print("Calibrated predictions saved to:", output_path)

if __name__ == "__main__":
    main() 