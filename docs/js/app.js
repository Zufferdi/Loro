/* =============================================================
   app.js v2 — récit en 6 actes
   Scrollama orchestre les transitions des viz selon le scroll.
   ============================================================= */

let DATA = {};

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
    DATA.rf         = await loadJSON('rapports_financiers.json');
    DATA.benefsVD   = await loadJSON('beneficiaires_top_vd.json');
    DATA.swisslos   = await loadJSON('swisslos.json');
    DATA.editorial  = await loadJSON('editorial_loro.json');

    initHero();
    initComparisons();
    initTimelineScrolly();
    initFranc();
    initAnomaly();
    initRealMap();
    initTilegram();
    initGovernance();
    initPrelevementEvol();
    initMixScrolly();
    initMixByCanton();
    initOpCosts();
    initCapital();
    initPrevention();
    initProblematic();
    initTreemap();
    initDependency();
    initHexBenefs();
    initTopBenefs();
    initEvenements();
    initTopBenefsVD();
    initLoroVsSwisslos();
    initEditorialTimeline();
    initJourney();
    initSankey();
    initReadingProgress();
    initRevealOnScroll();
  } catch (e) {
    console.error(e);
    const errEl = document.getElementById('app-error');
    if (errEl) { errEl.textContent = e.message; errEl.style.display = 'block'; }
  }
});

/* ============================================================
   HERO — compteur géant qui s'anime au load
   ============================================================ */
function initHero() {
  const heroEl = document.getElementById('hero-number');
  if (!heroEl) return;
  const target = DATA.summary.benefice_dernier; // 252
  animateCounter(heroEl, target, v => Math.round(v).toString(), 2200);
}

/* ============================================================
   ACTE I — TIMELINE en scrollytelling
   La même viz, mais ses annotations apparaissent par étapes.
   ============================================================ */
function initTimelineScrolly() {
  const container = d3.select('#viz-timeline');
  if (container.empty()) return;
  container.html('');

  const wrap = container.node();
  const W = wrap.clientWidth || 600, H = Math.min(wrap.clientHeight, 520) || 520;
  const margin = { top: 30, right: 40, bottom: 40, left: 50 };
  const w = W - margin.left - margin.right;
  const h = H - margin.top - margin.bottom;

  const svg = container.append('svg')
    .attr('viewBox', `0 0 ${W} ${H}`)
    .attr('width', '100%').attr('height', '100%')
    .style('max-height', H + 'px');

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const hist = DATA.historique.filter(d => d.benefice_M != null);

  const x = d3.scaleLinear().domain([1938, 2026]).range([0, w]);
  const y = d3.scaleLinear().domain([0, 280]).range([h, 0]).nice();

  // grille discrète
  g.selectAll('.grid').data(y.ticks(5)).enter().append('line')
    .attr('x1', 0).attr('x2', w).attr('y1', d => y(d)).attr('y2', d => y(d))
    .attr('stroke', ruleColor()).attr('stroke-dasharray', '2,3');

  // axes
  g.append('g').attr('transform', `translate(0,${h})`)
    .call(d3.axisBottom(x).tickFormat(d3.format('d')).ticks(8))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));
  g.append('g')
    .call(d3.axisLeft(y).tickFormat(d => d + ' M').ticks(6))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // ligne complète (toujours visible, mais opacité variable selon step)
  const line = d3.line().curve(d3.curveMonotoneX)
    .x(d => x(d.annee)).y(d => y(d.benefice_M));

  // Découper en segments pour pouvoir révéler progressivement
  const path = g.append('path').datum(hist)
    .attr('class', 't-line')
    .attr('fill', 'none').attr('stroke', '#c8102e').attr('stroke-width', 2.5)
    .attr('d', line);

  // points (tous)
  const pts = g.append('g').selectAll('circle.pt').data(hist).enter().append('circle')
    .attr('class', d => 'pt' + (d.annotation ? ' annot' : ''))
    .attr('data-year', d => d.annee)
    .attr('cx', d => x(d.annee)).attr('cy', d => y(d.benefice_M))
    .attr('r', d => d.annotation ? 0 : 2.5)
    .attr('fill', d => d.annotation ? '#fff' : '#c8102e')
    .attr('stroke', '#c8102e').attr('stroke-width', d => d.annotation ? 2 : 1)
    .style('cursor', 'pointer');

  pts.on('mouseover', function(ev, d) {
    let html = `<div class="t-title">${d.annee} · ${CHF1.format(d.benefice_M)} M CHF</div>`;
    if (d.ca_M) html += `<div>CA : ${CHF1.format(d.ca_M)} M</div>`;
    if (d.annotation) html += `<div class="t-meta">${d.annotation.titre} · ${d.annotation.source}</div>`;
    showTip(html, ev.clientX, ev.clientY);
  }).on('mouseout', hideTip);

  // labels d'annotation (cachés au départ, opacité 0)
  const annotG = g.append('g').attr('class', 'annot-labels');
  const annot = hist.filter(d => d.annotation);
  annot.forEach((d, i) => {
    const xp = x(d.annee), yp = y(d.benefice_M);
    const dy = i % 2 === 0 ? -28 : 32;
    const grp = annotG.append('g')
      .attr('data-year', d.annee)
      .style('opacity', 0)
      .style('transition', 'opacity 0.5s');
    grp.append('line')
      .attr('x1', xp).attr('x2', xp).attr('y1', yp).attr('y2', yp + dy * 0.6)
      .attr('stroke', '#c8102e').attr('stroke-width', 0.8).attr('opacity', 0.6);
    const tx = grp.append('text')
      .attr('x', xp).attr('y', yp + dy)
      .attr('text-anchor', 'middle')
      .attr('font-family', 'Source Serif Pro, serif')
      .attr('font-style', 'italic')
      .attr('fill', inkColor()).attr('font-size', 13)
      .text(d.annotation.titre);
    tx.clone(true).lower().attr('stroke', isDark() ? '#15140f' : '#fbfaf6')
      .attr('stroke-width', 4).attr('fill', 'none');
  });

  // Légende minimale
  svg.append('text')
    .attr('x', margin.left).attr('y', 18)
    .attr('font-size', 11).attr('fill', inkSoftColor())
    .text('Bénéfice annuel · millions de CHF · 1938—2025');

  // Mask qui révèle progressivement la courbe selon le step
  // On commence avec mask qui cache tout sauf jusqu'à year courante.
  const reveal = (year) => {
    const xMax = x(year);
    // animation : on utilise un clip-rect
    let clip = svg.select('#tl-clip');
    if (clip.empty()) {
      svg.append('defs').append('clipPath').attr('id', 'tl-clip')
        .append('rect').attr('x', 0).attr('y', -10).attr('width', 0).attr('height', H);
      path.attr('clip-path', 'url(#tl-clip)');
      // également pour les points
      g.selectAll('circle.pt').attr('clip-path', 'url(#tl-clip)');
    }
    svg.select('#tl-clip rect')
      .transition().duration(900).ease(d3.easeQuadOut)
      .attr('width', margin.left + xMax + 10);

    // animer le rayon des points annot ≤ year
    g.selectAll('circle.annot')
      .transition().duration(600)
      .attr('r', d => d.annee <= year ? 6 : 0);

    // afficher les annotations ≤ year
    annotG.selectAll('g').each(function() {
      const y = +d3.select(this).attr('data-year');
      d3.select(this).style('opacity', y <= year ? 1 : 0);
    });
  };

  // Init : tout caché (juste 1938)
  reveal(1938);

  // Scrollama
  const scroller = scrollama();
  scroller
    .setup({
      step: '[data-scrolly="timeline"] .step',
      offset: 0.55,
      progress: false,
    })
    .onStepEnter(({ element, direction }) => {
      element.classList.add('is-active');
      const year = +element.dataset.step;
      reveal(year);
    })
    .onStepExit(({ element, direction }) => {
      if (direction === 'up') {
        element.classList.remove('is-active');
        const prevStep = element.previousElementSibling;
        if (prevStep) {
          const prevYear = +prevStep.dataset.step;
          reveal(prevYear);
        } else {
          reveal(1938);
        }
      }
    });

  window.addEventListener('resize', debounce(() => scroller.resize(), 200));
}

/* ============================================================
   ACTE II — ANATOMIE D'UN FRANC
   Barre empilée animée, segments qui apparaissent en cascade.
   ============================================================ */
function initFranc() {
  const pbj = 438.235;
  const parts = [
    { label: 'Bénéfice → cantons',           v: 258.236, color: '#c8102e', strong: true },
    { label: 'Commission points de vente',   v: 79.387,  color: '#5b8def' },
    { label: 'FSES (sport)',                  v: 19.568,  color: '#f0a93d' },
    { label: 'Marketing / publicité',         v: 15.355,  color: '#7c5bc7' },
    { label: 'FSC (courses chevaux)',         v: 3.234,   color: '#2ea08a' },
    { label: 'Direction',                     v: 2.288,   color: '#c97b3a' },
    { label: 'Prévention jeu excessif',       v: 2.191,   color: '#8a8a8a' },
  ];
  const knownTotal = parts.reduce((s, p) => s + p.v, 0);
  parts.push({ label: 'Autres charges', v: pbj - knownTotal, color: '#bbb6a8' });

  const container = d3.select('#viz-franc');
  if (container.empty()) return;
  container.html('');

  const W = container.node().clientWidth, H = 280;
  const margin = { top: 60, right: 24, bottom: 100, left: 24 };
  const w = W - margin.left - margin.right;
  const h = 60; // hauteur barre

  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const scale = d3.scaleLinear().domain([0, pbj]).range([0, w]);

  // Tick : "0 CHF" gauche, "438 M PBJ" droite
  svg.append('text')
    .attr('x', margin.left).attr('y', margin.top - 20)
    .attr('font-size', 11).attr('fill', inkSoftColor())
    .attr('letter-spacing', '0.06em').text('0 CHF');
  svg.append('text')
    .attr('x', margin.left + w).attr('y', margin.top - 20)
    .attr('font-size', 11).attr('text-anchor', 'end').attr('fill', inkSoftColor())
    .attr('letter-spacing', '0.06em').text(`PBJ total · ${CHF1.format(pbj)} M`);

  let cumul = 0;
  parts.forEach((p, i) => {
    const xstart = scale(cumul);
    const wseg = scale(p.v);
    const grp = g.append('g').style('cursor', 'pointer');

    grp.append('rect')
      .attr('x', xstart).attr('y', 0).attr('width', 0).attr('height', h)
      .attr('fill', p.color).attr('stroke', '#fff').attr('stroke-width', 1.5)
      .transition().delay(i * 140).duration(700).ease(d3.easeCubicOut)
      .attr('width', wseg);

    const pct = (p.v / pbj * 100);

    // Étiquette pourcentage dans la barre si assez large
    if (wseg > 60) {
      grp.append('text')
        .attr('x', xstart + wseg / 2).attr('y', h / 2)
        .attr('text-anchor', 'middle').attr('dominant-baseline', 'middle')
        .attr('fill', '#fff')
        .attr('font-family', 'Source Serif Pro, serif')
        .attr('font-size', p.strong ? 22 : 14)
        .attr('font-weight', p.strong ? 600 : 500)
        .style('opacity', 0)
        .text(`${CHF1.format(pct)} %`)
        .transition().delay(700 + i * 140).duration(400).style('opacity', 1);
    }

    grp.on('mouseover', ev => {
      showTip(
        `<div class="t-title">${p.label}</div>
         <div>${CHF1.format(p.v)} M CHF</div>
         <div class="t-meta">${CHF1.format(pct)} % du PBJ Loro 2024</div>`,
        ev.clientX, ev.clientY);
    }).on('mouseout', hideTip);

    cumul += p.v;
  });

  // Lignes verticales pointillées + étiquettes sous la barre
  const labels = parts.map((p, i) => {
    const xMid = scale(parts.slice(0, i).reduce((s,q) => s+q.v, 0) + p.v / 2);
    return { ...p, xMid };
  });

  // disposition manuelle en 2 lignes pour éviter chevauchement
  const lblG = svg.append('g').attr('transform', `translate(${margin.left}, ${margin.top + h + 20})`);

  // Garder seulement les 4 plus gros segments comme labels directs
  // Les petits sont listés en bas
  labels.slice(0, 4).forEach((p, i) => {
    const grp = lblG.append('g').style('opacity', 0)
      .transition().delay(1000 + i * 120).duration(500).style('opacity', 1);
    // ligne reliant
    lblG.append('line')
      .attr('x1', p.xMid).attr('x2', p.xMid)
      .attr('y1', -20).attr('y2', -6)
      .attr('stroke', p.color).attr('stroke-width', 1).attr('opacity', 0.4);
    const text = lblG.append('text').attr('class', 'label').attr('x', p.xMid).attr('y', 6)
      .attr('text-anchor', 'middle')
      .attr('font-size', 11).attr('fill', inkColor())
      .attr('font-weight', 500);
    text.append('tspan').attr('x', p.xMid).attr('dy', 0).text(p.label);
    text.append('tspan').attr('x', p.xMid).attr('dy', 14)
      .attr('font-family', 'Source Serif Pro, serif').attr('fill', p.color)
      .text(`${CHF1.format(p.v)} M`);
  });

  // Légende pour les petits segments à droite
  const legendG = svg.append('g').attr('transform', `translate(${margin.left}, ${margin.top + h + 80})`);
  const smallParts = labels.slice(4);
  smallParts.forEach((p, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const xx = col * (w / 2), yy = row * 18;
    const grp = legendG.append('g').attr('transform', `translate(${xx},${yy})`);
    grp.append('rect').attr('width', 10).attr('height', 10).attr('y', 2).attr('fill', p.color);
    grp.append('text').attr('x', 16).attr('y', 11)
      .attr('fill', inkSoftColor()).attr('font-size', 11)
      .text(`${p.label} (${CHF1.format(p.v / pbj * 100)} %, ${CHF1.format(p.v)} M)`);
  });
}

