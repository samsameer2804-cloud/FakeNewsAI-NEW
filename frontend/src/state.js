export const CONFIG = {
  API_URL: 'http://127.0.0.1:8000/analyze'
};

export const PIPELINE_STEPS = [
  { id: 1, name: 'Claim Extraction',    role: 'Isolates entity arrays & factual data strings.' },
  { id: 2, name: 'Linguistic Analysis', role: 'Evaluates hyperbole and sensational text vectors.' },
  { id: 3, name: 'Source Credibility',  role: 'Queries authority registry databases.' },
  { id: 4, name: 'Evidence Retrieval',  role: 'Scans the Knowledge Graph node index.' },
  { id: 5, name: 'Model Classification',role: 'Executes statistical classification model.' },
  { id: 6, name: 'Cross Verification',  role: 'Resolves final override constraints.' }
];

export const SAMPLES = {
  real: `NASA successfully launched a new lunar mission.`,
  fake: `SHOCKING SECRET ALIEN CONSPIRACY REVEALED BY NASA`,
  neutral: `A company announced a new technology product yesterday.`
};

export const state = {
  activeTab: 'dashboard',
  activeMode: 'text',
  isAnalyzing: false,
  history: []
};

export function sanitize(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
}