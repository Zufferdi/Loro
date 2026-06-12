#!/usr/bin/env python3
"""
enrich_classifications_cross_year.py
======================================

Improve classification coverage by learning from entries classified in OTHER
years. Logic:

  1. For each classification (culture, sports, social, environnement, sante,
     jeunesse, patrimoine, formation, promotion):
     - Collect ALL entries currently classified into a non-'Autres' sub-category
       across 2023 / 2024 / 2025.
     - Build a mapping: normalized_name → sub-category (with confidence).

  2. Re-classify entries currently in 'Autres' by looking up their normalized
     name in the mapping.

  3. Output the improved classifications.

Key insight: many beneficiaries appear across years with slightly different
name variants. "Fond. du Théâtre du Jorat" might match a regex pattern
('théâtre') in 2025 but not in 2024 where it's written as "Fond. Jorat".
Cross-year learning catches this.

Conservative rules to avoid wrong assignments:
  - Use longest-common-prefix matching with a minimum length
  - Vote majority if same name was classified to different sub-cats across years
  - Only override 'Autres' (never override a real classification)
"""
import json
import re
import unicodedata
from pathlib import Path
from collections import defaultdict, Counter

DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'
YEARS = ['2023', '2024', '2025']
SUFFIX = {y: '' if y == '2025' else f'_{y}' for y in YEARS}

CLASSIFS = [
    'culture', 'sports', 'social',
    'environnement', 'sante', 'jeunesse',
    'patrimoine', 'formation', 'promotion',
]


