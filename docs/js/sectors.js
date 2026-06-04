/* ============================================================
   sectors.js — Generic sector classification viz
   ------------------------------------------------------------
   Auto-attaches to any element matching `[data-sector]`.
   The element ID is conventionally `viz-{slug}`, e.g.
     <div id="viz-environnement" data-sector="environnement"></div>

   Reads JSON from data/{slug}_classification.json (2025)
   and data/{slug}_classification_2024.json (2024), then renders
   a chart visually identical to sports.js / culture.js / social.js,
   with year toggle and cross-year deltas.

   Supported slugs (must match build_sectors_classification.py):
     environnement, sante, jeunesse, patrimoine, formation, promotion
   ============================================================ */
(function () {
  'use strict';

  // Optional human-readable labels per slug (used in stats line).
  const SECTOR_LABEL = {
    environnement: { noun: 'environnement', adj: "comme environnement" },
    sante:         { noun: 'santé & handicap', adj: "comme santé / handicap" },
    jeunesse:      { noun: 'jeunesse & éducation', adj: "comme jeunesse / éducation" },
    patrimoine:    { noun: 'patrimoine', adj: "comme conservation du patrimoine" },
    formation:     { noun: 'formation & recherche', adj: "comme formation / recherche" },
    promotion:     { noun: 'promotion & tourisme', adj: "comme promotion / tourisme" },
  };

  function init() {
    const targets = document.querySelectorAll('[data-sector]');
    if (!targets.length) return;
    targets.forEach(el => {
      if ('IntersectionObserver' in window) {
        const obs = new IntersectionObserver(entries => {
          entries.forEach(e => {
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
    });
  }

  function render(container, year) {
    const slug = container.dataset.sector;
    if (!slug) return;
    year = year || '2025';
    if (container.dataset.loaded === '1' && container.dataset.year === year) return;
    container.dataset.loaded = '1';
    container.dataset.year = year;
    container.innerHTML = '<div style="padding:32px;text-align:center;color:var(--ink-mute);font-style:italic">Chargement…</div>';

    Promise.all((window.YEARS || ['2024', '2025']).map(y =>
      fetch('data/' + slug + '_classification' + window.yearSuffix(y) + '.json')
        .then(r => r.json()).catch(() => null)
    )).then(allData => {
      const years = window.YEARS || ['2024', '2025'];
      const yearIdx = years.indexOf(year);
      const data = allData[yearIdx];
      const otherIdx = (yearIdx > 0) ? yearIdx - 1 : yearIdx + 1;
      const other = (otherIdx >= 0 && otherIdx < allData.length) ? allData[otherIdx] : null;
      const otherYear = (otherIdx >= 0 && otherIdx < years.length) ? years[otherIdx] : null;
      if (!data) throw new Error('no data for ' + year + ' (slug=' + slug + ')');
      doRender(container, data, year, other, slug, otherYear);
    }).catch(err => {
      console.error('sectors.js fetch failed (slug=' + slug + ')', err);
      container.innerHTML = '<div style="padding:24px;color:var(--c-loro)">Erreur de chargement.</div>';
    });
  }

  function doRender(container, data, year, other, slug, otherYear) {
    const cats = data.categories || [];
    const meta = data._meta || {};
    const label = SECTOR_LABEL[slug] || { noun: slug, adj: 'dans ce secteur' };
    const maxAmount = Math.max(...cats.map(c => c.total_chf), 1);

    container.innerHTML = '';
    addYearSelector(container, year, render);

    // Reuse the sports-list visual variant (mauve/violet) — works fine across sectors
    container.classList.add('sports-list-culture');

    const stats = document.createElement('div');
    stats.className = 'sports-stats';
    stats.innerHTML =
      '<div class="sports-stat">' +
        '<div class="sports-stat-val">' +
          (meta.total_chf_classified || 0).toLocaleString('fr-CH').replace(/,/g, "'") + ' CHF' +
        '</div>' +
        '<div class="sports-stat-lbl">total identifié ' + label.adj +
        ' (' + meta.pct_chf_classified + '% du secteur)</div>' +
      '</div>' +
      '<div class="sports-stat">' +
        '<div class="sports-stat-val">' + (meta.total_entries_classified || 0) + '</div>' +
        '<div class="sports-stat-lbl">attributions sur ' + cats.length +
        ' sous-catégorie' + (cats.length > 1 ? 's' : '') + '</div>' +
      '</div>';
    container.appendChild(stats);

    const list = document.createElement('div');
    list.className = 'sports-list';
    cats.forEach(s => {
      const row = document.createElement('div');
      row.className = 'sports-row';
      const barWidth = Math.max(2, (s.total_chf / maxAmount) * 100);
      const meanFmt = fmtCHFShort(s.mean_chf);
      const topCantons = Object.entries(s.cantons)
        .sort((a, b) => b[1].total_chf - a[1].total_chf)
        .slice(0, 4)
        .map(([c]) => '<span class="sports-canton ' + cantonClass(c) + '">' + (c || '?') + '</span>')
        .join('');

      let deltaHtml = '';
      if (other) {
        const o = findOtherCat(other, s.name);
        if (!o) {
          deltaHtml = '<span class="sports-delta sports-delta-new" title="Nouveau en ' + year + '">nouveau</span>';
        } else {
          const delta = s.total_chf - o.total_chf;
          const d = fmtDelta(delta);
          if (d) {
            const cls = delta > 0 ? 'sports-delta-up' : 'sports-delta-down';
            deltaHtml = '<span class="sports-delta ' + cls +
              '" title="vs ' + (otherYear || '?') + ': ' + fmtCHF(o.total_chf) + '">' + d + '</span>';
          }
        }
      }

      row.innerHTML =
        '<div class="sports-row-head">' +
          '<div class="sports-name">' + escapeHtml(s.name) + '</div>' +
          '<div class="sports-meta">' +
            '<span class="sports-count">' + s.count + ' attributions</span>' +
            '<span class="sports-cantons">' + topCantons + '</span>' +
            '<span class="sports-mean">' + meanFmt + ' moy.</span>' +
            '<span class="sports-total">' + fmtCHF(s.total_chf) + '</span>' +
            deltaHtml +
          '</div>' +
        '</div>' +
        '<div class="sports-bar-wrap">' +
          '<div class="sports-bar sports-bar-culture" style="width:' + barWidth + '%"></div>' +
        '</div>' +
        '<div class="sports-samples" style="display:none">' +
          '<div class="sports-samples-title">Tous les bénéficiaires (' + s.count + ') — triés par montant :</div>' +
          '<input type="text" class="samples-search" placeholder="🔎 Filtrer par nom, ville…" />' +
          '<div class="sports-samples-list"></div>' +
        '</div>';

      const entries = s.all_entries || s.samples || [];
      let rendered = false;
      row.querySelector('.sports-row-head').addEventListener('click', () => {
        const wrap = row.querySelector('.sports-samples');
        const open = wrap.style.display !== 'none';
        wrap.style.display = open ? 'none' : 'block';
        row.classList.toggle('is-open', !open);
        if (!open && !rendered) {
          rendered = true;
          wrap.querySelector('.sports-samples-list').innerHTML = entries.map(x =>
            '<div class="sports-sample">' +
              '<span class="sports-sample-nom">' + escapeHtml(x.nom) + '</span>' +
              (x.ville ? '<span class="sports-sample-ville">' + escapeHtml(x.ville) + '</span>' : '') +
              '<span class="sports-sample-amt">' + fmtCHF(x.montant_CHF) + '</span>' +
              '<span class="sports-sample-c ' + cantonClass(x.canton) + '">' + (x.canton || '?') + '</span>' +
            '</div>'
          ).join('');
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

  // ── Helpers ──────────────────────────────────────────────────
  function findOtherCat(other, name) {
    if (!other || !other.categories) return null;
    return other.categories.find(c => c.name === name) || null;
  }
  function fmtCHF(v) { return new Intl.NumberFormat('fr-CH').format(v) + ' CHF'; }
  function fmtCHFShort(v) {
    if (v >= 1e6) return (v / 1e6).toFixed(1).replace(/\.0$/, '') + ' M';
    if (v >= 1e3) return Math.round(v / 1e3) + ' k';
    return String(v);
  }
  function fmtDelta(d) {
    if (!d || Math.abs(d) < 1000) return '';
    const sign = d > 0 ? '+' : '−';
    return sign + fmtCHFShort(Math.abs(d));
  }
  function cantonClass(c) { return 'is-' + (c || '').toLowerCase().replace(/[^a-z]/g, ''); }
  function escapeHtml(s) {
    return (s || '').replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[c]);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
