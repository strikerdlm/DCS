## Tables
Page

1. Summary Statistics for RM Explanatory Variables ..............................  16
2. Summary Statistics for NM Explanatory Variables ..............................  17
3. Intervals that Define the Exercise Done During Prebreathe ..................... 22
4. Estimated versus Measured O2 Consumption During Exercise Prebreathe .. 24
5. Selection of Specific Model Data .................................................. 27
6. Data for Test of Prebreathe Hypothesis and Model Data ....................... 28
7. Summary Statistics for Explanatory and Outcome Variables in the RM .... 30
8. Summary Statistics for Explanatory and Outcome Variables in the NM .... 31
9. Data for Test of Prebreathe Hypothesis .......................................... 42
10. Seven Research Model Results .................................................... 46
11. Observed versus Predicted DCS with Research Model ........................ 47
12. Seven NASA Model Results ....................................................... 49
13. Observed versus Predicted DCS with NASA Model ........................... 50
14. Physical Characteristics and Results from Subjects that did Ergometry First 57
15. Physical Characteristics and Results from Subjects that did Ergometry Second 58
16. Counts of VGE Grades when Ergometry is done First or Second ............. 60
17. Example Application of Exercise Prebreathe Models ........................... 68

## Figures

1. Removal of N2 and He with and without exercise during prebreathe ................. 8
2. The correlation trend between DCS outcome and VO2 pk ............................. 12
3. Linear relationship between O2 uptake and workload up to VO2 max ............... 19
4. Linear relationship between k and mL*kg-1*min-1, the normalized VO2 rate ...... 34
5. Nonlinear relationship between k and mL*kg-1*min-1 with a slow initial response
in the exponential decay constant with a change in normalized VO2 rate .............. 35
6. Nonlinear relationship between k and mL*kg-1*min-1 with a rapid initial response
in the exponential decay constant with a change in normalized VO2 rate ............... 36
7. Best nonlinear relationship between k and mL*kg-1*min-1 for the NM and the
RM compared to a model with a constant 360 min half-time compartment .............. 51
8. RM that shows P(DCS) as a function of ETR and age. As simulated age increases
from 30 to 40 to 50 years, the P(DCS) for a given ETR increases ......................... 52
9. NM that shows P(DCS) as a function of ETR and gender. A female has a higher
P(DCS) than a male at any given ETR ......................................................... 53
10. The change in VGE incidence in the lower body through time ........................ 55
11. VGE latency time is shorter when ergometry is done at the start of exercise PB
rather than 10 to 15 minutes later .............................................................. 59
12. Incidence of VGE versus time at 4.3 psia and order of ergometry ..................... 61
---
# Acronyms and Nomenclature

BMI                    Body Mass Index
CEV                    Crew Excursion Vehicle
DCS                    Decompression Sickness
EVA                    Extravehicular Activity
ETR                    Exercise Tissue Ratio
H₂O                    water
ISS                    International Space Station
JSC                    Johnson Space Center
LR                     Logistic Regression
LL                     log likelihood
NASA                   National Aeronautics and Space Administration
NM                     NASA Model
N₂                     nitrogen
O₂                     oxygen
pk                     peak
PRP                    Prebreathe Reduction Protocol
psia                   pounds per square inch absolute
PB                     prebreathe
ppN₂                   partial pressure of nitrogen
ppO₂                   partial pressure of oxygen
RM                     Research Model
SD                     standard deviation
TR                     Tissue Ratio
VGE                    Venous Gas Emboli
---
# Abstract

Exercise during oxygen (O₂) prebreathe (PB) accelerates nitrogen (N₂) removal from the tissues. Exercise PB can reduce the risk of decompression sickness (DCS) on ascent to 4.3 psia when performed at the proper intensity and duration. We hypothesized that a probability model with a variable half-time compartment to compute the decrease in tissue N₂ pressure given specifics about exercise during the PB would be superior to a model based on a constant 360 min half-time compartment. Data are from seven tests. PB times ranged from 90 to 150 min. High intensity, short duration dual-cycle ergometry was done during the PB for seven min at 75% of peak O₂ consumption after a three min warm-up period at the start of PB. This was done by itself, or in combination with intermittent low intensity exercise or periods of rest for the remaining PB. Variations of exercise intensity in later tests reflected exercise that could be performed in a space suit. PBs in 167 exposures also included a 30-min exposure to 10.2 psia where subjects breathed 26.5% O₂ – 73.5% N₂, and all tests used a 30 min ascent to 4.3 psia. Non-ambulating men and women performed light exercise from a semi-recumbent position at 4.3 psia for four hrs. DCS at 4.3 psia was reported during 28 exposures, with two classified as Type II DCS. The exercise intervals for each subject was defined as the percentage of VO₂ pk with unit mL·kg⁻¹·min⁻¹ while rest intervals were assigned 9.5% of VO₂ pk. Some otherwise useful data did not have a measure of VO₂ pk. To exploit all the available data, we developed a Research Model (n = 229) with estimated VO₂ pk for 65 subjects, and a NASA Model (n = 159), all with measured VO₂ pk. An iterative approach established the best relationship between %VO₂ pk for each exercise and rest interval and the half-time for N₂ removal or uptake. The best-fit logistic model using decompression dose defined as computed tissue N₂ pressure at the end of ascent divided by ambient pressure (always 4.3 psia) was obtained with a nonlinear relationship between half-time and percentage of VO₂ pk. With this approach, aerobic fitness should relate to DCS outcome if aerobic fitness did indeed relate to DCS outcome, regardless if the exercise during the PB was characterized as relative work, absolute work, or a combination of both. The Research Model with age included improved over the null model by 7.5 log likelihood units, and over a model with a constant 360 min half-time compartment by 4.0 units. Both improvements were statistically significant. The probability of DCS increases with advancing age. The NASA Model with gender included improved over the null model by 7.7 log likelihood units, and over a model with a constant 360 min half-time compartment by 4.1 units. Both improvements were statistically significant. The probability of DCS increases if gender is female. Accounting for exercise and rest during PB with a variable half-time compartment for computed tissue N₂ pressure advances our probability modeling of hypobaric DCS. Both models show that a small increase in exercise intensity during PB expressed as a percentage of VO₂ pk reduces the risk of DCS, and a larger increase in exercise intensity dramatically reduces risk. These models support the hypothesis that aerobic fitness is an important consideration for the risk of hypobaric DCS when exercise is performed during the PB.
---
# A PROBABILITY MODEL OF DECOMPRESSION SICKNESS AT 4.3 PSIA AFTER EXERCISE PREBREATHE

## Introduction

### Fundamental Cause of Decompression Sickness:

Equation 1 defines a fundamental axiom about decompression sickness (DCS), which is that a transient gas supersaturation, known as pressure difference (ΔP), exists in a tissue region. The sum of all gas partial pressures in that region is greater than the ambient pressure opposing the release of the gas. Supersaturation exists when ΔP is positive:

$$\Delta P = \sum_{i=1}^{k} P_1 - P_2, \tag{Eq. 1}$$

where P₁ is the partial pressure of the i^th gas of k species in the tissue and P₂ is the ambient pressure after depressurization. The potential for bubble growth and rate of bubble growth are related to the magnitude of the supersaturation. The metabolic gases: oxygen (O₂), carbon dioxide (CO₂), and even water vapor (H₂O) at 37 c are controlled by physiology within narrow limits, so under most circumstances the inert gas partial pressure is the critical concern. Although gas supersaturation in the tissue is not in itself harmful, it is nevertheless an unstable condition between the tissue and the surrounding environment. The difference in tissue gas partial pressure and ambient pressure can be resolved with a phase transition, and some of the excess mass (moles) of gas in the form of bubbles would be accommodated by the tissue, causing no symptoms. However, when a gas space is formed due to the partial or complete desaturation of a supersaturated tissue, there is a possibility of DCS. The determining factor of DCS may not be the presence or even absolute volume of evolved gas in the tissue, but rather the pressure difference (deformation pressure) between the gas space and the tissue.
---
## Prevention of Decompression Sickness with Oxygen Prebreathe:

For aviators and astronauts the nitrogen (N₂) partial pressure (ppN₂) in the tissues is a concern. A 75 kg man at sea level pressure (one atmosphere absolute [ATA]) with 15% of total body weight as fat carries about one liter of N₂ dissolved in the tissues and fluids. About half (500 ml at standard temperature and pressure [STP]) is contained in 63 kg of "lean" tissues and body fluids and about half is contained in 12 kg of "lipid" tissues. During a 4-hr 100% O₂ resting prebreathe (PB) about 750 ml STP is removed, leaving only 250 ml STP in the tissues. However, an ascent to 1/3 ATA has the potential of transforming the 250 ml into 750 ml of evolved gas (simple application of Boyles Law). This worst-case scenario is never realized because the formation of bubbles takes time, time which is also available for additional N₂ removal from the tissues via the lungs, and not all supersaturation results in bubble formation.

## Exercise as a Means to Accelerate Nitrogen Washout:

Prebreathing O₂ while at rest is the simplest and most widely used risk mitigation strategy to prevent altitude DCS (26,34). Exercise during PB increases the rate of N₂ removal and shortens the PB time (3,4,6,55,57,58). This technique is successful because blood perfusion through tissues is the rate limiting process for N₂ washout during the PB, and exercise increases tissue blood perfusion in metabolically active tissues (34,53).

Two approaches are used to quantify the benefit of exercise during PB: measuring the N₂ removed during the PB (see Fig. 1), and measuring the decrease in incidence of DCS and venous gas emboli (VGE) during subsequent exposure to reduced pressure (54). The latter is the approach we have used (8,20,21,22,24). But there are many unanswered questions about using exercise to accelerate N₂ washout and thus shorten the PB time. What is the best exercise to use in terms of the type, intensity, and duration for maximum effect? Besides fatigue and dehydration, what are the contraindications for exercise during PB? Any kinetic motion in the body has the potential of forming micronuclei through tribonucleation (27,31), either stabilized or transient micronuclei. Micronuclei act as "seeds" to facilitate the transformation of dissolved gas into evolved gas (bubbles) during subsequent exposure to reduced pressure (18,29,50,52).
---
So there is a complex balance between the goal of accelerating N₂ washout with exercise and the potential to form micronuclei that could grow into bubbles on subsequent depressurization.

|                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| body stores eliminated (%)&#xA;100	&#xA;N₂ ELIMINATION WITH EXERCISE&#xA;&#xA;80	&#xA;He ELIMINATION AT REST&#xA;&#xA;60	&#xA;&#xA;40	&#xA;N₂ ELIMINATION AT REST&#xA;&#xA;30	&#xA;&#xA;20	&#xA;&#xA;10	&#xA;&#xA;0	&#xA;&#xA;	0	10	20	30	40	50	60	70	80&#xA;time of exposure to atmosphere free of gas (min) |

Figure 1. A greater amount of N₂ and He are removed if exercise is used during PB (5).

## Purpose of Report:

This report documents one analytical approach to quantify the benefit of exercise during PB to reduce the risk of DCS in subjects exposed to 4.3 psia. We quantify the risk by estimating the probability of DCS [P(DCS)] given the conditions of the PB and altitude exposure. Our analysis extends the work of others (37,39,41). Data are describe from seven tests that define the NASA Prebreathe Reduction Protocol (PRP) initiated in 1999, and a statistical analysis of those data is performed. Two models are developed: the first is called the NASA Model (NM), based on 159 exposures specific to the needs of NASA, and the second is called the Research Model (RM), based on 229 exposures specific to address other research questions.

## Exercise During Prebreathe:
---
Both the shuttle and International Space Station (ISS) operate at 14.7 pounds per square inch absolute (psia) with an air atmosphere, so a PB procedure is required to reduce N₂ partial pressure in the tissues to an acceptable level prior to depressurization to 4.3 psia. Exercise during PB is an effective way to reduce tissue ppN₂ and therefore the risk of DCS during a subsequent EVA. However, the magnitude of the benefit given specifics about the exercise type, intensity, and duration needs to be quantified.

It is known that exercise before a decompression in divers (63,17) and aviators (16), during decompression in divers (32,33), during O₂ PB (3,4,6,54,55,57), and certainly during the altitude exposure (1,14,30,35) influences the DCS or VGE outcomes. Exercise is a powerful stimulus to the body, so it is reasonable to expect that the type, intensity, duration, and timing of exercise before a depressurization would modify the outcome (also see Adynamia Section).

It is known that older men are at greater risk of DCS than younger men (9,10,25,28,49). Overweight men are at a greater risk of DCS than underweight men (1,15,25). Therefore, overweight older men are expected to be at a greater risk of DCS than underweight younger men. But how do you interpret the case of an underweight older man or overweight younger man? What is needed is an explanatory variable that is better associated with the decompression outcome than just age or body type. It is also desirable that the explanatory variable has some rational causal relationship to the development of DCS, not just a correlative relationship.

The removal of N₂ from the tissues during a denitrogenation procedure is limited by blood perfusion (34,53). Therefore, a fit person will eliminate more N₂ than an unfit person during an exercise-enhanced O₂ PB with the exercise intensity prescribed as a percentage of maximum O₂ consumption. Aerobic fitness declines with advancing age regardless of our individual efforts. Declines of 0.7% and 1.6% are reported for elite male athletes in categories of most active to least active, respectively, as they age from 25 to 40 years (38). Concomitant decreases in aerobic fitness and not the increase in age *per se* may be responsible for a greater risk of DCS (9,40,43). Similarly, overweight people generally have lower aerobic fitness that continues to decrease as they become more obese. Some women are less fit than men, which may give credence to the still controversial observations that females are at greater risk of DCS
---
than males (13,36,45,46,56,64). The relationship between aerobic fitness and age, body type, and gender may help to explain why some fit older men are less likely to contract DCS than some unfit younger men. Therefore we used aerobic fitness defined as maximum O₂ consumption (VO₂ max) with unit mLO₂ consumption (STPD)∗kg⁻¹∗min⁻¹ as one important explanatory variable for DCS, especially under conditions when N₂ is removed from the body during exercise PB. Age, body type, and even gender are potentially confounding correlative explanatory variables. In effect, they are poor surrogates for aerobic fitness to understand the risk of DCS after a denitrogenation procedure.

We will show that a probability model for DCS based on the *hypothesis* that DCS risk after exercise PB based on a percentage of VO₂ pk is inversely related to aerobic fitness. We will show that this is better than other alternatives we evaluate.

## Relative and Absolute Exercise (work) During Prebreathe:

There is a peculiarity in how this model is structured to account for relative and absolute work during an exercise PB that needs to be clearly stated. The model is fundamentally based on the hypothesis that aerobic fitness affects DCS outcome when the PB includes exercise to accelerate N₂ washout. We believe that subjects with high VO₂ pk are less likely to contract DCS after exercise PB compared to subjects with low VO₂ pk that perform the same exercise PB regardless of the type of exercise performed. Since high intensity, short duration exercise in our testing was assigned at 75%, 60%, 50%, etc., of VO₂ pk, the fit subject would actually consume more O₂ than the unfit subject. However, all exercise during PB in our testing was not prescribed as a percentage of VO₂ pk. We also assigned low intensity, long duration absolute work using various "crank-and-yank" devices mounted on an exercise cot. When a constant amount of work is prescribed, a fit or unfit person will still do the same total work. This means, baring any difference in exercise efficiency, a similar O₂ consumption for performing absolute work is expected, whether one is fit or unfit.
---
A limitation of our analysis is that there were no measurements of O₂ consumption in subjects during the exercise PB as they performed relative work as defined by a percentage of VO₂ pk using dual-cycle ergometers, absolute work on the crank-and-yank devices, or a combination of both in the same PB protocol. Instead, a measure of VO₂ pk was the only information available for most subjects. The O₂ consumption as ml·kg⁻¹·min⁻¹ for relative work based on a percentage of VO₂ pk was computed for the appropriate interval of time when this type of exercise was done. So the fit and unfit subjects were assigned the appropriate O₂ consumption for the exercise interval. This same approach was extended to assign O₂ consumption for exercise intervals where crank-and-yank absolute work was done. This is not strictly correct since absolute work would demand the same O₂ consumption whether the person is fit or unfit. But in our statistical model there are two practical advantages of taking this approach: you at least reference the estimate of O₂ consumption to a measurement of VO₂ pk that is available for the subject that actually performed the PB, and you preserve in the model the idea that fitness is related to DCS outcome when PB procedures use exercise to accelerate N₂ washout regardless of the type of exercise. To account for exercise during PB given both relative and absolute work with one methodology, we impose that a fit person will consume slightly more O₂ than an unfit person given that both perform low intensity, long duration absolute work.

The parameter estimates in the statistical models developed here maximize correlative relationships between explanatory variables and the response variable regardless if the model is based on a sound theoretical rationale. If a fit person does low intensity, long duration absolute work and does not contract DCS and the unfit person does the same work and contracts DCS, then the model will reflect this result by making small changes in O₂ consumption as ml·kg⁻¹·min⁻¹ important. If fitness during absolute work is not an important consideration, then the model will not be influenced by small changed in O₂ consumption using our methodology. An alternative is to assign a constant (mean) O₂ consumption in the interval for the crank-and-yank absolute work to each subject who performed that exercise. The assigned mean O₂ consumption would not be related to the only information collected for the subject, the VO₂ pk. The constant
---
would come from a representative sample of subjects. This alternative approach results in losing the opportunity to test for the importance of fitness given low intensity absolute work since the model is not provided with a distinction between fit or unfit subjects.

By what rationale do we favor a statistical model based on classifying both absolute and relative work as a percentage of VO2 pk? Figure 2 is based on an initial analysis before the Results section to make this crucial point. If VO2 pk for the subject correlates to the DCS outcome, even if the exercise during the PB was based on absolute or relative work, then a methodology that preserves this correlation should be used.

|                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Upper Panel: Absolute Work During PB&#xA;DCS	VO2 Peak&#xA;1.0	o o o ooo o&#xA;0.8	&#xA;0.6	&#xA;0.4	&#xA;0.2	───────────────&#xA;0.0	o	o o	o o	o o	o&#xA;	20	30	40	50	60 |

|                                                        |                      |     |     |       |    |    |
| ------------------------------------------------------ | -------------------- | --- | --- | ----- | -- | -- |
| Lower Panel: Combination of Absolute and Relative Work |                      |     |     |       |    |    |
| DCS                                                    | VO2 Peak             |     |     |       |    |    |
| 1.0                                                    | o o o oo oooo o o oo |     |     |       |    |    |
| 0.8                                                    |                      |     |     |       |    |    |
| 0.6                                                    |                      |     |     |       |    |    |
| 0.4                                                    |                      |     |     |       |    |    |
| 0.2                                                    | ───────────────      |     |     |       |    |    |
| 0.0                                                    | o                    | o o | o o | o o o | o  |    |
|                                                        | 20                   | 30  | 40  | 50    | 60 | 70 |

Figure 2. The correlation trend between DCS outcome and VO2 pk from exposures where absolute work was done during the PB (upper panel) and when a combination of absolute work and relative work was done (lower panel).
---
The upper panel in Fig. 2 shows a modest inverse trend between DCS outcome and VO₂ pk in 71 exposures from Phases III and IV in data used in the RM. Note that VO₂ pk in 64 of these exposures had to be estimated from other information about the test subjects (explained later). These data are for exercises during PB classified as absolute work. The mean VO₂ pk in 10 subjects with DCS is 40.73 ± 5.2 mL*kg⁻¹*min⁻¹ and 41.01 ± 4.7 in 61 subjects without DCS. Contrast this to a greater inverse trend (steeper slope) in the lower panel between DCS outcome and VO₂ pk in 152 exposures from Phases I, II, V-1, V-2, and V-3 in data used in the NM. These data are for exercise during PB just classified as relative work (percentage of VO₂ pk in Phase I) plus data where both relative exercise and absolute exercise were both done during the PB (Phases II, V-1, V-2, and V-3). The mean VO₂ pk in 20 subjects with DCS is 38.95 ± 8.4 mL*kg⁻¹*min⁻¹ and 41.78 ± 7.3 in 132 subjects without DCS. Unfortunately, we do not have enough data to evaluate the case where just relative work (only in Phase I) was done during the PB. A tentative conclusion is that aerobic fitness is inversely associated with DCS outcome whether only absolute work is performed during the PB (upper panel) and certainly if a combination of relative and absolute work is performed (lower panel).

We maximize the above correlative information about VO₂ pk and DCS outcome in a statistical model even if it conflicts with exercise physiology theory about O₂ consumption during absolute work. But how would you use this correlative information? One approach is to preserve the linkage to VO₂ pk for each subject by referencing all exercise to VO₂ pk, which takes advantage of one methodology. A second approach is to provide mean O₂ consumption for absolute work without the link to VO₂ pk, and then include VO₂ pk as a covariate in all future models to capture its contribution in a disjointed data file. A third approach is to actually measure O₂ consumption for both types of exercise during the PB on the day of the test in each subject that goes to altitude. We currently exploit the first approach. The second approach is possible, but more complicated than the first since the data about exercise is disjointed, containing one methodology for relative work and one methodology for absolute work. The second approach requires that you deal with covariate interactions since you essentially use VO₂ pk information twice, once to characterize relative work and once as a stand-alone covariate to
---
address any correlation with DCS outcome and absolute work. This requires additional degrees of freedom in the model, which may not be statistically justified compared to a simpler approach. The third option is the best approach, but is not how we have conducted this research.

In summary, tissue metabolic needs dictate the distribution of cardiac output. The distribution of cardiac output during a PB dictates the quality of the denitrogenation from the tissues. The limited blood volume cannot be distributed equally into the total volume of the capillary beds; there is exquisite physiological regulation of blood perfusion. When the exercise during PB is developed around relative work (a percentage of VO₂ pk), then a fit person will consume more O₂ than an unfit person, and more O₂ consumption indicates increased perfusion, and therefore greater N₂ washout. The fit person will have a lower decompression stress at the end of the PB, as reckoned by a lower Exercise Tissue Ratio (ETR), to be defined later. When the exercise during PB is a set amount of work, both fit and unfit persons will achieve about the same O₂ consumption, and each will have the same decompression stress. Our statistical approach is to use one methodology throughout the varied exercise performed during the PB to estimate the O₂ consumption based on a percentage of VO₂ pk.

## Methods

### Data: Exercise and Prebreathe

All subjects signed Informed Consent, were trained on the breathing and exercise equipment in the altitude chamber, received special training on the recognition and reporting of DCS, and were free to withdrawal at any time during the test. Three laboratories used altitude chambers to perform research over a four-year period: Duke University, Defense Research and Development Canada at Toronto, and the University of Texas in conjunction with Hermann Hospital. The respective Institutional Review Boards reviewed and approved all protocols prior to testing.

