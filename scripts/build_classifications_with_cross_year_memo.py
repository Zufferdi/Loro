#!/usr/bin/env python3
"""
build_classifications_with_cross_year_memo.py
==============================================

Builds all classification JSONs with TWO passes per classification:

  PASS 1 — Pattern matching on (nom + description), as before.
    Classifies entries into specific sub-categories or 'Autres'.

  Cross-year memo — Builds a dict {normalized_name → sub_category} from
    all entries CLASSIFIED in pass 1 across 2023/2024/2025.

  PASS 2 — Re-process 'Autres' entries: if the normalized name is in
    the memo, re-classify into the corresponding sub-category.

This catches beneficiaries that appear across years with name variants:
  - "Fond. du Théâtre du Jorat" (matches pattern 'théâtre')
  - "Théâtre du Jorat" (no 'fond' prefix)
  - "Fond. Jorat - Théâtre" (different word order)
  → All recognized as the same beneficiary, classified consistently.

Conservative rules:
  - Only re-classify 'Autres' entries (never override an existing sub-cat).
  - Require minimum normalized name length (6 chars).
  - When a normalized name maps to multiple sub-cats, use the most-frequent one
    (majority vote across years).
"""
import json
import re
import sys
import unicodedata
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path('/home/claude/audit2/Loro-main')
DATA = ROOT / 'docs' / 'data'
sys.path.insert(0, str(ROOT / 'scripts'))

YEARS = ['2023', '2024', '2025']
SUFFIX = {y: '' if y == '2025' else f'_{y}' for y in YEARS}


# ────────────────────────────────────────────────────────────────────────
# Import existing patterns from the build_* scripts
# ────────────────────────────────────────────────────────────────────────

from build_culture_classification import CULTURE_PATTERNS
from build_sport_classification import SPORT_PATTERNS
from build_social_classification import SOCIAL_PATTERNS

# build_sectors_classification has SECTORS dict with patterns per sector
from build_sectors_classification import SECTORS as SECTOR_PATTERNS_DICT


