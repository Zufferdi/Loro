/* =============================================================
   app.js — orchestration des visualisations de la page d'accueil
   Toutes les vis sont écrites en D3 v7 vanilla.
   ============================================================= */

let DATA = {};
let activeYear = 2024;

document.addEventListener('DOMContentLoaded', async () => {
  try {
    DATA.summary    = await loadJSON('summary.json');
    DATA.historique = await loadJSON('historique.json');
    DATA.metrics    = await loadJSON('metrics_annuels.json');
    DATA.detail     = await loadJSON('repartition_canton_jeu.json');
    DATA.secteurs   = await loadJSON('repartition_secteur.json');
    DATA.percapita  = await loadJSON('per_capita.json');
    DATA.benefs     = await loadJSON('beneficiaires.json');
    DATA.population = await loadJSON('population.json');

    initHero();
    initTimeline();
    initFranc();
    initSankey();
    initTreemap();
    initTilegram();
    initGamesMix();
    initCovidFocus();
    initTopBenefs();
  } catch (e) {
    console.error(e);
    document.getElementById('app-error').textContent = e.message;
    document.getElementById('app-error').style.display = 'block';
  }
});

/* ============================================================
   1. HERO — compteurs animés
   ============================================================ */
function initHero() {
  const s = DATA.summary;
  animateCounter(document.getElementById('kpi-benefice'), s.benefice_dernier, v => CHF1.format(v) + ' M');
  animateCounter(document.getElementById('kpi-pic'), s.benefice_pic, v => CHF1.format(v) + ' M');
  animateCounter(document.getElementById('kpi-redist'), s.redistribue_dernier_M, v => CHF1.format(v) + ' M');
  animateCounter(document.getElementById('kpi-cagr'), s.cagr_long_terme * 100, v => CHF1.format(v) + ' %');
  document.getElementById('kpi-pic-year').textContent = s.annee_pic;
  document.getElementById('kpi-last-year').textContent = s.derniere_annee;
  document.getElementById('kpi-redist-year').textContent = s.annee_redistribue;
  document.getElementById('hero-years').textContent = (s.derniere_annee - 1938);
}

/* ============================================================
   2. TIMELINE 1938-2025 — vis #1
   ============================================================ */
