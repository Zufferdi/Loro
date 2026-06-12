/* explorer.js — Page d'exploration des 120 bénéficiaires nommés
   Fonctionnalités : recherche floue, filtres par catégorie et canton, tri,
   sparkline annuelle pour chaque résultat. */

let BENEFS = [];
let state = {
  search: '',
  categories: new Set(),
  cantons: new Set(),
  sort: 'total-desc',
};

document.addEventListener('DOMContentLoaded', async () => {
  BENEFS = await loadJSON('beneficiaires.json');
  initFilters();
  bindEvents();
  render();
});

function initFilters() {
  const cats = Array.from(new Set(BENEFS.map(b => b.categorie))).sort();
  const cBox = document.getElementById('filter-categories');
  cats.forEach(c => {
    const cnt = BENEFS.filter(b => b.categorie === c).length;
    const id = 'cat_' + c.replace(/\W+/g, '_');
    const lbl = document.createElement('label');
    lbl.innerHTML = `
      <input type="checkbox" data-cat="${escapeHtml(c)}" id="${id}">
      <span>${escapeHtml(c)}</span>
      <span style="color:var(--ink-mute); margin-left:auto;">${cnt}</span>`;
    cBox.appendChild(lbl);
  });
  cBox.querySelectorAll('input').forEach(inp => {
    inp.addEventListener('change', () => {
      const v = inp.dataset.cat;
      if (inp.checked) state.categories.add(v); else state.categories.delete(v);
      render();
    });
  });

  const cantons = Array.from(new Set(BENEFS.map(b => b.canton).filter(Boolean))).sort();
  const ctBox = document.getElementById('filter-cantons');
  cantons.forEach(c => {
    const cnt = BENEFS.filter(b => b.canton === c).length;
    const lbl = document.createElement('label');
    lbl.innerHTML = `
      <input type="checkbox" data-canton="${escapeHtml(c)}">
      <span>${escapeHtml(c)}</span>
      <span style="color:var(--ink-mute); margin-left:auto;">${cnt}</span>`;
    ctBox.appendChild(lbl);
  });
  ctBox.querySelectorAll('input').forEach(inp => {
    inp.addEventListener('change', () => {
      const v = inp.dataset.canton;
      if (inp.checked) state.cantons.add(v); else state.cantons.delete(v);
      render();
    });
  });
}

function bindEvents() {
  const s = document.getElementById('search');
  s.addEventListener('input', debounce(() => { state.search = s.value.trim().toLowerCase(); render(); }, 150));
  document.getElementById('sort').addEventListener('change', e => { state.sort = e.target.value; render(); });
  document.getElementById('reset').addEventListener('click', () => {
    state = { search: '', categories: new Set(), cantons: new Set(), sort: 'total-desc' };
    document.getElementById('search').value = '';
    document.getElementById('sort').value = 'total-desc';
    document.querySelectorAll('.explorer-filters input').forEach(i => i.checked = false);
    render();
  });
}

function filterAndSort() {
  let out = BENEFS.slice();
  if (state.search) {
    out = out.filter(b => (b.nom || '').toLowerCase().includes(state.search)
                       || (b.categorie || '').toLowerCase().includes(state.search)
                       || (b.canton || '').toLowerCase().includes(state.search));
  }
  if (state.categories.size) out = out.filter(b => state.categories.has(b.categorie));
  if (state.cantons.size)    out = out.filter(b => state.cantons.has(b.canton));

  const latestKey = b => {
    const keys = b.series ? Object.keys(b.series) : [];
    return keys.length ? keys.sort().pop() : '0';
  };
  const sorters = {
    'total-desc': (a, b) => (b.total || 0) - (a.total || 0),
    'total-asc':  (a, b) => (a.total || 0) - (b.total || 0),
    'alpha':      (a, b) => (a.nom || '').localeCompare(b.nom || ''),
    'latest':     (a, b) => latestKey(b).localeCompare(latestKey(a)),
  };
  out.sort(sorters[state.sort] || sorters['total-desc']);
  return out;
}

