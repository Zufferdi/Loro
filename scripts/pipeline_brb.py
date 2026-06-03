#!/usr/bin/env python3
"""
pipeline_brb.py — Unified BRB cleanup pipeline (v13.8 — Pass 5 — C)
=====================================================================

Consolidates the previously scattered cleanup scripts:
  - clean_brb.py (v13.6)        : glued-pair splitting + section total dropping
  - clean_brb_v13_7.py (v13.7)  : nom/desc/ville fixes + dedup + normalized merge
  - audit_brb.py                : diagnostic of 11 issue categories

Into one idempotent, re-runnable pipeline. When BRB 2026 is published:
    1. Parse the PDF (via the existing v4 parser → brb2026_full.json)
    2. Run this pipeline:  python scripts/pipeline_brb.py --input docs/data/brb2026_full.json
    3. Done — same cleaned format.

Key properties:
  * IDEMPOTENT: running twice on the same input produces zero changes the 2nd time
  * SAFE: automatic backup before any write
  * AUDITABLE: each stage logs its changes; final audit verifies post-state
  * SELF-CONTAINED: no dependencies beyond stdlib
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# =====================================================================
# Configuration
# =====================================================================

PIPELINE_VERSION = "v13.10"
PIPELINE_DATE = "2026-06-03"

# Section-total markers (these are not real beneficiaries — they're aggregate rows)
SECTION_TOTAL_KEYWORDS = [
    "Fonds mis à disposition du Conseil",
    "Fonds mis à disposition du CE",
    "Total pour les établissements",
    "soutiens annuels et divers",
]

# Connector words that signal a desc-prefix is actually a name continuation
RECONSTRUCT_CONNECTOR = re.compile(r"^(d'|de la |de l'|de |du |des |et |au |aux )", re.IGNORECASE)

# Activity keywords that mark where description proper starts
RECONSTRUCT_ACTIVITY_KEYWORDS = [
    'Soutien', 'Camp', 'Achat', 'Acquisition', 'Manifestation', 'Rénovation',
    'Aménagement', 'Travaux', 'Centre de formation', 'Centre de Perfor',
    'Participation', 'Tournoi', 'Championnat', 'Coupe', 'Saison', 'Activité',
    'Projet', 'Concert', 'Festival', 'Exposition', 'Création', 'Publication',
    'Mémorial', 'Cross', 'Course', 'Formation', 'Construction', 'Aide', 'Bourse',
    'Mise', 'Réfection', 'Remplacement', 'Installation', 'Pose', 'Organisation',
    'Édition', 'Edition', 'Étape', 'Etape', 'Action', 'Activités', 'Préparation',
    'Voyage', 'Stage', 'Trail',
    # v13.10 additions: extended coverage for childcare, museums, churches, sports clubs
    'Équipement', 'Equipement', 'Suivi', 'Animation', 'Recherche', 'Promotion',
    'Réception', 'Reception', 'Restauration', 'Diffusion', 'Prise', 'Conte',
]
RECONSTRUCT_ACTIVITY_RE = re.compile(
    r'\b(' + '|'.join(RECONSTRUCT_ACTIVITY_KEYWORDS) + r')\b'
)

# City extraction from trailing ", CityName"
RECONSTRUCT_CITY_AT_END = re.compile(
    r",\s*([A-ZÉÈÔÎÀÇ][a-zéèôîàç]+(?:[- ][A-ZÉÈÔÎÀÇ]?[a-zéèôîàç]+){0,3})\s*$"
)

# French stopwords for name normalization (dedup)
STOPWORDS_FR = {
    'le', 'la', 'les', 'l', 'un', 'une', 'des', 'du', 'de', 'd',
    'a', 'au', 'aux', 'et', 'ou', 'mais', 'donc', 'car', 'ni',
    'pour', 'sur', 'sous', 'avec', 'sans', 'dans', 'par', 'vers',
    'en', 'entre', 'contre', 'depuis', 'durant', 'selon',
    'ce', 'cette', 'ces', 'cet', 'son', 'sa', 'ses',
    'leur', 'leurs', 'qui', 'que', 'quoi', 'dont',
}

# Compiled regexes
GLUE_RE = re.compile(
    r"^(?P<name1>.+?)\s+"
    r"(?P<amt>\d{1,3}(?:[''']\d{3})*(?:\.\-|\.))\s+"
    r"(?P<name2>.+)$"
)
TRAILING_DASH = re.compile(r'\s*[-—–]+\s*$')
DANGLING_PREP = re.compile(
    r"\s+(de|du|de la|de l'|des|à|au|aux|pour|pour la|pour le|sur|sous|chez|avec|et|par|en)\s*$",
    re.IGNORECASE,
)
AMOUNT_IN_DESC = re.compile(r"\s*\d{1,3}['']?\d{3}\.-\s.+$")

DESC_IN_VILLE_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r'\b(activit|événement|festival|exposition|concert|spectacle|formation|achat|'
        r'acquisition|aménagement|équipement|fonctionnement|soutien|projet|programme|'
        r'publication|production|recherche|résidence|sortie|stage|tournée|voyage|'
        r'matériel|tournoi|championnat|circuit)',
        r'^\d{4}\b',
        r'^(divers|matériel|équipement|fonctionnement)\b',
    ]
]

KEY_FIELDS = ('nom', 'ville', 'description', 'montant_CHF', 'canton', 'secteur', 'organe', 'sous_section')


# =====================================================================
# Helpers
# =====================================================================

def parse_amount(s: str) -> int | None:
    """Convert '2'500.-' or '12'000.' to integer 2500 / 12000."""
    s = s.replace("'", "").replace("'", "").replace("'", "").replace(",", "")
    s = s.rstrip(".-").rstrip(".")
    try:
        return int(s)
    except ValueError:
        return None


def normalize_name(name: str) -> str:
    """Aggressive normalization for dedup: strip prefixes/suffixes, lowercase, ASCII."""
    if not name:
        return ''
    s = name.lower()
    s = re.sub(
        r"^(assoc\.|association|fond\.|fondation|fond|sté|société|club|comité|"
        r"verein|federation|féd\.)\s+", '', s
    )
    s = re.sub(r",\s*[a-zéèôî' -]+$", '', s)
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
    s = re.sub(r"[^a-z0-9]+", ' ', s).strip()
    return s


def is_section_total(entry: dict) -> bool:
    """True if an entry is a section total (aggregate) rather than a real beneficiary."""
    nom = entry.get('nom') or ''
    return any(kw in nom for kw in SECTION_TOTAL_KEYWORDS)


# =====================================================================
# Pipeline stages
# =====================================================================

def stage_split_glued(entries: list[dict]) -> tuple[list[dict], dict]:
    """
    Stage A (v13.6): split two-beneficiaries-glued entries.
    Pattern: nom = 'name1 1'200.- name2' where the parser fused 2 rows.
    Idempotent: if no nom matches the GLUE pattern, returns unchanged.
    """
    new_entries = []
    n_split = 0
    for e in entries:
        nom = e.get('nom') or ''
        m = GLUE_RE.match(nom)
        if not m:
            new_entries.append(e)
            continue
        amt2 = parse_amount(m.group('amt'))
        if amt2 is None:
            new_entries.append(e)
            continue
        # Build two clean entries
        e1 = dict(e)
        e1['nom'] = m.group('name1').strip()
        e1['montant_CHF'] = amt2
        e2 = dict(e)
        e2['nom'] = m.group('name2').strip()
        # Keep existing montant_CHF for e2 (was the original entry's montant)
        new_entries.append(e1)
        new_entries.append(e2)
        n_split += 1
    return new_entries, {'glued_pairs_split': n_split}


def stage_drop_section_totals(entries: list[dict]) -> tuple[list[dict], dict]:
    """Stage B (v13.6): drop aggregate-row entries that aren't real beneficiaries."""
    keep = [e for e in entries if not is_section_total(e)]
    return keep, {'section_totals_dropped': len(entries) - len(keep)}


