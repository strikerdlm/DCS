import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# --- Profile Segment Definition (Example) ---
@dataclass
class ProfileSegment:
    duration_min: float
    P_amb_atm: float
    FIO2: float
    FIN2: float
    I_ex_L_min_wb: float # Exercise intensity (Whole Body V_O2_wb - V_O2_wb_rest)

# --- Parameters ---
@dataclass
class ModelParameters:
    """
    Stores all parameters for the 3RUT-MBe1 model.
    Values are based on Table 3 from NEDU TR 18-01 (3RUT_Theory 1.md)
    unless otherwise specified.
    """
    # Fixed Parameters (from Table 3 or common knowledge)
    P_H2O_mmHg: float = 47.0  # Water vapor pressure (mmHg)
    RQ_respiratory_quotient: float = 1.0
    pt_CO2_tissue_mmHg: float = 45.0  # Tissue CO2 partial pressure (mmHg)
    
    alpha_b_O2_ml_ml_atm: float = 0.02356 # O2 solubility in blood (mL_gas/mL_blood/atm)
    alpha_b_N2_ml_ml_atm: float = 0.01410 # N2 solubility in blood (mL_gas/mL_blood/atm)
    
    K_alpha_N2_solubility_factor: float = 0.5985 # alpha_t_N2 = K_alpha_N2 * alpha_t_O2
    K_D_N2_diffusivity_factor: float = 0.9091   # D_t_N2 = K_D_N2 * D_t_O2
    
    sigma_surface_tension_dyne_cm: float = 30.0 # Surface tension (dyne/cm) - unscaled

    # Adjustable Parameters (Values from Table 3, 3RUT-MBe1 column)
    gain_g_hazard: float = 0.06188 # Hazard function gain factor (1/(scaled_vol*time) if Nb^BN is dimensionless)
    
    N0_b_total_nuclei_unscaled: float = 1.198 # Total # nuclei (unscaled, per V_t)
    beta0_initial_nuclei_slope_unscaled_cm: float = 4.868E-5 # Initial nuclei size distribution slope (cm, unscaled)
                                                            # Note: Appendix C uses beta_hat (scaled)
    
    M_elastic_modulus_atm_V_neg1_unscaled: float = 1.341E-7 # Elastic modulus (atm*V^-1) - unscaled.
                                                        # Appendix C uses M_hat = (4pi/3)M/Lambda^3 (scaled, atm)
                                                        # Table 3 M units are atm.V^-1, M_hat in C.1 is M_bar
                                                        # M_bar in Appendix C (M_hat in A.42) has units of pressure.
                                                        # The M in table 3 needs conversion: M_hat = (4pi/3) * M_table3 * (Vt_unscaled / Lambda^3) / Vt_unscaled ???
                                                        # Or is M in table 3 already M_hat? Coeff of Var is huge.
                                                        # Let's assume M from table is M_bar directly for now (units atm)
    M_elastic_modulus_scaled_atm: float = 1.341E-7 # Directly using as M_hat (atm) from table for now.

    N_VGE_gas_loss_rate_ml_neg1_min_neg1: float = 4.758 # VGE gas loss rate (mL^-1 * min^-1)
    
    sigma_c_crumbling_compression_factor_unscaled: float = 19.64 # unitless factor for sigma_c = factor * sigma.
                                                                # Appendix C uses sigma_c_hat = Lambda * sigma_c
                                                                # This implies sigma_c from table is unscaled and needs scaling by Lambda.
                                                                # Let's treat it as (sigma_c/sigma) = 19.64, so sigma_c = 19.64 * sigma_surface_tension
                                                                # Then sigma_c_hat = Lambda * 19.64 * sigma_surface_tension

    alpha_t_O2_ml_ml_atm: float = 0.04536 # O2 solubility in tissue [mL(SPD,37).mL^-1.atm^-1]
    
    # V_t_tissue_volume_ml: float = 0.05279 # Tissue volume (mL) - This is likely V_t_hat (scaled volume)
                                        # because G_hat_k_n in C.25 uses V_t_hat.
                                        # Paper says V_t_hat = Vt * Lambda^3.
                                        # If this is V_t_hat, then V_t_unscaled = V_t_table3 / Lambda^3
    V_t_tissue_volume_scaled_dimensionless: float = 0.05279 # Assuming this is V_hat_t from Table 3

    Q_blood_flow_rate_ml_min: float = 0.004698 # Blood flow rate (mL/min) - This is likely Q_rest for the compartment
                                              # Q_n in C.23 is blood flow per unit tissue vol.
                                              # So Q_n_rest = Q_blood_flow_rate_ml_min / (V_t_tissue_volume_scaled / Lambda^3) if V_t is V_hat
                                              # Or if V_t in table is unscaled, then Q_n_rest = Q_blood_flow_rate_ml_min / V_t_tissue_volume_ml
    Q_rest_compartmental_ml_per_ml_tissue_per_min: float = 0.004698 / 0.05279 # Q_rest / V_t_unscaled assuming V_t from table is unscaled.
                                                                         # Or if V_t_table3 is V_hat, then Q_rest / (V_hat / Lambda^3)
                                                                         # Let's assume values from table for Q and Vt are unscaled Q_total and V_total for compartment
                                                                         # Q_dot_n = Q_total_n / V_total_unscaled
                                                                         # Value Q_dot from table is 4.698E-3 for Q_total, V_t is 5.279E-2 for V_total
                                                                         # So Q_dot_rest = (4.698E-3 ml/min) / (5.279E-2 ml) = 0.089 ml/ml_tissue/min

    D_t_O2_cm2_min: float = 0.001414 # O2 diffusivity (cm^2/min) - unscaled
    
    BN_bubble_number_power_factor: float = 2.172
    
    P_crush_decay_time_constant_min: float = 201.4 # tau_Pc (min)
    
    m_beta_ex_nucleation_exercise_factor: float = 0.6162 # (beta_ex = 1 + m_beta_ex * I_ex)
    
    V_O2_rest_compartmental_ml_per_ml_tissue_per_min: float = 4.401E-5 # V_O2_rest per unit tissue volume (ml_O2/ml_tissue/min)
    
    m_V_O2_slope_vs_Iex: float = 0.001677 # slope V_O2 vs I_ex ( (ml_O2/ml_tissue/min) / (L_wb_O2/min) )
    
    m_Q_slope_vs_V_O2: float = 6.997 # slope Q_dot vs V_O2_dot_compartmental ( (ml/ml_tissue/min) / (ml_O2/ml_tissue/min) ) dimensionless if V_O2 is per unit tissue

    # Parameters not in Table 3 but needed for scaled equations
    Lambda_scale_factor_cm_neg1: float = 100.0 # Arbitrary scale factor (1/cm), needs to be chosen.
                                               # Given D_t_O2 is cm^2/min, K_hat = 3*Lambda^2*K. K = D*alpha.
                                               # alpha_t_O2 is ml_gas/ml_tissue/atm.
                                               # Typical K might be ~1e-5 cm^2/min/atm * some_alpha.
                                               # K_hat units should be 1/min.
                                               # If K ~ D*alpha_t ~ 1e-3 * 0.04 ~ 4e-5 cm^2/min/atm
                                               # K_hat = 3 * Lambda^2 * D * alpha_t
                                               # To get K_hat ~ 1/min, Lambda^2 ~ 1 / (3*4e-5) ~ 1 / 12e-5 ~ 1e5/12 ~ 8300. Lambda ~ 90.
                                               # Let's choose Lambda = 100 cm^-1 for now.

    N_min_b_nuclei_threshold: float = 1e-6 # Arbitrary minimum number of bubbles for log term in C.6, C.10

    # Derived and Scaled Parameters will be calculated in __post_init__ or model
    P_infinity_mmHg: float = field(init=False)
    
    # Scaled parameters (will be derived from above and Lambda)
    # Example: sigma_hat_dyne_cm_neg2_or_atm (pressure units) = Lambda * sigma_dyne_cm
    # sigma_hat_atm = Lambda_cm_neg1 * sigma_dyne_cm * (1 atm / 1.01325e6 dyne/cm^2)
    sigma_hat_atm: float = field(init=False)
    sigma_c_hat_atm: float = field(init=False) # sigma_c_hat = Lambda * sigma_c_unscaled
    
    # K_hat_N2_per_min, K_hat_O2_per_min
    K_hat_N2_per_min: float = field(init=False)
    K_hat_O2_per_min: float = field(init=False)

    V_t_unscaled_ml: float = field(init=False) # V_t = V_t_hat / Lambda^3, but V_t_hat is dimensionless in Appendix C
                                          # Let's assume V_t_tissue_volume_scaled_dimensionless from table IS V_t_hat
                                          # V_t_unscaled_ml will be V_t_tissue_volume_scaled_dimensionless / (Lambda_scale_factor_cm_neg1 * (1ml_to_cm3_factor=1))^3
                                          # This seems off. V_hat_t in C.25 is V_t * Lambda^3. So V_t_unscaled should be used.
                                          # Let's assume the Vt from table (0.05279) is UN SCALED Vt in mL.
                                          # Then V_hat_t = Vt_ml * (Lambda_cm_neg1)^3
    
    # Let's redefine based on assumption that Table 3 Vt and Q are unscaled total compartment values.
    # Adjustable Parameters (Revisited based on scaling thoughts)
    # V_t_tissue_volume_ml: float = 0.05279 # UN SCALED total tissue volume of compartment (mL)
    # Q_blood_flow_rate_rest_ml_min: float = 0.004698 # UN SCALED total resting blood flow for compartment (mL/min)

    # So, let's rename for clarity:
    V_total_compartment_ml: float = 0.05279
    Q_total_compartment_rest_ml_min: float = 0.004698
    
    # These will be calculated:
    V_hat_t_scaled_dimensionless: float = field(init=False) # V_total_compartment_ml * (Lambda_scale_factor_cm_neg1 * 0.1)^3 (if Lambda in m-1)
                                                            # Lambda is cm^-1, Vt_ml is cm^3. V_hat_t = Vt_cm3 * Lambda_cm_neg1^3
    
    # Blood flow per unit UN SCALED tissue volume (q_n or Q_dot_n in B.13, B.25)
    # q_n = Q_total_n / V_total_compartment_ml
    # This will be calculated dynamically in the model.

    beta0_hat_initial_nuclei_slope_dimensionless: float = field(init=False) # beta0_unscaled_cm * Lambda


    def __post_init__(self):
        self.P_infinity_mmHg = self.P_H2O_mmHg + self.pt_CO2_tissue_mmHg
        
        # Convert sigma to atm (1 atm = 1.01325e6 dyne/cm^2)
        atm_per_dyne_cm2 = 1.0 / 1.01325E6
        
        # sigma_hat = Lambda * sigma (units of pressure)
        # sigma is dyne/cm. Lambda is 1/cm. Lambda*sigma is dyne/cm^2 (pressure)
        self.sigma_hat_atm = self.Lambda_scale_factor_cm_neg1 * self.sigma_surface_tension_dyne_cm * atm_per_dyne_cm2

        # sigma_c_hat = Lambda * sigma_c_unscaled
        # sigma_c_unscaled = (sigma_c_factor) * sigma_surface_tension_dyne_cm
        sigma_c_unscaled_dyne_cm = self.sigma_c_crumbling_compression_factor_unscaled * self.sigma_surface_tension_dyne_cm
        self.sigma_c_hat_atm = self.Lambda_scale_factor_cm_neg1 * sigma_c_unscaled_dyne_cm * atm_per_dyne_cm2

        # K_hat_k = 3 * Lambda^2 * K_k = 3 * Lambda^2 * D_t_k * alpha_t_k
        # Units: Lambda (cm^-1), D_t_k (cm^2/min), alpha_t_k (ml_gas/ml_tissue/atm)
        # K_hat_k units should be (1/min)
        # The alpha_t_k (ml_gas/ml_tissue/atm) is dimensionless if we consider partial pressure normalized by 1 atm.
        # Or, it's a conversion factor. Let's treat it as dimensionless for K_hat calculation structure.
        # K_k in B.1 has units of permeability (e.g. cm^2/(min*atm) if pt-Pb is in atm).
        # K_hat (tilde K in B.2) is 3*Lambda^2*K, units 1/min.
        # So K must have units like length^2 / (time * pressure_dim) / Lambda^2_dim ? No.
        # K in A.2 is permeability = solubility * diffusivity.
        # D_t_O2 (cm^2/min), alpha_t_O2 (ml/ml/atm - treat as dimensionless for combination with D)
        # K_O2_unscaled = self.D_t_O2_cm2_min * self.alpha_t_O2_ml_ml_atm (cm^2/min/atm if alpha is ratio)
        # K_O2_unscaled = self.D_t_O2_cm2_min * self.alpha_t_O2_ml_ml_atm (cm^2/min if alpha is dimensionless solubility)
        # Let's assume alpha_t_k is Ostwald coefficient (dimensionless). Then K_k = D_t_k.
        # But table lists alpha_t_O2 with units including atm^-1.
        # Let's assume alpha_t_k is Henry's Law solubility constant C_tissue = alpha_t * P_gas_tissue
        # And K (permeability in A.2, B.1) is D_t * alpha_t (where alpha_t is solubility in tissue medium, not blood)
        # Units of K: cm^2/min * (ml_gas/ml_tissue/atm).
        # Units of K_hat (K_bar in C tables): 3 * Lambda^2 * K = (cm^-2) * (cm^2/min * ml/ml/atm) = 1/min * (ml/ml/atm)
        # This means the (pt-Pb) term in B.1 implicitly handles the pressure unit.
        # So, K_hat_k = 3 * (self.Lambda_scale_factor_cm_neg1**2) * D_t_k_cm2_min * alpha_t_k_ml_ml_atm
        
        alpha_t_N2_ml_ml_atm = self.K_alpha_N2_solubility_factor * self.alpha_t_O2_ml_ml_atm
        D_t_N2_cm2_min = self.K_D_N2_diffusivity_factor * self.D_t_O2_cm2_min

        self.K_hat_O2_per_min = 3 * (self.Lambda_scale_factor_cm_neg1**2) * self.D_t_O2_cm2_min * self.alpha_t_O2_ml_ml_atm
        self.K_hat_N2_per_min = 3 * (self.Lambda_scale_factor_cm_neg1**2) * D_t_N2_cm2_min * alpha_t_N2_ml_ml_atm
        
        # V_hat_t = V_total_compartment_ml * (Lambda_cm^-1)^3 (assuming 1ml = 1cm^3)
        self.V_hat_t_scaled_dimensionless = self.V_total_compartment_ml * (self.Lambda_scale_factor_cm_neg1**3)

        # beta0_hat = beta0_unscaled_cm * Lambda_cm^-1
        self.beta0_hat_initial_nuclei_slope_dimensionless = self.beta0_initial_nuclei_slope_unscaled_cm * self.Lambda_scale_factor_cm_neg1


