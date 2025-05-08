## 10. Appendix C. Summary of Recursive Equations for Solution of 3RUT-MBe1 Model

### Subscripts:
- Compartments: i = 1, 2, ..., nc (suppressed)
- Bubble size group: m = 1, 2, ..., Nbs (suppressed)
- Diffusible gases: k = 1, 2, ..., Ng
- Time intervals: n = 1, 2, ...

Number of bubble size groups: Nbs = 1

### Scaled model parameters:

| Parameter | Equation |
|-----------|----------|
| $\hat{r} = \Lambda r$ | $\bar{K}_k = 3\Lambda^2K_k$ |
| $\hat{r}^o_{min} = \Lambda r^o_{min}$ | $\hat{r}_{min_n} = \Lambda r_{min_n}$ |
| $\hat{\beta}^o = \Lambda \beta^o$ | $\hat{\beta}_{f_n} = \Lambda \beta_{f_n}$ |
| $\hat{V}_t = \Lambda^3 V_t$ | |

| Parameter | Equation |
|-----------|----------|
| $\bar{\sigma} = \Lambda \sigma$ | $\bar{M} = \left(\frac{4\pi}{3}\right)\frac{M}{\Lambda^3}$ |
| $\bar{\sigma}_c = \Lambda \sigma_c$ | |

$$P_{\infty} = P_{H_2O} + p_{tCO_2}$$ (C.1)

$$t_{n+1} = t_n + \Delta t_n$$ (C.2)^a

### Bubble Number

$$\beta_{ex_n} = 1 + m_{\beta_{ex}}I_{ex_n}$$ (C.3)

$$P_{crush_n} = MAX\left[P_{crush_{n-1}}, (P_{amb_n} - P_{\infty}) - \sum_{k=1}^{N_g} p_{t_{k,n}}\right]$$ (C.4)^b

----

^a The integration step size Δtn is arbitrary and may be altered at any integration step, based on the magnitude of changes in bubble radii, δrn, to reduce computation time, but it should be small enough to yield results with desired accuracy.

^b The initial P^0_crush_0 ≡ P^0_crush is determined from saturation conditions at profile start (see footnotes c and e in this Appendix).

C-1
---

If $P_{\text{crush}_n} \leq P_{\text{crush}_{n-1}}$, $P_{\text{crush}_n} = P^o_{\text{crush}} + (P_{\text{crush}_{n-1}} - P^o_{\text{crush}}) \cdot \exp(-\Delta t_n / \tau_{P_c})$ (C.5)

$$\hat{\beta}_{f_n} = \hat{\beta}_{\text{ex}_n} \left[ \frac{2\hat{\sigma}_c \hat{\beta}^o}{2(\hat{\sigma}_c - \hat{\sigma}) + P_{\text{crush}_n} \hat{r}^o_{\text{min}}} \right]; \hat{r}^o_{\text{min}} = \hat{\beta}^o \left[ \ln(N^o_b) - \ln(N^{\text{min}}_b) \right]$$ (C.6)

$$P_{\text{ss}_n} = \left[ \sum_{k=1}^{N_g} p_{t_{k,n}} + P_\infty \right] - P_{\text{amb}_n}$$ (C.7)

$$N_{b_{\text{max},n}} = \text{MAX} \left[ N_{b_{\text{max},n-1}}, N^o_b \exp \left( -\frac{2\hat{\sigma}}{P_{\text{ss}_n} \cdot \hat{\beta}_{f_n}} \right) \right]$$ (C.8)

$\Delta n_{b_n} = [N_{b_{\text{max},n}} - N_{b_{\text{max},n-1}}]$

$n_{b_n} = n_{b_{n-1}} + \Delta n_{b_n}$ (C.9)

$$\hat{r}_{\text{min}_n} = \hat{\beta}_{f_n} \left[ \ln(N^o_b) - \ln(N^{\text{min}}_b) \right]$$ (C.10)

