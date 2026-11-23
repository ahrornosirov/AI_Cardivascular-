# Development-only model comparison plan v1

**Written 6 October 2026 before fitting the two new candidate models.** The fixed logistic-regression baseline and its 2007-2008 temporal result were already inspected. This comparison uses only the 1999-2006 development cohort. It cannot restore the later cycle to a wholly unseen final test set.

## Question and data

Can a conservative tree model improve prediction of **10-year cardiovascular mortality** over the existing logistic baseline? Use the same 8,902 development participants, 274 events, eight baseline predictors, and five stratified folds (`random_state=20261006`). The later 2007-2008 cycle is not loaded or scored by this script.

The script reads predictor columns from the cohort file and reads development outcome labels from `results/baseline_development_predictions.csv`, produced by `scripts/train_baseline.py`. This keeps evaluation outcome labels out of the comparison process.

## Fixed candidate models

All candidates use training-fold median imputation for five numeric variables, most-frequent imputation for the three recorded categorical/binary variables, one-hot encoding, and numeric standardization. The entire processor is refit in every fold. These fixed settings are a first comparison, not an exhaustive hyperparameter search.

| Candidate | Fixed settings | Reason |
| --- | --- | --- |
| Logistic regression | Existing L2 baseline; `C=1.0`, no class weighting | Transparent reference |
| Random forest | 300 trees; maximum depth 6; minimum leaf size 20; `max_features=sqrt`; no class weighting | Limits very small leaves with only 274 events |
| Histogram gradient boosting | 200 iterations; learning rate 0.05; maximum 7 leaves; minimum leaf size 40; L2 regularization 1.0; no early stopping | A conservative boosted-tree comparator available in scikit-learn without another dependency |

XGBoost and LightGBM remain possible future implementations, but the current comparison uses scikit-learn's histogram gradient boosting. This change does not change the research question or the model family. Adding another library is not needed to learn whether a boosted tree improves this cohort's development-fold results.

## Analysis and decision rule

Produce one out-of-fold probability per development participant for each candidate using identical folds. Report event count/prevalence, AUROC, AUPRC, Brier score, calibration intercept and slope. Compare Brier score first because the proposed output is a probability; consider AUROC and AUPRC alongside it. No risk threshold, category, SHAP display, or clinical claim is selected from this run.

Any later calibration method must be trained and chosen using disjoint development data. We will not select the final clinical model from the temporal evaluation cycle. If results are close, prefer the simpler model. The analysis is unweighted and its metrics describe this constructed sample; NHANES design-aware inference remains open.
