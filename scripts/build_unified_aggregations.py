#!/usr/bin/env python3
"""build_unified_aggregations.py — re-build avec normalisation améliorée
   Mieux fusionner : 'Fond. du Tour de Romandie' + 'Fond. Tour de Romandie' + 'Tour de Romandie',
   'Cinéforom' / 'Fond. Cinéforom' / 'Fond. romande pour le cinéma - Cinéforom', etc.
"""
import json
import re
import unicodedata
import statistics
from collections import defaultdict, Counter
from pathlib import Path

DATA = Path('/home/claude/audit3/Loro-main/docs/data')
YEARS = ['2021', '2022', '2023', '2024', '2025']

# Aliases pour fusion explicite (clé canonique → patterns à matcher)
ALIASES = {
    'tour_de_romandie': [
        r'\bFond\.?\s+(?:du\s+)?Tour\s+de\s+Romandie\b',
        r'\bTour\s+de\s+Romandie\b(?!\s+Féminin)',  # exclut féminin de la fusion
        r'\bFond\.?\s+du\s+Tour\s+de\s+Romandie\s+Complément\b',
    ],
    'tour_de_romandie_feminin': [
        r'\bTour\s+de\s+Romandie\s+Féminin\b',
    ],
    'cineforom': [
        r'\bCinéforom\b',
        r'\bFond\.\s+romande\s+pour\s+le\s+cinéma\b',
        r"\bromande\s+pour\s+le\s+cinéma\s*-\s*Cinéforom\b",
    ],
    'fiff': [
        r'\bFIFF\b\s*[-—]?\s*Festival\s+International\s+du\s+Film\s+de\s+Fribourg',
        r'^FIFF\b',
        r"^Festival\s+International\s+du\s+Film\s+de\s+Fribourg\b",
        r"^Festival\s+International\s+du\s+film\s+de\s+Fribourg\b",
    ],
    'verbier_festival': [
        r'\bVerbier\s+Festival\b',
        r'\bFond\.\s+Verbier\s+Festival\b',
    ],
    'osr': [
        r'\bOrchestre\s+de\s+la\s+Suisse\s+Romande\b',
        r"\bFond\.\s+pour\s+l[\u2019']?Orchestre\s+de\s+la\s+Suisse\s+Romande\b",
        r'\bOSR\b',
    ],
    'tertianum': [
        r'^Tertianum\s+',
    ],
    'theatre_du_jura': [
        r'\bTh[éeè]âtre\s+du\s+Jura\b',
        r'\bFond\.\s+(?:pour\s+le\s+)?Th[éeè]âtre\s+du\s+Jura\b',
    ],
    'theatre_du_jorat': [
        r'\bTh[éeè]âtre\s+du\s+Jorat\b',
    ],
    'gianadda': [
        r'\bFond\.\s+(?:Pierre\s+)?Gianadda\b',
        r'\bGianadda\b',
    ],
    'paleo': [
        r'\bPaléo\b',
        r"\bFestival\s+Paléo\s+Nyon\b",
    ],
    'montreux_jazz': [
        r'\bMontreux\s+Jazz\b',
        r"\bFond\.\s+du\s+Festival\s+(?:de\s+Jazz\s+)?(?:de\s+)?Montreux\b",
    ],
    'paleo_festival': [
        r'\bPaléo\s+(?:Festival|Nyon)\b',
    ],
    'belluard': [
        r'\bBelluard\s+Bollwerk\b',
        r'\bBelluard\b',
    ],
    'la_batie': [
        r'\bLa\s+Bâtie\b',
        r'\bBâtie\s*-?\s*Festival\b',
    ],
    'nifff': [
        r'\bNIFFF\b',
        r'\bNeuchâtel\s+International\s+Fantastic\b',
    ],
    'delemont_bd': [
        r"\bDelémont['\u2019']?BD\b",
    ],
    'faje': [
        r"\bFAJE\b",
        r"\bFond\.\s+pour\s+l['\u2019]?accueil\s+de\s+jour\s+des\s+enfants\b",
    ],
    'lanterne_magique': [r"\bLanterne\s+[Mm]agique\b"],
    'hermitage': [r"\b(?:Fond\.\s+de\s+l['\u2019]?)?Hermitage\b"],
    'corodis': [r'\bCORODIS\b'],
    'plateforme_10': [r'\bPlateforme\s+10\b'],
    'fond_partage': [r'\bFond\.\s+Partage\b'],
    'vaud_promotion': [r'\bVaud\s+Promotion\b'],
    'papiliorama': [r'\bPapiliorama\b'],
    'fond_aide_sportive': [r"\bFond\.\s+de\s+l['\u2019]?[Aa]ide\s+[Ss]portive\b"],
    'sport_toto': [
        r'\bSport-?Toto\b',
        r'\bSt[eé]\.\s+du\s+Sport-Toto\b',
    ],
}

