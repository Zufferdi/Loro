/* ============================================================
   trajectories.js — Pass 13 (v13.13)
   3-year trajectories (2023→2024→2025) for top beneficiaries.
   Sparklines showing growth/decline/one-shots per beneficiary.
   ============================================================ */
(function() {
  function init() {
    const el = document.getElementById('viz-trajectories');
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
    fetch('data/trajectories_2021_2025.json')
      .then(r => r.json())
      .then(data => doRender(container, data))
      .catch(err => {
        console.error('trajectories fetch fail', err);
        container.innerHTML = '<div style="padding:24px;color:var(--c-loro)">Erreur de chargement.</div>';
      });
  }

  function doRender(container, data) {
    const items = data.beneficiaires || data.trajectories || [];
    const meta = data._meta || {};
    container.innerHTML = '';

    // Stats banner
    const counts = { growth: 0, decline: 0, stable: 0, one_shot_2022: 0, one_shot_2023: 0, one_shot_2024: 0, one_shot_2025: 0 };
    items.forEach(t => { if (counts[t.trajectory_cat] !== undefined) counts[t.trajectory_cat]++; });
    const stats = document.createElement('div');
    stats.className = 'traj-stats';
    stats.innerHTML = `
      <div class="traj-stat"><div class="traj-stat-val">${items.length}</div><div class="traj-stat-lbl">bénéficiaires</div></div>
      <div class="traj-stat"><div class="traj-stat-val">${meta.count_4year || meta.count_3year || 0}</div><div class="traj-stat-lbl">avec 4 années complètes</div></div>
      <div class="traj-stat"><div class="traj-stat-val" style="color:#2a7c2a">${counts.growth + counts.one_shot_2025}</div><div class="traj-stat-lbl">📈 hausses + one-shots&nbsp;2025</div></div>
      <div class="traj-stat"><div class="traj-stat-val" style="color:#b8923a">${counts.one_shot_2024 + counts.one_shot_2023 + counts.one_shot_2022}</div><div class="traj-stat-lbl">⚡ one-shots passés</div></div>
      <div class="traj-stat"><div class="traj-stat-val" style="color:#888">${counts.stable + counts.decline}</div><div class="traj-stat-lbl">→ stables / 📉 baisses</div></div>
    `;
    container.appendChild(stats);

    // Filter controls
    const ctrls = document.createElement('div');
    ctrls.className = 'cross-controls';
    ctrls.innerHTML = `
      <button class="cross-filter is-active" data-filter="all">Tous (${items.length})</button>
      <button class="cross-filter" data-filter="5year">5 années (${meta.count_5year || 0})</button>
      <button class="cross-filter" data-filter="growth">📈 Croissance</button>
      <button class="cross-filter" data-filter="one_shot_2025">⚡ One-shots 2025</button>
      <button class="cross-filter" data-filter="stable">→ Stables</button>
      <button class="cross-filter" data-filter="decline">📉 Baisses</button>
    `;
    container.appendChild(ctrls);

    const grid = document.createElement('div');
    grid.className = 'traj-grid';
    container.appendChild(grid);

    const maxAmt = Math.max(...items.flatMap(t => [
      t.amount_2021 || 0, t.amount_2022 || 0, t.amount_2023 || 0, t.amount_2024 || 0, t.amount_2025 || 0
    ]), 1);

    function matchFilter(t, f) {
      if (f === 'all') return true;
      if (f === '5year') return t.amount_2021 > 0 && t.amount_2022 > 0 && t.amount_2023 > 0 && t.amount_2024 > 0 && t.amount_2025 > 0;
      if (f === '4year') return t.amount_2022 > 0 && t.amount_2023 > 0 && t.amount_2024 > 0 && t.amount_2025 > 0;
      if (f === '3year') return t.amount_2023 > 0 && t.amount_2024 > 0 && t.amount_2025 > 0;
      return t.trajectory_cat === f;
    }

    function buildSparkline(t) {
      // Mini SVG line chart: 5 points
      const w = 130, h = 30, pad = 4;
      const xStep = (w - 2*pad) / 4;
      const points = [
        { x: pad, y: t.amount_2021, lbl: '2021' },
        { x: pad + xStep, y: t.amount_2022, lbl: '2022' },
        { x: pad + 2*xStep, y: t.amount_2023, lbl: '2023' },
        { x: pad + 3*xStep, y: t.amount_2024, lbl: '2024' },
        { x: w - pad, y: t.amount_2025, lbl: '2025' },
      ];
      const validPts = points.filter(p => p.y !== null && p.y !== undefined && p.y > 0);
      if (!validPts.length) return '';
      const localMax = Math.max(...validPts.map(p => p.y), 1);
      const scale = (v) => h - pad - ((v / localMax) * (h - 2 * pad));
      let path = '';
      validPts.forEach((p, i) => {
        const cmd = i === 0 ? 'M' : 'L';
        path += `${cmd}${p.x},${scale(p.y)}`;
      });
      const dots = validPts.map(p => 
        `<circle cx="${p.x}" cy="${scale(p.y)}" r="2.5" fill="var(--c-loro,#c62828)"/>`
      ).join('');
      const ghosts = points.filter(p => !(p.y > 0))
        .map(p => `<circle cx="${p.x}" cy="${h-pad}" r="1.5" fill="#ccc" opacity="0.4"/>`).join('');
      return `
        <svg class="traj-spark" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" preserveAspectRatio="none">
          <path d="${path}" stroke="var(--c-loro,#c62828)" stroke-width="1.5" fill="none"/>
          ${dots}
          ${ghosts}
        </svg>
      `;
    }

    function fmtAmt(v) {
      if (v === null || v === undefined) return '—';
      if (v >= 1e6) return (v/1e6).toFixed(2).replace(/\.?0+$/, '') + ' M';
      if (v >= 1e3) return Math.round(v/1e3) + ' k';
      return String(v);
    }

    function cantonClass(c) { return 'is-' + (c || '').toLowerCase().replace(/[^a-z]/g, ''); }
    function escapeHtml(s) {
      return (s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
    }

    function renderList(f) {
      grid.innerHTML = '';
      const filtered = items.filter(t => matchFilter(t, f));
      if (!filtered.length) {
        grid.innerHTML = '<div style="padding:14px;color:var(--ink-mute);font-style:italic">Aucune trajectoire dans ce filtre.</div>';
        return;
      }
      filtered.forEach(t => {
        const flag = {
          'growth': '📈', 'decline': '📉', 'stable': '→',
          'one_shot_2024': '⚡24', 'one_shot_2025': '⚡25'
        }[t.trajectory_cat] || '→';
        const nSrc = (t.source_entries_2025 || []).length;
        const mergeTag = nSrc > 1 ? `<span class="traj-merge" title="${nSrc} attributions 2025 fusionnées dans cette entité">×${nSrc} fusionnés</span>` : '';
        const row = document.createElement('div');
        row.className = `traj-row is-${t.trajectory_cat}`;
        row.innerHTML = `
          <div class="traj-row-head">
            <span class="treemap-canton ${cantonClass(t.canton)}">${t.canton}</span>
            <span class="traj-name">${escapeHtml(t.nom)}</span>
            ${mergeTag}
            <span class="traj-flag">${flag}</span>
          </div>
          ${t.ville ? `<div class="traj-meta"><span class="traj-ville">📍 ${escapeHtml(t.ville)}</span>${t.sous_theme ? `<span class="traj-sous">${escapeHtml(t.secteur || '')} → ${escapeHtml(t.sous_theme)}</span>` : ''}</div>` : ''}
          <div class="traj-body">
            <div class="traj-values">
              <div class="traj-y"><span class="traj-y-lbl">2021</span><span class="traj-y-val">${fmtAmt(t.amount_2021)}</span></div>
              <div class="traj-y"><span class="traj-y-lbl">2022</span><span class="traj-y-val">${fmtAmt(t.amount_2022)}</span></div>
              <div class="traj-y"><span class="traj-y-lbl">2023</span><span class="traj-y-val">${fmtAmt(t.amount_2023)}</span></div>
              <div class="traj-y"><span class="traj-y-lbl">2024</span><span class="traj-y-val">${fmtAmt(t.amount_2024)}</span></div>
              <div class="traj-y"><span class="traj-y-lbl">2025</span><span class="traj-y-val">${fmtAmt(t.amount_2025)}</span></div>
            </div>
            <div class="traj-spark-wrap">${buildSparkline(t)}</div>
          </div>
          ${t.note_2024 ? `<div class="traj-note">2024&nbsp;: ${escapeHtml(t.note_2024)}</div>` : ''}
        `;
        grid.appendChild(row);
      });
    }

    renderList('all');
    ctrls.querySelectorAll('.cross-filter').forEach(btn => {
      btn.addEventListener('click', () => {
        ctrls.querySelectorAll('.cross-filter').forEach(b => b.classList.remove('is-active'));
        btn.classList.add('is-active');
        renderList(btn.dataset.filter);
      });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
