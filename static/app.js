const API = '/api';
const TOKEN_KEY = 'arborist_token';
let isGoogleLinked = false;
let allTrainings = [];

const loginScreen = document.getElementById('loginScreen');
const appWrap = document.getElementById('appWrap');
const loginForm = document.getElementById('loginForm');
const loginPassword = document.getElementById('loginPassword');
const loginError = document.getElementById('loginError');

const authText = document.getElementById('authText');
const linkGoogle = document.getElementById('linkGoogle');
const googleLinked = document.getElementById('googleLinked');
const loadSamplesBtn = document.getElementById('loadSamplesBtn');
const newTrainingBtn = document.getElementById('newTrainingBtn');
const searchInput = document.getElementById('searchInput');
const loading = document.getElementById('loading');
const emptyState = document.getElementById('emptyState');
const sectionsEl = document.getElementById('sections');
const emptyLoadSamples = document.getElementById('emptyLoadSamples');
const emptyNewTraining = document.getElementById('emptyNewTraining');
const toastEl = document.getElementById('toast');

const standardLabel = { ISA: 'ISA', ANSI_Z133: 'ANSI Z133', OSHA_CRANE: 'OSHA Crane' };
const CATEGORY_ORDER = [
  'Climbing & Aerial', 'Electrical Hazards', 'Power Line Safety', 'Risk Assessment', 'Tree Removal',
  'Rigging', 'Safety Equipment', 'Equipment Operations', 'Worksite Safety', 'Inspections',
  'Load Operations', 'Qualifications', 'Assembly & Ground', 'Signals & Communication',
  'Pruning', 'Tree Biology', 'Planting', 'Soil & Roots', 'Pest Management', 'Urban Forestry',
  'Deep Dive', 'General'
];
const CATEGORY_LABELS = { 'Risk Assessment': 'Tree Hazard & Risk Assessment' };
let coverFilter = 'all';
let categoryFilter = '';

// Toast notifications
function toast(message, type = 'success') {
  toastEl.textContent = message;
  toastEl.className = 'toast show ' + type;
  clearTimeout(toastEl._timeout);
  toastEl._timeout = setTimeout(() => {
    toastEl.className = 'toast';
  }, 3000);
}

// Google link (server-side)
async function fetchGoogleLinked() {
  try {
    const r = await api('GET', '/settings/google-linked');
    return !!r?.linked;
  } catch { return false; }
}

async function updateAuthUI() {
  isGoogleLinked = await fetchGoogleLinked();
  if (isGoogleLinked) {
    authText.style.display = 'none';
    if (linkGoogle) linkGoogle.style.display = 'none';
    if (googleLinked) googleLinked.style.display = 'inline-flex';
  } else {
    authText.style.display = 'inline';
    if (linkGoogle) linkGoogle.style.display = 'inline-flex';
    if (googleLinked) googleLinked.style.display = 'none';
  }
}

if (linkGoogle) linkGoogle.addEventListener('click', () => location.href = '/auth/google/link');

async function parseHashAfterLogin() {
  const hash = window.location.hash || '';
  if (hash.includes('google_linked=1')) {
    history.replaceState(null, '', location.pathname + location.search);
    toast('Google account linked');
    await updateAuthUI();
    if (allTrainings.length > 0) renderTrainings(allTrainings);
  }
}

// App login
function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(t) {
  localStorage.setItem(TOKEN_KEY, t);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function showApp() {
  if (loginScreen) loginScreen.style.display = 'none';
  if (appWrap) appWrap.style.display = 'block';
}

function showLogin() {
  clearToken();
  if (loginScreen) loginScreen.style.display = 'flex';
  if (appWrap) appWrap.style.display = 'none';
}

function checkAuth() {
  if (getToken()) {
    showApp();
    return true;
  }
  showLogin();
  return false;
}

if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (loginError) loginError.style.display = 'none';
    const pw = loginPassword ? loginPassword.value : '';
    try {
      const res = await fetch(API + '/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pw })
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || 'Login failed');
      setToken(data.token);
      showApp();
      parseHashAfterLogin();
      updateAuthUI();
      loadTrainings();
    } catch (err) {
      if (loginError) {
        loginError.textContent = err.message || 'Login failed';
        loginError.style.display = 'block';
      }
    }
  });
}