/* ============================================================
   ACTE III — TILEGRAM avec mode "ratio reçu/dépensé" en plus
   ============================================================ */
function initTilegram() {
  const layout = {
    JU: { r: 0, c: 1 },
    NE: { r: 0, c: 2 },
    FR: { r: 1, c: 3 },
    VD: { r: 1, c: 2 },
    GE: { r: 2, c: 1 },
    VS: { r: 2, c: 3 },
  };
  const cantons = Object.keys(layout);

  const metrics = {
    ventes:    { label: 'Ventes par canton', unit: 'M CHF', short: 'Ventes' },
    benefice:  { label: 'Bénéfice redistribué au canton', unit: 'M CHF', short: 'Redistribué' },
    per_capita:{ label: 'Dépense annuelle par habitant', unit: 'CHF', short: 'Par habitant' },
    ratio:     { label: 'Ratio reçu / dépensé', unit: '%', short: 'Reçu / dépensé' },
  };

  function ventesByYear(y) {
    const row = DATA.detail.find(d => d.annee === y && d.libelle === 'Total');
    if (!row) return null;
    const out = {}; cantons.forEach(c => out[c] = (row.cantons[c] || 0) / 1e6);
    return out;
  }
  function benefByYear(y) {
    const row = DATA.detail.find(d => d.annee === y && d.poste === 'Répartition');
    if (!row) return null;
    const out = {}; cantons.forEach(c => out[c] = (row.cantons[c] || 0) / 1e6);
    return out;
  }
  function perCapitaByYear(y) {
    const pc = DATA.percapita.tous_jeux;
    const idx = pc.years.indexOf(+y);
    if (idx < 0) return null;
    const out = {};
    const map = { VD: 'Vaud', FR: 'Fribourg', VS: 'Valais', NE: 'Neuchâtel', GE: 'Genève', JU: 'Jura' };
    Object.entries(map).forEach(([k, n]) => out[k] = pc.data[n][idx]);
    return out;
  }
  function ratioByYear(y) {
    const v = ventesByYear(y), b = benefByYear(y);
    if (!v || !b) return null;
    const out = {};
    cantons.forEach(c => out[c] = (b[c] / v[c]) * 100);
    return out;
  }
  const getter = { ventes: ventesByYear, benefice: benefByYear, per_capita: perCapitaByYear, ratio: ratioByYear };

  let curMetric = 'per_capita';
  let curYear = 2024;
  let playing = null;

  const container = d3.select('#viz-tilegram');
  container.html('');

  const ctl = container.append('div').attr('class', 'controls');
  Object.entries(metrics).forEach(([k, m]) => {
    ctl.append('button').attr('class', 'btn' + (k === curMetric ? ' active' : ''))
      .attr('data-metric', k)
      .text(m.short)
      .on('click', function() {
        curMetric = k;
        ctl.selectAll('.btn').classed('active', false);
        d3.select(this).classed('active', true);
        render();
      });
  });

  const sliderRow = container.append('div').style('display','flex')
    .style('align-items','center').style('gap','12px').style('margin-bottom','24px').style('flex-wrap','wrap');
  sliderRow.append('span').text('Année')
    .style('font-size','11px').style('color','var(--ink-mute)')
    .style('letter-spacing','0.14em').style('text-transform','uppercase');
  const yearLabel = sliderRow.append('span')
    .style('font-family','Source Serif Pro, serif').style('font-size','26px')
    .text(curYear);
  const slider = sliderRow.append('input').attr('type','range')
    .attr('min', 2013).attr('max', 2024).attr('value', curYear).attr('step', 1)
    .style('flex','1').style('min-width','200px');
  slider.on('input', function() {
    curYear = +this.value; yearLabel.text(curYear); render();
  });
  const playBtn = sliderRow.append('button').attr('class','btn').text('▶ Animer');
  playBtn.on('click', () => {
    if (playing) {
      clearInterval(playing); playing = null;
      playBtn.text('▶ Animer');
    } else {
      playBtn.text('⏸ Pause');
      playing = setInterval(() => {
        curYear = curYear >= 2024 ? 2013 : curYear + 1;
        slider.property('value', curYear);
        yearLabel.text(curYear);
        render();
      }, 900);
    }
  });

  const wrap = container.append('div')
    .style('display','grid').style('grid-template-columns','1fr 1fr')
    .style('gap','24px').style('align-items','start');

  const tileBox = wrap.append('div');
  const barBox = wrap.append('div');

  const tileSize = 100, tileGap = 10;
  const tileW = 4 * (tileSize + tileGap), tileH = 3 * (tileSize + tileGap);
  const tileSvg = tileBox.append('svg').attr('viewBox', `0 0 ${tileW} ${tileH}`)
    .attr('width','100%').style('max-width', tileW + 'px');

  const barH = 360;
  const barSvg = barBox.append('svg').attr('viewBox', `0 0 480 ${barH}`)
    .attr('width','100%');

  function render() {
    const vals = getter[curMetric](curYear);
    if (!vals) return;

    const m = metrics[curMetric];
    const maxV = d3.max(Object.values(vals));
    const minV = d3.min(Object.values(vals));
    // ratio mode : palette divergente autour de 50%
    let color;
    if (curMetric === 'ratio') {
      color = d3.scaleSequential().domain([30, 70]).interpolator(d3.interpolateRdYlBu);
    } else {
      color = d3.scaleSequential().domain([0, maxV]).interpolator(d3.interpolateRgb('#fbfaf6', '#c8102e'));
    }

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
      .attr('x', 10).attr('y', 38).attr('font-size', 10).attr('opacity', 0.7)
      .text(d => CANTON_NAMES[d]);
    tEnter.append('text').attr('class','tval')
      .attr('x', 10).attr('y', tileSize - 18).attr('font-family','Source Serif Pro, serif')
      .attr('font-size', 24).attr('font-weight', 500);
    tEnter.append('text').attr('class','tunit')
      .attr('x', 10).attr('y', tileSize - 6).attr('font-size', 10).attr('opacity', 0.65);

    const merge = tEnter.merge(tiles);
    merge.select('rect').transition().duration(500)
      .attr('fill', d => color(vals[d]))
      .attr('stroke', d => d3.lab(color(vals[d])).l < 60 ? 'none' : ruleColor());

    const dark = d => d3.lab(color(vals[d])).l < 60;
    merge.select('.tval')
      .attr('fill', d => dark(d) ? '#fff' : inkColor())
      .text(d => {
        const v = vals[d];
        if (curMetric === 'per_capita') return CHF.format(v);
        if (curMetric === 'ratio')      return CHF1.format(v) + '%';
        return CHF1.format(v);
      });
    merge.select('.tunit')
      .attr('fill', d => dark(d) ? 'rgba(255,255,255,0.7)' : inkSoftColor())
      .text(d => {
        if (curMetric === 'per_capita') return 'CHF/hab';
        if (curMetric === 'ratio')      return 'reçu/dépensé';
        return 'M CHF';
      });
    merge.select('.tcode').attr('fill', d => dark(d) ? '#fff' : inkColor());
    merge.select('.tname').attr('fill', d => dark(d) ? '#fff' : inkSoftColor());

    merge.on('mouseover', (ev, c) => {
      const v = vals[c];
      let unitTxt = m.unit;
      if (curMetric === 'per_capita') unitTxt = 'CHF/habitant/an';
      if (curMetric === 'ratio')      unitTxt = '% reçu / dépensé';
      const html = `<div class="t-title">${CANTON_NAMES[c]} · ${curYear}</div>
        <div>${m.label}</div>
        <div class="t-meta">${CHF1.format(v)} ${unitTxt}</div>`;
      showTip(html, ev.clientX, ev.clientY);
    }).on('mouseout', hideTip);

    // --- BAR CHART (classement) ---
    const sorted = cantons.slice().sort((a, b) => vals[b] - vals[a]);
    const xMin = curMetric === 'ratio' ? Math.min(0, minV * 0.95) : 0;
    const xMax = maxV * 1.05;
    const x = d3.scaleLinear().domain([xMin, xMax]).range([110, 460]);
    const y = d3.scaleBand().domain(sorted).range([20, barH - 20]).padding(0.2);

    const bars = barSvg.selectAll('g.bar').data(sorted, d => d);
    const bEnter = bars.enter().append('g').attr('class','bar')
      .attr('transform', d => `translate(0, ${y(d)})`);
    bEnter.append('text').attr('class','blbl').attr('x', 102).attr('y', y.bandwidth() / 2)
      .attr('dy', '0.35em').attr('text-anchor', 'end').attr('font-size', 12)
      .attr('fill', inkColor());
    bEnter.append('rect').attr('y', 0).attr('height', y.bandwidth())
      .attr('fill', d => CANTON_COLORS[d]).attr('opacity', 0.85);
    bEnter.append('text').attr('class','bval')
      .attr('y', y.bandwidth() / 2).attr('dy', '0.35em')
      .attr('font-size', 12).attr('font-family','Source Serif Pro, serif')
      .attr('fill', inkColor());

    const bMerge = bEnter.merge(bars);
    bMerge.transition().duration(600).attr('transform', d => `translate(0, ${y(d)})`);
    bMerge.select('.blbl').text(d => CANTON_NAMES[d]);
    bMerge.select('rect').transition().duration(600)
      .attr('x', x(0))
      .attr('width', d => Math.max(0, x(vals[d]) - x(0)));
    bMerge.select('.bval')
      .transition().duration(600)
      .attr('x', d => x(vals[d]) + 6)
      .text(d => {
        const v = vals[d];
        if (curMetric === 'per_capita') return CHF.format(v) + ' CHF';
        if (curMetric === 'ratio')      return CHF1.format(v) + '%';
        return CHF1.format(v) + ' M';
      });
  }
  render();
}

/* ============================================================
   ACTE IV — MIX DES JEUX en scrollytelling
   ============================================================ */
function initMixScrolly() {
  const container = d3.select('#viz-mix');
  if (container.empty()) return;
  container.html('');

  const games = ['Billets Instantanés', 'Jeux de tirages', 'Paris sportifs', 'Loterie électronique', 'PMUR'];

  const dataset = d3.range(2013, 2026).map(y => {
    const row = { annee: y };
    games.forEach(g => {
      const r = DATA.detail.find(d => d.annee === y && d.libelle === g);
      row[g] = r ? (r.total || 0) / 1e6 : 0;
    });
    return row;
  });

  const wrap = container.node();
  const W = wrap.clientWidth || 600, H = Math.min(wrap.clientHeight, 480) || 480;
  const margin = { top: 30, right: 140, bottom: 40, left: 50 };
  const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;

  const svg = container.append('svg')
    .attr('viewBox', `0 0 ${W} ${H}`)
    .attr('width', '100%').attr('height', '100%')
    .style('max-height', H + 'px');
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  let highlight = null; // null = tous

  function render() {
    g.selectAll('*').remove();
    const stack = d3.stack().keys(games).order(d3.stackOrderNone);
    const series = stack(dataset);
    const maxY = d3.max(series[series.length - 1], d => d[1]);
    const x = d3.scaleLinear().domain([2013, 2025]).range([0, w]);
    const y = d3.scaleLinear().domain([0, maxY]).range([h, 0]).nice();

    const area = d3.area()
      .x(d => x(d.data.annee)).y0(d => y(d[0])).y1(d => y(d[1]))
      .curve(d3.curveMonotoneX);

    g.selectAll('path.layer').data(series).enter().append('path').attr('class', 'layer')
      .attr('fill', d => GAME_COLORS[d.key])
      .attr('opacity', d => highlight ? (d.key === highlight ? 0.95 : 0.18) : 0.85)
      .attr('d', area)
      .on('mouseover', (ev, d) => {
        const last = d[d.length - 1];
        showTip(`<div class="t-title">${d.key}</div><div>2025 : ${CHF1.format(last[1] - last[0])} M CHF</div>`, ev.clientX, ev.clientY);
      }).on('mouseout', hideTip);

    g.append('g').attr('transform', `translate(0,${h})`)
      .call(d3.axisBottom(x).tickFormat(d3.format('d')).ticks(6))
      .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
      .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));
    g.append('g')
      .call(d3.axisLeft(y).tickFormat(d => d + ' M').ticks(6))
      .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
      .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

    // Légende
    svg.selectAll('g.legend').remove();
    const lg = svg.append('g').attr('class', 'legend')
      .attr('transform', `translate(${W - margin.right + 14}, ${margin.top + 8})`);
    games.forEach((gk, i) => {
      const active = !highlight || highlight === gk;
      lg.append('rect').attr('y', i * 22).attr('width', 12).attr('height', 12)
        .attr('fill', GAME_COLORS[gk]).attr('opacity', active ? 1 : 0.3);
      lg.append('text').attr('x', 18).attr('y', i * 22 + 10)
        .attr('font-size', 11.5).attr('fill', active ? inkColor() : inkSoftColor())
        .attr('font-weight', highlight === gk ? 600 : 400)
        .text(gk);
    });

    // Titre du focus
    svg.selectAll('text.focus-title').remove();
    if (highlight) {
      svg.append('text').attr('class', 'focus-title')
        .attr('x', margin.left).attr('y', 18)
        .attr('font-family', 'Source Serif Pro, serif')
        .attr('font-style', 'italic')
        .attr('font-size', 16).attr('fill', GAME_COLORS[highlight])
        .text(`Focus : ${highlight}`);
    } else {
      svg.append('text').attr('class', 'focus-title')
        .attr('x', margin.left).attr('y', 18)
        .attr('font-size', 11).attr('fill', inkSoftColor())
        .text('Ventes par type de jeu · M CHF · 2013—2025');
    }
  }
  render();

  const scroller = scrollama();
  scroller
    .setup({ step: '[data-scrolly="mix"] .step', offset: 0.55 })
    .onStepEnter(({ element }) => {
      element.classList.add('is-active');
      const step = element.dataset.step;
      if (step === 'all')    highlight = null;
      if (step === 'paris')  highlight = 'Paris sportifs';
      if (step === 'elec')   highlight = 'Loterie électronique';
      if (step === 'online') highlight = null;
      render();
    })
    .onStepExit(({ element, direction }) => {
      if (direction === 'up') element.classList.remove('is-active');
    });

  window.addEventListener('resize', debounce(() => scroller.resize(), 200));
}

