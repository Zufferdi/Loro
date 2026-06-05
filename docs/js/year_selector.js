// ============= Year toggle helpers (global) =============
// Extracted to a standalone file so it's available to all viz modules
// (aggregations.js, culture.js, sports.js, social.js, sectors.js, ...)

(function () {
  'use strict';

  // Available years (left-to-right in the UI). To add a year, just add it here
  // and ensure the corresponding _YYYY.json files exist in data/.
  const YEARS = ['2021', '2022', '2023', '2024', '2025'];

  function addYearSelector(container, currentYear, renderFn) {
    const sel = document.createElement('div');
    sel.className = 'year-selector';
    sel.style.cssText = 'display:flex;gap:8px;margin-bottom:14px;justify-content:flex-end';
    YEARS.forEach(function (y) {
      const btn = document.createElement('button');
      btn.textContent = y;
      btn.dataset.year = y;
      const active = y === currentYear;
      btn.style.cssText = 'background:' + (active ? 'var(--ink)' : 'transparent') +
        ';border:1px solid ' + (active ? 'var(--ink)' : 'var(--rule)') +
        ';padding:4px 12px;border-radius:14px;cursor:pointer;font-size:13px;' +
        'color:' + (active ? 'white' : 'var(--ink-mute)') + ';font-family:inherit';
      btn.addEventListener('click', function () {
        if (y === currentYear) return;
        container.dataset.loaded = '0';
        renderFn(container, y);
      });
      sel.appendChild(btn);
    });
    container.appendChild(sel);
  }

  // Build the JSON file suffix from a year (2025 → '', others → '_YYYY')
  // Matches the naming convention used in docs/data/ (latest year has no suffix).
  function yearSuffix(year) {
    return year === '2025' ? '' : '_' + year;
  }

  // Expose globally
  window.YEARS = YEARS;
  window.addYearSelector = addYearSelector;
  window.yearSuffix = yearSuffix;
  window.YEAR_TOTALS = {
    '2021': 203982260,  // brb2021_full.json (post-cleanup v1)
    '2022': 181331404,  // brb2022_full.json (post-nettoyage qualité approfondi)
    '2023': 202405156,  // brb2023_full.json (post-nettoyage qualité approfondi)
    '2024': 197467672,  // brb2024_full.json (post-nettoyage qualité approfondi)
    '2025': 206439481,  // brb2025_full.json (post-nettoyage qualité approfondi)
  };
})();

