"""Validation gate for quantitative 3RUT-MBe1 risk use."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RutBenchmarkProfile:
    profile_id: str
    description: str
    expected_risk_percent_range: tuple[float, float]


BENCHMARK_PROFILES: tuple[RutBenchmarkProfile, ...] = (
    RutBenchmarkProfile("A", "90 min O2 prebreathe, 35 kft, light exercise, 180 min exposure", (20.0, 30.0)),
    RutBenchmarkProfile("B", "30 min O2 prebreathe, 25 kft, heavy exercise, 240 min exposure", (40.0, 60.0)),
    RutBenchmarkProfile("C", "15 min O2 prebreathe, 22.5 kft, heavy exercise, 240 min exposure", (50.0, 70.0)),
    RutBenchmarkProfile("D", "0 min prebreathe, 18 kft, heavy exercise, 360 min exposure", (30.0, 50.0)),
    RutBenchmarkProfile("E", "75 min O2 prebreathe, 30 kft, rest, 240 min exposure", (10.0, 20.0)),
)

SOURCE_EQUATION_CHECKLIST: tuple[str, ...] = (
    "ambient_pressure_scaling",
    "tissue_n2_half_time",
    "supersaturation_terms",
    "bubble_number_density",
    "bubble_radius_update",
    "integrated_hazard",
    "final_probability_mapping",
    "time_step_invariance",
    "ascent_segment_handling",
    "lambda_normalization",
)


def rut_absolute_risk_enabled() -> bool:
    """Return whether 3RUT-MBe1 may be used as an absolute risk source."""

    return False


def assert_rut_absolute_risk_enabled() -> None:
    """Raise until source-equation and benchmark reconciliation is complete."""

    if not rut_absolute_risk_enabled():
        raise RuntimeError(
            "3RUT-MBe1 absolute-risk use is disabled until source-equation and "
            "benchmark-profile reconciliation passes."
        )
