# Journal Scout Report: TinyDCS Manuscript

**Date:** 2026-05-01
**Manuscript:** *TinyDCS: An edge-deployable machine-learning surrogate of the ADRAC altitude-decompression-sickness risk model with continuous-exposure covariates and calibrated uncertainty*
**Authors:** Diego Malpica, MD · Marian Farfán, MD (Colombian Aerospace Force)
**Type:** Original Research (prediction model / methodology)
**Word count:** ~6,200 (body) + 250 (abstract)
**Author context:** Colombia = Research4Life Group B (50% APC discount tier, NOT 100% waiver). No external funding.

---

## 1. Field Inference & Scoring Dimensions

| Dimension | Inference |
|---|---|
| **Primary field** | Aerospace / aviation medicine |
| **Subfield** | Altitude physiology, decompression sickness risk modeling |
| **Methodology** | Machine learning surrogate, conformal prediction, edge AI, hierarchical Bayesian personalization |
| **Reporting guideline** | TRIPOD + TRIPOD-AI extension |
| **Word cap risk** | None (~6,200 is comfortable for most journals; >10,000 would flag) |
| **Scope tension** | High: aerospace medicine journals may underweight ML methodology; ML/AI journals may underweight aerospace domain significance |

---

## 2. Top 10 Candidate Journals (Ranked)

| Rank | Journal | Publisher | Quartile | APC (USD) | Hybrid this OA? | Scope match | Word cap | Indexing | Score |
|---|---|---|---|---|---|---|---|---|---|
| **1** | **npj Microgravity** | Nature Portfolio | **Q1** | ~$3,590 (OA only) | N/A (gold OA) | 9/10 | ~6,000 | Scopus, WOS, PubMed | **91** |
| **2** | **Life Sciences in Space Research** | Elsevier | **Q1** | $3,190 (OA) / **$0 (hybrid)** | **YES** | 9/10 | ~8,000 | Scopus, WOS | **88** |
| **3** | **Aerospace Medicine and Human Performance** | AsMA (self) | **Q4** | ~$0 (hybrid) / ~$3,000 (OA) | **YES** | 10/10 | ~6,000 | Scopus, WOS, PubMed | **85** |
| 4 | PLOS Computational Biology | PLOS | Q1 | $3,043 | N/A (gold OA) | 7/10 | ~7,500 | Scopus, WOS, PubMed | 78 |
| 5 | Frontiers in Physiology | Frontiers | Q1 | ~$2,950 | N/A (gold OA) | 7/10 | ~12,000 | Scopus, WOS, PubMed | 76 |
| 6 | JMIR mHealth and uHealth | JMIR | Q1 | ~$2,500 | N/A (gold OA) | 6/10 | ~7,000 | Scopus, WOS, PubMed | 72 |
| 7 | Aerospace (MDPI) | MDPI | Q2 | CHF 2,400 (~$2,600) | N/A (gold OA) | 6/10 | None | Scopus, WOS | 68 |
| 8 | BMC Medical Research Methodology | BMC | Q1 | ~$2,990 | N/A (gold OA) | 6/10 | ~10,000 | Scopus, WOS, PubMed | 66 |
| 9 | BMJ Open | BMJ | Q2 | ~$2,000 | N/A (gold OA) | 5/10 | ~8,000 | Scopus, WOS, PubMed | 62 |
| 10 | Digital Health (SAGE) | SAGE | Q2-Q3 | ~$2,000 | Hybrid available | 5/10 | ~6,000 | Scopus, ESCI | 58 |

### Scoring rubric (0–100)

- **Scope fit** (0–20): Does the journal explicitly publish altitude physiology, DCS, ML surrogates, or wearable/edge AI?
- **Indexing** (0–15): Scopus + WOS + PubMed triple = 15; dual = 10; single = 5.
- **Quartile / impact** (0–20): Q1 = 20, Q2 = 15, Q3 = 10, Q4 = 5.
- **APC feasibility for Group B** (0–20): Free hybrid = 20; diamond OA = 20; 50% waiver → ~$1,500 = 12; full APC = 5.
- **Acceptance realism** (0–15): Known AsMA-friendly = 15; plausible = 10; long shot = 5.
- **Speed / pragmatism** (0–10): Fast track / no major revision history = 10; moderate = 7; slow = 4.

---

## 3. Top-3 Deep Dive

### #1 — npj Microgravity (Nature Portfolio)

**Fit rationale:** This is the highest-impact venue that explicitly serves the space-medicine and aerospace-physiology community. Published by Nature Portfolio, it carries Q1 status (SJR ~1.045, IF ~4.4) and is indexed in Scopus, WOS, and PubMed. The journal's scope includes "scientific research needed to develop advanced exploration technologies and processes" and "effects of space flight conditions on human bodies" — directly encompassing altitude-decompression physiology and the operational-need framing of the TinyDCS abstract. The edge-deployment angle (100 KB model, 2.44 µs inference) is a genuine technology-forward contribution that fits the journal's emphasis on exploration-enabling technologies.

