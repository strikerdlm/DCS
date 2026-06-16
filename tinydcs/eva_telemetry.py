"""Telemetry adapters for EVA scenario inputs.

Adapters normalize device-specific pressure, activity, and physiology samples
into small scenario adjustments. They are deliberately conservative: low
confidence or malformed samples are reported but ignored.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class NormalizedTelemetrySample:
    kind: str
    value: float
    unit: str
    source: str
    confidence: float = 1.0
    timestamp_sec: float | None = None


@dataclass
class TelemetryAdjustment:
    accepted: int = 0
    rejected: int = 0
    warnings: list[str] = field(default_factory=list)
    suit_pressure_psia: float | None = None
    mean_vo2_ml_kg_min: float | None = None
    peak_vo2_ml_kg_min: float | None = None
    spo2_percent: float | None = None
    heart_rate_bpm: float | None = None
    hrv_rmssd_ms: float | None = None
    skin_temp_c: float | None = None

    @classmethod
    def empty(cls) -> "TelemetryAdjustment":
        return cls()

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "rejected": self.rejected,
            "warnings": self.warnings,
            "suitPressurePsia": self.suit_pressure_psia,
            "meanVo2MlKgMin": self.mean_vo2_ml_kg_min,
            "peakVo2MlKgMin": self.peak_vo2_ml_kg_min,
            "spo2Percent": self.spo2_percent,
            "heartRateBpm": self.heart_rate_bpm,
            "hrvRmssdMs": self.hrv_rmssd_ms,
            "skinTempC": self.skin_temp_c,
        }


def _number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _confidence(sample: Mapping[str, Any]) -> float:
    value = _number(sample.get("confidence", 1.0))
    return 1.0 if value is None else max(0.0, min(1.0, value))


def _timestamp_sec(sample: Mapping[str, Any]) -> float | None:
    return _number(sample.get("timestampSec", sample.get("timestamp_sec")))


class PressureTelemetryAdapter:
    """Normalize pressure samples to psia."""

    supported_kinds = {"pressure", "suit_pressure", "habitat_pressure"}

    def normalize(self, sample: Mapping[str, Any]) -> NormalizedTelemetrySample | None:
        kind = str(sample.get("kind", "")).lower()
        if kind not in self.supported_kinds:
            return None
        value = _number(sample.get("value"))
        if value is None:
            return None
        unit = str(sample.get("unit", "psia")).lower()
        if unit == "psia":
            psia = value
        elif unit == "kpa":
            psia = value / 6.894757
        elif unit in {"mmhg", "torr"}:
            psia = value / 51.7149
        elif unit == "atm":
            psia = value * 14.6959
        else:
            return None
        return NormalizedTelemetrySample(
            kind="pressure",
            value=psia,
            unit="psia",
            source=str(sample.get("source", "pressure_adapter")),
            confidence=_confidence(sample),
            timestamp_sec=_timestamp_sec(sample),
        )


class AccelerometerWorkloadAdapter:
    """Estimate workload from acceleration magnitude or activity counts."""

    supported_kinds = {"accelerometer", "activity", "workload"}

    def normalize(self, sample: Mapping[str, Any]) -> NormalizedTelemetrySample | None:
        kind = str(sample.get("kind", "")).lower()
        if kind not in self.supported_kinds:
            return None
        unit = str(sample.get("unit", "")).lower()
        value = _number(sample.get("value"))
        if kind == "workload" and value is not None and unit in {"vo2_ml_kg_min", "ml/kg/min", "vo2"}:
            vo2 = value
        elif unit in {"counts_per_min", "cpm"} and value is not None:
            vo2 = 3.5 + min(42.0, max(0.0, value) / 135.0)
        else:
            x = _number(sample.get("x"))
            y = _number(sample.get("y"))
            z = _number(sample.get("z"))
            if x is None or y is None or z is None:
                return None
            magnitude_g = math.sqrt(x * x + y * y + z * z)
            if unit in {"mg", "milli-g", "millig"}:
                magnitude_g /= 1000.0
            dynamic_g = max(0.0, magnitude_g - 1.0)
            vo2 = 3.5 + min(46.0, dynamic_g * 28.0)
        return NormalizedTelemetrySample(
            kind="workload",
            value=max(3.5, vo2),
            unit="vo2_ml_kg_min",
            source=str(sample.get("source", "accelerometer_adapter")),
            confidence=_confidence(sample),
            timestamp_sec=_timestamp_sec(sample),
        )


class PhysiologyTelemetryAdapter:
    """Normalize HR, HRV, and SpO2 samples."""

    supported_kinds = {"heart_rate", "hr", "hrv", "spo2"}

    def normalize(self, sample: Mapping[str, Any]) -> NormalizedTelemetrySample | None:
        kind = str(sample.get("kind", "")).lower()
        if kind not in self.supported_kinds:
            return None
        value = _number(sample.get("value"))
        if value is None:
            return None
        if kind in {"heart_rate", "hr"}:
            normalized_kind = "heart_rate"
            unit = "bpm"
        elif kind == "hrv":
            normalized_kind = "hrv"
            unit = "rmssd_ms"
        else:
            normalized_kind = "spo2"
            unit = "percent"
        return NormalizedTelemetrySample(
            kind=normalized_kind,
            value=value,
            unit=unit,
            source=str(sample.get("source", "physiology_adapter")),
            confidence=_confidence(sample),
            timestamp_sec=_timestamp_sec(sample),
        )


class SkinTemperatureTelemetryAdapter:
    """Normalize skin temperature samples to Celsius."""

    supported_kinds = {"skin_temperature", "skin_temp", "temperature"}

    def normalize(self, sample: Mapping[str, Any]) -> NormalizedTelemetrySample | None:
        kind = str(sample.get("kind", "")).lower()
        if kind not in self.supported_kinds:
            return None
        value = _number(sample.get("value"))
        if value is None:
            return None
        unit = str(sample.get("unit", "c")).lower()
        if unit in {"c", "celsius", "degc"}:
            celsius = value
        elif unit in {"f", "fahrenheit", "degf"}:
            celsius = (value - 32.0) * 5.0 / 9.0
        else:
            return None
        return NormalizedTelemetrySample(
            kind="skin_temperature",
            value=celsius,
            unit="celsius",
            source=str(sample.get("source", "skin_temperature_adapter")),
            confidence=_confidence(sample),
            timestamp_sec=_timestamp_sec(sample),
        )


ADAPTERS = (
    PressureTelemetryAdapter(),
    AccelerometerWorkloadAdapter(),
    PhysiologyTelemetryAdapter(),
    SkinTemperatureTelemetryAdapter(),
)


def normalize_sample(sample: Mapping[str, Any]) -> NormalizedTelemetrySample | None:
    for adapter in ADAPTERS:
        normalized = adapter.normalize(sample)
        if normalized is not None:
            return normalized
    return None


def apply_telemetry_adjustment(
    scenario: dict[str, Any],
    samples: list[Mapping[str, Any]],
    mission_rules: Mapping[str, Any],
) -> TelemetryAdjustment:
    """Mutate ``scenario`` with valid telemetry-derived adjustments."""

    adjustment = TelemetryAdjustment.empty()
    min_confidence = float(mission_rules.get("telemetry", {}).get("min_confidence", 0.5))
    workload_values: list[float] = []

    for raw_sample in samples:
        normalized = normalize_sample(raw_sample)
        if normalized is None:
            adjustment.rejected += 1
            adjustment.warnings.append(f"Unsupported or malformed telemetry sample: {raw_sample.get('kind', 'unknown')}")
            continue
        if normalized.confidence < min_confidence:
            adjustment.rejected += 1
            adjustment.warnings.append(f"Low-confidence telemetry sample ignored: {normalized.kind}")
            continue
        adjustment.accepted += 1
        if normalized.kind == "pressure":
            adjustment.suit_pressure_psia = normalized.value
        elif normalized.kind == "workload":
            workload_values.append(normalized.value)
        elif normalized.kind == "spo2":
            adjustment.spo2_percent = normalized.value
        elif normalized.kind == "heart_rate":
            adjustment.heart_rate_bpm = normalized.value
        elif normalized.kind == "hrv":
            adjustment.hrv_rmssd_ms = normalized.value
        elif normalized.kind == "skin_temperature":
            adjustment.skin_temp_c = normalized.value

    if adjustment.suit_pressure_psia is not None:
        scenario["suit"]["pressurePsia"] = adjustment.suit_pressure_psia
    if workload_values:
        blend = float(mission_rules.get("telemetry", {}).get("workload_blend", 0.65))
        measured_mean = sum(workload_values) / len(workload_values)
        measured_peak = max(workload_values)
        scenario["meanVo2MlKgMin"] = (1.0 - blend) * scenario["meanVo2MlKgMin"] + blend * measured_mean
        scenario["peakVo2MlKgMin"] = max(
            scenario["meanVo2MlKgMin"],
            (1.0 - blend) * scenario["peakVo2MlKgMin"] + blend * measured_peak,
        )
        adjustment.mean_vo2_ml_kg_min = scenario["meanVo2MlKgMin"]
        adjustment.peak_vo2_ml_kg_min = scenario["peakVo2MlKgMin"]
    if adjustment.spo2_percent is not None:
        scenario["crew"]["spo2Percent"] = adjustment.spo2_percent
    if adjustment.skin_temp_c is not None:
        if adjustment.skin_temp_c >= 37.0:
            scenario["suit"]["coolingMargin"] = max(0.4, scenario["suit"]["coolingMargin"] - 0.08)
        elif adjustment.skin_temp_c <= 29.0:
            scenario["suit"]["coolingMargin"] = max(0.4, scenario["suit"]["coolingMargin"] - 0.04)

    # Return an isolated copy so callers cannot mutate stored status by accident.
    return copy.deepcopy(adjustment)
