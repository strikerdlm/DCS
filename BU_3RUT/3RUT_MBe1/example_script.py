from dcs_risk_model import FlightProfile, complete_run_simulation_full, compute_risk_probability

# Convert 40000 ft to meters (1 ft = 0.3048 m)
cruise_altitude_m = 20000 * 0.3048  # Approximately 12192 meters

# Create a FlightProfile with no preoxygenation and a plateau of 120 minutes.
# Setting ascent_rate to 0 means the simulation will start immediately at cruise altitude.
profile = FlightProfile(
    preox_duration=30,          # no preoxygenation
    ascent_rate=0,             # no ascent simulation (immediate altitude)
    cruise_altitude=cruise_altitude_m, 
    plateau_duration=15,      # 120 minutes at altitude
    exercise_intensity=1.0     # standard exercise intensity (can be adjusted if needed)
)

# Run the simulation using a small dt (e.g., 0.1 min)
times, p_t_series, bubble_series, hazard_series = complete_run_simulation_full(profile, dt=0.1)

# Compute the final DCS risk probability from the last hazard value generated
risk_probability = compute_risk_probability(hazard_series[-1])
print("The computed DCS risk probability is: {:.4f}".format(risk_probability)) 