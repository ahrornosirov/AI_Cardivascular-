# Development-only calibration experiment plan v1

**Written before running the calibration comparison.** The original logistic baseline and fixed development-only model comparison have already been examined. The 2007-2008 temporal outcome labels were inspected for the first logistic baseline, so that cycle is not a wholly unseen final test. This calibration experiment does not load or score its outcomes.

## Research question

Does sigmoid or isotonic calibration improve the **10-year cardiovascular mortality** probabilities from the fixed logistic baseline in the 1999-2006 NHANES development cohort (8,902 people, 274 events)? The model inputs, preprocessing, logistic hyperparameters, outer five stratified folds, and random seed remain unchanged.

## Methods fixed before fitting

Compare three sets of out-of-fold development predictions: the original logistic probabilities, sigmoid calibration, and isotonic calibration. For each outer five-fold training subset, fit the calibrator with a separate three-fold stratified cross-validation (`random_state=20261007`) and `CalibratedClassifierCV(ensemble=False)`. The outer fold is predicted only by an estimator and calibrator fitted without that fold. All preprocessing is inside the base model pipeline and refit inside training folds.

Report AUROC, AUPRC, Brier score, calibration intercept and slope, mean predicted risk, observed event rate, and decile calibration plots. Use paired person-level bootstrap intervals for Brier differences versus the original model. These preliminary intervals condition on the fixed out-of-fold predictions and do not account for model-fitting uncertainty or NHANES survey design.

## Decision rule for the web demo

Keep the original logistic probability unless a calibrated candidate has a lower Brier score with a paired 95% bootstrap interval for the difference entirely below zero **and** improves calibration intercept and slope jointly toward 0 and 1. If both qualify, choose the lower Brier score; if nearly tied, prefer sigmoid because it is simpler and preserves ranking. Even if a method qualifies here, describe it as development-selected until independently evaluated; do not claim individual clinical accuracy.

The Brier score mixes discrimination and calibration, so the plot, intercept and slope are essential to the decision. Isotonic can overfit, especially with few events. The web form does not show a low/medium/high category or confidence interval from this experiment alone.

## Sources

- [scikit-learn probability calibration guide](https://scikit-learn.org/stable/modules/calibration.html)
- [CalibratedClassifierCV documentation](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html)
