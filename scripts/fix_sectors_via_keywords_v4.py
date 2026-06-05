#!/usr/bin/env python3
"""
fix_sectors_via_keywords_v4.py
================================
Final-pass corrections for 2024 catch-all entries.
"""
import json, re
from pathlib import Path

DATA = Path('/home/claude/audit3/Loro-main/docs/data')

OVERRIDE_RULES_V4 = [
    # Culture (théâtres et orchestres encore mal classés)
    (r"\bTKM\b|\bThéâtre\s+Kléber[\s-]Méleau\b", 'Culture'),
    (r"\bFond\.\s+pour\s+le\s+Théâtre\s+du\s+Jura\b", 'Culture'),
    (r"\bSinfonietta\s+de\s+Lausanne\b", 'Culture'),
    (r"\bFond\.\s+OSR\b|\bOrchestre\s+de\s+la\s+Suisse\s+Romande\b", 'Culture'),
    (r"\bPoésie\s+en\s+Arrosoir\b", 'Culture'),
    (r"\bRFI\b.*Folklore|\bRencontres\s+Internationales\s+de\s+Folklore\b", 'Culture'),
    (r"\bFolklore\s+international\b", 'Culture'),
    (r"\bAssoc\.\s+(?:du\s+)?Théâtre\b", 'Culture'),
    
    # Formation et recherche
    (r"\bBIBEL\+ORIENT\b|\bBIBEL\s+und\s+ORIENT\b", 'Formation et recherche'),
    (r"\bUniversität\s+Fribourg\b|\bUniversität\s+Freiburg\b", 'Formation et recherche'),
    
    # Patrimoine
    (r"\bSauvetage\s+de\s+la\s+Belotte[\s-]Bellerive\b", 'Conservation du patrimoine'),
    
    # Promotion (événements / tourisme)
    (r"\bGeneva\s+Trophy\s+Promotion\b", 'Promotion, tourisme et développement'),
    
    # Sport (clubs avec terme spécifique)
    (r"\bAssoc\.\s+Cantonale\s+Genevoise\s*$", 'Sport'),  # cas générique
]


def find_override(entry):
    text = (entry.get('nom') or '') + ' ' + (entry.get('description') or '')
    for pattern, sector in OVERRIDE_RULES_V4:
        if re.search(pattern, text, re.IGNORECASE):
            return sector
    return None


def main():
    total = 0
    for y in ['2021', '2022', '2023', '2024', '2025']:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p))
        n = 0
        for e in d['entries']:
            t = find_override(e)
            if t and t != e['secteur']:
                e['secteur'] = t
                n += 1
        if n:
            d['_meta']['sector_overrides_v4'] = {'count': n, 'date': '2026-06-04'}
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
        print(f"  brb{y}: {n} overrides v4")
        total += n
    
    # Cleanup "Va la is" et autres fragments résiduels
    print(f"\n  Cleanup fragments orphelins (Va la is, etc.)")
    for y in ['2021', '2022', '2023', '2024', '2025']:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p))
        n_drop = 0
        new_entries = []
        for e in d['entries']:
            nom = e['nom'].strip()
            # Drop fragments like "Va la is", "et personnes âgées", trailing fragments
            if (nom in ('Va la is', 'Wallis', 'Wallis (allemand)',
                        'et personnes âgées', 'et développement', 'et éducation',
                        'Entités (activité générale)')
                or re.match(r'^[A-Za-z]{1,3}$', nom)):
                n_drop += 1
                continue
            new_entries.append(e)
        if n_drop:
            d['entries'] = new_entries
            d['_meta']['total_entries'] = len(new_entries)
            d['_meta']['total_chf'] = sum(e['montant_CHF'] for e in new_entries)
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
            print(f"    brb{y}: {n_drop} fragments orphelins droppés")
    
    print(f"\nTotal v4: {total}")


if __name__ == '__main__':
    main()
