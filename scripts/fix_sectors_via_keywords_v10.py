#!/usr/bin/env python3
"""fix_sectors_via_keywords_v10.py — corrections après audit Passe 3."""
import json, re
from pathlib import Path
DATA = Path('/home/claude/audit2/Loro-main/docs/data')

RULES = [
    # ─── Sport mal classés (entries actuellement en Sport sont CULTURE / SOCIAL) ───
    (r"\bFond\.\s+Partage\b", 'Action sociale et personnes âgées'),  # aide alimentaire GE
    (r"\bCapitale\s+culturelle\s+suisse\b", 'Culture'),
    (r"\bUnions\s+Chrétiennes\s+de\s+Genève\b|\bUCG\b", 'Action sociale et personnes âgées'),
    
    # ─── Culture mal classées en JEUNESSE/SANTE/SPORT ───
    (r"\bPanorama\s+de\s+la\s+Bataille\s+de\s+Morat\b", 'Conservation du patrimoine'),
    (r"\bFond\.\s+la\s+Tour\s+Vagabonde\b|\bTour\s+Vagabonde\b", 'Culture'),
    (r"\bPetit\s+Théâtre\s+de\s+Lausanne\b", 'Culture'),
    (r"\bPrix\s+de\s+Lausanne\b|\bArt\s+chorégraphique\b", 'Culture'),
    (r"\bKultur\s+im\s+Podium\b", 'Culture'),
    (r"\bFond\.\s+Bex\s+&\s+Arts\b|\bBex\s+&\s+Arts\b", 'Culture'),
    (r"\bAssoc\.\s+Grand\s+Mirific\b|\bGrand\s+Mirific\b", 'Culture'),
    (r"\bCORODIS\b", 'Culture'),
    
    # ─── Sport (entries actuellement en Promotion/Environnement)
    (r"\bAssoc\.\s+Cantonale\s+(?:Vaudoise|Genevoise|Valaisanne|Fribourgeoise|Neuchâteloise|Jurassienne)\s*,?\s+Football\b",
     'Sport'),
    
    # ─── EMS → Action sociale (vu en social 2022 catch-all)
    (r"\bLa\s+Rozavère\b", 'Action sociale et personnes âgées'),
    (r"\bFond\.\s+de\s+l['\u2019]?Orme\b", 'Action sociale et personnes âgées'),
    
    # ─── Jeunesse spécifique
    (r"\bJobtrek\b", 'Formation et recherche'),  # apprentissage
    (r"\bEducation\s+Familiale\b", 'Action sociale et personnes âgées'),
    
    # ─── Environnement (le bruit sport mal placé en environnement)
    # Note : "Bucher Louis Cyclisme" est un fragment, peu d'action
    
    # ─── Promotion (Commune d'Yverdon = manifestation)
    (r"\bCommune\s+de\s+Lucens\b", 'Promotion, tourisme et développement'),
]


def find_override(entry):
    text = (entry.get('nom') or '') + ' ' + (entry.get('description') or '')
    for pattern, sector in RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return sector
    return None


total = 0
for y in ['2022', '2023', '2024', '2025']:
    p = DATA / f'brb{y}_full.json'
    d = json.load(open(p))
    n = 0
    for e in d['entries']:
        t = find_override(e)
        if t and t != e['secteur']:
            e['secteur'] = t
            n += 1
    d['_meta']['sector_overrides_v10'] = {'count': n, 'date': '2026-06-04'}
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
    print(f"brb{y}: {n} overrides v10")
    total += n
print(f"Total: {total}")