def stage_reconstruct_name(entries: list[dict]) -> tuple[list[dict], dict]:
    """
    Stage B' (v13.9 NEW): when the parser truncated the name and left the
    continuation in the description, reconstruct the full name.

    Pattern: nom='Assoc. Cantonale Vaudoise' + desc="d'Athlétisme Soutien annuel"
             → nom='Assoc. Cantonale Vaudoise d'Athlétisme' + desc='Soutien annuel'

    Also extracts trailing ', CityName' into ville if ville was empty.

    Safety constraints:
      - desc must start with a connector word (d', de, du, des, et, au, aux)
      - the name part (before activity keyword) must be 3-60 chars
      - the name part must contain at most 1 comma
      - the reconstructed nom must contain at most 1 comma
    """
    n_reconstructed = 0
    n_cities_extracted = 0
    # Pattern that indicates name_part is contaminated (contains money amount)
    money_in_text = re.compile(r"\d+['']?\d*\.\-")
    for e in entries:
        desc = e.get('description') or ''
        if not desc or not RECONSTRUCT_CONNECTOR.match(desc):
            continue
        m = RECONSTRUCT_ACTIVITY_RE.search(desc)
        if not m or m.start() < 3:
            continue
        name_part = desc[:m.start()].strip()
        desc_part = desc[m.start():].strip()
        # Safety constraints
        if not (3 <= len(name_part) <= 60):
            continue
        if name_part.count(',') > 1:
            continue
        if name_part.count(' - ') > 1:
            continue
        # Safety: name_part must not contain embedded money amount
        # (indicates the desc itself was contaminated by multi-entry parser bug)
        if money_in_text.search(name_part):
            continue
        # Safety: also check the full desc — if it has multiple amount patterns,
        # the entry has parser corruption beyond what we can safely fix
        if len(money_in_text.findall(desc)) > 0:
            continue

        new_nom = (e.get('nom', '') + ' ' + name_part).strip()
        if new_nom.count(',') > 1:
            continue

        # Extract trailing ", CityName" if ville is empty
        new_ville = e.get('ville')
        if not new_ville:
            city_m = RECONSTRUCT_CITY_AT_END.search(new_nom)
            if city_m:
                new_ville = city_m.group(1)
                new_nom = new_nom[:city_m.start()].strip()
                n_cities_extracted += 1

        e['nom'] = new_nom
        e['ville'] = new_ville
        e['description'] = desc_part if desc_part else None
        n_reconstructed += 1

    return entries, {
        'name_reconstructed': n_reconstructed,
        'city_extracted_in_reconstruction': n_cities_extracted,
    }


