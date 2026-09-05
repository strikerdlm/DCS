# Accuracy-v3 methods

## Data and partitions

Retain the original grid unchanged. The primary policy excludes ambiguous scale rows and every duplicate cell whose reported targets disagree. Exact agreeing duplicates are collapsed. A source-row ledger records raw and suggested values, flags, cell IDs and primary inclusion; raw/rescaled sensitivity policies remain separate.

Freeze cell IDs before fitting any model: 65% train, 20% calibration, 15% test, seed 42. Every baseline, surrogate and compact comparison uses the same partition. Baseline selection uses calibration data only. Profile-grouped holdouts put all times for one altitude/PB/exercise profile in one split. Altitude-band holdouts and cleaning sensitivity are reported separately.

Targets are model probabilities, not patient events. Report MAE/RMSE in probability units (or explicitly labelled percentage points), MSE and R². Empty/constant/undefined metrics are null. Brier score and ROC-AUC require binary observed outcomes; thresholding a model grid does not create clinical validation.

## Surrogate and intervals

Synthetic VO2 traces augment categorical Rest/Mild/Heavy labels at a declared sampling interval; measured continuous-VO2 value is not established. Duration weighting includes partial samples, and one-minute windows use actual piecewise-constant durations.

The primary model uses 11 features. A redundant tissue proxy and duration-dependent VO2 integral are excluded because they can oppose the cumulative-duration monotonic constraint. The zero-event classifier has opposite monotone signs to the continuous probability model. The final point is (1−P(zero))×P(continuous). Split calibration uses absolute probability residuals of that final mixture on all calibration rows, never a post-calibration fixed zero gate.

Non-ZI Smithson–Verkuilen transforms are inverted using the training sample size. CQR quantiles are ordered and intervals use a conservative nonnegative correction. The finite-sample conformal rank is ceil((n+1)×confidence); insufficient calibration yields an uninformative interval. Support checking uses standardized covariance, training bounds and constant-feature constraints. These are distribution-support checks, not a clinical validity envelope.

Nominal 95% coverage relies on exchangeability. Dependent grid cells, profile shifts and conditioning on an accepted subset can defeat a marginal coverage interpretation. Coverage reports include sample counts and descriptive Wilson intervals; no guarantee is asserted for a subgroup or an individual.

## Personalization

Binary outcomes use y~Bernoulli(sigmoid(logit(base probability)+δ)), with δ~Normal(prior mean, prior variance). Accumulated observations are integrated by one-dimensional numerical quadrature; batch ordering must not change the result. Predictions integrate over the posterior and report equal-tailed credible intervals. Conformal coverage is not retained or inflated heuristically.

## EVA and source equations

NASA Eq. 6 uses k=exp(λ×VO2)/519.37 min⁻¹, λ=0.025 (RM) or 0.030 (NM), and dry ambient nitrogen. Humidified inspired O2 is a separate gas calculation. Habitat equilibration uses an explicitly declared 360-minute compartment starting from 11.6 psia tissue N2. PB and EVA workloads are separate; pressure and workload segments propagate sequentially to exact boundaries.

The Eq. 14/15 endpoint is a four-hour, 4.3-psia oxygen, adynamic source-reference calculation. It is not a cumulative hazard, a time-risk curve, an EVA confidence band, or validation of a novel profile. Unsupported quantities are null. Non-DCS hazards retain arithmetic/entered/measured indicators, not heuristic event probabilities.

Planning rules and scientific applicability are separate. Configured stop conditions remain visible during abstention. Telemetry snapshots cannot retrospectively replace a whole mission workload, and uncalibrated physiological proxies are not converted to risk.

3RUT remains quantitatively disabled: corrected units and solver checks do not resolve the gain/volume convention or replace full source-profile benchmarks. Reproduction and evidence are linked in the [runbook](runbook.md).
