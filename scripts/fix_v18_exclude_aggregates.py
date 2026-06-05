#!/usr/bin/env python3
"""fix_v18_exclude_aggregates.py — Exclure les entries qui sont en fait
des lignes de RÉCAP / TOTAUX du BRB et pas de vraies attributions.

Détection : entries dont le nom contient "Associations, institutions et fondations
bénéficiaires" qui sont en réalité des en-têtes de section / récaps.
"""
import json
from pathlib import Path

DATA = Path('/home/claude/audit3/Loro-main/docs/data')

# Patterns à exclure (vraies récap de fin de section)
EXCLUDE_NAME_PATTERNS = [
    "Associations, institutions et fondations bénéficiaires des contributions de la Loterie Romande Taxes prélevées par l",
    "Associations, institutions et fondations bénéficiaires des contributions de la Loterie Romande Contributions réserve",
    # NB: garder "Développement de la communication de l'Association Rhizome..." car c'est une vraie attribution
]


def main():
    total_excluded_amount = 0
    total_excluded_count = 0
    for y in ['2021', '2022', '2023', '2024', '2025']:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p))
        
        original_count = len(d['entries'])
        original_total = sum(e['montant_CHF'] for e in d['entries'])
        
        new_entries = []
        excluded = []
        for e in d['entries']:
            nom = e['nom'] or ''
            should_exclude = False
            for pat in EXCLUDE_NAME_PATTERNS:
                if nom.startswith(pat):
                    should_exclude = True
                    break
            # Aussi exclure les entries avec un seul mot "cantonales vaudoises" sans Assoc.
            if nom.strip() == 'cantonales vaudoises':
                should_exclude = True
            if should_exclude:
                excluded.append(e)
                total_excluded_amount += e['montant_CHF']
                total_excluded_count += 1
            else:
                new_entries.append(e)
        
        if len(excluded):
            d['entries'] = new_entries
            d['_meta'].setdefault('fixes', {})['v18_aggregates'] = {'count': len(excluded), 'total_chf': sum(e['montant_CHF'] for e in excluded)}
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
            new_total = sum(e['montant_CHF'] for e in new_entries)
            print(f"  {y}: {len(excluded)} agrégats exclus ({(original_total-new_total)/1e6:.2f}M retiré) — Total BRB {y} : {original_total/1e6:.1f}M → {new_total/1e6:.1f}M")
            for e in excluded:
                print(f"      - {e['nom'][:60]}... (canton={e['canton']}, montant={e['montant_CHF']:,})")
        else:
            print(f"  {y}: 0 agrégats")
    print(f"\n  TOTAL : {total_excluded_count} entries-récap retirées, {total_excluded_amount/1e6:.2f}M de double-comptage corrigé")


if __name__ == '__main__':
    main()