**Tradeoff:** Fully open-access gold model means no hybrid subscription path. APC is estimated at ~$3,590 USD. As a Research4Life Group B author, a 50% waiver (if granted) would bring the net to ~$1,795 — still substantial without external funding. Nature Portfolio's waiver policy is not automatic; it requires application and case-by-case approval. If the waiver is denied, this becomes the most expensive option.

**Risk:** The editorial board may question whether a model validated on synthetic/audited grid data (rather than prospective hypobaric-chamber data) meets the empirical bar for a Nature-family journal. The abstract already flags this limitation honestly; a cover letter should stress that this is a *methodology and engineering* contribution (surrogate + calibration + edge deployment), not a clinical validation study. Paper 3 is the prospective-validation follow-up.

**Indexing:** Scopus, Web of Science, PubMed. Strong.

---

### #2 — Life Sciences in Space Research (Elsevier)

**Fit rationale:** Elsevier's dedicated space-life-sciences journal, Q1 in Scimago (IF ~2.8, SJR 0.666). The scope explicitly includes "effects of space flight conditions on human bodies" and "animal models in space research." Altitude-decompression sickness is squarely within the human-spaceflight risk portfolio. The journal is hybrid: you can submit non-open-access at **zero APC** — the most underused and important path for unfunded Group B authors. Only color figures or extra tables incur charges. This is the most financially responsible choice that does not sacrifice indexing or field relevance.

**Tradeoff:** Lower impact factor than npj Microgravity, but still Q1 in Scimago. The journal's readership is narrower (space-life sciences specialists) than AMHP's (operational aerospace medicine), which may reduce operational-uptake visibility. However, the ML methodology is more likely to be reviewed seriously here than at a purely clinical journal.

**Risk:** Elsevier hybrid submission is functionally a subscription article — readers without institutional access will not see it. If open-access dissemination is a priority (e.g., for policy uptake by the Colombian Air Force or international partners), this is a genuine limitation. The solution is to deposit the accepted manuscript in an institutional repository or preprint server (arXiv, bioRxiv) under the embargo window.

**APC note:** If you later decide you need OA, the APC is $3,190; as a Research4Life Group B author, Elsevier typically grants a 50% discount on fully OA articles, bringing the net to ~$1,595.

**Indexing:** Scopus, Web of Science. Strong.

---

### #3 — Aerospace Medicine and Human Performance (AMHP)

**Fit rationale:** The journal you already cite in your manuscript header. AMHP is the flagship of the Aerospace Medical Association — the exact professional community that uses ADRAC operationally. The scope match is perfect (10/10): altitude DCS, prebreathe protocols, wearable computing in aviation, and operational risk models are all published here regularly. It is a hybrid journal: non-OA submission is free. For a Colombian military-affiliated author, this is the most natural home, and the editorial board will immediately understand the operational significance of a 95 KB edge-deployable ADRAC surrogate.

**Tradeoff:** Q4 in Scimago (IF ~0.9, SJR 0.244). This is the lowest-impact venue in the top 3. If your career trajectory or institutional evaluation rewards impact factor, this is a real cost. The low IF reflects the journal's small, specialized readership, not its quality — but metrics-driven committees may not make that distinction.

**Risk:** AMHP's peer-review pool is clinician-heavy. Reviewers may not have deep expertise in conformal prediction, zero-inflated modeling, or ONNX quantization. The TRIPOD+AI checklist (already prepared) will help, but you should anticipate reviewer requests to simplify or remove methodological detail. The 6,200-word count is comfortable for AMHP's typical research article length.

**APC note:** Hybrid = free to publish non-OA. Color figures incur extra charges (~$300–500). If OA is desired, the APC is approximately $3,000.

**Indexing:** Scopus, Web of Science, PubMed. Triple-indexed despite low IF.

---

## 4. The Q1 vs. Acceptance-Rate Tradeoff (Explicit)

| Axis | Conservative (high acceptance, lower impact) | Ambitious (lower acceptance, higher impact) |
|---|---|---|
| **Journal** | AMHP | npj Microgravity |
| **Acceptance probability** | High (home field, known readership) | Moderate (Nature-family bar, synthetic-data limitation) |
| **Impact factor** | ~0.9 | ~4.4 |
| **Cost** | $0 (hybrid) | ~$1,795 (with 50% waiver) or ~$3,590 (full) |
| **Reviewer expertise risk** | Low clinical / high operational | High scientific / moderate operational |
| **Best if** | You want guaranteed acceptance and zero cost | You want maximum visibility and can absorb APC risk |

**The balanced middle path:** Life Sciences in Space Research gives you Q1 impact, zero cost (hybrid), and a reviewer pool that understands both space physiology and technology-forward methods. It is the compromise that minimizes downside while preserving upside.

---

## 5. APC & Funding Context for Colombia

