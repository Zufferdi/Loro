/* ============================================================
   initBrbSecondarySectors() — viz unifiée pour les 6 secteurs
   manquants : jeunesse, santé, environnement, patrimoine,
   formation, promotion.
   ------------------------------------------------------------
   Permet de voir les sous-domaines de chacun en un coup d'œil.
   Pattern visuel inspiré de social.js / culture.js / sports.js.
   ============================================================ */
(function() {
  // Les 6 secteurs avec leurs configurations
  const SECTORS_CFG = [
    {key: 'jeunesse',      label: 'Jeunesse et éducation',    color: '#a78bfa', file: 'jeunesse_classification'},
    {key: 'sante',         label: 'Santé et handicap',         color: '#fb7185', file: 'sante_classification'},
    {key: 'environnement', label: 'Environnement',             color: '#34d399', file: 'environnement_classification'},
    {key: 'patrimoine',    label: 'Conservation du patrimoine',color: '#fbbf24', file: 'patrimoine_classification'},
    {key: 'formation',     label: 'Formation et recherche',    color: '#60a5fa', file: 'formation_classification'},
    {key: 'promotion',     label: 'Promotion et tourisme',     color: '#f97316', file: 'promotion_classification'},
  ];

  function init() {
    const el = document.getElementById('viz-secteurs-secondaires');
    if (!el) return;
    if ('IntersectionObserver' in window) {
      const obs = new IntersectionObserver(entries => {
        entries.forEach(e => {
          if (e.isIntersecting) { render(e.target); obs.unobserve(e.target); }
        });
      }, {rootMargin: '200px'});
      obs.observe(el);
    } else { render(el); }
  }

  async function render(container) {
    if (container.dataset.loaded === '1') return;
    container.dataset.loaded = '1';
    container.innerHTML = '<div style="padding:32px;text-align:center;color:var(--ink-mute);font-style:italic">Chargement…</div>';

    try {
      // Charger les 6 fichiers en parallèle
      const promises = SECTORS_CFG.map(cfg =>
        fetch('data/' + cfg.file + '.json').then(r => r.json()).catch(() => null)
      );
      const datas = await Promise.all(promises);

      const wrap = document.createElement('div');
      wrap.className = 'secondary-sectors-wrap';
      wrap.style.cssText = 'display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:32px;';

      SECTORS_CFG.forEach((cfg, idx) => {
        const data = datas[idx];
        if (!data || !data.categories) return;

        const block = document.createElement('div');
        block.className = 'sector-block';
        block.style.cssText = 'background:rgba(255,255,255,0.02);border:1px solid var(--c-border);border-radius:8px;padding:20px;';

        // Total du secteur
        const totalCount = data.categories.reduce((s, c) => s + c.count, 0);
        const totalChf = data.categories.reduce((s, c) => s + c.total_chf, 0);

        // Titre
        const h = document.createElement('h4');
        h.style.cssText = 'margin:0 0 4px;display:flex;align-items:center;gap:8px;font-size:16px;';
        h.innerHTML = `
          <span style="width:12px;height:12px;border-radius:50%;background:${cfg.color};display:inline-block"></span>
          <span style="flex:1">${cfg.label}</span>
          <span style="font-size:13px;color:var(--ink-mute);font-weight:normal">${(totalChf/1e6).toFixed(1)} M · ${totalCount}×</span>
        `;
        block.appendChild(h);

        const sub = document.createElement('p');
        sub.style.cssText = 'margin:0 0 16px;font-size:12px;color:var(--ink-mute);';
        sub.textContent = `${data.categories.length} sous-domaines · 2025`;
        block.appendChild(sub);

        // Liste des catégories (max 6) avec barre proportionnelle
        const maxChf = Math.max(...data.categories.map(c => c.total_chf));
        data.categories.slice(0, 6).forEach(c => {
          const row = document.createElement('div');
          row.style.cssText = 'margin-bottom:8px;';

          const labelRow = document.createElement('div');
          labelRow.style.cssText = 'display:flex;justify-content:space-between;align-items:baseline;font-size:13px;margin-bottom:3px;';
          labelRow.innerHTML = `
            <span style="color:var(--ink)">${escapeHtml(c.name)}</span>
            <span style="color:var(--ink-mute);font-size:11px">${c.count}× · <strong>${(c.total_chf/1e6).toFixed(2)} M</strong></span>
          `;
          row.appendChild(labelRow);

          const barBg = document.createElement('div');
          barBg.style.cssText = 'background:rgba(255,255,255,0.06);height:6px;border-radius:3px;overflow:hidden;';
          const bar = document.createElement('div');
          bar.style.cssText = `height:100%;background:${cfg.color};width:${(c.total_chf/maxChf*100).toFixed(1)}%;border-radius:3px;`;
          barBg.appendChild(bar);
          row.appendChild(barBg);

          block.appendChild(row);
        });

        // Footer : top 3 bénéficiaires du secteur
        const topCat = data.categories[0];
        if (topCat && topCat.samples && topCat.samples.length) {
          const foot = document.createElement('details');
          foot.style.cssText = 'margin-top:12px;padding-top:12px;border-top:1px solid var(--c-border);font-size:12px;';
          const summary = document.createElement('summary');
          summary.style.cssText = 'cursor:pointer;color:var(--ink-mute);';
          summary.textContent = `Top bénéficiaires « ${topCat.name} » →`;
          foot.appendChild(summary);
          const list = document.createElement('div');
          list.style.cssText = 'margin-top:8px;line-height:1.6;';
          topCat.samples.slice(0, 5).forEach(s => {
            const line = document.createElement('div');
            line.innerHTML = `<span style="color:var(--ink-mute)">${escapeHtml(s.canton || '?')}</span> · ${escapeHtml(s.nom.slice(0, 50))} <span style="float:right;color:var(--ink-mute)">${(s.montant_CHF/1e3).toFixed(0)} k</span>`;
            list.appendChild(line);
          });
          foot.appendChild(list);
          block.appendChild(foot);
        }

        wrap.appendChild(block);
      });

      container.innerHTML = '';
      container.appendChild(wrap);
    } catch (e) {
      container.innerHTML = `<div style="padding:32px;text-align:center;color:var(--ink-mute);font-style:italic">Erreur de chargement : ${e.message}</div>`;
    }
  }

  function escapeHtml(s) {
    return String(s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
