# Cardiovascular risk research prototype

This repository begins with the research design for the team's approved title, **AI-Based Cardiovascular Risk Assessment System Using Explainable Machine Learning**. The proposed first model estimates **10-year cardiovascular mortality** from baseline clinical and lifestyle measurements. It is a research decision-support prototype, not a diagnostic tool or a validated clinical risk calculator.

## Project documents

Browse the [documentation index](docs/README.md) for the cumulative IMRAD outline, proposal, earlier drafts, presentation, research plan, and experiment records.

## Current project scope

The team has **no access to hospital records or a private ten-year follow-up cohort**. This project uses only public NHANES baseline data and the public CDC linked-mortality outcomes already documented here. The web demonstration will use synthetic example patients; real-patient clinical use and hospital integration are outside the current project. If a hospital partnership becomes possible later, external validation would be a separate phase and would not require us to retrain the initial model.

Start with [Research Protocol v1](docs/research_protocol_v1.md), the [data dictionary](docs/data_dictionary_v1.md), and the [joined-cohort report](docs/cohort_report_v1.md). The target was confirmed on 6 October 2026. The cohort includes 8,902 development people (274 events) and 2,941 later-cycle people (87 events). A [preliminary logistic baseline](docs/baseline_results_v1.md) has been evaluated; it is not a validated clinical risk calculator. The [predictor-quality audit](docs/predictor_quality_v1.md) records missingness, observed extremes, and the HDL measurement issue.

## Reproduce the cohort audit

Use a Python environment with packages from `requirements.txt`. From this directory:

```bash
python scripts/audit_mortality.py
python scripts/download_nhanes.py
python scripts/build_cohort.py
```

The scripts download official CDC files, validate source checksums, and write the person-level cohort to ignored `data/processed/cohort_v1.csv`. The committed [source manifest](docs/nhanes_source_manifest.csv) and [machine-readable cohort audit](docs/cohort_feasibility.json) make the data provenance and counts reviewable.

The [baseline plan](docs/model_plan_v1.md) was written before training. Run `python scripts/train_baseline.py` to reproduce the [preliminary logistic-regression results](docs/baseline_results_v1.md). The temporal evaluation cycle has been inspected for this baseline; later model selection must still use development data only.

The [development-only comparison plan](docs/model_comparison_plan_v1.md) fixes the random-forest and histogram-gradient-boosting candidates before fitting them. After the baseline run, use `python scripts/audit_predictors.py` and `python scripts/compare_models.py` to reproduce the [predictor-quality audit](docs/predictor_quality_v1.md) and [model comparison](docs/model_comparison_v1.md). The model comparison reads development labels from the baseline's development prediction file and does not score the later cycle.

The [calibration plan](docs/calibration_plan_v1.md) specifies a nested development-only comparison of the original logistic probability, sigmoid calibration, and isotonic calibration. Run `python scripts/compare_calibration.py` after the baseline to reproduce the [calibration result](docs/calibration_results_v1.md). The written selection rule retained the original logistic output for the local demo: neither calibration method improved its Brier score. This does not establish clinical calibration in another population.

## Run the local web prototype

This is a working **synthetic-case research demo**, not a clinical service. It uses the fixed logistic baseline trained on the 1999-2006 development cohort. Its displayed probability is preliminary and has not been recalibrated or externally validated. The form has no name or identifier field and does not save submitted values.

Install the Python requirements, build the cohort as above, then fit the local artifact:

```bash
python -m pip install -r requirements.txt
python scripts/export_demo_model.py
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal, start the React frontend:

```bash
cd frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. The form accepts the eight modeled variables, flags missing and outside-training-range values, and shows exact logistic-model contributions on the log-odds scale. It deliberately does not assign low/medium/high categories, suggest treatment, or invent an uncertainty score. API documentation is available locally at `http://127.0.0.1:8000/docs`.

Run API checks after exporting the model with `python -m pytest -q`. The serialized model in ignored `models/` can be rebuilt from the public cohort; do not load an untrusted replacement artifact. Keep both local servers bound to your own computer and use invented examples only.

## Planned sequence

1. Confirm target, population, data access, predictor availability, and event count. **Cohort audit complete.**
2. Document the literature and data dictionary. **Data dictionary drafted; literature review pending.** A [parallel literature-review prompt](docs/antigravity_literature_task.md) is ready.
3. Build reproducible cleaning, preprocessing, and exploratory analysis. **Cohort and predictor-quality audits completed; additional sensitivity analyses pending.**
4. Compare logistic regression, random forest, and a justified boosting model using internal validation. **Fixed development-only comparison completed; calibration analysis pending.**
5. Evaluate discrimination, calibration, missing-data handling, and subgroups with transparent limitations. **Development-only calibration comparison completed; further sensitivity and subgroup analyses pending.**
6. Add explanations and uncertainty that correspond to the trained model and evaluation design. **Exact logistic contributions implemented for the local demo; formal SHAP and uncertainty study pending.**
7. Build the FastAPI and React demonstration. **First local synthetic-case version implemented; user and clinical review pending.**

## Source material

The problem, question, and objective mapping has been checked against the team's 2 October 2026 Week 3 submission. The source PDF is kept outside this repository in the user's Downloads folder.
