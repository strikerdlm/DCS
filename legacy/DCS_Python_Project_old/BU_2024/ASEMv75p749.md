## Page 1

```markdown
# RESEARCH ARTICLE

# Decompression Sickness Risk Model: Development and Validation by 150 Prospective Hypobaric Exposures

**Andrew A. Pilmanis, Lambros J. Petropoulos, Nandini Kannan, and James T. Webb**

---

**Pilmanis AA, Petropoulos LJ, Kannan N, Webb JT. Decompression sickness risk model: development and validation by 150 prospective hypobaric exposures. Aviat Space Environ Med 2004; 75:749–59.**

## Introduction
High altitude exposure has an inherent risk of altitude decompression sickness (DCS). A predictive DCS model was needed to reduce operational risk. To be operationally acceptable, such a theoretical model would need to be validated in the laboratory using human subjects.

## Methods
The Air Force Research Laboratory (AFRL) has conducted numerous studies on human subjects exposed to simulated altitudes in hypobaric chambers. The database from those studies was used to develop a statistical altitude DCS model. In addition, a bubble growth model was developed using a finite difference method to solve for bubble radius as a function of time. The bubble growth model, integrated with the statistical model, constitutes the AFRL DCS Risk Assessment Model. Validation of the model was accomplished by comparing computer predictions of DCS risk with results from subsequent prospective human subject exposures. There were five exposure profiles, not previously found in the database, covering a wide range of altitudes (18,000–35,000 ft), exposure time (180–360 min), prebreathing time (0–90 min), and activity level (rest-strenuous) that were tested. The subjects were monitored for DCS symptoms and development of emboli.

## Results
There were 30 subjects who were exposed to each of the 5 altitude profiles. The DCS incidence onsets predicted by the model were not significantly different from the experimental values for all scenarios tested and were generally within ± 5% of the actual values.

## Conclusion
A statistical altitude DCS model was successfully developed and validated.

**Keywords:** bubble growth, model, altitude, DCS, emboli, decompression sickness, hypobaric, decompression, prebreath, preoxygenation, venous gas emboli.

---

## Introduction

Decompression sickness (DCS) is caused by dissolved gas bubbles which form when living tissues are subjected to large reductions in environmental pressure. Such reductions in pressure can occur during decompression from compressed gas diving or pressurized tunnel work, ascent in the atmosphere, decompression during preparation for extravehicular activity in space, or decompression during training or research in hyperbaric or hypobaric chambers. Before decompression, nitrogen is dissolved in the tissues and fluids at a concentration related to the level of nitrogen in the breathing mixture prior to decompression. Thus, the tissues and fluids are saturated with nitrogen.

Nitrogen supersaturation occurs in the body during decompression as the environmental pressure is reduced more rapidly than the tissue pressure of nitrogen. When the magnitude and rate of environmental pressure reduction are sufficient, the supersaturation with nitrogen can lead to the transition of nitrogen from the dissolved phase into the gas phase as gas emboli. The various clinical symptoms of altitude DCS are thought to result mainly from the physical interactions of gas bubbles with tissues and fluids. The size and location of these bubbles are thought to have a significant effect on the resulting DCS symptoms. The gas bubbles may interact with nerve endings or block microcirculation. The resulting symptoms include pain, sensory deprivation, skin manifestations, and respiratory distress. The risk of DCS increases with extended exposure times, very high altitudes (45), and greater physical activity during the exposure (29). The risk decreases with preoxygenation (45).

Formal reports of DCS from the field are rare. Research indicates that the incidence of DCS during simulated altitudes is actually quite high, but reports are suppressed for fear of being grounded (3), and accurate evaluation of DCS incidence is significantly hindered by inconsistent classification of symptoms (14). When coupled with the extensive data from altitude chamber studies showing high rates of DCS incidence for simulated operational flight profiles, these findings indicate that DCS may continue to be an operational problem. With proper procedures (e.g., preoxygenation, suit/cabin pressurization, etc.), the risk of DCS can be significantly reduced. Countermeasures for preventing DCS are thus not the problem. Rather, the problem facing aircrews is how to quantify the risk of DCS and then select an appropriate combination of available
```


## Page 2

```markdown
# ALTITUDE DCS MODEL VALIDATION—PILMANIS ET AL.

Countermeasures compatible with the constraints of a given mission.

Protection from DCS depends on reducing the potential for nitrogen supersaturation and limiting the factors associated with bubble formation and growth. Adequate cabin pressurization will prevent DCS if unexpected loss of pressurization is followed quickly by a timely descent to below 10,000 ft, where the ambient pressure is sufficient to greatly reduce formation and growth of gas emboli. If the degree of planned pressure reduction cannot be avoided, the risk of DCS can be minimized or prevented with sufficient denitrogenation by prebreathing pure oxygen (preoxygenation) before such exposures. The duration of preoxygenation is directly related to its effectiveness over the practical range of preoxygenation times; i.e., up to 4 h (43). To determine the need for preoxygenation, the risk of DCS must be assessed.

There are several methods of assessing DCS risk. The simplest is to find the answer in the literature. However, data on a specific exposure profile is not usually available. The next obvious approach is to conduct an altitude chamber study to determine the DCS risk for that specific profile. However, such studies are expensive and time consuming. Finally, people with considerable experience in the field may extrapolate from available data and make a "best guess." A "best guess" is more intuitive than scientific and not likely to produce an accurate risk assessment. 

The best approach is to develop and validate a model that accurately predicts the DCS risk for a wide range of exposure profiles. There are many applications for an altitude DCS risk assessment computer-based model: mission planning, systems design, education and research, real-time risk prediction in a cockpit, pressure suit control, and cabin pressurization control. The ability to predict DCS risk, real-time in a cockpit, as well as for mission planning, is an operational need for both military and civilian aerospace applications (26). The ability to predict the onset of DCS during a planned exposure scenario would allow modification of any primary factors which determine DCS risk (duration of preoxygenation, exposure altitude, duration of exposure, and level of activity while decompressed) and enable operators to plan a safer mission.

Early altitude DCS modeling efforts involved modification of existing diving decompression models, ignoring the fundamental differences that exist between altitude and diving exposures (27). The lists below illustrate the significant differences between altitude and diving decompression.

## Altitude

1. Decompression starts from a ground level tissue N₂ saturated state.
2. Breathing gas is usually high in O₂ to prevent hypoxia and promote denitrogenation.
3. The time of decompressed exposure to altitude is limited.
4. Pre-mission denitrogenation (preoxygenation) reduces DCS risk.
5. DCS usually occurs during the mission.
6. Symptoms are usually mild and limited to joint pain.
7. Recompression to ground level is therapeutic and universal.
8. Tissue PN₂ decreases with altitude exposure to very low levels.
9. Metabolic gases become progressively more important as altitude increases.
10. There are very few documented chronic sequelae.

## Diving

1. Upward excursions from saturation diving are rare.
2. Breathing gas mixtures are usually high in inert gas due to oxygen toxicity concerns.
3. The time at surface pressure following decompression is not limited.
4. The concept of preoxygenation is generally not applicable.
5. DCS risk is usually greatest after mission completion.
6. Neurological symptoms are common.
7. Therapeutic chamber recompression is time limited and sometimes hazardous.
8. Tissue PN₂ increases with hyperbaric exposure to very high levels.
9. Inert gases dominate.
10. Chronic bone necrosis and neurological damage have been documented.

These differences illustrate the limited applicability of diving models in assessing and predicting DCS risk for altitude exposures. In recent years, a few articles have appeared that have proposed models specifically for altitude DCS. However, a standardized approach is not available and none of these altitude models have been validated with actual experimental data from hypobaric exposures with the primary factors which determine DCS risk as variables. The purpose of this paper is to describe the evolution of an altitude DCS model developed at the Air Force Research Laboratory (AFRL), Brooks Air Force Base, TX, and to present the results of the validation of this model with human subject altitude exposures.

### Altitude DCS Model Development

Van Liew et al. (38) developed a probabilistic, dose-response model of altitude DCS that related several independent variables accounting for decompression stress to the probability of occurrence of symptoms. The mechanistic principles used in their model were based on the premise that the risk of DCS is related to the number of bubbles and the volume of gas that can be liberated from a unit volume of tissue. Several competing models were tested and evaluated on the basis of how well they fit the data on human exposures from several different sources. The three independent variables used in the analysis were duration of breathing 100% oxygen at ground level (preoxygenation), exposure pressure, and exposure duration. The major assumption the authors made is that DCS incidence can
```


