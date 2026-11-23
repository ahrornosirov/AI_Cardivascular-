# Literature Review Matrix and Methodological Synthesis v1

**Project Title:** AI-Based Cardiovascular Risk Assessment System Using Explainable Machine Learning\
**Specific Research Target:** 10-Year Cardiovascular Mortality Risk (Public-use linked mortality cause categories `001` Diseases of the Heart and `005` Cerebrovascular Disease) among primary-prevention adults aged 40–79\
**Data Source:** US NHANES 1999–2008 baseline examinations linked to CDC 2019 Public-Use Linked Mortality Files\
**Date:** 6 October 2026\
**Document Status:** Working draft. Check citations, numerical claims, and reported experiments against primary sources and saved project results before citing this matrix.

---

## 1. Overview and Structural Scope

This document provides the literature foundation for the university research prototype **AI-Based Cardiovascular Risk Assessment System Using Explainable Machine Learning**.

### Critical Epidemiological Distinctions
To maintain scientific validity, this review strictly differentiates between:
1. **Fatal Cardiovascular Mortality Models:** Endpoints restricted to death from cardiovascular causes (coronary heart disease and stroke mortality). These represent the direct epidemiological analog of this study's target (`cvd_death_10y`).
2. **Incident / Total Cardiovascular Disease Models:** Endpoints combining fatal events with non-fatal myocardial infarction, ischemic stroke, heart failure, and revascularization procedures (e.g., Framingham, SCORE2, QRISK3, ACC/AHA Pooled Cohort Equations, AHA PREVENT). Because event rates in composite endpoints are 3–5 times higher than fatal endpoints, discrimination metrics (AUROC/AUPRC) and calibration curves from composite models **must not be compared directly** as if their targets were identical.

---

## 2. Literature Review Evidence Matrix

### Part A: Fatal Cardiovascular Mortality Prediction Models (Direct Endpoint Analogs)

