#!/usr/bin/env python3
"""
parse_brb2023.py — Parse BRB 2023 markdown into brb2023_full.json
==================================================================

Same output schema as brb2024_full.json / brb2025_full.json.
"""
import sys
import json
import re
import unicodedata
from pathlib import Path

INPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/mnt/user-data/uploads/BRB2023.md')
OUTPUT = (Path(__file__).resolve().parent.parent / 'docs' / 'data' / 'brb2023_full.json')

# ─── Canton header detection ──────────────────────────────────────────────
# Matches lines like "Vaud CHF 39'892'080.-" or "Genève CHF 46'510'288.-"
CANTON_NAMES = {
    'Vaud': 'VD', 'Fribourg': 'FR', 'Valais': 'VS', 'Wallis': 'VS',
    'Neuchâtel': 'NE', 'Genève': 'GE', 'Jura': 'JU',
    'Suisse romande': 'SR',
}
RE_CANTON_HEADER = re.compile(
    r'^(' + '|'.join(re.escape(n) for n in CANTON_NAMES) + r')\s+CHF\s+[\d\u2019\u0027\'\s]+\.-\s*$'
)

# ─── Official sectors (CPOR/ordinaire) ────────────────────────────────────
OFFICIAL_SECTORS = [
    'Action sociale et personnes âgées',
    'Jeunesse et éducation',
    'Santé et handicap',
    'Culture',
    'Formation et recherche',
    'Conservation du patrimoine',
    'Environnement',
    'Promotion, tourisme et développement',
    'Sport',
]

# ─── Sport sub-section headers (CPORS) all map to "Sport" ─────────────────
SPORT_SUB_SECTIONS = {
    'Associations sportives',
    'Soutien aux élèves des structures sport-études vaudoises',
    'Camps sportifs et sport scolaire',
    "Aménagements de terrains et locaux de sport",
    'Achat de matériel sportif',
    'Manifestations sportives',
    'Soutiens aux clubs élites en sport collectif',
    'Soutiens aux centres régionaux de performance',
    'Projets particuliers',
    "Soutien à la Fondation d'aide aux sportifs vaudois et aux sportifs d'élite en sport individuel",
    'Soutien à la Fondation',
    "d'aide aux sportifs vaudois et aux sportifs",
    "d'élite en sport individuel",
    'Maison du sport vaudois à Leysin',
    # Generic CPORS section labels:
    'Contributions annuelles',
    'Associations sportives cantonales',
    'Groupements à caractère spécial',
    'Contributions ponctuelles',
    'Construction et rénovation d’installations sportives',
    "Construction et rénovation d'installations sportives",
    'Achats de matériel sportif',
    'Compétitions, manifestations sportives, courses populaires, centres de compétences',
    'Bourses sportives',
    'Soutiens individuels',
    'Matériel sportif',
    'Soutiens annuels',
    'Soutiens Centres régionaux de performance',
    'Soutiens extraordinaires',
    'Infrastructures sportives',
    'Cours de formation et camps',
    'Entraînements fractionnés',
    'Sports et loisirs (sport pour tous)',
    'Sportifs de pointe ou de talent',
    'Sports de performance et de loisirs (aide ordinaire)',
    'Centres de formation',
    'Actions LoRo-Sport',
    'Actions JO',
    'Sport scolaire facultatif',
    'Actions extraordinaires',
    'Constructions',
    'Achats de matériel',
}

# These headers force secteur=Sport regardless of position
SPORT_SUB_NORM = {s.lower(): True for s in SPORT_SUB_SECTIONS}

# ─── Money regex ──────────────────────────────────────────────────────────
# Examples: "30'000.-", "1'000'000.-", "3'874'080.-", "30 000.-"
# Apostrophes can be U+0027 (') or U+2019 (’), and there may be a thin space
RE_MONEY = re.compile(r'^\s*([\d][\d\s\u2019\u0027\']*)\.-\s*$')

# ─── Description bullet ──────────────────────────────────────────────────
RE_BULLET = re.compile(r'^\s*•\s*(.*)$')

# ─── Section total line — number followed by .- right after a section header
# (e.g. after "Action sociale\net personnes âgées\n3'874'080.-")
# We'll consume the section total inline.


def normalize_text(s: str) -> str:
    """Normalize whitespace; strip backtick artifacts from markdown."""
    s = s.replace('`', '').strip()
    return s


def normalize_money(s: str) -> int:
    """Convert '3'874'080.-' or '3 874 080.-' to 3874080."""
    s = s.replace('.-', '').replace("'", '').replace('\u2019', '').replace(' ', '').replace('\u00a0', '')
    return int(s) if s else 0


