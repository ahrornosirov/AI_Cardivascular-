# Cardiovascular risk research prototype

This repository begins with the research design for the team's approved title, **AI-Based Cardiovascular Risk Assessment System Using Explainable Machine Learning**. The proposed first model estimates **10-year cardiovascular mortality** from baseline clinical and lifestyle measurements. It is a research decision-support prototype, not a diagnostic tool or a validated clinical risk calculator.

Start with [Research Protocol v1](docs/research_protocol_v1.md), the [data dictionary](docs/data_dictionary_v1.md), and the [joined-cohort report](docs/cohort_report_v1.md). The target was confirmed on 6 October 2026. The baseline audit includes 8,902 development people (274 events) and 2,941 held-out people (87 events). No model performance or patient risk estimates have been produced yet.

## Reproduce the cohort audit

Use a Python environment with packages from `requirements.txt`. From this directory:

```bash
python scripts/audit_mortality.py
python scripts/download_nhanes.py
python scripts/build_cohort.py
```

The scripts download official CDC files, validate source checksums, and write the person-level cohort to ignored `data/processed/cohort_v1.csv`. The committed [source manifest](docs/nhanes_source_manifest.csv) and [machine-readable cohort audit](docs/cohort_feasibility.json) make the data provenance and counts reviewable.

## Planned sequence

1. Confirm target, population, data access, predictor availability, and event count. **Cohort audit complete.**
2. Document the literature and data dictionary. **Data dictionary drafted; literature review pending.**
3. Build reproducible cleaning, preprocessing, and exploratory analysis.
4. Compare logistic regression, random forest, and a justified boosting model using internal validation.
5. Evaluate discrimination, calibration, missing-data handling, and subgroups on held-out data.
6. Add explanations and uncertainty that correspond to the trained model and evaluation design.
7. Build the FastAPI and React demonstration after the risk model is validated for research use.

## Source material

The problem, question, and objective mapping has been checked against the team's 2 October 2026 Week 3 submission. The source PDF is kept outside this repository in the user's Downloads folder.
