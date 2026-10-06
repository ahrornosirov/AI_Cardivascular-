# Cohort feasibility report v1

**Generated:** 6 October 2026 from the official NHANES 1999–2008 XPT files and CDC 2019 public-use linked mortality files. The person-level data are in ignored `data/processed/cohort_v1.csv`; [cohort_feasibility.json](cohort_feasibility.json) contains the machine-readable audit. Reproduce with `/opt/anaconda3/bin/python3 scripts/build_cohort.py` after running the download scripts. This is a feasibility analysis, not a trained model or a population-weighted risk estimate.

## Cohort flow

| Stage | 1999–2000 | 2001–2002 | 2003–2004 | 2005–2006 | 2007–2008 |
| --- | ---: | ---: | ---: | ---: | ---: |
| All survey records | 9,965 | 11,039 | 10,122 | 10,348 | 10,149 |
| Examined, age 40–79 | 2,553 | 2,782 | 2,637 | 2,576 | 3,474 |
| Eligible for mortality linkage | 2,550 | 2,779 | 2,630 | 2,576 | 3,473 |
| Known ten-year outcome | 2,550 | 2,778 | 2,630 | 2,576 | 3,473 |
| No reported prior CVD | 2,179 | 2,407 | 2,187 | 2,198 | 2,965 |
| Confirmed no prior CVD; final cohort | 2,157 | 2,383 | 2,178 | 2,184 | 2,941 |
| Cardiovascular deaths within ten years | 80 | 69 | 65 | 60 | 87 |

The first four cycles form the development set: **8,902 people, 274 events (3.08%)**. The 2007–2008 temporal evaluation set has **2,941 people, 87 events (2.96%)**. This split is set before model selection; evaluation data must not be used to select features, hyperparameters, calibration method, or thresholds.

## Predictor completeness

| Field | Development missing | Evaluation missing |
| --- | ---: | ---: |
| Age, NHANES recorded gender | 0% | 0% |
| Systolic blood pressure | 4.46% | 4.08% |
| BMI | 2.27% | 1.36% |
| Total cholesterol | 5.30% | 5.27% |
| HDL cholesterol | 5.30% | 5.27% |
| Current smoking | 0.12% | 0.10% |
| Diabetes | 1.66% | 1.90% |

All eight predictors are observed in **7,843 development people (220 events)** and **2,611 evaluation people (70 events)**. Therefore, complete-case analysis would discard 54 development events and 17 evaluation events. Imputation should be evaluated inside the development folds, with complete cases as a sensitivity analysis.

## Data-quality and evaluation implications

- The observed maxima include systolic BP 266 mmHg, BMI 130.21 kg/m², total cholesterol 727 mg/dL, and HDL 188 mg/dL. These are audit flags, not automatic exclusions. Review source records and define clinically justified validation rules before training or building the input form.
- The temporal evaluation set has only 87 events. Overall AUROC and calibration can be estimated, but intervals may be wide. Age-by-recorded-gender cells in that set have only 6–28 events; subgroup performance should be exploratory and reported with uncertainty rather than as strong fairness conclusions.
- CDC documents HDL assay changes over these cycles. A change between development and evaluation could reflect measurement methods as well as population differences.
- The 2019 public-use mortality file contains privacy-protecting substitutions for some follow-up times and causes. Claims about exact individual risk or clinical use require stronger validation. This project has no hospital or restricted-use data access, so such claims are outside its scope.
- NHANES has a complex sample design. The raw cohort retains sample weights, strata, and PSU identifiers; population-level estimates and interval methods need a documented design-aware analysis plan.

## Next research gate

Freeze the cohort definition and eight core predictors after review of the extreme values, HDL harmonization, and the limited held-out event count. Then write the prespecified model and evaluation plan before fitting any model.
