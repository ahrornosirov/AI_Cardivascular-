# Dataset feasibility: first mortality-file audit

**Date:** 5 October 2026. **Status:** Preliminary source-file check. These counts include all mortality-linkage-eligible adults and precede the proposed age and prior-CVD exclusions, predictor joins, and missingness analysis.

The official CDC 2019 public-use linked mortality files were read using the fixed-width positions in CDC's `R_ReadInProgramAllSurveys.R`. For each cycle, “known ten-year outcome” means linkage eligible, a numeric examination-based follow-up time, and either recorded as deceased with a known cause within ten years or followed at least 120 months from the examination. An event is underlying cause `001` (diseases of heart) or `005` (cerebrovascular diseases), death within 120 months of the exam. The audit is reproducible with `/opt/homebrew/bin/python3 scripts/audit_mortality.py` from the repository root on this machine, or another Python installation with working HTTPS certificates.

| NHANES cycle | File rows | Linkage-eligible adults | Known 10-year outcome | 10-year CVD deaths | Crude rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1999–2000 | 9,965 | 5,445 | 4,973 | 249 | 5.01% |
| 2001–2002 | 11,039 | 5,987 | 5,585 | 247 | 4.42% |
| 2003–2004 | 10,122 | 5,610 | 5,293 | 277 | 5.23% |
| 2005–2006 | 10,348 | 5,561 | 5,332 | 219 | 4.11% |
| **Development candidate total** | **41,474** | **22,603** | **21,183** | **992** | **4.68%** |
| **2007–2008 evaluation candidate** | **10,149** | **6,219** | **5,989** | **256** | **4.27%** |

These are unweighted counts from mortality files only. They are **not** results of the proposed model, and the crude rate is not a population risk estimate. Linkage-eligible people without numeric examination-based follow-up time are excluded from the known-outcome denominator. One early death in 2001–2002 has no listed underlying cause and is excluded. Baseline predictor files still need auditing. The CDC warns that some public-use follow-up times or causes of death were replaced with synthetic values for privacy. Any paper must state that limitation and consider restricted-use verification.

Downloaded file SHA-256 checksums, in cycle order: `562bd367107add0b2b40fed36a062d8b194fca31e11aab897a0efad4bebc8b26`, `2788c8c8a02995ea5686882b5fe65b4b9cd415016031525f8a3c1a3646c47f1b`, `639f6b3292a55b112fbfc842954af3d8d32bcce287cd8ae49319e5aca1c033c0`, `69388ea13a4f395f29d9d21bc51941b9759003490d4b00f6ff12a1bc5f8dba5c`, `75f89bd545a13ba726a7eb56de4d62f6dfc8f0f76d505dc18ced9752d5e2c77d`.

Next gate: join `SEQN` to the cycle-specific NHANES examination, lab, demographic, and questionnaire files; harmonize baseline variables; apply cohort exclusions; recount events; and assess missingness before training.

Sources: [CDC linked mortality documentation](https://www.cdc.gov/nchs/linked-data/mortality-files/index.html), [CDC codebook](https://www.cdc.gov/nchs/data/datalinkage/public-use-linked-mortality-files-data-dictionary.pdf), and [CDC official read-in program directory](https://ftp.cdc.gov/pub/Health_Statistics/NCHS/datalinkage/linked_mortality/).