Seven tests are available for analysis. There were four tests, designated Phase I, II, III, and IV, where subjects performed exercise during the PB, ascended to 10.2 psia and breathed
---
26.5% O₂ for 30 min, then completed a 40 min PB on 100% O₂. Three tests, designated as Phase V-1, V-2, and V-3, also included exercise during the PB, but there was no PB at 10.2 psia. All seven tests included a 30 min ascent from 14.7 psia and exposure to 4.3 psia for four hrs. All subjects performed regimented crank-and-yank exercise at 4.3 psia to simulate EVA activities. Subjects were adynamic (non-ambulatory) for two hrs before the start of the PB, during the PB, and while at 4.3 psia for four hrs. Total PB time ranged from 120 to 180 min. Total PB time included the 30 min to ascend to 4.3 psia and the 30 min at 10.2 psia in Phases I – IV where the subjects breathed 26.5% O₂ through a mask.

The PB and ascent profile for the seven tests were complex in that various exercises during PB were performed, and the ascent to 4.3 psia in Phases I - IV was staged at 10.2 psia for 30 min. After 50 min of PB at site pressure, the subjects in Phases I – IV ascended to 9.6 psia in 20 min followed by a 10-min descent to 10.2 psia, still breathing 100% O₂. The gas supply was switched in the mask, and the subjects then breathed 73.5% N₂ and 26.5% O₂ for 30 min while at 10.2 psia. One hundred percent O₂ PB was reestablished and a five min descent to site pressure was performed. The subjects remained on 100% O₂ for 35 min at site pressure and during the final 30-min ascent to 4.3 psia. An Appendix provides details too numerous to summarize here about the seven tests.

## Adynamia:

Adynamia is defined as the absence of ambulation, even a standing posture, during both the PB phase at site pressure and during the exercise phase while at altitude. This is currently our best analogue for μ-gravity adaptation (11,42). Subjects exercised the lower body while at altitude and were still classified as adynamic since they did not ambulate during the PB or while at altitude. This means that an adynamic person at altitude exercised from a semi-recumbent position, and we do not know how this exercise modified the adynamic condition. The results from these tests were used to define safe and effective PB procedures for astronauts performing EVAs from the ISS.
---
The fundamental untested premise of adynamia is about the control of nucleation processes within tissues and fluids (16,42,59). A comprehensive review of micronuclei is beyond the scope of this report. In the absence of supersaturation, as defined in Eq. 1, the spontaneous rate of nucleation is inconsequential when micronuclei on the order of microns in radius are considered. This is not to say, however, that the number or distribution of micronuclei sizes cannot be influenced before a supersaturation exists when mechanical energy is added to the system. A case in point is the observation that vigorous exercise during a 90 min PB reduces, not increases, the incidence of DCS and VGE (55). The enhanced removal of N₂ during the dual‑cycle exercise appears to dominate the DCS and VGE outcomes, regardless of how the number or distribution of micronuclei were changed. Since the tests have low decompression stress by design, it is important to control all variables that can modify the outcome. When ambulation is controlled through forced adynamia, then other variables such as age or gender that may correlate to DCS or VGE outcome can be better understood. Our control of adynamia is also the reason that the probability models in this report are specific to astronauts that perform EVAs.

Table 1 summarizes the explanatory (independent) variables for data used in the RM, and Table 2 is the summary for data used in the NM.

## TABLE 1. Summary Statistics for RM Explanatory Variables

|                       |     |       |      |             |
| --------------------- | --- | ----- | ---- | ----------- |
| Explanatory Variables | n   | mean  | SD   | range       |
| 1. AGE (yrs)          | 229 | 31.9  | 8.3  | 18 – 59     |
| 2. WT (kg)            | 229 | 77.3  | 13.8 | 46 – 118    |
| 3. HT (cm)            | 229 | 176.7 | 8.7  | 148 – 198   |
| 4. BMI (kg/m²)        | 229 | 24.6  | 3.2  | 17 – 35     |
| Body Mass Index       |     |       |      |             |
| 5. VO₂ pk\*           | 229 | 41.47 | 6.8  | 22.7 – 62.1 |
| (mL\*kg⁻¹\*min⁻¹)     |     |       |      |             |
| 6. TPBTM (min)\*\*    | 229 | 171   | 18   | 120 – 197   |
| Total Prebreathe Time |     |       |      |             |

16
---
|                 |                        |
| --------------- | ---------------------- |
| 7. GENDER       | 175 male<br/>54 female |
| 8. Exercise #1  | 49                     |
| 9. Exercise #2  | 47                     |
| 10. Exercise #3 | 9                      |
| 11. Exercise #4 | 62                     |
| 12. Exercise #5 | 9                      |
| 13. Exercise #6 | 3                      |
| 14. Exercise #7 | 50                     |

\* contains both measured (n=164) and estimated (n=65) VO2 pk.
\*\* includes 30 min ascent to 4.3 psia in all tests and 30 min at 10.2 psia in Phases I - IV

## TABLE 2. Summary Statistics for NM Explanatory Variables

|                                            |                        |       |      |             |
| ------------------------------------------ | ---------------------- | ----- | ---- | ----------- |
| Explanatory<br/>Variables                  | n                      | mean  | SD   | range       |
| 1. AGE (yrs)                               | 159                    | 32.8  | 8.6  | 19 – 59     |
| 2. WT (kg)                                 | 159                    | 77.7  | 14.3 | 46 – 115    |
| 3. HT (cm)                                 | 159                    | 176.7 | 8.9  | 148 – 198   |
| 4. BMI (kg/m2)<br/>Body Mass Index         | 159                    | 24.7  | 3.4  | 17 – 35     |
| 5. VO2 pk<br/>(mL∗kg-1∗min-1)              | 159                    | 41.39 | 7.4  | 22.7 – 61.9 |
| 6. TPBTM (min)\*<br/>Total Prebreathe Time | 159                    | 166   | 19   | 120 – 180   |
| 7. GENDER                                  | 120 male<br/>39 female |       |      |             |
| 8. Exercise #1                             | 47                     |       |      |             |
| 9. Exercise #2                             | 45                     |       |      |             |
| 10. Exercise #3                            | 4                      |       |      |             |
| 11. Exercise #4                            | 3                      |       |      |             |

---
|                 |    |
| --------------- | -- |
| 12. Exercise #5 | 9  |
| 13. Exercise #6 | 3  |
| 14. Exercise #7 | 48 |

\* includes 30 min ascent to 4.3 psia in all tests and 30 min at 10.2 psia in Phases I - IV

The first six variables are measured on a continuous scale, and the last eight are indicator variables taking only the values of zero or one. Even though there is a wide range for each continuous variable, the relatively small standard deviation (SD) for each variable indicates a homogeneous sample. This homogeneity is due to pretest medical selection criteria and a desire to match the physical characteristics of current U.S. astronauts. We do not separate the variables by gender, so this does contribute to a larger sample SD in height and weight in the combined data.

## Exercise During Prebreathe:

The last seven variables in Tables 1 and 2 identify the type and duration of exercise done during the PB. Some details about the specific exercise during the PBs are covered now, with more details provided in the Appendix. Exercise #1 is 10 min of dual-cycle arm and leg ergometery initiated at the start of PB, and performed at 75% of pk O₂ consumption for the last seven min. No additional exercise was allowed for the balance of the 150 min O₂ PB. Exercise #2 is the same exercise as Exercise #1 plus 24 min of additional intermittent light arm and leg exercise starting 55 min into the PB and ending 95 min after the start of PB. Here, heavy short-duration ergometry exercise was coupled with light intermittent short-duration exercise during the later part of the PB. Exercise #3 is the same 24 min of intermittent light arm and leg exercise also starting 55 min into the PB and ending 95 min after the start of PB. There was one case of Type II DCS in this protocol, and the testing was ended. Exercise #4 is 56 min of intermittent light long-duration arm and leg exercise that started four min into the PB and ended 95 min from the start of the PB. Exercise #5 is ten 2-min exercise and rest cycles with exercise between 40 – 60% of VO₂ pk in the first 44 min of PB followed by 46 min of rest. Exercise #6 is seven 3-min exercise and 2-min rest cycles with exercise between 50 – 60% of VO₂ pk in the first 44 min of PB followed by 46 min of rest. There was one case of Type II DCS in this protocol, and the
---
testing was ended. Finally, Exercise #7 is seven 3-min exercise and 2-min rest cycles with exercise between 50 – 60% of VO₂ pk in the first 36 min of PB followed by 24 min of light activity in 54 min followed by 30 min of rest.

In a typical logistic regression (LR), the contribution of the different exercise options during the PB to the DCS outcome would have to be coded, and six estimated parameters would be produced. An example of the coding of the PB conditions that could be used in a regression for the data in Table 1 is as follows: a one indicates the presence of Exercise #1 in 47 exposures and zero for the balance of 182 exposures, and so on for the six remaining exercise PB categories. This approach is not desirable here (is not parsimonious), and is replaced with a method that accounts for exercise during PB by a trial-and-error optimization of a single parameter called λ.

## Assigning %VO₂ pk O₂ Consumption for Intervals of Relative Work:

Figure 3 is helpful in describing our method to assign normalized O₂ consumption (mL∗kg⁻¹∗min⁻¹) during intervals of relative and absolute work during the PB. Exercise intervals of relative work using dual-cycle ergometry were assigned O₂ consumption normalized to body weight by taking a percentage of VO₂ pk.
---
# Linear relationship between O₂ uptake and workload up to the VO₂ max

|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | - |
| ```
endurance
athletes    (85)
6.0                                          80

5.0                                          70

4.0                      (53) conditioned   60

3.0                (45) normally active     50

2.0          (30) sedentary                 30

1.0

0   100     200      300     400
WORK (watts)
``` |   |

**Figure 3. Linear relationship between O₂ uptake and workload up to the VO₂ max. Thereafter, O₂ uptake reaches a plateau as work rate increases (44).**

Under idea conditions, the subject increases work load (watts) with a technique that does not fatigue a particular muscle group until the time the subject decides to stop the exercise after a maximum effort, a time that provides for an accurate measure of VO₂ maximum. In our testing, dual-cycle ergometry was used on a schedule described in the Appendix. We prefer to use the terminology VO₂ pk since our methodology was not standard. Dual-cycle ergometry was also used during the PB and an exercise prescription based on percentage of VO₂ pk was assigned, for example, 75%, 60%, 50% VO₂ pk. In this way, each subject performed the same exercise relative to his or her VO₂ pk. The absolute O₂ consumption using this approach is always greater for the fit subject compared to the unfit subject. A benefit of this approach is that the aerobic fitness of the subject is linked to O₂ consumption during an interval of time since the exercise is referenced to the VO₂ pk of the subject.

## Assigning %VO₂ pk O₂ Consumption for Intervals of Absolute Work:
---
There were also intervals during the PB when absolute work was assigned. The exercise cot was equipped with various devices that required the subject to crank-and-yank, using bungee cord and a torque wrench as described in the Appendix. If each subject was equally motivated, and all advantages of having long limbs can be ignored, then we assume that all subjects performed the same absolute work. Figure 3 shows that each subject would be assigned a constant O₂ consumption based on the amount of absolute work, irrespective of the aerobic fitness of the subject. A sample of 17 subjects representative of those that performed the test at 4.3 psia performed these crank-and-yank exercises and O₂ consumption was measured. The mean and SD were 5.8 ± 0.7 mL·kg⁻¹·min⁻¹. The mean VO₂ pk in a sample of five women and nine men was 42.2 ± 6.0 mL·kg⁻¹·min⁻¹, with a mean age of 35 years. One approach would be to assign a constant 5.8 mL·kg⁻¹·min⁻¹ to each interval of work in each subject that actually went to 4.3 psia that performed this absolute work during the PB. However, this approach eliminates the only linkage to information about the fitness of the subject that actually went to 4.3 psia, the VO₂ pk for the subject. For reasons explained in more detail later, we chose to reference this absolute work to the VO₂ pk of the subject to preserve a linkage to VO₂ pk in our statistical treatment of these data. Exercise intervals of absolute work using crank-and-yank devices mounted on the exercise cot were also assigned O₂ consumption normalized to body weight by taking a percentage of VO₂ pk. The absolute work was converted to 13.8% of VO₂ pk by dividing mean 5.8 mL·kg⁻¹·min⁻¹ by mean 42 mL·kg⁻¹·min⁻¹from our sample of subjects that did not go to 4.3 psia. In this way, one methodology was used to link all O₂ consumption to the fitness of the subject in our statistical approach even though this is contrary to our understanding about exercise physiology under conditions of absolute work. This approach was also extended to characterize intervals of rest. True resting (basal) conditions were not achieved in subjects anxious about the test and never told to truly rest, and 9.5% of VO₂ pk was assigned based on a measure under similar conditions of 4.0 ± 0.5 mL·kg⁻¹·min⁻¹ in our sample of 17 subjects. Therefore, none of the exercise in our seven tests was characterized as only relative work since all tests included intervals of rest during the PB. The closest was Phase I. All had both types of exercise, absolute and relative, characterized based on a percentage of VO₂ pk. We justify using a percentage of VO₂ pk for intervals of absolute work from our

21
---
sample of subjects to subjects that actually went to 4.3 psia because the mean VO₂ pk in these subjects was about 42 mL·kg⁻¹·min⁻¹. Subjects used in both the RM and NM had mean VO₂ pk of 41.5 ± 7.5 mL·kg⁻¹·min⁻¹.

Table 3 shows the type of exercise activity in the intervals that define the total exercise during the PB in Phases I through V-3, the assigned percentage of VO₂ pk, and the time of the interval. All of these intervals were defined as a percentage of VO₂ pk for the subject that went to altitude. The early tests included simpler exercise profiles compared to later tests as evident by fewer intervals of defined exercise activity. The characterization of VO₂ pk for relative work in the Phase V series (V-1, V-2, and V-3) was also less accurate since a confirmed steady state exercise condition was not achieved due to short intervals of relative exercise, two min in V-1 and three min in V-2 and V-3. The targets for the Phase V series were 40%, 50%, and 60% VO₂ pk. The actual performance from a representative sample of subjects that never went to altitude was 32%, 38%, and 45% in V-1 since subjects never reach a steady state with the 2-min exercise. In the construction of the exercise PB protocol for the Phase V series, 30%, 36%, and 45% of VO₂ pk was used in V-1, and is considered representative of what was actually done on the day of the test. Since exercise at 60% VO₂ pk in V-2 and V-3 went for three min, 60% VO₂ pk was assigned for the last two min of the exercise. The estimate of the exercise PB just needed to approximate the representative measured values. Exact measured data from each subject that went to 4.3 psia would be ideal, but we do not have these data. Finally, the slow 30 min ascent from 14.7 to 4.3 psia is part of each exercise PB, and we assigned 9.5% VO₂ pk to this last part of the PB.

## TABLE 3: Intervals that Define the Exercise Done During Prebreathing

| Phase | 1    | 2    | 3    | 4    | 5   | 6    | 7    | 8   | 9   | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
| ----- | ---- | ---- | ---- | ---- | --- | ---- | ---- | --- | --- | -- | -- | -- | -- | -- | -- | -- |
| I     | W    | R    | T    | T    | Q   | Q    | Q    |     |     |    |    |    |    |    |    |    |
| %VO₂  | 37.5 | 75.0 | 37.5 | 25.0 | 9.5 | 9.5  | 9.5  |     |     |    |    |    |    |    |    |    |
| time  | 3    | 7    | 3    | 17   | 50  | 30   | 70   |     |     |    |    |    |    |    |    |    |
| II    | W    | R    | T    | T    | Q   | A    | A    | Q   | Q   |    |    |    |    |    |    |    |
| %VO₂  | 37.5 | 75.0 | 37.5 | 25.0 | 9.5 | 13.8 | 13.8 | 9.5 | 9.5 |    |    |    |    |    |    |    |
|       | 3    | 7    | 3    | 17   | 35  | 15   | 15   | 15  | 70  |    |    |    |    |    |    |    |

---
|      |      |      |      |      |      |      |      |      |      |      |      |      |      |      |      |      |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| time |      |      |      |      |      |      |      |      |      |      |      |      |      |      |      |      |
| III  | Q    | A    | A    | Q    | Q    |      |      |      |      |      |      |      |      |      |      |      |
| %VO₂ | 9.5  | 13.8 | 13.8 | 9.5  | 9.5  |      |      |      |      |      |      |      |      |      |      |      |
| time | 65   | 15   | 15   | 15   | 70   |      |      |      |      |      |      |      |      |      |      |      |
| IV   | Q    | A    | A    | Q    | Q    |      |      |      |      |      |      |      |      |      |      |      |
| %VO₂ | 9.5  | 13.8 | 13.8 | 9.5  | 9.5  |      |      |      |      |      |      |      |      |      |      |      |
| time | 4    | 76   | 15   | 15   | 70   |      |      |      |      |      |      |      |      |      |      |      |
| V-1  | Q    | R    | R    | T    | R    | R    | T    | R    | R    | T    | R    | R    | T    | R    | R    | T    |
| %VO₂ | 9.5  | 30.0 | 30.0 | 25.0 | 36.0 | 36.0 | 25.0 | 45.0 | 45.0 | 25.0 | 45.0 | 45.0 | 25.0 | 45.0 | 45.0 | 25.0 |
| time | 2    | 1    | 1    | 2    | 1    | 1    | 2    | 1    | 1    | 2    | 1    | 1    | 2    | 1    | 1    | 6    |
| V-2  | R    | R    | T    | W    | R    | T    | T    | W    | R    | T    | T    | W    | R    | T    | T    | W    |
| %VO₂ | 36.0 | 36.0 | 25.0 | 30.0 | 60.0 | 30.0 | 25.0 | 30.0 | 60.0 | 30.0 | 25.0 | 30.0 | 60.0 | 30.0 | 25.0 | 30.0 |
| time | 1    | 1    | 2    | 1    | 2    | 1    | 1    | 1    | 2    | 1    | 1    | 1    | 2    | 1    | 3    | 1    |
| V-3  | Q    | R    | T    | W    | R    | T    | T    | W    | R    | T    | T    | W    | R    | T    | T    | W    |
| %VO₂ | 9.5  | 36.0 | 25.0 | 30.0 | 60.0 | 30.0 | 25.0 | 30.0 | 60.0 | 30.0 | 25.0 | 30.0 | 60.0 | 30.0 | 25.0 | 25.0 |
| time | 2    | 2    | 2    | 1    | 2    | 1    | 1    | 1    | 2    | 1    | 1    | 1    | 2    | 1    | 3    | 1    |

## TABLE 3: Continuation of V-1, V-2, and V-3

|       |      |      |      |      |      |      |      |      |      |      |      |      |      |      |      |     |
| ----- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | --- |
| Phase | 17   | 18   | 19   | 20   | 21   | 22   | 23   | 24   | 25   | 26   | 27   | 28   | 29   | 30   | 31   | 32  |
| V-1   | R    | R    | T    | R    | R    | T    | R    | R    | T    | R    | R    | T    | R    | R    | T    | Q   |
| %VO2  | 45.0 | 45.0 | 25.0 | 45.0 | 45.0 | 25.0 | 45.0 | 45.0 | 25.0 | 45.0 | 45.0 | 25.0 | 39.0 | 39.0 | 25.0 | 9.5 |
| time  | 1    | 1    | 2    | 1    | 1    | 2    | 1    | 1    | 2    | 1    | 1    | 2    | 1    | 1    | 10   | 66  |
| V-2   | R    | T    | T    | W    | R    | T    | T    | W    | R    | T    | Q    | Q    |      |      |      |     |
| %VO2  | 60.0 | 30.0 | 25.0 | 30.0 | 60.0 | 30.0 | 25.0 | 30.0 | 60.0 | 30.0 | 9.5  | 9.5  |      |      |      |     |
| time  | 2    | 1    | 1    | 1    | 2    | 1    | 1    | 1    | 2    | 1    | 10   | 75   |      |      |      |     |
| V-3   | R    | T    | T    | W    | R    | T    | T    | W    | R    | T    | Q    | A    | Q    | Q    |      |     |
| %VO2  | 60.0 | 30.0 | 25.0 | 30.0 | 60.0 | 30.0 | 25.0 | 30.0 | 60.0 | 30.0 | 9.5  | 13.8 | 9.5  | 9.5  |      |     |
| time  | 2    | 1    | 1    | 1    | 2    | 1    | 1    | 1    | 2    | 1    | 13   | 40   | 30   | 30   |      |     |

R = relative work (dual-cycle ergometry)
A = absolute work (crank-and-yank devices)
Q = quiet (rest) periods
T = transition from high intensity, low duration exercise to low intensity, long duration exercise, or transition from relative work to rest
W = warm up work (ramping up to dual-cycle relative work)
---
There was also a desire to account for total O₂ consumption in these tests by adjusting the percentage of VO₂ pk in a few intervals, mostly in the intervals designated as transition from high intensity, low duration exercise to low intensity, long duration exercise, or transition from relative work to rest. This was done so that the computed total O₂ consumption would reflect the measured O₂ consumption from a sample of subjects from Duke University and JSC that performed the exercise PB but never went to altitude. The transition from one exercise condition to another is expected to be a source of variability in O₂ consumption. The rationale was that since little is know about the O₂ consumption during the transition from exercise in the actual subjects that went to altitude, it would be reasonable to adjust the percentage of VO₂ pk in that interval such that computed total O₂ consumption would be similar to measured O₂ consumption from a sample of subjects.

Table 4 shows a comparison of estimated cumulative O₂ consumption in exposures used in the RM, which includes O₂ consumed during the time at 10.2 psia in Phases I through IV and during the 30-min ascent in all tests, to what was measured in a sample of 19 subjects for Phases I - IV, and 18 subjects for Phase V-1. There were no measurements available for V-2 and V-3.

## TABLE 4: Estimated versus Measured O₂ Consumption During Exercise Prebreathe

| Phase | estimated O₂ consumption(liters, STPD) | n  | measured O₂ consumption(liters, STPD) | n  |
| ----- | -------------------------------------- | -- | ------------------------------------- | -- |
| I     | 76.5 ± 20.1                            | 49 | 73.1 ± 14.3                           | 19 |
| II    | 88.1 ± 20.7                            | 47 | 79.1 ± 15.6                           | 19 |
| III   | 60.2 ± 6.2                             | 9  | 58.5 ± 9.4                            | 19 |
| IV    | 66.7 ± 12.3                            | 62 | 65.5 ± 11.9                           | 19 |
| V-1   | 78.4 ± 15.5                            | 9  | 75.0 ± 12.6                           | 18 |
| V-2   | 62.0 ± 28.5                            | 3  | no baseline data collected            |    |

