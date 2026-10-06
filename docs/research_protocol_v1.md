# Research Protocol v1

**Status:** Target confirmed by the project owner on 6 October 2026; cohort feasibility audit completed the same day. This protocol is ready for team review before model fitting. Do not report clinical performance or publish a risk calculator from this protocol alone. The title and traceability below were checked against the team's Week 3 submission dated 2 October 2026.

## 1. Research aim and traceability

**Approved project title:** AI-Based Cardiovascular Risk Assessment System Using Explainable Machine Learning.

**Study-specific outcome subtitle for reports:** Development and evaluation of an explainable model for 10-year cardiovascular mortality. This narrows the measured outcome without changing the team's approved project title.

**General objective in the submission:** “To design, implement, and evaluate an AI-based cardiovascular risk assessment system that integrates patient data, estimates risk, and explains its outputs.”

| Submitted research problem | Submitted research question | Submitted specific objective | Research work product |
| --- | --- | --- | --- |
| RP1: “Clinical and lifestyle data in varied formats can produce incomplete or inconsistent model inputs.” | RQ1: “How can data validation and preprocessing integrate clinical and lifestyle factors into reliable model inputs?” | RO1: “To build a data validation and preprocessing pipeline and measure input completeness.” | Dataset dictionary; schema and range checks; missingness, exclusion, and imputation reports; reproducible pipeline |
| RP2: “An AI model may classify risk poorly or output unreliable risk probabilities.” | RQ2: “How well does the AI model discriminate and calibrate cardiovascular risk on held-out data?” | RO2: “To train and evaluate a risk model using held-out data, discrimination, and calibration.” | Prespecified model comparison; internal cross-validation; untouched evaluation set; AUROC, AUPRC, calibration, Brier score, intervals |
| RP3: “Opaque predictions do not show which recorded factors shaped an individual risk result.” | RQ3: “How can explainable AI show the factors driving each risk estimate and communicate uncertainty?” | RO3: “To implement patient-level explanations and uncertainty displays, then assess their clarity.” | Model explanation study; missing-information display; uncertainty method tied to actual evaluation; user comprehension review |

## 2. Prediction task

- **Target population:** Examined adults ages 40–79 in the US NHANES baseline survey, eligible for mortality linkage and with a known ten-year outcome. The primary-prevention cohort excludes any self-reported prior congestive heart failure, coronary heart disease, angina, myocardial infarction, or stroke and requires definite “no” answers to all five questions. The cohort report records the exclusions.
- **Prediction time:** The baseline NHANES interview/examination. All predictors must be measured at or before that point.
- **Outcome:** Death from diseases of the heart or cerebrovascular disease within 120 months after the baseline examination, based on the CDC linked mortality file's underlying-cause categories `001` and `005` and follow-up time `PERMTH_EXM`.
- **Horizon:** 10 years. Use the exact label **“10-year cardiovascular mortality risk.”** Do not call this incident CVD, nonfatal CVD, heart-disease diagnosis, or a general CVD-event model.
- **Estimand:** Probability of cardiovascular death within ten years under the observed mix of competing causes of death. A non-cardiovascular death before ten years is a non-event for this binary ten-year outcome; do not treat it as a missing outcome. Exclude or otherwise account for people whose status at ten years cannot be determined.
- **Setting:** Retrospective model development and evaluation. The future web form is a research demonstration and must describe its US source population and limitations.

## 3. Data source and decision gate

**Selected source for the research prototype:** NHANES 1999–2008 examination, laboratory, demographic, and questionnaire data linked by `SEQN` to the CDC 2019 public-use Linked Mortality Files. The baseline cycles 1999–2008 have potential ten-year follow-up through 31 December 2019. The public-use mortality data contain privacy-protecting substitutions for some follow-up times and causes of death, which limits individual-risk and calibration claims. The team should seek restricted-use verification if publication or clinical translation is intended.

**Why this source:** It has a documented time horizon and a clearly defined fatal outcome, and its public files can be reproduced. The NHLBI Framingham *teaching* dataset is suitable for instruction but explicitly unsuitable for publication. The full Framingham cohort has incident CVD outcomes, but access requires ethics review and approval; it is a possible later replacement if the team obtains access.

**Feasibility checks before training:**

1. **Completed:** Record exact CDC file URLs and checksums in the source manifest; downloaded 6 October 2026.
2. **Completed:** Harmonize eight baseline predictors across all selected NHANES cycles and document units and collection timing.
3. **Completed:** Count eligible participants, exclusions, and events; inspect evaluation and subgroup event counts.
4. **Open:** Define the analysis response to privacy substitutions and the NHANES complex survey design, including uncertainty and weighting.
5. **Open:** Review extreme values and whether 87 held-out events are sufficient for the claims planned in the paper.

The preliminary mortality-file audit is in [dataset_feasibility.md](dataset_feasibility.md). The joined primary-prevention cohort and its flow are in [cohort_report_v1.md](cohort_report_v1.md), with variable definitions in [data_dictionary_v1.md](data_dictionary_v1.md).

## 4. Candidate predictors

