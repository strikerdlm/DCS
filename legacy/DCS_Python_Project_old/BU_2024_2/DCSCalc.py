# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 10:47:59 2023

@author: User
"""

def calculate_risk(altitude, prebreathing_time, time_at_altitude, exercise_level):
    coef = [3.59860256e-05, -1.59568206e-03, 2.23643207e-03, 1.03538731e-01, 2.09400437e-02, -1.24478775e-01]
    intercept = -0.8893607739537449

    # Convert altitude from feet to meters
    altitude_meters = altitude * 0.3048

    # One-hot encode the exercise_level input
    exercise_level_rest = 1 if exercise_level.lower() == "rest" else 0
    exercise_level_mild = 1 if exercise_level.lower() == "mild" else 0
    exercise_level_heavy = 1 if exercise_level.lower() == "heavy" else 0

    # Calculate the risk using the coefficients and intercept
    risk = (coef[0] * altitude_meters +
            coef[1] * prebreathing_time +
            coef[2] * time_at_altitude +
            coef[3] * exercise_level_rest +
            coef[4] * exercise_level_mild +
            coef[5] * exercise_level_heavy +
            intercept)

    return risk * 100

# Ask the user to enter variable data
altitude = float(input("Enter altitude (feet): "))
prebreathing_time = float(input("Enter prebreathing time (minutes): "))
time_at_altitude = float(input("Enter time at altitude (minutes): "))
exercise_level = input("Enter exercise level (Rest, Mild, Heavy): ")
    
# Calculate decompression sickness risk
risk = calculate_risk(altitude, prebreathing_time, time_at_altitude, exercise_level)

# Print the result
print(f"The estimated risk of decompression sickness is {risk:.2f}%")