---
V-3                       92.5 ± 22.2                     21          no baseline data collected

----

We conclude that the relative ranking of O₂ consumption is preserved, that the absolute values of the estimated O₂ consumption are similar to a sample of measured values, and that our adjustments of O₂ consumption as subjects transitioned from relative work to rest or other absolute work is reasonable.

## Exercise at 4.3 psia:

Intermittent upper and lower body exercise began for all subjects on reaching 4.3 psia for four hrs. The exercise continued until the end of the test or until the subject was removed from the chamber, mostly due to DCS. The subjects performed three bouts of repetitive four-min exercises under adynamic conditions while in a semi-recumbent position. There was a four-min period for bubble monitoring, and also a four-min period of rest after every 60 min. The subjects were encouraged to report any symptoms, and the attending physician made a diagnosis of DCS if warranted. Most of those with a diagnosed symptom of DCS were immediately removed from the altitude chamber through a transfer lock. Termination criteria did not permit subjects to remain at altitude with any persistent symptom(s). As a result, some of the VGE data is right censored, which means the test was ended earlier than planned. The details of the exercise during the PB and during the time at 4.3 psia are documented in the Appendix.

## Doppler Ultrasound Bubble Monitoring:

A Doppler Technician using a transcutaneous Doppler ultrasound bubble detector monitored the blood flow in the pulmonary artery, central venous blood, for bubbles. The VGE monitoring was performed approximately every 12 min for four min. While in a semi-recumbent position, the subject was prompted to flex each of his limbs in turn three times to dislodge VGE from the tissue capillaries and improve VGE detection and grading. Trained observers used the audio signal from the bubble detector to assign a grade for VGE from each of the four limbs on the zero to four Spencer scale (47). This report is about quantifying the risk of DCS, so we limit
---
an extensive description of methodology and the resulting information about VGE to just a few summary statements and three figures at the end of the Results. The Grade of VGE is mentioned, so we paraphrase the definitions as originally published by Spencer: Grade 0 is the complete lack of bubble signals in all cardiac cycles, Grade I is the occasional bubble signal detected in a cardiac cycle with the majority of cardiac cycles free of bubble signals, Grade II is when many, but less than half, of the cardiac cycles contain bubble signals, Grade III is when most of the cardiac cycles contain bubble signals, but not overriding the cardiac motion signals, and Grade IV is when bubble signals are detected continuously through the cardiac cycles such that the signal overrides the amplitude of the cardiac motion and blood flow signals.

## VO₂ Pk Measured or Estimated:

There are 229 records acceptable for analysis in the RM given that 65 records are provided an estimate of VO₂ pk. Except for the absence of measured VO₂ pk, these 65 records are valuable and should not be omitted if possible. Since it is reasonable to assume that VO₂ pk (aerobic fitness) is related to age, weight, and certainly gender, we constructed a multivariable linear regression model to estimate VO₂ pk for males and females given their age, weight, and height. There were 86 records for males and 30 records for females with measured VO₂ pk available when the regressions were performed. All the details about the regressions are not provided. Equation 2 is for males and Equation 3 is for females, and were applied to the height, weight, and age data for the 65 records (50 males and 15 females) that did not have a measured VO₂ pk.

$$\text{VO}_2 \text{ pk } (♂) = 24.274-0.175(\text{age})-0.122(\text{wt})+0.64(\text{ht}), \text{ n = 86} \quad \text{Eq. 2}$$

$$\text{VO}_2 \text{ pk } (♀) = 49.481+0.027(\text{age})-0.184(\text{wt})+0.15(\text{ht}), \text{ n = 30} \quad \text{Eq. 3}$$

This manipulation did not over or under represent these 65 records in that the mean VO₂ pk was 40.9 mL·kg⁻¹·min⁻¹ ± 4.6 SD compared to 41.7 mL·kg⁻¹·min⁻¹ ± 7.5 SD for the balance of 164 records in the RM where VO₂ pk was actually measured. There are 159 records acceptable for analysis in the NM, with a mean VO₂ pk of 41.4 ± 7.4 SD. The smaller set of data for the NM is mainly due to the exclusion of those 65 records without a measured VO₂ pk.
---
In this way, two models are evaluated that exploit all the available data and exploit the best available data.

## Selection of Data for RM and NM:

Table 5 documents the rationale to include or exclude data from the NM and the RM. The data for the NM could be characterized as all those data that were acceptable to test the primary hypothesis about accepting or rejecting the PB protocol being evaluated. For example, if the total PB time exceeded five min then the result of the test could not be used to test the hypothesis about the PB procedure, and therefore would not qualify to be included in the NM. However, the exercise PB model does account for the PB conditions, so tests that went long on PB time still qualify to be included in the RM. Other specifics are contained in Table 5.
---
## TABLE 5: Selection of Specific Model Data

| NASA Model                                                                                                                                           | Research Model                                                                                                                                                | PRP Phase                                                                                                  |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| no cases were included where PBs were longer than specified for the test since results were used to accept or reject the PB procedure                | 13 cases where PBs were extended are included since the model accounts for PB time                                                                            | 2 in Phase I<br/>3 in Phase II<br/>8 in Phase IV                                                           |
| 3 cases classified as ambiguous DCS outcome that did not stop the test early are included as cases of no DCS                                         | none of 5 cases classified as ambiguous DCS outcome were included: 2 cases stopped the test early and 3 cases did not stop the test early                     | 1 in Phase II<br/>2 in Phase IV<br/>1 in Phase IV that stopped early<br/>1 in Phase V-1 that stopped early |
| 2 cases that reported symptoms after the test are included                                                                                           | no cases that report symptoms after the test are included                                                                                                     | 2 in Phase I                                                                                               |
| 2 cases were stopped early due to DT with DCS, and not included                                                                                      | 2 cases were stopped early due to DT with DCS, and not included                                                                                               | 2 in Phase II                                                                                              |
| 2 cases classified as Type II are included with others classified as Type I                                                                          | 2 cases classified as Type II are included with others classified as Type I                                                                                   | 1 in Phase III<br/>1 in Phase V-2                                                                          |
| no cases are included where subjects over or under performed the exercise during the PB since results were used to accept or reject the PB procedure | 1 case where the subject under exercised and 1 case where the subject over exercised early during the PB is included since the model accounts for exercise PB | 2 in Phase V-3                                                                                             |
| no cases included where VO₂ pk was estimated, leaving only 4 cases in Phase III and 3 in Phase IV for the model                                      | 68 cases where VO₂ pk was estimated, with 66 that qualified to be in the research model                                                                       | 6 in Phase III<br/>62 in Phase IV                                                                          |
| 1 case that failed to complete a minimum of 230 min at 4.3 psia and later classified as no DCS was not included                                      | 1 case that failed to complete a minimum of 230 min at 4.3 psia and later classified as no DCS was not included                                               | 1 in Phase III                                                                                             |
| 1 case that failed to complete a minimum of 230 min at 4.3 psia was not included                                                                     | 1 case that failed to complete a minimum of 230 min at 4.3 psia was not included                                                                              | 1 in Phase V-2                                                                                             |
| 30 sec break in PB, with PB extended by 2 min was included                                                                                           | 30 sec break in PB, with PB extended by 2 min was included                                                                                                    | 1 in Phase V-3                                                                                             |
| 2 cases experienced a minor pressure transition at the beginning of the test, and were included                                                      | 2 cases experienced a minor pressure transition at the beginning of the test, and were included                                                               | 2 in Phase V-3                                                                                             |
| 1 case where subject peddled ergometer faster than needed during initial warm-up plus polar heart watch had failed was included                      | 1 case where subject peddled ergometer faster than needed during initial warm-up plus polar heart watch had failed was included                               | 1 in Phase V-3                                                                                             |

---
Table 6 is a summary of the number of exposures that finally qualified to be used to test the hypothesis about the seven PB protocols, and to be included in the NM and the RM. The incidence of DCS associated with these acceptable exposures serves as the observed outcome of the tests. The observed DCS outcome is later compared to the predicted outcome from the NM and the RM.

## TABLE 6: Data for Test of Prebreathe Hypothesis and Model Data

| Phase | Total n | Test of Hypothesis Data | Observed %TDCS\* | NM  | Observed %TDCS\* | RM    | Observed %DCS |
| ----- | ------- | ----------------------- | ---------------- | --- | ---------------- | ----- | ------------- |
| I     | 49      | 47                      | 19.1b (9)        | 47  | 19.1b (9)        | 49a   | 14.3 (7)      |
| II    | 50      | 45                      | 0 (0)            | 45  | 0 (0)            | 47c,j | 0 (0)         |
| III   | 10      | 9                       | 22.2 (2)         | 4   | 50.0 (2)         | 9d    | 22.2 (2)      |
| IV    | 65      | 56                      | 14.3 (8)         | 3   | 0 (0)            | 62e,f | 12.9 (8)      |
| V-1   | 10      | 9                       | 33.3 (3)         | 9   | 33.3 (3)         | 9g    | 33.3 (3)      |
| V-2   | 4       | 3                       | 33.3 (1)         | 3   | 33.3 (1)         | 3h    | 33.3 (1)      |
| V-3   | 50      | 48                      | 14.6 (7)         | 48  | 14.6 (7)         | 50i   | 14.0 (7)      |
| Sum   | 238     | 217                     | 30 DCS cases     | 159 | 22 DCS cases     | 229   | 28 DCS cases  |

\* TDCS is DCS reported during and after an altitude exposure, a. two cases went long on PB, b. two cases of DCS reported after altitude exposure was complete, c. three went long on PB, one classified as ambiguous, d. one failed to complete 230 min and later classified as no DCS, e. eight went long on PB, f. one classified as ambiguous and failed to complete 230 min, two classified as ambiguous, g. one classified as ambiguous and failed to complete 230 min, h. one failed to complete 230 min, i. two had modified exercise profiles very early in the PB, j. two failed to complete 230 min due to DCS in DT.
---
The data in Table 7 for the RM and Table 8 for the NM reveal subtle trends that relate explanatory variables to the DCS outcome. Those with DCS are on average about four years older than those without DCS, and VO₂ pk in the older subjects with DCS is about 3 mL*kg⁻¹*min⁻¹ lower than in those without DCS. The tables are formatted such that the information associated with DCS outcome is at the top of each table. Since the presence of VGE and Grade IV VGE are also outcomes of the exposures, those data are included. Since the seven PB protocols are confounders and act as covariates, the PB and exercise components need to be managed in the multivariable statistical analysis to follow before any trends in these data can be confirmed. In this way, small differences due to age, gender, or VO₂ pk might rise to statistical significance in the model. Also notice that a greater percentage of females out of the total number of females have DCS compared to males, about 17% (9 / 54) for females in the data for the RM from Table 7 have DCS compared to 11% (19 / 175) of the males. The same trend is seen in the data for the NM, about 28% (11 / 39) of the females in Table 8 have DCS compared to 9% (11 / 120) for the males. It is likely that age will be a significant predictor in the RM while gender is a significant predictor in the NM, and VO₂ pk is important in both models based on the descriptive statistics in Tables 7 and 8.

30
---
# TABLE 7. Summary Statistics for Explanatory and Outcome Variables in the RM

| Phase  | DCS | VGE | GIV VGE | AGE  | SD   | WT   | SD   | HT    | SD   | BMI  | SD  | VO₂ Pk   | SD  | SEX M F |
| ------ | --- | --- | ------- | ---- | ---- | ---- | ---- | ----- | ---- | ---- | --- | -------- | --- | ------- |
| I      | 7   | 7   | 2       | 32.1 | 9.4  | 69.2 | 12.0 | 170.3 | 12.5 | 23.8 | 2.8 | 37.5     | 5.6 | 4 3     |
| II     | 0   |     |         |      |      |      |      |       |      |      |     |          |     |         |
| III    | 2   | 1   | 1       | 36.0 | 9.4  | 77.1 | 19.2 | 174.0 | 9.0  | 25.2 | 3.7 | 36.5     | 9.5 | 1 1     |
| IV     | 8   | 7   | 3       | 32.1 | 7.6  | 84.9 | 12.3 | 182.4 | 5.9  | 25.5 | 3.2 | 41.7\*   | 4.0 | 8 0     |
| V-1    | 3   | 3   | 2       | 34.9 | 10.9 | 87.2 | 5.6  | 182.0 | 1.4  | 26.8 | 1.1 | 44.3     | 4.6 | 3 0     |
| V-2    | 1   | 1   | 1       | 42.7 | 0    | 65.8 | 0    | 165.1 | 0    | 24.2 | 0   | 31.2     | 0   | 0 1     |
| V-3    | 7   | 6   | 0       | 40.8 | 12.2 | 71.3 | 13.0 | 175.7 | 7.6  | 22.9 | 2.5 | 42.3     | 9.7 | 3 4     |
| total  | 28  | 25  | 9       | 35.2 | 9.8  | 76.6 | 13.5 | 176.5 | 9.4  | 24.5 | 2.8 | 40.3!!   | 6.8 | 19 9    |
| No DCS |     |     |         |      |      |      |      |       |      |      |     |          |     |         |
| I      | 42  | 17  | 0       | 28.9 | 7.3  | 76.2 | 13.7 | 176.7 | 9.6  | 24.2 | 3.0 | 39.2     | 7.3 | 31 11   |
| II     | 47  | 14  | 3       | 31.6 | 9.0  | 77.4 | 15.2 | 176.6 | 7.3  | 24.6 | 3.7 | 41.6     | 7.1 | 38 9    |
| III    | 7   | 0   | 0       | 28.2 | 6.3  | 81.4 | 6.2  | 178.4 | 4.2  | 25.5 | 1.7 | 42.3\*\* | 2.5 | 7 0     |
| IV     | 54  | 17  | 4       | 29.7 | 7.6  | 75.8 | 12.5 | 176.0 | 8.8  | 24.4 | 3.2 | 40.8!    | 4.9 | 39 15   |
| V-1    | 6   | 2   | 0       | 29.8 | 2.3  | 71.0 | 13.8 | 178.2 | 12.7 | 22.2 | 2.9 | 45.2     | 5.4 | 4 2     |
| V-2    | 2   | 2   | 1       | 37.5 | 3.6  | 86.4 | 37.5 | 177.1 | 18.8 | 26.7 | 6.3 | 36.9     | 2.2 | 1 1     |
| V-3    | 43  | 20  | 5       | 36.3 | 7.0  | 80.5 | 13.7 | 177.4 | 8.5  | 25.5 | 3.1 | 44.5     | 7.8 | 36 7    |
| total  | 201 | 72  | 13      | 31.4 | 8.0  | 77.4 | 13.8 | 176.7 | 8.6  | 24.6 | 3.2 | 41.6!!!  | 6.8 | 156 45  |

\* 8 of 8 had estimated VO₂ pk
\*\* 5 of 7 had estimated VO₂ pk
! 52 of 54 had estimated VO₂ pk
!! 8 of 28 had estimated VO₂ pk
!!! 57 of 201 had estimated VO₂ pk

31
---
# TABLE 8. Summary Statistics for Explanatory and Outcome Variables in the NM

| Phase | DCS    | VGE | GIV VGE | AGE  | SD   | WT   | SD   | HT    | SD   | BMI  | SD  | VO₂ Pk | SD  | SEX<br/>M F |
| ----- | ------ | --- | ------- | ---- | ---- | ---- | ---- | ----- | ---- | ---- | --- | ------ | --- | ----------- |
| I     | 9\*    | 8   | 2       | 29.8 | 9.3  | 68.0 | 11.3 | 169.4 | 11.0 | 23.6 | 2.9 | 35.4   | 6.9 | 4 5         |
| II    | 0      |     |         |      |      |      |      |       |      |      |     |        |     |             |
| III   | 2      | 1   | 1       | 36.0 | 9.4  | 77.1 | 19.2 | 174.0 | 9.0  | 25.2 | 3.7 | 36.5   | 9.5 | 1 1         |
| IV    | 0      |     |         |      |      |      |      |       |      |      |     |        |     |             |
| V-1   | 3      | 3   | 2       | 35.0 | 11.0 | 87.2 | 5.6  | 182.0 | 1.4  | 26.8 | 1.1 | 44.3   | 4.6 | 3 0         |
| V-2   | 1      | 1   | 1       | 42.7 | 0    | 65.8 | 0    | 165.1 | 0    | 24.2 | 0   | 31.2   | 0   | 0 1         |
| V-3   | 7      | 6   | 0       | 40.8 | 12.2 | 71.3 | 13.0 | 175.7 | 7.6  | 23.0 | 2.5 | 42.3   | 9.8 | 3 4         |
| total | 22\*   | 19  | 6       | 35.1 | 10.8 | 72.4 | 12.7 | 173.3 | 9.4  | 24.0 | 2.7 | 38.7   | 8.3 | 11 11       |
|       | No DCS |     |         |      |      |      |      |       |      |      |     |        |     |             |
| I     | 38     | 15  | 0       | 29.0 | 6.8  | 77.0 | 14.0 | 177.1 | 9.7  | 24.3 | 3.0 | 39.8   | 7.0 | 29 9        |
| II    | 45     | 14  | 3       | 31.7 | 9.0  | 77.6 | 15.4 | 176.3 | 7.8  | 24.8 | 4.0 | 40.8   | 7.2 | 35 10       |
| III   | 2      | 0   | 0       | 27.1 | 2.7  | 84.1 | 2.9  | 179.0 | 5.4  | 26.2 | 0.7 | 41.7   | 1.2 | 2 0         |
| IV    | 3      | 1   | 1       | 41.8 | 12.0 | 82.6 | 4.2  | 182.9 | 7.5  | 24.8 | 3.1 | 43.4   | 6.1 | 3 0         |
| V-1   | 6      | 2   | 0       | 29.8 | 2.3  | 71.6 | 13.8 | 178.2 | 12.7 | 22.2 | 2.9 | 45.2   | 5.4 | 4 2         |
| V-2   | 2      | 2   | 1       | 37.5 | 3.6  | 86.4 | 37.5 | 177.1 | 18.8 | 26.7 | 6.3 | 36.9   | 2.2 | 1 1         |
| V-3   | 41     | 19  | 5       | 36.2 | 7.1  | 81.2 | 13.6 | 177.8 | 8.5  | 25.5 | 3.1 | 44.3   | 7.3 | 35 6        |
| total | 137    | 53  | 10      | 32.5 | 8.2  | 78.5 | 14.5 | 177.3 | 8.8  | 24.8 | 3.4 | 41.8   | 7.2 | 109 28      |

\* two cases of DCS in Phase I reported after the test
---
## Exercise Prebreathe Model:

We must ultimately compute an ETR for each of the 159 records in the NM and 229 records in the RM. This ETR becomes the decompression dose for the LR model. The ratio of P1N₂ to P2 is the ETR, where P1N₂ is the calculated N₂ pressure after the ascent to altitude in a theoretical compartment with a variable half-time for N₂ pressure. Half-time is the time it takes to increase or decrease to one-half of the difference in the initial minus final condition, in our case N₂ pressure. Within four half-time periods about 94% of the difference in the initial minus final condition is achieved. The denominator of TR is P2, the ambient pressure after ascent. All of our depressurizations were to 4.3 psia since this is the operating pressure of the U.S. space suit.

Prebreathing 100% O₂ or O₂-enriched mixtures prior to an altitude exposure is often used to prevent DCS, so it is necessary to account for the use of O₂-enriched mixtures prior to the start of the altitude exposure. Equation 4 defines how P1N₂ is calculated. Following a change in N₂ partial pressure in the breathing mixture, such as during a switch from ambient air to a mask connected to 100% O₂, the N₂ partial pressure that is reached in a designated tissue compartment after a specific time is:

$$P1N₂ = P0 + (Pa - P0) * (1 - exp^{-k_i * t}),\quad\quad\quad\quad Eq. 4$$

where P1N₂ = the N₂ partial pressure in the tissue after "t" minutes, P0 = initial N₂ partial pressure in the compartment, Pa = ambient N₂ partial pressure in breathing mixture, exp = base of natural logarithm, and t = time at the new Pa in minutes. The tissue rate constant ki is related to the tissue N₂ half-time (t1/2) for N₂ pressure in a compartment. The "k" is equal to 0.693 / t1/2, where t1/2 is the half-time for N₂ partial pressure in the i₍th₎ minute compartment and 0.693 is the natural logarithm of two. The initial, equilibrium N₂ pressure (P0) in the tissue at sea level is taken as 11.6 psia instead of an average alveolar N₂ pressure of about 11.0 psia, a convention also used in some models for hyperbaric decompression. The use of dry-gas, ambient N₂
---
pressure as equilibrium tissue N₂ pressure (P₀) and as the N₂ pressure in the breathing mixture (Pa) makes the application of Eq. 4 simple. We chose to avoid the additional complexity of calculating alveolar N₂ pressure (indirectly with the alveolar O₂ equation) or measuring alveolar N₂ pressure in those tests where a mixture of 26.5% O₂ and 73.5% N₂ was breathed while at 10.2 psia.

## Functions that Define Half-Time Shift with Exercise:

The following are the functional structure of three equations, one of which will eventually define the best relationship between ki and mL·kg-1·min-1 to use in Eq. 4:

k1 = λ1 * mL·kg-1·min-1 + 0.0019254,                                                  Eq. 5

where the slope term λ1 is estimated by trial and error and additional parameters in the LR are estimated using maximum likelihood.

Figure 4 shows three examples of Eq. 5. Only three of an infinite number of isopleths are shown, where λ1 = 0.0003888 for the top curve, 0.0002888 for the middle curve, and 0.0001888 for the bottom curve. The best-fit to the DCS data could be a linear relationship between k and mL·kg-1·min-1 such that an incremental change in mL·kg-1·min-1 is associated with an incremental change in half-time compartment. Only a single slope term will be the best to define the change in half-time compartment through the exercise PB segments defined for each of the subjects in Phases I - V-3.
---
**hypothesis: exercise reduces DCS risk in proportion to exercise**

|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ```
exponential decay constant (k)
0.025 |                                                 /
|                                               /
0.020 |← t1/2 = 34.6                                /
|                                           /
0.015 |                                         /
|                                       /
0.010 |                                     /
|                                   /
0.005 |                                 /
|                               /
0.000 |← t1/2 = 360                 /
+-----+-----+-----+-----+-----+-----+
0    10    20    30    40    50    60
VO2 (ml/kg/min)
``` |