## Page 3

```markdown
# ALTITUDE DCS MODEL VALIDATION—PILMANIS ET AL.

be predicted from the characteristics of bubbles. In their conclusions (38), the authors recognize that symptoms may be secondary to bubbles and suggest that their mechanism requires be scrutinized and investigated further. Gerth and Vann (8) developed an extensive model of bubble dynamics to provide an assessment of DCS. The equations considered in the paper describing bubble growth and resolution are similar to those in Van Liew et al. (38), being dose-response models with the percentage of symptomatic individuals as the response variable. The unknown parameters in the models were estimated using maximum likelihood methods. The authors acknowledge the need for inclusion of symptom onset times for better assessment of DCS risk. These models focused on mathematical relationships describing bubble growth during a defined decompression and are called approximate models because they make certain assumptions (approximations). These approximations used did not account for the influence of any initial conditions due to their assumption that a quasi-steady state, or equilibrium, exists in the tissue surrounding a bubble nucleus. They also rely on only one or two factors that affect DCS risk, assuming the others are not as critical.

In addition, the approaches outlined in these articles rely heavily on the premise that DCS incidence can be predicted from the characteristics of bubbles. The relationship between bubble formation and DCS is not well understood. It is well established that there is a positive correlation between the presence of bubbles and the occurrence of DCS symptoms. However, this does not imply causation, nor is prediction of symptoms possible from venous gas emboli (VGE) scores (2,22,28). Most of these models involve equations describing bubble growth based on certain physiological assumptions. It is extremely difficult, in fact virtually impossible, to verify these assumptions with real data. The only data on bubble characteristics is from Doppler ultrasound of VGE in the heart and not of the tissue 'bubbles' that presumably cause the vast majority of the symptoms. Most of these models also only use the percentage of symptomatic individuals and ignore the symptom onset time. Finally, information from the large majority of subjects, those who remain asymptomatic throughout the exposures, is not adequately incorporated into these previous models.

## Development of the Bubble Growth Model

Once the determining factors that effect DCS risk are defined, a critical step in assessing DCS risk is modeling the growth of a bubble in the extravascular tissues based on those factors (see Appendix A for model equations and definition of symbols). The numerical methods portion of the model and most of the mathematical formulations and assumptions were based on a paper by Arefmanesh et al. (1).

The diffusion equation is defined within a hypothetical tissue shell surrounding the bubble. This shell has a finite thickness. In situations where a large number of bubbles nucleate and grow simultaneously in close proximity, the amount of tissue immediately surrounding the bubble is finite as is the amount of dissolved gas. The use of a tissue shell enables us to account for different bubble population densities by varying the shell/bubble radius ratio.

The convection-diffusion equation (Eq.1) is slightly modified from the one used by Arefmanesh (1). Since blood leaving the capillaries removes nitrogen gas from the system, especially when the breathing mixture contains a low percentage of nitrogen, a sink term (33) is added to the right-hand side of the equation. This new addition accounts for tissue nitrogen loss due to capillary-tissue gas exchanges. The gas inside the bubble is assumed to be an ideal gas whose pressure is related to the gas concentration at the interface through Henry’s law. The initial gas concentration used by the model is the concentration value just prior to ascent. Altitude decompressions are considered decompressions from a saturated condition. A single tissue denitrogenation rate is used during preoxygenation. During bubble growth, the variable perfusion parameters account for the different exercise levels which, in turn, effect the perfusion rate.

Prior to decompression, the dissolved inert gas is assumed to be uniformly distributed throughout the tissue shell [C(r,t) = C∞]. The reduced internal pressure at altitude (Boyle’s law) causes bubble expansion and induces a concentration gradient in the tissue shell. Internal pressure is related to the concentration in the tissue at the interface through Henry’s law. Since there are other bubbles growing in close proximity, the amount of dissolved gas in the tissue available for each bubble is finite. The concentration gradient at the outer boundary of the tissue shell is assumed zero at all times (no flux through the outer boundary of the shell). Nevertheless, the amount of gas in the tissue and the bubble is not constant, due to the sink term in the diffusion equation, which accounts for the perfusion effect on bubble growth. Hence the boundary conditions for Eq. 1 are given in Eqs. 4 and 5.

In the past, a number of studies have described bubble growth in supersaturated liquids (e.g., decompression) and bubble dissolution in undersaturated liquids (e.g., breathing 100% oxygen after bubble formation during altitude exposure) (9,15,23,35,37-39). In all of the studies, it has been assumed that the growth rate of the concentration boundary layer thickness around a dissolving bubble is fast compared with the rate of gas-tissue interface movement. This assumption provided the basis for approximate solutions of bubble dissolution. Epstein and Plesset (7) and Hatalala and Van Liew (9) obtained approximate quasi-stationary solutions by neglecting convective transport and by solving the resulting diffusion equation for the case

---

Aviation, Space, and Environmental Medicine • Vol. 75, No. 9 • September 2004

751
```


