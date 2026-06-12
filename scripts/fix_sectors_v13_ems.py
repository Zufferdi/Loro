#!/usr/bin/env python3
"""fix_sectors_v13_ems.py — EMS mal-classés Culture → Action sociale."""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'

# Reclassification EMS / Senior — patterns prioritaires
EMS_PATTERNS = [
    # Tertianum (groupe d'EMS) — toujours action sociale
    (r'^Tertianum\s+', 'Action sociale et personnes âgées'),
    # Senior / Pflegeheim
    (r'\bSeniorenzentrum\b', 'Action sociale et personnes âgées'),
    (r'\bSenioren[-\s]+und\s+Pflege', 'Action sociale et personnes âgées'),
    (r'\bPflegeheim\b', 'Action sociale et personnes âgées'),
    # EMS terme générique
    (r'\bEMS\s+\w', 'Action sociale et personnes âgées'),
    (r'\bem\s+ems\b|^EMS\b', 'Action sociale et personnes âgées'),
    # Home (résidences)
    (r'^Home\s+\w', 'Action sociale et personnes âgées'),
    (r'\bFond\.\s+du\s+Home\b', 'Action sociale et personnes âgées'),
    # Foyer pour personnes âgées / EMS  
    (r'^Foyer\s+(?:les?\s+)?(?:3\s+Sapins?|Saint-?Joseph|Beau-?Site)', 'Action sociale et personnes âgées'),
    (r'\bFoyer\s+Haut-de-Cry\b', 'Action sociale et personnes âgées'),
    (r'\bFoyer\s+Pierre-?Olivier\b', 'Action sociale et personnes âgées'),
    (r'^Foyer\s+Ma\s+Vallée\b', 'Action sociale et personnes âgées'),
    # Résidences EMS (pas résidences artistiques !)
    (r'^Résidence\s+(?:Gravelone|Plantzette|Belle-Vue|St-Sylvain|Beausite|Le\s+Cottage|Beau-?Soleil|Soleilmont|Tour-d[\u2019\']Aï|Forel|d[\u2019\']Anavière|Don\s+Bosco|Le\s+Carillon)\b', 'Action sociale et personnes âgées'),
    (r'^Fond\.\s+(?:la\s+)?Résidence\s*$', 'Action sociale et personnes âgées'),
    # Maisons de retraite
    (r'\bMaison\s+(?:de\s+|du\s+)?(?:retraite|soins\s+et\s+de\s+réhabilitation|de\s+repos)\b', 'Action sociale et personnes âgées'),
    (r'\bMaison\s+du\s+Vélan\b|\bMaison\s+St-?Vincent\b|\bMaison\s+Marie\b|\bMaison\s+Caritas\b', 'Action sociale et personnes âgées'),
    # Fédérations EMS / Senior
    (r'\bFegems\b|\bFédération\s+des\s+EMS\b|\bAssoc\.\s+des\s+EMS\b', 'Action sociale et personnes âgées'),
    # Cogest-EMS (gestion EMS)
    (r"\bCogest['\u2019]?ems?\b", 'Action sociale et personnes âgées'),
    # Pro-Home (résidence pour personnes âgées)
    (r'\bPro[-\s]+Home\b', 'Action sociale et personnes âgées'),
    # Termes spécifiques aux noms d'EMS jurassiens / valaisans / fribourgeois
    (r'^EMS\s+', 'Action sociale et personnes âgées'),
    (r"\bFond\.\s+pour\s+les\s+personnes?\s+âgées?\b", 'Action sociale et personnes âgées'),
    (r'^Le\s+Carillon\s*-\s*maison\s+de\s+retraite', 'Action sociale et personnes âgées'),
    (r'^Fond\.\s+du\s+Foyer\s+', 'Action sociale et personnes âgées'),
    (r'^Fond\.\s+(?:du\s+)?(?:home|Home)\s+', 'Action sociale et personnes âgées'),
]

# EXCLUSIONS — résidences artistiques / culturelles à NE PAS toucher
EXCLUDE_PATTERNS = [
    r"résidence\s+d['\u2019]?auteurs?",
    r'résidences?\s+de\s+(?:création|recherche|artistes?)',
    r'\bAssoc\.\s+Lestime\b',  # archives - résidence artistique
    r'\bRésidence\s+artistique\b',
    r'\bRésidence\s+de\s+théâtre\b',
    r'\bRésidence\s+littéraire\b',
    r'Activation\s+des\s+Archives',
]


def should_reclassify(entry):
    text = entry['nom']
    desc = entry.get('description', '') or ''
    full = text + ' ' + desc
    # Exclude résidences artistiques
    for pat in EXCLUDE_PATTERNS:
        if re.search(pat, full, re.IGNORECASE):
            return None
    # Match EMS patterns
    for pat, target in EMS_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return target
    return None


def main():
    total_fixed = 0
    for y in ['2021', '2022', '2023', '2024', '2025']:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p, encoding='utf-8'))
        fixed = 0
        for e in d['entries']:
            target = should_reclassify(e)
            if target and e.get('secteur') != target:
                old = e.get('secteur') or '(None)'
                e['secteur'] = target
                fixed += 1
        if fixed:
            d['_meta'].setdefault('fixes', {})['v13_ems'] = {'count': fixed}
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"  {y}: {fixed} entries reclassées en Action sociale (EMS/Senior)")
        total_fixed += fixed
    print(f"\n  Total : {total_fixed} entries fixées")


if __name__ == '__main__':
    main()