**Figure 4.** Linear relationship between k and mL∗kg⁻¹∗min⁻¹, which is the normalized VO₂ rate. The equation for the line is k₁ = λ₁ ∗ mL∗kg⁻¹∗min⁻¹ + 0.0019254, where the slope term is estimated by trial and error. When mL∗kg⁻¹∗min⁻¹ = 0, then k₁ = 0.0019254 or 360 t1/2 through t1/2 = ln2 / k₁.
---
$$k_2 = [(1 / \exp (-\lambda_2 * \text{mL}*\text{kg}^{-1}*\text{min}^{-1})) / 519.37],$$

where the slope term λ₂ is estimated by trial and error.                          Eq. 6

Figure 5 shows three examples of Eq. 6. Only three of an infinite number of isopleths are shown, where λ₂ = 0.045 for the top curve, 0.040 for the middle curve, and 0.035 for the bottom curve. The best fit to the DCS data may be a nonlinear relationship between k and mL*kg⁻¹*min⁻¹ such that light exercise is not as beneficial has heavy exercise. Only a single slope term will be the best to define the change in half-time compartment through the exercise PB segments defined for each of the subjects in Phases I - V-3.

|                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |   |   |   |   |   |
| ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | - | - | - | - | - |
| hypothesis: little extra exercise does not<br/>dramatically reduces DCS risk,<br/>but high exercise is important |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |   |   |   |   |   |
| 0.025                                                                                                            | \[This represents a graph showing three curves with different slope values. The top curve (λ₂ = 0.045) reaches about 0.023 at VO₂ = 60, the middle curve (λ₂ = 0.040) reaches about 0.018, and the bottom curve (λ₂ = 0.035) reaches about 0.013. The graph shows "t₁/₂ = 34.6" near the top curve and "t₁/₂ = 360" near the bottom where the curves begin. The x-axis shows VO₂ (ml/kg/min) from 0 to 60, and the y-axis shows exponential decay constant (k) from 0.000 to 0.025.] |   |   |   |   |   |
| 0.020                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |   |   |   |   |   |
| 0.015                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |   |   |   |   |   |
| 0.010                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |   |   |   |   |   |
| 0.005                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |   |   |   |   |   |
| 0.000                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |   |   |   |   |   |
| 0    10    20    30    40    50    60<br/>VO₂ (ml/kg/min)                                                        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |   |   |   |   |   |

Figure 5. Nonlinear relationship between k and mL*kg⁻¹*min⁻¹ with a slow initial response in the exponential decay constant with a change in normalized VO₂ rate. The equation for the curve is k₂ = [(1 / exp (-λ₂ * mL*kg⁻¹*min⁻¹)) / 519.37], where the slope term is estimated by trial and error. When mL*kg⁻¹*min⁻¹ = 0, then k₂ = 0.0019254 or 360 t₁/₂ through t₁/₂ = ln2 / k₂.
---
$$k_3 = ((1 - \exp (-\lambda_3 * \text{mL}*\text{kg}^{-1}*\text{min}^{-1})) / 51.937) + 0.0019254,$$        Eq. 7

where the slope term λ₃ is estimated by trial and error.

Figure 6 shows three examples of Eq. 7. Only three of an infinite number of isopleths are shown, where λ₃ = 0.25 for the top curve, 0.15 for the middle curve, and 0.05 for the bottom curve. The best-fit to the DCS data may be a nonlinear relationship between k and mL*kg⁻¹*min⁻¹ such that light exercise has a dramatic beneficial effect on decreasing the half-time compartment, but additional heavy exercise reaches a point of diminishing returns. Only a single slope term will be the best to define the change in half-time compartment through the exercise PB segments defined for each of subjects in Phases I - V-3.

|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |   |
| :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | - |
|                                                                                                                                                                                                                                                                                                                                                                          hypothesis: little extra exercise dramatically reduces DCS risk                                                                                                                                                                                                                                                                                                                                                                          |   |
| ```
0.025 |
|
0.020 |    t₁/₂= 34.6 ___-----------------------------
|   ,--''
0.015 |  /
| /
0.010 |/
|
0.005 |
|
0.000 | t₁/₂= 360
|_________________________________________________
0      10      20      30      40      50      60
VO2 (ml/kg/min)
``` |   |

Figure 6. Nonlinear relationship between k and mL*kg⁻¹*min⁻¹ with a rapid initial response in the exponential decay constant with a change in normalized VO₂ rate. The equation for the curve is k₃ = ((1 - exp (-λ₃ * mL*kg⁻¹*min⁻¹)) / 51.937) + 0.0019254, where the slope term is estimated by trial and error. When mL*kg⁻¹*min⁻¹ = 0, then k₃ = 0.0019254 or 360 t₁/₂ through t₁/₂ = ln2 / k₃.

37
---
## Logistic Regression Model:

Probabilistic modeling of DCS data requires four items: a) a data set that consists of a dichotomous response variable and one or more explanatory variables, b) a probability function that structures the model such that the outcome is a calculated probability between zero and one, c) a mechanistic model that is an expression of dose, and d) a parameter-estimation routine on a computer that uses maximum likelihood.

The logistic equation serves as our probability function, and has three characteristics. First, it is ideal in applications where the response variable is binary since the expected value of "Y" given the value of "x", symbolized as E(Y|x), must be bounded between zero and one. The conditional mean in this application is written as P(DCS), or more formally π^(x). Second, the change in π^(x) per unit change in "x" becomes progressively smaller as the conditional mean gets closer to zero or one. Third, the binomial, not the normal, distribution describes the distribution of errors when this equation is used with binary response data. As a result, the error has a distribution with mean zero, and variance that is not constant across all levels of the independent variable but equals [P(DCS) * (1 - P(DCS))]. There is no requirement of homoscedasticity (equality of variances) in LR.

The form of the logistic equation with only one independent variable is:

$$P(DCS) = \frac{\exp(B_0 + B_1x)}{(1 + \exp(B_0 + B_1x))} \quad \text{Eq. 8}$$

where B₀ is the intercept term, and B₁x is the slope for variable "x" on a plot of log of odds vs. "x". In this application, the log of odds, or logit, is ln[ P(DCS) / (1 - P(DCS))].

The logit transformation is a transformation of P(DCS) that is central to the application of LR. The logarithmic transformation linearizes the equation. The Logit module of SYSTAT®
---
(48,60) performs this transformation to calculate the log of odds, which is important in the calculation of the odds ratio, a measure of association between the independent and dependent variable. The logit transformation in this application is:

$$g(x) = \ln[ P(DCS) / (1 - P(DCS))] = B_0 + B_1x \quad \quad \quad \quad Eq. 9$$

and again, ln[ P(DCS) / (1 - P(DCS))] is called the log of odds or logit.

This transformation is important because the logit, [g(x)], is linear in its parameters, may be continuous, and may range from -∞ to +∞, depending on the range of "x". The logit is the log of the estimated odds of DCS given a value for "x" after B₀ and B₁x are found by maximizing the likelihood function.

If there are "n" explanatory variables, x₁, x₂, .... ,xₙ, the univariate logistic model is expanded to a multivariate logistic model as follows:

$$P(DCS)[x_1, x_2, .... ,x_n] = \exp(B_0 + B_1x_1 +...+ B_nx_n) / (1 + \exp(B_0 + B_1x_1 +...+ B_nx_n)) \quad Eq. 10$$

and the logit becomes:

$$\ln[P(DCS) / (1 - P(DCS))] = B_0 + B_1x_1 + ... + B_nx_n \quad \quad \quad \quad Eq. 11$$

Exponentiating the logit provides the odds of DCS, and the odds divided by 1 + odds gives the P(DCS). Note that it is not possible to draw a single dose-response curve from results of a multivariate LR. All but one covariate must be set constant to show how the P(DCS) changes through the range of the single independent variable of interest.

39
---
Now, for our specific case. The ETR after exercise PB is the dose for the LR. ETR is P1N₂ / 4.3. The numerator is computed using Eq. 6, for example, as k₂ = [(1 / exp(-λ₂ * mL*kg⁻¹*min⁻¹) / 519.37], where k₂ is used in Eq. 4 to compute P1N₂ across the exercise PB details for each subject once λ₂ is selected by trial and error. This means that three components make up the description of each PB interval performed by a subject: the elapsed time of the exercise during PB, the percentage of VO₂ pk as mL*kg⁻¹*min⁻¹ for the exercise during PB, and the P₁ for Eq. 4, usually zero ppN₂ for a 100% O₂ PB but would be 7.5 ppN₂ when the PB was continued at 10.2 psia while the subject breathed 26.5% O₂. Recall that P₁ is ambient N₂ partial pressure in breathing mixture. Now there were as few as five and as many as 32 intervals that defined the exercise PB to cover the seven tested exercise PB conditions (see Table 3). Intervals of rest were necessarily included, and 9.5% VO₂ pk was used for O₂ consumption during rest. Each of these intervals for each subject across all tests is assigned a half-time based on the value of λ used in either Eqs. 5,6, or 7. There can only be one best half-time for each interval depending on only one best λ value from either Eqs. 5,6, or 7. The outcome variable, DCS and no DCS, was used to find the value of λ from Eqs. 5,6, or 7 that best optimized the ETR expression of dose in the LR to the DCS outcome, using maximum likelihood optimization.

The denominator of ETR is a constant, 4.3 psia. So the simplest form of the LR is:

$$P(DCS) = exp(B_0 + B_1 * (P1N_2 / 4.3)) / (1 + exp B_0 + B_1 * (P1N_2 / 4.3))),        Eq. 12$$

where the values of B₀, B₁, and λ for the RM and the NM are estimated through the Logit module of SYSTAT®. Other explanatory variables such as age, sex, Body Mass Index (BMI), etc., are included to expand this basic LR model if they statistically contribute to the description of the DCS outcome.

An advantage of LR is the ability to include many variables, some of which may be on different measurement scales. When an explanatory variable is dichotomous it is inappropriate
---
to include it in the model as if it were a continuous, interval-scaled variable. Numbers used to represent various levels are merely identifiers, and have no numeric significance. Therefore, dummy variables are used to deal with our only polytomous categorical variable, the seven PB protocols. A polytomous variable has more than two categories. Converting a polytomous variable into a set of dummy variables is essentially creating n$$_c$$ - 1 dichotomous covariates where n$$_c$$ is the number of categories in the covariate. This variable was automatically converted by the computer to dummy variables for regressions that include them. But the results were very poor with this approach and no results are presented. Sex is the only dichotomous explanatory variable evaluated. A dichotomous covariate is coded as zero or one and treated as interval scaled. The remaining covariates are continuous, ordinal scaled.

## Measures of Goodness of Fit:

An important aspect of probabilistic modeling is to determine how confident one can be in an estimate of P(DCS) once the optimum parameters in a model are found. It is important to emphasize the distinction between the best fit of the model to the data and the goodness of fit of the model. With least squares or maximum likelihood, a function is optimized to the data regardless of the strength of the relationship between the independent and dependent variables. Goodness of fit, after obtaining the model with the best fit, is a measure of the agreement between the predicted outcome and the observed outcome. Without a measure of goodness of fit it is possible to be unjustifiably confident in the estimate of P(DCS).

In general, assessing the goodness of fit revolves around an overall summary measure of distance between actual (y$$_i$$) and estimated (y$$^_i$$) outcomes, and an examination of the individual components (y$$_i$$ - y$$^_i$$) of the summary statistics to identify outliers. The circumflex " ^ " denotes an estimate of the function. A model "fits" if summary measures of distance are small, and the contribution of each pair (y$$_i$$, y$$^_i$$) to these summary measures is unsystematic. In linear least squares regression, the sum of the differences between observed "y" and predicted "y$$^$$", the
---
residual, is a measure of agreement, and the goodness-of-fit statistic is the Coefficient of Determination (R²). The Coefficient of Determination is interpreted as the fraction of the variance in "y" predicted by "x". However, when the dependent variable is dichotomous and the data is fitted with a probability model, the difference between observed and predicted is not the same residual as defined in a linear least squares regression. In this case, one of two possible outcomes is observed, a yes (1) or no (0), but the predicted is a probability between zero and one.

The two summary measures of goodness-of-fit used here are: Hosmer-Lemeshow Goodness-of-Fit Test and One-Sample χ² Test, both of which provide an easily interpretable value that can be used to assess the fit. There are no quantitative methods available in the Logit module of SYSTAT® that help the user accept or reject a model based on the goodness of fit. Therefore, the user ultimately decides subjectively if the estimates of P(DCS) from the fitted model are useful. We also compare the LL of the best-fit NASA and Research continuous models to the null and discontinuous models. The difference in the LL number between the best-fit mechanistic model and the null and discontinuous models is used to assess goodness of fit of the NM and RM. The null model and discontinuous model are covered in the Results when the best fit NM and RM are described.

A high goodness of fit is not a validation of the model. It is expected that a model optimized to a set of training data will return an acceptable goodness of fit. Model validation is a separate process. Traditional approaches often involve randomly selecting a subset of data from the training set and comparing predicted outcome from the model to observed outcome in the subset. Another approach is to compare model predictions to outcomes from new data not used to optimize the initial model. Neither the NM nor the RM is validated as part of this report. Validation of the models is a subject for future work.
---
# Results

## Test of Hypothesis Data:

Before showing the results of the regressions, we show in Table 9 a summary of the results used in the test of hypothesis for the seven PBs. Phases I through V-3 were not designed to provide a range of data for a probability model. The analysis using multivariate statistical regression presents itself due to the complexity of the tested PBs. In all tests the goal was to only accept a PB option that produced ≤ 15% Type I DCS and ≤ 20% Grade IV VGE, with no Type II DCS and preferably in a sample of at least 50 subjects. Type I DCS include "pain only" symptoms in the limbs while Type II DCS includes signs and symptoms linked to disruptions in the cardiopulmonary and neurological systems. Grade IV VGE was defined earlier. We imposed that the accept condition for the PB had to meet or exceed 95% confidence. This means that the observed DCS and Grade IV VGE in a trial of 50 subjects could not exceed 6% and 10%, respectively. Table 9 shows that only Phase II met these accept conditions. Both Phase III and Phase V-2 had a case of Type II DCS, and no further testing was done.

### TABLE 9: Data for Test of Prebreathe Hypothesis

| Phase | Total n | Test of Hypothesis Data | Observed %DCS (n) | Observed %VGE (n) | Observed %Grade IV VGE (n) |
| ----- | ------- | ----------------------- | ----------------- | ----------------- | -------------------------- |
| I     | 49      | 47                      | 19.1\* (9)        | 48.9 (23)         | 4.2 (2)                    |
| II    | 50      | 45                      | 0 (0)             | 31.1 (14)         | 6.6 (3)                    |
| III   | 10      | 9                       | 22.2 (2)          | 11.1 (1)          | 11.1 (1)                   |
| IV    | 65      | 56                      | 14.3 (8)          | 41.0 (23)         | 12.5 (7)                   |
| V-1   | 10      | 9                       | 33.3 (3)          | 55.5 (5)          | 22.2 (2)                   |
| V-2   | 4       | 3                       | 33.3 (1)          | 100 (3)           | 66.6 (2)                   |
| V-3   | 50      | 48                      | 14.6 (7)          | 52.1 (25)         | 10.4 (5)                   |
| Sum   | 238     | 217                     | 30 DCS cases      | 94 VGE cases      | 22 Grade IV VGE cases      |

\* two cases of DCS reported after altitude exposure was completed
---
## Research Model:

Table 10 shows the results of optimizing nested models to the 229 exposures in the RM that resulted in 28 cases of DCS in seven tests. The first model in Table 10 is the null model. The null model is a constant-probability model based on the mean DCS incidence for all the individuals in the data set, 12.2% in this case. The null model has a single degree of freedom, and the LL necessarily represents a poor fit to a response variable; all explanatory variables are assumed irrelevant to the outcome. The null model returned a LL number of 85.05, using absolute value for LL. In the same data set, the LL from a discontinuous model is defined as the best, or perfect LL based on the assertion that the DCS incidence in each test is the true DCS incidence. The LL for the discontinuous model is 76.58. Equation 13 is used to compute the LL for the discontinuous model:

$$LL = \sum_{i=1}^{n} \ln [(1-c_i)^{nodcs_i} * (c_i)^{dcs_i}] \quad \text{Eq. 13}$$

where "n" is the number of tests, c₍ᵢ₎ is the fraction of subjects with DCS in test "i", nodcs₍ᵢ₎ is the number of subjects without DCS in test "i", and dcs₍ᵢ₎ is the number of subjects with DCS in test "i". Equation 13 uses the number of subjects in a particular test with and without DCS, and the incidence of DCS in the test. The discontinuous model has as many degrees of freedom as there are tests, seven in this case. A continuous model like the RM based on theory would not necessarily predict the observed DCS incidence, so the summed LL would always exceed the summed LL for the discontinuous model.

Accounting for the use of O₂ during the PB with a 360 min half-time compartment in a two-parameter LR reduced the LL to 81.61. So TR based on a 360 min half-time compartment at the start of exercise at 4.3 psia is helpful. However, exercise during the PB is expected to accelerate N₂ washout, so a model with the provision to change the half-time compartment over an interval of exercise activity that is functionally linked to the percentage of VO₂ pk in that
---
same interval is expected to be an improvement. The LL for the ETR model did decrease to 80.17 when λ₂ from Eq. 6 was 0.025. The same improvement in LL did not occur when λ₁ from Eq. 5 or λ₃ from Eq. 7 were evaluated over a wide range of values (results not shown). So the DCS outcome in the final RM, and also the NM, are best described with a model that says modest exercise intensity as defined by the percentage of VO₂ pk is helpful, but greater exercise intensity is best if the goal is to reduce the risk of DCS with exercise during PB. Figure 5 shows this functional relationship for three examples of λ₂.

Due to a limitation in the automated SYSTAT® process to optimize these models, the value of λ₂ was obtained in a trial and error fashion where new values were tried after each model optimization until there was no further improvement (decrease) in the LL. The ETR model with the LL of 80.17 is a three-parameter model since there are three degrees of freedom in which to optimize the observed incidence of DCS with the predicted incidence of DCS. But only the B₀ and Bₙ coefficients of this model have a standard error, and therefore computed p-values. This deficiency should be resolved in the next update to the model. This same limitation is the reason that only a best estimate of DCS risk is provided, without the ability to compute a confidence interval for the best estimate of P(DCS).

The improvement of the ETR model continued as useful explanatory variables were added. The addition of age and sex decreased the LL to 77.36, but sex was not significant enough to remain in the model (p = 0.49). The best model located at the bottom of Table 10 accounts for exercise during the PB and the age of the subject, and this model is called the RM. The positive sign on the coefficient for age in the RM means that the P(DCS) increases when age increases. The odds ratio for age was 1.055, with 1.008 to 1.103 as the lower and upper 95% bounds on the odds ratio. In this case, the odds ratio is the ratio of odds of DCS per year to the odds of DCS for a particular age. An example is helpful. The odds of DCS increased from 0.019 to 0.033 for a 10 year increase in age from 30 to 40 given an ETR of 1.8. Since the P(DCS) = odds / 1 + odds, the P(DCS) in this example increased from 1.9% to 3.2% for a 10 year increase in age.
---
A LL of 77.58 for the RM is a statistically significant improvement based on the Likelihood Ratio Test over the null model, the model with a constant 360 min half-time tissue compartment, and a model that just accounted for exercise during the PB. The Likelihood Ratio Test determines if the inclusion of an additional degree of freedom (an additional fitted parameter) significantly improves a particular model. It is the preferred method for hypothesis testing when using maximum likelihood. The test involves comparing the LLs of two models, the restricted and unrestricted, fitted to the same set of data. A restricted model can contain a single parameter, called the null model. The restricted model always has fewer degrees of freedom than the unrestricted model. The idea is to test if the addition of one or more parameters to the unrestricted model is better than the null model, or other restricted model, by testing the hypothesis that the additional coefficient in a model is equal to zero.

The value of the Likelihood Ratio statistic is calculated as two times the difference in the LL between the unrestricted and restricted models, which are different by at least one estimated parameter. The statistic follows an approximate $$\chi^2$$ distribution with degrees of freedom equal to the difference in the degrees of freedom between the unrestricted and restricted models. The value of the statistic and the degrees of freedom are entered into a $$\chi^2$$ table to find the corresponding $$\chi^2$$ p-value. A p-value less than 0.05 is generally taken to mean that the null hypothesis should be rejected, i.e., that the additional parameter is not equal to zero.

In addition to information on the parameter estimates, there is information on the goodness of fit of the models. For example, the ETR model with a LL of 80.17 shows a p-value of 0.31 based on the Hosmer-Lemshow statistic. The Hosmer-Lemeshow Goodness-of-Fit test provides a calculated statistic (C) and degrees of freedom for the logistic model. The distribution of the statistic C is approximated by the $$\chi^2$$ distribution with g - 2 degrees of freedom where "g" is the number of groups, usually ten. The number of groups is based on the values of the estimated probabilities, and is automatically calculated in the Logit module of SYSTAT®. The groups form a Deciles of Risk Table that is part of the output from the Logit module. The information in each cell of the table quantifies how well the model predicts the observations in a specific region of the data. The C statistic is used here to summarize the goodness of fit of the
---
model to the entire set of data. The p-value from a χ² table for the C statistic is provided, and the larger the p-value, the better the goodness of fit.

## TABLE 10: Seven Research Model Results