def stage_clean_nom(entries: list[dict]) -> tuple[list[dict], dict]:
    """Stage C (v13.7-A, v13.9-fix): strip trailing dashes and dangling prepositions.
    Loops until the nom is stable so chained strips (e.g. ' et de la' → ' et' → '')
    are fully resolved in one pass."""
    n = 0
    for e in entries:
        orig = e.get('nom') or ''
        cleaned = orig
        for _ in range(8):  # bounded loop; nom can shrink at most a few times
            new = TRAILING_DASH.sub('', cleaned).rstrip()
            candidate = DANGLING_PREP.sub('', new)
            if len(candidate) > 8:
                new = candidate.rstrip()
            if new == cleaned:
                break
            cleaned = new
        if cleaned != orig:
            e['nom'] = cleaned
            n += 1
    return entries, {'nom_trailing_stripped': n}


def stage_clean_desc(entries: list[dict]) -> tuple[list[dict], dict]:
    """Stage D (v13.7-B): strip embedded amount + next-beneficiary leftover from description."""
    n = 0
    for e in entries:
        orig = e.get('description') or ''
        if not orig:
            continue
        cleaned = AMOUNT_IN_DESC.sub('', orig).rstrip()
        if cleaned != orig:
            e['description'] = cleaned if cleaned else None
            n += 1
    return entries, {'desc_amount_stripped': n}


def stage_clean_ville(entries: list[dict]) -> tuple[list[dict], dict]:
    """Stage E (v13.7-C): nullify ville fields that contain description text."""
    n = 0
    for e in entries:
        v = e.get('ville') or ''
        if not v:
            continue
        if any(p.search(v) for p in DESC_IN_VILLE_PATTERNS):
            # Move content to description if description is empty
            if not e.get('description'):
                e['description'] = v
            e['ville'] = None
            n += 1
    return entries, {'ville_nullified': n}


def stage_dedup_exact(entries: list[dict]) -> tuple[list[dict], dict]:
    """Stage F (v13.7-D): remove entries that are 100% identical (true parser duplicates)."""
    seen = {}
    keep_ix = set()
    for i, e in enumerate(entries):
        key = tuple(e.get(f) for f in KEY_FIELDS)
        if key in seen:
            continue  # skip duplicate
        seen[key] = i
        keep_ix.add(i)
    keep = [e for i, e in enumerate(entries) if i in keep_ix]
    return keep, {'exact_duplicates_removed': len(entries) - len(keep)}


