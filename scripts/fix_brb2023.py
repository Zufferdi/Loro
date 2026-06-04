#!/usr/bin/env python3
"""
fix_brb2023.py — Post-parsing corrections for brb2023_full.json
================================================================

1. Assign secteur="Action sociale et personnes âgées" to the 31 entries
   at the start of the file that fell before the first detected section
   header (the PDF begins with Vaud Action sociale entries without an
   explicit header).

2. Fix corrupted ville="Section" entries (AVIVO Section de Lausanne etc.)
   that should be canton=VD.

3. Remove obvious parsing artifacts (e.g. "Figure" at 1 CHF).

Run AFTER parse_brb2023_v3.py + pipeline_brb.py.
"""
import json
from pathlib import Path

INPUT = Path('/home/claude/audit2/Loro-main/docs/data/brb2023_full.json')
BACKUP = Path('/home/claude/audit2/Loro-main/docs/data/brb2023_full.backup_pre_fix.json')


def main():
    d = json.load(open(INPUT))
    entries = d['entries']

    # Save backup
    BACKUP.write_text(json.dumps(d, ensure_ascii=False, indent=2))
    print(f"📦 Backup: {BACKUP.name}")

    n_sec_assigned = 0
    n_ville_fixed = 0
    n_dropped = 0
    new_entries = []

    for i, e in enumerate(entries):
        # 1. Drop obvious artifacts: nom == 'Figure' with montant <= 1
        if e['nom'].strip() == 'Figure' and e['montant_CHF'] <= 10:
            n_dropped += 1
            continue
        # Also drop other obvious artifacts (montant 0 ou 1 with very short nom)
        if e['montant_CHF'] <= 1 and len(e['nom']) < 8:
            n_dropped += 1
            continue

        # 2. Fix corrupted ville="Section" — should be VD (suburbs of Lausanne)
        if e['ville'] == 'Section':
            # "AVIVO Section de Lausanne", "AVIVO Section de Renens" → VD
            e['ville'] = None  # remove the bogus ville
            if e['canton'] != 'VD':
                e['canton'] = 'VD'
                n_ville_fixed += 1

        # 3. Fix Essertines-sur-Yverdon (real VD ville, was tagged SR)
        if e.get('ville') == 'Essertines-sur-Yverdon' and e['canton'] != 'VD':
            e['canton'] = 'VD'
            n_ville_fixed += 1

        # 4. Assign secteur to entries without one (all at start of file,
        # all belong to "Action sociale et personnes âgées" Vaud)
        if not e['secteur']:
            e['secteur'] = 'Action sociale et personnes âgées'
            n_sec_assigned += 1

        new_entries.append(e)

    d['entries'] = new_entries
    d['_meta']['total_entries'] = len(new_entries)
    d['_meta']['total_chf'] = sum(e['montant_CHF'] for e in new_entries)
    d['_meta']['post_parse_fixes'] = {
        'date': '2026-06-04',
        'sections_assigned': n_sec_assigned,
        'villes_fixed': n_ville_fixed,
        'artifacts_dropped': n_dropped,
        'note': "Assigned 'Action sociale et personnes âgées' to entries "
                "preceding the first section header (Vaud start-of-PDF); "
                "fixed corrupted 'Section' ville entries; dropped trivial artifacts.",
    }

    INPUT.write_text(json.dumps(d, ensure_ascii=False, indent=2))

    print(f"\n✅ Patched {INPUT.name}")
    print(f"   • {n_sec_assigned} entries assignées 'Action sociale et personnes âgées'")
    print(f"   • {n_ville_fixed} villes corrompues corrigées (VD)")
    print(f"   • {n_dropped} artefacts droppés")
    print(f"   • Final: {len(new_entries)} entries, {d['_meta']['total_chf']:,} CHF")


if __name__ == '__main__':
    main()
