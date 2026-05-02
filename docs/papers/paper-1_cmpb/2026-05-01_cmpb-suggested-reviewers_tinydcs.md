# Suggested Reviewers — TinyDCS to CMPB

> **All five emails verified via primary sources on 2026-05-01.** Two read off institutional faculty/profile pages; three confirmed via recent corresponding-author lines or maintainer-copyright lines on publicly published artefacts. Re-confirm at submission only if more than ~30 days have elapsed.
>
> **Selection criteria applied (CMPB Guide for Authors):** active researcher, published in last 5 years, no co-authorship with Malpica or Farfán in the past 3 years, no shared institution with the authors, verifiable institutional email, no known CMPB editorial-board membership.
>
> **CMPB editorial-board cross-check (verified 2026-05-01).** Editor-in-Chief: Filippo Molinari (Polytechnic of Turin). Main board members visible in public listings include J. G. Chase (Christchurch, NZ), I. Chouvarda (Thessaloniki, Greece), and D. D'Argenio (Los Angeles). None of the candidates below appears on these lists. Re-check the live editorial-board page (https://www.sciencedirect.com/journal/computer-methods-and-programs-in-biomedicine/about/editorial-board) before submission.

---

## Candidate 1 — Peter H. Charlton, PhD

| Field | Value |
|---|---|
| Affiliation | Senior Research Scientist, Nokia Bell Labs Cambridge, UK (since March 2025); previously British Heart Foundation Research Fellow, Department of Public Health and Primary Care, University of Cambridge (2020–2025) |
| ORCID | 0000-0003-3836-8655 |
| Institutional email | **`pete@oxon.org`** *(verified 2026-05-01 on his personal lab homepage)*. The `oxon.org` domain is the official University of Oxford alumni address — accepted by Editorial Manager as institutional. |
| Verification URL | https://peterhcharlton.github.io/ (Contact section lists `pete@oxon.org` directly) |
| Expertise rationale | Charlton's recent work centres on uncertainty quantification for wearable biomedical signals, including a 2025 systematic comparison of eight UQ techniques for photoplethysmography that explicitly evaluates conformal calibration on clinically relevant prediction tasks (atrial-fibrillation detection and blood-pressure regression). The methodological overlap with TinyDCS — calibrated intervals, local calibration assessment, wearable-grade physiological inference — is direct. |
| Representative work | Bench C, Pfeffer O, Desai V, Moulaeifard M, Coquelin L, Charlton PH, Strodthoff N, Hegemann N, Aston PJ, Thompson A. *A systematic evaluation of uncertainty quantification techniques in deep learning: a case study in photoplethysmography signal analysis.* arXiv:2511.00301 (2025). |

---

## Candidate 2 — Esther Rodriguez-Villegas, PhD, FREng

| Field | Value |
|---|---|
| Affiliation | Professor of Low Power Electronics, Department of Electrical and Electronic Engineering, Imperial College London, London, UK |
| ORCID | (see Imperial profile) |
| Institutional email | **e.rodriguez@imperial.ac.uk** *(verified at the Imperial profile page)* |
| Verification URL | https://profiles.imperial.ac.uk/e.rodriguez/professional |
| Expertise rationale | Rodriguez-Villegas leads research on TinyML and embedded ML for healthcare wearables. Her 2022 review, *Embedded Machine Learning Using Microcontrollers in Wearable and Ambulatory Systems for Health and Care Applications*, surveys the exact MCU-class deployment regime that TinyDCS targets (sub-100 KB ONNX, microsecond-class latency, energy-bounded inference) and is one of the most cited references in the TinyML-for-health space. She is well-positioned to evaluate TinyDCS's deployment claims and the realism of the wearable-monitoring framing. |
| Representative work | Diab MS, Rodriguez-Villegas E. *Embedded Machine Learning Using Microcontrollers in Wearable and Ambulatory Systems for Health and Care Applications: A Review.* IEEE Access 10 (2022): 98369–98390. https://doi.org/10.1109/access.2022.3206782 |

---

## Candidate 3 — Francesco Conti, PhD

