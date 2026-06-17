// =============================================
// CONFIG
// =============================================
const API_URL = 'http://127.0.0.1:8000/analyze';

// =============================================
// STATE
// =============================================
let state = {
  activeTab: 'text',
  isAnalyzing: false,
  history: [],
  currentStep: 0
};

// =============================================
// PIPELINE STEPS
// =============================================
const PIPELINE_STEPS = [
  { id: 1, name: 'Claim Extraction',    role: 'Extracts entities and factual assertions.',           icon: '🔍' },
  { id: 2, name: 'Linguistic Analysis', role: 'Detects clickbait, bias, and sensational language.',  icon: '🧠' },
  { id: 3, name: 'Source Credibility',  role: 'Audits credibility of identified entities.',          icon: '🏛' },
  { id: 4, name: 'Evidence Retrieval',  role: 'Queries the Knowledge Graph for verified facts.',     icon: '🗄' },
  { id: 5, name: 'ML Classification',   role: 'Runs TF-IDF + Logistic Regression classifier.',      icon: '⚙️' },
  { id: 6, name: 'Cross Verification',  role: 'Applies override logic and resolves final verdict.',  icon: '✅' },
];

// =============================================
// SAMPLE ARTICLES
// =============================================
const SAMPLES = {
  fake: `Scientists have discovered that drinking bleach cures all diseases including cancer and COVID-19. A secret government document leaked online proves that pharmaceutical companies have been hiding this miracle cure for decades. Share this before it gets deleted!`,
  real: `NASA successfully launched the Artemis II lunar mission with four astronauts on board. The mission marks the first crewed flight beyond low Earth orbit since Apollo 17 in 1972. The spacecraft is expected to complete a 10-day journey around the Moon before returning to Earth.`,
  clickbait: `SHOCKING: Unbelievable conspiracy exposed! The secret aliens have been living among us for years — 100% true and breaking news — the government doesn't want you to know this!`
};

// =============================================
// INIT
// =============================================
document.addEventListener('DOMContentLoaded', () => {
  renderStepper(0);
});

// =============================================
// TAB SWITCH
// =============================================
function switchTab(tab) {
  state.activeTab = tab;
  document.getElementById('tabText').classList.toggle('active', tab === 'text');
  document.getElementById('tabUrl').classList.toggle('active', tab === 'url');
  document.getElementById('newsInput').classList.toggle('hidden', tab !== 'text');
  document.getElementById('urlInput').classList.toggle('hidden', tab !== 'url');
}

// =============================================
// LOAD SAMPLE
// =============================================
function loadSample(type) {
  switchTab('text');
  document.getElementById('newsInput').value = SAMPLES[type];
}

// =============================================
// RENDER STEPPER
// =============================================
function renderStepper(currentStep, isAnalyzing = false) {
  const el = document.getElementById('stepper');
  el.innerHTML = PIPELINE_STEPS.map(step => {
    const done    = currentStep > step.id;
    const active  = isAnalyzing && currentStep === step.id;
    const pending = !done && !active;
    const cls     = done ? 'done' : active ? 'active' : 'pending';
    const badge   = done ? 'COMPLETED' : active ? 'ACTIVE' : 'QUEUED';
    const icon    = done ? '✓' : active ? '<span class="spinner"></span>' : step.icon;
    return `
      <div class="step ${cls}">
        <div class="step-icon">${icon}</div>
        <div class="step-info">
          <div class="step-name">${step.name}</div>
          <div class="step-role">${step.role}</div>
          <span class="step-badge">${badge}</span>
        </div>
      </div>`;
  }).join('');
}

// =============================================
// SET ANALYZING STATE
// =============================================
function setAnalyzing(val) {
  state.isAnalyzing = val;
  const btn = document.getElementById('analyzeBtn');
  const btnText = document.getElementById('btnText');
  const btnIcon = document.getElementById('btnIcon');
  btn.disabled = val;
  if (val) {
    btnText.textContent = 'Analyzing...';
    btnIcon.innerHTML = '<span class="spinner"></span>';
  } else {
    btnText.textContent = 'Analyze News';
    btnIcon.textContent = '→';
  }
}

