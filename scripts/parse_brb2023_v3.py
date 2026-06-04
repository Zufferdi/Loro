#!/usr/bin/env python3
"""
parse_brb2023_v3.py — Use ville→canton mapping + sector headers
================================================================

Approach (after v2 failed):
  - Build (ville → canton) dict from existing brb2024 + brb2025 (10k+ entries)
  - For each parsed entry, canton = dict[ville] (fallback SR or None)
  - Sector = last official section header seen before this entry
  - Do NOT use the "X CHF Y.-" headers for sector assignment — they are
    just sub-totals scattered through the document, sometimes at the start
    of a block (Genève), sometimes at the end (Vaud).
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path('/home/claude/audit2/Loro-main')
INPUT = Path('/mnt/user-data/uploads/BRB2023.md')
OUTPUT = ROOT / 'docs' / 'data' / 'brb2023_full.json'

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

# Sport sub-section markers (CPORS et CE) — force secteur=Sport ONLY when these
# specific headers are matched (not generic words like "constructions" anywhere)
SPORT_SECTION_HEADERS = {
    # CPORS Vaud
    'Associations sportives',
    'Camps sportifs',
    "Aménagements de terrains et locaux de sport",
    'Manifestations sportives',
    'Soutiens aux clubs élites en sport collectif',
    'Soutiens aux centres régionaux',
    'Soutiens aux centres régionaux de performance',
    'Maison du sport vaudois à Leysin',
    'Soutien à la Fondation',
    # CPORS Fribourg, Valais, others
    'Associations sportives cantonales',
    'Groupements à caractère spécial',
    'Compétitions, manifestations sportives, courses populaires, centres de compétences',
    'Bourses sportives',
    'Sportifs de pointe ou de talent',
    'Sports de performance et de loisirs (aide ordinaire)',
    'Centres de formation',
    'Actions LoRo-Sport',
    'Actions JO',
    'Sport scolaire facultatif',
    # CPORS Neuchâtel, Genève, Jura
    'Soutiens annuels',
    'Soutiens Centres régionaux de performance',
    'Soutiens extraordinaires',
    'Infrastructures sportives',
    'Cours de formation et camps',
    'Entraînements fractionnés',
    'Sports et loisirs (sport pour tous)',
    'Matériel sportif',
    'Achat de matériel sportif',
    'Achats de matériel sportif',
    'Projets particuliers',
    'Actions extraordinaires',
    # Generic sport sub-headers
    'Constructions',
    "Achats de matériel",
    "Construction et rénovation d’installations sportives",
    "Construction et rénovation d'installations sportives",
    'Camps sportifs et sport scolaire',
}

RE_MONEY = re.compile(r'^\s*([\d][\d\s\u2019\u0027\']*)\.-\s*$')
RE_BULLET = re.compile(r'^\s*•\s*(.*)$')


def normalize_text(s: str) -> str:
    return s.replace('`', '').strip()


def normalize_money(s: str) -> int:
    s = s.replace('.-', '').replace("'", '').replace('\u2019', '').replace(' ', '').replace('\u00a0', '')
    return int(s) if s else 0


def normalize_ville(v: str) -> str:
    """Normalize for ville-canton lookup."""
    if not v: return ''
    v = v.strip()
    # Remove accents for matching
    v = unicodedata.normalize('NFKD', v)
    v = ''.join(c for c in v if not unicodedata.combining(c))
    # Collapse multiple spaces, fix " - " → "-"
    v = re.sub(r'\s*-\s*', '-', v)
    v = re.sub(r'\s+', ' ', v)
    return v.lower().strip()


# Quartiers/villes spéciales connues mais souvent absentes ou mal-normalisées dans le dict
SPECIAL_VILLES = {
    # Genève (quartiers et communes périphériques)
    'les acacias': 'GE', 'acacias': 'GE', 'carouge': 'GE', 'meyrin': 'GE',
    'vernier': 'GE', 'plan-les-ouates': 'GE', 'grand-saconnex': 'GE',
    'le grand-saconnex': 'GE', 'thônex': 'GE', 'thonex': 'GE',
    'chêne-bougeries': 'GE', 'chene-bougeries': 'GE',
    'petit-lancy': 'GE', 'grand-lancy': 'GE', 'onex': 'GE',
    'versoix': 'GE', 'cologny': 'GE', 'bellevue': 'GE',
    'satigny': 'GE', 'chambésy': 'GE', 'chambesy': 'GE',
    'bernex': 'GE', 'chêne-bourg': 'GE', 'chene-bourg': 'GE',
    'troinex': 'GE', 'avusy': 'GE', 'confignon': 'GE', 'lancy': 'GE',
    # Fribourg
    'villars-sur-glâne': 'FR', 'villars-sur-glane': 'FR',
    'estavayer-le-lac': 'FR', 'plaffeien': 'FR',
    'cheyres': 'FR', 'la tour-de-trême': 'FR', 'la tour-de-treme': 'FR',
    'noréaz': 'FR', 'noreaz': 'FR', 'corminbœuf': 'FR', 'corminboeuf': 'FR',
    'wünnewil': 'FR', 'wunnewil': 'FR', 'flamatt': 'FR',
    'wünnewil-flamatt': 'FR', 'wunnewil-flamatt': 'FR',
    'düdingen': 'FR', 'dudingen': 'FR', 'tafers': 'FR',
    'kerzers': 'FR', 'morat': 'FR', 'gletterens': 'FR',
    'farvagny': 'FR', 'bulle': 'FR', 'romont': 'FR', 'broc': 'FR',
    'attalens': 'FR', 'châtel-st-denis': 'FR', 'chatel-st-denis': 'FR',
    'matran': 'FR', 'belfaux': 'FR', 'marsens': 'FR', 'charmey': 'FR',
    'fétigny': 'FR', 'fetigny': 'FR', 'ursy': 'FR',
    'siviriez': 'FR', 'st-aubin': 'FR', 'saint-aubin': 'FR',
    'corpataux': 'FR', 'givisiez': 'FR', 'cugy': 'FR',
    'granges-paccot': 'FR', 'cordast': 'FR',
    # Valais
    'guttet-feschel': 'VS', 'bourg-st-pierre': 'VS',
    'st-luc': 'VS', 'sion': 'VS', 'sierre': 'VS', 'martigny': 'VS',
    'monthey': 'VS', 'brig-glis': 'VS', 'brig': 'VS', 'visp': 'VS',
    'naters': 'VS', 'saas-fee': 'VS', 'saas-grund': 'VS', 'zermatt': 'VS',
    'kippel': 'VS', 'leukerbad': 'VS', 'fully': 'VS', 'savièse': 'VS',
    'saviese': 'VS', 'ayent': 'VS', 'crans-montana': 'VS',
    'verbier': 'VS', 'bagnes': 'VS', 'orsières': 'VS', 'orsieres': 'VS',
    'evolène': 'VS', 'evolene': 'VS', 'nendaz': 'VS',
    'salgesch': 'VS', 'goms': 'VS', 'ernen': 'VS', 'raron': 'VS',
    'leuk': 'VS', 'susten': 'VS', 'turtmann': 'VS',
    # Vaud
    'chexbres': 'VD', 'grandvaux': 'VD', 'bretonnières': 'VD',
    'montagny-près-yverdon': 'VD', 'bussigny-près-lausanne': 'VD',
    'eysins': 'VD', 'orny': 'VD', 'ste-croix': 'VD',
    'st-prex': 'VD', 'echichens': 'VD', 'apples': 'VD',
    'corsier-sur-vevey': 'VD', 'rennaz': 'VD', 'vers-l\'eglise': 'VD',
    'vers-leglise': 'VD', 'savigny': 'VD', 'ropraz': 'VD',
    'mézières': 'VD', 'mezieres': 'VD', 'oron': 'VD',
    'puidoux': 'VD', 'forel': 'VD', 'préverenges': 'VD',
    'preverenges': 'VD', 'mont-sur-rolle': 'VD', 'aubonne': 'VD',
    'rolle': 'VD', 'morges': 'VD', 'nyon': 'VD', 'aigle': 'VD',
    'bex': 'VD', 'leysin': 'VD', 'villars-sur-ollon': 'VD',
    'château-d\'œx': 'VD', 'chateau-doex': 'VD',
    'vallorbe': 'VD', 'penthalaz': 'VD', 'penthaz': 'VD',
    'cossonay': 'VD', 'gland': 'VD', 'epalinges': 'VD',
    'écublens': 'VD', 'ecublens': 'VD', 'pully': 'VD',
    'crissier': 'VD', 'renens': 'VD', 'prilly': 'VD',
    'lausanne': 'VD', 'vevey': 'VD', 'montreux': 'VD',
    'yverdon-les-bains': 'VD', 'yverdon': 'VD',
    # Neuchâtel
    'chézard-st-martin': 'NE', 'chezard-st-martin': 'NE',
    'la chaux-du-milieu': 'NE', 'les ponts-de-martel': 'NE',
    'st-blaise': 'NE', 'saint-blaise': 'NE',
    'neuchâtel': 'NE', 'neuchatel': 'NE',
    'la chaux-de-fonds': 'NE', 'le locle': 'NE',
    'colombier': 'NE', 'cortaillod': 'NE', 'peseux': 'NE',
    'cernier': 'NE', 'fleurier': 'NE', 'travers': 'NE',
    'couvet': 'NE', 'bevaix': 'NE', 'boudry': 'NE',
    'hauterive': 'NE', 'savagnier': 'NE', 'dombresson': 'NE',
    # Jura
    'saignelégier': 'JU', 'saignelegier': 'JU',
    'porrentruy': 'JU', 'delémont': 'JU', 'delemont': 'JU',
    'bassecourt': 'JU', 'courrendlin': 'JU', 'bure': 'JU',
    'courtelary': 'JU', 'reconvilier': 'JU',
    'courgenay': 'JU', 'courroux': 'JU', 'develier': 'JU',
    'alle': 'JU', 'boncourt': 'JU', 'fontenais': 'JU',
    'le noirmont': 'JU', 'les bois': 'JU', 'les breuleux': 'JU',
}


def build_ville_to_canton():
    """Build ville→canton dict from brb2024 + brb2025, plus SPECIAL_VILLES."""
    mapping = {}
    counter = {}
    for year in [2024, 2025]:
        p = ROOT / 'docs' / 'data' / f'brb{year}_full.json'
        if not p.exists():
            continue
        d = json.load(open(p))
        for e in d['entries']:
            v = e.get('ville')
            c = e.get('canton')
            if not v or not c or c == 'SR':
                continue
            key = normalize_ville(v)
            counter.setdefault(key, {}).setdefault(c, 0)
            counter[key][c] += 1
    for v, c_counts in counter.items():
        best = max(c_counts.items(), key=lambda x: x[1])
        mapping[v] = best[0]
    # Merge special villes (override if needed)
    for v, c in SPECIAL_VILLES.items():
        mapping[normalize_ville(v)] = c
    return mapping


# Module-level dict (filled in main, used by commit())
v2c_global = {}


def attribute_canton(ville: str, mapping: dict, default='SR') -> str:
    if not ville:
        return default
    key = normalize_ville(ville)
    return mapping.get(key, default)


def parse_entries(text: str):
    """Parse all entries with their starting line position, plus pre-collected sector markers."""
    lines = text.split('\n')

    # Pre-scan sector markers (line_idx → sector name)
    sector_markers = []  # list of (line_idx, sector_name)
    for i, raw in enumerate(lines):
        line = normalize_text(raw)
        if not line:
            continue
        # Single-line official section
        if line in OFFICIAL_SECTORS:
            sector_markers.append((i, line))
            continue
        # Multi-line: "Action sociale" + "et personnes âgées"
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
        # Sport sub-section header → force Sport
        if line in SPORT_SECTION_HEADERS:
            sector_markers.append((i, 'Sport'))
            continue

    # Pre-scan canton CHF markers (just for noise filtering, not for attribution)
    is_header_line = set()
    for i, raw in enumerate(lines):
        line = normalize_text(raw)
        if RE_CANTON_HEADER.match(line):
            is_header_line.add(i)
        elif line in OFFICIAL_SECTORS:
            is_header_line.add(i)
        elif line in SPORT_SECTION_HEADERS:
            is_header_line.add(i)

    # Also tag the joined-multiline sector headers as header lines
    for i, raw in enumerate(lines):
        line = normalize_text(raw)
        if i + 1 < len(lines):
            nxt = normalize_text(lines[i + 1])
            if (line + ' ' + nxt).strip() in OFFICIAL_SECTORS:
                is_header_line.add(i)
                is_header_line.add(i + 1)
        if i + 2 < len(lines):
            nxt = normalize_text(lines[i + 1])
            nxt2 = normalize_text(lines[i + 2])
            if (line + ' ' + nxt + ' ' + nxt2).strip() in OFFICIAL_SECTORS:
                is_header_line.add(i)
                is_header_line.add(i + 1)
                is_header_line.add(i + 2)

    # Entries
    raw_entries = []
    buf = []
    bullets = []
    in_bullets = False
    start_pos = None

    NOISE_LINES = {
        'Suisse romande', 'Vaud', 'Fribourg', 'Valais', 'Wallis',
        'Neuchâtel', 'Genève', 'Jura',
        'aud', 'alais', 'enève', 'uisse romande',
        'Associations, institutions et fondations bénéficiaires',
        'des contributions de la Loterie Romande',
        'Associations, manifestations et projets bénéficiaires des contributions',
        "de la Loterie Romande dans le domaine du sport",
        "Contributions de la Loterie Romande distribuées par le Conseil d'État",
        "Contributions de la Loterie Romande distribuées par",
        "le Conseil d'État ou par un service de l'État",
        'Contributions de la Loterie Romande',
        "Fonds d'attributions cantonales",
        "Fonds d’attributions cantonales",
        "distribuées par la Conférence",
        "des Présidents des Organes cantonaux de répartition (CPOR)",
        "des Présidents des Organes de Répartition du sport (CPORS)",
        "Tableau récapitulatif des versements 2023 de la Conférence",
        "Vom Staatsrat oder vom staatlichen Stellen gewährte Beiträge",
        "Fonds distribués par les services de l'État",
        "Fonds distribués par les services de l’État",
        "Fonds distribués par le Conseil d'État",
        "Fonds distribués par le Conseil d’État",
        "Vom Staatsrat gewährte Beiträge",
        "Von Staatlichen Stellen gewährte Beiträge",
        "Vom Staatsrat oder vom staatlichen Stellen",
        "Fonds distribués par le Conseil d’État ou par un service de l’État",
        # Bilingual section subtitles
        'Soziale Aktionen und Senioren',
        'Jugend und Erziehung',
        'Gesundheit und Behinderung',
        'Kultur',
        'Bildung und Forschung',
        'Schützenswerte Kulturgüter',
        'Schützenwerte Kulturgüter',
        'Umwelt',
        'Förderung, Tourismus und Entwicklung',
        'Materialeinkauf',
        'Stipendien für Nachwuchssportler',
        'Bau und Renovation von Sportinfrastrukturen-Sportanlagen',
        'Wettkämpfe, Sportanlässe, Volksläufe und Kompetenzzentren',
        'Kauf von Sportmaterial',
        'Kantonale Sportverbände',
        'Jährliche Unterstützungen',
        'Ausserordentliche Gruppen',
        'Punktuelle Unterstützungen',
        'Ausserordentliche Aktionen',
        'Veranstaltungen',
        'Ausbildungskurse und Lager',
        'Aufgeteilte Trainings',
        'Freizeitsport (Sport für alle)',
        'Spitzensportler oder Talente',
        'Leistungs- und Freizeitsport (ordentlicher Beitrag)',
        'Ausbildungszentren',
        'Aktionen LoRo-Sport',
        'Aktionen OS',
        'Freiwilliger Schulsport',
        'Sportstipendien',
    }

    # Adjectifs cantonaux → code canton (fallback si pas de ville détectée)
    CANTON_ADJECTIVES = {
        'vaudois': 'VD', 'vaudoise': 'VD',
        'fribourgeois': 'FR', 'fribourgeoise': 'FR', 'freiburger': 'FR',
        'valaisan': 'VS', 'valaisanne': 'VS', 'walliser': 'VS',
        'neuchâtelois': 'NE', 'neuchâteloise': 'NE',
        'genevois': 'GE', 'genevoise': 'GE',
        'jurassien': 'JU', 'jurassienne': 'JU',
    }
    # Pseudo-entries (sub-totals, summary lines) — to filter out
    PSEUDO_ENTRIES = {
        'camps sportifs scolaires',
        'contribution sportifs de pointe ou de talent',
        'sport scolaire facultatif',
        'soutiens individuels',
    }

    def commit(montant, end_pos):
        nonlocal buf, bullets, in_bullets, start_pos
        if buf and montant > 0:
            # Strategy 1: last buf line is a known ville → it IS the ville
            ville = None
            nom = None
            if len(buf) >= 2:
                last = buf[-1].strip().rstrip(',')
                last_clean = last.lstrip(' ,')
                if (last_clean
                    and len(last_clean) <= 40
                    and not re.search(r'\d', last_clean)
                    and not last_clean.endswith(('.', ',', ':'))):
                    key = normalize_ville(last_clean)
                    if key in v2c_global:
                        ville = last_clean
                        nom = ' '.join(s.strip() for s in buf[:-1] if s.strip())
                        if nom.endswith(','):
                            nom = nom[:-1].strip()

            # Strategy 2 (fallback): regex on full joined string "..., Ville"
            if not ville:
                name_full = ' '.join(s.strip() for s in buf if s.strip())
                nom = name_full
                m = re.match(r'^(.*?),\s*([A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜ][\wÀ-ÿ\-\'\s\(\)\.\/]+)$', name_full)
                if m:
                    candidate = m.group(2).strip()
                    if (len(candidate) <= 35
                        and not re.search(r'\d', candidate)
                        and 'Suisse' not in candidate[:6]
                        and not candidate.endswith(('SA', 'Sàrl', 'Sàrl.'))):
                        nom = m.group(1).strip()
                        ville = candidate

            # Strategy 3: "Commune de X" / "Commune d'X" / "Ville de X"
            if not ville and nom:
                m = re.match(
                    r"^(?:Commune\s+(?:de\s+|d['\u2019])|Ville\s+(?:de\s+|d['\u2019])|"
                    r"Gemeinde\s+|Stadt\s+|Administration\s+communale\s+(?:de\s+|d['\u2019]))"
                    r"([A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜ][\w\-\'\u2019À-ÿ\s]+?)(?:\s*$|,|\(.*)",
                    nom
                )
                if m:
                    cand = m.group(1).strip().rstrip(',')
                    if normalize_ville(cand) in v2c_global:
                        ville = cand

            # Strategy 4: scan name for any token matching a known ville
            if not ville and nom:
                words = re.findall(r"[A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜ][\wÀ-ÿ\-\'\u2019]+", nom)
                # Try 2-word combinations first (e.g. "La Sarraz", "St-Prex")
                for length in (3, 2, 1):
                    for j in range(len(words) - length + 1):
                        candidate = ' '.join(words[j:j + length])
                        if normalize_ville(candidate) in v2c_global:
                            ville = candidate
                            break
                    if ville:
                        break

            # Filter out pseudo-entries (sub-totals etc.)
            if nom and normalize_ville(nom) in PSEUDO_ENTRIES:
                buf = []
                bullets = []
                in_bullets = False
                start_pos = None
                return

            description = ' '.join(b.strip() for b in bullets if b.strip())
            raw_entries.append({
                'pos': start_pos,
                'nom': nom or '',
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
        # Skip headers and noise
        if i in is_header_line:
            buf.clear()
            bullets.clear()
            in_bullets = False
            start_pos = None
            continue
        if line in NOISE_LINES:
            continue
        if re.match(r'^\d+\s*$', line):
            continue  # page number
        if RE_CANTON_HEADER.match(line):
            buf.clear()
            bullets.clear()
            in_bullets = False
            start_pos = None
            continue

        m_bul = RE_BULLET.match(line)
        if m_bul:
            in_bullets = True
            bullets.append(m_bul.group(1))
            continue

        m_money = RE_MONEY.match(line)
        if m_money:
            if in_bullets and buf:
                commit(normalize_money(m_money.group(1) + '.-'), i)
            else:
                # Sub-total or stray money → discard
                buf.clear()
                bullets.clear()
                in_bullets = False
                start_pos = None
            continue

        if in_bullets:
            bullets.append(line)
            continue

        if start_pos is None:
            start_pos = i
        buf.append(line)

    return raw_entries, sector_markers


def attribute_sector(pos: int, sector_markers: list) -> str | None:
    best = None
    for line_idx, sec in sector_markers:
        if line_idx <= pos:
            best = sec
        else:
            break
    return best


def main():
    global v2c_global
    text = INPUT.read_text(encoding='utf-8')
    print(f"Building ville→canton mapping from brb2024/2025…")
    v2c_global = build_ville_to_canton()
    print(f"  {len(v2c_global)} villes mapped")

    print(f"\nParsing entries…")
    raw_entries, sector_markers = parse_entries(text)
    print(f"  {len(raw_entries)} raw entries, {len(sector_markers)} sector markers")

    # Attribute canton (via ville) and sector (via position)
    out = []
    no_canton_count = 0
    no_sector_count = 0
    # Adjectifs cantonaux (fallback ultime si pas de ville)
    CANTON_ADJ = {
        'vaudois': 'VD', 'vaudoise': 'VD',
        'fribourgeois': 'FR', 'fribourgeoise': 'FR', 'freiburger': 'FR',
        'valaisan': 'VS', 'valaisanne': 'VS', 'walliser': 'VS',
        'neuchâtelois': 'NE', 'neuchâteloise': 'NE',
        'genevois': 'GE', 'genevoise': 'GE',
        'jurassien': 'JU', 'jurassienne': 'JU',
    }
    for e in raw_entries:
        canton = attribute_canton(e['ville'], v2c_global, default=None)
        if not canton and e['nom']:
            # Fallback: scan name for canton adjective
            name_lower = e['nom'].lower()
            for adj, c in CANTON_ADJ.items():
                if adj in name_lower:
                    canton = c
                    break
        if not canton:
            canton = 'SR'
            no_canton_count += 1
        sector = attribute_sector(e['pos'], sector_markers)
        if not sector:
            no_sector_count += 1
        if not e['nom'] or len(e['nom']) < 4 or not re.search(r'[A-Za-zÀ-ÿ]', e['nom']):
            continue
        if 'Répartition des bénéfices' in e['nom']:
            continue
        out.append({
            'nom': e['nom'],
            'ville': e['ville'],
            'description': e['description'],
            'canton': canton,
            'secteur': sector,
            'montant_CHF': e['montant_CHF'],
            'annee': 2023,
        })

    total = sum(e['montant_CHF'] for e in out)
    by_c = {}
    by_s = {}
    for e in out:
        by_c[e['canton']] = by_c.get(e['canton'], 0) + e['montant_CHF']
        s = e['secteur'] or 'AUTRE'
        by_s[s] = by_s.get(s, 0) + e['montant_CHF']

    print(f"\n{len(out)} entries, total {total:,} CHF")
    print(f"  Entries without identified ville (→ SR): {no_canton_count}")
    print(f"  Entries without sector: {no_sector_count}")
    print("\nBy canton:")
    for c, v in sorted(by_c.items(), key=lambda x: -x[1]):
        print(f"  {c}: {v:>12,} CHF")
    print("\nBy secteur:")
    for s, v in sorted(by_s.items(), key=lambda x: -x[1]):
        print(f"  {s[:50]:<50}: {v:>12,} CHF")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({
        '_meta': {
            'source': 'BRB2023.pdf (ra.loro.ch/documents/BRB2023.pdf)',
            'parsed_from': 'BRB2023.md',
            'annee': 2023,
            'total_entries': len(out),
            'total_chf': total,
            'canton_attribution': 'via ville→canton mapping from brb2024/brb2025',
        },
        'entries': out,
    }, ensure_ascii=False, indent=2))
    print(f"\nWrote {OUTPUT}")


if __name__ == '__main__':
    main()