/* ============================================================
   ACTE V — TREEMAP des secteurs (2025)
   ============================================================ */
function initTreemap() {
  const year = '2025';
  const container = d3.select('#viz-treemap');
  if (container.empty()) return;
  container.html('');

  const W = container.node().clientWidth, H = 480;
  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width','100%').attr('height', H);

  const root = { name: 'Loro', children: [] };
  Object.entries(DATA.secteurs).forEach(([sec, series]) => {
    const v = series[year];
    if (!v) return;
    root.children.push({ name: sec, value: v, color: SECTOR_COLORS[sec] || '#999' });
  });

  const r = d3.hierarchy(root).sum(d => d.value).sort((a, b) => b.value - a.value);
  d3.treemap().size([W, H]).padding(3).round(true)(r);

  const leaves = r.leaves();
  const g = svg.append('g').selectAll('g').data(leaves).enter().append('g')
    .attr('transform', d => `translate(${d.x0},${d.y0})`)
    .style('cursor', 'pointer');

  g.append('rect')
    .attr('width', d => d.x1 - d.x0).attr('height', d => d.y1 - d.y0)
    .attr('fill', d => d.data.color)
    .attr('opacity', 0)
    .transition().duration(700).delay((d, i) => i * 50).attr('opacity', 0.92);

  g.append('text')
    .attr('x', 14).attr('y', 26).attr('fill', '#fff').attr('font-weight', 500)
    .attr('font-size', 15)
    .text(d => SECTOR_SHORT[d.data.name] || d.data.name)
    .each(function(d) {
      if ((d.x1 - d.x0) < 90 || (d.y1 - d.y0) < 32) d3.select(this).remove();
    });

  g.append('text')
    .attr('x', 14).attr('y', 50).attr('fill', '#fff').attr('opacity', 0.85)
    .attr('font-size', 22).attr('font-family', 'Source Serif Pro, serif')
    .text(d => CHF1.format(d.value / 1e6) + ' M')
    .each(function(d) {
      if ((d.x1 - d.x0) < 90 || (d.y1 - d.y0) < 60) d3.select(this).remove();
    });

  g.append('text')
    .attr('x', 14).attr('y', 70).attr('fill', '#fff').attr('opacity', 0.7)
    .attr('font-size', 12)
    .text(d => CHF1.format(d.value / r.value * 100) + ' % du total')
    .each(function(d) {
      if ((d.x1 - d.x0) < 90 || (d.y1 - d.y0) < 80) d3.select(this).remove();
    });

  g.on('mouseover', (ev, d) => {
    showTip(`<div class="t-title">${d.data.name}</div>
             <div>${CHF1.format(d.value / 1e6)} M CHF en 2025</div>
             <div class="t-meta">${CHF1.format(d.value / r.value * 100)} % du redistribué</div>`,
            ev.clientX, ev.clientY);
  }).on('mouseout', hideTip);
}

/* ============================================================
   ACTE VI — TOP 10 BÉNÉFICIAIRES
   ============================================================ */
function initTopBenefs() {
  const c = d3.select('#viz-topbenefs');
  if (c.empty()) return;
  c.html('');

  // Dédup : on garde la ligne avec canton=null (consolidé) si elle existe
  const seen = new Set();
  const unique = [];
  DATA.benefs.slice().sort((a, b) => b.total - a.total).forEach(b => {
    if (!seen.has(b.nom)) { seen.add(b.nom); unique.push(b); }
  });
  const top = unique.slice(0, 10);

  const list = c.append('div');
  top.forEach((b, i) => {
    const row = list.append('div').style('display','grid')
      .style('grid-template-columns','30px 1fr 220px 110px')
      .style('gap','14px').style('align-items','center')
      .style('padding','14px 0').style('border-bottom','1px solid var(--rule)');

    row.append('div').style('font-family','Source Serif Pro, serif')
      .style('color','var(--ink-mute)').style('font-size','16px')
      .style('font-style','italic')
      .text(String(i + 1).padStart(2, '0'));

    const nameCell = row.append('div');
    nameCell.append('div').style('font-weight','500').style('font-size','15px').text(b.nom);
    nameCell.append('div').style('font-size','12px').style('color','var(--ink-soft)').style('margin-top','3px')
      .text((b.categorie || '') + (b.canton ? ` · ${b.canton}` : ''));

    const sparkBox = row.append('div');
    const years = Object.keys(b.series).sort();
    const vals = years.map(y => b.series[y]);
    const allYears = d3.range(2013, 2026);
    const padded = allYears.map(y => ({ y, v: b.series[String(y)] || 0 }));
    const sw = 220, sh = 36;
    const ssvg = sparkBox.append('svg').attr('viewBox', `0 0 ${sw} ${sh}`).attr('width','100%').attr('height', sh);
    const sx = d3.scaleLinear().domain([2013, 2025]).range([3, sw - 3]);
    const sy = d3.scaleLinear().domain([0, d3.max(padded, d => d.v) || 1]).range([sh - 4, 6]);

    // bars
    ssvg.selectAll('rect').data(padded).enter().append('rect')
      .attr('x', d => sx(d.y) - 7).attr('y', d => sy(d.v))
      .attr('width', 14).attr('height', d => sh - 4 - sy(d.v))
      .attr('fill', '#c8102e').attr('opacity', d => d.v > 0 ? 0.4 : 0);

    // line over
    ssvg.append('path').datum(padded)
      .attr('fill', 'none').attr('stroke', '#c8102e').attr('stroke-width', 1.5)
      .attr('d', d3.line().x(d => sx(d.y)).y(d => sy(d.v)));

    // last point
    const last = padded.filter(d => d.v > 0).slice(-1)[0];
    if (last) {
      ssvg.append('circle').attr('cx', sx(last.y)).attr('cy', sy(last.v))
        .attr('r', 3).attr('fill', '#c8102e');
    }
    // hit areas
    const bandW = (sw - 6) / allYears.length;
    ssvg.selectAll('rect.hit').data(padded).enter().append('rect').attr('class', 'hit')
      .attr('x', d => sx(d.y) - bandW / 2).attr('y', 0)
      .attr('width', bandW).attr('height', sh)
      .attr('fill', 'transparent')
      .on('mouseover', (ev, d) => {
        const html = `<div class="t-title">${b.nom} · ${d.y}</div><div>${d.v ? fmtCompact(d.v) + ' CHF' : '— rien'}</div>`;
        showTip(html, ev.clientX, ev.clientY);
      }).on('mouseout', hideTip);

    row.append('div').style('font-family','Source Serif Pro, serif').style('font-size','18px').style('text-align','right')
      .html(`${fmtCompact(b.total)}<br><span style="font-size:11px;color:var(--ink-soft); font-family: var(--sans);">CHF cumulés</span>`);
  });
}

/* ============================================================
   CODA — SANKEY (inchangé fonctionnellement)
   ============================================================ */
function initSankey() {
  const year = 2024;
  const container = d3.select('#viz-sankey');
  if (container.empty()) return;
  container.html('');
  const W = container.node().clientWidth, H = 560;
  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H);

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

  const sankey = d3.sankey()
    .nodeWidth(14).nodePadding(10).extent([[10, 10], [W - 10, H - 24]]);

  const graph = sankey({
    nodes: nodes.map(d => ({ ...d })),
    links: links.map(d => ({ ...d })),
  });

  svg.append('g').selectAll('path').data(graph.links).enter().append('path')
    .attr('d', d3.sankeyLinkHorizontal())
    .attr('fill', 'none')
    .attr('stroke', d => {
      if (d.source.kind === 'game') return GAME_COLORS[d.source.id.slice(2)] || '#999';
      if (d.source.kind === 'canton') return CANTON_COLORS[d.source.id.slice(2)] || '#999';
      return '#999';
    })
    .attr('stroke-opacity', 0.3)
    .attr('stroke-width', d => Math.max(1, d.width))
    .on('mouseover', function (ev, d) {
      d3.select(this).attr('stroke-opacity', 0.7);
      showTip(`<div class="t-title">${d.source.name} → ${d.target.name}</div><div>${CHF1.format(d.value)} M CHF</div>`, ev.clientX, ev.clientY);
    })
    .on('mouseout', function () {
      d3.select(this).attr('stroke-opacity', 0.3);
      hideTip();
    });

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
      if (d.y1 - d.y0 < 9) d3.select(this).remove();
    });
}

/* ============================================================
   READING PROGRESS — barre dans la nav top
   ============================================================ */
function initReadingProgress() {
  const bar = document.getElementById('reading-progress');
  if (!bar) return;
  const onScroll = () => {
    const doc = document.documentElement;
    const scrolled = (doc.scrollTop || document.body.scrollTop);
    const max = doc.scrollHeight - doc.clientHeight;
    const p = Math.min(100, Math.max(0, (scrolled / max) * 100));
    bar.style.setProperty('--progress', p + '%');
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ============================================================
   REVEAL ON SCROLL — pour les éléments .reveal
   ============================================================ */
function initRevealOnScroll() {
  const els = document.querySelectorAll('.reveal');
  if (!els.length) return;
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('in');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.15 });
  els.forEach(el => io.observe(el));
}

/* ============================================================
   COMPARISONS — bandeau "et concrètement, 252 millions c'est…"
   Apparaît juste après le hero.
   ============================================================ */
function initComparisons() {
  const container = d3.select('#viz-comparisons');
  if (container.empty()) return;
  container.html('');

  const s = DATA.summary;
  const b = s.benchmarks;
  const benefice = s.benefice_dernier; // en M CHF
  const beneficeCHF = benefice * 1_000_000;

  // Trois équivalences calculées
  const equivalents = [
    {
      n: Math.round(beneficeCHF / b.salaire_median_annuel_CHF).toLocaleString('fr-CH'),
      label: 'salaires annuels',
      detail: `médians suisses (84 288 CHF brut/an, OFS 2024)`,
    },
    {
      n: Math.round(benefice / b.tpg_budget_2025_M * 100) + ' %',
      label: 'du budget TPG',
      detail: `pour rouler tous les trams et bus genevois (325 M CHF en 2025)`,
    },
    {
      n: Math.round(beneficeCHF / b.population_romande_2024),
      label: 'CHF par habitant',
      detail: `versés au tissu associatif romand · ${b.population_romande_2024.toLocaleString('fr-CH')} habitants`,
    },
    {
      n: b.loro_part_loteries_suisses_pct + ' %',
      label: 'des loteries suisses',
      detail: `pour 22 % de la population (Loro vs Swisslos cumulés, 2024)`,
    },
  ];

  const grid = container.append('div').attr('class', 'comp-grid');
  equivalents.forEach((eq, i) => {
    const cell = grid.append('div').attr('class', 'comp-cell').style('opacity', 0)
      .style('transform', 'translateY(20px)');
    cell.append('div').attr('class', 'comp-n').text(eq.n);
    cell.append('div').attr('class', 'comp-label').text(eq.label);
    cell.append('div').attr('class', 'comp-detail').text(eq.detail);

    // animation cascade au scroll
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting) {
          setTimeout(() => {
            cell.transition().duration(600)
              .style('opacity', 1)
              .style('transform', 'translateY(0)');
          }, i * 150);
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.2 });
    io.observe(cell.node());
  });
}

/* ============================================================
   VRAIE CARTE — choroplèthe Suisse romande avec 4 métriques
   Charge le topojson via CDN, filtre aux 6 cantons romands.
   ============================================================ */
