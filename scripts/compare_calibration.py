"""Nested development-only comparison of logistic probability calibration.

The later 2007-2008 outcomes are neither loaded nor scored here. See the
prespecified design in docs/calibration_plan_v1.md before changing methods.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from train_baseline import FEATURES, SEED, metrics, pipeline

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / "data" / "processed" / "cohort_v1.csv"
BASELINE = ROOT / "results" / "baseline_development_predictions.csv"
RESULTS = ROOT / "results"
DOCUMENTED = ROOT / "docs" / "calibration_metrics.json"
REPORT = ROOT / "docs" / "calibration_results_v1.md"
FIGURE = ROOT / "docs" / "figures" / "calibration_comparison.png"


def brier_difference(y: np.ndarray, original: np.ndarray, candidate: np.ndarray) -> dict:
    rng = np.random.default_rng(SEED)
    samples = []
    for _ in range(1000):
        index = rng.integers(0, len(y), size=len(y))
        samples.append(float(np.mean((candidate[index] - y[index]) ** 2)
                             - np.mean((original[index] - y[index]) ** 2)))
    return {
        "difference": round(float(np.mean((candidate - y) ** 2) - np.mean((original - y) ** 2)), 6),
        "bootstrap_95pct": [round(float(value), 6) for value in np.quantile(samples, [.025, .975])],
    }


def plot_curves(y: np.ndarray, predictions: dict[str, np.ndarray]) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 5.3))
    ax.plot([0, .20], [0, .20], linestyle="--", color="#707b80", label="Ideal")
    colors = {"Original logistic": "#235789", "Sigmoid": "#148a7c", "Isotonic": "#d78b51"}
    for label, probability in predictions.items():
        bins = pd.qcut(probability, 10, duplicates="drop")
        curve = pd.DataFrame({"observed": y, "predicted": probability, "bin": bins}).groupby("bin", observed=True).agg(
            predicted=("predicted", "mean"), observed=("observed", "mean")
        )
        ax.plot(curve.predicted, curve.observed, marker="o", linewidth=1.6,
                markersize=4.4, label=label, color=colors[label])
    ax.set(xlabel="Mean predicted 10-year cardiovascular mortality",
           ylabel="Observed 10-year cardiovascular mortality",
           xlim=(0, .20), ylim=(0, .20))
    ax.grid(alpha=.18)
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title("Development-only out-of-fold calibration (unweighted)")
    fig.tight_layout()
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE, dpi=180)
    plt.close(fig)


def main() -> None:
    frame = pd.read_csv(COHORT, usecols=["SEQN", "split_role", *FEATURES])
    development = frame.loc[frame.split_role == "development"].copy()
    labels = pd.read_csv(BASELINE, usecols=["SEQN", "target", "probability"])
    if labels.SEQN.duplicated().any() or development.SEQN.duplicated().any():
        raise ValueError("Duplicate development participant")
    development = development.merge(labels, on="SEQN", how="left", validate="one_to_one")
    if len(development) != 8902 or development.target.isna().any() or development.target.sum() != 274:
        raise ValueError("Development cohort differs from calibration plan")

    x = development[FEATURES]
    y = development.target.to_numpy(dtype=int)
    outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    predictions = {"Original logistic": development.probability.to_numpy(dtype=float)}
    for method, label in [("sigmoid", "Sigmoid"), ("isotonic", "Isotonic")]:
        inner = StratifiedKFold(n_splits=3, shuffle=True, random_state=20261007)
        candidate = CalibratedClassifierCV(estimator=pipeline(), method=method, cv=inner, ensemble=False)
        predictions[label] = cross_val_predict(candidate, x, y, cv=outer, method="predict_proba", n_jobs=1)[:, 1]
        if not np.isfinite(predictions[label]).all():
            raise ValueError(f"Non-finite probabilities from {label}")

    scores = {label: {**metrics(y, probability), "mean_predicted": round(float(probability.mean()), 6)}
              for label, probability in predictions.items()}
    differences = {label: brier_difference(y, predictions["Original logistic"], probability)
                   for label, probability in predictions.items() if label != "Original logistic"}
    base = scores["Original logistic"]
    qualifying = [label for label in differences
                  if differences[label]["bootstrap_95pct"][1] < 0
                  and abs(scores[label]["calibration_intercept"]) < abs(base["calibration_intercept"])
                  and abs(scores[label]["calibration_slope"] - 1) < abs(base["calibration_slope"] - 1)]
    selected = min(qualifying, key=lambda name: scores[name]["brier"]) if qualifying else "Original logistic"

    result = {
        "study_status": "Development-only research comparison; not clinical validation",
        "design": "5 outer stratified folds; 3 inner folds for calibration; ensemble=False",
        "n": len(y), "events": int(y.sum()),
        "models": scores, "brier_differences_vs_original": differences,
        "selected_for_local_demo": selected,
        "selection_note": "Prespecified conservative rule; no 2007-2008 outcome used",
        "interval_note": "Person bootstrap conditional on fixed OOF predictions; NHANES design and model-fitting uncertainty omitted",
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "calibration_metrics.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    DOCUMENTED.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame({"SEQN": development.SEQN, "target": y,
                  "original": predictions["Original logistic"],
                  "sigmoid": predictions["Sigmoid"],
                  "isotonic": predictions["Isotonic"]}).to_csv(
        RESULTS / "calibration_development_oof.csv", index=False
    )
    plot_curves(y, predictions)

    lines = [
        "# Development-only calibration comparison v1", "",
        "**Target:** 10-year cardiovascular mortality. **Cohort:** 8,902 NHANES 1999-2006 development participants, 274 events. **Status:** research analysis only. The 2007-2008 outcomes were not loaded or scored in this experiment.", "",
        "The methods and conservative web-demo selection rule were written first in [calibration_plan_v1.md](calibration_plan_v1.md). Each reported calibrated probability is out-of-fold from five outer folds; its sigmoid or isotonic map was fitted with three inner folds. Preprocessing and the logistic model were also refit inside the relevant folds.", "",
        "| Method | AUROC | AUPRC | Brier | Calibration intercept | Calibration slope | Mean predicted / observed |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, score in scores.items():
        lines.append(f"| {label} | {score['auroc']:.3f} | {score['auprc']:.3f} | {score['brier']:.5f} | {score['calibration_intercept']:+.3f} | {score['calibration_slope']:.3f} | {score['mean_predicted']:.2%} / {score['prevalence']:.2%} |")
    lines += ["", "## Paired Brier differences from the original logistic model", "",
              "Negative differences favor calibration. The 95% person-bootstrap intervals condition on the fixed out-of-fold predictions and omit model-fitting and NHANES-design uncertainty.", "",
              "| Method | Brier difference (95% interval) |", "| --- | ---: |"]
    for label, item in differences.items():
        lower, upper = item["bootstrap_95pct"]
        lines.append(f"| {label} | {item['difference']:+.6f} ({lower:+.6f} to {upper:+.6f}) |")
    lines += ["", f"**Selection under the written rule:** {selected}.", "",
              "![Development-only calibration comparison](figures/calibration_comparison.png)", "",
              "The Brier score reflects discrimination as well as calibration; the plot and intercept/slope must be read alongside it. The later US cycle has been inspected for the original baseline, and neither this development result nor a later comparison makes the model safe for patient care. An independent target-population cohort is still needed.", "",
              "[scikit-learn calibration guidance](https://scikit-learn.org/stable/modules/calibration.html)", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"scores": scores, "differences": differences, "selected": selected}, indent=2))


if __name__ == "__main__":
    main()
