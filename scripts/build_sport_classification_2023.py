#!/usr/bin/env python3
"""
build_sport_classification.py — Pass 7 — Sport categorization (v13.10)
========================================================================

Classifies BRB entries by specific sport using keyword patterns on nom + description.
Note: ignores the unreliable `secteur` field which is contaminated by parser bugs
(many "Sport"-tagged entries are actually cultural events).

Output: docs/data/sports_classification_2023.json
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / 'docs' / 'data' / 'brb2023_full.json'
OUTPUT = ROOT / 'docs' / 'data' / 'sports_classification_2023.json'

# Ordered: most specific first to avoid false matches
# (e.g., Hockey sur glace before Hockey sur gazon catches HC- abbreviation)
SPORT_PATTERNS = [
    ('Football',          r'\b(football|FC[\s-]|football\s+club)\b'),
    ('Hockey sur glace',  r'\b(hockey[\s-]+sur[\s-]+glace|hockey[\s-]+club|hockey[\s-]+féminin|hockey\s+academy|ice\s+hockey|rink\s+hockey|HC[\s-]|EHC[\s-])'),
    ('Hockey sur gazon',  r'\b(hockey[\s-]+sur[\s-]+gazon|hockey\s+gazon)\b'),
    ('Basketball',        r'\b(basket\b|basketball|BBC[\s-]|BC[\s-])'),
    ('Volleyball',        r'\b(volley\b|volleyball|VBC[\s-])'),
    ('Tennis de table',   r'\b(tennis\s+de\s+table|ping-pong)\b'),
    ('Tennis / Padel',    r'\b(tennis\s+club|TC[\s-]|tennis\b|squash|padel)\b'),
    ('Athlétisme',        r'\b(athlétisme|athletisme|athletic|coureur|running|marathon|trail\s+running)\b'),
    ('Ski / Snowboard',   r'\b(ski\b|skiclub|snowboard|saut\s+à\s+ski|ski\s+club|ski\s+freestyle|biathlon|nordique)\b'),
    ('Natation',          r'\b(natation|aquatique|water-?polo|piscine|nageur)\b'),
    ('Voile / Nautique',  r'\b(voile|nautique|yacht|optimist|skiff|catamaran)\b'),
    ('Cyclisme / VTT',    r'\b(cyclisme|vtt|cyclo|vélo|velo|tour\s+de|étape\s+cyclo|cycling)\b'),
    ('Gymnastique',       r'\b(gym\b|gymnastique|FSG[\s-]|gymnaste|trampoline|acro)\b'),
    ('Curling',           r'\b(curling)\b'),
    ('Patinage',          r'\b(patinage|patineurs|patinoire|patineuses)\b'),
    ('Boxe / Combat',     r'\b(boxe|MMA\b|boxing|combat|kickbox|muay\s+thai)\b'),
    ('Judo / Karaté',     r'\b(judo|karaté|karate|taekwondo|jiu-jitsu|aïkido|self-?défense)\b'),
    ('Escrime',           r'\b(escrime|épée|fleuret|sabre)\b'),
    ('Tir',               r'\b(tir\s+|tireurs|arquebusiers|carabine|tir\s+à\s+l\'arc)\b'),
    ('Handball',          r'\b(handball|HB[\s-])'),
    ('Rugby',             r'\b(rugby|RC[\s-])'),
    ('Équitation',        r'\b(équitation|cheval|hippique|chevaux|concours\s+hippique)\b'),
    ('Arts martiaux',     r'\b(arts\s+martiaux|kung\s+fu|wushu)\b'),
    ('Pétanque / Boules', r'\b(pétanque|boules)\b'),
    ('Triathlon',         r'\b(triathlon)\b'),
    ('Escalade / Montagne', r'\b(escalade|grimpe|alpinisme|montagne)\b'),
    ('Aviron',            r'\b(aviron)\b'),
    ('Lutte suisse',      r'\b(lutte\s+suisse|schwingen|schwingerverband|schwingklub)\b'),
    ("Course d'orientation", r"\b(orientation|course\s+d'orientation)\b"),
    ('Multi-sports',      r'\b(multi-?sport|polysportif|olympique|sportifs?\b|sportive\b|sports?\b)\b'),
]

# Pre-compile
COMPILED = [(name, re.compile(pat, re.IGNORECASE)) for name, pat in SPORT_PATTERNS]


def classify(entry: dict) -> str | None:
    """Return sport category or None."""
    nom = entry.get('nom', '') or ''
    desc = entry.get('description', '') or ''
    text = nom + ' ' + desc
    for name, pat in COMPILED:
        if pat.search(text):
            return name
    return None


def main():
    with open(INPUT) as f:
        data = json.load(f)
    entries = data['entries']
    total_chf_all = sum(e.get('montant_CHF', 0) for e in entries)

    buckets = defaultdict(lambda: {
        'count': 0, 'total_chf': 0, 'samples': [],
        'cantons': defaultdict(lambda: {'count': 0, 'total_chf': 0})
    })

    for e in entries:
        sport = classify(e)
        if not sport:
            continue
        amt = e.get('montant_CHF', 0) or 0
        b = buckets[sport]
        b['count'] += 1
        b['total_chf'] += amt
        c = e.get('canton', '')
        b['cantons'][c]['count'] += 1
        b['cantons'][c]['total_chf'] += amt
        sample_nom = e.get('nom', '')
        if sample_nom and sample_nom not in [s['nom'] for s in b['samples']]:
            b['samples'].append({
                'nom': sample_nom,
                'ville': e.get('ville'),
                'canton': c,
                'montant_CHF': amt,
            })

    # Convert defaultdicts and prepare output
    sports = []
    for name, b in buckets.items():
        sports.append({
            'name': name,
            'count': b['count'],
            'total_chf': b['total_chf'],
            'mean_chf': b['total_chf'] // b['count'] if b['count'] else 0,
            'cantons': {c: dict(d) for c, d in b['cantons'].items()},
            'samples': sorted(b['samples'], key=lambda s: -s['montant_CHF'])[:5],
        })
    sports.sort(key=lambda s: -s['total_chf'])

    total_classified_count = sum(s['count'] for s in sports)
    total_classified_chf = sum(s['total_chf'] for s in sports)

    out = {
        '_meta': {
            'source': 'docs/data/brb2023_full.json (v15.0 GE/JU/SR extracted)',
            'method': 'Keyword classification on nom + description (ignoring unreliable secteur field)',
            'date': '2026-06-03',
            'version': 'v13.10',
            'total_entries': len(entries),
            'total_entries_classified': total_classified_count,
            'total_chf_all': total_chf_all,
            'total_chf_classified': total_classified_chf,
            'pct_entries_classified': round(100 * total_classified_count / len(entries), 1),
            'pct_chf_classified': round(100 * total_classified_chf / total_chf_all, 1),
            'note': (
                "Classification basée sur les mots-clés présents dans le nom et "
                "la description. Une entrée est attribuée à une seule catégorie "
                "(la première qui matche dans l'ordre de spécificité). Les "
                "bénéficiaires inter-disciplinaires (associations cantonales "
                "multi-sports) sont rangés sous 'Multi-sports'."
            ),
        },
        'sports': sports,
    }

    with open(OUTPUT, 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Classified {total_classified_count} entries ({out['_meta']['pct_entries_classified']}%)")
    print(f"Total CHF classified: {total_classified_chf:,} ({out['_meta']['pct_chf_classified']}% of all)")
    print(f"Categories: {len(sports)}")
    print(f"Output: {OUTPUT}")


if __name__ == '__main__':
    main()
