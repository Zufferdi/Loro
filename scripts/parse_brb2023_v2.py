#!/usr/bin/env python3
"""
parse_brb2023_v2.py — Robust parser using pre-scan of canton & sector markers
==============================================================================

Key insight: in BRB 2023 PDF, the "X CHF Y.-" header marks the END of a block,
not its start. So the linear streaming parser must NOT trigger sector assignment
on encountering "Vaud CHF 39'892'080.-" because the entries belonging to this
total appear BEFORE the header in the file.

Solution: pre-scan to find all (canton-header, sector-header) positions.
Then each entry's (canton, sector) is determined by the markers that follow it
(canton) and that precede it (sector).
"""
import json
import re
from pathlib import Path

INPUT = Path('/mnt/user-data/uploads/BRB2023.md')
OUTPUT = Path('/home/claude/audit2/Loro-main/docs/data/brb2023_full.json')

CANTON_NAMES = {
    'Vaud': 'VD', 'Fribourg': 'FR', 'Valais': 'VS', 'Wallis': 'VS',
    'Neuchâtel': 'NE', 'Genève': 'GE', 'Jura': 'JU',
    'Suisse romande': 'SR',
}
RE_CANTON_HEADER = re.compile(
    r'^(' + '|'.join(re.escape(n) for n in CANTON_NAMES) + r')\s+CHF\s+[\d\u2019\u0027\'\s]+\.-\s*$'
)

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

# Sport sub-sections (CPORS) -> force secteur=Sport
SPORT_SUB_KEYWORDS = [
    'associations sportives', 'camps sportifs', 'soutien aux élèves',
    'aménagement', 'manifestations sportives', 'soutiens aux clubs élites',
    'centres régionaux de performance', "soutien à la fondation",
    'maison du sport', 'contributions annuelles',
    'associations sportives cantonales', 'groupements à caractère spécial',
    'contributions ponctuelles', 'construction et rénovation',
    'achat de matériel sportif', 'achats de matériel sportif',
    'compétitions, manifestations', 'bourses sportives',
    'soutiens individuels', 'matériel sportif', 'soutiens annuels',
    'soutiens centres régionaux', 'soutiens extraordinaires',
    'infrastructures sportives', 'cours de formation et camps',
    'entraînements fractionnés', 'sports et loisirs',
    'sportifs de pointe', 'sports de performance',
    'centres de formation', 'actions loro-sport', 'actions jo',
    'sport scolaire facultatif', 'actions extraordinaires',
    'constructions', 'achats de matériel', 'projets particuliers',
]

RE_MONEY = re.compile(r'^\s*([\d][\d\s\u2019\u0027\']*)\.-\s*$')
RE_BULLET = re.compile(r'^\s*•\s*(.*)$')


def normalize_text(s: str) -> str:
    return s.replace('`', '').strip()


def normalize_money(s: str) -> int:
    s = s.replace('.-', '').replace("'", '').replace('\u2019', '').replace(' ', '').replace('\u00a0', '')
    return int(s) if s else 0


def prescan(lines):
    """
    Returns:
      canton_markers: list of (line_idx, canton_code, block_num_within_canton)
      sector_markers: list of (line_idx, sector_name)

    Block numbering: each time the same canton header appears again, increment block.
    Block 1 = CPOR (ordinaire), Block 2 = CPORS (sport), Block 3 = Conseil d'État.
    """
    canton_markers = []
    sector_markers = []
    canton_seen = {}  # canton_code -> last block number

    for i, raw in enumerate(lines):
        line = normalize_text(raw)
        if not line:
            continue

        # Canton header
        m = RE_CANTON_HEADER.match(line)
        if m:
            cname = m.group(1)
            code = CANTON_NAMES[cname]
            block = canton_seen.get(code, 0) + 1
            canton_seen[code] = block
            canton_markers.append((i, code, block))
            continue

        # Sector header (single-line)
        if line in OFFICIAL_SECTORS:
            sector_markers.append((i, line))
            continue

        # Sector header (multi-line: line + next)
        if i + 1 < len(lines):
            nxt = normalize_text(lines[i + 1])
            joined = (line + ' ' + nxt).strip()
            if joined in OFFICIAL_SECTORS:
                sector_markers.append((i, joined))
                continue
        if i + 2 < len(lines):
            nxt = normalize_text(lines[i + 1])
            nxt2 = normalize_text(lines[i + 2])
            joined3 = (line + ' ' + nxt + ' ' + nxt2).strip()
            if joined3 in OFFICIAL_SECTORS:
                sector_markers.append((i, joined3))
                continue

        # Sport sub-section
        line_lower = line.lower()
        if any(kw in line_lower for kw in SPORT_SUB_KEYWORDS):
            # Only if the line is short (header-like, not part of a description)
            if len(line) <= 80:
                sector_markers.append((i, 'Sport'))
                continue

    return canton_markers, sector_markers