| Field | Value |
|---|---|
| Affiliation | Associate Professor (since September 2025), Department of Electrical, Electronic, and Information Engineering "Guglielmo Marconi" (DEI), University of Bologna, Bologna, Italy |
| ORCID | (see Google Scholar / unibo profile) |
| Institutional email | **`f.conti@unibo.it`** *(verified 2026-05-01 via two independent sources: ACM Digital Library byline on his FractalSync 2025 paper, and the maintainer-copyright line on the open-source HWPE documentation at hwpe-doc.readthedocs.io)*. |
| Verification URL | https://dl.acm.org/doi/abs/10.1145/3719276.3725203 (corresponding-author email) and https://hwpe-doc.readthedocs.io/en/latest/team.html |
| Expertise rationale | Conti's research is squarely in TinyML hardware and software for ultra-low-power systems-on-chip (PULP Platform), including recent biomedical applications. His co-authored 2026 BioTrain paper demonstrates sub-MB, sub-50 mW on-device fine-tuning of biosignal models on the GAP9 MCU — the deployment regime TinyDCS positions itself for. He is also based at the Polytechnic of Turin's sister Italian institution (U Bologna), which gives him familiarity with the CMPB editorial culture without sharing institutional affiliation with the EIC. |
| Representative work | Wang R, Jung VJB, Wiese P, Frey S, Spacone G, Conti F, Burrello A, Benini L. *BioTrain: Sub-MB, Sub-50mW On-Device Fine-Tuning for Edge-AI on Biosignals.* arXiv:2604.13359 (2026). |

---

## Candidate 4 — Allan Peter Engsig-Karup, PhD

