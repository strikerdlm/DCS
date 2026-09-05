# Scientific provenance and limits

The source reference for NASA kinetics and endpoints is [Conkin, NASA TP-2004-213158 (2004)](https://www.nasa.gov/wp-content/uploads/2023/03/conkin-dcs-exercise-tp-213158-2004.pdf). Eq. 6, RM/NM Eq. 14/15 and Table 17 are regression anchors. TP-2004-213158 must not be confused with the unrelated TM-2004-213093 citation in older project material.

The implemented transitions use dry ambient nitrogen. RM λ=0.025 and NM λ=0.030 belong to their fitted equations, not a user-tunable hybrid. Reference probabilities have a four-hour horizon at 4.3 psia with oxygen breathing and declared adynamic source assumptions; extrapolation to moving EVA, arbitrary durations or variable-pressure profiles is unsupported.

Pressure calculations use a layered standard atmosphere through 20 km, including the isothermal layer above 11 km. NASA's [standard-atmosphere explanation](https://www.grc.nasa.gov/www/k-12/airplane/atmosmet.html) describes the layer distinction. Pressure altitude is not geometric height or an individualized physiological equivalent.

ADRAC-form coefficients in the browser are re-fitted to the training portion of the repository's audited model grid, not transcribed original published coefficients. Grid agreement must not be described as clinical discrimination/calibration. The raw grid contains unresolved unit and duplicate disagreements; primary and sensitivity analyses are distinct.

The 3RUT source transcription is retained at `legacy/BU_3RUT/3RUT_MBe1/3RUT_Theory.md`. A44/B47 volume normalization, perfusion units, alveolar CO2 and adaptive-stage checks informed corrections. Gain/volume conventions and complete benchmark profiles remain unresolved. Neither absolute risk nor shape validity has been established.

Split conformal methods require held-out calibration on the final deployed predictor and exchangeability. [Romano, Patterson and Candès, Conformalized Quantile Regression (2019)](https://papers.nips.cc/paper/2019/file/5103c3584b063c431bd1268e9b5e76fb-Paper.pdf) is the primary method reference. Statistical interval coverage on a model grid does not quantify biological uncertainty.

Scenario preset names and contextual NASA/ESA links are background only: they do not validate those illustrative schedules. Configured L×C classifications are not agency-approved mission rules. Device accuracy, clinical outcome validation and operational acceptance require separate evidence.
