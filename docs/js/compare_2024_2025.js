/* ============================================================
   compare_2024_2025.js — Pass 14 (v13.14)
   Comparison BRB sur 4 années (2022, 2023, 2024, 2025) par canton.
   Renommé en interne mais conserve le nom de fichier + viz ID.
   ============================================================ */
(function() {
  function init() {
    const el = document.getElementById('viz-compare-2024-2025');
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
    fetch('data/comparison_2021_2025.json')
      .then(r => r.json())
      .then(data => doRender(container, data))
      .catch(err => {
        console.error('compare fetch fail', err);
        container.innerHTML = '<div style="padding:24px;color:var(--c-loro)">Erreur de chargement.</div>';
      });
  }

  function doRender(container, data) {
    const cantons = data.cantons || [];
    const meta = data._meta || {};
    container.innerHTML = '';

    const YEARS = ['2021', '2022', '2023', '2024', '2025'];
    const YEAR_COLORS = {
      '2021': '#bbb6a8', '2022': '#a8a399', '2023': '#7a7570', '2024': '#5b8def', '2025': '#c8102e',
    };
    const totals = meta.totaux_par_annee_M_CHF || {};
    const maxAmt = Math.max(...cantons.flatMap(c => YEARS.map(y => c[`total_${y}_chf`] || 0)), 1);

    // Banner — récap totaux 5 ans
    const banner = document.createElement('div');
    banner.className = 'compare-banner';
    banner.innerHTML = `
      <div class="compare-banner-row" style="display:flex;align-items:flex-end;gap:18px;justify-content:center;flex-wrap:wrap">
        ${YEARS.map(y => `
          <div class="compare-year" style="text-align:center">
            <div class="compare-year-lbl" style="font-size:11px;color:var(--ink-mute);text-transform:uppercase;letter-spacing:0.4px">${y}</div>
            <div class="compare-year-val" style="font-size:24px;font-family:'Source Serif Pro',serif;font-weight:600;color:${YEAR_COLORS[y]}">${(totals[y] || 0).toFixed(1)} M</div>
          </div>
        `).join('')}
      </div>
      <div class="compare-note" style="margin-top:12px;font-size:12.5px;color:var(--ink-mute);text-align:center">
        Totaux distribués chaque année dans le BRB. 2024 = année record (+jackpots, JO, Euro).
      </div>
    `;
    container.appendChild(banner);

    // Per-canton comparison
    const grid = document.createElement('div');
    grid.className = 'compare-grid';
    grid.style.cssText = 'margin-top:18px';
    const cantonLabels = {VD:'Vaud', FR:'Fribourg', VS:'Valais', NE:'Neuchâtel', GE:'Genève', JU:'Jura', SR:'Inter-cantonal'};

    cantons.forEach(c => {
      const dp = c.delta_pct_2021_2025;
      const isPositive = dp > 0;
      const deltaCls = isPositive ? 'is-up' : (dp < 0 ? 'is-down' : 'is-flat');
      const arrow = isPositive ? '▲' : (dp < 0 ? '▼' : '→');
      const row = document.createElement('div');
      row.className = 'compare-row';
      row.innerHTML = `
        <div class="compare-row-head">
          <span class="treemap-canton ${cantonClass(c.canton)}">${c.canton}</span>
          <span class="compare-canton-name">${cantonLabels[c.canton] || c.canton}</span>
          <span class="compare-delta ${deltaCls}" title="Évolution 2021 → 2025">${arrow} ${dp >= 0 ? '+' : ''}${dp}% (2021→2025)</span>
        </div>
        ${YEARS.map(y => {
          const v = c[`total_${y}_chf`] || 0;
          const w = (v / maxAmt) * 100;
          return `
            <div class="compare-bar-row">
              <span class="compare-bar-lbl">${y}</span>
              <div class="compare-bar-wrap">
                <div class="compare-bar" style="width:${w}%;background:${YEAR_COLORS[y]}"></div>
              </div>
              <span class="compare-bar-val">${fmtCHFShort(v)}</span>
            </div>
          `;
        }).join('')}
      `;
      grid.appendChild(row);
    });
    container.appendChild(grid);

    // Notable beneficiary movements (élargi 2022→2025)
    const movers = document.createElement('div');
    movers.className = 'compare-movers';
    movers.innerHTML = `
      <div class="compare-movers-title">Bénéficiaires marquants 2022 → 2025</div>
      <div class="compare-movers-list">
        <div class="compare-mover"><span class="compare-mover-icon up">▲</span><span class="compare-mover-name">Fond. de l'Hermitage</span><span class="compare-mover-vals">140 k → 4 M (×29 sur 4 ans)</span></div>
        <div class="compare-mover"><span class="compare-mover-icon up">▲</span><span class="compare-mover-name">Vaud (total canton)</span><span class="compare-mover-vals">46,6 M → 74,7 M (+60 %)</span></div>
        <div class="compare-mover"><span class="compare-mover-icon up">▲</span><span class="compare-mover-name">Jura (total canton)</span><span class="compare-mover-vals">5,9 M → 8,6 M (+46 %)</span></div>
        <div class="compare-mover"><span class="compare-mover-icon flat">→</span><span class="compare-mover-name">Verbier Festival, Gianadda</span><span class="compare-mover-vals">stables</span></div>
        <div class="compare-mover"><span class="compare-mover-icon down">▼</span><span class="compare-mover-name">SR (intercantonal)</span><span class="compare-mover-vals">21,1 M → 11,5 M (−46 %, recentrage cantonal)</span></div>
      </div>
    `;
    container.appendChild(movers);
  }

  function fmtCHFShort(v) {
    if (v >= 1e6) return (v/1e6).toFixed(1).replace(/\.0$/, '') + ' M';
    if (v >= 1e3) return Math.round(v/1e3) + ' k';
    return String(v);
  }
  function cantonClass(c) { return 'is-' + (c || '').toLowerCase().replace(/[^a-z]/g, ''); }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
