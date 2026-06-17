import { PIPELINE_STEPS, state, sanitize } from './state.js';

export const UIRenderer = {
  switchTab(targetTabId) {
    state.activeTab = targetTabId;
    
    // Toggle active navigation buttons
    document.querySelectorAll('.menu-item').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-tab') === targetTabId);
    });

    // Toggle viewport tab sections
    document.querySelectorAll('.tab-view').forEach(view => {
      view.classList.add('hidden');
    });
    
    const targetView = document.getElementById(`tabContent${targetTabId.charAt(0).toUpperCase() + targetTabId.slice(1)}`);
    if (targetView) {
      targetView.classList.remove('hidden');
    }

    // Update system frame headers to match WSO2 clean style (no "AI")
    const titleMap = { 
      dashboard: 'TRUTHLENS Verification Engine', 
      topology: 'Pipeline Node Topology', 
      ledger: 'Audit Ledger Transactions', 
      analytics: 'System Performance Metrics' 
    };
    document.getElementById('pageTitle').textContent = titleMap[targetTabId] || 'TRUTHLENS';
  },

  switchMode(mode) {
    state.activeMode = mode;
    document.getElementById('modeBtnText').classList.toggle('active', mode === 'text');
    document.getElementById('modeBtnUrl').classList.toggle('active', mode === 'url');
    document.getElementById('newsInput').classList.toggle('hidden', mode !== 'text');
    document.getElementById('urlInput').classList.toggle('hidden', mode !== 'url');
  },

  setProcessing(isAnalyzing) {
    state.isAnalyzing = isAnalyzing;
    const btn = document.getElementById('analyzeBtn');
    const btnText = document.getElementById('btnText');
    const btnIcon = document.getElementById('btnIcon');
    
    btn.disabled = isAnalyzing;
    if (isAnalyzing) {
      btnText.textContent = 'EXECUTING CONSENSUS CHAIN...';
      btnIcon.innerHTML = '<span class="spinner"></span>';
    } else {
      btnText.textContent = 'EXECUTE CONSENSUS AUDIT';
      btnIcon.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="5" y1="12" x2="19" y2="12"></line>
          <polyline points="12 5 19 12 12 19"></polyline>
        </svg>
      `;
    }
  },

  renderStepper(currentStepId, running = false) {
    const track = document.getElementById('stepper');
    if (!track) return;
    
    track.innerHTML = PIPELINE_STEPS.map(step => {
      const isDone = currentStepId > step.id;
      const isActive = running && currentStepId === step.id;
      const stepClass = isDone ? 'completed' : isActive ? 'active' : 'pending';
      
      let indicatorSvg = '';
      if (isDone) {
        indicatorSvg = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        `;
      } else if (isActive) {
        indicatorSvg = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="pulse-spin">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        `;
      } else {
        indicatorSvg = `<span style="font-size: 8px;">●</span>`;
      }

      return `
        <div class="step-node ${stepClass}">
          <div class="step-node-icon">${indicatorSvg}</div>
          <div class="step-node-body">
            <div class="step-node-name">${step.name}</div>
            <div class="step-node-role">${step.role}</div>
          </div>
        </div>`;
    }).join('');
  },

  clearResultsPanel() {
    document.getElementById('verdictPanel').classList.add('hidden');
    document.getElementById('modulesPanel').classList.add('hidden');
  },

  renderResults(data) {
    const vPanel = document.getElementById('verdictPanel');
    const mPanel = document.getElementById('modulesPanel');
    const grid = document.getElementById('modulesGrid');
    
    if (!vPanel || !mPanel || !grid) return;

    const finalVerdict = data.final_verdict || {};
    const contributions = data.agent_contributions || {};

    const verdictType = finalVerdict.verdict || 'UNVERIFIED';
    const confidenceScore = Math.round((finalVerdict.confidence_score || 0) * 100);
    const explanation = finalVerdict.explanation || 'No summary compilation logged.';

    // Setup verdict colors
    vPanel.className = `console-card verdict-card-base verdict-${verdictType}`;
    vPanel.classList.remove('hidden');
    
    document.getElementById('verdictText').textContent = verdictType;
    document.getElementById('verdictExplanation').textContent = explanation;
    
    // Animate radial progress confidence circle
    document.getElementById('confidencePct').textContent = `${confidenceScore}%`;
    const fillCircle = document.getElementById('ringFill');
    if (fillCircle) {
      const cRadius = fillCircle.r.baseVal.value;
      const circumference = 2 * Math.PI * cRadius;
      fillCircle.style.strokeDashoffset = circumference - (confidenceScore / 100) * circumference;
    }

    // Knowledge graph status badge
    const isKgVerified = contributions.evidence_retrieval?.evidence_found || false;
    const kgBadge = document.getElementById('kgBadge');
    if (kgBadge) {
      kgBadge.classList.toggle('hidden', !isKgVerified);
      if (isKgVerified && contributions.evidence_retrieval?.evidence_text) {
        document.getElementById('kgText').textContent = `Evidence anchored in Ledger Database: "${contributions.evidence_retrieval.evidence_text}"`;
      }
    }

    // Render 6 module cards in grid
    mPanel.classList.remove('hidden');
    
    const cardData = [
      // 1. Claim Extraction
      {
        title: 'Claim Extraction Module',
        desc: 'Identifies core targets & declared claims.',
        icon: `
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
        `,
        renderBody: () => {
          const entities = contributions.claim_extraction?.entities || [];
          const claims = contributions.claim_extraction?.claims || [];
          
          if (entities.length === 0 && claims.length === 0) {
            return `<div class="empty-state-card">No targets identified.</div>`;
          }
          
          const entityBadges = entities.map(ent => `<span class="tag-badge-gold">${sanitize(ent.toUpperCase())}</span>`).join(' ');
          const claimList = claims.map(clm => `<div class="sub-claim-text">• ${sanitize(clm)}</div>`).join('');
          
          return `
            <div style="display:flex; flex-direction:column; gap: 8px;">
              <div class="card-metric-row"><span class="metric-lbl">Target Subjects:</span><div class="badge-row">${entityBadges || 'None'}</div></div>
              <div class="card-metric-row"><span class="metric-lbl">Isolated Claims:</span><div style="margin-top:2px;">${claimList}</div></div>
            </div>`;
        }
      },
      // 2. Linguistic Analysis
      {
        title: 'Linguistic Analysis Module',
        desc: 'Measures vocabulary sensationalism metrics.',
        icon: `
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
          </svg>
        `,
        renderBody: () => {
          const score = Math.round((contributions.linguistic_analysis?.sensationalism_score || 0) * 100);
          const words = contributions.linguistic_analysis?.clickbait_words || [];
          
          const progressColorClass = score > 50 ? 'progress-danger' : 'progress-success';
          const wordBadges = words.map(w => `<span class="tag-badge-danger">${sanitize(w)}</span>`).join(' ');
          
          return `
            <div style="display:flex; flex-direction:column; gap: 8px;">
              <div class="card-metric-row">
                <span class="metric-lbl">Sensationalism Score:</span>
                <span class="metric-val" style="color: ${score > 50 ? 'var(--verdict-fake)' : 'var(--verdict-real)'};">${score}%</span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar-fill ${progressColorClass}" style="width: ${score}%;"></div>
              </div>
              <div class="card-metric-row" style="margin-top:4px;">
                <span class="metric-lbl">Trigger Terminology:</span>
                <div class="badge-row">${wordBadges || '<span style="color:var(--text-muted); font-style:italic;">None detected</span>'}</div>
              </div>
            </div>`;
        }
      },
      // 3. Source Credibility
      {
        title: 'Source Credibility Module',
        desc: 'Verifies registry authority reliability ratings.',
        icon: `
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
        `,
        renderBody: () => {
          const sources = contributions.source_credibility?.sources || {};
          const sourceKeys = Object.keys(sources);
          
          if (sourceKeys.length === 0) {
            return `<div class="empty-state-card">No validated sources identified.</div>`;
          }
          
          const sourceRows = sourceKeys.map(src => {
            const trust = sources[src];
            const isHigh = trust === 'High';
            return `
              <div class="meta-row">
                <span class="meta-key">${sanitize(src.toUpperCase())}</span>
                <span class="meta-val" style="color:${isHigh ? 'var(--verdict-real)' : 'var(--text-muted)'}; font-weight:700;">
                  ${isHigh ? '🛡 HIGH TRUST' : '⚠️ UNREGULATED'}
                </span>
              </div>`;
          }).join('');
          
          return `<div style="display:flex; flex-direction:column; gap: 4px;">${sourceRows}</div>`;
        }
      },
      // 4. Evidence Retrieval
      {
        title: 'Ledger Retrieval Module',
        desc: 'Cross-checks claim nodes against verified facts.',
        icon: `
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"></path>
          </svg>
        `,
        renderBody: () => {
          const found = contributions.evidence_retrieval?.evidence_found || false;
          const text = contributions.evidence_retrieval?.evidence_text || '';
          
          if (!found) {
            return `
              <div class="evidence-db-card empty">
                <div style="font-size: 10px; font-weight:700; color:var(--text-muted);">LEDGER QUERY: EMPTY</div>
                <div style="font-size: 11px; margin-top:4px;">No anchor matching this claim structure was found in historical fact matrices.</div>
              </div>`;
          }
          
          return `
            <div class="evidence-db-card found">
              <div style="display:flex; justify-content:space-between; font-size:9px; font-weight:700; color:var(--verdict-real);">
                <span>LEDGER MATCH VERIFIED</span>
                <span>NODE #KG-7402</span>
              </div>
              <div style="font-size: 11px; margin-top:6px; font-style:italic; line-height:1.4; color:var(--text-main);">"${sanitize(text)}"</div>
            </div>`;
        }
      },
      // 5. Model Classification
      {
        title: 'Classification Model Engine',
        desc: 'Calculates statistical probability predictions.',
        icon: `
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line>
          </svg>
        `,
        renderBody: () => {
          const pred = contributions.ml_classification?.prediction || 'UNVERIFIED';
          const prob = contributions.ml_classification?.probability || 0;
          const pct = Math.round(prob * 100);
          
          let color = 'var(--text-muted)';
          if (pred === 'REAL') color = 'var(--verdict-real)';
          if (pred === 'FAKE') color = 'var(--verdict-fake)';
          
          return `
            <div style="display:flex; flex-direction:column; gap: 8px;">
              <div class="card-metric-row">
                <span class="metric-lbl">Engine Prediction:</span>
                <span class="metric-val" style="color:${color}; font-weight:800;">${pred}</span>
              </div>
              <div class="card-metric-row">
                <span class="metric-lbl">Confidence Margin:</span>
                <span class="metric-val">${pct}%</span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: ${pct}%; background-color: var(--brand-accent);"></div>
              </div>
            </div>`;
        }
      },
      // 6. Cross Verification
      {
        title: 'Consensus Resolution Module',
        desc: 'Applies priority rules over module outcomes.',
        icon: `
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline>
          </svg>
        `,
        renderBody: () => {
          const rule = contributions.cross_verification?.rule_triggered || 'None';
          return `
            <div style="display:flex; flex-direction:column; gap: 6px;">
              <span class="metric-lbl">Orchestration Override Rule:</span>
              <div class="rule-trigger-box">
                <div style="font-size:9px; font-weight:700; color:var(--brand-accent); font-family:var(--font-mono); text-transform:uppercase;">Rule Triggered</div>
                <div style="font-size:11px; margin-top:2px; font-weight:600; color:#ffffff;">${sanitize(rule)}</div>
              </div>
            </div>`;
        }
      }
    ];

    grid.innerHTML = cardData.map(c => `
      <div class="agent-grid-node">
        <div class="agent-node-head">
          <div class="agent-node-icon">${c.icon}</div>
          <div class="agent-node-title">${c.title}</div>
        </div>
        <p class="agent-node-desc">${c.desc}</p>
        <div class="agent-node-body" style="margin-top: 10px;">
          ${c.renderBody()}
        </div>
      </div>
    `).join('');
  },

  saveHistoryToStorage() {
    try {
      localStorage.setItem('truthlens_ledger_logs', JSON.stringify(state.history));
    } catch (e) {
      console.warn("Storage write access blocked.", e);
    }
  },

  loadHistoryFromStorage() {
    try {
      const stored = localStorage.getItem('truthlens_ledger_logs');
      if (stored) {
        state.history = JSON.parse(stored);
      } else {
        state.history = [];
      }
    } catch (e) {
      console.warn("Storage read access blocked.", e);
      state.history = [];
    }
  },

  renderHistory() {
    const tbody = document.getElementById('historyTableBody');
    if (!tbody) return;

    if (state.history.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="3" style="text-align:center; color:var(--text-faint); font-style:italic; padding:40px 20px;">
            Transaction log ledger empty. Execute claims verification to write logs.
          </td>
        </tr>`;
      return;
    }

    tbody.innerHTML = state.history.map((log, index) => `
      <tr class="clickable-row" data-idx="${index}">
        <td class="ledger-text-cell" title="${sanitize(log.text)}">${sanitize(log.text)}</td>
        <td><span class="tbl-badge badge-${log.verdict}">${log.verdict}</span></td>
        <td style="font-family:var(--font-mono); font-size:11px; color:var(--text-muted); text-align:right;">${log.time}</td>
      </tr>`).join('');
  },

  renderAnalyticsTab() {
    // Generate/render metrics contents dynamically
    const metricsGrid = document.getElementById('analyticsMetricsContainer');
    if (!metricsGrid) return;

    metricsGrid.innerHTML = `
      <div class="console-card">
        <div class="card-lead">
          <div class="lead-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line><line x1="15" y1="3" x2="15" y2="21"></line><line x1="3" y1="9" x2="21" y2="9"></line><line x1="3" y1="15" x2="21" y2="15"></line>
            </svg>
          </div>
          <div>
            <h3>Confusion Matrix</h3>
            <p class="lead-sub">Module validation outcome distribution parameters</p>
          </div>
        </div>
        
        <div class="matrix-mock">
          <div class="matrix-cell true-positive">
            942
            <small>TRUE REAL</small>
          </div>
          <div class="matrix-cell false-positive">
            18
            <small>FALSE REAL</small>
          </div>
          <div class="matrix-cell false-negative">
            29
            <small>FALSE FAKE</small>
          </div>
          <div class="matrix-cell true-negative">
            811
            <small>TRUE FAKE</small>
          </div>
        </div>
      </div>

      <div class="console-card">
        <div class="card-lead">
          <div class="lead-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
          </div>
          <div>
            <h3>Classification Calibrations</h3>
            <p class="lead-sub">Consensus engine accuracy stats</p>
          </div>
        </div>

        <ul class="analytics-list">
          <li>
            <span>F1-Score (Factual claims):</span>
            <strong>97.4%</strong>
          </li>
          <li>
            <span>Precision Index:</span>
            <strong>98.1%</strong>
          </li>
          <li>
            <span>Recall Bound:</span>
            <strong>96.8%</strong>
          </li>
          <li>
            <span>Consensus Ledger Sync Latency:</span>
            <strong>12ms</strong>
          </li>
        </ul>
      </div>

      <div class="console-card" style="grid-column: span 2;">
        <div class="card-lead">
          <div class="lead-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          <div>
            <h3>Frequent Clickbait Trigger Words</h3>
            <p class="lead-sub">Linguistic modules vocabulary matches over last 10,000 queries</p>
          </div>
        </div>
        
        <div class="word-frequency-bars" style="display:flex; flex-direction:column; gap:10px; margin-top:10px;">
          <div>
            <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
              <span class="tag-badge-danger">SHOCKING</span>
              <span>1,482 hits</span>
            </div>
            <div class="progress-bar-container"><div class="progress-bar-fill progress-danger" style="width: 85%;"></div></div>
          </div>
          <div>
            <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
              <span class="tag-badge-danger">SECRET</span>
              <span>1,194 hits</span>
            </div>
            <div class="progress-bar-container"><div class="progress-bar-fill progress-danger" style="width: 68%;"></div></div>
          </div>
          <div>
            <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
              <span class="tag-badge-danger">CONSPIRACY</span>
              <span>908 hits</span>
            </div>
            <div class="progress-bar-container"><div class="progress-bar-fill progress-danger" style="width: 52%;"></div></div>
          </div>
          <div>
            <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
              <span class="tag-badge-danger">UNBELIEVABLE</span>
              <span>541 hits</span>
            </div>
            <div class="progress-bar-container"><div class="progress-bar-fill progress-danger" style="width: 31%;"></div></div>
          </div>
        </div>
      </div>
    `;
  },

  showToastError(msg) {
    const errorBanner = document.getElementById('errorBanner');
    const errorMsg = document.getElementById('errorMsg');
    if (errorBanner && errorMsg) {
      errorMsg.textContent = msg;
      errorBanner.classList.remove('hidden');
    }
  },

  dismissToastError() {
    const errorBanner = document.getElementById('errorBanner');
    if (errorBanner) {
      errorBanner.classList.add('hidden');
    }
  }
};