function initTimeline() {
  const container = d3.select('#viz-timeline');
  const W = container.node().clientWidth, H = 460;
  const margin = { top: 30, right: 60, bottom: 40, left: 60 };
  const w = W - margin.left - margin.right;
  const h = H - margin.top - margin.bottom;

  const svg = container.append('svg')
    .attr('viewBox', `0 0 ${W} ${H}`)
    .attr('width', '100%').attr('height', H);

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const hist = DATA.historique.filter(d => d.benefice_M != null);
  const histCA = DATA.historique.filter(d => d.ca_M != null);

  const x  = d3.scaleLinear().domain([1938, 2026]).range([0, w]);
  const yB = d3.scaleLinear().domain([0, 280]).range([h, 0]).nice();
  const yC = d3.scaleLinear().domain([0, 1800]).range([h, 0]).nice();

  // grille horizontale discrète
  g.selectAll('.grid').data(yB.ticks(5)).enter().append('line')
    .attr('x1', 0).attr('x2', w).attr('y1', d => yB(d)).attr('y2', d => yB(d))
    .attr('stroke', ruleColor()).attr('stroke-dasharray', '2,3');

  // axe X
  g.append('g').attr('transform', `translate(0,${h})`)
    .call(d3.axisBottom(x).tickFormat(d3.format('d')).ticks(10))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '12px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // axe Y bénéfice (gauche, rouge Loro)
  g.append('g')
    .call(d3.axisLeft(yB).tickFormat(d => d + ' M').ticks(6))
    .call(s => s.selectAll('text').attr('fill', '#c8102e').style('font-size', '11px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // axe Y chiffre d'affaires (droite, gris)
  g.append('g').attr('transform', `translate(${w},0)`)
    .call(d3.axisRight(yC).tickFormat(d => d + ' M').ticks(6))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // ligne CA (zone)
  const areaCA = d3.area().curve(d3.curveMonotoneX)
    .x(d => x(d.annee)).y0(h).y1(d => yC(d.ca_M));
  g.append('path').datum(histCA)
    .attr('fill', '#5b8def').attr('opacity', 0.13).attr('d', areaCA);
  g.append('path').datum(histCA)
    .attr('fill', 'none').attr('stroke', '#5b8def').attr('stroke-width', 1.5)
    .attr('opacity', 0.6).attr('d',
      d3.line().curve(d3.curveMonotoneX).x(d => x(d.annee)).y(d => yC(d.ca_M)));

  // ligne bénéfice principale
  const line = d3.line().curve(d3.curveMonotoneX)
    .x(d => x(d.annee)).y(d => yB(d.benefice_M));
  const path = g.append('path').datum(hist)
    .attr('fill', 'none').attr('stroke', '#c8102e').attr('stroke-width', 2.5).attr('d', line);

  // animation de tracé
  const totalLen = path.node().getTotalLength();
  path.attr('stroke-dasharray', totalLen).attr('stroke-dashoffset', totalLen)
    .transition().duration(1800).attr('stroke-dashoffset', 0);

  // points + annotations
  const pts = g.append('g').selectAll('circle').data(hist).enter().append('circle')
    .attr('cx', d => x(d.annee)).attr('cy', d => yB(d.benefice_M))
    .attr('r', d => d.annotation ? 6 : 2.5)
    .attr('fill', d => d.annotation ? '#fff' : '#c8102e')
    .attr('stroke', '#c8102e').attr('stroke-width', d => d.annotation ? 2 : 1)
    .style('cursor', 'pointer');

  pts.on('mouseover', function(ev, d) {
    let html = `<div class="t-title">${d.annee} · ${CHF1.format(d.benefice_M)} M CHF</div>`;
    if (d.ca_M) html += `<div>CA : ${CHF1.format(d.ca_M)} M</div>`;
    if (d.annotation) html += `<div class="t-meta">${d.annotation.titre} · ${d.annotation.source}</div>`;
    showTip(html, ev.clientX, ev.clientY);
  }).on('mouseout', hideTip);

  // étiquettes des annotations directement sur le graphe
  const annot = hist.filter(d => d.annotation);
  const labelG = g.append('g').attr('font-family', 'Source Serif Pro, serif').style('font-style','italic');
  annot.forEach((d, i) => {
    const xp = x(d.annee), yp = yB(d.benefice_M);
    const goUp = i % 2 === 0;
    const dy = goUp ? -22 : 28;
    labelG.append('line')
      .attr('x1', xp).attr('x2', xp).attr('y1', yp).attr('y2', yp + dy * 0.6)
      .attr('stroke', '#c8102e').attr('stroke-width', 0.8).attr('opacity', 0.5);
    const t = labelG.append('text')
      .attr('x', xp).attr('y', yp + dy)
      .attr('text-anchor', 'middle')
      .attr('fill', inkColor()).attr('font-size', 12)
      .text(d.annotation.titre);
    // contour blanc pour lisibilité
    t.clone(true).lower().attr('stroke', isDark() ? '#15140f' : '#fbfaf6')
      .attr('stroke-width', 4).attr('fill', 'none');
  });

  // légende
  const lg = svg.append('g').attr('transform', `translate(${margin.left + 20}, ${margin.top - 8})`);
  lg.append('rect').attr('width', 12).attr('height', 2).attr('y', 7).attr('fill', '#c8102e');
  lg.append('text').attr('x', 18).attr('y', 11).attr('fill', inkSoftColor()).attr('font-size', 12)
    .text('Bénéfice (M CHF, axe gauche)');
  lg.append('rect').attr('x', 200).attr('width', 12).attr('height', 2).attr('y', 7).attr('fill', '#5b8def').attr('opacity', 0.6);
  lg.append('text').attr('x', 218).attr('y', 11).attr('fill', inkSoftColor()).attr('font-size', 12)
    .text('Chiffre d\'affaires (M CHF, axe droit)');
}

/* ============================================================
   3. LE 1 CHF DÉPENSÉ — vis #6
   Décompose le PBJ 2024 (Produit Brut des Jeux) en flux.
   ============================================================ */
function initFranc() {
  // PBJ 2024 = 438.24 M. Décomposition selon Total sheet :
  const pbj = 438.235;
  const parts = [
    { label: 'Bénéfice → cantons',        v: 258.236, color: '#c8102e' },
    { label: 'Commission points de vente', v: 79.387,  color: '#5b8def' },
    { label: 'FSES (sport)',               v: 19.568,  color: '#f0a93d' },
    { label: 'Marketing / publicité',      v: 15.355,  color: '#7c5bc7' },
    { label: 'FSC (courses chevaux)',      v: 3.234,   color: '#2ea08a' },
    { label: 'Direction',                  v: 2.288,   color: '#c97b3a' },
    { label: 'Prévention jeu excessif',    v: 2.191,   color: '#8a8a8a' },
  ];
  const knownTotal = parts.reduce((s, p) => s + p.v, 0);
  parts.push({ label: 'Autres charges', v: pbj - knownTotal, color: '#bbb6a8' });

  const container = d3.select('#viz-franc');
  const W = container.node().clientWidth, H = 200;
  const margin = { top: 24, right: 24, bottom: 80, left: 24 };
  const w = W - margin.left - margin.right;
  const h = H - margin.top - margin.bottom;

  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const scale = d3.scaleLinear().domain([0, pbj]).range([0, w]);
  let cumul = 0;

  parts.forEach((p, i) => {
    const xstart = scale(cumul);
    const wseg = scale(p.v);
    const grp = g.append('g').style('cursor', 'pointer');
    grp.append('rect')
      .attr('x', xstart).attr('y', 0).attr('width', 0).attr('height', h)
      .attr('fill', p.color).attr('stroke', '#fff').attr('stroke-width', 1)
      .transition().delay(i * 120).duration(700).attr('width', wseg);

    // étiquette au-dessus pour les gros segments, en dessous pour les petits
    const isLarge = wseg > 70;
    const labelY  = isLarge ? h + 24 : h + 24;
    const pct = (p.v / pbj * 100);
    if (isLarge) {
      grp.append('text')
        .attr('x', xstart + wseg / 2).attr('y', h / 2)
        .attr('text-anchor', 'middle').attr('dominant-baseline', 'middle')
        .attr('fill', '#fff').attr('font-size', 12).attr('font-weight', 600)
        .style('opacity', 0)
        .text(CHF1.format(pct) + ' %')
        .transition().delay(700 + i * 120).duration(400).style('opacity', 1);
    }
    grp.on('mouseover', ev => {
      showTip(`<div class="t-title">${p.label}</div><div>${CHF1.format(p.v)} M CHF</div><div class="t-meta">soit ${CHF1.format(pct)}% du PBJ Loro 2024</div>`, ev.clientX, ev.clientY);
    }).on('mouseout', hideTip);
    cumul += p.v;
  });

  // Étiquettes en colonne sous le graphe
  const lblG = svg.append('g').attr('transform', `translate(${margin.left}, ${margin.top + h + 12})`);
  const colCount = Math.min(4, parts.length);
  const colW = w / colCount;
  parts.forEach((p, i) => {
    const col = i % colCount, row = Math.floor(i / colCount);
    const xx = col * colW, yy = row * 18;
    const grp = lblG.append('g').attr('transform', `translate(${xx},${yy})`);
    grp.append('rect').attr('width', 10).attr('height', 10).attr('y', 2).attr('fill', p.color);
    grp.append('text').attr('x', 16).attr('y', 11)
      .attr('fill', inkSoftColor()).attr('font-size', 11.5)
      .text(`${p.label} (${CHF1.format(p.v / pbj * 100)}%)`);
  });
}

/* ============================================================
   4. SANKEY — flux du ticket au bénéficiaire (vis #2)
   Type de jeu → Canton → Secteur, année 2024.
   ============================================================ */
function initSankey() {
  const year = 2024;
  const container = d3.select('#viz-sankey');
  const W = container.node().clientWidth, H = 540;
  container.html('');
  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H);

  // 1) Sommes par type de jeu × canton (depuis Détail, postes Vente.1..Vente.5)
  const games = ['Billets Instantanés', 'Jeux de tirages', 'Paris sportifs', 'Loterie électronique', 'PMUR'];
  const cantons = ['VD', 'GE', 'VS', 'FR', 'NE', 'JU'];
  const sectorsList = Object.keys(DATA.secteurs);

  const detailYear = DATA.detail.filter(d => d.annee === year);
  const nodes = [];
  const nodeIdx = new Map();
  function addNode(id, name, kind) {
    if (!nodeIdx.has(id)) {
      nodeIdx.set(id, nodes.length);
      nodes.push({ id, name, kind });
    }
    return nodeIdx.get(id);
  }
  games.forEach(g => addNode('g:' + g, g, 'game'));
  cantons.forEach(c => addNode('c:' + c, CANTON_NAMES[c], 'canton'));
  sectorsList.forEach(s => addNode('s:' + s, SECTOR_SHORT[s] || s, 'sector'));

  const links = [];

  // jeu → canton (ventes par jeu × canton)
  games.forEach(gn => {
    const row = detailYear.find(d => d.libelle === gn);
    if (!row) return;
    cantons.forEach(c => {
      const v = row.cantons[c];
      if (v && v > 0) links.push({
        source: nodeIdx.get('g:' + gn),
        target: nodeIdx.get('c:' + c),
        value: v / 1e6,
      });
    });
  });

  // canton → secteur (répartition proportionnelle)
  // On suppose : montant par secteur réparti aux cantons proportionnellement à
  // leur part dans la Répartition totale de l'année.
  const repRow = detailYear.find(d => d.poste === 'Répartition');
  if (repRow && repRow.total) {
    const cantonShare = {};
    cantons.forEach(c => { cantonShare[c] = (repRow.cantons[c] || 0) / repRow.total; });
    Object.entries(repRow.secteurs || {}).forEach(([sec, montant]) => {
      cantons.forEach(c => {
        const v = montant * cantonShare[c] / 1e6;
        if (v > 0.2) links.push({
          source: nodeIdx.get('c:' + c),
          target: nodeIdx.get('s:' + sec),
          value: v,
        });
      });
    });
  }

  // Layout Sankey
  const sankey = d3.sankey()
    .nodeWidth(14).nodePadding(10).extent([[10, 10], [W - 10, H - 24]]);

  const graph = sankey({
    nodes: nodes.map(d => ({ ...d })),
    links: links.map(d => ({ ...d })),
  });

  // links
  svg.append('g').selectAll('path').data(graph.links).enter().append('path')
    .attr('d', d3.sankeyLinkHorizontal())
    .attr('fill', 'none')
    .attr('stroke', d => {
      if (d.source.kind === 'game') return GAME_COLORS[d.source.id.slice(2)] || '#999';
      if (d.source.kind === 'canton') return CANTON_COLORS[d.source.id.slice(2)] || '#999';
      return '#999';
    })
    .attr('stroke-opacity', 0.32)
    .attr('stroke-width', d => Math.max(1, d.width))
    .on('mouseover', function (ev, d) {
      d3.select(this).attr('stroke-opacity', 0.7);
      showTip(`<div class="t-title">${d.source.name} → ${d.target.name}</div><div>${CHF1.format(d.value)} M CHF</div>`, ev.clientX, ev.clientY);
    })
    .on('mousemove', ev => showTip(ensureTip().innerHTML, ev.clientX, ev.clientY))
    .on('mouseout', function () {
      d3.select(this).attr('stroke-opacity', 0.32);
      hideTip();
    });

  // nodes
  const nodeG = svg.append('g').selectAll('g').data(graph.nodes).enter().append('g');
  nodeG.append('rect')
    .attr('x', d => d.x0).attr('y', d => d.y0)
    .attr('height', d => d.y1 - d.y0).attr('width', d => d.x1 - d.x0)
    .attr('fill', d => {
      if (d.kind === 'game')   return GAME_COLORS[d.id.slice(2)] || '#999';
      if (d.kind === 'canton') return CANTON_COLORS[d.id.slice(2)] || '#999';
      return '#c8102e';
    });

  nodeG.append('text')
    .attr('x', d => d.x0 < W / 2 ? d.x1 + 6 : d.x0 - 6)
    .attr('y', d => (d.y0 + d.y1) / 2)
    .attr('dy', '0.35em')
    .attr('text-anchor', d => d.x0 < W / 2 ? 'start' : 'end')
    .attr('font-size', 11.5)
    .attr('fill', inkColor())
    .text(d => d.name)
    .each(function(d) {
      if (d.y1 - d.y0 < 9) d3.select(this).remove(); // évite chevauchement
    });
}

/* ============================================================
   5. TREEMAP DES SECTEURS — vis #7
   ============================================================ */
function initTreemap() {
  const year = '2025';
  const container = d3.select('#viz-treemap');
  const W = container.node().clientWidth, H = 460;
  container.html('');
  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width','100%').attr('height', H);

  // Données : secteurs × beneficiaires nommés. On agrège niveau secteur + sous-niveau bénéficiaires.
  const root = { name: 'Loro', children: [] };
  const yKey = year;

  Object.entries(DATA.secteurs).forEach(([sec, series]) => {
    const v = series[yKey];
    if (!v) return;
    const child = { name: sec, value: v, color: SECTOR_COLORS[sec] || '#999' };
    root.children.push(child);
  });

  const r = d3.hierarchy(root).sum(d => d.value).sort((a, b) => b.value - a.value);
  d3.treemap().size([W, H]).padding(2).round(true)(r);

  const leaves = r.leaves();
  const g = svg.append('g').selectAll('g').data(leaves).enter().append('g')
    .attr('transform', d => `translate(${d.x0},${d.y0})`);

  g.append('rect')
    .attr('width', d => d.x1 - d.x0).attr('height', d => d.y1 - d.y0)
    .attr('fill', d => d.data.color)
    .attr('opacity', 0)
    .transition().duration(700).delay((d,i)=>i*40).attr('opacity', 0.92);

  g.append('text')
    .attr('x', 12).attr('y', 22).attr('fill', '#fff').attr('font-weight', 500)
    .attr('font-size', 14)
    .text(d => SECTOR_SHORT[d.data.name] || d.data.name)
    .each(function(d) {
      if ((d.x1 - d.x0) < 80 || (d.y1 - d.y0) < 30) d3.select(this).remove();
    });

  g.append('text')
    .attr('x', 12).attr('y', 40).attr('fill', '#fff').attr('opacity', 0.85)
    .attr('font-size', 12).attr('font-family', 'Source Serif Pro, serif')
    .text(d => CHF1.format(d.value / 1e6) + ' M')
    .each(function(d) {
      if ((d.x1 - d.x0) < 80 || (d.y1 - d.y0) < 45) d3.select(this).remove();
    });

  g.append('text')
    .attr('x', 12).attr('y', 58).attr('fill', '#fff').attr('opacity', 0.7)
    .attr('font-size', 11)
    .text(d => CHF1.format(d.value / r.value * 100) + ' %')
    .each(function(d) {
      if ((d.x1 - d.x0) < 80 || (d.y1 - d.y0) < 65) d3.select(this).remove();
    });

  g.on('mouseover', (ev, d) => {
    showTip(`<div class="t-title">${d.data.name}</div><div>${CHF1.format(d.value / 1e6)} M CHF (${year})</div><div class="t-meta">${CHF1.format(d.value / r.value * 100)} % du redistribué</div>`, ev.clientX, ev.clientY);
  }).on('mouseout', hideTip);
}

/* ============================================================
   6. TILEGRAM CANTONS — vis #3 (avec slider année + bar chart race)
   ============================================================ */
function initTilegram() {
  // Disposition approximative des 6 cantons romands en grille
  // (FR au nord, JU au nord, NE au centre-nord, GE au sud-ouest, VD au centre, VS au sud-est)
  const layout = {
    JU: { r: 0, c: 1 },
    NE: { r: 0, c: 2 },
    FR: { r: 1, c: 3 },
    VD: { r: 1, c: 2 },
    GE: { r: 2, c: 1 },
    VS: { r: 2, c: 3 },
  };
  const cantons = Object.keys(layout);

  // Construire les séries par canton et métrique
  const metrics = {
    ventes:    { label: 'Ventes totales par canton (M CHF)', unit: 'M', source: 'ventes' },
    benefice:  { label: 'Bénéfice redistribué par canton (M CHF)', unit: 'M', source: 'rep' },
    per_capita:{ label: 'Dépense par habitant (CHF)', unit: 'CHF', source: 'pc' },
  };

  // ventes totales par canton et année (poste = Vente.6 "Total")
  function ventesByYear(y) {
    const row = DATA.detail.find(d => d.annee === y && d.libelle === 'Total');
    if (!row) return null;
    const out = {};
    cantons.forEach(c => out[c] = (row.cantons[c] || 0) / 1e6);
    return out;
  }
  function benefByYear(y) {
    const row = DATA.detail.find(d => d.annee === y && d.poste === 'Répartition');
    if (!row) return null;
    const out = {};
    cantons.forEach(c => out[c] = (row.cantons[c] || 0) / 1e6);
    return out;
  }
  function perCapitaByYear(y) {
    const pc = DATA.percapita.tous_jeux;
    const idx = pc.years.indexOf(+y);
    if (idx < 0) return null;
    const out = {};
    Object.entries({ VD: 'Vaud', FR: 'Fribourg', VS: 'Valais', NE: 'Neuchâtel', GE: 'Genève', JU: 'Jura' })
      .forEach(([k, name]) => out[k] = pc.data[name][idx]);
    return out;
  }
  const getter = { ventes: ventesByYear, benefice: benefByYear, per_capita: perCapitaByYear };

  const years = d3.range(2013, 2026);
  let curMetric = 'ventes';
  let curYear = 2025;

  const container = d3.select('#viz-tilegram');
  container.html('');

  // Contrôles
  const ctl = container.append('div').attr('class', 'controls');
  Object.entries(metrics).forEach(([k, m]) => {
    ctl.append('button').attr('class', 'btn' + (k === curMetric ? ' active' : ''))
      .text(m.label.split(' (')[0])
      .on('click', function() {
        curMetric = k;
        ctl.selectAll('.btn').classed('active', false);
        d3.select(this).classed('active', true);
        render();
      });
  });

  // Slider année
  const sliderRow = container.append('div').style('display','flex')
    .style('align-items','center').style('gap','12px').style('margin-bottom','20px');
  sliderRow.append('span').text('Année')
    .style('font-size','12px').style('color','var(--ink-mute)')
    .style('letter-spacing','0.1em').style('text-transform','uppercase');
  const yearLabel = sliderRow.append('span')
    .style('font-family','Source Serif Pro, serif').style('font-size','26px')
    .text(curYear);
  const slider = sliderRow.append('input').attr('type','range')
    .attr('min', 2013).attr('max', 2025).attr('value', curYear).attr('step', 1)
    .style('flex','1');
  slider.on('input', function() {
    curYear = +this.value;
    yearLabel.text(curYear);
    render();
  });

  // Bouton play/pause
  let playing = null;
  const playBtn = sliderRow.append('button').attr('class','btn').text('▶ Animer');
  playBtn.on('click', () => {
    if (playing) {
      clearInterval(playing); playing = null;
      playBtn.text('▶ Animer');
    } else {
      playBtn.text('⏸ Pause');
      playing = setInterval(() => {
        curYear = curYear >= 2025 ? 2013 : curYear + 1;
        slider.property('value', curYear);
        yearLabel.text(curYear);
        render();
      }, 900);
    }
  });

  // Layout : tilegram à gauche, barres à droite
  const wrap = container.append('div')
    .style('display','grid').style('grid-template-columns','1fr 1fr')
    .style('gap','24px').style('align-items','start');

  const tileBox = wrap.append('div');
  const barBox = wrap.append('div');

  const tileSize = 96, tileGap = 10;
  const tileW = 4 * (tileSize + tileGap), tileH = 3 * (tileSize + tileGap);
  const tileSvg = tileBox.append('svg').attr('viewBox', `0 0 ${tileW} ${tileH}`)
    .attr('width','100%').style('max-width', tileW + 'px');

  const barH = 360;
  const barSvg = barBox.append('svg').attr('viewBox', `0 0 480 ${barH}`)
    .attr('width','100%');

  function render() {
    const vals = getter[curMetric](curYear);
    if (!vals) return;

    const maxV = d3.max(Object.values(vals));
    const color = d3.scaleSequential().domain([0, maxV])
      .interpolator(d3.interpolateRgb('#fbfaf6', '#c8102e'));

    // --- TILEGRAM ---
    const tiles = tileSvg.selectAll('g.tile').data(cantons, d => d);
    const tEnter = tiles.enter().append('g').attr('class','tile')
      .attr('transform', d => {
        const p = layout[d];
        return `translate(${p.c * (tileSize + tileGap)}, ${p.r * (tileSize + tileGap)})`;
      });
    tEnter.append('rect').attr('width', tileSize).attr('height', tileSize).attr('rx', 6);
    tEnter.append('text').attr('class','tcode')
      .attr('x', 10).attr('y', 22).attr('font-weight', 600).attr('font-size', 14)
      .text(d => d);
    tEnter.append('text').attr('class','tname')
      .attr('x', 10).attr('y', 38).attr('font-size', 10).attr('opacity', 0.65)
      .text(d => CANTON_NAMES[d]);
    tEnter.append('text').attr('class','tval')
      .attr('x', 10).attr('y', tileSize - 14).attr('font-family','Source Serif Pro, serif')
      .attr('font-size', 22).attr('font-weight', 500);

    const merge = tEnter.merge(tiles);
    merge.select('rect').transition().duration(500).attr('fill', d => color(vals[d]))
      .attr('stroke', d => d3.lab(color(vals[d])).l < 60 ? 'none' : ruleColor());
    merge.select('.tval')
      .attr('fill', d => d3.lab(color(vals[d])).l < 60 ? '#fff' : inkColor())
      .text(d => {
        const v = vals[d];
        return curMetric === 'per_capita' ? CHF.format(v) : CHF1.format(v);
      });
    merge.select('.tcode')
      .attr('fill', d => d3.lab(color(vals[d])).l < 60 ? '#fff' : inkColor());
    merge.select('.tname')
      .attr('fill', d => d3.lab(color(vals[d])).l < 60 ? '#fff' : inkSoftColor());

    merge.on('mouseover', (ev, c) => {
      const u = curMetric === 'per_capita' ? ' CHF/hab' : ' M CHF';
      showTip(`<div class="t-title">${CANTON_NAMES[c]} · ${curYear}</div><div>${metrics[curMetric].label}</div><div class="t-meta">${CHF1.format(vals[c])}${u}</div>`, ev.clientX, ev.clientY);
    }).on('mouseout', hideTip);

    // --- BAR CHART (classement) ---
    const sorted = cantons.slice().sort((a, b) => vals[b] - vals[a]);
    const x = d3.scaleLinear().domain([0, maxV * 1.05]).range([100, 460]);
    const y = d3.scaleBand().domain(sorted).range([20, barH - 20]).padding(0.2);

    const bars = barSvg.selectAll('g.bar').data(sorted, d => d);
    const bEnter = bars.enter().append('g').attr('class','bar')
      .attr('transform', d => `translate(0, ${y(d)})`);
    bEnter.append('text').attr('class','blbl').attr('x', 92).attr('y', y.bandwidth() / 2)
      .attr('dy', '0.35em').attr('text-anchor', 'end').attr('font-size', 12)
      .attr('fill', inkColor());
    bEnter.append('rect').attr('x', 100).attr('y', 0).attr('height', y.bandwidth())
      .attr('fill', d => CANTON_COLORS[d]).attr('opacity', 0.85);
    bEnter.append('text').attr('class','bval')
      .attr('y', y.bandwidth() / 2).attr('dy', '0.35em')
      .attr('font-size', 12).attr('font-family','Source Serif Pro, serif')
      .attr('fill', inkColor());

    const bMerge = bEnter.merge(bars);
    bMerge.transition().duration(600).attr('transform', d => `translate(0, ${y(d)})`);
    bMerge.select('.blbl').text(d => CANTON_NAMES[d]);
    bMerge.select('rect').transition().duration(600).attr('width', d => x(vals[d]) - 100);
    bMerge.select('.bval')
      .attr('x', d => x(vals[d]) + 6)
      .text(d => {
        const v = vals[d], u = curMetric === 'per_capita' ? ' CHF' : ' M';
        return CHF1.format(v) + u;
      })
      .transition().duration(600).attr('x', d => x(vals[d]) + 6);
  }
  render();
}

/* ============================================================
   7. MIX DES JEUX dans le temps — vis #11 (stacked area)
   ============================================================ */
function initGamesMix() {
  const games = ['Billets Instantanés', 'Jeux de tirages', 'Paris sportifs', 'Loterie électronique', 'PMUR'];
  const years = d3.range(2013, 2026);

  // Pour chaque année, totaliser le poste Vente.X = jeu
  const dataset = years.map(y => {
    const row = { annee: y };
    games.forEach(g => {
      const r = DATA.detail.find(d => d.annee === y && d.libelle === g);
      row[g] = r ? (r.total || 0) / 1e6 : 0;
    });
    return row;
  });

  const container = d3.select('#viz-mix');
  const W = container.node().clientWidth, H = 380;
  const margin = { top: 24, right: 140, bottom: 36, left: 50 };
  const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;
  container.html('');
  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  let stackMode = 'value'; // ou 'percent'
  const modeRow = container.append('div').attr('class','controls').style('margin-top','-30px');
  modeRow.append('button').attr('class','btn active').text('Valeurs absolues').on('click', function() {
    stackMode = 'value'; modeRow.selectAll('.btn').classed('active', false); d3.select(this).classed('active', true); render();
  });
  modeRow.append('button').attr('class','btn').text('100 % empilé').on('click', function() {
    stackMode = 'percent'; modeRow.selectAll('.btn').classed('active', false); d3.select(this).classed('active', true); render();
  });

  function render() {
    g.selectAll('*').remove();
    const stack = d3.stack().keys(games).order(d3.stackOrderNone);
    let series, maxY;
    if (stackMode === 'percent') {
      stack.offset(d3.stackOffsetExpand);
      series = stack(dataset);
      maxY = 1;
    } else {
      series = stack(dataset);
      maxY = d3.max(series[series.length - 1], d => d[1]);
    }

    const x = d3.scaleLinear().domain([2013, 2025]).range([0, w]);
    const y = d3.scaleLinear().domain([0, maxY]).range([h, 0]).nice();

    const area = d3.area()
      .x(d => x(d.data.annee)).y0(d => y(d[0])).y1(d => y(d[1]))
      .curve(d3.curveMonotoneX);

    g.selectAll('path.layer').data(series).enter().append('path').attr('class','layer')
      .attr('fill', d => GAME_COLORS[d.key]).attr('opacity', 0.9).attr('d', area)
      .on('mouseover', (ev, d) => {
        showTip(`<div class="t-title">${d.key}</div>`, ev.clientX, ev.clientY);
      }).on('mouseout', hideTip);

    g.append('g').attr('transform', `translate(0,${h})`)
      .call(d3.axisBottom(x).tickFormat(d3.format('d')).ticks(7))
      .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size','11px'))
      .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));
    g.append('g')
      .call(d3.axisLeft(y).tickFormat(stackMode === 'percent' ? d3.format('.0%') : (d => d + ' M')).ticks(6))
      .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size','11px'))
      .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

    // Légende à droite
    const lg = svg.append('g').attr('transform', `translate(${W - margin.right + 14}, ${margin.top + 8})`);
    games.forEach((gk, i) => {
      lg.append('rect').attr('y', i * 22).attr('width', 12).attr('height', 12).attr('fill', GAME_COLORS[gk]);
      lg.append('text').attr('x', 18).attr('y', i * 22 + 10).attr('font-size', 12).attr('fill', inkColor()).text(gk);
    });
  }
  render();
}

