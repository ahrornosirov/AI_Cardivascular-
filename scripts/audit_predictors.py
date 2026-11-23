"""Generate a reproducible descriptive audit of the eight baseline predictors.

This deliberately does not call an observed value clinically valid or invalid.
Range limits for a future patient form require clinical review.
"""

from pathlib import Path

import pandas as pd

from train_baseline import FEATURES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "cohort_v1.csv"
RAW_BMI = ROOT / "data" / "raw" / "BMX_D.xpt"
OUT = ROOT / "docs" / "predictor_quality_v1.md"


def main() -> None:
    frame = pd.read_csv(DATA, usecols=["SEQN", "cycle", "split_role", *FEATURES])
    if frame.SEQN.duplicated().any() or set(frame.split_role) != {"development", "evaluation"}:
        raise ValueError("Unexpected cohort structure")
    if frame.groupby("split_role").size().to_dict() != {"development": 8902, "evaluation": 2941}:
        raise ValueError("Unexpected cohort size")

    lines = [
        "# Baseline predictor-quality audit v1",
        "",
        "**Generated from `data/processed/cohort_v1.csv`.** This is descriptive quality control, not a clinical input-range policy. The 2007-2008 evaluation predictors are shown only to describe completeness and measurement shift; their outcomes are not used here to select a model.",
        "",
        "## Missing data and observed spread",
        "",
        "| Predictor | Development missing | 2007-08 missing | Development observed min / 1st / 99th / max |",
        "| --- | ---: | ---: | ---: |",
    ]
    dev = frame.loc[frame.split_role == "development"]
    later = frame.loc[frame.split_role == "evaluation"]
    for feature in FEATURES:
        s = dev[feature].dropna()
        spread = " / ".join(f"{v:g}" for v in [s.min(), s.quantile(.01), s.quantile(.99), s.max()])
        lines.append(f"| `{feature}` | {dev[feature].isna().mean():.2%} | {later[feature].isna().mean():.2%} | {spread} |")

    dev_complete = dev[FEATURES].notna().all(axis=1).sum()
    later_complete = later[FEATURES].notna().all(axis=1).sum()
    lines += [
        "",
        f"All eight predictors are complete in **{dev_complete:,}/{len(dev):,} development people** and **{later_complete:,}/{len(later):,} later-cycle people**. Complete-case analysis would discard participants with missing values; the primary baseline uses fold-fitted imputation to retain them. Event losses are reported separately in the cohort report.",
        "",
        "## Cycle review: HDL cholesterol",
        "",
        "| NHANES cycle | Observed n | Mean HDL (mg/dL) | Median HDL (mg/dL) | Missing |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for cycle, group in frame.groupby("cycle", sort=True):
        hdl = group.hdl_cholesterol_mg_dl
        lines.append(f"| {cycle} | {hdl.count():,} | {hdl.mean():.2f} | {hdl.median():.1f} | {hdl.isna().mean():.2%} |")

    impossible_pair = ((frame.hdl_cholesterol_mg_dl > frame.total_cholesterol_mg_dl)
                       & frame.hdl_cholesterol_mg_dl.notna()
                       & frame.total_cholesterol_mg_dl.notna()).sum()
    raw_bmi = pd.read_sas(RAW_BMI, format="xport")
    extreme_bmi = raw_bmi.loc[raw_bmi.SEQN == 33228, ["BMXBMI", "BMXWT", "BMXHT"]]
    if len(extreme_bmi) != 1:
        raise ValueError("Extreme BMI source record not found")
    recorded_bmi, weight_kg, height_cm = extreme_bmi.iloc[0]
    if abs(recorded_bmi - weight_kg / (height_cm / 100) ** 2) > .1:
        raise ValueError("Extreme BMI is inconsistent with recorded height and weight")
    lines += [
        "",
        f"HDL exceeded total cholesterol for **{impossible_pair}** records with both values observed. The CDC documents method changes and cautions against reading 1999-2008 HDL trends without considering assay effects. The cycle means above are unweighted cohort descriptions and must not be interpreted as a national trend. [CDC HDL documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/HDL_E.htm)",
        "",
        "## Values flagged for source and clinical review",
        "",
        f"The observed full-cohort maxima are systolic BP **266 mmHg**, BMI **130.21 kg/m2**, total cholesterol **727 mg/dL**, and HDL cholesterol **188 mg/dL**. These records are not silently removed or set to missing. The cohort builder keeps positive recorded values. The BMI {recorded_bmi:.2f} record was checked against raw `BMX_D.xpt`: recorded weight {weight_kg:.1f} kg and height {height_cm:.1f} cm agree with the reported BMI. Before building a patient form, a clinician should decide hard rejection rules and softer 'check this entry' warnings separately; a research-data maximum is not an appropriate clinical limit by itself.",
        "",
        "## Open checks",
        "",
        "1. Trace the remaining unusual BP and cholesterol values to raw XPT records and source documentation.",
        "2. Run a prespecified sensitivity analysis for influential extremes and HDL measurement changes within development data.",
        "3. Obtain clinical review of input validation ranges and measurement instructions before any form accepts real values.",
        "4. Distinguish unweighted sample metrics from design-aware population estimates; NHANES weights address its complex design. [CDC weighting guidance](https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx)",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
