#!/usr/bin/env python3
"""fix_sectors_via_keywords_v7.py — derniers bugs secteurs."""
import json, re
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'

RULES = [
    # ─── EMS → Action sociale et personnes âgées
    # Pattern strict pour éviter de faux positifs (EMS comme initiales)
    (r"\bEMS\s+[A-Z]\w|\bEMS\s+(?:Les?|La|du|de|St|Saint)\b|\bRésidence\s+(?:Jean|Les?)",
     'Action sociale et personnes âgées'),
    (r"\bFond\.\s+Jeanne-Milloud\b", 'Action sociale et personnes âgées'),
    
    # ─── Musées → Conservation du patrimoine
    (r"\bMusée\s+international\s+de\s+la\s+Croix-Rouge\b", 'Conservation du patrimoine'),
    (r"\bAmis\s+(?:des\s+)?Musées?\b", 'Conservation du patrimoine'),
    (r"\bMusée\s+(?:Cantonal\s+)?(?:de\s+)?Zoologie\b", 'Conservation du patrimoine'),
    (r"\bMusée\s+suisse\s+du\s+Cheval\b", 'Conservation du patrimoine'),
    (r"\bMusée\s+suisse\s+de\s+l['\u2019]?appareil\s+photographique\b",
     'Conservation du patrimoine'),
    (r"\bNuit\s+des\s+Musées\b", 'Conservation du patrimoine'),
    (r"\bMusée\s+(?:cantonal\s+)?(?:des\s+|d['\u2019])?Beaux-Arts\b", 'Conservation du patrimoine'),
    
    # ─── Crèches → Jeunesse
    (r"\bCrèche\s+(?:le|la|du|de|des|saint)\w*\s", 'Jeunesse et éducation'),  # crèche d'enfants
    # (mais pas "Route des Crèches" qui est un événement Culture)
]


def find(entry):
    text = (entry.get('nom') or '') + ' ' + (entry.get('description') or '')
    # Exclure les cas false positives connus
    if 'Route des Crèches' in text: return None
    # "Institut universitaire de sciences sociales des religions" contient "EMS"
    # par coincidence (sciences) — le filtrer
    if 'sciences sociales' in text and 'EMS' not in (entry.get('nom') or ''):
        # cas où EMS apparait seulement via "Eucumenique" etc.
        if not re.search(r'\bEMS\b', entry.get('nom', '')):
            return None
    for p, s in RULES:
        if re.search(p, text, re.IGNORECASE): return s
    return None


total = 0
for y in ['2021', '2022', '2023', '2024', '2025']:
    p = DATA / f'brb{y}_full.json'
    d = json.load(open(p, encoding='utf-8'))
    n = 0
    for e in d['entries']:
        t = find(e)
        if t and t != e['secteur']:
            e['secteur'] = t; n += 1
    d['_meta']['sector_overrides_v7'] = {'count': n, 'date': '2026-06-04'}
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"brb{y}: {n} overrides v7")
    total += n
print(f"Total: {total}")
