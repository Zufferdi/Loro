/* utils.js — helpers partagés entre toutes les visualisations */

const CHF = new Intl.NumberFormat('fr-CH', { maximumFractionDigits: 0 });
const CHF1 = new Intl.NumberFormat('fr-CH', { maximumFractionDigits: 1 });
const PCT = new Intl.NumberFormat('fr-CH', { style: 'percent', maximumFractionDigits: 1 });

function fmtCHF(v)  { return CHF.format(v) + ' CHF'; }
function fmtM(v)    { return CHF1.format(v) + ' M CHF'; }
function fmtPct(v)  { return PCT.format(v); }
function fmtNum(v)  { return CHF.format(v); }

/** Format compact 1234567 → 1,2 M */
function fmtCompact(v) {
  if (v == null || isNaN(v)) return '—';
  const abs = Math.abs(v);
  if (abs >= 1e9) return CHF1.format(v / 1e9) + ' Mrd';
  if (abs >= 1e6) return CHF1.format(v / 1e6) + ' M';
  if (abs >= 1e3) return CHF1.format(v / 1e3) + ' k';
  return CHF.format(v);
}

/** Couleurs cantons */
const CANTON_COLORS = {
  VD: '#e44d4d', FR: '#5b8def', VS: '#f0a93d',
  NE: '#7c5bc7', GE: '#2ea08a', JU: '#c97b3a',
};
const CANTON_NAMES = {
  VD: 'Vaud', FR: 'Fribourg', VS: 'Valais',
  NE: 'Neuchâtel', GE: 'Genève', JU: 'Jura',
};
const CANTONS_ORDER = ['VD', 'GE', 'VS', 'FR', 'NE', 'JU'];

/** Couleurs secteurs (palette éditoriale) */
const SECTOR_COLORS = {
  'Culture':                              '#c8102e',
  'Action sociale et personnes âgées':    '#5b8def',
  'Sport':                                '#f0a93d',
  'Jeunesse et éducation':                '#7c5bc7',
  'Conservation du patrimoine':           '#c97b3a',
  'Promotion, tourisme et développement': '#2ea08a',
  'Santé et handicap':                    '#e44d4d',
  'Formation et recherche':               '#8a8a8a',
  'Environnement':                        '#5fa052',
};
const SECTOR_SHORT = {
  'Culture': 'Culture',
  'Action sociale et personnes âgées': 'Action sociale',
  'Sport': 'Sport',
  'Jeunesse et éducation': 'Jeunesse',
  'Conservation du patrimoine': 'Patrimoine',
  'Promotion, tourisme et développement': 'Promotion',
  'Santé et handicap': 'Santé',
  'Formation et recherche': 'Formation',
  'Environnement': 'Environnement',
};

/** Couleurs types de jeu */
const GAME_COLORS = {
  'Billets Instantanés':  '#c8102e',
  'Jeux de tirages':      '#5b8def',
  'Paris sportifs':       '#f0a93d',
  'Loterie électronique': '#7c5bc7',
  'PMUR':                 '#2ea08a',
};

/** Tooltip global */
let tipEl = null;
function ensureTip() {
  if (!tipEl) {
    tipEl = document.createElement('div');
    tipEl.className = 'tooltip';
    document.body.appendChild(tipEl);
  }
  return tipEl;
}
function showTip(html, x, y) {
  const el = ensureTip();
  el.innerHTML = html;
  el.classList.add('show');
  // position au-dessus à droite du curseur, avec un offset
  const w = el.offsetWidth, h = el.offsetHeight;
  let px = x + 14, py = y - h - 14;
  if (px + w > window.innerWidth - 8)  px = x - w - 14;
  if (py < 8) py = y + 18;
  el.style.left = px + 'px';
  el.style.top  = py + 'px';
}
function hideTip() { if (tipEl) tipEl.classList.remove('show'); }

/** Charge un fichier JSON depuis data/ */
async function loadJSON(name) {
  const r = await fetch(`data/${name}`);
  if (!r.ok) throw new Error(`Impossible de charger ${name} (${r.status})`);
  return r.json();
}

/** Détection mode sombre (pour les couleurs canvas/D3) */
function isDark() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}
function inkColor()      { return isDark() ? '#f1efe7' : '#1a1917'; }
function inkSoftColor()  { return isDark() ? '#b6b2a4' : '#5c5a52'; }
function inkMuteColor()  { return isDark() ? '#7f7c70' : '#908d82'; }
function ruleColor()     { return isDark() ? '#322f27' : '#e0ddd2'; }

/** Animation compteur : 0 → cible sur 1.4 s */
function animateCounter(el, target, formatter = fmtNum, duration = 1400) {
  const start = performance.now();
  function tick(now) {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3); // ease-out cubic
    el.textContent = formatter(target * eased);
    if (t < 1) requestAnimationFrame(tick);
    else el.textContent = formatter(target);
  }
  requestAnimationFrame(tick);
}

/** Debounce */
function debounce(fn, ms = 200) {
  let h;
  return (...args) => { clearTimeout(h); h = setTimeout(() => fn(...args), ms); };
}

/** Charge le TopoJSON des cantons suisses depuis le CDN swiss-maps@4
 *  Retourne {cantons, lakes} ou null en cas d'échec réseau. */
async function loadSwissTopo() {
  try {
    const r = await fetch('https://unpkg.com/swiss-maps@4/2021/ch-combined.json');
    if (!r.ok) return null;
    return await r.json();
  } catch (e) {
    console.warn('Topojson swiss-maps indisponible :', e);
    return null;
  }
}

/** Map des codes canton vers id BFS (utilisé dans le topojson) */
const CANTON_BFS = {
  VD: 22, FR: 10, VS: 23, NE: 24, GE: 25, JU: 26,
};
const CANTON_BFS_REVERSE = Object.fromEntries(
  Object.entries(CANTON_BFS).map(([k, v]) => [v, k])
);
