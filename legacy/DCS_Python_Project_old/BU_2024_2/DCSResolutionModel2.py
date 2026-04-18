# -*- coding: utf-8 -*-
"""
Created on Tue May 16 14:01:35 2023

@author: User
"""

import numpy as np

# Define the logistic regression function
def logistic_regression(deltaP, AMB, P1, GENDER, TYPE_DCS, AGE, MAXINTEN):
    B1 = 0.395
    B2 = 1.905
    amb_coefficient = -0.569
    p1_coefficient = -0.0628
    gender_coefficient = -0.158
    type_dcs_coefficient = -0.418
    age_coefficient = -0.0083
    maxinten_coefficient = 0.055

    z = np.exp(-(np.log(deltaP) - B2 + amb_coefficient * AMB + p1_coefficient * P1 + gender_coefficient * GENDER + type_dcs_coefficient * TYPE_DCS - age_coefficient * AGE - maxinten_coefficient * MAXINTEN) / B1)
    return 1 / (1 + z)

# Prompt the user to enter the values for the explanatory variables
deltaP = float(input("Enter deltaP (psid): "))
AMB = int(input("Enter ambulation status (1 for ambulation, 0 for nonambulation): "))
P1 = float(input("Enter P1 (pressure at which a symptom appears): "))
GENDER = int(input("Enter gender (1 for male, 0 for female): "))
TYPE_DCS = int(input("Enter type of DCS (1 for Type I, 0 for Type II): "))
AGE = float(input("Enter age (in years): "))
MAXINTEN = float(input("Enter maximum symptom intensity (on a scale of 1-10): "))

# Make the prediction
prediction = logistic_regression(deltaP, AMB, P1, GENDER, TYPE_DCS, AGE, MAXINTEN)

# Print the predicted result
print("Predicted probability of symptom resolution: ", prediction)
