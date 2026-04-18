const API = '';

// ─── Navigation ─────────────────────────────────────────────────────
document.querySelectorAll('.sidebar-link').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const page = link.dataset.page;
    document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
    link.classList.add('active');
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const el = document.getElementById('page-' + page);
    if (el) { el.classList.add('active'); el.classList.add('fade-in'); }
    // Close sidebar on mobile after navigation
    if (window.innerWidth < 768) {
      document.getElementById('sidebar')?.classList.remove('open');
      document.getElementById('sidebar-overlay')?.classList.remove('active');
    }
    if (page === 'dashboard') loadDashboard();
    if (page === 'jobs') loadJobs();
    if (page === 'candidates') loadCandidates();
    if (page === 'pipeline') loadPipeline();
  });
});

// ─── Helpers ────────────────────────────────────────────────────────
async function api(path, opts = {}) {
  const res = await fetch(API + path, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'API error');
  }
  return res.json();
}

function show(id) { document.getElementById(id).classList.remove('hidden'); }
function hide(id) { document.getElementById(id).classList.add('hidden'); }

function scoreColor(score) {
  if (score >= 0.6) return 'bg-emerald-500';
  if (score >= 0.4) return 'bg-yellow-500';
  return 'bg-red-400';
}

function scoreBadge(score) {
  const pct = (score * 100).toFixed(1);
  const color = score >= 0.6 ? 'emerald' : score >= 0.4 ? 'yellow' : 'red';
  return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${color}-100 text-${color}-700">${pct}%</span>`;
}

function skillTags(skills, max = 8) {
  if (!skills || !skills.length) return '<span class="text-gray-400 text-xs">No skills</span>';
  return skills.slice(0, max).map(s =>
    `<span class="inline-block bg-indigo-50 text-indigo-600 text-xs px-2 py-0.5 rounded-md mr-1 mb-1">${s}</span>`
  ).join('') + (skills.length > max ? `<span class="text-xs text-gray-400">+${skills.length - max} more</span>` : '');
}

// ─── Dashboard ──────────────────────────────────────────────────────
async function loadDashboard() {
  try {
    const [health, stats] = await Promise.all([api('/health'), api('/dashboard/stats')]);

    document.getElementById('stat-candidates').textContent = stats.candidates;
    document.getElementById('stat-jobs').textContent = stats.job_roles;
    document.getElementById('stat-status').textContent = health.status === 'healthy' ? 'Online' : 'Error';

    const sorted = Object.entries(stats.category_counts).sort((a, b) => b[1] - a[1]);
    const maxCount = sorted.length ? sorted[0][1] : 1;

    const chartEl = document.getElementById('category-chart');
    chartEl.innerHTML = sorted.map(([cat, count]) => `
      <div class="flex items-center gap-2 sm:gap-3">
        <span class="text-xs font-medium text-gray-500 w-24 sm:w-40 truncate">${cat}</span>
        <div class="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
          <div class="score-bar h-5 bg-indigo-500 rounded-full flex items-center justify-end pr-2" style="width: ${(count / maxCount * 100)}%">
            <span class="text-xs font-medium text-white">${count}</span>
          </div>
        </div>
      </div>
    `).join('');
  } catch (e) {
    console.error('Dashboard error:', e);
  }
}

// ─── Jobs ───────────────────────────────────────────────────────────
async function loadJobs() {
  const jobs = await api('/jobs');
  const el = document.getElementById('jobs-list');
  el.innerHTML = jobs.map(j => `
    <div class="card bg-white rounded-xl p-5 border border-gray-100">
      <div class="flex items-start justify-between mb-3">
        <div>
          <h3 class="font-semibold text-gray-800">${j.title}</h3>
          <p class="text-sm text-gray-500">${j.department || ''} · ${j.location || 'Remote'}</p>
        </div>
        <span class="text-xs font-medium px-2 py-1 rounded-full ${j.status === 'open' ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500'}">${j.status}</span>
      </div>
      <p class="text-sm text-gray-600 mb-3 line-clamp-2">${j.description}</p>
      <div class="flex items-center justify-between text-xs text-gray-500">
        <span>${j.min_experience_years}+ years · ${j.salary_range || 'N/A'}</span>
        <button onclick="matchFromJob(${j.id})" class="text-indigo-600 font-medium hover:text-indigo-800">Find Matches →</button>
      </div>
    </div>
  `).join('');
  populateJobSelects(jobs);
}

