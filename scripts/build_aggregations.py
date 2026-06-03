#!/usr/bin/env python3
"""
build_aggregations.py — Pass 8 (v13.10) — Aggregated datasets for new vizes
============================================================================

Produces 4 aggregated JSON files used by the new visualizations:
  - top30_beneficiaires.json   : top 30 distinct beneficiaries by total CHF
  - top20_villes.json          : top 20 cities by total CHF received
  - treemap_canton_secteur.json: nested canton > secteur > top beneficiaries
  - per_capita_v2.json         : CHF received per capita per canton

All derived from docs/data/brb2025_full.json (post v13.10 cleanup).
"""
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / 'docs' / 'data' / 'brb2025_full.json'
OUT = ROOT / 'docs' / 'data'


def normalize_name(name):
    if not name: return ''
    s = name.lower()
    s = re.sub(r"^(assoc\.|association|fond\.|fondation|fond|sté|société|club|comité|verein|federation|féd\.)\s+", '', s)
    s = re.sub(r",\s*[a-zéèôî' -]+$", '', s)
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
    s = re.sub(r"[^a-z0-9]+", ' ', s).strip()
    return s


def main():
    with open(INPUT) as f:
        data = json.load(f)
    entries = data['entries']
    total_all = sum(e.get('montant_CHF', 0) for e in entries)

    # ===== 1. Top 30 bénéficiaires (across all cantons, aggregated by normalized name) =====
    benef_agg = defaultdict(lambda: {
        'count': 0, 'total': 0, 'cantons': set(),
        'sample_nom': '', 'sample_ville': None, 'top_sector': defaultdict(int),
    })
    for e in entries:
        nn = normalize_name(e.get('nom', ''))
        if not nn or len(nn) < 4: continue
        amt = e.get('montant_CHF', 0)
        b = benef_agg[nn]
        b['count'] += 1
        b['total'] += amt
        b['cantons'].add(e.get('canton', ''))
        b['top_sector'][e.get('secteur', '') or 'n/a'] += amt
        # Keep longest sample nom as canonical (most informative)
        nom = e.get('nom', '')
        if len(nom) > len(b['sample_nom']):
            b['sample_nom'] = nom
            b['sample_ville'] = e.get('ville')

    benefs = []
    for nn, b in benef_agg.items():
        top_secteur = max(b['top_sector'].items(), key=lambda kv: kv[1])[0] if b['top_sector'] else ''
        benefs.append({
            'nom': b['sample_nom'],
            'ville': b['sample_ville'],
            'cantons': sorted(b['cantons']),
            'total_chf': b['total'],
            'attributions': b['count'],
            'top_secteur': top_secteur,
            'is_multi_canton': len(b['cantons']) > 1,
        })
    benefs.sort(key=lambda x: -x['total_chf'])
    top30 = benefs[:30]
    top30_total = sum(b['total_chf'] for b in top30)

    with open(OUT / 'top30_beneficiaires.json', 'w') as f:
        json.dump({
            '_meta': {
                'description': 'Top 30 bénéficiaires distincts par montant cumulé en 2025',
                'method': 'Aggrégation par nom normalisé après cleanup v13.10',
                'top30_total_chf': top30_total,
                'top30_pct_of_brb': round(100 * top30_total / total_all, 1),
            },
            'beneficiaires': top30,
        }, f, ensure_ascii=False, indent=2)
    print(f"✓ top30_beneficiaires.json : {top30_total:,} CHF ({100*top30_total/total_all:.1f}% du BRB)")

    # ===== 2. Top 20 villes (where money lands geographically) =====
    villes = defaultdict(lambda: {
        'count': 0, 'total': 0, 'cantons': set(),
        'lat': None, 'lng': None, 'top_beneficiaires': defaultdict(int),
    })
    for e in entries:
        v = e.get('ville')
        if not v: continue
        amt = e.get('montant_CHF', 0)
        c = villes[v]
        c['count'] += 1
        c['total'] += amt
        c['cantons'].add(e.get('canton', ''))
        if c['lat'] is None and e.get('lat') is not None:
            c['lat'] = e.get('lat')
            c['lng'] = e.get('lng')
        nn = normalize_name(e.get('nom', ''))
        if nn: c['top_beneficiaires'][nn] += amt

    villes_list = []
    for v, data_v in villes.items():
        top_b = sorted(data_v['top_beneficiaires'].items(), key=lambda kv: -kv[1])[:3]
        villes_list.append({
            'ville': v,
            'count': data_v['count'],
            'total_chf': data_v['total'],
            'cantons': sorted(data_v['cantons']),
            'lat': data_v['lat'],
            'lng': data_v['lng'],
            'top_3_beneficiaires': [{'nom': nn, 'chf': chf} for nn, chf in top_b],
        })
    villes_list.sort(key=lambda x: -x['total_chf'])
    top20_villes = villes_list[:20]

    with open(OUT / 'top20_villes.json', 'w') as f:
        json.dump({
            '_meta': {
                'description': 'Top 20 villes destinataires par montant cumulé en 2025',
                'method': "Aggrégation par champ 'ville'. Les entrées sans ville (~53%) ne sont pas comptabilisées.",
                'top20_total_chf': sum(v['total_chf'] for v in top20_villes),
            },
            'villes': top20_villes,
        }, f, ensure_ascii=False, indent=2)
    print(f"✓ top20_villes.json : top = {top20_villes[0]['ville']} ({top20_villes[0]['total_chf']:,} CHF)")

    # ===== 3. Treemap canton × secteur =====
    cs_agg = defaultdict(lambda: defaultdict(lambda: {
        'total': 0, 'count': 0, 'top_beneficiaires': defaultdict(int),
    }))
    for e in entries:
        c = e.get('canton', '')
        s = e.get('secteur', '') or 'n/a'
        amt = e.get('montant_CHF', 0)
        cs = cs_agg[c][s]
        cs['total'] += amt
        cs['count'] += 1
        nn = normalize_name(e.get('nom', ''))
        if nn: cs['top_beneficiaires'][nn] += amt

    treemap_data = []
    for c, secteurs in cs_agg.items():
        c_total = sum(s['total'] for s in secteurs.values())
        c_entry = {'canton': c, 'total_chf': c_total, 'secteurs': []}
        for s, data_s in sorted(secteurs.items(), key=lambda kv: -kv[1]['total']):
            top3 = sorted(data_s['top_beneficiaires'].items(), key=lambda kv: -kv[1])[:3]
            c_entry['secteurs'].append({
                'secteur': s,
                'total_chf': data_s['total'],
                'count': data_s['count'],
                'top_3': [{'nom': nn, 'chf': chf} for nn, chf in top3],
            })
        treemap_data.append(c_entry)
    treemap_data.sort(key=lambda x: -x['total_chf'])

    with open(OUT / 'treemap_canton_secteur.json', 'w') as f:
        json.dump({
            '_meta': {
                'description': 'Treemap canton × secteur : où va chaque CHF par canton',
                'method': "Aggrégation par (canton, secteur). Inclut le canton 'R' pour les attributions romandes intercantonales.",
                'note': "Le champ 'secteur' est partiellement faussé par un bug parser (voir METHODOLOGY v13.10). Les sommes globales par canton sont correctes.",
            },
            'cantons': treemap_data,
        }, f, ensure_ascii=False, indent=2)
    print(f"✓ treemap_canton_secteur.json")

    # ===== 4. Per-capita comparison =====
    # Approximate Romande population (2024 sources, in thousands)
    POPULATION = {
        'VD': 825_000, 'GE': 515_000, 'VS': 360_000,
        'FR': 335_000, 'NE': 175_000, 'JU':  75_000,
        'R':       0,  # Intercantonal — not per-capita
    }
    canton_total = defaultdict(int)
    for e in entries:
        canton_total[e.get('canton', '')] += e.get('montant_CHF', 0)

    per_cap = []
    for c, pop in POPULATION.items():
        total = canton_total.get(c, 0)
        per_cap.append({
            'canton': c,
            'population': pop,
            'total_chf': total,
            'chf_per_capita': round(total / pop, 1) if pop > 0 else 0,
        })
    per_cap.sort(key=lambda x: -x['chf_per_capita'])

    with open(OUT / 'per_capita_v2.json', 'w') as f:
        json.dump({
            '_meta': {
                'description': 'CHF reçus par habitant et par canton en 2025',
                'method': "Total des attributions du BRB 2025 / population résidente (sources cantonales 2024)",
                'note': "Le canton 'R' (intercantonal romand) n'a pas de population définie ; exclu du ratio.",
                'sources_population': "OFS / Statistiques cantonales 2024",
            },
            'cantons': per_cap,
        }, f, ensure_ascii=False, indent=2)
    print(f"✓ per_capita_v2.json")

    # Summary
    print(f"\n=== Summary ===")
    print(f"Top 30 captures: {100*top30_total/total_all:.1f}% of total BRB")
    print(f"Top 20 villes captures: {100*sum(v['total_chf'] for v in top20_villes)/total_all:.1f}% of total BRB")


if __name__ == '__main__':
    main()
