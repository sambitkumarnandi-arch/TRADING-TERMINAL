const API_BASE = '';
let appState = { busy: false, autoRun: true };
let tvWidget = null;
let worldMap = null;
let mapMarkers = [];
let scannerData = [];

function fmt(v) {
  if (v === null || v === undefined) return '--';
  const n = parseFloat(v);
  if (isNaN(n)) return String(v);
  if (n === 0) return '0.00';
  if (Math.abs(n) < 1) {
    let s = n.toFixed(12).replace(/0+$/, '');
    return s.endsWith('.') ? s + '00' : s;
  }
  let s = n.toFixed(4).replace(/0+$/, '');
  if (s.endsWith('.')) s += '00';
  return s;
}

function fmtPct(v) { return (parseFloat(v) || 0).toFixed(4) + '%'; }

function clockUpdate() {
  const n = new Date();
  const t = n.toLocaleTimeString('en-IN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  document.getElementById('clock-display').textContent = t;
  document.getElementById('bottom-time').textContent = t + ' IST';
  const mem = (performance?.memory?.usedJSHeapSize / 1048576 || 0).toFixed(0);
  document.getElementById('bottom-memory').textContent = `MEM: ${mem} MB`;
}

// Map market type to TradingView symbol prefix
function tvSymbol(symbol, market) {
  const map = {
    INDIA_NSE: 'NSE', INDIA_BSE: 'BSE', FOREX: 'OANDA',
    BINANCE_SPOT: 'BITSTAMP', BINANCE_PERP: 'BITSTAMP',
    US_STOCKS: 'NASDAQ'
  };
  const prefix = map[market] || 'TVC';
  if (market === 'BINANCE_SPOT' || market === 'BINANCE_PERP') {
    if (symbol.includes('USD')) return `${prefix}:${symbol.replace('USD', 'USD')}`;
  }
  if (market === 'FOREX' && (symbol === 'XAUUSD' || symbol === 'XAGUSD')) return `OANDA:${symbol}`;
  return `${prefix}:${symbol}`;
}

function initChartForSymbol(symbol, market) {
  const label = document.getElementById('chart-sym-label');
  const mktLabel = document.getElementById('chart-market-label');
  if (label) label.textContent = symbol;
  if (mktLabel) mktLabel.textContent = (market || 'NSE').replace(/_/g, ' ');
  initTradingViewChart(tvSymbol(symbol, market || 'INDIA_NSE'));
}

document.addEventListener('DOMContentLoaded', () => {
  const n = new Date();
  const p = new Date(n); p.setDate(p.getDate() - 90);
  document.getElementById('input-end').value = `${n.getFullYear()}-${String(n.getMonth()+1).padStart(2,'0')}-${String(n.getDate()).padStart(2,'0')}`;
  document.getElementById('input-start').value = `${p.getFullYear()}-${String(p.getMonth()+1).padStart(2,'0')}-${String(p.getDate()).padStart(2,'0')}`;
  clockUpdate();
  setInterval(clockUpdate, 1000);

  // Auto-execute on market/symbol change
  document.getElementById('input-market').addEventListener('change', () => {
    const map = { FOREX: 'XAUUSD', BINANCE_SPOT: 'BTCUSD', BINANCE_PERP: 'BTCUSDT.P', INDIA_NSE: 'NIFTY', INDIA_BSE: 'SENSEX', US_STOCKS: 'AAPL', GLOBAL_UNIVERSAL: 'SPX' };
    document.getElementById('input-symbol').value = map[document.getElementById('input-market').value] || 'NIFTY';
    const sym = document.getElementById('input-symbol').value;
    const mkt = document.getElementById('input-market').value;
    initChartForSymbol(sym, mkt);
    if (appState.autoRun) runAllEngines();
  });

  document.getElementById('input-symbol').addEventListener('change', () => {
    const sym = document.getElementById('input-symbol').value.trim().toUpperCase() || 'NIFTY';
    document.getElementById('input-symbol').value = sym;
    const mkt = document.getElementById('input-market').value;
    initChartForSymbol(sym, mkt);
    if (appState.autoRun) runAllEngines();
  });

  // Tab switching
  document.querySelectorAll('.tab').forEach(t => {
    t.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(x => x.classList.remove('active'));
      t.classList.add('active');
      const p = document.getElementById('panel-' + t.dataset.tab);
      if (p) p.classList.add('active');
      // Load scanner when tab activated
      if (t.dataset.tab === 'scanner' && scannerData.length === 0) loadScanner();
    });
  });

  // Quick buttons
  document.querySelectorAll('.q-btn').forEach(b => {
    b.addEventListener('click', () => {
      document.getElementById('input-symbol').value = b.dataset.sym;
      document.getElementById('input-market').value = b.dataset.mkt;
      initChartForSymbol(b.dataset.sym, b.dataset.mkt);
      runAllEngines();
    });
  });

  // Execute buttons
  document.getElementById('btn-execute').addEventListener('click', runAllEngines);
  document.getElementById('btn-run-all').addEventListener('click', runAllEngines);

  // Init chart + map + news + scanner
  initChartForSymbol('NIFTY', 'INDIA_NSE');
  initWorldMap();
  loadNews();
  loadScanner();
  runAllEngines();
});