# Build pattern compilé
COMPILED_ALIASES = {k: [re.compile(p, re.IGNORECASE) for p in pats] for k, pats in ALIASES.items()}

CANONICAL_NAMES = {
    'tour_de_romandie': 'Tour de Romandie (Fondation)',
    'tour_de_romandie_feminin': 'Tour de Romandie Féminin',
    'cineforom': 'Cinéforom — Fond. romande pour le cinéma',
    'fiff': 'FIFF — Festival International du Film de Fribourg',
    'verbier_festival': 'Verbier Festival',
    'osr': 'OSR — Orchestre de la Suisse Romande',
    'tertianum': 'Tertianum (EMS, 4 résidences)',
    'theatre_du_jura': 'Théâtre du Jura',
    'theatre_du_jorat': 'Théâtre du Jorat',
    'gianadda': 'Fond. Pierre Gianadda',
    'paleo': 'Paléo Festival Nyon',
    'montreux_jazz': 'Montreux Jazz Festival',
    'paleo_festival': 'Paléo Festival',
    'belluard': 'Belluard Bollwerk',
    'la_batie': 'La Bâtie — Festival de Genève',
    'nifff': 'NIFFF — Neuchâtel International Fantastic Film Festival',
    'delemont_bd': "Delémont'BD",
    'faje': "FAJE — Fond. pour l'accueil de jour des enfants",
    'lanterne_magique': 'La Lanterne Magique',
    'hermitage': "Fond. de l'Hermitage",
    'corodis': 'CORODIS',
    'plateforme_10': 'Plateforme 10',
    'fond_partage': 'Fond. Partage',
    'vaud_promotion': 'Assoc. Vaud Promotion',
    'papiliorama': 'Fond. Papiliorama',
    'fond_aide_sportive': "Fond. de l'Aide Sportive Suisse",
    'sport_toto': 'Sport-Toto',
}


