#!/usr/bin/env python3
"""rebuild_top30_top20villes.py — recompute avec aliases (TDR, Cinéforom, FIFF, etc.)
   Pour chaque année 2021-2025 + global.
"""
import json
import re
import unicodedata
from collections import defaultdict, Counter
from pathlib import Path

DATA = Path('/home/claude/audit3/Loro-main/docs/data')
YEARS = ['2021', '2022', '2023', '2024', '2025']

# Aliases (extrait de rebuild_all_with_aliases.py)
ALIASES = {
    'tour_de_romandie': [
        r'\bFond\.?\s+(?:du\s+)?Tour\s+de\s+Romandie(?!\s+Féminin)',
        r'^Tour\s+de\s+Romandie(?!\s+Féminin)',
        r"\bArrivée\s+du\s+Tour\s+de\s+Romandie\b",
        r'\bComplément\s+GE\s+pour\s+TDR\b',
    ],
    'tour_de_romandie_feminin': [r'\bTour\s+de\s+Romandie\s+Féminin\b'],
    'cineforom': [
        r'\bCinéforom\b',
        r'\bFond\.\s+romande\s+pour\s+le\s+cinéma\b',
    ],
    'fiff': [
        r'\bFIFF\b',
        r"^Festival\s+International\s+du\s+[Ff]ilm\s+de\s+Fribourg\b",
    ],
    'verbier_festival': [r'\b(?:Fond\.\s+du\s+)?Verbier\s+Festival\b'],
    'osr': [r'\bOrchestre\s+de\s+la\s+Suisse\s+Romande\b', r'\bOSR\b'],
    'tertianum': [r'^Tertianum\s+'],
    'theatre_du_jura': [r'\bTh[éeè]âtre\s+du\s+Jura\b'],
    'theatre_du_jorat': [r'\bTh[éeè]âtre\s+du\s+Jorat\b'],
    'gianadda': [r'\b(?:Fond\.\s+(?:Pierre\s+)?)?Gianadda\b'],
    'paleo': [r'\bPaléo\b'],
    'montreux_jazz': [r'\bMontreux\s+Jazz\b', r"\bFestival\s+(?:de\s+Jazz\s+)?(?:de\s+)?Montreux\b"],
    'belluard': [r'\bBelluard\b'],
    'la_batie': [r"\bLa\s+Bâtie\b|\bBâtie[-\s]+Festival\b"],
    'nifff': [r'\bNIFFF\b'],
    'delemont_bd': [r"\bDelémont['\u2019']?BD\b"],
    'sport_toto': [r'\bSport-?Toto\b'],
    'fond_aide_sportive': [r"\bFond\.\s+de\s+l['\u2019]?[Aa]ide\s+[Ss]portive\b"],
    'corodis': [r'\bCORODIS\b'],
    'faje': [r"\bFAJE\b", r"\bFond\.\s+pour\s+l['\u2019]?accueil\s+de\s+jour\s+des\s+enfants\b"],
    'plateforme_10': [r"\bPlateforme\s+10\b"],
    'lanterne_magique': [r"\bLanterne\s+[Mm]agique\b"],
    'hermitage': [r"\b(?:Fond\.\s+de\s+l['\u2019]?)?Hermitage\b"],
    'fond_partage': [r"\bFond\.\s+Partage\b"],
    'vaud_promotion': [r"\bVaud\s+Promotion\b"],
    'papiliorama': [r"\bPapiliorama\b"],
    'opera_decentralise': [r"\bOpéra\s+décentralisé\b"],
    'vestiaire_social': [r"\bVestiaire\s+social\b"],
    'fond_ecrit': [r"\bFond\.\s+pour\s+l['\u2019]?Écrit\b"],
    'fond_art_dramatique': [r"\bFond\.\s+pour\s+l['\u2019]?art\s+dramatique\b"],
    'fond_off_jeunesse': [r"\bFond\.\s+[Oo]fficielle\s+de\s+la\s+jeunesse\b"],
    'equilibre_nuithonie': [r"\bEquilibre\s+et\s+Nuithonie\b|\bÉquilibre\s+et\s+Nuithonie\b"],
}
COMPILED = {k: [re.compile(p, re.IGNORECASE) for p in pats] for k, pats in ALIASES.items()}

CANONICAL = {
    'tour_de_romandie': 'Tour de Romandie',
    'tour_de_romandie_feminin': 'Tour de Romandie Féminin',
    'cineforom': 'Cinéforom — Fond. romande pour le cinéma',
    'fiff': 'FIFF — Festival International du Film de Fribourg',
    'verbier_festival': 'Verbier Festival',
    'osr': 'OSR — Orchestre de la Suisse Romande',
    'tertianum': 'Tertianum (EMS)',
    'theatre_du_jura': 'Théâtre du Jura',
    'theatre_du_jorat': 'Théâtre du Jorat',
    'gianadda': 'Fond. Pierre Gianadda',
    'paleo': 'Paléo Festival Nyon',
    'montreux_jazz': 'Montreux Jazz Festival',
    'belluard': 'Belluard Bollwerk Festival',
    'la_batie': 'La Bâtie — Festival de Genève',
    'nifff': 'NIFFF Neuchâtel',
    'delemont_bd': "Delémont'BD",
    'sport_toto': 'Sport-Toto',
    'fond_aide_sportive': "Fond. de l'Aide Sportive Suisse",
    'corodis': 'CORODIS',
    'faje': "FAJE — Fond. accueil de jour enfants",
    'plateforme_10': 'Plateforme 10',
    'lanterne_magique': 'La Lanterne Magique',
    'hermitage': "Fond. de l'Hermitage",
    'fond_partage': 'Fond. Partage',
    'vaud_promotion': 'Assoc. Vaud Promotion',
    'papiliorama': 'Fond. Papiliorama',
    'opera_decentralise': 'Opéra décentralisé',
    'vestiaire_social': 'Vestiaire social',
    'fond_ecrit': "Fond. pour l'Écrit",
    'fond_art_dramatique': "Fond. pour l'art dramatique",
    'fond_off_jeunesse': 'Fond. Officielle de la jeunesse',
    'equilibre_nuithonie': 'Fond. Equilibre et Nuithonie',
}


