#!/usr/bin/env python3
"""
fix_sectors_via_keywords_v3.py
================================

3rd-pass sector overrides. Focused on 2024 fixes after manual inspection of
catch-all entries. Each rule targets a specific beneficiary that should clearly
belong to another sector.

This complements fix_sectors_via_keywords_v2.py with newly identified cases.
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'

OVERRIDE_RULES_V3 = [
    # ─── CULTURE (entries currently elsewhere) ─────────────────────────
    (r"\bFond\.\s+Plateforme\s+10\b", 'Culture'),                        # pôle muséal Lausanne
    (r"\bFond\.\s+du\s+Festival\s+de\s+la\s+Cité\b", 'Culture'),         # festival Lausanne
    (r"\bThéâtre\s+Le\s+Reflet\b", 'Culture'),                            # Vevey
    (r"\bArts\s+et\s+Spectacles\s+de\s+Vevey\b", 'Culture'),
    (r"\bFond\.\s+FIFDH\b", 'Culture'),                                  # festival droits humains
    (r"\bL'avant-scène\s+Opéra\b|\bL\u2019avant-scène\s+Opéra\b", 'Culture'),
    (r"\bmarionNEttes\b", 'Culture'),                                    # festival marionnettes
    (r"\bStandard\s+Deluxe\b", 'Culture'),                               # centre d'art Lausanne
    (r"\bMaison\s+du\s+dessin\s+de\s+presse\b", 'Culture'),
    (r"\bMaison\s+Tavel\b", 'Culture'),
    
    # ─── FORMATION et recherche ──────────────────────────────────────────
    (r"\bCité\s+universitaire\s+de\s+Genève\b", 'Formation et recherche'),  # logement étudiant
    (r"\bMaison\s+d['\u2019]?Albert\b", 'Formation et recherche'),
    (r"\bFond\.\s+pour\s+le\s+soutien\s+de\s+la\s+recherche\b", 'Formation et recherche'),
    (r"\bNeurocelliA\b", 'Formation et recherche'),
    (r"\bSwiss\s+Solar\s+Boat\b", 'Formation et recherche'),             # EPFL Solar Boat
    (r"\bdéveloppement\s+de\s+l['\u2019]?on(?:co|to)logie\b", 'Formation et recherche'),
    
    # ─── JEUNESSE (entries currently in Social) ─────────────────────────
    (r"\bFond\.\s+officielle\s+de\s+la\s+jeunesse\b", 'Jeunesse et éducation'),
    (r"\bFond\.\s+de\s+l['\u2019]?Enfance\s+et\s+de\s+la\s+Jeunesse\b", 'Jeunesse et éducation'),
    (r"\bYverdonnoise\s+pour\s+l['\u2019]?Accueil\s+de\s+l['\u2019]?Enfance\b|\bFYAE\b",
     'Jeunesse et éducation'),
    (r"\bAssoc\.\s+REPER\b", 'Jeunesse et éducation'),                   # prévention jeunesse FR
    
    # ─── SANTE (entries currently in Jeunesse) ──────────────────────────
    (r"\bFond\.\s+Transport\s+Handicap\b|\bTHV\b", 'Santé et handicap'),
    (r"\bfond['\u2019]?IMAD\b|\bIMAD\b", 'Santé et handicap'),
    (r"\bLe\s+Foyer.*aveugles\b|\baveugles\s+ou\s+malvoyants\b",
     'Santé et handicap'),
    
    # ─── ACTION SOCIALE (entries currently in Jeunesse) ────────────────
    (r"\bEspacefemmes\b|\bfrauenraum\b", 'Action sociale et personnes âgées'),
    (r"\bFond\.\s+Morija\b", 'Action sociale et personnes âgées'),       # ONG humanitaire
    
    # ─── SPORT (entries currently in Promotion/Patrimoine) ─────────────
    (r"\bAssoc\.\s+Cantonale\s+Genevoise\s+(?:Football|Tennis|Volleyball|Basketball|Athlétisme)\b",
     'Sport'),
    (r"\bAssoc\.\s+Régionale\s+Genève\s+(?:Tennis|Football|Volleyball)\b", 'Sport'),
    (r"\bSwiss\s+Volley\b", 'Sport'),
    (r"\bAssoc\.\s+Bike\s+Freeride\b", 'Sport'),
    (r"\bFIS\s+Ski\s+Alpin\b|\bChampionnats?\s+du\s+monde\s+(?:de\s+)?Ski\b",
     'Sport'),
    (r"\bAssoc\.\s+FIS\b", 'Sport'),
    
    # ─── PROMOTION (cabanes du CAS, infrastructures montagne) ──────────
    (r"\bSAC\s+Sektion\b", 'Promotion, tourisme et développement'),     # = Club Alpin Suisse
    (r"\bClub\s+Alpin\s+Suisse\s+CAS\b", 'Promotion, tourisme et développement'),
    (r"\bCabane\s+du?\s+Vélan\b|\bCabane\s+du?\s+Schönbiel\b|\bCabane\s+du?\s+Trient\b",
     'Promotion, tourisme et développement'),
    (r"\bAssoc\.\s+Stand['\u2019]?été\b", 'Promotion, tourisme et développement'),
    
    # ─── ENVIRONNEMENT (centres de soins faune) ────────────────────────
    (r"\bErminea\b", 'Environnement'),                                   # centre faune VD
    (r"\bSPA\s+(?:de\s+|du\s+)?(?:Valais|Vaud|Genève|Fribourg|Neuchâtel|Jura)\b",
     'Environnement'),
    (r"\bLa\s+Vaux-Lierre\b|\bGarenne\b", 'Environnement'),              # refuges animaux VD
    
    # ─── ACTION SOCIALE (Switzerland for UNHCR) ────────────────────────
    (r"\bSwitzerland\s+for\s+UNHCR\b", 'Action sociale et personnes âgées'),  # déjà v2 mais re-affirmé
]


def find_override_sector(entry: dict) -> str | None:
    nom = entry.get('nom') or ''
    desc = entry.get('description') or ''
    text = nom + ' ' + desc
    for pattern, sector in OVERRIDE_RULES_V3:
        if re.search(pattern, text, re.IGNORECASE):
            return sector
    return None


def main():
    total_overrides = 0
    for y in ['2021', '2022', '2023', '2024', '2025']:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p, encoding='utf-8'))
        overrides_log = []
        for e in d['entries']:
            target = find_override_sector(e)
            if target and target != e['secteur']:
                overrides_log.append({
                    'old': e['secteur'], 'new': target,
                    'nom': e['nom'][:60], 'chf': e['montant_CHF'],
                })
                e['secteur'] = target
        d['_meta']['sector_overrides_v3'] = {
            'count': len(overrides_log), 'date': '2026-06-04',
        }
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        
        from collections import Counter
        changes = Counter(f"{op['old']} → {op['new']}" for op in overrides_log)
        print(f"─── BRB {y} ── {len(overrides_log)} overrides ({sum(op['chf'] for op in overrides_log):,} CHF)")
        for c, n in changes.most_common(8):
            print(f"  {n:>3d} × {c}")
        total_overrides += len(overrides_log)
    print(f"\nTotal: {total_overrides}")


if __name__ == '__main__':
    main()
