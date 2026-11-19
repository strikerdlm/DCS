# Aviation pressure histories

The **Aviation pressure history** page sends its displayed timeline to the Python calculation core. The ten-minute example returns physiological outputs and gives the applicability reasons for withholding a clinical probability. The second example reproduces the male chamber reference calculation at 6.5 psia in Table 5. In the simple form, the preoxygenation period includes the entered oxygen interruption. The advanced editor accepts multiple interruptions, changes of gas and pressure, and measured or externally reconstructed initial states.

## Run a calculation

Start the API with `uvicorn tinydcs.api:app --port 8180`, then open the model explorer, or send the example directly.

```sh
curl -s http://127.0.0.1:8180/api/v3/aviation/evaluate \
  -H "Content-Type: application/json" --data-binary @docs/examples/aviation-table5.json
```

The example starts at 14.7 psia on air. It specifies 115 minutes of oxygen at rest, 30 minutes of ascent on oxygen, and 240 minutes at 6.5 psia with ambulation on oxygen. The 145-minute washout includes ascent once. Eq. 7 gives **3.1011%** cumulative symptomatic DCS by four hours in the source male reference group. The source table describes an approximate 3% contour. [Example profile](examples/aviation-table5.json) · [NASA/TP-2020-220529, Table 5](https://ntrs.nasa.gov/api/citations/20200004317/downloads/20200004317.pdf)

For direct Python use, validate the same JSON with `tinydcs.exposure.ExposureProfile.model_validate_json` and pass it to `tinydcs.aviation_models.evaluate`. The OpenAPI document at `/openapi.json` describes the profile fields. `GET /api/v3/aviation/models` returns the reviewed model definitions. Both API and Python use schema and core version 1.0.0.

## What the quantities describe

- **Starting state.** Record the body-experienced absolute pressure or pressure altitude, breathing gas, prior exposures and the basis for initial nitrogen. A site-equilibrium assumption applies to the starting site entered. Earlier pressure or gas changes can be supplied as history. Unknown initial nitrogen can withhold a result.
- **Pressure and time.** The core normalizes pressure to pascals and segment times to its declared units. Pressure altitude uses the two-layer US Standard Atmosphere up to 20 km. Chamber pressure, body/suit absolute pressure, suit differential and breathing gas are distinct inputs. Linear interpolation describes absolute pressure between segment endpoints.
- **Nitrogen and workload.** The chosen compartment and driving-gas convention are part of the result. The source equations use dry nitrogen, including the source treatment of argon. A phase may specify workload and ambulation separately. Source-assigned exercise coding and estimated workload have distinct provenance.
- **Four physiological outputs.** Arrival nitrogen is the state at the beginning of the plateau. Exit nitrogen includes the plateau. Maximum tissue ratio spans the trajectory. Integrated positive supersaturation is reported in Pa·s. These quantities can describe a profile even when its clinical probability is unavailable.
- **Prediction window.** The source survival estimate concerns events during the plateau. Complete short exposures and delayed outcomes require their own data. For the 2004 fixed endpoint, NM counts post-test diagnoses in its source ascertainment window and RM counts events during exposure.
- **Quantitative release.** A source reference estimate carries the model/version, endpoint, window, assumptions and canonical input SHA-256. Unavailable probabilities are null. The sources lack the joint information needed for a complete probability interval. Interrupted protocols retain the gas trajectory and an applicability result. Operational rule authorization requires a controlled procedure.

The independent reference equations change at 5 psia. At arrival nitrogen 7.5 psia, four hours, ambulation, BMI 24 and no staged repressurization, the compatibility calculator gives 8.261463% at 5.000000 psia and 11.350402% at 5.000001 psia with the male reference selected. Version 3 also checks the full protocol before releasing a reference value. [Source model cards and discrepancies](source-discrepancies.md)

## Import an evaluated workbook experiment

The ML repository distributes an evaluated `.dcsbundle` and SHA-256. Configure the server environment with `TINYDCS_LABEL_BUNDLE` pointing to a local copy and `TINYDCS_LABEL_BUNDLE_SHA256` set to the digest of the reviewed release. Install the scikit-learn version recorded by the producer. The digest is verified before estimator deserialization. Only server configuration can select or replace an artifact.

```sh
curl -s http://127.0.0.1:8180/api/v3/workbook/predict \
  -H "Content-Type: application/json" \
  -d '{"altitude_ft":26000,"prebreathing_min":0,"time_at_altitude_min":60,"exercise_level":"Rest"}'
curl -s http://127.0.0.1:8180/api/v3/workbook/evaluation
```

The response identifies the fitted artifact, quantitative-release status and the profile-based residual interval for agreement with workbook labels. It checks the complete observed input grid. A missing bundle returns HTTP 503. An unsupported combination returns a null label estimate. The clinical probability is null for this experiment. [Workbook project](https://github.com/strikerdlm/DCS-model-with-Machine-Learning)

## Migration

Existing clients of `/api/v2/hypobaric/probability` can continue supplying their own source-compatible arrival nitrogen and receiving a percentage. Version 3 derives arrival nitrogen from segments and returns a fraction. The older surrogate feature `tissue_n2_ratio_360min` retains its humidified, sea-level, instantaneous-ascent, plateau-exit definition for artifact compatibility. Subject-specific projections carry the base release mask and a veto inherited from every observation used for that subject. In the Python array interface, withheld point and interval entries are NaN and the separately named diagnostic point remains available for research comparisons.

The aviation browser uses the same server as the EVA page by default. Set `VITE_TINYDCS_V3_API_URL` to override the version 3 API root. **Download profile and result** exports the entered timeline and the exact calculation record shown.

The Streamlit launcher uses the same profile evaluator, bundle reader and 3RUT reconciliation status. Install with `pip install -e '.[app]'` and run `streamlit run apps/streamlit/app.py`. The workbook view reads the same server-configured digest and evaluation as the API. Older separate scaler/encoder files require a newly evaluated bundle to use this view.
