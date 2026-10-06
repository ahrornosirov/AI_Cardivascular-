"""Join NHANES baseline predictors to 10-year cardiovascular mortality.

This is a cohort and missingness audit, not model training. Run from the repository
root with Python 3.12+ and pandas (tested with pandas 3.0.1).
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from audit_mortality import KNOWN_SHA256

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
REPORT = ROOT / "docs" / "cohort_feasibility.json"
CYCLES = {1999: "", 2001: "_B", 2003: "_C", 2005: "_D", 2007: "_E"}
VALID_CAUSES = {f"{code:03d}" for code in range(1, 11)}
PRIOR_CVD_FIELDS = [f"MCQ160{letter}" for letter in "BCDEF"]
PREDICTORS = ["age_years", "gender_code", "systolic_bp_mmhg", "bmi", "total_cholesterol_mg_dl", "hdl_cholesterol_mg_dl", "current_smoker", "diabetes"]


def verify_sources() -> None:
    manifest = ROOT / "docs" / "nhanes_source_manifest.csv"
    with manifest.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 42:
        raise ValueError(f"Expected 42 baseline source files, found {len(rows)}")
    for row in rows:
        path = RAW / row["filename"]
        payload = path.read_bytes()
        if len(payload) != int(row["bytes"]) or hashlib.sha256(payload).hexdigest() != row["sha256"]:
            raise ValueError(f"Source manifest mismatch: {path}")
    for year, expected in KNOWN_SHA256.items():
        path = RAW / f"NHANES_{year}_{year+1}_MORT_2019_PUBLIC.dat"
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Mortality file checksum mismatch: {path}")


def xpt(stem: str, columns: list[str]) -> pd.DataFrame:
    path = RAW / f"{stem}.xpt"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}; run scripts/download_nhanes.py")
    frame = pd.read_sas(path, format="xport")
    absent = set(columns) - set(frame.columns)
    if absent:
        raise ValueError(f"Missing columns in {path.name}: {sorted(absent)}")
    frame = frame[columns].copy()
    if frame["SEQN"].isna().any() or frame["SEQN"].duplicated().any():
        raise ValueError(f"Missing or duplicate SEQN in {path.name}")
    frame["SEQN"] = frame["SEQN"].astype("int64")
    return frame


def mortality(year: int) -> pd.DataFrame:
    path = RAW / f"NHANES_{year}_{year+1}_MORT_2019_PUBLIC.dat"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}; run scripts/audit_mortality.py")
    records = []
    for line in path.read_text(encoding="ascii").splitlines():
        get = lambda first, last: line[first - 1 : last].strip()
        records.append((get(1, 6), get(15, 15), get(16, 16), get(17, 19), get(46, 48)))
    frame = pd.DataFrame(records, columns=["SEQN", "eligstat", "mortstat", "cause", "months_from_exam"])
    frame["SEQN"] = pd.to_numeric(frame["SEQN"], errors="raise").astype("int64")
    if frame["SEQN"].duplicated().any():
        raise ValueError(f"Duplicate SEQN in {path.name}")
    frame["months_from_exam"] = pd.to_numeric(frame["months_from_exam"], errors="coerce")
    return frame


def count(stage: list[dict], cycle: str, name: str, frame: pd.DataFrame) -> None:
    stage.append({"cycle": cycle, "stage": name, "n": int(len(frame))})


def binary_question(values: pd.Series) -> pd.Series:
    return values.map({1.0: 1.0, 2.0: 0.0})


def current_smoker(smq020: pd.Series, smq040: pd.Series) -> pd.Series:
    # SMQ020 = ever smoked >=100 cigarettes; SMQ040 = now every/some/no days.
    result = pd.Series(np.nan, index=smq020.index, dtype="float64")
    result.loc[smq020 == 2] = 0.0
    result.loc[(smq020 == 1) & (smq040 == 3)] = 0.0
    result.loc[(smq020 == 1) & smq040.isin([1, 2])] = 1.0
    return result


def build_cycle(year: int, stage: list[dict]) -> pd.DataFrame:
    suffix = CYCLES[year]
    cycle = f"{year}-{year+1}"
    demo_columns = ["SEQN", "RIDSTATR", "RIDAGEYR", "RIAGENDR", "WTMEC2YR", "SDMVPSU", "SDMVSTRA"]
    if year in (1999, 2001):
        demo_columns.append("WTMEC4YR")
    demo = xpt("DEMO" + suffix, demo_columns)
    if year not in (1999, 2001):
        demo["WTMEC4YR"] = np.nan
    count(stage, cycle, "survey_rows", demo)
    demo = demo.loc[(demo.RIDSTATR == 2) & demo.RIDAGEYR.between(40, 79)].copy()
    count(stage, cycle, "examined_age_40_79", demo)

    cohort = demo.merge(mortality(year), on="SEQN", how="left", validate="one_to_one")
    cohort = cohort.loc[cohort.eligstat == "1"].copy()
    count(stage, cycle, "mortality_linkage_eligible", cohort)
    elapsed = cohort.months_from_exam
    known = elapsed.notna() & (
        ((cohort.mortstat == "0") & (elapsed >= 120))
        | ((cohort.mortstat == "1") & ((elapsed > 120) | cohort.cause.isin(VALID_CAUSES)))
    )
    cohort = cohort.loc[known].copy()
    count(stage, cycle, "known_10y_outcome", cohort)
    cohort["cvd_death_10y"] = (
        (cohort.mortstat == "1")
        & (cohort.months_from_exam <= 120)
        & cohort.cause.isin(["001", "005"])
    ).astype("int8")

    history = xpt("MCQ" + suffix, ["SEQN", *PRIOR_CVD_FIELDS])
    cohort = cohort.merge(history, on="SEQN", how="left", validate="one_to_one")
    prior_yes = cohort[PRIOR_CVD_FIELDS].eq(1).any(axis=1)
    cohort = cohort.loc[~prior_yes].copy()
    count(stage, cycle, "no_reported_prior_cvd", cohort)
    prior_complete_no = cohort[PRIOR_CVD_FIELDS].eq(2).all(axis=1)
    cohort = cohort.loc[prior_complete_no].copy()
    count(stage, cycle, "confirmed_no_prior_cvd", cohort)

    bp = xpt("BPX" + suffix, ["SEQN", "BPXSY1", "BPXSY2", "BPXSY3", "BPXSY4"])
    bmi = xpt("BMX" + suffix, ["SEQN", "BMXBMI"])
    if year < 2005:
        lipids = xpt("LAB13" if year == 1999 else "L13_B" if year == 2001 else "L13_C", ["SEQN", "LBXTC", "LBDHDL" if year < 2003 else "LBXHDD"])
    else:
        lipids = xpt("TCHOL" + suffix, ["SEQN", "LBXTC"])
        lipids = lipids.merge(xpt("HDL" + suffix, ["SEQN", "LBDHDD"]), on="SEQN", how="outer", validate="one_to_one")
    smoking = xpt("SMQ" + suffix, ["SEQN", "SMQ020", "SMQ040"])
    diabetes = xpt("DIQ" + suffix, ["SEQN", "DIQ010"])
    for source in [bp, bmi, lipids, smoking, diabetes]:
        cohort = cohort.merge(source, on="SEQN", how="left", validate="one_to_one")

    bp_cols = ["BPXSY1", "BPXSY2", "BPXSY3", "BPXSY4"]
    bp_values = cohort[bp_cols].where(cohort[bp_cols] > 0)
    cohort["systolic_bp_mmhg"] = bp_values.mean(axis=1)
    cohort["age_years"] = cohort.RIDAGEYR
    cohort["gender_code"] = cohort.RIAGENDR
    cohort["bmi"] = cohort.BMXBMI.where(cohort.BMXBMI > 0)
    cohort["total_cholesterol_mg_dl"] = cohort.LBXTC.where(cohort.LBXTC > 0)
    hdl_source = "LBDHDL" if year < 2003 else "LBXHDD" if year == 2003 else "LBDHDD"
    cohort["hdl_cholesterol_mg_dl"] = cohort[hdl_source].where(cohort[hdl_source] > 0)
    cohort["current_smoker"] = current_smoker(cohort.SMQ020, cohort.SMQ040)
    cohort["diabetes"] = binary_question(cohort.DIQ010)  # Borderline (3) remains missing.
    cohort["cycle"] = cycle
    cohort["split_role"] = "evaluation" if year == 2007 else "development"
    cohort = cohort[["SEQN", "cycle", "split_role", "WTMEC2YR", "WTMEC4YR", "SDMVPSU", "SDMVSTRA", "cvd_death_10y", *PREDICTORS]].copy()
    count(stage, cycle, "final_primary_prevention_cohort", cohort)
    return cohort


def main() -> None:
    verify_sources()
    stages: list[dict] = []
    cohort = pd.concat([build_cycle(year, stages) for year in CYCLES], ignore_index=True)
    if cohort.SEQN.duplicated().any():
        raise ValueError("Duplicate SEQN after combining cycles")
    PROCESSED.mkdir(parents=True, exist_ok=True)
    output = PROCESSED / "cohort_v1.csv"
    cohort.to_csv(output, index=False)
    missingness = []
    for cycle, group in cohort.groupby("cycle", sort=True):
        for name in PREDICTORS:
            missingness.append({"cycle": cycle, "variable": name, "n": len(group), "missing": int(group[name].isna().sum()), "missing_pct": round(float(group[name].isna().mean() * 100), 2)})
    summary = []
    for role, group in cohort.groupby("split_role"):
        summary.append({"role": role, "n": len(group), "events": int(group.cvd_death_10y.sum()), "event_pct": round(float(group.cvd_death_10y.mean() * 100), 2), "complete_cases": int(group[PREDICTORS].notna().all(axis=1).sum())})
    report = {
        "target": "Cardiovascular death within 120 months of NHANES examination",
        "population": "US NHANES examined adults 40-79 with definite no on five self-reported prior-CVD questions",
        "source_manifest_sha256": hashlib.sha256((ROOT / "docs" / "nhanes_source_manifest.csv").read_bytes()).hexdigest(),
        "stages": stages,
        "summary": summary,
        "missingness": missingness,
        "output": str(output.relative_to(ROOT)),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Cohort: {output}\nAudit: {REPORT}")


if __name__ == "__main__":
    main()