|                            |           |                   |               |
| -------------------------- | --------- | ----------------- | ------------- |
| Research Model             | N = 229   | DCS = 28 cases    |               |
| Null model LL              | 85.05     | 12.2% DCS         |               |
| Discontinuous model        | 76.58     |                   |               |
| TR360 model LL             | 81.61     |                   |               |
| ETR model LL               | 80.17     |                   |               |
| PARAMETER                  | ESTIMATE  | STANDARD ERROR    | P-VALUE       |
| constant                   | -29.11    | 8.718             | 0.001         |
| ETR                        | 14.11     | 4.513             | 0.002         |
| λ₂                         | 0.025     | not available     | not available |
| Hosmer-Lemshow C statistic | C = 3.549 | 3 degrees freedom | 0.31          |
|                            |           |                   |               |
| ETR+age+sex LL             | 77.36     |                   |               |
| PARAMETER                  | ESTIMATE  | STANDARD ERROR    | P-VALUE       |
| constant                   | -30.41    | 9.24              | 0.001         |
| ETR                        | 13.96     | 4.70              | 0.003         |
| age                        | 0.055     | 0.023             | 0.018         |
| sex                        | -0.32     | 0.473             | 0.49\*        |
| λ₂                         | 0.025     | not available     | not available |
| Hosmer-Lemshow C statistic | C = 4.45  | 5 degrees freedom | 0.48          |
|                            |           |                   |               |
| ETR+sex LL                 | 80.09     |                   |               |
| PARAMETER                  | ESTIMATE  | STANDARD ERROR    | P-VALUE       |
| constant                   | -28.19    | 9.01              | 0.002         |
| ETR                        | 13.71     | 4.62              | 0.003         |
| sex                        | -0.192    | 0.46              | 0.68\*        |
| λ₂                         | 0.025     | not available     | not available |
| Hosmer-Lemshow C statistic | C = 4.99  | 4 degrees freedom | 0.29          |
|                            |           |                   |               |
| ETR+age LL                 | 77.58     |                   |               |
| PARAMETER                  | ESTIMATE  | STANDARD ERROR    | P-VALUE       |
| constant                   | -31.717   | 9.000             | 0.000         |
| ETR                        | 14.55     | 4.600             | 0.002         |
| age                        | 0.053     | 0.023             | 0.021         |
| λ₂                         | 0.025     | not available     | not available |
| Hosmer-Lemshow C statistic | C = 3.851 | 5 degrees freedom | 0.57          |

---
\* parameter not significant enough to remain in model

Table 11 shows the comparison between the observed and predicted DCS outcome using the best-fit RM from the bottom of Table 10. The RM over predicted the results for Phase II, but either over or under predicted the remaining results. Therefore, the RM is not biased high or low. Besides a visual impression about how well the RM predicts the observed DCS, these data are also used in a One-Sample χ² Test as a second means to quantify goodness of fit. The test compares an observed distribution to a theoretical one. The null hypothesis is that there is no difference between the distributions. In the case where estimated always equals observed, the sum of all χ² values computed for each of the seven tests is zero. A p-value greater than 0.05 indicates that there is no statistical difference between the two sets of outcomes, the ones observed and ones predicted with a model. The RM gave a χ² of 6.25, and with three degrees of freedom (7 tests – 4 degrees of freedom in RM) the p-value was 0.10.

### TABLE 11: Observed versus Predicted DCS with Research Model

| Phase | n  | mean age | estimated oxygen consumption (l) | Observed %DCS | Predicted %DCS\* |
| ----- | -- | -------- | -------------------------------- | ------------- | ---------------- |
| I     | 49 | 29.41    | 76.5 ± 20.1                      | 14.3 (7)      | 12.8             |
| II    | 47 | 31.66    | 88.1 ± 20.7                      | 0 (0)         | 6.3              |
| III   | 9  | 29.94    | 60.2 ± 6.2                       | 22.2 (2)      | 11.5             |
| IV    | 62 | 30.0     | 66.7 ± 12.3                      | 12.9 (8)      | 9.3              |
| V-1   | 9  | 31.53    | 78.4 ± 15.5                      | 33.3 (3)      | 34.3             |
| V-2   | 3  | 39.23    | 62.0 ± 28.5                      | 33.3 (1)      | 55.4             |
| V-3   | 50 | 36.96    | 92.5 ± 22.2                      | 14.0 (7)      | 9.5              |

\* prediction based on model with age included
---
## NASA Model:

Table 12 shows the results of optimizing nested models to the 159 exposures on the NM that resulted in 22 cases of DCS in seven tests. Note that two cases of DCS in Phase I were reported after the conclusion of the test. These cases are included in the NM, but not the RM. Again, the LL numbers for the null and discontinuous models are shown to give the worst and best fit to these data. As before with the description of the RM, the LL improved as exercise during the PB is accounted for by fitting the $$\lambda_2$$ value from Eq. 6, and by expanding the LR to include other helpful explanatory variables. The best-fit NM required a $$\lambda_2$$ value of 0.030. In these data, sex and not age was selected as a variable that improved the description of the DCS outcomes. The negative sign on the coefficient for sex in the NM means that the P(DCS) is reduced when sex is male. The odds ratio for sex was 0.355 with 0.133 to 0.945 as the lower and upper 95% bounds on the odds ratio for sex. Explaining the odds ratio for sex is easier than for age in the RM since sex is binary while age is on a continuous scale. In this case, the odds ratio is the ratio of odds of DCS for sex = 1 to the odds for sex = 0. Because of our convention to code male = 1 and female = 0, the smaller the odds ratio, the stronger the effect. A person decreases the odds for DCS by a factor of about three (1 / 0.355) when sex is male. An example is helpful. The odds increase from 0.030 to 0.085 if gender is female and ETR is 1.8 for this example. Odds of DCS converts to P(DCS) through the expression odds / 1 + odds, so in this example the P(DCS) increases from 2.9% to 7.8% if gender is female and ETR is 1.8. The best-fit NM at the bottom of Table 12 had a p-value of 0.70 from the Hosmer-Lemshow C statistic, indicating a good fit of the model to the data.
---
## TABLE 12: Seven NASA Model Results

|                            |           |                   |               |
| -------------------------- | --------- | ----------------- | ------------- |
| NASA Model                 | N = 159   | TDCS\* = 22 cases |               |
| Null model LL              | 63.91     | 13.8% TDCS        |               |
| Discontinuous model        | 53.29     |                   |               |
| TR360 model LL             | 60.39     |                   |               |
| ETR model LL               | 58.36     |                   |               |
| PARAMETER                  | ESTIMATE  | STANDARD ERROR    | P-VALUE       |
| Constant                   | -30.02    | 8.81              | 0.000         |
| ETR                        | 14.80     | 4.59              | 0.001         |
| λ₂                         | 0.030     | not available     | not available |
| Hosmer-Lemshow C statistic | C = 0.834 | 4 degrees freedom | 0.93          |
|                            |           |                   |               |
| ETR+age LL                 | 57.32     |                   |               |
| PARAMETER                  | ESTIMATE  | STANDARD ERROR    | P-VALUE       |
| constant                   | -32.23    | 9.187             | 0.000         |
| ETR                        | 15.29     | 4.72              | 0.001         |
| age                        | 0.038     | 0.026             | 0.141\*\*     |
| λ₂                         | 0.030     | not available     | not available |
| Hosmer-Lemshow C statistic | C = 5.518 | 5 degrees freedom | 0.35          |
|                            |           |                   |               |
| ETR+age+sex LL             | 54.83     |                   |               |
| PARAMETER                  | ESTIMATE  | STANDARD ERROR    | P-VALUE       |
| constant                   | -28.18    | 9.68              | 0.004         |
| ETR                        | 13.41     | 4.95              | 0.007         |
| age                        | 0.047     | 0.027             | 0.085\*\*     |
| sex                        | -1.158    | 0.51              | 0.024         |
| λ₂                         | 0.030     | not available     | not available |
| Hosmer-Lemshow C statistic | C = 8.851 | 6 degrees freedom | 0.18          |
|                            |           |                   |               |
| ETR+sex LL                 | 56.28     |                   |               |
| PARAMETER                  | ESTIMATE  | STANDARD ERROR    | P-VALUE       |
| constant                   | -25.56    | 9.30              | 0.006         |
| ETR                        | 12.83     | 4.83              | 0.008         |
| sex                        | -1.037    | 0.50              | 0.038         |
| λ₂                         | 0.030     | not available     | not available |
| Hosmer-Lemshow C statistic | C = 2.997 | 5 degrees freedom | 0.70          |

\* two cases of DCS in Phase I reported after test
\** parameter not significant enough to remain in model
---
Table 13 shows that the NM also over predicted the results from Phase II, just like the RM in Table 11. The p-value from the One-Sample χ² test was 0.014 given a computed χ² of 10.62 with three degrees of freedom, which indicates the NM has a poorer goodness of fit compared to the RM using this statistic.

| TABLE 13: Observed versus Predicted DCS with NASA Model<br/>Phase | TABLE 13: Observed versus Predicted DCS with NASA Model<br/>n | TABLE 13: Observed versus Predicted DCS with NASA Model<br/>mean age | TABLE 13: Observed versus Predicted DCS with NASA Model<br/>gender (% male) | TABLE 13: Observed versus Predicted DCS with NASA Model<br/>estimated oxygen consumption (l) | TABLE 13: Observed versus Predicted DCS with NASA Model<br/>Observed %TDCS | TABLE 13: Observed versus Predicted DCS with NASA Model<br/>Predicted %TDCS\*\* |
| ----------------------------------------------------------------- | ------------------------------------------------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| I                                                                 | 47                                                            | 29.19                                                                | 0.70                                                                        | 76.5 ± 20.5                                                                                  | 19.1\* (9)                                                                 | 16.0                                                                            |
| II                                                                | 45                                                            | 31.76                                                                | 0.78                                                                        | 86.1 ± 20.2                                                                                  | 0 (0)                                                                      | 7.5                                                                             |
| III                                                               | 4                                                             | 31.57                                                                | 0.75                                                                        | 57.3 ± 8.6                                                                                   | 50.0 (2)                                                                   | 15.5                                                                            |
| IV                                                                | 3                                                             | 41.80                                                                | 1.00                                                                        | 75.2 ± 9.0                                                                                   | 0 (0)                                                                      | 9.6                                                                             |
| V-1                                                               | 9                                                             | 31.53                                                                | 0.78                                                                        | 78.4 ± 15.5                                                                                  | 33.3 (3)                                                                   | 30.6                                                                            |
| V-2                                                               | 3                                                             | 39.23                                                                | 0.33                                                                        | 62.0 ± 28.5                                                                                  | 33.3 (1)                                                                   | 53.4                                                                            |
| V-3                                                               | 48                                                            | 36.92                                                                | 0.79                                                                        | 92.7 ± 21.8                                                                                  | 14.6 (7)                                                                   | 7.4                                                                             |

* two cases of DCS in Phase I reported after test
** prediction based on model with sex included

In summary, we exploited all the otherwise acceptable data in the case of the RM by first estimating an important explanatory variable, the VO₂ pk, in about ¼ of the data. A more conservative approach was taken with the NM in that only data with measured VO₂ pk was evaluated. Each model has a similar ability to describe the DCS outcome. The RM is based on the most data, and predicts closer to the observed outcomes in seven tests. But we are less confidence in the estimate of DCS risk since 65 of the 229 records used in the model had an estimate of VO₂ pk. The alternative model based on 159 records does not predict as well, but we are more confident in the prediction since all the critical VO₂ pk data was measured. Figure 7 reiterates the point that the χ₂ value for the NM and RM are similar. Figures 8 and 9 are about the applications of the RM and NM. The user can get an appreciation for the change in DCS risk given a particular ETR and the age of the subject using Fig. 8. Figure 9 shows that for a given ETR in the NM, the risk for DCS is greater if you are female.
---
**Figure 7.** Best nonlinear relationship between k and mL∙kg⁻¹∙min⁻¹ for the NM and the RM compared to a model with a constant 360 min half-time compartment. The equation for the curves are k₂ = [(1 / exp (-λ₂ * mL∙kg⁻¹∙min⁻¹)) / 519.37], where the slope term λ₂ is 0.030 for the NM and 0.025 for the RM. At a very high O₂ consumption of 50 mL∙kg⁻¹∙min⁻¹ the half-time compartment has decreased from 360 min to 81 min for the NM and 99 min for the RM. The decrease in LL from the constant compartment model to a variable compartment model with exercise during PB is statistically significant for both the NM and RM.

|                                                                                                                                                                                                                                                                                     |   |   |   |   |   |   |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | - | - | - | - | - | - |
| **Graph: Relationship between exponential decay constant (k) and VO2**                                                                                                                                                                                                              |   |   |   |   |   |   |
| Y-axis: exponential decay constant (k) ranging from 0.000 to 0.015<br/>X-axis: VO2 (ml/kg/min) ranging from 0 to 60                                                                                                                                                                 |   |   |   |   |   |   |
| The graph shows two curves:<br/>- Upper curve: NASA MDL (ll = 56.3), reaching approximately k = 0.012 at VO2 = 60<br/>- Lower curve: RESH MDL (ll = 77.6), reaching approximately k = 0.008 at VO2 = 60<br/>- At the bottom of the graph: NASA MDL ll = 60.4 and RESH MDL ll = 81.6 |   |   |   |   |   |   |

---
## Figure 8. RM that shows P(DCS) as a function of ETR and age

|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ```
0.50 |                                        /
0.45 |                                      /50 years
0.40 |                                    /
0.35 |                                  /
0.30 |                                /40 years
0.25 |                              /
0.20 |                           /
0.15 |                        /30 years
0.10 |                     /
0.05 |                  /
0.00 |________________/___________________
1.60 1.65 1.70 1.75 1.80 1.85 1.90 1.95 2.00
Exercise Tissue Ratio
``` |

Figure 8. RM that shows P(DCS) as a function of ETR and age. As simulated age increases from 30 to 40 to 50 years, the P(DCS) for a given ETR increases. Gender was not an explanatory variable in these data, but 76.4% of 229 exposures were with males. The average age from Phase I through V-3 was 31.9 years ± 8.3 SD. Recall, that these estimates only apply to people who do similar exercise during PB and while at 4.3 psia as was done in the actual testing. These subjects were all semi-recumbent during the PB and while at altitude as a means to prevent ambulation.
---
| P(DCS) as a function of ETR and gender<br/>P(DCS) | P(DCS) as a function of ETR and gender<br/>Exercise Tissue Ratio (ETR)<br/>1.60 | P(DCS) as a function of ETR and gender<br/>Exercise Tissue Ratio (ETR)<br/>1.65 | P(DCS) as a function of ETR and gender<br/>Exercise Tissue Ratio (ETR)<br/>1.70 | P(DCS) as a function of ETR and gender<br/>Exercise Tissue Ratio (ETR)<br/>1.75 | P(DCS) as a function of ETR and gender<br/>Exercise Tissue Ratio (ETR)<br/>1.80 | P(DCS) as a function of ETR and gender<br/>Exercise Tissue Ratio (ETR)<br/>1.85 | P(DCS) as a function of ETR and gender<br/>Exercise Tissue Ratio (ETR)<br/>1.90 | P(DCS) as a function of ETR and gender<br/>Exercise Tissue Ratio (ETR)<br/>1.95-2.00 |
| ------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| 0.50                                              |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 | Female                                                                               |
| 0.45                                              |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                      |
| 0.40                                              |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                      |
| 0.35                                              |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                      |
| 0.30                                              |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                      |
| 0.25                                              |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 | Male                                                                                 |
| 0.20                                              |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 | Female curve rises                                                              |                                                                                      |
| 0.15                                              |                                                                                 |                                                                                 |                                                                                 |                                                                                 |                                                                                 | Female curve continues rising                                                   |                                                                                 |                                                                                      |
| 0.10                                              |                                                                                 |                                                                                 |                                                                                 |                                                                                 | Male curve begins rising                                                        |                                                                                 |                                                                                 |                                                                                      |
| 0.05                                              |                                                                                 |                                                                                 |                                                                                 | Both curves rise, female more steeply                                           |                                                                                 |                                                                                 |                                                                                 |                                                                                      |
| 0.00                                              | Both curves near zero                                                           |                                                                                 |                                                                                 | Both curves rise, female consistently higher                                    |                                                                                 |                                                                                 |                                                                                 |                                                                                      |

**Figure 9.** NM that shows P(DCS) as a function of ETR and gender. A female has a higher P(DCS) than a male at any given ETR. Age was not an explanatory variable in these data, but the average age was 32.8 years ± 8.6 SD. There was 75.5% male participation from Phase I through V-3 in the 159 exposures that comprise this set of data. Recall, that these estimates only apply to people who do similar exercise during PB and while at 4.3 psia as was done in the actual testing. These subjects were all semi-recumbent during the PB and while at altitude as a means to prevent ambulation.
---
## Summary of VGE Results:

This report is about the risk of DCS at 4.3 psia after exercise PB, but a large amount of VGE data were collected. The VGE data are not described in detail, but only in a brief summary. Figure 10 shows how the fraction of VGE detected in the pulmonary artery changed through time for tests where enough data were collected to justify this analysis (Phases I, II, IV, and V-3). The x-axis is time in epochs when VGE data were collected. An epoch represents 16 min of time. The x-axis shows the fraction of VGE from the combined left and right legs (lower body). For example, if there were 48 measurements in the left leg and 48 measurements in the right leg at epoch 3, and VGE of any grade appeared five times in the left leg and six times in the right leg, then the fraction of lower body VGE for epoch 3 is 11 / 96 = 11.4%, and so on. The mean DCS times ± SD are shown in relation to the changing VGE fraction through time. There is no mean DCS time for Phase II since there was no DCS. The mean DCS time is statistically longer for Phase V-3 compared to Phase IV, 139 versus 87 min, p = 0.04 by unpaired t-test. The curves in Fig. 10 are just descriptive; we make no attempt to determine if there is a statistical difference between any curve. The details of the exercise PB for Phase V-3 and Phase IV are provided in the Appendix for those who wish to attribute the difference in DCS time to some aspect of the exercise during the PB.
---
## Fraction of VGE from the Lower Body in Test of Hypothesis Data from Phase I (n=47), Phase II (n=45), Phase IV (n=56), and Phase V-3 (n=48)

| Time at 4.3 psia (epochs) | Fraction of VGE in pulmonary artery | Data Points                               | Phase          |
| ------------------------- | ----------------------------------- | ----------------------------------------- | -------------- |
| 0                         | 0.00                                |                                           | All Phases     |
| 3                         | 0.05-0.10                           |                                           | All Phases     |
| 6                         | 0.10-0.21                           | 104 ±28\* (Phase I)<br/>87 ±48 (Phase IV) | I, II, IV, V-3 |
| 9                         | 0.15-0.21                           | 139 ±43 (Phase V-3)                       | I, II, IV, V-3 |
| 12                        | 0.05-0.20                           |                                           | I, II, IV, V-3 |
| 15                        | 0.00-0.15                           |                                           | I, II, IV, V-3 |

\* two cases of DCS after test in Phase I not part of mean DCS time.
Difference in mean DCS time between Phase IV and Phase V-3 significant with unpaired t-test (p=0.04)

**Figure 10.** The change in VGE incidence in the lower body through time. Bubbles appear in the pulmonary artery shortly after ascent to 4.3 psia at the conclusion of the exercise PB protocols in Phases I, II, IV, and V-3. Notice that the mean time to report DCS symptoms appears near the point of greatest VGE occurrence.
---
## Order of Ergometry and VGE Latency Time:

The implementation of the ergometry exercise PB on the ISS requires that the first EVA astronaut start the ergometry while the second astronaut starts a resting PB. After 10 – 15 min, the second astronaut starts the ergometry, and then both complete the balance of the PB along the same time line. A similar situation was present in our testing of the exercise PB since there were often three subjects per test but only two sets of dual-cycle ergometers. So someone had to go first and someone had to go second after the start of PB. The ergometry required 10 min to complete, and there was about a five-min transition to get one subject off the ergometer and a second subject on the ergometer and ready to start their exercise prescription. We evaluated if the order of ergometry, only separated by at most 15 min, was an important consideration for the DCS and VGE outcomes.

Tables 14 and 15 show the DCS and VGE results for 27 subjects that did ergometry first and 27 subjects that did ergometry second. These results are from Phases I and II; no other tests provided the opportunity to study an order-effect for dual-cycle ergometry. Table 14 lists several physical characteristics for the 13 subjects that had VGE compared to 14 subjects without VGE in those that went first with ergometry exercise. There was no statistical difference in age, weight, height, gender distribution, or BMI between these groups. Notice that the mean latency time to the first detection of VGE was 53.5 ± 31.6 min. Compare these results with the same variables in Table 15 where 27 subjects went second with ergometry exercise. It is notable that the VGE latency time in this group increased to 94.1 ± 54.9 min, an increase that is statistically significant at p < 0.05 with unpaired t-test. There was no statistical difference in the DCS incidence (p = 0.28 with Fishers Exact χ²) between these groups and no difference in the VGE incidence, both with 13 of 27 subjects with VGE.
---
## TABLE 14. Physical Characteristics and Results from Subjects that did Ergometry First

===============================================================

### Phase I study

| age                                                                                                                       | weight | height | gender | BMI       | DCS   | max | VGE latency |
| ------------------------------------------------------------------------------------------------------------------------- | ------ | ------ | ------ | --------- | ----- | --- | ----------- |
| (yrs)                                                                                                                     | (kg)   | (m)    | 1=male | (kg / m2) | 1=yes | VGE | time (min)  |
| ------------------------------------------------------------------------------------------------------------------------- |        |        |        |           |       |     |             |
| 39.7                                                                                                                      | 93.0   | 1.78   | 1      | 29.4      | 0     | I   | 123         |
| 24.7                                                                                                                      | 54.4   | 1.69   | 0      | 19.1      | 0     | II  | 33          |
| 46.3                                                                                                                      | 86.2   | 1.85   | 1      | 25.1      | 1     | IV  | 16          |
| 29.3                                                                                                                      | 76.2   | 1.80   | 1      | 23.4      | 0     | I   | 51          |
| 37.0                                                                                                                      | 77.1   | 1.83   | 1      | 23.0      | 0     | I   | 71          |
| 21.9                                                                                                                      | 56.7   | 1.67   | 0      | 20.2      | 1\*   | I   | 74          |
| 27.3                                                                                                                      | 63.5   | 1.52   | 0      | 27.3      | 1     | III | 49          |
| 23.7                                                                                                                      | 76.2   | 1.88   | 1      | 21.6      | 0     | III | 28          |

### Phase II study

|      |       |      |   |      |   |     |    |
| ---- | ----- | ---- | - | ---- | - | --- | -- |
| 20.2 | 79.4  | 1.85 | 1 | 23.1 | 0 | II  | 17 |
| 22.7 | 86.2  | 1.80 | 1 | 26.5 | 0 | I   | 57 |
| 23.5 | 54.4  | 1.65 | 0 | 20.0 | 0 | III | 48 |
| 29.3 | 68.8  | 1.83 | 1 | 20.6 | 0 | I   | 98 |
| 40.1 | 106.8 | 1.91 | 1 | 29.3 | 0 | III | 30 |

===============================================================
|      |      |      |      |          |      |   |   |      |
| ---- | ---- | ---- | ---- | -------- | ---- | - | - | ---- |
| mean | 29.7 | 75.3 | 1.77 | 70% male | 23.7 |   |   | 53.5 |
| SD   | 8.4  | 15.7 | 0.11 |          | 3.5  |   |   | 31.6 |

===============================================================

