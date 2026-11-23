"""FastAPI service for synthetic cardiovascular-mortality examples.

No names or patient identifiers are accepted or stored. Do not expose this
research service for patient care or an internet-facing deployment.
"""

from __future__ import annotations

import math
import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = ROOT / "models" / "logistic_baseline_v1.joblib"

LABELS = {
    "age_years": "Age",
    "gender_code": "Recorded male/female category",
    "systolic_bp_mmhg": "Systolic blood pressure",
    "bmi": "Body mass index",
    "total_cholesterol_mg_dl": "Total cholesterol",
    "hdl_cholesterol_mg_dl": "HDL cholesterol",
    "current_smoker": "Current smoking",
    "diabetes": "Self-reported diabetes",
}


class AssessmentInput(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    age_years: int = Field(ge=40, le=79)
    recorded_category: Literal["male", "female"]
    systolic_bp_mmhg: float | None = Field(default=None, gt=0)
    bmi: float | None = Field(default=None, gt=0)
    total_cholesterol_mg_dl: float | None = Field(default=None, gt=0)
    hdl_cholesterol_mg_dl: float | None = Field(default=None, gt=0)
    current_smoker: bool | None = None
    diabetes: bool | None = None

    @model_validator(mode="after")
    def hdl_is_part_of_total(self):
        if (self.hdl_cholesterol_mg_dl is not None
                and self.total_cholesterol_mg_dl is not None
                and self.hdl_cholesterol_mg_dl > self.total_cholesterol_mg_dl):
            raise ValueError("HDL cholesterol cannot exceed total cholesterol; check the entered units and values")
        return self


class Factor(BaseModel):
    field: str
    label: str
    direction: Literal["higher", "lower", "neutral"]
    log_odds_contribution: float
    missing: bool


class AssessmentResult(BaseModel):
    probability: float
    percentage: float
    reference_probability: float
    outcome: str
    horizon_years: int
    model_id: str
    calibrated: bool
    factors: list[Factor]
    missing_fields: list[str]
    outside_training_range: list[str]
    notice: str


app = FastAPI(title="Cardiovascular Risk Research Demo", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@lru_cache(maxsize=1)
def load_artifact() -> dict:
    path = Path(os.getenv("CARDIO_MODEL_PATH", str(DEFAULT_MODEL_PATH)))
    if not path.is_file():
        raise FileNotFoundError(f"Model artifact missing: {path}. Run python scripts/export_demo_model.py")
    artifact = joblib.load(path)
    required = {"model", "features", "transformed_feature_names", "reference_transformed", "training_bounds"}
    if not required.issubset(artifact):
        raise ValueError("Model artifact is incomplete")
    return artifact


@app.get("/api/health")
def health() -> dict:
    try:
        artifact = load_artifact()
    except (FileNotFoundError, ValueError):
        return {"status": "model_not_ready", "research_only": True}
    return {"status": "ok", "model_id": artifact["model_id"], "research_only": True}


@app.get("/api/model")
def model_info() -> dict:
    try:
        artifact = load_artifact()
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {
        "model_id": artifact["model_id"],
        "outcome": artifact["outcome"],
        "horizon_years": 10,
        "population": artifact["population"],
        "training_n": artifact["training_n"],
        "training_events": artifact["training_events"],
        "calibrated": artifact["calibrated"],
        "research_only": True,
    }


def as_row(values: AssessmentInput, features: list[str]) -> tuple[pd.DataFrame, list[str]]:
    raw = values.model_dump()
    raw["gender_code"] = 1 if raw.pop("recorded_category") == "male" else 2
    for field in ("current_smoker", "diabetes"):
        if raw[field] is not None:
            raw[field] = int(raw[field])
    missing = [field for field in features if raw[field] is None]
    row = pd.DataFrame([{field: np.nan if raw[field] is None else raw[field] for field in features}])
    return row, missing


def explain(artifact: dict, row: pd.DataFrame, missing: list[str]) -> tuple[list[Factor], float]:
    model = artifact["model"]
    transformed = model.named_steps["preprocess"].transform(row)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    transformed = np.asarray(transformed, dtype=float)[0]
    reference = np.asarray(artifact["reference_transformed"], dtype=float)
    names = artifact["transformed_feature_names"]
    coefficients = model.named_steps["model"].coef_[0]
    if not (len(transformed) == len(reference) == len(names) == len(coefficients)):
        raise ValueError("Fitted model and explanation reference disagree")

    factors = []
    for field in artifact["features"]:
        indices = [i for i, name in enumerate(names)
                   if name == f"numeric__{field}" or name.startswith(f"categorical__{field}_")]
        if not indices:
            raise ValueError(f"No fitted feature found for {field}")
        contribution = float(np.dot(coefficients[indices], transformed[indices] - reference[indices]))
        direction = "neutral" if abs(contribution) < 1e-10 else ("higher" if contribution > 0 else "lower")
        factors.append(Factor(
            field=field, label=LABELS[field], direction=direction,
            log_odds_contribution=round(contribution, 5), missing=field in missing,
        ))
    factors.sort(key=lambda item: abs(item.log_odds_contribution), reverse=True)
    reference_log_odds = float(model.named_steps["model"].intercept_[0] + np.dot(coefficients, reference))
    reference_probability = 1 / (1 + math.exp(-reference_log_odds))
    return factors, reference_probability


@app.post("/api/predict", response_model=AssessmentResult)
def predict(values: AssessmentInput, response: Response) -> AssessmentResult:
    response.headers["Cache-Control"] = "no-store"
    try:
        artifact = load_artifact()
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    row, missing = as_row(values, artifact["features"])
    probability = float(artifact["model"].predict_proba(row)[0, 1])
    factors, reference_probability = explain(artifact, row, missing)
    outside = [field for field, limits in artifact["training_bounds"].items()
               if not pd.isna(row.at[0, field])
               and not limits["min"] <= float(row.at[0, field]) <= limits["max"]]
    return AssessmentResult(
        probability=probability,
        percentage=round(probability * 100, 1),
        reference_probability=reference_probability,
        outcome=artifact["outcome"], horizon_years=10,
        model_id=artifact["model_id"], calibrated=False,
        factors=factors, missing_fields=missing, outside_training_range=outside,
        notice="Research demonstration using synthetic examples only. The estimate is uncalibrated and is not a diagnosis or treatment recommendation.",
    )