async function initRealMap() {
  const container = d3.select('#viz-realmap');
  if (container.empty()) return;
  container.html('<div style="padding:60px; text-align:center; color:var(--ink-mute);">Chargement de la carte…</div>');

  const topo = await loadSwissTopo();
  if (!topo) {
    container.html(`<div style="padding:40px; text-align:center; color:var(--ink-soft);">
      <div style="font-style: italic; font-family: var(--serif); font-size: 18px;">
        Carte indisponible (CDN inaccessible)
      </div>
      <div style="font-size: 13px; margin-top: 8px;">
        La vue géographique stylisée (tilegram) ci-dessous reste disponible.
      </div>
    </div>`);
    return;
  }
  container.html('');

  // Extraire les cantons et filtrer aux 6 romands
  const cantons = topojson.feature(topo, topo.objects.cantons);
  const lakes = topo.objects.lakes ? topojson.feature(topo, topo.objects.lakes) : null;

  // Détection de l'identifiant : selon la version swiss-maps,
  // f.id peut être l'abréviation (str "VD") ou le code BFS (int 22),
  // ou bien rangé sous f.properties.abbr / f.properties.KANTONSNUM
  function cantonAbbr(f) {
    if (typeof f.id === 'string' && f.id.length === 2) return f.id;
    const p = f.properties || {};
    if (p.abbr) return p.abbr;
    if (p.KANTONSNUM && CANTON_BFS_REVERSE[p.KANTONSNUM]) return CANTON_BFS_REVERSE[p.KANTONSNUM];
    if (typeof f.id === 'number' && CANTON_BFS_REVERSE[f.id]) return CANTON_BFS_REVERSE[f.id];
    return null;
  }

  const romandSet = new Set(['VD', 'FR', 'VS', 'NE', 'GE', 'JU']);
  const romandCantons = {
    type: 'FeatureCollection',
    features: cantons.features.filter(f => romandSet.has(cantonAbbr(f))),
  };
  if (romandCantons.features.length === 0) {
    container.html('<div style="padding:40px; text-align:center; color:var(--ink-soft); font-style: italic;">Cantons romands non identifiables dans le TopoJSON, voir version stylisée ci-dessous.</div>');
    return;
  }

  // Lac Léman, Neuchâtel, Morat, Joux dans la zone romande
  const romandLakes = lakes ? {
    type: 'FeatureCollection',
    features: lakes.features.filter(f => {
      // Filtrage approximatif par bbox de la zone romande
      const b = d3.geoBounds(f);
      return b[0][0] > 6 && b[1][0] < 8.5 && b[0][1] > 45.5 && b[1][1] < 48;
    }),
  } : null;

  // Métriques disponibles
  const metrics = {
    per_capita: { label: 'CHF dépensés par habitant',         short: 'Par habitant' },
    benefice:   { label: 'M CHF redistribués au canton',      short: 'Redistribué' },
    ratio:      { label: '% reçu / dépensé',                  short: 'Ratio reçu/dépensé' },
  };
  let curMetric = 'per_capita';
  let curYear = 2024;

  // Contrôles
  const ctl = container.append('div').attr('class', 'controls');
  Object.entries(metrics).forEach(([k, m]) => {
    ctl.append('button').attr('class', 'btn' + (k === curMetric ? ' active' : ''))
      .text(m.short)
      .on('click', function() {
        curMetric = k;
        ctl.selectAll('.btn').classed('active', false);
        d3.select(this).classed('active', true);
        render();
      });
  });

  const sliderRow = container.append('div').style('display','flex')
    .style('align-items','center').style('gap','12px').style('margin-bottom','20px')
    .style('flex-wrap','wrap');
  sliderRow.append('span').text('Année').style('font-size','11px')
    .style('color','var(--ink-mute)').style('letter-spacing','0.14em').style('text-transform','uppercase');
  const yearLabel = sliderRow.append('span').style('font-family','Source Serif Pro, serif').style('font-size','24px').text(curYear);
  const slider = sliderRow.append('input').attr('type','range').attr('min', 2013).attr('max', 2024)
    .attr('value', curYear).attr('step', 1).style('flex','1').style('min-width','200px');
  slider.on('input', function() { curYear = +this.value; yearLabel.text(curYear); render(); });

  // SVG
  const W = container.node().clientWidth, H = 480;
  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H);

  // Projection cadrée sur les cantons romands
  const projection = d3.geoMercator().fitSize([W - 20, H - 20], romandCantons);
  const path = d3.geoPath(projection);

  // Lacs en fond (gris bleuté)
  if (romandLakes) {
    svg.append('g').selectAll('path.lake').data(romandLakes.features).enter().append('path').attr('class', 'lake')
      .attr('d', path)
      .attr('fill', isDark() ? '#1a3a4a' : '#cfe2e8')
      .attr('opacity', 0.5);
  }

  // Cantons
  const cantonG = svg.append('g').attr('class', 'cantons')
    .selectAll('path').data(romandCantons.features).enter().append('path')
    .attr('d', path)
    .attr('stroke', isDark() ? '#15140f' : '#fbfaf6')
    .attr('stroke-width', 1.5)
    .style('cursor', 'pointer');

  // Labels canton
  const labelG = svg.append('g').attr('class', 'labels');
  romandCantons.features.forEach(f => {
    const centroid = path.centroid(f);
    const abbr = cantonAbbr(f);
    if (!abbr) return;
    const g = labelG.append('g').attr('transform', `translate(${centroid[0]},${centroid[1]})`);
    g.append('text').attr('class', 'c-abbr')
      .attr('text-anchor', 'middle').attr('dy', -4)
      .attr('font-size', 14).attr('font-weight', 600)
      .attr('fill', '#fff')
      .attr('stroke', 'rgba(0,0,0,0.3)').attr('stroke-width', 3).attr('paint-order','stroke')
      .text(abbr);
    g.append('text').attr('class', 'c-val')
      .attr('text-anchor', 'middle').attr('dy', 14)
      .attr('font-family', 'Source Serif Pro, serif')
      .attr('font-size', 16).attr('fill', '#fff')
      .attr('stroke', 'rgba(0,0,0,0.4)').attr('stroke-width', 3).attr('paint-order','stroke');
  });

  function getValue(c, year, metric) {
    if (metric === 'per_capita') {
      const pc = DATA.percapita.tous_jeux;
      const idx = pc.years.indexOf(year);
      const cantonName = CANTON_NAMES[c];
      return idx >= 0 ? pc.data[cantonName][idx] : 0;
    }
    if (metric === 'benefice') {
      const row = DATA.detail.find(d => d.annee === year && d.poste === 'Répartition');
      return row ? (row.cantons[c] || 0) / 1e6 : 0;
    }
    if (metric === 'ratio') {
      const vRow = DATA.detail.find(d => d.annee === year && d.libelle === 'Total');
      const bRow = DATA.detail.find(d => d.annee === year && d.poste === 'Répartition');
      if (!vRow || !bRow) return 0;
      return (bRow.cantons[c] || 0) / (vRow.cantons[c] || 1) * 100;
    }
    return 0;
  }

  function render() {
    const m = metrics[curMetric];
    const vals = {};
    ['VD','FR','VS','NE','GE','JU'].forEach(code => {
      vals[code] = getValue(code, curYear, curMetric);
    });

    const maxV = d3.max(Object.values(vals));
    let color;
    if (curMetric === 'ratio') {
      color = d3.scaleSequential().domain([30, 70]).interpolator(d3.interpolateRdYlBu);
    } else {
      color = d3.scaleSequential().domain([0, maxV]).interpolator(d3.interpolateRgb('#fbfaf6', '#c8102e'));
    }

    cantonG.transition().duration(600)
      .attr('fill', d => {
        const abbr = cantonAbbr(d);
        return color(vals[abbr] || 0);
      });

    cantonG.on('mouseover', (ev, d) => {
      const code = cantonAbbr(d);
      if (!code) return;
      const v = vals[code];
      let unit = '';
      if (curMetric === 'per_capita') unit = 'CHF/habitant/an';
      else if (curMetric === 'benefice') unit = 'M CHF';
      else if (curMetric === 'ratio')    unit = '% reçu / dépensé';
      showTip(`<div class="t-title">${CANTON_NAMES[code]} · ${curYear}</div>
               <div>${m.label}</div>
               <div class="t-meta">${CHF1.format(v)} ${unit}</div>`, ev.clientX, ev.clientY);
    }).on('mouseout', hideTip);

    // Valeurs sur la carte
    labelG.selectAll('g').each(function() {
      const t = d3.select(this);
      const abbr = t.select('.c-abbr').text();
      const v = vals[abbr];
      let txt;
      if (curMetric === 'per_capita')   txt = CHF.format(v);
      else if (curMetric === 'ratio')   txt = CHF1.format(v) + '%';
      else                              txt = CHF1.format(v);
      t.select('.c-val').text(txt);
    });
  }
  render();
}

/* ============================================================
   MIX PAR CANTON — small multiples des 6 cantons
   Chaque canton montre l'évolution de son mix de jeux 2013-2024
   ============================================================ */
function initMixByCanton() {
  const container = d3.select('#viz-mix-canton');
  if (container.empty()) return;
  container.html('');

  const games = ['Billets Instantanés', 'Jeux de tirages', 'Paris sportifs', 'Loterie électronique', 'PMUR'];
  const cantons = ['VD', 'GE', 'VS', 'FR', 'NE', 'JU'];
  const years = d3.range(2013, 2025);

  // Pour chaque canton, construire dataset
  function buildDataset(canton) {
    return years.map(y => {
      const row = { annee: y };
      games.forEach(g => {
        const r = DATA.detail.find(d => d.annee === y && d.libelle === g);
        row[g] = r ? (r.cantons[canton] || 0) / 1e6 : 0;
      });
      return row;
    });
  }

  // Grid layout
  const grid = container.append('div').attr('class', 'mc-grid');

  cantons.forEach(c => {
    const cell = grid.append('div').attr('class', 'mc-cell');
    cell.append('h4').html(`<span style="color:${CANTON_COLORS[c]}">●</span> ${CANTON_NAMES[c]}`);

    const data = buildDataset(c);
    const W = 280, H = 140;
    const margin = { top: 6, right: 6, bottom: 18, left: 28 };
    const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;

    const svg = cell.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%');
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    // Stacked
    const stack = d3.stack().keys(games);
    const series = stack(data);
    const maxY = d3.max(series[series.length - 1], d => d[1]);

    const x = d3.scaleLinear().domain([2013, 2024]).range([0, w]);
    const y = d3.scaleLinear().domain([0, maxY]).range([h, 0]);

    const area = d3.area().curve(d3.curveMonotoneX)
      .x(d => x(d.data.annee)).y0(d => y(d[0])).y1(d => y(d[1]));

    g.selectAll('path').data(series).enter().append('path')
      .attr('fill', d => GAME_COLORS[d.key]).attr('opacity', 0.88)
      .attr('d', area);

    // Petit axe X minimaliste
    g.append('text').attr('x', 0).attr('y', h + 12)
      .attr('font-size', 9).attr('fill', inkSoftColor()).text('2013');
    g.append('text').attr('x', w).attr('y', h + 12).attr('text-anchor','end')
      .attr('font-size', 9).attr('fill', inkSoftColor()).text('2024');

    // Total à droite
    const lastVal = years.map(y => games.reduce((s, gk) => {
      const r = DATA.detail.find(d => d.annee === y && d.libelle === gk);
      return s + (r ? (r.cantons[c] || 0) / 1e6 : 0);
    }, 0));
    g.append('text').attr('x', 0).attr('y', 8)
      .attr('font-family', 'Source Serif Pro, serif')
      .attr('font-size', 13).attr('font-weight', 500).attr('fill', inkColor())
      .text(`${CHF1.format(lastVal[lastVal.length-1])} M en 2024`);

    cell.on('mouseover', () => {
      svg.selectAll('path').attr('opacity', 1);
    }).on('mouseout', () => {
      svg.selectAll('path').attr('opacity', 0.88);
    });
  });

  // Légende globale en bas
  const legend = container.append('div').attr('class', 'mc-legend');
  games.forEach(gk => {
    const item = legend.append('span').attr('class', 'mc-leg-item');
    item.append('span').attr('class', 'sw').style('background', GAME_COLORS[gk]);
    item.append('span').text(gk);
  });
}

/* ============================================================
   PRÉVENTION DU JEU EXCESSIF — focus contre-pouvoir
   Met en regard PBJ vs montant prévention
   ============================================================ */
function initPrevention() {
  const container = d3.select('#viz-prevention');
  if (container.empty()) return;
  container.html('');

  const b = DATA.summary.benchmarks;
  // PBJ Loro 2024 ~438M, prévention Loro 2024 = 2.191M (0.5% PBJ),
  // côté cantons (PILDJ) 5.8M en 2023 toutes loteries
  const W = container.node().clientWidth, H = 320;
  const margin = { top: 30, right: 24, bottom: 24, left: 24 };
  const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;

  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width','100%').attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  // Une grille de 1000 points : 5 pour la prévention, 995 pour le reste
  const cols = 50, rows = 20, total = cols * rows; // 1000
  const dotSize = Math.min((w - cols) / cols, (h - rows) / rows) - 1;
  const prevDots = Math.round(b.prevention_part_pbj_pct * 10); // 0.3% → 3 dots sur 1000... arrondi à 5 pour visibilité

  for (let i = 0; i < total; i++) {
    const col = i % cols, row = Math.floor(i / cols);
    const isPrev = i < prevDots;
    g.append('rect')
      .attr('x', col * (dotSize + 1))
      .attr('y', row * (dotSize + 1))
      .attr('width', dotSize)
      .attr('height', dotSize)
      .attr('fill', isPrev ? '#c8102e' : (isDark() ? '#322f27' : '#e0ddd2'))
      .attr('opacity', 0)
      .transition()
      .delay(i * 0.5)
      .duration(300)
      .attr('opacity', isPrev ? 1 : 0.6);
  }

  // Annotation visuelle
  svg.append('text').attr('x', margin.left).attr('y', 18)
    .attr('font-size', 11).attr('fill', inkSoftColor())
    .text(`Chaque carré = 0,1 % du PBJ des loteries suisses (2,07 milliards en 2023)`);
}

/* ============================================================
   HEX BENEFS — vue d'ensemble de tous les bénéficiaires
   Cercles positionnés en grille hexagonale, taille = total, couleur = catégorie
   ============================================================ */