// =============================================
// ANIMATE STEPPER
// =============================================
async function animatePipeline() {
  for (let i = 1; i <= 5; i++) {
    state.currentStep = i;
    renderStepper(i, true);
    await sleep(500);
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// =============================================
// MAIN ANALYZE FUNCTION
// =============================================
async function analyze() {
  clearError();

  const isText = state.activeTab === 'text';
  const input  = isText
    ? document.getElementById('newsInput').value.trim()
    : document.getElementById('urlInput').value.trim();

  if (!input) {
    showError('Please enter some news text or a URL before analyzing.');
    return;
  }

  // Hide previous results
  document.getElementById('verdictPanel').classList.add('hidden');
  document.getElementById('agentPanel').classList.add('hidden');

  setAnalyzing(true);
  renderStepper(1, true);

  // Run pipeline animation in parallel with the fetch
  const animPromise = animatePipeline();

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: input })
    });

    if (!res.ok) throw new Error(`Server returned HTTP ${res.status}`);

    const data = await res.json();

    // Wait for animation to finish
    await animPromise;

    if (data.status !== 'success') {
      throw new Error(data.message || 'Backend returned an error.');
    }

    // Step 6 - cross verification done
    state.currentStep = 6;
    renderStepper(7, false); // 7 = all done

    renderVerdict(data);
    renderAgents(data.agent_contributions);
    addHistory(input, data.final_verdict.verdict);

  } catch (err) {
    await animPromise;
    renderStepper(0, false);
    showError(
      err.message.includes('Failed to fetch')
        ? 'Cannot reach the backend. Make sure your FastAPI server is running on http://127.0.0.1:8000'
        : err.message
    );
  } finally {
    setAnalyzing(false);
  }
}

// =============================================
// RENDER VERDICT
// =============================================
function renderVerdict(data) {
  const { verdict, confidence_score, explanation } = data.final_verdict;
  const agents = data.agent_contributions;
  const pct = Math.round(confidence_score * 100);

  const panel = document.getElementById('verdictPanel');
  panel.className = `card verdict-card verdict-${verdict} fade-in`;
  panel.classList.remove('hidden');

  // Icon
  const icons = { REAL: '✅', FAKE: '🚫', UNVERIFIED: '❓' };
  document.getElementById('verdictIcon').textContent = icons[verdict] || '?';
  document.getElementById('verdictText').textContent = verdict;
  document.getElementById('verdictExplanation').textContent = explanation;

  // Confidence ring
  document.getElementById('confidencePct').textContent = pct + '%';
  const circumference = 2 * Math.PI * 40; // r=40
  const offset = circumference - (circumference * pct / 100);
  const ring = document.getElementById('ringFill');
  ring.style.strokeDasharray = circumference;
  // Animate: start at full offset, then transition to real offset
  ring.style.strokeDashoffset = circumference;
  setTimeout(() => { ring.style.strokeDashoffset = offset; }, 50);

  // Knowledge Graph badge
  const evidence = agents.knowledge_graph_evidence;
  const kgBadge = document.getElementById('kgBadge');
  const kgText  = document.getElementById('kgText');
  if (evidence && evidence.length > 0) {
    kgBadge.classList.remove('hidden');
    kgText.textContent = `Knowledge Graph: "${evidence[0]}"`;
  } else {
    kgBadge.classList.add('hidden');
  }
}

// =============================================
// RENDER AGENTS
// =============================================
function renderAgents(agents) {
  const panel = document.getElementById('agentPanel');
  panel.classList.remove('hidden');
  panel.classList.add('fade-in');

  const grid = document.getElementById('agentGrid');

  // Build agent cards from the actual API response structure
  const cards = [
    buildClaimCard(agents.claim_extraction_agent),
    buildLinguisticCard(agents.linguistic_agent),
    buildSourceCard(agents.source_credibility_agent),
    buildEvidenceCard(agents.knowledge_graph_evidence),
    buildMLCard(agents.ml_classifier),
  ];

  grid.innerHTML = cards.join('');
}

