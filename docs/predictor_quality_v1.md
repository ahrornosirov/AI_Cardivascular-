# Baseline predictor-quality audit v1

**Generated from `data/processed/cohort_v1.csv`.** This is descriptive quality control, not a clinical input-range policy. The 2007-2008 evaluation predictors are shown only to describe completeness and measurement shift; their outcomes are not used here to select a model.

## Missing data and observed spread

| Predictor | Development missing | 2007-08 missing | Development observed min / 1st / 99th / max |
| --- | ---: | ---: | ---: |
| `age_years` | 0.00% | 0.00% | 40 / 40 / 79 / 79 |
| `systolic_bp_mmhg` | 4.46% | 4.08% | 73 / 94 / 190.667 / 266 |
| `bmi` | 2.27% | 1.36% | 12.04 / 18.3499 / 48.7301 / 130.21 |
| `total_cholesterol_mg_dl` | 5.30% | 5.27% | 76 / 127 / 321 / 727 |
| `hdl_cholesterol_mg_dl` | 5.30% | 5.27% | 8 / 27 / 104 / 188 |
| `gender_code` | 0.00% | 0.00% | 1 / 1 / 2 / 2 |
| `current_smoker` | 0.12% | 0.10% | 0 / 0 / 1 / 1 |
| `diabetes` | 1.66% | 1.90% | 0 / 0 / 1 / 1 |

All eight predictors are complete in **7,843/8,902 development people** and **2,611/2,941 later-cycle people**. Complete-case analysis would discard participants with missing values; the primary baseline uses fold-fitted imputation to retain them. Event losses are reported separately in the cohort report.

## Cycle review: HDL cholesterol

| NHANES cycle | Observed n | Mean HDL (mg/dL) | Median HDL (mg/dL) | Missing |
| --- | ---: | ---: | ---: | ---: |
| 1999-2000 | 2,008 | 51.45 | 49.0 | 6.91% |
| 2001-2002 | 2,251 | 52.85 | 50.0 | 5.54% |
| 2003-2004 | 2,080 | 54.20 | 52.0 | 4.50% |
| 2005-2006 | 2,091 | 55.16 | 52.0 | 4.26% |
| 2007-2008 | 2,786 | 52.98 | 50.0 | 5.27% |

HDL exceeded total cholesterol for **0** records with both values observed. The CDC documents method changes and cautions against reading 1999-2008 HDL trends without considering assay effects. The cycle means above are unweighted cohort descriptions and must not be interpreted as a national trend. [CDC HDL documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/HDL_E.htm)

## Values flagged for source and clinical review

The observed full-cohort maxima are systolic BP **266 mmHg**, BMI **130.21 kg/m2**, total cholesterol **727 mg/dL**, and HDL cholesterol **188 mg/dL**. These records are not silently removed or set to missing. The cohort builder keeps positive recorded values. The BMI 130.21 record was checked against raw `BMX_D.xpt`: recorded weight 371.0 kg and height 168.8 cm agree with the reported BMI. Before building a patient form, a clinician should decide hard rejection rules and softer 'check this entry' warnings separately; a research-data maximum is not an appropriate clinical limit by itself.

## Open checks

1. Trace the remaining unusual BP and cholesterol values to raw XPT records and source documentation.
2. Run a prespecified sensitivity analysis for influential extremes and HDL measurement changes within development data.
3. Obtain clinical review of input validation ranges and measurement instructions before any form accepts real values.
4. Distinguish unweighted sample metrics from design-aware population estimates; NHANES weights address its complex design. [CDC weighting guidance](https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx)
