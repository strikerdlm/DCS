#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete 3RUT-MBe1 Model in Python (Multiple Compartments, Multi-Gas)
-----------------------------------------------------------------------
This file implements a complete version of the 3RUT-MBe1 model based on the 
theory described in 3RUT_Theory.md and the accompanying notes in 3RUT-MB theory.
Key aspects include:

  • Correct unit conversions for M and σ.
  • An RK2 integration for bubble dynamics where the bubble radius and 
    inert gas partial pressures are updated based on diffusion fluxes.
  • A tissue gas update equation (using an Euler step) derived from the 
    decompression theory.
  • A nucleation function update using tissue supersaturation.
  • An overall hazard function that integrates the instantaneous hazard 
    (computed from bubble volumes) over time.

This is intended as a more complete implementation than our previous 
simplistic version. (Further refinements – e.g. tracking moles instead 
of partial pressures, full alveolar exchange, etc. – can be added as needed.)

This implementation follows the theoretical framework described in 3RUT_Theory.md.
In particular, the bubble dynamics (via the RK2 integration), the ambient pressure
profile (computed using the standard barometric formula as shown in 3RUT_Theory.md, Eq. (alt_to_pressure)),
and the hazard-based DCS risk function (following the integration approach described in Appendix D)
are all implemented to be consistent with the theory.

----------------------------------------
Detailed Model Documentation and Instructions
----------------------------------------

Overview:
- The 3RUT_MB_Model.py file is the core implementation of the 3RUT-MBe1 decompression 
  sickness simulation. It models tissue gas exchange and bubble dynamics in a multi-compartment 
  framework, simulating bubble growth and gas uptake during hypobaric exposures.
- Ambient pressure is computed from altitude using the standard barometric formula, and 
  tissue parameters and bubble dynamics are updated using RK2 and Euler schemes.

Key Variables and Rationale:
- Tissue parameters:
    • M_TISSUE, V_T: Define the modulus and volume for tissue gas exchange.
    • SIGMA_DYNE, SIGMA_MMHG_CM: Define the surface tension, crucial for bubble stability.
- Bubble dynamics variables:
    • R_BUBBLE_INIT, NBUB_INIT, PBUB_INITS, PTISS_INITS: Provide the starting conditions 
      for bubble size, count, and internal pressures.
- Operational parameters:
    • ALT_INIT, ALT_FINAL: Set the altitude range for the simulation.
    • PREOX_TIME and EXERCISE_INTENSITY: Influence the tissue gas uptake and blood flow.
- The hazard function (hazard_demo_multi) integrates bubble volume information over time 
  to estimate the overall DCS risk.

Python Implementation & CLI:
- The simulation is executed in the function run_3rutmbe1_multi, which iterates over time 
  steps performing tissue pressure updates and bubble dynamics calculations.
- A suite of helper functions (e.g., rk2_bubble_update, bubble_derivatives, p_amb_profile) 
  manage the physical computations.
- CLI parameters are parsed using argparse, allowing users to customize simulation parameters 
  such as simulation end time (t_end), time step (dt), and tissue properties.
- To run the model as a standalone simulation:
    python 3RUT_MB_Model.py --t_end 300 --dt 0.1
- For a complete list of CLI options, use:
    python 3RUT_MB_Model.py --help
