/* ============================================================
   marquants_50.js — Top 50 bénéficiaires marquants 2021-2025
   Trajectoire 5 ans + texte éditorial + citation + source
   ============================================================ */
(function() {
  function init() {
    const el = document.getElementById('viz-marquants-50');
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
    container.innerHTML = '<div style="padding:32px;text-align:center;color:var(--ink-mute);font-style:italic">Chargement des 50 marquants…</div>';
    fetch('data/marquants_2021_2025_top50.json')
      .then(r => r.json())
      .then(data => doRender(container, data))
      .catch(err => {
        console.error('marquants_50 fetch fail', err);
        container.innerHTML = '<div style="padding:24px;color:var(--c-loro)">Erreur de chargement.</div>';
      });
  }

  const fmt = n => {
    if (n == null) return '—';
    if (n === 0) return '—';
    if (n >= 1e6) return (n / 1e6).toFixed(2) + ' M';
    if (n >= 1e3) return Math.round(n / 1e3) + ' k';
    return String(n);
  };

  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  // Filtre les URLs : autorise http(s) et chemins relatifs, rejette javascript: / data: / etc.
  function safeUrl(u) {
    if (!u) return '';
    const s = String(u).trim();
    if (/^(https?:|\/|\.\/|\.\.\/)/i.test(s)) return s;
    return '';
  }

  function makeSparkline(amts, w, h) {
    const max = Math.max(...amts.filter(x => x > 0), 1);
    const n = amts.length;
    const pts = amts.map((v, i) => {
      const x = (i / (n - 1)) * w;
      const y = h - (v / max) * (h - 4) - 2;
      return [x, y, v];
    });
    const linePath = pts.filter(p => p[2] > 0).map((p, i) => `${i === 0 ? 'M' : 'L'} ${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
    const dots = pts.map((p, i) => {
      const isZero = p[2] === 0;
      const fill = isZero ? '#ccc' : (i === n - 1 ? '#c8102e' : '#555');
      const r = isZero ? 1.5 : (i === n - 1 ? 3 : 2);
      return `<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="${r}" fill="${fill}"/>`;
    }).join('');
    return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="overflow:visible">
      <path d="${linePath}" fill="none" stroke="#888" stroke-width="1.2"/>
      ${dots}
    </svg>`;
  }

  function doRender(container, data) {
    const items = data.marquants || [];
    container.innerHTML = '';

    // Stats banner
    const stats = document.createElement('div');
    stats.className = 'traj-stats';
    const withEdit = items.filter(m => m.editorial).length;
    stats.innerHTML = `
      <div class="traj-stat"><div class="traj-stat-val">${items.length}</div><div class="traj-stat-lbl">bénéficiaires marquants</div></div>
      <div class="traj-stat"><div class="traj-stat-val">${withEdit}</div><div class="traj-stat-lbl">avec citation / source</div></div>
      <div class="traj-stat"><div class="traj-stat-val">${items.filter(m => m.is_consolidated).length}</div><div class="traj-stat-lbl">⊕ noms consolidés</div></div>
      <div class="traj-stat"><div class="traj-stat-val">${(items.reduce((s, m) => s + m.total_cumul, 0) / 1e6).toFixed(0)} M</div><div class="traj-stat-lbl">CHF cumulés 5 ans</div></div>
    `;
    container.appendChild(stats);

    // Filter controls
    const ctrls = document.createElement('div');
    ctrls.className = 'cross-controls';
    ctrls.innerHTML = `
      <button class="cross-filter is-active" data-filter="all">Tous (${items.length})</button>
      <button class="cross-filter" data-filter="with_editorial">✦ Avec citation (${withEdit})</button>
      <button class="cross-filter" data-filter="consolidated">⊕ Consolidés (${items.filter(m => m.is_consolidated).length})</button>
    `;
    container.appendChild(ctrls);

    const list = document.createElement('div');
    list.className = 'marquants-list';
    list.style.cssText = 'display:flex; flex-direction:column; gap:6px;';
    container.appendChild(list);

    function renderItems(filter) {
      let filtered = items;
      if (filter === 'with_editorial') filtered = items.filter(m => m.editorial);
      else if (filter === 'consolidated') filtered = items.filter(m => m.is_consolidated);
      
      list.innerHTML = '';
      filtered.forEach((m, idx) => {
        const row = document.createElement('div');
        row.className = 'marquant-row';
        row.style.cssText = `display:grid; grid-template-columns: 38px minmax(0,1fr) 110px 70px 60px 60px 70px 60px 60px 110px; align-items:center; gap:8px; padding:8px 10px; background:var(--bg-soft); border-radius:6px; cursor:${m.editorial ? 'pointer' : 'default'}; transition:background 0.15s;`;
        
        const mark = m.editorial ? '<span style="color:var(--c-loro); font-weight:bold">✦</span>' : (m.is_consolidated ? '<span style="color:#888">⊕</span>' : '');
        const cantons = (m.cantons || []).join(' ');
        
        row.innerHTML = `
          <div style="font-size:12px; color:var(--ink-mute); text-align:right">${idx + 1}.</div>
          <div>
            <div style="font-weight:600; font-size:13px; color:var(--ink); display:flex; align-items:center; gap:6px">${mark} ${escapeHtml(m.nom)}</div>
            <div style="font-size:11px; color:var(--ink-mute); margin-top:2px">${escapeHtml(m.secteur || '')} · ${escapeHtml(cantons)}</div>
          </div>
          <div style="font-size:12px; color:var(--ink); font-weight:600">${fmt(m.total_cumul)} <span style="color:var(--ink-mute); font-weight:normal">/${m.count_cumul}×</span></div>
          <div style="font-size:11px; color:var(--ink-mute); text-align:right">${fmt(m.amount_2021)}</div>
          <div style="font-size:11px; color:var(--ink-mute); text-align:right">${fmt(m.amount_2022)}</div>
          <div style="font-size:11px; color:var(--ink-mute); text-align:right">${fmt(m.amount_2023)}</div>
          <div style="font-size:11px; color:var(--ink-mute); text-align:right">${fmt(m.amount_2024)}</div>
          <div style="font-size:11px; color:var(--ink); text-align:right; font-weight:600">${fmt(m.amount_2025)}</div>
          <div></div>
          <div>${makeSparkline([m.amount_2021, m.amount_2022, m.amount_2023, m.amount_2024, m.amount_2025], 90, 24)}</div>
        `;
        
        if (m.editorial) {
          row.addEventListener('mouseenter', () => { row.style.background = 'var(--bg-soft-hover, rgba(200,16,46,0.06))'; });
          row.addEventListener('mouseleave', () => { row.style.background = 'var(--bg-soft)'; });
          row.addEventListener('click', () => toggleDetails(row, m));
        }
        list.appendChild(row);
      });
      
      // Header
      const header = document.createElement('div');
      header.style.cssText = 'display:grid; grid-template-columns: 38px minmax(0,1fr) 110px 70px 60px 60px 70px 60px 60px 110px; align-items:center; gap:8px; padding:4px 10px; font-size:10px; color:var(--ink-mute); letter-spacing:0.05em; text-transform:uppercase; border-bottom:1px solid var(--rule);';
      header.innerHTML = `
        <div></div><div>Bénéficiaire</div>
        <div>5 ans</div>
        <div style="text-align:right">2021</div>
        <div style="text-align:right">2022</div>
        <div style="text-align:right">2023</div>
        <div style="text-align:right">2024</div>
        <div style="text-align:right">2025</div>
        <div></div>
        <div>Trajectoire</div>
      `;
      list.insertBefore(header, list.firstChild);
    }

    function toggleDetails(row, m) {
      const existing = row.nextElementSibling;
      if (existing && existing.classList.contains('marquant-details')) {
        existing.remove();
        return;
      }
      // remove other open details
      document.querySelectorAll('.marquant-details').forEach(e => e.remove());
      
      const det = document.createElement('div');
      det.className = 'marquant-details';
      det.style.cssText = 'padding:16px 18px; background:var(--bg); border-left:4px solid var(--c-loro); margin:2px 0 8px 0; border-radius:0 6px 6px 0;';
      const ed = m.editorial;
      const safeCitationUrl = safeUrl(ed.citation_url);
      det.innerHTML = `
        <div style="font-weight:600; font-size:14px; color:var(--ink); margin-bottom:4px">${escapeHtml(ed.titre_court)}</div>
        <p style="margin:0 0 10px 0; font-size:13px; color:var(--ink); line-height:1.5">${escapeHtml(ed.texte)}</p>
        <blockquote style="border-left:3px solid var(--c-loro); padding:8px 14px; margin:10px 0; font-style:italic; font-family:'Source Serif Pro',serif; font-size:14px; color:var(--ink)">
          ${escapeHtml(ed.citation)}
          <footer style="font-size:11px; color:var(--ink-mute); margin-top:4px; font-style:normal">— <strong>${escapeHtml(ed.citation_source)}</strong>${ed.citation_date ? ' · ' + escapeHtml(ed.citation_date) : ''}${safeCitationUrl ? ' · <a href="' + escapeHtml(safeCitationUrl) + '" target="_blank" rel="noopener" style="color:var(--c-loro)">source ↗</a>' : ''}</footer>
        </blockquote>
      `;
      row.insertAdjacentElement('afterend', det);
    }

    renderItems('all');

    // Filter handlers
    ctrls.querySelectorAll('button').forEach(btn => {
      btn.addEventListener('click', () => {
        ctrls.querySelectorAll('button').forEach(b => b.classList.remove('is-active'));
        btn.classList.add('is-active');
        renderItems(btn.dataset.filter);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
