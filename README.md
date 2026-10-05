# Cardiovascular risk research prototype

This repository begins with the research design for the team's approved title, **AI-Based Cardiovascular Risk Assessment System Using Explainable Machine Learning**. The proposed first model estimates **10-year cardiovascular mortality** from baseline clinical and lifestyle measurements. It is a research decision-support prototype, not a diagnostic tool or a validated clinical risk calculator.

Start with [Research Protocol v1](docs/research_protocol_v1.md) and the [dataset feasibility note](docs/dataset_feasibility.md). The target and source must be reviewed by the team before model training. No model performance or patient risk estimates have been produced yet.

## Planned sequence

1. Confirm target, population, data access, predictor availability, and event count.
2. Document the literature and data dictionary.
3. Build reproducible cleaning, preprocessing, and exploratory analysis.
4. Compare logistic regression, random forest, and a justified boosting model using internal validation.
5. Evaluate discrimination, calibration, missing-data handling, and subgroups on held-out data.
6. Add explanations and uncertainty that correspond to the trained model and evaluation design.
7. Build the FastAPI and React demonstration after the risk model is validated for research use.

## Source material

The problem, question, and objective mapping has been checked against the team's 2 October 2026 Week 3 submission. The source PDF is kept outside this repository in the user's Downloads folder.
