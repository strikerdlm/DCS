import math
from dataclasses import dataclass
from typing import List

# This ProfileSegment definition should match the one in rut_mbe1_model.py
@dataclass
class ProfileSegment:
    """
    Represents a single, continuous phase of an exposure profile.
    Matches the definition in rut_mbe1_model.py.
    """
    duration_min: float       # Duration of this segment in minutes.
    P_amb_atm: float          # Ambient pressure in atmospheres (absolute) at the END of this segment.
    FIO2: float               # Fraction of inspired Oxygen (0.0 to 1.0).
    FIN2: float               # Fraction of inspired Nitrogen (0.0 to 1.0).
    I_ex_L_min_wb: float      # Exercise intensity (Whole Body V_O2_wb - V_O2_wb_rest) in L/min.
                              # For rest, this should be 0.0, assuming V_O2_wb_rest is handled internally by the model
                              # or I_ex is directly used.

# Constants
P_SEA_LEVEL_ATM = 1.0
FIO2_AIR = 0.21
FIN2_AIR = 0.79
# V_O2_WB_REST_L_MIN = 0.305 # This constant is used by the generator to calculate I_ex if vo2_wb was input.
                            # Since ProfileSegment takes I_ex directly, the generator will directly set I_ex.
                            # For resting segments, I_ex_L_min_wb = 0.0.
DEFAULT_ASCENT_RATE_FT_PER_MIN = 5000.0
DEFAULT_DESCENT_RATE_FT_PER_MIN = 5000.0

def altitude_to_pressure_atm(altitude_ft: float) -> float:
    """Converts altitude in feet to pressure in atmospheres."""
    if altitude_ft < 0:
        altitude_ft = 0 # Pressure doesn't make sense below sea level in this model context
    # Standard formula: P(h) = P0 * (1 - L*h / T0)^(g*M / (R*L))
    # Simplified for P0=1atm at h=0: P(h) = (1 - 0.00000687535 * h_ft)^5.2559
    pressure = (1 - 6.87535e-6 * altitude_ft)**5.2559
    return max(pressure, 0.001) # Avoid zero or negative pressure, ensure a minimum viable pressure

def generate_altitude_exposure_profile(
    target_altitude_ft: float,
    acclimatization_duration_min: float = 5.0,
    acclimatization_pressure_atm: float = P_SEA_LEVEL_ATM,
    acclimatization_fio2: float = FIO2_AIR,
    acclimatization_fin2: float = FIN2_AIR,
    acclimatization_i_ex_l_min_wb: float = 0.0,
    
    prebreathe_duration_min: float = 0.0,
    prebreathe_pressure_atm: float = P_SEA_LEVEL_ATM, # Usually same as acclimatization_pressure_atm
    prebreathe_fio2: float = 1.0,
    prebreathe_fin2: float = 0.0,
    prebreathe_i_ex_l_min_wb: float = 0.0,

    ascent_rate_ft_per_min: float = DEFAULT_ASCENT_RATE_FT_PER_MIN,
    ascent_fio2: float = FIO2_AIR,
    ascent_fin2: float = FIN2_AIR,
    ascent_i_ex_l_min_wb: float = 0.0,

    altitude_exposure_duration_min: float = 60.0,
    altitude_fio2: float = FIO2_AIR, # Allow different gas at altitude
    altitude_fin2: float = FIN2_AIR,
    altitude_i_ex_l_min_wb: float = 0.0,

    add_descent_segment: bool = False,
    descent_rate_ft_per_min: float = DEFAULT_DESCENT_RATE_FT_PER_MIN,
    descent_target_pressure_atm: float = P_SEA_LEVEL_ATM,
    descent_fio2: float = FIO2_AIR,
    descent_fin2: float = FIN2_AIR,
    descent_i_ex_l_min_wb: float = 0.0

) -> List[ProfileSegment]:
    
    profile: List[ProfileSegment] = []
    
    # Determine current altitude based on acclimatization pressure for ascent calculation
    # This is a simplification; a proper conversion from pressure to altitude would be needed if not sea level.
    current_altitude_ft = 0.0
    if abs(acclimatization_pressure_atm - P_SEA_LEVEL_ATM) > 0.01:
        # For simplicity, if not starting at sea level, we still calculate ascent duration
        # based on target_altitude_ft as if from 0 ft. The actual pressure change will be handled
        # by the simulation engine using the P_amb_atm of the segments.
        print(f"Warning: Acclimatization pressure is {acclimatization_pressure_atm} atm. Ascent duration calculation assumes climb from 0 ft for simplicity.")


    # 1. Acclimatization Segment
    if acclimatization_duration_min > 0:
        profile.append(ProfileSegment(
            duration_min=acclimatization_duration_min,
            P_amb_atm=acclimatization_pressure_atm,
            FIO2=acclimatization_fio2,
            FIN2=acclimatization_fin2,
            I_ex_L_min_wb=acclimatization_i_ex_l_min_wb
        ))

    # 2. Prebreathe Segment
    if prebreathe_duration_min > 0:
        profile.append(ProfileSegment(
            duration_min=prebreathe_duration_min,
            P_amb_atm=prebreathe_pressure_atm,
            FIO2=prebreathe_fio2,
            FIN2=prebreathe_fin2,
            I_ex_L_min_wb=prebreathe_i_ex_l_min_wb
        ))

    # 3. Ascent Segment
    target_pressure_atm = altitude_to_pressure_atm(target_altitude_ft)
    altitude_to_climb_ft = target_altitude_ft - current_altitude_ft # Simplified: assumes current_altitude_ft is 0 if prebreathe at sea level
    
    ascent_duration_min = 0
    if altitude_to_climb_ft > 0 and ascent_rate_ft_per_min > 0:
        ascent_duration_min = altitude_to_climb_ft / ascent_rate_ft_per_min
        profile.append(ProfileSegment(
            duration_min=ascent_duration_min,
            P_amb_atm=target_pressure_atm,
            FIO2=ascent_fio2,
            FIN2=ascent_fin2,
            I_ex_L_min_wb=ascent_i_ex_l_min_wb
        ))
    
    # 4. Altitude Exposure Segment
    if altitude_exposure_duration_min > 0:
        profile.append(ProfileSegment(
            duration_min=altitude_exposure_duration_min,
            P_amb_atm=target_pressure_atm, # Isobaric
            FIO2=altitude_fio2, # Use specific altitude gas mix
            FIN2=altitude_fin2,
            I_ex_L_min_wb=altitude_i_ex_l_min_wb
        ))

    # 5. Descent Segment (Optional)
    if add_descent_segment and descent_rate_ft_per_min > 0:
        altitude_to_descend_ft = target_altitude_ft # Assumes descending from target_altitude_ft to sea level equivalent
        # A more robust version would calculate target_descent_altitude_ft from descent_target_pressure_atm.
        # For now, assume descent is to sea level (0 ft altitude).
        
        descent_duration_min = altitude_to_descend_ft / descent_rate_ft_per_min
        if descent_duration_min > 0:
            profile.append(ProfileSegment(
                duration_min=descent_duration_min,
                P_amb_atm=descent_target_pressure_atm,
                FIO2=descent_fio2,
                FIN2=descent_fin2,
                I_ex_L_min_wb=descent_i_ex_l_min_wb
            ))
            
    return profile

