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
    const meta = data._meta || {};
    container.innerHTML = '';

    const YEARS = ['2021', '2022', '2023', '2024', '2025'];
    const YEAR_COLORS = {
      '2021': '#bbb6a8', '2022': '#a8a399', '2023': '#7a7570', '2024': '#5b8def', '2025': '#c8102e',
    };

    // Quick stats
    const n = list.length;
    const oneShots = list.filter(b => b.is_one_shot_2024).length;
    const stable5y = list.filter(b => b.nb_years_active === 5).length;
    const stats = document.createElement('div');
    stats.className = 'cross-stats';
    stats.innerHTML = `
      <div class="cross-stat">
        <div class="cross-stat-val">${n}</div>
        <div class="cross-stat-lbl">bénéficiaires top</div>
      </div>
      <div class="cross-stat">
        <div class="cross-stat-val">${stable5y}</div>
        <div class="cross-stat-lbl">présents 5 années (2021-2025)</div>
      </div>
      <div class="cross-stat">
        <div class="cross-stat-val">${oneShots}</div>
        <div class="cross-stat-lbl">one-shots 2024 (≥&nbsp;500&nbsp;k)</div>
      </div>
    `;
    container.appendChild(stats);

    const maxAmt = Math.max(...list.flatMap(b => YEARS.map(y => b[`montant_${y}_CHF`] || 0)), 1);

    // Filter controls
    const ctrls = document.createElement('div');
    ctrls.className = 'cross-controls';
    ctrls.innerHTML = `
      <button class="cross-filter is-active" data-filter="all">Tous (${n})</button>
      <button class="cross-filter" data-filter="rising">📈 En hausse 22-25</button>
      <button class="cross-filter" data-filter="stable">→ Stables</button>
      <button class="cross-filter" data-filter="falling">📉 En baisse</button>
      <button class="cross-filter" data-filter="oneshot">⚡ One-shots</button>
      <button class="cross-filter" data-filter="4year">4 années complètes</button>
    `;
    container.appendChild(ctrls);

    const grid = document.createElement('div');
    grid.className = 'cross-grid';
    container.appendChild(grid);

    function classify(b) {
      const a21 = b.montant_2021_CHF || 0;
      const a25 = b.montant_2025_CHF || 0;
      const a24 = b.montant_2024_CHF || 0;
      if (a25 === 0 && a24 >= 500000) return 'oneshot';
      // Calcul tendance sur 5 ans si dispo
      const dp21_25 = a21 > 0 ? ((a25 - a21) / a21 * 100) : (b.delta_pct || 0);
      if (dp21_25 > 20) return 'rising';
      if (dp21_25 < -20) return 'falling';
      return 'stable';
    }

    function renderList(filter) {
      grid.innerHTML = '';
      let filtered;
      if (filter === 'all') filtered = list;
      else if (filter === '5year') filtered = list.filter(b => b.nb_years_active === 5);
      else if (filter === '4year') filtered = list.filter(b => b.nb_years_active === 4);
      else filtered = list.filter(b => classify(b) === filter);
      if (!filtered.length) {
        grid.innerHTML = '<div style="padding:14px;color:var(--ink-mute);font-style:italic">Aucun bénéficiaire dans cette catégorie.</div>';
        return;
      }
      filtered.forEach(b => {
        const cls = classify(b);
        const arrow = cls === 'rising' ? '▲' : (cls === 'falling' ? '▼' : (cls === 'oneshot' ? '⚡' : '→'));
        const a21 = b.montant_2021_CHF || 0;
        const a25 = b.montant_2025_CHF || 0;
        const dp21_25 = a21 > 0 ? Math.round(((a25 - a21) / a21) * 100) : 0;
        const pctStr = (cls === 'oneshot' && b.montant_2025_CHF === 0) ? 'one-shot 2024' : (dp21_25 >= 0 ? '+' : '') + dp21_25 + '% (21-25)';
        const row = document.createElement('div');
        row.className = `cross-row is-${cls}`;
        const barsHtml = YEARS.map(y => {
          const v = b[`montant_${y}_CHF`] || 0;
          const w = (v / maxAmt) * 100;
          return `
            <div class="compare-bar-row">
              <span class="compare-bar-lbl">${y}</span>
              <div class="compare-bar-wrap"><div class="compare-bar" style="width:${w}%;background:${YEAR_COLORS[y]}"></div></div>
              <span class="compare-bar-val">${v === 0 ? '—' : fmtCHFShort(v)}</span>
            </div>`;
        }).join('');
        row.innerHTML = `
          <div class="cross-row-head">
            <span class="treemap-canton ${cantonClass(b.canton)}">${b.canton}</span>
            <span class="cross-name" title="${escapeHtml(b.nom_2025 || b.nom_2024)}">${escapeHtml(b.nom_2024 || b.nom_2025)}</span>
            <span class="cross-delta is-${cls}">${arrow} ${pctStr}</span>
          </div>
          ${b.note ? `<div class="cross-note">${escapeHtml(b.note)}</div>` : ''}
          ${barsHtml}
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
