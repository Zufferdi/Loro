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
    DATA.dependance = await loadJSON('dependance_cantons.json');
    DATA.juraHistoire = await loadJSON('jura_histoire.json');
    // brb2025_full.json (1.7 MB) — load lazily when Acte IX nears the viewport.
    // We don't await here — the initial paint stays fast.
    DATA.brb2025      = null;
    DATA.brb2025_loading = null;

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
    initShareSuisse();
    initTopBenefsVD();
    initLoroVsSwisslos();
    initEditorialTimeline();
    initJuraHistoire();
    initBrbLazyTrigger();   // BRB viz (1.7 MB) — loaded on demand via IntersectionObserver
    initJourney();
    initSankey();
    initReadingProgress();
    initRevealOnScroll();
    initBuildDate();
    initA11yDecoration();
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

  // Use a generous viewBox so the graphic always renders, regardless of parent height
  const W = 1100, H = 620;
  const margin = { top: 40, right: 60, bottom: 50, left: 70 };
  const w = W - margin.left - margin.right;
  const h = H - margin.top - margin.bottom;

  const svg = container.append('svg')
    .attr('viewBox', `0 0 ${W} ${H}`)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .attr('width', '100%').attr('height', '100%')
    .style('max-height', '85vh')
    .style('display', 'block');

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const hist = DATA.historique.filter(d => d.benefice_M != null);

  const x = d3.scaleLinear().domain([1938, 2026]).range([0, w]);
  const y = d3.scaleLinear().domain([0, 280]).range([h, 0]).nice();

  // Grille horizontale
  g.selectAll('.grid').data(y.ticks(5)).enter().append('line')
    .attr('x1', 0).attr('x2', w).attr('y1', d => y(d)).attr('y2', d => y(d))
    .attr('stroke', ruleColor()).attr('stroke-dasharray', '2,3').attr('opacity', 0.7);

  // Axes
  g.append('g').attr('transform', `translate(0,${h})`)
    .call(d3.axisBottom(x).tickFormat(d3.format('d')).ticks(8))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '12px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));
  g.append('g')
    .call(d3.axisLeft(y).tickFormat(d => d + ' M').ticks(6))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '12px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // Légende minimale
  svg.append('text')
    .attr('x', margin.left).attr('y', 24)
    .attr('font-size', 12).attr('fill', inkSoftColor())
    .attr('letter-spacing', '0.04em')
    .text('Bénéfice annuel · millions de CHF · 1938—2025');

  // === Ligne complète, toujours visible (la trajectoire générale est lisible d'emblée) ===
  const line = d3.line().curve(d3.curveMonotoneX)
    .x(d => x(d.annee)).y(d => y(d.benefice_M));

  // ligne d'arrière-plan : la TRAJECTOIRE COMPLÈTE, bien visible
  g.append('path').datum(hist)
    .attr('fill', 'none').attr('stroke', '#c8102e')
    .attr('stroke-width', 2).attr('opacity', 0.32)
    .attr('d', line);

  // ligne principale qui "illumine" la portion jusqu'à l'année courante
  const totalLength = (() => {
    const tmp = g.append('path').datum(hist).attr('d', line);
    const len = tmp.node().getTotalLength();
    tmp.remove();
    return len;
  })();

  const linePath = g.append('path').datum(hist)
    .attr('class', 't-line')
    .attr('fill', 'none').attr('stroke', '#c8102e').attr('stroke-width', 3.2)
    .attr('d', line)
    .attr('stroke-dasharray', totalLength + ' ' + totalLength)
    .attr('stroke-dashoffset', totalLength);

  // Aire sous la courbe (subtile)
  const area = d3.area().curve(d3.curveMonotoneX)
    .x(d => x(d.annee)).y0(h).y1(d => y(d.benefice_M));

  // Tous les points (visibles d'emblée, low opacity)
  const pts = g.append('g').selectAll('circle.pt').data(hist).enter().append('circle')
    .attr('class', d => 'pt' + (d.annotation ? ' annot' : ''))
    .attr('data-year', d => d.annee)
    .attr('cx', d => x(d.annee)).attr('cy', d => y(d.benefice_M))
    .attr('r', d => d.annotation ? 0 : 2)
    .attr('fill', d => d.annotation ? '#fff' : '#c8102e')
    .attr('stroke', '#c8102e').attr('stroke-width', d => d.annotation ? 2 : 1)
    .style('cursor', 'pointer')
    .style('opacity', 0.35);

  pts.on('mouseover', function(ev, d) {
    let html = `<div class="t-title">${d.annee} · ${CHF1.format(d.benefice_M)} M CHF</div>`;
    if (d.ca_M) html += `<div>CA : ${CHF1.format(d.ca_M)} M</div>`;
    if (d.annotation) html += `<div class="t-meta">${d.annotation.titre} · ${d.annotation.source}</div>`;
    showTip(html, ev.clientX, ev.clientY);
  }).on('mouseout', hideTip);

  // Annotations textuelles (cachées au départ)
  const annotG = g.append('g').attr('class', 'annot-labels');
  const annot = hist.filter(d => d.annotation);
  annot.forEach((d, i) => {
    const xp = x(d.annee), yp = y(d.benefice_M);
    const dy = i % 2 === 0 ? -34 : 36;
    const grp = annotG.append('g')
      .attr('data-year', d.annee)
      .style('opacity', 0)
      .style('transition', 'opacity 0.6s ease');
    grp.append('line')
      .attr('x1', xp).attr('x2', xp).attr('y1', yp).attr('y2', yp + dy * 0.55)
      .attr('stroke', '#c8102e').attr('stroke-width', 0.8).attr('opacity', 0.6);
    const tx = grp.append('text')
      .attr('x', xp).attr('y', yp + dy)
      .attr('text-anchor', 'middle')
      .attr('font-family', 'Source Serif Pro, serif')
      .attr('font-style', 'italic')
      .attr('fill', inkColor()).attr('font-size', 14)
      .text(d.annotation.titre);
    tx.clone(true).lower().attr('stroke', isDark() ? '#15140f' : '#fbfaf6')
      .attr('stroke-width', 4).attr('fill', 'none');
  });

  // === Étape courante : grand affichage de la valeur ===
  // Marqueur vertical et étiquette de l'année courante
  const focusG = g.append('g').attr('class', 'focus-group').style('opacity', 0);
  const focusLine = focusG.append('line')
    .attr('y1', 0).attr('y2', h)
    .attr('stroke', '#c8102e').attr('stroke-width', 1.5)
    .attr('stroke-dasharray', '4,3').attr('opacity', 0.4);
  const focusPt = focusG.append('circle')
    .attr('r', 9).attr('fill', '#c8102e').attr('stroke', '#fff').attr('stroke-width', 3);
  const focusPulse = focusG.append('circle')
    .attr('r', 9).attr('fill', 'none').attr('stroke', '#c8102e').attr('stroke-width', 2);
  // Animation pulse
  function pulse() {
    focusPulse.attr('r', 9).attr('opacity', 0.8)
      .transition().duration(1400).ease(d3.easeQuadOut)
      .attr('r', 26).attr('opacity', 0).on('end', pulse);
  }
  pulse();

  // Grand chiffre flottant (top-left du graphique) avec la valeur courante
  const valueLabel = svg.append('g').attr('class', 'value-label').style('opacity', 0);
  const valueText = valueLabel.append('text')
    .attr('x', W - margin.right).attr('y', margin.top + 50)
    .attr('text-anchor', 'end')
    .attr('font-family', 'Source Serif Pro, serif')
    .attr('font-size', 56).attr('font-weight', 500).attr('fill', '#c8102e');
  const yearText = valueLabel.append('text')
    .attr('x', W - margin.right).attr('y', margin.top + 78)
    .attr('text-anchor', 'end')
    .attr('font-size', 13).attr('fill', inkSoftColor())
    .attr('letter-spacing', '0.06em').attr('text-transform', 'uppercase');

  // === Reveal fonction qui MAJ la viz selon l'année active ===
  function reveal(year) {
    // 1. Révéler la ligne jusqu'à l'année
    const yearIdx = hist.findIndex(d => d.annee >= year);
    const ratio = yearIdx === -1 ? 1 :
      (hist.slice(0, yearIdx + 1).length / hist.length);
    linePath.transition().duration(900).ease(d3.easeCubicOut)
      .attr('stroke-dashoffset', totalLength * (1 - ratio));

    // 2. Révéler les points jusqu'à cette année
    pts.transition().duration(500)
      .style('opacity', d => d.annee <= year ? 1 : 0)
      .attr('r', d => {
        if (d.annee > year) return 0;
        return d.annotation ? 7 : 2.5;
      });

    // 3. Afficher les annotations jusqu'à year
    annotG.selectAll('g').each(function() {
      const yr = +d3.select(this).attr('data-year');
      d3.select(this).style('opacity', yr <= year ? 1 : 0);
    });

    // 4. Positionner le focus sur le dernier point ≤ year
    const focusData = [...hist].reverse().find(d => d.annee <= year);
    if (focusData) {
      focusG.transition().duration(600)
        .style('opacity', 1)
        .attr('transform', `translate(${x(focusData.annee)},${y(focusData.benefice_M)})`);
      // Update value label
      valueLabel.transition().duration(400).style('opacity', 1);
      valueText.text(CHF1.format(focusData.benefice_M) + ' M');
      yearText.text(`Bénéfice ${focusData.annee}`);
    }
  }

  // Init : tout à l'état 1938
  setTimeout(() => reveal(1938), 100);

  // === Scrollama avec fallback IntersectionObserver natif ===
  function setupScrollama() {
    if (typeof scrollama === 'undefined') {
      // Fallback IntersectionObserver
      const stepsEls = document.querySelectorAll('[data-scrolly="timeline"] .step');
      const obs = new IntersectionObserver((entries) => {
        entries.forEach(e => {
          if (e.isIntersecting && e.intersectionRatio > 0.4) {
            stepsEls.forEach(s => s.classList.remove('is-active'));
            e.target.classList.add('is-active');
            const year = +e.target.dataset.step;
            if (!isNaN(year)) reveal(year);
          }
        });
      }, { threshold: [0.4, 0.6] });
      stepsEls.forEach(s => obs.observe(s));
      return;
    }

    const scroller = scrollama();
    scroller
      .setup({
        step: '[data-scrolly="timeline"] .step',
        offset: 0.6,
        progress: false,
        debug: false,
      })
      .onStepEnter(({ element, direction }) => {
        document.querySelectorAll('[data-scrolly="timeline"] .step').forEach(s => s.classList.remove('is-active'));
        element.classList.add('is-active');
        const year = +element.dataset.step;
        if (!isNaN(year)) reveal(year);
      })
      .onStepExit(({ element, direction }) => {
        if (direction === 'up') {
          element.classList.remove('is-active');
          const prevStep = element.previousElementSibling;
          if (prevStep && prevStep.classList.contains('step')) {
            prevStep.classList.add('is-active');
            const prevYear = +prevStep.dataset.step;
            if (!isNaN(prevYear)) reveal(prevYear);
          } else {
            reveal(1938);
          }
        }
      });

    window.addEventListener('resize', debounce(() => scroller.resize(), 200));
  }

  // Setup avec un petit délai pour s'assurer que le layout est stable
  if (document.readyState === 'complete') {
    setTimeout(setupScrollama, 200);
  } else {
    window.addEventListener('load', () => setTimeout(setupScrollama, 200));
  }
}

/* ============================================================
   ACTE II — ANATOMIE D'UN FRANC
   Barre empilée animée, segments qui apparaissent en cascade.
   ============================================================ */