def normalize_default(s):
    if not s: return ''
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'^(?:fond\.|fondation|assoc\.|association|sté|société|st\.|comité|comite)\s+', '', s)
    s = re.sub(r'^(?:du|de\s+la|de\s+l[\u2019\']?|des?|le|la|les?)\s+', '', s)
    s = re.sub(r'\s*\([^)]*\)\s*', ' ', s)
    s = re.sub(r'[,;\-\.\u2019\']', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def get_canonical_key(name):
    if not name: return None
    for key, patterns in COMPILED.items():
        for pat in patterns:
            if pat.search(name):
                return ('alias', key)
    nn = normalize_default(name)
    return ('default', nn) if nn else None


# === Pour chaque année (et global) ===
def build_top30_for_year(year_or_all):
    if year_or_all == 'all':
        years = YEARS
    else:
        years = [year_or_all]
    
    by_key = defaultdict(lambda: {'entries': [], 'is_alias': False, 'cantons': set(), 'secteurs': set(), 'villes': set()})
    
    for y in years:
        d = json.load(open(DATA / f'brb{y}_full.json'))
        for e in d['entries']:
            key_info = get_canonical_key(e['nom'])
            if not key_info: continue
            ktype, key = key_info
            b = by_key[key]
            b['entries'].append({**e, 'annee': int(y)})
            if e.get('canton'): b['cantons'].add(e['canton'])
            if e.get('secteur'): b['secteurs'].add(e['secteur'])
            if e.get('ville'): b['villes'].add(e['ville'])
            if ktype == 'alias':
                b['is_alias'] = True
                b['key'] = key
    
    rows = []
    for key, g in by_key.items():
        if g['is_alias']:
            nom = CANONICAL.get(g['key'], key)
        else:
            nom_counts = Counter(e['nom'] for e in g['entries'])
            nom = nom_counts.most_common(1)[0][0]
        total = sum(e['montant_CHF'] for e in g['entries'])
        count = len(g['entries'])
        if total < 50_000 and count < 2:
            continue
        secteur = Counter(e['secteur'] for e in g['entries'] if e.get('secteur')).most_common(1)
        rows.append({
            'nom': nom,
            'total_CHF': total,
            'count': count,
            'cantons': sorted(g['cantons']),
            'secteur_principal': secteur[0][0] if secteur else None,
            'is_consolidated': g['is_alias'],
        })
    rows.sort(key=lambda x: -x['total_CHF'])
    return rows[:30]


# Top villes par année (similaire mais grouper par 'ville')
def build_top20_villes_for_year(year_or_all):
    if year_or_all == 'all':
        years = YEARS
    else:
        years = [year_or_all]
    by_ville = defaultdict(lambda: {'total_CHF': 0, 'count': 0, 'cantons': set(), 'beneficiaires': set()})
    for y in years:
        d = json.load(open(DATA / f'brb{y}_full.json'))
        for e in d['entries']:
            ville = e.get('ville') or ''
            if not ville: continue
            v = by_ville[ville]
            v['total_CHF'] += e['montant_CHF']
            v['count'] += 1
            if e.get('canton'): v['cantons'].add(e['canton'])
            v['beneficiaires'].add(e['nom'])
    rows = []
    for ville, v in by_ville.items():
        if v['total_CHF'] < 500_000: continue
        rows.append({
            'ville': ville,
            'total_CHF': v['total_CHF'],
            'count': v['count'],
            'cantons': sorted(v['cantons']),
            'nb_beneficiaires': len(v['beneficiaires']),
        })
    rows.sort(key=lambda x: -x['total_CHF'])
    return rows[:20]


# Build per year
for y in YEARS:
    rows = build_top30_for_year(y)
    out = {
        '_meta': {'year': y, 'consolidated_with_aliases': True, 'aliases_count': sum(1 for r in rows if r['is_consolidated'])},
        'beneficiaires': rows,
    }
    open(DATA / f'top30_beneficiaires_{y}.json', 'w').write(json.dumps(out, ensure_ascii=False, indent=2))
    
    villes = build_top20_villes_for_year(y)
    out_v = {
        '_meta': {'year': y, 'count': len(villes)},
        'villes': villes,
    }
    open(DATA / f'top20_villes_{y}.json', 'w').write(json.dumps(out_v, ensure_ascii=False, indent=2))
    print(f"  ✓ {y}: top30 ({sum(1 for r in rows if r['is_consolidated'])} consolidés) + top20 villes")

# Default (= 2025)
import shutil
shutil.copy(DATA / 'top30_beneficiaires_2025.json', DATA / 'top30_beneficiaires.json')
shutil.copy(DATA / 'top20_villes_2025.json', DATA / 'top20_villes.json')
print(f"  ✓ Default (2025) copié")

# Show top 10 of 2025
print("\n  ─── Top 10 absolus 2025 (avec consolidation) ───")
top_2025 = json.load(open(DATA / 'top30_beneficiaires_2025.json'))['beneficiaires']
for i, b in enumerate(top_2025[:10], 1):
    mark = '⊕' if b['is_consolidated'] else ' '
    print(f"   {i:>2}. {mark} {b['nom'][:55]:<55} {b['total_CHF']/1e6:>5.2f}M ({b['count']}×)")
