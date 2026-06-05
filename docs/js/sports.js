/* ============================================================
   initBrbSports() — sport classification chart
   ------------------------------------------------------------
   Horizontal bars showing top sports by total CHF + counts.
   Click a sport to reveal sample beneficiaries.
   ============================================================ */
(function() {
  function init() {
    const el = document.getElementById('viz-sports');
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

  function render(container, year) {
    year = year || '2025';
    if (container.dataset.loaded === '1' && container.dataset.year === year) return;
    container.dataset.loaded = '1';
    container.dataset.year = year;

    container.innerHTML = '<div style="padding:32px;text-align:center;color:var(--ink-mute);font-style:italic">Chargement…</div>';

    // Précharge toutes les années pour calcul de delta
    const years = window.YEARS || ['2022', '2023', '2024', '2025'];
    Promise.all(years.map(y =>
      fetch('data/sports_classification' + window.yearSuffix(y) + '.json')
        .then(r => r.json()).catch(() => null)
    )).then(allData => {
      const yearIdx = years.indexOf(year);
      const data = allData[yearIdx];
      // "other" = année précédente si dispo, sinon suivante (pour deltas)
      const otherIdx = (yearIdx > 0) ? yearIdx - 1 : yearIdx + 1;
      const other = (otherIdx >= 0 && otherIdx < allData.length) ? allData[otherIdx] : null;
      const otherYear = (otherIdx >= 0 && otherIdx < years.length) ? years[otherIdx] : null;
      if (!data) throw new Error('no data for ' + year);
      doRender(container, data, year, other, otherYear);
    }).catch(err => {
      console.error('sports.js fetch failed', err);
      container.innerHTML = '<div style="padding:24px;color:var(--c-loro)">Erreur de chargement.</div>';
    });
  }

  function doRender(container, data, year, other, otherYear) {
    const sports = data.sports || [];
    const meta = data._meta || {};
    const maxAmount = Math.max(...sports.map(s => s.total_chf), 1);

    container.innerHTML = '';
    addYearSelector(container, year, render);

    // Top stats banner
    const stats = document.createElement('div');
    stats.className = 'sports-stats';
    stats.innerHTML = `
      <div class="sports-stat">
        <div class="sports-stat-val">${(meta.total_chf_classified || 0).toLocaleString('fr-CH').replace(/,/g, "'")} CHF</div>
        <div class="sports-stat-lbl">total identifié comme sport (${meta.pct_chf_precisely_classified}% du secteur)</div>
      </div>
      <div class="sports-stat">
        <div class="sports-stat-val">${meta.total_entries_classified || 0}</div>
        <div class="sports-stat-lbl">attributions sur ${sports.length} disciplines</div>
      </div>
    `;
    container.appendChild(stats);

    // Bars list
    const list = document.createElement('div');
    list.className = 'sports-list';

    sports.forEach((s, idx) => {
      const row = document.createElement('div');
      row.className = 'sports-row';
      row.dataset.idx = idx;

      const barWidth = Math.max(2, (s.total_chf / maxAmount) * 100);
      const meanFmt = fmtCHFShort(s.mean_chf);

      // Top cantons (top 3 by amount within sport)
      const topCantons = Object.entries(s.cantons)
        .sort((a, b) => b[1].total_chf - a[1].total_chf)
        .slice(0, 4)
        .map(([c, d]) => `<span class="sports-canton ${cantonClass(c)}">${c}</span>`)
        .join('');

      row.innerHTML = `
        <div class="sports-row-head">
          <div class="sports-name">${s.name}</div>
          <div class="sports-meta">
            <span class="sports-count">${s.count} attributions</span>
            <span class="sports-cantons">${topCantons}</span>
            <span class="sports-mean">${meanFmt} moy.</span>
            <span class="sports-total">${fmtCHF(s.total_chf)}</span>${(() => {
                if (!other) return '';
                const o = findOtherCat(other, s.name);
                if (!o) return '<span class="sports-delta sports-delta-new" title="Nouveau en ' + year + '">nouveau</span>';
                const delta = s.total_chf - o.total_chf;
                const d = fmtDelta(delta);
                if (!d) return '';
                const cls = delta > 0 ? 'sports-delta-up' : 'sports-delta-down';
                return '<span class="sports-delta ' + cls + '" title="vs ' + (otherYear || '?') + ': ' + fmtCHF(o.total_chf) + '">' + d + '</span>';
              })()}
          </div>
        </div>
        <div class="sports-bar-wrap">
          <div class="sports-bar" style="width:${barWidth}%"></div>
        </div>
        <div class="sports-samples" style="display:none">
          <div class="sports-samples-title">Tous les bénéficiaires (${s.count}) — triés par montant :</div>
          <input type="text" class="samples-search" placeholder="🔎 Filtrer par nom, ville…" />
          <div class="sports-samples-list"></div>
        </div>
      `;

      // Click to toggle samples + lazy render full list
      const entries = s.all_entries || s.samples || [];
      let rendered = false;
      row.querySelector('.sports-row-head').addEventListener('click', () => {
        const wrap = row.querySelector('.sports-samples');
        const open = wrap.style.display !== 'none';
        wrap.style.display = open ? 'none' : 'block';
        row.classList.toggle('is-open', !open);
        if (!open && !rendered) {
          rendered = true;
          const listEl = wrap.querySelector('.sports-samples-list');
          listEl.innerHTML = entries.map(x => `
            <div class="sports-sample">
              <span class="sports-sample-nom">${escapeHtml(x.nom)}</span>
              ${x.ville ? `<span class="sports-sample-ville">${escapeHtml(x.ville)}</span>` : ''}
              <span class="sports-sample-amt">${fmtCHF(x.montant_CHF)}</span>
              <span class="sports-sample-c ${cantonClass(x.canton)}">${x.canton}</span>
            </div>
          `).join('');
          // Wire up text search
          const searchEl = wrap.querySelector('.samples-search');
          const items = wrap.querySelectorAll('.sports-sample');
          searchEl.addEventListener('input', () => {
            const q = searchEl.value.trim().toLowerCase();
            items.forEach(it => {
              const txt = it.textContent.toLowerCase();
              it.classList.toggle('is-hidden', q && !txt.includes(q));
            });
          });
        }
      });

      list.appendChild(row);
    });

    container.appendChild(list);
  }

  function fmtCHF(v) {
    return new Intl.NumberFormat('fr-CH').format(v) + ' CHF';
  }
  function fmtCHFShort(v) {
    if (v >= 1e6) return (v/1e6).toFixed(1).replace(/\.0$/, '') + ' M';
    if (v >= 1e3) return Math.round(v/1e3) + ' k';
    return String(v);
  }
  function cantonClass(c) {
    return 'is-' + (c || '').toLowerCase().replace(/[^a-z]/g, '');
  }
  function escapeHtml(s) {
    return (s || '').replace(/[&<>"']/g, c => ({
      '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
    })[c]);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