function initTradingViewChart(symbol) {
  const container = document.getElementById('tv-chart');
  if (!container) return;
  const sym = symbol || 'NSE:NIFTY';

  if (tvWidget && tvWidget.remove) {
    try { tvWidget.remove(); } catch(e) {}
    tvWidget = null;
  }

  container.innerHTML = '';

  if (typeof TradingView === 'undefined') {
    container.innerHTML = '<div style="padding:40px;text-align:center;color:#555;">Chart loading...</div>';
    return;
  }

  try {
    tvWidget = new TradingView.widget({
      container_id: 'tv-chart',
      symbol: sym,
      interval: '60',
      timezone: 'Asia/Kolkata',
      theme: 'dark',
      style: '1',
      locale: 'en',
      toolbar_bg: '#111',
      enable_publishing: false,
      allow_symbol_change: true,
      hideideas: true,
      show_popup_button: false,
      popup_width: 1000,
      popup_height: 650,
      width: '100%',
      height: '100%',
      studies: ['RSI@tv-basicstudies', 'MASimple@tv-basicstudies', 'MACD@tv-basicstudies'],
      backgroundColor: '#0a0a0e',
      gridColor: '#1a1a1e',
      disabled_features: ['left_toolbar', 'header_widget'],
      enabled_features: ['hide_left_toolbar_by_default'],
    });
  } catch(e) {
    container.innerHTML = '<div style="padding:30px;text-align:center;color:#555;">Chart unavailable</div>';
  }
}

function initWorldMap() {
  const container = document.getElementById('world-map');
  if (!container) return;
  try {
    worldMap = L.map('world-map', {
      center: [20, 0], zoom: 2, zoomControl: false, attributionControl: false,
    });
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 18, minZoom: 1,
    }).addTo(worldMap);
    L.control.zoom({ position: 'bottomright' }).addTo(worldMap);
    setTimeout(() => worldMap.invalidateSize(), 500);
  } catch(e) {
    container.innerHTML = '<div style="padding:30px;text-align:center;color:#555;">Map unavailable</div>';
  }
}

function updateWorldMap(newsItems) {
  if (!worldMap || !newsItems || newsItems.length === 0) return;
  mapMarkers.forEach(m => worldMap.removeLayer(m));
  mapMarkers = [];
  const bounds = [];
  const added = new Set();
  newsItems.forEach(item => {
    const key = `${item.country}-${item.category}`;
    if (added.has(key) && mapMarkers.length > 15) return;
    added.add(key);
    const lat = parseFloat(item.lat) || 0;
    const lon = parseFloat(item.lon) || 0;
    if (lat === 0 && lon === 0) return;
    if (Math.abs(lat) < 1 && Math.abs(lon) < 1) return;
    const colorMap = { bullish: '#00e676', bearish: '#ff1744', neutral: '#f5a623' };
    const color = colorMap[item.sentiment] || '#f5a623';
    const marker = L.circleMarker([lat, lon], {
      radius: Math.max(4, 12 - mapMarkers.length * 0.3),
      fillColor: color, color: color, weight: 1, opacity: 0.8, fillOpacity: 0.5,
    }).addTo(worldMap);
    const catMap = { equity: 'Stocks', forex: 'Forex', crypto: 'Crypto', commodity: 'Commodity', bonds: 'Bonds', mutual_funds: 'MF', economy: 'Economy' };
    marker.bindPopup(`<div style="font-size:11px;font-family:monospace;"><b style="color:${color};">${item.sentiment.toUpperCase()}</b><span style="color:#888;margin-left:6px;">${catMap[item.category] || item.category}</span><br><span style="color:#aaa;">${item.country}</span><br><span style="font-size:10px;">${item.title.substring(0, 60)}...</span><br><span style="color:#666;font-size:9px;">${item.source} · ${item.timestamp}</span></div>`);
    mapMarkers.push(marker);
    bounds.push([lat, lon]);
  });
  if (bounds.length > 0) {
    worldMap.fitBounds(bounds, { padding: [30, 30], maxZoom: 4 });
  }
}

