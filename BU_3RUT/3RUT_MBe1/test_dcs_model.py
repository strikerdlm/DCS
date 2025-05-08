import unittest

from dcs_risk_model import FlightProfile, complete_run_simulation, compute_risk_probability

class TestDCSModel(unittest.TestCase):
    def test_total_flight_time(self):
        # Use known flight profile parameters
        preox = 30.0
        ascent_rate = 200.0
        cruise_alt = 3000.0
        plateau = 60.0
        exercise = 1.0
        # Expected total duration: preox + (cruise_alt/ascent_rate) + plateau = 30 + (3000/200) + 60 = 30 + 15 + 60 = 105 minutes
        profile = FlightProfile(preox, ascent_rate, cruise_alt, plateau, exercise)
        self.assertAlmostEqual(profile.total_duration, 105.0, places=2, msg="Total flight time should be 105 minutes")

    def test_risk_probability_range(self):
        # Test that risk probability is between 0 and 1
        preox = 30.0
        ascent_rate = 200.0
        cruise_alt = 3000.0
        plateau = 60.0
        exercise = 1.0
        profile = FlightProfile(preox, ascent_rate, cruise_alt, plateau, exercise)
        times, P_series, x_series = complete_run_simulation(profile, dt=0.1)
        x_final = x_series[-1]
        risk = compute_risk_probability(x_final)
        self.assertGreaterEqual(risk, 0, "Risk probability should be >= 0")
        self.assertLessEqual(risk, 1, "Risk probability should be <= 1")

    def test_exercise_influence(self):
        # Test that higher exercise intensity yields a higher risk probability
        preox = 30.0
        ascent_rate = 200.0
        cruise_alt = 3000.0
        plateau = 60.0
        # Low exercise intensity
        profile_low = FlightProfile(preox, ascent_rate, cruise_alt, plateau, 1.0)
        times_low, P_series_low, x_series_low = complete_run_simulation(profile_low, dt=0.1)
        risk_low = compute_risk_probability(x_series_low[-1])

        # High exercise intensity
        profile_high = FlightProfile(preox, ascent_rate, cruise_alt, plateau, 1.5)
        times_high, P_series_high, x_series_high = complete_run_simulation(profile_high, dt=0.1)
        risk_high = compute_risk_probability(x_series_high[-1])

        self.assertGreater(risk_high, risk_low, "Higher exercise intensity should yield a higher DCS risk probability")

if __name__ == '__main__':
    unittest.main() 