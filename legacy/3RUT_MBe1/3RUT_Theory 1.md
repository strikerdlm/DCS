Navy Experimental Diving Unit                                      TA 10-12
321 Bullfinch Road                                                 NEDU TR 18-01
Panama City, FL 32407-7015                                         Jan 2018

# A Probabilistic Model of Altitude Decompression Sickness Based on the 3RUT-MB Model of Gas Bubble Evolution in Perfused Tissue

| NAVSEA |
|---------|
| NAVAL SEA SYSTEMS COMMAND |
| Navy Experimental Diving Unit |

| Authors: | Distribution Statement A: |
|----------|---------------------------|
| Wayne A. Gerth | Approved for public release; |
| Ramachandra Srini Srinivasan | distribution is unlimited. |
| F. Gregory Murphy | |
| Keith A. Gault | |
---
| REPORT DOCUMENTATION PAGE | Form Approved OMB No. 0704-0188 |
|-----------------------------------|----------------------------------|

Public reporting burden for this collection of information is estimated to average 1 hour per response, including the time for reviewing instructions, searching existing data sources, gathering and maintaining the data needed, and completing and reviewing this collection of information. Send comments regarding this burden estimate or any other aspect of this collection of information, including suggestions for reducing this burden to Department of Defense, Washington Headquarters Services, Directorate for Information Operations and Reports (0704-0188), 1215 Jefferson Davis Highway, Suite 1204, Arlington, VA 22202-4302. Respondents should be aware that notwithstanding any other provision of law, no person shall be subject to any penalty for failing to comply with a collection of information if it does not display a currently valid OMB control number. PLEASE DO NOT RETURN YOUR FORM TO THE ABOVE ADDRESS.

| 1. REPORT DATE (DD-MM-YYYY) | 2. REPORT TYPE | 3. DATES COVERED (From - To) |
|---------------------------|----------------|------------------------------|
| 19-01-2018 | Technical Report | Oct 2004 TO Sep 2017 |

| 4. TITLE AND SUBTITLE | 5a. CONTRACT NUMBER |
|----------------------|----------------------|
| A Probabilistic Model of Altitude Decompression Sickness Based on the 3RUT-MB Model of Gas | |
| Bubble Evolution in Perfused Tissue | 5b. GRANT NUMBER |
| | |
| | 5c. PROGRAM ELEMENT NUMBER |
| | |

| 6. AUTHOR(S) | 5d. PROJECT NUMBER |
|--------------|---------------------|
| Wayne A. Gerth, Ramachandra Srini Srinivasan; F. Gregory Murphy, Keith A. Gault. | |
| | 5e. TASK NUMBER |
| | 04-13 |
| | 5f. WORK UNIT NUMBER |
| | |

| 7. PERFORMING ORGANIZATION NAME(S) AND ADDRESS(ES) | 8. PERFORMING ORGANIZATION REPORT |
|---------------------------------------------------|-----------------------------------|
| Navy Experimental Diving Unit | NUMBER |
| 321 Bullfinch Road | 18-01 |
| Panama City FL 32407-7015 | |

| 9. SPONSORING / MONITORING AGENCY NAME(S) AND ADDRESS(ES) | 10. SPONSOR/MONITOR'S ACRONYM(S) |
|----------------------------------------------------------|----------------------------------|
| Naval Sea Systems Command | NAVSEA 00C |
| 1333 Isaac Hull Avenue, SE | |
| Washington Navy Yard D.C. 2037 | 11. SPONSOR/MONITOR'S REPORT |
| | NUMBER(S) |

12. DISTRIBUTION / AVAILABILITY STATEMENT
Distribution Statement A: Approved for public release; distribution is unlimited

13. SUPPLEMENTARY NOTES

14. ABSTRACT
Decompression sickness (DCS) in man can occur with excessively rapid and extensive reductions of the ambient pressure in diving, aviation, and spaceflight operations. Probabilistic models of DCS occurrence are particularly well suited for managing the risks of DCS in these operations, but have been limited in ability to accommodate the influences of known factors that govern DCS outcomes as such factors may come in and out of play during arbitrarily varying periods in an exposure. We here describe a probabilistic model of DCS occurrence able to accommodate the influences of pressure, changing inspired inert gas, oxygen breathing, and exercise in profiles of arbitrary complexity. The model is a time-dependent covariate survival model in which the risks of DCS during an exposure are determined as functions of the prevailing volumes and profusions of gas bubbles in a perfusion-limited gas exchange compartment. The bubbles vary in volume by diffusion-limited exchange of gas between the bubbles and their surroundings according to an implementation of a three-region unstirred tissue model of gas bubble evolution elaborated to accommodate the influences of exercise and oxygen breathing on compartmental gas exchange and bubble nucleation. Parameters in the model were fit with maximum likelihood techniques to training data comprising detailed descriptions of actual human decompressions and their observed DCS outcomes in 2598 man-exposures to hypobaric pressures completed in a wide variety of NASA, NASA-sponsored, and U.S. Air Force chamber trials. The model underestimates the observed DCS occurrence density in the first four hours after start of the last decompression and consequently fails to fit the data. However, when model estimates of DCS occurrence are made with planned times at altitude, not actual times that are shorter than planned due to occurrence of DCS, the model fits data from 84 of the 117 groups in the training data to within a chi-square P<0.05. In this form, the model is shown to perform better than other published models on a variety of data subset collections that is much more diverse than can be handled by any one of the other models.

15. SUBJECT TERMS
Decompression sickness risk, hypobaric exposure, survival analysis, maximum likelihood, probabilistic models, gas and bubble dynamics

| 16. SECURITY CLASSIFICATION OF: | 17. LIMITATION OF | 18. NUMBER | 19a. NAME OF RESPONSIBLE |
|----------------------------------|-------------------|------------|---------------------------|
| | ABSTRACT | OF PAGES | PERSON |
| | | | NEDU Librarian |
| a. REPORT | b. ABSTRACT | c. THIS PAGE | Unclassified | 123 | 19b. TELEPHONE NUMBER (include |
| Unclassified | Unclassified | Unclassified | | | area code) |
| | | | | | 850-230-3100 |

Standard Form 298 (Rev. 8-98)
Prescribed by ANSI Std. Z39.18

i
---
## CONTENTS

| Section | Page No. |
|---------|----------|
| Report Documentation Page | i |
| Contents | ii |
| Nomenclature | iv |
| 1. Introduction | 1 |
| 2. Methods | 3 |
| 2.1 3RUT-MB Model | 3 |
| 2.1.1 Quantification of Exercise | 5 |
| 2.1.2 Compartmental Oxygen Consumption, Perfusion, and O₂ Tension | 5 |
| 2.1.3 Bubble Nucleation | 6 |
| 2.1.4 Venous Gas Emboli (VGE) Formation | 7 |
| 2.2 Definition of the Hazard Function | 7 |
| 2.3 Model Optimization by Likelihood Maximization | 8 |
| 2.4 Model Training Data | 9 |
| 2.4.1 Augmented NMRI Standard format | 9 |
| 2.4.2 USAF Data | 9 |
| 2.4.3 NASA Data | 10 |
| 2.4.4 Exercise Coding | 10 |
| 2.4.5 Overall Training Data Summary | 13 |
| 3. Results | 14 |
| 3.1 Optimized 3RUT-MBe1 Model Parameters | 14 |
| 3.2 Model Goodness-of-Fit | 16 |
| 3.2.1 Observed and Estimated DCS Occurrence Density Distributions | 16 |
| 3.2.2 Pearson Residuals and Global Chi-Square | 17 |
| 4. Discussion | 21 |
| 4.1 Prebreathe and Exercise Effects on Gas Elimination | 21 |
| 4.2 Prebreathe and Exercise Effects on Bubble Nucleation | 23 |
| 4.3 Comparative Model Performance | 27 |
| 4.4 Feaures of Model Performance | 32 |
| 4.5 Model Deficiencies and Remaining Issues | 35 |
| 5. Conclusions | 37 |
| 6. Acknowledgements | 38 |
| 7. References | 39 |
| 8. Appendix A. Three-Region Unstirred Tissue Multiple Bubble (3RUT-MB) Model of Tissue Gas and Bubble Dynamics | A-1 |
---
8.1 Single Diffusible Gas.....................................................................................A-1
   8.1.1    Multiple Bubbles of Same Size ..........................................................A-1
   8.1.2    Multiple Bubbles of Different Sizes ....................................................A-3
   8.1.3    Exercise Effects on Blood-Tissue Gas Exchange .............................A-4

8.2 Multiple Diffusible Gases ...............................................................................A-4
   8.2.1    Tissue O2 Tension with O2 as a Diffusible Gas..................................A-6
   8.2.2    Exercise Effects on Tissue O2 Consumption .....................................A-8

8.3 Bubble Nucleation and Variable Bubble Number ...........................................A-9
   8.3.1    Single Time-Dependent Bubble Size Approximation .......................A-12

8.4 Scaled 3RUT-MB Model ..............................................................................A-13

8.5 Model Operation and Initial Values ..............................................................A-15

9. Appendix B. Piece-Wise Analytic Approximation of the Three-Region
   Unstirred Tissue Multiple Bubble (3RUT-MB) Model of Tissue Gas and
   Bubble Dynamics ....................................................................................................B-1

   9.1 Single Diffusible Gas......................................................................................B-1
      9.1.1    Multiple Bubbles of Same Size ..........................................................B-1
               9.1.1.1    Changes in Bubble Radius and Bubble Gas Pressure........B-1
               9.1.1.2    Tissue Gas Tension with Time-Dependent Changes
                            in Tissue Blood Flow .........................................................B-11
                            9.1.1.2.1    General Model of Time-Dependent Changes in
                                           Blood Flow ......................................................B-12
                            9.1.1.2.2    Multi-Exponential Model of Time-Dependent
                                           Changes in Blood Flow ...................................B-14
                            9.1.1.2.3    Coupling of Compartmental O2 Consumption and
                                           Blood flow........................................................B-18
      9.1.2    Multiple Bubbles of Different Sizes ..................................................B-19

   9.2 Multiple Diffusible Gases .............................................................................B-21
      9.2.1    Tissue O2 Tension with O2 as a Diffusible Gas................................B-23
               9.2.1.1    Multiple Bubbles of Same Size..........................................B-23
               9.2.1.2    Multiple Bubbles of Different Size .....................................B-26
      9.2.2    Variable Bubble Number: Single Time-Dependent Bubble Size
               Approximation .................................................................................B-27

   9.3 Semi-Analytic Solution of the Fick Equation in the 3RUT-MB Model ...........B-31

10. Appendix C. Summary of Recursive Equations for Solution of 3RUT-MBe1
    Model ..............................................................................................................C-1–C-6

11. Appendix D. Hazard Function Formulation and Optimization .........................D-1–D-2

12. Appendix E. Summary Description of A1309 Model Training Data................. E-1–E-5

13. Appendix F. Pearson χ2 Statistics for Optimized 3RUT-MBe1 Model on its
    A1309 Training Data ....................................................................................... F-1–F-3
---
# NOMENCLATURE

| Symbol | Definition |
|--------|------------|
| Ab | bubble surface area |
| α<sub>b<sub>k</sub></sub> | solubility of gas k in blood |
| α<sub>t<sub>k</sub></sub> | solubility of gas k in tissue |
| α<sub>b<sub>O2</sub></sub> | O<sub>2</sub> solubility in blood |
| α<sub>t<sub>O2</sub></sub> | O<sub>2</sub> solubility in tissue |
| α'<sub>O2</sub> | slope of the whole blood O<sub>2</sub> solubility curve in the region of the prevailing venous O<sub>2</sub> tension |
| BN,j | bubble number power factor |
| β | vector of adustable parameters in the hazard function; combination of ρ and W parameter vectors |
| β0, β1, β2 | adjustable parameters in fitted V̇<sub>O2</sub> versus work rate (Watts) equation |
| β | generalized slope factor for integral distribution of bubble nuclei sizes |
| β<sup>o</sup> | slope factor for initial integral distribution of bubble nuclei sizes |
| β<sub>ex</sub> | dimensionless exercise-dependent β modifying factor |
| β<sub>f</sub> | prevailing slope factor for integral distribution of bubble nuclei sizes after accommodation of P<sub>crush</sub> and exercise effects |
| C<sub>a<sub>O2</sub></sub> | O<sub>2</sub> concentration in arterial blood entering tissue |
| C<sub>v̄<sub>O2</sub></sub> | O<sub>2</sub> concentration in mixed venous blood leaving tissue |
| D<sub>t,k</sub> | diffusivity of gas k in tissue |
| dt | integration time step |
| dt<sub>max</sub> | maximum allowed integration time step |
| dt<sub>min</sub> | minimum allowed integration time step |
| dt<sub>k</sub> | integration time step decay constant |
| Δt<sub>n</sub> | integration time step n |
| Δ<sub>i,j</sub>(t) | time-dependent dose in compartment j during the i<sup>th</sup> exposure |
| δ<sub>i</sub> | binary outcome variable, exposure i |

iv
---
| Symbol | Definition |
|--------|------------|
| δ̂r̂m,n | scaled radius change of bubble in mth size group in integration step n |
| FIO2 | inspired oxygen fraction |
| f(t) | function in linearization of the Fick equation |
| Gk(t) | with xk(t), amount of gas k in Nb bubbles |
| g(t) | function in linearization of the Fick equation |
| gj | jth compartment gain factor in hazard function |
| h(t) | hazard function |
| Iq(t) | indefinite integral in integrating factor for general solution of p(t) with exercise |
| Iex | exercise intensity ≡ whole body O2 consumption rate |
| i | subscript for individual exposure, suppressed when reference is clear from context |
| j | subscript for individual compartment, suppressed when reference is clear from context |
| Km | bubble surface permeability; may be subscripted for individual gas, hatted if scaled |
| k | subscript for individual diffusible gas |
| L(β) | likelihood of a data set of N individual exposures, as function of β |
| li(β) | likelihood of individual exposure i |
| LR | compartmental bubble loss rate via VGE formation |
| Λ | 3RUT-MB scale factor |
| M | modulus of elasticity; may be subscripted for bubble size group, hatted if scaled |
| m | subscript for individual bubble size group, suppressed when reference is clear from context |
| mβex | factor (≥ 0) governing the sensitivity of β to exercise intensity, Iex |
| mV̇O2 | rate of change of V̇O2 with Iex |
| mQ̇ | rate of change of Q̇ with V̇O2 |
| N | number of exposures in training data |
---
| Symbol | Definition |
|--------|------------|
| N°b | total number of bubble nuclei in a compartment |
| Nb | total number of bubbles from recruited nuclei in a compartment |
| Nbs | number of bubble size groups in a compartment |
| Ng | total number of diffusible gases in model |
| n | subscript for integration step |
| nb | number of bubbles in size group m |
| nc | number of gas-exchange compartments in model |
| υk,n | rate of change of arterial gas k partial pressure in integration step n |
| P(0) | probability of no-DCS |
| P(E) | probability of DCS |
| Pamb | ambient hydrostatic pressure |
| P'amb | ambient hydrostatic pressure less partial pressures of the infinitely diffusible gases, assumed the same in all compartments |
| PDCS | ≡ P(E), probability of DCS |
| PAco2 | alveolar CO2 partial pressure |
| PAo2 | alveolar O2 partial pressure |
| pak | arterial O2 partial pressure |
| pvo2 | O2 partial pressure in mixed venous blood |
| PB | "prebreathe" |
| PbT,m | total pressure of all diffusible gases in bubbles of mth size group |
| Pb,k | partial pressure of gas k in bubble |
| P∞ | total pressure of the infinitely diffusible gases in bubble |
| pcrush | bubble nucleus crush pressure |
| Pss | prevailing compartmental gas supersaturation |
| pt,k | partial pressure of gas k in tissue |
| Q(t) | blood flow per unit volume of tissue |

vi
---
| Symbol | Definition |
|--------|------------|
| q | coefficient proportional to blood flow; may be a function of time t |
| RQ | respiratory quotient |
| r | bubble radius, hatted if scaled |
| r⁰ₘᵢₙ | minimum bubble nuclear radius that can be recruited for growth at prevailing gas-supersaturation |
| ρ | total number of adjustable parameters in model |
| ρ | vector of adjustable parameters in Δᵢ,ⱼ(t); i=1, ..., N; j=1, ..., nₑ |
| Sₓₙ | gas loss rate into bubbles in time step n |
| σ | gas-liquid surface tension, hatted if scaled |
| σc | crumbling compression; counters surface tension, hatted if scaled |
| t₁ | time an individual is last known to be DCS-free in an exposure |
| t₂ | time an individual is first known to have DCS in an exposure |
| τ | compartmental blood-tissue gas exchange time constant; may be subscripted for individual gas |
| τₚc | Pcrush decay time constant |
| τᵥₒ₂ | time constant associated with the exponential change in V̇O₂ |
| Vb | bubble volume, hatted if scaled |
| Vr0 | nucleonic bubble volume, hatted if scaled |
| V̇O₂ | compartmental O₂ consumption rate |
| V̇O₂,wb | whole-body O₂ consumption rate |
| V̇O₂,wb,rest | assumed whole body O₂ consumption rate during rest |
| ΔV̇O₂ex | change in compartmental O₂ consumption rate with exercise relative to resting rate |
| W | work rate (Watts) |
| W | vector of compartmental weights in the hazard function |
| xk(t) | with Gk(t), amount of gas k in Nb bubbles, hatted if scaled |
| χ² | chi-square statistic |

vii
---
# 1. Introduction

Decompression sickness (DCS) in man can occur with excessively rapid and extensive reductions of the ambient pressure.¹ Reductions of ambient pressure that put personnel at risk for DCS occur in diving, aviation, and spaceflight operations. Programmatic management of these risks requires: a) definition of risk envelopes for all routine and emergency decompressions that are or may be encountered by at-risk personnel; b) quantitative consideration of the inclusion or introduction of DCS risks in the design, testing, and implementation of new operational procedures and equipment, and; c) real-time monitoring of DCS risk incurred by personnel during various operations. Probabilistic models of DCS occurrence are particularly well suited for application to these problems.² Such models are readily used to estimate the probabilities of DCS in different pressure profiles and to compute decompression schedules that keep estimated risks of DCS within any user-specified acceptable limit.³,⁴

Risks of DCS in early probabilistic models of DCS occurrence were based on time-independent covariates, i.e., governing factors that are fixed properties of an exposure. Empirical log-logistic models of this type required additional model terms to accommodate added features of an exposure. As a result, such models were tailored to decompression profiles of particular type, limiting their ability to accommodate exposure profiles of arbitrary complexity. Models of this type were developed for no-stop air-diving⁵ and for simple single-ascent hypobaric exposures⁶⁻¹¹. Other dose-response models were applicable to more complex exposures for which a single-valued DCS dose could be computed. Gernhardt described the first model of this class in which the probability of DCS was given in terms of a computed maximum bubble volume attained in a series of parallel-perfused gas exchange compartments, a volume that could be computed for a profile of arbitrary complexity.¹² Other models of this type were described by Gerth and Vann.¹³ Such models provided a mechanistic foundation that conformed to the well-accepted idea that DCS is initiated by in vivo bubble formation and growth.¹,¹⁴

More comprehensive probabilistic models of DCS occurrence have been developed based on the formalism of survival analysis.¹⁵ Such models not only account for DCS occurrence per se, but also account for the time of DCS occurrence in an exposure. With consideration that an exposure can be completed only with an outcome of DCS or no DCS, the probability P(0) of surviving DCS-free to time t in an exposure profile is given in survival models by

$$P(0) = exp[-\int_0^t h(t)dt],$$

where h(t) is the hazard function that gives the instantaneous rate of DCS occurrence at time t in those individuals in the exposure that have not developed DCS up to time t and
---
hence remain at risk for DCS at that time.<sup>16,17</sup> The hazard function<sup>a</sup> expresses the quantitative relationships between the putative governing factors of DCS onset and the DCS or no DCS outcome. The probability P(E) that DCS will occur between times t<sub>1</sub> and t<sub>2</sub> in the profile is given by Eq. (2):

$$P(E) = \left\{exp\left[-\int_0^{t_1} h(t)dt\right]\right\}\left\{1-exp\left[-\int_{t_1}^{t_2} h(t)dt\right]\right\}. \qquad (2)$$

The challenge in the development of these models is to define the hazard function in such a fashion that it properly accommodates the known or suspected factors or covariates that govern DCS outcomes in the exposures of interest.

A variety of survival models have been developed in which the hazard is cast in terms of time-independent covariates.<sup>18-23</sup> Such accelerated failure time models incorporate time as a fixed-valued internal covariate which, when once specified, results in a hazard expression that does not vary with time in an exposure. As with other time-independent covariate models, additional model terms are required to accommodate added features of an exposure, preventing any one model from accommodating exposure profiles different from those for which the model was designed.

Survival models are also readily based on hazard functions that vary with time in an exposure. Such functions respond to a covariate process given by the time-dependent variation of a limited number of covariates throughout an exposure.<sup>16</sup> The covariate process is external to the individual at risk and hence to the model. Because the path of the covariate process through time (e.g., a matrix of pressure, time, inspired gas composition, and exercise that describes the time course of how these parameters vary during an exposure) is not fixed in such models, the models do not need to increase in complexity as the complexity of the covariate process increases. Such models can consequently accommodate the influences of known factors that govern DCS outcomes as the factors come in and out of play during different periods in exposures of arbitrary complexity, but exploitation of this capability has been limited in models developed to date.

Probabilistic gas and bubble dynamics models of DCS occurrence provide the structural flexibility to accommodate the influences of pressure, inspired gas, and exercise on DCS outcomes as these factors may change in arbitrarily complex exposure profiles. Such models are time-dependent covariate models in which the body is represented by a series of hypothetical tissues or compartments that exchange gas with the environment via the lungs and blood. Risks of DCS are determined as functions of the prevailing volumes and numbers of gas bubbles in the compartments, bubbles that vary in volume by diffusion-limited exchange of gas between the bubbles and their surroundings. Tikuisis and coworkers described the first models of this type based on a model of extravascular gas bubble evolution similar to that described by Gernhardt.<sup>24,25</sup> Shortly thereafter Gerth and Vann described a time-dependent covariate model of DCS

<sup>a</sup> The terms "hazard function" and "risk function" are used synomously in this report. The hazard is also referred to as the "instantaneous risk."

2
---
occurrence26,27 based on a model of gas bubble evolution developed by Van Liew and Hlastala.28 Theoretical inconsistencies in this model of bubble evolution29 were corrected in a more rigorous three region unstirred tissue model able to accommodate multiple bubbles in a compartment.30,31 This 3RUT-MB model of gas and bubble dynamics was enhanced in present work to account for effects of exercise and oxygen breathing on in vivo gas exchange and bubble nucleation and optimized about laboratory data from 2598 man-exposures in widely varying types of hypobaric decompression profiles.

## 2. Methods

Our modeling approach followed the paradigm for the pathophysiology of DCS described by Tikuisis and Gerth.1 Excessively rapid and extensive decompression can cause the hydrostatic pressure in one or more body tissues to fall below the sum of the dissolved gas partial pressures in the tissue, producing a thermodynamically unstable gas-supersaturated state. The latter may be relieved with return to a gas-saturated state either by physiological gas elimination or by in situ nucleation and growth of gas bubbles. The instantaneous risk of DCS is assumed to be a function of the numbers and volumes of gas bubbles formed in the latter event. Following the approach pioneered by Haldane and coworkers,32 the body was modeled in present work as a hypothetical series of parallel-perfused compartments. Bubble evolution producing risk of DCS was then modeled in each compartment with an enhanced version of the 3RUT-MB model.

### 2.1 3RUT-MB Model

Essential features of the 3RUT-MB model are schematized in Figure 1. The hypothetical series of parallel perfused compartments comprising the body is shown on the left, and a detail of one compartment is shown on the right.

As originally described, each compartment was envisioned to be perfused at a constant rate and contain a fixed number of bubbles of potentially different sizes. It was noted in principle that the model could account for the participation of multiple diffusible gases in the evolution of any given bubble, but the equations to do so were not explicitly given. Finally, oxygen was presumed to be present in tissue at a fixed partial pressure and particicpate in bubble evolution with water vapor and carbon dioxide as an infinitely diffusible gas. The quantitative relationships comprising the original 3RUT-MB model are outlined in Appendix A.

Provisions were added to the model in present work to accommodate hypothetical mechanisms by which risks of DCS may be influenced by performance of exercise during different parts of an exposure profile. These provisions included mechanisms for time-dependent variation of the compartmental perfusion rate and number of bubbles, and for the participation of oxygen as a diffusible gas in bubble evolution with exercise-dependent variation of the tissue oxygen partial pressure. These model enhancements are summarized below and described in more detail in Appendix A. A piece-wise

3
---
 analytic approximation of the model equations was developed by exploiting the linear
 structure of the Fick equation, as described in Appendix B. The approximation is
 formulated as a set of recursive analytic relationships that advance the model state from
 one integration step to the next throughout an exposure profile.


                                    Heart and Lungs



                            Q1                                                                                                                Qt                                                                                           Qt
                                                                                                                                              Pa
                                                                                                                                                                                                                                           Pv

                                                                                                                                                                                          Well-Stirred
                                                                                                                                                                                            Region



                                                                                                                                                                          1               Unstirred

                           Q2
                                                                                                                                                                                          Diffusion
                                                                                                                                                                                          Regions



                            Q3
                                                                                                                                                                       2
                                                                                                                                                                                          3
 Figure 1.                                                          Schematic of the three-region unstirred tissue multiple bubble (3RUT-MB)
compartmental                                                                     model                                 underlying                the  DCS     hazard       function  in           present  work.                    The
hypothetical series of parallel perfused compartments comprising the body is shown on
the left. Each compartment is perfused with arterial blood at a characteristic volume-
average rate of                                                                    Q                                                                                                                               (mL·mL tissue -1·minute -1), which is subscripted to indicate individual
 compartments. One or more bubbles can nucleate in any compartment depending on the
 history of ambient pressure and breathing gas. The compartment shown in detail on the
right has three bubbles. The diffusion region around each bubble is unstirred and
heterogeneously perfused with zero gas flux at the outer boundary indicated by the light
dotted line. Bubble 1 is totally isolated while bubbles 2 and 3 have some common
boundary, on either side of which gas diffuses in opposite directions. Pa denotes the
 vector of arterial gas tensions, which is the same for all compartments. Pv denotes the
 vector of compartment-specific venous gas tensions. Dotted double-headed arrows
 indicate that the overall compartmental volume varies with bubble volumes, while the
 compartmental liquid volume remains constant.



 Theoretical development of the model in Appendices A and B is presented for arbitrary
 numbers of hypothetical tissue-blood gas exchange compartments and diffusible gases.
 The final enhanced 3RUT-MB model in present work, designated 3RUT-MBe1, was a
 one-compartment model with two diffusible gases, nitrogen and oxygen, implemented
 with relationships summarized in Appendix C.



                                                                                                                                                            4
---
## 2.1.1 Quantification of Exercise

Exercise is the use of energy to generate force to do work or oppose a resistance. Power is the rate of energy usage, or equivalently, the rate of doing work. It is well known that the whole-body O₂ consumption rate, V̇O₂,wb, increases linearly with the power output (W/time) for most types of exercise.³³,³⁴ Accordingly, the intensity of exercise performed during any given period of time in an exposure, regardless of the type of exercise, was characterized in present work by the prevailing V̇O₂,wb during the period. Exercise effects on model parameters in the period were then considered in terms of the exercise intensity level, Iex, given by

Iex=MAX(V̇O₂,wb - V̇O₂,wb,rest , 0.0),                                 (3)

where V̇O₂,wb is the rate of whole-body O₂ consumption during the period of exercise and V̇O₂,wb,rest is an assumed rate of whole body O₂ consumption during rest.

## 2.1.2 Compartmental Oxygen Consumption, Perfusion, and O₂ Tension

Cardiac output and regional blood flow have been shown to be linear functions of the rate of whole body O₂ consumption (V̇O₂,wb) and the regional oxygen consumption rate (V̇O₂), respectively.³⁵ It was assumed on this basis that the O₂ consumption rate in a given model compartment is a linear function of the whole body O₂ consumption rate:

V̇O₂ = mV̇O₂ · Iex + V̇O₂,rest ,                                       (4)

where mV̇O₂ is the rate of V̇O₂ change with Iex, and V̇O₂,rest is the rate of tissue O₂ consumption at rest. The compartmental blood flow rate was then assumed to increase linearly with the compartmental O₂ consumption rate:

Q̇ = mQ · (V̇O₂ - V̇O₂,rest) + Q̇rest ,                                 (5)

where mQ is the rate of change of Q̇ with V̇O₂ , Q̇rest is the resting compartmental blood flow rate at V̇O₂ = V̇O₂,rest , and Q̇ and Q̇rest are in units of flow per unit tissue volume. Exercise then directly affects the kinetics of blood-tissue exchange of gas k by altering the compartmental time constants for such exchange:

τk = αtk / (Q̇αbk) for inert gases and τO₂ = αtO₂ / (Q̇α'O₂) for O₂,    (6)

5
---
where α<sub>tk</sub> and α<sub>bk</sub> are the solubilities of inert gas k in tissue and blood, respectively, and α'<sub>O2</sub> is the slope of the whole blood O<sub>2</sub> solubility curve in the region of the prevailing venous O<sub>2</sub> tension [see Eq. (B.50)]. The respective compartmental gas exchange half times are τ<sub>k,1/2</sub> = ln(2)·τ<sub>k</sub> and τ<sub>O2,1/2</sub> = ln(2)·τ<sub>O2</sub>.

Exercise also affects tissue O<sub>2</sub> tension by increasing the rate of metabolic O<sub>2</sub> consumption:

C<sub>av,O2</sub> = C<sub>a,O2</sub> - C<sub>v,O2</sub> = V̇<sub>O2</sub>/Q̇ (7)

Because oxygen constitutes only a small fraction of the overall gas pressures during diving, most models for computing diving decompressions either neglect the presence of oxygen altogether or consider oxygen to contribute only a constant small quantity to the prevailing total gas tension in tissue.<sup>36</sup> In earlier gas and bubble dynamics models, oxygen was additionaly assumed to be infinitely diffusible – and always in equilibrium – between bubble and tissue.<sup>13,25-27</sup> A number of models of DCS incidence in diving exposures have been developed in which oxygen at arterial tensions above a certain threshold tension contributes to DCS risk accumulation as if it were an inert gas.<sup>37,38</sup> More rigorously, the compartmental oxygen tension varies nonlinearly with lower values of the arterial oxygen tension because of the metabolic consumption of oxygen and the sigmoidal nature of the oxyhemoglobin dissociation curve.<sup>39</sup> This nonlinear behavior and its dependence on exercise was accommodated in the present model by consideration of exercise-dependent variations of compartmental oxygen consumption and numerical integration of the oxyhemoglobin dissociation curve [Appendix B].

Exercise-induced changes in compartmental gas exchange time constants were assumed to occur instantaneously with onset or cessation of exercise and were incorporated into expressions for the time-dependence of compartmental dissolved gas tensions as described in Appendix A. Methods to account for kinetics of such changes are considered in Appendix B.

### 2.1.3 Bubble Nucleation

The number of bubbles in each modeled compartment was allowed to increase with the compartmental gas supersaturation during decompression, as nuclei were recruited from a hypothetical pre-existing population in the compartment. The population of pre-existing nuclei was assumed to have a logarithmic distribution of sizes that could be affected by pressure and exercise. Increases in pressure shifted each distribution to smaller, more difficult to recruit sizes, while exercise shifted each distribution to larger, easier to recruit sizes. The nucleation model for this recruitment process was adopted from Yount<sup>40,41</sup> as described in Appendix A.

Notably the Yount model considers only integer numbers of bubbles, with one sensibly being the minimum nonzero number of bubbles in a compartment. In contrast, the

6
---
The present implementation of the Yount model allows fractional numbers of bubbles to avoid discontinuities in the hazard as compartmental gas supersaturations increase during decompression. The rationale for this allowance follows from the recognition that each modeled gas exchange compartment is not associated with any particular anatomic site, but is considered to represent a collection of sites distributed arbitrarily throughout the body. Quantities characterizing the compartment are averages from across the collection of distributed elements that the compartment represents. Thus, most compartmental properties, such as the blood-tissue gas exchange half-time, are intrinsic properties independent of the volumes or distribution of elements comprising the compartment, while the bubble number is an extrinsic property dependent in an indeterminant fashion on the overall volume of the compartment.

## 2.1.4 Venous Gas Emboli (VGE) Formation

VGE formation caused by migration of bubbles from the tissue into the vasculature was modeled as a mechanism for non-diffusive loss of gas from the tissue.42 VGE formation was assumed to decrease the number of bubbles remaining in a modeled compartment while the size of the remaining bubbles remains unchanged. The number of bubbles in a compartment was reduced at the end of each integration step by a proportion, LR, of the prevailing number of bubbles, so that the number remaining for the next integration step was given by

$$N_{b_{n+1}} = MAX[0,N_{b_n} \cdot (1-LR)],$$                       (8)

where the subscripts n and n+1 refer to values at the beginning and end of the nth integration step. In turn, the proportionality factor was increased with bubble volume:

$$LR = (V_b - V_{r0}) \cdot \dot{N}_{VGE} \cdot \Delta t_n,$$                       (9)

where $(V_b - V_{r0})$ is the amount by which the prevailing volume of any one of the $N_b$ bubbles in the compartment exceeds the nucleonic volume and $\dot{N}_{VGE}$ (mL$^{-1}$min$^{-1}$) is the rate of change of the proportionality constant. The number of bubbles lost to the vasculature as VGE at the end of each [t$_n$, t$_{n+1}$] interval is $N_{b_n} - N_{b_{n+1}}$. Note that this bubble loss increases with exercise to the extent that exercise increases $\dot{N}_{b_n}$.

## 2.2 Definition of the Hazard Function

As described in Appendix D, the instantaneous risk of DCS at time t, h(t), was expressed as a function of the prevailing compartmental bubble volumes and modified bubble number at the end of each integration step:
---
$$h(t) = \sum_{j}^{n_c} g_j (V_{b,j} - V_{r0_j}) \cdot (N_{b,j})^{BN,j},  \qquad (10)$$

where nc is the number of modeled gas exchange compartments, gj is a compartmental gain factor, and the prevailing number of bubbles Nb,j in each compartment at time t is raised to a power of BN,j. The instantaneous risk was integrated over time by numerical trapezoidal integration, while varying the time step size depending on the rate of bubble growth or resolution (Appendix A, Section 8.5). Note that the compartmental contribution to the instantaneous risk increases more sharply with increasing compartmental bubble number as the power factor BN,j increases.

## 2.3 Model Optimization by Likelihood Maximization

The implementation of Eq. (10) contains parameters, β = (β1, β2, ..., βp), that govern its quantitative behavior. These parameters scale the influences of explanatory variables (e.g., pressure, time, inspired O2 fraction, etc.) or are required "mechanistic" constants.43 Values of these parameters required to yield model performance in best possible conformance with selected training data are found by maximizing a likelihood function of the parameters.16,17 The likelihood, L(β), of one or more trials is defined as the probability of the observed overall outcome. Assuming statistical independence of all possible outcomes, the likelihood of an individual exposure, li(β), is the product of the probabilities of the possible outcomes, each conditioned by actual experience through the influence of an outcome variable, δi:

$$l_i(\beta) = P_i(E)^{\delta_i} \cdot P_i(0)^{(1-\delta_i)}, \qquad (11)$$

where Pi(E) and Pi(0) are given by Eqs. (1) and (2), respectively, δi = 0 if DCS does not occur in the exposure, and δi = 1 if DCS occurs. Marginal outcomes, for which 0 < δi < 1, are also allowed.b The likelihood of a trial of N exposures is then given as the product of the likelihoods of the individual exposures:

$$L(\beta) = \prod_{i=1}^N l_i(\beta). \qquad (12)$$

Parameter values were systematically adjusted to maximize Eq. (12) about the training data described in Section 2.4 using an implementation of the Marquardt algorithm.46 For convenience, Eq. (12) was cast in terms of the natural log of the likelihood to obviate need to work with excessively small-valued numbers. The results are the "best fit" values of the parameters for use in model applications. The maximum log likelihood

b The tendency for marginal outcomes in diving exposures to occur predominantly in only certain profile types has been shown to adversely bias model performance on other types of profiles, motivating a recommendation to code marginal events as nonevents (δi = 0).45,45 The few marginal outcomes in the present altitude data were coded with outcome variable δi = 0.1.

8
---
achieved by the model on the data serves as a quantitative index of model goodness-of-fit. A central and singularly most important feature of this approach is that a model is made to provide estimates of DCS risks and times of DCS occurrence that are in closest possible agreement with observed DCS incidences and times of occurrence in the actual experience expressed in the training data.

## 2.4 Model Training Data

### 2.4.1 Augmented NMRI Standard format

The description of the pressure and respired gas profile for each exposure in the model training data was coded in Augmented NMRI Standard (ANS) format, which comprised a record of exposure outcome followed by a sequence of nodes that gave the pressure and inspired gas composition at successive times in the exposure.27 Each node gave the conditions prevailing at the end of a profile stage or segment that was either a travel stage (compression or decompression) or an isobaric stage, either of which may have ended with start of a breathing gas switch that completed in the ensuing stage or stages. An unbroken description of the profile was obtained by linear interpolation in the time domain between successive nodes. The model was exercised on the profile by sequentially processing these nodes, preserving the model state at the end of each stage as the initial state for the next stage. The format accommodates an arbitrary number of nodes per profile, allowing representation of profiles of arbitrary complexity.

### 2.4.2 USAF Data

Altitude exposure data from the United States Air Force Armstrong Laboratory (USAFAL) Hypobaric Decompression Sickness Database comprised a large portion of the model training data. This database existed in two different architectures as it evolved from its inception in the early 1980s to its most current form described by Webb.47

In its first form, the database contained exposure profile information sufficient to construct a detailed node-by-node description of each profile.48 This information faithfully described each exposure as it was actually completed: Time at altitude ended at actual time of descent start when the occurrence of DCS caused termination of the exposure before completion of the planned time at altitude. Data for 1194 man-exposures completed at USAFAL between 1983 and 1993 had been extracted from the data base in this first form for earlier work13 and was used in present work. DCS onset t1 and t2 times for application of Eq. (2) were arbitrarily defined for each exposure that culminated with a DCS incident. In such cases, t1 and t2 were defined to bracket the last 10 min of the isobaric stage preceding final descent to ground level. This was equivalent to assuming that the subject remained DCS-free until 10 min before reporting DCS, which then caused immediate termination of the exposure with descent to ground. These t1 and t2 assignments are consistent with the use of DCS onset as the experimental end-point for the exposures in the USAFAL protocols. Thus, with the
---
exception of DCS cases that might have occurred after final return to ground, the assumed t1 and t2 values did not differ substantially from the actual values.

Data for an additional 673 man-exposures completed after 1993 were extracted from the USAFAL Hypobaric Decompression Sickness Database in its second and current form.47 In this form, the detailed node-by-node description of each profile is replaced with a summary description of the profile as it was planned: Actual time at altitude is replaced with planned time at altitude, although time of DCS onset is recorded for those exposures that terminated with DCS. DCS onset t2 times were taken as the recorded DCS onset times and, as with the legacy USAFAL data, each corresponding t1 time was arbitrarily defined to be 10 min before the recorded DCS onset time.

### 2.4.3 NASA Data

Data from eleven chamber tests conducted at NASA-JSC between 1980 and 1995 and recorded in the NASA-JSC historical database of altitude tests comprised the preponderance of the remaining data used for model calibration.49,50,51,52,53 Missing and erroneous entries were corrected by review of original laboratory logbooks. Deficiencies in profile descriptions were rectified and DCS onset times were determined from case summaries. The number of protocols per test varied from 1 to 6, with a total of 31 across the 11 tests. The data were from 237 subjects; 176 males and 61 females; who participated in a total number of 549 altitude exposures, 82 of which culminated in diagnosed cases of DCS and 467 of which were completed with no DCS for a 14.9% overall incidence of DCS. Data for male and female subjects within a given test series were pooled.

As in the legacy USAFAL data, time at altitude in each profile ended at the actual time of descent start when the occurrence of DCS caused termination of the exposure before completion of the planned time at altitude. No DCS onset after return to ground was recorded. Profiles were terminated at time of completion of planned time at altitude if DCS did not occur, or at time of DCS onset if DCS occurred.

Data from an additional 178 man-exposures completed at Duke University, the Canadian Defense and Civil Institue of Environmental Medicine, and the University of Texas Medical Branch in the course of Phases I through IV of a NASA prebreathe reduction protocol54,55,56 comprised the remainder of the model training data.

### 2.4.4 Exercise Coding

As described in Section 2.1.1, periods of exercise in each profile were characterized by the whole body O2 consumption rate during the period. Work rates reported in units of percent peak whole body O2 consumption rate ($\dot{V}_{O2,peak}$) were converted to absolute whole-body O2 consumption rates in L⋅min-1 by assuming $100\% \dot{V}_{O2,peak} = 3.15$ L·min-1
---
1,c Work rates reported in watts (W) were converted to whole-body O2 consumption rates with the following quadratic formula parameterized by fitting to the data of Astrand, et. al.,34 highlighted in Table 1:

$$\dot{V}O_2 (L \cdot min^{-1}) = \beta_0 + \beta_1W + \beta_2W^2,$$  (13)

where:

| Parameter | Value |
|-----------|-------|
| β0 | 3.0536x10-1 |
| β1 | 1.1369x10-2 |
| β2 | 5.4762x10-6 |

The goodness-of-fit of Eq. (13) to its calibration data is shown graphically in Figure 2. The fitted y-intercept, β0=0.305 L·min-1, is the value used for the resting whole-body $\dot{V}O_2$ assumed for all subjects.

Work rates reported in kcal·hr-1 were converted to whole-body O2 consumption rates in L·min-1 by assuming 0.2 L O2 are consumed to produce each kcal of energy (5 kcal·L O2-1).33 Finally, work rates reported in mL O2·kg-1·min-1 were converted to whole-body O2 consumption rates in L·min-1 by assuming a subject body weight of 70 kg.

Along with the calibration data for Eq. (13), Table 1 gives metabolic rates in various units during exercises typical of those performed during USAF and NASA EVA altitude exposures. The tabulated data for whole body $\dot{V}O_{2,wb}$ versus work rate in watts are included in Figure 2.

c A whole-body $\dot{V}O_{2,peak}$ of 40.8 mL·kg-1·min-1 was assumed for development of a NASA Exercise Prebreathe Model.57 This value corresponds to 3.15 L·min-1 for a 77.3 kg subject.

11
---
Table 1. Metabolic Rates During Exercise*

| Watts   | kcal·hr⁻¹ | mL O₂·kg⁻¹·min⁻¹ | L·min⁻¹   | % V̇O₂,peak |
|---------|-----------|-------------------|-----------|------------|
| 0.00    | 91.6      | 4.4               | 0.305     | 9.7        |
| 6.46    | 113.8     | 4.8¹              | 0.379     | 12.0       |
| 8.81    | 121.8     | 5.8²              | 0.406     | 12.9       |
| 14.90   | 142.8     | 6.8³              | 0.476     | 15.1       |
| 20.59   | 162.5     | 7.7               | 0.542     | 17.2⁴      |
| 21.59   | 166.0⁵    | 7.9               | 0.553     | 17.6       |
| 25.00   | 177.9     | 8.5               | 0.593     | 18.8       |
| 28.17   | 189.0     | 9.0               | 0.630     | 20.0       |
| 50.00   | 266.3     | 12.7              | 0.888 (0.9) | 28.2     |
| 100.00  | 449.1     | 21.4              | 1.497 (1.5) | 47.5     |
| 139.66  | 600.0     | 28.6              | 2.000     | 63.5       |
| 150.00  | 640.2     | 30.5              | 2.134 (2.1) | 67.7     |
| 155.45  | 661.5     | 31.5              | 2.205     | 70.0       |
| 167.44  | 708.8     | 33.8              | 2.363     | 75.0       |
| 200.00  | 839.5     | 40.0              | 2.798 (2.8) | 88.8     |
| 225.68  | 945.0     | 45.0              | 3.150     | 100.0      |
| 250.00  | 1047.0    | 49.9              | 3.490 (3.5) | 110.8    |

\* Highlighted data from Table 9.5 in Astrand, et al.³⁴

1.) knee bends and overhead presses; "BSI exercises."⁵⁸