function initFranc() {
  const container = d3.select('#viz-franc');
  if (container.empty()) return;

  // Données par année depuis rapports_financiers (compte_de_resultat)
  // M CHF, valeurs absolues (les frais sont stockés négativement dans le JSON)
  function getYearData(year) {
    const cr = DATA.rf && DATA.rf.compte_de_resultat && DATA.rf.compte_de_resultat[String(year)];
    if (!cr) return null;
    const abs = v => Math.abs(v || 0) / 1e6;  // → millions
    const pbj = abs(cr.produit_brut_jeux);
    const benefice = abs(cr.resultat_net);
    // Parts du PBJ : bénéfice + tous les coûts opérationnels du compte de résultat.
    // Le bénéfice net inclut déjà les distributions FSES/FSC (qui sont une part de
    // la répartition aux organes), donc on ne les compte pas séparément ici.
    const parts = [
      { label: 'Bénéfice → cantons',          v: benefice,                    color: '#c8102e', strong: true },
      { label: 'Commission points de vente',  v: abs(cr.commissions),         color: '#5b8def' },
      { label: 'Personnel',                   v: abs(cr.frais_personnel),     color: '#c97b3a' },
      { label: 'Informatique',                v: abs(cr.informatique),        color: '#2ea08a' },
      { label: 'Marketing / publicité',       v: abs(cr.marketing),           color: '#7c5bc7' },
      { label: 'Exploitation jeux',           v: abs(cr.exploitation_jeux),   color: '#a37a4f' },
      { label: 'Amortissements',              v: abs(cr.amortissements),      color: '#8a8a8a' },
      { label: 'Autres charges',              v: abs(cr.fabrication_jeux) + abs(cr.frais_generaux) + abs(cr.ventes_animations) + Math.max(0, abs(cr.frais_vendeurs)), color: '#bbb6a8' },
    ];
    // Note: la somme des parts peut légèrement dépasser le PBJ (de 5-10 M selon l'année)
    // car le bénéfice net inclut un résultat financier (produits hors-jeux).
    // On échelonne la barre sur la somme effective des parts, pas sur le PBJ.
    const total = parts.reduce((s, p) => s + p.v, 0);
    return { pbj, parts, benefice, total, year };
  }

  let currentYear = 2024;
  let dataByYear = {};
  for (const y of [2023, 2024, 2025]) {
    dataByYear[y] = getYearData(y);
  }
  if (!dataByYear[2024]) return;  // pas de données

  // Build chrome : year tabs + viz container
  container.html('');
  const tabBar = container.append('div').attr('class', 'franc-year-tabs').attr('role', 'tablist');
  [2023, 2024, 2025].forEach(y => {
    if (!dataByYear[y]) return;
    tabBar.append('button')
      .attr('class', 'franc-year-tab' + (y === currentYear ? ' active' : ''))
      .attr('data-year', y).attr('role', 'tab')
      .attr('aria-selected', y === currentYear ? 'true' : 'false')
      .text(y);
  });
  const vizWrap = container.append('div').attr('class', 'franc-viz-wrap');

  function render(year) {
    const data = dataByYear[year];
    if (!data) return;
    const { pbj, parts, benefice, total } = data;
    vizWrap.html('');

    const W = vizWrap.node().clientWidth || 1200, H = 280;
    const margin = { top: 60, right: 24, bottom: 100, left: 24 };
    const w = W - margin.left - margin.right;
    const h = 60;

    const svg = vizWrap.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H);
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);
    // La barre représente la somme des parts (généralement légèrement > PBJ à cause
    // du résultat financier net qui s'ajoute au bénéfice). On échelonne sur ce total.
    const scale = d3.scaleLinear().domain([0, total]).range([0, w]);

    svg.append('text').attr('x', margin.left).attr('y', margin.top - 20)
      .attr('font-size', 11).attr('fill', inkSoftColor())
      .attr('letter-spacing', '0.06em').text('0 CHF');
    svg.append('text').attr('x', margin.left + w).attr('y', margin.top - 20)
      .attr('font-size', 11).attr('text-anchor', 'end').attr('fill', inkSoftColor())
      .attr('letter-spacing', '0.06em').text(`PBJ ${year} : ${CHF1.format(pbj)} M · Bénéfice : ${CHF1.format(benefice)} M`);

    let cumul = 0;
    parts.forEach((p, i) => {
      const xstart = scale(cumul);
      const wseg = scale(p.v);
      const grp = g.append('g').style('cursor', 'pointer');
      grp.append('rect')
        .attr('x', xstart).attr('y', 0).attr('width', 0).attr('height', h)
        .attr('fill', p.color).attr('stroke', '#fff').attr('stroke-width', 1.5)
        .transition().delay(i * 100).duration(500).ease(d3.easeCubicOut)
        .attr('width', wseg);
      const pct = (p.v / pbj * 100);
      if (wseg > 60) {
        grp.append('text').attr('x', xstart + wseg / 2).attr('y', h / 2)
          .attr('text-anchor', 'middle').attr('dominant-baseline', 'middle')
          .attr('fill', '#fff').attr('font-family', 'Source Serif Pro, serif')
          .attr('font-size', p.strong ? 22 : 14).attr('font-weight', p.strong ? 600 : 500)
          .style('opacity', 0).text(`${CHF1.format(pct)} %`)
          .transition().delay(500 + i * 100).duration(400).style('opacity', 1);
      }
      grp.on('mouseover', ev => {
        showTip(`<div class="t-title">${p.label}</div>
                 <div>${CHF1.format(p.v)} M CHF</div>
                 <div class="t-meta">${CHF1.format(pct)} % du PBJ Loro ${year}</div>`,
          ev.clientX, ev.clientY);
      }).on('mouseout', hideTip);
      cumul += p.v;
    });

    // Labels under bar for top segments
    const labels = parts.map((p, i) => {
      const xMid = scale(parts.slice(0, i).reduce((s,q) => s+q.v, 0) + p.v / 2);
      return { ...p, xMid };
    });
    const lblG = svg.append('g').attr('transform', `translate(${margin.left}, ${margin.top + h + 20})`);
    labels.slice(0, 4).forEach((p, i) => {
      lblG.append('line').attr('x1', p.xMid).attr('x2', p.xMid)
        .attr('y1', -20).attr('y2', -6).attr('stroke', p.color).attr('stroke-width', 1).attr('opacity', 0.4);
      const text = lblG.append('text').attr('class', 'label').attr('x', p.xMid).attr('y', 6)
        .attr('text-anchor', 'middle').attr('font-size', 11)
        .attr('fill', inkColor()).attr('font-weight', 500);
      text.append('tspan').attr('x', p.xMid).attr('dy', 0).text(p.label);
      text.append('tspan').attr('x', p.xMid).attr('dy', 14)
        .attr('font-family', 'Source Serif Pro, serif').attr('fill', p.color)
        .text(`${CHF1.format(p.v)} M`);
    });

    // Legend for small segments
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

  // Wire tab switching
  tabBar.selectAll('.franc-year-tab').on('click', function() {
    const y = +this.dataset.year;
    currentYear = y;
    tabBar.selectAll('.franc-year-tab').classed('active', false).attr('aria-selected', 'false');
    d3.select(this).classed('active', true).attr('aria-selected', 'true');
    render(y);
  });

  render(currentYear);
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
  const tlYears = (DATA.percapita && DATA.percapita.tous_jeux && DATA.percapita.tous_jeux.years) || [];
  const tlMax = tlYears.length ? Math.max(...tlYears) : 2025;
  let curYear = tlMax;
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
    .attr('min', 2013).attr('max', tlMax).attr('value', curYear).attr('step', 1)
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
        curYear = curYear >= tlMax ? 2013 : curYear + 1;
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
    // Color scale:
    // - ratio: palette divergente around 50% (centered on parity)
    // - other metrics: use YlOrRd, a sequential palette with strong visible contrast
    //   between low/medium/high (yellow → orange → red).
    //   Domain starts at minV (not 0) so the full color range is used by the 6 cantons.
    let color;
    if (curMetric === 'ratio') {
      color = d3.scaleSequential().domain([30, 70]).interpolator(d3.interpolateRdYlBu);
    } else {
      // Pad domain by ~10% below to ensure even the smallest canton is visibly colored
      const lo = minV - (maxV - minV) * 0.1;
      color = d3.scaleSequential().domain([lo, maxV]).interpolator(d3.interpolateYlOrRd);
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
  const allYears = [...new Set(DATA.detail.map(d => d.annee))].sort((a,b)=>a-b);
  const yMin = allYears[0] || 2013;
  const yMax = allYears[allYears.length - 1] || 2025;

  const dataset = d3.range(yMin, yMax + 1).map(y => {
    const row = { annee: y };
    games.forEach(g => {
      const r = DATA.detail.find(d => d.annee === y && d.libelle === g);
      row[g] = r ? (r.total || 0) / 1e6 : 0;
    });
    return row;
  });

  // Use generous viewBox so the SVG fills available space
  const W = 1100, H = 620;
  const margin = { top: 40, right: 220, bottom: 50, left: 60 };
  const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;

  const svg = container.append('svg')
    .attr('viewBox', `0 0 ${W} ${H}`)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .attr('width', '100%').attr('height', '100%')
    .style('max-height', '85vh')
    .style('display', 'block');
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  let highlight = null;

  function render() {
    g.selectAll('*').remove();
    const stack = d3.stack().keys(games).order(d3.stackOrderNone);
    const series = stack(dataset);
    const maxY = d3.max(series[series.length - 1], d => d[1]);
    const x = d3.scaleLinear().domain([yMin, yMax]).range([0, w]);
    const y = d3.scaleLinear().domain([0, maxY]).range([h, 0]).nice();

    const area = d3.area()
      .x(d => x(d.data.annee)).y0(d => y(d[0])).y1(d => y(d[1]))
      .curve(d3.curveMonotoneX);

    g.selectAll('path.layer').data(series).enter().append('path').attr('class', 'layer')
      .attr('fill', d => GAME_COLORS[d.key])
      .attr('opacity', d => highlight ? (d.key === highlight ? 0.95 : 0.15) : 0.85)
      .attr('d', area)
      .style('transition', 'opacity 0.5s ease')
      .on('mouseover', (ev, d) => {
        const last = d[d.length - 1];
        showTip(`<div class="t-title">${d.key}</div><div>${yMax} : ${CHF1.format(last[1] - last[0])} M CHF</div>`, ev.clientX, ev.clientY);
      }).on('mouseout', hideTip);

    g.append('g').attr('transform', `translate(0,${h})`)
      .call(d3.axisBottom(x).tickFormat(d3.format('d')).ticks(7))
      .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '12px'))
      .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));
    g.append('g')
      .call(d3.axisLeft(y).tickFormat(d => d + ' M').ticks(6))
      .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '12px'))
      .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

    svg.selectAll('g.legend').remove();
    const lg = svg.append('g').attr('class', 'legend')
      .attr('transform', `translate(${W - margin.right + 14}, ${margin.top + 8})`);
    games.forEach((gk, i) => {
      const active = !highlight || highlight === gk;
      lg.append('rect').attr('y', i * 24).attr('width', 14).attr('height', 14)
        .attr('fill', GAME_COLORS[gk]).attr('opacity', active ? 1 : 0.3);
      lg.append('text').attr('x', 22).attr('y', i * 24 + 12)
        .attr('font-size', 12.5).attr('fill', active ? inkColor() : inkSoftColor())
        .attr('font-weight', highlight === gk ? 600 : 400)
        .text(gk);
    });

    svg.selectAll('text.focus-title').remove();
    if (highlight) {
      svg.append('text').attr('class', 'focus-title')
        .attr('x', margin.left).attr('y', 24)
        .attr('font-family', 'Source Serif Pro, serif')
        .attr('font-style', 'italic')
        .attr('font-size', 18).attr('fill', GAME_COLORS[highlight])
        .text(`Focus : ${highlight}`);
    } else {
      svg.append('text').attr('class', 'focus-title')
        .attr('x', margin.left).attr('y', 24)
        .attr('font-size', 12).attr('fill', inkSoftColor())
        .text(`Ventes par type de jeu · M CHF · ${yMin}—${yMax}`);
    }
  }
  render();

  // === Scrollama + IntersectionObserver fallback ===
  function setupMixScrollama() {
    if (typeof scrollama === 'undefined') {
      const stepsEls = document.querySelectorAll('[data-scrolly="mix"] .step');
      const obs = new IntersectionObserver((entries) => {
        entries.forEach(e => {
          if (e.isIntersecting && e.intersectionRatio > 0.4) {
            stepsEls.forEach(s => s.classList.remove('is-active'));
            e.target.classList.add('is-active');
            const step = e.target.dataset.step;
            if (step === 'all')    highlight = null;
            if (step === 'paris')  highlight = 'Paris sportifs';
            if (step === 'elec')   highlight = 'Loterie électronique';
            if (step === 'online') highlight = null;
            render();
          }
        });
      }, { threshold: [0.4, 0.6] });
      stepsEls.forEach(s => obs.observe(s));
      return;
    }

    const scroller = scrollama();
    scroller
      .setup({ step: '[data-scrolly="mix"] .step', offset: 0.6, debug: false })
      .onStepEnter(({ element }) => {
        document.querySelectorAll('[data-scrolly="mix"] .step').forEach(s => s.classList.remove('is-active'));
        element.classList.add('is-active');
        const step = element.dataset.step;
        if (step === 'all')    highlight = null;
        if (step === 'paris')  highlight = 'Paris sportifs';
        if (step === 'elec')   highlight = 'Loterie électronique';
        if (step === 'online') highlight = null;
        render();
      })
      .onStepExit(({ element, direction }) => {
        if (direction === 'up') {
          element.classList.remove('is-active');
          const prev = element.previousElementSibling;
          if (prev && prev.classList.contains('step')) {
            prev.classList.add('is-active');
            const step = prev.dataset.step;
            if (step === 'all')    highlight = null;
            if (step === 'paris')  highlight = 'Paris sportifs';
            if (step === 'elec')   highlight = 'Loterie électronique';
            if (step === 'online') highlight = null;
            render();
          }
        }
      });

    window.addEventListener('resize', debounce(() => scroller.resize(), 200));
  }

  if (document.readyState === 'complete') {
    setTimeout(setupMixScrollama, 200);
  } else {
    window.addEventListener('load', () => setTimeout(setupMixScrollama, 200));
  }
}

/* ============================================================
   ACTE V — TREEMAP des secteurs avec sélecteur d'année + animation
   ============================================================ */