## Page 4

```markdown
# ALTITUDE DCS MODEL VALIDATION—PILMANIS ET AL.

where the bubble surface is considered stationary. The mass flux at the interface determined from the solution of the standard diffusion equation was then used to establish the motion of the bubble surface. Further, it was assumed by Hlastala and Van Liew (9) that the interior of the bubble was uniform, inertial, and viscous, and surface tension effects were excluded. Under these assumptions, the equations of motion for the tissue phase allowed the internal bubble pressure, \(P_b\), to be set equal to the constant ambient pressure with negligible error. Consequently, the growth or dissolution of the bubble in those models was controlled strictly by the diffusion process in the tissue.

In more recent work (36,37) based on Van Liew and Hlastala (39), diffusion was assumed to quickly reach a steady state (in these models, concentration outside the bubble was governed by Laplace’s equation). This additional approximation could be referred to as a quasi-steady state approximation. In the quasi-steady state model the ratio of the difference between the pressure of nitrogen in the bubble and in the tissue divided by the pressure of nitrogen in the bubble (\((P_{bN_2} - P_{tN_2})/P_{bN_2}\)) defines the level of tissue supersaturation, and provides a measure of the driving force behind dissolution or growth. When the tissue nitrogen pressure is higher than the bubble gas partial pressure, this ratio is negative (the tissue is supersaturated) and the bubble grows. Conversely, if the partial pressure of nitrogen is higher in the bubble than in the tissue, the ratio is positive and the bubble shrinks. If the tissue is at the same pressure as the bubble, the ratio is zero.

More recently, Nukala (24) took a step beyond Van Liew’s efforts and used the steady state solutions of the diffusion equation with a discontinuity on the diffusion coefficient. He assumed two shells surrounding the bubble identifying the second one as a “massive layer of cells” with different diffusivity. His assumption that \(D1 = (0 - 3)D2\) is very similar to our no-flux outer boundary condition. However, instead of using approximate solutions as he did, we chose to solve the full system of equations, following Afremash’s (1) numerical methods (25).

## Development of the Statistical Model

For over two decades, AFRL has conducted human subject research in altitude chambers. The results of over 3,000 experiments, with both male and female subjects, have been deposited into the AFRL DCS Database. A number of articles have appeared that deal in detail with specific studies from the database (16,30,34,41,43,45,46). An examination of this database (40) reveals certain interesting characteristics of altitude DCS and offers some insight into an improved approach for statistical modeling of DCS:

- Not all individuals exposed to identical experimental conditions exhibit symptoms of DCS.
- The severity and breadth of symptoms for individuals who do experience DCS is extremely variable, ranging from mild knee pain to severe respiratory problems.
- The time of onset of symptoms varies significantly from individual to individual.
- An individual subject is sometimes required to perform identical exposures in successive weeks, resulting in the same reaction or something totally different, i.e., there is very little certainty about an individual response.

These observations reveal a stochastic nature of DCS, i.e., the onset of symptoms is not fixed, but a random variable. This necessitates the use of survival analysis/reliability techniques to adequately model the incidence of DCS (10).

In a series of papers, Kumar et al. (18–21) recognized that survival analysis techniques work well to model DCS risk. They developed logistic and loglinear models to predict DCS as a function of tissue ratio, a measure of tissue nitrogen pressure in relation to total ambient pressure. Maximum likelihood techniques were used to estimate the parameters of these models. They also examined the effects of other variables such as gender or operational exposures, the bubbles grow to a maximum radius and then lose their nitrogen to the ever-diminishing tissue shells if the person continues to breathe 100% oxygen. If diffusion rapidly approaches equilibrium, the concentration gradient would only vary with respect to the spatial coordinate. By definition, a steady-state model cannot show time-dependence in the concentration field or gradient. The initial sign of the concentration gradient will be maintained. The bubble will either grow or dissolve, but it cannot do both.

More recently, Kukral (24) took a step beyond Van Liew’s efforts and used the steady state solutions of the diffusion equation with a discontinuity on the diffusion coefficient. He assumed two shells surrounding the bubble identifying the second one as a “massive layer of cells” with different diffusivity. His assumption that \(D1 = (0 - 3)D2\) is very similar to our no-flux outer boundary condition. However, instead of using approximate solutions as he did, we chose to solve the full system of equations, following Afremash’s (1) numerical methods (25).

Experimental data from the database shows that the primary risk factors affecting DCS include altitude, preoxygenation duration, exposure duration, and level of exercise performed during the exposure. Several other factors including gender, height, and body mass were also examined, but the p-values for these risk factors were not significant. In other words, these factors do not add significantly to our ability to model DCS onset in the presence of the primary risk factors. In order to develop a comprehensive model that accurately describes altitude DCS, it is essential to include all of the primary factors. With this goal in mind, Kannan et al. (11,12) developed a model based on the logistic distribution incorporating several risk factors. We know from empirical evidence that the instantaneous risk of developing symptoms increases with increased exposure duration. However, because of deni-
```


## Page 5

