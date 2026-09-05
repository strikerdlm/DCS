"""Validation gate for quantitative 3RUT-MBe1 risk use."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RutBenchmarkProfile:
    profile_id: str
    description: str
    expected_risk_percent_range: tuple[float, float] | None = None
    evidence_status: str = "full_source_profile_not_reconstructed"


BENCHMARK_PROFILES: tuple[RutBenchmarkProfile, ...] = (
    *(RutBenchmarkProfile(key, f"Source MV-{key}: exact schedules and endpoint require reconstruction")
      for key in "ABCDE"),
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
