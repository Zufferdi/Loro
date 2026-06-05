#!/usr/bin/env python3
"""rebuild_all_with_aliases.py — re-build cross + comparison + trajectories
   avec les aliases unifiés (TDR, Cinéforom, FIFF, OSR, etc.)
"""
import json
import re
import unicodedata
from collections import defaultdict, Counter
from pathlib import Path

DATA = Path('/home/claude/audit3/Loro-main/docs/data')
YEARS = ['2021', '2022', '2023', '2024', '2025']

# Same aliases as in build_unified_aggregations
ALIASES = {
    'tour_de_romandie': [
        r'\bFond\.?\s+(?:du\s+)?Tour\s+de\s+Romandie(?!\s+Féminin)',
        r'^Tour\s+de\s+Romandie(?!\s+Féminin)',
        r"\bArrivée\s+du\s+Tour\s+de\s+Romandie\b",
        r"\bétape\s+(?:de\s+|d['\u2019]?)?[A-ZÉ][a-zé]+\s+.*Tour\s+de\s+Romandie\b",
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
    'osr': [
        r'\bOrchestre\s+de\s+la\s+Suisse\s+Romande\b',
        r'\bOSR\b',
    ],
    'tertianum': [r'^Tertianum\s+'],
    'theatre_du_jura': [r'\bTh[éeè]âtre\s+du\s+Jura\b'],
    'theatre_du_jorat': [r'\bTh[éeè]âtre\s+du\s+Jorat\b'],
    'gianadda': [r'\b(?:Fond\.\s+(?:Pierre\s+)?)?Gianadda\b'],
    'paleo': [r'\bPaléo\b'],
    'montreux_jazz': [
        r'\bMontreux\s+Jazz\b',
        r"\bFestival\s+(?:de\s+Jazz\s+)?(?:de\s+)?Montreux\b",
    ],
    'belluard': [r'\bBelluard\b'],
    'la_batie': [r"\bLa\s+Bâtie\b|\bBâtie[-\s]+Festival\b"],
    'nifff': [r'\bNIFFF\b'],
    'delemont_bd': [r"\bDelémont['\u2019']?BD\b"],
    'sport_toto': [
        r'\bSport-?Toto\b',
        r'\bSt[eé]\.\s+du\s+Sport[-\s]+Toto\b',
    ],
    'fond_aide_sportive': [r"\bFond\.\s+de\s+l['\u2019]?[Aa]ide\s+[Ss]portive\b"],
    'corodis': [r'\bCORODIS\b'],
    'faje': [
        r"\bFAJE\b",
        r"\bFond\.\s+pour\s+l['\u2019]?accueil\s+de\s+jour\s+des\s+enfants\b",
    ],
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
    'tertianum': 'Tertianum (EMS — groupe)',
    'theatre_du_jura': 'Théâtre du Jura',
    'theatre_du_jorat': 'Théâtre du Jorat',
    'gianadda': 'Fond. Pierre Gianadda',
    'paleo': 'Paléo Festival Nyon',
    'montreux_jazz': 'Montreux Jazz Festival',
    'belluard': 'Belluard Bollwerk Festival',
    'la_batie': 'La Bâtie — Festival de Genève',
    'nifff': 'NIFFF — Neuchâtel Int. Fantastic Film Festival',
    'delemont_bd': "Delémont'BD",
    'sport_toto': 'Sport-Toto',
    'fond_aide_sportive': "Fond. de l'Aide Sportive Suisse",
    'corodis': 'CORODIS',
    'faje': "FAJE — Fond. pour l'accueil de jour des enfants",
    'plateforme_10': 'Plateforme 10',
    'lanterne_magique': 'La Lanterne Magique',
    'hermitage': 'Fond. de l\'Hermitage',
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


# Load all BRBs
all_entries = []
for y in YEARS:
    d = json.load(open(DATA / f'brb{y}_full.json'))
    for e in d['entries']:
        all_entries.append({**e, 'annee': int(y)})

# Group by canonical key
groups = defaultdict(lambda: {'entries': [], 'is_alias': False, 'key': None})
for e in all_entries:
    key_info = get_canonical_key(e['nom'])
    if not key_info: continue
    ktype, key = key_info
    groups[key]['entries'].append(e)
    if ktype == 'alias':
        groups[key]['is_alias'] = True
        groups[key]['key'] = key

# ============================================================
# REBUILD cross_2021_2025_top (inter-cantonaux)
# ============================================================
out_cross = []
for key, g in groups.items():
    cantons = set(e['canton'] for e in g['entries'] if e.get('canton'))
    if len(cantons) < 2: continue
    if g['is_alias']:
        nom = CANONICAL.get(g['key'], key)
    else:
        nom_counts = Counter(e['nom'] for e in g['entries'])
        nom = nom_counts.most_common(1)[0][0]
    secteurs = Counter(e['secteur'] for e in g['entries'] if e.get('secteur'))
    sec = secteurs.most_common(1)[0][0] if secteurs else None
    canton_principal = Counter(e['canton'] for e in g['entries']).most_common(1)[0][0]
    montant_total = sum(e['montant_CHF'] for e in g['entries'])
    montants_par_canton = defaultdict(int)
    for e in g['entries']:
        if e.get('canton'):
            montants_par_canton[e['canton']] += e['montant_CHF']
    montants_par_an = {f'montant_{y}_CHF': sum(e['montant_CHF'] for e in g['entries'] if e['annee'] == int(y)) for y in YEARS}
    years_active = sorted(set(e['annee'] for e in g['entries']))
    out_cross.append({
        'nom': nom, 'canton': canton_principal, 'secteur': sec,
        'cantons': sorted(cantons), 'nb_cantons': len(cantons),
        'nb_years_active': len(years_active),
        **montants_par_an,
        'montant_total_CHF': montant_total,
        'montants_par_canton': dict(montants_par_canton),
        'is_consolidated': g['is_alias'],
    })
out_cross.sort(key=lambda x: -x['montant_total_CHF'])
out_cross_top100 = out_cross[:100]

cross_result = {
    '_meta': {
        'description': 'Bénéficiaires inter-cantonaux (≥2 cantons) 2021-2025, consolidés via aliases',
        'years': YEARS,
        'total_inter_cantonaux': len(out_cross),
        'top100_cumul_CHF': sum(b['montant_total_CHF'] for b in out_cross_top100),
        'method': 'aliases TDR/Cinéforom/FIFF/etc. + fallback normalisation',
    },
    'beneficiaires': out_cross_top100,
}
open(DATA / 'cross_2021_2025_top.json', 'w').write(json.dumps(cross_result, ensure_ascii=False, indent=2))
print(f"  ✓ cross_2021_2025_top — {len(out_cross_top100)} inter-cantonaux (post-aliases)")

# ============================================================
# REBUILD trajectories_2021_2025 (toutes années)
# ============================================================
out_traj = []
for key, g in groups.items():
    montants_par_an = {y: sum(e['montant_CHF'] for e in g['entries'] if e['annee'] == int(y)) for y in YEARS}
    years_with_data = [y for y in YEARS if montants_par_an[y] > 0]
    total = sum(montants_par_an.values())
    if total < 100_000: continue  # threshold
    if g['is_alias']:
        nom = CANONICAL.get(g['key'], key)
    else:
        nom_counts = Counter(e['nom'] for e in g['entries'])
        nom = nom_counts.most_common(1)[0][0]
    
    # Trajectory classification
    last_3 = [montants_par_an[y] for y in YEARS[-3:]]
    nb_years = len(years_with_data)
    
    # Detect one-shots (only one year with significant amount)
    significant_years = [y for y in YEARS if montants_par_an[y] > 50_000]
    if len(significant_years) == 1:
        traj_cat = f'one_shot_{significant_years[0]}'
    else:
        amts = [montants_par_an[y] for y in YEARS]
        non_zero = [a for a in amts if a > 0]
        if len(non_zero) >= 3:
            first_half = sum(amts[:len(YEARS)//2 + 1])
            second_half = sum(amts[len(YEARS)//2 + 1:])
            if second_half > first_half * 1.4:
                traj_cat = 'growth'
            elif first_half > second_half * 1.4:
                traj_cat = 'decline'
            else:
                traj_cat = 'stable'
        else:
            traj_cat = 'sparse'
    
    secteurs = Counter(e['secteur'] for e in g['entries'] if e.get('secteur'))
    sec = secteurs.most_common(1)[0][0] if secteurs else None
    cantons = Counter(e['canton'] for e in g['entries'] if e.get('canton'))
    canton = cantons.most_common(1)[0][0] if cantons else None
    
    out_traj.append({
        'nom': nom, 'canton': canton, 'secteur': sec,
        'amount_2021': montants_par_an['2021'],
        'amount_2022': montants_par_an['2022'],
        'amount_2023': montants_par_an['2023'],
        'amount_2024': montants_par_an['2024'],
        'amount_2025': montants_par_an['2025'],
        'total': total,
        'nb_years_active': nb_years,
        'trajectory_cat': traj_cat,
        'delta_pct': None if not montants_par_an['2021'] else round((montants_par_an['2025'] - montants_par_an['2021']) / montants_par_an['2021'] * 100),
        'is_consolidated': g['is_alias'],
    })
out_traj.sort(key=lambda x: -x['total'])

# Stats
counts = Counter(t['trajectory_cat'] for t in out_traj)
count_5y = sum(1 for t in out_traj if t['nb_years_active'] == 5)
count_4y = sum(1 for t in out_traj if t['nb_years_active'] >= 4)

traj_result = {
    '_meta': {
        'description': 'Trajectoires 5 ans 2021-2025 par bénéficiaire, threshold ≥100k cumulé',
        'years': YEARS,
        'count_5year': count_5y,
        'count_4year': count_4y,
        'count_by_cat': dict(counts),
        'total_beneficiaires': len(out_traj),
    },
    'beneficiaires': out_traj[:300],
}
open(DATA / 'trajectories_2021_2025.json', 'w').write(json.dumps(traj_result, ensure_ascii=False, indent=2))
print(f"  ✓ trajectories_2021_2025 — {len(out_traj)} (5y: {count_5y}, 4y+: {count_4y})")
print(f"    Catégories: {dict(counts)}")

# Show top 5 trajectories
print(f"\n  Top 5 trajectoires :")
for i, t in enumerate(out_traj[:5], 1):
    print(f"   {i}. {t['nom'][:50]:<50} 5y total={t['total']/1e6:.2f}M ({t['trajectory_cat']})")