```markdown
# ALTITUDE DCS MODEL VALIDATION—PILMANIS ET AL.

trogenation, the risk starts to drop after it reaches a maximum. This information on the shape of the risk function indicated that the lognormal and logistic distributions were appropriate for the data.

The model was fit to data from the database. The authors examined the data on preoxygenation times, pressure, and time of exposure. The data seemed to indicate that subjects with longer preoxygenation times were more likely to have longer exposure durations at higher altitudes. To adjust for this, they suggested the inclusion of a risk factor by taking the ratio of preoxygenation time to exposure time. The risk factors that were highly significant (p-value < 0.0001) were final pressure (altitude), ratio of preoxygenation to exposure time, and exercise level. The model also accounted for the large dispersion in exposure times by assigning weights to the observations. These weights were chosen to be inversely proportional to the variances of onset times. Maximum likelihood estimates of the unknown parameters were obtained using the LIFEREG procedure of the statistical package SAS (SAS Institute Inc, Cary, NC). The estimated cumulative distribution function was used to predict the probability of DCS for a variety of exposure profiles. Validation and cross-validation techniques were used to evaluate the predictions from the model. The predictions from this model agreed closely with empirical data from the database for a variety of different exposure profiles.

The database contained data from a wide range of altitudes. At higher altitudes, the effects of exercise were more pronounced than at lower altitudes. To address the interaction between exercise and altitude, stratified models were developed by Kannan et al. (12). These authors also addressed the possibility of DCS thresholds at both higher and lower altitudes. Webb et al. (42) described an abrupt increase in DCS symptoms with zero preoxygenation above 21,000 ft. To account for these thresholds, a stratified model was developed and the predictions improved dramatically over the previous logistic model.

The data contained in the Database include the time to onset of DCS symptoms, amount of time spent in preoxygenation, pressure/altitude, time at maximum altitude, and exercise code. During the experiments, subjects were monitored continuously for DCS and VGE. The experiment either lasted the entire exposure period or was terminated if the individual had DCS symptoms. For individuals reporting no symptoms, their onset time was replaced by their corresponding time at maximum altitude. A censoring variable was created to indicate the status of each individual: 1-DCS and 0-No DCS (censored). The altitude levels used in the analysis ranged from 11,500 ft (493 mmHg) to 35,000 ft (179 mmHg). The preoxygenation ranges ranged from 0 to 240 min.

The database protocols used to develop the model contained a variety of exercise types while at altitude. The exercise was not continuous. Periods of exercise were separated by periods of rest. These exercise types were divided into three categories by the mean level of oxygen consumption during the entire exposure as expressed by the percent of peak VO₂. The categories were rest, mild exercise, or heavy exercise. These three exercise categories were chosen with operational simplicity in mind for the projected model software. Rest was defined as a mean of about 5% of VO₂peak, mild exercise as a mean of 8–20% of VO₂peak, and heavy exercise as a mean of over 20% of VO₂peak. Detailed descriptions of the exercise types can be found in previous publications (17,41,44,45).

All exposures in this database used the same ascent rate and the same breathing gas mixture. For some protocols, the same individuals performed as many as five exposures of the same profiles. To avoid any possibility of data contamination, we decided to use only the results of the first exposures of these individuals. Even though this resulted in a smaller dataset, we felt that this would reduce the effects of susceptible or trained individuals. We also deleted data from runs where the breathing mixture was different from 100% O₂. With these deletions, the reduced dataset contained 1015 observations of which 522 (51%) were censored (non-symptomatic).

The earlier model developed by Kannan et al. (12) considered three risk factors: pressure, ratio of preoxygenation to exposure time, and exercise. Validation and cross-validation techniques were used to conclude that predictions from this model agreed closely with empirical data, for most exposure profiles. The model, however, did not seem adequate for all altitudes. At very high altitudes (> 30,000 ft), the effects of exercise and altitude were very pronounced. At 30,000 ft with mild exercise, almost 80% of subjects developed DCS. For the resting profile at 30,000 ft, 53% of subjects reported symptoms. This suggested either a strong interaction effect between altitude and exercise or some sort of threshold at 30,000 ft. It has been observed in the literature that there is a lower altitude threshold for DCS with zero preoxygenation (21,000 ft), below which very few cases of DCS occur (42). The risk of DCS increases sharply at altitudes above this threshold. Based on this, it seemed reasonable to assume such a threshold might exist at the higher altitudes. Kannan and Pilmanis (13) proposed a stratified or weighted model based on three strata. The first stratum consisted of altitude levels in the range between 22,500 ft (314 mmHg) and 25,000 ft (282 mmHg). The second stratum consisted of altitude levels in the range between 25,000 ft and 30,000 ft (226 mmHg). The final stratum consisted of altitudes at or above 30,000 ft. For each stratum, the exercise variable was defined appropriately and another risk factor measuring the interaction between pressure and exercise was added to the model. Table I provides the results of this analysis. We fitted the model to the data based on the logistic distribution using three risk factors: pressure in mmHg, preoxygenation time, and the interaction between exercise and pressure. The coefficients associated with the risk factors are estimated from the data using the LIFEREG procedure in SAS (parameter estimates), and approximately reflect the importance of
```


## Page 6

```markdown
# ALTITUDE DCS MODEL VALIDATION—PILMANIS ET AL.

## TABLE I. PARAMETER ESTIMATES FOR THE STRATIFIED LOGISTIC MODEL.

| Estimate | SE   | Chi-Squared | p-value |
|----------|------|-------------|---------|
| **Stratum 1: Altitudes below 7620 m (25,000 ft)** |      |             |         |
| Intercept | 25.93 | 51.39 | 0.25 | 0.6139 |
| Pressure  | -2.96 | 8.91  | 0.11 | 0.7396 |
| Preox     | 0.0009 | 0.006 | 1.88 | 0.1700 |
| Expres    | -0.29 | 0.89  | 9.62 | 0.0019 |
| Scale     | 0.074 | 0.10  |      |         |
| **Stratum 2: Altitudes above 7620 m (25,000 ft) and below 9,144 m (30,000 ft)** |      |             |         |
| Intercept | 3.97  | 4.62  | 0.88 | 0.3483 |
| Pressure  | 0.51  | 0.775 | 0.43 | 0.5105 |
| Preox     | 0.008 | 0.002 | 11.63 | 0.0007 |
| Expres    | -0.18 | 0.039 | 20.53 | 0.0001 |
| Scale     | 0.35  | 0.04  |      |         |
| **Stratum 3: Altitudes above and including 9,144 m (30,000 ft)** |      |             |         |
| Intercept | -6.529 | 2.531 | 6.66 | 0.0099 |
| Pressure  | 2.613 | 0.480 | 29.61 | 0.0001 |
| Preox     | 0.007 | 0.001 | 15.61 | 0.0001 |
| Expres    | -0.217 | 0.029 | 52.38 | 0.0001 |
| Scale     | 0.565 | 0.05  |      |         |

*Preox = preoxygenation; Expres = the interaction between exercise and pressure.*

The different risk factors are stratified, and chi-squared p-values are used to test the significance of the risk factors. For example, the p-value for the interaction between exercise and pressure in Table I is 0.0019, indicating that in Stratum 1, the interaction between altitude and exercise is significant, which is consistent with the belief that the incidence curve rises.

Since the scale parameter is less than one for all three strata, the risk function increases to a maximum and then decreases with increased exposure. For Stratum 1, the preoxygenation variable was not significant. This is not surprising since most profiles in this range had zero preoxygenation times. For Stratum 1, the interaction between exercise and pressure was the only significant risk factor. Pressure by itself was not significant. This was expected since the stratum contained lower altitudes. The intercept was large because at the lower altitudes, the baseline for DCS risk was fairly high (i.e., onset times are very large). This indicates that there is a substantial lag before symptoms occur. This is consistent with the belief that DCS is caused by increasing levels of nitrogen in the tissues relative to ambient, so at the lower altitudes, the supersaturation of tissues may take longer.

For Stratum 2, the interaction between pressure and exercise was again very significant. Preoxygenation time was also significant. For Stratum 3, all the risk factors are highly significant. The most significant is the interaction between exercise and altitude; even mild exercise at such altitudes presumably increases the formation of bubbles and results in very short onset times. This effect has also been observed in the paper by Webb et al. (45).

The results for all three strata indicate the relative importance of the three risk factors. The interaction between exercise and altitude clearly has the greatest effect on increasing the risk of DCS. The resulting logistic model is defined by Eq. 6, where the parameter λ is related to the risk factors through Eq. 7. The coefficients in Eq. 7 are estimated using SAS. Clearly, the parameter λ is always positive. At t = 0, the probability of DCS is 0, and the probability of DCS increases over time. The coefficients β0, β1, β2, and β3 are estimated using SAS and reflect the importance of the different risk factors. A large positive intercept β0 indicates a higher median DCS onset time (the time by which we expect 50% of the population to exhibit symptoms). On the other hand, a large negative intercept indicates a much shorter median onset time. Looking at Table I for Stratum 3, we can see that for the higher altitudes the intercept is indeed negative—we expect the onset times to be shorter.

### Combined Model

It is generally agreed that the symptoms of DCS are caused by the growth of nitrogen bubbles in the tissues. The size and location of these bubbles are believed to have a significant effect on the manifestation of symptoms. However, it is still not clear where these bubbles originate, and how exactly they affect the onset of symptoms. The database contains quantitative information on the VGE found during all exposures at altitude. Echocardiography was used to monitor the subjects at regular intervals. The extent of these circulating bubbles is graded using Spencer’s scale (32), which ranges from Grade 0 indicating no bubbles, to Grade 4 indicating a bubble grade and the time of onset.

The bubbles that are observed are circulating bubbles and it is clear that these are not directly the cause of most symptoms, such as joint pain. It is not clear whether the presence of these bubbles is somehow related to the size or growth of the extravascular bubbles that are thought to cause most symptoms. However, it is not possible to obtain measurements on the size or location of the bubbles that directly impact symptoms, and VGE are the only currently observable measure of bubble activity in human subjects.

Using the database, Kannan and Kauchardhuri (11) showed that in individuals who have at least bubbles of Grade 2 or more, the time at which the bubble grade is maximum is highly correlated with symptom onset time. A loglogistic model was fit to the data adding “maximum bubble grade” as a risk factor. The results indicated that maximum bubble grade is highly significant, dampening the effects of the other risk factors. This loglogistic model with maximum bubble grade was used to predict the probability of DCS for several profiles. For profiles with low preoxygenation times, the predictions were significantly closer to the database values compared with the model that did not include bubble data. However, the problem with considering maximum bubble grade as a risk factor is that, unlike the other risk factors, it is not fixed by the profile but varies from individual to individual. An estimate of maximum bubble grade must be provided before the model can be used for prediction. The mathematical model (bubble growth model) described above provides an estimate of the time at which the bubble
```