def attribute_canton(entry_pos, canton_markers):
    """
    Find the canton header AT OR AFTER entry_pos that owns this entry.
    Since the header appears AFTER the entries of its block, we look for
    the FIRST canton marker at line >= entry_pos.
    """
    for line_idx, code, block in canton_markers:
        if line_idx >= entry_pos:
            return code, block
    return None, 0


def attribute_sector(entry_pos, sector_markers, canton_block_start):
    """
    Find the most recent sector marker at line <= entry_pos,
    but AFTER the start of the current canton block (canton_block_start).
    """
    best = None
    for line_idx, sec in sector_markers:
        if canton_block_start <= line_idx <= entry_pos:
            best = sec
    return best


def parse_entries(lines):
    """Pass 1: extract raw entries with their starting line position.

    An entry consists of:
      name lines (one or more)
      bullet description (one or more lines starting with •, possibly continued)
      money line "X.-"
    """
    entries = []
    buf = []
    bullets = []
    in_bullets = False
    start_pos = None

    def commit(montant, end_pos):
        nonlocal buf, bullets, in_bullets, start_pos
        if buf and montant > 0:
            name_full = ' '.join(s.strip() for s in buf if s.strip())
            nom = name_full
            ville = None
            m = re.match(r'^(.*?),\s*([A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜ][\wÀ-ÿ\-\'\s\(\)\.\/]+)$', name_full)
            if m:
                candidate = m.group(2).strip()
                if (len(candidate) <= 35
                    and not re.search(r'\d', candidate)
                    and 'Suisse' not in candidate[:6]
                    and not candidate.endswith(('SA', 'Sàrl', 'Sàrl.'))):
                    nom = m.group(1).strip()
                    ville = candidate
            description = ' '.join(b.strip() for b in bullets if b.strip())
            entries.append({
                'pos': start_pos,
                'nom': nom,
                'ville': ville,
                'description': description,
                'montant_CHF': montant,
            })
        buf = []
        bullets = []
        in_bullets = False
        start_pos = None

    for i, raw in enumerate(lines):
        line = normalize_text(raw)
        if not line:
            continue

        # Skip headers (canton, sector, sport sub-section, section totals)
        if RE_CANTON_HEADER.match(line):
            # Drop any pending entry that has no money line
            buf = []
            bullets = []
            in_bullets = False
            start_pos = None
            continue
        if line in OFFICIAL_SECTORS:
            buf = []
            bullets = []
            in_bullets = False
            start_pos = None
            continue
        line_lower = line.lower()
        if len(line) <= 80 and any(kw in line_lower for kw in SPORT_SUB_KEYWORDS):
            buf = []
            bullets = []
            in_bullets = False
            start_pos = None
            continue

        # Bullet description
        m_bul = RE_BULLET.match(line)
        if m_bul:
            in_bullets = True
            bullets.append(m_bul.group(1))
            continue

        # Money line
        m_money = RE_MONEY.match(line)
        if m_money:
            if in_bullets and buf:
                commit(normalize_money(m_money.group(1) + '.-'), i)
            else:
                # Section sub-total or stray money line — discard
                buf = []
                bullets = []
                in_bullets = False
                start_pos = None
            continue

        # In bullet continuation?
        if in_bullets:
            bullets.append(line)
            continue

        # Otherwise: name line, skip noise
        if line in CANTON_NAMES:
            continue
        if re.match(r'^\d+\s*$', line):
            continue
        # Skip multi-line title fragments (e.g. "et personnes âgées" alone)
        # Heuristic: if no canton has been seen yet and line is part of a sector title fragment, skip
        # Actually we already strip those via OFFICIAL_SECTORS match — minor fragments will go into buf
        # as part of the next name and we'll filter at the end.

        # Skip very common page-header fragments
        if line in ('Suisse romande', 'aud', 'Fribourg', 'alais', 'Neuchâtel',
                   'enève', 'Jura', 'uisse romande',
                   'Associations, institutions et fondations bénéficiaires',
                   'des contributions de la Loterie Romande',
                   'Associations, manifestations et projets bénéficiaires des contributions',
                   "de la Loterie Romande dans le domaine du sport",
                   "Associations, manifestations et projets bénéficiaires des contributions",
                   'distribuées par le Conseil d’État ou par un service de l’État',
                   "Contributions de la Loterie Romande distribuées par le Conseil d'État",
                   'Contributions de la Loterie Romande',
                   "Fonds d’attributions cantonales",
                   "distribuées par la Conférence",
                   "des Présidents des Organes cantonaux de répartition (CPOR)",
                   "des Présidents des Organes de Répartition du sport (CPORS)",
                   "Tableau récapitulatif des versements 2023 de la Conférence",
                   "Vom Staatsrat oder vom staatlichen Stellen gewährte Beiträge",
                   "Fonds distribués par les services de l’État",
                   "Fonds distribués par le Conseil d’État",
                   "Vom Staatsrat gewährte Beiträge"):
            continue

        if start_pos is None:
            start_pos = i
        buf.append(line)

    return entries