function render() {
  const list = filterAndSort();
  const meta = document.getElementById('meta');
  const sum = list.reduce((s, b) => s + b.total, 0);
  meta.innerHTML = `<strong>${list.length}</strong> bénéficiaire${list.length>1?'s':''} affiché${list.length>1?'s':''} · <strong>${fmtCompact(sum)} CHF</strong> cumulés`;

  const box = document.getElementById('results');
  box.innerHTML = '';

  if (!list.length) {
    box.innerHTML = `<div class="note" style="text-align:center; padding:40px;">Aucun résultat. Essayez d'élargir vos filtres.</div>`;
    return;
  }

  const frag = document.createDocumentFragment();
  list.slice(0, 200).forEach(b => frag.appendChild(renderCard(b)));
  box.appendChild(frag);

  if (list.length > 200) {
    const more = document.createElement('div');
    more.className = 'note';
    more.style.textAlign = 'center';
    more.style.padding = '24px';
    more.textContent = `… ${list.length - 200} bénéficiaires supplémentaires (affinez les filtres).`;
    box.appendChild(more);
  }
}

function renderCard(b) {
  const card = document.createElement('div');
  card.className = 'b-card';

  const left = document.createElement('div');
  left.innerHTML = `
    <div class="name">${escapeHtml(b.nom)}</div>
    <div class="meta">
      ${escapeHtml(b.categorie || '—')}
      ${b.canton ? ' · ' + escapeHtml(b.canton) : ''}
      ${b.sous_categorie ? ' · ' + escapeHtml(b.sous_categorie) : ''}
    </div>`;
  card.appendChild(left);

  // spark
  const spark = document.createElement('div');
  spark.className = 'spark';
  spark.appendChild(buildSpark(b));
  card.appendChild(spark);

  // total
  const tot = document.createElement('div');
  tot.className = 'total';
  tot.innerHTML = `${fmtCompact(b.total)} <span class="unit">CHF cumulés</span>`;
  card.appendChild(tot);

  return card;
}

function buildSpark(b) {
  const years = Object.keys(b.series).map(Number).sort((a, b) => a - b);
  const vals  = years.map(y => b.series[y]);
  const allYears = d3.range(2013, 2026);
  const padded = allYears.map(y => ({ y, v: b.series[String(y)] || 0 }));

  const w = 240, h = 36;
  const sv = d3.create('svg').attr('viewBox', `0 0 ${w} ${h}`).attr('width', '100%').attr('height', h);
  const x = d3.scaleLinear().domain([2013, 2025]).range([4, w - 4]);
  const y = d3.scaleLinear().domain([0, d3.max(padded, d => d.v) || 1]).range([h - 4, 4]);

  // baseline
  sv.append('line').attr('x1', 4).attr('x2', w - 4).attr('y1', h - 4).attr('y2', h - 4)
    .attr('stroke', 'var(--rule)').attr('stroke-dasharray', '2,2');

  sv.append('path').datum(padded)
    .attr('fill', 'none').attr('stroke', '#c8102e').attr('stroke-width', 1.5)
    .attr('d', d3.line().x(d => x(d.y)).y(d => y(d.v)));

  // bars sous la courbe (subtil)
  sv.selectAll('rect').data(padded.filter(d => d.v > 0)).enter().append('rect')
    .attr('x', d => x(d.y) - 1).attr('y', d => y(d.v))
    .attr('width', 2).attr('height', d => h - 4 - y(d.v))
    .attr('fill', '#c8102e').attr('opacity', 0.4);

  // dernier point
  const last = padded.filter(d => d.v > 0).slice(-1)[0];
  if (last) {
    sv.append('circle').attr('cx', x(last.y)).attr('cy', y(last.v))
      .attr('r', 2.5).attr('fill', '#c8102e');
  }

  // tooltip
  const bandW = (w - 8) / allYears.length;
  sv.selectAll('rect.hit').data(padded).enter().append('rect').attr('class', 'hit')
    .attr('x', d => x(d.y) - bandW / 2).attr('y', 0)
    .attr('width', bandW).attr('height', h)
    .attr('fill', 'transparent')
    .on('mouseover', (ev, d) => {
      const html = `<div class="t-title">${d.y}</div><div>${d.v ? fmtCompact(d.v) + ' CHF' : '— pas de subvention'}</div>`;
      showTip(html, ev.clientX, ev.clientY);
    }).on('mouseout', hideTip);

  return sv.node();
}

// escapeHtml est exposé globalement par utils.js