2.) light exercise, Shuttle suit donning simulation, NASA PRP.⁵⁶

3.) leg ergometer exercise, NASA PRP.⁵⁶

4.) work rate of 15-20% V̇O₂,peak stated for 4-station (3 exercise, 1 rest)/16 min NASA EVA exercise simulation.⁵⁹
[The simulation consisted of arm exercise for 4 min at each of 3 stations;
a) subject standing: cycle ergometer hand-cranking at 24 rpm, 4 Newtons resistance, alternating arms after every two revolutions,
b) subject standing: apply 25 ft-lbs force with torque wrench for 5 sec to each of 5 bolt-like projections mounted on the top, bottom, left, right, and forward-facing surfaces of a wall-mounted rectangular box, alternating arms from position-to-position, and
c) subject seated: rope pull against 17 lb (8.5 kg) resistance from arm's reach at head level to waist once each 5 sec, alternating left, right, then both arms;
and a 4-min period of Doppler VGE monitoring during which subject was supine and sequentially flexed the four limbs while otherwise remaining at rest. The four-station cycle was repeated until completion of the intended EVA simulation.]⁶⁰

5.) average metabolic rate of 166 ± 17 kcal·hr⁻¹cited for NASA EVA exercise simulation described in (3) above.⁶¹
[also ref 62: males 119.4-193.3 kcal·hr⁻¹ (147.95 ± 24.51 SD); females 91.5-114.5 kcal·hr⁻¹ (104.6 ± 8.9 SD)].
---
| Work Rate (Watts) | Astrand, et al., 2003 | Estimated |
|-------------------|---------------------|-----------|
| 0                 | 0.305               | 0.305     |
| 50                | 0.95                | 0.95      |
| 100               | 1.5                 | 1.5       |
| 150               | 2.1                 | 2.1       |
| 200               | 2.9                 | 2.9       |
| 250               | 3.5                 | 3.5       |

Figure 2. Whole-body O₂ consumption rate, V̇O₂,wb, versus work rate. The extrapolated value for V̇O₂,wb,rest at zero work rate is 0.305 L·min⁻¹.

Exercise performed during a segment was characterized by an entry in the ANS code for the segment equal to the subject V̇O₂,wb during the segment.⁶³,⁶⁴ No exercise information was required for a segment if the segment was completed with the subject at rest and, conversely, subjects during segments coded without exercise information were presumed to be at rest during the segment. This convention allowed the modeling system to remain consistent with earlier profiles coded in the ANS format without exercise information, but required specification of the resting rate of whole-body O₂ consumption, V̇O₂,wb,rest, for the subject in each profile. In present work, V̇O₂,wb,rest = 0.305 L·min⁻¹ was assumed for all subjects in all profiles [Eq. (13)]. Nodes were added with appropriate time and exercise intensity information to accommodate changes in exercise intensity during segments in which no other covariate changed.

### 2.4.5 Overall Training Data Summary

The complete training dataset, named A1309, is summarized in Appendix E, excepting four man-exposures; man-flight numbers 88073, 91097, 93022, and 93033; of the 1194 exposures extracted from the original USAFAL Hypobaric Decompression Sickness Database. Each of these exposures had a unique profile that could not be associated with any study in the database and each culminated with occurrence of DCS. The coded NASA data included information on observed grades (0 – IV Spencer scale) and onset times of venous gas emboli detected with Doppler ultrasound instruments, but such information was not used in the present modeling work.

13
---
# 3. Results

## 3.1 Optimized 3RUT-MBe1 Model Parameters

The single compartment 3RUT-MBe1 model was fit to the combined NASA and USAF altitude data to obtain the optimized parameters given in Tables 2 and 3. Parameters assigned fixed values in the optimization process are indicated in Table 3.

### Table 2. 3RUT-MBe1 Model Fit Statistics

| Statistic | Value |
|-----------|-------|
| # Profiles in dataset | 2153 |
| Total # individual trials | 2598 |
| Total # DCS marginals | 3 |
| Total # DCS positives | 862 |
| Overall DCS incidence | 33.191 % |

| MODEL | Log Likelihood |
|-------|----------------|
| Fitted | -3774.066872 |
| Perfect | -0.97524892 |
| I-O Null | -1651.0873 |

c-index = 0.674018

| Tissue | Gas | Half-time (min) |
|--------|-----|-----------------|
| 1 | O₂ | 284.05 |
| | N₂ | 284.05 |

Integration control parameters*:
- 5.000×10⁻⁰⁴ : dtmin; Minimum time step (Max resolution, minutes)
- 1.000×10⁻⁰² : dtmax; Maximum time step (Min resolution, minutes)
- 6.931×10⁻⁰³ : dtK; time step decay constant
*See Appendix A, Eq. (A.52)

The optimized model yields a log likelihood of -1771.5 and c-index<sup>d</sup> of 0.612 on the 1194 man-exposures from the first version of the USAFAL database compared to -1742.0 and 0.560, respectively, yielded on the same data by an earlier model in which DCS was expressed in terms of the evolution of only a single bubble in the modeled compartment, exercise effects on blood tissue gas exchange were not considered, and compartmental dissolved oxygen was considered as a component of the fixed metabolic gases.<sup>13</sup> Reoptimization of the present model about these data yielded a log likelihood of -1743.0 and c-index of 0.645.

<sup>d</sup> Concordance index. Gives the fraction of all possible pairs of exposures in the data for which the model-estimated risks of DCS are in the same order as the observed incidences of DCS.<sup>65</sup>

14
---
| Parameter | Type* | Value | Std Error | Coeff. of Variation |
|-----------|-------|-------|-----------|---------------------|
| P<sub>H<sub>2</sub>O</sub>; water vapor pressure (mm-Hg) | F | 4.700E+01 | --- | --- |
| RQ; Respiratory Quotient | F | 1.000E+00 | --- | --- |
| p<sub>t,CO<sub>2</sub></sub> ; Tissue CO<sub>2</sub> partial pressure (mm-Hg); all tissues. | F | 4.500E+01 | --- | --- |
| Gain, g | A | 6.188E-02 | 7.38E-03 | 1.19E-01 |
| α<sub>b,O<sub>2</sub></sub> ; O<sub>2</sub> solubility in blood | F | 2.356E-02 | --- | --- |
| α<sub>b,N<sub>2</sub></sub> ; N<sub>2</sub> solubility in blood | F | 1.410E-02 | --- | --- |
| N<sub>b</sub><sup>0</sup>; Total # nuclei | A | 1.198E+00 | 8.70E-02 | 7.26E-02 |
| β<sup>0</sup>; initial nuclei size distribution slope | A | 4.868E-05 | 1.11E-06 | 2.27E-02 |
| M; elastic modulus (atm·V<sup>-1</sup>) | A | 1.341E-07 | 9.09E-02 | 6.77E+05 |
| N<sub>VGE</sub>; VGE gas loss rate (mL<sup>-1</sup>·min<sup>-1</sup>) | A | 4.758E+00 | 3.28E-01 | 6.89E-02 |
| σ<sub>c</sub> factor | A | 1.964E+01 | 1.30E+00 | 6.64E-02 |
| α<sub>t,O<sub>2</sub></sub> ; [mL(SPD,37)·mL<sup>-1</sup>·atm<sup>-1</sup>] | A | 4.536E-02 | 2.70E-03 | 5.95E-02 |
| Kα<sub>N<sub>2</sub></sub>; N<sub>2</sub> solubility factor: α<sub>t,N<sub>2</sub></sub> = Kα<sub>N<sub>2</sub></sub> ·α<sub>t,O<sub>2</sub></sub> [mL(SPD,37)·mL<sup>-1</sup>·atm<sup>-1</sup>] | F | 5.985E-01 | --- | --- |
| V<sub>t</sub>; tissue volume (mL) | A | 5.279E-02 | 6.51E-03 | 1.23E-01 |
| Q̇ ; blood flow rate (mL·min<sup>-1</sup>) | A | 4.698E-03 | 2.99E-04 | 6.37E-02 |
| D<sub>t,O<sub>2</sub></sub>; O<sub>2</sub> diffusivity (cm<sup>2</sup>·min<sup>-1</sup>) | A | 1.414E-03 | 7.61E-05 | 5.39E-02 |
| KD<sub>N<sub>2</sub></sub>; N<sub>2</sub> diffusivity factor: D<sub>t,N<sub>2</sub></sub> = KD<sub>N<sub>2</sub></sub> ·D<sub>t,O<sub>2</sub></sub> | F | 9.091E-01 | --- | --- |
| BN; bubble number power factor | A | 2.172E+00 | 3.99E-02 | 1.84E-02 |
| P<sub>crush</sub> decay time constant | A | 2.014E+02 | 2.33E+02 | 1.15E+00 |
| m<sub>β<sub>ex</sub></sub> ; (β<sub>ex</sub>=1+ m<sub>β<sub>ex</sub></sub> * I<sub>ex</sub>) | A | 6.162E-01 | 4.52E-02 | 7.33E-02 |
| V̇<sub>O<sub>2</sub>,rest</sub>; V̇<sub>O<sub>2</sub></sub> @ rest | A | 4.401E-05 | 2.12E-06 | 4.82E-02 |
| m<sub>V̇<sub>O<sub>2</sub></sub></sub> ; slope V̇<sub>O<sub>2</sub></sub> vs I<sub>ex</sub> | A | 1.677E-03 | 6.90E-04 | 4.12E-01 |
| m<sub>Q̇</sub> ; slope β<sub>f</sub> vs V̇<sub>O<sub>2</sub></sub> | A | 6.997E+00 | 3.14E+00 | 4.49E-01 |
| σ; surface tension (dyne·cm<sup>-1</sup>) | F | 30 | --- | --- |

*A ≡ adjustable parameter
F ≡ fixed parameter
---
## 3.2 Model Goodness-of-Fit

### 3.2.1 Observed and Estimated DCS Occurrence Density Distributions

Goodness-of-fit of the optimized model is illustrated graphically in Figure 3 by comparison of the observed DCS occurrence density distribution for the training data with that estimated for the data by the model. Eleven profiles accounting for 8.3 observed cases of DCS are omitted in this analysis for lack of t1 and t2 data. The small numbers of observed (30.9) and estimated (41.6) cases of DCS in the hours before the last decompression occurred after earlier decompressions in repetitive altitude and staged ascent profiles. The observed incidence of DCS onset increases sharply after the last decompression and peaks in the second hour after the last decompression. The shape of the estimated occurrence density distribution faithfully follows that of the observed distribution but with a tendency for overprediction before last decompression and a consistent trend for underprediction after last decompression. (The hour-by-hour difference between observed and estimated numbers of DCS cases is illustrated in Figure 4.) As a result, the model estimates a total number of 793.9 DCS cases (the sum of the illustrated numbers of estimated cases in each hour) compared with a total number of 854.0 observed cases.

| Time Since End Last Decompression (hr) | DCS Cases (/hr) |
|----------------------------------------|-----------------|
| -15 to -1                              | Low values      |
| 1                                      | ~250            |
| 2                                      | ~300            |
| 3                                      | ~150            |
| 4 to 5                                 | ~100            |
| 6 to 29                                | Low values      |

Figure 3. Observed and model-estimated occurrence density distributions for model training data computed at hourly resolution relative to the time of completion of last decompression.

Legend:
- OBS: Gray bars representing observed data
- A1309-3RUT-MBe1: Line with square markers representing estimated data

The graph shows a sharp peak in DCS cases around 1-2 hours after the end of last decompression, with the observed data (gray bars) slightly higher than the estimated data (line) at the peak. Both observed and estimated values drop off rapidly after the peak, with very low values before and long after the decompression event.

16
---

| Time Since End Last Decompression (hr) | Observed-Estimated Cases/hr |
|---------------------------------------|----------------------------|
| -15                                   | 0                          |
| -13                                   | 0                          |
| -11                                   | 0                          |
| -9                                    | 0                          |
| -7                                    | 0                          |
| -5                                    | 2                          |
| -3                                    | 0                          |
| -1                                    | -5                         |
| 1                                     | 35                         |
| 3                                     | 17                         |
| 5                                     | 13                         |
| 7                                     | 2                          |
| 9                                     | 0                          |
| 11                                    | 0                          |
| 13                                    | 0                          |
| 15                                    | 0                          |
| 17                                    | 0                          |
| 19                                    | 0                          |
| 21                                    | 0                          |
| 23                                    | 0                          |
| 25                                    | 0                          |
| 27                                    | 0                          |
| 29                                    | 0                          |

Figure 4. Differences between the observed and estimated numbers of DCS cases in hourly intervals before and after the time of completion of last decompression.

### 3.2.2 Pearson Residuals and Global Chi-Square

Model fit was also assessed by examining group-specific and global Pearson χ² statistics.¹⁷ Examination of group-specific residuals is useful to distinguish areas in a data set over which a model performs well from those over which it performs poorly. The squared Pearson residual for each group is given by

$$(Pearson residual_k)^2 = \frac{(o_k - n_k \cdot \pi_k)^2}{n_k \cdot \pi_k \cdot (1 - \pi_k)},  (14)$$

where o_k is the number of observed DCS cases, n_k is the number of man-exposures, and π_k is the average model-estimated P_DCS for exposures in the k^th group given by⁶⁶

$$\pi_k = \sum_{j=1}^{c_k} \frac{m_j \cdot \pi_j}{n_k}.  (15)$$

In Equation (15), c_k is the number of profiles in the k^th group and m_j and π_j are the number of exposures and the model-estimated P_DCS for the j^th profile in the group, respectively.

17

---
In place of the group average model-estimated risk given by Eq. (15), all profiles in each group were assumed to have estimated DCS risk equal to that for the profile with the highest estimated risk in the group. That profile was inevitably the profile with the longest time at altitude in the group, a profile that the subject had completed DCS-free. Coded times at altitude for profiles completed without DCS in each group were nearly the same and were within minutes of the planned times at altitude. Thus, the risk estimates for profiles that were terminated early due to DCS occurrence were adjusted for the unrealized risks that would have accumulated to produce the same outcome had the profiles been continued to the planned times at altitude. These adjustments cast the present goodness-of-fit assessments in the same form as those for time-independent covariate models developed by other workers for profiles with fixed times at altitude; models based on planned times at altitude or models fit only to profiles with the same times at altitude.

Results for all of the 117 groups in the training data are shown in Appendix F with the groups in order of increasing squared Pearson residual. Also shown is the running sum of the squared Pearson residual,

$$\chi^2 = \sum_{k=1}^g (\text{Pearson residual}_k)^2 = \sum_{k=1}^g \frac{(o_k - n_k \cdot \pi_k)^2}{n_k \cdot \pi_k \cdot (1-\pi_k)}, \quad (16)$$

each of which equals the global chi-square goodness-of-fit statistic for the g groups included in the sum. Each $\chi^2$ follows a chi-square distribution with g−ρ degrees of freedom, where ρ is the total number of adjustable parameters in the model (= 16 in 3RUT-MBe1). As the P-value of the chi-square increases, the evidence decreases that model estimated incidences are statistically different from observed incidences. Evidence is usually considered insufficient to reject a model if the P($\chi^2$) of its fit to the data groups exceeds 0.05. The P value corresponding to each $\chi^2$ is shown in the rightmost column of the table in Appendix F. A double line is placed after the last group in the table with P > 0.05. Model fit to groups above this line cannot be rejected at P < 0.05 significance, while it can be concluded at P < 0.05 significance that the model fails to fit the data for groups below the line. Thus, model fit to data for 1621 man-exposures in 84 groups cannot be rejected, while the model fails to fit the remaining data for 973 man-exposures in 33 groups.

All profiles in the CO2 study series, all profiles in the BSI (Bends Screening Index) study series except those in the BSI-A group, and the preponderance of the profiles completed in the EffctEX (Exercise effects) study series are among the profiles with the highest Pearson residuals. Incidences in the BSI study series were generally under-estimated, while incidences in the EffctEx series were generally over-estimated. It can therefore be argued that the data from these studies is not combinable with the other data and that a more restricted training data set that excludes these studies should be used.
---
The estimated number of DCS cases for each group in Appendix F is plotted versus the corresponding observed number of DCS cases in Figure 5. Panel A illustrates the raw data, while the bubble plot in panel B shows regions where the data are most concentrated. Figure 6 illustrates the same information for only those groups in Appendix F for which the cumulative global chi-square P-value is greater than 0.05. Both figures show that the model overestimates – often substantially – the DCS incidences in groups with no observed cases of DCS.

## A

| P DCS (Obs) | P DCS (Est) |
|-------------|-------------|
| 0.0         | 0.0-0.4     |
| 0.2         | 0.1-0.6     |
| 0.4         | 0.2-0.7     |
| 0.6         | 0.3-0.8     |
| 0.8         | 0.5-0.9     |
| 1.0         | 0.6-1.0     |

The scatter plot shows a positive correlation between observed and estimated DCS cases, with points generally clustered around a diagonal line. There is significant scatter, especially for lower observed values.

## B

| P DCS (Obs) | P DCS (Est) |
|-------------|-------------|
| -0.2 to 1.0 | 0.0 to 1.0  |

The bubble plot shows concentrations of data points, with bubble size proportional to the number of man-exposures in each group. The largest concentrations appear to be in the lower left quadrant, suggesting many groups with low observed and estimated DCS probabilities. There are also notable clusters in the mid-range and upper right of the plot.

Figure 5. Plots of estimated incidences of DCS versus observed incidences for all groups in the training data. Bubble size in panel B is proportional to the number of man-exposures in each group.

19
---
Figure 6. Plots of estimated incidences of DCS versus observed incidences for 84 groups (1621 man-exposures) in the training data fitted by the model (cumulative chi-square P > 0.05 for groups in order of increasing Pearson residual). Bubble size in panel B is proportional to the number of man-exposures in each group.

| A |
|---|
| Chart A |

| B |
|---|
| Chart B |

Chart A Description:
A scatter plot showing the relationship between P_DCS (Obs) on the x-axis and P_DCS (Est) on the y-axis. The x and y axes both range from 0.0 to 1.0. The plot contains numerous blue dots representing data points, with a light gray diagonal line representing the ideal 1:1 relationship. Most points cluster around this line, indicating a generally good fit between observed and estimated values.

Chart B Description:
A bubble chart showing a similar relationship between P_DCS (Obs) on the x-axis and P_DCS (Est) on the y-axis. The x-axis ranges from -0.2 to 1.0, while the y-axis ranges from -0.2 to 1.0. Each data point is represented by a light blue circle, with the size of the circle varying to represent the number of man-exposures in each group. Larger bubbles indicate more man-exposures. The bubbles generally follow a positive trend from the bottom left to the top right of the chart.

Both charts are labeled with "A1309-3RUT-MBe1" in the bottom right corner.

20
---
# 4. Discussion

The present model is the first applied to altitude decompression data able to accommodate how DCS risk is influenced by arbitrarily varying levels of exercise in different periods of a given exposure. This ability is facilitated by a time-dependent covariate model structure that includes explicit consideration of hypothetical exercise effects that act to enhance the efficacy of oxygen breathing before decompression (prebreathe) – reducing the risk of DCS during subsequent altitude exposure – and increase the risk of DCS when exercise is performed after decompression at altitude. The influences of exercise on DCS incidence and time of occurrence in diving exposures were also recently considered in a time-dependent covariate model able to accommodate profiles of arbitrary complexity, but were not shown to be significant.67 This result was not unexpected, given that exercise in the diving exposures considered was typically performed only before decompression and tended only to increase risks of DCS. Exercise effects consequently added insufficient heterogeneity to the data to warrant model factors to differentiate profiles with different exercise regimens.

## 4.1 Prebreathe and Exercise Effects on Gas Elimination

Exercise during prebreathe reduces the risk of DCS by hastening inert gas elimination and reducing the gas superaturation produced by subsequent ascent to altitude. The modeled exercise-induced enhancement of inert gas elimination is illustrated in Figures 7 and 8. Figure 7 shows the relationship between compartmental oxygen consumption and exercise intensity (whole-body $\dot{V}O_2$). In turn, the compartmental oxygen consumption is the independent variable in the relationship illustrated in Figure 8 for the dependence of compartmental blood flow and the blood-tissue gas exchange half-time on exercise intensity.
---
Figure 7. The relationship between compartmental oxygen consumption and whole-body VO₂ (Iex, L·min⁻¹) given by the parameterized Eq. (4).

| Iex (L/min) | O₂ Consumption (mL/mL/min) |
|-------------|----------------------------|
| 0.0         | 0.000                      |
| 1.0         | 0.002                      |
| 2.0         | 0.004                      |
| 3.0         | 0.006                      |
| 4.0         | 0.007                      |

Figure 8. Compartmental blood flow (mL·mL tissue⁻¹·min⁻¹) and corresponding gas exchange half-time (minutes) as functions of whole-body VO₂ (Iex, L·min⁻¹).

| Iex (L/min) | Half-time (min) | Blood flow (mL/mL/min) |
|-------------|-----------------|------------------------|
| 0.0         | 280             | 0.010                  |
| 1.0         | 120             | 0.020                  |
| 2.0         | 70              | 0.035                  |
| 3.0         | 50              | 0.048                  |
| 4.0         | 40              | 0.058                  |

Figure 9 illustrates how different intensities and durations of exercise manifest in the compartmental nitrogen and oxygen tensions during hypothetical 3-hr oxygen prebreathes before 30-min ascents to 0.292 atm (4.3 psia). Ten minutes of 75% VO₂,peak exercise performed early in an otherwise resting prebreathe abruptly

22
---
decreases both nitrogen and oxygen tensions relative to their values in the resting
prebreathe. The lower values persist through decompression, resulting in lower gas
superations during and after decompression. In comparison, while the divergence to
lower nitrogen and oxygen tensions is more gradual with performance of lighter, 17.6%
$\dot{V}_{O_2,peak}$ exercise throughout most of the prebreathe, both tensions decrease to lower
values than in the resting or short, heavy exercise cases by the end of the prebreathe,
resulting in the lowest gas supersaturations at altitude among the three cases.

| Pressure (atm) | Pressure (atm) |
|----------------|----------------|
| 1.0            | 1.0            |
| 0.8            | 0.8            |
| 0.6            | 0.6            |
| 0.4            | 0.4            |
| 0.2            | 0.2            |
| 0.0            | 0.0            |

| Left Panel                   | Right Panel                 |
|-----------------------------|-----------------------------|
| Ambient Pressure            | Ambient Pressure            |
| ptN2 Resting PB             | ptO2 Resting PB             |
| ptN2 10 min Iex=2.363       | ptO2 10 min Iex=2.363       |
| ptN2 Iex=0.55 throughout    | ptO2 Iex=0.55 throughout    |

Time (min): 0, 60, 120, 180, 240

Figure 9. Modeled effects of exercise on compartmental nitrogen elimination (Left
Panel) and oxygen tension (Right Panel) during ground-level oxygen prebreathes.
Heavy solid lines: Resting throughout; Dashed lines: 10 min 75% $\dot{V}_{O_2,peak}$ (Iex = 2.363
L·min⁻¹) exercise starting at 20 min, rest at all other times; Dotted lines: 17.6% $\dot{V}_{O_2,peak}$
(Iex = 0.55 L·min⁻¹) exercise starting at 20 min and continuing until ascent start at 180
min, rest at all other times throughout.

## 4.2 Prebreathe and Exercise Effects on Bubble Nucleation

Both prebreathe and exercise affect the compartmental populations of pre-existing
bubble nuclei from which bubbles are recruited to grow to produce risk of DCS. The
numbers of nuclei recruited, along with the volumes they subsequently attain, govern
the actual levels of DCS risk produced. Exercise shifts the distribution of nuclei to larger
sizes, causing more nuclei to be recruited at a given supersaturation than before the
exercise. Figure 10 illustrates this effect on the numbers of bubbles recruited in the
presently parameterized model during 0.55 L·min⁻¹ exercise at various altitudes after
no-prebreathe ascents.

23
---
| Number of nuclei recruited, N | Rest | Exercise |
|--------------------------------|------|----------|
| 0.6 | - | - |
| 0.5 | - | - |
| 0.4 | - | - |
| 0.3 | - | - |
| 0.2 | - | - |
| 0.1 | - | - |
| 0.0 | - | - |
| 0.0 | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 |
| PSS, atm | - | - |

| (Nb)BN | Rest | Exercise |
|--------|------|----------|
| 0.20 | - | - |
| 0.16 | - | - |
| 0.12 | - | - |
| 0.08 | - | - |
| 0.04 | - | - |
| 0.00 | - | - |
| 0.0 | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 |
| PSS, atm | - | - |

Figure 10. Modeled effects of exercise on number of bubbles nucleated at altitude with no prebreathe. Left Panel: Modeled numbers of bubbles recruited at rest and during exercise, Iex = 0.55 L·min-1, at various levels of gas-supersaturation, PSS. Right Panel: (Nb)BN factor in the hazard function corresponding to the recruited numbers of bubbles at the respective supersaturations in the Left Panel.

The numbers of bubbles recruited at altitude are also affected by oxygen breathing before decompression. Prebreathe shifts the distribution of nuclei to smaller sizes by imposing a Pcrush, causing fewer nuclei to be recruited at a given supersaturation than without the prebreathe. These effects are illustrated in Figures 11 and 12 for a Pcrush of 0.139 atm, the Pcrush produced by a 3-hr resting ground level oxygen prebreathe.

| Number of nuclei recruited, N | Rest | Crush + Rest |
|--------------------------------|------|--------------|
| 0.6 | - | - |
| 0.5 | - | - |
| 0.4 | - | - |
| 0.3 | - | - |
| 0.2 | - | - |
| 0.1 | - | - |
| 0.0 | - | - |
| 0.0 | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 |
| PSS, atm | - | - |

| (Nb)BN | Rest | Crush + Rest |
|--------|------|--------------|
| 0.20 | - | - |
| 0.16 | - | - |
| 0.12 | - | - |
| 0.08 | - | - |
| 0.04 | - | - |
| 0.00 | - | - |
| 0.0 | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 |
| PSS, atm | - | - |

Figure 11. Modeled effects of a 3-hr resting ground-level prebreathe on numbers of bubbles recruited during resting exposures at altitude. Left Panel: Modeled numbers of bubbles recruited at rest and after a 0.139 atm crush at various levels of gas-supersaturation, PSS. Right Panel: (Nb)BN factor in the hazard function corresponding to the recruited numbers of bubbles at respective supersaturations in Left Panel.

24
---
| Number of nuclei recruited, N | Rest | Crush + Exercise |
|--------------------------------|------|-------------------|
| 0.6 | | |
| 0.5 | | |
| 0.4 | | |
| 0.3 | | |
| 0.2 | | |
| 0.1 | | |
| 0.0 | | |
| 0.0 | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 |
| PSS, atm |

| (Nb)BN | Rest | Crush + Exercise |
|--------|------|-------------------|
| 0.20 | | |
| 0.16 | | |
| 0.12 | | |
| 0.08 | | |
| 0.04 | | |
| 0.00 | | |
| 0.0 | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 |
| PSS, atm |

Figure 12. Modeled effects of a 3-hr resting ground-level prebreathe on numbers of bubbles recruited during exercising exposures at altitude. Left Panel: Modeled numbers of bubbles recruited at rest and during exercise, Iex = 0.55 L·min-1, after a 0.139 atm crush at various levels of gas-supersaturation, PSS. Right Panel: (Nb)BN factor in the hazard function corresponding to the recruited numbers of bubbles at the respective supersaturations in the Left Panel.

Values of the (Nb)BN factor between zero and unity in the hazard function are a consequence of the fractional compartmental bubble number allowed in this model. As a result, the contribution of a given bubble volume to the hazard is potentiated by increasing numbers of bubbles, as intended, but the effect is to increasingly attenuate an overall diminution of the bubble volume contribution as the bubble number increases. One or more bubbles may attain a given volume but produce negligible risk with low numbers of bubbles. Bubble number thus acts as a potent factor that scales the contribution of bubble volume to the accumulation of DCS risk.

Figure 13 illustrates the modeled influence of exercise at altitude on the estimated risk of DCS during 4-hr exposures at 30,320 ft altitude (= 4.3 psia Shuttle EVA suit pressure) after resting oxygen prebreathes of various durations. At each level of exercise illustrated, the risk of DCS decreases with increasing oxygen prebreathe time. After short prebreathe times, exercise at altitude tends to increase the risk of DCS. After longer prebreathes, exercise-induced enhancement of inert gas elimination becomes increasingly important so that the risks of DCS at the higher levels of exercise tend towards the risks of DCS for resting subjects.

25
---
| Resting pre-breathe time (min) | Rest | Iex = 0.5 | Iex = 1.0 | Iex = 2.0 |
|----------------------------------|------|----------|----------|----------|
| 0                                | 60.0 | 67.0     | 78.0     | 89.0     |
| 60                               | 43.0 | 52.0     | 65.0     | 77.0     |
| 120                              | 32.0 | 42.0     | 53.0     | 65.0     |
| 180                              | 24.0 | 34.0     | 44.0     | 55.0     |
| 240                              | 19.0 | 28.0     | 37.0     | 47.0     |
| 300                              | 15.0 | 23.0     | 31.0     | 40.0     |

Figure 13. Estimated risks of DCS (P DCS ) during 4-hour exposures at 30,320 ft altitude (4.3 psia) while exercising at indicated levels (Iex=whole-body $$\dot{V}O_2$$, L·min⁻¹) after resting oxygen prebreathes of various duration.

Figure 14 illustrates the modeled influence of exercise on the estimated risk of DCS during 4-hr exercising exposures at 30,320 ft altitude (= 4.3 psia Shuttle EVA suit pressure) after oxygen prebreathes of various duration with exercise at indicated levels throughout. Even light exercise at a wholebody oxygen consumption rate of 0.5 L⋅min⁻¹ throughout the oxygen prebreathe greatly reduces the predicted risk of DCS during subsequent exposure to altitude.

26
---
| Exercising pre-breathe time (min) | Rest | Iex = 0.5 | Iex = 1.0 | Iex = 2.0 |
|-----------------------------------|------|----------|----------|----------|
| 0                                 | 67.5 | 13.0     | 2.5      | 2.5      |
| 60                                | 56.0 | 1.5      | 0.5      | 0.5      |
| 120                               | 41.0 | 0.5      | 0.5      | 0.5      |
| 180                               | 30.0 | 0.5      | 0.5      | 0.5      |
| 240                               | 21.0 | 0.5      | 0.5      | 0.5      |
| 300                               | 0.5  | 0.5      | 0.5      | 0.5      |

Figure 14. Estimated risks of DCS (PDCS) during 4-hour exposures at 30,320 ft altitude (4.3 psia) while exercising at Iex=0.55 L·min-1 after oxygen prebreathes of various duration with exercise at indicated levels throughout.

## 4.3 Comparative Model Performance

Performance of the present model can be compared with performance of other published models on selected data. An accelerated failure time model described by Conkin, et al.,7 is one such model from which results are readily calculated for comparison to 3RUT-MBe1 model results. Performance of the two models on NASA data subsets Test 1 through Test 7 is illustrated in Figure 15, with results of corresponding chi-square assessments of model fit given in Table 4.

The Conkin, et al., model provides estimates of DCS risk only for single exposures to altitude based on the values of computed gas tensions in a single 360-min half-time gas exchange compartment at the time of ascent start. Values for these tensions at the start of each recorded exposure were included in the raw NASA data and used to compute the illustrated risks for the Conkin, et al., model. The profiles for subsets Test 4b through Test 4f comprise data from profiles with successively increasing numbers of repetitive exposures to 4.3 psi separated by intervals at 10.2 psi. The Conkin, et al., model provides estimated conditional probabilities of DCS for the last exposure in such profiles governed only by fixed properties of the last exposure and the computed gas tensions at the start of that exposure. Because successive exposures in a given test were coded as a single profile for 3RUT-MBe1 model optimization, estimated risks of DCS tabulated for these subsets in Appendix F are the total risks accumulated over each entire multi-exposure profile. Risks of DCS for the last exposure in such profiles, conditional on the subject not having developed DCS by the start time of the last exposure, were approximated from the difference between the cumulative risk for the