### Information from 14 that did not have VGE
-------------------------------------------------------------------------------------------------------------------------

|      |      |      |      |          |      |   |   |       |
| ---- | ---- | ---- | ---- | -------- | ---- | - | - | ----- |
| mean | 27.6 | 75.0 | 1.77 | 71% male | 23.7 | 0 | 0 | n / a |
| SD   | 6.7  | 12.8 | 0.08 |          | 2.3  |   |   |       |

===============================================================

\* DCS reported after the altitude exposure
---
## TABLE 15. Physical Characteristics and Results from Subjects that did Ergometry Second

| Phase I study<br/>age(yrs)                | Phase I study<br/>weight(kg) | Phase I study<br/>height(m) | Phase I study<br/>gender1=male | Phase I study<br/>BMI(kg / m²) | Phase I study<br/>DCS1=yes | Phase I study<br/>maxVGE | Phase I study<br/>VGE latencytime (min) | Phase I study |
| ----------------------------------------- | ---------------------------- | --------------------------- | ------------------------------ | ------------------------------ | -------------------------- | ------------------------ | --------------------------------------- | ------------- |
| 29.0                                      | 68.0                         | 1.70                        | 1                              | 23.5                           | 0                          | I                        | 118                                     |               |
| 24.7                                      | 68.0                         | 1.85                        | 1                              | 19.8                           | 0                          | I                        | 94                                      |               |
| 23.3                                      | 68.0                         | 1.63                        | 0                              | 25.7                           | 1\*                        | III                      | 75                                      |               |
| 26.6                                      | 77.1                         | 1.75                        | 0                              | 25.1                           | 0                          | I                        | 81                                      |               |
| 59.3                                      | 48.1                         | 1.48                        | 0                              | 21.8                           | 0                          | II                       | 83                                      |               |
| 35.9                                      | 83.0                         | 1.80                        | 1                              | 25.5                           | 0                          | I                        | 186                                     |               |
| 21.9                                      | 95.2                         | 1.93                        | 1                              | 25.6                           | 0                          | I                        | 59                                      |               |
| 28.8                                      | 83.9                         | 1.90                        | 1                              | 23.1                           | 0                          | I                        | 47                                      |               |
| Phase II study                            |                              |                             |                                |                                |                            |                          |                                         |               |
| 19.0                                      | 62.6                         | 1.70                        | 1                              | 21.6                           | 0                          | I                        | 187                                     |               |
| 22.4                                      | 62.6                         | 1.73                        | 1                              | 21.0                           | 0                          | I                        | 164                                     |               |
| 46.5                                      | 84.8                         | 1.82                        | 1                              | 25.6                           | 0                          | IV                       | 78                                      |               |
| 46.2                                      | 70.8                         | 1.80                        | 1                              | 21.8                           | 0                          | IV                       | 26                                      |               |
| 39.4                                      | 79.8                         | 1.74                        | 1                              | 26.4                           | 0                          | IV                       | 26                                      |               |
| mean                                      | 32.5                         | 73.2                        | 1.76                           | 77% male                       | 23.6                       |                          | 94.1                                    |               |
| SD                                        | 12.1                         | 12.3                        | 0.12                           |                                | 2.2                        |                          | 54.9                                    |               |
| Information from 14 that did not have VGE |                              |                             |                                |                                |                            |                          |                                         |               |
| mean                                      | 32.1                         | 78.3                        | 1.74                           | 78% male                       | 25.7                       | 0                        | 0                                       | n / a         |
| SD                                        | 13.2                         | 17.5                        | 0.08                           |                                | 4.4                        |                          |                                         |               |

\* DCS reported after the altitude exposure
Two cases with VGE latency times of 162 and 163 min were removed from the analysis because PB time inadvertently extended.
---
Figure 11 shows the cumulative VGE cases plotted against VGE latency times from Tables 14 and 15. We conclude that those who went first on the ergometers showed earlier VGE latency times compared to those who went second. There were no differences in the DCS or VGE incidence observed between the two groups. The differences in latency times cannot be attributed to the fact that these data are combined from two PB studies, Phase I and Phase II. Eight of the 13 subjects (61%) did ergometry first and did the Phase I study and eight of the 13 subjects (61%) did ergometry second and did the Phase I study.

| time at 4.3 psia (min) | cumulative VGE cases         | cumulative VGE cases          |
| ---------------------- | ---------------------------- | ----------------------------- |
|                        | ergometry done first, n = 13 | ergometry done second, n = 13 |
| 0                      | 0                            | 0                             |
| 30                     | 3                            | 1                             |
| 60                     | 9                            | 4                             |
| 90                     | 11                           | 8                             |
| 120                    | 13                           | 10                            |
| 150                    | 13                           | 12                            |
| 180                    | 13                           | 13                            |
| 210                    | 13                           | 13                            |
| 240                    | 13                           | 13                            |

Figure 11. VGE latency time is shorter when ergometry is done at the start of exercise PB rather than 10 to 15 minutes later. Filled circles show the latency time for the first detected VGE in 13 of 27 subjects that did dual-cycle ergometry first. Open circles show the latency times for the 13 of 27 subjects that did the ergometry second. The mean latency time was 53 ± 31 min in those that went first and 94 ± 55 min in those that went second (p < 0.05 from unpaired t-test).
---
Table 16 provides additional details about the VGE by comparing the number of VGE grades between those subjects that went first to those that went second on ergometry exercise. There is no difference due to the order of ergometry in the counts of Grade I VGE. However, if ergometry is done first you have more Grade 0 counts, more Grade II counts, but fewer Grade III and IV counts. If VGE grades are combined into low (Grade I + II) and high (Grade III + IV) categories (bottom of Table 16), then the order of ergometry does not matter for low grade (p = 0.44), but going first on the ergometer means you have fewer counts of high VGE (p < 0.05). If the goal is to avoid large numbers of Grade III and IV VGE and to have more cases where no VGE are detected (Grade 0 VGE), then it is best not to delay the start of ergometry during the PB even if an early start reduces the latency time to the first VGE.

## TABLE 16. Counts of VGE Grades when Ergometry is done First or Second

| VGE GRADE                   | ERGO. FST RESULTS | (counts / total) | ERGO. SCD RESULTS | (counts / total) | p-value\* |
| --------------------------- | ----------------- | ---------------- | ----------------- | ---------------- | --------- |
| **SEPARATE VGE CATEGORIES** |                   |                  |                   |                  |           |
| 0                           | 74.2%             | (507 / 683)      | 61.4%             | (341 / 555)      | <0.05     |
| I                           | 13.7%             | (94 / 683)       | 15.1%             | (84 / 555)       | 0.54      |
| II                          | 7.6%              | (52 / 683)       | 4.3%              | (24 / 555)       | 0.022     |
| III                         | 2.8%              | (19 / 683)       | 12.4%             | (69 / 555)       | <0.05     |
| IV                          | 1.6%              | (11 / 683)       | 6.6%              | (37 / 555)       | <0.05     |
| **COMBINED VGE CATEGORIES** |                   |                  |                   |                  |           |
| I + II                      | 21.3%             | (146 / 683)      | 19.4%             | (108 / 555)      | 0.54      |
| III + IV                    | 4.4%              | (30 / 683)       | 19.1%             | (106 / 555)      | <0.05     |

\* p-values from χ² test with number of VGE grades recorded compared to total VGE measurements across the two experimental conditions.
---
Finally, Fig. 12 shows the results of an analysis similar to that done for Fig. 10. The incidence of VGE is shown as a function of elapsed time at 4.3 psia, and epochs were converted into min. The solid curve is the best fit to VGE incidence data for those that went first on the dual-cycle ergometer, and the dashed curve are for those that went second. The best-fit solid (ergometry first) and dashed (ergometry second) curves come from a maximum likelihood optimization of a function that combines a recovery function and a response function: incidence of VGE = [exp $$-kt$$ * $$(t^a / (t^a + b^a))$$], where "t" is the elapsed time at altitude, the incidence of VGE are from the observed dichotomous outcomes, and k, a, and b are the fitted constants. The values of the constants to produce the solid curve are: k = 0.01027, a = 1.71, and b = 100.7, and for the dashed curve are: k = 0.00714, a = 2.138, and b = 119.1. The shifted pattern to the right is attributed to the later onset of VGE in the group that did ergometry second, but the shapes of the curves are similar.

|                                          |                                                            |    |    |    |     |     |     |     |     |
| ---------------------------------------- | ---------------------------------------------------------- | -- | -- | -- | --- | --- | --- | --- | --- |
| **Incidence of VGE in pulmonary artery** |                                                            |    |    |    |     |     |     |     |     |
| 0.25                                     |                                                            |    |    |    |     |     |     |     |     |
| 0.20                                     | • ○ ○                                                      |    |    |    |     |     |     |     |     |
| 0.15                                     | • ○ •                                                      |    |    |    |     |     |     |     |     |
| 0.10                                     | • • • •                                                    |    |    |    |     |     |     |     |     |
| 0.05                                     | • ○ • = ergometry done first<br/>○ = ergometry done second |    |    |    |     |     |     |     |     |
| 0.00                                     | ○                                                          |    |    |    |     |     |     |     |     |
|                                          | 0                                                          | 30 | 60 | 90 | 120 | 150 | 180 | 210 | 240 |
| time at 4.3 psia (min)                   |                                                            |    |    |    |     |     |     |     |     |

Figure 12. Incidence of VGE versus time at 4.3 psia and order of ergometry. Once VGE are first detected in the pulmonary artery there is usually a short lag phase, a rapid response phase, and a gradual recovery phase in the incidence of VGE through time. Filled circles show the incidence of VGE during 14 measurement opportunities in the 27 subjects that did the ergometry first. Open circles are the results for the 27 that did the ergometry second.
---
# Discussion

## Aerobic Fitness and Susceptibility to Hypobaric Decompression Sickness:

The central theme of this report and in this analysis is that aerobic fitness is an important consideration in a model that accounts for exercise during PB as a means to reduce the risk of DCS. Exercise is a powerful stimulus to increase tissue blood flow (2). A fit person, or even animal, is expected to mobilize the cardiopulmonary system to a greater degree than an unfit person (7,9,10,40,61,62). If fitness were not a significant consideration, then the NM and RM would not have performed well. It must be understood that the NM and RM are statistical models. The data files and models were structured to provide for the simplest treatment of the data and models to maximize the correlative relationship between VO₂ pk and DCS outcome. All exercise and even rest intervals were characterized as a percentage of VO₂ pk to apply one methodology, even when the exercise consisted of absolute work.

An example is helpful to demonstrate how the model works when DCS risk for absolute work during the PB is computed. Say that 6.0 mL*kg⁻¹*min⁻¹ O₂ consumption is assigned to a 70 kg and 80 kg person and each performs a two hr PB. The 70 kg person will consume 50.4 liters of O₂ compared to 57.6 liters for the 80 kg person over the two hrs, but each consume the same O₂ on a per kg per min basis. This O₂ consumption represents 14.3% of VO₂ pk based on a sample of subjects with a mean VO₂ pk of 42 mL*kg⁻¹*min⁻¹ (6 / 42 = 14.3%). In this example, the lighter person is fitter at 60 mL*kg⁻¹*min⁻¹VO₂ pk compared to the heavier person at 40 mL*kg⁻¹*min⁻¹VO₂ pk. If all that is know is that both consumed 6.0 mL*kg⁻¹*min⁻¹based on some absolute work, then the optimized model will compute the same P(DCS) for each person since it assigns a particular optimized half-time to a particular mL*kg⁻¹*min⁻¹. But if the fitness of the subject is also known, then a better estimate of risk for each person is available since fitness is factored into the estimate of P(DCS). The fit subject is "rewarded" in a statistical sense by having absolute work indexed upward since the absolute work is referenced to VO₂ pk. In this case, the fit person is assigned 8.5 mL*kg⁻¹*min⁻¹ while the unfit person is
---
assigned 5.7 mL·kg-1·min-1. These are not true values for O2 consumption, but do distinguish one person from the other by accounting for aerobic fitness. In this case, the fit person has less DCS risk than the unfit person, thus using the correlative information about DCS risk and aerobic fitness even though each person did an interval of absolute work during the PB.

Another point to make is that the benefit of exercise during PB is more than just total O2 consumption during the PB. There is also a component of how one consumes the O2 with exercise. It appears that intense, short duration exercise followed by intermittent light exercise for a given O2 consumption is more effective to reduce the risk of DCS than less intense intermittent exercise spaced over a longer period that still results in the same O2 consumption. This is seen in both the data and in the ETR models since the models reflect the trends in the data. For example, Table 9 shows the estimated O2 consumption for Phase II was 88 liter compared to 92 liters in Phase V-3. Even with slightly less computed O2 consumption the protocol with 75% VO2 pk for a very short period at the start of the PB resulted in no cases of DCS compared to Phase V-3. Phase I did not couple the 75% VO2 pk with light exercise and resulted in 76 liters of O2 consumption compared to Phase IV where intermittent light activity over 56 min resulted in 67 liters O2 consumption. Phase I had a higher observed and predicted DCS compared to Phase IV and yet more O2 was consumed in Phase I. The point is that just consuming greater than 70 liters of O2 during a PB, be it a long resting PB or a shorter exercise PB, to reduce the risk of DCS is not the only consideration. The way the O2 is consumed has a role. It appears that high intensity, short duration exercise followed by intermittent low intensity exercise for the balance of the PB is most beneficial. This has the effect of dramatically reducing the half-time in the models for N2 removal during the PB at a time when tissue N2 pressure is high. The mobilization of metabolic control of local tissue blood flow caused by an intense bout of exercise is then maintained by intermittent low intensity exercise that facilitates the muscle pump to return venous blood to the lungs. A fit subject actually consumes more O2 over the same period compared to an unfit subject, which ultimately translates to more blood flow per kg of metabolizing tissue per interval of time. This has the effect of keeping the half-time smaller
---
for faster N₂ removal in the fit person compared to the unfit person doing the same work as defined by a percentage of VO₂ pk.

## Age and Gender:

Recent reports document a statistical association between physical characteristics, such as age, gender, and physical fitness, and the risk of DCS and VGE in both diving (9,10,35,63) and aviation (12,13,24,45,46,49,56) decompressions. These reports confirm some of the observations about aviator DCS during World War II (25). Both the historical and recent reports stimulated us to evaluate gender and age as explanatory variables in these data. It is important to understand if there is an association with age in our DCS and VGE data since the average age on the day of EVA in 68 astronauts over 171 EVAs since the Space Shuttle became operational is 43.4 ± 5.1 years SD. This is about 10 years older than tests subjects used in our research.

Since there are limited data available to us, and since these PRP tests were not designed *per se* to evaluate fitness, gender, or age, it is inevitable that these explanatory variables come in to and out of statistical significance in the various regressions. Gender was found to be a significant explanatory variable in the NM, but gender was not a significant predictor variable in the RM. Age was found to be a significant explanatory variable in the RM, but not in the NM. We did not evaluate these explanatory variables in the VGE data for this report, but advancing age is associated with more VGE in an evaluation of similar data (12). We conclude that it is likely the lack of sufficient data that allows gender to be only significant in the NM, and only age to be significant in the RM. We suspect that both variables would be significant predictors of DCS given additional data collected in a way to specifically test these variables.

It is easy to understand how modification of some environmental variables affects the DCS outcome. If you dive deep, stay long, and ascend quickly to the surface, then you may acquire DCS. If you do not perform a PB, ascend to 4.3 psia (30,250 feet altitude) breathing 100% O₂, and vigorously exercise the lower body, then you may acquire DCS. What is difficult to understand and to show is how exercise during PB affects outcomes and how differences in
---
variables that defines who we are, like age, weight, and gender affect outcomes. It is even more difficult when some variables change in a cyclical fashion, such as water retention associated with the menstrual cycle in women (45,46,56,64). There are at least three factors to consider about gender and the risk of DCS: 1) change in DCS risk within the normal menstrual cycle, 2) change in DCS risk with the use of a contraceptive, and 3) difference in DCS risk between men and women. It gets even more complicated when age is superimposed on the menstrual cycle, or if there has been a hysterectomy.

The most recent information by Webb (56) draws seemingly contrary conclusions than recent information from Lee (36). However, the analysis by Webb included both DCS (numerator) and non‑DCS cases (denominator) in 269 women‑exposures to different altitudes while Lee only included those 150 women that presented themselves for hyperbaric treatment (numerator) after SCUBA diving. In each study there were data on a subset of women that used contraceptives. In summary, Webb showed that the use of contraceptive was associated with a greater risk of DCS, and Lee showed for those reporting with DCS, the use of contraceptive was irrelevant. Webb showed there was no increased risk of DCS in the first half of the menstrual cycle, and Lee showed for those with DCS, there is a greater number of cases associated with the first half of the menstrual cycle. Finally, Webb showed there is an increased risk of DCS in the second half of the menstrual cycle if women use contraceptive, and Lee showed for those with DCS, there is about the same number of cases associated with the second half of the menstrual cycle whether a contraceptive was used (29 / 63 = 46%) or was not used (31 / 87 = 36%). It is not surprising that there is still no consensus of opinion on how each of these factors alone or in combination affect the risk of DCS.

Age was a variable important to describe DCS in the RM. There is good documentation to show that increasing age is associated with increased reporting of DCS. Gray (25) showed a linear increase in relative DCS susceptibility with age over an 18 – 28 year range in men. Sulaiman et al (49) reported a three‑fold increase in susceptibility between the age group 18 – 21 years and the group greater than 42 years. This is in agreement with a three‑fold increase in incidence between 19 to 25 and 40 to 45 year olds published by Heimbach and Sheffield (28), and similar to results reported by Webb et al (56). Our inability to show an association between
---
age and DCS in the NM may be related to the low overall decompression stress of the tests in that subset of data and our inability to recruit large numbers of older subjects.

Body composition changes with age. Finch (19) described age-related changes in several body systems. There is an increase in fat content and a decrease in water content such that there is a linear decline in specific gravity from 1.080 at age 20 to 1.033 at age 70 years. The connective tissue matrix changes with age; collagen becomes more stable (less flexible), and the basal lamina becomes thicker. Cardiac output reduces about one percent per year along with an increase in peripheral vascular resistance. An aging lung may reduce the ability of the lung to filter VGE from the circulation or excrete the evolved gas to the atmosphere. The internal surface area of the lung declines linearly from about 75 m² at age 20 to 62 m² at age 70 years, vital capacity decreases with a subsequent increase in residual volume, and there is an increase in lung compliance. There is a progressive increase in the alveolar-arterial O₂ partial pressure difference with age attributed to diffusion impairment across the alveoli and by increased ventilation and perfusion mismatching.

In summary, aging favors more inert gas to be present with a reduced ability to transport the gas, dissolved or evolved, from the tissues to the lungs to the atmosphere. There is a steady decline in physical fitness with age. A decline in fitness rather than age *per se* may be more closely related to an increased risk of DCS and VGE, but the two are often linked (9,10,56). Some divers and aviators do "age better than others", so it is not justified to characterize all older men and women as being at a greater risk of DCS and VGE.

## Application of Models: An Example

Our application of these models is to prevent DCS in astronauts. The tests were conducted under conditions similar to what would actually be implemented by NASA if the test had a favorable outcome, i.e., ≤ 15% total DCS and ≤ 20% Grade IV VGE, both with 95% confidence. The tests were conducted with several important variables held constant, such as adynamia before and during the altitude exposure, the length of time at 4.3 psia, and the type and intensity of exercise done at 4.3 psia. In effect, variations of the exercise during the PB and the
---
length of the total PB were the only conditions that changed from one test to another if we assume our samples of subjects were comparable. The subjects did provide a narrow range for age, gender distribution, and aerobic fitness, but were otherwise homogeneous in height, weight, BMI, percentage of body fat, etc., due to our subject inclusion criteria. At best, the RM and NM would predict the same DCS outcome as observed given the same input conditions from the tests (see comparisons in Tables 11 and 13).

The further we deviate from the range of conditions from the tests the less confident we become in the predicted outcome when we apply the models to a simulated PB. It is preferable to interpolate within the range of experience in our tests rather than extrapolate to untested conditions, i.e., very short or very long total PB times, or exotic combinations of relative or absolute work during the PB. For example, there is no provision in these models to account for any other condition than adynamic. Adynamia is our analog of μ-gravity adaptation (23,42,51).

With the above preface, an example is provided to show the application of the NM and RM to a simulated 4-hr EVA from the proposed Crew Excursion Vehicle (CEV) during a trip to the moon; a simulation that is an extrapolation from the models since total PB time is short at 90 min, the crew live at 10.5 psia prior to the EVA, and the proposed exercise during the PB deviates from what was tested. In this example, the astronaut is a 43 yo male with a VO₂ pk of 50 mL•kg⁻¹•min⁻¹. He has been breathing a ppN₂ of 8.0 psia and a ppO₂ of 2.5 psia for several days. Therefore, the CEV environment provides a total pressure of 10.5 psia with 23.8% O₂ (2.5 / 10.5). The suit pressure is 4.3 psia, so the TR at the start of EVA is 1.86 (8.0 / 4.3) if no PB is performed. The NM predicts 6.1% DCS while the RM model predicts 8.6% DCS under these conditions, but PB associated with suit donning and slow depressurization to 4.3 psia would provide some protection from DCS. It is judged that this risk is unacceptable given the lack of hyperbaric treatment capability in the CEV. So an exercise PB option is planned.

Table 17 lists the details of the PB. The astronaut will exercise using dual-cycle ergometry at 50% of his VO₂ pk for 20 min while breathing O₂ from a mask. He continues to breathe from the mask an additional 20 min as he dons the Liquid Cooling and Ventilation Garment, and is active during this time at 20% VO₂ pk. He will then remove the mask and be
---
re-exposed to a ppN₂ of 8.0 psia in the CEV during a 20 min suit donning procedure. It is estimated that he will also work at 20% of VO₂ pk during this activity. Suit purge, leak check, and other final checks plus final ascent to 4.3 psia will take 30 min with the astronaut in a rested state, at 9.5% VO₂ pk.

## TABLE 17: Example Application of Exercise Prebreathe Models

|           |      |      |      |      |      |     |
| --------- | ---- | ---- | ---- | ---- | ---- | --- |
| PB        | 1    | 2    | 3    | 4    | 5    | 6   |
| activity  | W    | R    | T    | A    | A    | Q   |
| %VO₂      | 25.0 | 50.0 | 25.0 | 20.0 | 20.0 | 9.5 |
| ml/kg/min | 12.5 | 25.0 | 12.5 | 10.0 | 10.0 | 4.7 |
| time      | 3    | 17   | 3    | 17   | 20   | 30  |
| Pa        | 0    | 0    | 0    | 0    | 8.0  | 0   |

