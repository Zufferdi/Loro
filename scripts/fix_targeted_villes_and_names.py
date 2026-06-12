#!/usr/bin/env python3
"""
fix_targeted_villes_and_names.py
==================================

Targeted fixes after manual investigation:

1. **`ville='Chablais'`**: Chablais is a REGION (VD-VS-France), not a city.
   Replace with null. (The benefits actually went to organizations in Aigle,
   Bex, Villeneuve, Monthey, etc., but the PDF labels them "Chablais".)

2. **`ville='Centre'`**: This is a parser artifact — entries like
   "Centre Sportif Vallée de Joux, Centre" were truncated at the wrong place.
   Replace with null.

3. **Specific truncated names**:
   - "Fond. pour la conservation" 3.3M GE 2025 → "Fond. pour la conservation
     des temples genevois construits avant 1907"
   - "Centre dramatique fribourgeois -" → "Centre dramatique fribourgeois"
   - "Centre Social Protestant - CSP, Centre" → "Centre Social Protestant - CSP"
   - Etc.
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'
YEARS = ['2022', '2023', '2024', '2025']

# Villes that are actually REGIONS or artifacts — to null out
REGION_OR_ARTIFACT_VILLES = {
    'chablais',         # Region (VD-VS-France)
    'centre',           # Parser artifact
    'broye',            # Region
    'gros-de-vaud',     # Region
    'gros de vaud',
    'glâne',            # Region
    'sarine',           # District not city
    'singine',          # District
    'lac',              # Region
    'see',              # Region
    'jura sud lémanique',
    'pays-d\'enhaut', 'pays d\'enhaut',
    'pays-d\'en-haut',
}

# Hard-coded name fixes (matched by exact name + amount + year for precision)
NAME_FIXES = {
    ('2025', 'Fond. pour la conservation', 3300000):
        'Fond. pour la conservation des temples genevois construits avant 1907',
    ('2024', 'Centre dramatique fribourgeois -', 501250):
        'Centre dramatique fribourgeois',
    ('2024', 'Centre Social Protestant - CSP, Centre', 600000):
        'Centre Social Protestant - CSP',
    ('2024', 'Centre Social Protestant - CSP, Centre', 48000):
        'Centre Social Protestant - CSP',
    ('2024', 'Fond. de la Cité universitaire de Genève Maison d\'Albert - Démolition', 4000000):
        "Fond. de la Cité universitaire de Genève — Maison d'Albert",
    # Some other long-name fixes
    ('2024', 'Établissements hospitaliers du Nord vaudois (eHnv), Pôle santé Pays d’En-haut (PSPE), Hôpital Riviera Chablais (HRC), Hôpital intercantonal de la Broye (HIB)', 6323000):
        "Établissements hospitaliers du Nord vaudois (eHnv) + Pôle santé Pays d'En-haut (PSPE) + Hôpital Riviera Chablais (HRC) + Hôpital intercantonal de la Broye (HIB)",
}


def main():
    summary = []
    for y in YEARS:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p, encoding='utf-8'))
        n_villes = 0
        n_names = 0
        for e in d['entries']:
            # Fix region/artifact villes
            v = e.get('ville')
            if v and v.lower().strip() in REGION_OR_ARTIFACT_VILLES:
                e['ville'] = None
                n_villes += 1
            # Fix specific names
            key = (y, e['nom'], e['montant_CHF'])
            if key in NAME_FIXES:
                e['nom'] = NAME_FIXES[key]
                n_names += 1
        d['_meta']['targeted_fixes'] = {
            'date': '2026-06-04',
            'region_artifact_villes_nulled': n_villes,
            'specific_names_fixed': n_names,
        }
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"  ─── BRB {y} ───")
        print(f"  Villes 'région/artefact' nullifiées: {n_villes}")
        print(f"  Noms tronqués spécifiques fixés:     {n_names}")
        summary.append((y, n_villes, n_names))

    print(f"\n  Total: {sum(s[1] for s in summary)} villes + {sum(s[2] for s in summary)} noms")


if __name__ == '__main__':
    main()
