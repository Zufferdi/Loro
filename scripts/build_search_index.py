#!/usr/bin/env python3
"""
build_search_index.py — Génère docs/data/search_index.json
================================================================================

Index unifié des bénéficiaires sur 5 ans (2021-2025), avec déduplication par
nom canonique. Utilisé par docs/js/find_org.js pour la recherche full-text.

Format compact (~400 KB-1 MB selon nombre d'orgs) :
{
  "_meta": {...},
  "orgs": [
    {
      "k": "key_courte",          # clé canonique normalisée (recherche)
      "n": "Nom affichable",      # premier nom non-tronqué trouvé
      "c": ["VD", "GE"],          # cantons (sorted unique)
      "s": "Culture",             # secteur principal (le plus fréquent)
      "a": {"2021": 12345, ...},  # montants par année (uniquement non-zéro)
      "t": 56789,                 # total cumulé sur 5 ans
      "p": 4                      # nombre années présent (1-5)
    },
    ...
  ]
}
"""
from __future__ import annotations
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'docs' / 'data'
OUT_PATH = DATA / 'search_index.json'

YEARS = [2021, 2022, 2023, 2024, 2025]


def normalize_name(name: str) -> str:
    """Normalise un nom pour comparaison / clé canonique.

    Stratégie : minuscule, suppression accents, suppression préfixes communs
    (Fondation, Association, Sté, Club), suppression suffixe canton entre virgules,
    suppression ponctuation, espaces collapsés.
    """
    if not name:
        return ''
    s = name.lower()
    # Retirer préfixes communs
    s = re.sub(
        r"^(assoc\.|association|fond\.|fondation|fond|sté|société|club|comité|"
        r"verein|federation|féd\.|coopérative|coop\.|institut|inst\.|centre|"
        r"groupe|gpe\.|service)\s+",
        '',
        s,
    )
    # Retirer suffixe ", lieu" (ex: "Festival, Lausanne")
    s = re.sub(r",\s*[a-zéèôî' -]+$", '', s)
    # Désaccentuer
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
    # Garder seulement alphanumérique + espace
    s = re.sub(r"[^a-z0-9]+", ' ', s).strip()
    return s


def shortest_display_name(names: list[str]) -> str:
    """Choisit le nom d'affichage le plus représentatif :
    - Préfère les non-tronqués (sans …)
    - Préfère les plus longs (plus informatifs)
    - Décourage les ALL CAPS si une alternative casse mixte existe
    """
    if not names:
        return ''
    non_truncated = [n for n in names if '…' not in n and '...' not in n]
    pool = non_truncated or names
    # Préférer les non-allcaps si possible
    mixed = [n for n in pool if not n.isupper()]
    pool = mixed or pool
    # Préférer le plus long, mais raisonnablement (cap à 80 chars)
    pool = sorted(pool, key=lambda n: (len(n) > 80, -len(n)))
    return pool[0]


def main() -> None:
    # Indexer : par clé canonique, collecter cantons, secteurs, montants annuels
    by_key = defaultdict(lambda: {
        'names': [],
        'cantons': set(),
        'villes': set(),
        'sectors': defaultdict(float),    # secteur → CHF agrégés
        'amounts': defaultdict(float),    # année → CHF
        'count_attributions': 0,
    })

    for year in YEARS:
        brb_path = DATA / f'brb{year}_full.json'
        if not brb_path.exists():
            print(f'  ⚠ {brb_path} absent, skip')
            continue
        with open(brb_path, encoding='utf-8') as f:
            data = json.load(f)
        entries = data.get('entries', [])
        added = 0
        for e in entries:
            nom = (e.get('nom') or '').strip()
            if not nom:
                continue
            key = normalize_name(nom)
            if not key or len(key) < 2:
                continue
            rec = by_key[key]
            rec['names'].append(nom)
            if e.get('canton'):
                rec['cantons'].add(e['canton'])
            if e.get('ville'):
                rec['villes'].add(e['ville'])
            sec = e.get('secteur') or 'n/a'
            amt = e.get('montant_CHF', 0) or 0
            rec['sectors'][sec] += amt
            rec['amounts'][year] += amt
            rec['count_attributions'] += 1
            added += 1
        print(f'  ✓ {year}: {added:5d} entries → {len(by_key):5d} orgs uniques (cumul)')

    # Construire la sortie compacte
    orgs = []
    skipped_pollution = 0
    for key, rec in by_key.items():
        display_name = shortest_display_name(rec['names'])
        # Filtrer noms invalides / vides
        if not display_name:
            continue
        # Filtrer les clés pathologiques (parser n'a pas découpé une liste — voir Acte VI fondations sportives)
        if len(key) > 200:
            skipped_pollution += 1
            continue
        # Secteur principal = celui avec le plus gros montant cumulé
        secteur_principal = (
            max(rec['sectors'].items(), key=lambda x: x[1])[0] if rec['sectors'] else 'n/a'
        )
        # Cantons triés
        cantons_sorted = sorted(c for c in rec['cantons'] if c)
        # Montants par année (filtrer les 0)
        amounts = {str(y): int(rec['amounts'][y]) for y in YEARS if rec['amounts'][y] > 0}
        total = sum(amounts.values())
        if total == 0:
            continue
        orgs.append({
            'k': key,
            'n': display_name,
            'c': cantons_sorted,
            's': secteur_principal,
            'a': amounts,
            't': total,
            'p': len(amounts),
            'na': rec['count_attributions'],   # nombre d'attributions sur 5 ans
        })

    if skipped_pollution:
        print(f'  ⚠ {skipped_pollution} entrées filtrées (clé > 200 chars, pollution parser)')

    # Trier par total décroissant (les recherches naturelles favoriseront les gros)
    orgs.sort(key=lambda o: -o['t'])

    out = {
        '_meta': {
            'description': 'Index unifié pour recherche full-text par nom d\'organisation, 2021-2025',
            'years': YEARS,
            'count_orgs': len(orgs),
            'count_attributions_total': sum(o['na'] for o in orgs),
            'normalization': 'lowercase + remove accents + strip common prefixes',
            'fields': {
                'k': 'clé canonique normalisée (recherche)',
                'n': 'nom d\'affichage',
                'c': 'liste cantons',
                's': 'secteur principal (cumulé)',
                'a': 'dict {année: montant CHF} (uniquement non-zéro)',
                't': 'total cumulé sur 5 ans',
                'p': 'nombre années présent (1-5)',
                'na': 'nombre d\'attributions distinctes',
            },
        },
        'orgs': orgs,
    }

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

    size_kb = OUT_PATH.stat().st_size / 1024
    print()
    print(f'✓ {OUT_PATH.relative_to(ROOT)} généré')
    print(f'  - {len(orgs):,} organisations uniques')
    print(f'  - taille : {size_kb:.0f} KB')
    print(f'  - total attributions : {out["_meta"]["count_attributions_total"]:,}')


if __name__ == '__main__':
    main()
