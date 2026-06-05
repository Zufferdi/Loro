#!/usr/bin/env python3
"""consolidate_classification_aliases.py — applique les aliases aux samples/all_entries
   des fichiers culture/social/sport/etc. _classification_{YEAR}.json
"""
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

DATA = Path('/home/claude/audit3/Loro-main/docs/data')

# Aliases (sous-ensemble principal pour affichage dans samples)
ALIASES = [
    (r'\bFond\.?\s+(?:du\s+)?Tour\s+de\s+Romandie(?!\s+Féminin)|^Tour\s+de\s+Romandie(?!\s+Féminin)|\bArrivée\s+du\s+Tour\s+de\s+Romandie\b', 'Tour de Romandie'),
    (r'\bTour\s+de\s+Romandie\s+Féminin\b', 'Tour de Romandie Féminin'),
    (r'\bCinéforom\b|\bFond\.\s+romande\s+pour\s+le\s+cinéma\b', 'Cinéforom — Fond. romande pour le cinéma'),
    (r'\bFIFF\b|^Festival\s+International\s+du\s+film\s+de\s+Fribourg', 'FIFF — Festival International du Film de Fribourg'),
    (r'\b(?:Fond\.\s+du\s+)?Verbier\s+Festival\b', 'Verbier Festival'),
    (r'\bOrchestre\s+de\s+la\s+Suisse\s+Romande\b|\bOSR\b', 'OSR — Orchestre de la Suisse Romande'),
    (r'^Tertianum\s+', 'Tertianum (groupe d\'EMS — 4 résidences)'),
    (r'\bThéâtre\s+du\s+Jura\b', 'Théâtre du Jura'),
    (r'\bThéâtre\s+du\s+Jorat\b', 'Théâtre du Jorat'),
    (r'\b(?:Fond\.\s+(?:Pierre\s+)?)?Gianadda\b', 'Fond. Pierre Gianadda'),
    (r'\bPaléo\b', 'Paléo Festival Nyon'),
    (r'\bMontreux\s+Jazz\b|\bFestival\s+(?:de\s+Jazz\s+)?(?:de\s+)?Montreux\b', 'Montreux Jazz Festival'),
    (r'\bNIFFF\b', 'NIFFF — Neuchâtel Int. Fantastic Film Festival'),
    (r'\bBelluard\b', 'Belluard Bollwerk Festival'),
    (r'\bLa\s+Bâtie\b|\bBâtie[-\s]+Festival\b', 'La Bâtie — Festival de Genève'),
    (r'\bCORODIS\b', 'CORODIS'),
    (r"\bFAJE\b|\bFond\.\s+pour\s+l['\u2019]?accueil\s+de\s+jour\s+des\s+enfants\b", "FAJE — Fond. pour l'accueil de jour des enfants"),
    (r"\bLanterne\s+[Mm]agique\b", 'La Lanterne Magique'),
    (r"\b(?:Fond\.\s+de\s+l['\u2019]?)?Hermitage\b", "Fond. de l'Hermitage"),
    (r"\bPlateforme\s+10\b", 'Plateforme 10'),
    (r"\bFond\.\s+Partage\b", 'Fond. Partage'),
    (r"\bVaud\s+Promotion\b", 'Assoc. Vaud Promotion'),
    (r"\bSport-?Toto\b", 'Sport-Toto'),
    (r"\b(?:Fond\.\s+de\s+l['\u2019]?)?Aide\s+Sportive\b", "Fond. de l'Aide Sportive Suisse"),
]
COMPILED = [(re.compile(p, re.IGNORECASE), canon) for p, canon in ALIASES]


def get_alias(name):
    if not name: return None
    for pat, canon in COMPILED:
        if pat.search(name):
            return canon
    return None


def consolidate_entries(entries):
    """Regroupe les entries par alias canonique."""
    # Group by alias key (or 'NO_ALIAS' if none)
    groups = defaultdict(lambda: {'entries': [], 'total': 0, 'count': 0, 'cantons': set()})
    
    for e in entries:
        alias = get_alias(e.get('nom', ''))
        if alias:
            g = groups[alias]
            g['entries'].append(e)
            g['total'] += e.get('montant_CHF', 0)
            g['count'] += 1
            if e.get('canton'): g['cantons'].add(e['canton'])
        else:
            # Garder l'entry telle quelle (clé unique)
            key = f"NO_ALIAS::{e.get('nom', '')}"
            groups[key]['entries'].append(e)
            groups[key]['total'] += e.get('montant_CHF', 0)
            groups[key]['count'] += 1
            if e.get('canton'): groups[key]['cantons'].add(e['canton'])
    
    # Transformer en liste flat : si alias → 1 ligne consolidée, sinon → entry original
    out = []
    for key, g in groups.items():
        if key.startswith('NO_ALIAS::'):
            out.extend(g['entries'])  # entries individuelles
        else:
            # Une ligne consolidée
            first = g['entries'][0]
            out.append({
                'nom': key,  # nom canonique
                'montant_CHF': g['total'],
                'canton': '+'.join(sorted(g['cantons'])) if len(g['cantons']) > 1 else (first.get('canton') or ''),
                'ville': first.get('ville', ''),
                'secteur': first.get('secteur', ''),
                'description': f"Consolidation de {g['count']} attributions : " + ', '.join(set(e['nom'] for e in g['entries']))[:200],
                '_consolidated': True,
                '_count': g['count'],
            })
    return out


def process_file(path):
    d = json.load(open(path))
    if 'categories' not in d: return False
    changed = False
    for cat in d['categories']:
        all_e = cat.get('all_entries', [])
        samples = cat.get('samples', [])
        # Consolidate
        new_all = consolidate_entries(all_e)
        new_all.sort(key=lambda x: -x.get('montant_CHF', 0))
        # Refresh count to match unique alias+individuals
        # NOTE: keep count as the number of original attributions
        # Update samples = top 5
        new_samples = new_all[:5]
        cat['all_entries'] = new_all
        cat['samples'] = new_samples
        changed = True
    if changed:
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2))
    return changed


# Process all classification files
YEARS = ['2021', '2022', '2023', '2024', '2025']
SECTORS = ['culture', 'sport', 'social', 'jeunesse', 'sante', 'environnement', 'patrimoine', 'formation', 'promotion']
n = 0
for sec in SECTORS:
    # Default (2025)
    p = DATA / f'{sec}_classification.json'
    if p.exists() and process_file(p):
        n += 1
    # Years
    for y in YEARS:
        p = DATA / f'{sec}_classification_{y}.json'
        if p.exists() and process_file(p):
            n += 1
print(f"  ✓ {n} fichiers de classification consolidés (Cinéforom, FIFF, TDR, etc.)")

# Vérification finale : culture default
d = json.load(open(DATA / 'culture_classification.json'))
cinema_cat = next((c for c in d['categories'] if c['name'] == 'Cinéma / Audiovisuel'), None)
if cinema_cat:
    print(f"\n  Top 5 Cinéma 2025 (consolidé) :")
    for s in cinema_cat.get('samples', [])[:5]:
        mark = '⊕' if s.get('_consolidated') else ' '
        print(f"    {mark} {s['nom'][:55]:<55} {s['montant_CHF']/1e6:>5.2f}M ({s.get('_count', 1)}×)")
