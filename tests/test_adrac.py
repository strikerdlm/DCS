"""Unit tests for mechanistic.adrac."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mechanistic.adrac import AdracModel, altitude_ft_to_mmhg, fit_adrac


def test_altitude_ft_to_mmhg_at_sea_level() -> None:
    assert altitude_ft_to_mmhg(np.array([0.0])) == pytest.approx(760.0, rel=1e-4)


def test_altitude_ft_to_mmhg_monotone() -> None:
    p = altitude_ft_to_mmhg(np.array([0, 10_000, 20_000, 40_000, 60_000], dtype=float))
    assert (np.diff(p) < 0).all()


def test_adrac_fit_recovers_monotonic_behaviour() -> None:
    """Fit on a tiny synthetic grid and verify the predictor respects
    the signs we expect from physiology:

      * Higher altitude -> higher P(DCS), all else equal.
      * Longer prebreathe -> lower P(DCS).
      * Heavy exercise -> higher P(DCS) than Rest.
    """
    rng = np.random.default_rng(0)
    rows = []
    for alt in (20_000, 25_000, 30_000, 35_000, 40_000):
        for pb in (0, 30, 60):
            for ex in ("Rest", "Mild", "Heavy"):
                for t in (30, 60, 120, 240):
                    p = alt / 50_000 + t / 400 + (0.1 if ex == "Mild" else 0.2 if ex == "Heavy" else 0.0) - pb / 200
                    p = float(np.clip(p + 0.01 * rng.standard_normal(), 0.02, 0.98))
                    rows.append({
                        "altitude": alt,
                        "prebreathing_time": pb,
                        "exercise_level": ex,
                        "time_at_altitude": t,
                        "risk_of_decompression_sickness": p * 100,
                    })
    df = pd.DataFrame(rows)
    model = fit_adrac(df)
    assert isinstance(model, AdracModel)
    assert model.beta_1 > 0

    base = dict(altitude_ft=25_000, prebreathe_min=30, exercise_level="Rest", time_at_altitude_min=120)
    p_base = model.predict(**{k: np.atleast_1d(v) for k, v in base.items()})[0]
    p_higher_alt = model.predict(**{**base, "altitude_ft": np.atleast_1d(35_000)})[0]
    p_longer_pb = model.predict(**{**base, "prebreathe_min": np.atleast_1d(60)})[0]
    p_heavy_ex = model.predict(**{**base, "exercise_level": np.atleast_1d("Heavy")})[0]

    assert p_higher_alt > p_base
    assert p_longer_pb < p_base
    assert p_heavy_ex > p_base


def test_adrac_predict_in_unit_interval() -> None:
    model = AdracModel(
        beta_1=1.0,
        beta_2=0.0,
        beta=np.array([-1e-3, -1e-2, 1.0, 2.0]),
    )
    p = model.predict(
        altitude_ft=np.array([25_000, 30_000]),
        prebreathe_min=np.array([30, 60]),
        exercise_level=np.array(["Rest", "Heavy"]),
        time_at_altitude_min=np.array([60, 120]),
    )
    assert p.shape == (2,)
    assert (p >= 0).all() and (p <= 1).all()
