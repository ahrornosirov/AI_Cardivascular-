# Logistic-regression baseline: preliminary research result

**Date:** 6 October 2026. **Source:** Public NHANES 1999–2008 baseline data linked to the CDC 2019 public-use mortality files. **Target:** Cardiovascular death within ten years. This model is for the university research prototype and synthetic examples; it is not clinically validated.

The analysis followed [model_plan_v1.md](model_plan_v1.md): five stratified development folds, fold-fitted imputation and scaling, no class weighting, and fixed logistic regularization. The model was then refit on the 1999–2006 development cohort and evaluated once on the 2007–2008 cohort. Exact numbers are in [baseline_metrics.json](baseline_metrics.json); the [calibration figure](figures/baseline_calibration.png) shows observed and predicted risk by probability decile.

| Metric | Development, out-of-fold | 2007–2008 held-out |
| --- | ---: | ---: |
| Participants | 8,902 | 2,941 |
| Cardiovascular deaths within ten years | 274 | 87 |
| Outcome prevalence | 3.08% | 2.96% |
| AUROC | 0.777 (95% bootstrap interval 0.749–0.803) | 0.778 (0.738–0.819) |
| AUPRC | 0.124 (0.097–0.160) | 0.080 (0.059–0.114) |
| Brier score | 0.0284 (0.0255–0.0315) | 0.0281 (0.0231–0.0340) |
| Calibration intercept | −0.125 | −0.223 |
| Calibration slope | 0.958 | 0.926 |

The bootstrap intervals resample people while holding predictions fixed. They do not account for NHANES strata, clusters, survey weights, or model-fitting uncertainty, and should be read as preliminary sample-level precision checks. Calibration intercept and slope are diagnostic fits to the fixed predictions; they were not used to modify or recalibrate this model.

The held-out cycle has now been inspected for this baseline. No model choices were changed in response. Further model and calibration comparisons must be selected from development-only cross-validation under a written plan; the 2007–2008 cycle can then be reported as a transparent temporal comparison, but it is no longer a wholly unseen final validation set. A later independent cohort would be needed for stronger confirmation.

The AUPRC should be read alongside the 2.96% event prevalence. The unweighted results describe this constructed NHANES sample, not a general population risk estimate or expected performance for an individual patient in Uzbekistan. Public-use follow-up and cause-of-death substitutions, the small held-out event count, HDL assay changes, and the absence of local external validation remain material limitations.