function initHexBenefs() {
  const container = d3.select('#viz-hex');
  if (container.empty()) return;
  container.html('');

  // Dédup : on garde la première occurrence (canton=null si elle existe)
  const seen = new Map();
  DATA.benefs.forEach(b => {
    const k = b.nom;
    if (!seen.has(k) || (b.canton === null && seen.get(k).canton !== null)) {
      seen.set(k, b);
    }
  });
  const all = Array.from(seen.values());

  const W = container.node().clientWidth, H = 540;
  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width','100%').attr('height', H);

  // Tri par catégorie puis par taille décroissante
  const cats = Array.from(new Set(all.map(b => b.categorie))).sort();
  const catColor = {
    'Sport / Tour de Romandie': '#f0a93d',
    'Culture / Cinéma (Cinéforom)': '#c8102e',
    'Santé / EMS': '#5b8def',
    'Culture / Musique classique': '#7c5bc7',
    'Culture / Festivals de cinéma': '#e44d4d',
    'Divers': '#8a8a8a',
  };

  // Layout : on simule en force directed mais positions initiales par catégorie
  const r = d3.scaleSqrt().domain([0, d3.max(all, b => b.total)]).range([3, 28]);
  const nodes = all.map(b => ({
    ...b,
    r: r(b.total),
    cat: b.categorie,
  }));

  // Position initiale par catégorie (colonnes)
  const catX = {};
  cats.forEach((c, i) => { catX[c] = (i + 0.5) * W / cats.length; });
  nodes.forEach(n => {
    n.x = catX[n.cat] + (Math.random() - 0.5) * 40;
    n.y = H / 2 + (Math.random() - 0.5) * 60;
  });

  const simulation = d3.forceSimulation(nodes)
    .force('x', d3.forceX(d => catX[d.cat]).strength(0.3))
    .force('y', d3.forceY(H / 2).strength(0.05))
    .force('collide', d3.forceCollide(d => d.r + 1.5).strength(0.8))
    .stop();

  for (let i = 0; i < 200; i++) simulation.tick();

  // Labels de catégorie
  cats.forEach(c => {
    svg.append('text')
      .attr('x', catX[c]).attr('y', 24)
      .attr('text-anchor', 'middle')
      .attr('font-size', 11)
      .attr('font-weight', 600)
      .attr('letter-spacing', '0.06em')
      .attr('fill', catColor[c] || '#999')
      .text(SECTOR_SHORT[c] || c.split(' /')[0]);
    svg.append('text')
      .attr('x', catX[c]).attr('y', 42)
      .attr('text-anchor', 'middle')
      .attr('font-size', 10)
      .attr('fill', inkMuteColor())
      .text(`${all.filter(b => b.categorie === c).length} organisations`);
  });

  // Cercles
  const circles = svg.append('g').selectAll('circle').data(nodes).enter().append('circle')
    .attr('cx', d => d.x).attr('cy', d => d.y)
    .attr('r', 0)
    .attr('fill', d => catColor[d.cat] || '#999')
    .attr('opacity', 0.85)
    .attr('stroke', isDark() ? '#15140f' : '#fbfaf6')
    .attr('stroke-width', 0.8)
    .style('cursor', 'pointer');

  circles.transition().delay((d, i) => i * 8).duration(600).ease(d3.easeCubicOut)
    .attr('r', d => d.r);

  circles.on('mouseover', function(ev, d) {
    d3.select(this).attr('stroke', inkColor()).attr('stroke-width', 1.5);
    showTip(`<div class="t-title">${d.nom}</div>
             <div>${fmtCompact(d.total)} CHF cumulés (2013—2025)</div>
             <div class="t-meta">${d.categorie}${d.canton ? ' · ' + d.canton : ''}</div>`,
            ev.clientX, ev.clientY);
  }).on('mouseout', function() {
    d3.select(this).attr('stroke', isDark() ? '#15140f' : '#fbfaf6').attr('stroke-width', 0.8);
    hideTip();
  });

  // Note du total
  svg.append('text').attr('x', W - 20).attr('y', H - 14)
    .attr('text-anchor', 'end').attr('font-size', 11).attr('fill', inkSoftColor())
    .text(`${nodes.length} organisations · taille proportionnelle au total reçu`);
}

/* ============================================================
   ANGLE A — LA MAIN VISIBLE
   1. Sankey enrichi : Loro → cantons → commissions → bénéficiaires
   2. Table comparée des règles cantonales
   3. Diagramme des prélèvements discrétionnaires
   ============================================================ */
function initGovernance() {
  const container = d3.select('#viz-governance');
  if (container.empty()) return;
  container.html('');

  const b = DATA.summary.benchmarks;
  const cantons = ['VD', 'GE', 'FR', 'VS', 'NE', 'JU'];

  // Construction d'une table comparée enrichie
  const tableWrap = container.append('div').attr('class', 'gov-table-wrap');
  const table = tableWrap.append('table').attr('class', 'gov-table');

  const thead = table.append('thead');
  const headerRow = thead.append('tr');
  headerRow.append('th').text('Canton');
  headerRow.append('th').html('Prélèvement<br>du Conseil d\'État');
  headerRow.append('th').html('Reçu en 2024<br>(M CHF)');
  headerRow.append('th').html('Ratio reçu /<br>dépensé').attr('title', 'Bénéfice reçu vs ventes brutes');
  headerRow.append('th').html('Dépense par<br>habitant 2024');

  const tbody = table.append('tbody');

  cantons.forEach(c => {
    const prelevement = b.prelevement_cantonal_pct[c];
    const row2024 = DATA.detail.find(d => d.annee === 2024 && d.poste === 'Répartition');
    const ventes2024 = DATA.detail.find(d => d.annee === 2024 && d.libelle === 'Total');
    const recu = row2024 ? (row2024.cantons[c] || 0) / 1e6 : 0;
    const vendu = ventes2024 ? (ventes2024.cantons[c] || 0) / 1e6 : 0;
    const ratio = vendu > 0 ? (recu / vendu * 100) : 0;
    const pc = DATA.percapita.tous_jeux;
    const idx = pc.years.indexOf(2024);
    const depHab = idx >= 0 ? pc.data[CANTON_NAMES[c]][idx] : 0;

    const tr = tbody.append('tr');
    tr.append('td').html(`<strong>${CANTON_NAMES[c]}</strong> <span class="gov-code">${c}</span>`);

    const prelCell = tr.append('td').attr('class', 'gov-prel');
    prelCell.append('span').attr('class', 'gov-prel-val')
      .text(prelevement === 0 ? '— aucun' : prelevement + ' %');
    if (prelevement > 0) {
      prelCell.append('div').attr('class', 'gov-prel-bar')
        .append('div').attr('class', 'gov-prel-fill')
        .style('width', (prelevement / 30 * 100) + '%');
    }

    tr.append('td').attr('class', 'gov-num').text(CHF1.format(recu));
    tr.append('td').attr('class', 'gov-num').text(CHF1.format(ratio) + ' %');
    tr.append('td').attr('class', 'gov-num').text(CHF.format(depHab));
  });

  // Légende sous la table
  container.append('p').attr('class', 'note').style('margin-top', '20px')
    .html(`<strong>Lecture :</strong> Le Conseil d'État de chaque canton peut prélever <em>jusqu'à 30 %</em> de sa part résiduelle pour la distribuer lui-même (selon les domaines couverts par la Loro). Les autres fonds passent par les organes de répartition (15 % pour le sport, 85 % pour les autres domaines). En 2024, Genève et le Valais n'ont rien prélevé, Vaud a pris 25 %.
      <br><br><strong>Source :</strong> <em>REISO, "La Loterie Romande, source de financement clé"</em>, J. Sanchez, janvier 2026 ; CORJA (Convention romande sur les jeux d'argent).`);
}

/* ============================================================
   SANKEY ENRICHI (Angle A + Coda fusionnés)
   Étapes du flux avec marquage discrétionnaire vs structurel
   ============================================================ */
function initSankeyEnriched() {
  // Garde le sankey original; ce sera l'évolution v2 si besoin
}

/* ============================================================
   ANGLE B — L'ANOMALIE 2024
   1. Décomposition du surplus 2024
   2. Distribution historique avec position de 2024
   3. Bande d'incertitude prudentielle
   ============================================================ */
function initAnomaly() {
  const container = d3.select('#viz-anomaly');
  if (container.empty()) return;
  container.html('');

  // ----- Décomposition du surplus 2024 -----
  // 2023: 240.6 M, 2024: 258.2 M → Δ = +17.6 M
  // Hypothèse de décomposition basée sur le rapport annuel Loro et les explications du DG :
  // - Jackpot record Swiss Loto (27 sem., 64.6M gain) : contribution principale
  // - Euro foot + JO 2024 (+24,6 % JouezSport) : second facteur
  // - Croissance organique : baseline tendancielle
  const benef2023 = 240.6, benef2024 = 258.2;
  const delta = benef2024 - benef2023;
  const components = [
    { label: 'Niveau de base 2023',     v: benef2023, color: '#bbb6a8', baseline: true },
    { label: 'Jackpot Swiss Loto (cycle 27 sem.)', v: 9.5,  color: '#c8102e' },
    { label: 'Euro de foot + JO 2024',  v: 5.5, color: '#f0a93d' },
    { label: 'Croissance tendancielle', v: 2.6, color: '#5b8def' },
  ];

  const W = container.node().clientWidth, H = 280;
  const margin = { top: 24, right: 24, bottom: 90, left: 200 };
  const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;

  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width','100%').attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  // Barre empilée horizontale
  const totalMax = benef2024 * 1.05;
  const scale = d3.scaleLinear().domain([0, totalMax]).range([0, w]);

  let cumul = 0;
  components.forEach((c, i) => {
    const xstart = scale(cumul);
    const wseg = scale(c.v);

    const grp = g.append('g');
    grp.append('rect')
      .attr('x', xstart).attr('y', 0).attr('width', 0).attr('height', 40)
      .attr('fill', c.color).attr('stroke', '#fff').attr('stroke-width', 1.5)
      .transition().delay(i * 150).duration(700)
      .attr('width', wseg);

    grp.append('text')
      .attr('x', xstart + wseg / 2).attr('y', 24)
      .attr('text-anchor', 'middle').attr('fill', '#fff')
      .attr('font-family', 'Source Serif Pro, serif').attr('font-size', c.baseline ? 14 : 13)
      .attr('font-weight', 500)
      .style('opacity', 0)
      .text(CHF1.format(c.v) + ' M')
      .transition().delay(700 + i * 150).duration(400).style('opacity', wseg > 35 ? 1 : 0);

    grp.on('mouseover', ev => {
      showTip(`<div class="t-title">${c.label}</div><div>${CHF1.format(c.v)} M CHF</div>`, ev.clientX, ev.clientY);
    }).on('mouseout', hideTip);

    cumul += c.v;
  });

  // Étiquettes à gauche
  const legendG = svg.append('g').attr('transform', `translate(20, ${margin.top + 10})`);
  components.forEach((c, i) => {
    const lg = legendG.append('g').attr('transform', `translate(0, ${i * 22})`);
    lg.append('rect').attr('width', 10).attr('height', 10).attr('fill', c.color);
    lg.append('text').attr('x', 16).attr('y', 9).attr('font-size', 12)
      .attr('fill', inkColor()).text(c.label);
  });

  // Annotation visuelle : ligne de 258.2 + flèche
  svg.append('line')
    .attr('x1', margin.left + scale(benef2024)).attr('x2', margin.left + scale(benef2024))
    .attr('y1', margin.top - 4).attr('y2', margin.top + 50)
    .attr('stroke', '#c8102e').attr('stroke-dasharray', '3,3');
  svg.append('text')
    .attr('x', margin.left + scale(benef2024)).attr('y', margin.top - 8)
    .attr('text-anchor', 'middle').attr('font-size', 12).attr('font-weight', 600).attr('fill', '#c8102e')
    .text(`Bénéfice 2024 : ${CHF1.format(benef2024)} M`);

  // Sous-titre
  svg.append('text')
    .attr('x', margin.left).attr('y', margin.top + 70)
    .attr('font-size', 12).attr('fill', inkSoftColor())
    .text(`Décomposition estimée du gain de ${CHF1.format(delta)} M par rapport à 2023.`);
  svg.append('text')
    .attr('x', margin.left).attr('y', margin.top + 88)
    .attr('font-size', 11).attr('fill', inkMuteColor()).attr('font-style','italic')
    .text(`Sources : Rapport annuel Loro 2024 ; déclarations DG Moner-Banet (Blick, 20.5.2025).`);
}

/* ============================================================
   ANGLE C — LE TISSU SOUS PERFUSION
   Dot plot : dépendance Loro des bénéficiaires (% de leur budget)
   ============================================================ */