function agentCard(icon, name, level, bodyHTML) {
  return `
    <div class="agent-card">
      <div class="agent-top">
        <div class="agent-name-row">
          <div class="agent-icon">${icon}</div>
          <div>
            <div class="agent-name">${name}</div>
            <div class="agent-level">Agent Level 2</div>
          </div>
        </div>
      </div>
      <div class="agent-body">${bodyHTML}</div>
    </div>`;
}

function dataRow(key, val) {
  return `<div class="data-row"><span class="data-key">${key}</span><span class="data-val">${val}</span></div>`;
}

function buildClaimCard(data) {
  const entities = data.identified_entities;
  const body = entities && entities.length > 0
    ? dataRow('Entities Found', entities.join(', '))
    : dataRow('Entities Found', 'None detected');
  return agentCard('🔍', 'Claim Extraction Agent', 2, body);
}

function buildLinguisticCard(data) {
  const score = Math.round(data.linguistic_integrity_score * 100);
  const flags = data.flags || [];
  let body = dataRow('Integrity Score', score + '%');
  if (flags.length > 0) {
    body += `<div class="flag-list">${flags.map(f => `<span class="flag-tag">⚠ ${f}</span>`).join('')}</div>`;
  } else {
    body += `<div class="flag-list"><span class="no-flags">✓ No clickbait detected</span></div>`;
  }
  return agentCard('🧠', 'Linguistic Analysis Agent', 2, body);
}

function buildSourceCard(data) {
  const entries = Object.entries(data || {});
  const body = entries.length > 0
    ? entries.map(([entity, score]) => dataRow(entity.toUpperCase(), score)).join('')
    : dataRow('Source Data', 'No known sources identified');
  return agentCard('🏛', 'Source Credibility Agent', 2, body);
}

function buildEvidenceCard(data) {
  const evidence = data || [];
  const body = evidence.length > 0
    ? evidence.map((e, i) => dataRow(`Evidence ${i + 1}`, e)).join('')
    : dataRow('Knowledge Graph', 'No matching records found');
  return agentCard('🗄', 'Evidence Retrieval Agent', 2, body);
}

function buildMLCard(data) {
  const conf = Math.round(data.confidence * 100);
  const body = dataRow('Model', data.model)
    + dataRow('Prediction', data.prediction)
    + dataRow('Confidence', conf + '%');
  return agentCard('⚙️', 'ML Classification Agent', 2, body);
}

// =============================================
// HISTORY
// =============================================
function addHistory(text, verdict) {
  const item = {
    text: text.slice(0, 80) + (text.length > 80 ? '...' : ''),
    verdict,
    time: new Date().toLocaleTimeString()
  };
  state.history = [item, ...state.history.slice(0, 4)];
  renderHistory();
}

function renderHistory() {
  const el = document.getElementById('historyList');
  if (state.history.length === 0) {
    el.innerHTML = '<div class="history-empty">No analyses yet in this session.</div>';
    return;
  }
  el.innerHTML = state.history.map((item, idx) => `
    <button class="history-item" onclick="reloadHistory(${idx})">
      <span class="history-text">${escHtml(item.text)}</span>
      <div class="history-meta">
        <span class="history-verdict hv-${item.verdict}">${item.verdict}</span>
        <span class="history-time">${item.time}</span>
      </div>
    </button>`).join('');
}

function reloadHistory(idx) {
  const item = state.history[idx];
  if (!item) return;
  switchTab('text');
  document.getElementById('newsInput').value = item.text;
}

// =============================================
// ERROR HANDLING
// =============================================
function showError(msg) {
  const banner = document.getElementById('errorBanner');
  document.getElementById('errorMsg').textContent = msg;
  banner.classList.remove('hidden');
}

function clearError() {
  document.getElementById('errorBanner').classList.add('hidden');
}

// =============================================
// UTILS
// =============================================
function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
