import numpy as np
from scipy.optimize import minimize
from sklearn.linear_model import LogisticRegression

# Constants
LN2 = np.log(2)  # Natural log of 2
P2 = 4.3  # Ambient pressure at altitude (psia)
DEFAULT_T_HALF = 360  # Default nitrogen half-time in minutes

# Define the variable nitrogen half-time model
def nitrogen_half_time(vo2_ml_kg_min, lambda_param):
    """
    Computes the nitrogen elimination rate constant (k) 
    based on oxygen consumption.
    """
    k = (1 - np.exp(-lambda_param * vo2_ml_kg_min)) / 51.937 + (LN2 / DEFAULT_T_HALF)
    return k

# Compute tissue nitrogen pressure P1N2
def compute_p1n2(p0, pa, vo2_ml_kg_min, pb_time_min, lambda_param):
    """
    Computes the final nitrogen tissue pressure (P1N2) after prebreathe.
    """
    k = nitrogen_half_time(vo2_ml_kg_min, lambda_param)
    p1n2 = p0 + (pa - p0) * (1 - np.exp(-k * pb_time_min))
    return p1n2

# Compute Exercise Tissue Ratio (ETR)
def compute_etr(p1n2, p2=P2):
    return p1n2 / p2  # ETR = P1N2 / P2

# Logistic regression model to predict DCS probability
def logistic_regression_model(etr, age, gender, coefficients):
    """
    Predicts the probability of DCS based on logistic regression model.
    coefficients = (B0, B1, B2) from regression fitting.
    """
    B0, B1, B2 = coefficients
    gender_factor = 1 if gender == "Female" else 0  # Binary encoding
    logit = B0 + B1 * etr + B2 * age + gender_factor
    return 1 / (1 + np.exp(-logit))  # Sigmoid function

# Example Dataset for Training Logistic Regression
data = np.array([
    # (ETR, Age, Gender, DCS)
    (1.5, 30, 0, 0),  # No DCS (Male)
    (1.8, 40, 1, 1),  # DCS (Female)
    (1.6, 35, 0, 0),  # No DCS (Male)
    (1.9, 50, 1, 1),  # DCS (Female)
    (1.7, 33, 0, 0),  # No DCS (Male)
    (2.0, 45, 1, 1)   # DCS (Female)
])

X_train = data[:, :3]  # Features: (ETR, Age, Gender)
y_train = data[:, 3]    # Target: DCS (1) or No DCS (0)

# Train Logistic Regression Model
log_reg = LogisticRegression()
log_reg.fit(X_train, y_train)

# Get coefficients from trained model
B0, B1, B2 = log_reg.intercept_[0], log_reg.coef_[0, 0], log_reg.coef_[0, 1]

# Example Prediction
p0 = 8.0  # Initial tissue nitrogen pressure (psia)
pa = 0.0  # Ambient nitrogen pressure during 100% O2 prebreathe
vo2_ml_kg_min = 45  # Example oxygen uptake (ml/kg/min)
pb_time_min = 90  # Example prebreathe time (minutes)
lambda_param = 0.025  # Optimized parameter for nitrogen washout

p1n2 = compute_p1n2(p0, pa, vo2_ml_kg_min, pb_time_min, lambda_param)
etr = compute_etr(p1n2)

age = 43
gender = "Male"

# Predict probability of DCS
p_dcs = logistic_regression_model(etr, age, gender, (B0, B1, B2))

print(f"Computed P1N2: {p1n2:.4f} psia")
print(f"Computed ETR: {etr:.4f}")
print(f"Predicted DCS Probability: {p_dcs:.4%}")
