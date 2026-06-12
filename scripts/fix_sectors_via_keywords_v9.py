#!/usr/bin/env python3
"""fix_sectors_via_keywords_v9.py — Culture mal classés ailleurs."""
import json, re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'

RULES = [
    # → CULTURE
    (r"\bCentre\s+Culturel\s+Neuchâtelois\b|\bCCN\b", 'Culture'),
    (r"\bEnsemble\s+Symphonique\s+Neuchâtel\b|\bESN\b", 'Culture'),
    (r"\bClub\s+44\b", 'Culture'),  # institution culturelle Chaux-de-Fonds
    (r"\bConservatoire\s+(?:cantonal\s+)?de\s+musique\b", 'Formation et recherche'),
]


def find_override(entry):
    text = (entry.get('nom') or '') + ' ' + (entry.get('description') or '')
    for pattern, sector in RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return sector
    return None


total = 0
for y in ['2021', '2022', '2023', '2024', '2025']:
    p = DATA / f'brb{y}_full.json'
    d = json.load(open(p, encoding='utf-8'))
    n = 0
    for e in d['entries']:
        t = find_override(e)
        if t and t != e['secteur']:
            e['secteur'] = t
            n += 1
    d['_meta']['sector_overrides_v9'] = {'count': n, 'date': '2026-06-04'}
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2, encoding='utf-8'))
    print(f"brb{y}: {n} overrides v9")
    total += n
print(f"Total: {total}")
