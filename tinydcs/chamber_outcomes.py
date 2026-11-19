"""Build explicit chamber histories from the same compact input in both applications."""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import Field, model_validator
from tinydcs.aviation_models import APPENDIX_A, TABLE5, evaluate
from tinydcs.chamber_equations import NASA_REPORT, SIMPLE_OXYGEN
from tinydcs.eva_contract import ScientificInput
from tinydcs.exposure import PA_PER_PSIA, ExposureProfile, Pressure
from tinydcs.study_models import study_comparisons

VERSION = "1.0.0"
TRAINING = "aviation_training"
TARGETS = (
    ("symptomatic_dcs", "Symptomatic DCS"),
    ("vge", "Any Doppler-detected VGE"),
    ("grade_iv_vge", "Grade IV VGE"),
)


class OutcomeInputs(ScientificInput):
    protocol_id: Literal[
        "nasa_2020_simple_oxygen",
        "nasa_2020_appendix_a_rest",
        "nasa_2020_table5",
        "aviation_training",
    ]
    altitude_ft: float | None = Field(default=None, ge=0, le=20000 / 0.3048)
    plateau_pressure_psia: float | None = Field(default=None, gt=0, le=17)
    starting_pressure_psia: float = Field(gt=0, le=17)
    time_at_altitude_min: float = Field(gt=0, le=1440)
    prebreathing_min: float = Field(ge=0, le=1440)
    ascent_min: float = Field(gt=0, le=1440)
    activity: Literal["ambulatory", "adynamic"]
    age_years: float | None = Field(default=None, gt=0, le=120)
    bmi_kg_m2: float | None = Field(default=None, gt=0, le=150)
    source_sex: Literal["male", "female"] | None = None
    oxygen_interrupted: bool

    def plateau(self):
        if self.altitude_ft is not None:
            return Pressure(kind="pressure_altitude", value=self.altitude_ft, unit="ft")
        return Pressure(kind="absolute", value=self.plateau_pressure_psia, unit="psia")

    @model_validator(mode="after")
    def verify_pressures(self):
        if (self.altitude_ft is None) == (self.plateau_pressure_psia is None):
            raise ValueError(
                "Supply exactly one of altitude_ft and plateau_pressure_psia."
            )
        if self.plateau().pascals() >= self.starting_pressure_psia * PA_PER_PSIA:
            raise ValueError("Plateau pressure must be below starting pressure.")
        return self


def protocols():
    common = dict(
        altitude_ft=None,
        plateau_pressure_psia=4.3,
        starting_pressure_psia=14.7,
        time_at_altitude_min=240,
        prebreathing_min=225,
        ascent_min=15,
        activity="ambulatory",
        age_years=32,
        bmi_kg_m2=24,
        source_sex="male",
        oxygen_interrupted=False,
    )
    options = [
        (
            SIMPLE_OXYGEN,
            "NASA resting oxygen chamber",
            "Resting oxygen at sea level and during ascent; one constant-pressure plateau with the source exercise pattern.",
            {},
        ),
        (
            APPENDIX_A,
            "NASA Appendix A resting example",
            "60 minutes of resting oxygen, 15 minutes ascending on oxygen and four hours at 6.0 psia.",
            dict(plateau_pressure_psia=6, prebreathing_min=60),
        ),
        (
            TABLE5,
            "NASA Table 5 chamber example",
            "Published four-hour male reference at 6.5 psia after 115 minutes of resting oxygen plus 30 minutes ascending on oxygen.",
            dict(plateau_pressure_psia=6.5, prebreathing_min=115, ascent_min=30),
        ),
        (
            TRAINING,
            "Aviation training on air",
            "An air-breathing training plateau. Published NASA oxygen-chamber probabilities do not cover this exposure or post-return events.",
            dict(
                altitude_ft=25000,
                plateau_pressure_psia=None,
                time_at_altitude_min=10,
                prebreathing_min=30,
                activity="adynamic",
                age_years=None,
                bmi_kg_m2=None,
                source_sex=None,
            ),
        ),
    ]
    return {
        "version": VERSION,
        "source_url": NASA_REPORT,
        "protocols": [
            dict(
                id=key,
                label=label,
                description=desc,
                defaults=OutcomeInputs(
                    **(common | changes), protocol_id=key
                ).model_dump(),
            )
            for key, label, desc, changes in options
        ],
    }


