# Baseline data dictionary v1

**Study:** 10-year cardiovascular mortality in the US NHANES 1999–2008 public-use linked mortality cohort. **Status:** Cohort audit complete; modeling definitions still require clinical and statistical review.

The 42 original NHANES XPT files, direct CDC URLs, byte counts, and SHA-256 checksums are recorded in [nhanes_source_manifest.csv](nhanes_source_manifest.csv). Raw downloads and the joined person-level cohort are kept under ignored `data/` folders. `SEQN` joins baseline files to the mortality file. All model inputs below are baseline measurements or questionnaire answers.

| Harmonized field | Source | Rule | Important missing/interpretation note |
| --- | --- | --- | --- |
| `age_years` | `DEMO*`: `RIDAGEYR` | Restrict to 40–79 at baseline exam | Age is recorded at screening; this small timing difference is retained as documented by NHANES. |
| `gender_code` | `DEMO*`: `RIAGENDR` | Keep NHANES code 1=male, 2=female | CDC labels this variable “Gender.” Its two codes do not capture gender identity beyond the recorded survey category. |
| `systolic_bp_mmhg` | `BPX*`: `BPXSY1`–`BPXSY4` | Mean of available positive systolic readings | Zero/absent readings become missing. This is a research-defined summary; retain the raw readings for sensitivity analysis. |
| `bmi` | `BMX*`: `BMXBMI` | Keep positive recorded BMI, kg/m² | Extreme values are flagged for review, not silently replaced. |
| `total_cholesterol_mg_dl` | `LAB13`, `L13_B`, `L13_C`, `TCHOL_D`, `TCHOL_E`: `LBXTC` | Keep positive recorded value in mg/dL | Laboratory measurement availability varies across cycles. |
| `hdl_cholesterol_mg_dl` | `LAB13`, `L13_B`: `LBDHDL`; `L13_C`: `LBXHDD`; `HDL_D`, `HDL_E`: `LBDHDD` | Keep positive recorded value in mg/dL | CDC documents changes in HDL assay methods across 1999–2008; assess this as a possible cycle shift. |
| `current_smoker` | `SMQ*`: `SMQ020`, `SMQ040` | 1 if ≥100 lifetime cigarettes and now smokes every/some days; 0 if <100 lifetime cigarettes or no longer smokes | Refused, don't know, or inconsistent/absent answers remain missing. |
| `diabetes` | `DIQ*`: `DIQ010` | 1=yes, 0=no | Borderline/prediabetes (code 3), refused, and don't know remain missing rather than being recoded as no. |
| `cvd_death_10y` | CDC 2019 public-use Linked Mortality File | 1 if death within 120 months of exam and underlying cause `001` (diseases of heart) or `005` (cerebrovascular disease); otherwise 0 when ten-year status is known | This is cardiovascular **mortality**, including the observed competing risk of other-cause death. It does not record nonfatal events. |
| `WTMEC2YR`, `WTMEC4YR`, `SDMVPSU`, `SDMVSTRA` | `DEMO*` | Retained for later design-aware analysis | Combined-cycle weights have not yet been constructed. Use CDC guidance; 1999–2002 requires the supplied four-year weight. |

## Inclusion and exclusion

1. Baseline mobile examination completed (`RIDSTATR=2`) and age 40–79.
2. Eligible for mortality linkage (`ELIGSTAT=1`).
3. Numeric examination-based follow-up (`PERMTH_EXM`) with a known 120-month outcome. People recorded alive with less than 120 months and early deaths lacking cause are excluded.
4. No self-reported prior congestive heart failure, coronary heart disease, angina, myocardial infarction, or stroke (`MCQ160B`–`MCQ160F`). Any “yes” is excluded, then any incomplete/uncertain history is excluded from this primary-prevention cohort.

No participant is dropped solely because a predictor is missing. Complete-case counts are reported as a sensitivity-analysis option; model preprocessing must be fitted within development folds.

## Items deferred from the core model

- Antihypertensive medication is present in `BPQ*`, but `BPQ050A` is asked through conditional branches. It requires a documented cross-cycle derivation before use.
- Physical activity questions are not yet harmonized across all five cycles.
- LDL cholesterol is not included because it is not measured for the full examined population in the same way as total and HDL cholesterol.

## Official documentation

- [NHANES demographics and cycle files](https://wwwn.cdc.gov/nchs/nhanes/Search/DataPage.aspx?Component=Demographics)
- [1999–2000 total and HDL cholesterol](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/1999/DataFiles/LAB13.htm)
- [2007–2008 HDL methods and assay-change note](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/HDL_E.htm)
- [2007–2008 smoking questionnaire](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/SMQ_E.htm)
- [2007–2008 diabetes questionnaire](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/DIQ_E.htm)
- [2005–2006 medical history questionnaire](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2005/DataFiles/MCQ_D.htm)
- [CDC linked mortality codebook](https://www.cdc.gov/nchs/data/datalinkage/public-use-linked-mortality-files-data-dictionary.pdf)
- [CDC NHANES cycle weighting guidance](https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx)