R = relative work (dual-cycle ergometry)
A = absolute work (crank-and-yank devices)
Q = quiet (rest) periods
T = transition from high intensity, low duration exercise to low intensity, long duration exercise, or transition from relative work to rest
W = warm up work (ramping up to dual-cycle relative work)

The information in Table 17 is evaluated by the computer using Eq. 4 with the optimized coefficients for λ₂ for both the NM (λ₂ = 0.030) and the RM (λ₂ = 0.025). The computed final tissue ppN2 is 6.62 psia for the NM and 6.69 psia for the RM. This is a decrease over 90 min from the initial equilibrium tissue ppN2 of 8.0 psia. Therefore, the computed ETR for the NM is 1.54 (6.62 / 4.3) and 1.55 (6.69 / 4.3) for the RM. The ETR for the NM plus the information about gender (sex = 1) are evaluated in Eq. 14. The P(DCS) for the NM is 0.001 (0.1%). The ETR for the RM plus the information about age (43 yo) are evaluated in Eq. 15. The P(DCS) for the RM is also 0.001 (0.1%).

$$P(DCS) \text{ from NM} = \frac{exp(-25.56 + 12.83 * ETR - 1.037 * SEX)}{(1 + exp(-25.56 + 12.83 * ETR - 1.037 * SEX))}$$
Eq. 14
---
$$P(DCS) \text{ from RM} = \frac{\exp(-31.71 + 14.55 * ETR + 0.053 * AGE)}{(1 + \exp(-31.71 + 14.55 * ETR + 0.053 * AGE))} \tag{Eq. 15}$$

These estimates of DCS risk are similar, are much less than the risk without the exercise PB intervention, and are deemed acceptable in relation to the importance of the EVA from the CEV on the way to the moon.
---
# References

1. Adler HF. Dysbarism. Aeromed. Rev. 1-64. Brooks AFB, TX, U.S. Air Force School of Aerospace Medicine, 1964:56.

2. Andersen P, Saltin B. Maximal perfusion of skeletal muscle in man. J Physiol 1985; 366:233-49.

3. Balke B. Rate of gaseous nitrogen elimination during rest and work in relation to the occurrence of decompression sickness at high altitude. San Antonio, TX: USAF School of Aviation Medicine, 1954; Project #21-1201-0014, Report #6.

4. Behnke AR, Willmon TL. Gaseous nitrogen and helium elimination from the body during rest and exercise. Am J Physiol 1941; 131:619-26.

5. Billings, CE. Barometric Pressure (Chap. 1). In: Bioastronautics Data Book, ed. 2. Parker JF, West VR (eds). NASA SP-3006, U.S. Government Printing Office, Washington, D.C., p. 29, 1973.

6. Boothby WM, Luft UC, Benson OO Jr. Gaseous nitrogen elimination. Experiments when breathing oxygen at rest and at work with comments on dysbarism. Aviat Med 1952; 23:141-76.

7. Broome J, Dutka A, McNamee G. Exercise conditioning reduces the risk of neurologic decompression sickness in swine. Undersea Hyperbaric Med 1995; 22:73-85.