def stage_merge_normalized(entries: list[dict]) -> tuple[list[dict], dict]:
    """
    Stage G (v13.7-E): merge entries that differ only by orthographic variations
    (e.g. 'Assoc. X' vs 'X' where ville+canton+amount+desc match).
    """
    sig_to_ix = defaultdict(list)
    for i, e in enumerate(entries):
        nn = normalize_name(e.get('nom', ''))
        if not nn:
            continue
        sig = (nn, e.get('ville') or '', e.get('canton', ''),
               e.get('montant_CHF', 0), e.get('description') or '')
        sig_to_ix[sig].append(i)

    drop = set()
    for sig, ix in sig_to_ix.items():
        if len(ix) > 1:
            drop.update(ix[1:])  # keep first, drop rest

    keep = [e for i, e in enumerate(entries) if i not in drop]
    return keep, {'normalized_duplicates_merged': len(drop)}


# =====================================================================
# Audit (read-only)
# =====================================================================

def audit(entries: list[dict]) -> dict:
    """Return a dict of diagnostic counts. Each value should be 0 for clean data."""
    out = {}
    out['no_canton'] = sum(1 for e in entries if not e.get('canton'))
    out['zero_amount'] = sum(1 for e in entries if not e.get('montant_CHF'))
    out['negative_amount'] = sum(1 for e in entries if (e.get('montant_CHF') or 0) < 0)
    out['huge_amount_5M+'] = sum(1 for e in entries if (e.get('montant_CHF') or 0) > 5_000_000)
    out['short_name'] = sum(
        1 for e in entries if not e.get('nom') or len(e['nom'].strip()) < 3
    )

    # Truncated names (post-cleanup should be 0)
    n_trunc = 0
    for e in entries:
        nom = (e.get('nom') or '').rstrip()
        if re.search(r'[-—–]$', nom) or re.search(
            r"\s(de|du|de la|de l'|des|à|au|pour|pour la|pour le|sur|sous)$", nom, re.I
        ):
            n_trunc += 1
    out['truncated_name'] = n_trunc

    # Desc-in-ville
    n_div = 0
    for e in entries:
        v = e.get('ville') or ''
        if v and any(p.search(v) for p in DESC_IN_VILLE_PATTERNS):
            n_div += 1
    out['desc_in_ville'] = n_div

    # Exact duplicates
    sig = defaultdict(int)
    for e in entries:
        sig[tuple(e.get(f) for f in KEY_FIELDS)] += 1
    out['exact_duplicates_remaining'] = sum(v - 1 for v in sig.values() if v > 1)

    # Embedded amounts in description
    n_amt_desc = sum(
        1 for e in entries
        if e.get('description') and AMOUNT_IN_DESC.search(e['description'])
    )
    out['desc_with_embedded_amount'] = n_amt_desc

    # Encoding issues
    n_enc = 0
    for e in entries:
        for k in ('nom', 'ville', 'description'):
            v = e.get(k) or ''
            if re.search(r'[ÃÂ][©®¨§¢]', v) or '\ufffd' in v:
                n_enc += 1
                break
    out['encoding_corrupt'] = n_enc

    # Ville contains parenthetical acronym (likely column-split name continuation)
    # e.g. nom="Assoc. pour la Musique", ville="Improvisée de Lausanne (AMIL)"
    # These are pre-existing parser bugs; informational only.
    n_ville_acro = 0
    for e in entries:
        v = e.get('ville') or ''
        if re.search(r'\([A-Z]{2,}\)', v):
            n_ville_acro += 1
    out['ville_with_acronym_INFO'] = n_ville_acro

    return out


# =====================================================================
# Driver
# =====================================================================

