"""Fit the prespecified public-data logistic-regression baseline.

Run after scripts/build_cohort.py. Writes research outputs only; it does not
produce a clinically deployable model.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.special import logit
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "cohort_v1.csv"
RESULTS = ROOT / "results"
FIGURES = ROOT / "docs" / "figures"
DOCUMENTED_METRICS = ROOT / "docs" / "baseline_metrics.json"
SEED = 20261006
NUMERIC = ["age_years", "systolic_bp_mmhg", "bmi", "total_cholesterol_mg_dl", "hdl_cholesterol_mg_dl"]
CATEGORICAL = ["gender_code", "current_smoker", "diabetes"]
FEATURES = NUMERIC + CATEGORICAL


def pipeline() -> Pipeline:
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("encode", OneHotEncoder(drop="if_binary", handle_unknown="ignore"))])
    return Pipeline(
        [
            ("preprocess", ColumnTransformer([("numeric", numeric, NUMERIC), ("categorical", categorical, CATEGORICAL)])),
            ("model", LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=SEED)),
        ]
    )


def calibration(y: np.ndarray, probability: np.ndarray) -> tuple[float, float]:
    clipped = np.clip(probability, 1e-8, 1 - 1e-8)
    recalibration = LogisticRegression(penalty=None, solver="lbfgs", max_iter=1000)
    recalibration.fit(logit(clipped).reshape(-1, 1), y)
    return float(recalibration.intercept_[0]), float(recalibration.coef_[0, 0])


def metrics(y: np.ndarray, probability: np.ndarray) -> dict[str, float | int]:
    intercept, slope = calibration(y, probability)
    return {
        "n": int(len(y)),
        "events": int(y.sum()),
        "prevalence": round(float(y.mean()), 6),
        "auroc": round(float(roc_auc_score(y, probability)), 6),
        "auprc": round(float(average_precision_score(y, probability)), 6),
        "brier": round(float(brier_score_loss(y, probability)), 6),
        "calibration_intercept": round(intercept, 6),
        "calibration_slope": round(slope, 6),
    }


def bootstrap_intervals(y: np.ndarray, probability: np.ndarray, n_boot: int = 1000) -> dict[str, list[float]]:
    rng = np.random.default_rng(SEED)
    values = {"auroc": [], "auprc": [], "brier": []}
    for _ in range(n_boot):
        sample = rng.integers(0, len(y), size=len(y))
        y_sample = y[sample]
        if len(np.unique(y_sample)) < 2:
            continue
        p_sample = probability[sample]
        values["auroc"].append(roc_auc_score(y_sample, p_sample))
        values["auprc"].append(average_precision_score(y_sample, p_sample))
        values["brier"].append(brier_score_loss(y_sample, p_sample))
    return {key: [round(float(v), 6) for v in np.quantile(samples, [0.025, 0.975])] for key, samples in values.items()}


def calibration_plot(outcomes: dict[str, tuple[np.ndarray, np.ndarray]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), sharex=True, sharey=True)
    for ax, (name, (y, probability)) in zip(axes, outcomes.items()):
        groups = pd.qcut(probability, 10, duplicates="drop")
        summary = pd.DataFrame({"y": y, "p": probability, "bin": groups}).groupby("bin", observed=True).agg(predicted=("p", "mean"), observed=("y", "mean"), n=("y", "size"))
        ax.plot([0, 0.2], [0, 0.2], color="#777777", linestyle="--", label="Ideal")
        ax.plot(summary.predicted, summary.observed, marker="o", color="#235789", label="Observed by decile")
        ax.set_title(name)
        ax.set_xlabel("Mean predicted 10-year mortality")
        ax.grid(alpha=0.2)
        ax.legend(loc="upper left", fontsize=8)
    axes[0].set_ylabel("Observed 10-year mortality")
    axes[0].set_xlim(0, 0.2)
    axes[0].set_ylim(0, 0.2)
    fig.suptitle("Logistic baseline calibration (unweighted sample)")
    fig.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "baseline_calibration.png", dpi=160)
    plt.close(fig)


def main() -> None:
    frame = pd.read_csv(DATA)
    development = frame.loc[frame.split_role == "development"].copy()
    evaluation = frame.loc[frame.split_role == "evaluation"].copy()
    if len(development) != 8902 or len(evaluation) != 2941:
        raise ValueError("Unexpected cohort size; review cohort protocol before training")
    x_dev = development[FEATURES]
    y_dev = development.cvd_death_10y.to_numpy(dtype=int)
    x_eval = evaluation[FEATURES]
    y_eval = evaluation.cvd_death_10y.to_numpy(dtype=int)
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    dev_prob = cross_val_predict(pipeline(), x_dev, y_dev, cv=folds, method="predict_proba", n_jobs=1)[:, 1]
    model = pipeline().fit(x_dev, y_dev)
    eval_prob = model.predict_proba(x_eval)[:, 1]
    outcomes = {"Development, out-of-fold": (y_dev, dev_prob), "2007-08 held-out": (y_eval, eval_prob)}
    report = {
        "study_status": "Preliminary research baseline; not clinically validated",
        "model": "Logistic regression; C=1.0; no class weighting; median/mode imputation inside folds",
        "cross_validation": "Five stratified development folds; random_state=20261006",
        "interval_note": "95% person-level bootstrap percentile intervals, conditional on fixed predictions; NHANES survey design not accounted for",
        "splits": {name: {**metrics(y, p), "bootstrap_95pct": bootstrap_intervals(y, p)} for name, (y, p) in outcomes.items()},
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    metrics_json = json.dumps(report, indent=2) + "\n"
    (RESULTS / "baseline_metrics.json").write_text(metrics_json, encoding="utf-8")
    DOCUMENTED_METRICS.write_text(metrics_json, encoding="utf-8")
    pd.DataFrame({"SEQN": development.SEQN, "split": "development_oof", "target": y_dev, "probability": dev_prob}).to_csv(RESULTS / "baseline_development_predictions.csv", index=False)
    pd.DataFrame({"SEQN": evaluation.SEQN, "split": "evaluation", "target": y_eval, "probability": eval_prob}).to_csv(RESULTS / "baseline_evaluation_predictions.csv", index=False)
    calibration_plot(outcomes)
    print(json.dumps(report["splits"], indent=2))


if __name__ == "__main__":
    main()
