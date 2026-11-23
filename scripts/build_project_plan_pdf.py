"""Build the shareable research and prototype plan from reviewed project facts."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "plans" / "cardiovascular_risk_project_plan_v1.pdf"
FIGURE = ROOT / "docs" / "figures" / "baseline_calibration.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

pdfmetrics.registerFont(TTFont("ArialCustom", "/System/Library/Fonts/Supplemental/Arial.ttf"))
pdfmetrics.registerFont(TTFont("ArialCustom-Bold", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"))
pdfmetrics.registerFontFamily("ArialCustom", normal="ArialCustom", bold="ArialCustom-Bold")

NAVY = colors.HexColor("#163148")
BLUE = colors.HexColor("#126C8F")
TEAL = colors.HexColor("#087F83")
LIGHT = colors.HexColor("#EEF5F7")
PALE = colors.HexColor("#F5F8F9")
INK = colors.HexColor("#243544")
MUTED = colors.HexColor("#5C6E78")
LINE = colors.HexColor("#D4E0E5")
WHITE = colors.white

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverKicker", fontName="ArialCustom-Bold", fontSize=10,
                          leading=13, textColor=TEAL, spaceAfter=14))
styles.add(ParagraphStyle(name="CoverTitle", fontName="ArialCustom-Bold", fontSize=27,
                          leading=32, textColor=NAVY, spaceAfter=15))
styles.add(ParagraphStyle(name="CoverSub", fontName="ArialCustom", fontSize=13,
                          leading=19, textColor=MUTED, spaceAfter=21))
styles.add(ParagraphStyle(name="H1Custom", fontName="ArialCustom-Bold", fontSize=17,
                          leading=21, textColor=NAVY, spaceAfter=8))
styles.add(ParagraphStyle(name="H2Custom", fontName="ArialCustom-Bold", fontSize=11.1,
                          leading=14, textColor=BLUE, spaceBefore=12, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyCustom", fontName="ArialCustom", fontSize=9.15,
                          leading=13.35, textColor=INK, spaceAfter=7))
styles.add(ParagraphStyle(name="SmallCustom", fontName="ArialCustom", fontSize=8.15,
                          leading=11.4, textColor=INK, spaceAfter=5))
styles.add(ParagraphStyle(name="TinyCustom", fontName="ArialCustom", fontSize=7.3,
                          leading=9.9, textColor=INK, spaceAfter=3))
styles.add(ParagraphStyle(name="BulletCustom", parent=styles["BodyCustom"],
                          leftIndent=14, firstLineIndent=-9, spaceAfter=5))
styles.add(ParagraphStyle(name="TableHeadCustom", fontName="ArialCustom-Bold", fontSize=8.1,
                          leading=10.6, textColor=WHITE))
styles.add(ParagraphStyle(name="TableCellCustom", fontName="ArialCustom", fontSize=8.0,
                          leading=10.8, textColor=INK))
styles.add(ParagraphStyle(name="TableCellSmall", fontName="ArialCustom", fontSize=7.6,
                          leading=10.1, textColor=INK))
styles.add(ParagraphStyle(name="CalloutCustom", fontName="ArialCustom-Bold", fontSize=9.1,
                          leading=13, textColor=NAVY))
styles.add(ParagraphStyle(name="LabelCustom", fontName="ArialCustom-Bold", fontSize=8.0,
                          leading=11, textColor=TEAL))

story = []


def p(text, style="BodyCustom"):
    return Paragraph(text, styles[style])


def add(text, style="BodyCustom"):
    story.append(p(text, style))


def bullet(text):
    story.append(p("&#8226; " + text, "BulletCustom"))


def heading(number, title, sub=None):
    add(f"{number}  {title}", "H1Custom")
    if sub:
        add(sub, "SmallCustom")
    story.append(HRFlowable(width="100%", thickness=0.7, color=LINE, spaceAfter=10))


def h2(text):
    add(text, "H2Custom")


def callout(label, text, bg=LIGHT):
    t = Table([[p(label, "LabelCustom"), p(text, "CalloutCustom")]], colWidths=[91, 410])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 9))


def table(headers, rows, widths, small=False):
    cell_style = "TableCellSmall" if small else "TableCellCustom"
    data = [[p(escape(str(x)), "TableHeadCustom") for x in headers]]
    data += [[p(str(x), cell_style) for x in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
        ("LINEBELOW", (0, 1), (-1, -1), 0.35, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    t.setStyle(TableStyle(cmds))
    story.append(t)
    story.append(Spacer(1, 8))


def next_page():
    story.append(PageBreak())


# 1 - Cover and executive decisions.
story.append(Spacer(1, 32))
add("RESEARCH + PRODUCT PLAN  |  VERSION 1  |  6 OCTOBER 2026", "CoverKicker")
add("AI-Based Cardiovascular<br/>Risk Assessment System", "CoverTitle")
add("An explainable machine-learning research prototype for 10-year cardiovascular mortality risk", "CoverSub")
story.append(HRFlowable(width="100%", thickness=2.4, color=TEAL, spaceAfter=24))
callout("EXACT TARGET", "Probability of death from heart disease or cerebrovascular disease within 10 years after a baseline examination.")
callout("DATA SOURCE", "Public US NHANES 1999-2008 survey data linked to the CDC 2019 public-use mortality files. No hospital records are available to the team.")
callout("CURRENT STAGE", "The cohort, eight input fields, and a preliminary logistic-regression baseline are built. Model comparison, calibration research, explanations, and the web demo remain to be completed.")
callout("REAL PATIENTS", "The finished university prototype cannot be used for patient-care decisions automatically. Clinical use requires local external validation, governance, regulatory review, and supervised evaluation.", colors.HexColor("#FFF5E9"))
story.append(Spacer(1, 9))
add("Prepared for Axror Nosirov, Jahongir Islomov and Abbosxoja Obidoxojayev. The approved Week 3 project title is retained; the outcome above specifies what the selected data can actually measure.", "SmallCustom")
add("Research decision-support prototype. It does not diagnose cardiovascular disease or recommend treatment.", "SmallCustom")


# 2 - Scientific question.
next_page()
heading("01", "What are we trying to solve?", "The project has three linked research problems, matching the team's submitted questions and objectives.")
table(["Problem", "Research work", "Evidence / deliverable"], [
    ("Data quality", "Clinical and lifestyle variables can be missing, inconsistent or measured differently across survey cycles.", "Documented data dictionary; validation; missingness, exclusions and imputation reports."),
    ("Prediction quality", "A model can rank people well while giving unreliable 10-year probabilities.", "Compare models on discrimination and calibration; report uncertainty and event counts."),
    ("Interpretability", "A probability alone does not tell users which recorded factors shaped the model output.", "Patient-level explanation, clear outcome wording and an empirically justified uncertainty display."),
], [102, 202, 197])
h2("Locked scientific question")
add("Among US NHANES adults aged 40-79 with no self-reported prior cardiovascular disease at baseline, can eight clinical and lifestyle variables estimate <b>10-year cardiovascular mortality risk</b> with useful discrimination, acceptable calibration and understandable explanations?")
h2("Definitions that cannot be blurred")
bullet("The outcome is <b>fatal cardiovascular disease</b> within 120 months. It is not diagnosis of existing heart disease, all heart attacks, all strokes or all nonfatal cardiovascular events.")
bullet("The baseline prediction time is the NHANES interview/examination. Follow-up and cause-of-death data are outcome labels only, never input features.")
bullet("The model is based on US public data. Transport to Uzbekistan or another clinical population is unproven.")
h2("What success means for this university project")
add("A reproducible cohort and pipeline; honest model comparison; reported calibration; an explanation demo using synthetic patients; a paper and presentation following TRIPOD+AI. A high AUROC by itself is not sufficient. [1-3]")


# 3 - Data and inputs.
next_page()
heading("02", "Dataset and exact model inputs", "The input form must match the variables the model was actually trained on.")
add("Public NHANES examination, laboratory and questionnaire files from 1999-2008 are joined to the CDC 2019 public-use linked mortality file. Adults with reported prior congestive heart failure, coronary heart disease, angina, myocardial infarction or stroke are excluded. Cardiovascular death is identified using the public file's underlying-cause categories 001 and 005 within 120 months after examination. [1, 2]")
table(["Input shown in form", "Type / unit", "Current derivation or rule"], [
    ("Age", "Years; 40-79", "NHANES recorded age at baseline."),
    ("Recorded male/female category", "Survey category", "NHANES RIAGENDR code; this two-category field does not represent all gender identities."),
    ("Systolic blood pressure", "mmHg", "Mean of available positive systolic readings at exam."),
    ("Body mass index", "kg/m2", "Positive recorded BMI."),
    ("Total cholesterol", "mg/dL", "Baseline laboratory value."),
    ("HDL cholesterol", "mg/dL", "Baseline laboratory value; assay changes across cycles need sensitivity analysis."),
    ("Current smoking", "Yes / no / unknown", "Defined from lifetime smoking and current smoking questions."),
    ("Self-reported diabetes", "Yes / no / unknown", "Borderline, refused and unknown answers stay missing."),
], [169, 91, 241], small=True)
add("<b>Not current inputs:</b> LDL cholesterol, physical activity, alcohol use, medication use and detailed prior diagnoses. They must not appear as model factors unless the data derivation and model are revised.", "SmallCustom")
callout("INPUT RULE", "Missing or invalid values are never silently set to zero. The form will validate type, unit and plausible range; unresolved values are flagged and handled only by a trained, tested preprocessing rule.")


# 4 - Cohort and methods.
next_page()
heading("03", "How the system will work")
table(["Stage", "What it does", "Main check"], [
    ("1. Web form", "Collect eight fields with units and clear choices.", "No patient identifiers in the research demo."),
    ("2. FastAPI validation", "Check data types, required fields, units and clinically reviewed ranges.", "Reject impossible entries; flag missing ones."),
    ("3. Preprocessing", "Apply the saved imputation, encoding and scaling pipeline.", "Fit on development folds only; prevent leakage."),
    ("4. Prediction", "Run the selected trained model.", "Return probability for the defined 10-year mortality outcome."),
    ("5. Calibration", "Apply only a calibration method validated on development data.", "Inspect calibration in temporal evaluation."),
    ("6. Explanation", "Show model-derived factors and data-completeness context.", "No causal or treatment claims."),
    ("7. Results page", "Present probability, horizon, source population and limitations.", "Synthetic examples for the university demo."),
], [104, 234, 163], small=True)
h2("Models we will compare")
table(["Model", "Why include it", "Main caution"], [
    ("Logistic regression", "Simple, interpretable baseline; already trained.", "May miss nonlinear patterns."),
    ("Random forest", "Can learn interactions and nonlinearities.", "Probabilities may need calibration; event count limits complexity."),
    ("One boosted-tree model", "XGBoost or LightGBM as a stronger flexible comparator, if justified.", "Tune conservatively; avoid overfitting 274 development events."),
], [125, 207, 169], small=True)
add("A neural network is optional only if the available sample size and comparison justify it. The best research model is the one with reliable, reproducible probability estimates, not necessarily the most complex one.", "SmallCustom")


# 5 - Design and results.
next_page()
heading("04", "Study design and evaluation")
callout("DEVELOPMENT", "NHANES 1999-2006: 8,902 adults, 274 cardiovascular deaths within 10 years (3.08%). Use five-fold cross-validation for processing, tuning, selection and calibration.")
callout("TEMPORAL CHECK", "NHANES 2007-2008: 2,941 adults, 87 events (2.96%). This later cycle checks performance over time; it is still US public survey data.")
add("The 2007-2008 outcomes were already inspected for the fixed logistic baseline. Future choices must be made within development data and reported transparently; this cycle is no longer a wholly unseen final test. A separate independent cohort would strengthen confirmation.", "SmallCustom")
h2("Measures to report")
table(["Question", "Measures", "Interpretation"], [
    ("Can it rank risk?", "AUROC; AUPRC with event prevalence", "AUPRC is particularly relevant when events are uncommon."),
    ("Are probabilities reliable?", "Calibration plot, intercept, slope, Brier score", "Predicted risks should agree with observed rates in suitable data."),
    ("How precise are estimates?", "95% intervals and event counts", "Current person bootstrap intervals omit the complex survey design."),
    ("Can it guide action?", "Sensitivity/specificity only at justified thresholds", "No clinical treatment threshold has yet been chosen."),
], [122, 178, 201], small=True)
h2("Preliminary logistic-regression result")
table(["Metric", "Development: out-of-fold", "2007-2008 temporal check"], [
    ("AUROC", "0.777 (95% interval 0.749-0.803)", "0.778 (0.738-0.819)"),
    ("AUPRC", "0.124 (0.097-0.160)", "0.080 (0.059-0.114)"),
    ("Brier score", "0.0284 (0.0255-0.0315)", "0.0281 (0.0231-0.0340)"),
    ("Calibration intercept / slope", "-0.125 / 0.958", "-0.223 / 0.926"),
], [135, 183, 183], small=True)
add("These are preliminary, unweighted sample-level results. They do not establish clinical safety, local accuracy or individual diagnosis. The temporal AUPRC should be read against 2.96% event prevalence.", "SmallCustom")


# 6 - Calibration figure, explainability.
next_page()
heading("05", "Explanations and uncertainty")
add("The interface will explain the selected model's prediction for one example person, identify which inputs were missing, and state the population and outcome. SHAP can help display model contributions, but contributions are <b>associations in the fitted model</b>, not proof that changing a factor will change a person's outcome.")
h2("Current baseline calibration plot")
if FIGURE.exists():
    img = Image(str(FIGURE))
    scale = min(495 / img.imageWidth, 270 / img.imageHeight)
    img.drawWidth = img.imageWidth * scale
    img.drawHeight = img.imageHeight * scale
    story.append(img)
    story.append(Spacer(1, 5))
    add("Figure: Observed versus predicted ten-year mortality risk by probability decile for the fixed logistic baseline. It is descriptive and does not validate individual decisions.", "TinyCustom")
h2("What the results screen should say")
table(["Display", "Required meaning"], [
    ("Estimated 10-year risk", "Probability of cardiovascular death within 10 years, with US NHANES source named."),
    ("Main model factors", "Directions and contributions computed on a clearly defined model scale; avoid invented percentage-point effects."),
    ("Missing inputs", "Which fields were missing and whether the model used an evaluated imputation rule."),
    ("Uncertainty", "Only a statistically defined and checked interval/summary. Until then, show limitations and data completeness without a 'confidence' score."),
    ("Risk category", "Low/medium/high only after thresholds are justified for a stated research purpose; none are set now."),
], [142, 359], small=True)


# 7 - Experiments and risks.
next_page()
heading("06", "Experiments, difficulties and safeguards")
table(["Planned experiment", "Comparison / output"], [
    ("Algorithms", "Logistic regression vs random forest vs one boosted-tree model, selected using development cross-validation."),
    ("Missing data", "Fold-fitted imputation vs complete cases; report people and events lost, then compare performance."),
    ("Calibration", "Original probabilities vs sigmoid/Platt or isotonic calibration, chosen only within development data."),
    ("Explainability", "Check explanation stability and whether intended users understand the wording."),
    ("Subgroups", "Exploratory age and recorded-gender estimates with event counts and uncertainty, if adequately supported."),
], [123, 378], small=True)
h2("The main problems we expect")
table(["Problem", "Why it matters", "Our response"], [
    ("Few outcome events", "Only 87 events in the later cycle; subgroup results can be unstable.", "Limit complexity and claims; show intervals and event counts."),
    ("Missing / extreme inputs", "Complete cases discard 54 development and 17 temporal events; extreme values need review.", "Fit imputation in folds; audit extremes; review form ranges clinically."),
    ("Survey design", "NHANES uses weights, clusters and strata.", "Separate unweighted model results from any population-level inference; add design-aware analysis."),
    ("Measurement shifts", "HDL assay methods changed across cycles.", "Document harmonization and test cycle sensitivity."),
    ("Public mortality file", "Some times and causes have privacy-protecting substitutions.", "Describe this limitation; seek stronger data for clinical translation."),
    ("Population transfer", "US data may behave differently in Uzbekistan or a hospital.", "Require external validation and local clinical review."),
], [106, 193, 202], small=True)
add("Additional guardrail: do not compare this fatal-outcome model directly with a broader 10-year CVD event score or WHO chart as if their endpoints were identical. [4]", "SmallCustom")


# 8 - roadmap.
next_page()
heading("07", "Twelve-week working roadmap", "The schedule is a planning sequence, not a claim that every listed item is finished.")
table(["Week", "Focus", "Deliverable / state as of 6 October"], [
    ("1", "Lock population, outcome and horizon", "Research protocol - drafted."),
    ("2", "Literature review", "20-30 strong papers and a comparison matrix - planned."),
    ("3", "Acquire and document data", "Public source manifest, cohort and data dictionary - built."),
    ("4", "Cleaning and exploratory analysis", "Missingness, extremes, event prevalence and data report - partial."),
    ("5", "Reusable preprocessing", "Validated schema and fold-safe pipeline - baseline version built."),
    ("6", "Logistic baseline", "Five-fold and temporal performance report - preliminary result built."),
    ("7", "Forest and boosting models", "Development-only comparison - planned."),
    ("8", "Calibration and evaluation", "Calibration study, intervals and sensitivity analyses - planned."),
    ("9", "Explanations and uncertainty", "SHAP study, wording and user-comprehension check - planned."),
    ("10", "FastAPI and React demo", "Validated synthetic-input form and results page - planned."),
    ("11", "Robustness and subgroup study", "Missing-data, cycle and exploratory subgroup report - planned."),
    ("12", "Paper and presentation", "TRIPOD+AI reporting, model card, reproducible demo - planned."),
], [39, 195, 267], small=True)
h2("Suggested division for three team members")
bullet("<b>Axror:</b> cohort, modeling, calibration, evaluation and explainability.")
bullet("<b>Jahongir:</b> FastAPI, validation, saved-model integration and automated checks.")
bullet("<b>Abbosxoja:</b> React interface, literature matrix, figures, user wording and paper assembly.")
add("All members should review the target definition, leakage controls, results and final clinical-use limitations. Keep code, versions, data-source checksums, exclusion counts, model settings and outputs reproducible.", "SmallCustom")


# 9 - pathway to real people.
next_page()
heading("08", "Can this eventually be used with real people?", "Yes, potentially - but the university prototype alone does not establish that it is safe for patient care.")
callout("NOW", "Use public records for research and synthetic cases for the web demo. Do not use the score to diagnose, triage or recommend treatment for a real patient.", colors.HexColor("#FFF5E9"))
add("A clinician typing a real patient's information into the form would still be using real health data. Avoiding a hospital-record integration does not remove the need for privacy controls or clinical validation.")
table(["Gate", "What would be needed before clinical use"], [
    ("1. Intended use", "Define users, setting, decisions, exclusions, outcomes and how the estimate should affect care."),
    ("2. Local validation", "Evaluate on independent people from the intended population, ideally with measured 10-year outcomes; check calibration, subgroups and missingness."),
    ("3. Clinical review", "Clinicians assess input definitions, thresholds, explanations, failure cases and whether the tool adds useful information."),
    ("4. Data governance", "Obtain approved data access and consent/legal basis as applicable; protect identifiers, access and logs."),
    ("5. Regulatory assessment", "Determine requirements in the intended jurisdiction for clinical decision-support or medical-device software."),
    ("6. Prospective evaluation", "Run an authorized, monitored pilot, initially without driving care decisions; monitor drift, errors and user behavior."),
], [125, 376], small=True)
h2("What hospital records could add later")
add("A hospital partner could first supply an independent cohort for <b>external validation</b>. Retraining is a separate decision and requires consistent baseline predictors, known outcome timing, permission to use the records and strict train/test separation. Without local follow-up outcomes, we cannot prove local 10-year calibration merely by entering local patients into the current model.")
add("Clinical translation should follow medical AI ethics and software clinical-evaluation guidance, with local legal and regulatory advice for the actual deployment setting. [5, 6]", "SmallCustom")


# 10 - decisions and references.
next_page()
heading("09", "Immediate next steps and reference notes")
h2("Next concrete work")
table(["Order", "Action", "Done when"], [
    ("1", "Review extreme input values, HDL measurement changes and the public mortality-file limitations.", "Data definitions and validation rules are frozen with team/clinical review."),
    ("2", "Build an official-source literature matrix and align comparisons by outcome and population.", "20-30 relevant papers with dataset, N, models, AUROC, calibration and explanation fields."),
    ("3", "Prespecify model comparison and calibration choices inside development data.", "Written analysis plan before additional evaluation-cycle inspection."),
    ("4", "Complete models, sensitivity analyses and reproducible tables.", "Performance report includes event counts, intervals and limitations."),
    ("5", "Build the synthetic-patient web demo and test user wording.", "Form accepts eight validated inputs and labels the exact outcome clearly."),
], [39, 239, 223], small=True)
h2("Source and reporting references")
refs = [
    ("1", "CDC National Center for Health Statistics, public-use linked mortality files", "https://www.cdc.gov/nchs/linked-data/mortality-files/index.html"),
    ("2", "CDC, 2019 public-use linked mortality data dictionary", "https://www.cdc.gov/nchs/data/datalinkage/public-use-linked-mortality-files-data-dictionary.pdf"),
    ("3", "TRIPOD+AI reporting statement (BMJ, 2024)", "https://www.bmj.com/content/385/bmj-2023-078378"),
    ("4", "WHO cardiovascular risk charts: regional context", "https://www.who.int/news-room/detail/02-09-2019-who-updates-cardiovascular-risk-charts"),
    ("5", "WHO, Ethics and governance of artificial intelligence for health", "https://www.who.int/publications/i/item/9789240029200"),
    ("6", "IMDRF, Software as a Medical Device: Clinical Evaluation", "https://www.imdrf.org/documents/software-medical-device-samd-clinical-evaluation"),
    ("7", "CDC NHANES analytic guidance: weighting", "https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx"),
]
for num, title, url in refs:
    add(f'[{num}] <link href="{escape(url)}" color="#126C8F">{escape(title)}</link>', "SmallCustom")
story.append(Spacer(1, 7))
add("Project evidence: team Week 3 submission (2 October 2026); repository protocol, data dictionary, cohort feasibility report and preliminary baseline result (6 October 2026).", "SmallCustom")
add("Terminology: AUROC measures ranking; AUPRC summarizes precision and recall across thresholds; calibration compares predicted and observed probability; Brier score measures mean squared probability error; SHAP explains a fitted model's output.", "SmallCustom")


PAGE_W, PAGE_H = A4


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(46, PAGE_H - 41, PAGE_W - 46, PAGE_H - 41)
    canvas.setFont("ArialCustom-Bold", 7.5)
    canvas.setFillColor(BLUE)
    canvas.drawString(46, PAGE_H - 31, "CARDIOVASCULAR RISK AI  /  PROJECT PLAN")
    canvas.setFont("ArialCustom", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(PAGE_W - 46, PAGE_H - 31, "6 OCT 2026")
    canvas.line(46, 43, PAGE_W - 46, 43)
    canvas.drawString(46, 30, "Research prototype - not for clinical use")
    canvas.drawRightString(PAGE_W - 46, 30, f"Page {doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUT), pagesize=A4, rightMargin=46, leftMargin=46,
    topMargin=59, bottomMargin=58, title="Cardiovascular Risk AI - Project Plan",
    author="Cardiovascular Risk AI project team", subject="Research protocol and prototype roadmap",
)
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(OUT)