## Page 7

```markdown
# ALTITUDE DCS MODEL VALIDATION—PILMANIS ET AL.

## TABLE II. PROFILE DESCRIPTIONS.

| Database Profile | Pre-Breathe, min | Exposure Duration, min | Altitude, ft | Exercise  |
|------------------|------------------|------------------------|-------------|-----------|
| A                | 90               | 180                    | 35,000      | Moderate  |
| B                | 30               | 240                    | 25,000      | Heavy     |
| C                | 15               | 240                    | 22,500      | Heavy     |
| D                | 0                | 360                    | 18,000      | Heavy     |
| E                | 75               | 240                    | 30,000      | Rest      |

The maximum bubble size time combines with other risk factors in the logistic model. In summary, inputs to the combined model were the following risk factors: 1) altitude/pressure; 2) exposure time; 3) preoxygenation time; 4) level of exercise; and 5) time to maximum bubble grade (bubble growth model). Thus, the statistical and deterministic (bubble growth) models described above were combined to provide a single output expressed as the percent of DCS predicted.

### Model Validation

Theoretical decompression models abound in the literature. Scientific discourse regarding pros and cons is a valuable academic process. However, such a theoretical model should not be transitioned to the operational setting until there is evidence of its efficacy. Thus, before this combined model can be transitioned to operational application, it must be validated for the altitude exposure. Such prospective human trials for validation of the model prediction are impractical because of time, expense, and potential sequelae in the subjects, especially with hyperbaric exposures. This study prospectively exposed human subjects to altitude scenarios not previously used in the development of the model. The incidence of DCS in these exposures was then compared with that predicted by the model. This validation process is crucial in determining that a given model is indeed accurate. This can only be assured by using the model to predict DCS risk during exposures where at least one of the primary factors affecting DCS risk is substantially at variance with the database used to develop the model. Human subject exposures are then accomplished under the same conditions used to develop the model prediction. Comparison of results from the model predictions and actual exposures, with identical primary factors affecting DCS risk, will determine the ability of the model to accurately predict DCS risk. Altitude profiles were selected for this validation study that represented “holes” in the database and would, therefore, provide the best test of the model.

### METHODS

The voluntary, fully informed written consent of the subjects used in this research was obtained and the protocol was approved by the Brooks Institutional Review Board and the USAF Surgeon General’s Office. All subjects passed an appropriate physical examination and were representative of the USAF rated aircrew population. The general procedures and precautions for altitude exposure of subjects were as in previously published AFRL studies (46). Breathing gas during preoxygenation, while decompressed, during descent, and during post-breathing was 100% oxygen (aviator’s breathing oxygen; normal analysis 99.7–99.8% oxygen). A neck-seal respirator made by Intertechnique® (Plaisir Cedex, France) was used to deliver oxygen. This mask provided a slight (2-cm of water) positive pressure, which reduced the opportunity for inboard leaks of nitrogen from the atmosphere and was more comfortable than the standard aviator’s mask. Subjects were not allowed to participate in scuba diving, hyperbaric exposures, or flying for at least 72 h before each scheduled altitude exposure. The five exposure profiles are described in Table II. For profiles B through E, chamber ascent was made to an altitude not higher than 30,000 ft at a rate not greater than 5000 ft · min⁻¹. For profile A, chamber ascent was at a rate of 5000 ft · min⁻¹ to 20,000 ft, and then to 35,000 ft at a rate of 10,000 ft · min⁻¹. Each subject accomplished two of the five exposure profiles shown in Table II. Subjects had to experience at least one heavy exercise profile.

At 16-min intervals during the exposure, the subjects were monitored for VGE using a 5,000 Doppler/Echo-Imaging System (Hewlett Packard, Houston, TX). This system permits both audio and visual monitoring and recording of gas emboli in all four chambers of the heart and allows for easier and more accurate determination of emboli presence than Doppler alone. Detection of any left ventricular gas emboli was made possible due to these echo-imaging sessions and was cause for immediate recompression to avoid potentially serious symptoms resulting from arterial gas emboli. VGE were graded using a modified Spencer scale (32).

At altitude, the subjects rested or performed moderate to heavy exercise (Table II). Moderate exercise consisted of a cycle of three exercises designed to simulate extravehicular activities performed by NASA shuttle crewmembers and described in more detail in Webb et al. (42). The subjects exercised at each station for 4 min each cycle. At one station, the subjects turned a Monarch® 868 cycle ergometer (Monarch, Varberg, Sweden) set up as a hand crank at 24 rpm (4 N), alternating every two revolutions; each 5 s. At a second station, the subjects applied force with a torque wrench, set at 25 ft-lbs, to bolt-like projections mounted on a wall for 5 s in each position alternately with each arm. At the third station, the subjects pulled on a handgrip attached to a pulley system set to 17 lbs (8.5 kg) of resistance. The subject pulled from arms reach at head level to their waist once each 5 s, alternating left, right, then both arms. Heavy exercise consisted of cycle ergometry. Subjects continuously alternated between exercising for a
```