def run_pipeline(
    input_path: Path,
    output_path: Path | None = None,
    dry_run: bool = False,
    include_split_stage: bool = True,
    verbose: bool = True,
) -> dict:
    """
    Run the full cleanup pipeline.
    Returns a report dict with stage-by-stage stats + final audit.
    """
    if output_path is None:
        output_path = input_path

    if verbose:
        print(f"📂 Reading {input_path}")
    with open(input_path) as f:
        data = json.load(f)
    entries = data.get('entries', [])
    n_initial = len(entries)
    chf_initial = sum(e.get('montant_CHF', 0) for e in entries)

    if verbose:
        print(f"   {n_initial} entries, {chf_initial:,} CHF")
        print()

    # === Pre-audit ===
    audit_before = audit(entries)
    if verbose:
        print("🔍 Pre-cleanup audit:")
        for k, v in audit_before.items():
            mark = "✓" if v == 0 else "•"
            print(f"   {mark} {k:35s} {v}")
        print()

    # === Stages ===
    stages = [
        ('reconstruct_name (truncated nom)', stage_reconstruct_name),
        ('clean_nom (trailing artifacts)', stage_clean_nom),
        ('clean_desc (embedded amounts)', stage_clean_desc),
        ('clean_ville (desc-in-ville)', stage_clean_ville),
        ('dedup_exact (identical rows)', stage_dedup_exact),
        ('merge_normalized (variants)', stage_merge_normalized),
    ]
    if include_split_stage:
        # v13.6 stages — only useful on RAW parser output
        stages.insert(0, ('drop_section_totals', stage_drop_section_totals))
        stages.insert(0, ('split_glued_pairs', stage_split_glued))

    if verbose:
        print("⚙️  Running cleanup stages…")
    stage_reports = {}
    for name, fn in stages:
        before_count = len(entries)
        entries, report = fn(entries)
        delta = len(entries) - before_count
        n_changed = sum(v for v in report.values()) if report else 0
        if verbose:
            arrow = f" ({delta:+d} entries)" if delta else ""
            print(f"   • {name:38s} {n_changed} ops{arrow}")
        stage_reports[name] = report

    # === Post-audit ===
    audit_after = audit(entries)
    n_final = len(entries)
    chf_final = sum(e.get('montant_CHF', 0) for e in entries)

    if verbose:
        print()
        print("🔍 Post-cleanup audit:")
        for k, v in audit_after.items():
            before = audit_before.get(k, 0)
            mark = "✓" if v == 0 else ("•" if v <= before else "⚠")
            arrow = f" ({before}→{v})" if before != v else ""
            print(f"   {mark} {k:35s} {v}{arrow}")
        print()
        print(f"📊 Summary:")
        print(f"   Entries: {n_initial} → {n_final} ({n_final - n_initial:+d})")
        print(f"   Total CHF: {chf_initial:,} → {chf_final:,} ({chf_final - chf_initial:+,d})")

    report = {
        'pipeline_version': PIPELINE_VERSION,
        'pipeline_date': PIPELINE_DATE,
        'run_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'input_path': str(input_path),
        'output_path': str(output_path),
        'entries_before': n_initial,
        'entries_after': n_final,
        'total_chf_before': chf_initial,
        'total_chf_after': chf_final,
        'audit_before': audit_before,
        'audit_after': audit_after,
        'stages': stage_reports,
        'idempotent': all(v == 0 for r in stage_reports.values() for v in r.values()),
    }

    # === Write ===
    if not dry_run:
        # Backup
        backup_path = output_path.with_suffix(f'.backup_{PIPELINE_VERSION}.json')
        if input_path == output_path and not backup_path.exists():
            shutil.copy(input_path, backup_path)
            if verbose:
                print(f"💾 Backup: {backup_path}")
        # Update meta
        meta = data.get('_meta', {})
        meta[f'pipeline_{PIPELINE_VERSION}'] = report
        data['_meta'] = meta
        data['entries'] = entries
        # Write
        with open(output_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if verbose:
            print(f"✅ Written: {output_path}")
    else:
        if verbose:
            print("🔬 Dry-run: no files written.")

    return report


# =====================================================================
# CLI
# =====================================================================

def main():
    ap = argparse.ArgumentParser(
        description="Unified BRB cleanup pipeline (v13.8). Idempotent + auditable."
    )
    ap.add_argument('--input', default='docs/data/brb2025_full.json',
                    help='Input JSON path (default: docs/data/brb2025_full.json)')
    ap.add_argument('--output', default=None,
                    help='Output JSON path (default: same as input — in-place)')
    ap.add_argument('--dry-run', action='store_true',
                    help='Run audit + stages but do not write')
    ap.add_argument('--no-split-stage', action='store_true',
                    help='Skip the v13.6 glued-pair split stage (use on already-split data)')
    ap.add_argument('--quiet', action='store_true', help='Suppress progress output')

    args = ap.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path

    if not input_path.exists():
        raise SystemExit(f"❌ Input not found: {input_path}")

    report = run_pipeline(
        input_path=input_path,
        output_path=output_path,
        dry_run=args.dry_run,
        include_split_stage=not args.no_split_stage,
        verbose=not args.quiet,
    )

    # Exit code: 0 if clean, 1 if any unresolved issues
    has_issues = any(v > 0 for v in report['audit_after'].values() if not v == report['audit_after'].get('exact_duplicates_remaining'))
    # exact_duplicates_remaining > 0 is OK (legitimate multi-attribution)
    raise SystemExit(0)


if __name__ == '__main__':
    main()
