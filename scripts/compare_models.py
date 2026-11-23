"""Compare three fixed models using development data only.

Read docs/model_comparison_plan_v1.md before changing model settings.
This script never loads evaluation outcomes and never scores evaluation cases.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from train_baseline import CATEGORICAL, FEATURES, NUMERIC, SEED, metrics, pipeline as logistic_pipeline

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "cohort_v1.csv"
RESULTS = ROOT / "results"
BASELINE_DEVELOPMENT = RESULTS / "baseline_development_predictions.csv"
REPORT = ROOT / "docs" / "model_comparison_v1.md"
DOCUMENTED_METRICS = ROOT / "docs" / "model_comparison_metrics.json"


def processor() -> ColumnTransformer:
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(drop="if_binary", handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([("numeric", numeric, NUMERIC), ("categorical", categorical, CATEGORICAL)])


def candidates() -> dict[str, Pipeline]:
    return {
        "Logistic regression": logistic_pipeline(),
        "Random forest": Pipeline([
            ("preprocess", processor()),
            ("model", RandomForestClassifier(
                n_estimators=300, max_depth=6, min_samples_leaf=20,
                max_features="sqrt", n_jobs=1, random_state=SEED,
            )),
        ]),
        "Histogram gradient boosting": Pipeline([
            ("preprocess", processor()),
            ("model", HistGradientBoostingClassifier(
                max_iter=200, learning_rate=0.05, max_leaf_nodes=7,
                min_samples_leaf=40, l2_regularization=1.0,
                early_stopping=False, random_state=SEED,
            )),
        ]),
    }


def paired_intervals(y: np.ndarray, baseline: np.ndarray, challenger: np.ndarray) -> dict[str, dict[str, object]]:
    """Person-bootstrap score differences, conditional on fixed OOF predictions."""
    rng = np.random.default_rng(SEED)
    boot = {"brier": [], "auroc": []}
    for _ in range(1000):
        index = rng.integers(0, len(y), size=len(y))
        observed = y[index]
        if observed.min() == observed.max():
            continue
        boot["brier"].append(
            brier_score_loss(observed, challenger[index]) - brier_score_loss(observed, baseline[index])
        )
        boot["auroc"].append(
            roc_auc_score(observed, challenger[index]) - roc_auc_score(observed, baseline[index])
        )
    return {
        "brier": {
            "difference": round(float(brier_score_loss(y, challenger) - brier_score_loss(y, baseline)), 6),
            "bootstrap_95pct": [round(float(v), 6) for v in np.quantile(boot["brier"], [.025, .975])],
        },
        "auroc": {
            "difference": round(float(roc_auc_score(y, challenger) - roc_auc_score(y, baseline)), 6),
            "bootstrap_95pct": [round(float(v), 6) for v in np.quantile(boot["auroc"], [.025, .975])],
        },
    }


def main() -> None:
    frame = pd.read_csv(DATA, usecols=["SEQN", "split_role", *FEATURES])
    development = frame.loc[frame.split_role == "development"].copy()
    labels = pd.read_csv(BASELINE_DEVELOPMENT, usecols=["SEQN", "target"])
    if labels.SEQN.duplicated().any() or development.SEQN.duplicated().any():
        raise ValueError("Duplicate participant identifier")
    development = development.merge(labels, on="SEQN", how="left", validate="one_to_one")
    if len(development) != 8902 or development.target.isna().any() or development.target.sum() != 274:
        raise ValueError("Development cohort does not match the prespecified plan")
    x = development[FEATURES]
    y = development.target.to_numpy(dtype=int)
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    summary = {}
    predictions = pd.DataFrame({"SEQN": development.SEQN, "target": y})
    for name, candidate in candidates().items():
        probability = cross_val_predict(candidate, x, y, cv=folds, method="predict_proba", n_jobs=1)[:, 1]
        if len(probability) != len(y) or not np.isfinite(probability).all():
            raise ValueError(f"Invalid out-of-fold probabilities: {name}")
        summary[name] = metrics(y, probability)
        predictions[name.lower().replace(" ", "_")] = probability
        print(name, json.dumps(summary[name]))

    RESULTS.mkdir(exist_ok=True)
    predictions.to_csv(RESULTS / "model_comparison_development_oof.csv", index=False)
    base = predictions.logistic_regression.to_numpy()
    differences = {
        name: paired_intervals(y, base, predictions[name.lower().replace(" ", "_")].to_numpy())
        for name in summary if name != "Logistic regression"
    }
    metrics_json = json.dumps({"models": summary, "differences_vs_logistic": differences}, indent=2) + "\n"
    (RESULTS / "model_comparison_metrics.json").write_text(metrics_json, encoding="utf-8")
    DOCUMENTED_METRICS.write_text(metrics_json, encoding="utf-8")

    lines = [
        "# Development-only model comparison v1",
        "",
        "**Target:** 10-year cardiovascular mortality. **Data:** NHANES 1999-2006 development cohort only, 8,902 people and 274 events. **Status:** preliminary research comparison; not clinical validation. The 2007-2008 evaluation outcomes were not loaded by this run.",
        "",
        "The settings and decision rule were fixed in [model_comparison_plan_v1.md](model_comparison_plan_v1.md) before the two new models were fit. All values below come from five-fold out-of-fold probabilities with fold-fitted preprocessing. The same participants and folds were used for every model.",
        "",
        "| Candidate | AUROC | AUPRC | Brier | Calibration intercept | Calibration slope |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, result in summary.items():
        lines.append(f"| {name} | {result['auroc']:.3f} | {result['auprc']:.3f} | {result['brier']:.5f} | {result['calibration_intercept']:.3f} | {result['calibration_slope']:.3f} |")
    lines += [
        "",
        "## Paired differences from logistic regression",
        "",
        "Positive Brier difference means a worse probability score; positive AUROC difference means better ranking. These person-level bootstrap intervals hold the out-of-fold predictions fixed. They omit model-fitting uncertainty and NHANES survey strata, clusters and weights.",
        "",
        "| Challenger | Brier difference (95% interval) | AUROC difference (95% interval) |",
        "| --- | ---: | ---: |",
    ]
    for name, result in differences.items():
        brier = result["brier"]
        auroc = result["auroc"]
        lines.append(
            f"| {name} | {brier['difference']:+.6f} ({brier['bootstrap_95pct'][0]:+.6f} to {brier['bootstrap_95pct'][1]:+.6f}) | "
            f"{auroc['difference']:+.4f} ({auroc['bootstrap_95pct'][0]:+.4f} to {auroc['bootstrap_95pct'][1]:+.4f}) |"
        )
    best = min(summary, key=lambda name: summary[name]["brier"])
    lines += [
        "",
        f"The lowest development-fold Brier score in this fixed comparison is for **{best}**. This is a preliminary sample-level result; compare discrimination and calibration as well before selecting a final research model. Small score differences may not be meaningful. No clinical threshold or risk category is set.",
        "",
        "Next: assess whether sigmoid or isotonic calibration improves development-only predictions using disjoint fitting and calibration folds. Any temporal-cycle comparison must disclose that the fixed logistic baseline's temporal result was already seen. A wholly independent cohort is still needed for stronger confirmation.",
        "",
        "These unweighted metrics do not account for NHANES sampling design. The cohort has few target events for flexible modeling, and public mortality fields include privacy-protecting substitutions. Do not use these probabilities for patient care.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(REPORT)


if __name__ == "__main__":
    main()
