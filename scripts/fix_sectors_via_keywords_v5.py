#!/usr/bin/env python3
"""
fix_sectors_via_keywords_v5.py — Final pass
"""
import json, re
from pathlib import Path
DATA = Path('/home/claude/audit3/Loro-main/docs/data')

RULES = [
    # Culture
    (r"\bCentre\s+dramatique\b", 'Culture'),
    (r"\bBéjart\s+Ballet\b|\bBBL\b", 'Culture'),
    (r"\bFond\.\s+de\s+l['\u2019]?Hermitage\b", 'Culture'),
    (r"\bFri[\s-]Son\b", 'Culture'),
    (r"\bUsine\s+à\s+Gaz\b", 'Culture'),
    (r"\bMusique\s+des\s+Lumières\b", 'Culture'),
    (r"\bAssoc\.\s+CORODIS\b", 'Culture'),
    (r"\bSalopard\b|\b\.\.\.\s*e\s+la\s+nave\s+va\b", 'Culture'),
    (r"\bBibliothèque\s+interculturelle\b|\bLivrEchange\b", 'Culture'),
    
    # Social
    (r"\bFond\.\s+Immobilière\s+Privée\s+pour\s+l['\u2019]?Insertion\s+Sociale\b",
     'Action sociale et personnes âgées'),
    (r"\bATD[\s-]?Quart\s+Monde\b", 'Action sociale et personnes âgées'),
    (r"\bAssoc\.\s+Argos\b", 'Action sociale et personnes âgées'),
    (r"\bAccueil\s+à\s+Bas\s+Seuil\b|\bABS\b", 'Action sociale et personnes âgées'),
    
    # Patrimoine
    (r"\bEspace\s+du\s+Blé\s+au\s+Pain\b", 'Conservation du patrimoine'),
    (r"\bASPAM\b|\bprotection\s+du\s+patrimoine\s+des\s+Montagnes\b",
     'Conservation du patrimoine'),
    
    # Promotion
    (r"\bIVV\b|\bInterprofession\s+de\s+la\s+Vigne\s+et\s+du\s+Vin\b",
     'Promotion, tourisme et développement'),
    (r"\bVapeur\s+Val[\s-]de[\s-]Travers\b|\bVVT\b", 'Promotion, tourisme et développement'),
    
    # Santé
    (r"\bPôle\s+Santé\b", 'Santé et handicap'),
    
    # Jeunesse  
    (r"\bCoopérative\s+Cité\s+Derrière\b", 'Action sociale et personnes âgées'),
]

def find(entry):
    text = (entry.get('nom') or '') + ' ' + (entry.get('description') or '')
    for p, s in RULES:
        if re.search(p, text, re.IGNORECASE): return s
    return None

for y in ['2021', '2022', '2023', '2024', '2025']:
    p = DATA / f'brb{y}_full.json'
    d = json.load(open(p))
    n = 0
    for e in d['entries']:
        t = find(e)
        if t and t != e['secteur']:
            e['secteur'] = t; n += 1
    d['_meta']['sector_overrides_v5'] = {'count': n, 'date': '2026-06-04'}
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
    print(f"brb{y}: {n} overrides v5")
