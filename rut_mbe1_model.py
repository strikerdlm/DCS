"""rut_mbe1_model.py

Mechanistic 3RUT-MBe1 altitude decompression sickness (DCS) risk model.

This module implements the *single-compartment, single bubble-size group* (Nbs=1)
variant of the 3RUT‑MBe1 model described in NEDU TR 18‑01:
"A Probabilistic Model of Altitude Decompression Sickness Based on the 3RUT‑MB Model
of Gas Bubble Evolution in Perfused Tissue" (Gerth et al., 2018).

Implementation notes
- This implementation follows Appendix C ("Summary of Recursive Equations") for the
  discrete-time recursion. Key equations are referenced in docstrings.
- All pressures are represented in **atm** in the state evolution (matching Appendix C
  when divided by 760 mmHg/atm). Surface tension σ is provided in dyne/cm as in Table 3
  but converted to an equivalent pressure scale via Λσ.
- The scale factor Λ is used exactly as described in Appendix C (Scaled model parameters).
  The report notes Λ can be chosen arbitrarily when the scaled formulation is used.

Scope & scientific validity
- This module is **not** a clinical or operational tool.
- This module intentionally implements the *published* recursion and performs strict
  input validation and numerically stable inversion of the O₂ content curve.

"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple


_ATM_PER_MMHG: float = 1.0 / 760.0
_MMHG_PER_ATM: float = 760.0
_ATM_PER_DYNE_PER_CM2: float = 1.0 / 1.01325e6


@dataclass(slots=True)
class ProfileSegment:
    """A piecewise-constant exposure segment.

    All pressures are absolute.

    Parameters
    - duration_min: segment duration (minutes), must be >= 0.
    - p_amb_atm: ambient pressure (atm), must be > 0.
    - fio2: inspired O2 fraction, must be in [0, 1].
    - fin2: inspired N2 fraction, must be in [0, 1]. Must satisfy fio2 + fin2 <= 1.
    - i_ex_l_min_wb: exercise intensity I_ex (L/min whole-body O2 above rest), must be >= 0.

    """

    duration_min: float
    p_amb_atm: float
    fio2: float
    fin2: float
    i_ex_l_min_wb: float

    def __post_init__(self) -> None:
        if not isinstance(self.duration_min, (int, float)):
            raise TypeError("duration_min must be a number")
        if self.duration_min < 0:
            raise ValueError("duration_min must be >= 0")

        if not isinstance(self.p_amb_atm, (int, float)):
            raise TypeError("p_amb_atm must be a number")
        if self.p_amb_atm <= 0:
            raise ValueError("p_amb_atm must be > 0")

        for name, val in ("fio2", self.fio2), ("fin2", self.fin2):
            if not isinstance(val, (int, float)):
                raise TypeError(f"{name} must be a number")
            if val < 0.0 or val > 1.0:
                raise ValueError(f"{name} must be in [0, 1]")

        if (self.fio2 + self.fin2) > 1.0 + 1e-12:
            raise ValueError("fio2 + fin2 must be <= 1")

        if not isinstance(self.i_ex_l_min_wb, (int, float)):
            raise TypeError("i_ex_l_min_wb must be a number")
        if self.i_ex_l_min_wb < 0.0:
            raise ValueError("i_ex_l_min_wb must be >= 0")


@dataclass(slots=True)
class ModelParameters:
    """3RUT‑MBe1 parameters (single compartment).

    Defaults follow Table 3 (3RUT‑MBe1) in the project theory file
    `BU_3RUT/3RUT_MBe1/3RUT_Theory.md`.

    Important: M is given in Table 3 as **atm·V⁻1**, i.e. pressure per volume.
    Appendix C defines the scaled modulus:
      M̄ = (4π/3) * M / Λ³.

    """

    # Fixed parameters (Table 3)
    p_h2o_mmhg: float = 47.0
    rq: float = 1.0
    pt_co2_mmhg: float = 45.0

    alpha_b_o2_ml_per_ml_per_atm: float = 2.356e-2
    alpha_b_n2_ml_per_ml_per_atm: float = 1.410e-2

    k_alpha_n2: float = 0.5985
    k_d_n2: float = 0.9091

    sigma_surface_tension_dyne_per_cm: float = 30.0

    # Adjustable parameters (Table 3)
    gain_g_hazard: float = 6.188e-2
    n0_b_total_nuclei: float = 1.198
    beta0_cm: float = 4.868e-5

    m_elastic_modulus_atm_per_ml: float = 1.341e-7

    n_vge_gas_loss_rate_ml_inv_min_inv: float = 4.758
    sigma_c_factor: float = 19.64

    alpha_t_o2_ml_per_ml_per_atm: float = 4.536e-2

    v_t_ml: float = 5.279e-2
    q_total_rest_ml_per_min: float = 4.698e-3

    d_t_o2_cm2_per_min: float = 1.414e-3

    bn_bubble_number_power_factor: float = 2.172
    tau_pcrush_min: float = 201.4

    m_beta_ex: float = 0.6162

    vdot_o2_rest_ml_per_ml_per_min: float = 4.401e-5
    m_vdot_o2_per_i_ex: float = 1.677e-3
    m_qdot_per_vdot_o2: float = 6.997

    # Modeling controls / assumptions
    lambda_cm_inv: float = 100.0
    n_min_b: float = 1e-6

    # Derived quantities (Appendix C scaled parameters)
    p_infty_atm: float = field(init=False)

    sigma_hat_atm: float = field(init=False)
    sigma_c_hat_atm: float = field(init=False)

    k_hat_o2_per_min: float = field(init=False)
    k_hat_n2_per_min: float = field(init=False)

    beta0_hat: float = field(init=False)
    v_hat_t: float = field(init=False)

    m_bar_atm: float = field(init=False)

    def __post_init__(self) -> None:
        # Basic validation
        if self.rq <= 0:
            raise ValueError("rq must be > 0")
        if self.lambda_cm_inv <= 0:
            raise ValueError("lambda_cm_inv must be > 0")
        if self.n0_b_total_nuclei <= 0:
            raise ValueError("n0_b_total_nuclei must be > 0")
        if self.n_min_b <= 0:
            raise ValueError("n_min_b must be > 0")
        if self.n0_b_total_nuclei <= self.n_min_b:
            raise ValueError("n0_b_total_nuclei must be > n_min_b")
        if self.v_t_ml <= 0:
            raise ValueError("v_t_ml must be > 0")
        if self.q_total_rest_ml_per_min <= 0:
            raise ValueError("q_total_rest_ml_per_min must be > 0")
        if self.tau_pcrush_min <= 0:
            raise ValueError("tau_pcrush_min must be > 0")

        self.p_infty_atm = (self.p_h2o_mmhg + self.pt_co2_mmhg) * _ATM_PER_MMHG  # (C.1)

        # Scaled surface tensions σ̄ = Λσ and σ̄c = Λσc, converted to atm.
        # σ has units dyne/cm; Λ has units 1/cm -> Λσ has units dyne/cm^2 (pressure).
        sigma_hat_dyne_per_cm2 = self.lambda_cm_inv * self.sigma_surface_tension_dyne_per_cm
        self.sigma_hat_atm = sigma_hat_dyne_per_cm2 * _ATM_PER_DYNE_PER_CM2

        sigma_c_dyne_per_cm = self.sigma_c_factor * self.sigma_surface_tension_dyne_per_cm
        sigma_c_hat_dyne_per_cm2 = self.lambda_cm_inv * sigma_c_dyne_per_cm
        self.sigma_c_hat_atm = sigma_c_hat_dyne_per_cm2 * _ATM_PER_DYNE_PER_CM2

        # Permeability K = D * alpha_t, then K̄ = 3 Λ^2 K (scaled permeability, 1/min).
        alpha_t_n2 = self.k_alpha_n2 * self.alpha_t_o2_ml_per_ml_per_atm
        d_t_n2 = self.k_d_n2 * self.d_t_o2_cm2_per_min

        self.k_hat_o2_per_min = 3.0 * (self.lambda_cm_inv**2) * self.d_t_o2_cm2_per_min * self.alpha_t_o2_ml_per_ml_per_atm
        self.k_hat_n2_per_min = 3.0 * (self.lambda_cm_inv**2) * d_t_n2 * alpha_t_n2

        # β̂⁰ = Λβ⁰
        self.beta0_hat = self.beta0_cm * self.lambda_cm_inv

        # V̂t = Λ³ Vt
        self.v_hat_t = self.v_t_ml * (self.lambda_cm_inv**3)

        # M̄ = (4π/3) M / Λ³
        self.m_bar_atm = ((4.0 * math.pi) / 3.0) * (self.m_elastic_modulus_atm_per_ml / (self.lambda_cm_inv**3))


@dataclass(slots=True)
class ModelState:
    """Dynamic model state at a discrete time tn."""

    t_min: float
    p_amb_atm: float
    fio2: float
    fin2: float
    i_ex_l_min_wb: float

    pt_n2_atm: float
    pt_o2_atm: float

    r_hat: float
    pb_n2_atm: float
    pb_o2_atm: float

    x_hat_n2: float
    x_hat_o2: float

    n_b: float
    n_b_max: float
    p_crush_atm: float

    beta_f_hat: float
    r_hat_min: float

    h_per_min: float
    p_survival: float
    p_dcs: float


class RutMbe1Model:
    """Single-compartment 3RUT‑MBe1 model.

    The recursion is implemented per Appendix C (C.3–C.46).

    """

    def __init__(self, params: Optional[ModelParameters] = None) -> None:
        self.params = params or ModelParameters()
        # P^o_crush in Appendix C Eq. (C.5): the *initial* crush pressure under
        # saturation conditions. This must remain constant for the exponential
        # decay formulation to match the literature.
        self._p_crush_origin_atm: float = 0.0
        self.state: Optional[ModelState] = None

        # Lobdell O₂ saturation constants (Appendix C footnote d)
        self._lob_a1 = 0.34332
        self._lob_a2 = 0.64073
        self._lob_b1 = 0.34128
        self._lob_b2 = 0.64073
        self._lob_eta = 1.58678
        self._lob_p_half_mmhg = 25.0
        self._hb_c_ml_o2_per_ml_blood = 0.20

    @staticmethod
    def _g_hat_inert(
        *,
        alpha_t_k: float,
        v_hat_t: float,
        n_b_n: float,
        n_b_prev: float,
    ) -> float:
        """Compute Ĝ_k,n for inert gas (Eq. C.25).

        Appendix C (C.25) for inert gases:
          Ĝ_k,n = (4π/3) α_tk V̂t (n_b,n / n_b,n-1)

        Notes
        - This term is undefined at n_b,n-1 = 0; in that edge case we return 0
          and rely on the ΔĜ term (C.26) during recruitment steps.
        """
        if n_b_n <= 0.0 or n_b_prev <= 0.0:
            return 0.0
        if alpha_t_k <= 0.0 or v_hat_t <= 0.0:
            raise ValueError("alpha_t_k and v_hat_t must be > 0")
        return (4.0 * math.pi / 3.0) * alpha_t_k * v_hat_t * (n_b_n / n_b_prev)

    @staticmethod
    def _delta_g_hat_inert(*, alpha_t_k: float, v_hat_t: float, delta_n_b: float) -> float:
        """Compute ΔĜ_k,n for inert gas (Eq. C.26)."""
        if delta_n_b <= 0.0:
            return 0.0
        if alpha_t_k <= 0.0 or v_hat_t <= 0.0:
            raise ValueError("alpha_t_k and v_hat_t must be > 0")
        return (4.0 * math.pi / 3.0) * alpha_t_k * v_hat_t * delta_n_b

    @staticmethod
    def mmhg_to_atm(p_mmhg: float) -> float:
        return p_mmhg * _ATM_PER_MMHG

    @staticmethod
    def atm_to_mmhg(p_atm: float) -> float:
        return p_atm * _MMHG_PER_ATM

    def _pa_inert_atm(self, p_amb_atm: float, fi_k: float) -> float:
        """Arterial inert gas partial pressure (Eq. C.28)."""
        p_a_h2o = self.params.p_h2o_mmhg * _ATM_PER_MMHG
        p_a_co2 = self.params.pt_co2_mmhg * _ATM_PER_MMHG
        term1 = p_amb_atm - p_a_h2o
        term2 = p_a_co2 * (1.0 - (1.0 / self.params.rq))
        return fi_k * (term1 - term2)

    def _pa_o2_atm(self, p_amb_atm: float, sum_pa_inert_atm: float) -> float:
        """Arterial O2 partial pressure (Eq. C.37)."""
        p_a_h2o = self.params.p_h2o_mmhg * _ATM_PER_MMHG
        p_a_co2 = self.params.pt_co2_mmhg * _ATM_PER_MMHG
        return p_amb_atm - p_a_h2o - p_a_co2 - sum_pa_inert_atm

    def _so2(self, p_o2_mmhg: float) -> float:
        if p_o2_mmhg <= 0.0:
            return 0.0
        p = (p_o2_mmhg / self._lob_p_half_mmhg) ** self._lob_eta
        num = self._lob_a1 * p + self._lob_a2 * (p**2)
        den = 1.0 + self._lob_b1 * p + self._lob_b2 * (p**2)
        if den <= 0.0:
            return 1.0
        return min(max(num / den, 0.0), 1.0)

    def blood_o2_content_ml_per_ml(self, p_o2_atm: float) -> float:
        """Whole blood O₂ content (Eqs. C.38/C.42 structure)."""
        if p_o2_atm <= 0.0:
            return 0.0
        dissolved = self.params.alpha_b_o2_ml_per_ml_per_atm * p_o2_atm
        sat = self._so2(self.atm_to_mmhg(p_o2_atm))
        bound = self._hb_c_ml_o2_per_ml_blood * sat
        return dissolved + bound

    def _alpha_prime_o2(self, p_v_o2_atm: float) -> float:
        """Slope α′O2 (Eq. C.31).

        Returns (ml O₂ / ml blood) / atm.

        """
        p_v_mmhg = max(self.atm_to_mmhg(max(p_v_o2_atm, 0.0)), 1e-6)

        p = (p_v_mmhg / self._lob_p_half_mmhg) ** self._lob_eta
        # dS/dp where S = (a1 p + a2 p^2)/(1 + b1 p + b2 p^2)
        num = self._lob_a1 + 2.0 * self._lob_a2 * p + (self._lob_a2 * self._lob_b1 - self._lob_a1 * self._lob_b2) * (p**2)
        den = (1.0 + self._lob_b1 * p + self._lob_b2 * (p**2)) ** 2
        dS_dp = 0.0 if den <= 0.0 else (num / den)

        # dp/dPO2(mmHg) for p = (PO2/P_half)^eta
        dp_dpo2_mmhg = (self._lob_eta * (p / p_v_mmhg)) if p_v_mmhg > 0.0 else 0.0

        dS_dpo2_mmhg = dS_dp * dp_dpo2_mmhg
        return max(
            self.params.alpha_b_o2_ml_per_ml_per_atm + self._hb_c_ml_o2_per_ml_blood * dS_dpo2_mmhg * _MMHG_PER_ATM,
            1e-12,
        )

    def _invert_o2_content_to_po2_atm(
        self,
        target_content_ml_per_ml: float,
        p_low_atm: float,
        p_high_atm: float,
        *,
        max_iter: int = 80,
        tol: float = 1e-9,
    ) -> float:
        """Invert blood O₂ content curve (Appendix C footnote e).

        Uses a bounded bisection (monotone function) with explicit iteration limit.
        """
        if target_content_ml_per_ml <= 0.0:
            return 0.0
        if p_low_atm < 0.0 or p_high_atm <= p_low_atm:
            raise ValueError("invalid bracket for pO2 inversion")

        c_low = self.blood_o2_content_ml_per_ml(p_low_atm)
        c_high = self.blood_o2_content_ml_per_ml(p_high_atm)
        if not (c_low <= target_content_ml_per_ml <= c_high):
            # Expand the upper bracket (bounded attempts)
            p_hi = p_high_atm
            for _ in range(12):
                p_hi *= 1.5
                c_hi = self.blood_o2_content_ml_per_ml(p_hi)
                if c_hi >= target_content_ml_per_ml:
                    p_high_atm = p_hi
                    c_high = c_hi
                    break
            else:
                # Clamp to upper bound if target is above achievable
                return p_high_atm

        lo = p_low_atm
        hi = p_high_atm
        for _ in range(max_iter):
            mid = 0.5 * (lo + hi)
            c_mid = self.blood_o2_content_ml_per_ml(mid)
            if abs(c_mid - target_content_ml_per_ml) <= tol:
                return mid
            if c_mid < target_content_ml_per_ml:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    def initialize_state(
        self,
        *,
        p_amb_atm: float,
        fio2: float,
        fin2: float,
        i_ex_l_min_wb: float = 0.0,
    ) -> ModelState:
        """Initialize state at t=0 under saturation steady-state (Appendix C footnotes c,e)."""
        seg = ProfileSegment(
            duration_min=0.0,
            p_amb_atm=p_amb_atm,
            fio2=fio2,
            fin2=fin2,
            i_ex_l_min_wb=i_ex_l_min_wb,
        )

        pa_n2 = self._pa_inert_atm(seg.p_amb_atm, seg.fin2)
        pa_o2 = self._pa_o2_atm(seg.p_amb_atm, pa_n2)
        pa_o2 = max(pa_o2, 0.0)

        # Initial tissue inert gas tension equals arterial (C.30 footnote c)
        pt_n2 = max(pa_n2, 0.0)

        # Exercise-dependent V̇O₂ and Q̇ (C.19, C.21)
        vdot_o2 = self.params.m_vdot_o2_per_i_ex * seg.i_ex_l_min_wb + self.params.vdot_o2_rest_ml_per_ml_per_min
        q_dot_rest = self.params.q_total_rest_ml_per_min / self.params.v_t_ml
        q_dot = self.params.m_qdot_per_vdot_o2 * (vdot_o2 - self.params.vdot_o2_rest_ml_per_ml_per_min) + q_dot_rest
        q_dot = max(q_dot, 1e-12)

        c_a = self.blood_o2_content_ml_per_ml(pa_o2)
        c_v = max(c_a - (vdot_o2 / q_dot), 0.0)

        # Invert content to p_vO2 == p_tO2 (Appendix C footnote e)
        pt_o2 = self._invert_o2_content_to_po2_atm(c_v, 0.0, max(pa_o2, 0.05))

        sum_pt = pt_n2 + pt_o2
        p_crush0 = (seg.p_amb_atm - self.params.p_infty_atm) - sum_pt  # (C.4 footnote b)
        p_crush0 = max(p_crush0, 0.0)
        self._p_crush_origin_atm = p_crush0

        # Initial nuclei distribution parameters (C.6)
        log_term = abs(math.log(self.params.n0_b_total_nuclei) - math.log(self.params.n_min_b))
        r_hat0_min = max(self.params.beta0_hat * log_term, 1e-12)
        beta_f_hat0 = 0.0
        denom = 2.0 * (self.params.sigma_c_hat_atm - self.params.sigma_hat_atm) + p_crush0 * r_hat0_min
        if denom > 0.0:
            beta_ex = 1.0 + self.params.m_beta_ex * seg.i_ex_l_min_wb
            beta_f_hat0 = beta_ex * (2.0 * self.params.sigma_c_hat_atm * self.params.beta0_hat) / denom

        state = ModelState(
            t_min=0.0,
            p_amb_atm=seg.p_amb_atm,
            fio2=seg.fio2,
            fin2=seg.fin2,
            i_ex_l_min_wb=seg.i_ex_l_min_wb,
            pt_n2_atm=pt_n2,
            pt_o2_atm=pt_o2,
            r_hat=1e-12,
            pb_n2_atm=0.0,
            pb_o2_atm=0.0,
            x_hat_n2=0.0,
            x_hat_o2=0.0,
            n_b=0.0,
            n_b_max=0.0,
            p_crush_atm=p_crush0,
            beta_f_hat=beta_f_hat0,
            r_hat_min=r_hat0_min,
            h_per_min=0.0,
            p_survival=1.0,
            p_dcs=0.0,
        )
        self.state = state
        return state

    def run_profile(self, segments: Sequence[ProfileSegment], *, dt_min: float) -> List[ModelState]:
        """Run a profile with fixed step size dt_min.

        dt_min is bounded and used to discretize each segment into an integer number
        of steps (so each segment ends exactly on its boundary).

        """
        if dt_min <= 0.0:
            raise ValueError("dt_min must be > 0")
        if not segments:
            return []
        if self.state is None:
            raise ValueError("Model not initialized; call initialize_state(...) first")

        history: List[ModelState] = [self.state]
        for seg in segments:
            if seg.duration_min <= 0.0:
                continue
            n_steps = max(1, int(math.ceil(seg.duration_min / dt_min)))
            step_dt = seg.duration_min / n_steps
            for _ in range(n_steps):
                self.state = self._advance_one_step(
                    dt_min=step_dt,
                    next_p_amb_atm=seg.p_amb_atm,
                    next_fio2=seg.fio2,
                    next_fin2=seg.fin2,
                    next_i_ex=seg.i_ex_l_min_wb,
                )
                history.append(self.state)
        return history

    def _advance_one_step(
        self,
        *,
        dt_min: float,
        next_p_amb_atm: float,
        next_fio2: float,
        next_fin2: float,
        next_i_ex: float,
    ) -> ModelState:
        """Advance one time step using Appendix C recursion."""
        if self.state is None:
            raise ValueError("Model not initialized")
        if dt_min <= 0.0:
            raise ValueError("dt_min must be > 0")

        s = self.state
        p = self.params

        # Next conditions
        p_amb_np1 = float(next_p_amb_atm)
        if p_amb_np1 <= 0.0:
            raise ValueError("next_p_amb_atm must be > 0")

        # 0) Physiological parameters for this interval (C.19, C.21)
        vdot_o2_n = p.m_vdot_o2_per_i_ex * next_i_ex + p.vdot_o2_rest_ml_per_ml_per_min
        q_dot_rest = p.q_total_rest_ml_per_min / p.v_t_ml
        q_dot_n = p.m_qdot_per_vdot_o2 * (vdot_o2_n - p.vdot_o2_rest_ml_per_ml_per_min) + q_dot_rest
        q_dot_n = max(q_dot_n, 1e-12)

        # 1) Bubble number (C.3–C.11)
        beta_ex_n = 1.0 + p.m_beta_ex * next_i_ex  # (C.3)

        sum_pt_n = s.pt_n2_atm + s.pt_o2_atm
        p_crush_candidate = (s.p_amb_atm - p.p_infty_atm) - sum_pt_n
        p_crush_n = max(s.p_crush_atm, p_crush_candidate)  # (C.4)
        p_crush_n = max(p_crush_n, 0.0)

        if p_crush_n <= s.p_crush_atm:
            p_crush_n = self._p_crush_origin_atm + (s.p_crush_atm - self._p_crush_origin_atm) * math.exp(-dt_min / p.tau_pcrush_min)  # (C.5)

        log_term = abs(math.log(p.n0_b_total_nuclei) - math.log(p.n_min_b))
        r_hat0_min = max(p.beta0_hat * log_term, 1e-12)

        denom_beta = 2.0 * (p.sigma_c_hat_atm - p.sigma_hat_atm) + p_crush_n * r_hat0_min
        beta_f_hat_n = 0.0
        if denom_beta > 0.0:
            beta_f_hat_n = beta_ex_n * (2.0 * p.sigma_c_hat_atm * p.beta0_hat) / denom_beta  # (C.6)

        p_ss_n = (sum_pt_n + p.p_infty_atm) - s.p_amb_atm  # (C.7)

        n_b_max = s.n_b_max
        if p_ss_n > 0.0 and beta_f_hat_n > 0.0:
            exponent = -(2.0 * p.sigma_hat_atm) / (p_ss_n * beta_f_hat_n)
            if exponent >= -700.0:
                n_b_candidate = p.n0_b_total_nuclei * math.exp(exponent)
            else:
                n_b_candidate = 0.0
            n_b_max = max(n_b_max, n_b_candidate)  # (C.8)

        delta_n_b = max(n_b_max - s.n_b_max, 0.0)
        n_b_n = s.n_b + delta_n_b  # (C.9)

        r_hat_min_n = max(beta_f_hat_n * log_term, 1e-12)  # (C.10)

        # Approximate initial bubble gas content for newly recruited bubbles (C.11)
        x_hat_o_n2 = 0.0
        x_hat_o_o2 = 0.0
        if delta_n_b > 0.0:
            # Use current tissue gas fractions at nucleation.
            frac_n2 = 0.5
            frac_o2 = 0.5
            if sum_pt_n > 1e-12:
                frac_n2 = s.pt_n2_atm / sum_pt_n
                frac_o2 = s.pt_o2_atm / sum_pt_n
            p_total = (s.p_amb_atm - p.p_infty_atm) + (2.0 * p.sigma_hat_atm / r_hat_min_n) + (p.m_bar_atm * (r_hat_min_n**3))
            p_total = max(p_total, 0.0)
            x_hat_o_n2 = (p_total * frac_n2) * (r_hat_min_n**3)
            x_hat_o_o2 = (p_total * frac_o2) * (r_hat_min_n**3)

        # 2) Bubble radius and pressure (C.12–C.18)
        r_hat_n = s.r_hat
        pb_n2_n = s.pb_n2_atm
        pb_o2_n = s.pb_o2_atm

        # If bubbles appear for the first time in this step, start at r_hat_min_n
        if s.n_b <= 1e-12 and delta_n_b > 0.0:
            r_hat_n = r_hat_min_n
            # Initialize bubble partial pressures from nucleation composition.
            if r_hat_min_n > 0.0:
                pb_n2_n = (x_hat_o_n2 / (r_hat_min_n**3)) if x_hat_o_n2 > 0.0 else 0.0
                pb_o2_n = (x_hat_o_o2 / (r_hat_min_n**3)) if x_hat_o_o2 > 0.0 else 0.0

        # Defaults for next state
        r_hat_np1 = max(r_hat_n, 1e-12)
        pb_n2_np1 = 0.0
        pb_o2_np1 = 0.0

        if n_b_n > 1e-12 and r_hat_n > 1e-12:
            b_n2 = p.k_hat_n2_per_min * dt_min / (r_hat_n**2)  # (C.12)
            a_n2 = (1.0 + r_hat_n) * b_n2  # (C.13)
            a_n2 = min(max(a_n2, 0.0), 1e6)

            a_o2 = (1.0 + r_hat_n) * (p.k_hat_o2_per_min * dt_min / (r_hat_n**2))
            a_o2 = min(max(a_o2, 0.0), 1e6)

            # C.14/C.15
            A_n2 = pb_n2_n + a_n2 * (1.0 - a_n2 / 2.0) * (s.pt_n2_atm - pb_n2_n)
            B_n2 = 0.5 * ((2.0 * a_n2 - b_n2 + a_n2 * b_n2) * s.pt_n2_atm + (a_n2 + b_n2) * (1.0 - a_n2) * pb_n2_n)

            b_o2 = p.k_hat_o2_per_min * dt_min / (r_hat_n**2)
            A_o2 = pb_o2_n + a_o2 * (1.0 - a_o2 / 2.0) * (s.pt_o2_atm - pb_o2_n)
            B_o2 = 0.5 * ((2.0 * a_o2 - b_o2 + a_o2 * b_o2) * s.pt_o2_atm + (a_o2 + b_o2) * (1.0 - a_o2) * pb_o2_n)

            p_prime_amb_np1 = p_amb_np1 - p.p_infty_atm
            term_2sigma = 2.0 * p.sigma_hat_atm / r_hat_n
            term_mr3 = p.m_bar_atm * (r_hat_n**3)

            num_dr = (A_n2 + A_o2) - (p_prime_amb_np1 + term_2sigma + term_mr3)
            den_dr = (3.0 * (A_n2 + A_o2) - (B_n2 + B_o2)) - (term_2sigma - 3.0 * term_mr3)

            if abs(den_dr) > 1e-14:
                delta_r = num_dr / den_dr
            else:
                delta_r = 0.0

            # Stability cap: limit fractional change per step.
            delta_r = max(min(delta_r, 0.10), -0.10)

            r_hat_np1 = max(r_hat_n * (1.0 + delta_r), 1e-12)  # (C.17)

            pb_n2_np1 = max(A_n2 - (3.0 * A_n2 - B_n2) * delta_r, 0.0)  # (C.18)
            pb_o2_np1 = max(A_o2 - (3.0 * A_o2 - B_o2) * delta_r, 0.0)

        x_hat_n2_np1 = pb_n2_np1 * (r_hat_np1**3)  # (C.27)
        x_hat_o2_np1 = pb_o2_np1 * (r_hat_np1**3)  # (C.36)

        # 3) Tissue gas tensions
        pa_n2_n = self._pa_inert_atm(s.p_amb_atm, s.fin2)
        pa_o2_n = self._pa_o2_atm(s.p_amb_atm, pa_n2_n)

        pa_n2_np1 = self._pa_inert_atm(p_amb_np1, next_fin2)
        pa_o2_np1 = self._pa_o2_atm(p_amb_np1, pa_n2_np1)

        # Inert gas (C.23–C.30)
        alpha_t_n2 = p.k_alpha_n2 * p.alpha_t_o2_ml_per_ml_per_atm
        tau_n2 = alpha_t_n2 / (p.alpha_b_n2_ml_per_ml_per_atm * q_dot_n)
        tau_n2 = max(tau_n2, 1e-12)
        eps_n2 = 1.0 - math.exp(-dt_min / tau_n2)

        # Ĝ_k,n for inert gas per Appendix C (C.25) and ΔĜ_k,n per (C.26).
        # NOTE: Ĝ_k,n depends on the ratio n_b,n / n_b,n-1, not the absolute n_b,n.
        g_hat_n2 = self._g_hat_inert(alpha_t_k=alpha_t_n2, v_hat_t=p.v_hat_t, n_b_n=n_b_n, n_b_prev=s.n_b)

        delta_g_hat_n2 = self._delta_g_hat_inert(alpha_t_k=alpha_t_n2, v_hat_t=p.v_hat_t, delta_n_b=delta_n_b)

        ups_n2 = (pa_n2_np1 - pa_n2_n) / dt_min
        term_g_x = 0.0
        if n_b_n > 1e-12:
            term_g_x = g_hat_n2 * (x_hat_n2_np1 - s.x_hat_n2) / dt_min

        pt_n2_np1 = (
            s.pt_n2_atm * (1.0 - eps_n2)
            + ups_n2 * dt_min
            + (pa_n2_n - tau_n2 * (ups_n2 + term_g_x)) * eps_n2
            - delta_g_hat_n2 * (s.x_hat_n2 - x_hat_o_n2)
        )
        pt_n2_np1 = max(pt_n2_np1, 0.0)

        # Oxygen (C.31–C.44)
        alpha_prime = self._alpha_prime_o2(s.pt_o2_atm)
        tau_o2 = p.alpha_t_o2_ml_per_ml_per_atm / (q_dot_n * alpha_prime)
        tau_o2 = max(tau_o2, 1e-12)
        eps_o2 = 1.0 - math.exp(-dt_min / tau_o2)

        g_hat_o2 = 0.0
        if n_b_n > 1e-12:
            g_hat_o2 = (4.0 * math.pi / 3.0) * (n_b_n / (p.alpha_t_o2_ml_per_ml_per_atm * p.v_hat_t))

        delta_g_hat_o2 = 0.0
        if delta_n_b > 0.0:
            delta_g_hat_o2 = (4.0 * math.pi / 3.0) * (delta_n_b / (p.alpha_t_o2_ml_per_ml_per_atm * p.v_hat_t))

        c_a_n = self.blood_o2_content_ml_per_ml(max(pa_o2_n, 0.0))
        c_a_np1 = self.blood_o2_content_ml_per_ml(max(pa_o2_np1, 0.0))

        p_o_prime_n = c_a_n / alpha_prime
        p_o_prime_np1 = c_a_np1 / alpha_prime
        ups_o2 = (p_o_prime_np1 - p_o_prime_n) / dt_min

        c_v_n = self.blood_o2_content_ml_per_ml(max(s.pt_o2_atm, 0.0))
        rho_dot = (vdot_o2_n + q_dot_n * (c_v_n - alpha_prime * s.pt_o2_atm)) / p.alpha_t_o2_ml_per_ml_per_atm

        term_g_x_o2 = 0.0
        if n_b_n > 1e-12:
            term_g_x_o2 = g_hat_o2 * (x_hat_o2_np1 - s.x_hat_o2) / dt_min

        pt_o2_np1 = (
            s.pt_o2_atm * (1.0 - eps_o2)
            + ups_o2 * dt_min
            + (p_o_prime_n - tau_o2 * (ups_o2 + rho_dot + term_g_x_o2)) * eps_o2
            - delta_g_hat_o2 * (s.x_hat_o2 - x_hat_o_o2)
        )
        pt_o2_np1 = max(pt_o2_np1, 0.0)

        # 4) VGE (C.45–C.46)
        # Unscaled bubble volumes: Vb = (4π/3) r^3 where r = r_hat/Λ.
        r_cm = r_hat_np1 / p.lambda_cm_inv
        r0_cm = r_hat_min_n / p.lambda_cm_inv
        v_b_ml = (4.0 / 3.0) * math.pi * (r_cm**3)
        v_r0_ml = (4.0 / 3.0) * math.pi * (r0_cm**3)

        lr = 0.0
        if v_b_ml > v_r0_ml:
            lr = (v_b_ml - v_r0_ml) * p.n_vge_gas_loss_rate_ml_inv_min_inv * dt_min
        lr = min(max(lr, 0.0), 1.0)

        n_b_after_vge = max(n_b_n * (1.0 - lr), 0.0)
        if n_b_after_vge < p.n_min_b:
            n_b_after_vge = 0.0
            r_hat_np1 = 1e-12
            pb_n2_np1 = 0.0
            pb_o2_np1 = 0.0
            x_hat_n2_np1 = 0.0
            x_hat_o2_np1 = 0.0

        # 5) Hazard and survival (D.3a + trapezoid update)
        hazard_vol = v_b_ml - v_r0_ml
        h_np1 = 0.0
        if n_b_after_vge > 1e-12 and hazard_vol > 0.0:
            h_np1 = p.gain_g_hazard * hazard_vol * (max(n_b_after_vge, 1e-12) ** p.bn_bubble_number_power_factor)
        h_np1 = max(h_np1, 0.0)

        avg_h = 0.5 * (s.h_per_min + h_np1)
        p_surv_np1 = min(max(s.p_survival * math.exp(-avg_h * dt_min), 0.0), 1.0)
        p_dcs_np1 = 1.0 - p_surv_np1

        return ModelState(
            t_min=s.t_min + dt_min,
            p_amb_atm=p_amb_np1,
            fio2=next_fio2,
            fin2=next_fin2,
            i_ex_l_min_wb=next_i_ex,
            pt_n2_atm=pt_n2_np1,
            pt_o2_atm=pt_o2_np1,
            r_hat=r_hat_np1,
            pb_n2_atm=pb_n2_np1,
            pb_o2_atm=pb_o2_np1,
            x_hat_n2=x_hat_n2_np1,
            x_hat_o2=x_hat_o2_np1,
            n_b=n_b_after_vge,
            n_b_max=n_b_max,
            p_crush_atm=p_crush_n,
            beta_f_hat=beta_f_hat_n,
            r_hat_min=r_hat_min_n,
            h_per_min=h_np1,
            p_survival=p_surv_np1,
            p_dcs=p_dcs_np1,
        )


def altitude_ft_to_p_amb_atm(altitude_ft: float) -> float:
    """Standard barometric model used in the project theory (altitude in feet).

    Matches the form cited in the project theory for converting altitude to pressure.

    P(atm) = (1 - 6.875e-6 * altitude_ft)^(5.25588)

    """
    if not isinstance(altitude_ft, (int, float)):
        raise TypeError("altitude_ft must be a number")
    if altitude_ft < 0.0:
        altitude_ft = 0.0
    factor = 1.0 - 6.875e-6 * float(altitude_ft)
    factor = max(factor, 0.0)
    return factor**5.25588
