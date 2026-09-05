"""Independent regression cases for published equations and physical limits."""

import numpy as np
import pytest

from mechanistic.adrac import AdracModel, altitude_ft_to_mmhg
from mechanistic.conkin_nasa import compute_p1n2, nitrogen_half_time


@pytest.mark.parametrize("lam, expected", [(0.025, 6.69), (0.030, 6.62)])
def test_nasa_table_17(lam, expected):
    # NASA TP-2004-213158, Table 17 (pp. 69-70), including the air break.
    pressure = 8.0
    for duration, vo2, inspired_n2 in [
        (3, 12.5, 0), (17, 25, 0), (3, 12.5, 0),
        (17, 10, 0), (20, 10, 8), (30, 4.7, 0),
    ]:
        pressure = compute_p1n2(pressure, inspired_n2, vo2, duration, lam)
    assert pressure == pytest.approx(expected, abs=0.02)


def test_nasa_rate_at_rest_uses_equation_6():
    assert nitrogen_half_time(0, 0.025) == pytest.approx(1 / 519.37, rel=1e-12)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1.0])
def test_nasa_rejects_invalid_exercise(value):
    with pytest.raises(ValueError):
        nitrogen_half_time(value, 0.025)


def test_adrac_zero_duration_is_exactly_zero_and_scalars_broadcast():
    model = AdracModel(1, 0, np.zeros(4))
    assert model.predict([25000, 30000], 0, "Rest", [0, 1]).tolist() == [0, 0.5]


@pytest.mark.parametrize("exercise", ["unknown", "", None])
def test_adrac_rejects_unknown_exercise(exercise):
    model = AdracModel(1, 0, np.zeros(4))
    with pytest.raises(ValueError):
        model.predict(25000, 0, exercise, 60)


def test_atmosphere_includes_isothermal_layer():
    # ICAO/US Standard Atmosphere: 11 km = 22632.06 Pa; 20 km = 5474.89 Pa.
    actual = altitude_ft_to_mmhg(np.array([0, 11000 / 0.3048, 20000 / 0.3048]))
    assert actual == pytest.approx(np.array([101325, 22632.06, 5474.89]) * 760 / 101325, rel=3e-5)


@pytest.mark.parametrize("altitude", [float("nan"), float("inf"), -100, 70000])
def test_atmosphere_rejects_outside_implemented_layers(altitude):
    with pytest.raises(ValueError):
        altitude_ft_to_mmhg(altitude)
