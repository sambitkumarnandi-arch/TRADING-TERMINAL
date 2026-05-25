function renderMidpoint(d) {
  if (!d || d.error) { showError('panel-midpoint', d?.error || 'No data'); return; }
  const p = document.getElementById('panel-midpoint');
  let html = `<div class="result-card fade-in">
    <div class="result-card-header">
      <h2>${d.Symbol} <span style="font-size:11px;color:var(--text-dim);font-weight:400;">${d.Exchange}</span></h2>
      <span class="exchange-badge">MID-POINT</span>
    </div>
    <div class="result-card-body">
      <div style="font-size:10px;color:var(--text-dim);margin-bottom:12px;">Base 1H Candle (IST): ${d.Time}</div>
      <div class="info-grid">
        <div class="info-grid-item" style="border-top-color:var(--cyan);"><div class="label">Open</div><div class="value cyan">${fmt(d.Open)}</div></div>
        <div class="info-grid-item" style="border-top-color:var(--green);"><div class="label">High</div><div class="value green">${fmt(d.High)}</div></div>
        <div class="info-grid-item" style="border-top-color:var(--red);"><div class="label">Low</div><div class="value red">${fmt(d.Low)}</div></div>
        <div class="info-grid-item" style="border-top-color:var(--amber);"><div class="label">Mid Point</div><div class="value amber">${fmt(d.Mid)}</div></div>
        <div class="info-grid-item" style="border-top-color:var(--purple);"><div class="label">Range</div><div class="value purple">${fmt(d.Range)}</div></div>
      </div>
      <div class="zone-grid">
        <div class="buy-zone">
          <div class="zone-title"><span>BUY ZONE</span></div>
          <div class="zone-row"><span class="lbl">ENTRY</span><span class="val">${fmt(d.Buy_Entry)}</span></div>
          <div class="zone-row"><span class="lbl">TARGET 1</span><span class="val">${fmt(d.Buy_T1)}</span></div>
          <div class="zone-row"><span class="lbl">MID TGT</span><span class="val">${fmt(d['Buy_between T1 & T2'])}</span></div>
          <div class="zone-row"><span class="lbl">TARGET 2</span><span class="val">${fmt(d.Buy_T2)}</span></div>
          <div class="zone-row"><span class="lbl">TARGET 3</span><span class="val">${fmt(d.Buy_T3)}</span></div>
        </div>
        <div class="sell-zone">
          <div class="zone-title"><span>SELL ZONE</span></div>
          <div class="zone-row"><span class="lbl">ENTRY</span><span class="val">${fmt(d.Sell_Entry)}</span></div>
          <div class="zone-row"><span class="lbl">TARGET 1</span><span class="val">${fmt(d.Sell_T1)}</span></div>
          <div class="zone-row"><span class="lbl">MID TGT</span><span class="val">${fmt(d['Sell_between T1 & T2'])}</span></div>
          <div class="zone-row"><span class="lbl">TARGET 2</span><span class="val">${fmt(d.Sell_T2)}</span></div>
          <div class="zone-row"><span class="lbl">TARGET 3</span><span class="val">${fmt(d.Sell_T3)}</span></div>
        </div>
      </div>
      <div class="stop-loss-box"><p>⚠ STOP LOSS: ${fmt(d.Stop_Loss)} (Mid-Point)</p></div>
      <div style="text-align:center;margin-top:14px;">
        <button class="btn-download" onclick="downloadExcel('${d._excel_b64 || ''}','${d._excel_filename || 'midpoint.xlsx'}')">⬇ DOWNLOAD EXCEL</button>
      </div>
    </div>
  </div>`;
  p.innerHTML = html;
}

