# This script implements a probabilistic model for Decompression Sickness (DCS) risk
# based on principles and equations found in NASA research literature.
# It calculates tissue nitrogen pressure (P1N2), Exercise Tissue Ratio (ETR),
# and uses a logistic regression model to predict the probability of DCS.
# Key references include NASA_model/Evidence_2024.md and conkin-dcs-exercise_2004.md.

import numpy as np
from scipy.optimize import minimize # This import is currently unused.
from sklearn.linear_model import LogisticRegression

# Constants
LN2 = np.log(2)  # Natural log of 2, used in half-time calculations
P2 = 4.3  # Ambient pressure at altitude (psia), e.g., EMU suit pressure. Ref: NASA_model/Evidence_2024.md, Section I (Ascent to Altitude)
DEFAULT_T_HALF = 360  # Default nitrogen half-time in minutes. Ref: conkin-dcs-exercise_2004.md, pg. 33 (for a 360-min compartment)

# Define the variable nitrogen half-time model
def nitrogen_half_time(vo2_ml_kg_min, lambda_param):
    """
    Computes the nitrogen elimination rate constant (k)
    based on oxygen consumption (VO2) and a lambda parameter.
    This model allows for a variable half-time based on metabolic activity.

    Args:
        vo2_ml_kg_min (float): Oxygen consumption in ml/kg/min.
        lambda_param (float): An empirical parameter tuning the VO2 effect on k.

    Returns:
        float: Nitrogen elimination rate constant (k).

    Reference:
        This formula is based on Eq. 7 (for k_3) in conkin-dcs-exercise_2004.md (page 36),
        which describes a model where k is influenced by VO2.
        k_3 = ((1 - exp(-lambda_3 * mL*kg-1*min-1)) / 51.937) + 0.0019254
        Here, 0.0019254 corresponds to LN2 / 360 (the baseline compartment rate).
    """
    k = (1 - np.exp(-lambda_param * vo2_ml_kg_min)) / 51.937 + (LN2 / DEFAULT_T_HALF)
    return k

# Compute tissue nitrogen pressure P1N2
def compute_p1n2(p0, pa, vo2_ml_kg_min, pb_time_min, lambda_param):
    """
    Computes the final nitrogen tissue pressure (P1N2) after prebreathe.

    Args:
        p0 (float): Initial tissue nitrogen partial pressure (psia).
        pa (float): Ambient nitrogen partial pressure in breathing mixture during prebreathe (psia).
        vo2_ml_kg_min (float): Oxygen consumption (ml/kg/min) during prebreathe.
        pb_time_min (float): Prebreathe time in minutes.
        lambda_param (float): Lambda parameter for the nitrogen_half_time model.

    Returns:
        float: Final tissue nitrogen pressure (P1N2) in psia.

    Reference:
        Based on Equation 2 in NASA_model/Evidence_2024.md (Section I, "Tissue Ratio")
        and Equation 4 in conkin-dcs-exercise_2004.md (page 33):
        P1N2 = P0 + (Pa - P0) * (1 - exp(-k * t))
    """
    k = nitrogen_half_time(vo2_ml_kg_min, lambda_param)
    p1n2 = p0 + (pa - p0) * (1 - np.exp(-k * pb_time_min))
    return p1n2

# Compute Exercise Tissue Ratio (ETR)
def compute_etr(p1n2, p2_val=P2): # Renamed p2 to p2_val to avoid conflict with global P2
    """
    Computes the Exercise Tissue Ratio (ETR), also known as Tissue Ratio (TR) or R-value.
    ETR is an index of decompression dose.

    Args:
        p1n2 (float): Computed tissue N2 partial pressure (psia).
        p2_val (float, optional): Ambient pressure after depressurization (psia). Defaults to global P2.

    Returns:
        float: Exercise Tissue Ratio.

    Reference:
        Definition from NASA_model/Evidence_2024.md (Section I, "Tissue Ratio"):
        TR = P1N2 / P2
    """
    return p1n2 / p2_val

# Logistic regression model to predict DCS probability
def logistic_regression_model(etr, age, gender_str, coefficients):
    """
    Predicts the probability of DCS based on a logistic regression model.

    Args:
        etr (float): Exercise Tissue Ratio.
        age (float): Age of the individual in years.
        gender_str (str): Gender of the individual ("Male" or "Female").
        coefficients (tuple): Tuple of logistic regression coefficients
                              (B0_intercept, B_etr, B_age, B_gender).

    Returns:
        float: Predicted probability of DCS (between 0 and 1).

    Reference:
        Approach consistent with NASA_model/Evidence_2024.md (Section I, "Statistical and Biophysical Models")
        which discusses probabilistic models using logistic regression.
        Inclusion of Age and Gender as risk factors is supported by Table 4
        in NASA_model/Evidence_2024.md.
    """
    B0, B_etr, B_age, B_gender = coefficients
    gender_encoded = 1 if gender_str == "Female" else 0  # Matches training data encoding
    logit = B0 + (B_etr * etr) + (B_age * age) + (B_gender * gender_encoded)
    return 1 / (1 + np.exp(-logit))  # Sigmoid function

