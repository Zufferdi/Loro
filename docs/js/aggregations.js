/* ============================================================
   aggregations.js — Pass 8 / v13.10 (4 new visualizations)
   ------------------------------------------------------------
   - initTop30Beneficiaires      → #viz-top30
   - initTop20Villes             → #viz-villes
   - initTreemapCantonSecteur    → #viz-treemap
   - initPerCapitaV2             → #viz-percapita
   ============================================================ */
(function() {
  'use strict';

  // ============= Shared utilities =============
  const fmtCHF = v => new Intl.NumberFormat('fr-CH').format(v) + ' CHF';
  const fmtCHFShort = v => {
    if (v >= 1e6) return (v/1e6).toFixed(1).replace(/\.0$/, '') + ' M';
    if (v >= 1e3) return Math.round(v/1e3) + ' k';
    return String(v);
  };
  const cantonClass = c => 'is-' + (c || '').toLowerCase().replace(/[^a-z]/g, '');
  const escapeHtml = s => (s || '').replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));

  // Sector palette (matches existing viz where possible)
  const SECTEUR_COLORS = {
    'Culture':         '#d04a4a',
    'Sport':           '#3a8acc',
    'Action sociale':  '#e08840',
    'Environnement':   '#5aa05a',
    'Santé':           '#a85ab8',
    'Patrimoine':      '#b8923a',
    'Jeunesse':        '#3a9aa8',
    'Formation':       '#7e5ab8',
    'Tourisme':        '#888888',
    'n/a':             '#bbbbbb',
  };

  function lazyInit(id, renderer) {
    const el = document.getElementById(id);
    if (!el) return;
    if ('IntersectionObserver' in window) {
      const obs = new IntersectionObserver(entries => {
        entries.forEach(e => {
          if (e.isIntersecting) {
            renderer(e.target);
            obs.unobserve(e.target);
          }
        });
      }, {rootMargin: '200px'});
      obs.observe(el);
    } else {
      renderer(el);
    }
  }

  function loaderMsg(container) {
    container.innerHTML = '<div style="padding:32px;text-align:center;color:var(--ink-mute);font-style:italic">Chargement…</div>';
  }

  function errMsg(container, msg) {
    container.innerHTML = `<div style="padding:24px;color:var(--c-loro)">${msg}</div>`;
  }

  // ============= Year toggle helpers =============
  const YEAR_TOTALS = { '2024': 155198729, '2025': 207000000 };
  
  function addYearSelector(container, currentYear, renderFn) {
    const sel = document.createElement('div');
    sel.className = 'year-selector';
    sel.style.cssText = 'display:flex;gap:8px;margin-bottom:14px;justify-content:flex-end';
    ['2024', '2025'].forEach(y => {
      const btn = document.createElement('button');
      btn.textContent = y;
      btn.dataset.year = y;
      const active = y === currentYear;
      btn.style.cssText = 'background:' + (active ? 'var(--ink)' : 'transparent') +
        ';border:1px solid ' + (active ? 'var(--ink)' : 'var(--rule)') +
        ';padding:4px 12px;border-radius:14px;cursor:pointer;font-size:13px;' +
        'color:' + (active ? 'white' : 'var(--ink-mute)') + ';font-family:inherit';
      btn.addEventListener('click', () => {
        if (y === currentYear) return;
        container.dataset.loaded = '0';
        renderFn(container, y);
      });
      sel.appendChild(btn);
    });
    container.appendChild(sel);
  }


  // ============= VIZ 1: Top 30 bénéficiaires =============
  function renderTop30(container, year) {
    year = year || '2025';
    if (container.dataset.loaded === '1' && container.dataset.year === year) return;
    container.dataset.loaded = '1';
    container.dataset.year = year;
    loaderMsg(container);
    fetch('data/top30_beneficiaires' + (year === '2024' ? '_2024' : '') + '.json')
      .then(r => r.json())
      .then(data => {
        const benefs = data.beneficiaires || [];
        const meta = data._meta || {};
        const maxAmt = Math.max(...benefs.map(b => b.total_chf), 1);
        container.innerHTML = '';
        addYearSelector(container, year, renderTop30);

        // Banner
        const banner = document.createElement('div');
        banner.className = 'top30-banner';
        banner.innerHTML = `
          <div class="top30-stat">
            <div class="top30-stat-val">${fmtCHF(meta.top30_total_chf || 0)}</div>
            <div class="top30-stat-lbl">cumul top 30 — soit ${meta.top30_pct_of_brb}&nbsp;% du BRB ${year}</div>
          </div>
        `;
        container.appendChild(banner);

        const list = document.createElement('div');
        list.className = 'top30-list';
        benefs.forEach((b, i) => {
          const w = Math.max(2, (b.total_chf / maxAmt) * 100);
          const cantonsHTML = b.cantons.map(c => `<span class="top30-canton ${cantonClass(c)}">${c}</span>`).join('');
          const row = document.createElement('div');
          row.className = 'top30-row';
          row.innerHTML = `
            <div class="top30-rank">${i + 1}</div>
            <div class="top30-body">
              <div class="top30-head">
                <div class="top30-nom">${escapeHtml(b.nom)}${b.is_multi_canton ? '<span class="top30-multi" title="Multi-canton">⇆</span>' : ''}</div>
                <div class="top30-meta">
                  ${b.ville ? `<span class="top30-ville">${escapeHtml(b.ville)}</span>` : ''}
                  <span class="top30-cantons">${cantonsHTML}</span>
                  <span class="top30-secteur">${escapeHtml(b.top_secteur || '')}</span>
                  <span class="top30-amt">${fmtCHF(b.total_chf)}</span>
                </div>
              </div>
              <div class="top30-bar-wrap">
                <div class="top30-bar" style="width:${w}%"></div>
              </div>
              ${b.attributions > 1 ? `<div class="top30-note">${b.attributions} attributions distinctes${b.is_multi_canton ? ` · réparties sur ${b.cantons.length} cantons` : ''}</div>` : ''}
            </div>
          `;
          list.appendChild(row);
        });
        container.appendChild(list);
      })
      .catch(err => { console.error('top30 fail', err); errMsg(container, 'Erreur de chargement.'); });
  }

  // ============= VIZ 2: Top 20 villes =============
  function renderTop20Villes(container, year) {
    year = year || '2025';
    if (container.dataset.loaded === '1' && container.dataset.year === year) return;
    container.dataset.loaded = '1';
    container.dataset.year = year;
    loaderMsg(container);
    fetch('data/top20_villes' + (year === '2024' ? '_2024' : '') + '.json')
      .then(r => r.json())
      .then(data => {
        const villes = data.villes || [];
        const meta = data._meta || {};
        const maxAmt = Math.max(...villes.map(v => v.total_chf), 1);
        container.innerHTML = '';
        addYearSelector(container, year, renderTop20Villes);

        const banner = document.createElement('div');
        banner.className = 'top30-banner';
        banner.innerHTML = `
          <div class="top30-stat">
            <div class="top30-stat-val">${fmtCHF(meta.top20_total_chf || 0)}</div>
            <div class="top30-stat-lbl">cumul top 20 villes — soit ${Math.round(100*meta.top20_total_chf/YEAR_TOTALS[year])}&nbsp;% du BRB ${year}</div>
          </div>
        `;
        container.appendChild(banner);

        const list = document.createElement('div');
        list.className = 'top30-list villes-list';
        villes.forEach((v, i) => {
          const w = Math.max(2, (v.total_chf / maxAmt) * 100);
          const cantonsHTML = v.cantons.filter(Boolean).map(c => `<span class="top30-canton ${cantonClass(c)}">${c}</span>`).join('');
          const row = document.createElement('div');
          row.className = 'top30-row';
          row.innerHTML = `
            <div class="top30-rank">${i + 1}</div>
            <div class="top30-body">
              <div class="top30-head">
                <div class="top30-nom">${escapeHtml(v.ville)}${v.lat ? '<span class="top30-geo" title="Géolocalisée">📍</span>' : ''}</div>
                <div class="top30-meta">
                  <span class="top30-cantons">${cantonsHTML}</span>
                  <span class="top30-secteur">${v.count} attributions</span>
                  <span class="top30-amt">${fmtCHF(v.total_chf)}</span>
                </div>
              </div>
              <div class="top30-bar-wrap">
                <div class="top30-bar" style="width:${w}%;background:linear-gradient(to right,#3a8acc,#5fb0d8)"></div>
              </div>
            </div>
          `;
          list.appendChild(row);
        });
        container.appendChild(list);
      })
      .catch(err => { console.error('top20 villes fail', err); errMsg(container, 'Erreur de chargement.'); });
  }

  // ============= VIZ 3: Treemap canton × secteur =============
  // Implementation: a horizontal stacked-bar grid (one row per canton)
  // because true treemap requires layout algorithm; this is cleaner on mobile.
  function renderTreemap(container, year) {
    year = year || '2025';
    if (container.dataset.loaded === '1' && container.dataset.year === year) return;
    container.dataset.loaded = '1';
    container.dataset.year = year;
    loaderMsg(container);
    fetch('data/treemap_canton_secteur' + (year === '2024' ? '_2024' : '') + '.json')
      .then(r => r.json())
      .then(data => {
        const cantons = data.cantons || [];
        const grandTotal = cantons.reduce((s, c) => s + c.total_chf, 0);
        const maxCantonTotal = Math.max(...cantons.map(c => c.total_chf), 1);
        const cantonLabels = {VD:'Vaud', FR:'Fribourg', VS:'Valais', NE:'Neuchâtel', GE:'Genève', JU:'Jura', R:'Romand intercantonal'};
        container.innerHTML = '';
        addYearSelector(container, year, renderTreemap);

        // Build legend
        const legend = document.createElement('div');
        legend.className = 'treemap-legend';
        const allSecteurs = new Set();
        cantons.forEach(c => c.secteurs.forEach(s => allSecteurs.add(s.secteur)));
        Array.from(allSecteurs).sort().forEach(s => {
          const swatch = document.createElement('span');
          swatch.className = 'treemap-legend-item';
          swatch.innerHTML = `<span class="treemap-swatch" style="background:${SECTEUR_COLORS[s] || '#999'}"></span>${escapeHtml(s)}`;
          legend.appendChild(swatch);
        });
        container.appendChild(legend);

        // Build rows
        const grid = document.createElement('div');
        grid.className = 'treemap-grid';
        cantons.forEach(c => {
          const rowW = (c.total_chf / maxCantonTotal) * 100;
          const row = document.createElement('div');
          row.className = 'treemap-row';
          const segments = c.secteurs.map(s => {
            const pct = (s.total_chf / c.total_chf) * 100;
            const sectorColor = SECTEUR_COLORS[s.secteur] || '#999';
            const top3HTML = s.top_3.slice(0, 3).map(b => `${b.nom.substring(0, 30)} (${fmtCHFShort(b.chf)})`).join(' · ');
            const tooltip = `${s.secteur}: ${fmtCHF(s.total_chf)} (${pct.toFixed(0)}% du canton) · ${s.count} attributions · Top: ${top3HTML}`;
            return `<div class="treemap-seg" style="flex:${s.total_chf};background:${sectorColor}" title="${escapeHtml(tooltip)}">
              ${pct > 8 ? `<span class="treemap-seg-lbl">${escapeHtml(s.secteur)}<br>${fmtCHFShort(s.total_chf)}</span>` : ''}
            </div>`;
          }).join('');
          row.innerHTML = `
            <div class="treemap-row-head">
              <span class="treemap-canton ${cantonClass(c.canton)}">${c.canton}</span>
              <span class="treemap-canton-name">${cantonLabels[c.canton] || c.canton}</span>
              <span class="treemap-canton-total">${fmtCHF(c.total_chf)}</span>
            </div>
            <div class="treemap-bar-wrap" style="width:${rowW}%">
              <div class="treemap-bar">${segments}</div>
            </div>
          `;
          grid.appendChild(row);
        });
        container.appendChild(grid);
      })
      .catch(err => { console.error('treemap fail', err); errMsg(container, 'Erreur de chargement.'); });
  }

  // ============= VIZ 4: Per-capita =============
  function renderPerCapita(container, year) {
    year = year || '2025';
    if (container.dataset.loaded === '1' && container.dataset.year === year) return;
    container.dataset.loaded = '1';
    container.dataset.year = year;
    loaderMsg(container);
    fetch(year === '2024' ? 'data/per_capita_2024.json' : 'data/per_capita_v2.json')
      .then(r => r.json())
      .then(data => {
        const cantons = (data.cantons || []).filter(c => c.population > 0);
        const maxRatio = Math.max(...cantons.map(c => c.chf_per_capita), 1);
        const maxTotal = Math.max(...cantons.map(c => c.total_chf), 1);
        const cantonLabels = {VD:'Vaud', FR:'Fribourg', VS:'Valais', NE:'Neuchâtel', GE:'Genève', JU:'Jura'};
        container.innerHTML = '';
        addYearSelector(container, year, renderPerCapita);

        const grid = document.createElement('div');
        grid.className = 'percap-grid';
        cantons.forEach(c => {
          const wRatio = (c.chf_per_capita / maxRatio) * 100;
          const wTotal = (c.total_chf / maxTotal) * 100;
          const row = document.createElement('div');
          row.className = 'percap-row';
          row.innerHTML = `
            <div class="percap-head">
              <span class="treemap-canton ${cantonClass(c.canton)}">${c.canton}</span>
              <span class="percap-name">${cantonLabels[c.canton] || c.canton}</span>
              <span class="percap-pop">${(c.population/1000).toFixed(0)} k habitants</span>
            </div>
            <div class="percap-twobars">
              <div class="percap-bar-row">
                <div class="percap-bar-lbl">CHF / habitant</div>
                <div class="percap-bar-wrap">
                  <div class="percap-bar percap-bar-ratio" style="width:${wRatio}%"></div>
                </div>
                <div class="percap-bar-val">${c.chf_per_capita.toFixed(1)} CHF</div>
              </div>
              <div class="percap-bar-row">
                <div class="percap-bar-lbl">total absolu</div>
                <div class="percap-bar-wrap">
                  <div class="percap-bar percap-bar-total" style="width:${wTotal}%"></div>
                </div>
                <div class="percap-bar-val">${fmtCHFShort(c.total_chf)}</div>
              </div>
            </div>
          `;
          grid.appendChild(row);
        });
        container.appendChild(grid);
      })
      .catch(err => { console.error('percap fail', err); errMsg(container, 'Erreur de chargement.'); });
  }

  // ============= Init =============
  function init() {
    lazyInit('viz-top30', renderTop30);
    lazyInit('viz-villes', renderTop20Villes);
    lazyInit('viz-canton-secteur', renderTreemap);
    lazyInit('viz-percapita', renderPerCapita);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