def normalize_name(s: str) -> str:
    """Normalize a beneficiary name for cross-year matching."""
    if not s: return ''
    # Lowercase, strip diacritics
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    # Remove common prefixes
    s = re.sub(r'^(?:fond\.|fondation|assoc\.|association|sté|societe|société|stiftung|stift\.)\s+', '', s, flags=re.IGNORECASE)
    # Remove trailing parens content (e.g. "(OCL)")
    s = re.sub(r'\s*\([^)]*\)\s*', ' ', s)
    # Remove punctuation, collapse spaces
    s = re.sub(r'[,;\-\.\!\?\:]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def load_classification(classif_name: str, year: str):
    """Load a classification JSON file."""
    p = DATA / f'{classif_name}_classification{SUFFIX[year]}.json'
    if not p.exists():
        return None
    return json.load(open(p, encoding='utf-8'))


def get_categories(d: dict) -> list:
    """Get the categories list from a classification JSON (handles different keys)."""
    return (d.get('categories') or d.get('sports') or d.get('cultures')
            or d.get('socials') or [])


def get_category_key(d: dict) -> str:
    """Get the key under which categories are stored."""
    for k in ['categories', 'sports', 'cultures', 'socials']:
        if k in d: return k
    return 'categories'


def build_name_mapping(classif: str) -> dict:
    """Build a {normalized_name → sub_category} mapping from all years."""
    name_votes = defaultdict(Counter)  # name → {sub_cat: count}
    
    for y in YEARS:
        d = load_classification(classif, y)
        if not d: continue
        cats = get_categories(d)
        for cat in cats:
            sub_cat = cat['name']
            if sub_cat == 'Autres':
                continue
            for sample in cat.get('samples', []):
                nom_norm = normalize_name(sample['nom'])
                if nom_norm and len(nom_norm) >= 6:  # ignore very short names
                    name_votes[nom_norm][sub_cat] += 1
            for entry in cat.get('all_entries', []):
                nom_norm = normalize_name(entry['nom'])
                if nom_norm and len(nom_norm) >= 6:
                    name_votes[nom_norm][sub_cat] += 1
    
    # Resolve votes: pick the sub-cat with most votes, only if unambiguous
    mapping = {}
    for name_norm, votes in name_votes.items():
        if not votes: continue
        top = votes.most_common(2)
        if len(top) == 1 or top[0][1] > top[1][1]:
            mapping[name_norm] = top[0][0]
        # else: ambiguous, skip
    return mapping


def re_classify(classif: str, mapping: dict):
    """Re-classify 'Autres' entries using the cross-year mapping."""
    reclassified_count = 0
    moved_chf = 0
    
    for y in YEARS:
        d = load_classification(classif, y)
        if not d: continue
        cats = get_categories(d)
        autres_cat = next((c for c in cats if c['name'] == 'Autres'), None)
        if not autres_cat:
            continue
        
        # Identify entries to move from 'Autres' to specific cats
        # 'Autres' has all_entries (or samples if shorter)
        entries_to_move = []
        remaining_in_autres = []
        all_autres_entries = autres_cat.get('all_entries') or autres_cat.get('samples') or []
        
        for entry in all_autres_entries:
            nom_norm = normalize_name(entry['nom'])
            target_cat = mapping.get(nom_norm)
            if target_cat:
                entries_to_move.append((target_cat, entry))
            else:
                remaining_in_autres.append(entry)
        
        if not entries_to_move:
            continue
        
        # Group moves by target category
        moves_by_cat = defaultdict(list)
        for target, entry in entries_to_move:
            moves_by_cat[target].append(entry)
        
        # Apply moves
        for target_cat_name, entries in moves_by_cat.items():
            # Find or create the target category
            target = next((c for c in cats if c['name'] == target_cat_name), None)
            if not target:
                continue  # target cat doesn't exist in this year — skip
            # Add entries to target
            for e in entries:
                target['count'] = target.get('count', 0) + 1
                target['total_chf'] = target.get('total_chf', 0) + e['montant_CHF']
                # Add to samples (max 5 by amount)
                if 'samples' not in target:
                    target['samples'] = []
                target['samples'].append(e)
                target['samples'].sort(key=lambda s: -s['montant_CHF'])
                target['samples'] = target['samples'][:5]
                # Add to all_entries if it exists
                if 'all_entries' in target:
                    target['all_entries'].append(e)
                    target['all_entries'].sort(key=lambda s: -s['montant_CHF'])
                # Add canton info if present
                if 'cantons' in target:
                    c = e.get('canton', '')
                    if c not in target['cantons']:
                        target['cantons'][c] = {'count': 0, 'total_chf': 0}
                    target['cantons'][c]['count'] += 1
                    target['cantons'][c]['total_chf'] += e['montant_CHF']
                # Mean
                if target['count'] > 0:
                    target['mean_chf'] = target['total_chf'] // target['count']
                reclassified_count += 1
                moved_chf += e['montant_CHF']
        
        # Update 'Autres' with remaining entries
        autres_cat['count'] = len(remaining_in_autres)
        autres_cat['total_chf'] = sum(e['montant_CHF'] for e in remaining_in_autres)
        autres_cat['mean_chf'] = (autres_cat['total_chf'] // autres_cat['count']
                                   if autres_cat['count'] else 0)
        if 'all_entries' in autres_cat:
            autres_cat['all_entries'] = sorted(remaining_in_autres, key=lambda e: -e['montant_CHF'])
        autres_cat['samples'] = sorted(remaining_in_autres, key=lambda e: -e['montant_CHF'])[:5]
        # Recompute Autres cantons
        if 'cantons' in autres_cat:
            new_cantons = defaultdict(lambda: {'count': 0, 'total_chf': 0})
            for e in remaining_in_autres:
                c = e.get('canton', '')
                new_cantons[c]['count'] += 1
                new_cantons[c]['total_chf'] += e['montant_CHF']
            autres_cat['cantons'] = dict(new_cantons)
        
        # Sort cats by total_chf desc
        key = get_category_key(d)
        d[key] = sorted(cats, key=lambda c: -c.get('total_chf', 0))
        
        # Update meta (only the count of classified entries)
        meta = d.get('_meta', {})
        total_classified_count = sum(c['count'] for c in cats if c['name'] != 'Autres')
        total_classified_chf = sum(c['total_chf'] for c in cats if c['name'] != 'Autres')
        meta['total_entries_classified'] = total_classified_count
        meta['total_chf_classified'] = total_classified_chf
        if meta.get('total_chf_sector'):
            meta['pct_chf_classified'] = round(100 * total_classified_chf / meta['total_chf_sector'], 1)
        elif meta.get('total_chf'):
            meta['pct_chf_classified'] = round(100 * total_classified_chf / meta['total_chf'], 1)
        meta['cross_year_enrichment'] = {
            'date': '2026-06-04',
            'note': 'Re-classified entries from Autres using names already classified in other years',
        }
        
        # Save
        p = DATA / f'{classif}_classification{SUFFIX[y]}.json'
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    
    return reclassified_count, moved_chf


def main():
    print("═" * 70)
    print(" ENRICHISSEMENT CROSS-YEAR DES CLASSIFICATIONS")
    print("═" * 70)
    
    total_reclassified = 0
    total_chf_moved = 0
    
    for classif in CLASSIFS:
        print(f"\n─── {classif.upper()} ───")
        # Show before
        before = {}
        for y in YEARS:
            d = load_classification(classif, y)
            if d:
                m = d.get('_meta', {})
                before[y] = m.get('pct_chf_classified', 0)
        
        # Build mapping
        mapping = build_name_mapping(classif)
        print(f"  Mapping cross-year: {len(mapping)} noms uniques")
        
        # Re-classify
        n, chf = re_classify(classif, mapping)
        total_reclassified += n
        total_chf_moved += chf
        print(f"  Re-classifié: {n} entries ({chf:,} CHF)")
        
        # Show after
        for y in YEARS:
            d = load_classification(classif, y)
            if d:
                m = d.get('_meta', {})
                pct_after = m.get('pct_chf_classified', 0)
                arrow = "↑" if pct_after > before.get(y, 0) else "="
                print(f"     {y}: {before.get(y, 0)}% → {pct_after}%  {arrow}")
    
    print(f"\n{'═'*70}")
    print(f"  TOTAL: {total_reclassified} entries re-classifiées ({total_chf_moved:,} CHF)")
    print(f"{'═'*70}")


if __name__ == '__main__':
    main()
