#!/usr/bin/env python3
"""fix_sectors_via_keywords_v12.py — corrections audit Passe 5."""
import json, re
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'

RULES = [
    # ─── CULTURE mal classés en SANTE 2024 (gros impact)
    (r"\bEnsemble\s+Vocal\s+de\s+Lausanne\b|\bEVL\b", 'Culture'),
    (r"\bFAR\s+Festival\b", 'Culture'),
    (r"\bJazzOnze\s*\+\s*Festival\b|\bJazz\s+Onze\s*\+\b", 'Culture'),
    (r"\bAssoc\.\s+Les\s+Francomanias\b|\bFrancomanias\b", 'Culture'),
    (r"\bL['\u2019]?Ensemble\s+Vocal\b", 'Culture'),
    (r"\bSwiss\s+Aware\b", 'Santé et handicap'),  # OK
    # ─── Sport en jeunesse (Swiss Bike Park)
    (r"\bSwiss\s+Bike\s+Park\b", 'Sport'),
    # ─── Action sociale en jeunesse
    (r"\bCollectif\s+d['\u2019]?Associations\s+pour\s+l['\u2019]?urgence\s+sociale\b",
     'Action sociale et personnes âgées'),
    (r"\bAssoc\.\s+Pacifique\b", 'Action sociale et personnes âgées'),
    (r"\bLa\s+Rouvraie\b", 'Jeunesse et éducation'),  # Camp de jeunesse OK
    # ─── Sport mal classés en Environnement
    (r"\bAssoc\.\s+JuraCycles\b|\bJuraCycles\.ch\b", 'Sport'),
    # ─── Promotion (manifestations populaires)
    (r"\bSechseläuten\b", 'Promotion, tourisme et développement'),
    (r"\bgîte\s+EL\s+JIRE\b|\bEl\s+Jire\b", 'Promotion, tourisme et développement'),  # gîte rural
    # ─── Environnement (NatureCulture)
    (r"\bNatureCulture\b", 'Environnement'),
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
    d['_meta']['sector_overrides_v12'] = {'count': n, 'date': '2026-06-04'}
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2, encoding='utf-8'))
    print(f"brb{y}: {n} overrides v12")
    total += n
print(f"Total: {total}")