// API
async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  const token = getToken();
  if (token) opts.headers['Authorization'] = 'Bearer ' + token;
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  if (res.status === 401) {
    showLogin();
    throw new Error('Session expired');
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

function escapeHtml(s) {
  if (!s) return '';
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function matchesSearch(t, q) {
  if (!q || !q.trim()) return true;
  const lower = q.toLowerCase();
  const title = (t.title || '').toLowerCase();
  const desc = (t.description || '').toLowerCase();
  const category = (t.category || '').toLowerCase();
  const std = (standardLabel[t.standard] || t.standard || '').toLowerCase();
  const topics = Array.isArray(t.topics) ? t.topics.join(' ') : (t.topics || '');
  const topicsLower = topics.toLowerCase();
  return title.includes(lower) || desc.includes(lower) || category.includes(lower) || std.includes(lower) || topicsLower.includes(lower);
}

function filterByCovered(t) {
  const covered = !!t.covered_at;
  if (coverFilter === 'covered') return covered;
  if (coverFilter === 'not_covered') return !covered;
  return true;
}

function filterByCategory(t) {
  if (!categoryFilter) return true;
  return (t.category || 'General') === categoryFilter;
}

function getUniqueCategories(list) {
  const set = new Set();
  list.forEach(t => {
    const c = t.category || 'General';
    if (c) set.add(c);
  });
  return [...set].sort((a, b) => {
    const ia = CATEGORY_ORDER.indexOf(a);
    const ib = CATEGORY_ORDER.indexOf(b);
    if (ia >= 0 && ib >= 0) return ia - ib;
    if (ia >= 0) return -1;
    if (ib >= 0) return 1;
    return a.localeCompare(b);
  });
}

function groupTrainings(list) {
  const searchFiltered = list.filter(t => matchesSearch(t, searchInput ? searchInput.value : ''));
  const filtered = searchFiltered.filter(filterByCovered).filter(filterByCategory);
  const deepDives = filtered.filter(t => (t.format || '').toLowerCase() === 'deep_dive');
  const standard = filtered.filter(t => (t.format || '').toLowerCase() !== 'deep_dive');
  const result = [];
  if (deepDives.length > 0 && (!categoryFilter || categoryFilter === 'Deep Dive')) {
    result.push({ category: 'Deep Dive', label: 'Deep Dive (2–4 hrs, ~30 slides)', byStandard: { '': deepDives } });
  }
  const byCat = {};
  standard.forEach(t => {
    const cat = t.category || 'General';
    if (!byCat[cat]) byCat[cat] = {};
    const std = t.standard || 'Other';
    if (!byCat[cat][std]) byCat[cat][std] = [];
    byCat[cat][std].push(t);
  });
  const catsToShow = categoryFilter ? [categoryFilter] : [
    ...CATEGORY_ORDER.filter(c => byCat[c]),
    ...Object.keys(byCat).filter(c => !CATEGORY_ORDER.includes(c)).sort()
  ];
  catsToShow.forEach(cat => {
    if (!byCat[cat] || Object.keys(byCat[cat]).length === 0) return;
    const stdOrder = ['ANSI_Z133', 'ISA', 'OSHA_CRANE'];
    const byStandard = {};
    Object.entries(byCat[cat]).forEach(([std, items]) => {
      byStandard[std] = items.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
    });
    result.push({
      category: cat,
      label: CATEGORY_LABELS[cat] || cat,
      byStandard: Object.keys(byStandard).sort((a, b) => {
        const ia = stdOrder.indexOf(a);
        const ib = stdOrder.indexOf(b);
        if (ia >= 0 && ib >= 0) return ia - ib;
        return (a || '').localeCompare(b || '');
      }).reduce((acc, k) => { acc[k] = byStandard[k]; return acc; }, {})
    });
  });
  return result;
}

function formatCoveredDate(coveredAt) {
  if (!coveredAt) return '';
  try {
    const d = new Date(coveredAt);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  } catch { return ''; }
}

function updateProgressSummary(list) {
  const progressSummary = document.getElementById('progressSummary');
  const progressText = document.getElementById('progressText');
  const progressFill = document.getElementById('progressFill');
  const categorySelect = document.getElementById('categoryFilter');
  if (!progressSummary || list.length === 0) return;
  progressSummary.style.display = 'block';
  const covered = list.filter(t => t.covered_at).length;
  const total = list.length;
  progressText.textContent = `${covered} of ${total} covered`;
  progressFill.style.width = total ? `${(covered / total) * 100}%` : '0%';
  if (categorySelect) {
    const cats = getUniqueCategories(list);
    const currentVal = categorySelect.value;
    categorySelect.innerHTML = '<option value="">All categories</option>' +
      cats.map(c => `<option value="${escapeHtml(c)}"${c === currentVal ? ' selected' : ''}>${escapeHtml(CATEGORY_LABELS[c] || c)}</option>`).join('');
  }
}

function renderTrainings(list) {
  allTrainings = list;
  updateProgressSummary(list);
  const grouped = groupTrainings(list);
  sectionsEl.innerHTML = '';
  if (grouped.length === 0) {
    const msg = searchInput?.value?.trim() ? 'No trainings match your search.' : 'No trainings yet.';
    sectionsEl.innerHTML = `<div class="empty-state"><p class="empty-desc">${msg}</p></div>`;
    return;
  }
  grouped.forEach(({ category, label, byStandard }) => {
    const sec = document.createElement('div');
    sec.className = 'section';
    sec.innerHTML = `<div class="section-header">${escapeHtml(label)}</div><div class="section-list"></div>`;
    const listEl = sec.querySelector('.section-list');
    Object.entries(byStandard).forEach(([std, items]) => {
      if (std) {
        const sub = document.createElement('div');
        sub.className = 'section-subheader';
        sub.textContent = standardLabel[std] || std;
        listEl.appendChild(sub);
      }
      items.forEach(t => {
        const card = document.createElement('div');
        card.className = 'card';
        const meta = [category || label, standardLabel[t.standard]].filter(Boolean).join(' · ');
        const isDeep = (t.format || '').toLowerCase() === 'deep_dive';
        const isCovered = !!t.covered_at;
        const coveredDate = formatCoveredDate(t.covered_at);
        card.innerHTML = `
          <div class="card-info">
            <div class="card-title">${escapeHtml(t.title)}</div>
            <div class="card-meta">${escapeHtml(meta)}</div>
            <div class="card-badges">
              ${isCovered ? `<span class="badge covered" title="Covered ${escapeHtml(coveredDate)}">✓ Covered${coveredDate ? ' ' + escapeHtml(coveredDate) : ''}</span>` : ''}
              ${isDeep ? '<span class="badge deep-dive">Deep Dive</span>' : ''}
              <span class="badge">${escapeHtml(t.status || 'planned')}</span>
              ${t.slides_url ? '<span class="badge slides">Slides ready</span>' : ''}
            </div>
          </div>
          <div class="card-actions">
            <button class="btn btn-ghost btn-sm btn-cover cover-btn ${isCovered ? 'covered' : ''}" title="${isCovered ? 'Mark as not covered' : 'Mark as covered'}">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="${isCovered ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>
            </button>
            ${t.slides_url ? `<a href="${escapeHtml(t.slides_url)}" target="_blank" rel="noopener">Open Slides</a>` : ''}
            <button class="btn btn-primary btn-sm gen-btn" ${!isGoogleLinked ? 'disabled title="Link Google first"' : ''}>Generate</button>
            <button class="btn btn-ghost btn-sm edit-btn">Edit</button>
            <button class="btn btn-ghost btn-sm btn-danger del-btn">Delete</button>
          </div>
        `;
        card.querySelector('.cover-btn').addEventListener('click', () => toggleCovered(t));
        card.querySelector('.gen-btn').addEventListener('click', () => {
          if (!isGoogleLinked) { toast('Link Google first', 'error'); return; }
          openGenerateModal(t);
        });
        card.querySelector('.edit-btn').addEventListener('click', () => openTrainingModal(t));
        card.querySelector('.del-btn').addEventListener('click', () => deleteTraining(t.id));
        listEl.appendChild(card);
      });
    });
    sectionsEl.appendChild(sec);
  });
}

async function loadTrainings() {
  loading.style.display = 'flex';
  emptyState.style.display = 'none';
  sectionsEl.innerHTML = '';
  try {
    const list = await api('GET', '/trainings');
    loading.style.display = 'none';
    if (list.length === 0) {
      emptyState.style.display = 'block';
      return;
    }
    renderTrainings(list);
  } catch (e) {
    loading.style.display = 'none';
    emptyState.style.display = 'block';
    emptyState.querySelector('.empty-desc').textContent = 'Error loading trainings. ' + e.message;
    toast('Error: ' + e.message, 'error');
  }
}

function openTrainingModal(t) {
  trainingModal.style.display = 'flex';
  if (t) {
    modalTitle.textContent = 'Edit Training';
    trainingId.value = t.id;
    trainingTitle.value = t.title;
    trainingDescription.value = t.description || '';
    trainingStandard.value = t.standard || 'ISA';
    trainingFormat.value = (t.format || 'standard').toLowerCase() === 'deep_dive' ? 'deep_dive' : 'standard';
    trainingCategory.value = t.category || '';
    trainingTopics.value = Array.isArray(t.topics) ? t.topics.join(', ') : (t.topics || '');
  } else {
    modalTitle.textContent = 'New Training';
    trainingId.value = '';
    trainingForm.reset();
    trainingStandard.value = 'ISA';
    trainingFormat.value = 'standard';
  }
}

async function toggleCovered(t) {
  const willCover = !t.covered_at;
  try {
    const updated = await api('POST', `/trainings/${t.id}/mark-covered`, { covered: willCover });
    const idx = allTrainings.findIndex(x => x.id === t.id);
    if (idx >= 0) allTrainings[idx] = updated;
    renderTrainings(allTrainings);
    toast(willCover ? 'Marked as covered' : 'Marked as not covered');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function deleteTraining(id) {
  if (!confirm('Delete this training?')) return;
  try {
    await api('DELETE', `/trainings/${id}`);
    loadTrainings();
    toast('Training deleted');
  } catch (e) {
    toast(e.message, 'error');
  }
}

// Modals
const trainingModal = document.getElementById('trainingModal');
const modalTitle = document.getElementById('modalTitle');
const modalClose = document.getElementById('modalClose');
const modalCancel = document.getElementById('modalCancel');
const trainingForm = document.getElementById('trainingForm');
const trainingId = document.getElementById('trainingId');
const trainingTitle = document.getElementById('trainingTitle');
const trainingDescription = document.getElementById('trainingDescription');
const trainingStandard = document.getElementById('trainingStandard');
const trainingFormat = document.getElementById('trainingFormat');
const trainingCategory = document.getElementById('trainingCategory');
const trainingTopics = document.getElementById('trainingTopics');
const generateModal = document.getElementById('generateModal');
const generateModalClose = document.getElementById('generateModalClose');
const generateTrainingName = document.getElementById('generateTrainingName');
const generateCancel = document.getElementById('generateCancel');
const generateConfirm = document.getElementById('generateConfirm');
const btnText = generateConfirm.querySelector('.btn-text');
const btnLoading = generateConfirm.querySelector('.btn-loading');

trainingModal.addEventListener('click', e => { if (e.target === trainingModal) trainingModal.style.display = 'none'; });
modalClose.addEventListener('click', () => trainingModal.style.display = 'none');
modalCancel.addEventListener('click', () => trainingModal.style.display = 'none');

newTrainingBtn.addEventListener('click', () => openTrainingModal(null));

if (emptyLoadSamples) emptyLoadSamples.addEventListener('click', () => loadSamplesBtn.click());
if (emptyNewTraining) emptyNewTraining.addEventListener('click', () => openTrainingModal(null));

loadSamplesBtn.addEventListener('click', async () => {
  const label = loadSamplesBtn.querySelector('.btn-label');
  const origText = label ? label.textContent : (loadSamplesBtn.dataset?.label || 'Load samples');
  loadSamplesBtn.disabled = true;
  if (label) label.textContent = 'Loading…';
  try {
    const r = await api('POST', '/trainings/seed');
    loadTrainings();
    toast(r.added > 0 ? `Added ${r.added} sample trainings` : 'Samples already loaded');
  } catch (e) {
    toast(e.message, 'error');
  } finally {
    loadSamplesBtn.disabled = false;
    if (label) label.textContent = origText;
  }
});

if (searchInput) {
  searchInput.addEventListener('input', () => {
    if (allTrainings.length > 0) renderTrainings(allTrainings);
  });
}

document.querySelectorAll('.progress-filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.progress-filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    coverFilter = btn.dataset.filter || 'all';
    if (allTrainings.length > 0) renderTrainings(allTrainings);
  });
});

const categoryFilterEl = document.getElementById('categoryFilter');
if (categoryFilterEl) {
  categoryFilterEl.addEventListener('change', () => {
    categoryFilter = categoryFilterEl.value || '';
    if (allTrainings.length > 0) renderTrainings(allTrainings);
  });
}

trainingForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = trainingId.value;
  const data = {
    title: trainingTitle.value.trim(),
    description: trainingDescription.value.trim(),
    standard: trainingStandard.value,
    category: trainingCategory.value.trim(),
    format: trainingFormat.value,
    topics: trainingTopics.value.split(',').map(s => s.trim()).filter(Boolean),
  };
  try {
    if (id) {
      await api('PATCH', `/trainings/${id}`, { title: data.title, description: data.description, category: data.category, format: data.format });
      toast('Training updated');
    } else {
      await api('POST', '/trainings', data);
      toast('Training created');
    }
    trainingModal.style.display = 'none';
    loadTrainings();
  } catch (e) {
    toast(e.message, 'error');
  }
});

let generateTraining = null;
function openGenerateModal(t) {
  generateTraining = t;
  generateTrainingName.textContent = t.title;
  generateModal.style.display = 'flex';
}

generateModal.addEventListener('click', e => { if (e.target === generateModal) generateModal.style.display = 'none'; });
generateModalClose.addEventListener('click', () => generateModal.style.display = 'none');
generateCancel.addEventListener('click', () => generateModal.style.display = 'none');

generateConfirm.addEventListener('click', async () => {
  if (!generateTraining || !isGoogleLinked) return;
  btnText.style.display = 'none';
  btnLoading.style.display = 'inline-flex';
  generateConfirm.disabled = true;
  try {
    const r = await api('POST', `/trainings/${generateTraining.id}/generate-slides`, {});
    generateModal.style.display = 'none';
    loadTrainings();
    toast('Slides created! Opening…');
    if (r.slides_url) window.open(r.slides_url, '_blank');
  } catch (e) {
    toast(e.message, 'error');
  } finally {
    btnText.style.display = 'inline';
    btnLoading.style.display = 'none';
    generateConfirm.disabled = false;
  }
});

if (checkAuth()) {
  parseHashAfterLogin();
  updateAuthUI();
  loadTrainings();
}
