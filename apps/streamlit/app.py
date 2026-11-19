"""Streamlit research views of the same versioned DCS core and bundle as the API."""

import json
from pathlib import Path

import streamlit as st
from fastapi import HTTPException
from pydantic import ValidationError

from tinydcs.api import workbook_evaluation, workbook_prediction
from tinydcs.aviation_models import evaluate
from tinydcs.eva import RutReconciliationStatus
from tinydcs.exposure import ExposureProfile
from tinydcs.label_bundle import LabelInput

EXAMPLE = Path(__file__).resolve().parents[2] / "docs/examples/aviation-table5.json"


def aviation_view():
    st.header("Aviation exposure profile")
    st.write(
        "Edit the pressure, gas and activity history and its requested endpoint. "
        "The supplied example reproduces a published NASA Table 5 chamber scenario at 6.5 psia."
    )
    initial = EXAMPLE.read_text(encoding="utf-8") if EXAMPLE.is_file() else ""
    text = st.text_area("Exposure profile JSON", value=initial, height=260)
    if not st.button("Evaluate profile", type="primary"):
        return
    try:
        profile = ExposureProfile.model_validate_json(text)
        result = evaluate(profile)
    except ValidationError as exc:
        issues = [
            f"{'.'.join(map(str, e['loc'])) or 'profile'} — {e['msg']}"
            for e in exc.errors(include_input=False, include_context=False)
        ]
        st.error("Invalid exposure profile. " + " · ".join(issues))
        return
    except ValueError as exc:
        st.error(f"Profile evaluation unavailable. {exc}")
        return

    applicability = result["applicability"]
    if (
        result["evidence_class"] == "published_reference"
        and result["quantitative_output_enabled"]
        and applicability["status"] == "supported"
        and not result["inherited_vetoes"]
        and result["probability_fraction"] is not None
    ):
        st.metric("Published reference probability", f"{result['probability_fraction']:.3%}")
    elif applicability["reasons"]:
        st.warning("Probability unavailable. " + ", ".join(applicability["reasons"]))
    st.caption(
        f"Endpoint {result['endpoint']} · Origin {result['prediction_origin']} · "
        f"Horizon {result['horizon_minutes']:g} min · Window {result['outcome_window']}"
    )
    st.write(f"Outcome ascertainment: {result['outcome_ascertainment']}")
    st.write(f"Uncertainty: {result['uncertainty']['status']}")
    st.subheader("Physiological exposure")
    physiology = result["physiology"]
    st.caption(f"{physiology['kinetics']} · {physiology['gas_convention']}")
    for field, label in (
        ("arrival_nitrogen_pa", "Tissue nitrogen at arrival (kPa)"),
        ("plateau_exit_nitrogen_pa", "Tissue nitrogen at plateau exit (kPa)"),
    ):
        value = physiology[field]
        st.metric(label, "Unavailable" if value is None else f"{value / 1000:.3f}")
    for assumption in result["assumptions"]:
        st.caption(assumption)
    st.caption(
        f"Model {result['model_id']} · Version {result['model_version']} · "
        f"Coefficients {result['coefficient_version']} · Core {result['core_version']}"
    )
    st.caption(f"Input fingerprint: {result['input_fingerprint']}")
    st.caption(f"Equation manifest SHA-256: {result['artifact_hash']}")
    with st.expander("Source, applicability and complete result"):
        st.write(result["source"])
        st.json(result, expanded=False)
    st.download_button(
        "Download exposure result",
        json.dumps(result, indent=2),
        "aviation-result.json",
        "application/json",
    )


def workbook_view():
    st.header("Workbook label study")
    st.write(
        "The model estimates a recorded workbook fraction. The origin of the labels is unverified."
    )
    try:
        evaluation = workbook_evaluation()
    except HTTPException as exc:
        st.warning(f"Workbook model and evaluation unavailable. {exc.detail}")
        return
    altitude = st.number_input("Altitude (ft)", min_value=0, value=30000)
    prebreathe = st.number_input("Prebreathing time (min)", min_value=0, value=0)
    duration = st.number_input("Time at altitude (min)", min_value=0, value=60)
    level = st.selectbox("Exercise level", ["Rest", "Mild", "Heavy"])
    if st.button("Estimate workbook label", type="primary"):
        try:
            result = workbook_prediction(
                LabelInput(
                    altitude_ft=altitude,
                    prebreathing_min=prebreathe,
                    time_at_altitude_min=duration,
                    exercise_level=level,
                )
            )
        except (HTTPException, ValueError):
            st.error("Workbook estimate unavailable. The service could not verify this prediction.")
            return
        if result["artifact_hash"] != evaluation["artifact_hash"]:
            st.warning("The model changed during evaluation. Submit the current inputs again.")
            return
        if (
            result["quantitative_output_enabled"]
            and result["applicability"]["status"] == "supported"
        ):
            st.metric("Estimated workbook label", f"{result['predicted_label_fraction']:.2%}")
            interval = result["uncertainty"]
            if interval["status"] == "available":
                st.write(
                    f"Nominal {interval['level']:.0%} workbook-label interval for a complete profile: "
                    f"{interval['lower']:.2%} to {interval['upper']:.2%}."
                )
                st.caption(f"Interval method: {interval['method']}")
        else:
            st.warning(
                "Workbook estimate unavailable. " + ", ".join(result["applicability"]["reasons"])
            )
        st.caption(
            f"Endpoint {result['endpoint']} · Time at altitude {result['horizon_minutes']:g} min"
        )
        st.caption(f"Input fingerprint: {result['input_fingerprint']}")
    st.caption(
        f"Model {evaluation['model_id']} · Version {evaluation['model_version']} · "
        f"Bundle SHA-256 {evaluation['artifact_hash']}"
    )
    st.subheader("Held-out workbook evaluation")
    report = evaluation["report"]
    try:
        metrics = report["final_test"]["metrics"]
        coverage = report["final_test"]["interval_coverage"]
        st.write(
            f"{metrics['n_rows']} rows from {metrics['n_profiles']} held-out profiles. "
            f"Mean absolute error {metrics['mae_pp']:.3f} percentage points. "
            f"Root mean squared error {metrics['rmse_pp']:.3f} percentage points."
        )
        st.write(
            f"The label interval covered {coverage['profiles_covered']} of "
            f"{metrics['n_profiles']} complete profiles."
        )
    except (KeyError, TypeError, ValueError):
        st.warning("Summary metrics unavailable for this evaluation schema.")
    with st.expander("Saved evaluation report"):
        st.json(report, expanded=False)
    st.download_button(
        "Download workbook evaluation",
        json.dumps(evaluation, indent=2),
        "workbook-evaluation.json",
        "application/json",
    )


def main():
    st.set_page_config(page_title="DCS exposure research", layout="centered")
    st.title("DCS exposure research")
    st.info(
        "Individual clinical DCS probability is unavailable. Source-reference results and workbook labels have separate endpoints."
    )
    view = st.sidebar.radio("Research view", ["Aviation profile", "Workbook labels", "3RUT-MBe1"])
    if view == "Aviation profile":
        aviation_view()
    elif view == "Workbook labels":
        workbook_view()
    else:
        st.header("3RUT-MBe1 reconciliation")
        state = RutReconciliationStatus().to_dict()
        st.warning(state["reason"])
        st.json(state, expanded=False)


if __name__ == "__main__":
    main()