## Page 8

```markdown
# ALTITUDE DCS MODEL VALIDATION—PILMANIS ET AL.

## TABLE III. RESULTS OF VALIDATION.

| Profile | N  | Preox (min) | Alt (ft) | Exercise | Duration | PDCS (%) | ADCS (%)* | AVGE (%) |
|---------|----|-------------|----------|----------|----------|----------|-----------|----------|
| A       | 7F, 23M | 90  | 35,000   | Mild     | 180      | 94       | 94 ± 6/9  | 83       |
| B       | 9F, 21M | 30  | 25,000   | Heavy    | 240      | 53       | 61 ± 17   | 90       |
| C       | 4F, 26M | 15  | 22,500   | Heavy    | 240      | 44       | 30 ± 16   | 73       |
| D       | 5F, 25M | 0   | 18,000   | Heavy    | 360      | 17       | 13 ± 12   | 63       |
| E       | 9F, 21M | 75  | 30,000   | Rest     | 240      | 63       | 58 ± 17   | 66       |

**NOTE:** 30 subjects were exposed to each of the 5 profiles; the N is divided into male (M) and female (F) subjects.  
PDCS is the DCS predicted by the model; ADCS and AVGE are the actual DCS and VGE incidences found experimentally.  
*The margin of error was computed using 95% confidence intervals for the Kaplan-Meier estimates.

---

The confidence bands are the criteria used here. A statistical test indicated the predicted and actual DCS curves were not significantly different (p > 0.05). In order to evaluate the predictions from the model, we use the estimates of the β coefficients from the Tables in the expression for the logistic distribution obtained from SAS to predict the probability of DCS over time for several exposure profiles (Fig. 1–5). The thick solid lines in Fig. 1–5 are the predicted probability of DCS over time. The thinner lines with dots represent the actual DCS results from the validation. The thin lines are the 95% confidence intervals (CI). Both the predicted curves and the actual curves are sigmoidal in shape. It is apparent that most of the predicted values are within the 95% intervals. Although as a whole the predicted and the actual DCS curves overlap, profiles 1, 2, and 3 are outside of the 95% CI. In Fig. 4 and 5, the predictive curves are entirely within the 95% CI. In Fig. 1, the predicted DCS is higher than the actual DCS early in the exposure duration, but the two curves are virtually indistinguishable at the end. The 35,000-ft exposures have provided valuable data about the effects of high altitude combined with exercise which will be used to update the model and further improve the predictions. In Fig. 2, between 60–150 min of exposure time, the predictive curve slightly underpredicts the DCS risk. As previously mentioned, there were no profiles that incorporated heavy exercise in the database. The addition of these data to the database will provide for greater accuracy in future model modifications.

## RESULTS

The model-predicted incidence of DCS (PDCS) and actual experimental DCS incidence (ADCS) from this prospective validation study are shown in Table III. The ADCS column also shows the margin of error for the actual DCS incidence. The actual incidence of “any” VGE (grade 1 or higher) at the end of the exposures (AVGE) is also shown in Table III. Shapes of the DCS and VGE onset curves representing cumulative DCS and VGE incidence vs. time for each of the model validation study profiles are shown in Fig. 1, 2, 3, 4 and 5. The 95% confidence intervals for the profiles’ curves encompass the respective predicted onset curves from the model.

---

![Fig. 1](image_url)
**Fig. 1.** Cumulative DCS and any VGE vs. exposure time for Profile A (35,000 ft); predicted vs. actual % DCS incidence and 95% confidence intervals.

---

*Aviation, Space, and Environmental Medicine • Vol. 75, No. 9 • September 2004*
```


## Page 9

```markdown
# ALTITUDE DCS MODEL VALIDATION—PILMANIS ET AL.

![Fig. 2](image-link)
**Fig. 2.** Cumulative DCS and any VGE vs. exposure time for Profile B (25,000 ft); predicted vs. actual % DCS incidence and 95% confidence intervals.

![Fig. 4](image-link)
**Fig. 4.** Cumulative DCS and any VGE vs. exposure time for Profile D (18,000 ft); predicted vs. actual % DCS incidence and 95% confidence intervals.

## DISCUSSION

An altitude DCS predictive model has been developed at AFRL and the predictive ability and accuracy of this model have been validated with prospective human subject exposures. Each of the five profiles in the model validation study was under different conditions than those used to develop the model. The chamber profiles resulted in symptom onset curves which were generally within 5% of the predicted curves. The predicted values for the end of the exposures were not significantly different from the actual experimental values found. After this validation process, the data from the five experimental exposures of this study will be added to the database and combined with the modified model to improve its prediction accuracy. Results from these and other studies at AFRL required the addition of new stratified models to adjust for interactions between pressure and exercise (13). The database used to develop the initial model contained no information on heavy exercise, whereas three of the five validation profiles used heavy exercise. These data on heavy exercise helped to better evaluate and understand the effects of various exercise levels on DCS symptoms. The data at 35,000 ft helped to separate the effects of rest, mild exercise, and heavy exercise, and led to a better definition of the risk factors.

Although the model does not predict VGE incidence, the VGE data for the actual exposures are included in Fig. 1–5 and Table III. The data include any VGE at grade 1 or higher. In Table III, the actual VGE incidences at the end of the exposures do not show much difference between the five profiles, even though the altitudes range from 18,000 ft to 35,000 ft. Furthermore, from Fig. 1–5 it is clear that the VGE incidence onset curves level off at approximately 90 min into the exposures for all five profiles. These data further support the concept that DCS cannot be predicted from VGE monitoring (28,2). Therefore, modeling VGE data for the purpose of predicting DCS would not be fruitful. It is interesting to note that at the lower altitudes, VGE onset curves are widely separated from the much lower DCS curves. Progressively, these VGE and DCS curves move closer together as the altitude increases. In Profile A, at 35,000 ft, the DCS curve increases above the VGE curve at approximately 110 min into the exposure. At this time, DCS symptoms would occur before VGE are detected.

## CONCLUSION

A predictive altitude DCS model has been developed at AFRL. The predictive ability and accuracy of this model have been validated by a total of five profiles using human subjects exposed in an altitude chamber. Although there have been attempts in the past to validate altitude DCS models (5), this study represents the first time an altitude DCS model has been successfully validated using subsequent human subject exposures and rigorous experimental/statistical techniques over a wide range of exposure profiles. It should be remembered that this model is based on DCS data from exposure of military subjects and application to the civilian sector.

![Fig. 3](image-link)
**Fig. 3.** Cumulative DCS and any VGE vs. exposure time for Profile C (22,500 ft); predicted vs. actual % DCS incidence and 95% confidence intervals.

![Fig. 5](image-link)
**Fig. 5.** Cumulative DCS and any VGE vs. exposure time for Profile E (30,000 ft); predicted vs. actual % DCS incidence and 95% confidence intervals.

*Aviation, Space, and Environmental Medicine • Vol. 75, No. 9 • September 2004*
```


