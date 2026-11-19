"""Symptomatic DCS by a specified time at a constant subatmospheric pressure.

NASA/TP-2020-220529, equations 4 and 7. The latter reproduces Conkin et al.
1996. Both inputs and probabilities describe chamber-like research scenarios.
"""
import math
from typing import Literal

from pydantic import Field

from tinydcs.eva_contract import ScientificInput


class HypobaricScenario(ScientificInput):
    plateauPressurePsia: float = Field(gt=0)
    elapsedPlateauHours: float = Field(ge=0)
    depressurizationMinutes: float = Field(gt=0)
    singleConstantPlateau: bool
    # A source-compatible modeled compartment at arrival, never a live SpO2
    # value or the current tissue/ambient ratio partway through the plateau.
    arrivalTissueN2Psia: float | None = Field(default=None, gt=0)
    ambulationAtPlateau: bool | None = None
    bmiKgM2: float | None = Field(default=None, gt=0)
    sourceRepressurizationProtocol: bool | None = None
    maleReferenceCohort: bool | None = None


class HypobaricResult(ScientificInput):
    model: Literal["NASA-2020-Eq4", "Conkin-1996-Eq7"] | None = None
    pDcsPercent: float | None = None
    elapsedPlateauHours: float
    reason: str | None = None
    endpoint: str = "Symptomatic DCS equation projection using supplied arrival nitrogen"
    evidenceClass: Literal["equation_projection"] = "equation_projection"
    protocolEligibilityChecked: Literal[False] = False
    researchUseOnly: bool = True


def probability(s: HypobaricScenario) -> HypobaricResult:
    def unavailable(reason: str) -> HypobaricResult:
        return HypobaricResult(elapsedPlateauHours=s.elapsedPlateauHours, reason=reason)

    p2 = s.plateauPressurePsia
    hours = s.elapsedPlateauHours
    if not s.singleConstantPlateau or not 5 <= s.depressurizationMinutes <= 30:
        return unavailable("Requires a 5–30 minute depressurization to a single constant plateau.")
    if not 4 <= p2 <= 7.5:
        return unavailable("Outside the implemented chamber pressure range (4.0–7.5 psia).")
    if s.arrivalTissueN2Psia is None or s.ambulationAtPlateau is None:
        return unavailable("Supply tissue nitrogen at plateau arrival and the chamber ambulation condition.")
    tr = s.arrivalTissueN2Psia / p2
    if p2 <= 5:
        if not 2 <= hours <= 6 or not .92 <= tr <= 2.02:
            return unavailable("Outside the Eq. 4 time or tissue-ratio range used here.")
        if s.bmiKgM2 is None or not 18 <= s.bmiKgM2 <= 30 or s.sourceRepressurizationProtocol is None:
            return unavailable("Eq. 4 requires a BMI from 18 to 30 and an explicit repressurization history.")
        if s.sourceRepressurizationProtocol and not math.isclose(p2, 4.3):
            return unavailable("The source repressurization protocol ends at 4.3 psia.")
        model = "NASA-2020-Eq4"
        log_odds = (math.log(hours) - 9.177 + 4.418*tr + .911*s.ambulationAtPlateau
                    - .0647*s.bmiKgM2 - .593*s.sourceRepressurizationProtocol) / .750
        percent = 100 / (1 + math.exp(-log_odds))
    else:
        if s.maleReferenceCohort is not True:
            return unavailable("Eq. 7 was fitted to male exposures. Select that reference population explicitly.")
        if s.sourceRepressurizationProtocol is not False:
            return unavailable("This Eq. 7 implementation requires a simple exposure without staged repressurization.")
        if not 2 <= hours <= 4 or not 1.23 <= tr <= 1.78:
            return unavailable("Outside the Eq. 7 time or tissue-ratio range used here.")
        model = "Conkin-1996-Eq7"
        stress = (s.arrivalTissueN2Psia + 1.563)/p2 - 1
        odds = stress**4.366 * (1 + 1.578*s.ambulationAtPlateau) * (.063*hours)**1.521
        percent = 100 * odds/(1 + odds)
    return HypobaricResult(model=model, pDcsPercent=percent, elapsedPlateauHours=hours)
