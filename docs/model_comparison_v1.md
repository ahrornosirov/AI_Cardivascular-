# Development-only model comparison v1

**Target:** 10-year cardiovascular mortality. **Data:** NHANES 1999-2006 development cohort only, 8,902 people and 274 events. **Status:** preliminary research comparison; not clinical validation. The 2007-2008 evaluation outcomes were not loaded by this run.

The settings and decision rule were fixed in [model_comparison_plan_v1.md](model_comparison_plan_v1.md) before the two new models were fit. All values below come from five-fold out-of-fold probabilities with fold-fitted preprocessing. The same participants and folds were used for every model.

| Candidate | AUROC | AUPRC | Brier | Calibration intercept | Calibration slope |
| --- | ---: | ---: | ---: | ---: | ---: |
| Logistic regression | 0.777 | 0.124 | 0.02841 | -0.125 | 0.958 |
| Random forest | 0.776 | 0.119 | 0.02855 | 0.716 | 1.233 |
| Histogram gradient boosting | 0.765 | 0.118 | 0.02866 | -0.499 | 0.824 |

## Paired differences from logistic regression

Positive Brier difference means a worse probability score; positive AUROC difference means better ranking. These person-level bootstrap intervals hold the out-of-fold predictions fixed. They omit model-fitting uncertainty and NHANES survey strata, clusters and weights.

| Challenger | Brier difference (95% interval) | AUROC difference (95% interval) |
| --- | ---: | ---: |
| Random forest | +0.000140 (-0.000138 to +0.000420) | -0.0013 (-0.0154 to +0.0125) |
| Histogram gradient boosting | +0.000253 (-0.000182 to +0.000619) | -0.0121 (-0.0277 to +0.0031) |

The lowest development-fold Brier score in this fixed comparison is for **Logistic regression**. This is a preliminary sample-level result; compare discrimination and calibration as well before selecting a final research model. Small score differences may not be meaningful. No clinical threshold or risk category is set.

Next: assess whether sigmoid or isotonic calibration improves development-only predictions using disjoint fitting and calibration folds. Any temporal-cycle comparison must disclose that the fixed logistic baseline's temporal result was already seen. A wholly independent cohort is still needed for stronger confirmation.

These unweighted metrics do not account for NHANES sampling design. The cohort has few target events for flexible modeling, and public mortality fields include privacy-protecting substitutions. Do not use these probabilities for patient care.
