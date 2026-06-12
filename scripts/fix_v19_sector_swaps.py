#!/usr/bin/env python3
"""fix_v19_sector_swaps.py — Corriger classifications sectorielles inversées."""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'

# Patterns : (regex_nom, secteur_courant_à_corriger, secteur_cible)
SECTOR_FIXES = [
    # Sports classés Culture → Sport
    (r'\bHockey[-\s]?Club\b', ['Culture'], 'Sport'),
    (r'\bVolleyball\b.*Develop|^Volleyball\b', ['Culture'], 'Sport'),
    (r'\bFC\s+\w', ['Culture'], 'Sport'),
    (r'\bTennis[-\s]?Club\b', ['Culture'], 'Sport'),
    (r'\bSki[-\s]?Club\b', ['Culture'], 'Sport'),
    (r'\bRugby[-\s]?Club\b', ['Culture'], 'Sport'),
    (r'\bBasket[-\s]?Club\b', ['Culture'], 'Sport'),
    (r'\bGym[-\s]?Danse\b', ['Culture'], 'Sport'),
    
    # Culturels classés Sport → Culture
    (r'\bchœur\s+d', ['Sport'], 'Culture'),
    (r'\bchoeur\s+d', ['Sport'], 'Culture'),
    (r'\bOrchestre\b', ['Sport'], 'Culture'),
    (r'\bOpéra\b', ['Sport'], 'Culture'),
    (r'\bMusique\s+classique\b', ['Sport'], 'Culture'),
    (r'\bBallet\b', ['Sport'], 'Culture'),
    
    # Sports/Culture classés Action sociale (sauf EMS clairs)
    # (déjà fait dans v13)
]


def main():
    total = 0
    for y in ['2021', '2022', '2023', '2024', '2025']:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p, encoding='utf-8'))
        fixed = 0
        for e in d['entries']:
            nom = e['nom'] or ''
            current_sec = e.get('secteur') or ''
            for pat, from_sectors, to_sector in SECTOR_FIXES:
                if current_sec in from_sectors and re.search(pat, nom, re.IGNORECASE):
                    # Exclude réfections de noms type "Tennis Maison/club d'aide sociale"
                    # if "aide sociale" in nom.lower(): continue
                    e['secteur'] = to_sector
                    fixed += 1
                    break
        if fixed:
            d['_meta'].setdefault('fixes', {})['v19_sector_swaps'] = {'count': fixed}
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"  {y}: {fixed} secteurs corrigés (Hockey/Volleyball/etc.)")
        total += fixed
    print(f"\n  Total : {total}")

if __name__ == '__main__':
    main()