async function createJob() {
  const title = document.getElementById('job-title').value.trim();
  const description = document.getElementById('job-description').value.trim();
  if (!title || !description) return alert('Title and Description are required');

  const reqText = document.getElementById('job-requirements').value.trim();
  const requirements = reqText ? reqText.split(',').map(r => r.trim()).filter(Boolean) : [];

  const statusEl = document.getElementById('job-create-status');
  statusEl.textContent = 'Creating...';
  statusEl.className = 'text-sm ml-2 text-gray-500';

  try {
    const data = await api('/jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        department: document.getElementById('job-department').value.trim() || null,
        description,
        requirements,
        min_experience_years: parseFloat(document.getElementById('job-min-exp').value) || 0,
        location: document.getElementById('job-location').value.trim() || null,
        salary_range: document.getElementById('job-salary').value.trim() || null,
      }),
    });

    statusEl.textContent = data.message;
    statusEl.className = 'text-sm ml-2 text-emerald-600 font-medium';

    // Clear form and reload jobs
    document.getElementById('job-title').value = '';
    document.getElementById('job-description').value = '';
    document.getElementById('job-requirements').value = '';
    document.getElementById('job-department').value = '';
    document.getElementById('job-location').value = '';
    document.getElementById('job-salary').value = '';
    document.getElementById('job-min-exp').value = '0';

    setTimeout(() => {
      document.getElementById('job-form-panel').classList.add('hidden');
      statusEl.textContent = '';
    }, 1500);

    await loadJobs();
  } catch (e) {
    statusEl.textContent = e.message;
    statusEl.className = 'text-sm ml-2 text-red-600';
  }
}

function populateJobSelects(jobs) {
  const selects = ['match-job-select', 'interview-job-select', 'bias-job-select', 'explain-job-select', 'pipeline-job-select'];
  selects.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = jobs.map(j => `<option value="${j.id}">${j.title} (${j.department})</option>`).join('');
  });
}

function matchFromJob(jobId) {
  document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
  document.querySelector('[data-page="matching"]').classList.add('active');
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-matching').classList.add('active');
  document.getElementById('match-job-select').value = jobId;
  runMatching();
}

// ─── Candidates ─────────────────────────────────────────────────────
async function loadCandidates() {
  const cat = document.getElementById('filter-category').value;
  const url = cat ? `/candidates?category=${cat}&limit=50` : '/candidates?limit=50';
  const candidates = await api(url);

  // Populate category filter
  const filterEl = document.getElementById('filter-category');
  if (filterEl.options.length <= 1) {
    const all = await api('/candidates?limit=200');
    const cats = [...new Set(all.map(c => c.category))].sort();
    cats.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c; opt.textContent = c;
      filterEl.appendChild(opt);
    });
  }

  const el = document.getElementById('candidates-list');
  el.innerHTML = candidates.map(c => `
    <div class="card bg-white rounded-xl p-4 border border-gray-100">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-9 h-9 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 text-sm font-bold">
              ${(c.name || '?')[0].toUpperCase()}
            </div>
            <div>
              <h4 class="font-medium text-gray-800">${c.name || 'Unknown'}</h4>
              <p class="text-xs text-gray-500">${c.category} · ${c.total_years_experience || '?'} years exp · ID: ${c.id}</p>
            </div>
          </div>
          <div class="ml-12">${skillTags(c.skills, 6)}</div>
        </div>
        <div class="flex gap-2 ml-4">
          <button onclick="document.getElementById('interview-candidate').value=${c.id}; navigateTo('interview')" class="text-xs bg-gray-100 text-gray-600 px-3 py-1.5 rounded-lg hover:bg-gray-200" title="Interview">
            <i data-lucide="message-square-text" class="w-3.5 h-3.5 inline"></i>
          </button>
          <button onclick="document.getElementById('explain-candidate').value=${c.id}; navigateTo('bias')" class="text-xs bg-gray-100 text-gray-600 px-3 py-1.5 rounded-lg hover:bg-gray-200" title="Explain">
            <i data-lucide="scan-search" class="w-3.5 h-3.5 inline"></i>
          </button>
        </div>
      </div>
    </div>
  `).join('');
  lucide.createIcons();
}

function navigateTo(page) {
  document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
  document.querySelector(`[data-page="${page}"]`).classList.add('active');
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + page).classList.add('active');
  // Close sidebar on mobile
  if (window.innerWidth < 768) {
    document.getElementById('sidebar')?.classList.remove('open');
    document.getElementById('sidebar-overlay')?.classList.remove('active');
  }
}

