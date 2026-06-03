#!/usr/bin/env python3
"""
============================================================
DEPRECATED — superseded by scripts/pipeline_brb.py (v13.8)

This script implements one stage of the BRB cleanup. As of
v13.8 (Pass 5 — C), all stages are consolidated into
pipeline_brb.py which is idempotent + auditable.

Kept here as historical reference. For new work:
    python scripts/pipeline_brb.py --input <path>
============================================================
"""
"""Clean up parser artifacts in brb2025_full.json.

Two systematic bugs detected:
1. Two consecutive PDF entries glued into one: nom contains "<name1> <amount1>.- <name2>"
   and montant_CHF holds amount2. We split into two clean entries.
2. Section totals (e.g. "Fonds mis à disposition du Conseil d'État") parsed as entries
   with huge montants. We tag these as section_total=True or remove them.
"""
import json, re, sys
from pathlib import Path

ROOT = Path('/home/claude/Loro-live/Loro-main/docs/data')
INPUT = ROOT / 'brb2025_full.json'
BACKUP = ROOT / 'brb2025_full.backup.json'

# Backup original
if not BACKUP.exists():
    import shutil
    shutil.copy(INPUT, BACKUP)

with open(INPUT) as f:
    d = json.load(f)

entries = d['entries']
n_orig = len(entries)
print(f"Input: {n_orig} entries, total {sum(e.get('montant_CHF',0) for e in entries):,} CHF")

# Regex to detect a "<name1> <amount>.- <name2>" pattern in nom
# Amount: 1-3 digits, optional thousand separator ' or ', then groups of 3 digits, .- or .
GLUE_RE = re.compile(
    r"^(?P<name1>.+?)\s+"
    r"(?P<amt>\d{1,3}(?:[''']\d{3})*(?:\.\-|\.))\s+"
    r"(?P<name2>.+)$"
)

# Patterns identifying SECTION TOTALS (not real beneficiaries)
SECTION_TOTAL_KEYWORDS = [
    "Fonds mis à disposition du Conseil",
    "Fonds mis à disposition du CE",
    "Total pour les établissements",
    "soutiens annuels et divers",
]

def parse_amount(s):
    """'2'500.-' or '2,500.-' → 2500"""
    s = s.replace("'", "").replace("'", "").replace("'", "").replace(",", "")
    s = s.rstrip(".-")
    s = s.rstrip(".")
    try:
        return int(s)
    except ValueError:
        return None

# Pass 1 : identify section totals and split glued entries
new_entries = []
n_split = 0
n_section_total = 0
n_unchanged = 0

for e in entries:
    nom = e.get('nom') or ''

    # Detect "Fonds mis à disposition du Conseil d'État" + 10.5M = section total
    if any(kw in nom for kw in SECTION_TOTAL_KEYWORDS) and (e.get('montant_CHF', 0) > 500_000):
        # Drop these — they are aggregate totals, not individual beneficiaries
        n_section_total += 1
        # But check if there's a real entry glued in front
        m = GLUE_RE.match(nom)
        if m and parse_amount(m.group('amt')):
            # Recover the prefixed real entry
            amt1 = parse_amount(m.group('amt'))
            new_entries.append({
                **e,
                'nom': m.group('name1').strip().rstrip(','),
                'montant_CHF': amt1,
                'description': e.get('description'),
                'note_parser': 'extracted from glued-with-section-total entry',
            })
            n_split += 1
        continue  # drop the section-total part

    # Standard glued-entry pattern
    m = GLUE_RE.match(nom)
    if m and parse_amount(m.group('amt')):
        amt1 = parse_amount(m.group('amt'))
        name1 = m.group('name1').strip().rstrip(',').rstrip()
        name2 = m.group('name2').strip()
        # Heuristic: only split if both names look like real beneficiary names (start with capital, length > 5)
        if (len(name1) > 4 and len(name2) > 4 and
            name1[0].isalpha() and name2[0].isalpha()):
            # Two entries:
            entry1 = {
                **e,
                'nom': name1,
                'montant_CHF': amt1,
                'note_parser': 'split-from-glued',
            }
            entry2 = {
                **e,
                'nom': name2,
                # montant_CHF stays as the existing value (it was for entry2)
                'note_parser': 'split-from-glued',
            }
            new_entries.append(entry1)
            new_entries.append(entry2)
            n_split += 1
            continue

    n_unchanged += 1
    new_entries.append(e)

print(f"\nPass 1 result:")
print(f"  - Glued entries split (yielding 2 each): {n_split}")
print(f"  - Section totals dropped: {n_section_total}")
print(f"  - Entries unchanged: {n_unchanged}")
print(f"  - New total: {len(new_entries)} entries")
print(f"  - New sum: {sum(e.get('montant_CHF',0) for e in new_entries):,} CHF")

# Sanity check: verify Tremplin
trempl = [e for e in new_entries if 'remplin' in (e.get('nom') or '') and 'Martigny' in (e.get('nom') or '')]
print(f"\nTremplin Martigny after cleanup:")
for e in trempl:
    print(f"  [{e['canton']}] '{e['nom']}' = {e['montant_CHF']:,} CHF (was 10'500'000)")

# Update metadata
d['entries'] = new_entries
d['_meta'] = d.get('_meta', {})
d['_meta']['cleanup_v13_6'] = {
    'date': '2026-06-03',
    'glued_split': n_split,
    'section_totals_dropped': n_section_total,
    'note': 'Parser v4 produced some glued entries (2 PDF lines merged); cleaned up by detecting the embedded amount pattern and splitting.'
}

with open(INPUT, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)

print(f"\n✓ Written cleaned data to {INPUT}")
print(f"✓ Original backed up to {BACKUP}")