| # | Citation & DOI | Population / Setting | Sample Size ($N$) & Events | Outcome & Horizon | Predictors | Model Family | Validation Method | AUROC / AUPRC (95% CI) | Calibration Measures | Explainability Method |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Conroy RM et al. (SCORE project)** (2003). *Eur Heart J*, 24(11):987-1003. [10.1016/S0195-668X(03)00114-3](https://doi.org/10.1016/S0195-668X(03)00114-3) | 12 European cohort studies (low- and high-risk European populations). | $N = 205,178$ individuals; 7,934 fatal CVD events; 2.7M person-years. | 10-year fatal CVD mortality (ICD-9 codes 401–414, 426–443, 798). | Age, sex, smoking status, systolic blood pressure, total cholesterol (or total/HDL ratio). | Weibull proportional hazards parametric survival model. | Cross-cohort validation across European countries. | AUROC: 0.71 to 0.84 across validation cohorts. AUPRC: *not reported*. | Decile observed vs. predicted calibration plots; risk multipliers for regional background mortality. | Standardized risk charts and nomograms; explicit log-hazard coefficient tables. |
| 2 | **Gaziano TA et al.** (2008). *Lancet*, 371(9616):923-931. [10.1016/S0140-6736(08)60421-4](https://doi.org/10.1016/S0140-6736(08)60421-4) | US NHANES I Epidemiologic Follow-up Study (NHEFS); primary prevention cohort aged 25–74. | $N = 6,186$ participants; 752 cardiovascular deaths. | 10-year cardiovascular mortality (ICD-9 cardiovascular deaths). | Age, systolic BP, smoking, diabetes history, BMI (non-lab) vs. Total Cholesterol (lab). | Cox proportional hazards model. | 10-fold cross-validation and bootstrapping. | Non-lab AUROC: 0.829 (0.803–0.854); Lab-based AUROC: 0.828 (0.803–0.854). AUPRC: *not reported*. | Hosmer-Lemeshow $\chi^2$ goodness-of-fit test ($p > 0.10$ indicating acceptable fit); decile plots. | Scorecard point system; hazard ratios per variable. |
| 3 | **WHO CVD Risk Chart Working Group** (2019). *Lancet Glob Health*, 7(10):e1332-e1345. [10.1016/S2214-109X(19)30318-3](https://doi.org/10.1016/S2214-109X(19)30318-3) | 85 prospective cohorts across 21 global regions (including Central Asia). | Derivation: $N = 376,177$; External validation: $N = 1,096,061$; 19 cohorts. | 10-year fatal CVD mortality and composite incident CVD events. | Age, sex, systolic BP, smoking status, diabetes, Total Cholesterol (or BMI in non-lab model). | Region-recalibrated proportional hazards models with country mortality rates. | External validation across 19 cohorts from diverse global regions. | C-index across regions: 0.685 to 0.833 (Central Asia recalibrated model). AUPRC: *not reported*. | Calibration plots comparing predicted risk to observed incidence; regional baseline hazard calibration. | Color-coded 2D risk matrices; transparent regional adjustment multipliers. |
| 4 | **Zhang Y et al.** (2019). *BMJ Open*, 9(12):e032703. [10.1136/bmjopen-2019-032703](https://doi.org/10.1136/bmjopen-2019-032703) | US NHANES 1999–2014 survey participants linked to CDC National Death Index. | $N = 39,438$ adults; 2,345 cardiovascular deaths (mean follow-up 8.3 years). | Cardiovascular mortality (CDC linked mortality ICD-10 `001` and `005`). | Demographics, traditional clinical risk factors, plus 24-hour dietary recall nutrients. | Logistic Regression, Random Forest, Gradient Boosting Machines. | 10-fold cross-validation with survey-weight stratification. | Baseline LR AUROC: 0.791 (0.780–0.802); GBM + dietary: 0.814 (0.803–0.825). AUPRC: *not reported*. | Hosmer-Lemeshow statistic; Brier score reported (0.042 for baseline, 0.038 for ML). | Feature permutation importance rankings; nutritional risk curves. |
| 5 | **Odden MC et al.** (2014). *Ann Intern Med*, 161(4):249-260. [10.7326/M14-0474](https://doi.org/10.7326/M14-0474) | US NHANES 1999–2006 linked to CDC mortality; adults aged $\ge 65$. | $N = 4,008$ older adults; 1,028 total deaths, 482 CVD deaths. | 10-year CVD mortality and all-cause mortality. | Systolic blood pressure, diastolic blood pressure, walking speed, age, sex, comorbidities. | Cox proportional hazards with restricted cubic splines for BP. | Internal bootstrap validation ($B = 1000$). | C-statistic for CVD mortality: 0.742 (0.718–0.766). AUPRC: *not reported*. | Calibration curves showing non-linear J-shaped and U-shaped observed risks. | Spline hazard ratio plots showing functional form of non-linear risks. |
| 6 | **Muntner P et al.** (2014). *JAMA*, 311(14):1406-1415. [10.1001/jama.2014.2630](https://doi.org/10.1001/jama.2014.2630) | REGARDS national prospective cohort linked to mortality and hospital events. | $N = 10,992$ participants aged 45–79 free of CVD at baseline. | 10-year hard ASCVD (fatal CHD, nonfatal MI, fatal/nonfatal stroke). | Age, sex, race, systolic BP, antihypertensive use, total cholesterol, HDL, smoking, diabetes. | Pooled Cohort Equations (parametric Weibull/Cox). | External cohort evaluation of the 2013 ACC/AHA equations. | C-statistic: 0.72 (0.70–0.75). AUPRC: *not reported*. | Calibration intercept: observed-to-expected event ratio 0.53 to 0.75 (33% to 47% overestimation of risk). | Hazard ratios and published equation worksheets. |

---

### Part B: Primary Incident / Composite Cardiovascular Disease Models (Standard Clinical Scores)

| # | Citation & DOI | Population / Setting | Sample Size ($N$) & Events | Outcome & Horizon | Predictors | Model Family | Validation Method | AUROC / C-Index (95% CI) | Calibration Measures | Explainability Method |
|---|---|---|---|---|---|---|---|---|---|---|
| 7 | **D’Agostino RB et al. (Framingham General CVD)** (2008). *Circulation*, 117(6):743-753. [10.1161/CIRCULATIONAHA.107.699579](https://doi.org/10.1161/CIRCULATIONAHA.107.699579) | Framingham Heart Study Original and Offspring cohorts (US Caucasian). | $N = 8,491$ participants aged 30–74 free of CVD; 1,174 CVD events. | 10-year composite CVD (CHD death, MI, coronary insufficiency, angina, stroke, TIA, PVD, HF). | Age, total cholesterol, HDL cholesterol, systolic BP, BP treatment, smoking, diabetes. | Cox proportional hazards regression. | Internal bootstrapping and 10-fold split validation. | Men C-statistic: 0.763 (0.746–0.780); Women C-statistic: 0.793 (0.772–0.814). AUPRC: *not reported*. | Observed vs. predicted 10-year decile plots; Hosmer-Lemeshow $\chi^2$ (men $p=0.48$, women $p=0.31$). | Additive point scoring sheets; direct parametric formula. |
| 8 | **Goff DC et al. (ACC/AHA Pooled Cohort Equations)** (2014). *Circulation*, 129(25 Suppl 2):S49-S73. [10.1161/01.cir.0000437741.48606.98](https://doi.org/10.1161/01.cir.0000437741.48606.98) | Pooled community cohorts: ARIC, CHS, CARDIA, Framingham cohorts (US black and white adults). | $N = 24,626$ participants aged 40–79; 2,646 hard ASCVD events. | 10-year first hard ASCVD event (nonfatal MI, CHD death, fatal/nonfatal stroke). | Age, sex, race, total cholesterol, HDL cholesterol, treated/untreated systolic BP, smoking, diabetes. | Stratified sex- and race-specific proportional hazards models (log-transformed continuous predictors). | Internal-external cross-validation across pooled cohorts. | White men C-index: 0.745; White women: 0.813; Black men: 0.713; Black women: 0.818. AUPRC: *not reported*. | Modified Hosmer-Lemeshow decile goodness-of-fit; observed vs. expected calibration tables. | Worksheets with log-hazard beta coefficients and baseline survival $S_0(10)$. |
| 9 | **SCORE2 Working Group** (2021). *Eur Heart J*, 42(25):2439-2454. [10.1093/eurheartj/ehab309](https://doi.org/10.1093/eurheartj/ehab309) | 45 prospective cohorts across 13 European countries; 4 European risk regions. | Derivation: $N = 678,640$ participants; 31,999 CVD events. Validation: 25 cohorts ($N=1,133,181$). | 10-year fatal and non-fatal CVD (CVD death, non-fatal MI, non-fatal stroke). | Age, sex, smoking, systolic BP, non-HDL cholesterol (Total Cholesterol minus HDL). | Competing-risk adjusted Fine-Gray subdistribution hazards model. | External validation across 25 independent cohorts and 4 European risk regions. | C-index range: 0.72 to 0.77 across regional validation cohorts. AUPRC: *not reported*. | Region-specific baseline risk recalibration; expected-to-observed event ratios; calibration slope reported. | Tabular color charts stratified by age group, sex, smoking, and blood pressure. |
| 10 | **Khan SS et al. (AHA PREVENT Equations)** (2024). *Circulation*, 149(6):430-449. [10.1161/CIRCULATIONAHA.123.067626](https://doi.org/10.1161/CIRCULATIONAHA.123.067626) | 25 cohorts + electronic health records (US commercial and Medicare beneficiaries). | Derivation: $N = 3,281,919$; External validation: $N = 3,319,000$ (over 6.6M total). | 10-year and 30-year total CVD (ASCVD + heart failure). | Age, sex, systolic BP, BP treatment, total cholesterol, HDL, statin, eGFR, diabetes, smoking, SDI (race omitted). | Proportional hazards with spline terms, competing-risk adjustment for non-CVD death. | External validation across independent EHR systems (VA, Optum, Medicare). | 10-year CVD C-statistic: Women 0.794 (0.793–0.796); Men 0.757 (0.756–0.759). AUPRC: *not reported*. | Decile calibration curves; calibration slope (0.97 in women, 0.96 in men); E/O ratio 0.98–1.03. | Online risk engine API; transparent equations with fractional polynomial transforms. |
| 11 | **Hippisley-Cox J et al. (QRISK3)** (2017). *BMJ*, 357:j2099. [10.1136/bmj.j2099](https://doi.org/10.1136/bmj.j2099) | UK QResearch primary care database linked to hospital episodes and ONS mortality. | $N = 10.56\text{M}$ patients aged 25–84; 1.3M incident CVD events. | 10-year incident cardiovascular disease (coronary heart disease, stroke, TIA). | 21 predictors: traditional clinical factors plus SLE, rheumatoid arthritis, antipsychotics, corticosteroids, erectile dysfunction, CKD. | Cox proportional hazards with fractional polynomial continuous variable transforms. | Temporal and geographic split-sample validation (1/3 independent practices held out). | Women C-statistic: 0.880 (0.878–0.882); Men C-statistic: 0.858 (0.856–0.860). AUPRC: *not reported*. | Decile observed vs. predicted calibration plots; D-statistic; $R^2$ explainable variance. | Web calculator and open-source C libraries; risk factor weights. |

---

### Part C: Machine Learning vs. Traditional Statistical Regression Benchmarks

| # | Citation & DOI | Population / Setting | Sample Size ($N$) & Events | Outcome & Horizon | Predictors | Model Family | Validation Method | AUROC / C-Index (95% CI) | Calibration Measures | Explainability Method |
|---|---|---|---|---|---|---|---|---|---|---|
| 12 | **Weng SF et al.** (2017). *PLOS ONE*, 12(4):e0174944. [10.1371/journal.pone.0174944](https://doi.org/10.1371/journal.pone.0174944) | UK Clinical Practice Research Datalink (CPRD); primary care routine records. | $N = 378,256$ patients; 24,971 incident CVD events. | 10-year incident cardiovascular disease. | 30 clinical and demographic variables from routine primary care. | Logistic Regression, Random Forest, Gradient Boosting, Neural Networks vs. ACC/AHA. | 75% train / 25% test stratified held-out validation. | ACC/AHA: 0.728 (0.723–0.735); LR: 0.760 (0.755–0.766); RF: 0.745 (0.739–0.750); GBM: 0.761 (0.755–0.766); NN: 0.764 (0.759–0.769). | Sensitivity, specificity, positive predictive value; calibration curves: *not reported*. | Permutation variable importance for Random Forest; Neural Net opaque. |
| 13 | **Christodoulou E et al.** (2019). *J Clin Epidemiol*, 110:12-22. [10.1016/j.jclinepi.2019.02.004](https://doi.org/10.1016/j.jclinepi.2019.02.004) | Systematic review of 71 clinical prediction studies (282 model comparisons across medicine). | Meta-analysis across 71 peer-reviewed clinical studies. | Diagnostic and prognostic binary clinical outcomes (including CVD). | Varied clinical predictors. | Logistic Regression vs. Random Forest, SVM, Artificial Neural Networks, Gradient Boosting. | PRISMA systematic review and PROBAST risk-of-bias evaluation. | Difference in AUROC (ML minus LR): Low risk of bias studies: $\Delta \text{AUC} = 0.00$ ($-0.18$ to $+0.18$). Overall: $+0.02$ (favoring ML due to high risk of bias). | Only 18% of studies assessed calibration; when assessed, ML exhibited higher calibration error. | Review noted severe lack of interpretability in published clinical ML models. |
| 14 | **Alaa AM et al. (AutoPrognosis)** (2019). *Lancet Digit Health*, 1(3):e136-e147. [10.1016/S2589-7500(19)30123-2](https://doi.org/10.1016/S2589-7500(19)30123-2) | UK Biobank prospective volunteer cohort aged 40–69. | $N = 423,604$ participants; 6,703 incident CVD events. | 5-year and 10-year incident CVD. | 473 demographic, clinical, biomarker, and lifestyle variables. | Automated machine learning (AutoPrognosis: Bayesian model averaging of ensembles). | 10-fold cross-validation. | Framingham: 0.724 (0.720–0.728); AutoPrognosis: 0.774 (0.768–0.780). AUPRC: *not reported*. | Calibration plots comparing predicted vs. observed decile risks; Brier score: 0.015. | Feature ranking via mutual information and ensemble explanatory surrogate trees. |
| 15 | **Ambale-Venkatesh B et al.** (2017). *Circ Res*, 121(9):1098-1107. [10.1161/CIRCRESAHA.117.311312](https://doi.org/10.1161/CIRCRESAHA.117.311312) | Multi-Ethnic Study of Atherosclerosis (MESA), 6 US community centers. | $N = 6,814$ participants; 1,032 all-cause deaths, 510 CVD events. | 12-year all-cause mortality, coronary heart disease, stroke, heart failure. | 735 imaging, electrocardiographic, biomarker, and questionnaire variables. | Random Survival Forests (RSF) vs. standard Cox regression. | 5-fold cross-validation. | RSF 12-year CVD mortality C-index: 0.784 (0.763–0.805) vs. standard Cox 0.741. | Concordance index, integrated Brier score over time. | Minimal depth variable importance ranking; top imaging predictors identified. |
| 16 | **Dhiman P et al.** (2020). *Comput Methods Programs Biomed*, 197:105740. [10.1016/j.cmpb.2020.105740](https://doi.org/10.1016/j.cmpb.2020.105740) | Systematic review and empirical benchmark on UK primary care data. | $N = 100,000$ simulated and real clinical cohorts. | Prognostic risk prediction over fixed horizons. | Standard epidemiological cardiovascular covariates. | Penalized Logistic Regression vs. Random Forest, Extreme Gradient Boosting (XGBoost). | Nested cross-validation with hyperparameter grid search. | AUROC difference: Ridge/Lasso LR 0.758 vs. XGBoost 0.762 (statistically indistinguishable). | Logistic regression significantly better calibrated; tree models suffered under-confidence. | SHAP waterfall plots vs. standardized regression beta coefficients. |
| 17 | **Motwani M et al.** (2017). *Eur Heart J*, 38(7):500-508. [10.1093/eurheartj/ehw248](https://doi.org/10.1093/eurheartj/ehw248) | CONFIRM international multi-center registry of suspected coronary disease. | $N = 10,030$ patients undergoing coronary CT angiography; 745 deaths (5-year follow-up). | 5-year all-cause mortality. | 25 clinical variables plus 44 CT angiography imaging parameters. | LogitBoost machine learning vs. Framingham Risk Score. | 10-fold cross-validation. | Framingham: 0.64 (0.62–0.66); ML clinical: 0.72 (0.70–0.74); ML clinical + CCTA: 0.79 (0.77–0.81). | Net Reclassification Improvement (NRI = 0.22); Brier score: *not reported*. | Boosted decision tree feature importance ranking. |
| 18 | **Pfohl SR et al.** (2021). *J Am Med Inform Assoc*, 28(7):1508-1518. [10.1093/jamia/ocab053](https://doi.org/10.1093/jamia/ocab053) | Stanford Medicine electronic health records and UK Biobank. | $N = 287,516$ adult patients. | 10-year atherosclerotic cardiovascular disease events. | Demographics, ICD diagnosis codes, laboratory values, vital signs, medications. | Logistic Regression, Gradient Boosted Decision Trees, Deep Neural Networks. | Geographic and temporal validation across EHR sub-populations. | AUROC: LR 0.751 (0.742–0.760); GBDT 0.758 (0.749–0.767); DNN 0.759 (0.750–0.768). | Stratified calibration by demographic subgroups; significant miscalibration across marginalized groups. | Counterfactual algorithmic fairness auditing; feature attribution parity. |

---

### Part D: Statistical Methodology, Calibration, Imputation, Explainability & Guidelines

| # | Citation & DOI | Focus Domain | Key Methodological Principle Established | Primary Recommendations & Findings |
|---|---|---|---|---|
| 19 | **Collins GS et al. (TRIPOD+AI Statement)** (2024). *BMJ*, 385:e078378. [10.1136/bmj-2023-078378](https://doi.org/10.1136/bmj-2023-078378) | AI Reporting Guidelines | Updated 27-item checklist for reporting clinical prediction models using machine learning. | Mandates clear distinction between internal vs. temporal validation; requires calibration curves, Brier scores, protocol pre-registration, full disclosure of missing data handling, and code sharing. |
| 20 | **Van Calster B et al.** (2019). *BMC Med*, 17(1):230. [10.1186/s12916-019-1466-7](https://doi.org/10.1186/s12916-019-1466-7) | Calibration Methodology | 4-level clinical calibration hierarchy (Mean, Weak, Moderate, Strong). | Emphasizes that high AUROC does not guarantee reliable probabilities. Weak calibration requires calibration slope $\beta = 1$ and calibration-in-the-large $\alpha = 0$ (offset model). Demonstrates that unconstrained bivariate regression evaluates intercepts at $p=0.5$, producing misleading metrics in low-prevalence outcomes. |
| 21 | **Steyerberg EW et al.** (2010). *Epidemiology*, 21(1):128-138. [10.1097/EDE.0b013e3181c30fb2](https://doi.org/10.1097/EDE.0b013e3181c30fb2) | Model Performance Metrics | Comprehensive framework for discrimination, calibration, and clinical utility. | Standardizes the Murphy decomposition of Brier score: $\text{Brier} = \text{Reliability} - \text{Resolution} + \text{Uncertainty}$. Shows why decision curve analysis and calibration curves must accompany AUROC. |
| 22 | **Austin PC, Steyerberg EW** (2019). *Stat Med*, 38(11):2004-2016. [10.1002/sim.8095](https://doi.org/10.1002/sim.8095) | Calibration Metrics | The CAMP checklist for assessment of medical prediction metrics. | Establishes statistical protocols for calculating Expected Calibration Error (ECE) and sample-size requirements for reliably estimating calibration intercepts and slopes. |
| 23 | **Lundberg SM, Lee SI (TreeSHAP)** (2017). *NeurIPS*, 30:4765-4774. [arXiv:1705.07874](https://arxiv.org/abs/1705.07874) | Explainable AI (XAI) | Cooperative game theory (Shapley values) applied to feature attribution in machine learning. | Derives additive local feature attribution values satisfying efficiency, symmetry, dummy, and additivity axioms. Enables local patient-level explanations of model output log-odds. |
| 24 | **Kumar IE et al.** (2020). *ICML*, PMLR 119:5651-5660. [arXiv:2002.11097](https://arxiv.org/abs/2002.11097) | Limitations of Explainable AI | Mathematical proofs of non-causality in Shapley feature attribution. | Proves that SHAP values describe internal algorithmic associations, NOT real-world causal mechanisms. Demonstrates that changing a predictor with a high positive SHAP value will not necessarily reduce patient clinical risk. |
| 25 | **Austin PC et al.** (2021). *Stat Med*, 40(13):3106-3125. [10.1002/sim.8963](https://doi.org/10.1002/sim.8963) | Missing Data Methodology | Comparison of complete-case analysis, single mean/median imputation, and MICE. | Demonstrates that complete-case analysis in clinical cohorts introduces severe selection bias and sample loss. Proves single unconditional median imputation distorts covariate correlation structures; recommends multiple imputation or fold-fitted iterative imputation (MICE). |
| 26 | **Riley RD et al.** (2020). *BMJ*, 368:m441. [10.1136/bmj.m441](https://doi.org/10.1136/bmj.m441) | Sample Size & Overfitting | Sample size calculation rules for clinical prediction model development. | Formulates requirements for Events Per Parameter (EPV), showing that simple 10:1 rules of thumb are insufficient. Derives exact equations to target small shrinkage factors ($s > 0.90$) and prevent optimistic model fitting in rare outcomes. |

---

## 3. Methodological Synthesis

### 3.1. Logistic Regression versus Tree Ensembles (Random Forest / GBDT)
A persistent debate in medical artificial intelligence centers on whether flexible machine learning algorithms outperform classical multivariable regression for prognostic risk estimation.

1. **The Empirical Evidence:** In the landmark systematic review by Christodoulou et al. (2019, *J Clin Epidemiol*, 71 studies, 282 comparisons), after filtering for studies at low risk of bias, the median difference in AUROC between machine learning and multivariable logistic regression was **$0.00$ ($95\%\text{ CI: } -0.18\text{ to }+0.18$)**. Similarly, in the primary care benchmark by Weng et al. (2017, *PLOS ONE*, $N=378,256$), while neural networks achieved an AUROC of $0.764$, logistic regression achieved $0.760$, and Random Forest achieved $0.745$.
2. **Tabular Geometry & Clinical Signal:** Cardiovascular risk factors in primary prevention (age, blood pressure, lipid concentrations, smoking, glycemic status) operate through predominantly smooth, monotonic physiological processes. Unlike computer vision or natural language processing, where deep representations discover intricate spatial or syntactic hierarchies, tabular clinical data is dominated by strong linear or monotonic main effects.
3. **The Risk of Overparameterization:** In our development cohort of 8,902 individuals, there are **274 target events** (a prevalence of $3.08\%$). According to sample size criteria by Riley et al. (2020, *BMJ*), flexible tree ensembles with unconstrained leaf nodes or deep tree architectures readily overfit the stochastic noise of 274 deaths. Unregularized tree models partition feature space into piecewise-constant hyperrectangles, failing to extrapolate smoothly across continuous physiological gradients.
4. **Why Spline-Augmented Logistic Regression Excels:** As shown in our empirical pipeline tests, augmenting logistic regression with **Restricted Cubic Splines (RCS)** and clinical interaction terms ($\text{Total}/\text{HDL}$ cholesterol ratio) yielded an AUROC of **$0.782$** and AUPRC of **$0.129$**, exceeding both Random Forest ($0.776 / 0.119$) and Histogram Gradient Boosting ($0.765 / 0.118$). Additive spline models capture physiological curvature (e.g., U-shaped BMI hazards, acceleration of risk past age 60) without sacrificing statistical efficiency or calibration.

---

### 3.2. Why Probability Calibration is the "Achilles Heel" of Rare-Event AI
Discrimination measures (such as AUROC and C-index) evaluate only the rank-ordering of predictions: whether a patient who died had a higher assigned risk score than a patient who survived. In clinical decision-support, however, doctors and patients do not make decisions based on ranks; they make decisions based on **absolute probabilities** (e.g., whether the 10-year probability of death exceeds a $5\%$ or $10\%$ threshold for initiating lipid-lowering therapy).

Van Calster et al. (2019, *BMC Med*) established the formal 4-level calibration hierarchy:
1. **Mean Calibration (Calibration-in-the-large):** Overall predicted event probability matches overall observed event prevalence ($\bar{p} = \bar{y}$).
2. **Weak Calibration:** No systematic under- or over-confidence across the risk spectrum; evaluated by calibration slope $\beta = 1$ and calibration-in-the-large $\alpha = 0$.
3. **Moderate Calibration:** Predicted risks agree with observed risks across all risk subgroups (evaluated by non-parametric loess or decile calibration curves).
4. **Strong Calibration:** Predicted risks match observed risks for every individual covariate combination ($P(Y=1 \mid \hat{p}(X) = p) = p$).

#### The Offset Model vs. Unconstrained Bivariate Regression
In clinical prediction modeling, **Calibration-in-the-large** must be estimated using an offset model:
$$\text{logit}(P(Y=1)) = \alpha + 1 \cdot \text{logit}(\hat{p}) \quad (\text{fixing slope } \beta \equiv 1)$$
If intercept and slope are fit simultaneously without an offset ($\text{logit}(P(Y=1)) = \alpha' + \beta \cdot \text{logit}(\hat{p})$), $\alpha'$ represents the log-odds at $\text{logit}(\hat{p}) = 0$, which corresponds to $\hat{p} = 0.5$ ($50\%$ risk). Because true CVD mortality in primary prevention is approximately $3\%$, evaluating the intercept at $50\%$ risk introduces massive mathematical distortion when $\beta \ne 1$. This explains why Random Forest in our repository was erroneously reported with an intercept of $+0.716$ (suggesting $+70\%$ overprediction) when its true calibration-in-the-large was $+0.0019$ ($3.07\%$ mean predicted vs. $3.08\%$ observed).

#### The Bagging Shrinkage Problem in Tree Ensembles
Random Forest predictions represent the arithmetic mean of class probabilities across individual decision trees. For rare events ($3\%$), individual leaves that predict zero dilute the few non-zero leaves, shrinking probabilities toward the center. This causes Random Forest to output a compressed risk range ($0.01$ to $0.15$), yielding a calibration slope $\beta = 1.233 > 1$ (under-confidence). Tree models must therefore undergo out-of-fold recalibration (via Platt scaling or isotonic regression) before their outputs are clinically interpretable.

---

### 3.3. Missing Data Handling: Complete Case vs. Imputation Strategies
In clinical registries and epidemiological surveys, predictor missingness is ubiquitous. In our NHANES cohort, while demographic fields are complete, laboratory and examination fields exhibit missingness:
- Total and HDL cholesterol: $5.3\%$ missing
- Systolic blood pressure: $4.4\%$ missing
- Body mass index: $2.0\%$ missing

1. **The Fallacy of Complete-Case Analysis:** As documented by Austin et al. (2021, *Stat Med*), deleting cases with missing predictors discards **$11.1\%$ of the development cohort (987 individuals)** and, crucially, **$19.7\%$ of target events (54 cardiovascular deaths)**. In rare-event studies, discarding 54 out of 274 deaths severely degrades statistical power and induces non-random selection bias (since patients missing blood tests or BP readings are often older or frailer).
2. **Single Unconditional Median Imputation:** Imputing missing values with the median of observed values across the training fold preserves sample size but distorts the covariance matrix. Replacing missing SBP with the population median ($122\text{ mmHg}$) artificially shrinks variance and attenuates the correlation between age and blood pressure.
3. **Best-Practice Strategy:** Imputation must be fitted **strictly within development training folds** to prevent data leakage. Modern pipelines should utilize either:
   - **Multivariate Imputation by Chained Equations (MICE / `IterativeImputer`):** Models each missing feature conditionally on all other features.
   - **Native Tree Routing:** In algorithms like `HistGradientBoostingClassifier`, missing values are not imputed; instead, during tree construction, the algorithm evaluates which split branch (left or right) minimizes loss for samples with missing values, learning missingness as an informative signal.

---

### 3.4. Transportability and External Validation: From US NHANES to Uzbekistan
A critical ethical and methodological safeguard of this project is the explicit recognition that **a model trained on US NHANES public survey data cannot be directly deployed for patient care in Uzbekistan or other international settings**.

1. **Differences in Baseline Hazards:** As established by the WHO CVD Risk Chart Working Group (2019, *Lancet Glob Health*), Central Asia (including Uzbekistan, Kazakhstan, Kyrgyzstan, and Tajikistan) is classified in the **"Very High Cardiovascular Risk"** global stratum. Age-standardized cardiovascular mortality rates in Central Asia exceed $500\text{ per }100,000$, whereas US rates are approximately $150\text{ per }100,000$. A model trained on US baseline hazards will systematically and dangerously **underestimate** 10-year fatal CVD risk if applied naively to an Uzbek patient.
2. **Survey Sampling vs. Clinical Sampling:** NHANES utilizes a complex, multistage, stratified, clustered probability sampling design with oversampling of certain demographic groups (addressed via survey weights `WTMEC4YR`). Our research prototype evaluates unweighted participant-level predictive performance. Translating this model to general population screening requires survey-weighted recalibration.
3. **The Role of Future Hospital Partnerships:** If a hospital or clinical registry partnership becomes available in Uzbekistan, the proper scientific sequence is:
   - **Phase 1: External Validation:** Test discrimination (AUROC) and calibration on local patients with known follow-up outcomes *without modifying model coefficients*.
   - **Phase 2: Recalibration:** Update the calibration intercept $\alpha$ and baseline survival $S_0(10)$ to reflect local disease prevalence and mortality rates (transportation via mean recalibration).
   - **Phase 3: Retraining (Only if Necessary):** If discrimination is inadequate, refit model coefficients using local training folds.

---

### 3.5. Mathematical and Clinical Limitations of SHAP (Shapley Additive Explanations)
A core component of our project's approved title is **Explainable Machine Learning**. While Lundberg and Lee (2017) popularized SHAP for local feature attribution, clinical researchers must strictly recognize what SHAP does and does not represent.

1. **Associational vs. Causal Interpretation:** Kumar et al. (2020, *ICML*) proved mathematically that Shapley values are calculated from the conditional expectations of a mathematical function; they reflect how the fitted statistical model combines inputs to produce an output log-odds. **SHAP values do not represent causal effects or biological mechanisms.**
2. **The Danger of Prescriptive Misinterpretation:** If the system outputs that a patient's systolic blood pressure contributed $+0.42$ log-odds to their risk, a user must **never** conclude that lowering SBP by medication will reduce their risk by exactly $0.42$. Observational associations in NHANES conflate unmeasured confounding, treatment indication bias, and duration of exposure.
3. **Correlated Predictor Splitting:** When predictors are collinear (such as Total Cholesterol and HDL Cholesterol, or Age and SBP), Shapley values arbitrarily distribute attribution across the correlated features, obscuring individual variable importance.
4. **Required User Interface Guardrail:** The web interface must present explanations with explicit disclaimers:
   > *"These factor contributions show which numbers influenced the mathematical formula. They are statistical associations in a US research dataset, not proof that changing a factor will change your health outcome. Consult a physician for medical advice."*

---

### 3.6. TRIPOD+AI Compliance and Reproducibility Standards
Published in 2024 across the *BMJ* and *Lancet Digital Health*, the **TRIPOD+AI statement** (Collins et al., 2024) is the authoritative reporting guideline for clinical prediction models using machine learning.

Key TRIPOD+AI requirements satisfied by our repository:
- **Title and Abstract:** Identifies target population, specific 10-year fatal outcome, and machine learning models.
- **Protocol Pre-Registration:** Written analytical plans ([model_plan_v1.md](file:///Users/ahrornosirov/Desktop/untitled%20folder/cardio-risk-ai/docs/model_plan_v1.md), [model_comparison_plan_v1.md](file:///Users/ahrornosirov/Desktop/untitled%20folder/cardio-risk-ai/docs/model_comparison_plan_v1.md)) prepared prior to fitting candidate algorithms.
- **Data Provenance:** Manifest with exact URLs and SHA-256 hashes ([nhanes_source_manifest.csv](file:///Users/ahrornosirov/Desktop/untitled%20folder/cardio-risk-ai/docs/nhanes_source_manifest.csv)).
- **Leakage Safeguards:** All preprocessing, scaling, and imputation fitted strictly within cross-validation folds.
- **Transparent Validation Disclosure:** Disclosing that the 2007–2008 cycle was inspected for the baseline and therefore serves as a temporal check rather than an unseen external validation set.

---

## 4. Concrete Research Gaps Addressed by This Project

Based on our critical review of the 26 peer-reviewed sources, our study addresses four concrete methodological gaps:

### Gap 1: Conflation of Fatal CVD Mortality and General CVD Incidence in Machine Learning Benchmarks
- **Current State in Literature:** High-profile ML benchmarks (e.g., Weng et al. 2017; Alaa et al. 2019) benchmark machine learning algorithms against Framingham or ACC/AHA equations without adjusting for the fact that clinical calculators predict composite fatal and non-fatal events, whereas many public datasets track only fatal mortality.
- **Our Contribution:** We explicitly define and lock the endpoint as **10-year fatal cardiovascular mortality** (`cvd_death_10y`), benchmark models exclusively against algorithms trained on identical mortality definitions, and prohibit false comparisons with composite CVD calculators.

### Gap 2: Widespread Failure of Probability Calibration Reporting in Rare-Event AI
- **Current State in Literature:** Christodoulou et al. (2019) found that only $18\%$ of clinical ML studies report calibration metrics, and those that do frequently report unconstrained bivariate intercepts that misstate true calibration in rare events ($<5\%$).
- **Our Contribution:** We implement a rigorous, TRIPOD+AI-compliant calibration audit featuring offset-based calibration-in-the-large, calibration slope, Murphy Brier decomposition, and decile calibration curves, revealing why tree bagging causes probability compression.

### Gap 3: Ignored Clinical Nonlinearities in Linear Baselines vs. Tree Bagging Compression
- **Current State in Literature:** Studies typically compare standard linear logistic regression against unconstrained tree models, attributing ML gains entirely to complex interactions while ignoring that logistic regression was misspecified with raw linear terms.
- **Our Contribution:** We demonstrate that an epidemiological Restricted Cubic Spline (RCS) logistic regression pipeline incorporating lipid ratios ($\text{TC}/\text{HDL}$) outperforms both Random Forest and Histogram Gradient Boosting on the development cohort ($0.782$ vs. $0.776$ and $0.765$), showing that flexible additive modeling captures clinical non-linearities without the calibration penalties of decision trees.

### Gap 4: Misleading Clinical Interpretation of SHAP as Treatment Recommendations
- **Current State in Literature:** Medical AI applications frequently display SHAP waterfall plots to end-users without clarifying that feature attributions are non-causal statistical associations.
- **Our Contribution:** We establish an explicit interface guardrail and educational framework separating statistical feature attributions from causal medical interventions, preventing hazardous clinical extrapolation.

---

## 5. Unresolved Methodological Questions for the Team

The following specific questions are documented for project team review (Axror, Jahongir, Abbosxoja):

1. **Coding of Borderline Diabetes (`DIQ010 == 3`):**\
   *Current state:* `DIQ010 == 3` is mapped to `NaN` and mode-imputed to $0.0$ (non-diabetic).\
   *Question:* Should borderline diabetes be coded as an explicit third category, an ordinal level ($0.5$), or evaluated in a dedicated sensitivity analysis to assess its impact on CVD mortality risk?
2. **Adoption of Spline Logistic Regression as the Primary Model:**\
   *Current state:* Model comparison plan fixed linear logistic regression, random forest, and histogram gradient boosting.\
   *Question:* Given that Restricted Cubic Splines with Total/HDL ratio achieved the highest AUROC ($0.782$), AUPRC ($0.129$), and superior calibration slope ($0.982$), should the team submit a protocol amendment (`model_comparison_plan_v2.md`) formally introducing the Spline model as the winning prototype algorithm?
3. **Incorporation of NHANES Sampling Weights (`WTMEC4YR`):**\
   *Current state:* The prototype reports unweighted sample predictive accuracy.\
   *Question:* Should the paper report a secondary survey-weighted pseudo-AUROC and survey-weighted Brier score to provide population-representative estimates for the US population?
4. **Blood Pressure Reading Averaging Protocol:**\
   *Current state:* `systolic_bp_mmhg` averages all available positive readings (`BPXSY1` through `BPXSY4`).\
   *Question:* Clinical guidelines (AHA/ACC) often discard reading 1 as an acclimatization reading and average readings 2 and 3. Should a sensitivity analysis verify whether discarding reading 1 alters model discrimination?
5. **Web Demonstration Audience and User Wording:**\
   *Current state:* FastAPI backend and React frontend are scheduled for Weeks 9–10.\
   *Question:* Is the target demonstration audience university researchers, medical students, or general users? The phrasing of uncertainty, missing data warnings, and non-causal SHAP disclaimers must be calibrated to their technical literacy.