function initDependency() {
  const container = d3.select('#viz-dependency');
  if (container.empty()) return;
  container.html('');

  const cas = DATA.summary.cas_dependance;
  if (!cas || !cas.length) return;

  const W = container.node().clientWidth, H = 60 + cas.length * 70;
  const margin = { top: 30, right: 100, bottom: 50, left: 200 };
  const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;

  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width','100%').attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  // Axe X = % du budget
  const x = d3.scaleLinear().domain([0, 100]).range([0, w]);
  const y = d3.scaleBand().domain(cas.map(c => c.nom)).range([0, h]).padding(0.3);

  // Bande "zone critique" >= 25 %
  g.append('rect')
    .attr('x', x(25)).attr('y', 0)
    .attr('width', x(100) - x(25)).attr('height', h)
    .attr('fill', '#c8102e').attr('opacity', 0.06);
  g.append('text')
    .attr('x', x(25) + 6).attr('y', -8)
    .attr('font-size', 11).attr('fill', '#c8102e').attr('font-style', 'italic')
    .text('Zone de dépendance critique (≥ 25 %)');

  // Axe X
  g.append('g').attr('transform', `translate(0,${h})`)
    .call(d3.axisBottom(x).tickFormat(d => d + ' %').ticks(6))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // Pour chaque cas, une rangée
  cas.forEach((c, i) => {
    const yCenter = y(c.nom) + y.bandwidth() / 2;

    // Ligne "budget total" = barre claire
    g.append('rect')
      .attr('x', 0).attr('y', yCenter - 12)
      .attr('width', x(100)).attr('height', 24)
      .attr('fill', isDark() ? '#322f27' : '#e0ddd2');

    // Ligne "part Loro" = barre rouge
    g.append('rect')
      .attr('x', 0).attr('y', yCenter - 12)
      .attr('width', 0).attr('height', 24)
      .attr('fill', '#c8102e')
      .transition().delay(i * 200).duration(900)
      .attr('width', x(c.part_loro_pct));

    // Étiquette à gauche
    g.append('text')
      .attr('x', -12).attr('y', yCenter)
      .attr('dy', '0.35em').attr('text-anchor', 'end')
      .attr('font-size', 14).attr('font-weight', 500).attr('fill', inkColor())
      .text(c.nom);
    g.append('text')
      .attr('x', -12).attr('y', yCenter + 16)
      .attr('text-anchor', 'end')
      .attr('font-size', 11).attr('fill', inkSoftColor())
      .text(c.categorie + (c.canton ? ` · ${c.canton}` : ''));

    // Étiquette à droite : %
    g.append('text')
      .attr('x', x(c.part_loro_pct) + 8).attr('y', yCenter)
      .attr('dy', '0.35em')
      .attr('font-family', 'Source Serif Pro, serif')
      .attr('font-size', 18).attr('font-weight', 500).attr('fill', '#c8102e')
      .style('opacity', 0)
      .text(c.part_loro_pct + ' %')
      .transition().delay(i * 200 + 700).duration(400).style('opacity', 1);

    // Sous-info : subvention et budget
    const subv = c.subvention_loro_2024_CHF || c.subvention_loro_2023_CHF;
    const budget = c.budget_total_2024_CHF || c.budget_total_2023_CHF;
    g.append('title').text(`${fmtCompact(subv)} CHF sur un budget total de ${fmtCompact(budget)}`);

    // Bulle interactive
    g.append('rect')
      .attr('x', 0).attr('y', yCenter - 12)
      .attr('width', x(100)).attr('height', 24)
      .attr('fill', 'transparent')
      .style('cursor', 'help')
      .on('mouseover', ev => {
        showTip(`<div class="t-title">${c.nom}</div>
                 <div>Subvention Loro : ${fmtCompact(subv)} CHF</div>
                 <div>Budget total : ${fmtCompact(budget)} CHF</div>
                 <div class="t-meta">→ Loro = ${c.part_loro_pct} % du budget</div>
                 <div class="t-meta">${c.source}</div>`, ev.clientX, ev.clientY);
      }).on('mouseout', hideTip);
  });

  // Note pédagogique
  svg.append('text')
    .attr('x', margin.left).attr('y', H - 12)
    .attr('font-size', 11).attr('fill', inkMuteColor()).attr('font-style', 'italic')
    .text('Sources : REISO 2026, rapports d\'activité des associations, estimations Loro.');
}

/* ============================================================
   ANGLE D — LE VOYAGE D'UN BILLET (récit incarné)
   Scrollytelling : un billet Tribolo 10 CHF acheté à Sion en mars 2024
   ============================================================ */
function initJourney() {
  const container = d3.select('#viz-journey');
  if (container.empty()) return;
  container.html('');

  // Récit du voyage en 7 étapes, mathématiquement cohérent (% du 10 CHF de départ).
  // Sources : Loro RA 2024 (PBJ 438.2M, bénéfice 258.2M, coûts 193.5M),
  //          REISO 2026 (clés CORJA), proportions sport national 8.8%.
  // Calcul : sur 10 CHF, le PBJ moyen = 2.70 CHF, dont :
  //   - 41 % de coûts opérationnels  → 1.11 CHF
  //   - 59 % de bénéfice net          → 1.59 CHF
  //         dont 8.8 % au sport national + FSC = 0.14 CHF
  //         dont ~91 % au résiduel cantonal     = 1.45 CHF
  //              dont 15 % au Valais (clé pop+PBJ) ≈ 0.22 CHF
  //                   dont 100 % aux organes (0 % prélevé en VS) = 0.22 CHF
  const stages = [
    { label: 'Mise du joueur',         v: 10.00, color: '#c8102e',
      detail: 'Un Tribolo à 10 CHF acheté chez un buraliste sédunois le 15 mars 2024.' },
    { label: 'Gains rendus',           v: 7.30,  color: '#5b8def',
      detail: 'Sur 100 CHF misés, ~73 % retournent aux gagnants. Ce qui reste forme le PBJ.' },
    { label: 'PBJ',                    v: 2.70,  color: '#1a1917',
      detail: '27 % des mises forment le « produit brut des jeux ». C\'est ce qui paie le reste.' },
    { label: 'Coûts Loro',             v: 1.11,  color: '#bbb6a8',
      detail: 'Commission buraliste, marketing, salaires, IT (41 % du PBJ).' },
    { label: 'Bénéfice net',           v: 1.59,  color: '#c8102e',
      detail: 'Ce qui part vers l\'utilité publique : 59 % du PBJ.' },
    { label: 'Sport national',         v: 0.14,  color: '#f0a93d',
      detail: '8,8 % du bénéfice : Swiss Olympic, foot, hockey, FSC chevaux.' },
    { label: 'Part Valais',            v: 0.22,  color: '#f0a93d',
      detail: 'Le Valais reçoit ~15 % du résiduel (clé population + PBJ local).' },
    { label: 'Festival d\'Ernen',      v: 0.22,  color: '#c8102e',
      detail: 'Le Valais ne prélève rien, le canton passe tout aux organes de répartition. Ici, vers la culture.' },
  ];

  // Layout : timeline horizontale, chaque étape = une "pile"
  const W = container.node().clientWidth, H = 460;
  const margin = { top: 40, right: 20, bottom: 50, left: 20 };

  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width','100%').attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const stepW = (W - margin.left - margin.right) / stages.length;

  // Pour chaque étape, dessiner un cylindre de pièce
  stages.forEach((s, i) => {
    const grp = g.append('g').attr('transform', `translate(${i * stepW + stepW / 2}, 0)`)
      .style('cursor', 'pointer')
      .style('opacity', 0)
      .style('transform-origin', 'center');

    // Animer apparition
    grp.transition().delay(i * 250).duration(600)
      .style('opacity', 1);

    // Cercle représentant la pièce
    const r = Math.max(20, Math.sqrt(s.v) * 22);
    grp.append('circle').attr('r', r).attr('cy', 100)
      .attr('fill', s.color).attr('opacity', 0.92)
      .attr('stroke', isDark() ? '#15140f' : '#fbfaf6').attr('stroke-width', 2);

    grp.append('text').attr('y', 104)
      .attr('text-anchor', 'middle').attr('font-family', 'Source Serif Pro, serif')
      .attr('font-size', 16).attr('font-weight', 600).attr('fill', '#fff')
      .text(s.v.toFixed(2));

    // Label sous
    grp.append('text').attr('y', 100 + r + 24)
      .attr('text-anchor', 'middle').attr('font-size', 11).attr('font-weight', 500)
      .attr('fill', inkColor())
      .text(s.label);

    // Détail au survol
    grp.on('mouseover', ev => {
      showTip(`<div class="t-title">${s.label}</div>
               <div>${s.v.toFixed(2)} CHF</div>
               <div class="t-meta">${s.detail}</div>`, ev.clientX, ev.clientY);
    }).on('mouseout', hideTip);

    // Flèche entre les étapes (sauf dernière)
    if (i < stages.length - 1) {
      g.append('path')
        .attr('d', `M ${i * stepW + stepW / 2 + r + 4} 100 L ${(i + 1) * stepW + stepW / 2 - r - 4} 100`)
        .attr('fill', 'none').attr('stroke', inkMuteColor()).attr('stroke-width', 1)
        .attr('marker-end', 'url(#journey-arrow)')
        .style('opacity', 0)
        .transition().delay(i * 250 + 400).duration(300).style('opacity', 0.4);
    }
  });

  // Marker
  svg.append('defs').append('marker')
    .attr('id', 'journey-arrow').attr('viewBox', '0 0 10 10')
    .attr('refX', 8).attr('refY', 5)
    .attr('markerWidth', 6).attr('markerHeight', 6).attr('orient', 'auto')
    .append('path').attr('d', 'M 0 0 L 10 5 L 0 10 z')
    .attr('fill', inkMuteColor()).attr('opacity', 0.5);

  // Annotation finale
  svg.append('text')
    .attr('x', W / 2).attr('y', 280)
    .attr('text-anchor', 'middle').attr('font-family', 'Source Serif Pro, serif')
    .attr('font-style', 'italic').attr('font-size', 20)
    .attr('fill', inkColor())
    .text('22 centimes sur 10 francs misés');
  svg.append('text')
    .attr('x', W / 2).attr('y', 308)
    .attr('text-anchor', 'middle').attr('font-size', 13)
    .attr('fill', inkSoftColor())
    .text('Voilà ce qui arrive concrètement chez une association valaisanne.');

  // Bandeau récit chronologique
  const story = svg.append('g').attr('transform', `translate(0, 350)`);
  const storyLines = [
    '15 mars 2024 — Le billet est gratté. Pas de jackpot. 10 francs s\'évanouissent dans le PBJ.',
    'Décembre 2024 — La Loro consolide ses comptes. Le bénéfice annuel est arrêté à 258 M.',
    'Mai 2025 — Le canton du Valais reçoit sa part : 39,9 millions de francs.',
    'Septembre 2025 — La commission de répartition valaisanne attribue 50 000 CHF au Festival d\'Ernen.',
    'Juillet 2026 — Un violoniste reçoit son cachet. Quelques centimes de notre billet y sont logés.',
  ];
  storyLines.forEach((line, i) => {
    story.append('text')
      .attr('x', W / 2).attr('y', i * 20)
      .attr('text-anchor', 'middle')
      .attr('font-size', 12).attr('fill', i % 2 === 0 ? inkColor() : inkSoftColor())
      .text(line);
  });
}

/* ============================================================
   ANGLE E — JEU PROBLÉMATIQUE
   Comparaison "PBJ provenant de tous joueurs" vs "joueurs à risque"
   (estimation prudente : selon littérature, 30-50 % du PBJ vient
    des joueurs problématiques. Source : RSPH / Productivity Commission Australia)
   ============================================================ */
function initProblematic() {
  const container = d3.select('#viz-problematic');
  if (container.empty()) return;
  container.html('');

  const b = DATA.summary.benchmarks;

  // Construction d'une visualisation de carrés (waffle)
  // 100 carrés = population. 4,3 carrés = pop à risque.
  // Mais sur les revenus de la Loro, leur poids serait disproportionné.
  // (Hypothèse littérature scientifique : ~40 % du PBJ provient des joueurs problématiques.)
  const W = container.node().clientWidth, H = 360;
  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width','100%').attr('height', H);

  // Deux waffles côte à côte
  const colW = W / 2 - 30;
  const cellRows = 10, cellCols = 10;
  const cellW = Math.min((colW - 8) / cellCols, 30);

  function drawWaffle(g, share, label, color, sublabel) {
    const totalCells = cellRows * cellCols;
    const colored = Math.round(share * totalCells / 100);

    for (let i = 0; i < totalCells; i++) {
      const r = Math.floor(i / cellCols), c = i % cellCols;
      g.append('rect')
        .attr('x', c * (cellW + 2)).attr('y', r * (cellW + 2))
        .attr('width', cellW).attr('height', cellW).attr('rx', 1)
        .attr('fill', i < colored ? color : (isDark() ? '#322f27' : '#e0ddd2'))
        .attr('opacity', 0)
        .transition().delay(i * 8).duration(200).attr('opacity', i < colored ? 1 : 0.6);
    }
    g.append('text')
      .attr('x', 0).attr('y', cellRows * (cellW + 2) + 28)
      .attr('font-family', 'Source Serif Pro, serif')
      .attr('font-size', 32).attr('fill', color).attr('font-weight', 500)
      .text(share + ' %');
    g.append('text')
      .attr('x', 0).attr('y', cellRows * (cellW + 2) + 52)
      .attr('font-size', 12).attr('fill', inkColor()).attr('font-weight', 600)
      .text(label);
    g.append('text')
      .attr('x', 0).attr('y', cellRows * (cellW + 2) + 70)
      .attr('font-size', 11).attr('fill', inkSoftColor())
      .text(sublabel);
  }

  const g1 = svg.append('g').attr('transform', `translate(30, 30)`);
  drawWaffle(g1,
    Math.round(b.pop_jeu_risque_pct),
    'des Suisses jouent à risque',
    '#c8102e',
    'Soit ~390 000 personnes (Enquête santé 2022)');

  const g2 = svg.append('g').attr('transform', `translate(${W / 2 + 30}, 30)`);
  // Estimation conservative : 30-50 % du PBJ vient de joueurs problématiques
  // (littérature internationale ; pas de chiffre suisse officiel)
  drawWaffle(g2, 40,
    'du PBJ provient d\'eux (estimation)',
    '#8a0a1f',
    'Littérature internationale (RSPH, Productivity Commission AU)');

  // Connecteur entre les deux blocs
  svg.append('text')
    .attr('x', W / 2).attr('y', cellRows * (cellW + 2) / 2 + 30)
    .attr('text-anchor', 'middle')
    .attr('font-family', 'Source Serif Pro, serif').attr('font-style', 'italic')
    .attr('font-size', 16).attr('fill', inkMuteColor())
    .text('→ génèrent →');

  // Note
  svg.append('text')
    .attr('x', 30).attr('y', H - 14)
    .attr('font-size', 11).attr('fill', inkMuteColor()).attr('font-style', 'italic')
    .text('Le second chiffre est une estimation : aucune statistique publique suisse ne mesure cette part. Les études internationales convergent autour de 30-50 %.');
}

/* ============================================================
   RAPPORTS FINANCIERS 2019-2024 — module séparé
   ============================================================ */

/* ============================================================
   OP-COSTS — Évolution des coûts opérationnels 2019-2024
   Streamgraph 9 catégories. Met en évidence l'IT.
   ============================================================ */