def normalize_default(s):
    """Normalisation fallback (pour entries sans alias)."""
    if not s: return ''
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'^(?:fond\.|fondation|assoc\.|association|sté|société|st\.|comité|comite)\s+', '', s)
    s = re.sub(r'^(?:du|de\s+la|de\s+l[\u2019\']?|des?|le|la|les?|l[\u2019\'])\s+', '', s)
    s = re.sub(r'\s*\([^)]*\)\s*', ' ', s)
    s = re.sub(r'[,;\-\.\u2019\']', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def get_canonical_key(name):
    """Si match un alias, retourne la clé canonique. Sinon, fallback normalisation."""
    if not name: return None
    for key, patterns in COMPILED_ALIASES.items():
        for pat in patterns:
            if pat.search(name):
                return ('alias', key)
    nn = normalize_default(name)
    return ('default', nn) if nn else None


# === BUILD CUMUL 2021-2025 ===
beneficiaires = defaultdict(lambda: {
    'noms_originaux': set(), 'cantons': set(), 'villes': set(), 'secteurs': set(),
    'attributions': [], 'total_par_an': defaultdict(int), 'count_par_an': defaultdict(int),
    'is_alias': False,
})

for year in YEARS:
    d = json.load(open(DATA / f'brb{year}_full.json'))
    for e in d['entries']:
        key_info = get_canonical_key(e['nom'])
        if not key_info: continue
        ktype, key = key_info
        b = beneficiaires[key]
        b['noms_originaux'].add(e['nom'])
        if e.get('canton'): b['cantons'].add(e['canton'])
        if e.get('ville'): b['villes'].add(e['ville'])
        if e.get('secteur'): b['secteurs'].add(e['secteur'])
        b['attributions'].append({
            'annee': int(year), 'nom': e['nom'], 'ville': e.get('ville'),
            'canton': e['canton'], 'secteur': e['secteur'],
            'description': (e.get('description') or '')[:120],
            'montant_CHF': e['montant_CHF'],
        })
        b['total_par_an'][year] += e['montant_CHF']
        b['count_par_an'][year] += 1
        if ktype == 'alias':
            b['is_alias'] = True

out = []
for key, b in beneficiaires.items():
    total = sum(b['total_par_an'].values())
    count_total = len(b['attributions'])
    if count_total < 2: continue
    if b['is_alias']:
        top_nom = CANONICAL_NAMES.get(key, key)
    else:
        nom_counts = Counter(a['nom'] for a in b['attributions'])
        top_nom = nom_counts.most_common(1)[0][0]
    years_active = sorted(b['total_par_an'].keys())
    sec_counts = Counter(a['secteur'] for a in b['attributions'] if a['secteur'])
    secteur = sec_counts.most_common(1)[0][0] if sec_counts else None
    out.append({
        'key': key if b['is_alias'] else str(key),
        'nom_canonique': top_nom,
        'noms_originaux': sorted(b['noms_originaux']),
        'cantons': sorted(b['cantons']),
        'villes': sorted(b['villes']) if b['villes'] else [],
        'secteurs': sorted(b['secteurs']), 'secteur_principal': secteur,
        'total_cumul': total, 'count_cumul': count_total,
        'years_active': years_active, 'nb_years_active': len(years_active),
        'totaux_par_an': {y: b['total_par_an'][y] for y in YEARS},
        'count_par_an': {y: b['count_par_an'][y] for y in YEARS},
        'attributions_detail': sorted(b['attributions'], key=lambda a: (a['annee'], -a['montant_CHF'])),
        'is_consolidated': b['is_alias'],
    })
out.sort(key=lambda x: -x['total_cumul'])
out_top = out[:200]

result = {
    '_meta': {
        'description': 'Bénéficiaires cumulés 2021-2025 avec consolidation TDR/Cinéforom/FIFF/OSR/etc.',
        'method': 'Aliases explicites pour grandes entités multi-noms + normalisation fallback',
        'sources': [f'brb{y}_full.json' for y in YEARS],
        'total_beneficiaires_distincts': len(out),
        'total_in_top200': sum(b['total_cumul'] for b in out_top),
        'top200_pct_of_5y': round(sum(b['total_cumul'] for b in out_top) / sum(b['total_cumul'] for b in out) * 100, 1),
        'years': YEARS,
        'aliases_count': len(ALIASES),
    },
    'beneficiaires': out_top,
}
open(DATA / 'beneficiaires_cumul_2021_2025.json', 'w').write(json.dumps(result, ensure_ascii=False, indent=2))
print(f"  ✓ beneficiaires_cumul_2021_2025 — {len(out_top)} top, dont {sum(1 for b in out_top if b['is_consolidated'])} consolidés via aliases")

# Show top 10 with consolidation info
print("\n  ─── Top 15 (post-consolidation) ───")
for i, b in enumerate(out_top[:15], 1):
    mark = '⊕' if b['is_consolidated'] else ' '
    print(f"   {i:>2}. {mark} {b['nom_canonique'][:55]:<55} {b['total_cumul']/1e6:>5.2f}M ({b['count_cumul']}× attrib)")