def _profile(inputs):
    start = dict(kind="absolute", value=inputs.starting_pressure_psia, unit="psia")
    plateau = inputs.plateau().model_dump(exclude_none=True)
    air = dict(
        basis="dry",
        oxygen_fraction=0.21,
        nitrogen_fraction=0.79,
        delivery_method="ambient",
    )
    oxygen = dict(
        basis="dry", oxygen_fraction=1.0, nitrogen_fraction=0.0, delivery_method="mask"
    )
    rest = dict(type="rest", ambulation=False, posture="semi_recumbent")
    ambulatory = inputs.activity == "ambulatory"
    task = dict(
        type="simulated_eva",
        ambulation=ambulatory,
        posture="standing" if ambulatory else "semi_recumbent",
        exercise_mode="source_simulated_eva",
    )
    training = inputs.protocol_id == TRAINING
    pb = inputs.prebreathing_min
    arrival = pb + inputs.ascent_min

    def leg(phase, first, last, p0, p1, gas, activity):
        return dict(
            id=phase,
            phase=phase,
            start=first,
            end=last,
            start_pressure=p0,
            end_pressure=p1,
            gas=gas,
            activity=activity,
            interpolation="linear_pressure" if phase == "ascent" else "constant",
            provenance="Declared chamber scenario",
        )

    segments = []
    if pb:
        segments.append(
            leg(
                "prebreathe",
                0,
                pb,
                start,
                start,
                None if inputs.oxygen_interrupted else oxygen,
                rest,
            )
        )
    ascent_gas = air if training else oxygen
    if inputs.oxygen_interrupted:
        ascent_gas = None  # interruption timing and actual delivery are unknown
    segments.append(leg("ascent", pb, arrival, start, plateau, ascent_gas, rest))
    segments.append(
        leg(
            "plateau",
            arrival,
            arrival + inputs.time_at_altitude_min,
            plateau,
            plateau,
            air if training else oxygen,
            rest if training and not ambulatory else task,
        )
    )
    return dict(
        schema_version="1.0.0",
        profile_id="hypobaric-reference",
        purpose="research",
        provenance="Declared protocol scenario",
        time_unit="min",
        initial_state=dict(
            method="assumed_equilibrium",
            body_pressure=start,
            gas=air,
            provenance="Assumed equilibrium breathing dry ordinary air at entered site pressure",
        ),
        history=dict(recent_diving=False, previous_altitude_exposure=False),
        person_covariates=dict(
            age_years=inputs.age_years,
            bmi_kg_m2=inputs.bmi_kg_m2,
            source_sex=inputs.source_sex,
        ),
        segments=segments,
    )


def predict_outcomes(inputs: OutcomeInputs) -> dict:
    inputs = OutcomeInputs.model_validate(
        inputs.model_dump() if isinstance(inputs, OutcomeInputs) else inputs
    )
    raw = inputs.model_dump(mode="json")
    fingerprint = hashlib.sha256(
        json.dumps(raw, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    profile = _profile(inputs)
    pressure = inputs.plateau().pascals() / PA_PER_PSIA
    outcomes = []
    first_physiology = None
    for endpoint, label in TARGETS:
        population = "nasa_hypobaric_chamber"
        if (
            endpoint == "symptomatic_dcs"
            and pressure > 5
            and inputs.source_sex == "male"
        ):
            population = "male_hypobaric_chamber"
        source_model = {"vge": "nasa_2020_eq5", "grade_iv_vge": "nasa_2020_eq6"}.get(
            endpoint, "conkin_1996_eq7" if pressure > 5 else "nasa_2020_eq4"
        )
        request = dict(
            model_id=source_model,
            endpoint=endpoint,
            window="during_plateau",
            source_protocol=inputs.protocol_id,
            horizon_minutes=inputs.time_at_altitude_min,
            reference_population=population,
            prediction_origin="plateau_arrival",
        )
        result = evaluate(
            ExposureProfile.model_validate(profile | {"prediction_request": request})
        )
        if first_physiology is None:
            first_physiology = result["physiology"]
        outcomes.append(
            dict(
                id=endpoint,
                label=label,
                model_id=result["model_id"],
                coefficient_version=result["coefficient_version"],
                model_digest=result["artifact_hash"],
                probability_fraction=result["probability_fraction"],
                applicability=result["applicability"],
                endpoint=result["outcome_ascertainment"],
                window=f"From plateau arrival through {inputs.time_at_altitude_min:g} minutes at test pressure",
                population=result["source_population"],
                source_url=NASA_REPORT,
                evidence_class=result["evidence_class"],
                uncertainty=dict(
                    status=result["uncertainty"]["status"],
                    detail=result["uncertainty"]["reason"],
                ),
            )
        )
    n2_pa = first_physiology["arrival_nitrogen_pa"]
    n2 = n2_pa / PA_PER_PSIA if n2_pa is not None else None
    assumptions = [
        "Initial equilibrium on ordinary air at the entered body pressure; no recent diving or earlier altitude exposure.",
        "Resting prebreathing time excludes ascent. The calculation includes the ascent once.",
        "Source sex is the binary covariate recorded in these historical studies.",
        "Estimates concern the specified chamber reference and plateau time. Follow-up after return requires separate outcomes.",
    ]
    if inputs.protocol_id == TRAINING:
        assumptions.append(
            "Air during ascent and the plateau; a training exposure is outside the oxygen-chamber source protocol."
        )
    else:
        assumptions.append(
            "Resting, semi-recumbent oxygen preparation and ascent, with oxygen and the source exercise pattern at the plateau."
        )
    if inputs.oxygen_interrupted:
        assumptions.append(
            "Gas and timing during the reported interruption are unknown. Arrival nitrogen is unavailable."
        )
    physiology = dict(
        plateau_pressure_psia=pressure,
        arrival_tissue_n2_psia=n2,
        arrival_tissue_ratio=n2 / pressure if n2 is not None else None,
    )
    comparisons = study_comparisons(inputs, physiology, outcomes)
    return dict(
        version=VERSION,
        inputs=raw,
        input_fingerprint=fingerprint,
        assumptions=assumptions,
        outcomes=outcomes + comparisons,
        clinical_individual_probability_available=False,
        physiology=physiology,
    )