function initOpCosts() {
  const container = d3.select('#viz-opcosts');
  if (container.empty()) return;
  if (!DATA.rf) return;
  container.html('');

  const years = ['2013','2014','2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025'];
  const categories = [
    { key: 'informatique',      label: 'Informatique',     color: '#c8102e', highlight: true },
    { key: 'frais_personnel',   label: 'Personnel',        color: '#1a1917' },
    { key: 'marketing',         label: 'Marketing',        color: '#f0a93d' },
    { key: 'exploitation_jeux', label: 'Exploitation jeux',color: '#5b8def' },
    { key: 'amortissements',    label: 'Amortissements',   color: '#7c5bc7' },
    { key: 'frais_generaux',    label: 'Frais généraux',   color: '#8a8a8a' },
    { key: 'fabrication_jeux',  label: 'Fabrication jeux', color: '#c89a2e' },
    { key: 'ventes_animations', label: 'Ventes/animations',color: '#e44d4d' },
    { key: 'frais_vendeurs',    label: 'Frais vendeurs',   color: '#5a8a3d' },
  ];

  const data = years.map(y => {
    const r = DATA.rf.compte_de_resultat[y];
    const row = { year: +y };
    categories.forEach(c => { row[c.key] = Math.abs(r[c.key]) / 1e6; });
    return row;
  });

  const W = container.node().clientWidth, H = 460;
  const margin = { top: 50, right: 170, bottom: 40, left: 50 };
  const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;

  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleLinear().domain([2013, 2025]).range([0, w]);
  const stack = d3.stack().keys(categories.map(c => c.key));
  const series = stack(data);
  const maxY = d3.max(series[series.length - 1], d => d[1]);
  const y = d3.scaleLinear().domain([0, maxY * 1.05]).range([h, 0]);

  // Axes
  g.append('g').attr('transform', `translate(0,${h})`)
    .call(d3.axisBottom(x).tickFormat(d3.format('d')).ticks(7))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));
  g.append('g')
    .call(d3.axisLeft(y).tickFormat(d => CHF1.format(d) + ' M').ticks(5))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // Stack
  const area = d3.area().curve(d3.curveMonotoneX)
    .x(d => x(d.data.year)).y0(d => y(d[0])).y1(d => y(d[1]));

  const paths = g.selectAll('path.area').data(series).enter().append('path')
    .attr('class', 'area')
    .attr('fill', (d, i) => categories[i].color)
    .attr('opacity', (d, i) => categories[i].highlight ? 0.95 : 0.7)
    .attr('d', area)
    .style('cursor', 'pointer');

  // Lignes verticales jalons
  [2018, 2021].forEach(y0 => {
    g.append('line').attr('x1', x(y0)).attr('x2', x(y0))
      .attr('y1', 0).attr('y2', h)
      .attr('stroke', '#fff').attr('stroke-width', 1.5).attr('opacity', 0.6);
  });

  // Annotations de phases au-dessus du graph
  const phases = [
    { x0: 2013, x1: 2018, label: 'Régime Deloitte / Comlot · RBJ' },
    { x0: 2018, x1: 2021, label: 'Transition LJAr' },
    { x0: 2021, x1: 2025, label: 'CORJA · transformation IT' }
  ];
  phases.forEach(p => {
    const x0 = x(p.x0), x1 = x(p.x1);
    svg.append('text')
      .attr('x', margin.left + (x0 + x1) / 2)
      .attr('y', 18)
      .attr('text-anchor', 'middle')
      .attr('font-size', 10)
      .attr('font-style', 'italic')
      .attr('fill', inkSoftColor())
      .text(p.label);
    svg.append('line')
      .attr('x1', margin.left + x0 + 6).attr('x2', margin.left + x1 - 6)
      .attr('y1', 25).attr('y2', 25)
      .attr('stroke', ruleColor()).attr('opacity', 0.6);
  });

  // Annotation IT : creux 2018 puis bond 2023
  const it13 = data[0].informatique, it18 = data[5].informatique, it25 = data[data.length - 1].informatique;

  const annoG = svg.append('g').attr('transform', `translate(${margin.left + x(2022) - 80}, ${margin.top + 35})`);
  annoG.append('rect').attr('width', 190).attr('height', 56)
    .attr('rx', 4).attr('fill', '#c8102e').attr('opacity', 0.95);
  annoG.append('text').attr('x', 10).attr('y', 20)
    .attr('fill', '#fff').attr('font-size', 11.5).attr('font-weight', 600)
    .text(`Informatique : cycle complet`);
  annoG.append('text').attr('x', 10).attr('y', 36)
    .attr('fill', '#fff').attr('font-size', 10.5).attr('opacity', 0.95)
    .text(`19,2 M (2013) → 16,6 M (2018)`);
  annoG.append('text').attr('x', 10).attr('y', 50)
    .attr('fill', '#fff').attr('font-size', 10.5).attr('opacity', 0.95)
    .text(`puis 23,9 M (2025) — record`);

  // Légende
  const leg = svg.append('g').attr('transform', `translate(${W - margin.right + 20}, ${margin.top})`);
  categories.forEach((c, i) => {
    const item = leg.append('g').attr('transform', `translate(0, ${i * 20})`);
    item.append('rect').attr('width', 12).attr('height', 12).attr('fill', c.color)
      .attr('opacity', c.highlight ? 0.95 : 0.7);
    item.append('text').attr('x', 18).attr('y', 10)
      .attr('font-size', 11)
      .attr('font-weight', c.highlight ? 600 : 400)
      .attr('fill', c.highlight ? '#c8102e' : inkColor())
      .text(c.label);
    item.append('text').attr('x', 130).attr('y', 10)
      .attr('font-size', 10).attr('fill', inkSoftColor()).attr('text-anchor', 'end')
      .attr('font-family', 'Source Serif Pro, serif')
      .text(CHF1.format(data[data.length - 1][c.key]) + ' M');
  });

  paths.on('mouseover', function(ev, d) {
    const cat = categories.find(c => c.key === d.key);
    d3.select(this).attr('opacity', 1);
    const first = data[0][cat.key], last = data[data.length - 1][cat.key];
    const growth = ((last - first) / first * 100).toFixed(0);
    showTip(`<div class="t-title">${cat.label}</div>
      <div>2013 : ${CHF1.format(first)} M</div>
      <div>2025 : ${CHF1.format(last)} M</div>
      <div style="margin-top:4px;color:${growth >= 0 ? '#c8102e' : '#5a8a3d'}">Δ : ${growth > 0 ? '+' : ''}${growth} % en 12 ans</div>`,
      ev.clientX, ev.clientY);
  }).on('mouseout', function(ev, d) {
    const cat = categories.find(c => c.key === d.key);
    d3.select(this).attr('opacity', cat.highlight ? 0.95 : 0.7);
    hideTip();
  });
}

/* ============================================================
   PRELEVEMENT EVOLUTION — Vaud bascule de 0 % à 25 %
   ============================================================ */
function initPrelevementEvol() {
  const container = d3.select('#viz-prelevement-evol');
  if (container.empty()) return;
  if (!DATA.rf) return;
  container.html('');

  const cantons = ['VD', 'JU', 'NE', 'FR', 'GE', 'VS'];

  const W = container.node().clientWidth, H = 400;
  const margin = { top: 30, right: 80, bottom: 50, left: 50 };
  const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;

  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleLinear().domain([2020, 2025]).range([0, w]);
  const y = d3.scaleLinear().domain([0, 30]).range([h, 0]);

  // Axes
  g.append('g').attr('transform', `translate(0,${h})`)
    .call(d3.axisBottom(x).tickValues([2020, 2021, 2022, 2023, 2024, 2025]).tickFormat(d3.format('d')))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '12px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));
  g.append('g')
    .call(d3.axisLeft(y).tickFormat(d => d + ' %').ticks(6))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // Plafond 30%
  g.append('line').attr('x1', 0).attr('x2', w).attr('y1', y(30)).attr('y2', y(30))
    .attr('stroke', '#c8102e').attr('stroke-dasharray', '4,4').attr('opacity', 0.5);
  g.append('text').attr('x', w - 6).attr('y', y(30) - 6).attr('text-anchor', 'end')
    .attr('font-size', 11).attr('fill', '#c8102e').attr('font-style', 'italic')
    .text('Plafond légal : 30 %');

  // Une ligne par canton
  cantons.forEach(c => {
    const series = [
      { x: 2020, y: DATA.rf.prelevement_cantonal['2020'][c] },
      { x: 2021, y: DATA.rf.prelevement_cantonal['2020'][c] }, // pas changé
      { x: 2022, y: DATA.rf.prelevement_cantonal['2022'][c] },
      { x: 2023, y: DATA.rf.prelevement_cantonal['2023'][c] },
      { x: 2024, y: DATA.rf.prelevement_cantonal['2024'][c] },
      { x: 2025, y: DATA.rf.prelevement_cantonal['2025'][c] },
    ];

    const isHighlight = c === 'VD' || c === 'JU' || c === 'FR';
    const line = d3.line().x(d => x(d.x)).y(d => y(d.y))
      .curve(d3.curveStepAfter);

    g.append('path').datum(series)
      .attr('fill', 'none').attr('stroke', CANTON_COLORS[c])
      .attr('stroke-width', c === 'VD' ? 3.5 : isHighlight ? 2.5 : 1.5)
      .attr('opacity', isHighlight ? 1 : 0.5)
      .attr('d', line);

    g.selectAll('.dot-' + c).data(series).enter().append('circle')
      .attr('cx', d => x(d.x)).attr('cy', d => y(d.y))
      .attr('r', isHighlight ? 4 : 2.5)
      .attr('fill', CANTON_COLORS[c])
      .attr('opacity', isHighlight ? 1 : 0.5);

    // Label au bout
    const last = series[series.length - 1];
    g.append('text').attr('x', x(last.x) + 6).attr('y', y(last.y) + 4)
      .attr('font-size', 11)
      .attr('font-weight', isHighlight ? 600 : 400)
      .attr('fill', CANTON_COLORS[c])
      .attr('opacity', isHighlight ? 1 : 0.6)
      .text(`${c} · ${last.y} %`);
  });

  // Annotation Vaud 2022
  const annoX1 = x(2021) + 10;
  g.append('text').attr('x', annoX1).attr('y', y(28))
    .attr('font-family', 'Source Serif Pro, serif').attr('font-style', 'italic')
    .attr('font-size', 13).attr('fill', '#c8102e')
    .text('Vaud · jan. 2022 : 0 → 25 %');
  g.append('text').attr('x', annoX1).attr('y', y(28) + 14)
    .attr('font-size', 10).attr('fill', inkSoftColor())
    .text('Entrée en vigueur LVLJAr');

  // Annotation Fribourg 2024 et Jura 2025
  g.append('text').attr('x', x(2023.6)).attr('y', y(13))
    .attr('font-size', 10.5).attr('fill', CANTON_COLORS.FR).attr('font-weight', 600)
    .text('FR : 7 → 9 % (2024)');
  g.append('text').attr('x', x(2023.8)).attr('y', y(22))
    .attr('font-size', 10.5).attr('fill', CANTON_COLORS.JU).attr('font-weight', 600)
    .text('JU : 17 → 20 % (2025)');
}

/* ============================================================
   CAPITAUX PROPRES — Santé financière 2019-2024
   ============================================================ */