$$\hat{x}^o_{k,n} = P_{b_{k,n}} \hat{r}^3_{\text{min}_n}$$ (C.11)

**Bubble Radius and Pressure**

$$b_{k,n} = \bar{K}_k \frac{\Delta t_n}{\hat{r}^2_n}$$ (C.12)

$$a_{k,n} = (1 + \hat{r}_n) b_{k,n}$$ (C.13)

$$A_{k,n} = P_{b_{k,n}} + a_{k,n} \left( 1 - \frac{a_{k,n}}{2} \right) (p_{t_{k,n}} - P_{b_{k,n}})$$ (C.14)

$$B_{k,n} = \frac{1}{2} [(2a_{k,n} - b_{k,n} + a_{k,n} b_{k,n}) p_{t_{k,n}} + (a_{k,n} + b_{k,n})(1 - a_{k,n}) P_{b_n}]$$ (C.15)

$$\delta \hat{r}_n = \frac{\sum_{k=1}^{N_g} A_{k,n} - \left( P'_{\text{amb}_{n+1}} + \frac{2\hat{\sigma}}{\hat{r}_n} + M\hat{r}^3_n \right)}{\sum_{k=1}^{N_g} (3A_{k,n} - B_{k,n}) - \left( \frac{2\hat{\sigma}}{\hat{r}_n} - 3M\hat{r}^3_n \right)}; P'_{\text{amb}} = P_{\text{amb}} - P_\infty$$ (C.16)

$$\hat{r}_{n+1} = \hat{r}_n (1 + \delta \hat{r}_n)$$ (C.17)

C-2
---
$$P_{b_{k,n+1}} = A_{k,n} - (3A_{k,n} - B_{k,n})b^3_{r_n}$$ (C.18)

## Tissue Gas Tensions

$$\dot{V}_{O_2,n} = m_{VO_2} \cdot I_{ex_n} + \dot{V}_{O_2,rest}$$ (C.19)

$$\dot{Q}_{ex_n} = m_Q \cdot (\dot{V}_{O_2,n} - \dot{V}_{O_2,rest}) + \dot{Q}_{rest}$$ (C.21)

## Inert Gases

$$\tau_{k_n} = \frac{\alpha_{t_k}}{\alpha_{b_k}\dot{Q}_n}$$ (C.23)

$$\varepsilon_{k,n} = 1 - \exp\left(-\frac{\Delta t_n}{\tau_{k_n}}\right)$$ (C.24)

$$\hat{G}_{k_n} = \left(\frac{4\pi}{3}\right)\alpha_{t_k}\hat{V}_t\frac{n_{b_n}}{n_{b_{n-1}}} = \hat{G}_{k_{n-1}}\frac{n_{b_n}}{n_{b_{n-1}}}$$ (C.25)

$$\Delta\hat{G}_{k_n} = \left(\frac{4\pi}{3}\right)\alpha_{t_k}\hat{V}_t\Delta n_{b_n}$$ (C.26)

$$\hat{x}_{k,n+1} = P_{b_{k,n+1}}\hat{r}^3_{n+1}$$ (C.27)

$$p_{a_{k,n+1}} = p_{a_k}@t_{n+1} = F_{I_{k,n+1}}\left[(P_{amb_{n+1}} - P_{A_{H_2O}}) - P_{A_{CO_2}}\left(1-\frac{1}{RQ}\right)\right]$$ (C.28)

$$\upsilon_{k,n} = \frac{p_{a_{k,n+1}} - p_{a_{k,n}}}{\Delta t_n}$$ (C.29)

C-3
---
$$p_{tk,n+1} = p_{tk,n}(1-\varepsilon_{k,n}) + v_{k,n}\Delta t_n + \left[p_{ak,n} - \tau_k \left\{v_{k,n} + \hat{G}_{k_n} \frac{\hat{x}_{k,n+1} - \hat{x}_{k,n}}{\Delta t_n}\right\}\right]\varepsilon_{k,n}$$

$$(C.30)^c$$

$$- \Delta\hat{G}_{k_n}(\hat{x}_{k,n} - \hat{x}^o_{k,n})$$

**Oxygen**

$$\alpha'_{O2_n} = \alpha_{bO2} + Hb_c \left[\frac{a_1 + 2a_2p - a_2(a_1 - b_1p^2)}{(1.0 + b_1p + b_2p^2)^2}\right]\left[\frac{np^{\eta-1}}{P_{half}}\right]; p = \left(\frac{p^v_{O2_n}}{P_{half}}\right)^{\eta}$$

$$(C.31)$$

$$\tau_{O2_n} = \frac{\alpha_{tO2}}{Q_n \alpha'_{O2_n}}$$

$$(C.32)$$

$$\varepsilon_{O2_n} = 1-\exp\left(-\frac{\Delta t_n}{\tau_{O2_n}}\right)$$

$$(C.33)$$

$$\hat{G}_{O2_n} = \left(\frac{4\pi}{3}\right)\frac{n_{b_n}}{\alpha_{tO2}\hat{V}_t} = \hat{G}_{O2_{n-1}}\left(\frac{n_{b_n}}{n_{b_{n-1}}}\right)$$

$$(C.34)$$

$$\Delta\hat{G}_{O2_n} = \left(\frac{4\pi}{3}\right)\frac{\Delta n_{b_n}}{\alpha_{tO2}\hat{V}_t}$$

$$(C.35)$$

$$\hat{x}_{O2_{n+1}} = P_{bO2_{n+1}}\hat{r}^3_{n+1}$$

$$(C.36)$$

$$p_{aO2_{n+1}} = p_{aO2} @ t_{n+1} = P_{amb_{n+1}} - P_{H_2O} - P_{ACO2} - \sum p_{ak,n+1}$$

$$(C.37)$$

c The initial tissue tension of the kth inert gas under saturation steady-state conditions, $p_{tk,0}$, is the aterial tension, $p_{ak,0}$, for the gas given by Eq. (C.28) for the saturation pressure and breathing gas mix.

C-4
---
$$C_{aO_2,n} = \alpha_{bO_2}p_{aO_{2_n}} + Hb_cSO_2(@ PO_2 = p_{aO_{2_n}})$$ (C.38)^d

$$C_{aO_2,n+1} = \alpha_{bO_2}p_{aO_{2_{n+1}}} + Hb_cSO_2(@ PO_2 = p_{aO_{2_{n+1}}})$$ (C.39)^c

$$pO'_{2_n} = \frac{C_{aO_2,n}}{\alpha'_{O_{2_n}}} ; pO'_{2_{n+1}} = \frac{C_{aO_2,n+1}}{\alpha'_{O_{2_n}}}$$ (C.40)

$$υO_{2_n} = \frac{pO'_{2_{n+1}} - pO'_{2_n}}{\Delta t_n}$$ (C.41)

$$C_{vO_2,n} = \alpha_{bO_2}p_{vO_{2_n}} + Hb_cSO_2(@ PO_2 = p_{vO_{2_n}})$$ (C.42)

$$\dot{ρ}_n = \frac{\dot{V}_{O_{2_n}} + Q_n(C_{vO_{2_n}} - \alpha'_{O_{2_n}}p_{vO_{2_n}})}{\alpha_{TO_2}}$$ (C.43)

^d The percent hemoglobin saturation, SO₂, at prevailing oxygen tension pO₂ is computed with Lobdell's equation:^69

$$SO_2 = \frac{a_1p + a_2p^2}{1.0 + b_1p + b_2p^2} ; p = \left(\frac{pO_2}{p_{half}}\right)^η,$$

where
  a₁ = 0.34332,
  a₂ = 0.64073,
  b₁ = 0.34128,
  b₂ = a₂ = 0.0.64073,
  
  η = 1.58678, and
  p_half = half-saturation pO₂ of hemoglobin
           (with pO₂ in units of mm-Hg, p_half = 25.0 mm-Hg.)

C-5
---
$$p_{tO_{2_{n+1}}} = p_{tO_{2_n}}(1-\varepsilon_{O_{2_n}}) + \upsilon_{O_{2_n}}\Delta t_n$$

$$+ \left[p_{O_{2_n}} - \tau_{O_{2_n}}\left\{\upsilon_{O_{2_n}} + \dot{p}_n + \dot{G}_{O_{2_n}}\frac{(\hat{x}_{O_{2_{n+1}}} - \hat{x}_{O_{2_n}})}{\Delta t_n}\right\}\right]\varepsilon_{O_{2_n}} \qquad (C.44)^e$$

$$- \Delta \dot{G}_{O_{2_n}}(\hat{x}_{O_{2_n}} - \hat{x}_{O_{2_n,0}})$$

## VGE formation

$$LR = (V_b - V_{r0})N_{VGE}\Delta t_n, \qquad (C.45)$$

$$n_{b_{n+1}} = MAX[0, N_{b_n}(1-LR)], \qquad (C.46)$$

e The initial tissue O₂ tension under saturation steady-state conditions, $p_{tO_{2_0}}$, is the partial pressure, $p_{\upsilon O_{2_0}}$, corresponding to $C_{\upsilon O_{2_0}} = C_{aO_{2_0}} - \frac{V_{O_{2_0}}}{Q_0}$, where $C_{aO_{2_0}}$ is given by Eq. (C.38) at $p_{aO_2}$ given by Eq. (C.37) for the saturation pressure and breathing gas mix. $p_{\upsilon O_{2_0}}$ is determined by numerically inverting the blood O₂ content versus partial pressure curve, Eq. (C.42), at $C_{\upsilon O_{2_0}}$.

C-6
---
## 11. Appendix D. Hazard Function Formulation and Optimization

The hazard function in present work was elaborated from that in the BVM(3) probabilistic gas and bubble dynamics model developed earlier for air and N₂-O₂ diving.²⁶'²⁷ In the latter model, the instantaneous risk of DCS at time t in exposure i, h₁(t), is the sum of a weighted time-dependent dose, Δᵢ,ⱼ(t), in each of j = 1, 2, ..., nᶜ hypothetical tissue compartments. That is,

$$h_i(t) = \sum_{j=1}^{n_c} w_j\Delta_{i,j}(t),$$  (D.1)

where wⱼ is the weight – constant over all i and independent of time and all parameters in Δᵢ,ⱼ(t) – associated with the jᵗʰ compartment, and

$$\Delta_{i,j}(t) = [V_{i,j}(t) - V_j(0)].$$  (D.2)

Vᵢ,ⱼ(t) in Eq. (D.2) is the bubble volume in the jᵗʰ compartment at time t in the iᵗʰ exposure, and Vⱼ(0) is the initial nucleonic bubble volume in the compartment. The initial nucleonic bubble volume in each compartment is constant and the same for all exposures. Because the hazard, hᵢ(t), is a failure rate that must integrate over time to a dimensionless quantity, wⱼ in Eq. (D.1) has dimensions of 1/(volume × time).

While an implementation of the Van Liew and Hlastala two-region unstirred tissue model²⁸'³¹'⁷⁰ was used to model bubble evolution in the BVM(3) probabilistic model, the more theoretically robust 3RUT-MB model was used for this purpose in present work. Eq. (D.2) was elaborated using Eq. (A.12) to obtain the hazard function used in present work:

$$h(t) = \sum_j^{n_c} w_j(V_{b,j} - V_{r0j}) \cdot (N_{b,j})^{\beta_{N,j}},$$  (D.3a)

where m=1 has been assumed, the time-dependence of the compartmental bubble number is explicitly indicated, and a compartment-specific power term, βN,j, for the prevailing bubble number has been arbitrarily added to potentiate the contribution of the bubble number to the hazard as the bubble number increases.

It is shown in Appendix A that the compartmental bubble volumes in the 3RUT-MB model scale with an arbitrary compartmental Λⱼ³ factor having dimension 1/volume. The scaled counterparts of the volumes in Eq. (D.3a), V̂ᵢ,ⱼ(t) = Λⱼ³Vᵢ,ⱼ(t) and

D-1
---
$\dot{V}_j(0) = \Lambda_j^3V_j(0)$, can then be calculated with the piecewise-analytic solution derived in Appendix B with arbitrarily specified values of $\Lambda_j$.

The best fit of a given expression for h(t) to a collection of DCS incidence and time of onset data is obtained by adjusting the parameters of h(t) to maximize the likelihood of h(t) about the data. The likelihood is the joint probability of the observed outcomes for all exposures in the data. For N independent exposures, the likelihood is given by

$$L = \prod_{i=1}^N P(0_i)^{1-\delta_i} P(E_i)^{\delta_i},\tag{D.4}$$

where $\delta_i$ is the outcome variable for the $i^{th}$ exposure: $\delta_i = 1$ for failure (event occurred) and $\delta_i = 0$ for no failure until end of observation (right-censored observation). Marginal outcomes, for which $0 < \delta_i < 1$, are also allowed. Referring to Eqs. (1) and (2) in the body of this report, Eq. (D.4) is elaborated to yield

$$L = \prod_{i=1}^N \left[\left\{\exp\left(-\int_0^{t_i} h_i(t)dt\right)\right\}^{(1-\delta_i)} \left\{\exp\left(-\int_0^{t_{1i}} h_i(t)dt\right)\right\}^{\delta_i} \left\{1-\exp\left(-\int_{t_{1i}}^{t_{2i}} h_i(t)dt\right)\right\}^{\delta_i}\right],\tag{D.5}$$

where $t_{1i}$ is the last time in exposure i at which failure had not yet occurred, $t_{2i}$ is the first time in exposure i at which failure was known to have occurred, and $t_i$ is the right-censored time for exposure i. The likelihood is given in terms of the parameters in the model used to compute $\Delta_{i,j}(t)$, represented by vector $\rho$, and the weights $w_j$ of the tissue compartments, represented by vector $\mathbf{W}$:

$$L \equiv L(\rho,\mathbf{W}).\tag{D.6a}$$

The vectors $\rho$ and $\mathbf{W}$ comprise the $\beta$ vector in Eqs. (11) and (12) in the body of this report. It is now recognized that because the compartmental weights are constant and independent of the other model parameters, a set of optimum $w_j$, $j = 1, 2, ..., n_c$, exists for a given data set for any set $\rho$ of other compartmental parameter values.$^{71}$ This optimal set $\mathbf{W}$ can be determined independently for the trial set $\rho$ in each iteration of the optimization procedure. In present work however, the likelihood was conventionally maximized with the Marquart iterative nonlinear parameter optimization algorithm$^{46}$ without making any distinction between the $\rho$ and $\mathbf{W}$ vectors.

D-2
---
## 12. Appendix E. Summary Description of A1309 Model Training Data

| Data Set | Profile Description Summary | # Exposures | # DCS Observed |
|----------|------------------------------|-------------|----------------|
| USAF |  |  |  |
| (4.37 psia, Unknown A) | 60 min PB; 4.37 psia EVA sim/240 min;180 min GL PstB | 43 | 23 |
| (4.37 psia, Unknown B) | 15 min PB; 4.37 psia EVA sim/240 min;138 min GL PstB | 12 | 7 |
| (5.45 psia, Unknown) | 60 min PB; 5.45 psia (25K ft) EVA sim/240 min | 21 | 1 |
| (6 psia, Unknown) | 60 min PB; 6 psia (22.5K ft) EVA sim/240 min | 24 | 1 |
| (9.5 psia, Unknown) | 60 min PB; 9.5 psia (11.5K ft) EVA sim/240 min | 42 | 0 |
| 100% Suit-A | 0PB; 15.0K ft (8.3 psia) EVA sim/6hr, males | 10 | 0 |
| 100% Suit-B | 0PB; 16.5K ft (7.8 psia) EVA sim/6hr, males | 10 | 0 |
| 100% Suit-C | 0PB; 18.1K ft (7.3 psia) EVA sim/6hr, males | 11 | 0 |
| 100% Suit-D | 0PB; 18.1K ft (7.3 psia) EVA sim/6hr, females | 9 | 0 |
| 100% Suit-E | 0PB; 19.8K ft (6.8 psia) EVA sim/6hr, males | 11 | 0 |
| 100% Suit-F | 0PB; 19.8K ft (6.8 psia) EVA sim/6hr, females | 10 | 1 |
| 7.8 psia-A | 0PB; 7.8 psia, 50% O2, EVA sim/360 min, males | 94 | 1 |
| 7.8 psia-B | 0PB; 7.8 psia, 50% O2, EVA sim/360 min, females | 92 | 4 |
| 8.3 psia-A | 0PB; 8.3 psia, 50% O2, EVA sim/360 min, males | 20 | 1 |
| 8.3 psia-B | 0PB; 8.3 psia, 50% O2, EVA sim/360 min, females | 11 | 0 |
| 9.5 psia Validation-A | 0PB; 9.5 psia, 40% O2, EVA sim/360 min, females | 20 | 0 |
| 9.5 psia Validation-B | 0PB; 9.5 psia, 40% O2, EVA sim/360 min, males | 12 | 0 |
| BSI-A | Bends Screening Index study: 60 min PB; 30.0K ft (4.37 psia), rest/480 min | 17 | 10 |
| BSI-B | Bends Screening Index study: 60 min PB; 30.0K ft (4.37 psia), knee bends-overhead presses/480 min | 36 | 32 |
| BSI-C | Bends Screening Index study: 60 min PB; 27.6K ft (4.87 psia), knee bends-overhead presses/480 min | 83 | 66 |
| BSI-D | Bends Screening Index study: 60 min PB; 25.0K ft (5.45 psia), knee bends-overhead presses/480 min | 28 | 22 |
| BSI-E | Bends Screening Index study: 60 min PB; 22.5K ft (6.1 psia), knee bends-overhead presses/480 min | 46 | 24 |
| Bubb Threshold-A | 0PB; 16.0K ft (8.0 psia), 50% O2, EVA sim/360 min | 25 | 0 |
| Bubb Threshold-B | 0PB; 14.4K ft (8.5 psia), 50% O2, EVA sim/360 min | 10 | 0 |
| Bubb Threshold-C | 0PB; 12.3K ft (9.0 psia), 50% O2, EVA sim/360 min | 23 | 3 |
| Bubb Threshold-D | 0PB; 11.5K ft (9.5 psia), 50% O2, EVA sim/360 min | 6 | 0 |
| Bubb Threshold-E | 0PB;10.28K ft (10.0 psia), 50% O2, EVA sim/360 min | 9 | 0 |
| Bubb Threshold-F | 0PB; 9.0K ft (10.5 psia), 50% O2, EVA sim/360 min | 2 | 0 |

E-1
---
| Data Set | Profile Description Summary | # Exposures | # DCS Observed |
|----------|----------------------------|-------------|----------------|
| CO2-A | CO₂ in PB gas: 60 min PB, 100% O₂; 25K ft EVA sim/180 min | 38 | 4 |
| CO2-B | CO₂ in PB gas: 60 min PB, 97% O₂, 3% CO₂; 25K ft EVA sim/180 min | 37 | 3 |
| CO2-C | CO₂ in PB gas: 60 min PB, 100% O₂; 25K ft EVA sim/360 min | 25 | 24 |
| CO2-D | CO₂ in PB gas: 60 min PB, 97% O₂, 3% CO₂; 25K ft EVA sim/360 min | 25 | 19 |
| DNT-A | Inflight denitrogenation-staged ascent: 60 min PB;29.5K ft, 100 kcal rope pull exercise/240 min | 39 | 24 |
| DNT-B | Inflight denitrogenation-staged ascent:75 min PB;29.5K ft, 100 kcal rope pull exercise/240 min | 18 | 7 |
| DNT-C | Inflight denitrogenation-staged ascent: 135 min PB;29.5K ft, 100 kcal rope pull exercise/240 min | 33 | 15 |
| DNT-D | Inflight denitrogenation-staged ascent: 15 min PB;8.0K ft/60 min;29.5K ft, 100 kcal rope pull exercise/240 min | 17 | 11 |
| DNT-E | Inflight denitrogenation-staged ascent: 15 min PB;8.0K ft/120 min;29.5K ft, 100 kcal rope pull exercise/240 min | 15 | 6 |
| DNT-F | Inflight denitrogenation-staged ascent: 15 min PB;12.0K ft/60 min;29.5K ft, 100 kcal rope pull exercise/240 min | 16 | 10 |
| DNT-G | Inflight denitrogenation-staged ascent: 15 min PB;12.0K ft/120 min;29.5K ft, 100 kcal rope pull exercise/240 min | 16 | 7 |
| DNT-H | Inflight denitrogenation-staged ascent: 15 min PB;16.0K ft/60 min;29.5K ft, 100 kcal rope pull exercise/240 min | 31 | 12 |
| DNT-I | Inflight denitrogenation-staged ascent: 15 min PB;16.0K ft/120 min;29.5K ft, 100 kcal rope pull exercise/240 min | 33 | 13 |
| DNT-J | Inflight denitrogenation-staged ascent: 15 min PB;18.0K ft/ 60 min;29.5K ft, 100 kcal rope pull exercise/240 min | 34 | 21 |
| DNT-K | Inflight denitrogenation-staged ascent: 15 min PB;18.0K ft/120 min;29.5K ft, 100 kcal rope pull exercise/240 min | 31 | 14 |
| EffctEx-A | 60 min PB; 29.5K ft rest/240 min | 46 | 15 |
| EffctEx-B | 60 min PB; 29.5K ft isometric stacked weight, arm exercise/240 min | 25 | 10 |
| EffctEx-C | 60 min PB; 29.5K ft isotonic stacked weight, arm exercise/240 min | 22 | 9 |
| EffctEx-D | 60 min PB; 29.5K ft isometric stacked weight, leg exercise/240 min | 26 | 7 |
| EffctEx-E | 60 min PB; 29.5K ft isotonic stacked weight, leg exercise/240 min | 25 | 8 |
| EffctEx-F | 60 min PB; 27.5K ft rest/240 min | 13 | 5 |
| EffctEx-G | 60 min PB; 27.5K ft isometric stacked weight, arm exercise/240 min | 7 | 3 |
| EffctEx-H | 60 min PB; 27.5K ft isotonic stacked weight, arm exercise/240 min | 8 | 7 |
| EffctEx-I | 60 min PB; 27.5K ft isometric stacked weight, leg exercise/240 min | 8 | 3 |
| EffctEx-J | 60 min PB; 27.5K ft isotonic stacked weight, leg exercise/240 min | 8 | 4 |
| EffctEx-K | 60 min PB; 25.0K ft rest/240 min | 4 | 2 |
| EffctEx-L | 60 min PB; 25.0K ft isometric stacked weight, arm exercise/240 min | 2 | 1 |
| EffctEx-M | 60 min PB; 25.0K ft isotonic stacked weight, arm exercise/240 min | 2 | 1 |
| EffctEx-N | 60 min PB; 25.0K ft isometric stacked weight, leg exercise/240 min | 2 | 0 |
| EffctEx-O | 60 min PB; 25.0K ft isotonic stacked weight, leg exercise/240 min | 2 | 1 |
| EffctEx-P | 60 min PB; 22.5K ft rest/240 min | 1 | 1 |
| EffctEx-U | 60 min PB; 20.0K ft rest/240 min | 1 | 0 |

E-2