// ─── Matching ───────────────────────────────────────────────────────
async function runMatching() {
  const jobId = document.getElementById('match-job-select').value;
  const topK = document.getElementById('match-topk').value || 10;
  show('match-loading');
  document.getElementById('match-results').innerHTML = '';

  try {
    const data = await api(`/match/${jobId}?top_k=${topK}`);
    hide('match-loading');

    let html = `<div class="mb-4"><h3 class="text-lg font-semibold">Top matches for <span class="text-indigo-600">${data.job_title}</span></h3></div>`;
    html += '<div class="space-y-3">';
    data.matches.forEach((m, i) => {
      const pct = (m.match_score * 100).toFixed(1);
      html += `
        <div class="card bg-white rounded-xl p-4 border border-gray-100">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-3">
              <span class="w-7 h-7 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 text-xs font-bold">#${i + 1}</span>
              <div>
                <h4 class="font-medium text-gray-800">${m.candidate_name || 'Unknown'}</h4>
                <p class="text-xs text-gray-500">${m.category} · ${m.total_years_experience || '?'} years · ID: ${m.candidate_id}</p>
              </div>
            </div>
            <div class="text-right">
              ${scoreBadge(m.match_score)}
            </div>
          </div>
          <div class="w-full bg-gray-100 rounded-full h-2 mb-3">
            <div class="score-bar ${scoreColor(m.match_score)} h-2 rounded-full" style="width: ${pct}%"></div>
          </div>
          <div>${skillTags(m.skills, 10)}</div>
          <div class="mt-3 flex flex-wrap gap-2">
            <button onclick="addToPipeline(${m.candidate_id}, ${jobId}, ${m.match_score})" class="text-xs text-emerald-600 border border-emerald-200 px-3 py-1 rounded-lg hover:bg-emerald-50 flex items-center gap-1">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
              Add to Pipeline
            </button>
            <button onclick="document.getElementById('interview-candidate').value=${m.candidate_id}; document.getElementById('interview-job-select').value=${jobId}; navigateTo('interview'); generateInterview()" class="text-xs text-indigo-600 border border-indigo-200 px-3 py-1 rounded-lg hover:bg-indigo-50">Generate Interview</button>
            <button onclick="document.getElementById('explain-candidate').value=${m.candidate_id}; document.getElementById('explain-job-select').value=${jobId}; navigateTo('bias'); runExplain()" class="text-xs text-indigo-600 border border-indigo-200 px-3 py-1 rounded-lg hover:bg-indigo-50">Explain Score</button>
          </div>
        </div>`;
    });
    html += '</div>';
    document.getElementById('match-results').innerHTML = html;
  } catch (e) {
    hide('match-loading');
    document.getElementById('match-results').innerHTML = `<div class="bg-red-50 text-red-600 p-4 rounded-xl text-sm">${e.message}</div>`;
  }
}

// ─── Conversational Query (ReAct Agent) ────────────────────────────
function setQuery(q) { document.getElementById('query-input').value = q; }

function appendUserBubble(question) {
  const chat = document.getElementById('query-chat');
  chat.innerHTML += `
    <div class="flex justify-end">
      <div class="bg-indigo-600 text-white rounded-2xl rounded-br-md px-4 py-2.5 max-w-lg text-sm">${question}</div>
    </div>`;
}

function appendAgentBubble(data) {
  const chat = document.getElementById('query-chat');

  // Natural language answer
  let html = `<div class="flex justify-start"><div class="max-w-2xl w-full space-y-3">`;

  // Answer bubble
  html += `<div class="bg-white border border-gray-100 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
    <p class="text-sm text-gray-800 leading-relaxed">${data.answer || data.explanation || 'No answer generated.'}</p>
  </div>`;

  // Thought (collapsible)
  if (data.thought) {
    html += `<details class="group">
      <summary class="text-xs text-gray-400 cursor-pointer hover:text-gray-600 flex items-center gap-1">
        <i data-lucide="brain" class="w-3 h-3"></i> Agent reasoning
      </summary>
      <div class="mt-1 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 text-xs text-amber-700">${data.thought}</div>
    </details>`;
  }

  // SQL (collapsible)
  if (data.sql) {
    html += `<details class="group">
      <summary class="text-xs text-gray-400 cursor-pointer hover:text-gray-600 flex items-center gap-1">
        <i data-lucide="terminal" class="w-3 h-3"></i> SQL query · ${data.row_count} result${data.row_count !== 1 ? 's' : ''}
      </summary>
      <div class="mt-1">
        <pre class="text-xs font-mono text-indigo-700 bg-indigo-50 p-3 rounded-lg border border-indigo-100 overflow-x-auto">${data.sql}</pre>`;

    // Results table
    if (data.results && data.results.length > 0) {
      html += `<div class="mt-2 overflow-x-auto max-h-64 overflow-y-auto"><table class="w-full text-xs">`;
      html += '<thead><tr class="border-b border-gray-200 bg-gray-50">';
      data.columns.forEach(col => { html += `<th class="text-left py-1.5 px-2 font-medium text-gray-600">${col}</th>`; });
      html += '</tr></thead><tbody>';
      data.results.slice(0, 30).forEach(row => {
        html += '<tr class="border-b border-gray-50 hover:bg-gray-50">';
        data.columns.forEach(col => {
          let val = row[col];
          if (val === null) val = '<span class="text-gray-300">-</span>';
          else if (typeof val === 'number') val = Number.isInteger(val) ? val : val.toFixed(2);
          html += `<td class="py-1.5 px-2">${val}</td>`;
        });
        html += '</tr>';
      });
      if (data.results.length > 30) html += `<tr><td colspan="${data.columns.length}" class="py-2 px-2 text-gray-400 text-center">... and ${data.results.length - 30} more rows</td></tr>`;
      html += '</tbody></table></div>';
    }
    html += `</div></details>`;
  }

  // Error
  if (data.error) {
    html += `<div class="bg-red-50 text-red-600 rounded-lg px-3 py-2 text-xs">${data.error}</div>`;
  }

  // Turn counter
  html += `<p class="text-xs text-gray-300">Turn ${data.conversation_turns || 1}</p>`;

  html += `</div></div>`;
  chat.innerHTML += html;
  lucide.createIcons();
}

