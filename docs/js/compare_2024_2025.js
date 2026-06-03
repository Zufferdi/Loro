/* ============================================================
   compare_2024_2025.js — Pass 11 (v13.11)
   Comparison visualization of BRB 2024 vs 2025 at canton level.
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
    fetch('data/comparison_2024_2025.json')
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

    // Find max for scaling
    const maxAmt = Math.max(...cantons.flatMap(c => [c.total_2024_chf, c.total_2025_chf]), 1);

    // Banner with total comparison
    const banner = document.createElement('div');
    banner.className = 'compare-banner';
    banner.innerHTML = `
      <div class="compare-banner-row">
        <div class="compare-year">
          <div class="compare-year-lbl">2024 (record)</div>
          <div class="compare-year-val">258,2 M CHF</div>
        </div>
        <div class="compare-arrow">→</div>
        <div class="compare-year">
          <div class="compare-year-lbl">2025</div>
          <div class="compare-year-val">252,0 M CHF</div>
        </div>
        <div class="compare-delta-banner">−2,4&nbsp;%</div>
      </div>
      <div class="compare-note">
        2024 a été une année record absolu (jackpots Swiss Loto exceptionnels, Euro de foot, JO de Paris).
        2025 confirme un retour à un niveau plus normal.
      </div>
    `;
    container.appendChild(banner);

    // Per-canton comparison
    const grid = document.createElement('div');
    grid.className = 'compare-grid';
    const cantonLabels = {VD:'Vaud', FR:'Fribourg', VS:'Valais', NE:'Neuchâtel', GE:'Genève'};
    cantons.forEach(c => {
      const w2024 = (c.total_2024_chf / maxAmt) * 100;
      const w2025 = (c.total_2025_chf / maxAmt) * 100;
      const isPositive = c.delta_pct > 0;
      const deltaCls = isPositive ? 'is-up' : (c.delta_pct < 0 ? 'is-down' : 'is-flat');
      const arrow = isPositive ? '▲' : (c.delta_pct < 0 ? '▼' : '→');
      const row = document.createElement('div');
      row.className = 'compare-row';
      row.innerHTML = `
        <div class="compare-row-head">
          <span class="treemap-canton ${cantonClass(c.canton)}">${c.canton}</span>
          <span class="compare-canton-name">${cantonLabels[c.canton] || c.canton}</span>
          <span class="compare-delta ${deltaCls}">${arrow} ${c.delta_pct >= 0 ? '+' : ''}${c.delta_pct}%</span>
          ${c.is_partial_2024 ? '<span class="compare-partial" title="Section partielle">⚠ partiel</span>' : ''}
        </div>
        <div class="compare-bar-row">
          <span class="compare-bar-lbl">2024</span>
          <div class="compare-bar-wrap">
            <div class="compare-bar compare-bar-2024" style="width:${w2024}%"></div>
          </div>
          <span class="compare-bar-val">${fmtCHFShort(c.total_2024_chf)}</span>
        </div>
        <div class="compare-bar-row">
          <span class="compare-bar-lbl">2025</span>
          <div class="compare-bar-wrap">
            <div class="compare-bar compare-bar-2025" style="width:${w2025}%"></div>
          </div>
          <span class="compare-bar-val">${fmtCHFShort(c.total_2025_chf)}</span>
        </div>
      `;
      grid.appendChild(row);
    });
    container.appendChild(grid);

    // Notable beneficiary movements
    const movers = document.createElement('div');
    movers.className = 'compare-movers';
    movers.innerHTML = `
      <div class="compare-movers-title">Bénéficiaires marquants 2024 → 2025</div>
      <div class="compare-movers-list">
        <div class="compare-mover"><span class="compare-mover-icon up">▲</span><span class="compare-mover-name">Fond. de l'Hermitage</span><span class="compare-mover-vals">300 k → 4 M (+1'233 %)</span></div>
        <div class="compare-mover"><span class="compare-mover-icon up">▲</span><span class="compare-mover-name">Cinéforom</span><span class="compare-mover-vals">700 k → 1,7 M (+143 %)</span></div>
        <div class="compare-mover"><span class="compare-mover-icon up">▲</span><span class="compare-mover-name">Théâtre Vidy (art dramatique)</span><span class="compare-mover-vals">650 k → 1,35 M (+108 %)</span></div>
        <div class="compare-mover"><span class="compare-mover-icon flat">→</span><span class="compare-mover-name">Verbier Festival, Gianadda, Banc Public</span><span class="compare-mover-vals">stable (0&nbsp;%)</span></div>
        <div class="compare-mover"><span class="compare-mover-icon down">▼</span><span class="compare-mover-name">Fonds catastrophes naturelles VS</span><span class="compare-mover-vals">3,7 M (Blatten 2024) → 0 (cause one-shot)</span></div>
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
