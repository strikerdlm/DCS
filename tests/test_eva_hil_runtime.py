"""Replay-based hardware-in-the-loop smoke tests for tablet/wearable runtime."""

from __future__ import annotations

import json
import time

from tinydcs.eva import simulation_response
from tests.test_eva import eva_scenario


def test_tablet_class_replay_runtime_and_payload_size() -> None:
    scenario = eva_scenario()
    telemetry = [
        {"kind": "pressure", "value": 5.8, "unit": "psia", "source": "tablet-pressure", "confidence": 0.96},
        {"kind": "accelerometer", "x": 0.1, "y": 0.2, "z": 1.3, "unit": "g", "source": "tablet-imu", "confidence": 0.88},
        {"kind": "heart_rate", "value": 128, "unit": "bpm", "source": "wearable-hr", "confidence": 0.9},
        {"kind": "hrv", "value": 36, "unit": "rmssd_ms", "source": "wearable-hrv", "confidence": 0.86},
        {"kind": "spo2", "value": 96, "unit": "%", "source": "wearable-spo2", "confidence": 0.91},
        {"kind": "skin_temperature", "value": 34.8, "unit": "c", "source": "wearable-temp", "confidence": 0.85},
    ]
    started = time.perf_counter()
    response = simulation_response(scenario, mission_rule_profile="artemis_lunar", telemetry=telemetry)
    elapsed_ms = (time.perf_counter() - started) * 1000
    encoded = json.dumps(response).encode("utf-8")

    assert elapsed_ms < 500
    assert len(encoded) < 1_000_000
    assert response["result"]["telemetryStatus"]["accepted"] == len(telemetry)
    assert response["result"]["timeline"][-1]["timeMin"] == scenario["evaDurationMin"]