function initTreemap() {
  const container = d3.select('#viz-treemap');
  if (container.empty()) return;
  container.html('');

  // Years available in repartition_secteur
  const allYears = new Set();
  Object.values(DATA.secteurs).forEach(series => {
    Object.keys(series).forEach(y => { if (/^\d{4}$/.test(y)) allYears.add(+y); });
  });
  const years = [...allYears].sort((a,b)=>a-b);
  const yMin = years[0], yMax = years[years.length - 1];
  let curYear = yMax;
  let tmPlaying = null;

  // === Controls ===
  const ctlRow = container.append('div').attr('class','controls-row')
    .style('display','flex').style('align-items','center').style('gap','14px')
    .style('flex-wrap','wrap').style('margin-bottom','16px');

  ctlRow.append('span').text('Année').style('font-size','11px')
    .style('color','var(--ink-mute)').style('letter-spacing','0.14em').style('text-transform','uppercase');
  const yearLabel = ctlRow.append('span')
    .style('font-family','Source Serif Pro, serif')
    .style('font-size','28px').style('font-weight','500').style('color','var(--accent, #c8102e)')
    .text(curYear);

  const slider = ctlRow.append('input').attr('type','range')
    .attr('min', yMin).attr('max', yMax).attr('value', curYear).attr('step', 1)
    .style('flex','1').style('min-width','220px');
  slider.on('input', function() { curYear = +this.value; yearLabel.text(curYear); render(); });

  const totalLabel = ctlRow.append('span')
    .style('font-size','13px').style('color','var(--ink-soft)').style('font-style','italic');

  const playBtn = ctlRow.append('button').attr('class','btn').text('▶ Animer');
  playBtn.on('click', () => {
    if (tmPlaying) {
      clearInterval(tmPlaying); tmPlaying = null;
      playBtn.text('▶ Animer');
    } else {
      playBtn.text('⏸ Pause');
      tmPlaying = setInterval(() => {
        curYear = curYear >= yMax ? yMin : curYear + 1;
        slider.property('value', curYear);
        yearLabel.text(curYear);
        render();
      }, 1100);
    }
  });

  // === SVG (preserves the same aspect for smooth tweening) ===
  const W = 1100, H = 520;
  const svg = container.append('svg')
    .attr('viewBox', `0 0 ${W} ${H}`)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .attr('width', '100%').attr('height', H)
    .style('height', 'auto').style('max-height', '70vh').style('display', 'block');

  const sectorOrder = Object.keys(DATA.secteurs); // stable layout key

  function render() {
    // Build hierarchy for current year
    const root = { name: 'Loro', children: [] };
    Object.entries(DATA.secteurs).forEach(([sec, series]) => {
      const v = series[String(curYear)];
      if (!v) return;
      root.children.push({ name: sec, value: v, color: SECTOR_COLORS[sec] || '#999' });
    });
    const total = root.children.reduce((s,c) => s+c.value, 0);
    totalLabel.text(`${CHF1.format(total/1e6)} M CHF redistribués`);

    const r = d3.hierarchy(root).sum(d => d.value).sort((a, b) => b.value - a.value);
    d3.treemap().size([W, H]).padding(3).round(true)(r);
    const leaves = r.leaves();

    // Bind by sector name (stable)
    const g = svg.selectAll('g.cell').data(leaves, d => d.data.name);

    // ENTER
    const gEnter = g.enter().append('g').attr('class', 'cell')
      .attr('transform', d => `translate(${d.x0},${d.y0})`)
      .style('cursor', 'pointer');
    gEnter.append('rect').attr('width', 0).attr('height', 0)
      .attr('fill', d => d.data.color).attr('opacity', 0.92);
    gEnter.append('text').attr('class','t-name').attr('x', 14).attr('y', 28)
      .attr('fill', '#fff').attr('font-weight', 500).attr('font-size', 16);
    gEnter.append('text').attr('class','t-val').attr('x', 14).attr('y', 54)
      .attr('fill', '#fff').attr('opacity', 0.9)
      .attr('font-size', 22).attr('font-family', 'Source Serif Pro, serif');
    gEnter.append('text').attr('class','t-pct').attr('x', 14).attr('y', 74)
      .attr('fill', '#fff').attr('opacity', 0.7).attr('font-size', 12);

    // MERGE + UPDATE
    const gAll = gEnter.merge(g);
    gAll.transition().duration(800).ease(d3.easeCubicInOut)
      .attr('transform', d => `translate(${d.x0},${d.y0})`);
    gAll.select('rect').transition().duration(800).ease(d3.easeCubicInOut)
      .attr('width', d => d.x1 - d.x0).attr('height', d => d.y1 - d.y0);
    gAll.select('.t-name')
      .text(d => SECTOR_SHORT[d.data.name] || d.data.name)
      .style('opacity', d => ((d.x1 - d.x0) >= 90 && (d.y1 - d.y0) >= 32) ? 1 : 0);
    gAll.select('.t-val')
      .text(d => CHF1.format(d.value / 1e6) + ' M')
      .style('opacity', d => ((d.x1 - d.x0) >= 90 && (d.y1 - d.y0) >= 60) ? 0.9 : 0);
    gAll.select('.t-pct')
      .text(d => CHF1.format(d.value / r.value * 100) + ' % du total')
      .style('opacity', d => ((d.x1 - d.x0) >= 90 && (d.y1 - d.y0) >= 80) ? 0.7 : 0);

    gAll.on('mouseover', function(ev, d) {
      showTip(`<div class="t-title">${d.data.name}</div>
               <div>${CHF1.format(d.value / 1e6)} M CHF en ${curYear}</div>
               <div class="t-meta">${CHF1.format(d.value / r.value * 100)} % du redistribué</div>`,
              ev.clientX, ev.clientY);
    }).on('mouseout', hideTip);

    // EXIT
    g.exit().remove();
  }

  render();
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
   ACCESSIBILITY DECORATOR
   Runs after all viz are rendered. Adds:
   - role="region" + aria-labelledby on each .viz-card (pairs the card with its title)
   - role="img" + aria-label on each <svg> inside .viz (derives label from card title)
   This works without touching the 20+ individual viz init functions.
   ============================================================ */
function initA11yDecoration() {
  let titleSeq = 0;
  document.querySelectorAll('.viz-card').forEach(card => {
    const titleEl = card.querySelector('.viz-title');
    if (!titleEl) return;
    if (!titleEl.id) {
      titleSeq += 1;
      titleEl.id = `viz-title-${titleSeq}`;
    }
    if (!card.hasAttribute('role')) card.setAttribute('role', 'region');
    if (!card.hasAttribute('aria-labelledby')) card.setAttribute('aria-labelledby', titleEl.id);

    // For SVGs inside this card, set role=img and aria-label from the title text
    const titleText = titleEl.textContent.trim();
    card.querySelectorAll('svg').forEach(svg => {
      if (!svg.hasAttribute('role')) svg.setAttribute('role', 'img');
      if (!svg.hasAttribute('aria-label')) svg.setAttribute('aria-label', titleText);
    });
  });
}

/* ============================================================
   BUILD DATE — affiche la date de la dernière mise à jour
   Stratégie : dernière modification connue de historique.json (extraite via fetch HEAD),
   sinon fallback au jour du chargement de la page.
   ============================================================ */
function initBuildDate() {
  const el = document.getElementById('build-date');
  if (!el) return;
  const fmt = d => new Intl.DateTimeFormat('fr-CH', {
    day: 'numeric', month: 'long', year: 'numeric'
  }).format(d);

  // Essai 1 : last-modified du fichier historique.json (le plus volatil)
  fetch('data/historique.json', { method: 'HEAD' })
    .then(r => {
      const lm = r.headers.get('last-modified');
      if (lm) {
        el.textContent = fmt(new Date(lm));
      } else {
        el.textContent = fmt(new Date());
      }
    })
    .catch(() => { el.textContent = fmt(new Date()); });
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
  // Auto-detect max year
  const rmYears = (DATA.percapita && DATA.percapita.tous_jeux && DATA.percapita.tous_jeux.years) || [];
  const rmMax = rmYears.length ? Math.max(...rmYears) : 2025;
  let curYear = rmMax;
  let rmPlaying = null;

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
  const slider = sliderRow.append('input').attr('type','range').attr('min', 2013).attr('max', rmMax)
    .attr('value', curYear).attr('step', 1).style('flex','1').style('min-width','200px');
  slider.on('input', function() { curYear = +this.value; yearLabel.text(curYear); render(); });

  const rmPlayBtn = sliderRow.append('button').attr('class','btn').text('▶ Animer');
  rmPlayBtn.on('click', () => {
    if (rmPlaying) {
      clearInterval(rmPlaying); rmPlaying = null;
      rmPlayBtn.text('▶ Animer');
    } else {
      rmPlayBtn.text('⏸ Pause');
      rmPlaying = setInterval(() => {
        curYear = curYear >= rmMax ? 2013 : curYear + 1;
        slider.property('value', curYear);
        yearLabel.text(curYear);
        render();
      }, 900);
    }
  });

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
    const minV = d3.min(Object.values(vals));
    let color;
    if (curMetric === 'ratio') {
      color = d3.scaleSequential().domain([30, 70]).interpolator(d3.interpolateRdYlBu);
    } else {
      // Sequential YlOrRd palette : yellow-orange-red, much more contrasted than the
      // previous white→red gradient that crammed all values in the pale end.
      const lo = minV - (maxV - minV) * 0.1;
      color = d3.scaleSequential().domain([lo, maxV]).interpolator(d3.interpolateYlOrRd);
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
  // Étendre à 2025 (dernière année dispo)
  const years = d3.range(2013, 2026);
  const lastYear = years[years.length - 1];

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

  // Grid 3 × 2 sur desktop (forcé via la classe CSS)
  const grid = container.append('div').attr('class', 'mc-grid mc-grid-3x2');

  cantons.forEach(c => {
    const cell = grid.append('div').attr('class', 'mc-cell');
    cell.append('h4').html(`<span style="color:${CANTON_COLORS[c]}">●</span> ${CANTON_NAMES[c]}`);

    const data = buildDataset(c);
    // Augmenter le SVG : 380×200 au lieu de 280×140 (largeur +36 %, hauteur +43 %)
    const W = 380, H = 200;
    const margin = { top: 14, right: 12, bottom: 24, left: 36 };
    const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;

    const svg = cell.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%');
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const stack = d3.stack().keys(games);
    const series = stack(data);
    const maxY = d3.max(series[series.length - 1], d => d[1]);

    const x = d3.scaleLinear().domain([2013, lastYear]).range([0, w]);
    const y = d3.scaleLinear().domain([0, maxY]).range([h, 0]).nice();

    // Grille horizontale en pointillé
    g.selectAll('.gridline').data(y.ticks(3)).enter().append('line')
      .attr('x1', 0).attr('x2', w).attr('y1', d => y(d)).attr('y2', d => y(d))
      .attr('stroke', ruleColor()).attr('stroke-dasharray', '2,2').attr('opacity', 0.5);

    // Ticks Y (M CHF)
    g.selectAll('.ytk').data(y.ticks(3)).enter().append('text')
      .attr('x', -6).attr('y', d => y(d) + 3)
      .attr('text-anchor', 'end').attr('font-size', 9)
      .attr('fill', inkSoftColor()).text(d => d + ' M');

    const area = d3.area().curve(d3.curveMonotoneX)
      .x(d => x(d.data.annee)).y0(d => y(d[0])).y1(d => y(d[1]));

    g.selectAll('path.area').data(series).enter().append('path')
      .attr('class', 'area')
      .attr('fill', d => GAME_COLORS[d.key]).attr('opacity', 0.88)
      .attr('d', area);

    // Petit axe X
    g.append('text').attr('x', 0).attr('y', h + 14)
      .attr('font-size', 10).attr('fill', inkSoftColor()).text('2013');
    g.append('text').attr('x', w).attr('y', h + 14).attr('text-anchor','end')
      .attr('font-size', 10).attr('fill', inkSoftColor()).text(String(lastYear));

    // Total dernière année à droite
    const lastVal = games.reduce((s, gk) => {
      const r = DATA.detail.find(d => d.annee === lastYear && d.libelle === gk);
      return s + (r ? (r.cantons[c] || 0) / 1e6 : 0);
    }, 0);
    g.append('text').attr('x', 0).attr('y', -2)
      .attr('font-family', 'Source Serif Pro, serif')
      .attr('font-size', 14).attr('font-weight', 500).attr('fill', inkColor())
      .text(`${CHF1.format(lastVal)} M en ${lastYear}`);

    cell.on('mouseover', () => {
      svg.selectAll('path.area').attr('opacity', 1);
    }).on('mouseout', () => {
      svg.selectAll('path.area').attr('opacity', 0.88);
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

  const cantons = ['VD', 'GE', 'FR', 'VS', 'NE', 'JU'];

  // Règles de prélèvement cantonal (% du bénéfice net que le Conseil d'État garde
  // pour le distribuer directement, hors organes de répartition culture/social/sport).
  // Source 2024 : REISO « La Loterie Romande, source de financement clé », janvier 2026.
  // Sources 2025 : ne.ch (FAC-LoRo nouveau), La Liberté (oct 2024) + Frapp (juin 2024) pour FR,
  // recueil officiel Jura (FO 2025 N° 23) pour JU.
  const prelevements = {
    VD: { 2024: 25, 2025: 25,                                                 changement: null },
    JU: { 2024: 17, 2025: 20,                                                 changement: 'Relevé de 17 % à 20 % (loi cantonale modifiée en 2024, effet 2025).' },
    NE: { 2024: 10, 2025: 10,                                                 changement: 'Création en 2025 du Fonds d\'attributions cantonales (FAC-LoRo) — 1,57 M en 13 dossiers touristiques.' },
    FR: { 2024: 9,  2025: 9,                                                  changement: '+2 % de l\'enveloppe redirigée vers le sport (de 7 % à 9 % du total). 500 000 CHF de plus pour le sport, sans baisse pour la culture (Conseil d\'État, juin 2024).' },
    GE: { 2024: 0,  2025: 0,                                                  changement: null },
    VS: { 2024: 0,  2025: 0,                                                  changement: null },
  };

  // === Comparaison 2024 vs 2025 — vue principale ===
  const compareWrap = container.append('div').attr('class', 'gov-compare-wrap');
  compareWrap.append('h4').attr('class', 'gov-section-title').text('Prélèvement du Conseil d\'État · 2024 → 2025');
  compareWrap.append('p').attr('class', 'gov-section-intro').html(
    'Pour chaque canton, la part de la Loterie Romande que le Conseil d\'État garde pour la distribuer directement (hors organes culture/social/sport). Plafond fédéral : 30 %.'
  );

  const compareTable = compareWrap.append('table').attr('class', 'gov-compare-table');
  const ch = compareTable.append('thead').append('tr');
  ch.append('th').text('Canton');
  ch.append('th').text('2024');
  ch.append('th').text('2025');
  ch.append('th').text('Changement effectif en 2025');
  const cb = compareTable.append('tbody');

  cantons.forEach(c => {
    const p = prelevements[c];
    const tr = cb.append('tr');
    tr.append('td').html(`<strong>${CANTON_NAMES[c]}</strong> <span class="gov-code">${c}</span>`);
    // 2024 with bar
    const td24 = tr.append('td').attr('class', 'gov-prel-cell');
    td24.append('span').attr('class', 'gov-prel-val').text(p[2024] === 0 ? '—' : p[2024] + ' %');
    if (p[2024] > 0) {
      td24.append('div').attr('class', 'gov-prel-bar')
        .append('div').attr('class', 'gov-prel-fill')
        .style('width', (p[2024] / 30 * 100) + '%');
    }
    // 2025
    const td25 = tr.append('td').attr('class', 'gov-prel-cell');
    const evol = p[2025] - p[2024];
    const arrow = evol > 0 ? ' <span class="gov-arrow-up">↑</span>' : (evol < 0 ? ' <span class="gov-arrow-down">↓</span>' : '');
    td25.append('span').attr('class', 'gov-prel-val').html((p[2025] === 0 ? '—' : p[2025] + ' %') + arrow);
    if (p[2025] > 0) {
      td25.append('div').attr('class', 'gov-prel-bar')
        .append('div').attr('class', 'gov-prel-fill' + (evol > 0 ? ' gov-prel-fill-changed' : ''))
        .style('width', (p[2025] / 30 * 100) + '%');
    }
    // Comment column
    const tdC = tr.append('td').attr('class', 'gov-change-cell');
    if (p.changement) {
      tdC.html(`<span class="gov-change-badge">Évolution</span> ${p.changement}`);
    } else {
      tdC.html('<span style="color:var(--ink-mute); font-style:italic;">Inchangé</span>');
    }
  });

  // === Détail historique (année la plus récente disponible) ===
  const detailWrap = container.append('div').attr('class', 'gov-detail-wrap');
  const detYears = [...new Set(DATA.detail.map(d => d.annee))].sort((a,b)=>a-b);
  const pcYrs = (DATA.percapita && DATA.percapita.tous_jeux && DATA.percapita.tous_jeux.years) || [];
  const govYear = Math.min(
    detYears.length ? Math.max(...detYears) : 2025,
    pcYrs.length ? Math.max(...pcYrs) : 2025
  );
  detailWrap.append('h4').attr('class', 'gov-section-title').text(`Flux financiers · ${govYear}`);

  const tableWrap = detailWrap.append('div').attr('class', 'gov-table-wrap');
  const table = tableWrap.append('table').attr('class', 'gov-table');
  const thead = table.append('thead');
  const headerRow = thead.append('tr');
  headerRow.append('th').text('Canton');
  headerRow.append('th').html(`Reçu en ${govYear}<br>(M CHF)`);
  headerRow.append('th').html('Ratio reçu /<br>dépensé').attr('title', 'Bénéfice reçu vs ventes brutes');
  headerRow.append('th').html(`Dépense par<br>habitant ${govYear}`);
  const tbody = table.append('tbody');

  cantons.forEach(c => {
    const rowY = DATA.detail.find(d => d.annee === govYear && d.poste === 'Répartition');
    const ventesY = DATA.detail.find(d => d.annee === govYear && d.libelle === 'Total');
    const recu = rowY ? (rowY.cantons[c] || 0) / 1e6 : 0;
    const vendu = ventesY ? (ventesY.cantons[c] || 0) / 1e6 : 0;
    const ratio = vendu > 0 ? (recu / vendu * 100) : 0;
    const pc = DATA.percapita.tous_jeux;
    const idx = pc.years.indexOf(govYear);
    const depHab = idx >= 0 ? pc.data[CANTON_NAMES[c]][idx] : 0;

    const tr = tbody.append('tr');
    tr.append('td').html(`<strong>${CANTON_NAMES[c]}</strong> <span class="gov-code">${c}</span>`);
    tr.append('td').attr('class', 'gov-num').text(CHF1.format(recu));
    tr.append('td').attr('class', 'gov-num').text(CHF1.format(ratio) + ' %');
    tr.append('td').attr('class', 'gov-num').text(CHF.format(depHab));
  });

  // Légende sous la table
  container.append('p').attr('class', 'note').style('margin-top', '20px')
    .html(`<strong>Lecture :</strong> Plafond fédéral du prélèvement Conseil d'État : 30 % du bénéfice net cantonal. Le reste passe par les organes de répartition (15 % sport, 85 % autres domaines).
    <br><br><strong>Sources 2024 :</strong> <em>REISO, "La Loterie Romande, source de financement clé"</em>, J. Sanchez, janvier 2026.
    <br><strong>Changements 2025 :</strong> Jura — recueil officiel cantonal (FO 2025 N° 23, mai 2025). Fribourg — La Liberté (7 oct 2024) + Frapp (9 juin 2024). Neuchâtel — communiqué République et Canton de Neuchâtel (mai 2026, FAC-LoRo).`);
}

/* ============================================================
   SANKEY ENRICHI (Angle A + Coda fusionnés)
   Étapes du flux avec marquage discrétionnaire vs structurel
   ============================================================ */
function initSankeyEnriched() {
  // Garde le sankey original; ce sera l'évolution v2 si besoin
}

/* ============================================================
   ANGLE B — DÉCOMPOSITION DES VARIATIONS 2018→2025
   Une vue d'ensemble (waterfall) + un détail par année sélectionnable.
   Sources : rapports annuels Loro 2018-2025, éditos du directeur,
   communiqués de presse (Blick mai 2025).
   ============================================================ */
function initAnomaly() {
  const container = d3.select('#viz-anomaly');
  if (container.empty()) return;
  container.html('');

  // === Données : bénéfices réels et décompositions narratives ===
  // benef en M CHF, sourcé rapports annuels Loro
  const benefs = {
    2017: 215.0, // baseline avant Covid
    2018: 221.4, // PBJ 388 M ; LJAr votée
    2019: 244.3, // PBJ 408 M record, 1ère année LJAr
    2020: 216.4, // Covid, PBJ -8%
    2021: 229.0, // CORJA en vigueur, rebond
    2022: 246.4, // Vaud bascule à 25%, Coupe du Monde
    2023: 243.7, // bond IT, EuroDreams
    2024: 258.2, // record : jackpot + Euro + JO
    2025: 252.0, // reflux : cycles EuroMillions plus courts
  };

  // Décompositions par année (delta vs N-1).
  // Total des facteurs doit ≈ matcher Δ = benef[y] - benef[y-1].
  // Sources : éditos directeur Loro + éditorial Acte VII des données du repo.
  const decomp = {
    2018: {
      facteurs: [
        { label: 'Croissance organique PBJ', v: 6.4, color: '#5b8def' },
      ],
      narratif: "Vote LJAr (10 juin 2018, 73 % de oui). Année de transition vers la nouvelle législation.",
    },
    2019: {
      facteurs: [
        { label: 'Effet LJAr : opérateurs étrangers bloqués', v: 14.0, color: '#c8102e' },
        { label: 'PBJ record (408 M)',                        v: 6.0,  color: '#f0a93d' },
        { label: 'Exonération impôt anticipé jusqu\'à 1 M',   v: 2.9,  color: '#5b8def' },
      ],
      narratif: "1er janvier 2019 : LJAr en vigueur. La Loro devient seule autorisée pour les jeux et paris en Suisse romande. Record absolu PBJ.",
    },
    2020: {
      facteurs: [
        { label: 'Covid : fermeture cafés-restaurants',      v: -22.0, color: '#7c5bc7' },
        { label: 'Loterie électronique -30 %',               v: -8.0,  color: '#c8102e' },
        { label: 'Gestion serrée des coûts',                  v: 2.1,   color: '#5b8def' },
      ],
      narratif: "Pandémie. PBJ -8 %, mais bénéfice tenu à 216 M grâce à des coûts comprimés. Obtention de l'autorisation Gespa pour 20 ans.",
    },
    2021: {
      facteurs: [
        { label: 'Rebond post-Covid (réouvertures)',         v: 13.0,  color: '#f0a93d' },
        { label: 'CORJA en vigueur (1.1.2021)',              v: 2.0,   color: '#5b8def' },
        { label: 'Soutien spécifique cafés-restaurants',     v: -2.4,  color: '#7c5bc7' },
      ],
      narratif: "Nouveau système CORJA. Lancement Live Betting en ligne. Soutien spécifique 3,3 M aux 800 cafés-restaurants qui exploitent les Tactilo.",
    },
    2022: {
      facteurs: [
        { label: 'Coupe du Monde Qatar (pic JouezSport)',    v: 12.0,  color: '#f0a93d' },
        { label: 'PBJ record 435 M',                          v: 21.0,  color: '#c8102e' },
        { label: 'Pertes sur placements financiers',         v: -15.6, color: '#7c5bc7' },
      ],
      narratif: "Coupe du Monde dope les paris sportifs. PBJ atteint un nouveau record. Mais les marchés baissiers grèvent le résultat financier de 15,6 M.",
    },
    2023: {
      facteurs: [
        { label: 'PBJ en baisse (-3,4 %)',                    v: -8.0,  color: '#7c5bc7' },
        { label: 'Investissement IT massif (+34 %)',         v: -5.7,  color: '#c8102e' },
        { label: 'Lancement EuroDreams (novembre)',          v: 2.0,   color: '#5b8def' },
        { label: 'Effet stabilisateur réserves',              v: 8.9,   color: '#f0a93d' },
      ],
      narratif: "Année de transition : moins de gros jackpots, mais investissement informatique majeur (22,5 M, +34 %). Lancement d'EuroDreams en novembre.",
    },
    2024: {
      facteurs: [
        { label: 'Jackpot Swiss Loto record (64,6 M le 2 mars)', v: 9.5, color: '#c8102e' },
        { label: 'Euro de foot + JO Paris (+24,6 % JouezSport)', v: 5.5, color: '#f0a93d' },
        { label: 'Live Betting en point de vente (sept.)',       v: 2.6, color: '#5b8def' },
      ],
      narratif: "Conjonction de facteurs exceptionnels. Jackpot record Swiss Loto à 64,585 M le 2 mars. Refonte du Loto Express. Live Betting déployé en point de vente.",
    },
    2025: {
      facteurs: [
        { label: 'Fin du jackpot record Swiss Loto',          v: -7.5, color: '#c8102e' },
        { label: 'Cycles EuroMillions plus courts',           v: -2.5, color: '#7c5bc7' },
        { label: 'Maintien base (gestion serrée)',            v: 3.8,  color: '#5b8def' },
      ],
      narratif: "Reflux annoncé par le DG dès mai 2025. PBJ 429,8 M, 3e meilleur résultat. Le Jura passe à 20 % de prélèvement. Outil de détection précoce mis en place.",
    },
  };

  const years = [2018,2019,2020,2021,2022,2023,2024,2025];

  // ====== Layout : 2 vues ======
  // 1. En haut : waterfall des deltas + bénéfice annuel
  // 2. En bas : détail interactif (clic sur une année)

  // --- VUE 1 : WATERFALL ---
  const headerRow = container.append('div')
    .style('display','flex').style('justify-content','space-between')
    .style('align-items','baseline').style('margin-bottom','12px')
    .style('flex-wrap','wrap').style('gap','12px');
  headerRow.append('div')
    .style('font-family', 'Source Serif Pro, serif')
    .style('font-size', '18px').style('font-weight', '600')
    .style('color', 'var(--ink)')
    .text('Bénéfice annuel · 2018→2025');
  headerRow.append('div')
    .style('font-size', '12px').style('color', 'var(--ink-mute)')
    .style('letter-spacing', '0.06em').style('text-transform','uppercase')
    .text('Cliquez sur une année pour la décomposition');

  const W1 = Math.max(600, container.node().clientWidth);
  const H1 = 320;
  const margin1 = { top: 30, right: 30, bottom: 80, left: 60 };
  const w1 = W1 - margin1.left - margin1.right;
  const h1 = H1 - margin1.top - margin1.bottom;

  const svg1 = container.append('svg')
    .attr('viewBox', `0 0 ${W1} ${H1}`).attr('width', '100%').attr('height', H1)
    .style('display', 'block').style('margin-bottom', '8px');

  const g1 = svg1.append('g').attr('transform', `translate(${margin1.left},${margin1.top})`);

  const yMin = 180, yMax = 270;
  const xScale = d3.scaleBand().domain(years).range([0, w1]).padding(0.18);
  const yScale = d3.scaleLinear().domain([yMin, yMax]).range([h1, 0]);

  // grille horizontale
  g1.selectAll('.h-grid').data(yScale.ticks(5)).enter().append('line')
    .attr('class', 'h-grid')
    .attr('x1', 0).attr('x2', w1)
    .attr('y1', d => yScale(d)).attr('y2', d => yScale(d))
    .attr('stroke', ruleColor()).attr('stroke-dasharray', '2,3').attr('opacity', 0.5);

  // axe y
  g1.append('g')
    .call(d3.axisLeft(yScale).tickFormat(d => d + ' M').ticks(5))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // axe x
  g1.append('g').attr('transform', `translate(0,${h1})`)
    .call(d3.axisBottom(xScale).tickFormat(d3.format('d')))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '13px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // Bandes COVID
  g1.append('rect')
    .attr('x', xScale(2020) - 2).attr('y', 0)
    .attr('width', xScale.bandwidth() + 4).attr('height', h1)
    .attr('fill', '#7c5bc7').attr('opacity', 0.06);
  g1.append('text')
    .attr('x', xScale(2020) + xScale.bandwidth()/2).attr('y', -8)
    .attr('text-anchor', 'middle').attr('font-size', 10)
    .attr('fill', '#7c5bc7').attr('font-style','italic').attr('letter-spacing','0.06em')
    .text('COVID');

  // Ligne de connexion
  const linePath = d3.line()
    .x(d => xScale(d) + xScale.bandwidth()/2)
    .y(d => yScale(benefs[d]))
    .curve(d3.curveMonotoneX);

  g1.append('path').datum(years)
    .attr('fill','none').attr('stroke','#c8102e').attr('stroke-width', 1.5)
    .attr('opacity', 0.4).attr('d', linePath);

  // Barres bénéfices
  let selectedYear = 2024;
  g1.selectAll('.bar').data(years).enter().append('rect')
    .attr('class', d => 'bar bar-' + d)
    .attr('x', d => xScale(d))
    .attr('y', d => yScale(benefs[d]))
    .attr('width', xScale.bandwidth())
    .attr('height', d => h1 - yScale(benefs[d]))
    .attr('fill', d => d === selectedYear ? '#c8102e' : (d === 2020 ? '#7c5bc7' : '#bbb6a8'))
    .style('cursor', 'pointer')
    .on('click', function(ev, d) {
      selectedYear = d;
      g1.selectAll('.bar')
        .attr('fill', dd => dd === selectedYear ? '#c8102e' : (dd === 2020 ? '#7c5bc7' : '#bbb6a8'));
      renderDetail(d);
    })
    .on('mouseover', function(ev, d) {
      const prev = d - 1;
      const delta = benefs[prev] !== undefined ? (benefs[d] - benefs[prev]) : null;
      showTip(`<div class="t-title">${d}</div>
               <div>Bénéfice : ${CHF1.format(benefs[d])} M CHF</div>
               ${delta !== null ? `<div class="t-meta">vs ${prev} : ${delta >= 0 ? '+' : ''}${CHF1.format(delta)} M</div>` : ''}
               <div class="t-meta" style="margin-top:4px;font-style:italic">Cliquez pour le détail</div>`, ev.clientX, ev.clientY);
    }).on('mouseout', hideTip);

  // Étiquettes valeurs au-dessus
  g1.selectAll('.bar-lbl').data(years).enter().append('text')
    .attr('class', 'bar-lbl')
    .attr('x', d => xScale(d) + xScale.bandwidth()/2)
    .attr('y', d => yScale(benefs[d]) - 6)
    .attr('text-anchor', 'middle')
    .attr('font-family', 'Source Serif Pro, serif')
    .attr('font-size', 12).attr('font-weight', 500)
    .attr('fill', d => d === 2020 ? '#7c5bc7' : '#c8102e')
    .text(d => CHF1.format(benefs[d]));

  // Annotations contextuelles : record 2024, reflux 2025
  const annot = g1.append('g');
  annot.append('text')
    .attr('x', xScale(2024) + xScale.bandwidth()/2)
    .attr('y', yScale(benefs[2024]) - 22)
    .attr('text-anchor', 'middle').attr('font-size', 10).attr('font-style','italic')
    .attr('fill', '#c8102e').attr('font-weight', 600)
    .text('★ record');

  annot.append('text')
    .attr('x', xScale(2019) + xScale.bandwidth()/2)
    .attr('y', yScale(benefs[2019]) - 22)
    .attr('text-anchor', 'middle').attr('font-size', 10).attr('font-style','italic')
    .attr('fill', inkSoftColor())
    .text('1ʳᵉ LJAr');

  // --- VUE 2 : DÉTAIL ANNÉE SÉLECTIONNÉE ---
  const detailWrap = container.append('div')
    .attr('class', 'anomaly-detail')
    .style('margin-top', '20px')
    .style('padding', '20px')
    .style('background', 'var(--bg-card, rgba(0,0,0,0.02))')
    .style('border-left', '4px solid #c8102e')
    .style('border-radius', '4px');

  function renderDetail(year) {
    detailWrap.html('');
    const prev = year - 1;
    const delta = benefs[prev] !== undefined ? (benefs[year] - benefs[prev]) : 0;
    const d = decomp[year];
    if (!d) {
      detailWrap.append('p').style('color','var(--ink-mute)').text('Décomposition non disponible pour cette année.');
      return;
    }

    // En-tête
    const head = detailWrap.append('div')
      .style('display','flex').style('justify-content','space-between')
      .style('align-items','baseline').style('flex-wrap','wrap').style('gap','12px')
      .style('margin-bottom','14px');
    head.append('div')
      .style('font-family','Source Serif Pro, serif').style('font-size','22px')
      .style('font-weight','600').style('color','var(--ink)')
      .html(`${year} : <span style="color:#c8102e">${CHF1.format(benefs[year])} M</span> <span style="font-size:14px;color:var(--ink-soft)">(${delta >= 0 ? '+' : ''}${CHF1.format(delta)} M vs ${prev})</span>`);

    detailWrap.append('p')
      .style('margin','0 0 14px').style('font-size','14px')
      .style('line-height','1.55').style('color','var(--ink-soft)')
      .text(d.narratif);

    // Mini-waterfall
    const W2 = Math.max(500, container.node().clientWidth);
    const H2 = 80 + d.facteurs.length * 28;
    const m2 = { top: 30, right: 30, bottom: 30, left: 30 };
    const w2 = W2 - m2.left - m2.right, h2 = H2 - m2.top - m2.bottom;
    const svg2 = detailWrap.append('svg')
      .attr('viewBox', `0 0 ${W2} ${H2}`).attr('width', '100%').attr('height', H2);
    const g2 = svg2.append('g').attr('transform', `translate(${m2.left},${m2.top})`);

    // Domain xMax = base + somme positive, à partir de benefs[prev]
    const base = benefs[prev] || 0;
    const positives = d.facteurs.filter(f => f.v >= 0).reduce((s,f) => s+f.v, 0);
    const negatives = d.facteurs.filter(f => f.v < 0).reduce((s,f) => s+f.v, 0);
    const xMin2 = Math.min(base + negatives, benefs[year]) - 5;
    const xMax2 = Math.max(base + positives, benefs[year]) + 5;
    const xS = d3.scaleLinear().domain([xMin2, xMax2]).range([0, w2]);

    // Bar : base (gris)
    g2.append('rect').attr('x', xS(xMin2)).attr('y', 0)
      .attr('width', xS(base) - xS(xMin2)).attr('height', 20)
      .attr('fill', '#bbb6a8').attr('opacity', 0.5);
    g2.append('text').attr('x', xS(base) - 6).attr('y', 14)
      .attr('text-anchor', 'end').attr('font-size', 11).attr('fill', inkSoftColor())
      .text(`Base ${prev} : ${CHF1.format(base)} M`);

    // Facteurs empilés
    let cumul = base;
    d.facteurs.forEach((f, i) => {
      const y = 32 + i * 28;
      const start = cumul;
      const end = cumul + f.v;
      const x0 = xS(Math.min(start, end));
      const x1 = xS(Math.max(start, end));

      g2.append('rect').attr('x', x0).attr('y', y).attr('width', 0).attr('height', 20)
        .attr('fill', f.color)
        .transition().delay(i * 100).duration(500).attr('width', x1 - x0);

      const labelX = f.v >= 0 ? x1 + 6 : x0 - 6;
      const anchor = f.v >= 0 ? 'start' : 'end';
      g2.append('text').attr('x', labelX).attr('y', y + 14)
        .attr('text-anchor', anchor).attr('font-size', 11)
        .attr('fill', inkColor()).attr('font-weight', 500)
        .style('opacity', 0)
        .text(`${f.v >= 0 ? '+' : ''}${CHF1.format(f.v)} M  ·  ${f.label}`)
        .transition().delay(i * 100 + 400).duration(300).style('opacity', 1);

      cumul = end;
    });

    // Final
    const finalY = 32 + d.facteurs.length * 28 + 8;
    g2.append('rect').attr('x', xS(xMin2)).attr('y', finalY)
      .attr('width', xS(benefs[year]) - xS(xMin2)).attr('height', 20)
      .attr('fill', '#c8102e').attr('opacity', 0.85);
    g2.append('text').attr('x', xS(benefs[year]) - 6).attr('y', finalY + 14)
      .attr('text-anchor', 'end').attr('font-size', 11)
      .attr('fill', '#fff').attr('font-weight', 600)
      .text(`${year} : ${CHF1.format(benefs[year])} M`);

    // Source attribution
    detailWrap.append('div')
      .style('margin-top','12px').style('font-size','11px')
      .style('color','var(--ink-mute)').style('font-style','italic')
      .text(`Source : Rapport annuel Loro ${year} · faits-marquants compilés depuis les éditos du DG.`);
  }

  renderDetail(2024);
}

/* ============================================================
   ANGLE C — LE TISSU SOUS PERFUSION
   Dot plot : dépendance Loro des bénéficiaires (% de leur budget)
   ============================================================ */
function initDependency() {
  const container = d3.select('#viz-dependency');
  if (container.empty()) return;
  container.html('');

  // ============================================================
  // PARTIE 1 — DOT PLOT : cas documentés avec % du budget
  // ============================================================
  const cas = (DATA.summary.cas_dependance || []).slice()
    .sort((a, b) => (b.part_loro_pct || 0) - (a.part_loro_pct || 0));

  if (cas.length) {
    container.append('h4').attr('class', 'dep-section-title')
      .text('Quand la Loro pèse beaucoup dans un budget');
    container.append('p').attr('class', 'dep-section-sub')
      .text("Cas documentés où la subvention représente une part majeure du budget annuel. La transparence sur ce ratio reste rare — ce sont des exemples révélés par les associations elles-mêmes (témoignages dans CultureEnJeu) ou par la presse spécialisée (REISO, La Liberté). Au-delà de 25 %, on parle de dépendance critique.");

    const W = Math.max(700, container.node().clientWidth);
    const rowH = 70;
    const H = 60 + cas.length * rowH;
    const margin = { top: 36, right: 110, bottom: 50, left: 260 };
    const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;

    const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H);
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear().domain([0, 100]).range([0, w]);
    const y = d3.scaleBand().domain(cas.map(c => c.nom)).range([0, h]).padding(0.25);

    // Bande critique
    g.append('rect')
      .attr('x', x(25)).attr('y', 0)
      .attr('width', x(100) - x(25)).attr('height', h)
      .attr('fill', '#c8102e').attr('opacity', 0.05);
    g.append('text')
      .attr('x', x(25) + 6).attr('y', -10)
      .attr('font-size', 11).attr('fill', '#c8102e').attr('font-style', 'italic')
      .text('Zone de dépendance critique (≥ 25 %)');

    g.append('g').attr('transform', `translate(0,${h})`)
      .call(d3.axisBottom(x).tickFormat(d => d + ' %').ticks(6))
      .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
      .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

    cas.forEach((c, i) => {
      const yCenter = y(c.nom) + y.bandwidth() / 2;
      // Track
      g.append('rect')
        .attr('x', 0).attr('y', yCenter - 14)
        .attr('width', x(100)).attr('height', 28)
        .attr('fill', isDark() ? '#2a2823' : '#e8e5da');
      // Bar
      g.append('rect')
        .attr('x', 0).attr('y', yCenter - 14)
        .attr('width', 0).attr('height', 28)
        .attr('fill', CANTON_COLORS[c.canton] || '#c8102e')
        .transition().delay(i * 150).duration(800)
        .attr('width', x(c.part_loro_pct));

      // Label nom
      g.append('text')
        .attr('x', -14).attr('y', yCenter - 4)
        .attr('text-anchor', 'end')
        .attr('font-size', 14).attr('font-weight', 600).attr('fill', inkColor())
        .text(c.nom);
      g.append('text')
        .attr('x', -14).attr('y', yCenter + 12)
        .attr('text-anchor', 'end')
        .attr('font-size', 11).attr('fill', inkSoftColor())
        .text(`${c.categorie}${c.canton ? ' · ' + c.canton : ''}`);

      // %
      g.append('text')
        .attr('x', x(c.part_loro_pct) + 10).attr('y', yCenter)
        .attr('dy', '0.35em')
        .attr('font-family', 'Source Serif Pro, serif')
        .attr('font-size', 19).attr('font-weight', 600).attr('fill', CANTON_COLORS[c.canton] || '#c8102e')
        .style('opacity', 0)
        .text(c.part_loro_pct + ' %')
        .transition().delay(i * 150 + 600).duration(400).style('opacity', 1);

      // Overlay tooltip
      const subv = c.subvention_loro_2024_CHF || c.subvention_loro_2023_CHF;
      const budget = c.budget_total_2024_CHF || c.budget_total_2023_CHF;
      g.append('rect')
        .attr('x', 0).attr('y', yCenter - 14)
        .attr('width', x(100)).attr('height', 28)
        .attr('fill', 'transparent').style('cursor', 'help')
        .on('mouseover', ev => {
          showTip(`<div class="t-title">${c.nom}</div>
                   <div>Subvention Loro : ${fmtCompact(subv)} CHF</div>
                   <div>Budget total : ${fmtCompact(budget)} CHF</div>
                   <div class="t-meta">→ Loro = ${c.part_loro_pct} % du budget</div>
                   ${c.narratif ? `<div class="t-meta" style="margin-top:6px;font-style:italic">${c.narratif}</div>` : ''}
                   <div class="t-meta" style="margin-top:4px">Source : ${c.source}</div>`, ev.clientX, ev.clientY);
        }).on('mouseout', hideTip);
    });

    svg.append('text')
      .attr('x', margin.left).attr('y', H - 14)
      .attr('font-size', 11).attr('fill', inkMuteColor()).attr('font-style', 'italic')
      .text("Sources : REISO 2026, CultureEnJeu nº53, rapports d'activité des associations, rapports annuels Cinéforom.");
  }

  // ============================================================
  // PARTIE 2 — BÉNÉFICIAIRES PAR CANTON, AVEC FILTRE D'ANNÉE
  // ============================================================
  if (!DATA.dependance || !DATA.dependance.cas) return;

  container.append('h4').attr('class', 'dep-section-title').style('margin-top', '54px')
    .text("Les visages de l'argent — bénéficiaires par canton");
  container.append('p').attr('class', 'dep-section-sub')
    .text("Pour chaque canton romand, les institutions notables identifiées dans les BRB 2024 et 2025. Cliquez sur un canton pour explorer. Le filtre d'année permet de voir l'évolution entre 2024 et 2025 (et les organes répartiteurs).");

  // Year filter (tabs)
  const yearBar = container.append('div').attr('class', 'dep-year-tabs')
    .style('display', 'flex').style('gap', '8px').style('margin-bottom', '14px')
    .style('align-items', 'center').style('flex-wrap', 'wrap');
  yearBar.append('span').text('Année :')
    .style('font-size', '11px').style('color', 'var(--ink-mute)')
    .style('letter-spacing', '0.14em').style('text-transform', 'uppercase');

  const allEntries = [];
  Object.entries(DATA.dependance.cas).forEach(([code, list]) => {
    list.forEach(item => allEntries.push({ ...item, canton: code }));
  });
  const allYears = [...new Set(allEntries.map(e => e.annee).filter(Boolean))].sort();
  let activeYear = 'all';

  // Canton tabs row
  const tabsRow = container.append('div').attr('class', 'canton-tabs');
  const contentDiv = container.append('div').attr('class', 'canton-content');

  const cantonOrder = ['VD', 'FR', 'GE', 'VS', 'NE', 'JU'];
  let activeCanton = 'VD';

  function renderCanton(code, yr) {
    contentDiv.html('');
    let items = (DATA.dependance.cas[code] || []).slice();
    if (yr !== 'all') items = items.filter(i => i.annee === yr);
    items.sort((a, b) => (b.montant_CHF || 0) - (a.montant_CHF || 0));

    if (!items.length) {
      contentDiv.append('p').style('color', 'var(--ink-mute)').style('font-style', 'italic')
        .text(`Aucun bénéficiaire répertorié pour ${CANTON_NAMES[code]} en ${yr === 'all' ? 'toute année' : yr}.`);
      return;
    }

    const summary = contentDiv.append('div').attr('class', 'canton-summary')
      .style('margin-bottom', '14px').style('font-size', '13px').style('color', 'var(--ink-soft)')
      .html(`<strong>${items.length}</strong> bénéficiaire${items.length > 1 ? 's' : ''} listé${items.length > 1 ? 's' : ''} pour <strong>${CANTON_NAMES[code]}</strong>${yr !== 'all' ? ' en ' + yr : ''}. Total visible : <strong>${fmtCompact(items.reduce((s, x) => s + (x.montant_CHF || 0), 0))} CHF</strong>.`);

    const grid = contentDiv.append('div').attr('class', 'benef-grid');
    items.forEach(item => {
      const card = grid.append('div').attr('class', 'benef-card')
        .style('border-left', `4px solid ${CANTON_COLORS[code] || '#888'}`);

      const top = card.append('div').attr('class', 'benef-card-top');
      top.append('div').attr('class', 'benef-name').text(item.nom);
      if (item.montant_CHF) {
        top.append('div').attr('class', 'benef-amount')
          .style('color', CANTON_COLORS[code])
          .text(item.montant_CHF >= 1e6 ? `${(item.montant_CHF / 1e6).toFixed(2)} M` : `${(item.montant_CHF / 1000).toFixed(0)} k`);
      }
      card.append('div').attr('class', 'benef-meta')
        .text(`${item.secteur}${item.annee ? ' · ' + item.annee : ''}`);
      if (item.narratif) {
        card.append('div').attr('class', 'benef-narratif').text(item.narratif);
      }
      if (item.pct_budget) {
        card.append('div').attr('class', 'benef-pct')
          .html(`<strong>${item.pct_budget} %</strong> du budget annuel`);
      }
      if (item.source) {
        card.append('div').attr('class', 'benef-source').text(`Source : ${item.source}`);
      }
    });
  }

  // Year buttons
  ['all', ...allYears].forEach(yr => {
    yearBar.append('button')
      .attr('class', 'btn-year' + (yr === activeYear ? ' active' : ''))
      .text(yr === 'all' ? 'Toutes' : yr)
      .on('click', function() {
        activeYear = yr;
        yearBar.selectAll('.btn-year').classed('active', false);
        d3.select(this).classed('active', true);
        renderCanton(activeCanton, activeYear);
      });
  });

  // Canton tabs
  cantonOrder.forEach(code => {
    tabsRow.append('button')
      .attr('class', 'canton-tab' + (code === activeCanton ? ' active' : ''))
      .style('border-color', CANTON_COLORS[code] || '#888')
      .html(`<span class="tab-canton-code">${code}</span> <span class="tab-canton-name">${CANTON_NAMES[code]}</span>`)
      .on('click', function() {
        activeCanton = code;
        tabsRow.selectAll('.canton-tab').classed('active', false);
        d3.select(this).classed('active', true);
        renderCanton(activeCanton, activeYear);
      });
  });

  renderCanton(activeCanton, activeYear);
}

/* ============================================================
   ACTE VIII bis — Le Jura, 47 ans dans la Confédération
   Aire chronologique 1979 → 2025 avec annotations narratives
   ============================================================ */
function initJuraHistoire() {
  const container = d3.select('#viz-jura-histoire');
  if (container.empty() || !DATA.juraHistoire) return;
  container.html('');

  const serie = (DATA.juraHistoire.serie || []).slice().sort((a, b) => a.annee - b.annee);
  const jalons = DATA.juraHistoire.jalons || [];
  if (!serie.length) return;

  const W = 1100, H = 520;
  const margin = { top: 70, right: 30, bottom: 60, left: 70 };
  const w = W - margin.left - margin.right, h = H - margin.top - margin.bottom;

  const svg = container.append('svg').attr('viewBox', `0 0 ${W} ${H}`)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .attr('width', '100%').attr('height', H).style('height', 'auto').style('max-height', '70vh');
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleLinear().domain([1978, 2027]).range([0, w]);
  const y = d3.scaleLinear().domain([0, d3.max(serie, d => d.recu_CHF) * 1.15]).range([h, 0]);

  // Reference at 1 M
  g.append('line').attr('x1', 0).attr('x2', w).attr('y1', y(1e6)).attr('y2', y(1e6))
    .attr('stroke', '#999').attr('stroke-dasharray', '2,4').attr('opacity', 0.55);
  g.append('text').attr('x', w - 4).attr('y', y(1e6) - 4)
    .attr('text-anchor', 'end').attr('font-size', 10).attr('fill', inkMuteColor())
    .text('1 M CHF');

  // Axes
  g.append('g').attr('transform', `translate(0,${h})`)
    .call(d3.axisBottom(x).tickFormat(d3.format('d')).ticks(10))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));
  g.append('g')
    .call(d3.axisLeft(y).tickFormat(d => d >= 1e6 ? `${d / 1e6} M` : d >= 1000 ? `${d / 1000}k` : d).ticks(6))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '11px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // Aire
  const area = d3.area()
    .x(d => x(d.annee)).y0(h).y1(d => y(d.recu_CHF))
    .curve(d3.curveMonotoneX);
  g.append('path').datum(serie)
    .attr('fill', CANTON_COLORS.JU || '#c97b3a').attr('opacity', 0.2).attr('d', area);

  // Ligne
  const line = d3.line()
    .x(d => x(d.annee)).y(d => y(d.recu_CHF))
    .curve(d3.curveMonotoneX);
  g.append('path').datum(serie)
    .attr('fill', 'none').attr('stroke', CANTON_COLORS.JU || '#c97b3a').attr('stroke-width', 2.5)
    .attr('d', line);

  // Points
  g.selectAll('circle.jura-pt').data(serie).enter().append('circle')
    .attr('class', 'jura-pt')
    .attr('cx', d => x(d.annee)).attr('cy', d => y(d.recu_CHF))
    .attr('r', 3.5).attr('fill', CANTON_COLORS.JU || '#c97b3a').style('cursor', 'help')
    .on('mouseover', (ev, d) => {
      showTip(`<div class="t-title">${d.annee}</div>
               <div>${d.recu_CHF >= 1e6 ? CHF1.format(d.recu_CHF / 1e6) + ' M CHF' : Math.round(d.recu_CHF / 1000) + 'k CHF'}</div>`,
        ev.clientX, ev.clientY);
    }).on('mouseout', hideTip);

  // Titre / sous-titre
  svg.append('text').attr('x', margin.left).attr('y', 28)
    .attr('font-family', 'Source Serif Pro, serif').attr('font-size', 20)
    .attr('font-weight', 600).attr('fill', CANTON_COLORS.JU || '#c97b3a')
    .text("Le Jura : 47 ans dans la Confédération, autant d'années Loro");
  svg.append('text').attr('x', margin.left).attr('y', 50)
    .attr('font-size', 12).attr('fill', inkSoftColor())
    .text(`De 145'786 CHF en 1979 à ${CHF1.format(serie[serie.length - 1].recu_CHF / 1e6)} M en 2025 — cumul estimé : ~${CHF1.format(DATA.juraHistoire._meta.cumul_estime_CHF / 1e6)} M CHF`);

  // Annotations
  const annotations = [
    { annee: 1979, text: "1ʳᵉ année dans la Confédération · 145'786 CHF", dx: 40, dy: -32 },
    { annee: 1995, text: "Premier million franchi (2,5 M)", dx: 20, dy: -42 },
    { annee: 2016, text: "+2 M exceptionnels — création Théâtre du Jura", dx: -10, dy: -70 },
    { annee: 2025, text: "Record : 8,7 M · prélèvement passe à 20 %", dx: -240, dy: -30 },
  ];
  annotations.forEach(a => {
    const d = serie.find(s => s.annee === a.annee);
    if (!d) return;
    const cx = x(a.annee), cy = y(d.recu_CHF);
    g.append('line')
      .attr('x1', cx).attr('y1', cy)
      .attr('x2', cx + a.dx).attr('y2', cy + a.dy)
      .attr('stroke', inkSoftColor()).attr('stroke-width', 0.8).attr('stroke-dasharray', '2,2');
    g.append('text').attr('x', cx + a.dx).attr('y', cy + a.dy - 4)
      .attr('text-anchor', 'start')
      .attr('font-size', 11).attr('fill', inkColor()).attr('font-weight', 500)
      .text(a.text);
    // Cercle d'emphase
    g.append('circle').attr('cx', cx).attr('cy', cy)
      .attr('r', 7).attr('fill', 'none')
      .attr('stroke', CANTON_COLORS.JU || '#c97b3a').attr('stroke-width', 2);
  });

  // Annotation Moutier 2026
  const x2026 = x(2026);
  g.append('line').attr('x1', x2026).attr('x2', x2026)
    .attr('y1', 0).attr('y2', h).attr('stroke', '#888').attr('stroke-dasharray', '4,3');
  g.append('text').attr('x', x2026 - 6).attr('y', 14).attr('text-anchor', 'end')
    .attr('font-size', 10).attr('fill', inkMuteColor()).attr('font-style', 'italic')
    .text('1.1.2026 : Moutier rejoint le Jura');
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

/* ============================================================
   INTERMÈDE — Part LoRo dans le total CA loterie suisse 1924-2018
   Source : Office fédéral de la justice (BFJ)
   ============================================================ */
function initShareSuisse() {
  const container = d3.select('#viz-share-suisse');
  if (container.empty() || !DATA.historique) return;
  container.html('');

  // Garder uniquement les années où on a CA Loro ET CA total Suisse
  // (les pré-1938 ont seulement le total, on les inclut pour le contexte mais
  // sans calcul de ratio)
  const hist = DATA.historique.filter(d =>
    d.ca_total_suisse_M != null && d.annee >= 1924 && d.annee <= 2018
  );
  // Sous-ensemble avec ratio calculable
  const withRatio = hist.filter(d => d.ca_M != null);
  withRatio.forEach(d => { d.share = d.ca_M / d.ca_total_suisse_M * 100; });

  const W = 1200, H = 560;
  const margin = { top: 50, right: 120, bottom: 60, left: 70 };
  const w = W - margin.left - margin.right;
  const h = H - margin.top - margin.bottom;

  const svg = container.append('svg')
    .attr('viewBox', `0 0 ${W} ${H}`)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .attr('width', '100%').attr('height', H)
    .style('height', 'auto')
    .style('display', 'block');

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleLinear().domain([1924, 2018]).range([0, w]);
  const y = d3.scaleLinear().domain([0, 70]).range([h, 0]).nice();

  // Grille horizontale (% par tranches de 10)
  g.selectAll('.grid').data(y.ticks(7)).enter().append('line')
    .attr('x1', 0).attr('x2', w).attr('y1', d => y(d)).attr('y2', d => y(d))
    .attr('stroke', ruleColor()).attr('stroke-dasharray', '2,3').attr('opacity', 0.6);

  // Axes
  g.append('g').attr('transform', `translate(0,${h})`)
    .call(d3.axisBottom(x).tickFormat(d3.format('d')).ticks(10))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '12px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));
  g.append('g')
    .call(d3.axisLeft(y).tickFormat(d => d + ' %').ticks(7))
    .call(s => s.selectAll('text').attr('fill', inkSoftColor()).style('font-size', '12px'))
    .call(s => s.selectAll('path,line').attr('stroke', ruleColor()));

  // Titre + sous-titre dans la viz
  svg.append('text')
    .attr('x', margin.left).attr('y', 28)
    .attr('font-size', 13).attr('fill', inkSoftColor()).attr('letter-spacing', '0.04em')
    .text('Part de la Loterie Romande dans le CA total des loteries suisses · % par année');

  // Bandes de couleur pour les époques narratives
  const periods = [
    { from: 1924, to: 1937, label: 'Avant LoRo',           color: 'rgba(140,140,140,0.06)' },
    { from: 1937, to: 1969, label: 'Domination déclinante', color: 'rgba(200,16,46,0.04)' },
    { from: 1969, to: 2006, label: 'Marginalité (Sport-Toto + SEVA)', color: 'rgba(91,141,239,0.05)' },
    { from: 2007, to: 2018, label: 'Reprise (Sport-Toto absorbé)',   color: 'rgba(46,160,138,0.07)' },
  ];
  g.selectAll('.period').data(periods).enter().append('rect')
    .attr('x', d => x(d.from))
    .attr('y', 0)
    .attr('width', d => x(d.to) - x(d.from))
    .attr('height', h)
    .attr('fill', d => d.color);

  // Aire sous la courbe
  const area = d3.area().curve(d3.curveMonotoneX)
    .x(d => x(d.annee)).y0(h).y1(d => y(d.share));
  g.append('path').datum(withRatio)
    .attr('fill', '#c8102e').attr('opacity', 0.08)
    .attr('d', area);

  // Ligne principale
  const line = d3.line().curve(d3.curveMonotoneX)
    .x(d => x(d.annee)).y(d => y(d.share));
  g.append('path').datum(withRatio)
    .attr('fill', 'none').attr('stroke', '#c8102e').attr('stroke-width', 2.5)
    .attr('d', line);

  // Points sur la courbe
  g.selectAll('.pt').data(withRatio).enter().append('circle')
    .attr('cx', d => x(d.annee)).attr('cy', d => y(d.share))
    .attr('r', d => [1940, 1970, 1990, 2007, 2018].includes(d.annee) ? 5 : 2.5)
    .attr('fill', '#c8102e').attr('stroke', 'white').attr('stroke-width', 1.5)
    .style('cursor', 'pointer')
    .on('mouseover', function(ev, d) {
      d3.select(this).attr('r', 7);
      showTip(`<strong>${d.annee}</strong><br>
        LoRo: <strong>${d3.format(',.1f')(d.ca_M)} M CHF</strong> (${d.share.toFixed(1)}%)<br>
        Total Suisse: ${d3.format(',.0f')(d.ca_total_suisse_M)} M CHF`,
        ev.pageX, ev.pageY);
    })
    .on('mouseout', function(ev, d) {
      d3.select(this).attr('r', [1940, 1970, 1990, 2007, 2018].includes(d.annee) ? 5 : 2.5);
      hideTip();
    });

  // Annotations clés (positionnées au-dessus des points pivots)
  const annotations = [
    { annee: 1940, label: '38 % à ses débuts',          dy: -25, anchor: 'start' },
    { annee: 1970, label: '5 %  Sport-Toto + SEVA dominent', dy: 24,  anchor: 'middle' },
    { annee: 2007, label: '2007 transfert Sport-Toto',  dy: -50, anchor: 'middle' },
    { annee: 2018, label: '55 % aujourd\'hui',          dy: -25, anchor: 'end' },
  ];
  annotations.forEach(a => {
    const d = withRatio.find(x => x.annee === a.annee);
    if (!d) return;
    g.append('text')
      .attr('x', x(a.annee))
      .attr('y', y(d.share) + a.dy)
      .attr('text-anchor', a.anchor)
      .attr('font-size', 12)
      .attr('font-style', 'italic')
      .attr('fill', '#8a0a1f')
      .text(a.label);
  });

  // Marqueur LoRo création 1938
  const x1938 = x(1938);
  g.append('line')
    .attr('x1', x1938).attr('x2', x1938).attr('y1', 0).attr('y2', h)
    .attr('stroke', '#1a1917').attr('stroke-width', 1)
    .attr('stroke-dasharray', '4,4').attr('opacity', 0.4);
  g.append('text')
    .attr('x', x1938 + 6).attr('y', 14)
    .attr('font-size', 11).attr('font-style', 'italic').attr('fill', inkColor())
    .text('1938 — naissance de la LoRo');

  // Légende latérale (encart en haut à droite)
  const legend = svg.append('g')
    .attr('transform', `translate(${W - margin.right + 12},${margin.top + 20})`);
  legend.append('text').attr('x', 0).attr('y', 0).attr('font-size', 11)
    .attr('fill', inkSoftColor()).attr('font-weight', 600).text('Lecture :');
  ['LoRo seule a',
   'depuis 95 ans',
   'connu trois',
   'régimes. 1924',
   'précède la LoRo.',
   '',
   '1938-1969 :',
   'présence forte',
   'dans un marché',
   'encore petit.',
   '',
   '1970-2006 :',
   'Sport-Toto et',
   'SEVA captent',
   'l\'essentiel.',
   '',
   '2007+ :',
   'LoRo + Swisslos',
   'reprennent',
   'Sport-Toto.'
  ].forEach((line, i) => {
    legend.append('text')
      .attr('x', 0).attr('y', 16 + i * 13)
      .attr('font-size', 10).attr('fill', inkSoftColor())
      .text(line);
  });
}

function initLoroVsSwisslos() {
  const container = d3.select('#viz-loro-vs-swisslos');
  if (container.empty()) return;
  if (!DATA.swisslos) return;
  container.html('');

  const m2024 = DATA.swisslos.comparaison_loro_2024.metriques;
  const m2025 = DATA.swisslos.comparaison_loro_2025.metriques;

  // Catégorisation visuelle des métriques
  const sections = {
    'Échelle': ['PBJ / BSE (M CHF)', 'Bénéfice net (M CHF)', 'Total actif', 'Capitaux propres / réserves'],
    'Efficacité': ['Ratio bénéfice/PBJ', 'Commissions / PBJ'],
    'Structure de coûts': ['Commissions points de vente', 'Informatique', 'Personnel', 'Marketing/Publicité+Promo', 'Amortissements', 'Taxe jeu excessif (0,5 %)'],
    'Périmètre': ['EPT moyens', 'Nb cantons membres', 'Pop. desservie (M)'],
    'Coussin': ['Provision risque exploitation', 'Réserves libres']
  };

  // Helpers
  function fmtUnit(val, unite) {
    if (val == null) return 'n.d.';
    const u = unite ? unite.replace('M CHF', 'M').replace('M hab.', 'M') : '';
    return CHF1.format(val) + (u ? ' ' + u : '');
  }

  const W = container.node().clientWidth || 900;
  // Computed height: section header (22) + each metric row (40) + section gap (12) per section + top/bottom margins
  const rowH = 40;
  const sectionGap = 14;
  const sectionHeaderH = 26;
  let totalRows = 0; let totalSections = 0;
  Object.values(sections).forEach(arr => { totalRows += arr.length; totalSections += 1; });
  const H = 80 + totalSections * (sectionHeaderH + sectionGap) + totalRows * rowH;

  const margin = { top: 70, right: 20, bottom: 30, left: 240 };
  const w = W - margin.left - margin.right;
  const halfW = (w - 40) / 2; // 40px gutter in the middle for centerline
  const centerX = margin.left + w / 2;

  const svg = container.append('svg')
    .attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%').attr('height', H)
    .style('height', 'auto')
    .style('display', 'block');

  // ============== HEADERS ==============
  // Top legend: LORO (left) / SWISSLOS (right) with year sub-legend
  svg.append('text').attr('x', margin.left + w / 4).attr('y', 22)
    .attr('text-anchor', 'middle').attr('font-size', 16).attr('font-weight', 700).attr('fill', '#c8102e')
    .attr('font-family', 'Source Serif Pro, serif')
    .text('LORO');
  svg.append('text').attr('x', margin.left + 3 * w / 4).attr('y', 22)
    .attr('text-anchor', 'middle').attr('font-size', 16).attr('font-weight', 700).attr('fill', inkColor())
    .attr('font-family', 'Source Serif Pro, serif')
    .text('SWISSLOS');

  // Year sub-legend (color blocks)
  function legendItem(g, color, label, x) {
    g.append('rect').attr('x', x).attr('y', 0).attr('width', 14).attr('height', 14).attr('fill', color).attr('opacity', 0.55);
    g.append('text').attr('x', x + 20).attr('y', 11).attr('font-size', 11).attr('fill', inkSoftColor()).text(label);
  }
  const legG = svg.append('g').attr('transform', `translate(${margin.left + w / 4 - 70}, 32)`);
  legendItem(legG, '#c8102e', '2024', 0);
  legendItem(legG.append('g').attr('transform', 'translate(70, 0)'), '#c8102e', '2025', 0);
  legG.selectAll('rect').filter((d, i) => i === 1).attr('opacity', 1);
  // For swisslos side
  const legG2 = svg.append('g').attr('transform', `translate(${margin.left + 3 * w / 4 - 70}, 32)`);
  legendItem(legG2, '#1a1917', '2024', 0);
  legendItem(legG2.append('g').attr('transform', 'translate(70, 0)'), '#1a1917', '2025', 0);
  legG2.selectAll('rect').filter((d, i) => i === 1).attr('opacity', 1);

  // Centerline
  svg.append('line').attr('x1', centerX).attr('x2', centerX).attr('y1', 60).attr('y2', H - 10)
    .attr('stroke', ruleColor()).attr('stroke-width', 1).attr('opacity', 0.5);

  let cursorY = margin.top;

  Object.entries(sections).forEach(([sectionName, metricLabels]) => {
    // Section header — italic serif, full width subtle bar above
    svg.append('line').attr('x1', margin.left).attr('x2', W - margin.right)
      .attr('y1', cursorY).attr('y2', cursorY)
      .attr('stroke', ruleColor()).attr('stroke-width', 0.5).attr('opacity', 0.4);
    svg.append('text')
      .attr('x', margin.left).attr('y', cursorY + 17)
      .attr('font-family', 'Source Serif Pro, serif').attr('font-style', 'italic')
      .attr('font-size', 13).attr('fill', inkSoftColor())
      .text(sectionName);
    cursorY += sectionHeaderH;

    metricLabels.forEach(lbl => {
      const item24 = m2024.find(x => x.label === lbl);
      const item25 = m2025.find(x => x.label === lbl);
      if (!item24 && !item25) return;

      const unite = (item24 && item24.unite) || (item25 && item25.unite) || '';

      // === Label métrique à gauche (lisible !) ===
      svg.append('text')
        .attr('x', margin.left - 12).attr('y', cursorY + 18)
        .attr('text-anchor', 'end')
        .attr('font-size', 13).attr('font-weight', 500)
        .attr('fill', inkColor())
        .text(lbl);

      // Unit small below label
      if (unite && !unite.match(/^%$/)) {
        svg.append('text')
          .attr('x', margin.left - 12).attr('y', cursorY + 32)
          .attr('text-anchor', 'end')
          .attr('font-size', 10).attr('fill', inkSoftColor())
          .text(unite);
      }

      // === Calcule échelle locale (max des 4 valeurs disponibles) ===
      const allVals = [item24, item25].flatMap(i => i ? [i.loro, i.swisslos] : [])
        .filter(v => v != null && !Number.isNaN(v));
      const maxVal = allVals.length ? Math.max(...allVals) : 0;
      if (maxVal === 0) {
        // Just write "n.d." both sides
        svg.append('text').attr('x', centerX - 8).attr('y', cursorY + 22).attr('text-anchor', 'end')
          .attr('font-size', 11).attr('fill', inkSoftColor()).attr('font-style', 'italic').text('n.d.');
        svg.append('text').attr('x', centerX + 8).attr('y', cursorY + 22).attr('text-anchor', 'start')
          .attr('font-size', 11).attr('fill', inkSoftColor()).attr('font-style', 'italic').text('n.d.');
        cursorY += rowH;
        return;
      }
      const x = d3.scaleLinear().domain([0, maxVal]).range([0, halfW]);

      // === LORO side (gauche, barres groupées 2024 sur le haut, 2025 en bas) ===
      const barH = 11, barGap = 3;
      // Helper: place value text inside the bar if it would collide with the row label outside.
      // Threshold: bar fills > 65% of halfW → render inside, right-anchored, white.
      const INSIDE_THRESHOLD = halfW * 0.65;
      // 2024 Loro
      if (item24 && item24.loro != null) {
        const lW = x(item24.loro);
        svg.append('rect')
          .attr('x', centerX - 12 - lW)
          .attr('y', cursorY + 6).attr('width', lW).attr('height', barH)
          .attr('fill', '#c8102e').attr('opacity', 0.55);
        const isWide = lW > INSIDE_THRESHOLD;
        svg.append('text')
          .attr('x', isWide ? (centerX - 12 - 6) : (centerX - 12 - lW - 6))
          .attr('y', cursorY + 6 + barH - 1)
          .attr('text-anchor', 'end').attr('font-size', 11)
          .attr('fill', isWide ? 'white' : '#c8102e')
          .text(fmtUnit(item24.loro, unite) + (item24.loro_est ? ' (est.)' : ''));
      } else {
        svg.append('text').attr('x', centerX - 12).attr('y', cursorY + 6 + barH - 1)
          .attr('text-anchor', 'end').attr('font-size', 10).attr('fill', inkSoftColor()).attr('font-style', 'italic').text('n.d.');
      }
      // 2025 Loro
      if (item25 && item25.loro != null) {
        const lW = x(item25.loro);
        const rect = svg.append('rect')
          .attr('x', centerX - 12 - lW)
          .attr('y', cursorY + 6 + barH + barGap).attr('width', lW).attr('height', barH)
          .attr('fill', '#c8102e').attr('opacity', 1);
        if (item25.loro_est) rect.attr('stroke', '#c8102e').attr('stroke-width', 1.5).attr('stroke-dasharray', '3,2').attr('fill-opacity', 0.5);
        const isWide = lW > INSIDE_THRESHOLD;
        svg.append('text')
          .attr('x', isWide ? (centerX - 12 - 6) : (centerX - 12 - lW - 6))
          .attr('y', cursorY + 6 + barH + barGap + barH - 1)
          .attr('text-anchor', 'end').attr('font-size', 11).attr('font-weight', 600)
          .attr('fill', isWide ? 'white' : '#c8102e')
          .text(fmtUnit(item25.loro, unite) + (item25.loro_est ? ' (est.)' : ''));
      } else {
        svg.append('text').attr('x', centerX - 12).attr('y', cursorY + 6 + barH + barGap + barH - 1)
          .attr('text-anchor', 'end').attr('font-size', 10).attr('fill', inkSoftColor()).attr('font-style', 'italic').text('n.d.');
      }

      // === SWISSLOS side (droite) ===
      // 2024
      if (item24 && item24.swisslos != null) {
        const sW = x(item24.swisslos);
        svg.append('rect')
          .attr('x', centerX + 12).attr('y', cursorY + 6)
          .attr('width', sW).attr('height', barH)
          .attr('fill', '#1a1917').attr('opacity', 0.55);
        const isWide = sW > INSIDE_THRESHOLD;
        svg.append('text')
          .attr('x', isWide ? (centerX + 12 + 6) : (centerX + 12 + sW + 6))
          .attr('y', cursorY + 6 + barH - 1)
          .attr('text-anchor', isWide ? 'start' : 'start')
          .attr('font-size', 11).attr('fill', isWide ? 'white' : inkColor())
          .text(fmtUnit(item24.swisslos, unite) + (item24.swisslos_est ? ' (est.)' : ''));
      } else {
        svg.append('text').attr('x', centerX + 12).attr('y', cursorY + 6 + barH - 1)
          .attr('font-size', 10).attr('fill', inkSoftColor()).attr('font-style', 'italic').text('n.d.');
      }
      // 2025
      if (item25 && item25.swisslos != null) {
        const sW = x(item25.swisslos);
        const rect = svg.append('rect')
          .attr('x', centerX + 12).attr('y', cursorY + 6 + barH + barGap)
          .attr('width', sW).attr('height', barH)
          .attr('fill', '#1a1917').attr('opacity', 1);
        if (item25.swisslos_est) rect.attr('stroke', '#1a1917').attr('stroke-width', 1.5).attr('stroke-dasharray', '3,2').attr('fill-opacity', 0.5);
        const isWide = sW > INSIDE_THRESHOLD;
        svg.append('text')
          .attr('x', isWide ? (centerX + 12 + 6) : (centerX + 12 + sW + 6))
          .attr('y', cursorY + 6 + barH + barGap + barH - 1)
          .attr('font-size', 11).attr('font-weight', 600).attr('fill', isWide ? 'white' : inkColor())
          .text(fmtUnit(item25.swisslos, unite) + (item25.swisslos_est ? ' (est.)' : ''));
      } else {
        svg.append('text').attr('x', centerX + 12).attr('y', cursorY + 6 + barH + barGap + barH - 1)
          .attr('font-size', 10).attr('fill', inkSoftColor()).attr('font-style', 'italic').text('n.d.');
      }

      cursorY += rowH;
    });
    cursorY += sectionGap;
  });

  // Bottom note about estimates
  svg.append('text')
    .attr('x', margin.left).attr('y', H - 4)
    .attr('font-size', 10).attr('fill', inkSoftColor()).attr('font-style', 'italic')
    .text("Barres hachurées = estimations (Geschäftsbericht Swisslos 2025 et rapport financier Loro 2025 non encore publiés à la date du build).");
}

function initEditorialTimeline() {
  const container = d3.select('#viz-editorial-timeline');
  if (container.empty()) return;
  if (!DATA.editorial) return;
  container.html('');

  const annees = DATA.editorial.annees;

  // Group years into decades: 2012-2015, 2016-2019, 2020-2025
  const decadeBuckets = [
    { id: 'd1', label: '2012—2015',   min: 2012, max: 2015 },
    { id: 'd2', label: '2016—2019',   min: 2016, max: 2019 },
    { id: 'd3', label: '2020—2025',   min: 2020, max: 2025 },
  ];

  // Build the tab bar
  const tabBar = container.append('div').attr('class', 'editorial-tabs').attr('role', 'tablist');
  decadeBuckets.forEach((d, i) => {
    const count = annees.filter(a => a.year >= d.min && a.year <= d.max).length;
    tabBar.append('button')
      .attr('class', 'editorial-tab' + (i === decadeBuckets.length - 1 ? ' active' : '')) // last decade (most recent) active by default
      .attr('data-decade', d.id)
      .attr('role', 'tab')
      .attr('aria-selected', i === decadeBuckets.length - 1 ? 'true' : 'false')
      .html(`${d.label} <span class="editorial-tab-count">(${count})</span>`);
  });

  // List container — we'll render the active decade only
  const listWrap = container.append('div').attr('class', 'editorial-list-wrap');

  function renderDecade(decadeId) {
    const decade = decadeBuckets.find(d => d.id === decadeId);
    if (!decade) return;
    const rows = annees
      .filter(a => a.year >= decade.min && a.year <= decade.max)
      .sort((a, b) => b.year - a.year);  // most recent first within decade

    listWrap.html('');
    const list = listWrap.append('div').attr('class', 'editorial-list');
    rows.forEach(a => {
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

  // Wire the tab switching
  tabBar.selectAll('.editorial-tab').on('click', function(ev) {
    const decadeId = this.dataset.decade;
    tabBar.selectAll('.editorial-tab')
      .classed('active', false)
      .attr('aria-selected', 'false');
    d3.select(this).classed('active', true).attr('aria-selected', 'true');
    renderDecade(decadeId);
  });

  // Initial render — most recent decade
  renderDecade(decadeBuckets[decadeBuckets.length - 1].id);
}

/* ============================================================
   ACTE IX — BRB 2025 EXPLORER (~600 bénéficiaires)
   ============================================================ */

// Couleur pour Suisse romande "R" (utils.js a déjà VD/FR/VS/NE/GE/JU)
const CANTON_COLORS_R = '#888';
const BRB_CANTON_LABELS = {
  VD: 'Vaud', FR: 'Fribourg', VS: 'Valais',
  NE: 'Neuchâtel', GE: 'Genève', JU: 'Jura', R: 'Suisse rom.'
};
const BRB_SECTEUR_COLORS = {
  'Action sociale': '#e44d4d',
  'Jeunesse': '#5b8def',
  'Santé': '#2ea08a',
  'Culture': '#f0a93d',
  'Formation': '#7c5bc7',
  'Patrimoine': '#c97b3a',
  'Environnement': '#7fb069',
  'Tourisme': '#d96b9a',
  'Sport': '#3d5a80'
};

// Helper local : couleur canton (gère "R" + 6 cantons)
function brbCantonColor(c) {
  return c === 'R' ? CANTON_COLORS_R : (CANTON_COLORS[c] || '#888');
}

// Format CHF compact pour BRB (utils.js a fmtCHF qui ajoute ' CHF' — ici on veut sans)
function brbFmtAmt(v) {
  if (v >= 1000000) return (v / 1000000).toFixed(2).replace(/\.?0+$/, '') + ' M';
  if (v >= 1000) return (v / 1000).toFixed(0) + ' k';
  return String(v);
}

/* ============================================================
   BRB 2025 LAZY LOADER
   Charges brb2025_full.json (1.7 MB) only when the user nears Acte IX.
   Triggers all 3 BRB visualisations once the data lands.
   Idempotent — repeated calls reuse the in-flight promise.
   ============================================================ */
function ensureBrbLoaded() {
  if (DATA.brb2025) return Promise.resolve(DATA.brb2025);
  if (DATA.brb2025_loading) return DATA.brb2025_loading;
  // Show a lightweight loading indicator in each BRB container
  ['viz-explorer', 'viz-multicantons', 'viz-longtail', 'viz-geomap'].forEach(id => {
    const el = document.getElementById(id);
    if (el && !el.children.length) {
      el.innerHTML = '<div style="padding:48px;text-align:center;color:var(--ink-mute);font-style:italic">Chargement de l\'inventaire BRB 2025 (≈ 1,7 Mo)…</div>';
    }
  });
  DATA.brb2025_loading = loadJSON('brb2025_full.json')
    .then(d => {
      DATA.brb2025 = d;
      DATA.brb2025_loading = null;
      // Now actually render the 4 viz
      initBrbExplorer();
      initBrbMulticantons();
      initBrbLongtail();
      initBrbGeomap();
      return d;
    })
    .catch(err => {
      console.error('Failed to load brb2025_full.json', err);
      ['viz-explorer', 'viz-multicantons', 'viz-longtail', 'viz-geomap'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = '<div style="padding:24px;color:var(--c-loro)">Erreur de chargement des données BRB. Rafraîchissez la page.</div>';
      });
    });
  return DATA.brb2025_loading;
}

function initBrbLazyTrigger() {
  // First container present is enough to attach the observer to.
  const target = document.getElementById('viz-explorer');
  if (!target) return;

  // Trigger when user clicks a hash link like #brb=canton:JU
  // (immediate load, then scroll-into-view once data lands)
  function maybeTriggerFromHash() {
    if (/#brb=/.test(window.location.hash)) {
      ensureBrbLoaded().then(() => {
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    }
  }
  window.addEventListener('hashchange', maybeTriggerFromHash);
  // On first page load if hash is already set
  if (/#brb=/.test(window.location.hash)) maybeTriggerFromHash();

  if ('IntersectionObserver' in window) {
    const obs = new IntersectionObserver((entries) => {
      if (entries.some(e => e.isIntersecting)) {
        ensureBrbLoaded();
        obs.disconnect();
      }
    }, { rootMargin: '800px 0px' });  // pre-load when within 800px of viewport
    obs.observe(target);
  } else {
    ensureBrbLoaded();
  }
}

function initBrbExplorer() {
  const container = document.getElementById('viz-explorer');
  if (!container || !DATA.brb2025) return;
  const entries = DATA.brb2025.entries.slice();
  const allCantons = ['VD', 'FR', 'VS', 'NE', 'GE', 'JU', 'R'];
  const allSecteurs = [...new Set(entries.map(e => e.secteur))].sort();

  // State
  // Initialize state — check URL hash for pre-filter (e.g., #brb=canton:JU)
  const state = { query: '', cantons: new Set(allCantons), secteurs: new Set(allSecteurs), sortBy: 'montant' };
  function applyHashFilter() {
    const m = window.location.hash.match(/brb=canton:([A-Z]{1,2})/);
    if (m && allCantons.includes(m[1])) {
      state.cantons = new Set([m[1]]);
    }
  }
  applyHashFilter();

  // Build chrome
  container.innerHTML = `
    <div class="brb-controls">
      <input type="search" class="brb-search" placeholder="Rechercher une association, une ville…">
      <div class="brb-filter-group">
        <span class="brb-filter-label">Canton :</span>
        <div class="brb-pills" data-filter="canton">
          ${allCantons.map(c => `<button class="brb-pill${state.cantons.has(c) ? ' active' : ''}" data-value="${c}" style="--pill-color:${brbCantonColor(c)}">${BRB_CANTON_LABELS[c]}</button>`).join('')}
        </div>
      </div>
      <div class="brb-filter-group">
        <span class="brb-filter-label">Secteur :</span>
        <div class="brb-pills" data-filter="secteur">
          ${allSecteurs.map(s => `<button class="brb-pill${state.secteurs.has(s) ? ' active' : ''}" data-value="${s}" style="--pill-color:${BRB_SECTEUR_COLORS[s] || '#888'}">${s}</button>`).join('')}
        </div>
      </div>
      <div class="brb-filter-group">
        <span class="brb-filter-label">Tri :</span>
        <select class="brb-sort">
          <option value="montant">Montant décroissant</option>
          <option value="montant_asc">Montant croissant</option>
          <option value="nom">Nom A→Z</option>
          <option value="canton">Canton</option>
        </select>
      </div>
    </div>
    <div class="brb-stats" id="brb-stats"></div>
    <div class="brb-list" id="brb-list"></div>
  `;

  const searchEl = container.querySelector('.brb-search');
  const sortEl = container.querySelector('.brb-sort');
  const statsEl = container.querySelector('#brb-stats');
  const listEl = container.querySelector('#brb-list');

  // Pagination state — initial 200 rows, +200 per "Voir plus" click
  const PAGE_SIZE = 200;
  let displayCount = PAGE_SIZE;

  function applyFilters(resetPagination = true) {
    if (resetPagination) displayCount = PAGE_SIZE;
    const q = state.query.toLowerCase().trim();
    let filtered = entries.filter(e => {
      if (!state.cantons.has(e.canton)) return false;
      if (!state.secteurs.has(e.secteur)) return false;
      if (q && !(
        (e.nom || '').toLowerCase().includes(q) ||
        (e.ville || '').toLowerCase().includes(q) ||
        (e.description || '').toLowerCase().includes(q)
      )) return false;
      return true;
    });

    // Sort
    if (state.sortBy === 'montant') filtered.sort((a, b) => b.montant_CHF - a.montant_CHF);
    else if (state.sortBy === 'montant_asc') filtered.sort((a, b) => a.montant_CHF - b.montant_CHF);
    else if (state.sortBy === 'nom') filtered.sort((a, b) => (a.nom || '').localeCompare(b.nom || ''));
    else if (state.sortBy === 'canton') filtered.sort((a, b) => a.canton.localeCompare(b.canton) || b.montant_CHF - a.montant_CHF);

    // Stats
    const totalEur = filtered.reduce((s, e) => s + e.montant_CHF, 0);
    statsEl.innerHTML = `<strong>${filtered.length}</strong> bénéficiaire${filtered.length > 1 ? 's' : ''} · <strong>${brbFmtAmt(totalEur)} CHF</strong> au total`;

    // Render with pagination
    const SHOWN = Math.min(filtered.length, displayCount);
    const max = filtered.length > 0 ? filtered[0].montant_CHF : 1;
    const rows = filtered.slice(0, SHOWN).map(e => {
      const widthPct = Math.max(1, (e.montant_CHF / max) * 100);
      const cColor = brbCantonColor(e.canton) || '#888';
      // Cross-canton aggregate badge: this beneficiary appears in multiple cantons
      const aggBadge = (e.agg_cantons && e.agg_cantons.length >= 2)
        ? `<span class="brb-agg-badge" title="Aussi présent dans : ${e.agg_cantons.filter(c => c !== e.canton).join(', ')}. Cumul ${e.agg_count} entrées = ${(e.agg_total_CHF/1000).toFixed(0)}'000 CHF">+${e.agg_cantons.length - 1}↗</span>`
        : '';
      return `
        <div class="brb-row">
          <div class="brb-row-bar" style="background: ${cColor}; width: ${widthPct}%;"></div>
          <div class="brb-row-content">
            <div class="brb-row-main">
              <span class="brb-canton-tag" style="background:${cColor}">${e.canton}</span>
              <span class="brb-row-name">${e.nom}</span>
              ${aggBadge}
              ${e.ville ? `<span class="brb-row-ville">· ${e.ville}</span>` : ''}
            </div>
            <div class="brb-row-meta">
              <span class="brb-row-secteur">${e.secteur}</span>
              ${e.description ? `<span class="brb-row-desc">— ${e.description}</span>` : ''}
              ${e.agg_cantons && e.agg_cantons.length >= 2 ? `<span class="brb-row-agg">Cumul tous cantons : <strong>${e.agg_total_CHF.toLocaleString('fr-CH').replace(/,/g, "'")} CHF</strong> (${e.agg_cantons.length} cantons)</span>` : ''}
            </div>
          </div>
          <div class="brb-row-montant">${e.montant_CHF.toLocaleString('fr-CH').replace(/,/g, "'")} <span class="brb-chf">CHF</span></div>
        </div>
      `;
    }).join('');

    const remaining = filtered.length - SHOWN;
    const showMoreBtn = remaining > 0
      ? `<div class="brb-more"><button class="brb-more-btn" type="button">Voir ${Math.min(remaining, PAGE_SIZE)} de plus <span class="brb-more-count">(${remaining} restants)</span></button></div>`
      : (filtered.length > PAGE_SIZE
        ? `<div class="brb-more"><span style="opacity:0.6">Toutes les ${filtered.length} entrées affichées.</span></div>`
        : '');
    listEl.innerHTML = rows + showMoreBtn;

    // Wire the "show more" button if present
    const moreBtn = listEl.querySelector('.brb-more-btn');
    if (moreBtn) {
      moreBtn.addEventListener('click', () => {
        displayCount += PAGE_SIZE;
        applyFilters(false);  // don't reset pagination
        // Scroll the new rows into view
        const lastRow = listEl.querySelectorAll('.brb-row')[SHOWN - 1];
        if (lastRow) lastRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
    }
  }

  searchEl.addEventListener('input', e => { state.query = e.target.value; applyFilters(); });
  sortEl.addEventListener('change', e => { state.sortBy = e.target.value; applyFilters(); });
  container.querySelectorAll('.brb-pills').forEach(group => {
    const filterType = group.dataset.filter;
    group.addEventListener('click', e => {
      const btn = e.target.closest('.brb-pill');
      if (!btn) return;
      const v = btn.dataset.value;
      const set = filterType === 'canton' ? state.cantons : state.secteurs;
      if (set.has(v)) {
        set.delete(v);
        btn.classList.remove('active');
      } else {
        set.add(v);
        btn.classList.add('active');
      }
      applyFilters();
    });
  });

  applyFilters();
}

/* ============================================================
   ACTE IX — BRB 2025 MULTICANTONS (Pass 2 — D)
   Top 20 bénéficiaires inter-cantonaux, bar horizontal empilé.
   Une barre = un bénéficiaire (nom normalisé) ; les segments sont
   les contributions par canton (incl. organe romand "R").
   ============================================================ */
function initBrbMulticantons() {
  const container = document.getElementById('viz-multicantons');
  if (!container || !DATA.brb2025) return;

  const entries = DATA.brb2025.entries;

  // Normalisation du nom — alignée sur le pattern clean_brb / explorer
  function normName(name) {
    if (!name) return '';
    let s = name.toLowerCase();
    s = s.replace(/^(assoc\.|association|fond\.|fondation|fond|sté|société|club|comité|verein|federation|féd\.)\s+/, '');
    s = s.replace(/,\s*[a-zéèôî' -]+$/i, '');
    s = s.normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
    s = s.replace(/[^a-z0-9]+/g, ' ').trim();
    return s;
  }

  // Stopwords FR pour détection des merges ambigus
  const STOPWORDS_FR = new Set([
    'le','la','les','l','un','une','des','du','de','d',
    'a','au','aux','et','ou','mais','donc','car','ni',
    'pour','sur','sous','avec','sans','dans','par','vers','en','entre','contre','depuis','durant','selon',
    'ce','cette','ces','cet','son','sa','ses','leur','leurs',
    'qui','que','quoi','dont','ou'
  ]);
  function specificTokens(normalized) {
    return normalized.split(/\s+/).filter(w => w.length >= 2 && !STOPWORDS_FR.has(w));
  }
  function hasAcronym(originalName) {
    // Mot entièrement en majuscules >= 3 lettres (acronyme distinctif)
    return /\b[A-Z]{3,}\b/.test(originalName);
  }

  // Agrégation : par nom normalisé, dict {canton -> sum}
  const agg = new Map();
  for (const e of entries) {
    const k = normName(e.nom || '');
    if (k.length < 4) continue;
    const m = e.montant_CHF || 0;
    if (!m) continue;
    const canton = e.canton || '?';
    let g = agg.get(k);
    if (!g) {
      g = { cantons: new Map(), total: 0, count: 0, sample_name: e.nom, sample_secteur: e.secteur, sample_ville: e.ville, originals: new Set() };
      agg.set(k, g);
    }
    g.cantons.set(canton, (g.cantons.get(canton) || 0) + m);
    g.total += m;
    g.count += 1;
    g.originals.add(e.nom || '');
  }

  // Filtre multi-cantons (>= 2 cantons distincts) AVEC haute confiance
  // Confiance = >= 2 tokens spécifiques OU au moins un acronyme dans les noms originaux
  const multi = [];
  for (const [k, g] of agg) {
    if (g.cantons.size < 2) continue;
    const toks = specificTokens(k);
    const anyAcronym = Array.from(g.originals).some(hasAcronym);
    if (toks.length >= 2 || anyAcronym) {
      multi.push({ key: k, ...g });
    }
  }
  multi.sort((a, b) => b.total - a.total);

  const top = multi.slice(0, 20);
  if (!top.length) {
    container.innerHTML = '<div style="padding:24px;color:var(--ink-mute)">Aucun bénéficiaire multi-cantons trouvé.</div>';
    return;
  }

  // Ordre canonique des cantons + R en fin (pour la légende et la pile)
  const CANTONS_USED = new Set();
  top.forEach(t => t.cantons.forEach((_, c) => CANTONS_USED.add(c)));
  const STACK_ORDER = ['VD', 'GE', 'VS', 'FR', 'NE', 'JU', 'R'].filter(c => CANTONS_USED.has(c));

  // Échelle commune : 0 → max total
  const maxTotal = top[0].total;

  // Render
  container.innerHTML = '';

  // Légende cantons
  const legend = document.createElement('div');
  legend.className = 'brb-multi-legend';
  STACK_ORDER.forEach(c => {
    const item = document.createElement('span');
    item.className = 'brb-multi-legend-item';
    item.innerHTML = `<span class="brb-multi-legend-swatch" style="background:${brbCantonColor(c)}"></span>${BRB_CANTON_LABELS[c]}`;
    legend.appendChild(item);
  });
  container.appendChild(legend);

  // Rows
  top.forEach((row, i) => {
    const rowEl = document.createElement('div');
    rowEl.className = 'brb-multi-row';

    // Rank
    const rank = document.createElement('div');
    rank.className = 'brb-multi-rank';
    rank.textContent = String(i + 1).padStart(2, '0');
    rowEl.appendChild(rank);

    // Name + meta
    const nameCell = document.createElement('div');
    nameCell.className = 'brb-multi-name-cell';
    const cleanName = (row.sample_name || '')
      .replace(/^Assoc\. /, 'Association ')
      .replace(/^Fond\. /, 'Fondation ')
      .replace(/^Sté /, 'Société ')
      .replace(/[\s\-—–]+$/, '')   // strip trailing dash/whitespace (PDF truncation)
      .trim();
    nameCell.innerHTML = `
      <div class="brb-multi-name">${cleanName}</div>
      <div class="brb-multi-meta">
        ${row.sample_secteur || '—'} ·
        ${row.cantons.size} cantons · ${row.count} attribution${row.count > 1 ? 's' : ''}
      </div>`;
    rowEl.appendChild(nameCell);

    // Bar (stacked) — width proportional to total / maxTotal
    const barWrap = document.createElement('div');
    barWrap.className = 'brb-multi-bar-wrap';
    const widthPct = (row.total / maxTotal) * 100;
    barWrap.style.width = widthPct.toFixed(2) + '%';

    // Segments ordered by STACK_ORDER, only those present
    const segs = STACK_ORDER
      .filter(c => row.cantons.has(c))
      .map(c => ({ canton: c, amount: row.cantons.get(c) }));

    segs.forEach(s => {
      const seg = document.createElement('div');
      seg.className = 'brb-multi-seg';
      const pct = (s.amount / row.total) * 100;
      seg.style.width = pct.toFixed(2) + '%';
      seg.style.background = brbCantonColor(s.canton);

      // Label inside if segment large enough
      if (pct >= 18) {
        const lbl = document.createElement('span');
        lbl.className = 'brb-multi-seg-label';
        lbl.textContent = s.canton;
        seg.appendChild(lbl);
      }

      // Hover tooltip
      seg.addEventListener('mouseenter', (ev) => {
        const r = seg.getBoundingClientRect();
        showTip(
          `<div class="t-title">${cleanName}</div>
           <div><span style="display:inline-block;width:9px;height:9px;background:${brbCantonColor(s.canton)};border-radius:2px;vertical-align:1px;margin-right:6px"></span>${BRB_CANTON_LABELS[s.canton]}</div>
           <div><strong>${brbFmtAmt(s.amount)} CHF</strong> · ${((s.amount / row.total) * 100).toFixed(0)}% du cumul</div>`,
          r.left + r.width / 2, r.top
        );
      });
      seg.addEventListener('mouseleave', hideTip);

      barWrap.appendChild(seg);
    });

    rowEl.appendChild(barWrap);

    // Total
    const totalCell = document.createElement('div');
    totalCell.className = 'brb-multi-total';
    totalCell.innerHTML = `${brbFmtAmt(row.total)}<span>CHF cumulés</span>`;
    rowEl.appendChild(totalCell);

    container.appendChild(rowEl);
  });
}

/* ============================================================
   ACTE IX — BRB 2025 LONG-TAIL (distribution log-scale)
   ============================================================ */
function initBrbLongtail() {
  const container = document.getElementById('viz-longtail');
  if (!container || !DATA.brb2025) return;
  const entries = DATA.brb2025.entries
    .filter(e => e.montant_CHF > 0)
    .slice()
    .sort((a, b) => b.montant_CHF - a.montant_CHF);

  const W = container.clientWidth || 800;
  const H = 480;
  const margin = { top: 30, right: 30, bottom: 60, left: 70 };
  const innerW = W - margin.left - margin.right;
  const innerH = H - margin.top - margin.bottom;

  const svg = d3.select(container).append('svg')
    .attr('viewBox', `0 0 ${W} ${H}`)
    .attr('width', '100%').attr('height', H)
    .style('height', 'auto').style('overflow', 'visible');

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleLinear().domain([1, entries.length]).range([0, innerW]);
  const y = d3.scaleLog().domain([Math.max(1, d3.min(entries, e => e.montant_CHF)), d3.max(entries, e => e.montant_CHF)]).range([innerH, 0]);

  // Axes
  const xAxis = d3.axisBottom(x).ticks(8).tickFormat(d3.format('d'));
  const yAxis = d3.axisLeft(y).tickFormat(d => brbFmtAmt(d) + '');
  g.append('g').attr('transform', `translate(0,${innerH})`).call(xAxis)
    .selectAll('text').style('fill', '#888').style('font-size', '12px');
  g.append('g').call(yAxis)
    .selectAll('text').style('fill', '#888').style('font-size', '12px');
  g.selectAll('.tick line').style('stroke', '#ddd');
  g.selectAll('.domain').style('stroke', '#ddd');

  // Axis labels
  svg.append('text').attr('x', W / 2).attr('y', H - 15)
    .attr('text-anchor', 'middle').style('font-size', '13px').style('fill', '#666')
    .text("rang du bénéficiaire (1 = plus gros montant)");
  svg.append('text').attr('transform', `translate(20,${H / 2}) rotate(-90)`)
    .attr('text-anchor', 'middle').style('font-size', '13px').style('fill', '#666')
    .text("montant CHF (échelle log)");

  // Reference lines: median, top 10
  const medianAmount = d3.median(entries, e => e.montant_CHF);
  g.append('line').attr('x1', 0).attr('x2', innerW)
    .attr('y1', y(medianAmount)).attr('y2', y(medianAmount))
    .style('stroke', '#999').style('stroke-dasharray', '3,3').style('opacity', 0.5);
  g.append('text').attr('x', innerW - 4).attr('y', y(medianAmount) - 4)
    .attr('text-anchor', 'end').style('font-size', '11px').style('fill', '#666')
    .text(`médiane ≈ ${brbFmtAmt(medianAmount)} CHF`);

  // Points
  const tooltip = d3.select(container).append('div').attr('class', 'brb-tooltip');
  const points = g.selectAll('circle').data(entries).join('circle')
    .attr('cx', (_, i) => x(i + 1))
    .attr('cy', d => y(d.montant_CHF))
    .attr('r', d => d.montant_CHF >= 500000 ? 5 : d.montant_CHF >= 50000 ? 3 : 2)
    .attr('fill', d => brbCantonColor(d.canton) || '#888')
    .attr('opacity', 0.7)
    .style('cursor', 'pointer')
    .on('mouseenter', function(event, d) {
      d3.select(this).attr('opacity', 1).attr('r', 7);
      const rect = container.getBoundingClientRect();
      tooltip.style('display', 'block')
        .style('left', (event.clientX - rect.left + 12) + 'px')
        .style('top', (event.clientY - rect.top + 12) + 'px')
        .html(`<strong>${d.nom}</strong>${d.ville ? `<br><span style="opacity:.7">${d.ville}</span>` : ''}<br><span style="color:${brbCantonColor(d.canton)}">●</span> ${BRB_CANTON_LABELS[d.canton]} · ${d.secteur}<br><strong>${d.montant_CHF.toLocaleString('fr-CH').replace(/,/g, "'")} CHF</strong>`);
    })
    .on('mouseleave', function(event, d) {
      d3.select(this).attr('opacity', 0.7).attr('r', d.montant_CHF >= 500000 ? 5 : d.montant_CHF >= 50000 ? 3 : 2);
      tooltip.style('display', 'none');
    });

  // Annotate top 3
  entries.slice(0, 3).forEach((d, i) => {
    const cx = x(i + 1), cy = y(d.montant_CHF);
    g.append('text').attr('x', cx + 10).attr('y', cy + i * 14 + 5)
      .style('font-size', '11px').style('fill', '#333')
      .text(`${d.nom.length > 40 ? d.nom.slice(0, 38) + '…' : d.nom} (${brbFmtAmt(d.montant_CHF)} CHF)`);
  });

  // Legend (canton colors)
  const legendG = svg.append('g').attr('transform', `translate(${margin.left + 20}, ${margin.top + 10})`);
  const cantons = ['VD', 'FR', 'VS', 'NE', 'GE', 'JU'];
  cantons.forEach((c, i) => {
    const lg = legendG.append('g').attr('transform', `translate(${i * 70}, 0)`);
    lg.append('circle').attr('r', 5).attr('fill', brbCantonColor(c));
    lg.append('text').attr('x', 10).attr('y', 4).style('font-size', '12px').style('fill', '#666').text(BRB_CANTON_LABELS[c]);
  });
}

/* ============================================================
   ACTE IX — BRB 2025 GEO MAP (bulles par ville)
   ============================================================ */
function initBrbGeomap() {
  const container = document.getElementById('viz-geomap');
  if (!container || !DATA.brb2025) return;
  const entries = DATA.brb2025.entries.filter(e => e.lat != null && e.lng != null && e.montant_CHF > 0);

  // Aggregate by city
  const cityMap = d3.group(entries, e => e.ville);
  const cities = [];
  cityMap.forEach((list, ville) => {
    const total = d3.sum(list, e => e.montant_CHF);
    const cantonPrimary = list[0].canton;
    cities.push({
      ville,
      lat: list[0].lat,
      lng: list[0].lng,
      total,
      count: list.length,
      canton: cantonPrimary,
      entries: list.slice().sort((a, b) => b.montant_CHF - a.montant_CHF)
    });
  });

  const W = container.clientWidth || 800;
  const H = 600;

  // Suisse romande bounding box (approx)
  const lats = cities.map(c => c.lat), lngs = cities.map(c => c.lng);
  const latMin = Math.min(...lats) - 0.15, latMax = Math.max(...lats) + 0.15;
  const lngMin = Math.min(...lngs) - 0.2, lngMax = Math.max(...lngs) + 0.2;

  // Mercator projection
  const projection = d3.geoMercator()
    .center([(lngMin + lngMax) / 2, (latMin + latMax) / 2])
    .scale(8000)
    .translate([W / 2, H / 2]);

  // Adjust scale to fit
  const [topLeftX, topLeftY] = projection([lngMin, latMax]);
  const [botRightX, botRightY] = projection([lngMax, latMin]);
  const currentWidth = botRightX - topLeftX;
  const currentHeight = botRightY - topLeftY;
  const scaleFactor = Math.min(W / currentWidth, H / currentHeight) * 0.85;
  projection.scale(8000 * scaleFactor);
  const [newTopLeftX, newTopLeftY] = projection([lngMin, latMax]);
  const [newBotRightX, newBotRightY] = projection([lngMax, latMin]);
  projection.translate([
    W / 2 - ((newTopLeftX + newBotRightX) / 2 - W / 2),
    H / 2 - ((newTopLeftY + newBotRightY) / 2 - H / 2)
  ]);

  const svg = d3.select(container).append('svg')
    .attr('viewBox', `0 0 ${W} ${H}`)
    .attr('width', '100%').attr('height', H)
    .style('height', 'auto').style('background', '#fafaf7')
    .style('border-radius', '12px');

  // Radius scale by total
  const maxTotal = d3.max(cities, c => c.total);
  const r = d3.scaleSqrt().domain([1000, maxTotal]).range([3, 50]);

  const tooltip = d3.select(container).append('div').attr('class', 'brb-tooltip');

  // Add light background lake outline (Geneva approximated)
  // Simple: just draw circles for cities
  svg.selectAll('circle').data(cities.sort((a, b) => b.total - a.total)).join('circle')
    .attr('cx', d => projection([d.lng, d.lat])[0])
    .attr('cy', d => projection([d.lng, d.lat])[1])
    .attr('r', d => r(d.total))
    .attr('fill', d => brbCantonColor(d.canton) || '#888')
    .attr('fill-opacity', 0.45)
    .attr('stroke', d => brbCantonColor(d.canton) || '#888')
    .attr('stroke-width', 1.2)
    .style('cursor', 'pointer')
    .on('mouseenter', function(event, d) {
      d3.select(this).attr('fill-opacity', 0.8);
      const rect = container.getBoundingClientRect();
      const topList = d.entries.slice(0, 5).map(e =>
        `<div style="font-size:11px;margin-top:3px"><span style="opacity:.6">${e.secteur}</span> · ${e.nom.length > 45 ? e.nom.slice(0, 43) + '…' : e.nom} <strong>${brbFmtAmt(e.montant_CHF)} CHF</strong></div>`
      ).join('');
      tooltip.style('display', 'block')
        .style('left', (event.clientX - rect.left + 12) + 'px')
        .style('top', (event.clientY - rect.top + 12) + 'px')
        .html(`<strong>${d.ville}</strong> · ${BRB_CANTON_LABELS[d.canton]}<br><strong>${brbFmtAmt(d.total)} CHF</strong> · ${d.count} bénéficiaire${d.count > 1 ? 's' : ''}<hr style="margin:6px 0; border-color: rgba(0,0,0,.1)">${topList}${d.entries.length > 5 ? `<div style="font-size:10px;opacity:.5;margin-top:4px">+ ${d.entries.length - 5} autres</div>` : ''}`);
    })
    .on('mouseleave', function() {
      d3.select(this).attr('fill-opacity', 0.45);
      tooltip.style('display', 'none');
    });

  // Labels for top cities
  const topCities = cities.slice().sort((a, b) => b.total - a.total).slice(0, 12);
  svg.selectAll('.city-label').data(topCities).join('text')
    .attr('class', 'city-label')
    .attr('x', d => projection([d.lng, d.lat])[0])
    .attr('y', d => projection([d.lng, d.lat])[1] - r(d.total) - 5)
    .attr('text-anchor', 'middle')
    .style('font-size', '11px')
    .style('font-weight', '600')
    .style('fill', '#333')
    .style('pointer-events', 'none')
    .text(d => d.ville);

  // Legend
  const legend = svg.append('g').attr('transform', `translate(20, ${H - 80})`);
  legend.append('text').attr('y', -8).style('font-size', '11px').style('fill', '#666').style('font-weight', '600').text('Total reçu en 2025');
  const sampleSizes = [100000, 500000, 2000000];
  sampleSizes.forEach((s, i) => {
    legend.append('circle').attr('cx', i * 70 + 15).attr('cy', 20).attr('r', r(s))
      .attr('fill', '#888').attr('fill-opacity', 0.3).attr('stroke', '#666');
    legend.append('text').attr('x', i * 70 + 15).attr('y', 55).attr('text-anchor', 'middle')
      .style('font-size', '10px').style('fill', '#666').text(brbFmtAmt(s) + ' CHF');
  });

  // Canton legend top right
  const cantonLegend = svg.append('g').attr('transform', `translate(${W - 130}, 20)`);
  ['VD', 'FR', 'VS', 'NE', 'GE', 'JU'].forEach((c, i) => {
    const cg = cantonLegend.append('g').attr('transform', `translate(0, ${i * 18})`);
    cg.append('circle').attr('r', 6).attr('fill', brbCantonColor(c)).attr('fill-opacity', 0.5).attr('stroke', brbCantonColor(c));
    cg.append('text').attr('x', 14).attr('y', 4).style('font-size', '11px').style('fill', '#444').text(BRB_CANTON_LABELS[c]);
  });
}