27
---
profile of interest and the cumulative risk of the profile with one fewer repetitive
exposure.

The chi-square for the Conkin, et al., model on all of the subsets is much lower than the
chi-square for the 3RUT-MBe1 model. Corresponding P-values warrant rejection only of
the 3RUT-MBe1 model. The situation reverses with omission of Test 6 data. The chi-
square for the 3RUT-MBe1 model is then less than the chi-square for the Conkin, et al.,
model and the corresponding P-values motivate rejection of neither model. Thus, the
3RUT-MBe1 model outperforms the Conkin, et al., model on all of the subsets except
Test 6. The 0.1% 3RUT-MBe1 model estimate of PDCS for the Test 6 profile is
considerably lower than the observed 3.4% DCS incidence for reasons that are not
clear.

| Estimated Incidence, % | 3RUT-MBe1 | Conkin, et al., 1996 | Identity |
|------------------------|------------|----------------------|----------|
| 40.0                   | ♦          | △                    | —        |
| 30.0                   | ♦          | △                    | —        |
| 20.0                   | ♦          | △                    | —        |
| 10.0                   | ♦          | △                    | —        |
| 0.0                    | ♦          | △                    | —        |
| Observed Incidence, %  | 0.0        | 10.0                 | 20.0     | 30.0 | 40.0 |

Figure 15. Model performance on data from NASA Tests 1 through 7.

28
---
# Table 4.Chi-square Results for Performance of Conkin, et al., 1996 and 3RUT-MBe1 Models on Data from NASA Tests 1 through 7

| Data subset | (Pearson Residual)² |  |
|-------------|---------------------|-----------------|
|             | Conkin, et al., 1966 | 3RUT-MBe1 |
| Test 1a | 0.514 | 0.006 |
| Test 1b | 0.030 | 0.003 |
| Test 1c | 2.048 | 1.854 |
| Test 2a | 0.014 | 0.035 |
| Test 2b | 0.296 | 3.127 |
| Test 3a | 1.904 | 0.595 |
| Test 3b | 5.781 | 1.791 |
| Test 3c | 0.056 | 1.434 |
| Test 3d | 0.080 | 0.023 |
| Test 4a | 1.044 | 0.028 |
| Test 4b | 0.099 | 0.536 |
| Test 4c | 0.642 | 0.130 |
| Test 4d | 0.015 | 0.046 |
| Test 4e | 0.566 | 0.078 |
| Test 4f | 0.013 | 0.038 |
| Test 5a | 0.042 | 0.951 |
| Test 5b | 0.122 | 0.883 |
| Test 6 | 0.113 | 34.358 |
| Test 7a | 2.639 | 0.160 |
| Test 7b | 0.002 | 0.077 |
| χ²(All) | 16.018 | 46.152 |
| P= | 0.591 | 0.000 |
| χ²(not including Test 6) | 15.905 | 11.794 |
| P= | 0.531 | 0.812 |

Note: Residuals in shaded cells were computed with approximated conditional probabilities of DCS for the last exposure in each profile (See text).

The USAF Altitude Decompression Sickness Risk Assessment Calculator (ADRAC) developed by Pilmanis, et al.,²³ is another accelerated failure time model from which data are available for comparison to 3RUT-MBe1 model results. ADRAC is a stratified time-independent covariate model with values of some parameters uniquely defined for different ranges of altitude. Unlike the present 3RUT-MBe1 model, ADRAC is applicable only to profiles with single ascents to a given altitude at which subjects may be either at rest or performing exercise at one of three discrete levels; mild, moderate, or heavy. The model also accommodates effects of resting ground-level oxygen prebreathes, but

29
---
exercsie during such prebreathes cannot be considered. Pilmanis and coworkers completed a series of man-exposures to validate this model. Performance of the present 3RUT-MBe1 model on the data from these exposures is compared to the corresponding performance of the ADRAC model in Figure 16. Results from corresponding chi-square assessments of model fit in Table 5 indicate that the 3RUT-MBe1 model outperforms the ADRAC model on all of these data except the data for validation profile A. The model underpredicts the observed DCS incidence for this profile that included only a moderately long resting prebreathe followed by exercising exposure to the highest altitude tested in the series.

| ADRAC Validation |
|-------------------|
| Estimated Incidence, % | Observed Incidence, % |
|:----------------------:|:----------------------:|
| 100.0 | 100.0 |
| 80.0 | 80.0 |
| 60.0 | 60.0 |
| 40.0 | 40.0 |
| 20.0 | 20.0 |
| 0.0 | 0.0 |

Legend:
- A, B, C, D, E: Different profiles
- ♦: 3RUT-MBe1
- △: ADRAC
- ——: Identity line

Figure 16. Model performance on USAF ADRAC validation data consisting of 153 man-exposures on five different profiles: A) 90 min prebreathe; 35K ft EVA sim (light exercise)/180 min; B) 30 min prebreathe; 25K ft, 30% $$\dot{V}_{O_2,peak}$$ exercise-rest cycles (heavy exercise)/240 min; C) 15 min prebreathe; 22.5K ft, 30% $$\dot{V}_{O_2,peak}$$ exercise-rest cycles (heavy exercise)/240 min; D) No prebreathe; 18.0K ft, 30% $$\dot{V}_{O_2,peak}$$ exercise-rest cycles (heavy exercise)/360 min; E) 75 min prebreathe; 30K ft rest/240 min.

30
---
Table 5.Chi-square Results for Performance of ADRAC and 3RUT-MBe1 Models on USAF ADRAC Validation Data

| Subset | (Pearson Residual)² |  |
|--------|---------------------|-----------------|
|        | ADRAC               | 3RUT-MBe1       |
| A      | 0.011               | 6.111           |
| B      | 0.855               | 0.747           |
| C      | 2.386               | 1.239           |
| D      | 0.286               | 0.006           |
| E      | 0.324               | 0.229           |
| χ² (All) | 3.863               | 8.333           |
| χ² (not including A) | 3.851               | 2.222           |

Performance of the present 3RUT-MBe1 model on data from man-exposures completed to develop a reduced prebreathe protocol for Space Shuttle extra-vehicular activities is compared to the corresponding performance of the NASA-RM2004 model¹⁰ in Figure 17. The NASA-RM2004 model is an accelerated failure time model cast in terms of time-independent covariates applicable only to stylized profiles typical of 4-hr Shuttle extravehicular activity (EVA) exposures with astronauts at Shuttle extravehicular mobility unit (EMU) – or EVA suit – pressure of 4.3 psia (30,320 ft altitude in the U.S. Standard Atmosphere) after various types of exercising prebreathe. Results from corresponding chi-square assessments of model fit in Table 6 indicate that the 3RUT-MBe1 model outperforms the NASA-RM2004 model on all of these data except the data for PRP Phase I.

PRP

| Estimated Incidence, % | PRP |
|------------------------|-----|
| 30.0 | • 3RUT-MBe1 |
| 25.0 | Δ NASA-RM2004 III |
|      | Identity |
| 20.0 | |
| 15.0 | IV I |
| 10.0 | II |
| 5.0  | |
| 0.0  | |
|      | 0.0 5.0 10.0 15.0 20.0 25.0 |
|      | Observed Incidence, % |

Figure 17. Model performance on NASA PRP data, Phases I through IV.

31
---
Table 6. Chi-square Results for Performance of NASA-RM2004 and 3RUT-MBe1 Models on NASA PRP Data

| Subset | (Pearson Residual)² |  |
|--------|---------------------|-----------------|
|        | NASA-RM2004         | 3RUT-MBe1       |
| I      | 1.361               | 5.124           |
| II     | 3.362               | 3.145           |
| III    | 0.710               | 0.137           |
| IV     | 0.609               | 0.079           |
| χ² (All) | 6.042             | 8.485           |
| χ² (not including I) | 4.681 | 3.360           |

## 4.4 Feaures of Model Performance

Important features of the 3RUT-MBe1 model compared to those of the other log-logistic models considered above are illustrated by considering 3RUT-MBe1 model performance on the PRP Phase II profile described in Table 7. The profile is a prototype Space Shuttle extravehicular activity (EVA) profile with a 2-hr exercise-enhanced O₂ prebreathe that was ultimately transitioned into Space Shuttle operational use.⁵⁶ A requirement to breathe ambient atmosphere for a period of 15 - 90 min during the Hard Upper Torso (HUT) donning procedure in the crewlock was a significant operational constraint on prebreathe design. To mitigate the adverse impact of this air breathing break, the EVA crew complete the donning procedure for the Lower Torso Assembly (LTA) of the Shuttle EMU in the crewlock while being slowly decompressed to 9.6 psia. The crewlock is then backfilled with O₂ to bring the crewlock to a pressure of 10.2 psia with the maximium allowed FO₂ of 26.5%, afterwhich the crew breathes ambient atmosphere to complete the HUT donning procedure.ᵉ Oxygen breathing is resumed with recompression of the crewlock to cabin pressure and completion of a 35 min O₂ prebreathe before final decompression to EMU pressure and egress for EVA.

ᵉ A 12-hr minimum O₂-breathing stage at 10.2 psia before decompression to Shuttle suit pressure and egress for EVA was a standard feature of Shuttle prebreathe protocols before the 2-hr prebreathe protocol was developed.

32
---
Table 7. PRP Phase II Profile Description

| • 100 min "adynamic" air breathing period. (Ground-based micro-gravity simulation; subjects semi-recumbent and prohibited from walking from start of this period until end of the EVA simulation.) |
|---|
| • 50 min O2-breathing period during which exercise is performed to enhance N2 washout. Schedule: |
|   1 min rest; pulmonary residual volume washout |
|   10 min; 75% $\dot{V}_{O_2,peak}$ exercise (Iex = 2.36); dual cycle (upper and lower body) |
|   cranking on Monark cycle ergometers |
|   39 min rest   (Subject transfer to altitude chamber) |
|   --------------------------------------------------- |
|   50 min total in segment |
| • 20 min decompression to 9.6 psia; lower torso assembly (LTA) donning. "Intermediate exercise" (Iex = 0.41) programmed to simulate work of LTA donning is started 5 min into this decompression and continued throughout the ensuing 40 min. |
| • 10 min repressurization to 10.2 psia; Backfill crewlock with O2 to raise O2 to 26.5%. |
| • 30 min "air" break (26.5% O2; balance N2) at 10.2 psia; hard upper torso (HUT) donning, comms check, etc. (PIO2=0.184 atm). End "intermediate exercise" at 15 min into "air" break. |
| • Switch to O2 and start 5 min repressurization to 14.7 psia cabin pressure. |
| • 35 min O2 breathing period at 14.7 psia; crewlock prebreathe. |
| • 30 min crewlock decompression to 4.3 psia suit pressure. |
| • 4 hr EVA simulation (Iex = 0.55) at 4.3 psia. |
| --------------------------------------------------------------------------------------------------- |
| Total prebreathe time, including air break:         150 min (2 hr 30 min) |
| Total O2 time:                                      120 min (2 hr) |
| Total Test Duration, excluding post-flight watch:   530 min (8 hr 50 min) |

Various aspects of model performance on this profile are shown in Figures 18 and 19. Exercise-induced acceleration of N2 elimination during the initial 75% $\dot{V}_{O_2,peak}$ exercise period is readily apparent in the compartmental N2 tension profile shown in panel A of Figure 18. It is also apparent that as a result of the prebreathe-induced reduction of compartmental N2, the gas supersaturation prevailing on arrival at the Shuttle suit pressure of 4.3 psia (0.293 atm) is considerably reduced from what would have prevailed had no prebreathe been performed. The bubble number and volume profiles in panel B are the modeled responses to this supersaturaion. Bubbles are nucleated in increasing number as the supersaturation develops during decompression, reaching a maximum number on arrival at suit pressure. The bubble volume profile shows that each of the bubbles continues to grow throughout the ensuing 4-hr period at suit pressure. This growth drives the migration of some bubbles from the tissue to the vasculature perfusing the tissue, which in turn causes the number of bubbles to decrease. The corresponding instantaneous risk of DCS, which is a function of both bubble volume and bubble number, is shown in panel C of Figure 18. Because of the loss of bubbles to the circulation, the instantaneous risk passes through a maximum and decreases somewhat before completion of the 4-hr period at 4.3 psia.

33
---
Figure 18

Figure 18. Model performance on a NASA PRP Phase II profile. Pressure, inspired O2 fraction, and compartmental O2 and N2 tension profiles are shown in panel A. Corresponding compartmental bubble number, bubble volume, and instantaneous DCS risk profiles are shown in panels B and C. All panels: 75% $\dot{V}_{O_2,peak}$ exercise (Iex = 2.36) [a arrows]; intermediate exercise (Iex = 0.41) [b arrows]; EVA exercise (Iex = 0.55) [c arrows].

## A

| Time (min) | Pressure (atm) | FIO2 | ptO2 | ptN2 |
|------------|----------------|------|------|------|
| 0          | 1.0            | 0.2  | 0.1  | 0.8  |
| 60         | 1.0            | 0.2  | 0.1  | 0.8  |
| 120        | 1.0            | 1.0  | 0.1  | 0.7  |
| 180        | 0.7            | 0.3  | 0.15 | 0.6  |
| 240        | 1.0            | 0.3  | 0.2  | 0.5  |
| 300        | 0.3            | 0.3  | 0.15 | 0.4  |
| 360        | 0.3            | 0.3  | 0.1  | 0.3  |
| 420        | 0.3            | 0.3  | 0.1  | 0.25 |
| 480        | 0.3            | 0.3  | 0.1  | 0.2  |
| 540        | 0.3            | 0.3  | 0.1  | 0.2  |
| 600        | 1.0            | 0.3  | 0.1  | 0.3  |
| 660        | 1.0            | 0.2  | 0.1  | 0.4  |

## B

| Time (min) | Pressure (atm) | Bubble Volume, VB (mL) | Bubble Number, NB |
|------------|----------------|------------------------|-------------------|
| 0          | 1.0            | 0.000                  | 0.000             |
| 60         | 1.0            | 0.000                  | 0.000             |
| 120        | 1.0            | 0.000                  | 0.000             |
| 180        | 0.7            | 0.000                  | 0.000             |
| 240        | 1.0            | 0.000                  | 0.000             |
| 300        | 0.3            | 0.005                  | 0.035             |
| 360        | 0.3            | 0.010                  | 0.033             |
| 420        | 0.3            | 0.015                  | 0.031             |
| 480        | 0.3            | 0.020                  | 0.029             |
| 540        | 0.3            | 0.025                  | 0.028             |
| 600        | 1.0            | 0.005                  | 0.027             |
| 660        | 1.0            | 0.000                  | 0.026             |

## C

| Time (min) | Pressure (atm) | Instantaneous risk, h(t) |
|------------|----------------|--------------------------|
| 0          | 1.0            | 0.00000                  |
| 60         | 1.0            | 0.00000                  |
| 120        | 1.0            | 0.00000                  |
| 180        | 0.7            | 0.00000                  |
| 240        | 1.0            | 0.00000                  |
| 300        | 0.3            | 0.00005                  |
| 360        | 0.3            | 0.00015                  |
| 420        | 0.3            | 0.00025                  |
| 480        | 0.3            | 0.00030                  |
| 540        | 0.3            | 0.00033                  |
| 600        | 1.0            | 0.00010                  |
| 660        | 1.0            | 0.00002                  |
---
| Time (min) | Pressure (atm) | PDCS (%) |
|------------|----------------|-----------|
| 0          | 1.0            | 0.0       |
| 60         | 1.0            | 0.0       |
| 120        | 1.0            | 0.0       |
| 180        | 0.65           | 0.0       |
| 240        | 1.0            | 0.0       |
| 300        | 0.3            | 0.0       |
| 360        | 0.3            | 1.5       |
| 420        | 0.3            | 3.0       |
| 480        | 0.3            | 4.5       |
| 540        | 1.0            | 5.8       |
| 600        | 1.0            | 6.0       |
| 660        | 1.0            | 6.2       |

Figure 19. Pressure and model-estimated cumulative risk of DCS during the NASA PRP Phase II profile described in Table 7 and illustrated in Figure 18. Exercise periods are labeled as described in Figure 18.

All illustrated model features for this PRP Phase II profile, including the instantaneous and cumulative risks of DCS, are computed as they evolve in response to changes in the covariates of pressure, inspired O2 fraction, and exercise intensity within the profile. As a result, the instantaneous risk of DCS varies with time as illustrated in panel C of Figure 18. This model behavior contrasts sharply with that of models with time-invariant covariates and constant hazards in any given profile, such as the ADRAC,23 and Conkin, et al.,7,10 models considered above. Such models are based on planned times at altitude or are fit only to profiles with the same times at altitude, and reduce to simple occurrence-only binary quantal response assays, which are insensitive to the shape of the actual hazard function within any given profile.17 Such models can be used to illustrate how the probability of DCS changes with time in a given profile only by compiling model solutions for different profiles with successively increased times at altitude. However, because these models are not fit to actual failure times but to factitious failure times presumed equal to the planned times at altitude or to the fixed time at attitude of the data, the time-dependences of DCS risk accumulation obtained in this fashion are extrapolations strictly beyond the scope of the models.

## 4.5 Model Deficiencies and Remaining Issues

The favorable chi-square comparisons above depend on the adjustment of model-estimated DCS incidences for risk that would have accumulated in profiles that were terminated early due to occurrence of DCS. However, the overall results indicate that the model does not perform as favorably on other profiles in the calibration data. Referring to data in Appendix F, the sum of the adjusted estimated incidences of DCS exceeds the sum of the actual incidences by 38 (896.5 vs. 858.3) in the full set of calibration data, and by 43 (501.2 vs. 458.3) in the 84 subsets of the calibration data

35
---
considered to be fit by the model according to chi-square tests of subsets ordered by
Pearson Residual. In contrast, comparison of the observed and model-estimated
occurrence density functions, where such adjustments are inapplicable, indicates that
the model tends to incorrectly delay DCS risk accumulation and underestimate
incidences by 3 – 15 % in the first four hours after last decompression. Thus, the model
overestimates risk in the latter parts of long expoures at altitude, and provides only poor
representations of the actual time courses of DCS risk accumulation in many types of
profile.

Model failure to capture essential features of the time courses of DCS risk accumulation
may reflect that some subsets in the calibration data are not combinable due to
oversimplification of exercise effects. The types of exercise performed in the profiles of
the various data subsets varied widely, ranging from various isometric and isotonic arm
and leg weight lifting exercises, constant torque arm pull exercises, fixed resistance
rope pull arm exercises, knee bends, stair stepping, leg cycle ergometry, arm cycle
ergometry, and dual cycle ergometry. The intensity of the exercises, regardless of type,
was considered only in terms of the whole-body oxygen consumption rate associated
with the exercise. This oxygen consumption rate was not normalized with respect to any
subject-specific index such as maximum oxygen consumption rate or body weight.
Other workers have argued convincingly that such normalization is essential for whole-
body oxygen consumption to accurately represent the intensity of work performed by
different subjects in a given type of exercise.10,58 Moreover, exercise at altitude in most
profiles was intermittent, with periods of exercise alternated with periods of rest.
Exercise intensity during profile segments in which such intermittent exercise was
performed was defined in the present calibration data as the whole-body oxygen
consumption rate averaged over all periods of exercise and rest in the segment. All
possible characterizations of different types of exercise were collapsed into a single
independent variable, the average whole-body oxygen consumption rate, because of
lack of data to support more detailed descriptions and to limit the number of covariates
in the model, a compromise that almost certainly limited the attainable scope of model
success.

Consideration of exercise effects on compartmental bubble nucleation to be manifest
instantaneously with the onset of exercise was an additional simplifying assumption in
the present model. With exercise at altitude coded to commence upon arrival at altitude,
the exercise-induced shifts in the compartmental populations of pre-existing nuclei
occurred at the points in the profiles with the highest compartmental gas
supersaturations, where conditions prevailed to recruit the largest number of bubbles
and promote the highest rates of DCS risk accumulation. It is therefore unlikely that
treatments of the kinetics of exercise effects on compartmental bubble nucleation
different from that implemented in the present model could cause higher risks of DCS
earlier in an altitude exposure. On the other hand, exercise effects on blood-tissue gas
exchange were also considered to be fully manifest immediately upon commencement
of exercise and fully absent immediately upon cessation of exercise. Consideration of
on-effect kinetics for such effects would cause the higher gas supersaturations
prevailing upon initial arrival at altitude to persist and promote early bubble growth and
higher rates of DCS risk accumulation than with the instant-on exercise-induced
acceleration of gas elimination presently assumed. Incorporation of on- and off-effect

36
---
kinetics for the influences of exercise on blood-tissue gas exchange – as described, for example, in Appendix B – has yet to be explored.

Finally, the Λ parameter in the 3RUT-MBe1 model was assumed constant in present work to allow use of the piece-wise analytic solution of the model equations described in Appendix B. In principle, however, the Λ parameter accommodates the influences on bubble evolution of heterogeneity in the diffusion field around each modeled bubble.31 Because such influences include bubble-bubble interactions when more than one bubble is present in a compartment, Λ must vary with time as a function of bubble number and volume. Such time dependent variation of Λ warrants examination as a model feature that may allow more accurate modeling of the time courses of DCS risk accumulation at altitude.

## 5. Conclusions

A probabilistic model of DCS incidence and time of occurrence has been developed that is able to accommodate the influences of pressure, changing inspired inert gas, oxygen breathing, and exercise in profiles of arbitrary complexity. The model is a time-dependent covariate survival model in which the risks of DCS are determined as functions of the prevailing volumes and profusions of gas bubbles in a perfusion-limited gas exchange compartment. The bubbles vary in volume by diffusion-limited exchange of gas between the bubbles and their surroundings according to an implementation of the three-region unstirred tissue model of gas bubble evolution elaborated to accommodate the influences of exercise and oxygen breathing on compartmental gas exchange and bubble nucleation. The model has been shown to provide performance superior to that of other published models on a variety of data subset collections that is much more diverse than can be handled by any one of the other models.

Model successes are tempered by model failure to accurately represent the time courses of DCS risk accumulation at altitude and consequent failure to fit all subsets of the calibration data. The subsets on which the model fails may be incombinable with the subsets on which the model succeeds, in large part due to the wide variety of exercise types performed in the different subsets and the oversimplification of the independent variable for exercise in the model. Model tendency to skew DCS risk accumulation to later periods at altitude and underestimate risk early in the exposures may be rectified with implementation of model features that were not exercised in the present model.

Numerical issues with model implementation remain to be solved before the model will be applicable to diving data.

37
---
## 6. Acknowledgements

Portions of this work were supported by National Aeronautics and Space Administration (NASA) Biomedical Research and Countermeasures Program grant, "Optimization of Astronaut Decompression Sickness Prevention Protocols Using Probabilistic Gas and Bubble Dynamics Models," MIPR Number NNJ04HF521, and NAVSEA Task Assignment 10-12, "Decompression Algorithm Development and Implementation." The authors are grateful to Dr. Johnny Conkin, who provided validated copies of data from NASA Tests 1 through 11 for inclusion in the present model calibration data. The authors also thank Dr. David Doolette for his critical review of this manuscript and many helpful suggestions for revision.
---
## 7. References

1. Tikuisis P, Gerth WA. Decompression theory. In: Brubakk AO, Neuman TS, editors. Bennett and Elliott's physiology and medicine of diving. 5th ed. Edinburg: W.B. Saunders Co.; 2003. p. 419-454.

2. Weathersby PK, Homer LD, Flynn ET. On the likelihood of decompression sickness. Journal of Applied Physiology: Respiration, Environmental and Exercise Physiology 1984; 57(3):815-25.

3. Weathersby PK, Survanshi SS, Homer LD, Hart BL, Flynn ET, Bradley ME. Statistically based decompression tables II: Equal risk air diving decompression schedules. Bethesda, MD: Naval Medical Research Institute, 1985; NMRI Technical Report 85-17.

4. Survanshi SS, Weathersby PK, Thalmann ED. Statistically based decompression tables X: Real-time decompression algorithm using a probabilistic model. Bethesda, MD: Naval Medical Research Institute, 1996; NMRI Technical Report 96-06.

5. Southerland DG. Logistic regression and decompression sickness. M.S. Thesis, Duke Univerity, 1992.

6. Conkin, J., B.F. Edwards, J.M. Waligora, and D.J. Horrigan, Jr. Empirical models for use in designing decompression procedures for space operations. NASA Technical Memorandum 100456, Johnson Space Center, Houston, TX, June 1987.

7. Conkin J, Kumar K, Powell MR, Foster PP, Waligora JM. A probabilistic model of hypobaric decompression sickness based on 66 chamber tests. Aviation, Space, and Environmental Medicine 1996; 67:176-183.

8. Loftin KC, Conkin J, Powell MR. Modeling the effects of exercise during 100% oxygen prebreathe on the risk of hypobaric decompression sickness. Aviation Space and Environmental Medicine 1997; 68:199-204.

9. Kannan N, Raychaudhuri A, Pilmanis AA. A loglogistic model for altitude decompression sickness. Aviation, Space, and Environmental Medicine 1998; 69:965-70.

10. Conkin J, Gernhardt ML, Powell MR, Pollock N. A probability model of decompression sickness at 4.3 psia after exercise prebreathe. NASA/TP-2004-213158, Johnson Space Center, Houston, TX, December 2004.

11. Conkin J, Gernhardt ML, Abercromby AF, Feiveson AH. Probability of hypobaric decompression sickness including extreme exposures. Aviation, Space, and Environmental Medicine 2013; 84(7): 661-668.

12. Gernhardt ML. Development and evaluation of a decompression stress index based on tissue bubble dynamics [Dissertation]. Philadelphia, PA: University of Pennsylvania; 1991.

39
---
13. Gerth WA, Vann RD. Statistical bubble dynamics algorithms for assessment of altitude decompression sickness incidence. Armstrong Laboratory Technical Report AL/CF-TR-1995-0037. Brooks Air Force Base, San Antonio, TX, 1995.

14. Vann RD, Thalmann ED, Decompression physiology and practice. Bennett PB, Elliot DH, editors. The physiology and medicine of diving. 4th ed. London: W.B. Saunders, 1993: 376-432.

15. Weathersby PK, Survanshi SS, Homer LD, Parker E, Thalmann ED. Predicting the time of occurrence of decompression sickness. Journal of Applied Physiology 1992; 72(4):1541-8.

16. Kalbfleisch JD, Prentice RL. The statistical analysis of failure time data. New York: Wiley, 1980.

17. Gerth WA. Overview of survival functions and methodology. In: Weathersby PK and Gerth WA, editors. Survival analysis and maximum likelihood techniques as applied to physiological modeling. Fifty-first Workshop, Undersea and Hyperbaric Medical Sociey Inc., Bethesda, MD; 2002, p. 1-48.

18. Van Liew HD, Conkin J, Burkhard ME. Probabilistic model of altitude decompression sickness based on mechanistic principles. Journal of Applied Physiology 1994; 76(6):2726-34.

19. Van Liew HD, Burkhard ME, Conkin J. Testing of hypotheses about altitude decompression sickness by statistical analyses. Undersea and Hyperbaric Medicine 1996; 23(4):225-33.

20. Kannan N, Raychaudhuri A. Survival models for predicting altitude decompression sickness. Brooks Air Force Base, TX, 1997; AL/CF-TR-1997-0030.

21. Conkin J. Evidence-based approach to the analysis of serious decompression sickness with application to EVA astronauts. NASA/TP-2001-210196. NASA Center for Aerospace Information, Hanover MD. Jan 2001.

22. Kannan N. Survival models for altitude decompression sickness. In: Weathersby PK and Gerth WA, editors. Survival analysis and maximum likelihood techniques as applied to physiological modeling. Fifty-first Workshop, Undersea and Hyperbaric Medical Sociey Inc., 2002, p. 101-109.

23. Pilmanis AA, Petropoulos LJ, Kannan N, Webb JT. Decompression sickness risk model: Development and validation by 150 prospective hypobaric exposures. Aviation, Space, and Environmental Medicine 2004; 75:749-59.

24. Tikuisis P, Gault KA, Nishi RY. Prediction of decompression illness using bubble models. Undersea and Hyperbaric Medicine 1994; 21(2): 129-143.

25. Tikuisis, Nishi RY. Role of oxygen in a bubble model for predicting decompression illness. Defence and Civil Institute of Environmental Medicine, Ontario, Canada, DCIEM No. 94-04, 1994.

40
---
26. Gerth WA, Vann RD. Development of iso-DCS risk air and nitrox decompression tables using statistical bubble dynamics models. Bethesda, MD: National Oceanic and Atmospheric Administration, Office of Undersea Research, 1996; Final Report, Contract # NA46RU0505.

27. Gerth WA, Vann RD. Probabilistic gas and bubble dynamics models of DCS occurrence in air and N₂O₂ diving. Undersea and Hyperbaric Medicine 1997; 24(4):275-92.

28. Van Liew HD, Hlastala MP. Influence of bubble size and blood perfusion on absorption of gas bubbles in tissues. Resp Physiol 1969; 7:111-121.

29. Srinivasan RS, Gerth WA, Powell MR. Mathematical models of diffusion-limited gas bubble dynamics in tissue. Journal of Applied Physiology 1999; 86(2):732-41.

30. Srinivasan RS, Gerth WA, Powell MR. Mathematical model of diffusion-limited evolution of multiple gas bubbles in tissue. Annals of Biomedical Engineering 2003; 31:471-81.

31. Srinivasan RS, Gerth WA, Mathematical models of diffusion-limited gas bubble evolution in perfused tissue. NEDU TR 13-05, Navy Experimental Diving Unit, Panama City, FL, Aug 2013.

32. Boycott AE, Damant GCC, Haldane JB. The prevention compressed air illness. Journal of Hygiene, London 1908; 8:342-443.

33. McArdle WD, Katch FI, Katch VL. Exercise physiology. Energy, nutrition and human performance. 4th ed. Baltimore: Williams and Wilkins, 1996. p. 147.

34. Astrand P-O, Rodahl K, Dahl HA, Stromme SS. Textbook of Work Physiology: Physiological Bases of Exercise. 4th ed. Human Kinetics, Champaign, IL, 2003.

35. Kalliokoski KK et al. Relationship between muscle blood flow and oxygen uptake during exercise in endurance-trained and untrained men. Journal of Applied Physiology 2005; 98:380-3.

36. Thalmann ED, Parker EC, Survanshi SS, Weathersby PK. Improved probabilistic decompression model predictions using linear-exponential kinetics. Undersea and Hyperbaric Medicine 1997; 24(4):255-74.

37. Parker EC, Survanshi SS, Massell PB, Weathersby PK. Probabilistic models of the role of oxygen in human decompression sickness. Journal of Applied Physiology 1998; 84:1096-102.

38. Gerth WA, Johnson TM. Development and Validation of 1.3 ATA PO₂-in-He Decompression Tables for the MK 16 MOD 1 UBA. NEDU TR 02-10. Panama City, FL, Navy Experimental Diving Unit, 2002.

39. Severinghaus JW. Simple accurate equations for human blood O₂ dissociation computations. J. Appl. Physiol: Respir Environ Exercise Physiol 1979; 46: 599-602.

41
---
40. Yount DE. Skins of varying permeability: A stabilization mechanism for gas cavitation nuclei. Journal of the Acoustical Society of America 1979; 65:1429-39.

41. Yount DE. On the evolution, generation, and regeneration of gas cavitation nuclei. Journal of the Acoustical Society of America 1982; 71(6): 1473-1481.

42. Kindwall EP, Baz A, Lightfoot EN, Lanphier EH, Seireg S. Nitrogen elimination in man during decompression. Undersea Biomedical Research 1974; 2(4): 285-297.

43. Gerth WA. Probabilistic models of decompression sickness during flying after diving: motivation for mechanism. In: Weathersby PK and Gerth WA, editors. Survival analysis and maximum likelihood techniques as applied to physiological modeling. Fifty-first Workshop, Undersea and Hyperbaric Medical Sociey Inc., 2002, p. 118-136.

44. Howle LE, Weber PW, Vann RD, Campbell MC. Marginal DCS events: their relation to decompression and use in DCS models. Journal of Applied Physiology 2009; 107: 1539-1547.

45. Murphy FG, Swingler AJ, Gerth WA, Howle LE. Iso-risk air no decompression limits after scoring marginal decompression sickness cases as non-events. Computers in Biology and Medicine 2018; 92(1):110-117.

46. Marquart DW. An algorithm for least-squares estimation of nonlinear parameters. J Soc Indust Appl. Math 1963; 11:431-441.

47. Webb JT. Documentation for the USAF School of Aerospace Medicine altitude decompression sickness research database, AFRL-SA-BR-SR-2009-0007, USAF School of Aerospace Medicine, Brooks City Base, TX, May 2010.

48. Gerth WA, Besich W, DeCelles T, Eshaghian B. The USAFSAM computerized hypobaric decompression sickness data base. Brooks Air Force Base, TX: USAF School of Aerospace Medicine; 1984. Lineprinter output of text and tables in 1 bound volume. Located at: Navy Experimental Diving Unit, Panama City, FL.

49. Conkin J. email, Transfer of all Bends 1 data. 10-Sep-2004.

50. Conkin J. email, Transfer of all Bends 2 data. 16-Sep-2004.

51. Conkin J. email, Bends 3 test series. 23-Sep-2004.

52. Conkin J. email, Bends 4, 5, 6, and 7 data. 30-Sep-2004.

53. Conkin J. email, Bends 8, 9, 10, and 11 data. 7-Oct-2004.

54. Gernhardt ML, Conkin J, Foster PP, Pilmanis AA, Butler BD, Fife CE, Vann RD, Gerth WA, Loftin KC, Dervay JP, Waligora JM and Powell MR. Design of a 2-hour prebreathe protocol for space walks from the International Space Station. 2000 Annual Scientific Meeting of the Aerospace Medical Association, Houston, TX May

42
---
14-18, 2000.

55. Gernhardt ML, Conkin J, Foster PP, Pilmanis AA, Butler BD, Beltran E, Fife CE, Vann RD, Gerth WA, Loftin KC, Acock K, Dervay JP, Waligora JM, Powell MR, Feiveson AH, Nishi RY, Sullivan PA, Schneider SM. Design and testing of a 2-hour oxygen prebreathe protocol for space walks from the International Space Station. Undersea and Hyperbaric Medicine 2000; 27(S): 12.

56. Gernhardt ML. Prebreathe reduction program – Phase V. Summary of research. In: Bennett PB, Michaelson R, Butler F, Moon R, editors. Best practice guidelines for prevention and effective treatment of decompresion illness proceedings: Part I. Undersea and Hyperbaric Medical Society, Durham, NC, 2010. pp. 132-174.

57. Gernhardt ML. Modified oxygen prebreathe to include a slightly longer oxygen-breathing period with a heavy exercise period followed by a light exercise period. In: Bennett PB, Michaelson R, Butler F, Moon R, editors. Best practice guidelines for prevention and effective treatment of decompresion illness proceedings: Part 2. Undersea and Hyperbaric Medical Society, Durham, NC, 2010. pp. 117-147.

58. Webb JT, Krock LP, Gernhardt ML. Oxygen consumption during exposure as a risk factor for altitude decompression sickness. Aviat Sp Environ Med 2010; 81:987-992.

59. Webb JT, Pilmanis AA, Balldin UI. "Altitude decompression sickness at 7620 m following prebreathe enhanced with exercise periods." Aviat Space Environ Med 2004; 75:859-864.

60. Webb JT, Fischer MD, Heaps CL, Pilmanis AA. Exercise-enhanced preoxygenation increases protection from decompression sickness. Aviation, Space and Environmental Medicine 1996; 67:628-4.

61. Conkin J, Waligora JM, Horrigan DJ Jr, Hadley AT. The effect of exercise on venous gas emboli and decompression sickness in human subjects at 4.3 psia. NASA Technical Memorandum 58278, Lyndon B. Johnson Space Center, Houston, TX, March 1987.

62. Inderbitzen RS and DeCarlis JJ. Energy expenditure during simulated EVA workloads. San Diego, CA: SAE Technical Paper *860921, 16th ICES, 1986:4pp.

63. Doolette DJ, Gerth WA, Gault KA. Addition of work rate and temperature Information to the augmented NMRI standard (ANS) data files in the "NMRI98" subset of the USN N2-O2 primary data set. NEDU TR 11-02, Navy Experimental Diving Unit, Jan 2011.

64. Doolette DJ. Addition of work rate and temperature information to the augmented NMRI standard (ANS) data files in the "he8n25" subset of the U.S.N. primary data set. NEDU TR 17-10, Navy Experimental Diving Unit, 2017.

43
---
65. Harrell FE Jr. Regression modeling strategies, with applications to linear models, logistic regresssion, and survival analysis, 2nd ed. New York: Springer, 2015.

66. Hosmer DW, Lemeshow S. Applied logistic regression. New York: John Wiley & Sons, 1989.

67. Doolette DJ, Gerth WA, Gault KA. Decompression models with work-induced changes in compartment gas kinetic time constants. Undersea and Hyperbaric Medicine 2010; 37:294.

68. West, J. B. Respiratory physiology. Baltimore: Williams and Wilkins, 1985.

69. Lobdell DD. An invertible simple equation for computation of blood O2 dissociation relations. Journal of Applied Physiology 1981; 50(5):971-3.

70. Van Liew HD. Simulation of the dynamics of decompression sickness bubbles and the generation of new bubbles. Undersea Biomedical Research 1991; 18:333-345.

71. Howle LE. Analytic gain in probabilistic decompression sickness models. Computers in Biology and Medicine, 2013; 43(11): 1739-1747.
---
# 8. Appendix A. Three-Region Unstirred Tissue Multiple Bubble (3RUT-MB) Model of Tissue Gas and Bubble Dynamics

In the original 3RUT-MB model,30,31 the total gas bubble volume Vg(t) in a given hypothetical tissue compartment at time t is the sum of the volumes of Nb bubbles of equal radius r(t) and volume Vb(t) = 4π/3 r3(t) in the compartment:

Vg(t) = NbVb(t) = Nb 4π/3 r3(t). (A.1)

