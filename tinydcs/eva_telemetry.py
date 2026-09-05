"""Unit-checked, timestamped telemetry; unvalidated proxies remain indicators."""

from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from typing import Any, Mapping
from mechanistic.atmosphere import KPA_PER_PSIA, MMHG_PER_PSIA, PSIA_PER_ATM


@dataclass(frozen=True)
class NormalizedTelemetrySample:
    kind: str
    value: float
    unit: str
    source: str
    confidence: float
    timestamp_sec: float | None


@dataclass
class TelemetryAdjustment:
    accepted: int = 0
    rejected: int = 0
    warnings: list[str] = field(default_factory=list)
    suit_pressure_psia: float | None = None
    habitat_pressure_psia: float | None = None
    mean_vo2_ml_kg_min: float | None = None
    peak_vo2_ml_kg_min: float | None = None
    spo2_percent: float | None = None
    heart_rate_bpm: float | None = None
    hrv_rmssd_ms: float | None = None
    skin_temp_c: float | None = None
    raw_indicators: list[dict] = field(default_factory=list)

    @classmethod
    def empty(cls):
        return cls()

    def to_dict(self):
        return {
            "accepted": self.accepted,
            "rejected": self.rejected,
            "warnings": self.warnings,
            "suitPressurePsia": self.suit_pressure_psia,
            "habitatPressurePsia": self.habitat_pressure_psia,
            "meanVo2MlKgMin": self.mean_vo2_ml_kg_min,
            "peakVo2MlKgMin": self.peak_vo2_ml_kg_min,
            "spo2Percent": self.spo2_percent,
            "heartRateBpm": self.heart_rate_bpm,
            "hrvRmssdMs": self.hrv_rmssd_ms,
            "skinTempC": self.skin_temp_c,
            "rawIndicators": self.raw_indicators,
        }


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        value = float(value)
    except (ValueError, TypeError):
        return None
    return value if math.isfinite(value) else None


def normalize_sample(sample: Mapping[str, Any]):
    kind, unit = str(sample.get("kind", "")).lower(), str(sample.get("unit", "")).lower()
    value = _number(sample.get("value"))
    confidence = _number(sample.get("confidence", 1))
    timestamp = _number(sample.get("timestampSec"))
    if confidence is None or not 0 <= confidence <= 1:
        return None
    if kind in {"pressure", "suit_pressure", "habitat_pressure"}:
        factors = {
            "psia": 1,
            "kpa": 1 / KPA_PER_PSIA,
            "mmhg": 1 / MMHG_PER_PSIA,
            "torr": 1 / MMHG_PER_PSIA,
            "atm": PSIA_PER_ATM,
        }
        if value is None or unit not in factors:
            return None
        value, unit = value * factors[unit], "psia"
        if not 0 < value <= 30:
            return None
    elif kind == "workload":
        if (
            value is None
            or unit not in {"vo2_ml_kg_min", "ml/kg/min", "vo2"}
            or not 0 <= value <= 120
        ):
            return None
        unit = "mL/kg/min"
    elif kind in {"activity", "accelerometer"}:
        if unit in {"cpm", "counts_per_min"} and value is not None and value >= 0:
            kind, unit = "activity_counts", "counts/min"
        elif unit in {"g", "mg", "milli-g", "millig"}:
            xyz = [_number(sample.get(axis)) for axis in ("x", "y", "z")]
            if any(v is None for v in xyz):
                return None
            value = math.hypot(*xyz) / (1 if unit == "g" else 1000)
            kind, unit = "acceleration_magnitude", "g"
        else:
            return None
    elif kind in {"hr", "heart_rate"}:
        if value is None or unit != "bpm" or not 0 < value <= 300:
            return None
        kind = "heart_rate"
    elif kind == "hrv":
        if value is None or unit not in {"rmssd_ms", "ms"} or not 0 <= value <= 1000:
            return None
        unit = "rmssd_ms"
    elif kind == "spo2":
        if value is None or unit not in {"%", "percent", "fraction"}:
            return None
        value = value * 100 if unit == "fraction" else value
        if not 0 <= value <= 100:
            return None
        unit = "percent"
    elif kind in {"skin_temperature", "skin_temp", "temperature"}:
        if value is None:
            return None
        if unit in {"f", "fahrenheit", "degf"}:
            value = (value - 32) * 5 / 9
        elif unit not in {"c", "celsius", "degc"}:
            return None
        if not 0 <= value <= 60:
            return None
        kind, unit = "skin_temperature", "celsius"
    else:
        return None
    return NormalizedTelemetrySample(
        kind, value, unit, str(sample.get("source") or "unspecified"), confidence, timestamp
    )