## Page 10

```markdown
# ALTITUDE DCS MODEL VALIDATION—PILMANIS ET AL.

population may not be valid because the anthropometry may differ. Finally, it is important to understand that the model predictions are population predictions and not individual predictions. As has been mentioned, there is great individual DCS variation to altitude exposure and application of DCS prediction from this model to individuals is strongly discouraged.

## ACKNOWLEDGMENTS
This work was supported by the Air Force Research Laboratory, Brooks City-Base, TX, USAF Contract F41624-97-D-6004. The authors gratefully acknowledge Kevin M. Krause, Ph.D., for his academic and experimental methods contributions to this project. We further acknowledge the support of Ms. Heather O. Alexander of Wyle Laboratories, Inc., in all aspects of subject affairs, including procurement of subjects, scheduling of subjects both for experiments and for training examinations, and the monitoring of subjects at altitude. Appreciation is expressed to the USAF Office of Scientific Research, Summer Research Extension Program for support in 1997 and 1999.

## REFERENCES
1. Afermanhan A, Advani SG, Michaelides EE. An accurate numerical solution for mass diffusion-induced bubble growth in viscous liquids containing limited dissolved gas. Int J Heat Mass Transfer 1992; 35: 1311–7.
2. Bayne CG, Hunt WS, Johanson DC, et al. Doppler bubble detection and decompression sickness: a prospective clinical trial. Undersea Biomedical Res 1985; 12: 327–32.
3. Bendrick GA, Ainscough MJ, Pilmanis AA, Bisson RU. Prevalence of decompression sickness among U-2 pilots. Aviat Space Environ Med 1996; 67: 696–9.
4. Borg GA. Psychophysical bases of perceived exertion. Med Sci Sports Exerc 1982; 14: 377–81.
5. Conkin J, Edwards BF, Wigalano JM, Horrigan DJ Jr. Empirical models for use in designing decompression procedures for space operations. Houston, TX: NASA; 1987. NASA Technical Memorandum 100456.
6. Conkin J, Kumar KV, Powell MR, et al. A probabilistic model of hypobaric decompression sickness based on 66 chamber tests. Aviat Space Environ Med 1996; 67: 176–83.
7. Epstein PS, Plesset MS. On the stability of gas bubbles in liquids as solutions. J Chem Phys 1950; 18: 1505–9.
8. Gerth WA, Vann RD. Statistical bubble dynamics algorithms for the assessment of altitude decompression sickness incidence. San Antonio, TX: AFRL; 1997. Armstrong Laboratory Technical Report. Report No. AL/OE-TR-1995–0037.
9. Hlastala MP, Van Liew HD. Absorption of in vivo inert gas bubbles. Resp Physiol 1975; 24: 147–58.
10. Kalbfleisch JD, Prentice RL. The statistical analysis of failure time data. New York: Wiley; 1980.
11. Kannan N, Raychaudhuri A. Survival models for predicting altitude decompression sickness. San Antonio, TX: AFRL; 1998. Armstrong Laboratory Technical Report. AL/OE-TR-1997–0030.
12. Kannan N, Raychaudhuri A, Pilmanis AA. A log-logistic model for predicting decompression sickness. Aviat Space Environ Med 1998; 69: 696–70.
13. Kannan N, Raychaudhuri A. A stratified statistical model for predicting the incidence of type I/type II decompression sickness [Abstract]. Aviat Space Environ Med 1992; 63: 410.
14. Kislovky Y, Kopylov AV. The rate of gas-bubble growth in tissue under decompression. Mathematical modelling. Respir Physiol 1988; 71: 299–306.
15. Krause KM, Pilmanis AA. Effectiveness of ground-level oxygen in the treatment of altitude decompression sickness. Aviat Space Environ Med 2000; 71: 115–8.
16. Krutz RW, Dixon GA. The effects of exposure on bubble formation and bends susceptibility at 9,100 m (30,000 ft; 43.3 psia). Aviat Space Environ Med 1986; 57: A97–9.
17. Kumar KV, Calkins DS, Waligora JM, et al. Time to detection of circulating microbubbles as a risk factor for symptoms of altitude decompression sickness. Aviat Space Environ Med 1992; 63: 691–4.
18. Kumar KV, Powell MR. Survival models for estimating the risk of decompression sickness. Aviat Space Environ Med 1994; 65: 661–5.
19. Kumar KV, Waligora JM, Calkins DS. Threshold altitude resulting in decompression sickness. Aviat Space Environ Med 1990; 61: 685–9.
20. Kumar KV, Waligora JM, Powell MR. Epidemiology of decompression sickness under simulated space extravehicular activities. Aviat Space Environ Med 1993; 64: 1032–9.
21. Lambertsen CJ, Nishi RY, Temple JR. Relationships of Doppler venous gas embolism to decompression sickness. Philadelphia, PA: Environmental Biomedical Research Data Center, Institute for Environmental Medicine, University of Pennsylvania Medical Center; 1997. Report No. 7–10–1997.
22. Meliss N, Nir A, Kerem D. Bubble dynamics in perfused tissue undergoing decompression. Respir Physiol 1981; 43: 89–98.
23. Nikolaev YP. Effects of heterogeneous structure and diffusion permeability of body tissues on decompression gas bubble dynamics. Aviat Space Environ Med 2000; 71: 723–9.
24. Petropoulos LJ, Kannan N, Pilmanis AA. Altitude decompression sickness (DCS) risk assessment computer (ADRAC). Toronto, Canada: NATO RTO; 1999: 27–16. NATO RTO-MP-20 AC/323(HFM)TP/7.

## APPENDIX A. DEFINITIONS OF SYMBOLS

- \( C \) = Concentration of nitrogen gas (a function of space and time)
- \( c \) = Partial Derivative of the nitrogen gas concentration
- \( D \) = Diffusion constant
- \( R(t) \) = The location of the bubble surface
- \( R(t) = R \) = The radius of the outer shell that encloses the bubble
- \( p \) = Partial pressure of the diffusing gas inside the bubble
- \( R_g \) = Gas law constant
- \( T \) = Temperature
- \( M \) = Molecular weight of the gas
- \( \rho \) = Density associated with the concentration measured in moles of dissolved gas per unit volume of the media surrounding the bubble
- \( \sigma \) = Surface tension
- \( \eta \) = Viscosity of the media surrounding the bubble
- \( p_a \) = The equilibrated (at ambient level) pressure of the dissolved \( N_2 \)
- \( R' \) = First derivative of \( R \) with respect to time
- \( R'' \) = Second derivative with respect to time
- \( \xi = (R'/V + R'') \) is non-dimensional
- \( k_m \) = Henry's law constant

### Equations

\[
\frac{\partial C}{\partial t} + u_r \frac{\partial C}{\partial r} = \frac{D}{r} \frac{\partial}{\partial r} \left( r \frac{\partial C}{\partial r} \right) - k \cdot R(t) < r < \delta(t)
\]

Eq. 1

\[
\frac{\partial C}{\partial t} = \frac{D}{r^2} \frac{\partial}{\partial r} \left( r^2 \frac{\partial C}{\partial r} \right) - k
\]

Eq. 2

\[
\left( \frac{1}{2} \xi^2 - 1 \right) R^2 - \left( \sigma - 1 \right) R' R + 2 R R''
\]

Eq. 3

\[
(p_s - p_R) = 2 \sigma + 4 \eta \xi - 1 R
\]

Eq. 4

\[
C(R,t) = K_p p_R
\]

Eq. 5

\[
\frac{\partial C(\delta,t)}{\partial t} = 0
\]

Eq. 6

\[
P(DCS \text{ up to time } t) = 1 - \left( \Delta t \right)^t
\]

Eq. 7

\[
\lambda = \exp \left( -(\beta_0 + \beta_1 p_R + \beta_2 \text{prox} + \beta_3 \text{exp}) \right)
\]

Eq. 8
```


