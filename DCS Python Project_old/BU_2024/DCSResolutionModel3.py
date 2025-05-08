# -*- coding: utf-8 -*-
"""
Created on Tue May 16 14:01:35 2023

@author: DiegoMalpica

"""

import numpy as np

def symptom_resolution_probability(deltaP, AMB, Ts):
    B1 = 0.478
    B2 = 1.510
    amb_coefficient = 0.795
    Ts_coefficient = -0.00308

    z = np.exp(-(np.log(deltaP) - B2 + amb_coefficient * AMB - Ts_coefficient * Ts) / B1)
    return 1 / (1 + z)

# Prompt the user to enter the values for deltaP, AMB, and Ts
deltaP = float(input("Enter deltaP (pressure change): "))
AMB = int(input("Enter ambulation status (1 for ambulation, 0 for nonambulation): "))
Ts = float(input("Enter elapsed time from start of EVA to symptom recognition (in minutes): "))

# Calculate the probability of symptom resolution using the model
probability = symptom_resolution_probability(deltaP, AMB, Ts)

# Print the estimated probability of symptom resolution
print("Estimated probability of symptom resolution:", probability)
