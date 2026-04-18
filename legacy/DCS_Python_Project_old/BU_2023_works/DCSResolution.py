# -*- coding: utf-8 -*-
"""
Created on Tue May 16 13:57:10 2023

@author: DiegoMalpica
From: Conkin, J., Abercromby, A. F. J., Dervay, J. P., Feiveson, A. H., Gernhardt, M. L., Norcross, J. R., Ploutz-Snyder, R., &#38; Wessel III, J. H. (2014). 
Probabilistic Assessment of Hypobaric Decompression Sickness Treatment Success</i>.</div>

As seen on Mendeley app

"""

import numpy as np

# Define the logistic regression function
def logistic_regression(deltaP, AMB, GENDER, TYPE_DCS, AGE):
    B1 = 0.425
    B2 = 2.091
    amb_coefficient = -0.461
    gender_coefficient = -0.201
    type_dcs_coefficient = -0.772
    age_coefficient = 0.0092

    z = np.exp(-(np.log(deltaP) - B2 + amb_coefficient * AMB + gender_coefficient * GENDER + type_dcs_coefficient * TYPE_DCS - age_coefficient * AGE) / B1)
    return 1 / (1 + z)

# Prompt the user to enter the values for the explanatory variables
deltaP = float(input("Enter deltaP (psid): "))
AMB = int(input("Enter ambulation status (1 for ambulation, 0 for nonambulation): "))
GENDER = int(input("Enter gender (1 for male, 0 for female): "))
TYPE_DCS = int(input("Enter type of DCS (1 for Type I, 0 for Type II): "))
AGE = float(input("Enter age (in years): "))

# Make the prediction
prediction = logistic_regression(deltaP, AMB, GENDER, TYPE_DCS, AGE)

# Print the predicted result
print("Predicted probability of symptom resolution: ", prediction)