## Page 11

```markdown
## ALTITUDE DCS MODEL VALIDATION—PILMANIS ET AL.

26. Pilmanis AA, Meltonian AD. Altitude decompression computer development progress report. In: AA Pilmanis, ed. Proceedings of the 1999 Hypoxia Decompression Sickness Workshop. San Antonio, TX: AFRL; 1999:27–40. Armstrong Laboratories Special Report, AL-SR-1999-0002-0050.

27. Pilmanis AA. Altitude decompression sickness. In: Moon RE, Sheffield PJ, eds. Treatment of decompression illness: proceedings of the forty-fifth UHMS workshop on treatment of decompression sickness: 18–19 June 1995; Palm Beach, FL. Bethesda, MD: Undersea and Hyperbaric Medical Society; 1996:25–42.

28. Pilmanis AA, Kannan N, Krause KM, Webb JT. Relating venous gas emboli (VGE) scores to acute decompression sickness (DCS) symptoms [abstract]. Aviat Space Environ Med 1999; 70:364.

29. Pilmanis AA, Olson RM, Fischer MD, et al. Exercise-induced altitude decompression sickness. Aviat Space Environ Med 1999; 70:22–9.

30. Ryles MT, Pilmanis AA. The initial signs and symptoms of altitude decompression sickness. Aviat Space Environ Med 1996; 67:783–9.

31. Spencer HF, Hamilton RW, eds. Validation of decompression tables. 37th UHMS workshop proceedings. Bethesda, MD: Undersea and Hyperbaric Medical Society; 1989. UHMS Publication Number 71, V1–1–88.

32. Spencer MP. Decompression limits for compressed air determined by ultrasonically detected blood bubbles. J Appl Physiol 1976; 40:229–35.

33. Subramanian S, Chi B. Bubble dissolution with chemical reaction. Chem Eng Sci 1993; 50:2185.

34. Sulaiman MA, Pilmanis AA, O’Connor RB. Relationship between age and susceptibility to decompression sickness. Aviat Space Environ Med 1997; 68:695–8.

35. Tveiten R, Ward CA, Venter RD. Bubble evolution in a stirred vessel of liquid cooled by a constant heat flux. J Appl Phys 1963; 54:1–9.

36. Van Liew HD. Simulation of the dynamics of decompression sickness bubbles and the generation of new bubbles. Undersea Biomed Res 1991; 18:353–435.

37. Van Liew HD, Burkard ME. Density of decompression bubbles and composition of gas among bubbles, tissue, and blood. J Appl Physiol 1993; 75:2293–301.

38. Van Liew HD, Conkin J, Burkard ME. Probabilistic model of altitude decompression sickness based on mechanistic premises. J Appl Physiol 1994; 76:2762–74.

39. Van Liew HD, Hlastala MP. Influence of bubble size and blood perfusion on absorption of gas bubbles in tissues. Respir Physiol 1969; 7:171–21.

40. Webb JT, Krutz RW, Dixon GA. An annotated bibliography of hypobaric decompression research conducted at the Crew Technology Division, USAF School of Aerospace Medicine, Brooks AFB, Texas from 1938 to 1985. Brooks AFB, TX: USAF-SAM; 1990. USAFSAM Technical Paper AS-108.

41. Webb JT, Fischer MD, Pilmanis AA. Exercise-enhanced preoxygenation increases protection from decompression sickness. Aviat Space Environ Med 1996; 67:618–24.

42. Webb JT, Pilmanis AA, O’Connor RB. An abrupt zero-preoxygenation altitude threshold for decompression sickness symptoms. Aviat Space Environ Med 1998; 69:335–40.

43. Webb JT, Pilmanis AA, Krause KM. Preoxygenation time versus decompression sickness incidence. Aviat Space Environ Med 1997; 68:702–5.

44. Webb JT, Pilmanis AA, Kannan N, Olson RM. Risk of staged decompression sickness following 100% oxygen at altitude decompression schedule. Aviat Space Environ Med 2000; 71:692–8.

45. Webb JT, Krause KM, Pilmanis AA, et al. The effect of exposure to 35,000 ft on an incidence of altitude decompression sickness. Aviat Space Environ Med 2001; 72:509–12.

46. Webb JT, Kannan N, Pilmanis AA. Gender as factor for altitude-decompression sickness risk. Aviat Space Environ Med 2003; 74:758–65.

---

*Aviation, Space, and Environmental Medicine • Vol. 75, No. 9 • September 2004*  
759
```