Several versions of the 3RUT-MB model equations for computing Vg(t) have been developed as described below to handle increasingly general and more complex scenarios for bubble evolution in tissue, including cases in which the bubbles are not of equal volume, evolve under the influences of multiple diffusible gases, and are present in numbers that change with time.

## 8.1 Single Diffusible Gas

In single diffusible gas systems, the diffusible gas is inert and the metabolic gases water vapor, carbon dioxide (CO2), and oxygen (O2) are assumed to be infinitely diffusible – and hence always in equilibrium – between bubble, tissue, and blood.

### 8.1.1 Multiple Bubbles of Same Size

The bubble radius r and inert gas pressure Pb in each of the Nb bubbles in a single diffusible gas system satisfy the equation for the rate of change of bubble radius given by

$$
\frac{dr}{dt} = \frac{[K(p_t - P_b)[\Lambda + \frac{1}{r}]] - \frac{r}{3}\frac{dP_{amb}}{dt}}{P_{amb} - P_\infty + \frac{4\sigma}{3r} + \frac{8\pi}{3}Mr^3},
$$ (A.2)

where the bracketed term in the numerator on the right is the inert gas flux per unit area across the bubble-tissue surface (positive for inward flux), K is the permeability (= solubility × diffusivity) of the diffusible gas in tissue, pt is the spatial average tissue inert gas tension, Pb is the diffusible gas partial pressure in the bubble, Pamb is the ambient hydrostatic pressure, σ is surface tension, M is tissue modulus of elasticity, and Λ is a

A-1
---
parameter with dimension 1/r that accommodates all effects of perfusion heterogeneity^f and bubble-bubble interactions on bubble evolution. P∞ is the total pressure of the infinitely diffusible gases in the bubble, i.e., P∞ = P<sub>H<sub>2</sub>O</sub> + P<sub>CO<sub>2</sub></sub> + P<sub>O<sub>2</sub></sub>, equal to p∞ in the tissue. P∞ and its components are assumed constant and the same in all tissue compartments. The diffusible gas partial pressure in each bubble is given by the LaPlace equation with an added term to account for the pressure exerted by tissue elasticity:

$$P_b(t) = P_{amb}-P_∞ + \frac{2σ}{r(t)} + \frac{4π}{3}Mr^3(t),$$
(A.3)

The spatial average tissue inert gas tension p<sub>t</sub> in Eq. (A.2) has been shown to be given by

$$\frac{dp_t}{dt} + qp_t = qp_a - G\frac{dx(t)}{dt}.$$
(A.4)

where q = 1/τ, with the blood-tissue gas exchange time constant τ = α<sub>t</sub>/α<sub>b</sub>Q̇<sub>t</sub>,

G = (4π/3)N<sub>b</sub>/α<sub>t</sub>V<sub>t</sub>, and x(t) = P<sub>b</sub>(t)r<sup>3</sup>(t).

Inspired gas is assumed to contain no CO<sub>2</sub> and equilibrium is assumed between alveolar gas and arterial blood, so p<sub>a</sub> equals the alveolar inert gas partial pressure P<sub>A</sub> as given by combining Dalton's law for alveolar gas and the alveolar gas equation;^68

$$P_{AO_2} = P_{amb} - P_{H_2O} - P_{ACO_2} - P_A = F_{IO_2}(P_{amb} - P_{H_2O}) - P_{ACO_2}\left[F_{IO_2} + \left(1 - \frac{F_{IO_2}}{RQ}\right)\right];$$
(A.5)

and solving for P<sub>A</sub>:

$$P_A = p_a = (1 - F_{IO_2})\left[(P_{amb} - P_{H_2O}) - P_{ACO_2}\left(1 - \frac{1}{RQ}\right)\right],$$
(A.6)

where F<sub>IO<sub>2</sub></sub> is the fraction of oxygen in dry inspired gas, P<sub>ACO<sub>2</sub></sub> is the alveolar CO<sub>2</sub> partial pressure (assumed equal to 35 mm-Hg in present work), and RQ is the respiratory quotient (ratio of the rate of whole body CO<sub>2</sub> production to the rate of whole body O<sub>2</sub> consumption = V̇<sub>CO<sub>2</sub>,wb</sub>/V̇<sub>O<sub>2</sub>,wb</sub>).

^f Spatial variations in perfusion are assumed to sum to zero over the tissue volume.

A-2
---
The equations for dr/dt and dp/dt are coupled nonlinear equations that require numerical solution.

## 8.1.2 Multiple Bubbles of Different Sizes

The relationships in Eqs. (A.2) through (A.4) are readily elaborated to accommodate the solution for the radii and gas pressures of multiple bubbles present in an arbitrary distribution of N<sub>bs</sub> different sizes. Such elaboration entails repeating the dr/dt and P<sub>b</sub> solutions in Eqs. (A.2) and (A.3) for the bubbles of each size in the distribution. Thus, for bubbles of m<sup>th</sup> size, Eq. (A.2) becomes

$$
\frac{dr_m}{dt} = \frac{K_m\left[\Lambda + \frac{1}{r_m}(p_t - P_{b_m}) - \frac{r_m}{3}\frac{dP_{amb}}{dt}\right]}{P_{amb} - P_\infty + \frac{4\sigma_m}{3r_m} + \frac{8\pi}{3}M_mr_m^3},
$$

(A.9)

and Eq. (A.3) becomes

$$
P_{b_m}(t) = P_{amb} - P_\infty + \frac{2\sigma_m}{r_m(t)} + \frac{4\pi}{3}M_m r_m^3(t).
$$

(A.10)

Although not necessary, the bubble surface permeability, K<sub>m</sub>, surface tension, σ<sub>m</sub>, and modulus of elasticity, M<sub>m</sub>, are considered to be different for each bubble size group.

Eq. (A.4) for the tissue gas tension, p<sub>t</sub>, also requires modification to account for the net gas exchange between all bubbles and the tissue, as such exchange differs for bubbles of different sizes. The right-most term in Eq. (A.4) is replaced by the sum of the amounts of gas exchanged between tissue and all bubbles of N<sub>bs</sub> different sizes to yield:

$$
\frac{dp_t}{dt} + qp_t = qp_a - \sum_{m}^{N_{bs}} G_m \frac{dx_m(t)}{dt},
$$

(A.11)

where

$$
G_m = \left(\frac{4\pi}{3}\right)\frac{n_{b_m}}{\alpha_t V_t},
$$

$$
x_m(t) = P_{b_m}(t)r_m^3(t),
$$

A-3
---
and n_bm is the number of bubbles in the m^th size group; i.e., the number of identically sized bubbles of radius r_m.

Finally, the total volume of bubbles in the tissue is given by appropriate elaboration of Eq. (A.1):

$$V_g(t) = \sum_{m} n_{b_m} \frac{4\pi}{3} r_m^3(t) = \sum_{m} n_{b_m} V_{b_m}(t).$$ (A.12)

Determination of r_m and P_bm for bubble size groups m=1, 2, ..., N_bs, and p_t at any time t requires computation time in excess of that required for the N_bs = 1 case (multiple bubbles of the same size) roughly in proportion to the number of bubble sizes considered.

### 8.1.3 Exercise Effects on Blood-Tissue Gas Exchange

Blood flow Q̇ changes with activity level and consequently varies with time, which causes the time constant τ to be a function of time. Accordingly, Eq. (A.11) is modified to explicitly indicate the time-dependence of the coefficients:

$$\frac{dp_t}{dt} + q(t)p_t = q(t)p_a - \sum_{m} G_m \frac{dx_m(t)}{dt},$$ (A.13)

where q(t) = 1/τ(t) = α_b Q̇(t) / α_t is proportional to blood flow.

Eq. (A.13) is a linear differential equation in p_t with a variable coefficient q(t). Solutions of Eq. (A.13) with general and specific models of q(t) are described in Appendix B. The specific q(t) model includes dependence of compartmental Q̇ on compartmental O_2 consumption, which is in turn dependent on exercise intensity.

## 8.2 Multiple Diffusible Gases

The bubble evolution Eq. (A.9) is elaborated as follows to accommodate more than one diffusible gas:

A-4
---
$$\frac{dr_m}{dt} = \frac{\left\{\sum_{k=1}^{N_g} K_{k,m}(p_{t_k} - P_{b_{k,m}})\right\}\left[\Lambda + \frac{1}{r_m}\right] - \frac{r_m}{3} \frac{dP_{amb}}{dt}}{P_{amb} - P_\infty + \frac{4\sigma_m}{3r_m} + \frac{8\pi}{3} M_mr_m^3}; \quad m = 1, 2, ..., N_{bs},\quad (A.14)$$

where $N_g$ is the total number of gases with finite diffusivity and the subscript k denotes the k^th gas with spatial average tissue tension $p_{t_k}$, bubble gas partial pressure $P_{b_{k,m}}$, and bubble surface permeability $K_{k,m}$ associated with bubbles of the m^th size. Note that $\Lambda$ is assumed to be the same for all bubble sizes and diffusible gases but that each diffusible gas beyond the first (gases for which k > 1) introduces an additional permeability coefficient.

The total pressure $P_{b_{T,m}}$ of all diffusible gases in bubbles of m^th size is computed using Eq. (A.10) as with a single gas:

$$P_{b_{T,m}}(t) = P_{amb} - P_\infty + \frac{2\sigma_m}{r_m(t)} + \frac{4\pi}{3} M_mr_m^3(t) . \quad (A.15)$$

However, the partial pressure of each diffusible gas k in the m^th size bubble, $P_{b_{k,m}}$, must be determined by integrating the flux × area product for gas k in conjunction with the dr/dt integration.

The average tissue tension is computed separately for each diffusible gas using Eq. (A.13):

$$\frac{dp_{t_k}}{dt} + q_k(t)p_{t_k} = q_k(t)p_{a_k} - \sum_m^{N_{bs}} G_{k,m} \frac{dx_{k,m}(t)}{dt}; \quad k = 1, 2, ..., N_g; \quad (A.16)$$

where $p_{t_k}$ and $p_{a_k}$ are the average tissue and arterial tensions of the k^th diffusible gas, respectively, $q_k(t) = \frac{1}{\tau_k(t)} = \frac{\alpha_{b_k} \dot{Q}(t)}{\alpha_{t_k}}$,

$$G_{k,m} = \left(\frac{4\pi}{3}\right) \frac{n_{b_m}}{\alpha_{t_k} V_t},$$

and

$$x_{k,m}(t) = P_{b_{k,m}}(t)r_m^3(t).$$

$\tau_k(t)$ – and hence $q_k(t)$ – is different for each gas because of differences in solubility ratio, $\alpha_{b_k}/\alpha_{t_k}$. The arterial tension of the k^th diffusible gas, $p_{a_k}$, is obtained

A-5
---
under the assumptions applied in the single diffusible gas case with appropriate elaboration of Eq.(A.6):

$$\sum_{k=1}^{N_g} PA_k = \sum_{k=1}^{N_g} pa_k = \sum_{k=1}^{N_g} FI_k \left[(P_{amb} - P_{H_2O}) - P_{ACO_2} \left(1 - \frac{1}{RQ}\right)\right],\tag{A.17}$$

$$PA_k = pa_k = FI_k \left[(P_{amb} - P_{H_2O}) - P_{ACO_2} \left(1 - \frac{1}{RQ}\right)\right], \quad k=1, ..., N_g.\tag{A.18}$$

Note that the gas fraction sum, $\sum_{k=1}^{N_g} FI_k$, in Eq. (A.17) must equal $(1 - FI_{O_2})$.

Eqs. (A.14), (A.15), and (A.16) are the requisite equations for computing the evolution of bubbles of $N_{bs}$ different sizes, and the corresponding bubble pressures and total volumes, when more than one diffusible gas is present in the tissue. Eq. (A.14) for the rate of change of bubble radius is more complex than Eq. (A.9) for the $N_g = 1$ case, but there is no increase in the number of equations, $N_{bs}$. Eq. (A.16) for the average tissue gas tension is the same as before, but there are now as many of these equations as the number of diffusible gases, $N_g$. Thus, the overall model comprises a total of $(N_{bs} + N_g)$ equations for each tissue compartment along with Eq. (A.12) for calculating the gas volume $V_g(t)$.

## 8.2.1 Tissue O₂ Tension with O₂ as a Diffusible Gas

When equilibrium of O₂ tensions between bubble and tissue is not assumed, bubble evolution is influenced by O₂ pressure gradients across the bubble-tissue interface. Under such conditions, O₂ must be treated as a gas with finite diffusivity along with the inert gases present in the tissue. Because O₂ mass balance between bubble, tissue, and blood must include accounting for the metabolic consumption of O₂ in the tissue and the nonlinear relationship between blood O₂ content and O₂ partial pressure due to O₂ binding to hemoglobin in blood, the expression for tissue O₂ tension as it is affected by bubble-tissue and tissue-blood gas exchange is more complex than the corresponding expression for the inert gases.

As for the inert gases, the expression for tissue O₂ tension, $p_{tO_2}$, is obtained from the expression for mass balance of O₂ in tissue, which differs from that for the inert gases and is given by

$$\frac{d}{dt}(\alpha_{tO_2}p_{tO_2}) = \dot{Q}(t)[C_{aO_2} - C_{vO_2}] - \frac{1}{V_t} \sum_{m=1}^{N_{bs}} n_{bm} \frac{d}{dt}[P_{bO_2,m}(t) \cdot V_{bm}(t)] - \dot{V}_{O_2}(t),\tag{A.19}$$

where $\dot{Q}(t)$ = blood flow per unit volume of tissue
      $\dot{V}_{O_2}(t)$ = tissue O₂ consumption rate

A-6
---

$$C_{aO_2}$$ = O₂ concentration in arterial blood entering tissue,

$$C_{\bar{v}O_2}$$ = O₂ concentration in mixed venous blood leaving tissue,

$$p_{aO_2}$$ = arterial O₂ partial pressure,

$$p_{\bar{v}O_2}$$ = O₂ partial pressure in mixed venous blood,

$$α_{tO_2}$$ = O₂ solubility in tissue, and

$$α_{bO_2}$$ = O₂ solubility in blood.

Note that $$\dot{V}_{O2}(t)$$, along with $$\dot{Q}(t)$$, are explicit functions of time as exercise-induced changes in compartmental $$\dot{Q}$$ are presumed to be driven by changes in $$\dot{V}_{O2}$$ (Section 8.2.2).

Under steady-state conditions, the derivative terms in Eq. (A.19) are absent, and O₂ consumption is the product of blood flow and the arterial-venous O₂ content difference. Note that Eq. (A.19) reduces to Eq. (A.16) for the inert gases with substitution of the subscript k for subscript O₂, $$\dot{V}_k = 0$$ (gas k inert), $$C_{a_k} = α_{b_k}p_{a_k}$$, and $$C_{\bar{v}_k} = α_{b_k}p_{\bar{v}_k} = α_{b_k}p_{t_k}$$, with equilibrium assumed between end-capillary venous blood and tissue, in accord with the 3RUT-MB model assumption that blood-tissue gas exchange is perfusion limited.

The arterial and venous O₂ contents, $$C_{aO_2}$$ and $$C_{\bar{v}O_2}$$, in Eq. (A.19) are readily computed at any time from the prevailing arterial and mixed venous O₂ partial pressures; $$p_{aO_2}$$ and $$p_{\bar{v}O_2} = p_{tO_2}$$, respectively; and a suitable approximation of the oxyhemoglobin dissociation curve. As for the inert gases, equilibrium between alveolar gas and arterial blood is assumed so that $$p_{aO_2}$$ equals the alveolar O₂ partial pressure $$P_{AO_2}$$ given by:

$$p_{aO_2} = P_{AO_2} = P_{amb} - P_{H_2O} - P_{ACO_2} - \sum P_{A_k}$$, (A.20)

where $$\sum P_{A_k}$$ is given by Eq. (A.17).

A variety of empirical equations have been described that relate O₂ content and O₂ partial pressure in blood. We use a simple expression developed by Lobdell for $$S_{O_2}$$, the fraction of hemoglobin saturated with O₂ at partial pressure $$P_{O_2}$$:⁶⁹

A-7
---
$$S_{O2} = \frac{a_1p + a_2p^2}{1.0 + b_1p + b_2p^2},$$  (A.21)

where a₁ = 0.34332,
      a₂ = 0.64073,
      b₁ = 0.34128,
      b₂ = a₂ = 0.64073,

$$p = \left(\frac{p_{O2}}{p_{half}}\right)^\eta$$ with

η = 1.58678, and
p_half = half-saturation p_O2 of hemoglobin
         (with p_O2 in units of mm-Hg, p_half = 25.0 mm-Hg.)

The O₂ content of blood C_O2 in mL O₂/ mL blood at O₂ tension p_O2 is then given by

$$C_{O2} = \alpha_{bO2}p_{O2} + Hb_cS_{O2},$$  (A.22)

where Hb_c is the O₂ carrying capacity of hemoglobin in whole blood (= 0.20 mL/mL) and
α_bO2 is the solubility of O₂ in plasma in mL O₂/ mL plasma mm-Hg, and S_O2 is obtained
from Eq. (A.21).

There is no analytic solution of the nonlinear differential Eq. (A.19) for p_tO2, which must
therefore be solved numerically. Recursive relations for the numerical solution of Eq.
(A.19) are given in Appendix B.

## 8.2.2 Exercise Effects on Tissue O₂ Consumption

Exercise-induced changes in compartmental V̇_O2(t) are readily modeled as a single
exponential function of time:

$$\dot{V}_{O2}(t) = \dot{V}_{O2_{rest}} + \Delta\dot{V}_{O2_{ex}}\left\{1-\exp\left(-\frac{t}{\tau_{VO2}}\right)\right\},$$  (A.25)

where V̇_O2_rest is the resting O₂ consumption, τ_VO2 is the time constant associated with
the exponential change in V̇_O2, and ΔV̇_O2_ex is the increase in O₂ consumption from its

A-8
---
resting value after reaching a steady state (t = ∞) with exercise at intensity I<sub>ex</sub>.
ΔV̇O<sub>2ex</sub> is given by

$$\Delta\dot{V}O_{2ex} = m_{\dot{V}O_2}I_{ex},$$  (A.26)

where m<sub>V̇O<sub>2</sub></sub> is a factor governing the sensitivity of V̇O<sub>2</sub> to exercise. The time required
to reach a given fraction f of the total V̇O<sub>2</sub> response to a change in exercise intensity is

given by solving $$f = 1 - exp\left(-\frac{t}{\tau_{\dot{V}O_2}}\right)$$ for t: $$t = \tau_{\dot{V}O_2}ln\left[\frac{1}{(1-f)}\right]$$. Thus, with a time

constant τ<sub>V̇O<sub>2</sub></sub> of 0.75 minute, 98% of the change to a new level of O<sub>2</sub> consumption is
reached in approximately 3 minutes after a change in exercise intensity.

## 8.3 Bubble Nucleation and Variable Bubble Number

Bubbles are recruited from a pre-existing population of bubble nuclei in each
compartment as the gas supersaturation increases during decompression. This
recruitment process causes the number of bubble size groups to increase as
decompression proceeds, so that N<sub>bs</sub> becomes a function of time. In present models,
the pre-existing nuclei are assumed to be stabilized against extinction by skins of
adsorbed amphiphilic molecules, and have an integral distribution of sizes given by<sup>40</sup>

$$N_b = N_b^0exp\left(-\frac{r_{min}}{\beta}\right),$$  (A.27)

where N<sub>b</sub> is the number of nuclei present in the compartment with radius ≥ r<sub>min</sub>, N<sup>0</sup><sub>b</sub> is the
constant total number of nuclei in the compartment, and β is a compartment-specific
distribution slope factor.

The distribution of nuclear sizes is assumed to be affected by pressure, under the
constraints that: (i) no nuclei are extinguished by any overpressures, and (ii) the original
ordering of nuclear sizes is always preserved. Under these constraints, the number of
nuclei with radii greater than or equal to r<sub>min</sub> after exposure to an overpressure given by

$$P_{crush} = P_{amb} - \left(\sum_{k=1}^{N_g} p_{t_k} + P_\infty\right)$$  (A.28)

must equal the number of nuclei with radii greater than or equal to r<sup>0</sup><sub>min</sub> in the
distribution before the exposure. Using Eq. (A.27), we therefore have

A-9
---
$$N_b = N_b^o \exp\left(-\frac{r_{min}}{\beta}\right) = N_b^o \exp\left(-\frac{r_{min}^o}{\beta^o}\right),$$ (A.29)

where β⁰ is the slope factor for the initial nuclear size distribution.

If the adsorbed skins on the nuclei are assumed to remain always permeable to dissolved gases, the post-crush gas supersaturation P_ss required to nucleate the N_b bubbles in Eq. (A.29) depends on the initial r⁰_min and P_crush as given by [6]:

$$P_{ss} = \frac{2\sigma}{r_{min}}$$ (A.30)

$$= \frac{2\sigma(\sigma_c - \sigma)}{\sigma_c r_{min}^o} + P_{crush}\left(\frac{\sigma}{\sigma_c}\right) = \left(\frac{\sigma}{\sigma_c}\right)\frac{2(\sigma_c - \sigma) + P_{crush}r_{min}^o}{r_{min}^o},$$ (A.31)

where Eq. (A.30) is the Laplace equation with tissue elasticity neglected and σ_c (> σ) in Eq. (A.31) is the "crumbling compression" that counters the tendency for surface tension to extinguish nuclei of r⁰_min radius. The crumbling compression is constant for given r⁰_min and N_b, but decreases linearly with decreasing r⁰_min and increasing N_b.

The slope factor, β, for the distribution at a given pressure is obtained using Eqs. (A.29), (A.30), and (A.31):

$$\beta = \left(\frac{\beta^o}{r_{min}^o}\right)r_{min} = \left(\frac{\beta^o}{r_{min}^o}\right)\left(\frac{2\sigma}{P_{ss}}\right) = \left(\frac{\beta^o}{r_{min}^o}\right)\left[2\sigma\left(\frac{\sigma_c}{\sigma}\right)\frac{r_{min}^o}{2(\sigma_c - \sigma) + P_{crush}r_{min}^o}\right]$$

$$= \frac{\beta^o 2\sigma_c}{2(\sigma_c - \sigma) + P_{crush}r_{min}^o}.$$ (A.32)

The r⁰_min and r_min in Eq. (A.29) correspond to the respective pre- and post-crush P_ss values required to nucleate a given number of bubbles N_b. These radii and their corresponding β⁰ and β factors were initially defined in terms of the supersaturations required to form the same number of bubbles in two samples from a given gelatin preparation before and after a P_crush exposure.⁴⁰ In the present context, we wish to determine the supersaturation at which bubbles initially begin to form after a P_crush exposure. If the number of bubbles in any specific anatomical compartment must

A-10
---
increase in integer increments, this supersaturation is that at which the first bubble
forms. Thus, for given β⁰ and N⁰ᵇ, Eq. (A.29) with Nᵇ = 1 is rearranged to give r⁰ₘᵢₙ:

r⁰ₘᵢₙ = β⁰ ln(N⁰ᵇ).                                                                (A.33a)

In present work, however, each hypothetical compartment represents an average of an
indeterminate number of distributed anatomical sites. The number of bubbles in each of
these composite compartments was consequently considered to increase continuously
with allowance of fractional bubble numbers so that Eq. (A.33a) became:

r⁰ₘᵢₙ = β⁰[ln(N⁰ᵇ) - ln(N^min_b)],                                              (A.33b)

where N^min_b is an arbitrary minimum number of bubbles, 0 < N^min_b << 1, allowed in a
compartment.

Note from Eq. (A.32) that β = β⁰ when Pcrush = 2σ/r⁰ₘᵢₙ, which consequently defines the
minimum crushing pressure required to affect the initial distribution.

Substituting Eq. (A.30) into Eq. (A.27) gives the cumulative number of nucleated (or
recruited) bubbles at an arbitrary Pss = [∑ᴺᵍₖ₌₁ pₜₖ + P∞] - Pamb:

Nᵇ = N⁰ᵇ exp(-2σ / βfPss).                                                       (A.34)

Exercise is modeled to affect the nuclei size distribution and bubble nucleation by
modifying the distribution slope factor as follows:

βf = βexβ = βex[2σcβ⁰ / (2(σc - σ) + Pcrushr⁰ₘᵢₙ)],                           (A.35)

where βex is a compartment-specific, dimensionless factor given by

βex = 1 + mβex Iex.                                                              (A.36)

Iex is a measure of exercise intensity (= 0 at rest) and mβex is a factor (≥ 0) governing
the sensitivity of the distribution slope factor to increasing exercise intensities.

Increasing values of Pcrush decrease βf and shift the population of nuclei towards smaller
sizes, while increasing values of βex increase βf and shift the population of nuclei

A-11
---
towards larger sizes. The bubble of largest size in the distribution governs the inception
of bubble formation. The radius of this bubble is given by:

$$r_{min} = \beta_f \left[ \ln(N_b^o) - \ln(N_b^{min}) \right].$$  (A.37)

The corresponding nucleonic volume, V<sub>min</sub>, is

$$V_{min} = \frac{4}{3}\pi r_{min}^3.$$  (A.38)

Supersaturations of magnitude smaller than required to recruit a nucleus of r<sub>min</sub> radius
are sustained metastably; i.e., without bubble formation. Larger supersaturations are
accompanied by bubble nucleation and growth from increasing numbers of nuclei
recruited as given by Equation (A.34). Increasing P<sub>crush</sub> consequently increases the
threshold supersaturation for bubble inception and reduces the number of nuclei
recruited to become macroscopic bubbles at given supersaturations larger than this
threshold. Increasing β<sub>ex</sub>, on the other hand, decreases the threshold supersaturation
for bubble inception and increases the number of nuclei recruited to macroscopic
bubbles at supersaturations above this threshold. In the present model
implementations, compartmental β<sub>f</sub> is updated for effects of P<sub>crush</sub> throughout a given
profile only when no nucleated bubbles are present in the compartment. Compartmental
β<sub>f</sub> is updated for the effects of exercise at the outset of every stage in which exercise is
performed.

Note that Eq. (A.28) indicates that P<sub>crush</sub> increases with increases in P<sub>amb</sub> or decreases in
the total dissolved gas tension. Thus exercise-induced decreases in tissue N<sub>2</sub> and O<sub>2</sub>
tensions during oxygen prebreathes increase P<sub>crush</sub> and shift the distribution of nuclei to
smaller sizes that require higher supersaturations to recruit.

The population of pre-existing nuclei is presumed to be dynamic, maintained by ever-
active mechanisms for nuclei generation. The effects of a given crush must
consequently decay over time as the population of nuclei is restored to the pre-crush
state – even at pressure. Thus, the prevailing P<sub>crush</sub> is considered to instantaneously
achieve the computed crush pressure when the computed P<sub>crush</sub> is increasing. When the
computed P<sub>crush</sub> is constant or decreasing, the prevailing P<sub>crush</sub> is modeled to decay to its
initial value P<sub>crush</sub><sup>o</sup> according to:

$$P_{crush} = P_{crush}^o + (P_{crush} - P_{crush}^o) \exp(-t/\tau_{Pc}),$$  (A.39)

where τ<sub>Pc</sub> is the P<sub>crush</sub> decay time constant.

### 8.3.1 Single Time-Dependent Bubble Size Approximation

In order to obviate need to track the evolution of multiple bubbles of different sizes in
any given compartment, each newly nucleated bubble is assumed to instantaneously

A-12
---
attain the size of prevailing already-nucleated bubbles. Because all bubbles are
consequently the same size, rm, P_bm, and pt must be tracked for only a single bubble
size group (Nbs = 1) in which only nb changes:

$$N_b(t) = \left( \sum_{m}^{N_{bs}(t)} n_{b_m} \right) \equiv n_b(t), \quad N_{bs} = 1. \tag{A.40}$$

Eq. (A.16) is thus simplified:

$$\frac{dp_{t_k}}{dt} + q_k(t)p_{t_k} = q_k(t)p_{a_k} - G_k(t)\frac{dx_k(t)}{dt}, \tag{A.41}$$

where nb – and hence G_k – are now explicit functions of time:

$$G_k(t) = \left(\frac{4\pi}{3}\right) \frac{N_b(t)}{\alpha_{t_k} V_t}$$

and

$$x_k(t) = P_{b_k}(t)r^3(t).$$

Maintenance of mass balance in this approach requires a change in bubble gas content
and a resultant adjustment in tissue gas tension corresponding to the difference
between the nucleonic volume and the prevailing bubble volume whenever a nucleus is
'recruited' during decompression. Regardless of the functional representation of the
G_k(t) factor, it may be approximated by a constant in each integration interval.
Implementation of this approach in the numerical solution of Eq. (A.41) for p_t_k is
described in Appendix B.

## 8.4 Scaled 3RUT-MB Model

If the Λ parameter is constant and independent of the other parameters in the 3RUT-MB
model, the dependent variable rm can be scaled by defining r̂_m = Λrm, where the
overstrike "hat' denotes a scaled quantity. Substituting for rm in terms of r̂_m in Eq. (A.14)
yields

$$\frac{dr̂_m}{dt} = \Lambda\frac{dr_m}{dt} = \frac{\sum_{k=1}^{N_g} \hat{K}_{k,m} \frac{p_{t_k} - P_{b_{k,m}}}{3} \left[1 + \frac{1}{r̂_m}\right] - \frac{r̂_m}{3}\frac{dP_{amb}}{dt}}{P_{amb} - P_\infty + \frac{4\hat{\sigma}_m}{3r̂_m} + 2\hat{M}_m(r̂_m)^3}; \quad m = 1, 2, ..., N_{bs}, \tag{A.42}$$

A-13
---
where $\hat{K}_{k,m} = 3\Lambda^2 K_{k,m}$, $\hat{\sigma}_m = \Lambda\sigma_m$, and $\hat{M}_m = \left(\frac{4\pi}{3}\right)\frac{M_m}{\Lambda^3}$ are the scaled permeability,

surface tension, and tissue modulus of elasticity, respectively, for a bubble in the m^th
bubble size group. Note that $\hat{r}_m$ is dimensionless with $\Lambda$ having dimension of 1/radius,

$\hat{K}_{k,m}$ having dimension of 1/time, and $\hat{\sigma}_m$ and $\hat{M}_m$ having dimension of pressure. The
permeability coefficient for each diffusible gas beyond the first in the tissue (gases for
which k>1) can be specified relative to the first on the basis of the unscaled coefficients:

$$\hat{K}_{k,m} = \hat{K}_{1,m} \left[\frac{\hat{K}_{k,m}}{\hat{K}_{1,m}}\right] = \hat{K}_{1,m} \left[\frac{K_{k,m}}{K_{1,m}}\right].$$

Similarly, substituting for $r_m$ in terms of $\hat{r}_m$, $\sigma_m$ in terms of $\hat{\sigma}_m$, and $M_m$ in terms of $\hat{M}_m$ in
Eq. (A.15) yields the following for the total diffusible gas pressure in bubbles of the m^th
bubble size group:

$$P_{b_{T,m}}(t) = P_{amb}-P_\infty + \frac{2\hat{\sigma}_m}{\hat{r}_m(t)} + \hat{M}_m \hat{r}^3_m(t).  \tag{A.43}$$

The components of $P_{b_{T,m}}(t)$; i.e., the individual partial pressures of the diffusible gases in

the bubble, $P_{b_{k,m}}$, k = 1, 2, ..., $N_g$; are determined as part of the numerical integration of
Eq. (A.42) described in Appendix B [see Eq. (B.41)].

Finally, from Eq. (A.16) the average tissue tension of the k^th diffusible gas is given by

$$\frac{dp_{t_k}}{dt} + q_k(t)p_{t_k} = q_k(t)p_{a_k} - \sum_{m}^{N_{bs}} \hat{G}_{k,m} \frac{d\hat{x}_{k,m}(t)}{dt}; \quad k = 1, 2, ..., N_g, \tag{A.44}$$

where $\hat{G}_{k,m} = \left(\frac{4\pi}{3}\right)\frac{n_{b_m}}{\alpha_{t_k}\hat{V}_t}$ with $\hat{V}_t = V_t\Lambda^3$, and

$$\hat{x}_{k,m}(t) = P_{b_{k,m}}\hat{r}^3_m(t).$$

Neither Eq. (A.42), (A.43), or (A.44), which comprise the bubble dynamics equations for
the scaled system, contain the scale factor $\Lambda$. The scale factor can therefore be
chosen arbitrarily. A single solution of the equations with a given value of $\Lambda$ is
analytically related to all other solutions of the equations obtained with any other value
of $\Lambda$. Scaling non-dimensionalizes the bubble volume for application in the hazard
function of survival models.

In terms of the dimensionless scaled bubble volumes in the m^th size group,

A-14
---
$$\hat{V}_{bm} = \frac{4\pi}{3}\hat{r}_m^3 = \frac{4\pi}{3}(\Lambda r_m)^3 = \Lambda^3 V_{bm}.$$

Eq. (A.12) for total bubble volume is then expressed in scaled form as

$$\hat{V}_g(t) = \sum_{m}^{N_{bs}} \Lambda^3V_{bm}(t)n_{bm} = \sum_{m}^{N_{bs}}\hat{V}_{bm}(t)n_{bm}.$$ (A.45)

With the single time-dependent bubble size approximation in Eq. (A.40), m=1, and $r_{min}$,

$r_{min}^0$, $\sigma_c$, $\beta^o$, and $\beta_f$ in Eqs. (A.27) through (A.37) of the bubble nucleation model then

scale with the compartmental $\Lambda$; $\hat{r}_{min} = \Lambda r_{min}$, $\hat{r}_{min}^0 = \Lambda r_{min}^0$, $\hat{\sigma}_c = \Lambda \sigma_c$, $\hat{\beta}^o = \Lambda \beta^o$, and $\hat{\beta}_f = \Lambda \beta_f$.

Eq. (A.45) then becomes

$$\hat{V}_g(t) = \hat{V}_b(t)n_b(t).$$ (A.46)

Eqs. (A.42), (A.41), (A.44), and (A.45) or (A.46) describe the scaled 3RUT-MB model in its final form.

## 8.5 Model Operation and Initial Values

The tissue tensions of the inert gases at profile start were assumed equal to the corresponding arterial tensions in the saturation steady state at ground level pressure breathing air.

Unlike the tissue tensions of the inert gases, the tissue O₂ tension ($p_{tO_2^0}$) is not equal to the arterial O₂ tension in the saturation steady state because of the metabolic consumption of O₂ in the tissue ($\dot{V}_{O_2} > 0$). The tissue O₂ tension ($p_{tO_2^0}$) for initiating the calculations at profile start was calculated assuming $p_{tO_2^0} = p_{\bar{v}O_2^0}$ and using the steady state O₂ mass balance relationship between blood flow and O₂ consumption given by the Fick principle:

$$\dot{Q}(C_{a\bar{v}O_2^0}) = \dot{Q}(C_{aO_2^0} - C_{\bar{v}O_2^0}) = \dot{V}_{O_2^0}.$$ (A.47)

Solving Eq. (A.47) for $C_{\bar{v}O_2^0}$ yields

$$C_{\bar{v}O_2^0} = C_{aO_2^0} - \frac{\dot{V}_{O_2^0}}{\dot{Q}}.$$ (A.48)

A-15
---
The partial pressure p̄vO₂ corresponding to C̄vO₂⁰ was then determined using the secant method to numerically invert the blood O₂ content versus partial pressure curve, Eq. (A.22), at C̄vO₂⁰.

Exercise-induced changes in compartmental V̇O₂(t) and consequent changes in compartmental blood flow, Q̇, were assumed to manifest instantaneously.

Present models incorporated the simplification described in Sections 11.3.1 and 12.2.2, wherein multiple bubbles in a given tissue compartment are considered to evolve in parallel at the same size, requiring consideration of only a single bubble size group. The initial nucleus size of the bubble was specified by Eq. (A.37), which includes an accounting for the effects of O₂ prebreathe and exercise on bubble nucleation.

The initial pressure of the kth diffusible gas in the bubble (Pᵇₖ,₀) was computed assuming that the ratio of the gas pressure to the total bubble pressure is the same as the ratio of the tissue tension of the gas to the total tissue tension at the moment of recruitment; i.e.,

$$\frac{P_{b,k,0}}{\sum_k P_{b,k,0}} = \frac{p_{t,k,0}}{\sum_k p_{t,k,0}} = c_{r_k} \text{ when } V_b = V_{r0},$$

(A.49)

where $\sum_{k=1}^{N_g} P_{b,k,0} = P'_{amb_0} + \frac{2\sigma}{r_0} + Mr_0^3$,

and P'ₐₘb₀ is the ambient hydrostatic pressure when the first bubble is nucleated, less pressures exerted by the infinitely diffusible gases (CO₂ and water vapor; O₂ pressure is not subtracted when treated as a finitely diffusible gas). Nominal values for tissue CO₂ pressure and water vapor pressure at body temperature are 45 and 47 mm-Hg, respectively. The total correction for CO₂ and water vapor was thus 45 + 47 = 92 mm-Hg.

From Eq. (A.49), the initial bubble pressure of the kth diffusible gas is

$$P_{b_k,0} = c_{r_k} \sum_k P_{b_k,0}$$

(A.50)

and the scaled bubble gas content is

$$\hat{x}_{k,0} = P_{b_k,0} \hat{r}_0^3.$$

(A.51)

A-16
---
Before bubble nucleation (and after complete bubble resolution), when compartmental
$$p_{t_{k,n}} \leq P_{b_{k,n}}$$ for all diffusible gases, the bubble was assumed to remain stable at its
nucleus size with $$\delta r_n = 0$$.

The coupled bubble radius and bubble pressure equations were solved with the
piecewise analytic solution derived in Appendix B. The integration step size, dt, for each
time step was reduced or increased as a function of the rate of bubble radius change,
$$\frac{dr}{dt}$$, in the previous step according to:

$$dt = (dt_{max} - dt_{min}) \exp[-dt_k (\frac{dr}{dt})] + dt_{min},\qquad\qquad (A.52)$$

where $$dt_{max}$$ and $$dt_{min}$$ are the largest and smallest allowed time step sizes, respectively,
and $$dt_k$$ is a decay constant.

