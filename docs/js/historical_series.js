/* ============================================================
   initBrbHistoricalSeries() — small multiples chart
   ------------------------------------------------------------
   15 bénéficiaires "piliers" sur 4 années (2022, 2023, 2024, 2025).
   Source : BRB officiels Loterie Romande (extraction manuelle).
   ============================================================ */
(function() {
  function initBrbHistoricalSeries() {
    const container = document.getElementById('viz-historical-series');
    if (!container) return;
    if (container.dataset.loaded === '1') return;
    container.dataset.loaded = '1';

    container.innerHTML = '<div style="padding:32px;text-align:center;color:var(--ink-mute);font-style:italic">Chargement de la série historique…</div>';

    fetch('data/beneficiaires_series_2022_2025.json')
      .then(r => r.json())
      .then(data => render(container, data))
      .catch(err => {
        console.error('Failed to load series', err);
        container.innerHTML = '<div style="padding:24px;color:var(--c-loro)">Erreur de chargement de la série historique.</div>';
      });
  }

  function render(container, data) {
    const cands = data.candidats || [];
    const years = [2022, 2023, 2024, 2025];

    // Sort by 2025 desc
    const sorted = cands.slice().sort((a, b) => (b.series['2025'] || 0) - (a.series['2025'] || 0));

    // Compute max across all cells for global y-scale option
    container.innerHTML = '';

    // Wrap
    const grid = document.createElement('div');
    grid.className = 'hist-series-grid';

    sorted.forEach(c => {
      const card = document.createElement('div');
      card.className = 'hist-series-card';

      // Header
      const head = document.createElement('div');
      head.className = 'hist-series-head';
      const name = c.nom_canonique
        .replace(/^Fondation\s+/, 'Fond. ')
        .replace(/^Festival International du Film de Fribourg \(FIFF\)/, 'FIFF Fribourg')
        .replace(/\s*\(.+\)$/, '');
      head.innerHTML = `<div class="hist-series-name">${name}</div>
                       <div class="hist-series-meta">${c.canton_principal} · ${c.secteur}</div>`;
      card.appendChild(head);

      // Mini chart: series of bars per year
      const chart = document.createElement('div');
      chart.className = 'hist-series-chart';

      // Find max for this candidate
      const values = years.map(y => c.series[String(y)] || c.series[y]);
      const localMax = Math.max(...values.filter(v => v != null), 1);

      years.forEach((y, i) => {
        const v = c.series[String(y)] !== undefined ? c.series[String(y)] : c.series[y];
        const col = document.createElement('div');
        col.className = 'hist-series-col';
        if (v == null) {
          col.classList.add('is-empty');
          col.innerHTML = `<div class="hist-series-bar hist-series-bar-empty" title="Donnée non extraite pour ${y}">—</div>
                           <div class="hist-series-yr">${y}</div>`;
        } else {
          const h = Math.max(2, Math.round(80 * v / localMax)); // 2px min
          col.innerHTML = `<div class="hist-series-bar" style="height:${h}px" title="${y}: ${fmtCHF(v)}"></div>
                           <div class="hist-series-val">${fmtCHFShort(v)}</div>
                           <div class="hist-series-yr">${y}</div>`;
        }
        chart.appendChild(col);
      });

      card.appendChild(chart);
      grid.appendChild(card);
    });

    container.appendChild(grid);
  }

  function fmtCHF(v) {
    return new Intl.NumberFormat('fr-CH').format(v) + ' CHF';
  }
  function fmtCHFShort(v) {
    if (v >= 1e6) return (v/1e6).toFixed(2).replace(/\.?0+$/, '') + ' M';
    if (v >= 1e3) return Math.round(v/1e3) + ' k';
    return String(v);
  }

  // Trigger on page load + on intersection observer
  function init() {
    const el = document.getElementById('viz-historical-series');
    if (!el) return;
    if ('IntersectionObserver' in window) {
      const obs = new IntersectionObserver(entries => {
        entries.forEach(e => { if (e.isIntersecting) { initBrbHistoricalSeries(); obs.unobserve(e.target); }});
      }, {rootMargin: '200px'});
      obs.observe(el);
    } else {
      initBrbHistoricalSeries();
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