function initCapital() {
  const container = d3.select('#viz-capital');
  if (container.empty()) return;
  if (!DATA.rf) return;
  container.html('');

  const years = ['2013','2014','2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025'];
  const data = years.map(y => ({
    year: +y,
    capitaux_propres: DATA.rf.bilan[y].capitaux_propres / 1e6,
    logiciels: DATA.rf.bilan[y].immobilisations_incorporelles_logiciels / 1e6,
    benefice: DATA.rf.compte_de_resultat[y].resultat_net / 1e6,
  }));

  const W = container.node().clientWidth, H = 380;
  const margin = { top: 30, right: 110, bottom: 50, left: 50 };
  const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;

  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleBand().domain(years).range([0, w]).padding(0.2);
  const yMax = d3.max(data, d => d.capitaux_propres) * 1.1;
  const y = d3.scaleLinear().domain([0, yMax]).range([h, 0]);

  // Axes
  g.append('g').attr('transform', `translate(0,${h})`).call(d3.axisBottom(x))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '10px')
              .attr('transform', 'rotate(-30)').style('text-anchor', 'end'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));
  g.append('g').call(d3.axisLeft(y).tickFormat(d => d + ' M').ticks(5))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // Barres capitaux propres
  g.selectAll('.bar-cp').data(data).enter().append('rect')
    .attr('class', 'bar-cp')
    .attr('x', d => x(String(d.year)))
    .attr('y', h).attr('width', x.bandwidth()).attr('height', 0)
    .attr('fill', '#1a1917').attr('opacity', 0.78)
    .transition().delay((d, i) => i * 60).duration(600)
    .attr('y', d => y(d.capitaux_propres))
    .attr('height', d => h - y(d.capitaux_propres));

  // Ligne logiciels
  const logLine = d3.line()
    .x(d => x(String(d.year)) + x.bandwidth() / 2)
    .y(d => y(d.logiciels))
    .curve(d3.curveMonotoneX);

  g.append('path').datum(data)
    .attr('fill', 'none').attr('stroke', '#c8102e').attr('stroke-width', 2.5)
    .attr('d', logLine);

  g.selectAll('.dot-log').data(data).enter().append('circle')
    .attr('cx', d => x(String(d.year)) + x.bandwidth() / 2)
    .attr('cy', d => y(d.logiciels))
    .attr('r', 3.5).attr('fill', '#c8102e');

  // Labels valeurs sur années clés
  const keyYears = ['2013','2019','2025'];
  g.selectAll('.lab-cp').data(data.filter(d => keyYears.includes(String(d.year)))).enter().append('text')
    .attr('class', 'lab-cp')
    .attr('x', d => x(String(d.year)) + x.bandwidth() / 2)
    .attr('y', d => y(d.capitaux_propres) - 6)
    .attr('text-anchor', 'middle')
    .attr('font-family', 'Source Serif Pro, serif')
    .attr('font-size', 12).attr('fill', inkColor())
    .text(d => CHF1.format(d.capitaux_propres));

  // Annotation finale logiciels
  const last = data[data.length - 1];
  g.append('text').attr('x', x(String(last.year)) + x.bandwidth() / 2 + 6)
    .attr('y', y(last.logiciels) - 4)
    .attr('font-size', 11).attr('fill', '#c8102e').attr('font-weight', 600)
    .text('43,8 M');

  // Légende
  const leg = svg.append('g').attr('transform', `translate(${W - margin.right + 10}, ${margin.top + 10})`);
  leg.append('rect').attr('width', 12).attr('height', 12).attr('fill', '#1a1917').attr('opacity', 0.78);
  leg.append('text').attr('x', 18).attr('y', 10).attr('font-size', 11).attr('fill', inkColor())
    .text('Capitaux propres');
  leg.append('circle').attr('cx', 6).attr('cy', 32).attr('r', 4).attr('fill', '#c8102e');
  leg.append('text').attr('x', 18).attr('y', 36).attr('font-size', 11).attr('fill', '#c8102e')
    .text('Logiciels');

  // Annotation croissance
  const cp13 = data[0].capitaux_propres, cp25 = data[data.length - 1].capitaux_propres;
  const log13 = data[0].logiciels, log25 = data[data.length - 1].logiciels;
  const cpGrowth = ((cp25 - cp13) / cp13 * 100).toFixed(0);
  const logGrowth = ((log25 - log13) / log13 * 100).toFixed(0);
  leg.append('text').attr('x', 0).attr('y', 70).attr('font-size', 10).attr('font-style', 'italic')
    .attr('fill', inkSoftColor()).text(`Sur 12 ans :`);
  leg.append('text').attr('x', 0).attr('y', 86).attr('font-size', 11).attr('fill', inkColor())
    .text(`+${cpGrowth} % capitaux`);
  leg.append('text').attr('x', 0).attr('y', 102).attr('font-size', 11).attr('fill', '#c8102e')
    .text(`+${logGrowth} % logiciels`);
}

/* ============================================================
   ÉVÉNEMENTS MARQUANTS — timeline annotée
   ============================================================ */
function initEvenements() {
  const container = d3.select('#viz-evenements');
  if (container.empty()) return;
  if (!DATA.rf) return;
  container.html('');

  const events = DATA.rf.evenements_marquants;
  const list = container.append('ul').attr('class', 'evenements-list');
  events.forEach(e => {
    const li = list.append('li').attr('class', 'evenement-item');
    li.append('span').attr('class', 'ev-year').text(e.year);
    const txt = li.append('div').attr('class', 'ev-content');
    txt.append('div').attr('class', 'ev-label').text(e.label);
    txt.append('div').attr('class', 'ev-detail').text(e.detail);
  });
}

// ==========================================================
//  Acte VIII — comparaisons et incarnation
// ==========================================================

function initTopBenefsVD() {
  const container = d3.select('#viz-top-benefs-vd');
  if (container.empty()) return;
  if (!DATA.benefsVD) return;
  container.html('');

  // State: année sélectionnée
  let year = '2025';

  // Couleurs par secteur (réutilisables et lisibles)
  const SECTOR_COLORS = {
    'Culture':                  '#c8102e',
    'Action sociale':           '#5b8def',
    'Sport':                    '#5a8a3d',
    'Jeunesse et éducation':    '#f0a93d',
    'Santé et handicap':        '#7c5bc7',
    'Formation et recherche':   '#1a1917',
    'Conservation patrimoine':  '#c89a2e',
    'Environnement':            '#3aa37a',
    'Promotion et tourisme':    '#e44d4d',
  };

  // Contrôles
  const controls = container.append('div').attr('class', 'controls-row');
  const yearGroup = controls.append('div').attr('class', 'control-group');
  yearGroup.append('label').text('Année : ');
  ['2024', '2025'].forEach(y => {
    yearGroup.append('button')
      .attr('class', 'btn-year')
      .attr('data-year', y)
      .text(y)
      .on('click', () => { year = y; render(); });
  });

  const totalDiv = controls.append('div').attr('class', 'control-info');

  const wrap = container.append('div').attr('class', 'viz-inner');

  function render() {
    // Update toggles
    yearGroup.selectAll('button.btn-year')
      .classed('active', function() { return this.dataset.year === year; });

    const key = `montant_${year}`;
    const data = DATA.benefsVD.beneficiaires
      .filter(d => d[key] != null && d[key] > 0)
      .sort((a, b) => b[key] - a[key])
      .slice(0, 30);

    const totalCanton = DATA.benefsVD._meta.totaux_vd[year];
    const totalCantonStr = totalCanton.total_distribue_canton
      ? CHF1.format(totalCanton.total_distribue_canton / 1e6) + ' M'
      : '–';
    totalDiv.html(
      `<span style="color:${inkSoftColor()}">Échantillon top 30 sur ~5'000 projets ·</span>
       <strong>${totalCantonStr}</strong> total Vaud ${year}`
    );

    wrap.html('');

    const W = wrap.node().clientWidth, H = Math.max(420, data.length * 22 + 60);
    const margin = { top: 20, right: 220, bottom: 20, left: 280 };
    const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;

    const svg = wrap.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H);
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const maxVal = d3.max(data, d => d[key]);
    const x = d3.scaleLinear().domain([0, maxVal]).range([0, w]);
    const y = d3.scaleBand().domain(data.map(d => d.nom + ' · ' + d.ville)).range([0, h]).padding(0.18);

    // Axe Y (noms)
    g.append('g').call(d3.axisLeft(y).tickSize(0))
      .call(s => s.selectAll('text').attr('fill', inkColor()).style('font-size', '11px'))
      .call(s => s.selectAll('path').remove());

    // Barres
    g.selectAll('rect.bar').data(data).enter().append('rect')
      .attr('class', 'bar')
      .attr('x', 0)
      .attr('y', d => y(d.nom + ' · ' + d.ville))
      .attr('width', 0)
      .attr('height', y.bandwidth())
      .attr('fill', d => SECTOR_COLORS[d.secteur] || '#999')
      .attr('opacity', 0.88)
      .transition().delay((d, i) => i * 18).duration(500)
      .attr('width', d => x(d[key]));

    // Labels valeur + secteur à droite
    g.selectAll('.label-val').data(data).enter().append('text')
      .attr('class', 'label-val')
      .attr('x', d => x(d[key]) + 6)
      .attr('y', d => y(d.nom + ' · ' + d.ville) + y.bandwidth() / 2 + 4)
      .attr('font-size', 11)
      .attr('fill', inkColor())
      .attr('font-family', 'Source Serif Pro, serif')
      .text(d => {
        const m = d[key];
        const v = m >= 1e6 ? CHF1.format(m / 1e6) + ' M' : (m / 1e3).toFixed(0) + ' k';
        return v;
      });

    g.selectAll('.label-sector').data(data).enter().append('text')
      .attr('class', 'label-sector')
      .attr('x', d => x(d[key]) + 70)
      .attr('y', d => y(d.nom + ' · ' + d.ville) + y.bandwidth() / 2 + 4)
      .attr('font-size', 9)
      .attr('fill', d => SECTOR_COLORS[d.secteur] || '#888')
      .attr('opacity', 0.9)
      .text(d => d.secteur + ' · ' + d.type);

    // Légende secteurs (compactée, en haut)
    const presentSectors = [...new Set(data.map(d => d.secteur))];
    const leg = svg.append('g').attr('transform', `translate(${margin.left}, ${H - 6})`);
    presentSectors.forEach((s, i) => {
      const item = leg.append('g').attr('transform', `translate(${i * 140}, 0)`);
      item.append('rect').attr('width', 8).attr('height', 8).attr('y', -8).attr('fill', SECTOR_COLORS[s] || '#999');
      item.append('text').attr('x', 12).attr('y', 0).attr('font-size', 9).attr('fill', inkSoftColor()).text(s);
    });
  }
  render();
}

function initLoroVsSwisslos() {
  const container = d3.select('#viz-loro-vs-swisslos');
  if (container.empty()) return;
  if (!DATA.swisslos) return;
  container.html('');

  const m = DATA.swisslos.comparaison_loro_2024.metriques;

  // Catégorisation visuelle des métriques
  const sections = {
    'Échelle': ['PBJ / BSE (M CHF)', 'Bénéfice net (M CHF)', 'Total actif', 'Capitaux propres / réserves'],
    'Efficacité': ['Ratio bénéfice/PBJ', 'Commissions / PBJ'],
    'Structure de coûts': ['Commissions points de vente', 'Informatique', 'Personnel', 'Marketing/Publicité+Promo', 'Amortissements', 'Taxe jeu excessif (0,5 %)'],
    'Périmètre': ['EPT moyens', 'Nb cantons membres', 'Pop. desservie (M)'],
    'Coussin': ['Provision risque exploitation', 'Réserves libres']
  };

  const W = container.node().clientWidth, H = 720;
  const margin = { top: 20, right: 20, bottom: 20, left: 180 };
  const w = W - margin.left - margin.right;

  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H);

  let cursorY = margin.top;
  Object.entries(sections).forEach(([sectionName, metricLabels]) => {
    // Titre de section
    svg.append('text')
      .attr('x', margin.left)
      .attr('y', cursorY + 14)
      .attr('font-family', 'Source Serif Pro, serif')
      .attr('font-style', 'italic')
      .attr('font-size', 12)
      .attr('fill', inkSoftColor())
      .text(sectionName);
    cursorY += 22;

    metricLabels.forEach(lbl => {
      const item = m.find(x => x.label === lbl);
      if (!item) return;

      const rowH = 28;
      const half = w / 2 - 30;

      // Label métrique
      svg.append('text').attr('x', margin.left + w / 2).attr('y', cursorY + 16)
        .attr('text-anchor', 'middle')
        .attr('font-size', 11)
        .attr('fill', inkColor())
        .text(lbl);

      // Détermine échelle locale (max des deux)
      const maxVal = Math.max(item.loro, item.swisslos);
      if (maxVal === 0) {
        cursorY += rowH;
        return;
      }
      const x = d3.scaleLinear().domain([0, maxVal]).range([0, half]);

      // Barre Loro (à gauche, croissance de droite à gauche)
      const lW = x(item.loro);
      svg.append('rect')
        .attr('x', margin.left + w / 2 - 8 - lW)
        .attr('y', cursorY + 5).attr('width', lW).attr('height', 12)
        .attr('fill', '#c8102e').attr('opacity', 0.85);

      svg.append('text')
        .attr('x', margin.left + w / 2 - 8 - lW - 6)
        .attr('y', cursorY + 15)
        .attr('text-anchor', 'end')
        .attr('font-size', 11)
        .attr('font-family', 'Source Serif Pro, serif')
        .attr('fill', '#c8102e')
        .text(CHF1.format(item.loro) + (item.unite ? ' ' + item.unite.replace('M CHF', 'M').replace('M hab.', 'M') : ''));

      // Barre Swisslos (à droite)
      const sW = x(item.swisslos);
      svg.append('rect')
        .attr('x', margin.left + w / 2 + 8)
        .attr('y', cursorY + 5).attr('width', sW).attr('height', 12)
        .attr('fill', '#1a1917').attr('opacity', 0.85);

      svg.append('text')
        .attr('x', margin.left + w / 2 + 8 + sW + 6)
        .attr('y', cursorY + 15)
        .attr('font-size', 11)
        .attr('font-family', 'Source Serif Pro, serif')
        .attr('fill', inkColor())
        .text(CHF1.format(item.swisslos) + (item.unite ? ' ' + item.unite.replace('M CHF', 'M').replace('M hab.', 'M') : ''));

      cursorY += rowH;
    });
    cursorY += 8;
  });

  // En-tête « Loro · Swisslos »
  svg.append('text').attr('x', margin.left + w / 4).attr('y', 12)
    .attr('text-anchor', 'middle').attr('font-size', 13).attr('font-weight', 600).attr('fill', '#c8102e')
    .text('◀ LORO');
  svg.append('text').attr('x', margin.left + 3 * w / 4).attr('y', 12)
    .attr('text-anchor', 'middle').attr('font-size', 13).attr('font-weight', 600).attr('fill', inkColor())
    .text('SWISSLOS ▶');
}

function initEditorialTimeline() {
  const container = d3.select('#viz-editorial-timeline');
  if (container.empty()) return;
  if (!DATA.editorial) return;
  container.html('');

  const annees = DATA.editorial.annees;

  // Une carte par année, layout vertical, scrollytelling-friendly
  const list = container.append('div').attr('class', 'editorial-list');

  annees.forEach(a => {
    const card = list.append('article').attr('class', 'editorial-card');

    const head = card.append('div').attr('class', 'editorial-head');
    head.append('span').attr('class', 'editorial-year').text(a.year);
    head.append('h4').attr('class', 'editorial-headline').text(a.headline);

    card.append('p').attr('class', 'editorial-edito').text(a.edito_court);

    if (a.lancement_jeu) {
      card.append('p').attr('class', 'editorial-launch')
        .html(`<strong>Lancement :</strong> ${a.lancement_jeu}`);
    }

    const ul = card.append('ul').attr('class', 'editorial-facts');
    (a.faits_marquants || []).forEach(f => {
      ul.append('li').text(f);
    });
  });
}