# --- Model State ---
@dataclass
class ModelState:
    """Holds the dynamic state of the 3RUT-MBe1 model at a given time step."""
    t_min: float = 0.0                         # Current time (minutes)
    P_amb_atm: float = 1.0                     # Current ambient pressure (atm)
    FIO2: float = 0.209                        # Current inspired O2 fraction
    FIN2: float = 0.791                        # Current inspired N2 fraction
    I_ex_L_min_wb: float = 0.0                 # Current exercise intensity (Whole Body V_O2_wb - V_O2_wb_rest)

    # Tissue gas partial pressures (atm)
    pt_N2_atm: float = 0.0
    pt_O2_atm: float = 0.0

    # Bubble properties
    r_hat_dimensionless: float = 0.0           # Scaled bubble radius
    Pb_N2_atm: float = 0.0                     # Partial pressure of N2 in bubble (atm)
    Pb_O2_atm: float = 0.0                     # Partial pressure of O2 in bubble (atm)
    
    # Gas contents (scaled, P_bk * r_hat^3)
    x_hat_N2: float = 0.0
    x_hat_O2: float = 0.0
    
    # Nucleation and bubble number
    n_b: float = 0.0                           # Number of bubbles in compartment (can be fractional)
    N_b_max_cumulative: float = 0.0            # Cumulative max number of nuclei ever recruited
    P_crush_atm: float = 0.0                   # Current crush pressure (atm)
    beta_f_hat_dimensionless: float = 0.0      # Current scaled slope factor for nuclei distribution
    r_hat_min_nucleation_dimensionless: float = 0.0 # Scaled minimum radius for nucleation at current Pss, beta_f_hat

    # Compartmental physiological state
    # Q_dot_n_ml_per_ml_tissue_per_min: float # Current compartmental blood flow per unit tissue volume
    # V_dot_O2_n_ml_O2_per_ml_tissue_per_min: float # Current compartmental O2 consumption per unit tissue volume
    # These will be calculated per step based on I_ex and parameters

    # Hazard and DCS Probability
    h_t_hazard_per_min: float = 0.0            # Instantaneous hazard rate (1/min)
    P_DCS: float = 0.0                         # Cumulative probability of DCS
    P_survival: float = 1.0                    # Cumulative probability of no DCS (P(0))