Numerical instabilities in the solution were avoided by comparing the sum of the bubble
diffusible gas partial pressures to the sum of the tissue diffusible gas tensions in each
iteration of the recursive solution process. If the bubble pressure sum exceeded the
tissue tension sum with positive dr/dt at any point in an isobaric stage, the stage was
restarted with the integration step size reduced by a factor of ten.

A-17
---
# 9. Appendix B. Piece-Wise Analytic Approximation of the Three-Region Unstirred Tissue Multiple Bubble (3RUT-MB) Model of Tissue Gas and Bubble Dynamics

The three-region, unstirred-tissue, multiple-bubble (3RUT-MB) model of gas and bubble dynamics [36] comprises two sets of coupled nonlinear differential equations; one for the rates of change of volumes and pressures of gas bubbles in a hypothetical tissue compartment, and a second for the rates of change of dissolved gas tensions in the compartment. These equations must be solved simultaneously by numerical methods. A numerical piece-wise analytic approximation of the coupled equations was developed for efficient and stable solution of the equations.

To simplify the notation in the development, we begin by considering the evolution of one or more bubbles of the same size under the influence of a single diffusible gas. We then advance to consider the evolution of multiple bubbles of different sizes under the influence of a single diffusible gas and conclude by considering the evolution of multiple bubbles of different sizes under the influence of multiple diffusible gases.

## 9.1 Single Diffusible Gas

### 9.1.1 Multiple Bubbles of Same Size

#### 9.1.1.1 Changes in Bubble Radius and Bubble Gas Pressure

The changes in bubble radius, r, as well as the bubble pressures exerted by the diffusible gases that participate in the evolution of a bubble are determined from the Fick equation, which is expressed for a single diffusible gas in the 3RUT-MB model as

$$\frac{d}{dt}(P_bV_b) = KA_b(\Lambda + \frac{1}{r})(p_t - P_b),\tag{B.1}$$

where $(\Lambda + \frac{1}{r})(p_t - P_b)$ is the pressure gradient of the diffusible gas at the bubble surface, $A_b$ is the bubble surface area (= $4\pi r^2$), and K, $p_t$, $P_b$, and $\Lambda$ are defined as before. With the dimensionless scaled bubble radius $\hat{r} = \Lambda r$, $V_b = \frac{4\pi}{3}\Lambda^3\hat{r}^3$ and $A_b = 4\pi\Lambda^2\hat{r}^2$.

Substituting for r, $V_b$, and $A_b$ in terms of $\hat{r}$ in Eq. (B.1), we obtain

$$\frac{4\pi}{3}\Lambda^3\frac{d}{dt}(P_b\hat{r}^3) = K(4\pi)\hat{r}^2\Lambda^2(\Lambda + \frac{\Lambda}{\hat{r}})(p_t - P_b),$$

B-1
---

$$\frac{d}{dt}(P_b\hat{r}^3) = 3\Lambda^2K(\hat{r}^2 + \hat{r})(p_t - P_b) ,$$

$$\frac{d}{dt}(P_b\hat{r}^3) + 3\Lambda^2K\left(\hat{r}^2 + \hat{r}\right)P_b = 3\Lambda^2K\left(\hat{r}^2 + \hat{r}\right)p_t ,$$

$$\frac{d}{dt}(P_b\hat{r}^3) + \tilde{K}\left(\frac{1}{\hat{r}} + \frac{1}{\hat{r}^2}\right)(P_b\hat{r}^3) = \tilde{K}\left(\hat{r}^2 + \hat{r}\right)p_t , \tag{B.2}$$

where $\tilde{K} = 3\Lambda^2K$ is the scaled permeability, which has a dimension 1/time.

With $\hat{x} = P_b\hat{r}^3$, $f(t) = \tilde{K}\left(\frac{1}{\hat{r}} + \frac{1}{\hat{r}^2}\right)$, $g(t) = \tilde{K}(\hat{r}^2 + \hat{r})p_t$, and bubble radius $\hat{r}$ and tissue gas tension $p_t$ treated as explicit functions of time, Eq. (B.2) becomes

$$\frac{d\hat{x}}{dt} + f(t)\hat{x} = g(t) , \tag{B.3}$$

which is a linear differential equation in $\hat{x}$ with variable coefficients. Eq. (B.3) is solved using the integrating factor method to obtain the following recursive relationship (See Section 9.3):

$$\hat{x}_{n+1} = \hat{x}_n + [(g_n + g_{n+1}) - (f_n + f_{n+1})\hat{x}_n]\frac{\Delta t_n}{2} + \left[(f_n + f_{n+1})^2\hat{x}_n\right]\frac{\Delta t_n^2}{8}$$

$$- \left[3(g_nf_n + g_{n+1}f_{n+1}) + (g_nf_{n+1} - g_{n+1}f_n)\right]\frac{\Delta t_n^2}{12}, \quad n = 0,1,2,3,... \tag{B.4}$$

where $\hat{x}_n$, $f_n$, and $g_n$ are respectively the values of $\hat{x}(t)$, $f(t)$, and $g(t)$ at time $t_n$, and $\hat{x}_{n+1}$, $f_{n+1}$, and $g_{n+1}$ are the corresponding values at time $t_{n+1}$. The step size, $\Delta t_n = t_{n+1} - t_n$, is subscripted to indicate that it may be assigned a different value for each integration step.

The coefficients on the right side of Eq. (B.4) are now evaluated using the definitions of $f(t)$ and $g(t)$ and denoting $\hat{r}(t)$ at times $t_n$ and $t_{n+1}$ by $\hat{r}_n$ and $\hat{r}_{n+1}$, respectively, and the change $(\hat{r}_{n+1} - \hat{r}_n)$ by $\Delta\hat{r}_n$. Defining the tissue tension $p_{t_n}$ as the value of $p_t$ at time $t_n$ and assuming that $p_{t_n}$ stays steady in the interval $[t_n, t_{n+1}]$, consistent with the quasi-static approximation on which the 3RUT-MB model is based, we have the following for the coefficient $(g_n + g_{n+1})$:

B-2
---
$$\frac{g_n + g_{n+1}}{Kp_{t_n}} = \hat{r}_n^2 + \hat{r}_n + \hat{r}_{n+1}^2 + \hat{r}_{n+1}$$

$$= \hat{r}_n^2 + \hat{r}_n + (\hat{r}_n + \Delta\hat{r}_n)^2 + (\hat{r}_n + \Delta\hat{r}_n)$$

$$= \hat{r}_n^2 + \hat{r}_n + (\hat{r}_n^2 + 2\hat{r}_n \Delta\hat{r}_n + \Delta\hat{r}_n^2) + (\hat{r}_n + \Delta\hat{r}_n)$$

$$= 2\left(\hat{r}_n^2 + \hat{r}_n\right) + (2\hat{r}_n + 1)\Delta\hat{r}_n + \Delta\hat{r}_n^2$$

Considering $\Delta\hat{r}_n$ to be sufficiently small so that terms containing powers of $\Delta\hat{r}_n$ may be ignored, we have

$$\frac{g_n + g_{n+1}}{Kp_{t_n}} = 2\hat{r}_n(\hat{r}_n + 1) + \hat{r}_n(2\hat{r}_n + 1)\delta\hat{r}_n,\tag{B.5a}$$

where $\delta\hat{r}_n = \frac{\Delta\hat{r}_n}{\hat{r}_n}$ is the fractional change in bubble radius in the n$^{th}$ integration step.

Now, for the coefficient $(f_n + f_{n+1})$, we have

$$\frac{f_n + f_{n+1}}{K} = \frac{1}{\hat{r}_n^2} + \frac{1}{\hat{r}_n} + \frac{1}{\hat{r}_{n+1}^2} + \frac{1}{\hat{r}_{n+1}}$$

$$= \frac{1}{\hat{r}_n^2} + \frac{1}{\hat{r}_n} + \frac{1}{(\hat{r}_n + \Delta\hat{r}_n)^2} + \frac{1}{(\hat{r}_n + \Delta\hat{r}_n)}$$

$$= \frac{1}{\hat{r}_n^2} + \frac{1}{\hat{r}_n} + \frac{1}{\hat{r}_n^2}(1+\delta\hat{r}_n)^{-2} + \frac{1}{\hat{r}_n}(1+\delta\hat{r}_n)^{-1}$$

The $(1+\delta\hat{r}_n)^{-2}$ and $(1+\delta\hat{r}_n)^{-1}$ terms in the above equation are of general form, $(1+x)^n$,

which is expanded about $x=0$ and approximated to first order by $(1+x)^n \cong (1+nx)$.

Substituting the first order approximations for the $(1+\delta\hat{r}_n)^{-2}$ and $(1+\delta\hat{r}_n)^{-1}$ terms yields

B-3
---

$$\frac{f_n + f_{n+1}}{K} \approx \frac{1}{\hat{r}_n^2} + \frac{1}{\hat{r}_n} + \frac{1}{\hat{r}_n^2}(1-2\delta\hat{r}_n) + \frac{1}{\hat{r}_n}(1-\delta\hat{r}_n)$$

$$= \frac{2}{\hat{r}_n^2} + \frac{2}{\hat{r}_n} - \left[\frac{2}{\hat{r}_n^2} + \frac{1}{\hat{r}_n}\right]\delta\hat{r}_n$$

$$= \frac{2(\hat{r}_n + 1)}{\hat{r}_n^2} - \left[\frac{\hat{r}_n + 2}{\hat{r}_n^2}\right]\delta\hat{r}_n$$

$$= \frac{1}{\hat{r}_n^2}[2(\hat{r}_n + 1) - (\hat{r}_n + 2)\delta\hat{r}_n].  \tag{B.5b}$$

The following expression for the coefficient associated with $\Delta t_n/2$ on the right side of Eq. (B.4) is then obtained from Eqs. (B.5a) and (B.5b) and the definition of $\hat{x}_n$:

$$(g_n + g_{n+1}) - (f_n + f_{n+1})\hat{x}_n$$

$$= [2\hat{r}_n(\hat{r}_n + 1) + \hat{r}_n(2\hat{r}_n + 1)\delta\hat{r}_n]Kp_{t_n} - \left[\frac{1}{\hat{r}_n^2}[2(\hat{r}_n + 1) - (\hat{r}_n + 2)\delta\hat{r}_n]K\right]P_{b_n}\hat{r}_n^3$$

$$= [2\hat{r}_n(\hat{r}_n + 1) + \hat{r}_n(2\hat{r}_n + 1)\delta\hat{r}_n]Kp_{t_n} - \hat{r}_n[2(\hat{r}_n + 1) - (\hat{r}_n + 2)\delta\hat{r}_n]KP_{b_n}$$

$$= 2\hat{r}_n(\hat{r}_n + 1)K(p_{t_n} - P_{b_n}) + [\hat{r}_n(2\hat{r}_n + 1)Kp_{t_n} + \hat{r}_n(\hat{r}_n + 2)KP_{b_n}]\delta\hat{r}_n.  \tag{B.6}$$

The coefficient associated with $\Delta t_n^2/8$ on the right side of Eq. (B.4) is

$$(f_n + f_{n+1})^2\hat{x}_n = \left[\frac{1}{\hat{r}_n^2}[2(\hat{r}_n + 1) - (\hat{r}_n + 2)\delta\hat{r}_n]K\right]^2P_{b_n}\hat{r}_n^3$$

$$\approx \frac{1}{\hat{r}_n^4}[4(\hat{r}_n + 1)^2 - 4(\hat{r}_n + 1)(\hat{r}_n + 2)\delta\hat{r}_n]K^2P_{b_n}$$

$$= \left[\frac{4(\hat{r}_n + 1)^2}{\hat{r}_n} - \frac{4(\hat{r}_n + 1)(\hat{r}_n + 2)}{\hat{r}_n}\delta\hat{r}_n\right]K^2P_{b_n}.  \tag{B.7}$$

Now, for the coefficients associated with the last term on the right side of Eq. (B.4), we have

B-4
---

$$g_n f_n + g_{n+1} f_{n+1} = \left[\left(\hat{r}_n^2 + \hat{r}_n\right)\left(\frac{1}{\hat{r}_n^2} + \frac{1}{\hat{r}_n}\right) + \left(\hat{r}_{n+1}^2 + \hat{r}_{n+1}\right)\left(\frac{1}{\hat{r}_{n+1}^2} + \frac{1}{\hat{r}_{n+1}}\right)\right] \hat{K}^2 p_{t_n}$$

$$= \left[1 + \hat{r}_n + \frac{1}{\hat{r}_n} + 1 + 1 + \hat{r}_{n+1} + \frac{1}{\hat{r}_{n+1}} + 1\right] \hat{K}^2 p_{t_n}$$

$$= \left[4 + \hat{r}_n + \frac{1}{\hat{r}_n} + (\hat{r}_n + \Delta\hat{r}_n) + \frac{1}{(\hat{r}_n + \Delta\hat{r}_n)}\right] \hat{K}^2 p_{t_n}$$

$$= \left[4 + \hat{r}_n + \frac{1}{\hat{r}_n} + \hat{r}_n(1 + \delta\hat{r}_n) + \frac{(1 + \delta\hat{r}_n)^{-1}}{\hat{r}_n}\right] \hat{K}^2 p_{t_n}$$

$$\simeq \left[4 + \hat{r}_n + \frac{1}{\hat{r}_n} + \hat{r}_n(1 + \delta\hat{r}_n) + \frac{1 - \delta\hat{r}_n}{\hat{r}_n}\right] \hat{K}^2 p_{t_n}$$

$$= \left[4 + 2\hat{r}_n + \frac{2}{\hat{r}_n} + \hat{r}_n\delta\hat{r}_n - \frac{\delta\hat{r}_n}{\hat{r}_n}\right] \hat{K}^2 p_{t_n}$$

$$= \left[\frac{2(2\hat{r}_n + \hat{r}_n^2 + 1)}{\hat{r}_n} + \left(\hat{r}_n - \frac{1}{\hat{r}_n}\right)\delta\hat{r}_n\right] \hat{K}^2 p_{t_n}$$

$$= \left[\frac{2(\hat{r}_n + 1)^2}{\hat{r}_n} + \frac{\hat{r}_n^2 - 1}{\hat{r}_n}\delta\hat{r}_n\right] \hat{K}^2 p_{t_n},\quad (B.8a)$$

and

B-5
---

$$g_nf_{n+1} - g_{n+1}f_n = \left(\hat{r}_n^2 + \hat{r}_n \left[\frac{1}{\hat{r}_{n+1}^2} + \frac{1}{\hat{r}_{n-1}}\right]\right)K^2p_{t_n} - \left(\hat{r}_{n+1}^2 + \hat{r}_{n+1}\left[\frac{1}{\hat{r}_n^2} + \frac{1}{\hat{r}_n}\right]\right)K^2p_{t_n}$$

$$= \left[\left(\frac{\hat{r}_n^2}{\hat{r}_{n+1}^2} + \frac{\hat{r}_n}{\hat{r}_{n+1}^2} + \frac{\hat{r}_n^2}{\hat{r}_{n+1}} + \frac{\hat{r}_n}{\hat{r}_{n+1}}\right) - \left(\frac{\hat{r}_{n+1}^2}{\hat{r}_n^2} + \frac{\hat{r}_{n+1}}{\hat{r}_n^2} + \frac{\hat{r}_{n+1}^2}{\hat{r}_n} + \frac{\hat{r}_{n+1}}{\hat{r}_n}\right)\right]K^2p_{t_n}$$

$$= \left[\left(\frac{\hat{r}_n^2}{(\hat{r}_n + \Delta\hat{r}_n)^2} + \frac{\hat{r}_n}{(\hat{r}_n + \Delta\hat{r}_n)^2} + \frac{\hat{r}_n^2}{(\hat{r}_n + \Delta\hat{r}_n)} + \frac{\hat{r}_n}{(\hat{r}_n + \Delta\hat{r}_n)}\right) - \left(\frac{(\hat{r}_n + \Delta\hat{r}_n)^2}{\hat{r}_n^2} + \frac{(\hat{r}_n + \Delta\hat{r}_n)}{\hat{r}_n^2} + \frac{(\hat{r}_n + \Delta\hat{r}_n)^2}{\hat{r}_n} + \frac{(\hat{r}_n + \Delta\hat{r}_n)}{\hat{r}_n}\right)\right]K^2p_{t_n}$$

$$= \left[\left((1+\delta\hat{r}_n)^{-2} + \frac{1}{\hat{r}_n}(1+\delta\hat{r}_n)^{-2} + \hat{r}_n(1-\delta\hat{r}_n)^{-1} + (1+\delta\hat{r}_n)^{-1}\right) - \left((1+\delta\hat{r}_n)^2 + \frac{1}{\hat{r}_n}(1+\delta\hat{r}_n) + \hat{r}_n(1+\delta\hat{r}_n)^2 + (1+\delta\hat{r}_n)\right)\right]K^2p_{t_n}$$

$$\simeq \left[\left((1-2\delta\hat{r}_n) + \frac{1}{\hat{r}_n}(1-2\delta\hat{r}_n) + \hat{r}_n(1+\delta\hat{r}_n) + (1-\delta\hat{r}_n)\right) - \left((1+2\delta\hat{r}_n) + \frac{1}{\hat{r}_n}(1+\delta\hat{r}_n) + \hat{r}_n(1+2\delta\hat{r}_n) + (1+\delta\hat{r}_n)\right)\right]K^2p_{t_n}$$

$$= \left[(-4\delta\hat{r}_n) + \frac{1}{\hat{r}_n}(-3\delta\hat{r}_n) + \hat{r}_n(-3\delta\hat{r}_n) + (-2\delta\hat{r}_n)\right]K^2p_{t_n}$$

$$= \left[-3\left(2 + \frac{1}{\hat{r}_n} + \hat{r}_n\right)\delta\hat{r}_n\right]K^2p_{t_n}$$

$$= 3 - \left[\frac{(\hat{r}_n + 1)^2}{\hat{r}_n}\delta\hat{r}_n\right]K^2p_{t_n}. \tag{B.8b}$$

Combining Eqs. (B.8a) and (B.8b), the coefficient associated with the last term on the right side of Eq. (B.4) is

$$3(g_nf_n + g_{n+1}f_{n+1}) + (g_nf_{n+1} - g_{n+1}f_n) = 3\left[\frac{2(\hat{r}_n + 1)^2}{\hat{r}_n} + \frac{\hat{r}_n^2 - 1}{\hat{r}_n}\delta\hat{r}_n\right]K^2p_{t_n} + 3\left[-\frac{(\hat{r}_n + 1)^2}{\hat{r}_n}\delta\hat{r}_n\right]K^2p_{t_n}$$

$$= 3\left[\frac{2(\hat{r}_n + 1)^2}{\hat{r}_n} + \frac{(\hat{r}_n^2 - 1) - (\hat{r}_n + 1)^2}{\hat{r}_n}\delta\hat{r}_n\right]K^2p_{t_n}$$

B-6
---
$$= 3 \left[\frac{2(\hat{r}_n +1)^2}{\hat{r}_n} - \frac{2(\hat{r}_n +1)}{\hat{r}_n} \delta\hat{r}_n\right] K^2 p_{t_n}.$$
(B.9)

The expressions for the coefficients given by Eqs. (B.6), (B.7), and (B.9) are inserted into Eq. (B.4) to obtain

$$\hat{x}_{n+1} = \hat{x}_n + \left[2\hat{r}_n(\hat{r}_n +1)K(p_{t_n} - P_{b_n}) + \{\hat{r}_n(2\hat{r}_n +1)Kp_{t_n} + \hat{r}_n(\hat{r}_n +2)KP_{b_n}\}\delta\hat{r}_n\right]\frac{\Delta t_n}{2}$$

$$+ \left[\frac{4(\hat{r}_n +1)^2}{\hat{r}_n} - \frac{4(\hat{r}_n +1)(\hat{r}_n +2)}{\hat{r}_n} \delta\hat{r}_n\right] K^2P_{b_n} \frac{\Delta t_n^2}{8}$$

$$- 3 \left[\frac{2(\hat{r}_n +1)^2}{\hat{r}_n} - \frac{2(\hat{r}_n +1)}{\hat{r}_n} \delta\hat{r}_n\right] K^2p_{t_n} \frac{\Delta t_n^2}{12}$$

$$=\hat{x}_n +L_{0_n} +L_{1_n} \delta\hat{r}_n,$$
(B.10)

where

$L_{0_n} =$ sum of the terms independent of $\delta\hat{r}_n$ in the expression for $\hat{x}_{n+1}$

$$= \left[2\hat{r}_n(\hat{r}_n +1)K(p_{t_n} - P_{b_n})\right]\frac{\Delta t_n}{2} + \frac{4(\hat{r}_n +1)^2}{\hat{r}_n} K^2P_{b_n} \frac{\Delta t_n^2}{8} - 3\frac{2(\hat{r}_n +1)^2}{\hat{r}_n} K^2p_{t_n} \frac{\Delta t_n^2}{12}$$

$$= \hat{r}_n(\hat{r}_n +1)K(p_{t_n} - P_{b_n})\Delta t_n + \frac{(\hat{r}_n +1)^2}{\hat{r}_n} K^2P_{b_n} \frac{\Delta t_n^2}{2} - \frac{(\hat{r}_n +1)^2}{\hat{r}_n} K^2p_{t_n} \frac{\Delta t_n^2}{2}$$

$$= \hat{r}_n(\hat{r}_n +1)K(p_{t_n} - P_{b_n})\Delta t_n - \frac{(\hat{r}_n +1)^2}{\hat{r}_n} \frac{\Delta t_n^2}{2} K^2(p_{t_n} - P_{b_n})$$

$$= \left\hat{r}_n(\hat{r}_n + 1)K\Delta t_n - \frac{1}{2} \frac{(\hat{r}_n +1)^2}{\hat{r}_n} K^2\Delta t_n^2\right,$$
(B.11a)

and $L_{1_n} =$ sum of the terms with $\delta\hat{r}_n$ as multiplier in the expression for $\hat{x}_{n+1}$

B-7
---

$$= \hat{r}_n [(2\hat{r}_n + 1)Kp_{t_n} + \hat{r}_n (\hat{r}_n + 2)KP_{b_n}] \frac{\Delta t_n}{2} - \frac{4(\hat{r}_n + 1)(\hat{r}_n + 2)}{r_n} K^2P_{b_n} \frac{\Delta t_n^2}{8}$$

$$+ 3\frac{2(\hat{r}_n + 1)}{\hat{r}_n} K^2p_{t_n} \frac{\Delta t_n^2}{12}$$

$$= \hat{r}_n [(2\hat{r}_n + 1)Kp_{t_n} + (\hat{r}_n + 2)KP_{b_n}] \frac{\Delta t_n}{2} - \frac{(\hat{r}_n + 1)(\hat{r}_n + 2)}{\hat{r}_n} K^2P_{b_n} \frac{\Delta t_n^2}{2}$$

$$+ \frac{\hat{r}_n + 1}{\hat{r}_n} K^2p_{t_n} \frac{\Delta t_n^2}{2}$$

$$= \hat{r}_n [(2\hat{r}_n + 1)p_{t_n} + (\hat{r}_n + 2)P_{b_n}] K\frac{\Delta t_n}{2} + \frac{\hat{r}_n + 1}{\hat{r}_n} [p_{t_n} - (\hat{r}_n + 2)P_{b_n}] K^2 \frac{\Delta t_n^2}{2}. \tag{B.11b}$$

Recall $\hat{x} = P_b \hat{r}^3$. Therefore, $\hat{x}_n = P_{b_n} \hat{r}_n^3$ and $\hat{x}_{n+1} = P_{b_{n+1}} \hat{r}_{n+1}^3$. Substituting for $\hat{x}_n$ and $\hat{x}_{n+1}$ in Eq. (B.10), we obtain

$$P_{b_{n+1}} \hat{r}_{n+1}^3 = P_{b_n} \hat{r}_n^3 + L_{0_n} + L_{1_n} \delta \hat{r}_n,$$

from which

$$P_{b_{n+1}} = P_{b_n} \frac{\hat{r}_n^3}{\hat{r}_{n+1}^3} + \frac{L_{0_n} + L_{1_n} \delta \hat{r}_n}{\hat{r}_{n+1}^3}$$

$$= P_{b_n} \frac{\hat{r}_n^3}{\hat{r}_n^3(1 + \delta \hat{r}_n)^3} + \frac{L_{0_n} + L_{1_n} \delta \hat{r}_n}{\hat{r}_n^3(1 + \delta \hat{r}_n)^3}$$

$$= P_{b_n} (1 + \delta \hat{r}_n)^{-3} + \frac{1}{\hat{r}_n^3} [L_{0_n} + L_{1_n} \delta \hat{r}_n] (1 + \delta \hat{r}_n)^{-3}$$

$$\cong P_{b_n} (1 - 3\delta \hat{r}_n) + \frac{1}{\hat{r}_n^3} [L_{0_n} + L_{1_n} \delta \hat{r}_n] (1 - 3\delta \hat{r}_n).$$

Neglect of terms of order ≥ 2 yields

$$P_{b_{n+1}} = P_{b_n} (1 - 3\delta \hat{r}_n) + \frac{L_{0_n}}{\hat{r}_n^3} (1 - 3\delta \hat{r}_n) + \frac{L_{1_n} \delta \hat{r}_n}{\hat{r}_n^3}$$

B-8
---

$$= \left(Pb_n + \frac{L0_n}{r_n^3}\right) - \left[3Pb_n + 3\frac{L0_n}{r_n^3} - \frac{L1_n}{r_n^3}\right]\delta r_n$$

$$= \left(Pb_n + \frac{L0_n}{r_n^3}\right) - \left[\left(3Pb_n + \frac{L0_n}{r_n^3}\right) - \frac{L1_n}{r_n^3}\right]\delta r_n$$

$$= A_n - (3A_n - B_n)\delta r_n \tag{B.12}$$

where

$$A_n = Pb_n + \frac{L0_n}{r_n^3} \tag{B.12a}$$

and

$$B_n = \frac{L1_n}{r_n^3}. \tag{B.12b}$$

Eqs. (B.12a) and (B.11a) are combined to obtain the following expressions for A_n:

$$A_n = Pb_n + \frac{L0_n}{r_n^3}$$

$$= Pb_n + \frac{1}{r_n^3}[r_n(r_n + 1)\Delta t_n]K[p_{t_n} - Pb_n] - \frac{1}{2}\frac{1}{r_n^3}\left(\frac{(r_n + 1)^2}{r_n}\Delta t_n^2\right)K^2[p_{t_n} - Pb_n]$$

$$= Pb_n + \left(\frac{r_n + 1}{r_n^2}\Delta t_n K\right)[p_{t_n} - Pb_n] - \frac{1}{2}\left(\frac{(r_n + 1)^2}{r_n^4}\Delta t_n^2 K^2\right)[p_{t_n} - Pb_n]$$

$$= Pb_n + \left(\frac{r_n + 1}{r_n^2}\Delta t_n K\right)[p_{t_n} - Pb_n] - \frac{1}{2}\left(\frac{r_n + 1}{r_n^2}\Delta t_n K\right)^2[p_{t_n} - Pb_n]$$

$$= Pb_n + a_n\left(1 - \frac{a_n}{2}\right)(p_{t_n} - Pb_n), \tag{B.13a}$$

where $a_n = \left(\frac{r_n + 1}{r_n^2}\Delta t_n\right)K$.

Likewise, Eqs. (B.12b) and (B.11b) are combined to express B_n as follows:

$$B_n = \frac{L1_n}{r_n^3} = \frac{1}{r_n^3}\left[r_n\{(2r_n + 1)p_{t_n} + (r_n + 2)Pb_n\}K\frac{\Delta t_n}{2} + \frac{r_n + 1}{r_n}\{p_{t_n} - (r_n + 2)Pb_n\}K^2\frac{\Delta t_n^2}{2}\right]$$

B-9
---

$$
\begin{aligned}
&= \frac{1}{2}\left[\left(\frac{2\hat{r}_n+1}{\hat{r}_n^2}\Delta t_n\hat{K}\right)pt_n + \left(\frac{\hat{r}_n+2}{\hat{r}_n^2}\Delta t_n\hat{K}\right)Pb_n\right. \\
&\quad \left.+ \left(\frac{\hat{r}_n+1}{\hat{r}_n^2}\Delta t_n\hat{K}\right)\left\{\left(\frac{1}{\hat{r}_n^2}\Delta t_n\hat{K}\right)pt_n - \left(\frac{\hat{r}_n+2}{\hat{r}_n^2}\Delta t_n\hat{K}\right)Pb_n\right\}\right] \\[10pt]
&= \frac{1}{2}\left[\left(\frac{2(\hat{r}_n+1)}{\hat{r}_n^2}\Delta t_n\hat{K} - \frac{1}{\hat{r}_n^2}\Delta t_n\hat{K}\right)pt_n + \left(\frac{\hat{r}_n+1}{\hat{r}_n^2}\Delta t_n\hat{K} + \frac{\Delta t_n}{\hat{r}_n^2}\hat{K}\right)Pb_n\right. \\
&\quad \left.+ \left(\frac{\hat{r}_n+1}{\hat{r}_n^2}\Delta t_n\hat{K}\right)\left(\frac{\Delta t_n}{\hat{r}_n^2}\hat{K}pt_n - \left(\frac{\hat{r}_n+1}{\hat{r}_n^2}\Delta t_n\hat{K} + \frac{\Delta t_n}{\hat{r}_n^2}\hat{K}\right)Pb_n\right)\right] \\[10pt]
&= \frac{1}{2}[(2a_n - b_n)pt_n + (a_n + b_n)Pb_n + a_n\{b_npt_n - (a_n + b_n)Pb_n\}] \\[10pt]
&= \frac{1}{2}[2a_n - b_n + a_nb_n)pt_n + (a_n + b_n)(1 - a_n)Pb_n], \quad (B.13b)
\end{aligned}
$$

where $b_n = \frac{\Delta t_n}{\hat{r}_n^2}\hat{K}$ and $a_n = \frac{\hat{r}_n+1}{\hat{r}_n^2}\Delta t_n\hat{K} = (\hat{r}_n+1)b_n$.

The bubble diffusible gas pressure is given in terms of the scaled radius $\hat{r}_{n+1}$ by Eq. (A.43):

$$
P_{b_{n+1}} = P'_{amb_{n+1}} + \frac{2\sigma}{\hat{r}_{n+1}} + M\hat{r}_{n+1}^3, \quad (B.14)
$$

where $P'_{amb} = (P_{amb} - P_\infty)$ is the ambient hydrostatic pressure corrected for the pressures of the infinitely-diffusible gases in the system (e.g., $P_\infty = P_{CO_2} + P_{H_2O}$). Substituting $\hat{r}_{n+1} = \hat{r}_n(1 + \delta\hat{r}_n)$ in Eq. (B.14), we obtain

$$
\begin{aligned}
P_{b_{n+1}} &= P'_{amb_{n+1}} + \frac{2\sigma}{\hat{r}_n(1 + \delta\hat{r}_n)} + M\hat{r}_n^3(1 + \delta\hat{r}_n)^3 \\[10pt]
&= P'_{amb_{n+1}} + \frac{2\sigma}{\hat{r}_n}(1 + \delta\hat{r}_n)^{-1} + M\hat{r}_n^3(1 + \delta\hat{r}_n)^3.
\end{aligned}
$$

Substituting the first order approximations for $(1+\delta\hat{r}_n)^{-1}$ and $(1+\delta\hat{r}_n)^3$ about $\delta\hat{r}_n = 0$ yields

B-10
---

$$P_{b_{n+1}} \cong P'_{amb_{n+1}} + \frac{2\sigma}{\hat{r}_n}(1-\delta\hat{r}_n) + M\hat{r}_n^3(1+3\delta\hat{r}_n)$$

