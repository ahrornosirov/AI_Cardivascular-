"""Fit and save the preliminary logistic model for the local synthetic-case demo.

Run after building the public NHANES cohort. The saved model is a research
artifact, not a calibrated or clinically validated risk calculator.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from train_baseline import FEATURES, NUMERIC, pipeline

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / "data" / "processed" / "cohort_v1.csv"
ARTIFACT = ROOT / "models" / "logistic_baseline_v1.joblib"


def main() -> None:
    frame = pd.read_csv(COHORT, usecols=["split_role", "cvd_death_10y", *FEATURES])
    development = frame.loc[frame.split_role == "development"]
    if len(development) != 8902 or development.cvd_death_10y.sum() != 274:
        raise ValueError("Cohort differs from the prespecified development sample")

    x = development[FEATURES]
    y = development.cvd_death_10y.to_numpy(dtype=int)
    fitted = pipeline().fit(x, y)
    preprocessor = fitted.named_steps["preprocess"]
    transformed = preprocessor.transform(x)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    feature_names = list(preprocessor.get_feature_names_out())
    reference = np.asarray(transformed, dtype=float).mean(axis=0)
    if len(feature_names) != len(reference):
        raise ValueError("Feature reference does not match fitted pipeline")

    artifact = {
        "model": fitted,
        "model_id": "logistic-baseline-v1",
        "features": FEATURES,
        "transformed_feature_names": feature_names,
        "reference_transformed": reference,
        "training_bounds": {
            name: {"min": float(x[name].min()), "max": float(x[name].max())}
            for name in NUMERIC
        },
        "training_n": len(development),
        "training_events": int(y.sum()),
        "outcome": "Death from heart disease or cerebrovascular disease within 10 years",
        "population": "US NHANES adults aged 40-79 without reported prior cardiovascular disease",
        "calibrated": False,
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, ARTIFACT)
    print(f"Saved {ARTIFACT} ({len(development):,} development participants, {y.sum()} events)")


if __name__ == "__main__":
    main()