async function runQuery() {
  const question = document.getElementById('query-input').value.trim();
  if (!question) return;

  appendUserBubble(question);
  document.getElementById('query-input').value = '';
  show('query-loading');

  try {
    const data = await api('/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    hide('query-loading');
    appendAgentBubble(data);
  } catch (e) {
    hide('query-loading');
    appendAgentBubble({ answer: e.message, error: e.message, conversation_turns: 0 });
  }

  // Scroll to bottom
  const chat = document.getElementById('query-chat');
  chat.scrollTop = chat.scrollHeight;
}

async function clearConversation() {
  try { await api('/query/clear', { method: 'POST' }); } catch(e) {}
  document.getElementById('query-chat').innerHTML = '';
}

document.getElementById('query-input').addEventListener('keydown', e => { if (e.key === 'Enter') runQuery(); });

// ─── Interview ──────────────────────────────────────────────────────
async function generateInterview() {
  const candidateId = document.getElementById('interview-candidate').value;
  const jobId = document.getElementById('interview-job-select').value;
  if (!candidateId || !jobId) return alert('Please enter a candidate ID and select a job role');

  show('interview-loading');
  document.getElementById('interview-results').innerHTML = '';

  try {
    const data = await api(`/interview/${candidateId}?job_id=${jobId}`);
    hide('interview-loading');

    const catColors = { technical: 'indigo', behavioral: 'emerald', situational: 'amber' };

    let html = `
      <div class="card bg-white rounded-xl p-6 border border-gray-100">
        <div class="mb-4">
          <h3 class="text-lg font-semibold">${data.candidate_name || 'Candidate #' + data.candidate_id}</h3>
          <p class="text-sm text-gray-500">Interview questions for <span class="font-medium text-indigo-600">${data.job_title}</span></p>
        </div>
        <div class="space-y-4">`;

    data.questions.forEach((q, i) => {
      const color = catColors[q.category] || 'gray';
      html += `
        <div class="border border-gray-100 rounded-lg p-4">
          <div class="flex items-start gap-3">
            <span class="w-6 h-6 bg-${color}-100 text-${color}-600 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">${i + 1}</span>
            <div>
              <p class="font-medium text-gray-800">${q.question}</p>
              <div class="flex items-center gap-2 mt-2">
                <span class="text-xs px-2 py-0.5 rounded-full bg-${color}-50 text-${color}-600 font-medium">${q.category}</span>
                <span class="text-xs text-gray-400">${q.rationale}</span>
              </div>
            </div>
          </div>
        </div>`;
    });

    html += '</div></div>';
    document.getElementById('interview-results').innerHTML = html;
  } catch (e) {
    hide('interview-loading');
    document.getElementById('interview-results').innerHTML = `<div class="bg-red-50 text-red-600 p-4 rounded-xl text-sm">${e.message}</div>`;
  }
}

// ─── Bias ───────────────────────────────────────────────────────────
async function runAudit() {
  const jobId = document.getElementById('bias-job-select').value;
  const threshold = document.getElementById('bias-threshold').value;
  show('bias-loading');
  document.getElementById('bias-results').innerHTML = '';

  try {
    const data = await api(`/bias/audit/${jobId}?threshold=${threshold}`);
    hide('bias-loading');

    const statusColor = data.is_fair ? 'emerald' : 'red';
    const statusIcon = data.is_fair ? 'check-circle-2' : 'alert-triangle';

    let html = `
      <div class="card bg-white rounded-xl p-6 border border-gray-100 mb-4">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 bg-${statusColor}-100 rounded-full flex items-center justify-center">
            <i data-lucide="${statusIcon}" class="w-5 h-5 text-${statusColor}-600"></i>
          </div>
          <div>
            <h3 class="font-semibold text-gray-800">Fairness Audit: ${data.job_title || 'Job #' + jobId}</h3>
            <p class="text-sm ${data.is_fair ? 'text-emerald-600' : 'text-red-600'}">${data.is_fair ? 'Passed' : 'Failed'} — ${data.recommendation}</p>
          </div>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div class="bg-gray-50 rounded-lg p-3">
            <p class="text-xs text-gray-500">Overall Selection Rate</p>
            <p class="text-lg font-bold">${(data.overall_selection_rate * 100).toFixed(1)}%</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3">
            <p class="text-xs text-gray-500">Parity Difference</p>
            <p class="text-lg font-bold">${(data.demographic_parity_difference * 100).toFixed(1)}%</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3">
            <p class="text-xs text-gray-500">Parity Ratio</p>
            <p class="text-lg font-bold">${data.demographic_parity_ratio?.toFixed(3) || 'N/A'}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3">
            <p class="text-xs text-gray-500">4/5ths Rule</p>
            <p class="text-lg font-bold ${data.four_fifths_rule_passed ? 'text-emerald-600' : 'text-red-600'}">${data.four_fifths_rule_passed ? 'Passed' : 'Failed'}</p>
          </div>
        </div>`;

    if (data.group_selection_rates) {
      html += '<h4 class="font-medium text-sm text-gray-700 mb-2">Selection Rates by Group</h4>';
      html += '<div class="space-y-2">';
      Object.entries(data.group_selection_rates).forEach(([group, rate]) => {
        const pct = (rate * 100).toFixed(1);
        const flagged = data.flagged_groups?.some(g => g.group === group);
        html += `
          <div class="flex items-center gap-3">
            <span class="text-xs w-36 truncate ${flagged ? 'text-red-600 font-medium' : 'text-gray-500'}">${group} ${flagged ? '⚠' : ''}</span>
            <div class="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
              <div class="h-4 ${flagged ? 'bg-red-400' : 'bg-indigo-500'} rounded-full" style="width: ${pct}%"></div>
            </div>
            <span class="text-xs font-medium w-12 text-right">${pct}%</span>
          </div>`;
      });
      html += '</div>';
    }
    html += '</div>';
    document.getElementById('bias-results').innerHTML = html;
    lucide.createIcons();
  } catch (e) {
    hide('bias-loading');
    document.getElementById('bias-results').innerHTML = `<div class="bg-red-50 text-red-600 p-4 rounded-xl text-sm">${e.message}</div>`;
  }
}

async function runExplain() {
  const candidateId = document.getElementById('explain-candidate').value;
  const jobId = document.getElementById('explain-job-select').value;
  if (!candidateId || !jobId) return alert('Please enter candidate ID and select a job');

  show('bias-loading');
  document.getElementById('bias-results').innerHTML = '';

  try {
    const data = await api(`/bias/explain/${candidateId}?job_id=${jobId}`);
    hide('bias-loading');

    let html = `
      <div class="card bg-white rounded-xl p-6 border border-gray-100">
        <h3 class="font-semibold text-gray-800 mb-1">${data.candidate_name || 'Candidate #' + data.candidate_id}</h3>
        <p class="text-sm text-gray-500 mb-4">Score explanation for <span class="text-indigo-600 font-medium">${data.job_title}</span></p>
        <div class="flex items-center gap-4 mb-6">
          <div class="bg-indigo-50 rounded-xl p-4 text-center">
            <p class="text-xs text-gray-500">Match Score</p>
            <p class="text-2xl font-bold text-indigo-600">${(data.match_score * 100).toFixed(1)}%</p>
          </div>
          <div class="bg-gray-50 rounded-xl p-4 text-center">
            <p class="text-xs text-gray-500">Explained Score</p>
            <p class="text-2xl font-bold text-gray-700">${(data.explained_score * 100).toFixed(1)}%</p>
          </div>
        </div>
        <h4 class="font-medium text-sm text-gray-700 mb-3">Feature Importance</h4>
        <div class="space-y-3">`;

    data.explanations.forEach(exp => {
      const pct = (exp.importance * 100).toFixed(1);
      const dirColor = exp.direction === 'positive' ? 'emerald' : exp.direction === 'negative' ? 'red' : 'gray';
      html += `
        <div>
          <div class="flex items-center justify-between mb-1">
            <span class="text-sm font-medium text-gray-700">${exp.feature.replace(/_/g, ' ')}</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-${dirColor}-50 text-${dirColor}-600">${exp.direction} (${pct}%)</span>
          </div>
          <div class="w-full bg-gray-100 rounded-full h-2.5">
            <div class="h-2.5 bg-${dirColor}-500 rounded-full" style="width: ${Math.min(pct * 2.5, 100)}%"></div>
          </div>
          <p class="text-xs text-gray-400 mt-1">${exp.detail}</p>
        </div>`;
    });

    html += '</div>';
    if (data.top_positive_factors.length) {
      html += '<div class="mt-4 p-3 bg-emerald-50 rounded-lg"><p class="text-xs font-medium text-emerald-700 mb-1">Positive Factors</p>';
      data.top_positive_factors.forEach(f => { html += `<p class="text-xs text-emerald-600">✓ ${f}</p>`; });
      html += '</div>';
    }
    if (data.top_negative_factors.length) {
      html += '<div class="mt-2 p-3 bg-red-50 rounded-lg"><p class="text-xs font-medium text-red-700 mb-1">Areas of Concern</p>';
      data.top_negative_factors.forEach(f => { html += `<p class="text-xs text-red-600">✗ ${f}</p>`; });
      html += '</div>';
    }
    html += '</div>';
    document.getElementById('bias-results').innerHTML = html;
  } catch (e) {
    hide('bias-loading');
    document.getElementById('bias-results').innerHTML = `<div class="bg-red-50 text-red-600 p-4 rounded-xl text-sm">${e.message}</div>`;
  }
}

// ─── Upload ─────────────────────────────────────────────────────────
const fileInput = document.getElementById('file-input');
const dropZone = document.getElementById('drop-zone');

fileInput.addEventListener('change', () => {
  if (fileInput.files.length) {
    document.getElementById('file-name').textContent = fileInput.files[0].name;
  }
});

dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('border-indigo-400', 'bg-indigo-50'); });
dropZone.addEventListener('dragleave', () => { dropZone.classList.remove('border-indigo-400', 'bg-indigo-50'); });
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('border-indigo-400', 'bg-indigo-50');
  if (e.dataTransfer.files.length) {
    fileInput.files = e.dataTransfer.files;
    document.getElementById('file-name').textContent = e.dataTransfer.files[0].name;
  }
});

