#!/usr/bin/env python3
"""
parse_brb2021.py — Parser BRB 2021 v2 (gestion section multi-ligne + sous-totaux)
"""
import sys
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/mnt/user-data/uploads/BRB2021.md')
OUTPUT = ROOT / 'docs' / 'data' / 'brb2021_full.json'

CANTON_NAMES = {
    'Vaud': 'VD', 'Fribourg': 'FR', 'Valais': 'VS', 'Wallis': 'VS',
    'Neuchâtel': 'NE', 'Genève': 'GE', 'Jura': 'JU',
    'Suisse romande': 'SR',
}

RE_CANTON_DOUBLE = re.compile(
    r'^(' + '|'.join(re.escape(n) for n in CANTON_NAMES) + r')\1\s*$'
)
RE_CANTON_SUBTOTAL = re.compile(
    r'^(' + '|'.join(re.escape(n) for n in CANTON_NAMES) + r')CHF\s+.+\.\-?\s*$'
)

# Sections officielles + leurs début (pour matching split sur 2 lignes)
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
# Premiers mots de chaque secteur (pour détecter section split sur 2 lignes)
SECTOR_FIRST_TOKENS = {
    'Action sociale et': 'Action sociale et personnes âgées',
    'Jeunesse et': 'Jeunesse et éducation',
    'Santé et': 'Santé et handicap',
    'Culture': 'Culture',
    'Formation et': 'Formation et recherche',
    'Conservation du': 'Conservation du patrimoine',
    'Environnement': 'Environnement',
    'Promotion, tourisme': 'Promotion, tourisme et développement',
    'Sport': 'Sport',
}

# Sport sub-section markers
SPORT_SECTION_HEADERS = {
    'Associations sportives', 'Camps sportifs', 'Manifestations sportives',
    'Aménagements de terrains et locaux de sport',
    'Aménagement de terrains et locaux de sport',
    'Soutiens aux clubs élites en sport collectif',
    'Soutiens aux centres régionaux',
    'Soutiens aux centres régionaux de performance',
    'Maison du sport vaudois à Leysin', 'Soutien à la Fondation',
    'Associations sportives cantonales', 'Groupements à caractère spécial',
    'Bourses sportives', 'Sportifs de pointe ou de talent',
    'Sports de performance et de loisirs (aide ordinaire)',
    'Centres de formation', 'Actions LoRo-Sport', 'Actions JO',
    'Sport scolaire facultatif', 'Soutiens annuels',
    'Soutiens Centres régionaux de performance', 'Soutiens extraordinaires',
    'Infrastructures sportives', 'Cours de formation et camps',
    'Entraînements fractionnés', 'Sports et loisirs (sport pour tous)',
    'Matériel sportif', 'Achat de matériel sportif', 'Achats de matériel sportif',
    'Projets particuliers', 'Actions extraordinaires', 'Constructions',
    'Achats de matériel', "Construction et rénovation d'installations sportives",
    'Camps sportifs et sport scolaire', 'Natation', 'Athlétisme', 'Tennis',
    'Volleyball', 'Football', 'Basketball', 'Hockey', 'Ski', 'Cyclisme',
    'Patinage', 'Plongée', 'Paddle', 'Patinage artistique',
    'Promotion de la relève', 'Sport pour tous',
}

RE_MONEY_LINE = re.compile(r'^\s*([\d][\d\s\u2019\u0027\']*)\.-\s*$')
RE_MONEY_INLINE = re.compile(r"^(.+?)([\d][\d\s\u2019\u0027\']{2,})\.-\s*$")
RE_YEAR_PREFIX = re.compile(r'^((?:18|19|20)\d{2})([\d\u2019\u0027\'].*)$')


def norm_text(s):
    return s.replace('`', '').strip()


def norm_money(s):
    s = s.replace('.-', '').replace("'", '').replace('\u2019', '').replace(' ', '').replace('\u00a0', '')
    return int(s) if s.isdigit() else 0


def norm_ville(v):
    if not v: return ''
    v = unicodedata.normalize('NFKD', v.strip())
    v = ''.join(c for c in v if not unicodedata.combining(c))
    v = re.sub(r'\s*-\s*', '-', v)
    v = re.sub(r'\s+', ' ', v)
    return v.lower().strip()