# --- Model Class ---
class RutMbe1Model:
    """
    Implements the 3RUT-MBe1 model for predicting Altitude Decompression Sickness.
    Based on NEDU TR 18-01, Appendices A, B, C, D.
    """
    def __init__(self, params: ModelParameters):
        self.params = params
        self.P_infinity_atm = self.params.P_infinity_mmHg / 760.0 # Convert to atm

        # Constants for Lobdell's SO2 equation (footnote d, Appendix C)
        self.lobdell_a1: float = 0.34332
        self.lobdell_a2: float = 0.64073
        self.lobdell_b1: float = 0.34128
        self.lobdell_b2: float = 0.64073 # Note: b2 = a2 in the doc text, but table has 0.0.64073. Using 0.64073
        self.lobdell_eta: float = 1.58678
        self.lobdell_p_half_mmHg: float = 25.0
        self.Hb_c_ml_O2_per_ml_blood: float = 0.20 # O2 carrying capacity of hemoglobin

        # Initial state will be set by a dedicated method
        self.current_state: Optional[ModelState] = None
        self.P_crush_initial_atm_for_decay: float = 0.0 # Store P_o_crush for C.5 decay logic

    def _mmhg_to_atm(self, pressure_mmhg: float) -> float:
        return pressure_mmhg / 760.0

    def _atm_to_mmhg(self, pressure_atm: float) -> float:
        return pressure_atm * 760.0

    def _calculate_arterial_gas_pressure_k_atm(self, P_amb_atm: float, FI_k: float) -> float:
        """ Implements Eq. C.28 for inert gas k. """
        P_A_H2O_atm = self.params.P_H2O_mmHg / 760.0
        P_A_CO2_atm = self.params.pt_CO2_tissue_mmHg / 760.0 # Assuming Alveolar CO2 = tissue CO2 for this
        
        # (Pamb - P_AH2O) - P_ACO2 * (1 - 1/RQ)
        term1 = P_amb_atm - P_A_H2O_atm
        term2 = P_A_CO2_atm * (1.0 - (1.0 / self.params.RQ_respiratory_quotient))
        return FI_k * (term1 - term2)

    def _calculate_arterial_O2_pressure_atm(self, P_amb_atm: float, sum_p_a_inert_k_atm: float) -> float:
        """ Implements Eq. C.37. """
        P_A_H2O_atm = self.params.P_H2O_mmHg / 760.0
        P_A_CO2_atm = self.params.pt_CO2_tissue_mmHg / 760.0 # Assuming Alveolar CO2 = tissue CO2
        return P_amb_atm - P_A_H2O_atm - P_A_CO2_atm - sum_p_a_inert_k_atm

    def _calculate_SO2(self, pO2_mmHg: float) -> float:
        """ Implements Lobdell's equation for Hemoglobin O2 saturation (footnote d, Appendix C). """
        if pO2_mmHg <= 0: return 0.0
        
        p_lob = (pO2_mmHg / self.lobdell_p_half_mmHg)**self.lobdell_eta
        
        numerator = self.lobdell_a1 * p_lob + self.lobdell_a2 * (p_lob**2)
        denominator = 1.0 + self.lobdell_b1 * p_lob + self.lobdell_b2 * (p_lob**2)
        if denominator == 0: return 1.0 # Avoid division by zero, assume full saturation if somehow
        return min(max(numerator / denominator, 0.0), 1.0) # Clamp between 0 and 1

    def _calculate_blood_O2_content_ml_per_ml(self, pO2_atm: float) -> float:
        """ Combines dissolved O2 and Hb-bound O2. Uses C.38/C.39 structure. """
        pO2_mmHg = self._atm_to_mmhg(pO2_atm)
        dissolved_O2 = self.params.alpha_b_O2_ml_ml_atm * pO2_atm # alpha_b_O2 is per atm
        hb_bound_O2 = self.Hb_c_ml_O2_per_ml_blood * self._calculate_SO2(pO2_mmHg)
        return dissolved_O2 + hb_bound_O2

    def _calculate_alpha_prime_O2_ml_per_ml_per_atm(self, p_vO2_atm_n: float) -> float:
        """
        Implements Eq. C.31: slope of the whole blood O2 solubility curve.
        p_vO2_atm_n: O2 partial pressure in mixed venous blood (atm) at step n.
        Returns slope in (ml_O2/ml_blood) / atm.
        """
        if p_vO2_atm_n <= 0: # Avoid issues with p_lob at zero or negative pO2
            # At very low pO2, the curve is steep. Return a highish, positive slope.
            # Or approximate with a small positive pO2.
            # For simplicity, let's use a small positive value to avoid log(0) or division by zero in p_lob.
             p_vO2_mmHg_n = 0.1
        else:
            p_vO2_mmHg_n = self._atm_to_mmhg(p_vO2_atm_n)

        p_lob = (p_vO2_mmHg_n / self.lobdell_p_half_mmHg)**self.lobdell_eta
        
        # Numerator of dS/dp term in C.31's Hb_c part
        # [a1 + 2*a2*p - a2*(a1 - b1*p^2)] -- typo in doc, should be a2(a1*p - b1*p^2) or similar?
        # The formula in B.50 is: a1 + 2a2p - a2(a1 - b1)p^2. Let's use B.50.
        # B.50 numerator: a1 + 2*a2*p - (a1*b2 - 2*a2*b1)*p^2 - 2*a2*b2*p^3 ? No, that's too complex from derivation.
        # Let's re-derive dS/dp from S = (a1p + a2p^2)/(1+b1p+b2p^2)
        # dS/dp = [ (a1+2a2p)(1+b1p+b2p^2) - (a1p+a2p^2)(b1+2b2p) ] / (1+b1p+b2p^2)^2
        # Numerator: a1 + a1b1p + a1b2p^2 + 2a2p + 2a2b1p^2 + 2a2b2p^3
        #            - (a1b1p + 2a1b2p^2 + a2b1p^2 + 2a2b2p^3)
        #          = a1 + (a1b2 - 2a1b2)p^2 + 2a2p + (2a2b1 - a2b1)p^2
        #          = a1 + 2a2p + (a2b1 - a1b2)p^2
        # This is the form used in other implementations (e.g. Gerth and Vann 1997)
        
        dS_dp_numerator = self.lobdell_a1 + 2 * self.lobdell_a2 * p_lob + \
                          (self.lobdell_a2 * self.lobdell_b1 - self.lobdell_a1 * self.lobdell_b2) * (p_lob**2)
        
        dS_dp_denominator = (1.0 + self.lobdell_b1 * p_lob + self.lobdell_b2 * (p_lob**2))**2
        if dS_dp_denominator == 0: dS_dp = 0 # Avoid division by zero
        else: dS_dp = dS_dp_numerator / dS_dp_denominator
            
        # dp/dPO2 term: (eta * p^(eta-1)) / P_half
        if p_vO2_mmHg_n <= 0: dp_dPO2_mmHg = 0 # Avoid issues if p_vO2_mmHg_n is zero
        else:
            # p_lob is p_norm^eta. p_norm = pO2/P_half.
            # dp_lob / d_pO2_mmHg = eta * ( (pO2/P_half)^(eta-1) ) * (1/P_half)
            #                  = eta * p_lob / pO2_mmHg_n if eta != 0 and pO2 != 0
            #                  = (self.lobdell_eta / p_vO2_mmHg_n) * p_lob if p_vO2_mmHg_n is not 0
            dp_dPO2_mmHg = (self.lobdell_eta * (p_lob / p_vO2_mmHg_n)) if p_vO2_mmHg_n != 0 else 0


        # alpha_prime_O2 = alpha_b_O2 (per atm) + Hb_c * dS/dPO2 (dimensionless / mmHg) * (1 atm / 760 mmHg)
        # dS/dPO2_atm = dS/dPO2_mmHg * 760
        # So dS/dPO2_mmHg = dS_dp * dp_dPO2_mmHg
        dS_dPO2_mmHg = dS_dp * dp_dPO2_mmHg

        # alpha_prime_O2_n is in (ml_O2/ml_blood)/atm
        # self.params.alpha_b_O2_ml_ml_atm is already per atm.
        # Hb_c * dS/dPO2_mmHg needs to be converted to per atm.
        # dS/dPO2_mmHg has units of (1/mmHg). So Hb_c * dS/dPO2_mmHg has units (ml_O2/ml_blood)/mmHg.
        # To convert to per atm: multiply by 760 mmHg/atm.
        
        alpha_prime_O2_n = self.params.alpha_b_O2_ml_ml_atm + \
                             self.Hb_c_ml_O2_per_ml_blood * dS_dPO2_mmHg * 760.0
        
        return max(alpha_prime_O2_n, 1e-9) # Ensure it's a small positive number

    def initialize_state(self, initial_P_amb_atm: float, initial_FIO2: float, initial_FIN2: float, initial_I_ex: float = 0.0):
        """Initializes the model state for t=0."""
        
        self.current_state = ModelState(
            P_amb_atm=initial_P_amb_atm,
            FIO2=initial_FIO2,
            FIN2=initial_FIN2,
            I_ex_L_min_wb=initial_I_ex
        )

        # 1. Initial Arterial Gas Pressures
        pa_N2_initial_atm = self._calculate_arterial_gas_pressure_k_atm(
            initial_P_amb_atm, initial_FIN2
        )
        # For O2, sum_p_a_inert_k is just pa_N2 here
        pa_O2_initial_atm = self._calculate_arterial_O2_pressure_atm(
            initial_P_amb_atm, pa_N2_initial_atm
        )

        # 2. Initial Tissue Gas Tensions (Footnote c, e Appendix C)
        # Inert gas (N2): pt_N2_0 = pa_N2_0
        self.current_state.pt_N2_atm = pa_N2_initial_atm

        # Oxygen: pt_O2_0 = pv_O2_0. Need initial Q0 and V_O2_0
        # V_O2_0 (compartmental) = m_V_O2 * Iex_0 + V_O2_rest_compartmental
        V_O2_compartmental_0 = self.params.m_V_O2_slope_vs_Iex * initial_I_ex + \
                               self.params.V_O2_rest_compartmental_ml_per_ml_tissue_per_min
        
        # Q_dot_0 (compartmental, per unit tissue volume)
        # Q_dot_ex_0 = m_Q * (V_O2_comp_0 - V_O2_rest_comp) + Q_dot_rest_comp
        # Q_dot_rest_comp = Q_total_comp_rest / V_total_comp
        Q_dot_rest_compartmental = self.params.Q_total_compartment_rest_ml_min / self.params.V_total_compartment_ml
        
        Q_dot_compartmental_0 = self.params.m_Q_slope_vs_V_O2 * \
                                (V_O2_compartmental_0 - self.params.V_O2_rest_compartmental_ml_per_ml_tissue_per_min) + \
                                Q_dot_rest_compartmental
        
        # C_aO2_0
        C_aO2_0_ml_per_ml = self._calculate_blood_O2_content_ml_per_ml(pa_O2_initial_atm)
        
        # C_vO2_0 = C_aO2_0 - (V_O2_compartmental_0 / Q_dot_compartmental_0) (if V_O2 is per tissue vol, Q_dot is per tissue vol)
        # V_O2_comp_0 units: ml_O2/ml_tissue/min
        # Q_dot_comp_0 units: ml_blood/ml_tissue/min
        # Ratio units: ml_O2/ml_blood
        if Q_dot_compartmental_0 == 0: # Avoid division by zero if no blood flow
            C_vO2_0_ml_per_ml = 0.0 
        else:
            C_vO2_0_ml_per_ml = C_aO2_0_ml_per_ml - (V_O2_compartmental_0 / Q_dot_compartmental_0)
        C_vO2_0_ml_per_ml = max(C_vO2_0_ml_per_ml, 0.0) # Content cannot be negative

        # Numerically invert C_vO2_0 to get p_vO2_0 (which is pt_O2_0)
        # This requires an iterative solver or a lookup. For now, a simple search.
        pt_O2_initial_atm_search = 0.0
        min_diff = float('inf')
        # Search for pO2_atm that gives C_vO2_0_ml_per_ml
        for p_test_atm in [i * 0.001 for i in range(1, 250)]: # Test 0.001 to 0.25 atm
            c_test = self._calculate_blood_O2_content_ml_per_ml(p_test_atm)
            diff = abs(c_test - C_vO2_0_ml_per_ml)
            if diff < min_diff:
                min_diff = diff
                pt_O2_initial_atm_search = p_test_atm
            if diff < 1e-5 : break # Close enough
        self.current_state.pt_O2_atm = pt_O2_initial_atm_search

        # 3. Initial P_crush_0 (Footnote b, Appendix C)
        # P_crush_0 = (P_amb_0 - P_inf) - sum(ptk_0)
        sum_ptk_0_atm = self.current_state.pt_N2_atm + self.current_state.pt_O2_atm
        self.current_state.P_crush_atm = (initial_P_amb_atm - self.P_infinity_atm) - sum_ptk_0_atm
        # Pcrush should not be negative (it's a compression effect)
        self.current_state.P_crush_atm = max(0.0, self.current_state.P_crush_atm)
        self.P_crush_initial_atm_for_decay = self.current_state.P_crush_atm # Store P_o_crush for C.5

        # 4. Initial Bubble Number and Radii
        self.current_state.n_b = 0.0 # Or self.params.N_min_b_nuclei_threshold if allowing initial nuclei
        self.current_state.N_b_max_cumulative = self.current_state.n_b
        
        # beta_f_hat_0 from C.6 (depends on P_crush_0)
        # r_hat_o_min_dimensionless = beta0_hat * [ln(N0_b) - ln(N_min_b)]
        # Ensure N0_b > N_min_b
        if self.params.N0_b_total_nuclei_unscaled <= self.params.N_min_b_nuclei_threshold:
            # This would lead to log errors or non-positive r_hat_o_min.
            # Set a sensible small r_hat_o_min or handle this case.
            # For now, let's assume N0_b is always greater.
             # Or if N0_b_total_nuclei_unscaled is small, then maybe no nuclei can form.
            r_hat_o_min_num = math.log(self.params.N0_b_total_nuclei_unscaled) - math.log(self.params.N_min_b_nuclei_threshold)
            if r_hat_o_min_num <=0: # Avoid issues if N0_b <= N_min_b
                 r_hat_o_min_dimensionless = 1e-9 # a very small number
            else:
                 r_hat_o_min_dimensionless = self.params.beta0_hat_initial_nuclei_slope_dimensionless * r_hat_o_min_num
        else:
            r_hat_o_min_dimensionless = self.params.beta0_hat_initial_nuclei_slope_dimensionless * \
                (math.log(self.params.N0_b_total_nuclei_unscaled) - math.log(self.params.N_min_b_nuclei_threshold))


        beta_ex_0 = 1.0 + self.params.m_beta_ex_nucleation_exercise_factor * initial_I_ex # C.3
        
        beta_f_hat_0_numerator = 2 * self.params.sigma_c_hat_atm * self.params.beta0_hat_initial_nuclei_slope_dimensionless
        beta_f_hat_0_denominator = 2 * (self.params.sigma_c_hat_atm - self.params.sigma_hat_atm) + \
                                   self.current_state.P_crush_atm * r_hat_o_min_dimensionless
        if beta_f_hat_0_denominator == 0: # Avoid division by zero
            self.current_state.beta_f_hat_dimensionless = 0.0
        else:
            self.current_state.beta_f_hat_dimensionless = beta_ex_0 * (beta_f_hat_0_numerator / beta_f_hat_0_denominator) # C.6

        # Initial r_hat_dimensionless: If n_b is 0, this is not well-defined for an existing bubble.
        # Could be r_hat_min_nucleation for the *next* step if supersaturation occurs.
        # Let's set it to a very small number or based on N_min_b threshold if needed.
        # If no bubbles, r_hat is not really a state variable for an *existing* bubble.
        # C.10 is r_min_n for nucleation threshold, not necessarily current r_hat if nb=0.
        self.current_state.r_hat_dimensionless = 1e-9 # Placeholder if no bubbles
        self.current_state.Pb_N2_atm = 0.0
        self.current_state.Pb_O2_atm = 0.0
        self.current_state.x_hat_N2 = 0.0
        self.current_state.x_hat_O2 = 0.0

        # Hazard and P_DCS
        self.current_state.h_t_hazard_per_min = 0.0
        self.current_state.P_DCS = 0.0
        self.current_state.P_survival = 1.0
        
        # print(f"Initial State: {self.current_state}")
        # print(f"Params: P_inf_atm={self.P_infinity_atm}, sigma_hat={self.params.sigma_hat_atm}, K_O2_hat={self.params.K_hat_O2_per_min}")


    def run_profile(self, profile_segments: List[ProfileSegment], delta_t_min: float) -> List[ModelState]:
        """
        Runs the simulation for a given exposure profile.
        profile_segments: A list of ProfileSegment objects.
        delta_t_min: Time step for the simulation.
        Returns a list of ModelState objects representing the history of the simulation.
        """
        if not profile_segments:
            return []

        # Initialize state based on the start of the first segment or a predefined sea-level air condition
        # For now, assume profile starts from a defined initial condition (e.g. 1 ATA air at rest)
        # The `initialize_state` should be called before `run_profile` if specific start needed, 
        # or we can initialize here based on first segment.
        
        # Let's assume the model is initialized *before* calling run_profile to the t=0 state.
        # If not initialized, we could use the first segment's start, but that might miss pre-profile saturation.
        if not self.current_state:
             # Initialize to conditions of the very start of the first segment if not already done.
             # This assumes the model starts *at* the beginning of the first segment, already saturated to its conditions if it were prolonged.
             print("Warning: Model not pre-initialized. Initializing to start of first profile segment.")
             first_seg = profile_segments[0]
             self.initialize_state( # This sets t=0
                 initial_P_amb_atm=first_seg.P_amb_atm, 
                 initial_FIO2=first_seg.FIO2, 
                 initial_FIN2=first_seg.FIN2, 
                 initial_I_ex=first_seg.I_ex_L_min_wb
             )
        
        history: List[ModelState] = [self.current_state] # type: ignore[list-item]
        
        current_sim_time_min = self.current_state.t_min # Should be 0 if initialized for profile start

        for segment_idx, segment in enumerate(profile_segments):
            segment_end_time = current_sim_time_min + segment.duration_min
            # print(f"Running Segment {segment_idx+1}: duration={segment.duration_min}, Pamb={segment.P_amb_atm}, FIO2={segment.FIO2}, Iex={segment.I_ex_L_min_wb}")

            num_steps_in_segment = math.ceil(segment.duration_min / delta_t_min)
            actual_dt_this_segment = segment.duration_min / num_steps_in_segment if num_steps_in_segment > 0 else 0

            if actual_dt_this_segment == 0 and segment.duration_min > 0:
                # Handle case where duration is smaller than delta_t_min - take one step for the full duration
                num_steps_in_segment = 1
                actual_dt_this_segment = segment.duration_min
            elif segment.duration_min == 0: # Skip zero-duration segments
                continue

            for step in range(num_steps_in_segment):
                # Conditions for this step are those of the current segment
                self._advance_state_one_step(
                    delta_t_min=actual_dt_this_segment,
                    next_P_amb_atm=segment.P_amb_atm,
                    next_FIO2=segment.FIO2,
                    next_FIN2=segment.FIN2,
                    next_I_ex=segment.I_ex_L_min_wb
                )
                history.append(self.current_state) # type: ignore[list-item]
            
            # Ensure simulation time aligns with segment end after loop
            current_sim_time_min = segment_end_time 
            if self.current_state:
                 self.current_state.t_min = current_sim_time_min # Correct slight float inaccuracies

        return history

    def _advance_state_one_step(self, delta_t_min: float, next_P_amb_atm: float, next_FIO2: float, next_FIN2: float, next_I_ex: float):
        """
        Advances the model state by one time step (delta_t_min) using recursive equations from Appendix C.
        Assumes current_state is populated for step 'n'. Calculates state for 'n+1'.
        next_P_amb_atm, etc., are the conditions prevailing *during* the interval from tn to tn+1,
        or at tn+1 if they change stepwise. For P_amb_n+1 in C.16, it's the pressure at end of step.
        """
        if not self.current_state:
            raise ValueError("Model state not initialized. Call initialize_state() first.")

        s = self.current_state
        p = self.params
        
        # --- Current conditions at start of step 'n' (from s.xxx) ---
        # P_amb_n = s.P_amb_atm (will be updated to next_P_amb_atm at end of step for P_amb_n+1 in C.16)
        # FIO2_n = s.FIO2
        # FIN2_n = s.FIN2
        # I_ex_n = s.I_ex_L_min_wb (exercise during this interval leading to state at n+1)
        
        # --- Conditions for the interval [tn, tn+1] or at tn+1 ---
        # These are 'next_...' inputs, representing conditions for the *current* step being calculated
        # P_amb_n_plus_1_for_bubble_eq = next_P_amb_atm # For C.16
        # FIO2_n_plus_1 = next_FIO2 # For C.28, C.37 (arterial pressures at n+1)
        # FIN2_n_plus_1 = next_FIN2
        # I_ex_n_for_current_step = next_I_ex # Exercise level during current step

        # Store state for n+1
        next_s = ModelState()
        next_s.t_min = s.t_min + delta_t_min
        next_s.P_amb_atm = next_P_amb_atm # This becomes P_amb_n for *next* iteration, or P_amb_n+1 for *current* C.16
        next_s.FIO2 = next_FIO2
        next_s.FIN2 = next_FIN2
        next_s.I_ex_L_min_wb = next_I_ex


        # --- 0. Determine current physiological parameters based on next_I_ex ---
        V_O2_compartmental_n = p.m_V_O2_slope_vs_Iex * next_I_ex + \
                               p.V_O2_rest_compartmental_ml_per_ml_tissue_per_min
        
        Q_dot_rest_compartmental = p.Q_total_compartment_rest_ml_min / p.V_total_compartment_ml
        
        Q_dot_compartmental_n = p.m_Q_slope_vs_V_O2 * \
                                 (V_O2_compartmental_n - p.V_O2_rest_compartmental_ml_per_ml_tissue_per_min) + \
                                 Q_dot_rest_compartmental
        Q_dot_compartmental_n = max(1e-9, Q_dot_compartmental_n) # Avoid zero flow

        # --- 1. Bubble Number (Eqs. C.3 - C.11) ---
        # C.3: beta_ex_n
        beta_ex_n = 1.0 + p.m_beta_ex_nucleation_exercise_factor * next_I_ex # Use I_ex for current interval

        # C.4: P_crush_n
        # P_crush_n = MAX[P_crush_{n-1}, (P_amb_n - P_inf) - sum(ptk_n)]
        # s.P_crush_atm is P_crush_{n-1}
        # s.P_amb_atm is P_amb_n
        # s.pt_N2_atm, s.pt_O2_atm are ptk_n
        sum_ptk_n_atm = s.pt_N2_atm + s.pt_O2_atm
        P_crush_candidate_atm = (s.P_amb_atm - self.P_infinity_atm) - sum_ptk_n_atm
        P_crush_n_atm = max(s.P_crush_atm, P_crush_candidate_atm)
        P_crush_n_atm = max(0.0, P_crush_n_atm) # Ensure non-negative

        # C.5: P_crush decay
        if P_crush_n_atm <= s.P_crush_atm : # If Pcrush is not increasing due to new compression
            P_crush_n_atm = self.P_crush_initial_atm_for_decay + \
                            (s.P_crush_atm - self.P_crush_initial_atm_for_decay) * \
                            math.exp(-delta_t_min / p.P_crush_decay_time_constant_min)
        else: # Pcrush increased or stayed same due to active compression
            self.P_crush_initial_atm_for_decay = P_crush_n_atm # Reset decay origin

        next_s.P_crush_atm = P_crush_n_atm
        
        # C.6: beta_f_hat_n, r_hat_o_min
        r_hat_o_min_num = math.log(p.N0_b_total_nuclei_unscaled) - math.log(p.N_min_b_nuclei_threshold)
        if r_hat_o_min_num <= 0: r_hat_o_min_dimensionless = 1e-9
        else: r_hat_o_min_dimensionless = p.beta0_hat_initial_nuclei_slope_dimensionless * r_hat_o_min_num

        beta_f_hat_n_numerator = 2 * p.sigma_c_hat_atm * p.beta0_hat_initial_nuclei_slope_dimensionless
        beta_f_hat_n_denominator = 2 * (p.sigma_c_hat_atm - p.sigma_hat_atm) + \
                                   P_crush_n_atm * r_hat_o_min_dimensionless
        if beta_f_hat_n_denominator == 0 or beta_f_hat_n_denominator < 1e-9: # Avoid division by zero or extreme values
            beta_f_hat_n = 0.0
        else:
            beta_f_hat_n = beta_ex_n * (beta_f_hat_n_numerator / beta_f_hat_n_denominator)
        next_s.beta_f_hat_dimensionless = beta_f_hat_n

        # C.7: P_ss_n (Supersaturation at start of step 'n')
        # Uses P_amb_n (s.P_amb_atm) and p_tk_n (s.pt_N2_atm, s.pt_O2_atm)
        P_ss_n_atm = (sum_ptk_n_atm + self.P_infinity_atm) - s.P_amb_atm
        
        # C.8: N_b_max,n
        # N_b_max_n = MAX[N_b_max_{n-1}, N0_b * exp(-2*sigma_hat / (P_ss_n * beta_f_hat_n))]
        # s.N_b_max_cumulative is N_b_max_{n-1}
        N_b_max_n = s.N_b_max_cumulative
        if P_ss_n_atm > 0 and beta_f_hat_n > 1e-9: # Only nucleate if supersaturated and beta_f is valid
            exponent_val = - (2 * p.sigma_hat_atm) / (P_ss_n_atm * beta_f_hat_n)
            # Protect against overly large negative exponent leading to underflow for exp
            if exponent_val < -700: # exp(-700) is ~0
                 N_b_candidate = 0.0
            else:
                 N_b_candidate = p.N0_b_total_nuclei_unscaled * math.exp(exponent_val)
            N_b_max_n = max(s.N_b_max_cumulative, N_b_candidate)
        next_s.N_b_max_cumulative = N_b_max_n
        
        # C.9: delta_n_b_n, n_b_n
        # delta_n_b is number of *newly* recruited bubbles this step
        delta_n_b_n = N_b_max_n - s.N_b_max_cumulative # Can be 0 if no new nuclei recruited
        delta_n_b_n = max(0, delta_n_b_n) # ensure not negative due to float precision
        
        n_b_n = s.n_b + delta_n_b_n # Current bubble number for this step's calculations
        next_s.n_b = n_b_n # This will be n_b_{n+1} after VGE

        # C.10: r_hat_min_n (nucleation threshold radius for *this* step's conditions)
        # This is the size of newly recruited nuclei IF P_ss_n > 0
        log_term_r_min = math.log(p.N0_b_total_nuclei_unscaled) - math.log(p.N_min_b_nuclei_threshold)
        if log_term_r_min <=0: next_s.r_hat_min_nucleation_dimensionless = 1e-9
        else: next_s.r_hat_min_nucleation_dimensionless = beta_f_hat_n * log_term_r_min
        
        # C.11: x_hat_o_k_n (initial gas content of newly recruited bubbles)
        # This is (P_bk_n_at_nucleation_of_new_bubble * r_hat_min_n^3)
        # P_bk at nucleation of *new* bubble. Assume new bubbles form in equilibrium with current tissue gas?
        # Or, use current P_bk from existing bubbles if delta_n_b_n > 0 and s.n_b > 0?
        # The paper implies (Section 8.3.1) new bubbles attain size of existing ones.
        # Appendix A.5 (initial P_bk_0) for *first* bubble.
        # For now, if new bubbles (delta_n_b_n > 0), they adopt current P_bk of *existing* bubbles (s.Pb_N2_atm, s.Pb_O2_atm)
        # and current r_hat (s.r_hat_dimensionless) or r_hat_min_n if no existing bubbles?
        # "Maintenance of mass balance in this approach requires a change in bubble gas content and a resultant
        # adjustment in tissue gas tension corresponding to the difference between the nucleonic volume
        # and the prevailing bubble volume whenever a nucleus is 'recruited'" (Appendix B, start of 9.2.2)
        # x_hat_o_k_n in C.30/C.44 is content of the delta_n_b_n new bubbles *at their nucleonic size* (r_hat_min_n).
        # P_bk_n in C.11 is pressure in that nucleonic bubble. Assume this P_bk_n is total diffusable pressure at nucleation conditions.
        # Let's use P_amb_n - P_inf + 2*sigma_hat/r_hat_min_n + M_hat*r_hat_min_n^3
        # And assume gas fractions are same as tissue gas fractions at nucleation.
        
        x_hat_o_N2_n = 0.0
        x_hat_o_O2_n = 0.0
        if delta_n_b_n > 0:
            r_nuc_hat = next_s.r_hat_min_nucleation_dimensionless
            if r_nuc_hat > 1e-9 : # if nucleating radius is valid
                P_total_diffusible_in_nucleonic_bubble = (s.P_amb_atm - self.P_infinity_atm) + \
                                                         (2 * p.sigma_hat_atm / r_nuc_hat) + \
                                                         (p.M_elastic_modulus_scaled_atm * (r_nuc_hat**3))
                P_total_diffusible_in_nucleonic_bubble = max(0, P_total_diffusible_in_nucleonic_bubble)

                # Assume gas fractions in new nuclei are proportional to current tissue partial pressures
                if sum_ptk_n_atm > 1e-9:
                    frac_N2_tissue = s.pt_N2_atm / sum_ptk_n_atm
                    frac_O2_tissue = s.pt_O2_atm / sum_ptk_n_atm
                else: # Avoid division by zero if no tissue gas
                    frac_N2_tissue = 0.5 
                    frac_O2_tissue = 0.5
                
                Pb_N2_at_nucleation = P_total_diffusible_in_nucleonic_bubble * frac_N2_tissue
                Pb_O2_at_nucleation = P_total_diffusible_in_nucleonic_bubble * frac_O2_tissue

                x_hat_o_N2_n = Pb_N2_at_nucleation * (r_nuc_hat**3)
                x_hat_o_O2_n = Pb_O2_at_nucleation * (r_nuc_hat**3)


        # --- 2. Bubble Radius and Pressure (C.12 - C.18) ---
        # Only proceed if there are bubbles (n_b_n > 0)
        # And if r_hat_n (s.r_hat_dimensionless) is sensible. If it's first bubble, use r_hat_min_n?
        # "Before bubble nucleation... bubble was assumed to remain stable at its nucleus size" (A.52 context)
        # If s.n_b was 0 and delta_n_b_n > 0, then current r_hat for calculation should be r_hat_min_n.
        
        r_hat_n_current_calc = s.r_hat_dimensionless
        if s.n_b == 0 and delta_n_b_n > 0: # First bubble(s) forming this step
            r_hat_n_current_calc = next_s.r_hat_min_nucleation_dimensionless
            # Also need to initialize Pb_k_n for this first bubble.
            # Assume it starts with the nucleonic pressures calculated for x_hat_o_k_n
            s.Pb_N2_atm = Pb_N2_at_nucleation if delta_n_b_n > 0 else 0.0
            s.Pb_O2_atm = Pb_O2_at_nucleation if delta_n_b_n > 0 else 0.0


        if n_b_n > 1e-9 and r_hat_n_current_calc > 1e-9 :
            # For N2
            b_N2_n = p.K_hat_N2_per_min * delta_t_min / (r_hat_n_current_calc**2)
            a_N2_n = (1 + r_hat_n_current_calc) * b_N2_n
            A_N2_n = s.Pb_N2_atm + a_N2_n * (1 - a_N2_n / 2) * (s.pt_N2_atm - s.Pb_N2_atm)
            # Correcting C.15 for P_b_k,n (using s.Pb_N2_atm for N2)
            B_N2_n = 0.5 * ( (2 * a_N2_n - b_N2_n + a_N2_n * b_N2_n) * s.pt_N2_atm + \
                             (a_N2_n + b_N2_n) * (1 - a_N2_n) * s.Pb_N2_atm )

            # For O2
            b_O2_n = p.K_hat_O2_per_min * delta_t_min / (r_hat_n_current_calc**2)
            a_O2_n = (1 + r_hat_n_current_calc) * b_O2_n
            A_O2_n = s.Pb_O2_atm + a_O2_n * (1 - a_O2_n / 2) * (s.pt_O2_atm - s.Pb_O2_atm)
            # Correcting C.15 for P_b_k,n (using s.Pb_O2_atm for O2)
            B_O2_n = 0.5 * ( (2 * a_O2_n - b_O2_n + a_O2_n * b_O2_n) * s.pt_O2_atm + \
                             (a_O2_n + b_O2_n) * (1 - a_O2_n) * s.Pb_O2_atm )

            # C.16: delta_r_hat_n
            # P'_amb_n+1 is pressure at END of step (next_s.P_amb_atm)
            P_prime_amb_n_plus_1_atm = next_s.P_amb_atm - self.P_infinity_atm 
            
            # r_n for these terms is r_hat_n_current_calc
            term_2sigma_r = 2 * p.sigma_hat_atm / r_hat_n_current_calc 
            # M_hat is p.M_elastic_modulus_scaled_atm
            term_Mr3 = p.M_elastic_modulus_scaled_atm * (r_hat_n_current_calc**3)
            
            numerator_dr_hat = (A_N2_n + A_O2_n) - (P_prime_amb_n_plus_1_atm + term_2sigma_r + term_Mr3)
            denominator_dr_hat = (3 * (A_N2_n + A_O2_n) - (B_N2_n + B_O2_n)) - (term_2sigma_r - 3 * term_Mr3)

            delta_r_hat_n = 0.0
            if abs(denominator_dr_hat) > 1e-12: # Increased precision for check
                delta_r_hat_n = numerator_dr_hat / denominator_dr_hat
            else: # Denominator is zero or too small, implies equilibrium or problematic state
                # If numerator is also very small, effectively dr_hat = 0.
                # If numerator is large, this is an instability. For now, cap dr_hat.
                if abs(numerator_dr_hat) < 1e-9:
                    delta_r_hat_n = 0.0
                else:
                    # This case should be rare with small delta_t and limited changes.
                    # Potentially log a warning. For now, cap to avoid large jumps.
                    delta_r_hat_n = 0.1 * math.copysign(1, numerator_dr_hat) 

            # Limit delta_r_hat_n to prevent excessive changes per step, e.g., +/- 50% of r_hat_n is large
            # Let's make this limit smaller, e.g., 10-20% to maintain stability of approximations B.5-B.9
            max_frac_change = 0.10 # Max 10% change in radius per step
            delta_r_hat_n = min(max(delta_r_hat_n, -max_frac_change), max_frac_change) 

            # C.17: r_hat_n+1
            next_s.r_hat_dimensionless = r_hat_n_current_calc * (1 + delta_r_hat_n)
            
            if next_s.r_hat_dimensionless < 1e-9: # Bubble resolved or too small
                next_s.r_hat_dimensionless = 1e-9 # Keep it a tiny positive number for subsequent calcs if needed
                next_s.n_b = 0 # Bubble resolved, n_b will be set to 0
                n_b_n = 0 # Update local n_b_n for consistency in this step's calculations
                next_s.Pb_N2_atm = 0.0
                next_s.Pb_O2_atm = 0.0
                next_s.x_hat_N2 = 0.0
                next_s.x_hat_O2 = 0.0
            else:
                # C.18: P_b_k,n+1 (Corrected: use delta_r_hat_n)
                next_s.Pb_N2_atm = A_N2_n - (3 * A_N2_n - B_N2_n) * delta_r_hat_n
                next_s.Pb_O2_atm = A_O2_n - (3 * A_O2_n - B_O2_n) * delta_r_hat_n
                
                next_s.Pb_N2_atm = max(0, next_s.Pb_N2_atm)
                next_s.Pb_O2_atm = max(0, next_s.Pb_O2_atm)

        else: # No bubbles currently or r_hat is too small to be meaningful for existing bubble dynamics
            delta_r_hat_n = 0.0 
            # If r_hat_n_current_calc was already tiny (e.g. from init when nb=0), keep it tiny.
            # If it was a valid radius but n_b_n just became 0 (e.g. before this block), it should resolve.
            if n_b_n < 1e-9 : # If no bubbles, effectively radius is non-existent for dynamics
                 next_s.r_hat_dimensionless = 1e-9
            else: # Keep previous small radius if n_b_n was >0 but r_hat was already tiny
                 next_s.r_hat_dimensionless = r_hat_n_current_calc 
            
            next_s.Pb_N2_atm = 0.0 
            next_s.Pb_O2_atm = 0.0
            next_s.x_hat_N2 = 0.0 # Ensure gas content is zeroed if no bubble
            next_s.x_hat_O2 = 0.0


        # --- 3. Tissue Gas Tensions ---
        # Arterial pressures at t_n (s.FIO2, s.FIN2, s.P_amb_atm) and t_n+1 (next_s.FIO2, next_s.FIN2, next_s.P_amb_atm)
        # These are conditions at the START of the interval [tn, tn+1] for pa_k,n
        # and at the END of the interval [tn, tn+1] for pa_k,n+1
        pa_N2_n_atm = self._calculate_arterial_gas_pressure_k_atm(s.P_amb_atm, s.FIN2)
        # For pa_O2_n_atm, sum_p_a_inert_k is just pa_N2_n_atm here (single inert gas model)
        pa_O2_n_atm = self._calculate_arterial_O2_pressure_atm(s.P_amb_atm, pa_N2_n_atm)

        pa_N2_n_plus_1_atm = self._calculate_arterial_gas_pressure_k_atm(next_s.P_amb_atm, next_s.FIN2)
        pa_O2_n_plus_1_atm = self._calculate_arterial_O2_pressure_atm(next_s.P_amb_atm, pa_N2_n_plus_1_atm)

        # C.27 / C.36: x_hat_k,n+1 (Gas content in bubble at n+1)
        # This was calculated in the Bubble Radius/Pressure block and stored in next_s.x_hat_N2, next_s.x_hat_O2
        # Based on next_s.Pb_k_atm and next_s.r_hat_dimensionless.
        # Ensure it's done *after* Pb_k,n+1 and r_hat,n+1 are known, which it is.

        # --- Tissue Inert Gas (N2) - Eqs. C.23 to C.30 ---
        # Q_dot_compartmental_n is the flow per unit tissue volume for the current step duration
        alpha_t_N2_eff = p.K_alpha_N2_solubility_factor * p.alpha_t_O2_ml_ml_atm
        
        # tau_N2_n (C.23)
        # Q_n here is Q_dot_compartmental_n (ml_blood/ml_tissue/min)
        # alpha_tk / (alpha_bk * Q_n)
        if p.alpha_b_N2_ml_ml_atm * Q_dot_compartmental_n == 0:
            tau_N2_n = float('inf') # Effectively infinite time constant if no flow or no blood solubility
        else:
            tau_N2_n = alpha_t_N2_eff / (p.alpha_b_N2_ml_ml_atm * Q_dot_compartmental_n)
        tau_N2_n = max(1e-6, tau_N2_n) # Avoid zero time constant, ensure positive

        # epsilon_N2_n (C.24)
        epsilon_N2_n = 1.0 - math.exp(-delta_t_min / tau_N2_n)
        
        # G_hat_N2_n (C.25), delta_G_hat_N2_n (C.26)
        # G_hat_k,n = (4*pi/3) * n_b_n / (alpha_tk * V_hat_t)
        # n_b_n is the bubble number for the current step *before* VGE loss.
        G_hat_N2_n = 0.0
        if n_b_n > 1e-9 and alpha_t_N2_eff > 1e-9 and p.V_hat_t_scaled_dimensionless > 1e-9:
             G_hat_N2_n = (4 * math.pi / 3) * n_b_n / (alpha_t_N2_eff * p.V_hat_t_scaled_dimensionless)
        
        delta_G_hat_N2_n = 0.0
        # delta_n_b_n is the number of *newly recruited* bubbles this step.
        if delta_n_b_n > 0 and alpha_t_N2_eff > 1e-9 and p.V_hat_t_scaled_dimensionless > 1e-9:
            # Typo in C.26 in doc for Vt implies V_hat_t should be in denominator for G_hat or similar term.
            # (4pi/3) / (alpha_tk * V_hat_t) is a coefficient for delta_n_b_n
            delta_G_hat_N2_n_coeff = (4 * math.pi / 3) / (alpha_t_N2_eff * p.V_hat_t_scaled_dimensionless)
            delta_G_hat_N2_n = delta_G_hat_N2_n_coeff * delta_n_b_n

        # upsilon_N2_n (C.29) - rate of change of arterial N2 partial pressure
        if delta_t_min == 0: upsilon_N2_n = 0.0
        else: upsilon_N2_n = (pa_N2_n_plus_1_atm - pa_N2_n_atm) / delta_t_min
        
        # pt_N2,n+1 (C.30)
        # Term1: pt_N2_n * (1 - epsilon_N2_n)
        term1_ptN2 = s.pt_N2_atm * (1.0 - epsilon_N2_n)
        # Term2: upsilon_N2_n * delta_t_min
        term2_ptN2 = upsilon_N2_n * delta_t_min
        # Term3: [pa_N2_n - tau_N2_n * {upsilon_N2_n + G_hat_N2_n * (x_hat_N2,n+1 - x_hat_N2,n)/delta_t_n}] * epsilon_N2_n
        # x_hat_N2,n+1 is next_s.x_hat_N2 (already calculated)
        # x_hat_N2,n is s.x_hat_N2 (from previous state)
        term_G_N2_xchange = 0.0
        if n_b_n > 1e-9 and delta_t_min > 0: # only if bubbles exist and delta_t is non-zero
            term_G_N2_xchange = G_hat_N2_n * (next_s.x_hat_N2 - s.x_hat_N2) / delta_t_min
        
        bracket_term3_ptN2 = pa_N2_n_atm - tau_N2_n * (upsilon_N2_n + term_G_N2_xchange)
        term3_ptN2 = bracket_term3_ptN2 * epsilon_N2_n
        
        # Term4: - delta_G_hat_N2_n * (x_hat_N2,n - x_hat_o_N2,n)
        # x_hat_N2,n is s.x_hat_N2
        # x_hat_o_N2,n is the initial content of *newly* formed bubbles (calculated in Bubble Number section)
        term4_ptN2 = 0.0
        if delta_n_b_n > 0: # only if new bubbles formed
            term4_ptN2 = delta_G_hat_N2_n * (s.x_hat_N2 - x_hat_o_N2_n) 
            
        pt_N2_n_plus_1 = term1_ptN2 + term2_ptN2 + term3_ptN2 - term4_ptN2
        next_s.pt_N2_atm = max(0, pt_N2_n_plus_1) # Ensure non-negative


        # --- Tissue Oxygen (O2) - Eqs. C.31 to C.44 ---
        # Add diagnostic prints for the first few steps (e.g., t_min < 1.0)
        if s.t_min < 0.5: # Print for first 5 steps if dt=0.1
            print(f"DEBUG O2 @ t={s.t_min:.2f}: START ptO2={s.pt_O2_atm:.4f}")

        # alpha_prime_O2_n (C.31) - slope of O2 dissociation curve at current pt_O2_n (s.pt_O2_atm)
        alpha_prime_O2_n = self._calculate_alpha_prime_O2_ml_per_ml_per_atm(s.pt_O2_atm)
        
        # tau_O2_n (C.32)
        # Q_n is Q_dot_compartmental_n
        if Q_dot_compartmental_n * alpha_prime_O2_n == 0:
            tau_O2_n = float('inf')
        else:
            tau_O2_n = p.alpha_t_O2_ml_ml_atm / (Q_dot_compartmental_n * alpha_prime_O2_n)
        tau_O2_n = max(1e-6, tau_O2_n) # Ensure positive
        
        # epsilon_O2_n (C.33)
        epsilon_O2_n = 1.0 - math.exp(-delta_t_min / tau_O2_n)

        # G_hat_O2_n (C.34) & delta_G_hat_O2_n (C.35)
        G_hat_O2_n = 0.0
        if n_b_n > 1e-9 and p.alpha_t_O2_ml_ml_atm > 1e-9 and p.V_hat_t_scaled_dimensionless > 1e-9:
             G_hat_O2_n = (4 * math.pi / 3) * n_b_n / (p.alpha_t_O2_ml_ml_atm * p.V_hat_t_scaled_dimensionless)

        delta_G_hat_O2_n = 0.0
        if delta_n_b_n > 0 and p.alpha_t_O2_ml_ml_atm > 1e-9 and p.V_hat_t_scaled_dimensionless > 1e-9:
            delta_G_hat_O2_n_coeff = (4 * math.pi / 3) / (p.alpha_t_O2_ml_ml_atm * p.V_hat_t_scaled_dimensionless)
            delta_G_hat_O2_n = delta_G_hat_O2_n_coeff * delta_n_b_n

        # x_hat_O2,n+1 (C.36) is next_s.x_hat_O2 (already calculated)
        # pa_O2,n+1 (C.37) is pa_O2_n_plus_1_atm (already calculated)

        # C_aO2,n (C.38) and C_aO2,n+1 (C.39)
        C_aO2_n_ml_per_ml = self._calculate_blood_O2_content_ml_per_ml(pa_O2_n_atm)
        C_aO2_n_plus_1_ml_per_ml = self._calculate_blood_O2_content_ml_per_ml(pa_O2_n_plus_1_atm)

        # pO'_2n, pO'_2,n+1 (C.40)
        # alpha_prime_O2_n is slope at pt_O2_n (venous equivalent)
        pO_prime_2_n_atm = 0.0
        if alpha_prime_O2_n > 1e-9: pO_prime_2_n_atm = C_aO2_n_ml_per_ml / alpha_prime_O2_n
        
        pO_prime_2_n_plus_1_atm = 0.0
        if alpha_prime_O2_n > 1e-9: pO_prime_2_n_plus_1_atm = C_aO2_n_plus_1_ml_per_ml / alpha_prime_O2_n
        
        # upsilon_O2_n (C.41)
        if delta_t_min == 0: upsilon_O2_n = 0.0
        else: upsilon_O2_n = (pO_prime_2_n_plus_1_atm - pO_prime_2_n_atm) / delta_t_min
        
        # C_vO2,n (C.42) - Venous O2 content corresponding to pt_O2_n (s.pt_O2_atm)
        C_vO2_n_ml_per_ml = self._calculate_blood_O2_content_ml_per_ml(s.pt_O2_atm)
        
        # rho_dot_n (C.43)
        # V_O2_n is V_O2_compartmental_n for the current step
        # Q_n is Q_dot_compartmental_n for the current step
        # alpha_TO2 is p.alpha_t_O2_ml_ml_atm
        rho_dot_n_numerator = V_O2_compartmental_n + Q_dot_compartmental_n * (C_vO2_n_ml_per_ml - alpha_prime_O2_n * s.pt_O2_atm)
        if p.alpha_t_O2_ml_ml_atm == 0: rho_dot_n_atm_per_min = 0.0
        else: rho_dot_n_atm_per_min = rho_dot_n_numerator / p.alpha_t_O2_ml_ml_atm
        
        # pt_O2,n+1 (C.44)
        # Term1: pt_O2_n * (1 - epsilon_O2_n)
        term1_ptO2 = s.pt_O2_atm * (1.0 - epsilon_O2_n)
        # Term2: upsilon_O2_n * delta_t_min
        term2_ptO2 = upsilon_O2_n * delta_t_min
        
        # Term3: [p'_O2_n - tau_O2_n * {upsilon_O2_n + rho_dot_n + G_hat_O2_n * (x_hat_O2,n+1 - x_hat_O2,n)/delta_t_n}] * epsilon_O2_n
        # p'_O2_n is pO_prime_2_n_atm
        term_G_O2_xchange = 0.0
        if n_b_n > 1e-9 and delta_t_min > 0:
            term_G_O2_xchange = G_hat_O2_n * (next_s.x_hat_O2 - s.x_hat_O2) / delta_t_min
            
        bracket_calc_for_term3 = (upsilon_O2_n + rho_dot_n_atm_per_min + term_G_O2_xchange)
        bracket_term3_ptO2 = pO_prime_2_n_atm - tau_O2_n * bracket_calc_for_term3
        term3_ptO2 = bracket_term3_ptO2 * epsilon_O2_n
        
        # Term4: - delta_G_hat_O2_n * (x_hat_O2,n - x_hat_o_O2,n)
        # x_hat_O2,n is s.x_hat_O2 (content of existing bubbles at start of step)
        # x_hat_o_O2,n is initial content of *newly* formed bubbles (from Bubble Number section)
        term4_ptO2 = 0.0
        if delta_n_b_n > 0:
            term4_ptO2 = delta_G_hat_O2_n * (s.x_hat_O2 - x_hat_o_O2_n)
            
        pt_O2_n_plus_1 = term1_ptO2 + term2_ptO2 + term3_ptO2 - term4_ptO2
        next_s.pt_O2_atm = max(0, pt_O2_n_plus_1) # Ensure non-negative

        if s.t_min < 0.5:
            print(f"    alpha'={alpha_prime_O2_n:.4f}, tauO2={tau_O2_n:.4f}, rho_dot={rho_dot_n_atm_per_min:.4f}")
            print(f"    pO'_2n={pO_prime_2_n_atm:.4f}, upsilonO2={upsilon_O2_n:.4f}, G_term={term_G_O2_xchange:.4e}")
            print(f"    target_B_eff = {bracket_term3_ptO2 / epsilon_O2_n if epsilon_O2_n > 1e-9 else float('nan'):.4f} (from bracket_term3 / eps)")
            # Target B for simple s_next = s_curr*(1-eps) + B*eps is B = bracket_term3_ptO2 / epsilon_O2_n (if upsilon=0, G=0, deltaG=0)
            # More general target towards which ptO2 is driven:
            # If ptO2_n+1 = ptO2_n, then ptO2_n * eps = ups_dt + bracket_term3*eps - deltaG_term 
            # ptO2_n = (ups_dt - deltaG_term)/eps + bracket_term3
            effective_target_ptO2 = (term2_ptO2 - term4_ptO2)/epsilon_O2_n + bracket_term3_ptO2 if epsilon_O2_n > 1e-9 else float('nan')
            print(f"    FullEffTarget={effective_target_ptO2:.4f}, next_ptO2={next_s.pt_O2_atm:.4f}")

        # --- 4. VGE Formation (C.45 - C.46) ---
        # n_b_n is the bubble number *before* VGE loss (calculated from C.9, delta_n_b_n + s.n_b)
        # Vb and Vr0 are UN SCALED.
        # r_hat_n_plus_1 is next_s.r_hat_dimensionless (calculated in bubble radius/pressure section)
        # Lambda is p.Lambda_scale_factor_cm_neg1
        
        Vb_n_plus_1_unscaled_ml = 0.0
        # Only calculate Vb if a bubble exists and has a meaningful radius
        if next_s.r_hat_dimensionless > 1e-9 and n_b_n > 1e-9: # Use n_b_n (before VGE) to check if bubble existed to grow
             r_n_plus_1_unscaled_cm = next_s.r_hat_dimensionless / p.Lambda_scale_factor_cm_neg1
             # Assuming 1cm^3 = 1ml for direct conversion
             Vb_n_plus_1_unscaled_ml = (4.0/3.0) * math.pi * (r_n_plus_1_unscaled_cm**3) 

        # Vr0_n_plus_1 is nucleonic volume corresponding to r_min_n for *this* step's nucleation conditions.
        # next_s.r_hat_min_nucleation_dimensionless was calculated in Bubble Number section (C.10)
        r_min_current_step_unscaled_cm = next_s.r_hat_min_nucleation_dimensionless / p.Lambda_scale_factor_cm_neg1
        Vr0_current_step_unscaled_ml = (4.0/3.0) * math.pi * (r_min_current_step_unscaled_cm**3)
        
        LR_n = 0.0
        # VGE occurs if current bubble volume exceeds current nucleonic volume threshold
        if Vb_n_plus_1_unscaled_ml > Vr0_current_step_unscaled_ml:
            LR_n = (Vb_n_plus_1_unscaled_ml - Vr0_current_step_unscaled_ml) * \
                   p.N_VGE_gas_loss_rate_ml_neg1_min_neg1 * delta_t_min
        
        LR_n = min(max(LR_n, 0.0), 1.0) # LR_n is a fraction, cannot be > 1 or < 0

        # n_b_n was bubble number *before* VGE (from C.9). Update to n_b_{n+1} and store in next_s.n_b
        # This is the number of bubbles REMAINING after VGE for the *next* step.
        next_s.n_b = max(0, n_b_n * (1.0 - LR_n))
        
        # If all bubbles are lost via VGE or resolved earlier, ensure dependent states are clean.
        if next_s.n_b < p.N_min_b_nuclei_threshold: # Effectively all bubbles gone
            next_s.n_b = 0.0 
            # If n_b becomes 0, reset associated bubble properties for the *next* state.
            next_s.r_hat_dimensionless = 1e-9 # Reset to a very small number
            next_s.Pb_N2_atm = 0.0
            next_s.Pb_O2_atm = 0.0
            next_s.x_hat_N2 = 0.0
            next_s.x_hat_O2 = 0.0
            # N_b_max_cumulative should persist as it tracks *ever recruited* nuclei.

        # --- 5. Hazard Calculation (Eq. 10 / D.3a from main text) ---
        # h(t) = g * (V_b - V_r0) * (N_b)^BN
        # V_b is Vb_n_plus_1_unscaled_ml (volume at end of step, *before* VGE for this step's hazard calc?)
        #   No, hazard should be based on bubbles *present* that can cause DCS.
        #   So N_b here is next_s.n_b (after VGE). V_b should also reflect this state.
        #   If N_b (after VGE) is 0, then hazard is 0.
        # V_r0 is Vr0_current_step_unscaled_ml (nucleonic volume for current conditions)
        
        h_t_n_plus_1 = 0.0
        # Use bubble volume Vb_n_plus_1_unscaled_ml (volume bubbles reached in this step)
        # And N_b after VGE (next_s.n_b) for hazard calculation
        hazard_term_volume_diff = Vb_n_plus_1_unscaled_ml - Vr0_current_step_unscaled_ml

        if next_s.n_b > 1e-9 and hazard_term_volume_diff > 0: # Only if bubbles exist and are larger than nucleonic
            # Ensure N_b for power is not too small to cause issues if BN is large, or zero.
            n_b_for_hazard = max(next_s.n_b, 1e-9) # Use a small floor if n_b is tiny but non-zero
            h_t_n_plus_1 = p.gain_g_hazard * hazard_term_volume_diff * (n_b_for_hazard ** p.BN_bubble_number_power_factor)
        
        next_s.h_t_hazard_per_min = max(0, h_t_n_plus_1) # Hazard cannot be negative

        # --- 6. Update P_DCS (Integral of hazard) ---
        # P(0)_n+1 = P(0)_n * exp[ - (h_n + h_n+1)/2 * dt ]
        # s.h_t_hazard_per_min is h_n (hazard from the *previous* state, leading into this step)
        # next_s.h_t_hazard_per_min is h_n+1 (hazard calculated for the *current* state, end of this step)
        avg_hazard_this_step = (s.h_t_hazard_per_min + next_s.h_t_hazard_per_min) / 2.0
        integral_h_dt = avg_hazard_this_step * delta_t_min
        
        next_s.P_survival = s.P_survival * math.exp(-integral_h_dt)
        next_s.P_survival = min(max(next_s.P_survival, 0.0), 1.0) # Clamp between 0 and 1
        next_s.P_DCS = 1.0 - next_s.P_survival
        
        # Update current state for the next iteration
        self.current_state = next_s
        # print(f"State at t={self.current_state.t_min:.2f}: P_DCS={self.current_state.P_DCS:.4f}, r_hat={self.current_state.r_hat_dimensionless:.3e}, n_b={self.current_state.n_b:.3e}, ptN2={self.current_state.pt_N2_atm:.3f}, ptO2={self.current_state.pt_O2_atm:.3f}")


