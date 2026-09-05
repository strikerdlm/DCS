"""US Standard Atmosphere (1976), geopotential altitude 0--20 km.

Altitude inputs are pressure/geopotential altitude, not geometric height.
Hydrostatic integration uses the tropospheric lapse rate then the 11--20 km
isothermal layer. Units and coefficients are mirrored by the browser runtime.
"""

import numpy as np

G0 = 9.80665
R_AIR = 287.05287
T0 = 288.15
LAPSE = 0.0065
T11 = 216.65
PSIA_PER_ATM = 14.695948775513449
KPA_PER_PSIA = 6.894757293168
MMHG_PER_PSIA = 760 / PSIA_PER_ATM


def altitude_ft_to_atm(altitude_ft):
    altitude = np.asarray(altitude_ft, dtype=float)
    height = altitude * 0.3048
    if not np.isfinite(height).all() or np.any(height < 0) or np.any(height > 20000 + 1e-9):
        raise ValueError("pressure altitude must be finite and within 0--20 km")
    exponent = G0 / (R_AIR * LAPSE)
    p11 = (T11 / T0) ** exponent
    return np.where(height <= 11000,
                    (1 - LAPSE * np.minimum(height, 11000) / T0) ** exponent,
                    p11 * np.exp(-G0 * (height - 11000) / (R_AIR * T11)))


def pressure_atm_to_altitude_ft(pressure_atm):
    pressure = np.asarray(pressure_atm, dtype=float)
    p11 = (T11 / T0) ** (G0 / (R_AIR * LAPSE))
    p20 = p11 * np.exp(-G0 * 9000 / (R_AIR * T11))
    if not np.isfinite(pressure).all() or np.any(pressure < p20) or np.any(pressure > 1):
        raise ValueError("pressure is outside the implemented atmosphere")
    height = np.where(pressure >= p11,
                      T0 / LAPSE * (1 - pressure ** (R_AIR * LAPSE / G0)),
                      11000 - R_AIR * T11 / G0 * np.log(pressure / p11))
    return height / 0.3048