def build_v2c():
    counter = {}
    for year in [2022, 2023, 2024, 2025]:
        p = ROOT / 'docs' / 'data' / f'brb{year}_full.json'
        if not p.exists(): continue
        d = json.load(open(p, encoding='utf-8'))
        for e in d['entries']:
            v, c = e.get('ville'), e.get('canton')
            if not v or not c or c == 'SR': continue
            key = norm_ville(v)
            counter.setdefault(key, {}).setdefault(c, 0)
            counter[key][c] += 1
    return {v: max(cc.items(), key=lambda x: x[1])[0] for v, cc in counter.items()}


RE_VILLE_NOM = re.compile(
    r'^(.+?),\s*([A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜ][\w\-\'\u2019À-ÿ\s]+?)\s*(?:\([A-Z]+\))?\s*$'
)


def extract_ville(text, v2c):
    if not text: return text, None
    m = RE_VILLE_NOM.match(text)
    if not m: return text, None
    nom, ville = m.group(1).strip(), m.group(2).strip()
    ville = re.sub(r'\s*\([A-Z]+\)\s*$', '', ville)
    if norm_ville(ville) in v2c:
        return nom, ville
    first = ville.split()[0] if ville else ''
    if first and norm_ville(first) in v2c:
        return nom, first
    return text, None


BULLET_PREFIXES = ['Activité', 'Manifestation', 'Acquisition', 'Travaux', 'Création',
                   'Exposition', 'Tournée', 'Spectacle', 'Concert', 'Festival',
                   'Édition', 'Recherche', 'Construction', 'Achat', 'Bourse',
                   'Soutien', 'Aide', 'Cours', 'Recensement', 'Restauration',
                   'Camp', 'Projet', 'Saison', 'Mise', 'Aménagement', 'Glossaire',
                   'Concours', 'Démarche', 'Atelier', 'Stage', 'Tournoi',
                   'Championnat', 'Cinéma']


def is_bullet(line):
    return any(line.startswith(p) for p in BULLET_PREFIXES)