def apply_telemetry_adjustment(scenario, samples, mission_rules, *, now_sec=None):
    """Apply fresh pressure/SpO2 measurements only; retain other raw indicators.

    No acceleration-to-VO2 or skin-temperature-to-cooling calibration is assumed.
    Timestamp-less, future, stale and low-confidence samples cannot update state.
    """
    adjustment = TelemetryAdjustment()
    now = time.time() if now_sec is None else now_sec
    if not math.isfinite(now):
        raise ValueError("finite telemetry reference time required")
    settings = mission_rules.get("telemetry", {})
    latest, workloads = {}, []
    for raw in samples:
        normalized = normalize_sample(raw)
        if normalized is None:
            adjustment.rejected += 1
            adjustment.warnings.append(
                f"Unsupported or malformed telemetry sample: {raw.get('kind', 'unknown')}"
            )
            continue
        if normalized.confidence < settings.get("min_confidence", 0.5):
            adjustment.rejected += 1
            adjustment.warnings.append(
                f"Low-confidence telemetry sample ignored: {normalized.kind}"
            )
            continue
        if (
            normalized.timestamp_sec is None
            or not 0 <= now - normalized.timestamp_sec <= settings.get("max_sample_age_sec", 120)
        ):
            adjustment.rejected += 1
            adjustment.warnings.append(
                f"Unverified timestamp, stale or future telemetry ignored: {normalized.kind}"
            )
            continue
        adjustment.accepted += 1
        kind = normalized.kind
        if kind == "pressure":
            kind = settings.get("pressure_source", "suit") + "_pressure"
        if kind not in latest or normalized.timestamp_sec >= latest[kind].timestamp_sec:
            latest[kind] = normalized
        adjustment.raw_indicators.append(
            {
                "kind": kind,
                "value": normalized.value,
                "unit": normalized.unit,
                "source": normalized.source,
                "timestampSec": normalized.timestamp_sec,
            }
        )
        if kind == "workload":
            workloads.append(normalized.value)
    for kind, attribute in [
        ("suit_pressure", "suit_pressure_psia"),
        ("habitat_pressure", "habitat_pressure_psia"),
        ("spo2", "spo2_percent"),
        ("heart_rate", "heart_rate_bpm"),
        ("hrv", "hrv_rmssd_ms"),
        ("skin_temperature", "skin_temp_c"),
    ]:
        if kind in latest:
            setattr(adjustment, attribute, latest[kind].value)
    if adjustment.suit_pressure_psia is not None:
        if scenario.get("pressureSegments"):
            adjustment.warnings.append(
                "Pressure snapshot displayed; explicit mission pressure schedule retained."
            )
        else:
            scenario["suit"]["pressurePsia"] = adjustment.suit_pressure_psia
    if adjustment.habitat_pressure_psia is not None:
        scenario["habitat"]["pressurePsia"] = adjustment.habitat_pressure_psia
    if adjustment.spo2_percent is not None:
        scenario["crew"]["spo2Percent"] = adjustment.spo2_percent
    if workloads:
        adjustment.mean_vo2_ml_kg_min = sum(workloads) / len(workloads)
        adjustment.peak_vo2_ml_kg_min = max(workloads)
        adjustment.warnings.append(
            "Measured VO2 samples displayed; a snapshot does not replace the mission workload schedule."
        )
    if "acceleration_magnitude" in latest or "activity_counts" in latest:
        adjustment.warnings.append(
            "Acceleration/activity remains a raw indicator; no validated VO2 conversion supplied."
        )
    return adjustment