async function uploadResume() {
  const file = fileInput.files[0];
  if (!file) return alert('Please select a PDF file');

  const category = document.getElementById('upload-category').value;
  const formData = new FormData();
  formData.append('file', file);

  show('upload-loading');
  document.getElementById('upload-results').innerHTML = '';

  try {
    const data = await api(`/upload?category=${category}`, { method: 'POST', body: formData });
    hide('upload-loading');

    document.getElementById('upload-results').innerHTML = `
      <div class="card bg-white rounded-xl p-6 border border-emerald-200 bg-emerald-50">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center">
            <i data-lucide="check-circle-2" class="w-5 h-5 text-emerald-600"></i>
          </div>
          <div>
            <h3 class="font-semibold text-emerald-800">${data.message}</h3>
            <p class="text-sm text-emerald-600">Candidate ID: ${data.candidate_id}</p>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div><span class="text-gray-500">Name:</span> <span class="font-medium">${data.name || 'Unknown'}</span></div>
          <div><span class="text-gray-500">Category:</span> <span class="font-medium">${data.category}</span></div>
          <div><span class="text-gray-500">Experience:</span> <span class="font-medium">${data.total_years_experience || '?'} years</span></div>
          <div><span class="text-gray-500">Skills:</span> <span class="font-medium">${data.skills?.length || 0} found</span></div>
        </div>
        <div class="mt-3">${skillTags(data.skills, 12)}</div>
      </div>`;
    lucide.createIcons();
  } catch (e) {
    hide('upload-loading');
    document.getElementById('upload-results').innerHTML = `<div class="bg-red-50 text-red-600 p-4 rounded-xl text-sm">${e.message}</div>`;
  }
}

