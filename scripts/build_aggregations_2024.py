#!/usr/bin/env python3
"""build_aggregations_2024.py — version 2024 du builder d'agrégations.
Génère top30/villes/treemap/per_capita avec suffixe _2024 depuis brb2024_full.json.
"""
# (Bloc importlib.exec_module supprimé : il écrasait les JSON 2025 à chaque run.
# Ce script fait sa propre computation en dessous, c'est suffisant.)
import json, re, unicodedata
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / 'docs' / 'data' / 'brb2024_full.json'
OUT   = ROOT / 'docs' / 'data'

data = json.load(open(INPUT, encoding='utf-8'))
entries = data['entries']
total_all = sum(e.get('montant_CHF', 0) for e in entries)

# Reproduce the 4 aggregations with _2024 suffix
# Top 30
def normalize_name(name):
    if not name: return ''
    s = name.lower()
    s = re.sub(r"^(assoc\.|association|fond\.|fondation|fond|sté|société|club|comité|verein|federation|féd\.)\s+", '', s)
    s = re.sub(r",\s*[a-zéèôî' -]+$", '', s)
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
    s = re.sub(r"[^a-z0-9]+", ' ', s).strip()
    return s

by_name = defaultdict(lambda: {'nom': '', 'cantons': set(), 'ville': None, 'secteurs': defaultdict(float), 'count': 0, 'total': 0})
for e in entries:
    key = normalize_name(e['nom'])
    if not key: continue
    rec = by_name[key]
    if not rec['nom'] or len(e['nom']) < len(rec['nom']):
        rec['nom'] = e['nom']
    rec['cantons'].add(e.get('canton') or '')
    if not rec['ville'] and e.get('ville'):
        rec['ville'] = e['ville']
    sec = e.get('secteur', 'n/a')
    rec['secteurs'][sec] += e.get('montant_CHF', 0)
    rec['count'] += 1
    rec['total'] += e.get('montant_CHF', 0)

top30 = []
for key, r in by_name.items():
    top_sec = max(r['secteurs'].items(), key=lambda x: x[1])[0] if r['secteurs'] else 'n/a'
    top30.append({
        'nom': r['nom'], 'ville': r['ville'],
        'cantons': sorted([c for c in r['cantons'] if c]),
        'is_multi_canton': len(r['cantons']) > 1,
        'count': r['count'],
        'total_CHF': int(r['total']), 'secteur_principal': top_sec, 'is_consolidated': False,
    })
top30.sort(key=lambda x: -x['total_CHF'])
top30 = top30[:30]
top30_total = sum(x['total_CHF'] for x in top30)
out = {
    '_meta': {'description': 'Top 30 (2024)', 'method': 'normalized', 'top30_total_chf': top30_total, 'top30_pct_of_brb': round(100*top30_total/total_all, 1)},
    'beneficiaires': top30
}
json.dump(out, open(OUT / 'top30_beneficiaires_2024.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print(f"✓ top30_beneficiaires_2024.json")

# Top 20 villes
by_ville = defaultdict(lambda: {'count': 0, 'total': 0, 'cantons': set(), 'top3': []})
for e in entries:
    v = e.get('ville')
    if not v: continue
    rec = by_ville[v]
    rec['count'] += 1
    rec['total'] += e.get('montant_CHF', 0)
    rec['cantons'].add(e.get('canton'))
    rec['top3'].append({'nom': e['nom'], 'chf': e.get('montant_CHF', 0)})

villes = []
for v, r in by_ville.items():
    r['top3'].sort(key=lambda x: -x['chf'])
    villes.append({
        'ville': v, 'count': r['count'], 'total_CHF': int(r['total']),
        'cantons': sorted([c for c in r['cantons'] if c]),
        'top_3_beneficiaires': r['top3'][:3],
    })
villes.sort(key=lambda x: -x['total_CHF'])
villes = villes[:20]
villes_total = sum(x['total_CHF'] for x in villes)
out = {'_meta': {'description': 'Top 20 villes (2024)', 'method': 'group by ville', 'top20_total_chf': villes_total}, 'villes': villes}
json.dump(out, open(OUT / 'top20_villes_2024.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print(f"✓ top20_villes_2024.json")

# Treemap canton x secteur
by_canton_sec = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'total': 0, 'top3': []}))
for e in entries:
    c = e.get('canton') or '?'
    s = e.get('secteur') or 'n/a'
    rec = by_canton_sec[c][s]
    rec['count'] += 1
    rec['total'] += e.get('montant_CHF', 0)
    rec['top3'].append({'nom': e['nom'], 'chf': e.get('montant_CHF', 0)})

cantons_out = []
for c, sec_dict in by_canton_sec.items():
    sec_list = []
    total_c = 0
    for s, r in sec_dict.items():
        r['top3'].sort(key=lambda x: -x['chf'])
        sec_list.append({'secteur': s, 'count': r['count'], 'total_CHF': int(r['total']), 'top_3': r['top3'][:3]})
        total_c += r['total']
    sec_list.sort(key=lambda x: -x['total_CHF'])
    cantons_out.append({'canton': c, 'total_CHF': int(total_c), 'secteurs': sec_list})
cantons_out.sort(key=lambda x: -x['total_CHF'])
out = {'_meta': {'description': 'Treemap canton×secteur (2024)'}, 'cantons': cantons_out}
json.dump(out, open(OUT / 'treemap_canton_secteur_2024.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print(f"✓ treemap_canton_secteur_2024.json")

# Per capita
POP = {'VD': 825000, 'GE': 519000, 'FR': 330000, 'VS': 358000, 'NE': 175000, 'JU': 75000}
by_c = defaultdict(float)
for e in entries:
    by_c[e.get('canton')] += e.get('montant_CHF', 0)
out_pc = []
for c, total in by_c.items():
    pop = POP.get(c, 0)
    out_pc.append({'canton': c, 'population': pop, 'total_CHF': int(total),
                   'chf_per_capita': round(total/pop, 1) if pop else 0})
out_pc.sort(key=lambda x: -x['chf_per_capita'])
out = {'_meta': {'description': 'CHF par habitant (2024)'}, 'cantons': out_pc}
json.dump(out, open(OUT / 'per_capita_2024.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print(f"✓ per_capita_2024.json")
