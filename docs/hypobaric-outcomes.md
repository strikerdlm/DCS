# Hypobaric DCS and Doppler VGE

The chamber outcomes page evaluates symptomatic decompression sickness (DCS), first Doppler detection of venous gas emboli (VGE) and first Grade IV VGE detection for the same pressure history. Each result identifies the endpoint, population, observation window, evidence, model digest and eligibility reasons. A recorded zero and an unavailable estimate have different representations. An individual clinical probability for routine aviation training remains unavailable.

## Run a profile

Start the Python service with `python -m uvicorn tinydcs.api:app --port 8180`. Open **Chamber research outcomes** in the browser or send the included JSON directly.

```sh
curl -s http://127.0.0.1:8180/api/v3/hypobaric/outcomes/models
curl -s http://127.0.0.1:8180/api/v3/hypobaric/outcomes/predict \
  -H 'Content-Type: application/json' --data-binary @docs/examples/hypobaric-outcomes.json
```

Enter body-experienced absolute plateau pressure in psia or pressure altitude in feet, starting absolute pressure, resting oxygen time, ascent duration and minutes at plateau. Activity includes ambulation. Age, source-coded sex and BMI contribute only to models that use them. The compact NASA presets assume ordinary-air equilibrium, no recent diving or prior altitude exposure, oxygen during ascent, and the source exercise assignment. An oxygen interruption with unknown timing or gas withholds arrival nitrogen. The aviation history editor accepts detailed interruptions, gas mixtures, previous exposures and return profiles. [Example input](examples/hypobaric-outcomes.json) · [Full pressure-history interface](aviation-profile.md)

## Reading the estimates

| Output | What is being estimated | Evidence and eligibility |
|---|---|---|
| Published symptomatic DCS | Symptomatic DCS by the requested time at test pressure in the named chamber reference | The NASA recommendation selects Eq. 4 at 4–5 psia and the male-cohort Eq. 7 above 5 psia. Checks also cover the protocol, duration, arrival nitrogen and model-specific covariates. |
| Published any VGE or Grade IV VGE | First detection of the specified Doppler endpoint by plateau time | NASA Eqs. 5 and 6 use time in hours, age, sex as recorded, arrival TR360, ambulation and staged repressurization. The report counts 368 any-VGE and 166 Grade IV detections in 903 monitored exposures. |
| Observed DCS study | Group incidence at a combination of mean TR360, pressure, duration and ambulation appearing in NASA Table F1 | Fitted to medical officers' counts in 41 tests. Within the browser calculation, the entered dose represents a hypothetical group mean rounded to the two decimals in the source. The card reports source test IDs and their observed numerator and denominator. |
| Observed Grade IV VGE study | Cumulative Grade IV detection in a hypothetical monitored chamber study profile | An interval-censored fit uses age, source sex, TR360 and ambulation. The public records lack individual gas/pressure histories. The comparison requires an eligible chamber history near 4.3 psia, the training covariate ranges, and 2–4 hours. |

The published VGE adapter conservatively supports the 4.3-psia research setting and the explicit Appendix A worked example at 6.0 psia, ages 20–54 and TR360 of 0.92–2.02. Its study comparator has a training age range of 21–54. Each endpoint retains its own gate. Scientific source populations may overlap across these studies. The observations do not support transport to short air-breathing chambers, chronic high-altitude residents or post-return clinical follow-up. [NASA/TP-2020-220529, Tables 2 and 3 and §§3–5](https://ntrs.nasa.gov/citations/20200004317) · [NASA Table F1](https://www.nasa.gov/wp-content/uploads/2023/03/abercromby-suited-chamber-testing-tp220343-2019.pdf) · [VGE study dictionary](https://raw.githubusercontent.com/cran/thregI/11919e13da5be6412dde3184c814ffd3fb4f1873/man/hdsd.Rd)

The resting Appendix A example uses 60 minutes of surface oxygen, a 15-minute ascent and four hours at 6.0 psia. The software yields 58.75% any VGE and 33.44% Grade IV VGE, within 0.1 percentage points of the report's 58.8% and 33.5%. For symptomatic DCS the software follows the report's pressure-branch recommendation in §5.1 and returns 19.13% using Eq. 7. Appendix A instead illustrates 20.2% from Eq. 4 at that pressure. [NASA technical report, Appendix A and §5.1](https://ntrs.nasa.gov/citations/20200004317)

The supplied JSON uses 229 minutes of resting oxygen plus 15 minutes of ascent. The modeled arrival ratio rounds to 1.69 at 4.3 psia. Test 2a shares that published mean, four-hour duration and ambulation. Its medical officers counted 7 cases in 23 exposures. The fitted protocol-group incidence is 22.66%. The comparison does not identify a participant or establish that the two oxygen schedules were identical. In the source tables most symptoms occurred at altitude, and some cases were first reported after the test. Post-return surveillance was not standardized. [NASA Table F1](https://www.nasa.gov/wp-content/uploads/2023/03/abercromby-suited-chamber-testing-tp220343-2019.pdf)

## Verification

The DCS group fit held out all tests of each protocol family in turn. Among 885 evaluable exposures and 124 DCS cases, held-out log loss was 0.39157 versus 0.40959 using the training incidence alone. Anonymous group totals prevent adjustment for repeat volunteers across families. The Grade IV study held out 60 of 238 published IDs. Mean interval negative log likelihood was 1.1912 versus 1.3642 for the intercept-only comparator. At four hours, 18 held-out records had detected Grade IV VGE, 22 were observed detection-free and 20 had unresolved outcomes. The data bound the event fraction at 30.0–63.3%. Neither study supplies an externally calibrated individual probability interval. [Group DCS export](../tinydcs/studies/nasa-chamber-dcs-v1.json) · [Grade IV VGE export](../tinydcs/studies/grade-iv-vge-v1.json)

The API returns probabilities as fractions and the browser displays percentages. The workbook experiment has its own model, endpoints and uncertainty. With a verified workbook configured, `GET /api/v3/workbook/support` lists the supported curves and their actual time points. `GET /api/v3/workbook/coverage` reports complete-curve coverage, point coverage and interval widths in percentage points by altitude, prebreathing and activity.
