/* ============================================================
   cas_dependance.js — viz dédiée
   ------------------------------------------------------------
   Pour chaque organisation, ratio subvention Loro / budget total.
   L'angle éditorial : « ce que Loro représente pour eux ».

   Charge data/cas_dependance.json en lazy via IntersectionObserver.
   ============================================================ */
(function () {
  'use strict';

  function init() {
    const el = document.getElementById('viz-cas-dependance');
    if (!el) return;
    if ('IntersectionObserver' in window) {
      const obs = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            render(e.target);
            obs.unobserve(e.target);
          }
        });
      }, { rootMargin: '200px' });
      obs.observe(el);
    } else {
      render(el);
    }
  }

  function render(container) {
    if (container.dataset.loaded === '1') return;
    container.dataset.loaded = '1';
    container.innerHTML =
      '<div style="padding:32px;text-align:center;color:var(--ink-mute);font-style:italic">Chargement…</div>';

    fetch('data/cas_dependance.json')
      .then((r) => {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then((data) => doRender(container, data))
      .catch((err) => {
        console.error('cas_dependance fetch fail', err);
        container.innerHTML =
          '<div style="padding:24px;color:var(--c-loro)">Erreur de chargement des cas de dépendance.</div>';
      });
  }

  function doRender(container, data) {
    const cases = (data.cases || []).slice();
    container.innerHTML = '';

    // Header : stats résumé
    const documented = cases.filter((c) => c.confidence === 'documenté').length;
    const estim = cases.filter((c) => c.confidence === 'estim.').length;
    const avgPct =
      cases
        .filter((c) => c.part_loro_pct != null && c.part_loro_label !== 'exceptionnel')
        .reduce((s, c) => s + c.part_loro_pct, 0) /
      Math.max(
        1,
        cases.filter((c) => c.part_loro_pct != null && c.part_loro_label !== 'exceptionnel').length
      );

    const stats = document.createElement('div');
    stats.className = 'dep-stats';
    stats.innerHTML = `
      <div class="dep-stat">
        <div class="dep-stat-val">${cases.length}</div>
        <div class="dep-stat-lbl">cas analysés</div>
      </div>
      <div class="dep-stat">
        <div class="dep-stat-val" style="color:#2a7c2a">${documented}</div>
        <div class="dep-stat-lbl">documentés</div>
      </div>
      <div class="dep-stat">
        <div class="dep-stat-val" style="color:#b8860b">${estim}</div>
        <div class="dep-stat-lbl">estimations</div>
      </div>
      <div class="dep-stat">
        <div class="dep-stat-val">${Math.round(avgPct)}<small style="font-size:0.5em">%</small></div>
        <div class="dep-stat-lbl">part Loro moyenne</div>
      </div>
    `;
    container.appendChild(stats);

    // Contrôles : tri
    const ctrls = document.createElement('div');
    ctrls.className = 'dep-controls';
    ctrls.innerHTML = `
      <span class="dep-ctrl-label">Trier par&nbsp;:</span>
      <button class="dep-sort is-active" data-sort="pct">% dépendance</button>
      <button class="dep-sort" data-sort="loro">Montant Loro</button>
      <button class="dep-sort" data-sort="budget">Budget total</button>
      <button class="dep-sort" data-sort="canton">Canton</button>
    `;
    container.appendChild(ctrls);

    // Conteneur graph
    const graph = document.createElement('div');
    graph.className = 'dep-graph';
    container.appendChild(graph);

    // Footer méthode
    const foot = document.createElement('div');
    foot.className = 'dep-foot';
    foot.innerHTML = `
      <div class="dep-legend">
        <span class="dep-legend-item"><span class="dep-swatch dep-swatch-documented"></span> Documenté (rapport d'activité ou citation directe)</span>
        <span class="dep-legend-item"><span class="dep-swatch dep-swatch-estim"></span> Estimation (budget non publié intégralement)</span>
      </div>
      <p class="dep-method">
        ${escapeHtml(data._meta && data._meta.limites ? data._meta.limites : '')}
      </p>
    `;
    container.appendChild(foot);

    // Sorting helpers
    const sortFns = {
      pct: (a, b) => (b.part_loro_pct || 0) - (a.part_loro_pct || 0),
      loro: (a, b) => (b.subvention_loro_CHF || 0) - (a.subvention_loro_CHF || 0),
      budget: (a, b) => (b.budget_total_CHF || 0) - (a.budget_total_CHF || 0),
      canton: (a, b) => (a.canton || '').localeCompare(b.canton || ''),
    };

    // Initial render
    renderList(graph, cases, 'pct', sortFns);

    // Sort buttons
    ctrls.querySelectorAll('.dep-sort').forEach((btn) => {
      btn.addEventListener('click', () => {
        ctrls.querySelectorAll('.dep-sort').forEach((b) => b.classList.remove('is-active'));
        btn.classList.add('is-active');
        renderList(graph, cases, btn.dataset.sort, sortFns);
      });
    });
  }

  function renderList(graph, cases, sortKey, sortFns) {
    const sorted = cases.slice().sort(sortFns[sortKey]);
    // Échelle : on prend max 100% (les cas "exceptionnels" sont à 100%, les autres en-dessous)
    const maxPct = 100;
    graph.innerHTML = '';

    sorted.forEach((c, i) => {
      const row = document.createElement('div');
      row.className = 'dep-row';
      // Classe selon confiance
      if (c.confidence === 'documenté') row.classList.add('is-documented');
      else if (c.confidence === 'estim.') row.classList.add('is-estim');

      const pct = c.part_loro_pct || 0;
      const w = Math.min(100, (pct / maxPct) * 100);
      const isExceptionnel = c.part_loro_label === 'exceptionnel';

      row.innerHTML = `
        <div class="dep-head">
          <span class="dep-rank">${i + 1}</span>
          <div class="dep-name-wrap">
            <div class="dep-name">${escapeHtml(c.nom)}</div>
            <div class="dep-meta">
              <span class="dep-canton ${cantonClass(c.canton)}">${escapeHtml(c.canton || '?')}</span>
              <span class="dep-cat">${escapeHtml(c.categorie || '')}</span>
              ${c.ville && c.ville !== '—' ? `<span class="dep-ville">${escapeHtml(c.ville)}</span>` : ''}
            </div>
          </div>
          <div class="dep-pct">
            ${isExceptionnel ? '<span class="dep-pct-excep">exceptionnel</span>' : pct + '<small>%</small>'}
          </div>
        </div>
        <div class="dep-bar-wrap">
          <div class="dep-bar ${isExceptionnel ? 'is-exceptionnel' : ''}"
               style="width:${w}%" aria-hidden="true"></div>
          <div class="dep-bar-track"></div>
        </div>
        <div class="dep-amounts">
          <span><strong>${fmtCHF(c.subvention_loro_CHF)}</strong> Loro ${c.year ? '(' + c.year + ')' : ''}</span>
          <span class="dep-sep">·</span>
          <span>sur <strong>${fmtCHF(c.budget_total_CHF)}</strong> de budget</span>
        </div>
        ${c.context ? `<div class="dep-context">${escapeHtml(c.context)}</div>` : ''}
        ${c.source ? `<div class="dep-source">Source : ${escapeHtml(c.source)}</div>` : ''}
        ${c.note_editorial ? `<div class="dep-note">💡 ${escapeHtml(c.note_editorial)}</div>` : ''}
      `;
      graph.appendChild(row);
    });
  }

  // ---- helpers ----
  function fmtCHF(v) {
    if (v == null) return '—';
    if (v >= 1e6) return (v / 1e6).toFixed(v >= 10e6 ? 0 : 1).replace(/\.0$/, '') + ' M';
    if (v >= 1e3) return Math.round(v / 1e3) + ' k';
    return String(v);
  }
  function cantonClass(c) {
    return 'is-' + (c || '').toLowerCase().replace(/[^a-z]/g, '');
  }
  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