| Field | Value |
|---|---|
| Affiliation | Associate Professor in Scientific Computing, Department of Applied Mathematics and Computer Science (DTU Compute), Technical University of Denmark, Kongens Lyngby, Denmark; affiliated with the Pioneer Centre for Artificial Intelligence |
| ORCID | 0000-0001-8626-1575 |
| Institutional email | **apek@dtu.dk** *(verified at https://www.dtu.dk/english/person/allan-peter-engsig-karup)* |
| Verification URL | https://www.dtu.dk/english/person/allan-peter-engsig-karup |
| Expertise rationale | Engsig-Karup recently co-authored a study applying conformal prediction with Venn-ABERS calibration to clinical bacterial-infection-focus prediction, combining gradient-boosting risk classifiers with conformal risk control — a direct methodological parallel to TinyDCS's split-conformal calibration over a gradient-boosting backbone. His broader portfolio in scientific machine learning, fast solvers, and uncertainty-aware modelling makes him well-placed to evaluate the monotonicity-constrained surrogate construction and the mathematical correctness of the Mondrian / zero-inflated calibration stack. |
| Representative work | Schmidt JB, Nielsen KL, Strunin D, Kirkby NS, Thomassen JQ, Rasmussen SC, Frikke-Schmidt R, Hertz FB, Engsig-Karup AP. *Conformal Prediction and Venn-ABERS Calibration for Reliable Machine Learning-Based Prediction of Bacterial Infection Focus.* medRxiv 2025.01.21.25320878 (2025). |

---

## Candidate 5 — Nils Strodthoff, PhD

| Field | Value |
|---|---|
| Affiliation | Professor of eHealth (Interpretable and Explainable Learning Algorithms), Department of Health Services Research, Carl von Ossietzky Universität Oldenburg, Oldenburg, Germany |
| ORCID | (see UOL profile) |
| Institutional email | **`nils.strodthoff@uni-oldenburg.de`** *(verified 2026-05-01 via arXiv 2211.07579 byline as corresponding author; UOL email format pattern `First.Last@uni-oldenburg.de` confirmed independently)*. |
| Verification URL | https://arxiv.org/pdf/2211.07579 (corresponding-author line); https://uol.de/en/ai4health (Head of Division: Prof. Dr. Nils Strodthoff) |
| Expertise rationale | Strodthoff leads the AI4Health group at U Oldenburg and is the first author of *Deep Learning for ECG Analysis: Benchmarks and Insights from PTB-XL* (IEEE JBHI 2021), a reference work in ML on biomedical time series. He is also a co-author on the 2025 Bench et al. systematic UQ-on-PPG paper alongside Charlton — making him an independent second voice on whether TinyDCS's UQ design choices are state-of-the-art. His combined expertise in interpretable/explainable ML and uncertainty quantification on physiological signals matches the manuscript's core methodology. |
| Representative work | Strodthoff N, Wagner P, Schaeffter T, Samek W. *Deep Learning for ECG Analysis: Benchmarks and Insights from PTB-XL.* IEEE J Biomed Health Inform 25, no. 5 (2021): 1519–1528. https://doi.org/10.1109/JBHI.2020.3022989 |

---

## Editorial Manager portal entry — copy-paste table

For each candidate, EM typically requires Title, First name, Last name, Email, Institution, and a 1–2 sentence rationale. Use the table below.

| # | Title | First | Last | Institution | Email (verified 2026-05-01) | Rationale (≤ 2 sentences) |
|---|---|---|---|---|---|---|
| 1 | Dr | Peter H. | Charlton | Nokia Bell Labs Cambridge / U Cambridge (Public Health) | pete@oxon.org | UQ for wearable biomedical signals incl. conformal calibration on PPG (2025); direct overlap with TinyDCS calibration methodology. |
| 2 | Prof | Esther | Rodriguez-Villegas | Imperial College London (EEE) | e.rodriguez@imperial.ac.uk | TinyML / MCU-class ML for healthcare wearables; her IEEE Access review surveys exactly TinyDCS's deployment regime. |
| 3 | Prof | Francesco | Conti | University of Bologna (DEI) | f.conti@unibo.it | Edge AI / TinyML for biosignals on GAP9-class MCUs; recent BioTrain paper covers the same sub-MB sub-50 mW regime. |
| 4 | Prof | Allan Peter | Engsig-Karup | Technical University of Denmark (DTU Compute) | apek@dtu.dk | Conformal prediction with gradient-boosting backbones in clinical risk; scientific ML and uncertainty-aware modelling. |
| 5 | Prof | Nils | Strodthoff | Carl von Ossietzky Universität Oldenburg (Dept. Health Services Research) | nils.strodthoff@uni-oldenburg.de | Interpretable / explainable ML on biomedical time series; co-author on 2025 systematic UQ-on-PPG paper. |

---

## Geographic and conflict-of-interest sanity check

| Candidate | Country | Same institution as authors? | Co-authored with authors (3y)? | On CMPB editorial board? | Notes |
|---|---|---|---|---|---|
| Charlton | UK | No | No | No | Shifted Cambridge → Nokia Bell Labs Mar 2025 |
| Rodriguez-Villegas | UK | No | No | No | Imperial profile email confirmed |
| Conti | Italy | No (Bologna ≠ Turin) | No | No | EIC is at Polytechnic of Turin; Conti at U Bologna — independent institutions |
| Engsig-Karup | Denmark | No | No | No | DTU email confirmed |
| Strodthoff | Germany | No | No | No | UOL faculty page confirmed |

All 5 candidates are based in Europe with no shared institution with the Colombian Aerospace Force authors. All have published in the last 5 years on at least one of the four topical pillars. None is on the published CMPB editorial board as of the audit date.

---

## Verification record (2026-05-01)

All five emails were verified against primary sources on 2026-05-01:

| # | Reviewer | Email | Primary verification source |
|---|---|---|---|
| 1 | Charlton | pete@oxon.org | Personal lab homepage Contact section: https://peterhcharlton.github.io/#contact |
| 2 | Rodriguez-Villegas | e.rodriguez@imperial.ac.uk | Imperial College London faculty profile: https://profiles.imperial.ac.uk/e.rodriguez/professional |
| 3 | Conti | f.conti@unibo.it | ACM DL byline (FractalSync 2025) + HWPE-doc maintainer line |
| 4 | Engsig-Karup | apek@dtu.dk | DTU faculty profile: https://www.dtu.dk/english/person/allan-peter-engsig-karup |
| 5 | Strodthoff | nils.strodthoff@uni-oldenburg.de | arXiv 2211.07579 corresponding-author line; UOL AI4Health page (Head of Division) |

If more than ~30 days have elapsed before submission, re-confirm each at the listed source. Personal Gmail / Yahoo / Hotmail addresses are auto-rejected by Editorial Manager.

**Back-up candidates** (in case any of the above is unavailable):
- Davide Rossi, U Bologna DEI (TinyML / PULP) — verify at unibo.it directory
- Andrew Thompson, National Physical Laboratory UK (UQ on biosignals; co-author on Bench et al. 2025) — verify at npl.co.uk
- Yuan-Ting Zhang, Hong Kong Polytechnic University (wearable BP / cardiovascular AI) — verify via institutional profile
