#!/usr/bin/env python3
"""fix_sectors_via_keywords_v6.py — derniers cas évidents."""
import json, re
from pathlib import Path
DATA = Path('/home/claude/audit3/Loro-main/docs/data')

RULES = [
    # → CULTURE (entries Culture mal classées en Santé/Patrimoine/Jeunesse/...)
    (r"\bLe\s+Temple\s+du\s+Polar\b", 'Culture'),
    (r"\bBelluard\s+Bollwerk\b", 'Culture'),
    (r"\bVisions\s+du\s+Réel\b", 'Culture'),
    (r"\bFond\.\s+pour\s+les\s+musiques\s+actuelles\b|\bFMA\b.*Docks|\bLes\s+Docks\b", 'Culture'),
    (r"\bSté\s+Cantonale\s+des\s+Musiques?\s+Vaudoises\b|\bSCMV\b", 'Culture'),
    (r"\bFond\.\s+CMA\b", 'Culture'),
    (r"\bAssoc\.\s+Culture\s+Valais\b", 'Culture'),
    (r"\bDreamAgo\b", 'Culture'),
    (r"\bFerme[\s-]Asile\b", 'Culture'),
    (r"\bAssoc\.\s+CORODIS\b|\bCORODIS\b", 'Culture'),
    (r"\b\.\.\.e\s+la\s+nave\s+va\b", 'Culture'),  # bizarre nom
    (r"\bSalopard\b", 'Culture'),
    
    # → PATRIMOINE
    (r"\bFond\.\s+Jean\s+Monnet\b", 'Conservation du patrimoine'),
    (r"\bVitrocentre\s+Romont\b|\brecherche\s+sur\s+le\s+vitrail\b",
     'Conservation du patrimoine'),
    
    # → SPORT
    (r"\bWorldcup\s+Veysonnaz\b|\bAssoc\.\s+Genevoise\s+d['\u2019]?Athlétisme\b",
     'Sport'),
    (r"\bLions\s+de\s+Genève\b", 'Sport'),  # basket Genève
    (r"\bGenève\s+Snowsports\b", 'Sport'),
    
    # → ACTION SOCIALE
    (r"\bSolidarité\s+Femmes\b", 'Action sociale et personnes âgées'),
    (r"\bCCSI\b|\bCentre\s+de\s+Contact\s+Suisses[\s-]Immigrés\b",
     'Action sociale et personnes âgées'),
]


def find(entry):
    text = (entry.get('nom') or '') + ' ' + (entry.get('description') or '')
    for p, s in RULES:
        if re.search(p, text, re.IGNORECASE): return s
    return None


total = 0
for y in ['2021', '2022', '2023', '2024', '2025']:
    p = DATA / f'brb{y}_full.json'
    d = json.load(open(p))
    n = 0
    for e in d['entries']:
        t = find(e)
        if t and t != e['secteur']:
            e['secteur'] = t; n += 1
    d['_meta']['sector_overrides_v6'] = {'count': n, 'date': '2026-06-04'}
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
    print(f"brb{y}: {n} overrides v6")
    total += n
print(f"Total: {total}")