def parse_brb2023(text: str):
    """Returns list of entries dict {nom, ville, description, canton, secteur, montant_CHF, annee}."""
    lines = text.split('\n')
    entries = []

    canton = None          # current canton code (VD, FR, …)
    sector = None          # current official sector name
    # Some Vaud sport block actually opens with "Associations sportives" → set sector=Sport
    # We detect any line in SPORT_SUB_SECTIONS to force sector=Sport.

    # Buffer for the current entry being assembled
    buf = []               # list of non-bullet name lines
    bullets = []           # list of bullet description lines (sans the •)
    in_bullets = False     # whether we are currently inside the bullet block

    def flush_entry(montant_int):
        if not buf or montant_int <= 0:
            buf.clear()
            bullets.clear()
            return
        # Reassemble name lines
        name_full = ' '.join(s.strip() for s in buf if s.strip())
        # Last segment after the LAST comma is usually the ville,
        # IF it doesn't contain digits and is short (≤ 35 chars).
        # But: the name may legitimately contain commas (e.g. "AAEE, Lausanne").
        # Heuristic: ville is the chunk after the last comma, only if it looks like
        # a town (letters, dashes, apostrophes; no parens; no commas of its own).
        nom = name_full
        ville = None
        m = re.match(r'^(.*?),\s*([A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜ][\wÀ-ÿ\-\'\s\(\)\.\/]+)$', name_full)
        if m:
            candidate_ville = m.group(2).strip()
            # Reject if too long or contains digits or is an org suffix
            if (len(candidate_ville) <= 35
                and not re.search(r'\d', candidate_ville)
                and 'Suisse' not in candidate_ville[:6]
                and not candidate_ville.endswith(('SA', 'Sàrl', 'Sàrl.'))):
                nom = m.group(1).strip()
                ville = candidate_ville

        # Reassemble description from bullets
        description = ' '.join(b.strip() for b in bullets if b.strip())

        entries.append({
            'nom': nom,
            'ville': ville,
            'description': description,
            'canton': canton,
            'secteur': sector,
            'montant_CHF': montant_int,
            'annee': 2023,
        })
        buf.clear()
        bullets.clear()

    i = 0
    while i < len(lines):
        raw = lines[i]
        line = normalize_text(raw)
        i += 1

        if not line:
            continue

        # 1. Canton header → switch canton, reset sector
        m_canton = RE_CANTON_HEADER.match(line)
        if m_canton:
            cname = m_canton.group(1)
            canton = CANTON_NAMES[cname]
            sector = None
            # Discard any pending half-parsed entry
            buf.clear()
            bullets.clear()
            in_bullets = False
            continue

        # 2. Official sector header — may span 2 lines (e.g. "Action sociale\net personnes âgées")
        joined = line
        if i < len(lines):
            joined2 = (line + ' ' + normalize_text(lines[i])).strip()
            joined3 = joined2
            if i + 1 < len(lines):
                joined3 = (joined2 + ' ' + normalize_text(lines[i + 1])).strip()
        else:
            joined2 = joined3 = line

        matched_sector = None
        consume_extra = 0
        for sec in OFFICIAL_SECTORS:
            if line == sec:
                matched_sector = sec
                break
            if joined2 == sec:
                matched_sector = sec
                consume_extra = 1
                break
            if joined3 == sec:
                matched_sector = sec
                consume_extra = 2
                break

        if matched_sector:
            sector = matched_sector
            i += consume_extra
            # Section total line follows immediately
            if i < len(lines):
                nxt = normalize_text(lines[i])
                if RE_MONEY.match(nxt):
                    i += 1  # skip section total
            # Reset entry buffers
            buf.clear()
            bullets.clear()
            in_bullets = False
            continue

        # 3. Sport sub-section (CPORS / Conseil d'État) → force sector=Sport
        if line.lower() in SPORT_SUB_NORM:
            sector = 'Sport'
            # Possible total line follows
            if i < len(lines):
                nxt = normalize_text(lines[i])
                if RE_MONEY.match(nxt):
                    i += 1
            buf.clear()
            bullets.clear()
            in_bullets = False
            continue

        # 4. Bullet description
        m_bul = RE_BULLET.match(line)
        if m_bul:
            in_bullets = True
            bullets.append(m_bul.group(1))
            continue

        # If we are in the bullets block and the line is not a money line,
        # treat it as a description continuation.
        if in_bullets:
            m_money = RE_MONEY.match(line)
            if m_money:
                # End of entry
                montant = normalize_money(m_money.group(1) + '.-')
                flush_entry(montant)
                in_bullets = False
                continue
            else:
                # Continuation of last bullet description
                bullets.append(line)
                continue

        # 5. Money line at top level (no bullets) — unusual, skip (sub-totals)
        m_money = RE_MONEY.match(line)
        if m_money:
            # Could be a stray total; reset accumulators
            buf.clear()
            continue

        # 6. Otherwise: it's part of a name (multi-line)
        # Skip page-header noise like "Vaud", "Suisse romande", page numbers
        # (single line consisting only of canton name(s)).
        if line in CANTON_NAMES:
            continue
        # Skip pure-digit lines (page numbers)
        if re.match(r'^\d+\s*$', line):
            continue
        # Skip lines that are clearly headers/titles (start with caps and < 4 chars after stripping)
        # Otherwise accumulate as name
        buf.append(line)

    return entries


def main():
    text = INPUT.read_text(encoding='utf-8')
    print(f"Parsing {INPUT} ({len(text):,} chars, {text.count(chr(10)):,} lines)…")
    entries = parse_brb2023(text)

    # Summary
    total = sum(e['montant_CHF'] for e in entries)
    by_canton = {}
    by_secteur = {}
    for e in entries:
        c = e['canton'] or '?'
        s = e['secteur'] or 'AUTRE'
        by_canton[c] = by_canton.get(c, 0) + e['montant_CHF']
        by_secteur[s] = by_secteur.get(s, 0) + e['montant_CHF']

    print(f"\nParsed {len(entries)} entries, total {total:,} CHF")
    print(f"\nBy canton:")
    for c, v in sorted(by_canton.items(), key=lambda x: -x[1]):
        print(f"  {c}: {v:>12,} CHF")
    print(f"\nBy secteur:")
    for s, v in sorted(by_secteur.items(), key=lambda x: -x[1]):
        print(f"  {s[:50]:<50}: {v:>12,} CHF")

    # Write out
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out = {
        '_meta': {
            'source': 'BRB2023.pdf (ra.loro.ch/documents/BRB2023.pdf)',
            'parsed_from': 'BRB2023.md (markdown extraction)',
            'annee': 2023,
            'total_entries': len(entries),
            'total_chf': total,
        },
        'entries': entries,
    }
    OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nWrote {OUTPUT}")


if __name__ == '__main__':
    main()