if __name__ == '__main__':
    # Example of generating profiles for the sweep:
    altitude_profiles_to_simulate = {}
    for alt_ft_sweep in range(15000, 50000 + 1000, 1000):
        profile_name = f"profile_{alt_ft_sweep}ft"
        altitude_profiles_to_simulate[profile_name] = generate_altitude_exposure_profile(
            target_altitude_ft=float(alt_ft_sweep),
            acclimatization_duration_min=5.0,
            altitude_exposure_duration_min=60.0
        )

    print("Profile for 15000 ft:")
    for seg in altitude_profiles_to_simulate["profile_15000ft"]:
        print(f"  {seg}")
    
    print("\\nProfile for 25000 ft with 30 min O2 prebreathe at rest:")
    profile_pb = generate_altitude_exposure_profile(
        target_altitude_ft=25000.0,
        prebreathe_duration_min=30.0,
        prebreathe_fio2=1.0,
        prebreathe_fin2=0.0,
        prebreathe_i_ex_l_min_wb=0.0, # Rest during prebreathe
        ascent_fio2=1.0, # Continue O2 on ascent
        ascent_fin2=0.0,
        altitude_fio2=1.0, # Continue O2 at altitude
        altitude_fin2=0.0,
        altitude_exposure_duration_min=60.0
    )
    for seg in profile_pb:
        print(f"  {seg}")

    print("\\nProfile for 18000 ft, 60 min O2 prebreathe with I_ex=0.7, ascent on air, 120 min at alt on air with I_ex=0.3")
    # For I_ex = 0.7 L/min, if V_O2_wb_rest = 0.305, then V_O2_wb = 1.005 L/min
    # For I_ex = 0.3 L/min, if V_O2_wb_rest = 0.305, then V_O2_wb = 0.605 L/min
    profile_ex = generate_altitude_exposure_profile(
        target_altitude_ft=18000.0,
        acclimatization_duration_min=5.0,
        prebreathe_duration_min=60.0,
        prebreathe_fio2=1.0,
        prebreathe_fin2=0.0,
        prebreathe_i_ex_l_min_wb=0.695, # Matches 1.0 L/min total V_O2_wb if V_O2_wb_rest is 0.305
        ascent_fio2=FIO2_AIR, # Switch to air for ascent
        ascent_fin2=FIN2_AIR,
        altitude_fio2=FIO2_AIR,
        altitude_fin2=FIN2_AIR,
        altitude_exposure_duration_min=120.0,
        altitude_i_ex_l_min_wb=0.295 # Matches 0.6 L/min total V_O2_wb
    )
    for seg in profile_ex:
        print(f"  {seg}") 