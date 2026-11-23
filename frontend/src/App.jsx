import { useEffect, useMemo, useState } from 'react';

const examples = {
  a: {
    age_years: '45', recorded_category: 'female', systolic_bp_mmhg: '120',
    bmi: '25.4', total_cholesterol_mg_dl: '190', hdl_cholesterol_mg_dl: '58',
    current_smoker: 'no', diabetes: 'no',
  },
  b: {
    age_years: '68', recorded_category: 'male', systolic_bp_mmhg: '164',
    bmi: '31.2', total_cholesterol_mg_dl: '255', hdl_cholesterol_mg_dl: '38',
    current_smoker: 'yes', diabetes: 'yes',
  },
};

const labels = {
  age_years: 'Age', gender_code: 'Recorded category',
  systolic_bp_mmhg: 'Systolic blood pressure', bmi: 'Body mass index',
  total_cholesterol_mg_dl: 'Total cholesterol',
  hdl_cholesterol_mg_dl: 'HDL cholesterol',
  current_smoker: 'Current smoking', diabetes: 'Self-reported diabetes',
};

function PulseIcon() {
  return (
    <svg viewBox="0 0 42 42" width="34" height="34" aria-hidden="true">
      <rect width="42" height="42" rx="12" fill="#d2f5ec" />
      <path d="M7 22h8l3-7 5 14 4-9h8" fill="none" stroke="#0b776e" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function PrintIcon() {
  return (
    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polyline points="6 9 6 2 18 2 18 9" />
      <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
      <rect x="6" y="14" width="12" height="8" />
    </svg>
  );
}

function NumericField({ id, label, unit, value, onChange, hint, required, min, max }) {
  return (
    <label className="field" htmlFor={id}>
      <span className="field-label">{label}{!required && <span className="optional"> · optional</span>}</span>
      <span className="input-wrap">
        <input
          id={id} name={id} type="number" inputMode="decimal" step={id === 'age_years' ? '1' : 'any'}
          min={min} max={max} value={value} required={required}
          placeholder={required ? 'Required' : 'Leave blank if unknown'}
          onChange={(event) => onChange(id, event.target.value)}
        />
        {unit && <span className="unit">{unit}</span>}
      </span>
      {hint && <span className="field-hint">{hint}</span>}
    </label>
  );
}

function SelectField({ id, label, value, onChange, options, hint }) {
  return (
    <label className="field" htmlFor={id}>
      <span className="field-label">{label}</span>
      <select id={id} name={id} value={value} onChange={(event) => onChange(id, event.target.value)}>
        {options.map(({ value: optionValue, label: optionLabel }) => (
          <option key={optionValue} value={optionValue}>{optionLabel}</option>
        ))}
      </select>
      {hint && <span className="field-hint">{hint}</span>}
    </label>
  );
}

function FactorRow({ factor, maximum }) {
  const width = Math.max(3, Math.abs(factor.log_odds_contribution) / maximum * 100);
  return (
    <div className="factor-row">
      <div className="factor-top">
        <span>{factor.label}{factor.missing && <em> · imputed</em>}</span>
        <span className={`factor-direction ${factor.direction}`}>
          {factor.direction === 'higher' ? 'Higher' : factor.direction === 'lower' ? 'Lower' : 'Neutral'}
        </span>
      </div>
      <div className="factor-track"><span className={factor.direction} style={{ width: `${width}%` }} /></div>
    </div>
  );
}

function PrintableReport({ result, form, modelInfo }) {
  if (!result) return null;

  const populationText = modelInfo?.population ||
    'US NHANES 1999–2008 adults aged 40–79 without reported prior cardiovascular disease';

  const calibrationStatus = result.calibrated
    ? 'Calibrated probability'
    : 'Preliminary research estimate (uncalibrated model)';

  const topFactors = result.factors.slice(0, 6);

  const inputRows = [
    { label: 'Age', value: `${form.age_years} years`, key: 'age_years' },
    { label: 'Recorded category', value: form.recorded_category === 'male' ? 'Male' : 'Female', key: 'recorded_category' },
    { label: 'Systolic blood pressure', value: form.systolic_bp_mmhg ? `${form.systolic_bp_mmhg} mmHg` : 'Not provided (imputed)', key: 'systolic_bp_mmhg' },
    { label: 'Body mass index', value: form.bmi ? `${form.bmi} kg/m²` : 'Not provided (imputed)', key: 'bmi' },
    { label: 'Total cholesterol', value: form.total_cholesterol_mg_dl ? `${form.total_cholesterol_mg_dl} mg/dL` : 'Not provided (imputed)', key: 'total_cholesterol_mg_dl' },
    { label: 'HDL cholesterol', value: form.hdl_cholesterol_mg_dl ? `${form.hdl_cholesterol_mg_dl} mg/dL` : 'Not provided (imputed)', key: 'hdl_cholesterol_mg_dl' },
    { label: 'Current smoking', value: form.current_smoker === 'yes' ? 'Yes' : form.current_smoker === 'no' ? 'No' : 'Unknown (imputed)', key: 'current_smoker' },
    { label: 'Self-reported diabetes', value: form.diabetes === 'yes' ? 'Yes' : form.diabetes === 'no' ? 'No' : 'Unknown (imputed)', key: 'diabetes' },
  ];

  return (
    <div className="printable-report" aria-hidden="true">
      <div className="print-header">
        <div className="print-header-brand">
          <h2>CardioRisk Research Lab</h2>
          <span className="print-subtitle">Synthetic Case Assessment Report · University Prototype</span>
        </div>
        <div className="print-header-meta">
          <span className="print-badge">SYNTHETIC PROFILE</span>
          <span className="print-date">Generated: {new Date().toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}</span>
        </div>
      </div>

      <div className="print-disclaimer-banner">
        <strong>FOR RESEARCH EVALUATION ONLY · SYNTHETIC CASE DEMONSTRATION · NOT A CLINICAL TOOL</strong>
        <p>
          This report was generated from synthetic/invented data for algorithm demonstration.
          It has not been clinically validated for an individual patient and does not provide medical diagnosis, clinical risk stratification, or treatment recommendations.
        </p>
      </div>

      <div className="print-main-grid">
        <div className="print-estimate-box">
          <span className="print-eyebrow">PRELIMINARY MODEL ESTIMATE</span>
          <div className="print-risk-display">
            <span className="print-risk-val">{result.percentage.toFixed(1)}%</span>
            <span className="print-horizon">{result.horizon_years || 10}-YEAR HORIZON</span>
          </div>
          <p className="print-outcome-name">
            <strong>Target Outcome:</strong> {result.outcome}
          </p>
        </div>

        <div className="print-model-box">
          <span className="print-eyebrow">MODEL PROVENANCE & STATUS</span>
          <ul className="print-meta-list">
            <li><strong>Model ID:</strong> {result.model_id}</li>
            <li><strong>Calibration Status:</strong> {calibrationStatus}</li>
            <li><strong>Source Population:</strong> {populationText}</li>
            <li><strong>Reference Risk:</strong> {(result.reference_probability * 100).toFixed(1)}% (development sample baseline)</li>
          </ul>
        </div>
      </div>

      <div className="print-section">
        <h4 className="print-section-title">Supplied Baseline Inputs (Synthetic Case Profile)</h4>
        <div className="print-inputs-grid">
          {inputRows.map((item) => (
            <div key={item.key} className="print-input-cell">
              <span className="print-cell-label">{item.label}</span>
              <span className="print-cell-val">{item.value}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="print-section">
        <div className="print-section-header">
          <h4 className="print-section-title">Top Model Factors Shaping This Estimate</h4>
          <span className="print-section-sub">Relative to the development sample reference</span>
        </div>
        <table className="print-factors-table">
          <thead>
            <tr>
              <th>Predictor Factor</th>
              <th>Input Status</th>
              <th>Model Direction</th>
              <th style={{ textAlign: 'right' }}>Log-Odds Contribution</th>
            </tr>
          </thead>
          <tbody>
            {topFactors.map((factor) => (
              <tr key={factor.field}>
                <td><strong>{factor.label}</strong></td>
                <td>{factor.missing ? 'Imputed by pipeline' : 'Observed'}</td>
                <td>
                  <span className={`print-dir ${factor.direction}`}>
                    {factor.direction === 'higher' ? 'Higher risk' : factor.direction === 'lower' ? 'Lower risk' : 'Neutral'}
                  </span>
                </td>
                <td style={{ textAlign: 'right', fontFamily: 'monospace' }}>
                  {factor.log_odds_contribution > 0 ? `+${factor.log_odds_contribution.toFixed(3)}` : factor.log_odds_contribution.toFixed(3)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="print-factor-disclaimer">
          <strong>Methodological Note:</strong> Factor attributions represent mathematical associations in the fitted model relative to the development reference population. They are model-derived attributions, NOT causal effects, biological mechanisms, or medical treatment recommendations.
        </p>
      </div>

      <div className="print-section print-quality-box">
        <h4 className="print-section-title">Input Data Quality & Boundary Audit</h4>
        <div className="print-quality-details">
          <p>
            <strong>Missing Inputs: </strong>
            {result.missing_fields.length === 0
              ? 'None. All eight required baseline predictors were supplied.'
              : `Missing inputs imputed by the trained model pipeline: ${result.missing_fields.map((f) => labels[f] || f).join(', ')}.`}
          </p>
          {result.outside_training_range.length > 0 ? (
            <p className="print-warning">
              <strong>Boundary Warning: </strong>
              Inputs outside observed development ranges: {result.outside_training_range.map((f) => labels[f] || f).join(', ')}. Predictions at extreme values carry higher statistical uncertainty.
            </p>
          ) : (
            <p>
              <strong>Boundary Check: </strong>
              All supplied numeric inputs fall within observed development sample bounds.
            </p>
          )}
        </div>
      </div>

      <div className="print-footer">
        <div>
          <span>CardioRisk Research Lab · Academic Prototype</span>
          <p>Strictly for research decision-support evaluation · Not for clinical diagnosis or prescription</p>
        </div>
        <div className="print-footer-right">
          <span>Page 1 of 1</span>
          <span>No Patient Identifiers Recorded</span>
        </div>
      </div>
    </div>
  );
}

function Results({ result }) {
  if (!result) {
    return (
      <div className="empty-result">
        <div className="empty-graphic" aria-hidden="true"><span>10</span><small>years</small></div>
        <h3>Ready for a synthetic case</h3>
        <p>Choose an example or complete the fields, then calculate to see the model estimate and the factors behind it.</p>
      </div>
    );
  }

  const maxFactor = Math.max(...result.factors.map((factor) => Math.abs(factor.log_odds_contribution)), 0.01);
  return (
    <div className="result-content" aria-live="polite">
      <div className="result-summary">
        <div>
          <div className="eyebrow light">PRELIMINARY MODEL ESTIMATE</div>
          <div className="risk-number">{result.percentage.toFixed(1)}<span>%</span></div>
          <div className="result-outcome">Estimated chance of cardiovascular death within 10 years</div>
        </div>
        <div className="ring" style={{ '--risk': `${Math.min(result.percentage, 100)}%` }} aria-hidden="true">
          <span>10<br /><small>YEARS</small></span>
        </div>
      </div>

      <div className="result-actions">
        <button
          type="button"
          className="btn-print"
          onClick={() => window.print()}
          aria-label="Print or save synthetic case assessment report as PDF"
        >
          <PrintIcon />
          <span>Print / Save as PDF</span>
        </button>
      </div>

      <div className="research-alert"><strong>Research output only.</strong> This probability has not been clinically validated or recalibrated for an individual patient.</div>

      <div className="section-heading"><h3>What shaped this estimate</h3><span>Relative to the development-sample reference</span></div>
      <div className="factor-list">
        {result.factors.slice(0, 6).map((factor) => <FactorRow key={factor.field} factor={factor} maximum={maxFactor} />)}
      </div>
      <p className="microcopy">Bars show the size and direction of each input's contribution to model log-odds. They are not percentage-point changes or causal effects.</p>

      <div className="quality-card">
        <div className="quality-icon">i</div>
        <div>
          <strong>Input quality</strong>
          <p>{result.missing_fields.length === 0 ? 'All eight model inputs were supplied.' : `Missing inputs imputed by the trained pipeline: ${result.missing_fields.map((field) => labels[field]).join(', ')}.`}</p>
          {result.outside_training_range.length > 0 && <p className="warning">Outside the development data's observed range: {result.outside_training_range.map((field) => labels[field]).join(', ')}. Check these entries.</p>}
        </div>
      </div>
      <p className="model-note">Model: logistic baseline · US NHANES 1999-2006 development data · uncalibrated</p>
    </div>
  );
}

function App() {
  const [form, setForm] = useState(examples.a);
  const [result, setResult] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('/api/model').then((response) => response.ok ? response.json() : Promise.reject())
      .then(setModelInfo).catch(() => setModelInfo(null));
  }, []);

  const completeCount = useMemo(() => [
    form.age_years, form.recorded_category, form.systolic_bp_mmhg, form.bmi,
    form.total_cholesterol_mg_dl, form.hdl_cholesterol_mg_dl,
    form.current_smoker, form.diabetes,
  ].filter((value) => value !== '').length, [form]);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
    setResult(null);
    setError('');
  }

  function loadExample(key) {
    setForm({ ...examples[key] });
    setResult(null);
    setError('');
  }

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    const numeric = (value) => value.trim() === '' ? null : Number(value);
    const yesNo = (value) => value === '' ? null : value === 'yes';
    const payload = {
      age_years: Number(form.age_years), recorded_category: form.recorded_category,
      systolic_bp_mmhg: numeric(form.systolic_bp_mmhg), bmi: numeric(form.bmi),
      total_cholesterol_mg_dl: numeric(form.total_cholesterol_mg_dl),
      hdl_cholesterol_mg_dl: numeric(form.hdl_cholesterol_mg_dl),
      current_smoker: yesNo(form.current_smoker), diabetes: yesNo(form.diabetes),
    };
    try {
      const response = await fetch('/api/predict', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
      });
      const body = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(body.detail) ? body.detail.map((item) => item.msg).join(' · ') : body.detail;
        throw new Error(detail || 'The assessment could not be calculated.');
      }
      setResult(body);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Could not connect to the local API.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="site-shell">
      <header className="site-header">
        <div className="header-inner">
          <div className="brand"><PulseIcon /><span><strong>CardioRisk</strong><small>RESEARCH LAB</small></span></div>
          <div className="header-right"><span className={`status-dot${modelInfo ? '' : ' offline'}`} />{modelInfo ? 'Local model ready' : 'Connect the local API'}<span className="header-divider" /><span className="prototype-tag">PROTOTYPE 01</span></div>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-content">
            <div className="eyebrow">EXPLAINABLE CARDIOVASCULAR RISK RESEARCH</div>
            <h1>Understand the estimate.<br /><span>See what shapes it.</span></h1>
            <p>Explore a 10-year cardiovascular mortality model with synthetic examples. Each estimate is paired with its model factors and input-quality context.</p>
            <div className="hero-meta"><span><span className="meta-mark">01</span> Eight baseline inputs</span><span><span className="meta-mark">02</span> Transparent model factors</span><span><span className="meta-mark">03</span> Research use only</span></div>
          </div>
          <div className="hero-art" aria-hidden="true"><div className="art-orbit orbit-one" /><div className="art-orbit orbit-two" /><div className="art-core"><svg viewBox="0 0 220 130"><path d="M0 67h48l16-32 30 66 24-50 16 16h86" fill="none" stroke="#b7f8eb" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" /></svg></div></div>
        </section>

        <div className="workspace-intro"><div><div className="eyebrow">INTERACTIVE RESEARCH DEMO</div><h2>Explore a synthetic patient profile</h2><p>Use an example or enter invented values. Do not enter a real person's health information.</p></div><span className="method-tag">US NHANES DATA · 1999-2008</span></div>

        <div className="workspace-grid">
          <section className="panel form-panel" aria-labelledby="form-title">
            <div className="panel-header"><div><span className="step-number">01</span><h3 id="form-title">Baseline information</h3></div><span className="completeness">{completeCount} / 8 supplied</span></div>
            <div className="example-strip"><span>Start with an example</span><div><button type="button" onClick={() => loadExample('a')}>Example A</button><button type="button" onClick={() => loadExample('b')}>Example B</button></div></div>
            <form onSubmit={submit}>
              <div className="form-section"><h4>Personal characteristics</h4><div className="fields two"><NumericField id="age_years" label="Age" unit="years" value={form.age_years} onChange={update} required min="40" max="79" hint="Model studied ages 40-79" /><SelectField id="recorded_category" label="NHANES recorded category" value={form.recorded_category} onChange={update} options={[{ value: 'male', label: 'Male' }, { value: 'female', label: 'Female' }]} hint="Two categories available in the source data" /></div></div>
              <div className="form-section"><h4>Measurements</h4><div className="fields two"><NumericField id="systolic_bp_mmhg" label="Systolic blood pressure" unit="mmHg" value={form.systolic_bp_mmhg} onChange={update} /><NumericField id="bmi" label="Body mass index" unit="kg/m²" value={form.bmi} onChange={update} /></div></div>
              <div className="form-section"><h4>Laboratory values</h4><div className="fields two"><NumericField id="total_cholesterol_mg_dl" label="Total cholesterol" unit="mg/dL" value={form.total_cholesterol_mg_dl} onChange={update} /><NumericField id="hdl_cholesterol_mg_dl" label="HDL cholesterol" unit="mg/dL" value={form.hdl_cholesterol_mg_dl} onChange={update} /></div></div>
              <div className="form-section"><h4>History & lifestyle</h4><div className="fields two"><SelectField id="current_smoker" label="Current smoking" value={form.current_smoker} onChange={update} options={[{ value: '', label: 'Unknown' }, { value: 'no', label: 'No' }, { value: 'yes', label: 'Yes' }]} /><SelectField id="diabetes" label="Self-reported diabetes" value={form.diabetes} onChange={update} options={[{ value: '', label: 'Unknown' }, { value: 'no', label: 'No' }, { value: 'yes', label: 'Yes' }]} /></div></div>
              {error && <div className="error-box" role="alert">{error}</div>}
              <button className="calculate" type="submit" disabled={loading}>{loading ? 'Calculating…' : 'Calculate research estimate'}<span aria-hidden="true">→</span></button>
              <p className="form-footnote">Missing optional values are imputed by the trained model and identified in the result.</p>
            </form>
          </section>

          <section className="panel output-panel" aria-labelledby="output-title">
            <div className="panel-header">
              <div>
                <span className="step-number">02</span>
                <h3 id="output-title">Assessment view</h3>
              </div>
              <div className="panel-header-actions">
                <button
                  type="button"
                  className="btn-print-compact"
                  onClick={() => window.print()}
                  disabled={!result}
                  title={result ? 'Print or save synthetic case report as PDF' : 'Calculate an assessment first'}
                  aria-label="Print or save synthetic case report as PDF"
                >
                  <PrintIcon />
                  <span>Print / PDF</span>
                </button>
                <span className="research-pill">RESEARCH ONLY</span>
              </div>
            </div>
            <Results result={result} form={form} modelInfo={modelInfo} />
          </section>
        </div>

        <section className="context-band"><div><span className="context-num">01</span><h3>A defined outcome</h3><p>The model estimates death from heart disease or cerebrovascular disease within 10 years, not whether someone currently has heart disease.</p></div><div><span className="context-num">02</span><h3>Source population</h3><p>It was developed from US NHANES adults aged 40-79 without reported prior cardiovascular disease.</p></div><div><span className="context-num">03</span><h3>Research limitations</h3><p>Probabilities are preliminary and uncalibrated. Local clinical validation and governance are required before any patient-care use.</p></div></section>
      </main>
      <footer><div className="footer-inner"><span>CardioRisk Research Lab · University prototype</span><span>No diagnosis · No treatment recommendation · Synthetic cases only</span></div></footer>
    </div>
    <PrintableReport result={result} form={form} modelInfo={modelInfo} />
  </>
  );
}

export default App;