function renderTrend11(d) {
  if (!d || d.error) { showError('panel-trend11', d?.error || 'No data'); return; }
  const p = document.getElementById('panel-trend11');
  let html = `<div class="result-card fade-in">
    <div class="result-card-header">
      <h2>${d.Symbol} <span style="font-size:11px;color:var(--text-dim);font-weight:400;">${d.Exchange}</span></h2>
      <span class="exchange-badge">11-TREND</span>
    </div>
    <div class="result-card-body">
      <div class="info-grid">
        <div class="info-grid-item" style="border-top-color:${d.Status_Color || '#888'};">
          <div class="label">Market</div>
          <div class="value" style="color:${d.Status_Color || '#888'};font-size:14px;">${d.Market_Status || '--'}</div>
        </div>
        <div class="info-grid-item" style="border-top-color:var(--cyan);"><div class="label">Close</div><div class="value cyan">${fmt(d.Close)}</div></div>
        <div class="info-grid-item" style="border-top-color:var(--amber);"><div class="label">Volatility</div><div class="value amber">${fmtPct(d.Volatility)}</div></div>
        <div class="info-grid-item" style="border-top-color:var(--purple);"><div class="label">Expected Range</div><div class="value purple">${fmt(d.Expected_Range)}</div></div>
        <div class="info-grid-item" style="border-top-color:var(--green);"><div class="label">Live Price</div><div class="value green">${fmt(d.Live_Price)}</div></div>
      </div>
      <div style="margin-top:14px;">
        <table class="terminal-table">
          <thead><tr><th>Degree</th><th>Buy Target</th><th>Sell Target</th></tr></thead>
          <tbody>
            ${d.Degrees_List.map(deg => {
              const b = d.Targets.BUY[String(deg)];
              const s = d.Targets.SELL[String(deg)];
              const isKey = [15, 45, 86.25].includes(deg);
              const cls = idx => isKey ? 'cell-key' : '';
              return `<tr><td class="${cls(0)}">${deg}°</td><td class="cell-buy ${cls(1)}">${fmt(b)}</td><td class="cell-sell ${cls(2)}">${fmt(s)}</td></tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>
      <div style="text-align:center;margin-top:14px;">
        <button class="btn-download" onclick="downloadExcel('${d._excel_b64 || ''}','${d._excel_filename || 'trend11.xlsx'}')">⬇ DOWNLOAD EXCEL</button>
      </div>
    </div>
  </div>`;
  p.innerHTML = html;
}

function renderGann144(d) {
  if (!d || d.error) { showError('panel-gann144', d?.error || 'No data'); return; }
  const p = document.getElementById('panel-gann144');
  const lastClose = d.Last_Close;
  let html = `<div class="result-card fade-in">
    <div class="result-card-header">
      <h2>${d.Symbol} <span style="font-size:11px;color:var(--text-dim);font-weight:400;">${d.Timeframe} · ${d.Multiplier}x</span></h2>
      <span class="exchange-badge">GANN 144</span>
    </div>
    <div class="result-card-body">
      <div class="info-grid">
        <div class="info-grid-item" style="border-top-color:var(--cyan);"><div class="label">Last Close</div><div class="value cyan">${fmt(lastClose)}</div></div>
        <div class="info-grid-item" style="border-top-color:var(--green);"><div class="label">Max High</div><div class="value green">${fmt(d.Max_High)}</div></div>
        <div class="info-grid-item" style="border-top-color:var(--red);"><div class="label">Min Low</div><div class="value red">${fmt(d.Min_Low)}</div></div>
        <div class="info-grid-item" style="border-top-color:var(--purple);"><div class="label">Diff</div><div class="value purple">${fmt(d.Diff)}</div></div>
      </div>
      <div class="buy-zone" style="margin-bottom:8px;"><b style="color:var(--green);">🟢 BUY:</b> ${d.Buy_Status}</div>
      <div class="sell-zone" style="margin-bottom:14px;"><b style="color:var(--red);">🔴 SELL:</b> ${d.Sell_Status}</div>
      <div class="gann-matrix">
        <table class="terminal-table">
          <thead><tr><th>TC</th><th>%</th><th colspan="5" style="color:var(--red);">RESISTANCE</th><th colspan="5" style="color:var(--green);">SUPPORT</th></tr></thead>
          <tbody>
            ${d.Matrix.map(row => {
              return `<tr><td class="cell-key">${row.tc}</td><td>${row.pc}</td>
                ${row.h.map(v => `<td class="cell-sell" style="opacity:${0.3 + row.h.indexOf(v) * 0.15}">${fmt(v)}</td>`).join('')}
                ${row.l.map(v => `<td class="cell-buy" style="opacity:${0.3 + row.l.indexOf(v) * 0.15}">${fmt(v)}</td>`).join('')}
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>
      <div style="text-align:center;margin-top:14px;">
        <button class="btn-download" onclick="downloadExcel('${d._excel_b64 || ''}','${d._excel_filename || 'gann144.xlsx'}')">⬇ DOWNLOAD EXCEL</button>
      </div>
    </div>
  </div>`;
  p.innerHTML = html;
}

function renderFootprint(d) {
  if (!d || d.error) { showError('panel-footprint', d?.error || 'No data'); return; }
  const p = document.getElementById('panel-footprint');
  let html = `<div class="result-card fade-in">
    <div class="result-card-header">
      <h2>${d.Symbol} <span style="font-size:11px;color:var(--text-dim);font-weight:400;">${d.Exchange}</span></h2>
      <span class="exchange-badge">SMART MONEY</span>
    </div>
    <div class="result-card-body">`;

  // Live Alerts
  if (d.Live_Alerts && d.Live_Alerts.length > 0) {
    html += `<div style="border:1px solid rgba(234,179,8,0.4);border-radius:6px;padding:10px;margin-bottom:12px;background:rgba(234,179,8,0.04);">
      <h3 style="color:var(--amber);font-size:11px;text-transform:uppercase;margin-bottom:6px;letter-spacing:1px;">📡 Live Radar (3-Min)</h3>`;
    d.Live_Alerts.forEach(a => {
      html += `<div class="alert-item"><span class="alert-time">${a.Time}</span><span class="alert-action" style="color:${a.Color};">${a.Action}</span><span class="alert-vol">${a.Volume_Spike}</span><span class="alert-price">${fmt(a.Price)}</span></div>`;
    });
    html += '</div>';
  } else {
    html += `<div style="border:1px solid var(--border-subtle);border-radius:6px;padding:10px;margin-bottom:12px;"><div style="color:var(--text-dim);text-align:center;font-size:11px;">No live whale orders in last 15 min</div></div>`;
  }

  // Intraday Zones
  if (d.Intraday_Zones && d.Intraday_Zones.length > 0) {
    html += `<h3 style="color:var(--cyan);font-size:11px;text-transform:uppercase;margin-bottom:6px;letter-spacing:1px;">🐋 Intraday Zones</h3>
    <table class="terminal-table"><thead><tr><th>Time</th><th>TF</th><th>Action</th><th>Vol</th><th>Zone</th></tr></thead><tbody>`;
    d.Intraday_Zones.forEach(z => {
      html += `<tr><td>${z.Time}</td><td>${z.TF}</td><td style="color:${z.Color};">${z.Action}</td><td style="color:var(--amber);">${z.Volume_Spike}</td><td style="color:${z.Color};">${z.Zone}</td></tr>`;
    });
    html += '</tbody></table>';
  }

  // Macro Zones
  if (d.Macro_Zones && d.Macro_Zones.length > 0) {
    html += `<h3 style="color:var(--purple);font-size:11px;text-transform:uppercase;margin:12px 0 6px;letter-spacing:1px;">🏦 Macro Walls (4H)</h3>
    <table class="terminal-table"><thead><tr><th>Time</th><th>TF</th><th>Posture</th><th>Intensity</th><th>Zone</th></tr></thead><tbody>`;
    d.Macro_Zones.forEach(z => {
      html += `<tr><td>${z.Time}</td><td>${z.TF}</td><td style="color:${z.Color};font-weight:600;">${z.Action}</td><td style="color:var(--amber);font-weight:600;">${z.Volume_Spike}</td><td style="color:${z.Color};">${z.Zone}</td></tr>`;
    });
    html += '</tbody></table>';
  }

  html += '</div></div>';
  p.innerHTML = html;
}

function renderScanner(data) {
  const p = document.getElementById('panel-scanner');
  if (!p) return;
  if (!data || (!data.results && !data.crypto_perp)) {
    p.innerHTML = '<div class="panel-placeholder">No scanner results available</div>';
    return;
  }

  let html = '';
  const allMarkets = data.results ? [...new Set(data.results.map(r => r.market))] : [];

  if (data.results && data.results.length > 0) {
    html += `<div class="scanner-meta">
      <span>Scanned <span class="scanner-total">${data.total_scanned} assets</span> across ${allMarkets.length} markets</span>
      <span class="scanner-time">${data.scanned_at}</span>
      <select class="scanner-market-select" onchange="filterScanner(this.value)">
        <option value="all">ALL MARKETS</option>
        ${allMarkets.map(m => `<option value="${m}">${m.replace(/_/g, ' ')}</option>`).join('')}
      </select>
    </div>
    <div id="scanner-table-wrap">
    <table class="scan-table">
      <thead><tr>
        <th>#</th><th>Symbol</th><th>Market</th><th>Price</th><th>Chg%</th>
        <th>ADX</th><th>RSI</th><th>Alpha</th><th>Rating</th><th>Signal</th>
      </tr></thead><tbody>`;

    data.results.forEach((r, i) => {
      const alpha = r.alpha || 0;
      const alphaColor = alpha >= 75 ? 'var(--green)' : alpha >= 60 ? '#66bb6a' : alpha >= 45 ? 'var(--amber)' : alpha >= 30 ? 'var(--orange)' : 'var(--red)';
      const chgCls = r.change_pct >= 0 ? 'cell-buy' : 'cell-sell';
      html += `<tr>
        <td style="color:var(--text-dim);">${i + 1}</td>
        <td class="scan-sym" onclick="document.getElementById('input-symbol').value='${r.symbol}';document.getElementById('input-market').value='${r.market}';initChartForSymbol('${r.symbol}','${r.market}');runAllEngines();">${r.symbol}</td>
        <td style="font-size:9px;color:var(--text-dim);">${r.exchange}</td>
        <td>${fmt(r.price)}</td>
        <td class="${chgCls}">${r.change_pct >= 0 ? '+' : ''}${r.change_pct}%</td>
        <td class="scan-adx">${r.adx}</td>
        <td class="scan-rsi">${r.rsi}</td>
        <td class="scan-alpha" style="color:${alphaColor};">${alpha}</td>
        <td class="scan-rating rating-${r.rating.replace(' ', '')}">${r.rating}</td>
        <td class="signal-${r.signal}">${r.signal}</td>
      </tr>`;
    });
    html += '</tbody></table></div>';
  }

  if (data.crypto_perp && data.crypto_perp.results && data.crypto_perp.results.length > 0) {
    const perp = data.crypto_perp;
    html += `<div class="crypto-perp-section">
      <div class="crypto-perp-header">
        <h3>CRYPTO PERPETUAL CONTRACTS</h3>
        <div class="perp-summary">
          <span class="perp-total">${perp.total_scanned} pairs</span>
          <span class="perp-breakouts">Breakouts: ${perp.breakouts ? perp.breakouts.length : 0}</span>
          <span class="perp-breakdowns">Breakdowns: ${perp.breakdowns ? perp.breakdowns.length : 0}</span>
        </div>
      </div>
      <div class="perp-benchmarks-note">
        Alpha vs Benchmarks: ETH/BTC · SOL/BTC · TOTAL Mkt Cap (90d)
      </div>
      <table class="scan-table perp-table">
        <thead><tr>
          <th>#</th><th>Symbol</th><th>Price</th><th>ADX</th><th>RSI</th><th>Vol%</th>
          <th>Δ7d</th><th>Δ14d</th><th>α Score</th><th>Rating</th><th>Signal</th><th>Pattern</th>
        </tr></thead><tbody>`;

    perp.results.forEach((r, i) => {
      const alphaScore = r.alpha_score || 0;
      const alphaColor = alphaScore >= 75 ? 'var(--green)' : alphaScore >= 60 ? '#66bb6a' : alphaScore >= 45 ? 'var(--amber)' : alphaScore >= 30 ? 'var(--orange)' : 'var(--red)';
      const deltaCls = r.delta_14d >= 0 ? 'cell-buy' : 'cell-sell';
      let pattern = r.breakout ? '🟢 BREAKOUT' : r.breakdown ? '🔴 BREAKDOWN' : '—';
      let patternCls = r.breakout ? 'cell-buy' : r.breakdown ? 'cell-sell' : '';
      html += `<tr>
        <td style="color:var(--text-dim);">${i + 1}</td>
        <td class="scan-sym" onclick="document.getElementById('input-symbol').value='${r.symbol}';document.getElementById('input-market').value='CRYPTO';initChartForSymbol('${r.symbol}','CRYPTO');runAllEngines();">${r.symbol}</td>
        <td>${fmt(r.price)}</td>
        <td class="scan-adx">${r.adx}</td>
        <td class="scan-rsi">${r.rsi}</td>
        <td class="scan-vol">${r.volatility_pct}%</td>
        <td class="${deltaCls}">${r.delta_7d >= 0 ? '+' : ''}${r.delta_7d}%</td>
        <td class="${deltaCls}">${r.delta_14d >= 0 ? '+' : ''}${r.delta_14d}%</td>
        <td class="scan-alpha" style="color:${alphaColor};">${alphaScore}</td>
        <td class="scan-rating rating-${r.rating.replace(' ', '')}">${r.rating}</td>
        <td class="signal-${r.signal}">${r.signal}</td>
        <td class="${patternCls}">${pattern}</td>
      </tr>`;
    });
    html += '</tbody></table></div>';
  }

  p.innerHTML = html;
  scannerData = data;
}

function filterScanner(market) {
  if (!scannerData || !scannerData.results) return;
  const filtered = market === 'all'
    ? scannerData.results
    : scannerData.results.filter(r => r.market === market);
  const p = document.getElementById('panel-scanner');
  if (!p) return;
  const tableWrap = document.getElementById('scanner-table-wrap');
  if (!tableWrap) return;

  let html = `<table class="scan-table">
    <thead><tr>
      <th>#</th><th>Symbol</th><th>Market</th><th>Price</th><th>Chg%</th>
      <th>ADX</th><th>RSI</th><th>Alpha</th><th>Rating</th><th>Signal</th>
    </tr></thead><tbody>`;

  filtered.forEach((r, i) => {
    const alpha = r.alpha || 0;
    const alphaColor = alpha >= 75 ? 'var(--green)' : alpha >= 60 ? '#66bb6a' : alpha >= 45 ? 'var(--amber)' : alpha >= 30 ? 'var(--orange)' : 'var(--red)';
    const chgCls = r.change_pct >= 0 ? 'cell-buy' : 'cell-sell';
    html += `<tr>
      <td style="color:var(--text-dim);">${i + 1}</td>
      <td class="scan-sym" onclick="document.getElementById('input-symbol').value='${r.symbol}';document.getElementById('input-market').value='${r.market}';initChartForSymbol('${r.symbol}','${r.market}');runAllEngines();">${r.symbol}</td>
      <td style="font-size:9px;color:var(--text-dim);">${r.exchange}</td>
      <td>${fmt(r.price)}</td>
      <td class="${chgCls}">${r.change_pct >= 0 ? '+' : ''}${r.change_pct}%</td>
      <td class="scan-adx">${r.adx}</td>
      <td class="scan-rsi">${r.rsi}</td>
      <td class="scan-alpha" style="color:${alphaColor};">${alpha}</td>
      <td class="scan-rating rating-${r.rating.replace(' ', '')}">${r.rating}</td>
      <td class="signal-${r.signal}">${r.signal}</td>
    </tr>`;
  });

  html += '</tbody></table>';
  tableWrap.innerHTML = html;
}

  const allMarkets = [...new Set(data.results.map(r => r.market))];
  let html = `<div class="scanner-meta">
    <span>Scanned <span class="scanner-total">${data.total_scanned} assets</span> across ${allMarkets.length} markets</span>
    <span class="scanner-time">${data.scanned_at}</span>
    <select class="scanner-market-select" onchange="filterScanner(this.value)">
      <option value="all">ALL MARKETS</option>
      ${allMarkets.map(m => `<option value="${m}">${m.replace(/_/g, ' ')}</option>`).join('')}
    </select>
  </div>
  <div id="scanner-table-wrap">
  <table class="scan-table">
    <thead><tr>
      <th>#</th><th>Symbol</th><th>Market</th><th>Price</th><th>Chg%</th>
      <th>ADX</th><th>RSI</th><th>Alpha</th><th>Rating</th><th>Signal</th>
    </tr></thead><tbody>`;

  data.results.forEach((r, i) => {
    const alpha = r.alpha || 0;
    const alphaColor = alpha >= 75 ? 'var(--green)' : alpha >= 60 ? '#66bb6a' : alpha >= 45 ? 'var(--amber)' : alpha >= 30 ? 'var(--orange)' : 'var(--red)';
    const chgCls = r.change_pct >= 0 ? 'cell-buy' : 'cell-sell';
    html += `<tr>
      <td style="color:var(--text-dim);">${i + 1}</td>
      <td class="scan-sym" onclick="document.getElementById('input-symbol').value='${r.symbol}';document.getElementById('input-market').value='${r.market}';initChartForSymbol('${r.symbol}','${r.market}');runAllEngines();">${r.symbol}</td>
      <td style="font-size:9px;color:var(--text-dim);">${r.exchange}</td>
      <td>${fmt(r.price)}</td>
      <td class="${chgCls}">${r.change_pct >= 0 ? '+' : ''}${r.change_pct}%</td>
      <td class="scan-adx">${r.adx}</td>
      <td class="scan-rsi">${r.rsi}</td>
      <td class="scan-alpha" style="color:${alphaColor};">${alpha}</td>
      <td class="scan-rating rating-${r.rating.replace(' ', '')}">${r.rating}</td>
      <td class="signal-${r.signal}">${r.signal}</td>
    </tr>`;
  });

  html += '</tbody></table></div>';
  p.innerHTML = html;
  scannerData = data;
}

function filterScanner(market) {
  if (!scannerData || !scannerData.results) return;
  const filtered = market === 'all'
    ? scannerData.results
    : scannerData.results.filter(r => r.market === market);
  const p = document.getElementById('panel-scanner');
  if (!p) return;
  const tableWrap = document.getElementById('scanner-table-wrap');
  if (!tableWrap) return;

  let html = `<table class="scan-table">
    <thead><tr>
      <th>#</th><th>Symbol</th><th>Market</th><th>Price</th><th>Chg%</th>
      <th>ADX</th><th>RSI</th><th>Alpha</th><th>Rating</th><th>Signal</th>
    </tr></thead><tbody>`;

  filtered.forEach((r, i) => {
    const alpha = r.alpha || 0;
    const alphaColor = alpha >= 75 ? 'var(--green)' : alpha >= 60 ? '#66bb6a' : alpha >= 45 ? 'var(--amber)' : alpha >= 30 ? 'var(--orange)' : 'var(--red)';
    const chgCls = r.change_pct >= 0 ? 'cell-buy' : 'cell-sell';
    html += `<tr>
      <td style="color:var(--text-dim);">${i + 1}</td>
      <td class="scan-sym" onclick="document.getElementById('input-symbol').value='${r.symbol}';document.getElementById('input-market').value='${r.market}';initChartForSymbol('${r.symbol}','${r.market}');runAllEngines();">${r.symbol}</td>
      <td style="font-size:9px;color:var(--text-dim);">${r.exchange}</td>
      <td>${fmt(r.price)}</td>
      <td class="${chgCls}">${r.change_pct >= 0 ? '+' : ''}${r.change_pct}%</td>
      <td class="scan-adx">${r.adx}</td>
      <td class="scan-rsi">${r.rsi}</td>
      <td class="scan-alpha" style="color:${alphaColor};">${alpha}</td>
      <td class="scan-rating rating-${r.rating.replace(' ', '')}">${r.rating}</td>
      <td class="signal-${r.signal}">${r.signal}</td>
    </tr>`;
  });

  html += '</tbody></table>';
  tableWrap.innerHTML = html;
}
