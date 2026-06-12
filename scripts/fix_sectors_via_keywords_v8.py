#!/usr/bin/env python3
"""
fix_sectors_via_keywords_v8.py — audit transverse fin Passe 2
================================================================
Corrections trouvées en regardant les catch-all des 4 années (2022-2025).
Beaucoup d'entries mal classées au niveau du SECTEUR officiel.
"""
import json, re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'

RULES = [
    # ─── CULTURE (entries actuellement social/sante/jeunesse/promotion)
    (r"\bPôle\s+Musique\s+Sion\b", 'Culture'),  # 3.5M social 2022 → musique
    (r"\bKunsthalle\s+Friart\b", 'Culture'),
    (r"\bFond\.\s+Barnabé\b", 'Culture'),  # théâtre Servion
    (r"\bBiblioFR\b|\bbibliothèques?\s+fribourgeoises?\b", 'Culture'),
    (r"\bCrans-Montana\s+Classics\b", 'Culture'),
    (r"\bArc\s+en\s+Scène\b", 'Culture'),  # centre arts vivants NE
    (r"\bCentre\s+culturel\s+ABC\b", 'Culture'),
    (r"\bEX-pression\b|\bEx-pression\b", 'Culture'),
    
    # ─── CONSERVATION DU PATRIMOINE (musées en social/patrimoine étiqueté trop large)
    (r"\bFond\.\s+Martin\s+Bodmer\b", 'Conservation du patrimoine'),
    (r"\bFond\.\s+Opale\b", 'Conservation du patrimoine'),
    (r"\bFond\.\s+Pierre\s+Gianadda\b", 'Conservation du patrimoine'),
    (r"\bFond\.\s+Maurice\s+Favre\b", 'Conservation du patrimoine'),
    (r"\bMusée\s+Bodmer\b|\bBibliothèque\s+Bodmer\b", 'Conservation du patrimoine'),
    (r"\bFond\.\s+La\s+Tour\s+de\s+Choully\b", 'Conservation du patrimoine'),
    (r"\bVallée\s+des\s+dinosaures\b", 'Conservation du patrimoine'),  # paléontologie JU
    
    # ─── ENVIRONNEMENT (Papiliorama → centre faune & biodiversité, pas culturel)
    (r"\bPapiliorama\b", 'Environnement'),
    
    # ─── FORMATION ET RECHERCHE (écoles, recherche scientifique mal classées)
    (r"\bInstitut\s+de\s+Hautes\s+Études\s+Internationales\b|\bIHEID\b", 'Formation et recherche'),
    (r"\bDind\s+Cottier\b", 'Formation et recherche'),  # recherche peau
    (r"\bEuroVacc\b", 'Formation et recherche'),  # vaccin recherche
    (r"\bSwiss\s+Biobanking\s+Platform\b", 'Formation et recherche'),
    (r"\bFond\.\s+EspeRare\b", 'Formation et recherche'),  # maladies rares recherche
    (r"\bécole\s+Rudolf\s+Steiner\b", 'Formation et recherche'),
    (r"\bInstallateurs?\s+en\s+chauffage\b|\bApprentissage\s+du\s+chauffage\b", 'Formation et recherche'),
    
    # ─── SPORT (mal classés)
    (r"\bJura\s+Bike\s+Park\b", 'Sport'),
    (r"\bPro\s+Junior\s+(?:Fribourg|Vaud|Valais|Genève)\b", 'Sport'),
    
    # ─── ACTION SOCIALE (Le CARÉ : centre aide réfugiés/migrants GE)
    (r"\ble\s+C\.A\.R\.É\b|\bC\.A\.R\.É\b", 'Action sociale et personnes âgées'),
    (r"\bHome\s+Saint\s+Pierre\s+Petershöfli\b|\bSaint\s+Pierre\s+Petershöfli\b",
     'Action sociale et personnes âgées'),
    (r"\bAssoc\.\s+SemoNord\b|\bSEMO\b", 'Action sociale et personnes âgées'),
    
    # ─── PROMOTION (musées spécifiques en promotion = OK, mais Tour Grévin = promotion)
    (r"\bBy\s+Grevin\s+SA\b|\bGrevin\b", 'Promotion, tourisme et développement'),
]


def find_override(entry):
    text = (entry.get('nom') or '') + ' ' + (entry.get('description') or '')
    for pattern, sector in RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return sector
    return None


def main():
    total = 0
    by_year = {}
    for y in ['2021', '2022', '2023', '2024', '2025']:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p, encoding='utf-8'))
        log = []
        for e in d['entries']:
            t = find_override(e)
            if t and t != e['secteur']:
                log.append((e['secteur'], t, e['montant_CHF'], e['nom'][:50]))
                e['secteur'] = t
        d['_meta']['sector_overrides_v8'] = {'count': len(log), 'date': '2026-06-04'}
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        by_year[y] = log
        total += len(log)
    
    # Stats par année
    for y, log in by_year.items():
        from collections import Counter
        changes = Counter(f"{a} → {b}" for a, b, c, n in log)
        print(f"\n─── BRB {y} ── {len(log)} overrides ({sum(c for _, _, c, _ in log):,} CHF)")
        for c, n in changes.most_common(8):
            print(f"  {n:>3d} × {c[:65]}")
    print(f"\nTotal: {total}")


if __name__ == '__main__':
    main()