$$= \left[P'_{amb_{n+1}} + \frac{2\sigma}{\hat{r}_n} + M\hat{r}_n^3\right] - \left[\frac{2\sigma}{\hat{r}_n} - 3M\hat{r}_n^3\right]\delta\hat{r}_n. \tag{B.15}$$

The final equation for determining $\delta\hat{r}_n$ is obtained by equating $P_{b_{n+1}}$ given by Eqs. (B.12) and (B.15);

$$A_n - (3A_n - B_n)\delta\hat{r}_n = \left[P'_{amb_{n+1}} + \frac{2\sigma}{\hat{r}_n} + M\hat{r}_n^3\right] - \left[\frac{2\sigma}{\hat{r}_n} - 3M\hat{r}_n^3\right]\delta\hat{r}_n; \tag{B.16}$$

and rearranging terms to yield

$$\left[(3A_n - B_n) - \left(\frac{2\sigma}{\hat{r}_n} - 3M\hat{r}_n^3\right)\right]\delta\hat{r}_n - \left[A_n - \left(P'_{amb_{n+1}} + \frac{2\sigma}{\hat{r}_n} + M\hat{r}_n^3\right)\right] = 0. \tag{B.17}$$

The fractional change in bubble radius at the n^th integration step is then given by solving Eq. (B.17) for $\delta\hat{r}_n$ to obtain:

$$\delta\hat{r}_n = \frac{A_n - \left(P'_{amb_{n+1}} + \frac{2\sigma}{\hat{r}_n} + M\hat{r}_n^3\right)}{(3A_n - B_n) - \left(\frac{2\sigma}{\hat{r}_n} - 3M\hat{r}_n^3\right)}. \tag{B.18}$$

### 9.1.1.2 Tissue Gas Tension with Time-Dependent Changes in Tissue Blood Flow

With the tissue gas tension $p_{t_n}$ constant in the interval [t_n, t_n+1], consistent with the quasi-static approximation [see Eq. (B.5a)], $p_{t_n}$ is updated to $p_{t_{n+1}}$ at the end of the interval based on calculations that account for gas transfer between blood, tissue, and bubbles during the interval. We use the integrating factor method to obtain a recursion formula for solving Eq. (A.13) for a single diffusible gas and a single bubble size group; i.e., for calculating $p_{t_{n+1}}$ at time t_n+1 given $p_{t_n}$ at time t_n with k=1 and N_bs=1. We first treat the blood flow coefficient q(t) in Eq. (A.13) as a general function of time. We then modify the relation with a specific model for q(t) under exercise conditions.

B-11
---
## 9.1.1.2.1 General Model of Time-Dependent Changes in Blood Flow

We multiply both sides of Eq. (A.13) by the integrating factor exp[I_q(t)], where I_q(t) is the

indefinite integral, $I_q(t) = \int q(t)dt$, and integrate between t_n and t_{n+1}:

$$p_t(t)exp[I_q(t)]_{t_n}^{t_{n+1}} = \int_{t_n}^{t_{n+1}} q(t)p_a(t)exp[I_q(t)]dt - \int_{t_n}^{t_{n+1}} \hat{G}S_{x_n}exp[I_q(t)]dt,$$ (B.19)

where $\hat{G} = (\frac{4\pi}{3})(\frac{n_b}{\alpha_t V_t \Lambda^3})$, and $S_{x_n} = \frac{\hat{x}_{n+1} - \hat{x}_n}{\Delta t_n}$ is the rate of gas loss into each of n_b_n

identically sized bubbles in the [t_n, t_{n+1}] integration interval. Evaluating the left side and
expanding the right side of Eq. (B.19) yields

$$p_{t_{n+1}}exp[I_q(t)]_{t=t_{n+1}} - p_{t_n}exp[I_q(t)]_{t=t_n}$$

$$= \int_{t_n}^{t_{n+1}} p_a(t)q(t)exp[I_q(t)]dt - \int_{t_n}^{t_{n+1}} \hat{G}S_{x_n}exp[I_q(t)]dt$$

$$= \int_{t_n}^{t_{n+1}} p_a(t)\frac{d}{dt}\{exp[I_q(t)]\}dt - \int_{t_n}^{t_{n+1}} \hat{G}S_{x_n}exp[I_q(t)]dt.$$

Since $\frac{d}{dt}\{exp[I_q(t)]\} = q(t)exp[I_q(t)]$

$$p_{t_{n+1}} = p_a(t)exp[I_q(t)]_{t_n}^{t_{n+1}} - \int_{t_n}^{t_{n+1}} exp[I_q(t)]\frac{d}{dt}[p_a(t)]dt - \int_{t_n}^{t_{n+1}} \hat{G}S_{x_n}exp[I_q(t)]dt.$$ (B.20)

The first two terms of Eq. (B.20) result from integrating by parts. In the interval [t_n, t_{n+1}],
p_a(t) = p_{a_n} + υ_n(t-t_n), and therefore, $\frac{d}{dt}[p_a(t)] = υ_n$. Expanding the first term on the right side,

substituting υ_n for $\frac{d}{dt}[p_a(t)]$ in the second term, and denoting $[I_q(t)]_{t=t_{n+1}}$ and

$[I_q(t)]_{t=t_n}$ by I_{q_{n+1}} and I_{q_n}, respectively, Eq. (B.20) becomes

$$p_{t_{n+1}}exp(I_{q_{n+1}}) - p_{t_n}exp(I_{q_n})$$

$$= p_{a_{n+1}}exp(I_{q_{n+1}}) - p_{a_n}exp(I_{q_n}) - \int_{t_n}^{t_{n+1}} υ_n exp[I_q(t)]dt - \int_{t_n}^{t_{n+1}} \hat{G}S_{x_n}exp[I_q(t)]dt$$

B-12
---
$$= p_{a_{n+1}} \exp(I_{q_{n+1}}) - p_{a_n} \exp(I_{q_n}) - (\upsilon_n + \hat{G}S_{x_n}) \int_{t_n}^{t_{n+1}} \exp[I_q(t)]dt.$$ (B.21)

Multiplying both sides of Eq. (B.21) by $$\exp(-I_{q_{n+1}})$$ and rearranging terms,

$$p_{t_{n+1}} = p_{t_n} \exp(-I_{q_{n+1}})\exp(I_{q_n}) + p_{a_{n+1}} - p_{a_n}\exp(-I_{q_{n+1}})\exp(I_{q_n})$$

$$- \exp(-I_{q_{n+1}})(\upsilon_n + \hat{G}S_{x_n}) \int_{t_n}^{t_{n+1}} \exp[I_q(t)]dt$$

$$=p_{t_n} \exp[-(I_{q_{n+1}} - I_{q_n})] + p_{a_{n+1}} - p_{a_n}\exp[-(I_{q_{n+1}} - I_{q_n})]$$

$$- (\upsilon_n + \hat{G}S_{x_n}) \int_{t_n}^{t_{n+1}} \exp\{-[I_{q_{n+1}} - I_q(t)]\}dt.$$ (B.22)

Now, $$p_{a_{n+1}} = p_{a_n} + \upsilon_n \Delta t_n$$, and from the definition of $$I_q$$, $$I_{q_{n+1}} - I_{q_n} = \int_{t_n}^{t_{n+1}} q(t)dt$$ and

$$I_{q_{n+1}} - I_q(t) = \int_t^{t_{n+1}} q(t)dt$$. With these substitutions in Eq. (B.22), $$p_{t_{n+1}}$$ is expressed as:

$$p_{t_{n+1}} = (p_{t_n} - p_{a_n})\exp\left[-\int_{t_n}^{t_{n+1}} q(t)dt\right] + p_{a_n} + \upsilon_n \Delta t_n - (\upsilon_n + \hat{G}S_{x_n}) \int_{t_n}^{t_{n+1}} \exp\left[-\int_t^{t_{n+1}} q(t)dt\right]dt.$$ (B.23)

Eq. (B.23) is the general solution for determining tissue gas tension using any function q(t) to represent changes in blood flow. The specification of q(t) may be based on experimental data, if available, or on a model of blood flow changes during exercise. The integrals in Eq. (B.23) may require numerical evaluation if q(t) is an empirical representation of experimental data or represented by a complex model that renders analytic treatment infeasible.

If q(t) is constant, $$\int_{t_n}^{t_{n+1}} q(t)dt = q\Delta t = \frac{\Delta t}{\tau}$$, $$\int_{t_n}^{t_{n+1}} \exp\left[-\int_t^{t_{n+1}} q(t)dt\right]dt = \tau\left[1-\exp\left(-\frac{\Delta t}{\tau}\right)\right]$$ and Eq. (B.23)

reduces to

$$p_{t_{n+1}} = p_{t_n} (1-\varepsilon_n) + \upsilon_n \Delta t_n + [p_{a_n} - \tau\{\upsilon_n + \hat{G}S_{x_n}\}]\varepsilon_n,$$ (B.24)

where $$\varepsilon_n = 1 - \exp\left(-\frac{\Delta t_n}{\tau}\right).$$

B-13
---
### 9.1.1.2.2 Multi-Exponential Model of Time-Dependent Changes in Blood Flow

We assume a multi-exponential representation of changes in Q̇(t) to be general and to accommodate possible bi-phasic responses of blood flow to exercise. Such a representation, which allows evaluation of the integrals of q(t) in Eq. (B.23) to be analytically tractable, is given by the following equation in the interval [tn , tn+1]:

$$Q̇(t) = Q̇_{ex_n} - (Q̇_{ex_n} - Q̇_n) \sum_{ℓ=1}^{N_{exp}} f_{exp_ℓ,n} \exp \left(-\frac{t-t_n}{\tau_{exp_ℓ,n}}\right),$$

(B.25)

Where Q̇n = blood flow per unit volume of tissue at t = tn ,

Q̇exn = steady-state blood flow that would be reached if exercise is continued
        indefinitely at its prevailing level in the interval [tn , tn+1],

Nexp = number of exponential components,

fexpℓ,n = fraction of blood flow change associated with the ℓth exponential
         component in the interval [tn , tn+1], and

τexpℓ,n = time constant associated with ℓth exponential component in the interval
         [tn , tn+1].

The fractions fexpℓ,n should add up to 1, so that at t = tn,

$$Q̇(t) = Q̇_{ex_n} - (Q̇_{ex_n} - Q̇_n) \sum_{ℓ=1}^{N_{exp}} f_{exp_ℓ,n} = Q̇_n.$$

As t → ∞, Q̇(t) → Q̇exn. Also, Q̇(t) = Q̇n if Q̇exn = Q̇n (resting conditions), and Q̇(t) = Q̇exn if τexpℓ,n = 0 for all exponential components (instantaneous change). With appropriate specification of fexpℓ,n and τexpℓ,n, Eq. (B.25) can accommodate different rates of blood flow change as exercise begins (onset) and ends (recovery). It should be noted that the blood flow level Q̇exn remains unchanged until there is a change in exercise level.

We now evaluate the integrals in Eq. (B.23) using Eq. (B.25) to calculate q(t), which is proportional to Q̇(t), and the change of variable, (t – tn) = δ, which leads to δ = 0 at t = tn, δ = tn+1 – tn = ∆tn at t = tn+1, and dt = dδ.

B-14
---
$$\int_{t_n}^{t_{n+1}} q(t)dt = \int_{t_n}^{t_{n+1}} \left[q_{ex_n} - (q_{ex_n} - q_n) \sum_{l=1}^{N_{exp}} f_{exp,l,n} \exp\left(-\frac{t-t_n}{\tau_{exp,l,n}}\right)\right] dt$$

$$= \int_0^{\Delta t_n} \left[q_{ex_n} - (q_{ex_n} - q_n) \sum_{l=1}^{N_{exp}} f_{exp,l,n} \exp\left(-\frac{\delta}{\tau_{exp,l,n}}\right)\right] d\delta$$

$$= q_{ex_n} \Delta t_n - (q_{ex_n} - q_n) \int_0^{\Delta t_n} \sum_{l=1}^{N_{exp}} f_{exp,l,n} \exp\left(-\frac{\delta}{\tau_{exp,l,n}}\right) d\delta$$

$$= q_{ex_n} \Delta t_n - (q_{ex_n} - q_n) \sum_{l=1}^{N_{exp}} \tau_{exp,l,n} f_{exp,l,n} \left[1 - \exp\left(-\frac{\Delta t_n}{\tau_{exp,l,n}}\right)\right] \tag{B.26}$$

Eq. (B.26) is considerably simplified by expanding the term in brackets to obtain

$$1 - \exp\left(-\frac{\Delta t_n}{\tau_{exp,l,n}}\right) = 1 - \left[1 - \left(\frac{\Delta t_n}{\tau_{exp,l,n}}\right) + \frac{1}{2}\left(\frac{\Delta t_n}{\tau_{exp,l,n}}\right)^2 .......\right] = \frac{\Delta t_n}{\tau_{exp,l,n}},$$

where terms of order greater than 2 are neglected. Then Eq. (B.26) becomes

$$\int_{t_n}^{t_{n+1}} q(t)dt = q_{ex_n} \Delta t_n - (q_{ex_n} - q_n) \sum_{l=1}^{N_{exp}} \tau_{exp,l,n} f_{exp,l,n} \left[\frac{\Delta t_n}{\tau_{exp,l,n}}\right]$$

$$= q_{ex_n} \Delta t_n - (q_{ex_n} - q_n) \Delta t_n \sum_{l=1}^{N_{exp}} f_{exp,l,n}$$

$$= q_{ex_n} \Delta t_n - (q_{ex_n} - q_n) \Delta t_n, \quad \text{because } \sum_{l=1}^{N_{exp}} f_{exp,l,n} = 1$$

$$= q_n \Delta t_n \tag{B.27}$$

The error in the approximation $1-\exp\left(-\frac{\Delta t_n}{\tau_{exp,l,n}}\right) \approx \frac{\Delta t_n}{\tau_{exp,l,n}}$ is less than 0.5% if $\frac{\Delta t_n}{\tau_{exp,l,n}} < 0.01$,

that is, if $\tau_{exp,l,n} > 100 \Delta t_n$. Assuming a nominal integration step size of 0.001 min,
$\tau_{exp,l,n} > 0.1$ min. This means that if the time constant is less than 0.1 min for any
exponential component in Eq. (B.25), the integration step size must be reduced to keep
the approximation error less than 0.5%.

B-15
---
Next, we evaluate $$\int_{t_n}^{t_{n+1}} q(t)dt$$, noting that the lower limit = (t - t_n) for q(t) as defined by

Eq. (B.25) is valid in the interval [t_n, t_n+1] with an initial value of q_n. Thus,

$$\int_{t_n}^{t_{n+1}} q(t)dt = \int_{t-t_n}^{t_{n+1}} \left[q_{ex_n} - (q_{ex_n} - q_n) \sum_{l=1}^{N_{exp}} f_{exp_{l,n}} \exp\left(-\frac{t-t_n}{\tau_{exp_{l,n}}}\right)\right] dt$$

$$= \int_0^{\Delta t_n} \left[q_{ex_n} - (q_{ex_n} - q_n) \sum_{l=1}^{N_{exp}} f_{exp_{l,n}} \exp\left(-\frac{\delta}{\tau_{exp_{l,n}}}\right)\right] d\delta$$

$$= q_{ex_n} (\Delta t_n - \delta) - (q_{ex_n} - q_n) \int_0^{\Delta t_n} \sum_{l=1}^{N_{exp}} f_{exp_{l,n}} \exp\left(-\frac{\delta}{\tau_{exp_{l,n}}}\right) d\delta$$

$$= q_{ex_n} (\Delta t_n - \delta) - (q_{ex_n} - q_n) \sum_{l=1}^{N_{exp}} \tau_{exp_{l,n}} f_{exp_{l,n}} \left[\exp\left(-\frac{\delta}{\tau_{exp_{l,n}}}\right) - \exp\left(-\frac{\Delta t_n}{\tau_{exp_{l,n}}}\right)\right]$$

The integral associated with the last term on the right side of Eq. (B.23) is then

$$\int_{t_n}^{t_{n+1}} \exp\left[-\int_{t_n}^{t_{n+1}} q(t)dt\right] dt$$

$$= \int_0^{\Delta t_n} \exp\left\{-q_{ex_n} (\Delta t_n - \delta) + (q_{ex_n} - q_n) \sum_{l=1}^{N_{exp}} \tau_{exp_{l,n}} f_{exp_{l,n}} \left[\exp\left(-\frac{\delta}{\tau_{exp_{l,n}}}\right) - \exp\left(-\frac{\Delta t_n}{\tau_{exp_{l,n}}}\right)\right]\right\} d\delta \qquad (B.28)$$

The integral on the right side of Eq. (B.28) cannot be evaluated in closed form without approximation. Therefore, we expand the exponential terms, truncate the series by neglecting higher order terms, and then perform the integration, as described below:

$$\exp\left(-\frac{\delta}{\tau_{exp_{l,n}}}\right) - \exp\left(-\frac{\Delta t_n}{\tau_{exp_{l,n}}}\right) = \left[1 - \frac{\delta}{\tau_{exp_{l,n}}} + \frac{1}{2}\left(\frac{\delta}{\tau_{exp_{l,n}}}\right)^2 .......\right] - \left[1 - \frac{\Delta t_n}{\tau_{exp_{l,n}}} + \frac{1}{2}\left(\frac{\Delta t_n}{\tau_{exp_{l,n}}}\right)^2 .......\right]$$

$$\approx \frac{\Delta t_n - \delta}{\tau_{exp_{l,n}}}, \quad \text{neglecting terms of order > 2.} \qquad (B.29)$$

Eq. (B.28) is reduced using Eq. (B.29) as follows:

B-16
---
$$\int_{t_n}^{t_{n+1}} \exp\left[-\int_{t_n}^{t_{n+1}} q(t)dt\right]dt = \int_0^{\Delta t_n} \exp\left[-q_{ex_n}(\Delta t_n - \delta) + (q_{ex_n} - q_n) \sum_{l=1}^{N_{exp}} \tau_{exp,n} f_{exp,n} \frac{\Delta t_n - \delta}{\tau_{exp,n}}\right] d\delta$$

$$= \int_0^{\Delta t_n} \exp\left[-q_{ex_n}(\Delta t_n - \delta) + (q_{ex_n} - q_n)(\Delta t_n - \delta) \sum_{l=1}^{N_{exp}} f_{exp,n}\right] d\delta$$

Then, because $\sum_{l=1}^{N_{exp}} f_{exp,n} = 1$, we have

$$\int_{t_n}^{t_{n+1}} \exp\left[-\int_{t_n}^{t_{n+1}} q(t)dt\right]dt = \int_0^{\Delta t_n} \exp\left[-q_{ex_n}(\Delta t_n - \delta) + (q_{ex_n} - q_n)(\Delta t_n - \delta)\right] d\delta$$

$$= \int_0^{\Delta t_n} \exp\left[-q_n(\Delta t_n - \delta)\right]d\delta$$

$$= \frac{\exp\left[-q_n(\Delta t_n - \delta)\right]}{q_n}\bigg|_0^{\Delta t_n}$$

$$= \frac{1 - \exp(-q_n\Delta t_n)}{q_n} \tag{B.30}$$

Our final recursive relation for tissue gas tension is obtained by substituting the
evaluated expressions for the integrals given by Eqs. (B.27) and (B.30) into Eq. (B.23)
and rearranging terms:

$$p_{t_{n+1}} = (p_{t_n} - p_{a_n})\exp(-q_n\Delta t_n) + p_{a_n} + v_n\Delta t_n - (v_n + G\hat{S}_{x_n})\frac{1-\exp(-q_n\Delta t_n)}{q_n}$$

$$= (p_{t_n} - p_{a_n})[\exp(-q_n\Delta t_n) - 1] + p_{t_n} + v_n\Delta t_n - (v_n + G\hat{S}_{x_n})\frac{1-\exp(-q_n\Delta t_n)}{q_n}$$

$$= p_{t_n} + v_n\Delta t_n + (p_{a_n} - p_{t_n})[1-\exp(-q_n\Delta t_n)] - (v_n + G\hat{S}_{x_n})\frac{1}{q_n}[1 - \exp(-q_n\Delta t_n)]$$

$$= p_{t_n} + v_n\Delta t_n + \left[p_{a_n} - p_{t_n} - \tau_n\left(v_n + G\frac{\hat{x}_{n+1} - \hat{x}_n}{\Delta t_n}\right)\right]\varepsilon_n, \tag{B.31}$$

B-17
---

$$\text{where } \tau_n = \frac{1}{q_n} = \frac{\alpha_t}{\alpha_b Q_n}, \text{ and } \varepsilon_n = 1 - \exp(-q_n \Delta t_n) = 1 - \exp\left(-\frac{\Delta t_n}{\tau_n}\right). \text{ Also, we have}$$

$$\text{substituted } S_{x_n} = \frac{\hat{x}_{n+1} - \hat{x}_n}{\Delta t_n} \text{ for the gas loss rate into bubbles.}$$

The variables τn and εn in Eq. (B.31) depend on qn, which is proportional to blood flow $\dot{Q}_n$ at time tn. The recursive relation for calculating $\dot{Q}_n$ is obtained from Eq. (B.25):

$$\dot{Q}_{n+1} = \dot{Q}_{ex_n} - (\dot{Q}_{ex_n} - \dot{Q}_n) \sum_{\ell=1}^{N_{exp}} f_{exp,\ell,n} \exp\left(-\frac{\Delta t}{\tau_{exp,\ell,n}}\right).$$

The parameters in this relation include steady-state blood flows at different exercise intensities, and time constants and blood flow fractions associated with each exponential component. Note that $\dot{Q}_{n+1} = \dot{Q}_{ex_n}$ if the change in blood flow rate is instantaneous ($\tau_{exp,\ell,n} = 0$ for all $\ell$).

As an example, consider a tissue compartment with a resting half time of 100 min. The time constant is 100/ln(2) = 144 min, and compartmental blood flow per unit volume of tissue is 1/144 or approximately 0.007 mL per min. The compartmental blood flow per unit volume of tissue during 50% maximum exercise would increase by a factor of about 2.5 to 0.0175 mL per min, corresponding to a time constant of 57 min. Exponential time constants associated with such a change in blood flow would range from a fraction of a minute to several minutes.

Eq. (B.31) is identical to Eq. (B.24) except for the dependency of τ – and hence ε – and G on time. The model we adopted for blood flow changes and the approximations we made for closed-form evaluation of the integral terms in the solution did not alter the basic structure of the recursive relation for calculating the tissue gas tension. This may not be true with more complex models of blood flow. The multi-exponential model is fairly realistic and the approximations (with second order terms neglected) are reasonable, requiring that blood flow time constants be greater than 0.1 min to limit the error to less than 0.5 % with an integration step size of 0.001 min. The demands on accuracy can always be met by reducing the step size, if the increased computational burden can be accommodated.

### 9.1.1.2.3 Coupling of Compartmental O2 Consumption and Blood flow

We assume that exercise-induced changes in compartmental blood flow are driven by changes in compartmental O2 consumption due to exercise, and that the latter changes are given by Eq. (A.25). The recursive relation for solving Eq. (A.25) is

B-18
---
$$\dot{V}_{O2_{n+1}} = \dot{V}_{O2_n} - (\dot{V}_{O2_{ex,n}} - \dot{V}_{O2_n})\left\{1-\exp\left(-\frac{\Delta t_n}{\tau_{VO2_n}}\right)\right\},\tag{B.32}$$

where $\dot{V}_{O2_{n+1}}$ and $\dot{V}_{O2_n}$ are the O₂ consumption rates at times t_{n+1} and t_n, respectively,

$$\dot{V}_{O2_{ex,n}} = \Delta\dot{V}_{O2_{ex}} + \dot{V}_{O2_{rest}} = m_{VO_2}I_{ex_n} + \dot{V}_{O2_{rest}}\tag{B.33}$$

is the steady-state O₂ consumption at exercise intensity $I_{ex_n}$, and $\tau_{VO2_n}$ is the time constant associated with the exponential change in $\dot{V}_{O2}$ in the interval [t_n , t_{n+1}].

The steady-state blood flow during exercise is then estimated by assuming that compartmental blood flow increases linearly with compartmental O₂ consumption:

$$\dot{Q}_{ex_n} = m_Q \cdot (\dot{V}_{O2,n} - \dot{V}_{O2,rest}) + \dot{Q}_{rest}\tag{B.34}$$

## 9.1.2 Multiple Bubbles of Different Sizes

The recursive relationships derived above are readily elaborated to accommodate the solution for the radii and gas pressures of multiple bubbles present in an arbitrary distribution of N_bs different sizes. Such elaboration entails repeating the calculations of $\hat{r}_{n+1}$ and $P_{b_{n+1}}$ for the $n_{b_m}$ bubbles of each size m, m=1, 2, ..., N_bs, in the distribution.

The bubble gas pressures are obtained from Eq. (B.12)

$$P_{b_{m,n+1}} = A_{m,n} - (3A_{m,n} - B_{m,n})\delta\hat{r}_{m,n}.\tag{B.35}$$

where A_{m,n} is obtained from Eq. (B.13a);

$$A_{m,n} = P_{b_{m,n}} + a_{m,n}\left(1-\frac{a_{m,n}}{2}\right)(p_{t_n} - P_{b_{m,n}}),\tag{B.36}$$

with $a_{m,n} = \left(\frac{\hat{r}_{m,n} + 1}{\hat{r}^2_{m,n}}\right)\Delta t_n \hat{K}_m$; and $B_{m,n}$ is obtained from Eq. (13.b);

$$B_{m,n} = \frac{1}{2}[(2a_{m,n} - b_{m,n} + a_{m,n}b_{m,n})p_{t_n} + (a_{m,n} + b_{m,n})(1 - a_{m,n})P_{b_{m,n}}],\tag{B.37}$$

with $b_{m,n} = \frac{\Delta t_n}{\hat{r}^2_{m,n}} \hat{K}_m$.

B-19
---
Finally, from Eq. (B.18)

$$\delta\hat{r}_{m,n} = \frac{A_{m,n} \left(P_{amb_{n+1}} + \frac{2\sigma_m}{\hat{r}_{m,n}} + \hat{M}_m\hat{r}^3_{m,n}\right)}{(3A_{m,n} - B_{m,n}) \left(\frac{2\sigma_m}{\hat{r}_{m,n}} - 3\hat{M}\hat{r}^3_{m,n}\right)}. \tag{B.38}$$

The tissue tension of the diffusible gas $p_{t_{n+1}}$ is calculated using Eq. (B.23) for any function $q_k (t)$ or Eq. (B.31) for $q_k (t)$ as a multiexponential, after modification to account for the net gas exchange between all bubbles and the tissue as such exchange differs for bubbles of different sizes. Accordingly, Eq. (B.23) is modified by summing the amounts of gas exchanged between bubbles and tissue for all bubbles of $N_{bs}$ different sizes as follows:

$$p_{t_{n+1}} = (p_{t_n} - p_{a_n})\exp\left[-\int_{t_n}^{t_{n+1}}q(t)dt\right] + p_{a_n} + v_n\Delta t_n - \left(v_n + \sum_{m=1}^{N_{bs}} \hat{G}_mS_{x_{m_n}}\right)\int_{t_n}^{t_{n+1}}\exp\left[-\int_t^{t_{n+1}}q(t)dt\right]dt \tag{B.39}$$

where $\hat{x}_{m,n+1}$ and $\hat{x}_{m,n}$ are the gas contents at times $t_{n+1}$ and $t_n$ respectively in each of $n_{b_{m,n}}$ bubbles of radius $r_m$ in the $m^{th}$ bubble size group with

$$\hat{G}_m = \left(\frac{4\pi}{3}\right)\frac{n_{b_m}}{\alpha_t V_t \lambda^3_m}, \text{ and}$$

$$S_{x_{m_n}} = \frac{\hat{x}_{m_n + 1} - \hat{x}_{m_n}}{\Delta t_n}.$$

Similarly, Eq. (B.31) becomes

$$p_{t_{n+1}} = p_{t_n} + v_n\Delta t_n + \left[p_{a_n} - p_{t_n} - \tau_n\left(v_n + \frac{\sum_{m=1}^{N_{bs}}\hat{G}_m(\hat{x}_{m,n+1} - \hat{x}_{m,n})}{\Delta t_n}\right)\right]\varepsilon_n. \tag{B.40}$$

With constant q(t), $\tau_n$ becomes a constant equal to $\tau$ and Eq. (B.40) reduces to Eq. (B.24).

B-20
---
Determination of $\hat{r}_{m,n+1}$, $P_{bn+1}$, and $p_{tn+1}$ requires computation time in excess of that required for the $N_{bs} = 1$ case (multiple bubbles of the same size) roughly in proportion to the number of bubble sizes considered.

## 9.2 Multiple Diffusible Gases

With $N_g > 1$ diffusible gases in the tissue-bubble system, the recursive relations derived in the previous sections hold for each diffusible gas. Referring to Eq. (B.35), the pressure of the $k^{th}$ diffusible gas in bubbles of $m^{th}$ size is

$$P_{bk,m,n+1} = A_{k,m,n} - (3A_{k,m,n} - B_{k,m,n})\delta\hat{r}_{m,n} . \tag{B.41}$$

where

$$A_{k,m,n} = P_{bk,m,n} + a_{k,m,n}\left(1-\frac{a_{k,m,n}}{2}\right)(p_{tk,n} - P_{bk,m,n}), \tag{B.42}$$

with $a_{k,m,n} = \left(\frac{\hat{r}_{m,n}+1}{\hat{r}^2_{m,n}}\right)\Delta t_n \hat{K}_{k,m}$, and

$$B_{k,m,n} = \frac{1}{2}[(2a_{k,m,n} - b_{k,m,n} + a_{k,m,n}b_{k,m,n})p_{tk,n} + (a_{k,m,n} + b_{k,m,n})(1-a_{k,m,n})P_{bk,m,n}], \tag{B.43}$$

with $b_{k,m,n} = \frac{\Delta t_n}{\hat{r}^2_{m,n}}\hat{K}_{k,m}$.

Coefficients $A_{k,m,n}$ and $B_{k,m,n}$ at time $t_n$ are different for each diffusible gas due to differences in the scaled permeabilities, $\hat{K}_k$, of the gases in the tissue.

The total diffusible gas pressure in a bubble must equal the hydrostatic pressure less the sum of the infinitely-diffusible gas partial pressures, $P_\infty$, plus the pressures due to surface tension and tissue elasticity as indicated by Eq. (B.14). Therefore, for bubbles of size m

$$\sum_{k=1}^{N_g} P_{bk,m,n+1} = \sum_{k=1}^{N_g} A_{k,m,n} - \left[\sum_{k=1}^{N_g}(3A_{k,m,n} - B_{k,m,n})\right]\delta\hat{r}_{m,n}$$

B-21
---
= P'amb,n+1 + 2σ/r̂m,n+1 + Mr̂3m,n+1. (B.44)

Following the steps from Eq. (B.14) to Eq. (B.18), we obtain

$$
\delta \bar{r}_{m,n} = \frac{\sum_{k=1}^{N_g} A_{k,m,n} \left(P'_{amb_{n+1}} + \frac{2\sigma}{\hat{r}_{m,n}} + M\hat{r}^3_{m,n}\right)}{\sum_{k=1}^{N_g} (3A_{k,m,n} - B_{k,m,n}) \left(\frac{2\sigma}{\hat{r}_{m,n}} - 3M\hat{r}^3_{m,n}\right)}.
$$ (B.45)

Note that Eq. (B.45) reduces to Eq. (B.18) if the number of diffusible gases Ng = 1.

The tissue tension of each diffusible gas is calculated using Eq. (B.39) for any function qk(t) or Eq. (B.40) for qk(t) as a multiexponential. For the kth diffusible gas in the interval [tn, tn+1], Eq. (B.39) becomes

$$
p_{t_{k,n+1}} = (p_{t_{k,n}} - p_{a_{k,n}}) \exp \left[-\int_{t_n}^{t_{n+1}} q_k(t)dt\right] + p_{a_{k,n}} + \upsilon_{k,n}\Delta t_n
$$ 

$$
- \left(\upsilon_{k,n} + \sum_{m=1}^{N_{bs}} \hat{G}_{k,m}S_{x_{k,mn}}\right) \int_{t_n}^{t_{n+1}} \exp \left[-\int_t^{t_{n+1}} q_k(t)dt\right] dt
$$ (B.46)

and Eq. (B.40) becomes

$$
p_{t_{k,n+1}} = p_{t_{k,n}}(1-\varepsilon_{k,n}) + \upsilon_{k,n}\Delta t_n
$$

$$
+ \left[p_{a_{k,n}} - \tau_{k,n} \left(\upsilon_{k,n} + \sum_{m=1}^{N_{bs}} \hat{G}_{k,m}S_{x_{k,mn}}\right)\right] \varepsilon_{k,n},
$$ (B.47)

where $\hat{G}_{k,m} = \left(\frac{4\pi}{3}\right) \frac{n_{bm}}{\alpha_k V_t \Lambda^3_m}$,

$\hat{x}_{k,m,n+1} = P_{b_{k,m,n+1}} \hat{r}^3_{m,n+1}$,

$S_{x_{k,mn}} = \frac{\hat{x}_{k,m,n+1} - \hat{x}_{k,m,n}}{\Delta t_n}$, and

$\upsilon_{k,n} = \frac{p_{a_{k,n+1}} - p_{a_{k,n}}}{\Delta t_n}$ is the rate of change in arterial tension of the kth diffusible gas in

the interval [tn , tn+1]. With constant qk(t), Eq. (B.47) applies with τk,n a constant equal to

B-22
---
τk. Omission of subscripts for gas-specific variables then renders Eq. (B.47) identical to
Eq. (B.24).

## 9.2.1 Tissue O2 Tension with O2 as a Diffusible Gas

Eqs. (B.41) through (B.45) also apply when O2 is considered to be among the Ng
diffusible gases. However, Eqs. (B.46) and (B.47) require modification to account for the
nonlinear relationship between O2 content and O2 partial pressure in arterial blood due
to the Hb-O2 dissociation curve.

Semi-analytic solutions similar to Eq. (B.46) and (B.47) can be derived for recursive
calculation of PtO2 in each integration interval. To simplify notation, we describe the
derivation for cases involving multiple bubbles of the same size in a tissue and then
elaborate the result for cases involving multiple bubbles of different size.

### 9.2.1.1 Multiple Bubbles of Same Size

We begin by substituting x̂O2 = PbO2r̂³ and ĜO2 = 4π αtO2nbr³/3VtΛ³ into Eq. (A.15) (with Nbs =
1) for O2 mass balance in tissue to obtain:

$$\frac{d}{dt}(\alpha_{tO2}p_{tO2}) = \dot{Q}(t)[C_{aO2} - C_{vO2}] - \alpha_{tO2}\hat{G}_{O2}\frac{d\hat{x}_{O2}}{dt} - \dot{V}_{O2}(t),$$

(B.48)

where Q̇(t) is blood flow per unit volume of tissue and the tissue O2 consumption,
V̇O2(t), is determined with the recursive formula in Eq. (B.32). We then approximate the
blood O2 content (plasma + Hb-bound) versus O2 partial pressure curve by a linear
segment for the time interval [tn, tn+1] and express CvO2, the venous O2 content
corresponding to partial pressure pvO2n at time tn, as

$$C_{vO2} = C_{vO2n} + \alpha'_{O2n}(p_{vO2} - p_{vO2n}),$$

(B.49)

where α'O2n is the slope of the whole blood solubility curve in the region of pvO2n.
Referring to the a1, a2, b1, b2, p, η, and phalf parameters defined with Eq. (A.21), this
slope is given by

B-23
---
$$\alpha'_{O_{2n}} = \frac{dC_{O2}}{dP_{O2}} = \alpha_{bO2} + Hb_c\frac{dS_{O2}}{dP_{O2}}$$

$$= \alpha_{bO2} + Hb_c\frac{dS_{O2}}{dp}\frac{dp}{dP_{O2}}$$

$$= \alpha_{bO2} + Hb_c\left[\frac{(a_1 + 2a_2p)(1.0 + b_1p + b_2p^2) - (a_1p + a_2p^2)(b_1 + 2b_2p)}{(1.0 + b_1p + b_2p^2)^2}\right]\left[\frac{\eta p^{\eta-1}}{p_{half}}\right]$$

$$= \alpha_{bO2} + Hb_c\left[\frac{\left(a_1 + a_1b_1p + a_1b_2p^2 + 2a_2p + 2a_2b_1p^2 + 2a_2b_2p^3\right) - \left(a_1b_1p + 2a_1b_2p^2 + 2a_2b_1p^2 + 2a_2b_2p^3\right)}{(1.0 + b_1p + b_2p^2)^2}\right]\left[\frac{\eta p^{\eta-1}}{p_{half}}\right]$$

$$= \alpha_{bO2} + Hb_c\left[\frac{a_1 + 2a_2p - a_2(a_1 - b_1)p^2}{(1.0 + b_1p + b_2p^2)^2}\right]\left[\frac{\eta p^{\eta-1}}{p_{half}}\right],\tag{B.50}$$

with $$p = \left(\frac{p_{vO_{2n}}}{p_{half}}\right)^{\eta}.$$

Note that $\alpha'_{O_{2n}}$ has the units of solubility. Assuming that compartmental blood-tissue gas exchange is perfusion limited, end-capillary blood and tissue are at equilibrium; i.e., $p_{vO_2} = p_{tO_2}$; and Eq. (B.49) becomes

$$C_{vO_2} = C_{vO_{2n}} - \alpha'_{O_{2n}}p_{vO_{2n}} + \alpha'_{O_{2n}}p_{tO_2}$$

$$= C'_{O_{2n}} + \alpha'_{O_{2n}}p_{tO_2},\tag{B.51}$$

where

$$C'_{O_{2n}} = C_{vO_{2n}} - \alpha'_{O_{2n}}p_{vO_{2n}}.\tag{B.52}$$

Substitution of Eq. (B.51) into Eq. (B.48) yields

B-24
---

$$\frac{d}{dt}(\alpha_{tO_2}p_{tO_2}) = \dot{Q}_n[C_{aO_2} - C'_{O_2n} - \alpha'_{O_2n}p_{tO_2}] - \alpha_{tO_2}\hat{G}_{O_2}\frac{d\hat{x}_{O_2}}{dt} - \dot{V}_{O_2n},$$

(B.53)

which is valid for t_n ≤ t < t_n+1 with blood flow of $\dot{Q}_n$ and O_2 consumption of $\dot{V}_{O_2n}$. Dividing
both sides of Eq. (B.53) by $\alpha_{tO_2}$ yields

$$\frac{dp_{tO_2}}{dt} = \frac{\dot{Q}_n}{\alpha_{tO_2}}[C_{aO_2} - C'_{O_2n} - \alpha'_{O_2n}p_{tO_2}] - \hat{G}_{O_2}\frac{d\hat{x}_{O_2}}{dt} - \frac{\dot{V}_{O_2n}}{\alpha_{tO_2}}$$

$$= \frac{\dot{Q}_n\alpha'_{O_2n}}{\alpha_{tO_2}}[\frac{C_{aO_2}}{\alpha'_{O_2n}} - \frac{C'_{O_2n}}{\alpha'_{O_2n}} - p_{tO_2}] - \hat{G}_{O_2}\frac{d\hat{x}_{O_2}}{dt} - \frac{\dot{V}_{O_2n}}{\alpha_{tO_2}}$$

$$= \frac{\dot{Q}_n\alpha'_{O_2n}}{\alpha_{tO_2}}(\frac{C_{aO_2}}{\alpha'_{O_2n}} - p_{tO_2}) - \frac{\dot{Q}C'_{O_2n}}{\alpha_{tO_2}} - \hat{G}_{O_2}\frac{d\hat{x}_{O_2}}{dt} - \frac{\dot{V}_{O_2n}}{\alpha_{tO_2}}$$

$$= \frac{p'_{O_2} - p_{tO_2}}{\tau_{O_2n}} - \hat{G}_{O_2}\frac{d\hat{x}_{O_2}}{dt} - \hat{\rho}_n,$$

(B.54)

where $p'_{O_2} = \frac{C_{aO_2}}{\alpha'_{O_2n}}$, $\tau_{O_2n} = \frac{\alpha_{tO_2}}{\alpha'_{O_2n}\dot{Q}_n}$ is a time constant that changes in each time
interval depending on changes in blood flow and changes in the slope of the blood O_2
content versus O_2 partial pressure curve at the prevailing $p_{tO_2}$, and $\hat{\rho}_n$ is a constant

rate of change of pressure in each time interval, defined as $\hat{\rho}_n = \frac{\dot{V}_{O_2n} + \dot{Q}_nC'_{O_2n}}{\alpha_{tO_2}}$,

which upon substitution for C'_O_2n from Eq. (B.51) becomes

$$\hat{\rho}_n = \frac{\dot{V}_{O_2n} + \dot{Q}_n(C_{\bar{v}O_2n} - \alpha'_{O_2n}p_{\bar{v}O_2n})}{\alpha_{tO_2}}.$$

(B.55)

Note from Eq. (B.50) that $\alpha'_{O_2n} \geq \alpha_b$, which obviates excessively small values of
$\alpha'_{O_2n}$ that could cause numerical errors. Rearranging terms, Eq. (B.54) for the interval
[t_n , t_n+1] becomes,

$$\frac{dp_{tO_2}}{dt} + \frac{p_{tO_2}}{\tau_{O_2n}} = \frac{p'_{O_2}}{\tau_{O_2n}} - \frac{d\hat{x}'_{O_2}}{dt},$$

(B.56)

where $\hat{x}'_{O_2} = \hat{G}_{O_2}\hat{x}_{O_2} + \hat{\rho}_nt$.

(B.57)

B-25
---
Eq. (B.56) is identical in form to Eq. (A.22) with k=1 and N_bs = 1 for the tissue tension of an inert gas. Comparison of the two equations shows that variables p'O2, x'O2, and τ'O2n in Eq. (B.56) correspond respectively to variables pa, x̂, and τ in Eq. (A.22), and the constant G in Eq. (A.22) is 1 in Eq. (B.56). With these changes in variables and the value for G, the solution to Eq. (A.22) given by Eq. (B.31) is applicable to Eq. (B.53) as well. Thus, for identically sized bubbles in tissue, the recursive formula for tissue O2 tension ptO2,n+1 at time tn+1, given the tissue O2 tension ptO2,n at time tn, is

$$ptO2_{n+1} = ptO2_n + υO2_n \Delta t_n + \left[p'O2 - ptO2_n - τO2_n \left\{υO2_n + \frac{x̂'O2_{n+1} - x̂'O2_n}{\Delta t_n}\right\}\right] εO2_n,$$

(B.58)

where εO2_n = 1 - exp(-Δtn / τO2_n). Using Eq. (B.57),

$$\frac{x'O2_{n+1} - x'O2_n}{\Delta t_n} = GO2 \frac{xO2_{n+1} - xO2_n}{\Delta t_n} + \frac{\hat{ρ}_n (t_{n+1} - t_n)}{\Delta t_n} = \hat{G}O2 \frac{x̂O2_{n+1} - x̂O2_n}{\Delta t_n} + \hat{ρ}_n,$$

which is substituted into Eq. (B.58) to yield:

$$ptO2_{n+1} = ptO2_n (1 - εO2_n) + υO2_n \Delta t_n + \left[p'O2_n - τO2_n \left\{υO2_n + \hat{ρ}_n + \hat{G}O2 \frac{x̂O2_{n+1} - x̂O2_n}{\Delta t_n}\right\}\right] εO2_n.$$

(B.59)

The rate υO2_n for O2 is defined by the difference in p'O2 in the interval [tn , tn+1];

$$υO2_n = \frac{p'O2_{n+1} - p'O2_n}{\Delta t_n} = \frac{CaO2_{n+1} - CaO2_n}{\Delta t_n α'O2_n},$$

(B.60)

where CaO2_n+1 and CaO2_n are arterial O2 contents corresponding to arterial O2 partial pressures paO2_n+1 and paO2_n at times tn+1 and tn respectively.

### 9.2.1.2 Multiple Bubbles of Different Size

If the tissue contains multiple bubbles of different sizes, Eq. (B.46) or (B.47) is used to calculate the tissue tension of each of the inert gases. Referring to Eq. (B.59), the corresponding tissue O2 tension is given by

B-26
---
$$p_{tO_{2_{n+1}}} = p_{tO_{2_n}}(1-\varepsilon_{O_{2_n}}) + \upsilon_{O_{2_n}}\Delta t_n$$

$$\begin{bmatrix} + \left[p'_{O_{2_n}} - \tau_{O_{2_n}} \upsilon_{O_{2_n}} + \rho_n + \frac{\sum_{m=1}^{N_{bs}} \hat{G}_{O_{2m}}(\hat{x}_{O_{2m,n+1}} - \hat{x}_{O_{2m,n}})}{\Delta t_n}\right] \end{bmatrix} \varepsilon_{O_{2_n}}, \qquad (B.61)$$

where $\hat{G}_{O_{2m}} = \left(\frac{4\pi}{3}\right) \frac{n_{bm}}{\alpha_{tO_2}V_t \Lambda_m^3} \frac{1}{n_{bm}}$ for bubbles of m^th size. Note that the $n_{bm}$ are constant.

## 9.2.2 Variable Bubble Number: Single Time-Dependent Bubble Size Approximation

As noted in Appendix A, the accumulation of bubbles recruited with increasing supersaturation during decompression is accommodated in present models by assuming that each newly nucleated bubble instantaneously attains the size of prevailing already-nucleated bubbles, which allows $r_{n+1}$, $P_{b_{n+1}}$, and $p_{t_{n+1}}$ to be tracked for only a single bubble size group ($N_{bs} = 1$) in which only $n_b$ changes:

$$N_b = \sum_{m}^{N_{bs}} n_{bm}$$. Maintenance of mass balance in this approach requires a change in bubble gas content and a resultant adjustment in tissue gas tension corresponding to the difference between the nucleonic volume and the prevailing bubble volume whenever a nucleus is 'recruited' during decompression. These requirements are met by allowing the coefficient $\hat{G}_k$ to vary with the number of bubbles and by modifying Eq. (B.47) as described below.

Let $\hat{G}_{k,n}$ denote the coefficient associated with the bubble content of gas k, $\hat{x}_{k,n}$, at the outset of the n^th integration step. The change in gas content, $\hat{x}_{k,n+1} - \hat{x}_{k,n}$, in the interval $[t_n, t_{n+1}]$ is preceded by a change in $\hat{G}_{k,n}$ at the beginning of the interval if any new bubbles are considered to be recruited at the beginning of the interval. We therefore consider the $\Delta t_n$ interval to consist of two subintervals; an initial $\Delta t_{n,0}$ interval in which the bubble number increases from $\hat{G}_{k,n-1}$ to $\hat{G}_{k,n}$, and a subsequent $\Delta t_{n,1}$ interval in which the $\hat{G}_{k,n}$ bubbles evolve, as illustrated in Figure B.1. In the sub-interval $\Delta t_{n,0}$, newly recruited bubbles expand from gas content $\hat{x}_{k,n,0}$ to $\hat{x}_{k,n,1}$. The gas content $\hat{x}_{k,n,1}$ of $\Delta \hat{G}_{k,n}$ newly nucleated bubbles at time $(t_n + \Delta t_{n,0})$ is the same as that of $\hat{G}_{k,n-1}$ 'older' bubbles that grow from $\hat{x}_{k,n}$ at $t_n$ to $\hat{x}_{k,n+1}$ at $t_{n+1}$. In the sub-interval $\Delta t_{n,1}$, the total gas content of

B-27
---
 all bubbles changes from                                                                                                                                  x k,n,1
                                                                                                                                                                  ˆ                        to x k,n+ 1. The total number of bubbles is                                                                                                                                                         ˆ
   Gk =G                                                                                      ˆ n                                                                                            ,                                                                                                                                                               ˆk,n−                                1+∆G                                                                                                                                                       ˆk,n. Including the change in G                             ˆ k,n, Eq. (B.47) becomes



                                   ptk,n+1                        =          ptk,n(1−εk,n)                                                           +               υk,nΔtn                                  +          pan
                                                                                                                                                                                                                                               −        τk     
                                                                                                                                                                                                                                                                υk,n
                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                      +   Gk,n−                                                                                                                          ˆ                                                                                                                       1xk,n+Δtn                                                                                                                     ˆ                  1−ˆxk,n     εk,n
                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                                                                                                   (B.62)

                                                                                                               −             ˆ
                                                                                                                            ΔGk,n
                                                                                                                                                               x                                                                                                                                                                                ˆk,n,1                                                               −x                                                                                                                                                                                      ˆk,n,0                                τk                                                                    εk,n,0
                                                                                                                                                                                                                                                                      −                                                                                                                                      ˆk,n
                                                                                                                                                                                                                                                                            ΔG                       ˆxk,n+1                       −x                                                                                                       ˆk,n,1                                                                                                                                           τk                                                                                     εk,n,1
                                                                                                                                                                                                                                                                                                                                                         
                                                                                                                                                                                   Δtn,0                                                                                                                              Δtn,1                           

where εk,n,0=1                                                                                                                                                                   −exp                                                                                                                                                                                   −∆tn,0
                                                                                                                                                 
                                                                                                                                                          and εn,1=                                               1−exp                                                                                                                                                                                                                            −∆tn,1
                                                                                                                                                                                                                                                                       .
                                                                                                                                                                                                                                                                        
                                                                                                                              τk                                                                                                                         τk          



                                                                                                                                                                                                                                                                                                                                    xk,n+1

                                                                                                                                xk,n,1

                                                                                                                                        xk,n

                                                                                                                                xk,n,0

                                                                                                                                                                          ∆t n,0                                                                       ∆t n,1


                                                                                                                                                        t n                                                                                                                                                    t n+1

                                                                                                                                                                                                                                        ∆t n

                                                             Fig. B.1: Sub-intervals of ∆t n accommodating growth of newly formed bubbles.



 The contribution of the newly formed bubbles is evaluated assuming the change from
   x                                                                                  ˆ k,n,0                                                                                                                 to                                                                                                     x                                                                                                               ˆ n,1                         occurs instantaneously. We thus let ∆t n,0 → 0 and, consequently xk,n,1                                                                            ˆ                                                  →
    x                                                                                   ˆ k,n, to obtain
                                                        lim                          ˆ
                                                                                    ∆Gk,n
                                                                                                                        x                                                                                                                                                                       ˆk,n,1−x                                                                                                                    ˆk,n,0                                                                                                         τ                                                                                                                  εk,n,0            =           ∆G                                                                 ˆk,n     ( k,n

                                                                                                                                                                                                                                                                     x                                                                                                                                     ˆ                                                                                                                                  −x                                                                                                                    ˆk,n,                                                           0)∆tnlim  
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               ∆tn,0εk,n,0  τk        
                                              ∆tn,0→0                                                                                       ∆tn,0                                                
                                                                                                                                                                                                                                                                                                                             ,0→0            
                                                                                                                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                                                                          



                                                                                                                                                                                                                         ˆk,n( k,n                                               0)∆tnlim                               
                                                                                                                                                                                                                                                                                                                         ∆tn,01−exp                                                                                                     τk                                                                                                                                                     −∆tn,0
                                                                                                                                                                                                     =          ∆G                           x                                                                                                                                                          ˆ                                                      −x                                                                                                                                                                                        ˆk,n,                                                      
                                                                                                                                                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                               ,0→0                     
                                                                                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                                                                                   τk           



                                                                                                                                                                                                                                                 B-28
---
= ΔĜk,n (x̂k,n - x̂k,n,0) with the limit evaluating to 1.

Also, as Δtn,0 → 0, Δtn,1 → Δtn and εκ,n,1 → εκ,n. Substituting these limits and using
Ĝk,n = Ĝk,n-1 + ΔĜk,n, Eq. (B.62) becomes

ptk,n+1 = ptk,n (1 - εk,n) + υk,nΔtn + [pak,n - τk {υk,n + Ĝk,n-1 (x̂k,n+1 - x̂k,n) / Δtn}] εk,n

- ΔĜk,n(x̂k,n - x̂k,n,0) - [ΔĜk,n (x̂k,n+1 - x̂k,n) / Δtk,n τ] εk,n

= ptk,n (1 - εk,n) + υk,nΔtn + [pak,n - τk {υk,n + Ĝk,n (x̂k,n+1 - x̂k,n) / Δtn}] εk,n

(B.63)

- ΔĜn(x̂k,n - x̂k,n,0)

Following a similar development from Eq. (B.61), the tissue O2 tension is given by

ptO2n+1 = ptO2n (1 - εO2n) + υO2n Δtn

+ [pO2n' - τO2n {υO2n + ρ̂n + ĜO2n ((x̂O2n+1 - x̂O2n) / Δtn)}] εO2n

- ΔĜO2n(x̂O2n - x̂O2n,0),                                                (B.64)

where ΔĜO2n = (4π / 3) 1 / (αtO2VΛ3) (nbtn - nbtn-1).

In applying Eq. (B.63) and (B.64), the change ΔĜk,n at time tn is obtained from the
number of nuclei recruited in the interval from the assumed nuclei size distribution; i.e.,
the number of nuclei versus their radii. The gas content x̂k,n,0 at tn is that of the nuclei
from which the ΔĜk,n new bubbles were formed.

The number of nuclei recruited at the outset of any integration interval and the
corresponding ΔĜk,n must be determined in a fashion that ensures that nuclei already
recruited from the distribution and lost to the vasculature as VGE are not double-
counted in the nucleation process: The number of bubbles remaining in the
compartment at any time may be fewer than the cumulative number of nuclei that have
been recruited in the compartment at that time. Accordingly, the total number of nuclei

B-29
---
recruited must be tracked independently of the number of bubbles remaining in the
compartment. The cumulative number of bubbles recruited for the nth integration step is

$$N_{b_{max,n}} = MAX\left[N_{b_{max,n-1}}, N_b^0 \exp\left(-\frac{2\sigma}{P_{ss_n} \cdot \beta f_n}\right)\right],$$
(B.65)

where $N_{b_{max,n-1}}$ is the cumulative number of nuclei that were recruited at the outset of
the (n-1) integration step. The number of bubbles recruited at the outset of the nth
integration step to join those already present in the compartment (of number $N_{b_{n-1}}$) is
consequently

$$\Delta n_{b_n} = (N_{b_{max,n}} - N_{b_{max,n-1}}),$$
(B.66)

so that the number of bubbles participating in the nth integration step is

$$n_{b_n} = n_{b_{n-1}} + \Delta n_{b_n}.$$
(B.67)

Thus, $$\Delta \hat{G}_{k,n} = \left(\frac{4\pi}{3}\right) \frac{\Delta n_{b_n}}{\alpha_{t_k} V_t \Lambda^3}$$
(B.68)

and $$\hat{G}_{k,n} = \hat{G}_{k,n-1} \frac{N_{b_n}}{N_{b_{n-1}}}.$$
(B.69)

Increases in the compartmental bubble number density and nb as bubbles are nucleated
from one integration step to the next with increasing supersaturation during
decompression are accommodated in Eqs. (B.63) and (B.64) by the respective $\Delta \hat{G}_{k,n}$
factors and thereafter by the sustained change in $n_{b_n}$ in the corresponding $\hat{G}_{k,n}$ factors.

B-30
---
## 9.3 Semi-Analytic Solution of the Fick Equation in the 3RUT-MB Model

The Fick equation for the 3RUT-MB model given by Equation (B.3) is reproduced following:

$$\frac{dx}{dt} + f(t)x = g(t).$$  (B.3)

This is a linear differential equation in the dependent variable x with coefficients that vary with time. We apply the integrating factor method to obtain a numerical solution of this equation for x(t) at time t<sub>n+1</sub> given x(t) at time t<sub>n</sub>. Recursion of this solution through time provides the entire solution x(t<sub>i</sub>), i = 0, 1, 2, ...

The integrating factor is exp[I<sub>f</sub>(t)], where I<sub>f</sub>(t) is the indefinite integral $$\int f(t)dt.$$ Both sides of Eq. (B.3) are multiplied by the integrating factor to obtain

$$\frac{d}{dt}[x(t)exp\{I_f(t)\}] = g(t)exp\{I_f(t)\}.$$  (B.70)

Integration of Eq. (B.70) in the interval t<sub>n</sub> ≤ t ≤ t<sub>n+1</sub> yields

$$x(t)exp\{I_f(t)\}|_{t_n}^{t_{n+1}} = \int_{t_n}^{t_{n+1}}g(t)exp\{I_f(t)\}dt$$

i.e., $$x(t_{n+1})exp\{I_f(t_{n+1})\} - x(t_n)exp\{I_f(t_n)\} = \int_{t_n}^{t_{n+1}}g(t)exp\{I_f(t)\}dt.$$  (B.71)

Denote x(t<sub>n</sub>) and x(t<sub>n+1</sub>) by x<sub>n</sub> and x<sub>n+1</sub>, respectively. Then from Eq. (B.71)

$$x_{n+1} = x_n exp\{-[I_f(t_{n+1}) - I_f(t_n)]\} + exp\{-I_f(t_{n+1})\}\int_{t_n}^{t_{n+1}}g(t)exp\{I_f(t)\}dt$$

i.e., $$x_{n+1} = x_n exp\{-[I_f(t_{n+1}) - I_f(t_n)]\} + \int_{t_n}^{t_{n+1}}g(t)exp\{-[I_f(t_{n+1}) - I_f(t)]\}dt.$$  (B.72)

Letting t – t<sub>n</sub> = δ and t<sub>n+1</sub> – t<sub>n</sub> = Δt<sub>n</sub> in the interval [t<sub>n</sub> , t<sub>n+1</sub>], Eq. (B.72) becomes

$$x_{n+1} = x_n exp\{-[I_f(t_{n+1}) - I_f(t_n)]\} + \int_0^{\Delta t_n}g(\delta)exp\{-[I_f(t_{n+1}) - I_f(\delta)]\}d\delta.$$  (B.73)

B-31
---
We evaluate I (t) using a straight-line approximation of f(t) in the interval                                                                                                                                        f                                                                                                            t n  ≤ t ≤ tn+1 (Fig.
B.3). Let fn  = f(t n )                                                                            and fn+1  = f(t n+1 ). The step size ∆t n may be adjusted based on the
magnitude of the fractional increase in bubble radius calculated for the preceding
integration step ∆tn-1.



                                                        f n+1
                                                                                                                                                                                                                                       Slope = S f

                                                                                                                                                                                                                                       n
                                                                                                           f(t) = f n + S fn (t – t n)



                                                                 f n
                                                                                                                                                                                                                                     ∆t n

                                                                                                                                                                                                                                                                                      (t n+1 – t)



                                                                                                                                                         t n                                                    t                                                                                                                   t n+1



                                                     Fig. B.3: Straight-line approximation of                                                                                                                                                      f(t) in the interval                                     t n  ≤ t ≤ tn+1.



Applying the trapezoidal rule of integration in the interval [tn  , t n+1 ],



                                        If(tn+1)                                   −         If(tn)                             =           fn            +fn+1                   (tn+1−tn)                              =       fn   +fn+1                          ∆tn                  =        ∆tn   .                                                  (B.74)

                                                                                                                                                              2                                                                            2                                                         θn



where θ                                                                                                                             n=                                                                                                                               2                                                                                              is the “time constant” for the nth integration step. For the interval [t ,
t n+1], we have+fn+1                                                                                                 fn
                    If(tn+1)                                          −           If(t)                          =            f(t)+fn+1(tn+1−t)                                                                       =        fn    +Sfn                         (t−tn)+fn+1(tn+1−t)
                                                                                                                                                     2                                                                                                                       2



                                                                                                                 =           fn              +fn+1+Sfn                                         (t−tn)[ n+1−tn)                                                                                                                                                                                                                (t                                                                                                      −      (t     −          tn)]

                                                                                                                                                                            2



where S f n =
                                                                      fn+                                                                                                                                        1−                                                                                                           fn                                                                                                                     is the slope of f(t) in the interval [tn  , tn+1 ]. In terms of δ, the above
                                                                                   ∆tn
equation reads



                    If(tn+1)                                  −                                                                                                                                 If(δ)                                                                                                                      =                                                                                                                     n
                                                                                                                    f                 +fn+1                             +    Sfn                                                                                                                                                                        2δ(∆tn−                                                                                                                                                                       δ)      =     ∆tn  −        δ  +  Sfn  2δ(∆tn  −  δ)  (B.75)
                                                                                                                    
                                                                                                                                           2                                                
                                                                                                                                                                                                                                                      θn



                                                                                                                                                                                                                         B-32
---
The function g(t) is approximated in a similar fashion by a straight line in the interval [tn, tn+1]:

$$g(\delta) = g_n + S_{g_n}\delta, 0 \leq \delta \leq \Delta t_n, \delta = t - t_n,$$ (B.76)

where gn = g(tn) and $S_{g_n} = \frac{g_{n+1} - g_n}{\Delta t_n}$ is the slope of g(t) in the interval [tn, tn+1].

Substituting Eqs. (B.74), (B.75), and (B.76) into Eq. (B.73) yields

$$x_{n+1} = x_n \exp\left(-\frac{\Delta t_n}{\theta_n}\right) + I_{\phi_n},$$ (B.77)

where $I_{\phi_n}$ is the contribution to the solution due to g(t) in Eq. (B.3). It is the particular integral given by

$$I_{\phi_n} = \int_0^{\Delta t_n} [g_n + S_{g_n}\delta]\exp\left[-\left(\frac{\Delta t_n - \delta}{\theta_n} + \frac{S_{f_n}\delta}{2}(\Delta t_n - \delta)\right)\right] d\delta.$$ (B.78)

A closed-form expression for $I_{\phi_n}$ is not possible because of the δ² term contained in the exponent of the exponential factor. We could evaluate the integral using the trapezoidal rule of integration, but a more accurate evaluation is obtained by expanding the exponential factor in series form and truncating the series to a few terms. The truncated series will be valid only if the magnitude of the exponent is less than unity. Here the magnitude is

$$\left|\frac{\Delta t_n - \delta}{\theta_n} + \frac{S_{f_n}\delta}{2}(\Delta t_n - \delta)\right| = (\Delta t_n - \delta)\left|\frac{1}{\theta_n} + \frac{S_{f_n}\delta}{2}\right|$$ because (Δtn - δ) ≥ 0

$$= (\Delta t_n - \delta)\left|\frac{f_n + f_{n+1}}{2} + \frac{f_{n+1} - f_n}{2\Delta t_n}\delta\right|$$ substituting for θn and Sfn

$$\leq (\Delta t_n - \delta)\left|\frac{f_n + f_{n+1}}{2} + \frac{f_{n+1} - f_n}{2}\right|$$ because δ ≤ Δtn

$$\leq (\Delta t_n - \delta)|f_{n+1}|,$$

which may not be less than unity, even with very small values of step size Δtn.
Therefore, we split the exponential factor into two factors and express $I_{\phi_n}$ as

B-33
---

$$I_{\phi_n} = \int_0^{\Delta t_n} [g_n + S_{g_n}\delta]\exp\left[-\frac{\Delta t_n - \delta}{\theta_n}\right]\exp\left[-\frac{S_f \delta}{2}(\Delta t_n - \delta)\right] d\delta. \tag{B.79}$$

Now, the exponent of the second (right most) exponential factor in Eq. (B.79) has a magnitude

$$\left|\frac{S_{f_n} \delta}{2}(\Delta t_n - \delta)\right| = (\Delta t_n - \delta)\left|\frac{f_{n+1} - f_n}{2\Delta t_n}\delta\right| \quad \text{substituting for } \theta_n \text{ and } S_{f_n}$$

$$\leq \Delta t_n \frac{|f_{n+1} - f_n|}{2} \quad \text{because } \delta \leq \Delta t_n.$$

Thus, the magnitude is no greater than the product of the step size $\Delta t_n$ at the $n^{th}$ integration step and the change in $f_n$ therein, a magnitude that is consequently less than unity for sufficiently small values of the step size. Depending on the choice of step size, Eq. (B.79) may thus be evaluated to appropriate accuracy with a truncated series expansion of the second exponential factor.

We proceed by rewriting Eq. (B.79) with a series expansion of the second exponential factor truncated to include terms only through order 2:

$$I_{\phi_n} = \int_0^{\Delta t_n} \exp\left[-\frac{\Delta t_n - \delta}{\theta_n}\right][g_n + S_{g_n}\delta]\exp\left[-\frac{S_f \delta}{2}(\Delta t_n - \delta)\right] d\delta$$

$$= \exp\left[-\frac{\Delta t_n}{\theta_n}\right]\int_0^{\Delta t_n} \exp\left[\frac{\delta}{\theta_n}\right][g_n + S_{g_n}\delta]\left[1 - \frac{S_{f_n} \delta}{2}(\Delta t_n - \delta) + \frac{(S_{f_n} \delta)^2}{8}(\Delta t_n - \delta)^2\right] d\delta$$

$$= \exp\left[-\frac{\Delta t_n}{\theta_n}\right]\int_0^{\Delta t_n} \exp\left[\frac{\delta}{\theta_n}\right]\left[
\begin{array}{l}
g_n + S_{g_n}\delta - \frac{g_n(S_{f_n} \delta)}{2}(\Delta t_n - \delta) - \frac{(S_{g_n} \delta)(S_{f_n} \delta)}{2}(\Delta t_n - \delta) \\
+ \frac{g_n(S_{f_n} \delta)^2}{8}(\Delta t_n - \delta)^2 + \frac{(S_{g_n} \delta)(S_{f_n} \delta)^2}{8}(\Delta t_n - \delta)^2
\end{array}
\right] d\delta \tag{B.80}$$

The terms shown in brackets on the right side of Eq. (B.80) contain terms up to order 5 in $\delta$. Since $\delta \leq t - t_n \leq t_{n+1} - t_n \leq \Delta t_n$, and the integration step size $\Delta t_n$ may be chosen as small as desired, we neglect terms of order greater than 2 in $\delta$, and simplify the integral expression for $I_{\phi_n}$ as follows:

$$I_{\phi_n} = \exp\left[-\frac{\Delta t_n}{\theta_n}\right]\int_0^{\Delta t_n} \exp\left[\frac{\delta}{\theta_n}\right]\left[g_n + \left(S_{g_n} - \frac{g_n S_{f_n} \Delta t_n}{2}\right)\delta + \left(\frac{g_n S_{f_n}}{2} - \frac{S_{g_n} S_{f_n} \Delta t_n}{2} + \frac{g_n S_{f_n}^2 \Delta t_n^2}{8}\right)\delta^2\right] d\delta$$

B-34
---
= g_n I_{\phi 0_n} + \left(S_{g_n} - \frac{g_n S_{f_n} \Delta t_n}{2}\right) I_{\phi 1_n} + \left(\frac{g_n S_{f_n}}{2} - \frac{S_{g_n} S_{f_n} \Delta t_n}{2} + \frac{g_n S_{f_n}^2 \Delta t_n^2}{8}\right) I_{\phi 2_n} \qquad (B.81)

where

$$I_{\phi 0_n} = \exp\left(-\frac{\Delta t_n}{\theta_n}\right) \int_0^{\Delta t_n} \exp\left(\frac{\delta}{\theta_n}\right) d\delta = \exp\left(-\frac{\Delta t_n}{\theta_n}\right) \left[\theta_n \exp\left(\frac{\delta}{\theta_n}\right)\right]_0^{\Delta t_n} = \theta_n \left[1-\exp\left(-\frac{\Delta t_n}{\theta_n}\right)\right],$$

$$I_{\phi 1_n} = \exp\left(-\frac{\Delta t_n}{\theta_n}\right) \int_0^{\Delta t_n} \delta\exp\left(\frac{\delta}{\theta_n}\right) d\delta = \exp\left(-\frac{\Delta t_n}{\theta_n}\right) \left[(\theta_n \delta - \theta_n^2)\exp\left(\frac{\delta}{\theta_n}\right)\right]_0^{\Delta t_n}$$

$$= \exp\left(-\frac{\Delta t_n}{\theta_n}\right) \left[(\theta_n \Delta t_n - \theta_n^2)\exp\left(\frac{\Delta t_n}{\theta_n}\right) + \theta_n^2\right]$$

$$= (\theta_n \Delta t_n - \theta_n^2) + \theta_n^2 \exp\left(-\frac{\Delta t_n}{\theta_n}\right)$$

$$= \theta_n^2 \left[\frac{\Delta t_n}{\theta_n} - \left\{1-\exp\left(-\frac{\Delta t_n}{\theta_n}\right)\right\}\right],$$

and

$$I_{\phi 2_n} = \exp\left(-\frac{\Delta t_n}{\theta_n}\right) \int_0^{\Delta t_n} \delta^2 \exp\left(\frac{\delta}{\theta_n}\right) d\delta = \exp\left(-\frac{\Delta t_n}{\theta_n}\right) \left[(\theta_n \delta^2 - 2\theta_n^2 \delta + 2\theta_n^3)\exp\left(\frac{\delta}{\theta_n}\right)\right]_0^{\Delta t_n}$$

$$= \exp\left(-\frac{\Delta t_n}{\theta_n}\right) \left[(\theta_n \Delta t_n^2 - 2\theta_n^2 \Delta t_n + 2\theta_n^3)\exp\left(\frac{\Delta t_n}{\theta_n}\right) - 2\theta_n^3\right]$$

$$= (\theta_n \Delta t_n^2 - 2\theta_n^2 \Delta t_n + 2\theta_n^3) - 2\theta_n^3 \exp\left(-\frac{\Delta t_n}{\theta_n}\right)$$

$$= \theta_n^3 \left[\left(\frac{\Delta t_n}{\theta_n}\right)^2 - 2\left(\frac{\Delta t_n}{\theta_n}\right) + 2\left\{1-\exp\left(-\frac{\Delta t_n}{\theta_n}\right)\right\}\right].$$

Substituting for $I_{\phi 0_n}$, $I_{\phi 1_n}$, and $I_{\phi 2_n}$ in Eq. (B.81), we obtain

B-35
---
$$I_{\phi_n} = g_n \theta_n \left\{1-\exp\left(-\frac{\Delta t_n}{\theta_n}\right)\right\} + \left(S_{g_n} - \frac{g_n S_{f_n} \Delta t_n}{2}\right) \theta_n^2 \left[\frac{\Delta t_n}{\theta_n} - \left\{1-\exp\left(-\frac{\Delta t_n}{\theta_n}\right)\right\}\right]$$

$$+ \left(\frac{g_n S_{f_n}}{2} - \frac{S_{g_n} S_{f_n} \Delta t_n}{2} + \frac{g_n S_{f_n}^2 \Delta t_n^2}{8}\right) \theta_n^3 \left[\left(\frac{\Delta t_n}{\theta_n}\right)^2 - 2\left(\frac{\Delta t_n}{\theta_n}\right) + 2\left\{1-\exp\left(-\frac{\Delta t_n}{\theta_n}\right)\right\}\right] \qquad (B.82)$$

Returning to Eq. (B.77), we can calculate x_{n+1} at the n^th integration step knowing x_n from the previous step and the solution for I_{\phi_n} in Eq. (B.82). However, the solution for I_{\phi_n} requires f_{n+1} and g_{n+1} (and thus the unknown r_{n+1}) to determine the slopes S_{f_n} and S_{g_n}. This poses no problem if the functions f(t) and g(t) are known functions of time. In our application, f(t) and g(t) are implicit functions of time related through bubble radius, as indicated by Eqs. (B.1) and (B.2). We solve for bubble radius and bubble pressure simultaneously by applying Eq. (B.77) as well as the constitutive equation for bubble pressure (Young-LaPlace relationship), as indicated by Eqs. (B.12) and (B.14).

The expression for I_{\phi_n} also contains f_{n+1} in the exponential factors. Without further simplification, the expression becomes a nonlinear equation in r_{n+1}, or equivalently in the change in bubble radius δr_n, which requires an iterative solution at each integration step — a significant increase in computational overhead. In order to reduce the computations, the expression for I_{\phi_n} in Eq. (B.82) is simplified by first expanding the exponential factors in series form and retaining only terms up to third order:

$$\left\{1-\exp\left(-\frac{\Delta t_n}{\theta_n}\right)\right\} = 1 - \left[1 - \frac{\Delta t_n}{\theta_n} + \frac{1}{2}\left(\frac{\Delta t_n}{\theta_n}\right)^2 - \frac{1}{6}\left(\frac{\Delta t_n}{\theta_n}\right)^3 + ......\right]$$

$$\approx \frac{\Delta t_n}{\theta_n} - \frac{1}{2}\left(\frac{\Delta t_n}{\theta_n}\right)^2 + \frac{1}{6}\left(\frac{\Delta t_n}{\theta_n}\right)^3 . \qquad (B.83)$$

With appropriate substitution of Eq. (B.83), Eq. (B.82) becomes

B-36
---

$$I_{\phi_n} = g_n \theta_n \left\{ \frac{\Delta t_n}{\theta_n} - \frac{1}{2} \left( \frac{\Delta t_n}{\theta_n} \right)^2 + \frac{1}{6} \left( \frac{\Delta t_n}{\theta_n} \right)^3 \right\}$$

$$+ \left( S_{g_n} - \frac{g_n S_{f_n} \Delta t_n}{2} \right) \theta_n^2 \left[ \frac{\Delta t_n}{\theta_n} - \left\{ \frac{\Delta t_n}{\theta_n} - \frac{1}{2} \left( \frac{\Delta t_n}{\theta_n} \right)^2 + \frac{1}{6} \left( \frac{\Delta t_n}{\theta_n} \right)^3 \right\} \right]$$

$$+ \left( \frac{g_n S_{f_n}}{2} - \frac{S_{g_n} S_{f_n} \Delta t_n}{2} + \frac{g_n S_{f_n}^2 \Delta t_n^2}{8} \right) \theta_n^3 \left[ \left( \frac{\Delta t_n}{\theta_n} \right)^2 - 2 \left( \frac{\Delta t_n}{\theta_n} \right) + 2 \left\{ \frac{\Delta t_n}{\theta_n} - \frac{1}{2} \left( \frac{\Delta t_n}{\theta_n} \right)^2 + \frac{1}{6} \left( \frac{\Delta t_n}{\theta_n} \right)^3 \right\} \right]$$

$$= g_n \left( \Delta t_n - \frac{\Delta t_n^2}{2\theta_n} + \frac{\Delta t_n^3}{6\theta_n^2} \right) + \left( S_{g_n} - \frac{g_n S_{f_n} \Delta t_n}{2} \right) \left( \frac{\Delta t_n^2}{2} - \frac{\Delta t_n^3}{6\theta_n} \right)$$

$$+ \left( \frac{g_n S_{f_n}}{2} - \frac{S_{g_n} S_{f_n} \Delta t_n}{2} + \frac{g_n S_{f_n}^2 \Delta t_n^2}{8} \right) \frac{\Delta t_n^3}{3}. \tag{B.84}$$

We now substitute $S_{g_n} = \frac{g_{n+1} - g_n}{\Delta t_n}$ and $S_{f_n} = \frac{f_{n+1} - f_n}{\Delta t_n}$ in Eq. (B.84), cancel out $\Delta t_n$ in the numerator and the denominator of various terms, and retain only terms up to order 2 in $\Delta t_n$ to obtain

$$I_{\phi_n} = g_n \left( \Delta t_n - \frac{\Delta t_n^2}{2\theta_n} + \frac{\Delta t_n^3}{6\theta_n^2} \right) + \left( S_{g_n} - \frac{g_n S_{f_n} \Delta t_n}{2} \right) \left( \frac{\Delta t_n^2}{2} - \frac{\Delta t_n^3}{6\theta_n} \right)$$

$$+ \left( \frac{g_n S_{f_n}}{2} - \frac{S_{g_n} S_{f_n} \Delta t_n}{2} + \frac{g_n S_{f_n}^2 \Delta t_n^2}{8} \right) \frac{\Delta t_n^3}{3}$$

$$= g_n \left( \Delta t_n - \frac{\Delta t_n^2}{2\theta_n} \right) + (g_{n+1} - g_n) \left( \frac{\Delta t_n}{2} - \frac{\Delta t_n^2}{6\theta_n} \right) - \frac{g_n (f_{n+1} - f_n)}{2} \left( \frac{\Delta t_n^2}{2} \right)$$

$$+ \frac{g_n (f_{n+1} - f_n)}{2} \left( \frac{\Delta t_n^2}{3} \right) - \frac{(g_{n+1} - g_n)(f_{n+1} - f_n)}{2} \left( \frac{\Delta t_n^2}{3} \right)$$

$$= [2g_n + (g_{n+1} - g_n)] \frac{\Delta t_n}{2} - \left[ \frac{g_n}{2} + \frac{g_{n+1} - g_n}{6} \right] \left( \frac{\Delta t_n^2}{\theta_n} \right) - \left[ \frac{g_n}{2} - \frac{g_n}{3} + \frac{g_{n+1} - g_n}{3} \right] \frac{(f_{n+1} - f_n)}{2} \Delta t_n^2$$

$$= (g_n + g_{n+1}) \frac{\Delta t_n}{2} - \frac{2g_n + g_{n+1}}{6} \frac{f_n + f_{n+1}}{2} \Delta t_n^2 - \frac{2g_{n+1} - g_n}{6} \frac{(f_{n+1} - f_n)}{2} \Delta t_n^2$$

B-37
---
Substituting $\theta_n = \frac{2}{f_n + f_{n+1}}$,

$$I_{\phi_n} = (g_n + g_{n+1})\frac{\Delta t_n}{2} - \frac{2g_n + g_{n+1}}{6} \frac{f_n + f_{n+1}}{2} \Delta t_n^2 - \frac{2g_{n+1} - g_n}{6} \frac{(f_{n+1} - f_n)}{2} \Delta t_n^2$$

$$= (g_n + g_{n+1})\frac{\Delta t_n}{2} - [(2g_n + g_{n+1})(f_n + f_{n+1}) + (2g_{n+1} - g_n)(f_{n+1} - f_n)]\frac{\Delta t_n^2}{12}$$

$$= (g_n + g_{n+1})\frac{\Delta t_n}{2} - [3(g_nf_n + g_{n+1}f_{n+1}) + (g_nf_{n+1} - g_{n+1}f_n)]\frac{\Delta t_n^2}{12}$$ (B.85)

Eq. (B.85) is a second-order approximation to $I_{\phi_n}$. Note that this does not compromise accuracy as we already limited $I_{\phi_n}$ to terms containing powers of $\Delta t_n$ less than 3 to obtain Eq. (B.81). It is not necessary to include higher power terms in $\Delta t_n$ as accuracy may be improved to any desired level by sufficiently decreasing the step size.

Returning to the solution Eq. (B.77), we expand the exponential factor retaining only terms up to order 2 in $\Delta t_n$ so that

$$x_{n+1} = x_n \exp\left(-\frac{\Delta t_n}{\theta_n} + I_{\phi_n}\right) = x_n\left[1 - \frac{\Delta t_n}{\theta_n} + \frac{1}{2}\left(\frac{\Delta t_n}{\theta_n}\right)^2 + I_{\phi_n}\right].$$ (B.86)

Substituting for $I_{\phi_n}$ from Eq. (B.85) and $\theta_n = \frac{2}{f_n + f_{n+1}}$ into Eq. (B.86) yields

$$x_{n+1} = x_n - x_n(f_n + f_{n+1})\frac{\Delta t_n}{2} + x_n(f_n + f_{n+1})^2 \frac{\Delta t_n^2}{8}$$ 

$$+ (g_n + g_{n+1})\frac{\Delta t_n}{2} - [3(g_nf_n + g_{n+1}f_{n+1}) + (g_nf_{n+1} - g_{n+1}f_n)]\frac{\Delta t_n^2}{12}$$ (B.87)

Equation (B.87) simplifies to our final expression for $x_{n+1}$:

$$x_{n+1} = x_n + [(g_n + g_{n+1}) - (f_n + f_{n+1})x_n]\frac{\Delta t_n}{2} + [(f_n + f_{n+1})^2x_n]\frac{\Delta t_n^2}{8}$$

$$- [3(g_nf_n + g_{n+1}f_{n+1}) + (g_nf_{n+1} - g_{n+1}f_n)]\frac{\Delta t_n^2}{12}$$ (B.88)

B-38
---
# 10. Appendix C. Summary of Recursive Equations for Solution of 3RUT-MBe1 Model

Subscripts:
- Compartments: i = 1, 2, ..., nc (suppressed)
- Bubble size group: m = 1, 2, ..., Nbs (suppressed)
- Diffusible gases: k = 1, 2, ..., Ng
- Time intervals: n = 1, 2, ...

Number of bubble size groups: Nbs = 1

Scaled model parameters:

| Parameter | Equation |
|-----------|----------|
| r̂ = Λr | K̄k = 3Λ²Kk |
| r̂⁰min = Λr⁰min | r̂minn = Λrminn |
| β̂⁰ = Λβ⁰ | β̂fn = Λβfn |
| V̂t = Λ³Vt | |

σ̄ = Λσ

M̄ = (4π/3) M/Λ³

σ̄c = Λσc

P∞ = PH₂O + ptCO₂ (C.1)

tn+1 = tn + Δtn (C.2)ᵃ

## Bubble Number

βexn = 1 + mβexIexn (C.3)

Pcrushn = MAX[Pcrushn-1, (Pambn - P∞) - ∑ᵏ⁼¹ᴺᵍ ptk,n] (C.4)ᵇ

ᵃ The integration step size Δtn is arbitrary and may be altered at any integration step, based on the magnitude of changes in bubble radii, δrn, to reduce computation time, but it should be small enough to yield results with desired accuracy.

ᵇ The initial Pcrush₀ ≡ P⁰crush is determined from saturation conditions at profile start (see footnotes c and e in this Appendix).

C-1
---

If $P_{\text{crush}_n} \leq P_{\text{crush}_{n-1}}$, $P_{\text{crush}_n} = P^o_{\text{crush}} + (P_{\text{crush}_{n-1}} - P^o_{\text{crush}}) \cdot \exp(-\Delta t_n / \tau_{P_c})$ (C.5)

$$\hat{\beta}_{f_n} = \beta_{\text{ex}_n} \left[ \frac{2\hat{\sigma}_c \hat{\beta}^o}{2(\hat{\sigma}_c - \hat{\sigma}) + P_{\text{crush}_n} \hat{r}^o_{\text{min}}} \right]; \hat{r}^o_{\text{min}} = \hat{\beta}^o \left| \ln(N^o_b) - \ln(N^{\text{min}}_b) \right|$$ (C.6)

$$P_{\text{ss}_n} = \left[ \sum_{k=1}^{N_g} p_{t_{k,n}} + P_\infty \right] - P_{\text{amb}_n}$$ (C.7)

$$N_{b_{\text{max},n}} = \text{MAX} \left[ N_{b_{\text{max},n-1}}, N^o_b \exp \left( -\frac{2\hat{\sigma}}{P_{\text{ss}_n} \cdot \hat{\beta}_{f_n}} \right) \right]$$ (C.8)

$\Delta n_{b_n} = |N_{b_{\text{max},n}} - N_{b_{\text{max},n-1}}|$

$n_{b_n} = n_{b_{n-1}} + \Delta n_{b_n}$ (C.9)

$$\hat{r}_{\text{min}_n} = \hat{\beta}_{f_n} \left| \ln(N^o_b) - \ln(N^{\text{min}}_b) \right|$$ (C.10)

$\hat{x}^o_{k,n} = P_{b_{k,n}} \hat{r}^3_{\text{min}_n}$ (C.11)

## Bubble Radius and Pressure

$b_{k,n} = \hat{K}_k \frac{\Delta t_n}{\hat{r}^2_n}$ (C.12)

$a_{k,n} = (1 + \hat{r}_n) b_{k,n}$ (C.13)

$$A_{k,n} = P_{b_{k,n}} + a_{k,n} \left(1 - \frac{a_{k,n}}{2}\right)(p_{t_{k,n}} - P_{b_{k,n}})$$ (C.14)

$$B_{k,n} = \frac{1}{2}[(2a_{k,n} - b_{k,n} + a_{k,n}b_{k,n})p_{t_{k,n}} + (a_{k,n} + b_{k,n})(1-a_{k,n})P_{b_n}]$$ (C.15)

$$\delta \hat{r}_n = \frac{\sum_{k=1}^{N_g} A_{k,n} - \left(P'_{\text{amb}_{n+1}} + \frac{2\hat{\sigma}}{\hat{r}_n} + M\hat{r}^3_n\right)}{\sum_{k=1}^{N_g} (3A_{k,n} - B_{k,n}) - \left(\frac{2\hat{\sigma}}{\hat{r}_n} - 3M\hat{r}^3_n\right)}; P'_{\text{amb}} = P_{\text{amb}} - P_\infty$$ (C.16)

$\hat{r}_{n+1} = \hat{r}_n (1 + \delta \hat{r}_n)$ (C.17)

C-2
---
$$P_{b_{k,n+1}} = A_{k,n} - (3A_{k,n} - B_{k,n})δ^3_{r_n}$$ (C.18)

## Tissue Gas Tensions

$$\dot{V}_{O_2,n} = m_{VO_2} \cdot I_{ex_n} + \dot{V}_{O_2,rest}$$ (C.19)

$$\dot{Q}_{ex_n} = m_Q \cdot (\dot{V}_{O_2,n} - \dot{V}_{O_2,rest}) + Q_{rest}$$ (C.21)

## Inert Gases

$$τ_{k_n} = \frac{α_{t_k}}{α_{b_k}\dot{Q}_n}$$ (C.23)

$$ε_{k,n} = 1 - exp\left(-\frac{Δt_n}{τ_{k_n}}\right)$$ (C.24)

$$\hat{G}_{k_n} = \left(\frac{4π}{3}\right)α_{t_k}\hat{V}_t\frac{n_{b_n}}{n_{b_{n-1}}} = \hat{G}_{k_{n-1}}\frac{n_{b_n}}{n_{b_{n-1}}}$$ (C.25)

$$Δ\hat{G}_{k_n} = \left(\frac{4π}{3}\right)α_{t_k}\hat{V}_t\frac{Δn_{b_n}}{n_{b_n}}$$ (C.26)

$$\hat{x}_{k,n+1} = P_{b_{k,n+1}}r^3_{n+1}$$ (C.27)

$$p_{a_{k,n+1}} = p_{a_k}@t_{n+1} = F_{I_{k,n+1}}\left[(P_{amb_{n+1}} - P_{AH_2O}) - P_{ACO_2}\left(1 - \frac{1}{RQ}\right)\right]$$ (C.28)

$$υ_{k,n} = \frac{p_{a_{k,n+1}} - p_{a_{k,n}}}{Δt_n}$$ (C.29)

C-3
---
$$p_{t_{k,n+1}} = p_{t_{k,n}}(1-\varepsilon_{k,n}) + v_{k,n}\Delta t_n + \left[p_{a_{k,n}} - \tau_k \left\{v_{k,n} + \hat{G}_{k_n} \frac{\hat{x}_{k,n+1} - \hat{x}_{k,n}}{\Delta t_n}\right\}\right]\varepsilon_{k,n}$$

$$- \Delta\hat{G}_{k_n}(\hat{x}_{k,n} - \hat{x}^o_{k,n})$$

(C.30)^c

**Oxygen**

$$\alpha'_{O_{2_n}} = \alpha_{b_{O_2}} + Hb_c \left[\frac{a_1 + 2a_2p - a_2(a_1 - b_1p^2)}{(1.0 + b_1p + b_2p^2)^2}\right]\left[\frac{np^{\eta-1}}{P_{half}}\right]; p = \left(\frac{p^v_{O_{2_n}}}{P_{half}}\right)^\eta$$

(C.31)

$$\tau_{O_{2_n}} = \frac{\alpha_{t_{O_2}}}{Q_n \alpha'_{O_{2_n}}}$$

(C.32)

$$\varepsilon_{O_{2_n}} = 1 - \exp\left(-\frac{\Delta t_n}{\tau_{O_{2_n}}}\right)$$

(C.33)

$$\hat{G}_{O_{2_n}} = \left(\frac{4\pi}{3}\right)\frac{n_{b_n}}{\alpha_{t_{O_2}}\hat{V}_t} = \hat{G}_{O_{2_{n-1}}}\left(\frac{n_{b_n}}{n_{b_{n-1}}}\right)$$

(C.34)

$$\Delta\hat{G}_{O_{2_n}} = \left(\frac{4\pi}{3}\right)\frac{\Delta n_{b_n}}{\alpha_{t_{O_2}}\hat{V}_t}$$

(C.35)

$$\hat{x}_{O_{2_{n+1}}} = P_{b_{O_{2_{n+1}}}}\hat{r}^3_{n+1}$$

(C.36)

$$p_{a_{O_{2_{n+1}}}} = p_{a_{O_2}} @ t_{n+1} = P_{amb_{n+1}} - P_{H_2O} - P_{A_{CO_2}} - \sum p_{a_{k,n+1}}$$

(C.37)

^c The initial tissue tension of the k^th inert gas under saturation steady-state conditions, $p_{t_{k,0}}$, is the aterial tension, $p_{a_{k,0}}$, for the gas given by Eq. (C.28) for the saturation pressure and breathing gas mix.

C-4
---
$$C_{aO_2,n} = \alpha_{bO_2}p_{aO_{2_n}} + Hb_cSO_2(@ PO_2 = p_{aO_{2_n}})$$ (C.38)^d

$$C_{aO_2,n+1} = \alpha_{bO_2}p_{aO_{2_{n+1}}} + Hb_cSO_2(@ PO_2 = p_{aO_{2_{n+1}}})$$ (C.39)^c

$$pO'_{2_n} = \frac{C_{aO_2,n}}{\alpha'_{O_{2_n}}} ; pO'_{2_{n+1}} = \frac{C_{aO_2,n+1}}{\alpha'_{O_{2_n}}}$$ (C.40)

$$υO_{2_n} = \frac{pO'_{2_{n+1}} - pO'_{2_n}}{\Delta t_n}$$ (C.41)

$$C_{vO_2,n} = \alpha_{bO_2}p_{vO_{2_n}} + Hb_cSO_2(@ PO_2 = p_{vO_{2_n}})$$ (C.42)

$$\dot{ρ}_n = \frac{\dot{V}_{O_{2_n}} + Q_n(C_{vO_{2_n}} - \alpha'_{O_{2_n}}p_{vO_{2_n}})}{\alpha_{TO_2}}$$ (C.43)

^d The percent hemoglobin saturation, SO₂, at prevailing oxygen tension pO₂ is computed with Lobdell's equation:^69

$$SO_2 = \frac{a_1p + a_2p^2}{1.0 + b_1p + b_2p^2}; p = \left(\frac{pO_2}{p_{half}}\right)^η,$$

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
$$p_{tO_{2_{n+1}}} = p_{tO_{2_n}}(1-\varepsilon_{O_{2_n}}) + \nu_{O_{2_n}}\Delta t_n$$

$$+ \left[p'_{O_{2_n}} - \tau_{O_{2_n}}\left\{\nu_{O_{2_n}} + \dot{p}_n + \dot{G}_{O_{2_n}}\frac{(\hat{x}_{O_{2_{n+1}}} - \hat{x}_{O_{2_n}})}{\Delta t_n}\right\}\right]\varepsilon_{O_{2_n}} \qquad (C.44)^e$$

$$- \Delta\dot{G}_{O_{2_n}}(\hat{x}_{O_{2_n}} - \hat{x}_{O_{2_n,0}})$$

## VGE formation

$$LR = (V_b - V_{r0})N_{VGE}\Delta t_n, \qquad (C.45)$$

$$n_{b_{n+1}} = MAX[0, N_{b_n}(1-LR)], \qquad (C.46)$$

e The initial tissue O₂ tension under saturation steady-state conditions, $p_{tO_{2_0}}$, is the partial pressure, $p_{vO_{2_0}}$, corresponding to $C_{vO_{2_0}} = C_{aO_{2_0}} - \frac{V_{O_{2_0}}}{Q_0}$, where $C_{aO_{2_0}}$ is given by Eq. (C.38) at $p_{aO_2}$ given by Eq. (C.37) for the saturation pressure and breathing gas mix. $p_{vO_{2_0}}$ is determined by numerically inverting the blood O₂ content versus partial pressure curve, Eq. (C.42), at $C_{vO_{2_0}}$.

C-6
---
## 11. Appendix D. Hazard Function Formulation and Optimization

The hazard function in present work was elaborated from that in the BVM(3) probabilistic gas and bubble dynamics model developed earlier for air and N₂-O₂ diving.²⁶'²⁷ In the latter model, the instantaneous risk of DCS at time t in exposure i, h₁(t), is the sum of a weighted time-dependent dose, Δᵢ,ⱼ(t), in each of j = 1, 2, ..., nᶜ hypothetical tissue compartments. That is,

$$h_i(t) = \sum_{j=1}^{n_c} w_j\Delta_{i,j}(t),$$  (D.1)

where wⱼ is the weight – constant over all i and independent of time and all parameters in Δᵢ,ⱼ(t) – associated with the jᵗʰ compartment, and

$$\Delta_{i,j}(t) = [V_{i,j}(t) - V_j(0)].$$  (D.2)

Vᵢ,ⱼ(t) in Eq. (D.2) is the bubble volume in the jᵗʰ compartment at time t in the iᵗʰ exposure, and Vⱼ(0) is the initial nucleonic bubble volume in the compartment. The initial nucleonic bubble volume in each compartment is constant and the same for all exposures. Because the hazard, hᵢ(t), is a failure rate that must integrate over time to a dimensionless quantity, wⱼ in Eq. (D.1) has dimensions of 1/(volume × time).

While an implementation of the Van Liew and Hlastala two-region unstirred tissue model²⁸'³¹'⁷⁰ was used to model bubble evolution in the BVM(3) probabilistic model, the more theoretically robust 3RUT-MB model was used for this purpose in present work. Eq. (D.2) was elaborated using Eq. (A.12) to obtain the hazard function used in present work:

$$h(t) = \sum_j^{n_c} w_j (V_{b,j} - V_{r0j}) \cdot (N_{b,j})^{\beta_{N,j}},$$  (D.3a)

where m=1 has been assumed, the time-dependence of the compartmental bubble number is explicitly indicated, and a compartment-specific power term, βN,j, for the prevailing bubble number has been arbitrarily added to potentiate the contribution of the bubble number to the hazard as the bubble number increases.

It is shown in Appendix A that the compartmental bubble volumes in the 3RUT-MB model scale with an arbitrary compartmental Λⱼ³ factor having dimension 1/volume. The scaled counterparts of the volumes in Eq. (D.3a), V̂ᵢ,ⱼ(t) = Λⱼ³Vᵢ,ⱼ(t) and

D-1
---
$\hat{V}_j(0) = \Lambda_j^3V_j(0)$, can then be calculated with the piecewise-analytic solution derived in Appendix B with arbitrarily specified values of $\Lambda_j$.

The best fit of a given expression for h(t) to a collection of DCS incidence and time of onset data is obtained by adjusting the parameters of h(t) to maximize the likelihood of h(t) about the data. The likelihood is the joint probability of the observed outcomes for all exposures in the data. For N independent exposures, the likelihood is given by

$$L = \prod_{i=1}^N P(0_i)^{1-\delta_i} P(E_i)^{\delta_i},\tag{D.4}$$

where $\delta_i$ is the outcome variable for the $i^{th}$ exposure: $\delta_i = 1$ for failure (event occurred) and $\delta_i = 0$ for no failure until end of observation (right-censored observation). Marginal outcomes, for which $0 < \delta_i < 1$, are also allowed. Referring to Eqs. (1) and (2) in the body of this report, Eq. (D.4) is elaborated to yield

$$L = \prod_{i=1}^N \left[\left\{\exp\left(-\int_0^{t_i}h_i(t)dt\right)\right\}^{(1-\delta_i)}\left\{\exp\left(-\int_0^{t_{1i}}h_i(t)dt\right)\right\}^{\delta_i}\left\{1-\exp\left(-\int_{t_{1i}}^{t_{2i}}h_i(t)dt\right)\right\}^{\delta_i}\right],\tag{D.5}$$

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
---
| Data Set | Profile Description Summary | # Exposures | # DCS Observed |
|----------|----------------------------|-------------|----------------|
| EffctEx-V | 60 min PB; 20.0K ft isometric stacked weight, arm exercise/240 min | 1 | 1 |
| EffctEx-W | 60 min PB; 20.0K ft isotonic stacked weight, arm exercise/240 min | 1 | 1 |
| EffctEx-X | 60 min PB; 20.0K ft isometric stacked weight, leg exercise/240 min | 1 | 1 |
| EffctEx-Y | 60 min PB; 20.0K ft isotonic stacked weight, leg exercise/240 min | 1 | 0 |
| 35K-A | 75 min PB;35K ft rest/180 min, males | 37 | 21 |
| 35K-B | 75 min PB;35K ft, 30% VO₂ peak exercise/180 min, males | 30 | 28 |
| 35K-C | 75 min PB;35K ft rest/180 min, females | 36 | 19 |
| 35K-D | 75 min PB;35K ft, 30% VO2 peak exercise/180 min, females | 31 | 31 |
| 40K-A | 90 min PB; 40K ft (2.72 psia) resting/90 min | 40 | 18 |
| ZPB-A | Bends Threshold study: 0PB; 22.5 K ft, rest/360 min, males | 20 | 12 |
| ZPB-B | Bends Threshold study: 0PB; 22.5 K ft, EVA sim/360 min, males | 21 | 7 |
| ZPB-C | Bends Threshold study: 0PB; 21.2 K ft, EVA sim/360 min, males | 20 | 1 |
| ZPB-D | Bends Threshold study: 0PB; 23.8 K ft, EVA sim/360 min, males | 10 | 5 |
| PE1-A | 60 min PB (10 min 75% VO₂ peak exercise, 50 min rest); 30K ft EVA sim/240 min | 26 | 11 |
| PE1-B | 60 PB (rest), EVA sim/240 min | 28 | 21 |
| PE2-A | 240 min PB (rest); EVA sim/240 min | 32 | 15 |
| PE2-B | 90 min PB (rest); EVA sim/240 min | 32 | 21 |
| MV-A | ADRAC Validation A) 90 min PB; 35K ft EVA sim/180 min | 31 | 29 |
| MV-B | ADRAC Validation B) 30 min PB; 25K ft, 30% VO₂ peak exercise-rest cycles/240 min | 31 | 19 |
| MV-C | ADRAC Validation C) 15 min PB; 22.5K ft, 30% VO₂ peak exercise-rest cycles/240 min | 30 | 9 |
| MV-D | ADRAC Validation D) 0PB; 18.0K ft, 30% VO₂ peak exercise-rest cycles/360 min | 30 | 4 |
| MV-E | ADRAC Validation E) 75 min PB; 30K ft rest/240 min | 31 | 18 |

**NASA**

| Data Set | Profile Description Summary | # Exposures | # DCS Observed |
|----------|----------------------------|-------------|----------------|
| Test 1a; Rprt 204 | 210 min PB; 4.3 psia LB exercise/3 hr | 11 | 4 |

E-3
---
| Data Set | Profile Description Summary | # Exposures | # DCS Observed |
|----------|----------------------------|-------------|----------------|
| Test 1b; Rprt 206 | 0PB; 10.2 psia*/12hr; 10.2 psia O2/40 min; 4.3 psia LB exercise/3 hr | 13 | 3 |
| Test 1c; Rprt 208 | 0PB; 10.2 psia*/12hr; 10.2 psia O2/90 min; 4.3 psia LB exercise/3 hr | 12 | 4 |
| Test 1d; Rprt 418 | 0PB; 10.2 psia*/18hr; 10.2 psia O2/40 min; 4.3 psia LB exercise/3 hr | 3 | 2 |
| Test 2a; Rprt 209 | 210 min PB; 9.2 psia/10 min; 4.3 psia EVA sim/230 min | 23 | 7 |
| Test 2b; Rprt 211 | 0PB; 10.2 psia*/12hr; 10.2 psia O2/40 min; 9.2 psia/10 min; 4.3 psia EVA sim/240 min | 22 | 6 |
| Test 3a; Rprt 212 | 240 min PB; 9.2 psia/10 min; 4.3 psia EVA sim/350 min | 28 | 6 |
| Test 3b; Rprt 215 | 45 min PB; 10.2 psia*/12hr; 10.2 psia O2/40 min; 4.3 psia EVA sim/350 min | 35 | 8 |
| Test 3c; Rprt 213 | A:[240 min PB; 9.2 psia/10 min; 4.3 psia EVA sim/350 min]; 13hr SI; repeat A | 14 | 3 |
| Test 3d; Rprt 217 | 45 min PB; 10.2 psia*/12hr; A:[10.2 psia O2/40 min; 9.2 psia/10 min; 4.3 psia EVA sim/350 min]; 10.2 psia*/980 min; repeat A | 12 | 2 |
| Test 4a; Rprt 219 | 45 min PB; 10.2 psia*/12hr; 10.2 psia O2/40 min; 9.2 psia/10 min; 4.3 psia EVA sim/170 min | 12 | 1 |
| Test 4b; Rprt 220 | 45 min PB; 10.2 psia*/12hr; A:[10.2 psia O2/40 min; 9.2 psia/10 min; 4.3 psia EVA sim/170 min]; 10.2 psia*/80 min; repeat A | 12 | 0 |
| Test 4c; Rprt 221 | 45 min PB; 10.2 psia*/12hr; A:[10.2 psia O2/40 min; 9.2 psia/10 min; 4.3 psia EVA sim/170 min]; 10.2 psia*/80 min; repeat A; 10.2 psia*/14hr; repeat A | 12 | 0 |
| Test 4d; Rprt 222 | 45 min PB; 10.2 psia*/12hr; A:[10.2 psia O2/40 min; 9.2 psia/10 min; 4.3 psia EVA sim/170 min]; 10.2 psia*/80 min; repeat A; 10.2 psia*/14hr; repeat A; 10.2 psia*/80 min; repeat A | 12 | 0 |
| Test 4e; Rprt 223 | 45 min PB; 10.2 psia*/12hr; A:[10.2 psia O2/40 min; 9.2 psia/10 min; 4.3 psia EVA sim/170 min]; 10.2 psia*/80 min; repeat A; 10.2 psia*/14hr; repeat A; 10.2 psia*/80 min; repeat A; 10.2 psia*/14hr; repeat A | 12 | 0 |
| Test 4f; Rprt 224 | 45 min PB; 10.2 psia*/12hr; A:[10.2 psia O2/40 min; 9.2 psia/10 min; 4.3 psia EVA sim/170 min]; 10.2 psia*/80 min; repeat A; 10.2 psia*/14hr; repeat A; 10.2 psia*/80 min; repeat A; 10.2 psia*/14hr; repeat A; 10.2 psia*/80 min; repeat A | 12 | 0 |
| Test 5a; Rprt 237, 238 | 6hr PB; 4.3 psia EVA sim/360 min | 38 | 4 |
| Test 5b; Rprt 239 | 8hr PB; 4.3 psia EVA sim/360 min | 11 | 0 |
| Test 6; Rprt 241, 243 | 2hr PB; 10.2 psia, 28% O2/24hr; 6.0 psia, 60% O2, EVA sim/6hr | 29 | 1 |
| Test 7a; Rprt 257 | 0PB; 6.5 psia (21K ft) mod EVA sim (~400 kcal/hr)/180 min | 11 | 4 |
| Test 7b; Rprt 258 | 0PB; 6.5 psia (21K ft) mod EVA sim (~200 kcal/hr)/180 min | 11 | 2 |
| Test 8a; Rprt 378, 379 | 0PB; 6.5 psia (21K ft) EVA sim/180 min | 40 | 7 |
| Test 8b; Rprt 378, 379 | 3d x 30 min heavy treadmill exercise/day; 0PB; 6.5 psia (21K ft) EVA sim/180 min | 41 | 10 |
| Test 9a; Rprt 407, 409 | ARGO, Phase I; 0PB; 6.5 psia EVA sim/180 min | 24 | 1 |
| Test 9b; Rprt 408, 410 | ARGO, Phase I: 3d 6deg HDT; 0PB; 6.5 psia EVA sim, nonambulatory/180 min | 23 | 2 |
| Test 9c; Rprt 419, 420 | ARGO, Phase II: 4hr PB; 4.3 psia EVA sim/180 min | 11 | 3 |
| Test 9d; Rprt 421 | ARGO, Phase II: 2hr adynamia, 4hr PB (adynamia); 4.3 psia EVA sim, adynamia/180 min | 7 | 0 |
| Test 9e; Rprt 421 | ARGO, Phase II: 2hr adynamia, 4hr PB (UB exercise, 3.5hr @ 188 kcal/hr); 4.3 psia EVA sim, adynamia/180 min | 7 | 0 |
| Test 10; Rprt 413, 414 | flying after diving: 20fsw (dry), light exercise/400 min; SI, air/14hr; 10.1 psia (10.0K ft), rest/3hr | 19 | 1 |

E-4
---
| Data Set | Profile Description Summary | # Exposures | # DCS Observed |
|----------|----------------------------|-------------|----------------|
| Test 11a; Rprt 453, 454 | ARGO Phase III: 3hr PB; 4.3 psia EVA sim, nonambulatory/240 min | 28 | 3 |
| Test 11b; Rprt 450, 451 | 0PB; 6.5 psia: (2 min walk, 4 min rest) cycles w/VGE dtctn/120 min | 4 | 0 |
| PRP I | NASA Prebreathe Reduction Protocol‡, Phase I | 49 | 9 |
| PRP II | NASA Prebreathe Reduction Protocol‡, Phase II | 50 | 0 |
| PRP III | NASA Prebreathe Reduction Protocol‡, Phase III | 10 | 2 |
| PRP IV | NASA Prebreathe Reduction Protocol‡, Phase IV | 69 | 8.3 |
| | Totals | 2594 | 858.3 |

\* 26.5% O₂

‡ NASA Prebreathe Reduction Program (PRP): Man-trials conducted at Duke University, Memorial Hermann-Texas Medical Center, and Defense and Civil Institute of Environmental Medicine.

Note: Four man-exposures; man-flight numbers 88073, 91097, 93022, and 93033; of the 1194 exposures extracted from the original USAFAL Hypobaric Decompression Sickness Database are not counted in this table but were included in the model training data. Each of these exposures had a unique profile that could not be associated with any study in the database and each culminated with occurrence of DCS.

E-5
---
## 13. Appendix F. Pearson χ2 Statistics for Optimized 3RUT-MBe1 Model on its A1309 Training Data

| Data Set | # Exposures (N) | # DCS Incidents Observed (f) | Predicted A1309-3RUT MBe1 (n) | π | (Pearson Residual)² (f-n)²/n(1-π) | cumulative χ² | P |
|----------|-----------------|------------------------------|-------------------------------|---|-----------------------------------|---------------|---|
| Test 9e | 7 | 0 | 0.000 | 0.00 | 0.000 | 0.00 | --- |
| Bubb Threshold-F | 2 | 0 | 0.000 | 0.00 | 0.000 | 0.00 | --- |
| 8.3 psia-A | 20 | 1 | 0.984 | 0.05 | 0.000 | 0.00 | --- |
| Bubb Threshold-E | 9 | 0 | 0.003 | 0.00 | 0.003 | 0.00 | --- |
| Test 1b | 13 | 3 | 3.090 | 0.24 | 0.003 | 0.01 | --- |
| Test 1a | 11 | 4 | 3.882 | 0.35 | 0.006 | 0.01 | --- |
| MV-D | 30 | 4 | 4.143 | 0.14 | 0.006 | 0.02 | --- |
| Bubb Threshold-D | 6 | 0 | 0.014 | 0.00 | 0.014 | 0.03 | --- |
| Test 3d | 12 | 2 | 2.205 | 0.18 | 0.023 | 0.06 | --- |
| Test 4a | 12 | 1 | 1.172 | 0.10 | 0.028 | 0.08 | --- |
| (9.5 psia, Unknown) | 42 | 0 | 0.034 | 0.00 | 0.034 | 0.12 | --- |
| Test 2a | 23 | 7 | 6.597 | 0.29 | 0.035 | 0.15 | --- |
| 9.5 psia Val-B | 12 | 0 | 0.038 | 0.00 | 0.038 | 0.19 | --- |
| DNT-E | 15 | 6 | 5.587 | 0.37 | 0.049 | 0.24 | --- |
| Test 8a | 40 | 7 | 7.604 | 0.19 | 0.059 | 0.30 | --- |
| 9.5 psia Val-A | 20 | 0 | 0.064 | 0.00 | 0.064 | 0.36 | --- |
| Test 9c | 11 | 3 | 2.635 | 0.24 | 0.067 | 0.43 | --- |
| Test 7b | 11 | 2 | 2.378 | 0.22 | 0.077 | 0.51 | --- |
| PRP IV | 69 | 8.3 | 9.089 | 0.13 | 0.079 | 0.58 | 0.900 |
| ZPB-D | 10 | 5 | 5.456 | 0.55 | 0.084 | 0.67 | 0.955 |
| DNT-C | 33 | 15 | 14.052 | 0.43 | 0.111 | 0.78 | 0.978 |
| EffctEx-Y | 1 | 0 | 0.118 | 0.12 | 0.134 | 0.91 | 0.989 |
| EffctEx-U | 1 | 0 | 0.118 | 0.12 | 0.134 | 1.05 | 0.994 |
| BSI-A ? | 17 | 10 | 10.731 | 0.63 | 0.135 | 1.18 | 0.997 |
| PRP III | 10 | 2 | 2.507 | 0.25 | 0.137 | 1.32 | 0.998 |
| Test 7a | 11 | 4 | 3.388 | 0.31 | 0.160 | 1.48 | 0.999 |
| EffctEx-L | 2 | 1 | 0.711 | 0.36 | 0.183 | 1.66 | 0.999 |
| EffctEx-M | 2 | 1 | 0.711 | 0.36 | 0.183 | 1.84 | 1.000 |
| EffctEx-O | 2 | 1 | 0.711 | 0.36 | 0.183 | 2.03 | 1.000 |
| DNT-A | 39 | 24 | 22.667 | 0.58 | 0.187 | 2.21 | 1.000 |
| MV-E | 31 | 18 | 16.671 | 0.54 | 0.229 | 2.44 | 1.000 |
| EffctEx-G | 7 | 3 | 3.640 | 0.52 | 0.235 | 2.68 | 1.000 |
| 100% Suit-A | 10 | 0 | 0.268 | 0.03 | 0.275 | 2.95 | 1.000 |
| PE2-B | 32 | 21 | 19.512 | 0.61 | 0.291 | 3.24 | 1.000 |
| Bubb Threshold-B | 10 | 0 | 0.326 | 0.03 | 0.337 | 3.58 | 1.000 |
| EffctEx-K | 4 | 2 | 1.422 | 0.36 | 0.364 | 3.95 | 1.000 |

F-1
---
| Data Set | # Exposures (N) | # DCS Incidents Observed (f) | # DCS Incidents Predicted A1309-3RUT MBe1 (n) | π | (Pearson Residual)² (f-n)²/n(1-π) | cumulative χ² | P |
|----------|-----------------|-------------------------------|-------------------------------------------|------|----------------------------------|----------------|-----|
| DNT-I | 33 | 13 | 11.345 | 0.34 | 0.368 | 4.31 | 1.000 |
| DNT-H | 31 | 12 | 13.698 | 0.44 | 0.377 | 4.69 | 1.000 |
| Test 11b | 4 | 0 | 0.361 | 0.09 | 0.396 | 5.09 | 1.000 |
| EffctEx-J | 8 | 4 | 4.918 | 0.61 | 0.445 | 5.53 | 1.000 |
| Test 8b | 41 | 10 | 8.189 | 0.20 | 0.501 | 6.03 | 1.000 |
| 8.3 psia-B | 11 | 0 | 0.541 | 0.05 | 0.569 | 6.60 | 1.000 |
| ZPB-B | 21 | 7 | 8.733 | 0.42 | 0.589 | 7.19 | 1.000 |
| Test 3a | 28 | 6 | 7.832 | 0.28 | 0.595 | 7.79 | 1.000 |
| EffctEx-I | 8 | 3 | 4.160 | 0.52 | 0.674 | 8.46 | 1.000 |
| 100% Suit-B | 10 | 0 | 0.694 | 0.07 | 0.746 | 9.21 | 1.000 |
| MV-B | 31 | 19 | 16.599 | 0.54 | 0.747 | 9.95 | 1.000 |
| PE1-B | 28 | 21 | 18.824 | 0.67 | 0.768 | 10.72 | 1.000 |
| Test 5b | 11 | 0 | 0.817 | 0.07 | 0.883 | 11.60 | 1.000 |
| Test 5a | 38 | 4 | 6.225 | 0.16 | 0.951 | 12.55 | 1.000 |
| DNT-D | 17 | 11 | 8.841 | 0.52 | 1.099 | 13.65 | 1.000 |
| EffctEx-N | 2 | 0 | 0.711 | 0.36 | 1.103 | 14.76 | 0.999 |
| 35K-B | 30 | 28 | 25.949 | 0.86 | 1.200 | 15.96 | 0.999 |
| MV-C | 30 | 9 | 11.987 | 0.40 | 1.239 | 17.20 | 0.999 |
| 35K-A | 37 | 21 | 24.255 | 0.66 | 1.268 | 18.46 | 0.998 |
| 100% Suit-F, females | 10 | 1 | 2.660 | 0.27 | 1.411 | 19.87 | 0.997 |
| DNT-F | 16 | 10 | 7.611 | 0.48 | 1.430 | 21.30 | 0.995 |
| Test 3c | 14 | 3 | 5.162 | 0.37 | 1.434 | 22.74 | 0.993 |
| DNT-G | 16 | 7 | 4.782 | 0.30 | 1.468 | 24.21 | 0.991 |
| ZPB-A | 20 | 12 | 9.249 | 0.46 | 1.522 | 25.73 | 0.987 |
| (4.37 psia PB15-PstB138, Unknown) | 12 | 7 | 8.946 | 0.75 | 1.664 | 27.39 | 0.982 |
| Test 9b | 23 | 2 | 4.484 | 0.19 | 1.710 | 29.10 | 0.975 |
| Test 3b | 35 | 8 | 5.187 | 0.15 | 1.791 | 30.89 | 0.966 |
| Test 1c | 12 | 4 | 2.181 | 0.18 | 1.854 | 32.75 | 0.955 |
| 100% Suit-D, females | 9 | 0 | 1.550 | 0.17 | 1.873 | 34.62 | 0.940 |
| DNT-B | 18 | 7 | 9.923 | 0.55 | 1.919 | 36.54 | 0.922 |
| 100% Suit-C | 11 | 0 | 1.660 | 0.15 | 1.955 | 38.49 | 0.901 |
| PE1-A | 26 | 11 | 7.738 | 0.30 | 1.958 | 40.45 | 0.877 |
| Test 4b | 12 | 0 | 1.685 | 0.14 | 1.960 | 42.41 | 0.851 |
| Test 4c | 12 | 0 | 1.813 | 0.15 | 2.136 | 44.55 | 0.817 |
| Test 4d | 12 | 0 | 1.859 | 0.15 | 2.200 | 46.75 | 0.778 |
| Test 9d | 7 | 0 | 1.677 | 0.24 | 2.205 | 48.95 | 0.736 |
| Test 4e | 12 | 0 | 1.937 | 0.16 | 2.309 | 51.26 | 0.689 |
| Bubb Threshold-A | 25 | 0 | 2.145 | 0.09 | 2.347 | 53.61 | 0.639 |
| Test 4f | 12 | 0 | 1.975 | 0.16 | 2.364 | 55.97 | 0.588 |
| 35K-C | 36 | 19 | 23.599 | 0.66 | 2.602 | 58.58 | 0.528 |
| Test 2b | 22 | 6 | 3.110 | 0.14 | 3.127 | 61.70 | 0.451 |
| PRP II | 50 | 0 | 2.959 | 0.06 | 3.145 | 64.85 | 0.378 |
| EffctEx-P | 1 | 1 | 0.230 | 0.23 | 3.344 | 68.19 | 0.305 |

F-2
---
| Data Set | # Exposures | # DCS Incidents | | | | (Pearson Residual)² | | |
|----------|-------------|------------------|------------------|------------------|------------------|------------------|------------------|
| | (N) | Observed (f) | Predicted n | π | (f-n)²/n(1-π) | cumulative χ² | P |
| | | | A1309-3RUT MBe1 | | | | |
| EffctEx-C | 22 | 9 | 13.329 | 0.61 | 3.567 | 71.76 | 0.236 |
| Test 9a | 24 | 1 | 4.679 | 0.19 | 3.594 | 75.35 | 0.178 |
| (4.37 psia PB60-PstB180, Unknown) | 43 | 23 | 28.968 | 0.67 | 3.768 | 79.12 | 0.129 |
| 7.8 psia-B | 92 | 4 | 9.933 | 0.11 | 3.973 | 83.09 | 0.089 |
| 100% Suit-E | 11 | 0 | 2.926 | 0.27 | 3.987 | 87.08 | 0.059 |
| EffctEx-F | 13 | 5 | 8.458 | 0.65 | 4.048 | 91.13 | 0.038 |
| EffctEx-H | 8 | 7 | 4.157 | 0.52 | 4.049 | 95.18 | 0.024 |
| EffctEx-B | 25 | 10 | 15.071 | 0.60 | 4.296 | 99.47 | 0.015 |
| Test 1d | 3 | 2 | 0.580 | 0.19 | 4.306 | 103.78 | 0.008 |
| PE2-A | 32 | 15 | 9.418 | 0.29 | 4.688 | 108.47 | 0.004 |
| 35K-D | 31 | 31 | 26.814 | 0.86 | 4.839 | 113.30 | 0.002 |
| PRP I | 49 | 9 | 4.448 | 0.09 | 5.124 | 118.43 | 0.001 |
| DNT-J | 34 | 21 | 14.473 | 0.43 | 5.125 | 123.55 | 0.000 |
| DNT-K | 31 | 14 | 8.050 | 0.26 | 5.940 | 129.49 | 0.000 |
| (6 psia, Unknown) | 24 | 1 | 6.287 | 0.26 | 6.023 | 135.52 | 0.000 |
| MV-A | 31 | 29 | 22.970 | 0.74 | 6.111 | 141.63 | 0.000 |
| CO2-D | 25 | 19 | 12.301 | 0.49 | 7.182 | 148.81 | 0.000 |
| BSI-E | 46 | 24 | 15.287 | 0.33 | 7.438 | 156.25 | 0.000 |
| EffctEx-V | 1 | 1 | 0.118 | 0.12 | 7.449 | 163.70 | 0.000 |
| EffctEx-W | 1 | 1 | 0.118 | 0.12 | 7.449 | 171.15 | 0.000 |
| EffctEx-X | 1 | 1 | 0.118 | 0.12 | 7.449 | 178.59 | 0.000 |
| 40K-A | 40 | 18 | 26.500 | 0.66 | 8.077 | 186.67 | 0.000 |
| EffctEx-E | 25 | 8 | 15.071 | 0.60 | 8.353 | 195.03 | 0.000 |
| BSI-B | 36 | 32 | 23.655 | 0.66 | 8.585 | 203.61 | 0.000 |
| ZPB-C | 20 | 1 | 7.399 | 0.37 | 8.784 | 212.39 | 0.000 |
| 7.8 psia-A | 94 | 1 | 10.154 | 0.11 | 9.252 | 221.65 | 0.000 |
| EffctEx-A | 46 | 15 | 25.627 | 0.56 | 9.949 | 231.59 | 0.000 |
| Test 11a | 28 | 3 | 11.234 | 0.40 | 10.080 | 241.67 | 0.000 |
| CO2-A | 38 | 4 | 13.394 | 0.35 | 10.175 | 251.85 | 0.000 |
| BSI-D | 28 | 22 | 12.885 | 0.46 | 11.944 | 263.79 | 0.000 |
| (5.45 psia, Unknown) | 21 | 1 | 8.834 | 0.42 | 11.992 | 275.79 | 0.000 |
| CO2-B | 37 | 3 | 13.225 | 0.36 | 12.302 | 288.09 | 0.000 |
| BSI-C ? | 83 | 66 | 48.068 | 0.58 | 15.895 | 303.98 | 0.000 |
| Test 10 | 19 | 1 | 0.047 | 0.00 | 19.577 | 323.56 | 0.000 |
| EffctEx-D | 26 | 7 | 17.856 | 0.69 | 21.073 | 344.63 | 0.000 |
| CO2-C | 25 | 24 | 12.226 | 0.49 | 22.190 | 366.82 | 0.000 |
| Bubb Threshold-C (?) | 23 | 3 | 0.244 | 0.01 | 31.459 | 398.28 | 0.000 |
| Test 6 | 29 | 1 | 0.028 | 0.00 | 34.358 | 432.64 | 0.000 |
| Totals: | 2594 | 858.3 | 896.453 | | | | |

F-3