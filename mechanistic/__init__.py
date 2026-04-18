"""Mechanistic (physics-informed) altitude-DCS risk models.

This package exposes the three published mechanistic models this repository
depends on for surrogate modelling, ablations, and external comparisons:

* :mod:`mechanistic.rut_mbe1` — Single-compartment 3RUT-MBe1 bubble-dynamics
  model (Gerth et al., NEDU TR 18-01, 2018). **Calibration reconciliation in
  progress** — see ``docs/methods.md``.
* :mod:`mechanistic.conkin_nasa` — Conkin NASA RM/NM logistic models with
  exercise tissue ratio (Eq. 14/15 of TP-2004-213158).
* :mod:`mechanistic.adrac` — Closed-form log-logistic ADRAC surrogate
  (Kannan–Pilmanis 1998 / Pilmanis 2004), fitted to the USAF
  DCS_Risk_DB_2025 grid.

Only the public classes/functions are re-exported here. Import the submodule
directly for internal helpers.
"""

from .adrac import AdracModel, altitude_ft_to_mmhg, fit_adrac  # noqa: F401
from .rut_mbe1 import ModelParameters, ModelState, ProfileSegment, RutMbe1Model  # noqa: F401

__all__ = [
    "AdracModel",
    "ModelParameters",
    "ModelState",
    "ProfileSegment",
    "RutMbe1Model",
    "altitude_ft_to_mmhg",
    "fit_adrac",
]