def parse():
    print("Building ville→canton…")
    v2c = build_v2c()
    print(f"  {len(v2c)} villes")

    lines = INPUT.read_text(encoding='utf-8').split('\n')
    print(f"\nParsing {len(lines)} lignes…\n")

    entries = []
    cur_canton = None
    cur_sector = None
    name_buf, desc_buf = [], []
    just_after_section = False  # flag pour ignorer le sous-total

    def commit(montant):
        nonlocal name_buf, desc_buf, just_after_section
        if montant <= 0:
            name_buf = []; desc_buf = []; return
        if just_after_section:
            # Premier montant après section header = sous-total → ignorer
            just_after_section = False
            name_buf = []; desc_buf = []; return
        if not name_buf:
            return
        nom = ' '.join(p.strip() for p in name_buf if p.strip())
        nom = re.sub(r'\s+', ' ', re.sub(r'\s+,', ',', nom)).strip()
        if not nom or len(nom) < 3:
            name_buf = []; desc_buf = []; return
        nom_clean, ville = extract_ville(nom, v2c)
        if ville:
            nom = nom_clean
        canton = v2c.get(norm_ville(ville), cur_canton) if ville else (cur_canton or 'SR')
        desc = ' '.join(d.strip() for d in desc_buf if d.strip())
        desc = re.sub(r'\s+', ' ', desc).strip()
        entries.append({
            'nom': nom, 'ville': ville, 'canton': canton,
            'secteur': cur_sector, 'description': desc,
            'montant_CHF': montant,
        })
        name_buf = []; desc_buf = []

    i = 0
    while i < len(lines):
        line = norm_text(lines[i])
        if not line:
            i += 1
            continue
        # Skip num page
        if re.match(r'^##\s+\d+\s*$', line) or re.match(r'^\d+\s*$', line):
            i += 1
            continue

        # Canton header double
        m_dbl = RE_CANTON_DOUBLE.match(line)
        if m_dbl:
            cur_canton = CANTON_NAMES[m_dbl.group(1)]
            name_buf = []; desc_buf = []
            cur_sector = None
            just_after_section = False
            i += 1
            continue
        # Canton sous-total à ignorer
        if RE_CANTON_SUBTOTAL.match(line):
            i += 1
            continue

        # Strip "## "
        clean = re.sub(r'^##\s+', '', line).strip()

        # Section header sur 1 ou 2 lignes
        if clean in OFFICIAL_SECTORS:
            cur_sector = clean
            name_buf = []; desc_buf = []
            just_after_section = True
            i += 1
            continue
        # Section "X / German"
        m_bil = re.match(r'^(.+?)\s*/\s*[A-ZÄÖÜ].*$', clean)
        if m_bil and m_bil.group(1).strip() in OFFICIAL_SECTORS:
            cur_sector = m_bil.group(1).strip()
            name_buf = []; desc_buf = []
            just_after_section = True
            i += 1
            continue
        # Section "X (suite)"
        m_suite = re.match(r'^(.+?)\s*\(suite\)', clean)
        if m_suite and m_suite.group(1).strip() in OFFICIAL_SECTORS:
            cur_sector = m_suite.group(1).strip()
            name_buf = []; desc_buf = []
            just_after_section = True
            i += 1
            continue
        # Section sur 2 lignes : combiner avec la suivante
        if clean in SECTOR_FIRST_TOKENS:
            if i + 1 < len(lines):
                next_line = norm_text(lines[i + 1])
                next_clean = re.sub(r'^##\s+', '', next_line).strip()
                combined = clean + ' ' + next_clean
                # Cherche match
                for sec in OFFICIAL_SECTORS:
                    if combined.startswith(sec) or sec.startswith(combined):
                        cur_sector = sec
                        name_buf = []; desc_buf = []
                        just_after_section = True
                        i += 2  # skip both lines
                        break
                else:
                    # Pas trouvé : traiter normalement
                    i += 1
                    continue
                continue

        # Sport sub-section header
        if clean in SPORT_SECTION_HEADERS:
            cur_sector = 'Sport'
            name_buf = []; desc_buf = []
            i += 1
            continue

        # Montant seul ?
        m_m = RE_MONEY_LINE.match(clean)
        if m_m:
            montant = norm_money(m_m.group(1) + '.-')
            commit(montant)
            i += 1
            continue

        # Montant collé en fin ?
        m_in = RE_MONEY_INLINE.match(clean)
        if m_in:
            text_part = m_in.group(1).strip()
            money_part = m_in.group(2).strip()
            # Splitter si année dans le money_part
            m_yr = RE_YEAR_PREFIX.match(money_part)
            if m_yr:
                year_str = m_yr.group(1)
                real_money = m_yr.group(2).strip()
                rm = real_money.replace("'", "").replace("\u2019", "").replace(" ", "")
                if rm.isdigit() and int(rm) >= 500:
                    text_part = text_part + ' ' + year_str
                    money_part = real_money
                else:
                    text_part = text_part + ' ' + money_part
                    name_buf.append(text_part)
                    i += 1
                    continue
            if len(text_part) > 3:
                ms = money_part.replace("'", "").replace("\u2019", "").replace(" ", "")
                if ms.isdigit() and int(ms) >= 500:
                    name_buf.append(text_part)
                    commit(int(ms))
                    i += 1
                    continue

        # Bullet description ?
        if is_bullet(clean):
            desc_buf.append(clean)
            i += 1
            continue

        # Sinon : nom
        if clean and len(clean) <= 150 and not clean.startswith('Total'):
            name_buf.append(clean)
        i += 1

    # === Stats ===
    print(f"  Entries: {len(entries)}")
    total = sum(e['montant_CHF'] for e in entries)
    print(f"  Total: {total:,} CHF ({total/1e6:.1f} M)")

    by_c = Counter()
    by_c_chf = {}
    for e in entries:
        c = e['canton']
        by_c[c] += 1
        by_c_chf[c] = by_c_chf.get(c, 0) + e['montant_CHF']
    print(f"\n  Par canton :")
    for c in ['VD', 'GE', 'FR', 'VS', 'NE', 'JU', 'SR']:
        if c in by_c:
            print(f"    {c}: {by_c[c]:>5} entries, {by_c_chf[c]/1e6:>6.1f} M")

    by_s = Counter(e['secteur'] or '(None)' for e in entries)
    print(f"\n  Par secteur :")
    for s, n in by_s.most_common():
        print(f"    {n:>5}× {s}")

    output = {
        '_meta': {
            'source': 'BRB2021.pdf (ra.loro.ch/documents/BRB2021.pdf)',
            'parsed_from': 'BRB2021.md',
            'annee': 2021,
            'total_entries': len(entries),
            'total_CHF': total,
            'parser_version': 'parse_brb2021.py v2',
        },
        'entries': entries,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2, encoding='utf-8'))
    print(f"\n  ✓ Wrote {OUTPUT}")


if __name__ == '__main__':
    parse()
