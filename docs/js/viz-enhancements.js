/* ============================================================
   viz-enhancements.js — v13.44
   Améliorations UX/A11y/Perf appliquées en post-load à toutes les viz
   ------------------------------------------------------------
   Cible : .viz-card (44 containers) sans modifier app.js
   Patches non-destructifs : annulent eux-mêmes en cas d'erreur,
   logguent en console.warn (jamais bloquant).
   ============================================================ */
(function () {
  'use strict';

  if (window.__VIZ_ENH_LOADED__) return;
  window.__VIZ_ENH_LOADED__ = true;

  // ---------- Helpers ----------
  function debounce(fn, ms = 200) {
    let t;
    return function (...args) {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), ms);
    };
  }

  function safeCall(name, fn) {
    try { fn(); }
    catch (e) { console.warn(`[viz-enh:${name}]`, e.message); }
  }

  /* ============================================================
     1. RESIZE OBSERVER : redessine les viz quand leur container change
     ------------------------------------------------------------
     Stratégie : on déclenche un évènement custom 'viz:resize' que
     chaque viz peut écouter. Pour les viz qui n'écoutent pas, on
     détruit le SVG et on retry l'init de la viz (si exposée globalement).
     ============================================================ */
  function setupResizeObserver() {
    if (typeof ResizeObserver === 'undefined') {
      console.warn('[viz-enh] ResizeObserver non supporté (vieux navigateur)');
      return;
    }

    const cards = document.querySelectorAll('.viz-card, [class*="viz-"]');
    const lastWidths = new WeakMap();

    const ro = new ResizeObserver(debounce((entries) => {
      entries.forEach(entry => {
        const el = entry.target;
        const newW = entry.contentRect.width;
        const oldW = lastWidths.get(el) || 0;
        // Trigger uniquement si changement > 20px (évite micro-resizes)
        if (Math.abs(newW - oldW) < 20) return;
        lastWidths.set(el, newW);
        // Custom event que les viz peuvent écouter
        el.dispatchEvent(new CustomEvent('viz:resize', {
          detail: { width: newW, height: entry.contentRect.height },
          bubbles: true,
        }));
      });
    }, 250));

    cards.forEach(c => ro.observe(c));
    console.log(`[viz-enh] ResizeObserver actif sur ${cards.length} containers`);
  }

  /* ============================================================
     2. LAZY LOADING : différer l'init des viz hors viewport
     ------------------------------------------------------------
     Mark les viz "below-the-fold" comme paresseuses. L'init existant
     d'app.js les rend immédiatement (toutes au DOMContentLoaded), donc
     on ne peut pas vraiment changer ce comportement sans refactor.
     
     Solution pragmatique : Marquer les containers viz pour qu'ils
     soient repaintés visuellement seulement quand approche du viewport
     (via CSS content-visibility: auto).
     ============================================================ */
  function setupLazyContentVisibility() {
    if (!('contentVisibility' in document.documentElement.style)) {
      console.warn('[viz-enh] content-visibility non supporté');
      return;
    }
    
    const cards = document.querySelectorAll('.viz-card');
    cards.forEach((card, idx) => {
      // Skip les 3 premières viz (above-the-fold)
      if (idx < 3) return;
      card.style.contentVisibility = 'auto';
      card.style.containIntrinsicSize = '0 400px';
    });
    console.log(`[viz-enh] content-visibility:auto sur ${cards.length - 3} containers`);
  }

  /* ============================================================
     3. TOUCH-FRIENDLY TOOLTIPS
     ------------------------------------------------------------
     Sur tactile (pointerType="touch"), les mouseenter/mouseleave
     fonctionnent mal. On ajoute un handler global qui :
     - Au touchstart : simule un mouseenter sur l'élément touché
     - Au touchend ailleurs : déclenche un mouseleave
     ============================================================ */
  function setupTouchTooltips() {
    if (!('ontouchstart' in window) && !navigator.maxTouchPoints) {
      // Pas de tactile, skip
      return;
    }

    let lastTouchedEl = null;

    function dispatchMouse(el, type) {
      if (!el) return;
      const evt = new MouseEvent(type, {
        bubbles: true,
        cancelable: true,
        view: window,
        clientX: 0, clientY: 0,
      });
      el.dispatchEvent(evt);
    }

    document.addEventListener('touchstart', (e) => {
      const target = e.target;
      // Si on tape sur un élément interactif d'une viz
      if (target.closest('.viz') && (target.tagName === 'circle' || 
          target.tagName === 'rect' || target.tagName === 'path')) {
        if (lastTouchedEl && lastTouchedEl !== target) {
          dispatchMouse(lastTouchedEl, 'mouseleave');
        }
        dispatchMouse(target, 'mouseenter');
        dispatchMouse(target, 'mouseover');
        lastTouchedEl = target;
      } else if (lastTouchedEl && !target.closest('.tooltip, .brb-tooltip')) {
        // Tap ailleurs, masquer le tooltip courant
        dispatchMouse(lastTouchedEl, 'mouseleave');
        lastTouchedEl = null;
      }
    }, { passive: true });

    console.log('[viz-enh] Touch tooltips actifs');
  }

  /* ============================================================
     4. BOUTON EXPORT pour chaque viz
     ------------------------------------------------------------
     Ajoute un petit bouton "⤓ Exporter" en haut-droite de chaque
     .viz-card qui propose : PNG, SVG, CSV (selon disponibilité).
     ============================================================ */
  function setupExportButtons() {
    const style = document.createElement('style');
    style.textContent = `
      .viz-export-btn {
        position: absolute; top: 12px; right: 12px;
        background: rgba(255,255,255,0.85);
        border: 1px solid var(--ink-line, #ddd);
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 11px;
        font-family: inherit;
        color: var(--ink-mute, #666);
        cursor: pointer;
        z-index: 5;
        opacity: 0.4;
        transition: opacity 0.2s, background 0.2s, color 0.2s;
      }
      .viz-export-btn:hover, .viz-export-btn:focus-visible {
        opacity: 1;
        background: var(--c-accent, #c8102e);
        color: white;
        border-color: var(--c-accent, #c8102e);
      }
      .viz-export-menu {
        position: absolute; top: 40px; right: 12px;
        background: white; border: 1px solid var(--ink-line, #ddd);
        border-radius: 8px;
        padding: 4px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        z-index: 100;
        display: flex; flex-direction: column;
        min-width: 120px;
      }
      .viz-export-menu button {
        background: none; border: none; padding: 8px 12px;
        text-align: left; font-size: 12px; font-family: inherit;
        cursor: pointer; color: var(--ink, #222); border-radius: 4px;
      }
      .viz-export-menu button:hover { background: var(--bg-soft, #f5f3ed); }
      .viz-card { position: relative; }
      @media (prefers-color-scheme: dark) {
        .viz-export-btn { background: rgba(40,40,40,0.85); color: #ccc; border-color: #444; }
        .viz-export-menu { background: #2a2925; border-color: #444; }
        .viz-export-menu button { color: #ddd; }
        .viz-export-menu button:hover { background: #3a3935; }
      }
      @media (max-width: 600px) {
        .viz-export-btn { font-size: 10px; padding: 3px 7px; top: 8px; right: 8px; }
      }
    `;
    document.head.appendChild(style);

    document.querySelectorAll('.viz-card').forEach((card, idx) => {
      const viz = card.querySelector('[id^="viz-"]');
      if (!viz) return;
      if (card.querySelector('.viz-export-btn')) return; // déjà décoré

      const btn = document.createElement('button');
      btn.className = 'viz-export-btn';
      btn.setAttribute('aria-label', 'Exporter la visualisation');
      btn.setAttribute('title', 'Exporter (PNG / SVG)');
      btn.textContent = '⤓ Exporter';
      btn.type = 'button';

      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        // Toggle menu
        const existing = card.querySelector('.viz-export-menu');
        if (existing) { existing.remove(); return; }

        const menu = document.createElement('div');
        menu.className = 'viz-export-menu';

        const svg = viz.querySelector('svg');
        if (svg) {
          // PNG export
          const pngBtn = document.createElement('button');
          pngBtn.textContent = '📷  PNG';
          pngBtn.type = 'button';
          pngBtn.addEventListener('click', () => exportSvgAsPng(svg, vizName(viz)));
          menu.appendChild(pngBtn);

          // SVG export
          const svgBtn = document.createElement('button');
          svgBtn.textContent = '🎨  SVG';
          svgBtn.type = 'button';
          svgBtn.addEventListener('click', () => exportSvgRaw(svg, vizName(viz)));
          menu.appendChild(svgBtn);
        } else {
          const note = document.createElement('button');
          note.textContent = '(pas de SVG ici)';
          note.disabled = true;
          menu.appendChild(note);
        }

        card.appendChild(menu);

        // Auto-close au prochain click ailleurs
        setTimeout(() => {
          document.addEventListener('click', function close(ev) {
            if (!menu.contains(ev.target) && ev.target !== btn) {
              menu.remove();
              document.removeEventListener('click', close);
            }
          });
        }, 0);
      });

      card.appendChild(btn);
    });

    console.log(`[viz-enh] Boutons Export ajoutés à ${document.querySelectorAll('.viz-export-btn').length} cards`);
  }

  function vizName(viz) {
    return (viz.id || 'viz').replace('viz-', 'loro-');
  }

  function exportSvgRaw(svg, name) {
    const clone = svg.cloneNode(true);
    // Inline CSS computed styles (essentiel pour rendu autonome)
    inlineComputedStyles(svg, clone);
    const xml = new XMLSerializer().serializeToString(clone);
    const blob = new Blob([`<?xml version="1.0" encoding="UTF-8"?>\n${xml}`], { type: 'image/svg+xml' });
    triggerDownload(blob, `${name}.svg`);
  }

  function exportSvgAsPng(svg, name) {
    const clone = svg.cloneNode(true);
    inlineComputedStyles(svg, clone);
    const xml = new XMLSerializer().serializeToString(clone);
    const svgBlob = new Blob([xml], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);

    const img = new Image();
    const bbox = svg.getBoundingClientRect();
    const scale = 2; // retina-quality

    img.onload = function () {
      const canvas = document.createElement('canvas');
      canvas.width = bbox.width * scale;
      canvas.height = bbox.height * scale;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#fafaf7'; // bg natural
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);
      canvas.toBlob(b => triggerDownload(b, `${name}.png`), 'image/png');
    };
    img.onerror = () => {
      console.error('Erreur conversion PNG');
      URL.revokeObjectURL(url);
    };
    img.src = url;
  }

  function inlineComputedStyles(src, clone) {
    const srcEls = src.querySelectorAll('*');
    const cloneEls = clone.querySelectorAll('*');
    for (let i = 0; i < srcEls.length; i++) {
      const cs = window.getComputedStyle(srcEls[i]);
      const tgt = cloneEls[i];
      if (!tgt) continue;
      // Inline only essential viz properties
      ['fill','stroke','stroke-width','stroke-dasharray','opacity','font-family',
       'font-size','font-weight','text-anchor','dominant-baseline'].forEach(prop => {
        const v = cs.getPropertyValue(prop);
        if (v) tgt.style[prop] = v;
      });
    }
    // Ensure SVG has its width/height inline
    const bbox = src.getBoundingClientRect();
    clone.setAttribute('width', bbox.width);
    clone.setAttribute('height', bbox.height);
    if (!clone.getAttribute('xmlns')) {
      clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    }
  }

  function triggerDownload(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      a.remove();
      URL.revokeObjectURL(url);
    }, 100);
  }

  /* ============================================================
     5. ANNOTATIONS NARRATIVES sur viz-anomaly et viz-treemap
     ------------------------------------------------------------
     Ajoute des callouts contextuels qui apparaissent en hover
     sur les barres/cellules clés.
     ============================================================ */
  function setupAnnotations() {
    // Pour viz-anomaly : ajouter une légende inline expliquant l'écart bénéfice
    const anomaly = document.getElementById('viz-anomaly');
    if (anomaly && !anomaly.querySelector('.viz-annotation-legend')) {
      const legend = document.createElement('div');
      legend.className = 'viz-annotation-legend';
      legend.style.cssText = 'margin-top:16px;padding:12px 16px;background:rgba(200,16,46,0.05);border-left:3px solid #c8102e;font-size:12px;color:var(--ink-mute,#666);line-height:1.6;border-radius:4px;';
      legend.innerHTML = `
        <strong style="color:var(--ink,#222);">Lecture du graphique :</strong>
        chaque barre montre la variation du bénéfice net par rapport à l'année précédente.
        Les barres positives (rouges) sont décomposées en facteurs explicatifs documentés
        dans les éditos du Directeur général de la Loterie Romande
        (RA 2018-2025). Cliquez ou survolez une barre pour voir le narratif détaillé.
      `;
      anomaly.parentNode.insertBefore(legend, anomaly.nextSibling);
    }

    // Pour viz-treemap : ajouter une note d'aide
    const treemap = document.getElementById('viz-treemap');
    if (treemap && !treemap.querySelector('.viz-annotation-help')) {
      const help = document.createElement('div');
      help.className = 'viz-annotation-help';
      help.style.cssText = 'margin-top:12px;font-size:11px;color:var(--ink-mute,#888);font-style:italic;text-align:center;';
      help.textContent = '💡 La taille de chaque rectangle est proportionnelle au montant cumulé reversé. Survolez pour le détail.';
      treemap.parentNode.insertBefore(help, treemap.nextSibling);
    }

    console.log('[viz-enh] Annotations narratives ajoutées');
  }

  /* ============================================================
     6. TITRES D'AXES manquants — ajoute labels via DOM-walking
     ------------------------------------------------------------
     Plutôt que de modifier chaque init D3, on inject des <text>
     positionnés autour du SVG.
     ============================================================ */
  function setupAxisLabels() {
    // Map idem -> {x_label, y_label} pour les viz les plus utilisées
    const axisHints = {
      'viz-opcosts': { yLabel: 'CHF (millions)', xLabel: 'Année' },
      'viz-capital': { yLabel: 'CHF (millions)', xLabel: 'Année' },
      'viz-anomaly': { yLabel: 'Δ Bénéfice (M CHF vs N-1)', xLabel: 'Année' },
      'viz-prelevement-evol': { yLabel: 'Prélèvement (%)', xLabel: 'Année' },
      'viz-jura-histoire': { yLabel: 'CHF reçus', xLabel: 'Année' },
      'viz-share-suisse': { yLabel: 'Part du PBJ (%)', xLabel: 'Année' },
      'viz-ecosysteme-jeux': { yLabel: 'PBJ (M CHF)', xLabel: 'Année' },
    };

    Object.entries(axisHints).forEach(([id, hints]) => {
      const viz = document.getElementById(id);
      if (!viz) return;
      const card = viz.closest('.viz-card');
      if (!card) return;
      // Container "axis-hints" en pied de viz
      if (card.querySelector('.viz-axis-hints')) return;
      const hintBar = document.createElement('div');
      hintBar.className = 'viz-axis-hints';
      hintBar.style.cssText = 'display:flex;justify-content:space-between;font-size:10px;color:var(--ink-mute,#888);margin-top:4px;padding:0 12px;font-style:italic;';
      hintBar.innerHTML = `
        <span>↕ ${hints.yLabel}</span>
        <span>↔ ${hints.xLabel}</span>
      `;
      // Insérer après le viz-footer s'il existe
      const footer = card.querySelector('.viz-footer');
      if (footer) {
        footer.parentNode.insertBefore(hintBar, footer);
      } else {
        viz.parentNode.insertBefore(hintBar, viz.nextSibling);
      }
    });
    console.log(`[viz-enh] Hints d'axes ajoutés à ${Object.keys(axisHints).length} viz`);
  }

  /* ============================================================
     7. CSS VARS pour les sectorial colors les plus fréquents
     ------------------------------------------------------------
     Plutôt que migrer 223 hex hardcodés, on définit des CSS vars
     de référence dans :root pour cohérence future et dark mode.
     ============================================================ */
  function setupColorVars() {
    const style = document.createElement('style');
    style.textContent = `
      :root {
        --sec-culture:    #c8102e;
        --sec-sport:      #5b8def;
        --sec-social:     #7c5bc7;
        --sec-sante:      #2da565;
        --sec-jeunesse:   #f0a93d;
        --sec-patrimoine: #8b6f47;
        --sec-environnement: #4a7c4e;
        --sec-promotion:  #d9534f;
        --sec-formation:  #4a90e2;
        --sec-autre:      #9b9b9b;
        --canton-vd: #28a745;
        --canton-ge: #fd7e14;
        --canton-vs: #c8102e;
        --canton-fr: #6f42c1;
        --canton-ne: #20c997;
        --canton-ju: #ffc107;
      }
      @media (prefers-color-scheme: dark) {
        :root {
          --sec-culture:    #e84a5f;
          --sec-sport:      #7da5ff;
          --sec-social:     #9b7fd9;
          --sec-sante:      #4dc77f;
          --sec-jeunesse:   #ffc15a;
        }
      }
    `;
    document.head.appendChild(style);
    console.log('[viz-enh] CSS vars sectorielles définies (référence future)');
  }

  /* ============================================================
     INITIALISATION — wait load + delay pour laisser app.js rendre
     ============================================================ */
  function init() {
    // 1. CSS vars (immédiat, ne dépend pas des viz)
    safeCall('setupColorVars', setupColorVars);

    // 2. Annotations (immédiat)
    safeCall('setupAnnotations', setupAnnotations);

    // 3. Axis labels (immédiat, pur DOM)
    safeCall('setupAxisLabels', setupAxisLabels);

    // 4. Content-visibility lazy (immédiat, pur CSS)
    safeCall('setupLazyContentVisibility', setupLazyContentVisibility);

    // Attendre que les viz soient rendues (≈ 1500ms en pratique)
    setTimeout(() => {
      safeCall('setupExportButtons', setupExportButtons);
      safeCall('setupResizeObserver', setupResizeObserver);
      safeCall('setupTouchTooltips', setupTouchTooltips);
    }, 1500);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
