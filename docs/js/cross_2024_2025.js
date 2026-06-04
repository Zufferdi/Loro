/* ============================================================
   cross_2024_2025.js — Pass 12B (v13.12)
   Side-by-side bars showing top 2024 beneficiaries vs their
   2025 amounts. Reveals one-shots vs recurring grants.
   ============================================================ */
(function() {
  function init() {
    const el = document.getElementById('viz-cross-2024-2025');
    if (!el) return;
    if ('IntersectionObserver' in window) {
      const obs = new IntersectionObserver(entries => {
        entries.forEach(e => {
          if (e.isIntersecting) {
            render(e.target);
            obs.unobserve(e.target);
          }
        });
      }, {rootMargin: '200px'});
      obs.observe(el);
    } else {
      render(el);
    }
  }

  function render(container) {
    if (container.dataset.loaded === '1') return;
    container.dataset.loaded = '1';
    container.innerHTML = '<div style="padding:32px;text-align:center;color:var(--ink-mute);font-style:italic">Chargement…</div>';
    fetch('data/cross_2024_2025_top.json')
      .then(r => r.json())
      .then(data => doRender(container, data))
      .catch(err => {
        console.error('cross fetch fail', err);
        container.innerHTML = '<div style="padding:24px;color:var(--c-loro)">Erreur de chargement.</div>';
      });
  }

  function doRender(container, data) {
    const list = data.beneficiaires || [];
    container.innerHTML = '';

    // Quick stats
    const n = list.length;
    const oneShots = list.filter(b => b.is_one_shot_2024).length;
    const recurring = list.filter(b => b.montant_2025_CHF > 0).length;
    const stats = document.createElement('div');
    stats.className = 'cross-stats';
    stats.innerHTML = `
      <div class="cross-stat">
        <div class="cross-stat-val">${n}</div>
        <div class="cross-stat-lbl">bénéficiaires top 2024</div>
      </div>
      <div class="cross-stat">
        <div class="cross-stat-val">${recurring}</div>
        <div class="cross-stat-lbl">retrouvés en 2025</div>
      </div>
      <div class="cross-stat">
        <div class="cross-stat-val">${oneShots}</div>
        <div class="cross-stat-lbl">projets one-shot 2024 (≥&nbsp;500&nbsp;k)</div>
      </div>
    `;
    container.appendChild(stats);

    const maxAmt = Math.max(...list.flatMap(b => [b.montant_2024_CHF, b.montant_2025_CHF]), 1);

    // Filter controls
    const ctrls = document.createElement('div');
    ctrls.className = 'cross-controls';
    ctrls.innerHTML = `
      <button class="cross-filter is-active" data-filter="all">Tous (${n})</button>
      <button class="cross-filter" data-filter="rising">📈 En hausse</button>
      <button class="cross-filter" data-filter="stable">→ Stables</button>
      <button class="cross-filter" data-filter="falling">📉 En baisse</button>
      <button class="cross-filter" data-filter="oneshot">⚡ One-shots 2024</button>
    `;
    container.appendChild(ctrls);

    const grid = document.createElement('div');
    grid.className = 'cross-grid';
    container.appendChild(grid);

    function classify(b) {
      if (b.montant_2025_CHF === 0 && b.montant_2024_CHF >= 500000) return 'oneshot';
      if (b.delta_pct > 20) return 'rising';
      if (b.delta_pct < -20) return 'falling';
      return 'stable';
    }

    function renderList(filter) {
      grid.innerHTML = '';
      const filtered = filter === 'all' ? list : list.filter(b => classify(b) === filter);
      if (!filtered.length) {
        grid.innerHTML = '<div style="padding:14px;color:var(--ink-mute);font-style:italic">Aucun bénéficiaire dans cette catégorie.</div>';
        return;
      }
      filtered.forEach(b => {
        const cls = classify(b);
        const w2024 = (b.montant_2024_CHF / maxAmt) * 100;
        const w2025 = (b.montant_2025_CHF / maxAmt) * 100;
        const arrow = cls === 'rising' ? '▲' : (cls === 'falling' ? '▼' : (cls === 'oneshot' ? '⚡' : '→'));
        const pctStr = b.montant_2025_CHF === 0
          ? 'one-shot'
          : (b.delta_pct >= 0 ? '+' : '') + b.delta_pct + '%';
        const row = document.createElement('div');
        row.className = `cross-row is-${cls}`;
        row.innerHTML = `
          <div class="cross-row-head">
            <span class="treemap-canton ${cantonClass(b.canton)}">${b.canton}</span>
            <span class="cross-name" title="${escapeHtml(b.nom_2025 || b.nom_2024)}">${escapeHtml(b.nom_2024)}</span>
            <span class="cross-delta is-${cls}">${arrow} ${pctStr}</span>
          </div>
          ${b.note ? `<div class="cross-note">${escapeHtml(b.note)}</div>` : ''}
          <div class="compare-bar-row">
            <span class="compare-bar-lbl">2024</span>
            <div class="compare-bar-wrap"><div class="compare-bar compare-bar-2024" style="width:${w2024}%"></div></div>
            <span class="compare-bar-val">${fmtCHFShort(b.montant_2024_CHF)}</span>
          </div>
          <div class="compare-bar-row">
            <span class="compare-bar-lbl">2025</span>
            <div class="compare-bar-wrap"><div class="compare-bar compare-bar-2025" style="width:${w2025}%"></div></div>
            <span class="compare-bar-val">${b.montant_2025_CHF === 0 ? '—' : fmtCHFShort(b.montant_2025_CHF)}</span>
          </div>
        `;
        grid.appendChild(row);
      });
    }

    renderList('all');

    // Filter buttons
    ctrls.querySelectorAll('.cross-filter').forEach(btn => {
      btn.addEventListener('click', () => {
        ctrls.querySelectorAll('.cross-filter').forEach(b => b.classList.remove('is-active'));
        btn.classList.add('is-active');
        renderList(btn.dataset.filter);
      });
    });
  }

  function fmtCHFShort(v) {
    if (v >= 1e6) return (v/1e6).toFixed(2).replace(/\.?0+$/, '') + ' M';
    if (v >= 1e3) return Math.round(v/1e3) + ' k';
    return String(v);
  }
  function cantonClass(c) { return 'is-' + (c || '').toLowerCase().replace(/[^a-z]/g, ''); }
  function escapeHtml(s) {
    return (s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