| Publisher | Research4Life Group B Policy | Effective APC (OA, post-discount) |
|---|---|---|
| Elsevier | 50% discount on fully OA articles | ~$1,595 (Life Sciences in Space Research) |
| Nature Portfolio | Case-by-case waiver application | Unpredictable; assume full unless confirmed |
| PLOS | Fee assistance program (not automatic) | Unpredictable; Group B does NOT get automatic free OA |
| Frontiers | 45% discount for some countries | ~$1,623 |
| MDPI | Waiver application possible | Unpredictable |
| AsMA (AMHP) | No Research4Life program known | Hybrid = free; OA = ~$3,000 |

**Critical rule:** Colombia is Group B. Do not assume 100% waivers. Any gold-OA journal (npj, PLOS, Frontiers, MDPI, BMC) requires either paying the full APC or successfully negotiating a waiver — neither is guaranteed.

**Recommendation:** Unless you have secured an APC waiver in writing *before* submission, submit hybrid (non-OA) to **Life Sciences in Space Research** or **AMHP** for the first attempt. If rejected, use the reviews to strengthen the manuscript and reconsider a gold-OA venue with a waiver application.

---

## 6. Similar-Paper Scope Validation

Papers published in the last 3–5 years that validate scope fit:

| Paper | Venue | Relevance to TinyDCS |
|---|---|---|
| Yan et al. (2022) — *Machine Learning Methods to Predict Incidence Risk of Altitude Decompression Sickness* | IEEE CME Conference | Direct competitor: RF regression on ADRAC data. Not published in a journal — TinyDCS has a journal-ready advantage. |
| Wei et al. (2022) — *Using machine learning to determine the correlation between physiological and environmental parameters and the induction of acute mountain sickness* | BMC Bioinformatics | ML + altitude physiology published in a methods journal. Validates that ML methodology is acceptable in this domain. |
| Masum et al. (2025) — *AMS-HD: Hyperdimensional Computing for Real-Time and Energy-Efficient Acute Mountain Sickness Detection* | arXiv / ISCAS | Edge AI + altitude sickness, but conference venue. TinyDCS targets journal publication, which is a step up. |

**Observation:** No prior journal article has combined (a) altitude DCS, (b) ML surrogate, (c) conformal uncertainty, and (d) edge deployment in a single paper. This is a genuine gap that any of the top 3 journals could credibly fill.

---

## 7. Paper 2 (Hierarchical Bayesian Personalization) — Cross-Cutting Note

The Paper 2 scope document already lists three targets: PLOS Computational Biology (primary), Frontiers in Physiology (secondary), AMHP (tertiary). My analysis supports this ranking with one adjustment: **PLOS Computational Biology is an excellent methods fit for Paper 2** because the hierarchical Bayesian personalization is a pure methodology contribution validated on synthetic cohorts — exactly what PLOS Comp Biol publishes. The APC ($3,043) is a concern for unfunded Group B authors, but PLOS has a Publication Fee Assistance program that may reduce this further.

For Paper 2, the sequence should be:
1. **PLOS Computational Biology** (methodology primary)
2. **BMC Medical Research Methodology** (if PLOS rejects; similar methods scope, lower APC)
3. **Frontiers in Physiology** (if you want faster turnaround and are willing to pay OA)

AMHP is less suitable for Paper 2 because the clinical readership will not appreciate the hierarchical Bayesian methodology as deeply as a computational-biology audience.

---

## 8. Final Recommendation

For **Paper 1 (TinyDCS)**:

| Priority | Action |
|---|---|
| **1st choice** | Submit hybrid (non-OA) to **Life Sciences in Space Research** — zero cost, Q1, strong scope fit, balanced reviewer pool. |
| **2nd choice** | Submit hybrid (non-OA) to **AMHP** — zero cost, perfect scope, highest acceptance probability, lowest impact. |
| **3rd choice** | Apply for APC waiver + submit to **npj Microgravity** — highest impact, best visibility, but financial risk. |

For **Paper 2 (Hierarchical Bayesian Personalization)**:

| Priority | Action |
|---|---|
| **1st choice** | Apply for PLOS Publication Fee Assistance + submit to **PLOS Computational Biology**. |
| **2nd choice** | Submit to **BMC Medical Research Methodology** (check APC waiver policy for Group B). |

---

## 9. Next Steps

1. **Confirm hybrid submission intent** for Life Sciences in Space Research (no APC) vs. gold-OA intent (APC risk).
2. **Draft cover letter** emphasizing the operational gap (wearable-deployable DCS risk model) and the methodology novelty (zero-inflated conformal calibration).
3. **Verify TRIPOD+AI checklist** is complete — all flagged journals will expect it.
4. **Check Research4Life APC portal** for any 2026 policy updates before submission.
5. **Consider preprint deposit** on arXiv or bioRxiv before submission to establish priority and enable open access regardless of journal choice.

---

*Report generated by Journal Scout v2.0*
*Output: /root/repos/DCS/docs/papers/2026-05-01_journal-scout_tinydcs.md*