// ─── LLM Provider Selector ──────────────────────────────────────────
let currentProvider = 'ollama';

async function loadLLMStatus() {
  try {
    const data = await api('/llm/status');
    currentProvider = data.provider;
    updateProviderUI(data.provider, data.model, data.available);
  } catch (e) {
    console.error('Failed to load LLM status:', e);
  }
}

function updateProviderUI(provider, model, available) {
  const dot = document.getElementById('llm-status-dot');
  const modelLabel = document.getElementById('llm-model-label');

  // Update button states
  document.querySelectorAll('.provider-btn').forEach(btn => {
    if (btn.dataset.provider === provider) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  dot.className = `w-2 h-2 rounded-full ${available ? 'bg-emerald-400' : 'bg-red-400'}`;
  modelLabel.textContent = `${model} ${available ? '' : '(offline)'}`;
}

async function switchProvider(provider) {
  if (provider === currentProvider) return;
  try {
    const data = await api(`/llm/switch?provider=${provider}`, { method: 'POST' });
    currentProvider = data.provider;
    await loadLLMStatus();
  } catch (e) {
    alert(`Failed to switch: ${e.message}`);
  }
}

// ─── Pipeline (Kanban Board) ────────────────────────────────────────
const STAGE_META = {
  applied:   { label: 'Applied',   color: 'bg-indigo-100 text-indigo-700' },
  screened:  { label: 'Screened',  color: 'bg-sky-100 text-sky-700' },
  interview: { label: 'Interview', color: 'bg-amber-100 text-amber-700' },
  offer:     { label: 'Offer',     color: 'bg-violet-100 text-violet-700' },
  hired:     { label: 'Hired',     color: 'bg-emerald-100 text-emerald-700' },
  rejected:  { label: 'Rejected',  color: 'bg-red-100 text-red-700' },
};

async function loadPipeline() {
  const sel = document.getElementById('pipeline-job-select');
  if (!sel || !sel.value) return;
  const jobId = sel.value;

  show('pipeline-loading');
  document.getElementById('pipeline-board').innerHTML = '';

  try {
    const data = await api(`/pipeline/${jobId}`);
    hide('pipeline-loading');
    document.getElementById('pipeline-total').textContent = data.total;
    renderPipelineBoard(data);
  } catch (e) {
    hide('pipeline-loading');
    document.getElementById('pipeline-board').innerHTML =
      `<div class="bg-red-50 text-red-600 p-4 rounded-xl text-sm w-full">${e.message}</div>`;
  }
}

function renderPipelineBoard(data) {
  const board = document.getElementById('pipeline-board');
  board.innerHTML = data.columns.map(col => `
    <div class="kanban-col">
      <div class="kanban-col-header">
        <span class="kanban-col-title">
          <span class="stage-dot dot-${col.stage}"></span>
          ${col.label}
        </span>
        <span class="kanban-count">${col.count}</span>
      </div>
      <div class="kanban-col-body" data-stage="${col.stage}"
           ondragover="kanbanDragOver(event)"
           ondragleave="kanbanDragLeave(event)"
           ondrop="kanbanDrop(event)">
        ${col.cards.length === 0
          ? '<div class="kanban-empty">Drop here</div>'
          : col.cards.map(c => renderKanbanCard(c)).join('')}
      </div>
    </div>
  `).join('');
  lucide.createIcons();
}

function renderKanbanCard(c) {
  const score = c.match_score != null
    ? `<span class="card-score ${scoreColor(c.match_score)} text-white">${(c.match_score * 100).toFixed(0)}%</span>`
    : '';
  const skills = (c.skills || []).slice(0, 4)
    .map(s => `<span class="card-skill">${escapeHtml(s)}</span>`).join('');
  const initials = (c.candidate_name || '?').split(' ').map(s => s[0]).filter(Boolean).slice(0, 2).join('').toUpperCase();
  return `
    <div class="kanban-card stage-${c.stage}"
         draggable="true"
         data-application-id="${c.application_id}"
         data-stage="${c.stage}"
         ondragstart="kanbanDragStart(event)"
         ondragend="kanbanDragEnd(event)">
      <div class="flex items-start justify-between gap-2">
        <div class="flex-1 min-w-0">
          <div class="card-name truncate">${escapeHtml(c.candidate_name || 'Unknown')}</div>
          <div class="card-meta">${escapeHtml(c.category || '—')} · ${c.total_years_experience ?? '?'} yrs · #${c.candidate_id}</div>
        </div>
        <span class="text-[10px] font-bold text-gray-400 bg-gray-100 rounded w-7 h-7 flex items-center justify-center flex-shrink-0">${initials}</span>
      </div>
      <div class="card-skills">${skills}</div>
      <div class="card-footer">
        ${score || '<span class="text-[10px] text-gray-400">No score</span>'}
        <span class="card-delete" onclick="removeFromPipeline(${c.application_id}, event)" title="Remove from pipeline">✕</span>
      </div>
    </div>`;
}

function escapeHtml(s) {
  if (s == null) return '';
  return String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

// ─── Drag & drop handlers ──────────────────────────────────────────
let _draggedAppId = null;
let _draggedFromStage = null;

function kanbanDragStart(e) {
  const card = e.currentTarget;
  _draggedAppId = card.dataset.applicationId;
  _draggedFromStage = card.dataset.stage;
  card.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'move';
  try { e.dataTransfer.setData('text/plain', _draggedAppId); } catch (_) {}
}

function kanbanDragEnd(e) {
  e.currentTarget.classList.remove('dragging');
  document.querySelectorAll('.kanban-col-body.drag-over').forEach(el => el.classList.remove('drag-over'));
}

function kanbanDragOver(e) {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
  e.currentTarget.classList.add('drag-over');
}

function kanbanDragLeave(e) {
  // Only remove if leaving the column body entirely
  if (e.currentTarget.contains(e.relatedTarget)) return;
  e.currentTarget.classList.remove('drag-over');
}

async function kanbanDrop(e) {
  e.preventDefault();
  const col = e.currentTarget;
  col.classList.remove('drag-over');
  const newStage = col.dataset.stage;
  const appId = _draggedAppId;
  if (!appId || !newStage) return;
  if (newStage === _draggedFromStage) return;

  try {
    await api(`/applications/${appId}/stage`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stage: newStage }),
    });
    await loadPipeline();
  } catch (err) {
    alert('Failed to move: ' + err.message);
    await loadPipeline();
  } finally {
    _draggedAppId = null;
    _draggedFromStage = null;
  }
}

