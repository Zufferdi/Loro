/* ============================================================
   find_org.js — recherche "Trouvez votre organisation"
   ------------------------------------------------------------
   Recherche full-text sur 12 363 organisations dédupliquées
   (BRB 2021-2025). Lazy load de l'index (~2 MB) au premier focus,
   filtrage par substring sur la clé canonique normalisée.
   ============================================================ */
(function () {
  'use strict';

  // ---- état module ----
  let INDEX = null;             // { _meta, orgs: [...] }
  let indexLoadPromise = null;  // singleton de la promesse de chargement
  let currentResults = [];
  let activeResultIdx = -1;     // index dans currentResults pour navigation clavier

  // ---- helpers ----
  function normalizeQuery(q) {
    // Même normalisation que le builder Python
    return String(q || '')
      .toLowerCase()
      .normalize('NFKD').replace(/[\u0300-\u036f]/g, '')  // désaccenter
      .replace(/[^a-z0-9]+/g, ' ')
      .trim();
  }

  function fmtCHF(v) {
    if (v == null || v === 0) return '—';
    if (v >= 1e6) return (v / 1e6).toFixed(v >= 10e6 ? 0 : 2).replace(/\.?0+$/, '') + ' M';
    if (v >= 1e3) return Math.round(v / 1e3) + ' k';
    return String(v);
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[c]));
  }

  function cantonClass(c) {
    return 'is-' + (c || '').toLowerCase().replace(/[^a-z]/g, '');
  }

  // ---- chargement de l'index (lazy, singleton) ----
  function loadIndex() {
    if (INDEX) return Promise.resolve(INDEX);
    if (indexLoadPromise) return indexLoadPromise;
    indexLoadPromise = fetch('data/search_index.json')
      .then(r => {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(d => { INDEX = d; return d; })
      .catch(err => {
        indexLoadPromise = null;
        throw err;
      });
    return indexLoadPromise;
  }

  // ---- recherche : retourne top N orgs matchant la requête ----
  function search(query, limit) {
    if (!INDEX) return [];
    const nq = normalizeQuery(query);
    if (!nq || nq.length < 2) return [];

    const terms = nq.split(' ').filter(t => t.length >= 2);
    if (!terms.length) return [];

    const out = [];
    for (const org of INDEX.orgs) {
      // Tous les termes doivent matcher dans la clé canonique
      let matched = true;
      for (const t of terms) {
        if (!org.k.includes(t)) { matched = false; break; }
      }
      if (matched) {
        // Score : préfère les matches en début de mot et les orgs avec gros total
        let score = org.t || 0;
        if (org.k.startsWith(nq)) score *= 100;
        else if (org.k.includes(' ' + nq)) score *= 50;
        out.push({ org, score });
      }
    }
    out.sort((a, b) => b.score - a.score);
    return out.slice(0, limit || 10).map(x => x.org);
  }

  // ---- init UI ----
  function init() {
    const root = document.getElementById('viz-find-org');
    if (!root) return;
    renderShell(root);
  }

  function renderShell(root) {
    root.innerHTML = `
      <div class="findorg-wrap">
        <div class="findorg-search">
          <span class="findorg-icon" aria-hidden="true">🔍</span>
          <input
            type="search"
            id="findorg-input"
            class="findorg-input"
            placeholder="Ex&nbsp;: Verbier, Cinéforom, Lanterne magique, Pro Senectute…"
            aria-label="Rechercher une organisation"
            aria-autocomplete="list"
            aria-controls="findorg-results"
            autocomplete="off"
            spellcheck="false">
          <button type="button" class="findorg-clear" id="findorg-clear" aria-label="Effacer la recherche" hidden>✕</button>
        </div>
        <div class="findorg-status" id="findorg-status" role="status" aria-live="polite"></div>
        <ul class="findorg-results" id="findorg-results" role="listbox" aria-label="Résultats de recherche" hidden></ul>
        <div class="findorg-detail" id="findorg-detail" hidden></div>
        <div class="findorg-hint" id="findorg-hint">
          12&nbsp;363 organisations distinctes sur 5 ans (2021-2025). Tapez les premières lettres&nbsp;: la recherche démarre à 2 caractères.
        </div>
      </div>
    `;

    const input = root.querySelector('#findorg-input');
    const clearBtn = root.querySelector('#findorg-clear');
    const status = root.querySelector('#findorg-status');
    const resultsEl = root.querySelector('#findorg-results');
    const detailEl = root.querySelector('#findorg-detail');
    const hintEl = root.querySelector('#findorg-hint');

    // Premier focus déclenche le load
    let firstFocus = true;
    input.addEventListener('focus', () => {
      if (firstFocus) {
        firstFocus = false;
        status.textContent = 'Chargement de l\'index…';
        loadIndex()
          .then(d => {
            status.textContent = '';
            // Si l'utilisateur a déjà tapé pendant le chargement
            if (input.value) doSearch();
          })
          .catch(err => {
            status.innerHTML = '<span style="color:var(--c-loro)">Erreur de chargement de l\'index. Réessaie ou recharge la page.</span>';
            console.error('find_org index load', err);
          });
      }
    });

    // Debounce 80ms (tap-tap-tap fluide)
    let debounceTimer = null;
    function doSearch() {
      const q = input.value;
      clearBtn.hidden = !q;
      if (!q || q.length < 2) {
        currentResults = [];
        resultsEl.hidden = true;
        resultsEl.innerHTML = '';
        activeResultIdx = -1;
        hintEl.hidden = false;
        return;
      }
      if (!INDEX) {
        // Le chargement n'est pas fini. On attend.
        return;
      }
      hintEl.hidden = true;
      currentResults = search(q, 10);
      renderResults(resultsEl, currentResults, q);
      activeResultIdx = -1;
    }
    input.addEventListener('input', () => {
      if (debounceTimer) clearTimeout(debounceTimer);
      debounceTimer = setTimeout(doSearch, 80);
    });

    // Navigation clavier dans les résultats
    input.addEventListener('keydown', (e) => {
      if (resultsEl.hidden || !currentResults.length) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeResultIdx = Math.min(activeResultIdx + 1, currentResults.length - 1);
        updateActiveResult(resultsEl);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeResultIdx = Math.max(activeResultIdx - 1, 0);
        updateActiveResult(resultsEl);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (activeResultIdx >= 0 && activeResultIdx < currentResults.length) {
          showDetail(detailEl, currentResults[activeResultIdx]);
          resultsEl.hidden = true;
        } else if (currentResults.length === 1) {
          showDetail(detailEl, currentResults[0]);
          resultsEl.hidden = true;
        }
      } else if (e.key === 'Escape') {
        resultsEl.hidden = true;
        activeResultIdx = -1;
      }
    });

    // Click sur résultat
    resultsEl.addEventListener('click', (e) => {
      const li = e.target.closest('[data-org-key]');
      if (!li) return;
      const key = li.dataset.orgKey;
      const org = currentResults.find(o => o.k === key);
      if (org) {
        showDetail(detailEl, org);
        resultsEl.hidden = true;
      }
    });

    // Click ailleurs : ferme résultats
    document.addEventListener('click', (e) => {
      if (!root.contains(e.target)) {
        resultsEl.hidden = true;
      }
    });

    // Bouton clear
    clearBtn.addEventListener('click', () => {
      input.value = '';
      doSearch();
      input.focus();
    });
  }

  function updateActiveResult(resultsEl) {
    resultsEl.querySelectorAll('.findorg-result').forEach((el, i) => {
      el.classList.toggle('is-active', i === activeResultIdx);
      if (i === activeResultIdx) el.scrollIntoView({ block: 'nearest' });
    });
  }

  function highlightMatch(name, query) {
    // Mettre en gras les portions du nom qui matchent les termes de la requête
    const nq = normalizeQuery(query);
    if (!nq) return escapeHtml(name);
    const terms = nq.split(' ').filter(t => t.length >= 2);
    if (!terms.length) return escapeHtml(name);
    let html = escapeHtml(name);
    // Pour chaque terme, surligner dans le nom (case-insensitive, accent-insensitive est complexe en JS — on fait simple : matcher en regex i)
    for (const t of terms) {
      // Échapper les regex specials du terme
      const escaped = t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      try {
        const re = new RegExp('(' + escaped + ')', 'gi');
        html = html.replace(re, '<mark>$1</mark>');
      } catch (e) { /* skip */ }
    }
    return html;
  }

  function renderResults(resultsEl, orgs, query) {
    if (!orgs.length) {
      resultsEl.innerHTML =
        '<li class="findorg-noresult">Aucune organisation trouvée. Essaie avec moins de mots, ou un nom plus court (« verbier » plutôt que « verbier festival academy »).</li>';
      resultsEl.hidden = false;
      return;
    }
    resultsEl.innerHTML = orgs.map((o, i) => {
      const cantonsHtml = o.c.map(c =>
        `<span class="findorg-canton ${cantonClass(c)}">${escapeHtml(c)}</span>`
      ).join('');
      return `
        <li class="findorg-result" data-org-key="${escapeHtml(o.k)}" tabindex="-1" role="option">
          <div class="findorg-result-main">
            <div class="findorg-result-name">${highlightMatch(o.n, query)}</div>
            <div class="findorg-result-meta">
              ${cantonsHtml}
              <span class="findorg-result-sector">${escapeHtml(o.s)}</span>
              <span class="findorg-result-presence">${o.p} an${o.p > 1 ? 's' : ''}</span>
            </div>
          </div>
          <div class="findorg-result-amount">
            <div class="findorg-result-total">${fmtCHF(o.t)}</div>
            <div class="findorg-result-lbl">cumul 5 ans</div>
          </div>
        </li>
      `;
    }).join('');
    resultsEl.hidden = false;
  }

  function showDetail(detailEl, org) {
    const YEARS = ['2021', '2022', '2023', '2024', '2025'];
    const maxA = Math.max(...YEARS.map(y => org.a[y] || 0), 1);

    // Sparkline SVG
    const svgW = 280, svgH = 60;
    const pad = 4;
    const usableW = svgW - pad * 2, usableH = svgH - pad * 2 - 14;
    const pts = YEARS.map((y, i) => {
      const v = org.a[y] || 0;
      const x = pad + (usableW * i / (YEARS.length - 1));
      const yPos = pad + (usableH - (v / maxA) * usableH);
      return { x, y: yPos, v, year: y };
    });
    const pathD = pts.map((p, i) => (i === 0 ? 'M' : 'L') + p.x + ',' + p.y).join(' ');

    const cantonsHtml = org.c.map(c =>
      `<span class="findorg-canton ${cantonClass(c)}">${escapeHtml(c)}</span>`
    ).join('');

    // Calcul tendance 2021 → 2025
    const a21 = org.a['2021'] || 0;
    const a25 = org.a['2025'] || 0;
    let trendStr = '';
    if (a21 > 0 && a25 > 0) {
      const delta = Math.round(((a25 - a21) / a21) * 100);
      trendStr = (delta >= 0 ? '+' : '') + delta + '% sur 5 ans';
    } else if (a21 === 0 && a25 > 0) {
      trendStr = 'nouvelle (apparue ≥ 2022)';
    } else if (a21 > 0 && a25 === 0) {
      trendStr = 'disparue (présente jusqu\'à ≤ 2024)';
    } else if (org.p === 1) {
      trendStr = 'one-shot (une seule année)';
    }

    detailEl.innerHTML = `
      <div class="findorg-detail-head">
        <div>
          <div class="findorg-detail-name">${escapeHtml(org.n)}</div>
          <div class="findorg-detail-meta">
            ${cantonsHtml}
            <span class="findorg-detail-sector">${escapeHtml(org.s)}</span>
            ${trendStr ? '<span class="findorg-detail-trend">' + escapeHtml(trendStr) + '</span>' : ''}
          </div>
        </div>
        <div class="findorg-detail-total">
          <div class="findorg-detail-total-val">${fmtCHF(org.t)}</div>
          <div class="findorg-detail-total-lbl">cumul ${org.p > 1 ? '5 ans' : ''}</div>
        </div>
      </div>

      <div class="findorg-detail-spark">
        <svg viewBox="0 0 ${svgW} ${svgH}" width="100%" preserveAspectRatio="none" role="img" aria-label="Évolution 2021-2025 pour ${escapeHtml(org.n)}">
          <path d="${pathD}" fill="none" stroke="var(--c-loro)" stroke-width="2" stroke-linejoin="round"/>
          ${pts.map(p => `<circle cx="${p.x}" cy="${p.y}" r="${p.v === 0 ? 2 : 3}" fill="${p.v === 0 ? 'var(--ink-mute)' : 'var(--c-loro)'}"><title>${p.year}: ${fmtCHF(p.v)}</title></circle>`).join('')}
        </svg>
      </div>

      <div class="findorg-detail-grid">
        ${YEARS.map(y => `
          <div class="findorg-detail-year">
            <div class="findorg-detail-year-lbl">${y}</div>
            <div class="findorg-detail-year-val ${(org.a[y] || 0) === 0 ? 'is-zero' : ''}">${fmtCHF(org.a[y] || 0)}</div>
          </div>
        `).join('')}
      </div>

      <div class="findorg-detail-info">
        <span><strong>${org.na}</strong> attribution${org.na > 1 ? 's' : ''} distincte${org.na > 1 ? 's' : ''}</span>
        <span class="findorg-sep">·</span>
        <span>Présent <strong>${org.p}/5</strong> année${org.p > 1 ? 's' : ''}</span>
        <span class="findorg-sep">·</span>
        <span>Secteur principal&nbsp;: <strong>${escapeHtml(org.s)}</strong></span>
      </div>

      <div class="findorg-detail-foot">
        <button type="button" class="findorg-detail-back">← Nouvelle recherche</button>
        <a class="findorg-detail-explorer" href="#acte-9">Explorer plus de bénéficiaires ↘</a>
      </div>
    `;
    detailEl.hidden = false;

    const backBtn = detailEl.querySelector('.findorg-detail-back');
    backBtn.addEventListener('click', () => {
      detailEl.hidden = true;
      const input = document.getElementById('findorg-input');
      if (input) { input.value = ''; input.focus(); }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
