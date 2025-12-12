import math
import unittest

from rut_mbe1_model import RutMbe1Model


class TestRutMbe1ModelAppendixC(unittest.TestCase):
    def test_g_hat_inert_matches_eq_c25(self) -> None:
        # Appendix C (C.25): Ĝ_k,n = (4π/3) α_tk V̂t (n_b,n / n_b,n-1)
        alpha_t_k = 2.0
        v_hat_t = 3.0
        n_b_n = 10.0
        n_b_prev = 5.0
        expected = (4.0 * math.pi / 3.0) * alpha_t_k * v_hat_t * (n_b_n / n_b_prev)
        got = RutMbe1Model._g_hat_inert(
            alpha_t_k=alpha_t_k,
            v_hat_t=v_hat_t,
            n_b_n=n_b_n,
            n_b_prev=n_b_prev,
        )
        self.assertAlmostEqual(got, expected, places=12)

    def test_delta_g_hat_inert_matches_eq_c26(self) -> None:
        # Appendix C (C.26): ΔĜ_k,n = (4π/3) α_tk V̂t Δn_b,n
        alpha_t_k = 2.0
        v_hat_t = 3.0
        delta_n_b = 4.0
        expected = (4.0 * math.pi / 3.0) * alpha_t_k * v_hat_t * delta_n_b
        got = RutMbe1Model._delta_g_hat_inert(alpha_t_k=alpha_t_k, v_hat_t=v_hat_t, delta_n_b=delta_n_b)
        self.assertAlmostEqual(got, expected, places=12)

    def test_p_crush_origin_is_constant_after_nonmonotonic_steps(self) -> None:
        # Appendix C (C.5) requires P^o_crush (initial crush pressure) to remain constant.
        m = RutMbe1Model()
        s0 = m.initialize_state(p_amb_atm=1.0, fio2=0.21, fin2=0.79, i_ex_l_min_wb=0.0)
        p0 = m._p_crush_origin_atm

        # Force an increase in crush candidate by making tissue tensions unrealistically low.
        m.state = s0.__class__(
            t_min=s0.t_min,
            p_amb_atm=s0.p_amb_atm,
            fio2=s0.fio2,
            fin2=s0.fin2,
            i_ex_l_min_wb=s0.i_ex_l_min_wb,
            pt_n2_atm=0.0,
            pt_o2_atm=0.0,
            r_hat=s0.r_hat,
            pb_n2_atm=s0.pb_n2_atm,
            pb_o2_atm=s0.pb_o2_atm,
            x_hat_n2=s0.x_hat_n2,
            x_hat_o2=s0.x_hat_o2,
            n_b=s0.n_b,
            n_b_max=s0.n_b_max,
            p_crush_atm=s0.p_crush_atm,
            beta_f_hat=s0.beta_f_hat,
            r_hat_min=s0.r_hat_min,
            h_per_min=s0.h_per_min,
            p_survival=s0.p_survival,
            p_dcs=s0.p_dcs,
        )

        _ = m._advance_one_step(
            dt_min=1.0,
            next_p_amb_atm=1.0,
            next_fio2=0.21,
            next_fin2=0.79,
            next_i_ex=0.0,
        )

        self.assertAlmostEqual(m._p_crush_origin_atm, p0, places=12)


if __name__ == "__main__":
    unittest.main()
