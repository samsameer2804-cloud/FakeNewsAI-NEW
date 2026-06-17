import { state, SAMPLES } from './state.js';
import { UIRenderer } from './ui.js';
import { APIService } from './api.js';

document.addEventListener('DOMContentLoaded', () => {
  // Initialize presentation structures
  UIRenderer.loadHistoryFromStorage();
  UIRenderer.renderStepper(1, false);
  UIRenderer.renderHistory();
  UIRenderer.renderAnalyticsTab();
  initializeListeners();
});

function initializeListeners() {
  // Hamburger Sidebar Toggle
  const hamburgerBtn = document.querySelector('.hamburger-btn');
  const sidebar = document.querySelector('.sidebar');
  if (hamburgerBtn && sidebar) {
    hamburgerBtn.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });
  }

  // Navigation Sidebar Controls (Tab Switchers)
  document.querySelectorAll('.sidebar-menu .menu-item').forEach(button => {
    button.addEventListener('click', (e) => {
      const selectedTab = e.currentTarget.getAttribute('data-tab');
      UIRenderer.switchTab(selectedTab);
    });
  });

  // Mode Toggles inside Input Console
  document.getElementById('modeBtnText').addEventListener('click', () => {
    if (!state.isAnalyzing) UIRenderer.switchMode('text');
  });
  document.getElementById('modeBtnUrl').addEventListener('click', () => {
    if (!state.isAnalyzing) UIRenderer.switchMode('url');
  });

  // Mock Injection Listeners
  document.getElementById('sampleFakeBtn').addEventListener('click', () => injectText('fake'));
  document.getElementById('sampleRealBtn').addEventListener('click', () => injectText('real'));
  document.getElementById('sampleNeutralBtn').addEventListener('click', () => injectText('neutral'));

  // Main Execution Link Event Ingestion
  document.getElementById('analyzeBtn').addEventListener('click', () => {
    if (state.isAnalyzing) return;

    const isTextMode = state.activeMode === 'text';
    const targetElement = document.getElementById(isTextMode ? 'newsInput' : 'urlInput');
    const rawPayload = targetElement.value.trim();

    if (!rawPayload) {
      UIRenderer.showToastError(isTextMode 
        ? 'Operation aborted: Text input cannot be empty.' 
        : 'Operation aborted: System requires a valid target URL.'
      );
      return;
    }

    APIService.runAnalysisPipeline(rawPayload);
  });

  // Error Clear Controls
  const closeErrorBtn = document.getElementById('closeErrorBtn');
  if (closeErrorBtn) {
    closeErrorBtn.addEventListener('click', UIRenderer.dismissToastError);
  }

  // Table Row Selection Delegation to reload historical data items
  const historyTableBody = document.getElementById('historyTableBody');
  if (historyTableBody) {
    historyTableBody.addEventListener('click', (e) => {
      const historicalRow = e.target.closest('.clickable-row');
      if (!historicalRow || state.isAnalyzing) return;

      const chosenIndex = parseInt(historicalRow.getAttribute('data-idx'), 10);
      const contextRecord = state.history[chosenIndex];

      if (contextRecord) {
        UIRenderer.switchTab('dashboard');
        UIRenderer.switchMode('text');
        document.getElementById('newsInput').value = contextRecord.text;
      }
    });
  }
}

function injectText(sampleKey) {
  if (state.isAnalyzing) return;
  UIRenderer.switchMode('text');
  const newsInput = document.getElementById('newsInput');
  if (newsInput) {
    newsInput.value = SAMPLES[sampleKey];
  }
}