async function removeFromPipeline(appId, e) {
  if (e) { e.stopPropagation(); }
  if (!confirm('Remove this candidate from the pipeline?')) return;
  try {
    await api(`/applications/${appId}`, { method: 'DELETE' });
    await loadPipeline();
  } catch (err) {
    alert('Failed: ' + err.message);
  }
}

async function addToPipeline(candidateId, jobId, matchScore) {
  try {
    const res = await api('/applications', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        candidate_id: candidateId,
        job_role_id: parseInt(jobId),
        stage: 'applied',
        match_score: matchScore,
      }),
    });
    const msg = res.duplicate ? 'Already in pipeline' : 'Added to pipeline ✓';
    showToast(msg, res.duplicate ? 'warn' : 'success');
  } catch (err) {
    showToast('Failed: ' + err.message, 'error');
  }
}

async function seedPipelineFromMatches() {
  const sel = document.getElementById('pipeline-job-select');
  if (!sel || !sel.value) return;
  const jobId = parseInt(sel.value);
  const btn = document.getElementById('pipeline-seed-btn');
  const orig = btn ? btn.innerHTML : '';
  if (btn) {
    btn.disabled = true;
    btn.style.opacity = '0.6';
    btn.innerHTML = '<span class="loader" style="width:12px;height:12px;border-width:2px;vertical-align:middle;margin-right:6px"></span> Adding top 10...';
  }
  // Also show the main pipeline loader
  show('pipeline-loading');

  try {
    // 1) Fetch top 10 matches
    const data = await api(`/match/${jobId}?top_k=10`);
    if (!data.matches?.length) {
      showToast('No matches found for this job', 'warn');
      return;
    }

    // 2) One bulk POST — avoids rate-limit thrash
    const bulkPayload = data.matches.map(m => ({
      candidate_id: m.candidate_id,
      job_role_id: jobId,
      stage: 'applied',
      match_score: m.match_score,
    }));
    const res = await api('/applications/bulk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bulkPayload),
    });

    const msg = `Added ${res.added} new · ${res.duplicates} already in pipeline` +
                (res.errors?.length ? ` · ${res.errors.length} failed` : '');
    showToast(msg, res.added > 0 ? 'success' : 'warn');

    // 3) Refresh board
    await loadPipeline();
  } catch (err) {
    hide('pipeline-loading');
    showToast('Failed: ' + err.message, 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.style.opacity = '';
      btn.innerHTML = orig;
      lucide.createIcons();
    }
  }
}

function showToast(msg, type = 'info') {
  const colors = {
    success: 'bg-emerald-600',
    warn:    'bg-amber-600',
    error:   'bg-red-600',
    info:    'bg-gray-800',
  };
  const toast = document.createElement('div');
  toast.className = `fixed bottom-6 right-6 ${colors[type] || colors.info} text-white px-4 py-2 rounded-lg shadow-lg text-sm z-50`;
  toast.style.animation = 'fadeIn 0.2s ease';
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; }, 2500);
  setTimeout(() => toast.remove(), 3000);
}

// ─── Init ───────────────────────────────────────────────────────────
loadDashboard();
loadJobs();
loadLLMStatus();
