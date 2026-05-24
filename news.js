let allNews = [];
let newsFilter = 'all';

const NEWSCAT = {
  equity: '#00e676', forex: '#40c4ff', crypto: '#f5a623',
  commodity: '#ff6d00', bonds: '#aa80ff', mutual_funds: '#ff4081', economy: '#69f0ae'
};

function loadNews() {
  apiGet('/api/news')
    .then(d => {
      allNews = d.news || d.articles || [];
      renderNews();
    })
    .catch(() => {
      document.getElementById('panel-news').innerHTML =
        '<div class="panel-placeholder" style="color:var(--red);">⚠ News feed unavailable</div>';
    });
}

function renderNews() {
  const filtered = newsFilter === 'all' ? allNews : allNews.filter(a => a.category === newsFilter);

  const cats = ['all', ...new Set(allNews.map(a => a.category))];

  let html = '<div class="news-filter-bar">';
  cats.forEach(c => {
    html += `<span class="news-filter-tab${c === newsFilter ? ' active' : ''}" data-cat="${c}"
      onclick="newsFilter='${c}';renderNews();">${c.toUpperCase().replace(/_/g, ' ')}</span>`;
  });
  html += '</div>';

  html += '<div class="news-grid">';

  filtered.forEach(a => {
    const catColor = NEWSCAT[a.category] || '#888';
    const sColor = a.sentiment === 'bullish' ? '#00e676' : a.sentiment === 'bearish' ? '#ff1744' : '#f5a623';
    const ts = a.timestamp || '--';
    const sr = a.source || '--';

    html += `<div class="news-card glass-panel" onclick="toggleNewsDetail(this)">
      <div class="news-card-header">
        <span class="news-cat-badge" style="border-color:${catColor};color:${catColor};">${a.category?.toUpperCase()}</span>
        <span class="news-time">${ts}</span>
      </div>
      <div class="news-title">${a.title || '--'}</div>
      <div class="news-card-footer">
        <span class="news-source">${sr}</span>
        <span class="news-sentiment" style="color:${sColor};">● ${a.sentiment?.toUpperCase()}</span>
        <span class="news-country-tag">${a.country || '--'}</span>
      </div>
      <div class="news-detail" style="display:none;">
        <div class="news-divider"></div>
        <div class="news-summary">${a.narrative || a.summary || 'No narrative available.'}</div>
        ${a.mf_take ? `<div class="news-mf-take">
          <span class="mf-take-label">🏦 Mutual Fund Take</span>
          <p>${a.mf_take}</p>
        </div>` : ''}
      </div>
    </div>`;
  });

  html += '</div>';

  // Update map with filtered news
  updateWorldMap(filtered);

  document.getElementById('panel-news').innerHTML = html;
}

function toggleNewsDetail(el) {
  const d = el.querySelector('.news-detail');
  if (d) {
    const isOpen = d.style.display === 'block';
    d.style.display = isOpen ? 'none' : 'block';
    el.style.borderColor = isOpen ? 'var(--glass-border)' : 'var(--amber)';
  }
}

// Auto-refresh every 2 minutes
setInterval(() => {
  if (!document.hidden) loadNews();
}, 120000);
