/* ============================================================
   beneficiaires_cumul.js — Pass 14 (v13.14)
   Top bénéficiaires cumulés 2022-2025 avec drill-down détaillé
   au clic. Affiche toutes les attributions de chaque entité,
   triées par année et montant (ex: Tour de Romandie = 34 attributions).
   ============================================================ */
(function() {
  function init() {
    const el = document.getElementById('viz-cumul-multi');
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
    fetch('data/beneficiaires_cumul_2022_2025.json')
      .then(r => r.json())
      .then(data => doRender(container, data))
      .catch(err => {
        console.error('cumul fetch fail', err);
        container.innerHTML = '<div style="padding:24px;color:var(--c-loro)">Erreur de chargement.</div>';
      });
  }

  function doRender(container, data) {
    const benefs = data.beneficiaires || [];
    const meta = data._meta || {};
    container.innerHTML = '';

    // State : filtre + recherche + topN
    const state = {
      filter: 'all',
      search: '',
      topN: 50,
    };

    // ─── Stats banner ───
    const stats = document.createElement('div');
    stats.className = 'sports-stats';
    stats.style.cssText = 'display:flex;gap:24px;margin-bottom:18px;padding:16px;background:var(--bg-mute,#f7f5ee);border-radius:8px';
    stats.innerHTML = `
      <div class="sports-stat">
        <div class="sports-stat-val">${benefs.length.toLocaleString('fr-CH').replace(/,/g, "'")}</div>
        <div class="sports-stat-lbl">bénéficiaires top 200 (cumulés 4 ans)</div>
      </div>
      <div class="sports-stat">
        <div class="sports-stat-val">${(meta.total_in_top200 / 1e6).toFixed(0)} M CHF</div>
        <div class="sports-stat-lbl">soit ${meta.top200_pct_of_4y}% du total redistribué 2022-2025</div>
      </div>
      <div class="sports-stat">
        <div class="sports-stat-val">${meta.total_beneficiaires_distincts.toLocaleString('fr-CH').replace(/,/g, "'")}</div>
        <div class="sports-stat-lbl">bénéficiaires distincts (≥2 attributions)</div>
      </div>
    `;
    container.appendChild(stats);

    // ─── Contrôles : recherche + filtre + topN ───
    const ctrls = document.createElement('div');
    ctrls.className = 'cumul-ctrls';
    ctrls.style.cssText = 'display:flex;gap:12px;margin-bottom:18px;flex-wrap:wrap;align-items:center';
    ctrls.innerHTML = `
      <input type="text" class="cumul-search" placeholder="🔎 Rechercher (ex : Tour de Romandie, Orchestre…)" 
             style="flex:1;min-width:200px;padding:8px 12px;border:1px solid var(--rule);border-radius:18px;font-size:13px;font-family:inherit;background:transparent;color:var(--ink)">
      <div class="cumul-filters" style="display:flex;gap:6px;flex-wrap:wrap">
        <button class="cumul-filter is-active" data-filter="all">Tous</button>
        <button class="cumul-filter" data-filter="4y">4 années</button>
        <button class="cumul-filter" data-filter="3y">≥ 3 années</button>
        <button class="cumul-filter" data-filter="growth">📈 Croissance</button>
        <button class="cumul-filter" data-filter="multi-cantonal">🔀 Multi-cantonal</button>
      </div>
      <select class="cumul-topn" style="padding:6px 10px;border:1px solid var(--rule);border-radius:18px;font-size:13px;background:transparent;color:var(--ink);font-family:inherit">
        <option value="20">Top 20</option>
        <option value="50" selected>Top 50</option>
        <option value="100">Top 100</option>
        <option value="200">Top 200</option>
      </select>
    `;
    container.appendChild(ctrls);

    const list = document.createElement('div');
    list.className = 'cumul-list';
    list.style.cssText = 'display:flex;flex-direction:column;gap:8px';
    container.appendChild(list);

    function matchFilter(b, f) {
      if (f === 'all') return true;
      if (f === '4y') return b.nb_years_active === 4;
      if (f === '3y') return b.nb_years_active >= 3;
      if (f === 'multi-cantonal') return b.cantons.length >= 2;
      if (f === 'growth') {
        const a22 = b.totaux_par_an['2022'] || 0;
        const a25 = b.totaux_par_an['2025'] || 0;
        return a25 > a22 * 1.5;
      }
      return true;
    }
    function matchSearch(b, q) {
      if (!q) return true;
      const ql = q.toLowerCase();
      if (b.nom_canonique.toLowerCase().includes(ql)) return true;
      if (b.noms_originaux.some(n => n.toLowerCase().includes(ql))) return true;
      if (b.villes.some(v => v && v.toLowerCase().includes(ql))) return true;
      return false;
    }

    function fmtCHF(v) {
      if (v >= 1e6) return (v/1e6).toFixed(2).replace(/\.?0+$/, '') + ' M';
      if (v >= 1e3) return Math.round(v/1e3) + ' k';
      return String(v);
    }
    function escapeHtml(s) {
      return (s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
    }
    function cantonClass(c) { return 'is-' + (c || '').toLowerCase().replace(/[^a-z]/g, ''); }

    function renderList() {
      list.innerHTML = '';
      const filtered = benefs
        .filter(b => matchFilter(b, state.filter))
        .filter(b => matchSearch(b, state.search))
        .slice(0, state.topN);

      if (!filtered.length) {
        list.innerHTML = '<div style="padding:14px;color:var(--ink-mute);font-style:italic">Aucun bénéficiaire ne correspond.</div>';
        return;
      }

      const maxCumul = Math.max(...filtered.map(b => b.total_cumul), 1);

      filtered.forEach((b, idx) => {
        const cantonChips = b.cantons.map(c =>
          `<span class="treemap-canton ${cantonClass(c)}">${c}</span>`).join(' ');
        const yearChips = ['2022','2023','2024','2025'].map(y => {
          const v = b.totaux_par_an[y] || 0;
          const dim = v === 0 ? 'opacity:0.25' : '';
          return `<span style="font-size:11px;padding:2px 7px;border:1px solid var(--rule);border-radius:10px;${dim}">${y}: ${v === 0 ? '—' : fmtCHF(v)}</span>`;
        }).join(' ');

        const row = document.createElement('div');
        row.className = 'cumul-row';
        row.style.cssText = 'border:1px solid var(--rule);border-radius:8px;overflow:hidden;background:var(--bg,#fff)';
        const w = (b.total_cumul / maxCumul) * 100;
        row.innerHTML = `
          <div class="cumul-head" style="padding:12px 14px;cursor:pointer;display:flex;align-items:center;gap:12px;flex-wrap:wrap">
            <span class="cumul-rank" style="font-family:'Source Serif Pro',serif;font-size:13px;color:var(--ink-mute);min-width:28px">#${idx+1}</span>
            ${cantonChips}
            <span class="cumul-name" style="flex:1;font-family:'Source Serif Pro',serif;font-size:15px;font-weight:500;color:var(--ink)">${escapeHtml(b.nom_canonique)}</span>
            <span class="cumul-count" style="font-size:11.5px;color:var(--ink-mute)">${b.count_cumul} attr.</span>
            <span class="cumul-years" style="font-size:11.5px;color:var(--ink-mute)">${b.nb_years_active} ans</span>
            <span class="cumul-total" style="font-family:'Source Serif Pro',serif;font-weight:600;color:var(--c-loro,#c8102e);font-size:15px;min-width:75px;text-align:right">${fmtCHF(b.total_cumul)}</span>
            <span class="cumul-expand" style="font-size:13px;color:var(--ink-mute);width:14px;text-align:center">▸</span>
          </div>
          <div class="cumul-bar-row" style="padding:0 14px 8px 14px">
            <div style="height:4px;background:var(--rule);border-radius:2px;overflow:hidden">
              <div style="height:100%;width:${w}%;background:var(--c-loro,#c8102e);opacity:0.85"></div>
            </div>
          </div>
          <div class="cumul-meta" style="padding:0 14px 10px 14px;display:flex;gap:6px;flex-wrap:wrap;font-size:11px;color:var(--ink-mute)">
            ${yearChips}
            <span style="font-size:11px;color:var(--ink-mute);margin-left:8px">·</span>
            <span style="font-size:11px;color:var(--ink-mute);font-style:italic">${escapeHtml(b.secteur_principal || '–')}</span>
            ${b.villes.length ? `<span style="font-size:11px;color:var(--ink-mute);margin-left:8px">📍 ${b.villes.slice(0,3).map(escapeHtml).join(', ')}${b.villes.length > 3 ? ` +${b.villes.length-3}` : ''}</span>` : ''}
          </div>
          <div class="cumul-detail" style="display:none;border-top:1px solid var(--rule);padding:14px;background:var(--bg-mute,#f7f5ee)">
            <div style="font-size:12px;font-weight:600;color:var(--ink);margin-bottom:10px">Détail des ${b.count_cumul} attributions</div>
            <div class="cumul-attribs"></div>
          </div>
        `;
        list.appendChild(row);

        // Click handler — toggle detail
        const head = row.querySelector('.cumul-head');
        const detail = row.querySelector('.cumul-detail');
        const expand = row.querySelector('.cumul-expand');
        let opened = false;
        head.addEventListener('click', () => {
          opened = !opened;
          detail.style.display = opened ? 'block' : 'none';
          expand.textContent = opened ? '▾' : '▸';
          if (opened) {
            // Lazy-render the attribs
            const wrap = row.querySelector('.cumul-attribs');
            if (!wrap.dataset.rendered) {
              wrap.dataset.rendered = '1';
              // Grouper par année
              const byYear = {};
              b.attributions_detail.forEach(a => {
                (byYear[a.annee] = byYear[a.annee] || []).push(a);
              });
              const html = Object.keys(byYear).sort().map(year => `
                <div style="margin-bottom:12px">
                  <div style="font-family:'Source Serif Pro',serif;font-size:12.5px;font-weight:600;color:var(--c-loro);margin-bottom:6px">${year} — ${byYear[year].length} attribution(s) · ${fmtCHF(byYear[year].reduce((s, a) => s + a.montant_CHF, 0))} CHF</div>
                  <div style="display:flex;flex-direction:column;gap:4px">
                    ${byYear[year].map(a => `
                      <div style="display:flex;gap:10px;align-items:flex-start;font-size:12px;padding:5px 8px;background:var(--bg,#fff);border-radius:4px">
                        <span style="color:var(--ink-mute);min-width:30px">${a.canton}</span>
                        <div style="flex:1">
                          <div style="color:var(--ink)">${escapeHtml(a.nom)}</div>
                          ${a.description ? `<div style="color:var(--ink-mute);font-size:11px;font-style:italic;margin-top:1px">› ${escapeHtml(a.description)}</div>` : ''}
                          ${a.ville ? `<div style="color:var(--ink-mute);font-size:11px;margin-top:1px">📍 ${escapeHtml(a.ville)}</div>` : ''}
                        </div>
                        <span style="font-family:'Source Serif Pro',serif;font-weight:600;color:var(--ink);min-width:80px;text-align:right">${fmtCHF(a.montant_CHF)}</span>
                      </div>
                    `).join('')}
                  </div>
                </div>
              `).join('');
              wrap.innerHTML = html;
            }
          }
        });
      });
    }

    // Wire up search
    const searchInput = ctrls.querySelector('.cumul-search');
    let searchTimer;
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        state.search = searchInput.value;
        renderList();
      }, 200);
    });

    // Wire up filters
    ctrls.querySelectorAll('.cumul-filter').forEach(btn => {
      btn.style.cssText = 'padding:4px 12px;border:1px solid var(--rule);border-radius:14px;background:transparent;color:var(--ink-mute);cursor:pointer;font-size:12.5px;font-family:inherit';
      btn.addEventListener('click', () => {
        ctrls.querySelectorAll('.cumul-filter').forEach(b => {
          b.classList.remove('is-active');
          b.style.background = 'transparent';
          b.style.color = 'var(--ink-mute)';
          b.style.borderColor = 'var(--rule)';
        });
        btn.classList.add('is-active');
        btn.style.background = 'var(--ink)';
        btn.style.color = 'white';
        btn.style.borderColor = 'var(--ink)';
        state.filter = btn.dataset.filter;
        renderList();
      });
    });
    // Set initial active state styling
    const activeFilter = ctrls.querySelector('.cumul-filter.is-active');
    if (activeFilter) {
      activeFilter.style.background = 'var(--ink)';
      activeFilter.style.color = 'white';
      activeFilter.style.borderColor = 'var(--ink)';
    }

    // Wire up topN
    ctrls.querySelector('.cumul-topn').addEventListener('change', (ev) => {
      state.topN = parseInt(ev.target.value);
      renderList();
    });

    renderList();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
