/* Daily AI Insights — 前端載入邏輯 */
(() => {
  const dateSelect = document.getElementById('dateSelect');
  const themeToggle = document.getElementById('themeToggle');
  const content = document.getElementById('content');
  const dashboard = document.getElementById('dashboard');
  const dashboardGrid = document.getElementById('dashboardGrid');
  const meta = document.getElementById('meta');
  const empty = document.getElementById('empty');

  /* ---------- Theme ---------- */
  const applyTheme = (mode) => {
    document.documentElement.classList.toggle('dark', mode === 'dark');
    localStorage.setItem('theme', mode);
  };
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) applyTheme(savedTheme);
  else if (window.matchMedia('(prefers-color-scheme: dark)').matches) applyTheme('dark');

  themeToggle.addEventListener('click', () => {
    const isDark = document.documentElement.classList.contains('dark');
    applyTheme(isDark ? 'light' : 'dark');
  });

  /* ---------- Render ---------- */
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[c]);

  const renderDashboard = (data) => {
    if (!data || Object.keys(data).length === 0) {
      dashboard.classList.add('hidden');
      return;
    }
    dashboard.classList.remove('hidden');
    dashboardGrid.innerHTML = Object.entries(data).map(([k, v]) => {
      const color = v.includes('+') ? 'text-finance dark:text-dark-finance'
        : v.includes('-') ? 'text-accent dark:text-dark-accent'
        : 'text-gray-500';
      return `<div><span class="font-semibold">${esc(k)}</span> <span class="${color}">${esc(v)}</span></div>`;
    }).join('');
  };

  const renderItem = (item) => {
    const tags = (item.tags || []).map(t =>
      `<span class="inline-block bg-gray-200 dark:bg-gray-700 text-xs px-2 py-0.5 rounded mr-1">#${esc(t)}</span>`
    ).join('');
    const priorityBadge = item.priority === 'high'
      ? '<span class="bg-accent dark:bg-dark-accent text-white text-xs px-2 py-0.5 rounded mr-2">重點</span>'
      : '';
    const borderColor = item.priority === 'high'
      ? 'border-accent dark:border-dark-accent'
      : 'border-primary dark:border-gray-600';

    return `
      <details class="bg-white dark:bg-dark-card rounded-lg p-4 shadow-sm border-l-4 ${borderColor}">
        <summary class="flex items-start gap-2 font-semibold">
          <span class="chev">▸</span>
          <span class="flex-1">${priorityBadge}${esc(item.title)}</span>
        </summary>
        <div class="mt-3 text-sm leading-relaxed space-y-2">
          <p>${esc(item.core_summary)}</p>
          <p class="bg-policy/10 dark:bg-dark-policy/10 border-l-2 border-policy dark:border-dark-policy px-3 py-2 italic">
            💡 ${esc(item.expert_insight)}
          </p>
          <div>${tags}</div>
          <a href="${esc(item.source_url)}" target="_blank" rel="noopener"
             class="inline-block text-xs underline text-primary dark:text-dark-text">→ 原文連結</a>
        </div>
      </details>
    `;
  };

  const renderSection = (section) => {
    const body = section.items && section.items.length
      ? section.items.map(renderItem).join('')
      : `<p class="bg-white dark:bg-dark-card rounded-lg p-4 text-gray-500 dark:text-gray-400 text-sm">${esc(section.fallback_note || '本日無資料')}</p>`;
    return `
      <section>
        <h2 class="text-lg font-bold border-b-2 border-primary dark:border-gray-500 pb-1 mb-3">${esc(section.category_display)}</h2>
        <div class="space-y-3">${body}</div>
      </section>
    `;
  };

  const renderReport = (report) => {
    empty.classList.add('hidden');
    renderDashboard(report.dashboard);
    meta.textContent = `生成時間: ${report.generated_at} · 模型: ${report.model_version}${
      report.anomalies?.skipped_sources?.length ? ` · 異常: ${report.anomalies.skipped_sources.join(', ')}` : ''
    }`;
    content.innerHTML = (report.sections || []).map(renderSection).join('');
  };

  /* ---------- Data loading ---------- */
  const fetchJSON = async (url) => {
    const r = await fetch(url, { cache: 'no-cache' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  };

  const loadDate = async (date) => {
    try {
      const report = await fetchJSON(`./data/${date}.json`);
      renderReport(report);
      history.replaceState(null, '', `?date=${date}`);
    } catch (e) {
      content.innerHTML = '';
      empty.classList.remove('hidden');
      empty.querySelector('p').textContent = `載入 ${date} 失敗: ${e.message}`;
    }
  };

  const init = async () => {
    try {
      const index = await fetchJSON('./data/index.json');
      const dates = index.dates || [];
      if (!dates.length) {
        empty.classList.remove('hidden');
        return;
      }
      dateSelect.innerHTML = dates.map(d => `<option value="${d}">${d}</option>`).join('');
      const params = new URLSearchParams(location.search);
      const initialDate = params.get('date') && dates.includes(params.get('date'))
        ? params.get('date')
        : (index.latest || dates[0]);
      dateSelect.value = initialDate;
      await loadDate(initialDate);
    } catch (e) {
      empty.classList.remove('hidden');
      empty.querySelector('p').textContent = `初始化失敗: ${e.message}`;
    }
  };

  dateSelect.addEventListener('change', (e) => loadDate(e.target.value));
  init();
})();
