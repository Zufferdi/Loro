/* ============================================================
   embed.js — helpers communs aux pages embed
   ============================================================
   - postMessage pour iframe-resizer (le parent peut auto-ajuster
     la hauteur de l'iframe à son contenu)
   - opt-in : si le parent écoute 'loro:embed:resize', il reçoit
     un objet { type:'loro:embed:resize', height: N } à chaque
     resize du contenu
   - également : un mode "compact" si la query string contient
     ?compact=1 (cache encore plus la chrome)
   ============================================================ */
(function () {
  'use strict';

  // 1. Compact mode via query string
  const params = new URLSearchParams(window.location.search);
  if (params.get('compact') === '1') {
    document.documentElement.classList.add('embed-compact');
  }
  if (params.get('theme') === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
  } else if (params.get('theme') === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
  }

  // 2. PostMessage hauteur sur resize / mutation
  function postHeight() {
    const h = Math.max(
      document.body.scrollHeight,
      document.documentElement.scrollHeight
    );
    try {
      window.parent.postMessage({ type: 'loro:embed:resize', height: h }, '*');
    } catch (e) {
      // Cross-origin restrict, on n'a pas accès au parent — silent
    }
  }

  // Debounce simple
  let pending = false;
  function scheduleHeight() {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => {
      pending = false;
      postHeight();
    });
  }

  // Sur load + sur resize + sur changement DOM
  window.addEventListener('load', scheduleHeight);
  window.addEventListener('resize', scheduleHeight);

  // Observer les changements DOM (les viz lazy-loadent leur contenu)
  if ('MutationObserver' in window) {
    const obs = new MutationObserver(scheduleHeight);
    if (document.body) {
      obs.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: false,
        characterData: false,
      });
    }
  }

  // Premier post après un délai (laisse le temps aux fonts de charger)
  setTimeout(scheduleHeight, 500);
  setTimeout(scheduleHeight, 1500);
})();