The eight core predictors measured at baseline are age, NHANES recorded gender category, systolic blood pressure, body mass index, total cholesterol, HDL cholesterol, current smoking, and self-reported diabetes. Antihypertensive treatment and physical activity are deferred until their cross-cycle coding is justified. Never derive a predictor from follow-up, death certificate, or outcome fields.

Represent missing values explicitly. Define plausible input ranges from source documentation and clinical review. Show missingness and invalidity by variable and cycle. Fit all imputation, scaling, and encoding steps on the development folds only. Compare complete-case and prespecified imputation approaches as a sensitivity analysis.

## 5. Study design and models

- **Development:** NHANES 1999–2006: 8,902 people and 274 target events after cohort exclusions. Use cross-validation for feature processing, tuning, and model selection; keep each participant within a single fold.
- **Temporal evaluation:** NHANES 2007–2008: 2,941 people and 87 target events. Do not inspect it for choosing hyperparameters, thresholds, calibration methods, or the winning model.
- **Models:** Logistic regression as the transparent baseline; random forest; one gradient-boosted tree implementation if event count supports it. Predefine a simple prevalence or conventional-score comparator only if its endpoint and population are compatible.
- **Calibration:** Fit sigmoid or isotonic calibration only inside development data using disjoint folds. Select one method through cross-validation. Evaluate its final performance once on the temporal set.
- **Outcome balance:** Report event counts and prevalence before choosing model complexity or subgroup comparisons. The preliminary public mortality-file count is about 4–5% before study exclusions.
- **Survey design:** Record NHANES sampling weights, strata, and primary sampling units. Seek statistical review of design-aware estimates and uncertainty; distinguish participant-level predictive performance from population-representative estimates. Follow the CDC rules for combining cycles, including the special 1999–2002 weighting requirement.

## 6. Prespecified evaluation

Report denominators, event counts, point estimates, and 95% intervals where supportable.

| Domain | Measures / output |
| --- | --- |
| Discrimination | AUROC, AUPRC, and event prevalence |
| Calibration | Calibration curve, calibration intercept and slope, Brier score, observed versus predicted ten-year risk |
| Decision thresholds | Sensitivity, specificity, and predictive values only at thresholds justified before test-set inspection; no clinical action threshold is assumed |
| Missingness | Percent missing, invalid, imputed, and complete-case; performance sensitivity across handling strategies |
| Subgroups | Age and NHANES recorded gender groups as exploratory analyses only; the held-out age-by-gender cells contain just 6–28 events |
| Robustness | Bootstrap intervals where appropriate; cycle-level and complete-case sensitivity analyses |

Do not present a fabricated individual “confidence” score or interval. A prediction interval, model uncertainty summary, or data-completeness warning requires a defined method and empirical checking before it appears in the UI. SHAP values describe how the model produced a prediction, not causal effects or treatment benefits. Any percentage-point contribution shown in the UI must be computed on the calibrated probability scale or described more carefully.

## 7. Prototype output

Only after evaluation, the web prototype may accept validated inputs and show the model estimate, exact outcome/horizon, source population, factor explanations, missing-input status, and a plain-language research-use notice. Low/medium/high categories require thresholds chosen for a stated research purpose and checked for calibration; do not copy thresholds from a different endpoint or region.

WHO Central Asia charts are relevant literature context, but a US cardiovascular-**mortality** model cannot be directly compared to their broader regional CVD-event risk without matching population and endpoint.

## 8. Reporting and reproducibility

Use the 27-item TRIPOD+AI checklist to plan and report the study. Preserve code, dependency versions, raw-data provenance, exclusion flow, preprocessing fits, random seeds, parameter search, model artifacts, and evaluation outputs. Publish data only as permitted by its source. Record ethical review and data-use requirements before any restricted-data work.

## 9. Open decisions for team review

1. Review whether the 87-event temporal evaluation set supports the intended precision; avoid strong subgroup claims.
2. Confirm publication ambitions and whether restricted data or institutional ethics approval are feasible.
3. Clinically review the extreme baseline values and the planned input-validation ranges before model fitting.
4. Specify the survey-design and combined-weight analysis strategy before population-level claims.
5. Confirm whether the final demo is for clinicians, students, or researchers; wording and comprehension testing depend on this.

## Sources

- [CDC: public-use linked mortality files and privacy alterations](https://www.cdc.gov/nchs/linked-data/mortality-files/index.html)
- [CDC: 2019 public-use linked mortality file codebook](https://www.cdc.gov/nchs/data/datalinkage/public-use-linked-mortality-files-data-dictionary.pdf)
- [CDC: public mortality files and official read-in programs](https://ftp.cdc.gov/pub/Health_Statistics/NCHS/datalinkage/linked_mortality/)
- [CDC: NHANES weighting guidance](https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx)
- [NHLBI: Framingham teaching data and publication restriction](https://biolincc.nhlbi.nih.gov/teaching/)
- [NHLBI: full Framingham cohort access and ethics requirements](https://biolincc.nhlbi.nih.gov/studies/framcohort/)
- [TRIPOD+AI statement](https://www.bmj.com/content/385/bmj-2023-078378)
- [WHO cardiovascular risk charts and regions](https://www.who.int/news-room/detail/02-09-2019-who-updates-cardiovascular-risk-charts)
