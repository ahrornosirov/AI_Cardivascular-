"""Checks for the local synthetic-case research endpoint."""

import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app import app


MODEL = Path(__file__).resolve().parents[1] / "models" / "logistic_baseline_v1.joblib"
pytestmark = pytest.mark.skipif(not MODEL.exists(), reason="Run python scripts/export_demo_model.py first")
client = TestClient(app)

EXAMPLE = {
    "age_years": 45,
    "recorded_category": "female",
    "systolic_bp_mmhg": 120,
    "bmi": 25.4,
    "total_cholesterol_mg_dl": 190,
    "hdl_cholesterol_mg_dl": 58,
    "current_smoker": False,
    "diabetes": False,
}


def test_predict_returns_defined_outcome_and_exact_factor_decomposition():
    response = client.post("/api/predict", json=EXAMPLE)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    result = response.json()
    assert 0 < result["probability"] < 1
    assert result["horizon_years"] == 10
    assert result["calibrated"] is False
    assert len(result["factors"]) == 8
    assert result["missing_fields"] == []
    logit = lambda probability: math.log(probability / (1 - probability))
    difference = logit(result["probability"]) - logit(result["reference_probability"])
    assert sum(factor["log_odds_contribution"] for factor in result["factors"]) == pytest.approx(difference, abs=0.0001)


def test_missing_input_is_reported_and_model_still_predicts():
    values = {**EXAMPLE, "hdl_cholesterol_mg_dl": None}
    response = client.post("/api/predict", json=values)
    assert response.status_code == 200
    result = response.json()
    assert result["missing_fields"] == ["hdl_cholesterol_mg_dl"]
    assert any(factor["field"] == "hdl_cholesterol_mg_dl" and factor["missing"] for factor in result["factors"])


@pytest.mark.parametrize("field,value", [("age_years", 500), ("systolic_bp_mmhg", -30), ("total_cholesterol_mg_dl", 0)])
def test_impossible_inputs_are_rejected(field, value):
    response = client.post("/api/predict", json={**EXAMPLE, field: value})
    assert response.status_code == 422


def test_inconsistent_lipids_and_extra_identifier_are_rejected():
    assert client.post("/api/predict", json={**EXAMPLE, "hdl_cholesterol_mg_dl": 250}).status_code == 422
    assert client.post("/api/predict", json={**EXAMPLE, "patient_name": "Not accepted"}).status_code == 422


def test_outside_training_range_is_flagged():
    response = client.post("/api/predict", json={**EXAMPLE, "systolic_bp_mmhg": 300})
    assert response.status_code == 200
    assert response.json()["outside_training_range"] == ["systolic_bp_mmhg"]