def main():
    text = INPUT.read_text(encoding='utf-8')
    lines = text.split('\n')

    print(f"Pre-scanning markers…")
    canton_markers, sector_markers = prescan(lines)
    print(f"  {len(canton_markers)} canton headers, {len(sector_markers)} sector headers")

    print(f"\nParsing entries…")
    raw_entries = parse_entries(lines)
    print(f"  {len(raw_entries)} raw entries")

    # Attribute canton & sector
    out_entries = []
    for e in raw_entries:
        pos = e['pos']
        canton, block = attribute_canton(pos, canton_markers)
        # Find start of this canton block (line of canton_markers[block-1] for prior occurrences? Actually it's the END)
        # Block-start = end of previous canton-marker (or 0 if this is the first)
        # For sector attribution: scope is the previous canton-marker's line (or 0).
        if canton:
            # The header of this block is at line `canton_markers[k].line_idx` for the matching marker.
            # Block-start = previous canton-marker line + 1 (or 0 if first).
            prev_idx = 0
            for cm_pos, cm_code, cm_block in canton_markers:
                if cm_pos < pos:
                    prev_idx = cm_pos
            block_start = prev_idx
        else:
            block_start = 0

        sector = attribute_sector(pos, sector_markers, block_start)

        # If block_num >= 2 and canton is one of the standard cantons,
        # the block is the CPORS sport block → force Sport (the block-2 of each canton is sport)
        if canton and block == 2 and canton != 'SR':
            sector = 'Sport'
        if canton == 'SR' and block == 2:
            sector = 'Sport'  # CPORS too

        # Filter junk: must have a real-ish name (≥ 4 chars, contains a letter)
        if not e['nom'] or len(e['nom']) < 4 or not re.search(r'[A-Za-zÀ-ÿ]', e['nom']):
            continue
        # Reject summary-page leftovers
        if 'Répartition des bénéfices' in e['nom']:
            continue

        out_entries.append({
            'nom': e['nom'],
            'ville': e['ville'],
            'description': e['description'],
            'canton': canton,
            'secteur': sector,
            'montant_CHF': e['montant_CHF'],
            'annee': 2023,
        })

    total = sum(e['montant_CHF'] for e in out_entries)
    by_canton = {}
    by_sec = {}
    for e in out_entries:
        c = e['canton'] or '?'
        s = e['secteur'] or 'AUTRE'
        by_canton[c] = by_canton.get(c, 0) + e['montant_CHF']
        by_sec[s] = by_sec.get(s, 0) + e['montant_CHF']

    print(f"\nFinal: {len(out_entries)} entries, total {total:,} CHF\n")
    print("By canton:")
    for c, v in sorted(by_canton.items(), key=lambda x: -x[1]):
        print(f"  {c}: {v:>12,} CHF")
    print("\nBy secteur:")
    for s, v in sorted(by_sec.items(), key=lambda x: -x[1]):
        print(f"  {s[:50]:<50}: {v:>12,} CHF")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({
        '_meta': {
            'source': 'BRB2023.pdf (ra.loro.ch/documents/BRB2023.pdf)',
            'parsed_from': 'BRB2023.md',
            'annee': 2023,
            'total_entries': len(out_entries),
            'total_chf': total,
        },
        'entries': out_entries,
    }, ensure_ascii=False, indent=2))
    print(f"\nWrote {OUTPUT}")


if __name__ == '__main__':
    main()