/* ============================================================
   8. FOCUS COVID — vis #9 (deltas 2019 → 2021 par canton et par jeu)
   ============================================================ */
function initCovidFocus() {
  const games = ['Billets Instantanés', 'Jeux de tirages', 'Paris sportifs', 'Loterie électronique', 'PMUR'];
  const yA = 2019, yB = 2021;
  const rows = games.map(g => {
    const ra = DATA.detail.find(d => d.annee === yA && d.libelle === g);
    const rb = DATA.detail.find(d => d.annee === yB && d.libelle === g);
    if (!ra || !rb) return null;
    const a = ra.total / 1e6, b = rb.total / 1e6;
    return { game: g, a, b, delta: b - a, pct: (b - a) / a };
  }).filter(Boolean);

  const container = d3.select('#viz-covid');
  const W = container.node().clientWidth, H = 240;
  const margin = { top: 20, right: 140, bottom: 24, left: 180 };
  const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;
  container.html('');
  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width','100%').attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleLinear()
    .domain([d3.min(rows, d => Math.min(d.a, d.b)) * 0.95, d3.max(rows, d => Math.max(d.a, d.b)) * 1.05])
    .range([0, w]);
  const y = d3.scaleBand().domain(rows.map(d => d.game)).range([0, h]).padding(0.35);

  g.append('g').attr('transform', `translate(0,${h})`)
    .call(d3.axisBottom(x).tickFormat(d => d + ' M').ticks(5))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size','11px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // Labels jeux
  g.selectAll('text.glbl').data(rows).enter().append('text').attr('class','glbl')
    .attr('x', -10).attr('y', d => y(d.game) + y.bandwidth() / 2).attr('dy','0.35em')
    .attr('text-anchor','end').attr('font-size', 12).attr('fill', inkColor())
    .text(d => d.game);

  // Lignes de connexion
  rows.forEach(d => {
    g.append('line')
      .attr('x1', x(d.a)).attr('x2', x(d.a)) // animation depuis x1
      .attr('y1', y(d.game) + y.bandwidth() / 2).attr('y2', y(d.game) + y.bandwidth() / 2)
      .attr('stroke', d.delta < 0 ? '#c8102e' : '#1f6f5c').attr('stroke-width', 3).attr('opacity', 0.4)
      .transition().duration(800).attr('x2', x(d.b));
  });
  // Points 2019
  g.selectAll('circle.a').data(rows).enter().append('circle').attr('class','a')
    .attr('cx', d => x(d.a)).attr('cy', d => y(d.game) + y.bandwidth() / 2)
    .attr('r', 6).attr('fill', '#fff').attr('stroke', inkSoftColor()).attr('stroke-width', 2);
  // Points 2021
  g.selectAll('circle.b').data(rows).enter().append('circle').attr('class','b')
    .attr('cx', d => x(d.a)).attr('cy', d => y(d.game) + y.bandwidth() / 2)
    .attr('r', 7).attr('fill', d => d.delta < 0 ? '#c8102e' : '#1f6f5c')
    .transition().duration(800).attr('cx', d => x(d.b));

  // Annotations à droite : delta
  g.selectAll('text.dlt').data(rows).enter().append('text').attr('class','dlt')
    .attr('x', w + 10).attr('y', d => y(d.game) + y.bandwidth() / 2).attr('dy','0.35em')
    .attr('font-size', 12).attr('font-family','Source Serif Pro, serif')
    .attr('fill', d => d.delta < 0 ? '#c8102e' : '#1f6f5c')
    .text(d => (d.pct > 0 ? '+' : '') + CHF1.format(d.pct * 100) + ' %');

  // En-tête
  svg.append('text').attr('x', margin.left).attr('y', 14)
    .attr('font-size', 11).attr('fill', inkSoftColor())
    .text(`Évolution 2019 → 2021 par type de jeu (Suisse romande, M CHF)`);
}