# Example Dataset for Training Logistic Regression
# NOTE: This is a very small, synthetic dataset for demonstration purposes.
# A robust model would require a comprehensive dataset from human subject testing,
# such as those described in conkin-dcs-exercise_2004.md.
data = np.array([
    # (ETR, Age, Gender_encoded (0=Male, 1=Female), DCS_outcome (0=No, 1=Yes))
    (1.5, 30, 0, 0),  # No DCS (Male)
    (1.8, 40, 1, 1),  # DCS (Female)
    (1.6, 35, 0, 0),  # No DCS (Male)
    (1.9, 50, 1, 1),  # DCS (Female)
    (1.7, 33, 0, 0),  # No DCS (Male)
    (2.0, 45, 1, 1)   # DCS (Female)
])

X_train = data[:, :3]  # Features: (ETR, Age, Gender_encoded)
y_train = data[:, 3]    # Target: DCS (1) or No DCS (0)

# Train Logistic Regression Model
log_reg = LogisticRegression()
log_reg.fit(X_train, y_train)

# Get coefficients from trained model
B0 = log_reg.intercept_[0]
# log_reg.coef_[0] will contain coefficients for ETR, Age, Gender in that order
coefficients_all = (B0, log_reg.coef_[0, 0], log_reg.coef_[0, 1], log_reg.coef_[0, 2])

# --- Example Usage ---
# Define input parameters for a hypothetical scenario
p0_initial_n2 = 8.0  # Initial tissue nitrogen pressure (psia) - e.g., after equilibration at an 8.2 psia / 34% O2 habitat (approx. 0.66 * (8.2-0.9) = 4.8 psia N2 if starting from sea level N2 partial pressure, or higher if vehicle has more N2)
                        # For this example, using 8.0 psia as a higher starting N2, assuming different habitat conditions.
pa_prebreathe_n2 = 0.0  # Ambient nitrogen pressure during 100% O2 prebreathe (psia)
vo2_ml_kg_min_pb = 45  # Example oxygen uptake during prebreathe (ml/kg/min)
pb_duration_min = 90  # Example prebreathe time (minutes)
lambda_parameter = 0.025  # Optimized lambda parameter for the nitrogen washout model (empirical)

# Calculate P1N2 and ETR
p1n2_final = compute_p1n2(p0_initial_n2, pa_prebreathe_n2, vo2_ml_kg_min_pb, pb_duration_min, lambda_parameter)
etr_calculated = compute_etr(p1n2_final) # Uses default P2 = 4.3 psia

# Subject-specific parameters for DCS prediction
subject_age = 43
subject_gender = "Male"  # String "Male" or "Female"

# Predict probability of DCS using the trained model and calculated ETR
# Note: The predictive accuracy heavily depends on the quality and size of the training dataset.
# The coefficients_all are derived from the minimal example dataset above.
predicted_dcs_probability = logistic_regression_model(etr_calculated, subject_age, subject_gender, coefficients_all)

print("--- DCS Model Prediction Example ---")
print(f"Input Parameters:")
print(f"  Initial P1N2 (p0): {p0_initial_n2} psia")
print(f"  Ambient N2 during PB (pa): {pa_prebreathe_n2} psia")
print(f"  VO2 during PB: {vo2_ml_kg_min_pb} ml/kg/min")
print(f"  Prebreathe Duration: {pb_duration_min} min")
print(f"  Lambda for k: {lambda_parameter}")
print(f"  Suit Pressure (P2): {P2} psia")
print(f"  Subject Age: {subject_age} years")
print(f"  Subject Gender: {subject_gender}")
print("\\nCalculated Values:")
print(f"  Nitrogen elimination rate constant (k): {nitrogen_half_time(vo2_ml_kg_min_pb, lambda_parameter):.6f}")
print(f"  Computed Final P1N2: {p1n2_final:.4f} psia")
print(f"  Computed ETR: {etr_calculated:.4f}")
print("\\nPrediction:")
print(f"  Predicted DCS Probability: {predicted_dcs_probability:.4%}")