function setStatus(text, isLive) {
  const el = document.getElementById('status-indicator');
  el.innerHTML = `● ${text}`;
  el.className = 'status-pulse' + (isLive ? '' : ' off');
  document.getElementById('bottom-status').textContent = `● ${text}`;
}

function showLoading(panelId, msg) {
  const p = document.getElementById(panelId);
  if (p) p.innerHTML = `<div class="panel-placeholder shimmer" style="padding:60px;border-radius:6px;"><div style="position:relative;z-index:1;">${msg}</div></div>`;
}

function showError(panelId, msg) {
  const p = document.getElementById(panelId);
  if (p) p.innerHTML = `<div class="panel-placeholder" style="color:var(--red);">⚠ ${msg}</div>`;
}

function downloadExcel(b64, filename) {
  const a = document.createElement('a');
  a.href = 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,' + b64;
  a.download = filename;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
}

async function apiPost(endpoint, body) {
  const r = await fetch(API_BASE + endpoint, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
  });
  if (!r.ok) { const e = await r.json().catch(() => ({detail:r.statusText})); throw new Error(e.detail || 'API Error'); }
  return await r.json();
}

async function apiGet(endpoint) {
  const r = await fetch(API_BASE + endpoint);
  if (!r.ok) throw new Error(r.statusText);
  return await r.json();
}

async function runAllEngines() {
  if (appState.busy) return;
  appState.busy = true;

  const btn = document.getElementById('btn-execute');
  btn.disabled = true;
  btn.innerHTML = '<span style="font-size:10px;">⏳</span> RUNNING...';

  setStatus('BUSY', false);

  const symbol = document.getElementById('input-symbol').value.trim().toUpperCase() || 'NIFTY';
  const market = document.getElementById('input-market').value;
  const tf = document.getElementById('input-tf').value;
  const mult = parseInt(document.getElementById('input-mult').value) || 1;
  const start = document.getElementById('input-start').value;
  const end = document.getElementById('input-end').value;

  document.querySelector('.tab[data-tab="midpoint"]').click();

  showLoading('panel-midpoint', '⚡ Analyzing 1-Hour Candle for Mid-Point...');
  showLoading('panel-trend11', '🔥 Calculating 11-Trend Volatility...');
  showLoading('panel-gann144', '📐 Building Gann 144 Cycle Matrix...');
  showLoading('panel-footprint', '📡 Scanning Institutional Flow...');

  const payload = { symbol, market_type: market, timeframe: tf, multiplier: mult, start_date: start, end_date: end };

  await Promise.all([
    apiPost('/api/midpoint', { symbol, market_type: market })
      .then(d => renderMidpoint(d)).catch(e => showError('panel-midpoint', e.message)),
    apiPost('/api/trend11', { symbol, market_type: market })
      .then(d => renderTrend11(d)).catch(e => showError('panel-trend11', e.message)),
    apiPost('/api/gann144', payload)
      .then(d => renderGann144(d)).catch(e => showError('panel-gann144', e.message)),
    apiPost('/api/footprint', { symbol, market_type: market })
      .then(d => renderFootprint(d)).catch(e => showError('panel-footprint', e.message))
  ]);

  btn.disabled = false;
  btn.innerHTML = '<span class="btn-text">EXECUTE ALL</span><span class="btn-icon">►</span>';
  setStatus('READY', true);
  appState.busy = false;
}

async function loadScanner() {
  try {
    const data = await apiGet('/api/scanner');
    scannerData = data;
    renderScanner(data);
  } catch(e) {
    const p = document.getElementById('panel-scanner');
    if (p) p.innerHTML = '<div class="panel-placeholder" style="color:var(--red);">⚠ Scanner unavailable</div>';
  }
}
