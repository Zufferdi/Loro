#!/usr/bin/env python3
"""fix_sectors_via_keywords_v11.py — corrections audit Passe 4."""
import json, re
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'

RULES = [
    # ─── Culture mal classés en Jeunesse/Environnement/Sante ───
    (r"\bEva\s+Prod\b|\bLuxor\s+Factory\b", 'Culture'),
    (r"\bRock\s+Altitude\s+Festival\b|\bCorbak\s+Festival\b", 'Culture'),
    (r"\bCirco\s+Bello\b", 'Culture'),
    (r"\bCafé-théâtre\s+La\s+Grange\b", 'Culture'),
    (r"\bAssoc\.\s+CO2\b|\bCO2\s+Fribourg\b", 'Environnement'),
    (r"\bEspace\s+Culturel\s+Le\s+Nouveau\s+Monde\b", 'Culture'),
    (r"\bMagnifique\s+Théâtre\b", 'Culture'),
    (r"\bBDFIL\b|\bbande\s+dessinée\b", 'Culture'),
    (r"\bMaison\s+Visinand\b", 'Culture'),
    (r"\bSeptembre\s+Musical\b|\bMontreux-Vevey\b", 'Culture'),
    (r"\bFond\.\s+Jean\s+Monnet\b", 'Culture'),  # culture/idée européenne
    (r"\bAssoc\.\s+scène\s+active\b", 'Culture'),
    
    # ─── Environnement (apiculture, alpage)
    (r"\bSté\s+d['\u2019]?apiculture\b", 'Environnement'),
    (r"\bAlpage\s+de\s+Serin\b", 'Environnement'),
    
    # ─── Promotion (rurale interjurassienne = terroir)
    (r"\bFond\.\s+rurale\s+interjurassienne\b", 'Promotion, tourisme et développement'),
    (r"\bVitrocentre\s+Romont\b", 'Formation et recherche'),  # recherche vitrail
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
    d['_meta']['sector_overrides_v11'] = {'count': n, 'date': '2026-06-04'}
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2, encoding='utf-8'))
    print(f"brb{y}: {n} overrides v11")
    total += n
print(f"Total: {total}")