8. Butler BD, Vann RD, Nishi RY, et al. Human trials of a 2-hour prebreathe protocol for extravehicular activity. [Abstract # 44]. Aviat Space Environ Med 2000; 71:50.

9. Carturan D, Boussuges A, Burnet H, Fondaral J, Vanuxem P, Gardette B. Circulating venous bubbles in recreational diving: relationship with age, weight, maximum oxygen uptake, and body fat percentage. Int J Sports Med 1999; 20:410-14.

10. Carturan D, Boussuges A, Vanuxem P, Bar-Hen A, Burnet H, Gardette B. Ascent rate, age, maximal oxygen uptake, adiposity, and circulating venous bubbles after diving. J Appl Physiol 2002; 93:1349-56.

11. Conkin J, Powell MR. Lower body adynamia as a factor to reduce the risk of hypobaric decompression sickness. Aviat Space Environ Med 2001; 72:202-14.

12. Conkin J, Powell MR, Gernhardt ML. Age affects severity of venous gas emboli on decompression from 14.7 to 4.3 psia. Aviat Space Environ Med 2003; 74:1142-1150.

13. Conkin J. Gender and decompression sickness: a critical review and analysis. NASA Technical Publication NASA/TP-2004-213148, Johnson Space Center, Houston, TX, November 2004.
---
14. Cook SF. Part II. Role of exercise, temperature, drugs, and water balance in decompression sickness. In: Fulton JF, editor. Decompression sickness. Philadelphia: WB Saunders; 1951:223-35.

15. Dembert ML, Jekel JF, Mooley LW. Health risk factors for the development of decompression sickness among US Navy divers. Undersea Biomed Res 1984; 11:395-406.

16. Dervay JP, Powell MR, Butler B, Fife CE. The effect of exercise and rest duration on the generation of venous gas bubbles at altitude. Aviat Space Environ Med 2002; 73:22-7.

17. Dujic Z, Duplancic D, et al. Aerobic exercise before diving reduces venous gas bubble formation in humans. J Physiol 2004; 555:637-42.

18. Evans A, Walder DN. Significance of gas micronuclei in the aetiology of decompression sickness. Nature 1969; 222:251-52.

19. Finch CE, Hayflick, ed. The handbook of the biology of aging, New York: Van Nostrand Reinhold Co., 1977.

20. Gernhardt ML, Conkin J, et al. Design of a 2-hour prebreathe protocol for space walks from the international space station. [Abstract # 43]. Aviat Space Environ Med 2000; 71:49.

21. Gernhardt ML, Conkin J, et al. Design and testing of a 2-hour oxygen prebreathe protocol for space walks from the international space station. [Abstract # 11]. Undersea Hyperbaric Med 2000; 27(Suppl.):12.

22. Gernhardt ML, Dervay JP, Welch J, Conkin J, Acock K, Lee S, Moore A, Foster P. Implementation of an exercise prebreathe protocol for construction and maintance of the international space station- results to date. [Abstract # 145]. Aviat Space Environ Med 2003; 74:397.

23. Gerth, WA, Vann RD, Leatherman, NE, Feezor MD. Effects of microgravity on tissue perfusion and the efficacy of astronaut denitrogenation for EVA. Aviat Space Environ Med 1987; 58(Suppl.):A100-105.

24. Gerth WA, Gernhardt ML, Conkin J, et al. Statistical analysis of risk factors in the prebreathe reduction protocol. [Abstract # 45]. Aviat Space Environ Med 2000; 71:50.

25. Gray JS. Constitutional factors affecting susceptibility to decompression sickness. In: Fulton JF, ed. Decompression sickness, Philadelphia: WB Saunders, 1951:182 - 91.

26. Gray JS. The prevention of aeroembolism by denitrogenation procedures. Washington, DC: National Research Council, 1942; Report No. 123.

27. Hayward ATJ. Tribonucleation of bubbles. Brit J Appl Phys 1967; 18:641-44.
---
28. Heimbach RD, Sheffield PJ. Decompression sickness and pulmonary overpressure accidents. In: DeHart RL, ed. Fundamentals of aerospace medicine (2nd ed.), Baltimore: Williams and Wilkins, 1996: 138.

29. Hemmingsen EA. Nucleation of bubbles in vitro and in vivo. In: Brubakk AO, Hemmingsen BB, Sundnes G, editors. Supersaturation and bubble formation in fluid and organisms. Trondheim, Norway: Tapir Publishers; 1989: 43-68.

30. Henry FM. Effects of exercise and altitude on the growth and decay of aviator's bends. J Aviat Med 1956; 27:250-59.

31. Ikles KG. Production of gas bubbles in fluid by tribonucleation. J Appl Physiol 1970; 28:524-27.

32. Jankowski LW, Nishi RY, Eaton DJ, Griffin AP. Exercise during decompression reduces the amount of venous gas emboli. Undersea Hyperbaric Med 1997; 24:59-65.

33. Jankowski LW, Tikuisis P, Nishi RY. Exercise effects during diving and decompression on postdive venous gas emboli. Aviat Space Environ Med 2004; 75:489-95.

34. Jones HB. Gas exchange and blood-tissue perfusion factors in various body tissues. In: Fulton JF, ed. Decompression sickness, Philadelphia: WB Saunders, 1951:278 - 321.

35. Krutz RW Jr, Dixon GA. The effect of exercise on bubble formation and bends susceptibility at 9,100 m (30,000 ft; 4.3 psia). Aviat Space Environ Med 1987; 58(Suppl.):A97-9.

36. Lee V, St. Leger Dowse M, Edge C, Gunby A, Bryson P. Decompression sickness in women: a possible relationship with the menstrual cycle. Aviat Space Environ Med 2003; 74:1177-82.

37. Loftin KC, J Conkin, MR Powell. Modeling the effects of exercise during 100% oxygen prebreathe on the risk of hypobaric decompression sickness. Aviat Space Environ Med 1997; 68:199-204.

38. Marti B, Howald H. Long-term effects of physical training on aerobic capacity: controlled study of former elite athletes. J Appl Physiol 1990; 69:1451-59.

39. Miller KJ, Powell MR, Srinivasan RS. An algorithm for calculation of gas uptake and elimination with variable blood flow. [Abstract # 16]. Undersea Hyperbaric Med 2000; 27(Suppl.):14.

40. Pollock NW, Natoli MJ, Vann RD, Nishi RY, Sullivan PJ, Gernhardt ML, Conkin J, Acock KE. High altitude DCS risk is greater for low fit individuals completing oxygen prebreathe based on relative intensity exercise prescriptions. [Abstract # 50]. Aviat Space Environ Med 2004; 74:B11.

73
---
41. Powell MR, Loftin KC, Conkin J. An algorithm for the calculation of change of the longest half times under various metabolic work loads. [Abstract # 41]. Undersea Hyperbaric Med 1998; 25(Suppl):20.

42. Powell MR, Waligora JM, Kumar KV. Decompression gas phase formation in simulated null gravity. 25th International Conference on Environmental Systems. SAE Technical Paper Series, # 951590. San Diego: Ca, 1-8, 1995.

43. Powell ML. Exercise and physical fitness decrease gas phase formation during hypobaric decompression. [Abstract # 92]. Undersea Biomed Res 1991; 18(Suppl.):61.

44. Rowell LB. Human Cardiovascular Control. Oxford University Press, Inc., New York, pp.164, 1993.

45. Rudge FW. Relationship of menstrual history to altitude chamber decompression sickness. Aviat Space Environ Med 1990; 61:657-59.

46. Schirmer JU, Workman WT. Menstrual history in altitude chamber trainees. Aviat Space Environ Med 1992; 63:616-18.

47. Spencer MP. Decompression limits for compressed air determined by ultrasonically detected blood bubbles. J Appl Physiol 1976; 40:229-35.

48. Steinberg D, Colla P. LOGIT: a supplementary module for SYSTAT. Evanston, IL: SYSTAT Inc.; 1991.

49. Sulaiman ZM, Pilmanis AA, O'Connor RB. Relationship between age and susceptibility to altitude decompression sickness. Aviat Space Environ Med 1997; 68:695-98.

50. Van Liew HD. Evidence that breathing of oxygen inactivates precursors if decompression bubbles. [Abstract # 8]. Undersea Hyperbaric Med 1998; 25(Suppl.):11.

51. Vann RD, Gerth WA. Is the risk of DCS in microgravity less than on earth? [Abstract # 45]. Aviat Space Environ Med 1997; 68(Suppl.):A8.

52. Vann RD, Grimstad J, Nielsen CH. Evidence for gas nuclei in decompressed rats. Undersea Biomed Res 1980; 7:107-12.

53. Vann RD, Gerth WA, Leatherman NE. Exercise and decompression sickness. In: Vann RD, ed. The physiological basis of decompression. Proceedings of the 38th Undersea and Hyperbaric Medical Society Workshop. Durham, NC: Duke University Medical Center, 1989:119-137. UHMS Pub. # 75(Phys) 6/1/89.

54. Webb JT, Dixon GA, Wiegman JF. Potential for reduction of decompression sickness by prebreathing with 100% oxygen while exercising. San Diego, CA: SAE Technical Paper #891490, 19th ICES, 1989:4pp.
---
55. Webb JT, Fischer MD, Heaps CL, Pilmanis AA. Exercise-enhanced preoxygenation increases protection from decompression sickness. Aviat Space Environ Med 1996; 67:618-24.

56. Webb JT, Kannan N, Pilmanis AA. Gender not a factor for altitude decompression sickness risk. Aviat Space Environ Med 2003; 74:2-10.

57. Webb JT, Pilmanis AA, Fischer MD, Kannan N. Enhancement of preoxygenation for decompression sickness protection: effect of exercise duration. Aviat Space Environ Med 2002; 73:1161-6.

58. Webb JP, Ryder HW, Engel GL, Romano J, et al. The effect on susceptibility to decompression sickness of preflight oxygen inhalation at rest as compared to oxygen inhalation during strenuous exercise. Washington, DC: National Research Council, 1943; Report No. 134.

59. Whitaker DM, Blinks LR, Berg WE, Twitty VC, Harris M. Muscular activity and bubble formation in animals decompressed to simulated altitudes. J Gen Physiol 1945; 28:213-23.

60. Wilkinson L. SYSTAT (version 8.0): the system for statistics. Evanston, Il: SYSTAT Inc., 1998.

61. Wisloff U, Brubakk AO. Aerobic endurance training reduces bubble formation and increases survival in rats exposed to hyperbaric pressure. J Physiol 2001; 537:607-11.

62. Wisloff U, Richardson RS, Brubakk AO. NOS inhibition increases bubble formation and reduces survival in sedentary and not exercised rats. J Physiol 2003; 546:577-82.

63. Wisloff U, Richardson RS, Brubakk AO. Exercise and nitric oxide prevent bubble formation: a novel approach to the prevention of decompression sickness? J Physiol 2004; 555:825-29.

64. Zwingelberg KM, Knight MA, Biles JB. Decompression sickness in women divers. Undersea Biomed Res 1987; 14:311-17.
---
# Appendices

## Exercise Prebreathe Details for Phase I through V-3 and Exercise at 4.3 psia

| Appendix | page |
| -------- | ---- |

----

|                                                               |    |
| ------------------------------------------------------------- | -- |
| A: Maximum Aerobic Capacity Test using Dual-Cycle Egrometry   | 77 |
| B: Maximum Aerobic Capacity Test Protocol for Male and Female | 78 |
| C: Execution of 75% VO₂ pk Protocol                           | 79 |
| D: Time and Events for Phase I through IV                     | 80 |
| E: Phase I Exercise Details                                   | 81 |
| F: Phase I Exercise Profile                                   | 83 |
| G: Time and Events for Phase II                               | 85 |
| H: Time and Events for Phase III                              | 86 |
| I: Prebreathe Exercise Protocol for Phase IV                  | 87 |
| J: Phase II, III, IV, V-1 through V-3 Exercise Details        | 88 |
| K: Phase II, III, IV, V-1 through V-3 Exercise Profile        | 90 |
| L: Prebreathe Exercise Protocol for Phase V-1, V-2, and V-3   | 92 |
| M: Phase V-3 Exercise During Prebreathe Details               | 94 |

---
---
# Appendix A: Maximal Aerobic Capacity Test using Dual-Cycle Ergometry

The subject was instrumented for EKG, heart rate, and O2 consumption and seated on the leg ergometer. The subject began pedaling both the Monarch 818E leg ergometer and the Monarch 881 arm ergometer, with a low workload, at a cadence of 65 rpm to become familiar with maintaining equal cadence for both ergometers. Thereafter, the test began at workloads described in the tables below for males and females. The workloads on the ergometer were controlled manually. The workloads on both ergometers were increased at 2.5 mins into each exercise level. The subject was instructed to pedal as long as possible while still maintaining a cadence of 65 rpms on both ergometers. At two min of each stage, heart rate, and O2 consumption values were recorded. The mean O2 consumption for each exercise stage was determined to be the average of the values collected in the last min of each stage. The test was terminated when the subject reached volitional fatigue or could not maintain the required arm or leg cadence. VO2 pk and pk heart rates were accepted as the highest O2 consumption and heart rates over a 60 sec period, which typically occurred in the last stage of the maximal exercise sessions.

Oxygen consumption versus heart rate and O2 consumption versus workload of the maximal exercise tests were plotted using the values recorded at each stage. Examples of these are shown below. A linear regression was determined for each exercise graph, and the slope and y-intercept of the lines describing these relationships were used to determine the total workloads and predict the heart rates for each stage of the 75% submaximal exercise sessions. Of the total workload prescribed for submaximal exercise, 88% was performed by the legs and 12% was performed by the arms.
---
## Appendix B: Maximal Aerobic Capacity Test Protocol for Male and Female

### MALE

| Stage | Time<br/>(min.) | Leg Load<br/>(W) |   | Arm Load<br/>(W) |   | Total<br/>Workload<br/>(W) |
| ----- | --------------- | ---------------- | - | ---------------- | - | -------------------------- |
|       |                 | 65 rpm           |   | 65 rpm           |   |                            |
| 1     | 0-2.5           | 75               |   | 11.3             |   | 86.3                       |
| 2     | 2.5-5.0         | 125              |   | 18.7             |   | 143.7                      |
| 3     | 5.0-7.5         | 175              |   | 26.3             |   | 201.3                      |
| 4     | 7.5-10.0        | 225              |   | 33.7             |   | 258.7                      |
| 5     | 10.0-12.5       | 275              |   | 41.3             |   | 316.3                      |
| 6     | 12.5-15.0       | 325              |   | 48.7             |   | 373.7                      |
| 7     | 15.0-17.5       | 375              |   | 56.3             |   | 431.3                      |

### FEMALE

| Stage | Time<br/>(min.) | Leg Load<br/>(W) |   | Arm Load<br/>(W) |   | Total<br/>Workload<br/>(W) |
| ----- | --------------- | ---------------- | - | ---------------- | - | -------------------------- |
|       |                 | 65 rpm           |   | 65 rpm           |   |                            |
| 1     | 0-2.5           | 53               |   | 7.9              |   | 60.9                       |
| 2     | 2.5-5.0         | 88               |   | 13.1             |   | 101.1                      |
| 3     | 5.0-7.5         | 123              |   | 18.4             |   | 141.4                      |
| 4     | 7.5-10.0        | 158              |   | 23.6             |   | 181.6                      |
| 5     | 10.0-12.5       | 193              |   | 28.9             |   | 221.9                      |
| 6     | 12.5-15.0       | 228              |   | 34.1             |   | 262.1                      |
| 7     | 15.0-17.5       | 263              |   | 39.4             |   | 302.4                      |

|                                                                                                                                                                                                                                                                                                                                                                                                 |                                                                                                                                                                                                                                                                                                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Figure 1: Heart Rate vs. Oxygen Consumption**<br/>y = 0.025x - 1.709 r² = 0.929<br/><br/>A scatter plot showing the relationship between heart rate (x-axis, 75-200 bpm) and oxygen consumption (y-axis, 0.5-3.5 L/min). The data points form a positive linear relationship with a trend line. The VO₂ values increase from approximately 0.5 L/min at 75 bpm to about 3.3 L/min at 200 bpm. | **Figure 2: Workload vs. Oxygen Consumption**<br/>y = 0.008x + 0.946 r² = 0.856<br/><br/>A scatter plot showing the relationship between workload (x-axis, 0-200 W) and oxygen consumption (y-axis, 1.0-2.5 L/min). The data points form a positive linear relationship with a trend line. The VO₂ values increase from approximately 1.0 L/min at 0 W to about 2.5 L/min at 200 W. |

---
# Appendix C: Execution of 75% VO₂ pk Protocol

|                   |              |                      |             |
| ----------------- | ------------ | -------------------- | ----------- |
| event             | Δt<br/>(min) | total time<br/>(min) | % of VO₂ pk |
| ***               |              |                      |             |
| increment stage 1 | 1            | 1                    | 37.5%       |
| increment stage 2 | 1            | 2                    | 50.0%       |
| increment stage 3 | 1            | 3                    | 62.5%       |
| exercise stage    | 7            | 10                   | 75.0%       |
| ***               |              |                      |             |

## Research Protocol:
Both arm and leg ergometry was done, so the total workload expressed as watts at 75% of VO₂ pk from a linear regression had to be partitioned into arm watts and leg watts. We used 88% of prescribed watts for the legs and 12% of prescribed watts for the arms for the three 1-min warm up stages and the 7-min exercise stage.

## Operational Protocol:
Leg ergometry was performed and surgical tubing was used in place of an arm ergometer. We used 88% of the prescribed watts for the legs and the balance of 12% of the total workload was attributed to upper body work with the surgical tubing for the arms for the three 1-min warm up stages and the 7-min exercise stage.
---
## Appendix D: Time and Events for Phase I through IV

| Phase                                                                                  | I    | II   | III  | IV         |
| -------------------------------------------------------------------------------------- | ---- | ---- | ---- | ---------- |
| Number of Subjects                                                                     | 47   | 45   | 9    | 56         |
| ***                                                                                    |      |      |      |            |
| start adynamia in recumbent subjects                                                   | -100 | -100 | -100 | -100 (min) |
| start prebreathe and dual-cycle ergo. in Phase I and II                                | 0    | 0    | 0    | 0          |
| start 56 min of EVA prep. Exercise                                                     | --   | --   | --   | 4          |
| end dual-cycle ergometry                                                               | 10   | 10   | --   | --         |
| start chamber depress from 14.7 psi to 9.6 psia in 20 min, then to 10.2 psi in 10 min  | 50   | 50   | 50   | 50         |
| start 24 min of EVA prep. exercise                                                     | --   | 55   | 55   | --         |
| switch from 100% O₂ to 26.5% O₂                                                        | 80   | 80   | 80   | 80         |
| stop EVA prep. exercise                                                                | 95   | 95   | 95   | 95         |
| switch from 26.5% O₂ to 100% O₂ and repress chamber from 10.2 psi to 14.7 psi in 5 min | 110  | 110  | 110  | 110        |
| continue resting prebreathe                                                            | 115  | 115  | 115  | 115        |
| start chamber depress from 14.7 psi to 4.3 psi in 30 min                               | 150  | 150  | 150  | 150        |
| start 240 min of simulated EVA exercise                                                | 180  | 180  | 180  | 180        |
| end test                                                                               | 420  | 420  | 420  | 420        |

---
# Appendix E: Phase I Exercise Details

## Pull Station (PS)
pull with both arms to: pounds of pull = 0.25 * body weight (lbs) + 25
hold 10 seconds and rest for 5 seconds
repeat contraction -- 16 cycles

## Torque Station (TSLH)
pull and hold with left hand for 5 seconds at 25 ft-pounds at the next 5 second cadence
push and hold with the left for 5 seconds at 25 ft-pounds at the next 5 second cadence
do for two mins on one stud then shift to another
repeat contractions -- 20 - 24 cycles depending on how much time it takes to move torque wrench from one stud to the next

## Torque Station (TSRH)
pull and hold with the right hand for 5 seconds at 25 ft-pounds at the next 5 second cadence
push and hold with the right hand for 5 seconds at 25 ft-pounds at the next 5 second cadence
do for two mins on one stud then shift to another
repeat contractions -- 20 - 24 cycles depending on how much time it takes to move torque wrench from one stud to the next

## Arm Station (AS1)
make 5 sit-ups in a 5 second against the resistance of the bungee while holding torque fixture with both hands
5 contractions of the right arm in 5 seconds against the bungee
5 contractions of the left arm in 5 seconds against the bungee
rest 5 seconds
repeat contractions -- 12 cycles

## Arm Station (AS2)
make 4 sit-ups in a 5 second against the resistance of the bungee while holding torque fixture with both hands
rest 5 seconds
4 contractions of the right arm in 5 seconds against the bungee
4 contractions of the left arm in 5 seconds against the bungee
rest 5 seconds
repeat contractions -- 12 cycles

## Hand Station (HS)
two min with right hand and two min with left
one right hand contraction and hold for the 5 second interval
rest 10 seconds
---
repeat right hand contraction for two mins -- 8 cycles with right hand
one left hand contraction and hold for the 5 second interval
rest 10 seconds
repeat left hand contraction for two mins -- 8 cycles with left hand

## Rest Station (VGE)
four min duration to relax hands, VGE monitoring, and symptom report

72
---
# Appendix F: Phase I Exercise Profile

| START TIME | SUB1 | SUB2 | DOP TECH |
| ---------- | ---- | ---- | -------- |
| 0          | AS1  | AS1  | REST     |
| 4          | AS1  | AS1  | REST     |
| 8          | VGE  | HS   | DOP1     |
| 12         | PS   | VGE  | DOP2     |
| 16         | TSRH | PS   | DOPDT    |
| 20         | AS2  | TSRH | REST     |
| 24         | VGE  | AS2  | DOP1     |
| 28         | PS   | VGE  | DOP2     |
| 32         | TSLH | PS   | DOPDT    |
| 36         | HS   | TSLH | REST     |
| 40         | VGE  | HS   | DOP1     |
| 44         | PS   | VGE  | DOP2     |
| 48         | TSRH | PS   | DOPDT    |
| 52         | AS2  | TSRH | REST     |
| 56         | VGE  | AS2  | DOP1     |
| 60         | REST | REST | REST     |
| 64         | PS   | VGE  | DOP2     |
| 68         | TSLH | PS   | DOPDT    |
| 72         | HS   | TSLH | REST     |
| 76         | VGE  | HS   | DOP1     |
| 80         | PS   | VGE  | DOP2     |
| 84         | TSRH | PS   | DOPDT    |
| 88         | AS2  | TSRH | REST     |
| 92         | VGE  | AS2  | DOP1     |
| 96         | PS   | VGE  | DOP2     |
| 100        | TSLH | PS   | DOPDT    |
| 104        | HS   | TSLH | REST     |
| 108        | VGE  | HS   | DOP1     |
| 112        | PS   | VGE  | DOP2     |
| 116        | TSRH | PS   | DOPDT    |
| 120        | REST | REST | REST     |
| 124        | AS2  | TSRH | REST     |
| 128        | VGE  | AS2  | DOP1     |
| 132        | PS   | VGE  | DOP2     |
| 136        | TSLH | PS   | DOPDT    |
| 140        | HS   | TSLH | REST     |
| 144        | VGE  | HS   | DOP1     |
| 148        | PS   | VGE  | DOP2     |
| 152        | TSRH | PS   | DOPDT    |
| 156        | AS2  | TSRH | REST     |

---
|     |      |      |       |
| --- | ---- | ---- | ----- |
| 160 | VGE  | AS2  | DOP1  |
| 164 | PS   | VGE  | DOP2  |
| 168 | TSLH | PS   | DOPDT |
| 172 | HS   | TSLH | REST  |
| 176 | VGE  | HS   | DOP1  |
| 180 | REST | REST | REST  |
| 184 | PS   | VGE  | DOP2  |
| 188 | TSRH | PS   | DOPDT |
| 192 | AS2  | TSRH | REST  |
| 196 | VGE  | AS2  | DOP1  |
| 200 | PS   | VGE  | DOP2  |
| 204 | TSLH | PS   | DOPDT |
| 208 | HS   | TSLH | REST  |
| 212 | VGE  | HS   | DOP1  |
| 216 | PS   | VGE  | DOP2  |
| 220 | TSRH | PS   | DOPDT |
| 224 | AS2  | TSRH | REST  |
| 228 | VGE  | AS2  | DOP1  |
| 232 | PS   | VGE  | DOP2  |
| 236 | TSLH | PS   | DOPDT |
| 240 | END  | END  | END   |

---
## Appendix G: Time and Events for Phase II

### Elapsed Time from start of dual cycle ergometry on 100% O₂

|                                                                                                           |                                                                                                                                                                                                                                                                                                 |
| --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| -120                                                                                                      | 1. Start Doppler Technician (DT) prebreathe at 7:30 a.m. for the 4.5 hr prebreathe option.                                                                                                                                                                                                      |
| -100                                                                                                      | 2. Start period of adynamia at 7:50 a.m. Subjects are recumbent and breathe air for 100 mins prior to start of dual cycle exercise.                                                                                                                                                             |
| --------------------------------------------------------------------------------------------------------- |                                                                                                                                                                                                                                                                                                 |
| 0                                                                                                         | 3. Start dual cycle exercise at 9:30 a.m. with all subjects on 100% O₂, two at Hermann and three at Duke.                                                                                                                                                                                       |
| 50                                                                                                        | 4. At 10:20 a.m. the dual cycle exercise is over. Depress the chamber from site pressure to 9.6 psia in 20 mins and maintain the subjects and DT on 100% O₂ for an additional 10 mins as you repress to 10.2 psia.                                                                              |
| 55                                                                                                        | 5. Start warm-up for EVA Prep activity. Do TSRH.                                                                                                                                                                                                                                                |
| 59                                                                                                        | 6. Continue warm-up for EVA Prep activity. Do TSLH.                                                                                                                                                                                                                                             |
| 63                                                                                                        | 7. Rest in preparation for AS2 activity.                                                                                                                                                                                                                                                        |
| 67                                                                                                        | 8. Do AS2 activity.                                                                                                                                                                                                                                                                             |
| 71                                                                                                        | 9. Rest in preparation for AS2 activity.                                                                                                                                                                                                                                                        |
| 75                                                                                                        | 10. Do AS2 activity.                                                                                                                                                                                                                                                                            |
| 79                                                                                                        | 11. Rest in preparation for AS2 activity.                                                                                                                                                                                                                                                       |
| 80                                                                                                        | 12. At 10:50 a.m. switch to bottled gas supply and breathe the 26.5% O₂ - 73.5% N₂ mixture for 30 mins. DT stays on 100% O₂. Continue EVA Prep exercises for 12 more mins.                                                                                                                      |
| 83                                                                                                        | 13. Do AS2 activity.                                                                                                                                                                                                                                                                            |
| 87                                                                                                        | 14. Rest in preparation for AS2 activity.                                                                                                                                                                                                                                                       |
| 91                                                                                                        | 15. Do AS2 activity.                                                                                                                                                                                                                                                                            |
| 95                                                                                                        | 16. At 11:05 a.m., discontinue EVA Prep activities.                                                                                                                                                                                                                                             |
| 110                                                                                                       | 17. At 11:20 a.m. switch from mixed gas supply to 100% O₂, then repress the chamber to 14.7 psia (site pressure) in 5 mins.                                                                                                                                                                     |
| 115                                                                                                       | 18. At 11:25 a.m. continue a 35 min prebreathe on 100% O₂ at site pressure.                                                                                                                                                                                                                     |
| 150                                                                                                       | 19. At 12:00 a.m. the subjects have completed 250 mins of adynamia prior to depress to 4.3 psia, 120 mins of 100% O₂ prebreathing, and 30 mins of breathing 26.5% O₂. The DT has completed 4.5 hrs of uninterrupted 100% O₂ prebreathing. At 12:00 a.m. depress chamber to 4.3 psia in 30 mins. |
| 180                                                                                                       | 20. At 12:30 a.m. begin four hrs of exercise that simulates EVA activity and monitor for VGE and DCS signs and symptoms. It is a nine hr day for the DT and a 8.7 hr day for the subjects.                                                                                                      |

---
# Appendix H: Time and Events for Phase III

Elapsed Time from start of prebreathe on 100% O₂

| Time | Event |
|------|-------|
| -120 | 1. Start Doppler Technician (DT) prebreathe at 7:30 a.m. for the 4.5 hr prebreathe option. |
| -100 | 2. Start period of adynamia at 7:50 a.m. Subjects are recumbent and breathe air for 100 mins prior to start of prebreathe. |
| --- | --------------------------------------------------------------------------------------------------------- |
| 0 | 3. Start prebreathe at 9:30 a.m. with all subjects on 100% O₂, two at Hermann and three at Duke. |
| 50 | 4. At 10:20 a.m. start the depress the chamber from site pressure to 9.6 psia in 20 mins and maintain the subjects and DT on 100% O₂ for an additional 10 mins as you repress to 10.2 psia. |
| 55 | 5. Start warm-up for EVA Prep activity. Do TSRH. |
| 59 | 6. Continue warm-up for EVA Prep activity. Do TSLH. |
| 63 | 7. Rest in preparation for AS2 activity. |
| 67 | 8. Do AS2 activity. |
| 71 | 9. Rest in preparation for AS2 activity. |
| 75 | 10. Do AS2 activity. |
| 79 | 11. Rest in preparation for AS2 activity. |
| 80 | 12. At 10:50 a.m. switch to bottled gas supply and breathe the 26.5% O₂ - 73.5% N₂ mixture for 30 mins. DT stays on 100% O₂. Continue EVA Prep exercises for 12 more mins. |
| 83 | 13. Do AS2 activity. |
| 87 | 14. Rest in preparation for AS2 activity. |
| 91 | 15. Do AS2 activity. |
| 95 | 16. At 11:05 a.m., discontinue EVA Prep activities. |
| 110 | 17. At 11:20 a.m. switch from mixed gas supply to 100% O₂, then repress the chamber to 14.7 psia (site pressure) in 5 mins. |
| 115 | 18. At 11:25 a.m. continue a 35 min prebreathe on 100% O₂ at site pressure. |
| 150 | 19. At 12:00 a.m. the subjects have completed 250 mins of adynamia prior to depress to 4.3 psia, 120 mins of 100% O₂ prebreathing, and 30 mins of breathing 26.5% O₂. The DT has completed 4.5 hrs of uninterrupted 100% O₂ prebreathing. At 12:00 a.m. depress chamber to 4.3 psia in 30 mins. |
| 180 | 20. At 12:30 a.m. begin four hrs of exercise that simulates EVA activity and monitor for VGE and DCS signs and symptoms. It is a nine hr day for the DT and a 8.7 hr day for the subjects. |

---
# Appendix I: Prebreathe Exercise Protocol for Phase IV

| Elapsed time (min) | event                                               |
| ------------------ | --------------------------------------------------- |
| 0                  | rest                                                |
| 4                  | do TSRH                                             |
| 8                  | do TSLH                                             |
| 12                 | do AS2                                              |
| 16                 | rest                                                |
| 20                 | do TSRH                                             |
| 24                 | do TSLH                                             |
| 28                 | do AS2                                              |
| 32                 | rest                                                |
| 36                 | do AS2                                              |
| 40                 | rest                                                |
| 44                 | do AS2                                              |
| 48                 | rest (7 min of rest as depress to 9.6 psia is done) |
| 55                 | do TSRH                                             |
| 59                 | do TSLH                                             |
| 63                 | rest                                                |
| 67                 | do AS2                                              |
| 71                 | rest                                                |
| 75                 | do AS2                                              |
| 79                 | rest                                                |
| 83                 | do AS2                                              |
| 87                 | rest                                                |
| 91                 | do AS2                                              |
| 95                 | stop activity                                       |

---
# Appendix J: Phase II, III, IV, V-1 through V-3 Exercise Details

## Pull Station / Arm Station (PS/AS2)
pull with both arms to: pounds of pull = 0.25 * body weight (lbs) + 25
hold 30 seconds and rest for 30 seconds
make 4 sit-ups in a 5 second against the resistance of the bungee while holding torque fixture with both hands
rest 5 seconds
4 contractions of the right arm in 5 seconds against the bungee
4 contractions of the left arm in 5 seconds against the bungee
rest 5 seconds
repeat contractions -- 9 cycles

## Torque Station (TSLH)
pull and hold with left hand for 5 seconds at 25 ft-pounds at the next 5 second cadence
push and hold with the left for 5 seconds at 25 ft-pounds at the next 5 second cadence
do for two mins on one stud then shift to another
repeat contractions -- 20 - 24 cycles depending on how much time it takes to move torque wrench from one stud to the next

## Torque Station (TSRH)
pull and hold with the right hand for 5 seconds at 25 ft-pounds at the next 5 second cadence
push and hold with the right hand for 5 seconds at 25 ft-pounds at the next 5 second cadence
do for two mins on one stud then shift to another
repeat contractions -- 20 - 24 cycles depending on how much time it takes to move torque wrench from one stud to the next

## Arm Station (AS1)
make 5 sit-ups in a 5 second against the resistance of the bungee while holding torque fixture with both hands
5 contractions of the right arm in 5 seconds against the bungee
5 contractions of the left arm in 5 seconds against the bungee
rest 5 seconds
repeat contractions -- 12 cycles

## Arm Station (AS2)
make 4 sit-ups in a 5 second against the resistance of the bungee while holding torque fixture with both hands
rest 5 seconds
4 contractions of the right arm in 5 seconds against the bungee
4 contractions of the left arm in 5 seconds against the bungee
rest 5 seconds
repeat contractions -- 12 cycles
---
## Hand Station (HS)
two min with right hand and two min with left
one right hand contraction and hold for the 5 second interval
rest 10 seconds
repeat right hand contraction for two mins -- 8 cycles with right hand
one left hand contraction and hold for the 5 second interval
rest 10 seconds
repeat left hand contraction for two mins -- 8 cycles with left hand

## Rest Station (VGE)
four min duration to relax hands, VGE monitoring, and symptom report
---
# Appendix K: Phase II, III, IV, V-1 through V-3 Exercise Profile

| START TIME | SUB1   | SUB2   | DOP TECH |
| ---------- | ------ | ------ | -------- |
| 0          | AS1    | AS1    | REST     |
| 4          | AS1    | AS1    | REST     |
| 8          | VGE    | HS     | DOP1     |
| 12         | HS     | VGE    | DOP2     |
| 16         | TSRH   | HS     | DOPDT    |
| 20         | PS/AS2 | TSRH   | REST     |
| 24         | VGE    | PS/AS2 | DOP1     |
| 28         | PS/AS2 | VGE    | DOP2     |
| 32         | TSLH   | PS/AS2 | DOPDT    |
| 36         | HS     | TSLH   | REST     |
| 40         | VGE    | HS     | DOP1     |
| 44         | PS/AS2 | VGE    | DOP2     |
| 48         | TSRH   | PS/AS2 | DOPDT    |
| 52         | PS/AS2 | TSRH   | REST     |
| 56         | VGE    | PS/AS2 | DOP1     |
| 60         | REST   | REST   | REST     |
| 64         | PS/AS2 | VGE    | DOP2     |
| 68         | TSLH   | PS/AS2 | DOPDT    |
| 72         | HS     | TSLH   | REST     |
| 76         | VGE    | HS     | DOP1     |
| 80         | PS/AS2 | VGE    | DOP2     |
| 84         | TSRH   | PS/AS2 | DOPDT    |
| 88         | PS/AS2 | TSRH   | REST     |
| 92         | VGE    | PS/AS2 | DOP1     |
| 96         | PS/AS2 | VGE    | DOP2     |
| 100        | TSLH   | PS/AS2 | DOPDT    |
| 104        | HS     | TSLH   | REST     |
| 108        | VGE    | HS     | DOP1     |
| 112        | PS/AS2 | VGE    | DOP2     |
| 116        | TSRH   | PS/AS2 | DOPDT    |
| 120        | REST   | REST   | REST     |
| 124        | PS/AS2 | TSRH   | REST     |
| 128        | VGE    | PS/AS2 | DOP1     |
| 132        | PS/AS2 | VGE    | DOP2     |
| 136        | TSLH   | PS/AS2 | DOPDT    |
| 140        | HS     | TSLH   | REST     |
| 144        | VGE    | HS     | DOP1     |
| 148        | PS/AS2 | VGE    | DOP2     |
| 152        | TSRH   | PS/AS2 | DOPDT    |
| 156        | PS/AS2 | TSRH   | REST     |

---
|     |        |        |       |
| --- | ------ | ------ | ----- |
| 160 | VGE    | PS/AS2 | DOP1  |
| 164 | PS/AS2 | VGE    | DOP2  |
| 168 | TSLH   | PS/AS2 | DOPDT |
| 172 | HS     | TSLH   | REST  |
| 176 | VGE    | HS     | DOP1  |
| 180 | REST   | REST   | REST  |
| 184 | PS/AS2 | VGE    | DOP2  |
| 188 | TSRH   | PS/AS2 | DOPDT |
| 192 | PS/AS2 | TSRH   | REST  |
| 196 | VGE    | PS/AS2 | DOP1  |
| 200 | PS/AS2 | VGE    | DOP2  |
| 204 | TSLH   | PS/AS2 | DOPDT |
| 208 | HS     | TSLH   | REST  |
| 212 | VGE    | HS     | DOP1  |
| 216 | PS/AS2 | VGE    | DOP2  |
| 220 | TSRH   | PS/AS2 | DOPDT |
| 224 | PS/AS2 | TSRH   | REST  |
| 228 | VGE    | PS/AS2 | DOP1  |
| 232 | PS/AS2 | VGE    | DOP2  |
| 236 | TSLH   | PS/AS2 | DOPDT |
| 240 | END    | END    | END   |

---
# Appendix L: Prebreathe Exercise Protocol for PhaseV-1, V-2, and V-3

## V-1:
Two min exercise with two min rest in a 90 min total prebreathe, with arms and legs moving for the two min. Note: middle of exercise has a 6 min period of rest. 160 min adynamia before start of prebreathe, with adynamia maintained during the 90 min prebreathe, 30 min ascent and 240 min during the exposure to 4.3 psia

2 min rest at start of PB
2 min at 40% VO2 pk
2 min rest
2 min at 50% VO2 pk
2 min rest
2 min at 60% VO2 pk
2 min rest
2 min at 60% VO2 pk
2 min rest
2 min at 60% VO2 pk
6 min rest
2 min at 60% VO2 pk
2 min rest
2 min at 60% VO2 pk
2 min rest
2 min at 60% VO2 pk
2 min rest
2 min at 60% VO2 pk
2 min rest
2 min at 50% VO2 pk
46 min rest
30 min ascent
240 min at 4.3 psia

## V-2:
Three min exercise with two min rest in a 90 min total prebreathe. After two min of upper and lower body exercise, the arms are stopped, but the legs continue for the third min. Note: my records show we did not start Protocol 2 with the initial two min rest. Note: middle of exercise has a 4 min rest. 160 min adynamia before start of prebreathe, with adynamia maintained during the 90 min prebreathe, 30 min ascent and 240 min during the exposure to 4.3 psia

2 min at 50% VO2 pk
2 min rest
3 min at 60% VO2 pk
2 min rest
3 min at 60% VO2 pk
2 min rest
3 min at 60% VO2 pk
4 min rest
---
```
3 min at 60% VO2 pk
2 min rest
3 min at 60% VO2 pk
2 min rest
3 min at 60% VO2 pk
46 min rest
30 min ascent
240 min at 4.3 psia

V-3: three min exercise with two min rest plus 24 min of light exercise in a 120 min total prebreathe. After two min of upper and lower body exercise, the arms are stopped, but the legs continue for the third min. Note: we do start Protocol 3 with the initial two min rest. Note: middle of exercise has a 4 min rest.
160 min adynamia before start of prebreathe, with adynamia maintained during the 120 min prebreathe, 30 min ascent and 240 min during the exposure to 4.3 psia

2 min rest
2 min at 50% VO2 pk
2 min rest
3 min at 60% VO2 pk
2 min rest
3 min at 60% VO2 pk
2 min rest
3 min at 60% VO2 pk
4 min rest
3 min at 60% VO2 pk
2 min rest
3 min at 60% VO2 pk
2 min rest
3 min at 60% VO2 pk
14 min transfer from ergometer to exercise cot
4 min TSRH exercise
4 min TSLH exercise
4 min rest
4 min AS2 exercise
4 min rest
4 min AS2 exercise
4 min rest
4 min AS2 exercise
4 min rest
4 min AS2 exercise
30 min rest
30 min ascent
240 min at 4.3 psia
```
---
# Appendix M: Phase V-3 Exercise During Prebreathe Details

## Torque Station (TSLH)
pull and hold with left hand for 5 seconds at 25 ft-pounds at the next 5 second cadence
push and hold with the left for 5 seconds at 25 ft-pounds at the next 5 second cadence
do for two mins on one stud then shift to another
repeat contractions -- 20 - 24 cycles depending on how much time it takes to move torque
wrench from one stud to the next

## Torque Station (TSRH)
pull and hold with the right hand for 5 seconds at 25 ft-pounds at the next 5 second
cadence
push and hold with the right hand for 5 seconds at 25 ft-pounds at the next 5 second
cadence
do for two mins on one stud then shift to another
repeat contractions -- 20 - 24 cycles depending on how much time it takes to move torque
wrench from one stud to the next

## Arm Station (AS2)
make 4 sit-ups in a 5 second against the resistance of the bungee while holding torque
fixture with both hands
rest 5 seconds
4 contractions of the right arm in 5 seconds against the bungee
4 contractions of the left arm in 5 seconds against the bungee
rest 5 seconds
repeat contractions -- 12 cycles