def normalize_name(s: str) -> str:
    """Normalize a beneficiary name for cross-year matching."""
    if not s: return ''
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'^(?:fond\.|fondation|assoc\.|association|sté|societe|société|stiftung|stift\.|verein)\s+',
               '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s*\([^)]*\)\s*', ' ', s)  # strip parens
    s = re.sub(r'[,;\-\.\!\?\:\u2019\u2018]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def classify_by_patterns(entry: dict, compiled_patterns: list) -> str | None:
    """First-match wins. Returns sub-category name or None."""
    text = (entry.get('nom') or '') + ' ' + (entry.get('description') or '')
    for name, pat in compiled_patterns:
        if pat.search(text):
            return name
    return None


def get_entries_for_classif(classif: str, year: str) -> list:
    """Get entries to classify for (classif, year). Filter by official secteur
    to get meaningful coverage percentages (an entry in Sport secteur isn't
    supposed to be classified by culture patterns)."""
    d = json.load(open(DATA / f'brb{year}_full.json'))
    entries = d['entries']
    
    SECTOR_NAMES = {
        'culture':       'Culture',
        'sports':        'Sport',
        'social':        'Action sociale et personnes âgées',
        'environnement': 'Environnement',
        'sante':         'Santé et handicap',
        'jeunesse':      'Jeunesse et éducation',
        'patrimoine':    'Conservation du patrimoine',
        'formation':     'Formation et recherche',
        'promotion':     'Promotion, tourisme et développement',
    }
    sector_name = SECTOR_NAMES.get(classif)
    if sector_name:
        return [e for e in entries if e.get('secteur') == sector_name]
    return entries


def get_patterns(classif: str) -> list:
    """Get compiled patterns for a classification."""
    raw = {
        'culture': CULTURE_PATTERNS,
        'sports': SPORT_PATTERNS,
        'social': SOCIAL_PATTERNS,
    }
    if classif in raw:
        return [(name, re.compile(p, re.IGNORECASE)) for name, p in raw[classif]]
    # Sectors
    SECTOR_NAMES = {
        'environnement': 'Environnement',
        'sante': 'Santé et handicap',
        'jeunesse': 'Jeunesse et éducation',
        'patrimoine': 'Conservation du patrimoine',
        'formation': 'Formation et recherche',
        'promotion': 'Promotion, tourisme et développement',
    }
    sec = SECTOR_NAMES.get(classif)
    if sec and sec in SECTOR_PATTERNS_DICT:
        patterns = SECTOR_PATTERNS_DICT[sec]['patterns']
        return [(name, re.compile(p, re.IGNORECASE)) for name, p in patterns]
    return []


CLASSIFS = ['culture', 'sports', 'social',
            'environnement', 'sante', 'jeunesse',
            'patrimoine', 'formation', 'promotion']


def build_classifications():
    """Main: run 2-pass classification for all classifs × years."""
    print("═" * 70)
    print(" CLASSIFICATIONS AVEC MEMO CROSS-YEAR")
    print("═" * 70)
    
    for classif in CLASSIFS:
        print(f"\n─── {classif.upper()} ───")
        patterns = get_patterns(classif)
        if not patterns:
            print(f"  ✗ no patterns found")
            continue
        
        # ─── PASS 1: classify with patterns ────────────────────────────
        # Collect per (year, entry_idx) → sub-category (or None for Autres)
        classifs_by_year = {}  # year → list of (entry, sub_cat)
        for y in YEARS:
            entries = get_entries_for_classif(classif, y)
            for_year = []
            for e in entries:
                sub_cat = classify_by_patterns(e, patterns)
                for_year.append((e, sub_cat))
            classifs_by_year[y] = for_year
        
        # ─── Build cross-year memo ─────────────────────────────────────
        name_votes = defaultdict(Counter)
        for y in YEARS:
            for entry, sub_cat in classifs_by_year[y]:
                if sub_cat is None: continue
                nom_norm = normalize_name(entry['nom'])
                if nom_norm and len(nom_norm) >= 6:
                    name_votes[nom_norm][sub_cat] += 1
        
        # Filter out memo entries that are too generic to be discriminating.
        # These are single common words / cantonal adjectives / common prefixes.
        GENERIC_TOKENS = {
            'neuchateloise', 'neuchatelois', 'vaudoise', 'vaudois',
            'fribourgeoise', 'fribourgeois', 'genevoise', 'genevois',
            'valaisanne', 'valaisan', 'jurassienne', 'jurassien',
            'romande', 'romand', 'suisse',
            'cantonale', 'cantonal', 'cantonales', 'cantonaux',
            'fond', 'assoc', 'association', 'fondation',
        }
        
        def is_generic(nom_norm: str) -> bool:
            """Reject memo entries that are too generic (single common word, etc.)"""
            tokens = nom_norm.split()
            # Must be ≥ 2 tokens to be a meaningful identifier
            if len(tokens) < 2:
                return True
            # If ALL tokens are generic adjectives, reject
            non_generic = [t for t in tokens if t not in GENERIC_TOKENS]
            if not non_generic:
                return True
            return False
        
        memo = {}
        for nom_norm, votes in name_votes.items():
            if is_generic(nom_norm):
                continue
            top = votes.most_common(2)
            # Accept if unambiguous (only one cat OR top dominates 2x)
            if len(top) == 1 or top[0][1] >= 2 * top[1][1]:
                memo[nom_norm] = top[0][0]
        
        # ─── PASS 2: re-classify None via memo (exact + substring) ─────
        # Pré-compute: memo entries discriminantes pour substring matching
        # Critères: ≥ 15 chars, ≥ 2 tokens (pour éviter "neuchateloise" tout seul)
        memo_substrings = []
        for nom_norm, sub_cat in memo.items():
            if len(nom_norm) >= 15 and len(nom_norm.split()) >= 2:
                memo_substrings.append((nom_norm, sub_cat))
        # Tri par longueur DESC pour matcher les plus spécifiques d'abord
        memo_substrings.sort(key=lambda x: -len(x[0])) 
        
        pass2_recovered = 0
        pass2_chf = 0
        pass2_via_substring = 0
        for y in YEARS:
            for i, (entry, sub_cat) in enumerate(classifs_by_year[y]):
                if sub_cat is not None:
                    continue
                nom_norm = normalize_name(entry['nom'])
                if not nom_norm or len(nom_norm) < 6:
                    continue
                # 1. Exact match
                target = memo.get(nom_norm)
                # 2. Substring match: memo name is a substring of entry name
                if not target:
                    for mn, mc in memo_substrings:
                        if mn in nom_norm or nom_norm in mn:
                            target = mc
                            pass2_via_substring += 1
                            break
                if target:
                    classifs_by_year[y][i] = (entry, target)
                    pass2_recovered += 1
                    pass2_chf += entry['montant_CHF']
        
        # ─── Write output JSONs ────────────────────────────────────────
        before_pct = {}
        after_pct = {}
        
        for y in YEARS:
            entries_with_cat = classifs_by_year[y]
            # Aggregate
            cats = defaultdict(lambda: {
                'count': 0, 'total_chf': 0, 'samples': [],
                'cantons': defaultdict(lambda: {'count': 0, 'total_chf': 0})
            })
            for entry, sub_cat in entries_with_cat:
                cat = sub_cat or 'Autres'
                b = cats[cat]
                amt = entry.get('montant_CHF', 0) or 0
                b['count'] += 1
                b['total_chf'] += amt
                c = entry.get('canton', '')
                b['cantons'][c]['count'] += 1
                b['cantons'][c]['total_chf'] += amt
                # Track samples (top 5 by amount)
                b['samples'].append({
                    'nom': entry.get('nom', ''),
                    'ville': entry.get('ville'),
                    'canton': c,
                    'montant_CHF': amt,
                })
            
            # Build category list
            cat_list = []
            for name, b in cats.items():
                cat_list.append({
                    'name': name,
                    'count': b['count'],
                    'total_chf': b['total_chf'],
                    'mean_chf': b['total_chf'] // b['count'] if b['count'] else 0,
                    'cantons': {c: dict(d) for c, d in b['cantons'].items()},
                    'samples': sorted(b['samples'], key=lambda s: -s['montant_CHF'])[:5],
                })
            cat_list.sort(key=lambda c: -c['total_chf'])
            
            # Meta
            total_entries = len(entries_with_cat)
            total_chf = sum(e['montant_CHF'] for e, _ in entries_with_cat)
            total_classified = sum(c['count'] for c in cat_list if c['name'] != 'Autres')
            total_classified_chf = sum(c['total_chf'] for c in cat_list if c['name'] != 'Autres')
            
            meta = {
                'classif': classif,
                'year': y,
                'source': f'brb{y}_full.json',
                'method': 'Pattern matching (PASS 1) + cross-year memo (PASS 2)',
                'date': '2026-06-04',
                'total_entries': total_entries,
                'total_chf': total_chf,
                'total_entries_classified': total_classified,
                'total_chf_classified': total_classified_chf,
                'pct_chf_classified': round(100 * total_classified_chf / max(1, total_chf), 1),
                'cross_year_recovered': pass2_recovered,
            }
            
            # For sectors, also add the sector-specific metadata
            SECTOR_NAMES = {
                'environnement': 'Environnement',
                'sante': 'Santé et handicap',
                'jeunesse': 'Jeunesse et éducation',
                'patrimoine': 'Conservation du patrimoine',
                'formation': 'Formation et recherche',
                'promotion': 'Promotion, tourisme et développement',
            }
            if classif in SECTOR_NAMES:
                meta['sector'] = SECTOR_NAMES[classif]
                meta['sector_slug'] = classif
                meta['total_entries_sector'] = total_entries
                meta['total_chf_sector'] = total_chf
                meta['pct_entries_classified'] = round(100 * total_classified / max(1, total_entries), 1)
            
            # Pick category key for backward compat
            if classif == 'sports':
                output = {'_meta': meta, 'sports': cat_list}
            elif classif == 'culture':
                output = {'_meta': meta, 'categories': cat_list}
            elif classif == 'social':
                output = {'_meta': meta, 'categories': cat_list}
            else:
                output = {'_meta': meta, 'categories': cat_list}
            
            # Compute before/after for display (load old if exists)
            old_p = DATA / f'{classif}_classification{SUFFIX[y]}.json'
            if old_p.exists():
                old_d = json.load(open(old_p))
                old_pct = old_d.get('_meta', {}).get('pct_chf_classified', 0)
                before_pct[y] = old_pct if isinstance(old_pct, (int, float)) else float(str(old_pct).replace('%', '').strip())
            after_pct[y] = meta['pct_chf_classified']
            
            old_p.write_text(json.dumps(output, ensure_ascii=False, indent=2))
        
        # Print summary
        print(f"  Memo cross-year: {len(memo)} noms  ({len(memo_substrings)} discriminants ≥10 chars)")
        print(f"  PASS 2 recovered: {pass2_recovered} entries / {pass2_chf:,} CHF  "
              f"(dont {pass2_via_substring} via substring)")
        for y in YEARS:
            b = before_pct.get(y, 0)
            a = after_pct.get(y, 0)
            arrow = "↑" if a > b else "="
            delta = f"(+{a-b:.1f})" if a > b else ""
            print(f"    {y}: {b}% → {a}% {arrow} {delta}")


if __name__ == '__main__':
    build_classifications()