/* ============================================================
   9. TOP BÉNÉFICIAIRES (mini, pour aiguiller vers l'explorer)
   ============================================================ */
function initTopBenefs() {
  const top = DATA.benefs.slice().sort((a, b) => b.total - a.total).slice(0, 8);
  const c = d3.select('#viz-topbenefs');
  c.html('');
  const list = c.append('div');

  const maxTotal = d3.max(top, d => d.total);

  top.forEach((b, i) => {
    const row = list.append('div').style('display','grid')
      .style('grid-template-columns','30px 1fr 200px 110px')
      .style('gap','12px').style('align-items','center')
      .style('padding','10px 0').style('border-bottom','1px solid var(--rule)');

    row.append('div').style('font-family','Source Serif Pro, serif')
      .style('color','var(--ink-mute)').style('font-size','15px')
      .text(String(i + 1).padStart(2, '0'));

    const nameCell = row.append('div');
    nameCell.append('div').style('font-weight','500').text(b.nom);
    nameCell.append('div').style('font-size','12px').style('color','var(--ink-soft)')
      .text((b.categorie || '') + (b.canton ? ` · ${b.canton}` : ''));

    // mini sparkline
    const sparkBox = row.append('div');
    const years = Object.keys(b.series).sort();
    const vals  = years.map(y => b.series[y]);
    const sw = 200, sh = 32;
    const ssvg = sparkBox.append('svg').attr('viewBox', `0 0 ${sw} ${sh}`).attr('width','100%').attr('height', sh);
    const sx = d3.scaleLinear().domain([d3.min(years), d3.max(years)]).range([2, sw - 2]);
    const sy = d3.scaleLinear().domain([0, d3.max(vals)]).range([sh - 4, 4]);
    ssvg.append('path').datum(years.map((y, k) => ({ y, v: vals[k] })))
      .attr('fill','none').attr('stroke','#c8102e').attr('stroke-width', 1.5)
      .attr('d', d3.line().curve(d3.curveMonotoneX).x(d => sx(d.y)).y(d => sy(d.v)));
    ssvg.selectAll('circle').data(years.map((y, k) => ({ y, v: vals[k] }))).enter().append('circle')
      .attr('cx', d => sx(d.y)).attr('cy', d => sy(d.v)).attr('r', 1.5).attr('fill', '#c8102e');

    row.append('div').style('font-family','Source Serif Pro, serif').style('font-size','17px').style('text-align','right')
      .html(`${fmtCompact(b.total)}<span style="font-size:11px;color:var(--ink-soft)"> CHF cumul.</span>`);
  });
}