if __name__ == '__main__':
    # Example usage (illustrative)
    params = ModelParameters()
    # print(f"P_infinity_atm: {params.P_infinity_mmHg / 760.0}")
    # print(f"sigma_hat_atm: {params.sigma_hat_atm}")
    # print(f"sigma_c_hat_atm: {params.sigma_c_hat_atm}")
    # print(f"K_hat_O2: {params.K_hat_O2_per_min}")
    # print(f"K_hat_N2: {params.K_hat_N2_per_min}")
    # print(f"V_hat_t: {params.V_hat_t_scaled_dimensionless}")
    # print(f"beta0_hat: {params.beta0_hat_initial_nuclei_slope_dimensionless}")

    model = RutMbe1Model(params)
    
    # Define a test profile
    # Standard air composition
    FIO2_air = 0.21
    FIN2_air = 0.79

    # Initial conditions (t=0)
    P_amb_initial_atm = 1.0
    I_ex_initial = 0.0 # Rest

    # Initialize model to t=0 state
    model.initialize_state(
        initial_P_amb_atm=P_amb_initial_atm, 
        initial_FIO2=FIO2_air, 
        initial_FIN2=FIN2_air, 
        initial_I_ex=I_ex_initial
    )
    print(f"Initial State (t=0 min, Pamb={model.current_state.P_amb_atm:.2f} atm): ")
    print(f"  ptN2={model.current_state.pt_N2_atm:.3f}, ptO2={model.current_state.pt_O2_atm:.3f}, Pcrush={model.current_state.P_crush_atm:.3f}")
    print(f"  n_b={model.current_state.n_b:.2e}, r_hat={model.current_state.r_hat_dimensionless:.2e}, P_DCS={model.current_state.P_DCS:.3e}\n")

    test_profile = [
        ProfileSegment(duration_min=60.0, P_amb_atm=1.0, FIO2=FIO2_air, FIN2=FIN2_air, I_ex_L_min_wb=0.0), # Ground level
        ProfileSegment(duration_min=1.0,  P_amb_atm=0.5, FIO2=FIO2_air, FIN2=FIN2_air, I_ex_L_min_wb=0.0), # Ascent phase (rapid)
        ProfileSegment(duration_min=120.0,P_amb_atm=0.5, FIO2=FIO2_air, FIN2=FIN2_air, I_ex_L_min_wb=0.0), # Altitude exposure
    ]

    simulation_dt_min = 0.1 # Simulation time step
    history = model.run_profile(profile_segments=test_profile, delta_t_min=simulation_dt_min)

    print(f"Simulation finished. Total steps: {len(history)}")

    # Print state at key points
    # State after ground level (approx 60 min)
    time_point_1 = 60.0
    state_at_60_min = next((s for s in history if abs(s.t_min - time_point_1) < simulation_dt_min/2), history[0]) 
    # find state closest to 60min, default to first if not found (though it should be)
    if state_at_60_min.t_min < time_point_1 and time_point_1/simulation_dt_min < len(history):
        state_at_60_min = history[int(time_point_1/simulation_dt_min)] # More direct index if times are regular
    
    print(f"State at t={state_at_60_min.t_min:.2f} min (Pamb={state_at_60_min.P_amb_atm:.2f} atm - End of Ground Level): ")
    print(f"  ptN2={state_at_60_min.pt_N2_atm:.3f}, ptO2={state_at_60_min.pt_O2_atm:.3f}, Pcrush={state_at_60_min.P_crush_atm:.3f}")
    print(f"  n_b={state_at_60_min.n_b:.2e}, r_hat={state_at_60_min.r_hat_dimensionless:.2e}, P_DCS={state_at_60_min.P_DCS:.3e}\n")

    # State after ascent (approx 60 + 1 = 61 min)
    time_point_2 = 61.0
    state_at_61_min = history[0]
    try:
        state_at_61_min = history[int(time_point_2/simulation_dt_min)]
    except IndexError:
        state_at_61_min = history[-1] # if profile shorter than expected

    print(f"State at t={state_at_61_min.t_min:.2f} min (Pamb={state_at_61_min.P_amb_atm:.2f} atm - End of Ascent): ")
    print(f"  ptN2={state_at_61_min.pt_N2_atm:.3f}, ptO2={state_at_61_min.pt_O2_atm:.3f}, Pcrush={state_at_61_min.P_crush_atm:.3f}")
    print(f"  n_b={state_at_61_min.n_b:.2e}, r_hat={state_at_61_min.r_hat_dimensionless:.2e}, P_DCS={state_at_61_min.P_DCS:.3e}\n")

    # State at end of altitude exposure (approx 61 + 120 = 181 min)
    time_point_3 = 181.0
    state_at_end = history[-1] # Last state in history
    print(f"State at t={state_at_end.t_min:.2f} min (Pamb={state_at_end.P_amb_atm:.2f} atm - End of Altitude): ")
    print(f"  ptN2={state_at_end.pt_N2_atm:.3f}, ptO2={state_at_end.pt_O2_atm:.3f}, Pcrush={state_at_end.P_crush_atm:.3f}")
    print(f"  n_b={state_at_end.n_b:.2e}, r_hat={state_at_end.r_hat_dimensionless:.2e}, P_DCS={state_at_end.P_DCS:.3e}\n")

    # Optional: Plot P_DCS vs time
    # import matplotlib.pyplot as plt
    # times = [s.t_min for s in history]
    # p_dcs_values = [s.P_DCS for s in history]
    # n_b_values = [s.n_b for s in history]
    # r_hat_values = [s.r_hat_dimensionless for s in history]

    # fig, ax1 = plt.subplots()
    # color = 'tab:red'
    # ax1.set_xlabel('Time (min)')
    # ax1.set_ylabel('P(DCS)', color=color)
    # ax1.plot(times, p_dcs_values, color=color)
    # ax1.tick_params(axis='y', labelcolor=color)

    # ax2 = ax1.twinx() 
    # color = 'tab:blue'
    # ax2.set_ylabel('Bubble Number (n_b)', color=color) 
    # ax2.plot(times, n_b_values, color=color, linestyle=':')
    # ax2.tick_params(axis='y', labelcolor=color)
    
    # ax3 = ax1.twinx()
    # ax3.spines["right"].set_position(("outward", 60))
    # color = 'tab:green'
    # ax3.set_ylabel('Scaled Radius (r_hat)', color=color)
    # ax3.plot(times, r_hat_values, color=color, linestyle='--')
    # ax3.tick_params(axis='y', labelcolor=color)

    # fig.tight_layout() 
    # plt.title('DCS Model Simulation')
    # plt.show()

    # --- Test Scenario 1: O2 Prebreathe Effects ---
    print("\n--- Test Scenario 1: O2 Prebreathe Effects ---")
    model_scen1 = RutMbe1Model(params) # New model instance for clean state
    
    FIO2_O2 = 1.0
    FIN2_O2 = 0.0
    
    # Initial conditions (t=0)
    model_scen1.initialize_state(
        initial_P_amb_atm=P_amb_initial_atm, 
        initial_FIO2=FIO2_air, # Start saturating on air
        initial_FIN2=FIN2_air, 
        initial_I_ex=I_ex_initial
    )
    print(f"SCEN1 Initial State (t=0 min, Pamb={model_scen1.current_state.P_amb_atm:.2f} atm, Air): ")
    print(f"  ptN2={model_scen1.current_state.pt_N2_atm:.3f}, ptO2={model_scen1.current_state.pt_O2_atm:.3f}, Pcrush={model_scen1.current_state.P_crush_atm:.3f}")
    print(f"  n_b={model_scen1.current_state.n_b:.2e}, r_hat={model_scen1.current_state.r_hat_dimensionless:.2e}, P_DCS={model_scen1.current_state.P_DCS:.3e}\n")

    profile_scen1 = [
        ProfileSegment(duration_min=120.0, P_amb_atm=1.0, FIO2=FIO2_O2, FIN2=FIN2_O2, I_ex_L_min_wb=0.0), # O2 Prebreathe at 1 ATA
        ProfileSegment(duration_min=1.0,   P_amb_atm=0.3, FIO2=FIO2_O2, FIN2=FIN2_O2, I_ex_L_min_wb=0.0), # Ascent to 0.3 ATA on O2
        ProfileSegment(duration_min=180.0, P_amb_atm=0.3, FIO2=FIO2_O2, FIN2=FIN2_O2, I_ex_L_min_wb=0.0), # Altitude exposure on O2
    ]

    history_scen1 = model_scen1.run_profile(profile_segments=profile_scen1, delta_t_min=simulation_dt_min)
    print(f"SCEN1 Simulation finished. Total steps: {len(history_scen1)}")

    # State after O2 Prebreathe (approx 120 min)
    time_s1_pt1 = 120.0
    state_s1_pb_end = history_scen1[0]
    try: state_s1_pb_end = history_scen1[int(time_s1_pt1/simulation_dt_min)]
    except IndexError: state_s1_pb_end = history_scen1[-1]
    print(f"SCEN1 State at t={state_s1_pb_end.t_min:.2f} min (Pamb={state_s1_pb_end.P_amb_atm:.2f} atm - End of O2 Prebreathe): ")
    print(f"  ptN2={state_s1_pb_end.pt_N2_atm:.3f}, ptO2={state_s1_pb_end.pt_O2_atm:.3f}, Pcrush={state_s1_pb_end.P_crush_atm:.3f}")
    print(f"  n_b={state_s1_pb_end.n_b:.2e}, r_hat={state_s1_pb_end.r_hat_dimensionless:.2e}, P_DCS={state_s1_pb_end.P_DCS:.3e}\n")

    # State after Ascent (approx 120 + 1 = 121 min)
    time_s1_pt2 = 121.0
    state_s1_ascent_end = history_scen1[0]
    try: state_s1_ascent_end = history_scen1[int(time_s1_pt2/simulation_dt_min)]
    except IndexError: state_s1_ascent_end = history_scen1[-1]
    print(f"SCEN1 State at t={state_s1_ascent_end.t_min:.2f} min (Pamb={state_s1_ascent_end.P_amb_atm:.2f} atm - End of Ascent): ")
    print(f"  ptN2={state_s1_ascent_end.pt_N2_atm:.3f}, ptO2={state_s1_ascent_end.pt_O2_atm:.3f}, Pcrush={state_s1_ascent_end.P_crush_atm:.3f}")
    print(f"  n_b={state_s1_ascent_end.n_b:.2e}, r_hat={state_s1_ascent_end.r_hat_dimensionless:.2e}, P_DCS={state_s1_ascent_end.P_DCS:.3e}\n")

    # State at end of altitude exposure (approx 121 + 180 = 301 min total sim time from t=0)
    state_s1_end = history_scen1[-1] # Last state
    print(f"SCEN1 State at t={state_s1_end.t_min:.2f} min (Pamb={state_s1_end.P_amb_atm:.2f} atm - End of Altitude): ")
    print(f"  ptN2={state_s1_end.pt_N2_atm:.3f}, ptO2={state_s1_end.pt_O2_atm:.3f}, Pcrush={state_s1_end.P_crush_atm:.3f}")
    print(f"  n_b={state_s1_end.n_b:.2e}, r_hat={state_s1_end.r_hat_dimensionless:.2e}, P_DCS={state_s1_end.P_DCS:.3e}\n")

    # --- Test Scenario 2: Exercise during O2 Prebreathe ---
    print("\n--- Test Scenario 2: Exercise during O2 Prebreathe ---")
    model_scen2 = RutMbe1Model(params) # New model instance
    I_ex_moderate = 1.0 # L/min whole body O2 consumption above rest

    # Initial conditions (t=0)
    model_scen2.initialize_state(
        initial_P_amb_atm=P_amb_initial_atm, 
        initial_FIO2=FIO2_air, 
        initial_FIN2=FIN2_air, 
        initial_I_ex=I_ex_initial # Start at rest
    )
    print(f"SCEN2 Initial State (t=0 min, Pamb={model_scen2.current_state.P_amb_atm:.2f} atm, Air): ")
    print(f"  ptN2={model_scen2.current_state.pt_N2_atm:.3f}, ptO2={model_scen2.current_state.pt_O2_atm:.3f}, Pcrush={model_scen2.current_state.P_crush_atm:.3f}")
    print(f"  n_b={model_scen2.current_state.n_b:.2e}, r_hat={model_scen2.current_state.r_hat_dimensionless:.2e}, P_DCS={model_scen2.current_state.P_DCS:.3e}\n")

    profile_scen2 = [
        ProfileSegment(duration_min=120.0, P_amb_atm=1.0, FIO2=FIO2_O2, FIN2=FIN2_O2, I_ex_L_min_wb=I_ex_moderate), # O2 Prebreathe with exercise
        ProfileSegment(duration_min=1.0,   P_amb_atm=0.3, FIO2=FIO2_O2, FIN2=FIN2_O2, I_ex_L_min_wb=0.0),         # Ascent to 0.3 ATA on O2, rest
        ProfileSegment(duration_min=180.0, P_amb_atm=0.3, FIO2=FIO2_O2, FIN2=FIN2_O2, I_ex_L_min_wb=0.0),         # Altitude exposure on O2, rest
    ]

    history_scen2 = model_scen2.run_profile(profile_segments=profile_scen2, delta_t_min=simulation_dt_min)
    print(f"SCEN2 Simulation finished. Total steps: {len(history_scen2)}")

    # State after O2 Prebreathe with Exercise (approx 120 min)
    time_s2_pt1 = 120.0
    state_s2_pb_end = history_scen2[0]
    try: state_s2_pb_end = history_scen2[int(time_s2_pt1/simulation_dt_min)]
    except IndexError: state_s2_pb_end = history_scen2[-1]
    print(f"SCEN2 State at t={state_s2_pb_end.t_min:.2f} min (Pamb={state_s2_pb_end.P_amb_atm:.2f} atm - End of O2 Prebreathe w/ Exercise): ")
    print(f"  ptN2={state_s2_pb_end.pt_N2_atm:.3f}, ptO2={state_s2_pb_end.pt_O2_atm:.3f}, Pcrush={state_s2_pb_end.P_crush_atm:.3f}")
    print(f"  I_ex={state_s2_pb_end.I_ex_L_min_wb:.2f}, n_b={state_s2_pb_end.n_b:.2e}, P_DCS={state_s2_pb_end.P_DCS:.3e}\n")

    # State after Ascent (approx 121 min)
    time_s2_pt2 = 121.0
    state_s2_ascent_end = history_scen2[0]
    try: state_s2_ascent_end = history_scen2[int(time_s2_pt2/simulation_dt_min)]
    except IndexError: state_s2_ascent_end = history_scen2[-1]
    print(f"SCEN2 State at t={state_s2_ascent_end.t_min:.2f} min (Pamb={state_s2_ascent_end.P_amb_atm:.2f} atm - End of Ascent): ")
    print(f"  ptN2={state_s2_ascent_end.pt_N2_atm:.3f}, ptO2={state_s2_ascent_end.pt_O2_atm:.3f}, Pcrush={state_s2_ascent_end.P_crush_atm:.3f}")
    print(f"  n_b={state_s2_ascent_end.n_b:.2e}, r_hat={state_s2_ascent_end.r_hat_dimensionless:.2e}, P_DCS={state_s2_ascent_end.P_DCS:.3e}\n")

    # State at end of altitude exposure (approx 301 min)
    state_s2_end = history_scen2[-1]
    print(f"SCEN2 State at t={state_s2_end.t_min:.2f} min (Pamb={state_s2_end.P_amb_atm:.2f} atm - End of Altitude): ")
    print(f"  ptN2={state_s2_end.pt_N2_atm:.3f}, ptO2={state_s2_end.pt_O2_atm:.3f}, Pcrush={state_s2_end.P_crush_atm:.3f}")
    print(f"  n_b={state_s2_end.n_b:.2e}, r_hat={state_s2_end.r_hat_dimensionless:.2e}, P_DCS={state_s2_end.P_DCS:.3e}\n")