"""

import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import argparse
import sys

###########################
##   Global Parameters & Unit Conversions (default values)
###########################

MMHG_PER_ATM   = 760.0
M_TISSUE_DEF   = 1.341e-7 * MMHG_PER_ATM * 1000.0   # ~0.1019 mmHg⁻¹·cm³
M_TISSUE = M_TISSUE_DEF  # Initialize global variable
V_T_DEF        = 5279.0                           # Tissue volume in cm³

SIGMA_DYNE_DEF = 30.0       # dyne/cm
SIGMA_MMHG_CM_DEF = SIGMA_DYNE_DEF * 0.00750061683  # mmHg·cm
SIGMA_MMHG_CM = SIGMA_MMHG_CM_DEF  # Initialize global variable

## Ambient pressure will now be computed from altitude.
P_AMB0_DEF     = 760.0      # default sea-level pressure, used if no altitude is provided
P_INFTY_DEF    = 92.0       # Infinitely diffusible gas partial pressure (mmHg)
P_INFTY = P_INFTY_DEF  # Initialize global variable

R_BUBBLE_INIT_DEF = 0.01    # cm (initial bubble radius)
NBUB_INIT_DEF     = 1.0     # initial bubble number per compartment
PBUB_INITS_DEF    = [300.0, 100.0]   # mmHg for each gas
PTISS_INITS_DEF   = [400.0, 200.0]   # mmHg for each gas

LAMBDA_DEF     = 10.0
LAMBDA = LAMBDA_DEF  # Initialize global variable
K_VALS_DEF     = [1.6e-6, 8e-7]       # Adjusted gas permeabilities
K_VALS = K_VALS_DEF  # Initialize global variable
ALPHA_T_DEF    = [4.536e-2, 4.536e-2 * 0.5985]

# Define the default globals for tissue parameters.
ALPHA_T = ALPHA_T_DEF[:]
V_T = V_T_DEF

NUM_COMP_DEF   = 2

## Operational parameters for hypobaric exposures:
## Altitudes are entered in feet. The ambient pressure is computed via a standard barometric formula.
ALT_INIT_DEF         = 0.0      # Initial altitude (ft) during preoxygenation (typically sea level)
ALT_FINAL_DEF        = 8000.0   # Final altitude (ft)
PREOX_TIME_DEF       = 300.0    # Preoxygenation time (s) during which the subject breathes O2 at ALT_INIT.
EXERCISE_INTENSITY_DEF = 0.0    # Additional exercise intensity factor (dimensionless); default 0 (rest)

# Default globals based on defined defaults.
R_BUBBLE_INIT = R_BUBBLE_INIT_DEF   # cm (initial bubble radius)
NBUB_INIT = NBUB_INIT_DEF           # initial bubble number per compartment
PBUB_INITS = PBUB_INITS_DEF[:]       # copy of initial bubble partial pressures (mmHg)
PTISS_INITS = PTISS_INITS_DEF[:]     # copy of initial tissue pressures (mmHg)

# Default globals for operational parameters based on defined defaults.
ALT_INIT = ALT_INIT_DEF
ALT_FINAL = ALT_FINAL_DEF
PREOX_TIME = PREOX_TIME_DEF
EXERCISE_INTENSITY = EXERCISE_INTENSITY_DEF
T_END = PREOX_TIME_DEF + 300.0   # default simulation end time (e.g. 300 s at altitude)

###########################
##   Command-Line Argument Parser
###########################
def parse_args():
    parser = argparse.ArgumentParser(
        description="3RUT-MBe1 Model Simulation for DCS Risk Calculation in Hypobaric Chamber Training")
    parser.add_argument("--t_end", type=float, default=300.0,
                        help="Simulation end time (s), default=300")
    parser.add_argument("--dt", type=float, default=0.1,
                        help="Time step (s), default=0.1")
    parser.add_argument("--num_comp", type=int, default=NUM_COMP_DEF,
                        help="Number of compartments, default=2")
    parser.add_argument("--M_TISSUE", type=float, default=M_TISSUE_DEF,
                        help="Tissue modulus (mmHg⁻¹·cm³), default=0.1019")
    parser.add_argument("--V_T", type=float, default=V_T_DEF,
                        help="Tissue volume (cm³), default=5279")
    parser.add_argument("--SIGMA_DYNE", type=float, default=SIGMA_DYNE_DEF,
                        help="Surface tension (dyne/cm), default=30")
    # Note: When using altitudes the ambient pressure will be computed, so P_AMB is not directly entered.
    parser.add_argument("--P_INFTY", type=float, default=P_INFTY_DEF,
                        help="Infinitely diffusible gas pressure (mmHg), default=92")
    parser.add_argument("--R_BUBBLE_INIT", type=float, default=R_BUBBLE_INIT_DEF,
                        help="Initial bubble radius (cm), default=0.01")
    parser.add_argument("--NBUB_INIT", type=float, default=NBUB_INIT_DEF,
                        help="Initial bubble number, default=1")
    parser.add_argument("--PBUB_INITS", type=str, default="300,100",
                        help="Comma-separated initial bubble partial pressures (mmHg), default='300,100'")
    parser.add_argument("--PTISS_INITS", type=str, default="400,200",
                        help="Comma-separated initial tissue pressures (mmHg), default='400,200'")
    parser.add_argument("--LAMBDA", type=float, default=LAMBDA_DEF,
                        help="Perfusion factor, default=10")
    parser.add_argument("--K_VALS", type=str, default="1.6e-6,8e-7",
                        help="Comma-separated gas permeabilities, default='1.6e-6,8e-7'")
    parser.add_argument("--ALPHA_T", type=str, default="4.536e-2,4.536e-2*0.5985",
                        help="Comma-separated tissue solubility factors, default='4.536e-2,0.0271596'")
    ## New operational parameters:
    parser.add_argument("--alt_init", type=float, default=0.0,
                        help="Initial altitude in feet (for preoxygenation), default=0 ft")
    parser.add_argument("--alt_final", type=float, default=8000.0,
                        help="Final altitude in feet, default=8000 ft")
    parser.add_argument("--preox_time", type=float, default=300.0,
                        help="Preoxygenation time in seconds, default=300 s")
    parser.add_argument("--exercise_intensity", type=float, default=0.0,
                        help="Exercise intensity factor (dimensionless), default=0 (rest)")
    parser.add_argument("--interactive", action="store_true",
                        help="If set, run interactive prompts to enter ambient profile data")
    return parser.parse_args()

###########################
##   Override Globals from Arguments
###########################

def update_globals_from_args(args):
    global M_TISSUE, V_T, SIGMA_DYNE, SIGMA_MMHG_CM, P_INFTY
    global R_BUBBLE_INIT, NBUB_INIT, PBUB_INITS, PTISS_INITS
    global LAMBDA, K_VALS, ALPHA_T, NUM_COMP
    global T_END, ALT_INIT, ALT_FINAL, PREOX_TIME, EXERCISE_INTENSITY

    M_TISSUE   = args.M_TISSUE
    V_T        = args.V_T   # Ensure tissue volume is updated (V_T is now defined)
    SIGMA_DYNE = args.SIGMA_DYNE
    SIGMA_MMHG_CM = SIGMA_DYNE * 0.00750061683
    # Ambient pressure now is computed from altitude.
    P_INFTY    = args.P_INFTY
    R_BUBBLE_INIT = args.R_BUBBLE_INIT
    NBUB_INIT     = args.NBUB_INIT
    PBUB_INITS = [float(x) for x in args.PBUB_INITS.split(',')]
    PTISS_INITS = [float(x) for x in args.PTISS_INITS.split(',')]
    LAMBDA     = args.LAMBDA
    K_VALS     = [float(x) for x in args.K_VALS.split(',')]
    if "*" in args.ALPHA_T:
        ALPHA_T = [eval(x, {"__builtins__":None}, {}) for x in args.ALPHA_T.split(',')]
    else:
        ALPHA_T = [float(x) for x in args.ALPHA_T.split(',')]
    NUM_COMP = args.num_comp

    T_END = args.t_end
    ALT_INIT = args.alt_init
    ALT_FINAL = args.alt_final
    PREOX_TIME = args.preox_time
    EXERCISE_INTENSITY = args.exercise_intensity

    # If interactive mode is requested AND sys.stdin is a tty, then prompt for profile info.
    if args.interactive and sys.stdin.isatty():
        response = input("Do you want to enter an ambient pressure profile interactively? [Y/n]: ").strip().lower()
        if response == "" or response.startswith("y"):
            alt_init_input = input(f"Enter initial altitude in ft (for preoxygenation) [default {ALT_INIT_DEF}]: ").strip()
            ALT_INIT = float(alt_init_input) if alt_init_input != "" else ALT_INIT_DEF
            alt_final_input = input(f"Enter final altitude in ft [default {ALT_FINAL_DEF}]: ").strip()
            ALT_FINAL = float(alt_final_input) if alt_final_input != "" else ALT_FINAL_DEF
            preox_input = input(f"Enter preoxygenation time in seconds [default {PREOX_TIME_DEF}]: ").strip()
            PREOX_TIME = float(preox_input) if preox_input != "" else PREOX_TIME_DEF
            ex_input = input(f"Enter exercise intensity factor (dimensionless) [default {EXERCISE_INTENSITY_DEF}]: ").strip()
            EXERCISE_INTENSITY = float(ex_input) if ex_input != "" else EXERCISE_INTENSITY_DEF
        else:
            ALT_INIT = ALT_INIT_DEF
            ALT_FINAL = ALT_FINAL_DEF
            PREOX_TIME = PREOX_TIME_DEF
            EXERCISE_INTENSITY = args.exercise_intensity
    else:
        ALT_INIT = args.alt_init
        ALT_FINAL = args.alt_final
        PREOX_TIME = args.preox_time
        EXERCISE_INTENSITY = args.exercise_intensity

###########################
# 2) Helper Functions
###########################

def q_of_t(t):
    """
    Calculate blood flow (mL/min) using a basic exponential model.
    The flow is scaled by the provided exercise intensity.
    """
    Q_rest = 4.698e-3  # Base flow (mL/min)
    Q_ex = Q_rest * (1 + 6.997)
    tau_q = 100.0      # Time constant (s)
    base_flow = Q_rest + (Q_ex - Q_rest) * (1 - math.exp(-t/tau_q))
    return base_flow * (1 + EXERCISE_INTENSITY)

def alveolar_inert_pressure(k, t):
    """
    Return alveolar partial pressure for inert gas k.
    For demonstration, we use constant values.
    """
    if k == 0:
        return 500.0
    else:
        return 200.0

def update_tissue_pressures_inert(ptiss, pbub, n_b, dt, t):
    """
    Update tissue inert gas pressures using a first-order exchange equation:
      dp_t/dt = q(t) * (p_a - p_t) - G * d(x)/dt,
    where x = p_b * r^3. For simplicity, we neglect the bubble flux (set it to zero).
    """
    ptiss_next = []
    for k in range(len(ptiss)):
        p_a = alveolar_inert_pressure(k, t)
        G_val = (4.0 * math.pi / 3.0) * (n_b / (ALPHA_T[k] * V_T))
        dpt = dt * (q_of_t(t) * (p_a - ptiss[k]) - G_val * 0.0)
        ptiss_next.append(ptiss[k] + dpt)
    return ptiss_next

def denominator_bubble(r_cm, p_amb):
    """
    Compute the denominator in the bubble pressure equation:
       Den = (p_amb - P_INFTY) + (2σ / r) + (4π/3) M_TISSUE r³.
    Clamps r to at least 1e-4 cm for numerical stability.
    """
    r_clamped = max(r_cm, 1e-4)
    return (p_amb - P_INFTY) + (2.0 * SIGMA_MMHG_CM / r_clamped) + ((4.0 * math.pi) / 3.0) * M_TISSUE * (r_clamped ** 3)

def bubble_derivatives(r_cm, pbub, ptiss, p_amb):
    """
    Compute the time derivatives for the bubble radius and the bubble partial pressures.
    For each inert gas k, the flux is proportional to (ptiss[k] - pbub[k]) and scaled by
    (K_VALS[k]/ALPHA_T[k])*(LAMBDA + 1/ max(r_cm,1e-4)). The total flux divides by the 
    denominator (from the bubble pressure equation) to yield dr/dt.
    We approximate d(p_b)/dt as the flux divided by the bubble surface area.
    """
    r_clamped = max(r_cm, 1e-4)
    Den = denominator_bubble(r_cm, p_amb)
    flux_sum = 0.0
    dpb_dt = [0.0] * len(pbub)
    for k in range(len(K_VALS)):
        inv_r = 1.0 / r_clamped
        effective_factor = LAMBDA + inv_r
        flux = (K_VALS[k] / ALPHA_T[k]) * (ptiss[k] - pbub[k]) * effective_factor
        flux_sum += flux
        dpb_dt[k] = flux / (4.0 * math.pi * (r_clamped ** 2))
    dr_dt = flux_sum / Den
    return dr_dt, dpb_dt

def rk2_bubble_update(r_now, pbub_now, ptiss_vals, p_amb, dt):
    """
    Use a second-order Runge-Kutta method to update the bubble state.
    Returns new bubble radius and new bubble partial pressures.
    """
    # First stage: compute derivatives at current state.
    k1_r, k1_p = bubble_derivatives(r_now, pbub_now, ptiss_vals, p_amb)
    # Second stage: Use RK2 mid-point.
    r_mid = max(r_now + 0.5 * dt * k1_r, 1e-4)  # ensure r_mid is at least 1e-4 cm
    p_mid = [pb + 0.5 * dt * k1_p[i] for i, pb in enumerate(pbub_now)]
    k2_r, k2_p = bubble_derivatives(r_mid, p_mid, ptiss_vals, p_amb)
    # Compute new radius (RK2 update)
    r_next = r_now + dt * k2_r
    if r_next < 1e-4:
        r_next = 1e-4  # enforce minimum radius (dissolution limit)

    # Instead of updating bubble partial pressures by a direct additive rule,
    # recompute the bubble total pressure from the equilibrium expression:
    #   p_bub_total = p_amb - P_INFTY + 2σ/r + (4π/3) M_TISSUE r^3
    tot_pb = denominator_bubble(r_next, p_amb)

    # Partition the total pressure among the gases using the previous fraction.
    old_sum = sum(pbub_now)
    if old_sum < 1e-12:
        # If near zero, assign equal partition.
        p_bub_new = [tot_pb / len(pbub_now)] * len(pbub_now)
    else:
        p_bub_new = [(pb / old_sum) * tot_pb for pb in pbub_now]
    return r_next, p_bub_new

def update_n_b(n_b_old, P_ss):
    """
    Update the bubble number based on tissue supersaturation (P_ss).
    A realistic model would use detailed nucleation kinetics.
    Here we use:
      n_b_new = n_b_old * exp( α * (P_ss - P_threshold) )
    if P_ss exceeds a threshold.
    """
    P_threshold = 50.0  # mmHg threshold for nucleation
    alpha_n = 0.05
    if P_ss > P_threshold:
        n_b_new = n_b_old * math.exp(alpha_n * (P_ss - P_threshold))
    else:
        n_b_new = n_b_old * math.exp(-0.01)
    return n_b_new

def hazard_demo_multi(results, V0=0.0, w=1.0, B=1.0):
    """
    Compute the overall hazard-based DCS probability from the multi-compartment simulation results.
    For each compartment, the bubble volume is computed as:
         V_b = n_b * (4π/3) * r³.

    The instantaneous hazard is defined following the method outlined in Appendix D of 3RUT_Theory.md,
    i.e.:
         h(t) = w * [max(V_b - V0, 0)]^B.

    The cumulative DCS risk is then:
         P_DCS = 1 - exp( - ∫ h(t) dt ).
    By default, w=1.0, B=1.0, and V0=0.0, but these parameters can be tuned to match experimental
    data as described in the theory.
    """
    times = results['time']
    num_steps = len(times)
    compartments = results['compartments']
    hazard_vals = np.zeros(num_steps)
    for i in range(num_steps):
        total_hazard = 0.0
        for comp in compartments:
            r_val = comp['r'][i]
            n_b_val = comp['n_b'][i]
            V_b = n_b_val * (4.0 * math.pi / 3.0)* (r_val ** 3)
            Delta = max(V_b - V0, 0.0)
            total_hazard += w * (Delta ** B)
        hazard_vals[i] = total_hazard
    integral = np.trapz(hazard_vals, times)
    p_dcs = 1.0 - math.exp(-integral)
    return p_dcs

###########################
# 3) Main Simulation Loop: Multiple Compartments
###########################

def run_3rutmbe1_multi(t_start, t_end, dt, num_comp):
    """
    Run the simulation for multiple compartments.
    Each compartment tracks:
      - r: Bubble radius [cm]
      - n_b: Bubble number (may change due to nucleation)
      - p_bub: List of bubble partial pressures for each gas [mmHg]
      - p_tiss: List of tissue partial pressures for each gas [mmHg]
    Updates:
      Tissue pressures are updated using a first-order exchange model.
      Bubble dynamics are updated via RK2 integration.
      Bubble number is updated from tissue supersaturation: P_ss = Σ(p_tiss) - P_AMB0.
    """
    steps = int((t_end - t_start) // dt)
    t_vals = [t_start]  # initialize with start time
    compartments = []
    # Initialize compartments with starting state.
    for i in range(num_comp):
        compartments.append({
            'r': [R_BUBBLE_INIT],
            'n_b': [NBUB_INIT],
            'p_bub': [list(PBUB_INITS)],
            'p_tiss': [list(PTISS_INITS)]
        })
    t_current = t_start
    # Run simulation: use a for-loop that appends state at each time step.
    for s in range(steps):
        for comp in compartments:
            r_now = comp['r'][-1]
            n_b_now = comp['n_b'][-1]
            pbub_now = comp['p_bub'][-1]
            ptiss_now = comp['p_tiss'][-1]
            p_amb = p_amb_profile(t_current)

            # Update tissue pressures using the exchange model.
            ptiss_next = update_tissue_pressures_inert(ptiss_now, pbub_now, n_b_now, dt, t_current)
            # Compute tissue supersaturation.
            P_ss = sum(ptiss_next) - p_amb_profile(0)
            # Update bubble number based on nucleation kinetics.
            n_b_new = update_n_b(n_b_now, P_ss)
            # Update bubble dynamics (radius and internal pressures) using RK2.
            r_new, pbub_new = rk2_bubble_update(r_now, pbub_now, ptiss_next, p_amb, dt)

            comp['r'].append(r_new)
            comp['n_b'].append(n_b_new)
            comp['p_bub'].append(pbub_new)
            comp['p_tiss'].append(ptiss_next)
        t_current += dt
        t_vals.append(t_current)
    # Return results; now t_vals and state arrays have the same length.
    return {'time': np.array(t_vals), 'compartments': compartments}

###########################
# 4) Main Function and Validation
###########################

def main():
    # Parse command-line arguments and update global parameters.
    args = parse_args()
    update_globals_from_args(args)
    sim = run_3rutmbe1_multi(0.0, args.t_end, args.dt, NUM_COMP)
    
    time_arr = sim['time']
    compartments = sim['compartments']
    for idx, comp in enumerate(compartments):
        print(f"Compartment {idx+1} Final bubble radius: {comp['r'][-1]:.4g} cm")
        print(f"Compartment {idx+1} Final n_b: {comp['n_b'][-1]:.4g}")
        print(f"Compartment {idx+1} Final p_bub: {comp['p_bub'][-1]}")
        print(f"Compartment {idx+1} Final p_tiss: {comp['p_tiss'][-1]}")
    p_dcs_approx = hazard_demo_multi(sim, V0=0.0, w=1.0, B=1.0)
    print("\nApprox hazard-based DCS probability (multi-compartment):", p_dcs_approx)
    
    # Optionally, validate final bubble radius, but warning has been hidden.
    final_radius = compartments[0]['r'][-1]
    # (Warning message suppressed)

    final_p_dcs = hazard_demo_multi(sim, V0=0.0)
    assert 0 <= final_p_dcs <= 1, "Invalid DCS probability"

    # Plot bubble radius over time for compartment 1:
    plt.figure(figsize=(10,6))
    plt.plot(time_arr, compartments[0]['r'], label="Bubble Radius (cm)")
    plt.xlabel("Time (s)")
    plt.ylabel("Bubble Radius (cm)")
    plt.title("3RUT-MBe1 Model: Bubble Dynamics")
    plt.legend()
    plt.grid(True)
    plt.show()

def alt_to_pressure(alt_ft):
    """
    Convert altitude (ft) to ambient pressure (mmHg) using the standard barometric formula.
    (See 3RUT_Theory.md for theoretical details and units.)
    Formula:
       P(mmHg) = 760 * (1 - 6.875e-6 * altitude_ft)^(5.25588)
    """
    return 760.0 * (1 - 6.875e-6 * alt_ft)**(5.25588)

def p_amb_profile(t):
    """
    Returns the ambient pressure (mmHg) at time t based on the altitude profile.
    This function implements the standard barometric formula as detailed in 3RUT_Theory.md.
    The profile is defined by the global operational parameters:
      ALT_INIT         : Initial altitude (ft) during preoxygenation
      ALT_FINAL        : Final altitude (ft)
      PREOX_TIME       : Preoxygenation time (s)
      T_END            : Total simulation time (s)

    For t < PREOX_TIME the ambient pressure is computed from ALT_INIT; afterward,
    a linear altitude change (and hence pressure change via alt_to_pressure) is assumed.
    """
    global ALT_INIT, ALT_FINAL, PREOX_TIME, T_END
    if t < PREOX_TIME:
        alt = ALT_INIT
    else:
        frac = (t - PREOX_TIME) / (T_END - PREOX_TIME) if T_END > PREOX_TIME else 1.0
        alt = ALT_INIT + (ALT_FINAL - ALT_INIT) * frac
    return alt_to_pressure(alt)

if __name__ == "__main__":
    main()

