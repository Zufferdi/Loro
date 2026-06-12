#!/usr/bin/env python3
"""
parse_brb2024_v2.py — Re-parse BRB 2024 with new markdown format
==================================================================

Key differences vs 2023/2025 format:
  - Lines often prefixed with '##' (markdown headers from pdftotext)
  - No '•' bullets — descriptions are just lines between name and amount
  - Amounts formatted as '## 1'330.-' (with ## prefix)
  - Canton headers '## Vaud' etc. appear as page-nav repeats (unreliable)
  - Section/canton bounds detected mostly via section title scanning

Entry parsing:
  Stack lines until a money line. Then split stack into:
    - name (top of stack, possibly multi-line, possibly ending with ", Ville"
      or with a separate '## Ville' line)
    - description (lines from the first known description prefix to bottom)
"""
import sys
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/mnt/user-data/uploads/BRB2024.md')
OUTPUT = ROOT / 'docs' / 'data' / 'brb2024_full.json'
BACKUP = ROOT / 'docs' / 'data' / 'brb2024_full.backup_pre_reparse.json'


OFFICIAL_SECTORS = [
    'Action sociale et personnes âgées',
    'Action sociale',  # short form used in headers
    'Jeunesse et éducation',
    'Santé et handicap',
    'Culture',
    'Formation et recherche',
    'Conservation du patrimoine',
    'Environnement',
    'Promotion, tourisme et développement',
    'Promotion, tourisme',  # short form
    'Sport',
    # German versions (bilingual VS pages)
    'Kultur',
    'Soziale Aktionen und Senioren',
    'Soziale Aktionen',
    'Jugend und Erziehung',
    'Gesundheit und Behinderung',
    'Bildung und Forschung',
    'Schützenswerte Kulturgüter',
    'Schützenwerte Kulturgüter',
    'Umwelt',
    'Förderung, Tourismus und Entwicklung',
    'Förderung',
]
SECTOR_NORMALIZE = {
    'Action sociale': 'Action sociale et personnes âgées',
    'Promotion, tourisme': 'Promotion, tourisme et développement',
    # German → French normalized sector
    'Kultur': 'Culture',
    'Soziale Aktionen und Senioren': 'Action sociale et personnes âgées',
    'Soziale Aktionen': 'Action sociale et personnes âgées',
    'Jugend und Erziehung': 'Jeunesse et éducation',
    'Gesundheit und Behinderung': 'Santé et handicap',
    'Bildung und Forschung': 'Formation et recherche',
    'Schützenswerte Kulturgüter': 'Conservation du patrimoine',
    'Schützenwerte Kulturgüter': 'Conservation du patrimoine',
    'Umwelt': 'Environnement',
    'Förderung, Tourismus und Entwicklung': 'Promotion, tourisme et développement',
    'Förderung': 'Promotion, tourisme et développement',
}
# Orphan section fragments — to skip (NOT section headers themselves)
SECTION_FRAGMENTS = {
    'et personnes âgées', 'et développement', 'et éducation',
    'et handicap', 'et recherche', 'tourisme',
    'tourisme et développement',
    'und Senioren', 'und Erziehung', 'und Behinderung',
    'und Forschung', 'und Entwicklung',
    'Tourismus und Entwicklung',
}

# Description-line prefixes — if a line starts with any of these, it's a desc
DESCRIPTION_PREFIXES = [
    'Acquisition matériel', 'Acquisition de matériel', 'Acquisition',
    'Travaux', 'Aménagements',
    'Manifestation', 'Manifestations',
    'Activité', 'Activités',
    'Création artistique', 'Création',
    'Saison artistique', 'Saison musicale', 'Saison',
    'Projet', 'Projets',
    'Événement', 'Évènement', 'Evénement', 'Evènement',
    'Publication',
    'Exposition', 'Expositions',
    'Soutien annuel', 'Soutien',
    'Investissement', 'Investissements',
    'Contribution ordinaire', 'Contribution', 'Contributions',
    'Participation', 'Participations',
    'Animation', 'Animations',
    'Matériel',
    'Édition', 'Edition',
    'Concert', 'Concerts',
    'Tournée',
    'Festival',
    'Achat',
    'Construction', 'Constructions',
    'Aide', 'Aides',
    'Bourse', 'Bourses',
    'Cours',
    'Camp', 'Camps',
    'Stage',
    'Conférence',
    'Formation',
    'Spectacle',
    'Théâtre',
    'Film',
    'Frais',
    'Renouvellement',
    'Rénovation',
    'Subvention',
    'Programme',
    'Mise en place',
    'Mise en scène',
    'Organisation',
    'Tour',
    'Réalisation',
    'Production',
    'Œuvre',
    'Recherche',
    'Édition',
    'Étude',
    'Etude',
    'Diffusion',
    'Promotion',
    'Soutien',
    'Refonte',
    'Lancement',
    'Mise en œuvre',
    'Acquisition d',
    'Atelier', 'Ateliers',
    'Workshop',
    'Concours',
    "Acquisition d'instruments",
    'Création',
    'Activité 2024', 'Activité 2025', 'Activité 2023',
    'Activités 2024', 'Activités 2025', 'Activités 2023',
    'Activités pédagogiques',
    'Manifestation 2024', 'Manifestation 2025', 'Manifestation 2023',
    'Édition 2024', 'Édition 2025',
    'édition',
    'Saison',
]

RE_MONEY = re.compile(r"^(?:##\s+)?(\d[\d\s\u2019']*)\.-\s*$")

# Section headers (sans préfixe ##)
SECTION_HEADERS_NORM = {s.lower(): s for s in OFFICIAL_SECTORS}


def normalize_text(s: str) -> str:
    """Strip leading '##' markdown headers, normalize whitespace and NBSP."""
    s = s.replace('\xa0', ' ')  # NBSP → regular space
    s = s.strip()
    while s.startswith('##'):
        s = s[2:].lstrip()
    # Collapse multiple internal spaces
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def normalize_money(s: str) -> int:
    s = s.replace("'", '').replace('\u2019', '').replace(' ', '').replace('\u00a0', '')
    return int(s) if s else 0


def normalize_ville(v: str) -> str:
    if not v: return ''
    v = v.strip()
    v = unicodedata.normalize('NFKD', v)
    v = ''.join(c for c in v if not unicodedata.combining(c))
    v = re.sub(r'\s*-\s*', '-', v)
    v = re.sub(r'\s+', ' ', v)
    return v.lower().strip()


# ─── ville→canton mapping (re-use 2023/2025 + special villes) ──────────────
SPECIAL_VILLES = {
    'les acacias': 'GE', 'acacias': 'GE', 'carouge': 'GE', 'meyrin': 'GE',
    'vernier': 'GE', 'plan-les-ouates': 'GE', 'grand-saconnex': 'GE',
    'le grand-saconnex': 'GE', 'thônex': 'GE', 'thonex': 'GE',
    'chêne-bougeries': 'GE', 'petit-lancy': 'GE', 'grand-lancy': 'GE',
    'onex': 'GE', 'versoix': 'GE', 'cologny': 'GE', 'bellevue': 'GE',
    'satigny': 'GE', 'chambésy': 'GE', 'bernex': 'GE', 'chêne-bourg': 'GE',
    'troinex': 'GE', 'confignon': 'GE', 'lancy': 'GE',
    'villars-sur-glâne': 'FR', 'villars-sur-glane': 'FR',
    'estavayer-le-lac': 'FR', 'plaffeien': 'FR', 'cheyres': 'FR',
    'la tour-de-trême': 'FR', 'noréaz': 'FR', 'corminbœuf': 'FR',
    'wünnewil': 'FR', 'wunnewil': 'FR', 'flamatt': 'FR',
    'wünnewil-flamatt': 'FR', 'düdingen': 'FR', 'tafers': 'FR',
    'kerzers': 'FR', 'morat': 'FR', 'gletterens': 'FR', 'farvagny': 'FR',
    'bulle': 'FR', 'romont': 'FR', 'broc': 'FR', 'attalens': 'FR',
    'châtel-st-denis': 'FR', 'matran': 'FR', 'belfaux': 'FR',
    'marsens': 'FR', 'charmey': 'FR', 'fétigny': 'FR', 'ursy': 'FR',
    'siviriez': 'FR', 'corpataux': 'FR', 'givisiez': 'FR',
    'granges-paccot': 'FR', 'cordast': 'FR',
    'guttet-feschel': 'VS', 'bourg-st-pierre': 'VS', 'st-luc': 'VS',
    'sion': 'VS', 'sierre': 'VS', 'martigny': 'VS', 'monthey': 'VS',
    'brig-glis': 'VS', 'brig': 'VS', 'visp': 'VS', 'naters': 'VS',
    'saas-fee': 'VS', 'saas-grund': 'VS', 'zermatt': 'VS', 'kippel': 'VS',
    'leukerbad': 'VS', 'fully': 'VS', 'savièse': 'VS', 'ayent': 'VS',
    'crans-montana': 'VS', 'verbier': 'VS', 'bagnes': 'VS', 'orsières': 'VS',
    'evolène': 'VS', 'nendaz': 'VS', 'salgesch': 'VS', 'goms': 'VS',
    'ernen': 'VS', 'raron': 'VS', 'leuk': 'VS', 'susten': 'VS',
    'turtmann': 'VS',
    'chexbres': 'VD', 'grandvaux': 'VD', 'bretonnières': 'VD',
    'montagny-près-yverdon': 'VD', 'bussigny-près-lausanne': 'VD',
    'eysins': 'VD', 'orny': 'VD', 'ste-croix': 'VD', 'st-prex': 'VD',
    'echichens': 'VD', 'apples': 'VD', 'corsier-sur-vevey': 'VD',
    'rennaz': 'VD', "vers-l'eglise": 'VD', 'savigny': 'VD', 'ropraz': 'VD',
    'mézières': 'VD', 'oron': 'VD', 'puidoux': 'VD', 'forel': 'VD',
    'préverenges': 'VD', 'mont-sur-rolle': 'VD', 'aubonne': 'VD',
    'rolle': 'VD', 'morges': 'VD', 'nyon': 'VD', 'aigle': 'VD',
    'bex': 'VD', 'leysin': 'VD', 'villars-sur-ollon': 'VD',
    "château-d'œx": 'VD', 'vallorbe': 'VD', 'penthalaz': 'VD',
    'penthaz': 'VD', 'cossonay': 'VD', 'gland': 'VD', 'epalinges': 'VD',
    'écublens': 'VD', 'pully': 'VD', 'crissier': 'VD', 'renens': 'VD',
    'prilly': 'VD', 'lausanne': 'VD', 'vevey': 'VD', 'montreux': 'VD',
    'yverdon-les-bains': 'VD', 'yverdon': 'VD',
    "l'auberson": 'VD', 'salavaux': 'VD', 'etagnières': 'VD',
    'blonay': 'VD', 'grandson': 'VD', 'clarens': 'VD', 'château-d\'œx': 'VD',
    'chézard-st-martin': 'NE', 'la chaux-du-milieu': 'NE',
    'les ponts-de-martel': 'NE', 'st-blaise': 'NE', 'saint-blaise': 'NE',
    'neuchâtel': 'NE', 'la chaux-de-fonds': 'NE', 'le locle': 'NE',
    'colombier': 'NE', 'cortaillod': 'NE', 'peseux': 'NE', 'cernier': 'NE',
    'fleurier': 'NE', 'travers': 'NE', 'couvet': 'NE', 'bevaix': 'NE',
    'boudry': 'NE', 'hauterive': 'NE', 'savagnier': 'NE',
    'dombresson': 'NE',
    'saignelégier': 'JU', 'porrentruy': 'JU', 'delémont': 'JU',
    'bassecourt': 'JU', 'courrendlin': 'JU', 'bure': 'JU',
    'courtelary': 'JU', 'reconvilier': 'JU', 'courgenay': 'JU',
    'courroux': 'JU', 'develier': 'JU', 'alle': 'JU', 'boncourt': 'JU',
    'fontenais': 'JU', 'le noirmont': 'JU', 'les bois': 'JU',
    'les breuleux': 'JU',
    'payerne': 'VD',  # Payerne is VD
}


def build_ville_to_canton():
    mapping = {}
    counter = {}
    # Use brb2023 + brb2025 as references (skip current brb2024 since we are replacing it)
    for year in [2023, 2025]:
        p = ROOT / 'docs' / 'data' / f'brb{year}_full.json'
        if not p.exists():
            continue
        d = json.load(open(p, encoding='utf-8'))
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
    for v, c in SPECIAL_VILLES.items():
        mapping[normalize_ville(v)] = c
    return mapping


v2c_global = {}


def is_description_line(line: str) -> bool:
    """Heuristic: does this line look like a description?"""
    for prefix in DESCRIPTION_PREFIXES:
        if line.startswith(prefix):
            return True
    return False


def parse_entries(text: str):
    raw_lines = text.split('\n')
    # Pre-clean: strip '##' prefix from every line, keep original index
    lines = []
    for raw in raw_lines:
        s = normalize_text(raw)
        lines.append(s)

    # Detect section markers (line → sector name)
    sector_markers = []  # (line_idx, normalized_sector)
    
    # CPORS sport sub-sections — when these appear standalone (without
    # embedded amount), they mark a switch to "Sport" sector
    SPORT_SUB_SECTION_HEADERS = {
        normalize_ville(s) for s in [
            "Associations sportives", "Associations sportives cantonales",
            "Associations sportives cantonales vaudoises",
            "Compétitions, manifestations sportives",
            "Compétitions, manifestations sportives, courses populaires, centres de compétences",
            "Camps sportifs et sport scolaire", "Camps sportifs",
            "Aménagements de terrains et locaux de sport",
            "Achat de matériel sportif", "Achats de matériel sportif",
            "Manifestations sportives",
            "Soutiens aux clubs élites en sport collectif",
            "Soutiens aux centres régionaux de performance",
            "Maison du sport vaudois à Leysin",
            "Soutiens individuels", "Soutiens annuels", "Soutiens extraordinaires",
            "Infrastructures sportives", "Cours de formation et camps",
            "Entraînements fractionnés", "Sports et loisirs (sport pour tous)",
            "Sportifs de pointe ou de talent",
            "Sports de performance et de loisirs (aide ordinaire)",
            "Centres de formation", "Actions LoRo-Sport", "Actions JO",
            "Sport scolaire facultatif",
            "Bourses sportives", "Matériel sportif",
            "Groupements à caractère spécial",
            "Contributions ponctuelles",
            "Materialeinkauf", "Stipendien für Nachwuchssportler",
            "Wettkämpfe, Sportanlässe, Volksläufe und Kompetenzzentren",
            "Kauf von Sportmaterial", "Kantonale Sportverbände",
            "Sportstipendien", "Aktionen LoRo-Sport", "Aktionen OS",
            "Freiwilliger Schulsport",
            "Spitzensportler oder Talente",
            "Freizeitsport (Sport für alle)",
            "Ausbildungszentren",
            "Leistungs- und Freizeitsport (ordentlicher Beitrag)",
        ]
    }
    
    for i, ln in enumerate(lines):
        if not ln:
            continue
        ln_key = ln.lower().strip()
        if ln_key in SECTION_HEADERS_NORM:
            sec = SECTION_HEADERS_NORM[ln_key]
            sec = SECTOR_NORMALIZE.get(sec, sec)
            sector_markers.append((i, sec))
            continue
        # CPORS sport sub-section → mark as Sport sector
        if normalize_ville(ln) in SPORT_SUB_SECTION_HEADERS:
            sector_markers.append((i, 'Sport'))
            continue

    # Pseudo-entries to filter (block-headers, regional sub-totals).
    # All keys must be lowercased + NFKD-decomposed (no accents) to match
    # what normalize_ville produces.
    _raw_pseudo = [
        "Fonds du sport vaudois", "Fonds du Conseil d'État",
        "Commission Fonds du sport", "Fonds du sport",
        "Fonds d'utilité publique", "Fondation d'aide sociale et culturelle",
        "Page", "Répartition",
        "Délégation valaisanne", "Délégation valaisanne à la Loterie Romande",
        "Délégation jurassienne",
        "Commission cantonale", "Commission cantonale de la Loterie Romande",
        "Commission neuchâteloise", "Commission neuchâteloise de répartition",
        "Commission neuchâteloise de répartition du bénéfice",
        "à la Loterie Romande", "à la Loterie Romande de la Loterie Romande",
        "de la Loterie Romande",
        # German page-headers
        "Kultur", "Soziale Aktionen", "Umwelt", "Förderung",
        "Jugend und Erziehung", "Gesundheit und Behinderung",
        "Bildung und Forschung", "Schützenswerte Kulturgüter",
        "Commission", "Délégation",
        # CPORS sport sub-section headers (these have totals collected, but no
        # individual entries — just block totals or concatenated listings)
        "Associations sportives", "Associations sportives cantonales",
        "Associations sportives cantonales vaudoises",
        "Associations cantonales",
        "Compétitions, manifestations sportives",
        "Compétitions, manifestations sportives, courses populaires, centres de compétences",
        "Camps sportifs", "Camps sportifs et sport scolaire",
        "Aménagements de terrains et locaux de sport",
        "Achat de matériel sportif", "Achats de matériel sportif",
        "Manifestations sportives",
        "Soutiens aux clubs élites en sport collectif",
        "Soutiens aux centres régionaux de performance",
        "Maison du sport vaudois à Leysin",
        "Soutien à la Fondation",
        "Soutiens individuels", "Soutiens annuels", "Soutiens extraordinaires",
        "Infrastructures sportives", "Cours de formation et camps",
        "Entraînements fractionnés", "Sports et loisirs (sport pour tous)",
        "Sportifs de pointe ou de talent",
        "Sports de performance et de loisirs (aide ordinaire)",
        "Centres de formation", "Actions LoRo-Sport", "Actions JO",
        "Sport scolaire facultatif", "Constructions",
        "Achats de matériel",
        "Construction et rénovation d'installations sportives",
        "Groupements à caractère spécial",
        "Contributions annuelles", "Contributions ponctuelles",
        "Bourses sportives", "Matériel sportif",
        "Projets particuliers", "Actions extraordinaires",
        # German sport sub-sections
        "Materialeinkauf", "Stipendien für Nachwuchssportler",
        "Bau und Renovation von Sportinfrastrukturen-Sportanlagen",
        "Wettkämpfe, Sportanlässe, Volksläufe und Kompetenzzentren",
        "Kauf von Sportmaterial", "Kantonale Sportverbände",
        "Jährliche Unterstützungen", "Ausserordentliche Gruppen",
        "Punktuelle Unterstützungen", "Ausserordentliche Aktionen",
        "Veranstaltungen", "Ausbildungskurse und Lager",
        "Aufgeteilte Trainings", "Freizeitsport (Sport für alle)",
        "Spitzensportler oder Talente",
        "Leistungs- und Freizeitsport (ordentlicher Beitrag)",
        "Ausbildungszentren", "Aktionen LoRo-Sport", "Aktionen OS",
        "Freiwilliger Schulsport", "Sportstipendien",
    ]
    PSEUDO_ENTRIES = set(normalize_ville(s) for s in _raw_pseudo)

    # Block-header pattern: line ending with money but starting with text
    # like "Fondation d'aide sociale et culturelle37'054'220.-"
    # These should be split: drop the entry, the amount is just the block total.
    RE_BLOCK_HEADER_WITH_AMOUNT = re.compile(
        r"^([A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜàâäéèêëîïôöùûüç][^\d]{5,}?)(\d[\d\u2019']+)\.-\s*$"
    )

    # Pseudo-canton-header lines to skip (the page-nav repeats)
    NOISE_LINES = {
        'Vaud', 'Vau d', 'Vaud Suisse romande Jura Genève Neuchâtel Valais Fribourg',
        'Suisse romande', 'Jura', 'Genève', 'Neuchâtel', 'Valais', 'Fribourg',
        'Wallis', 'Sport', 'CHF',
    }
    # Headers/preamble noise (page intro paragraph)
    PREAMBLE_KEYWORDS = (
        'Loterie Romande', 'Crédit photo', 'Page ', 'Fonds ',
        'Fondation ', 'Conseil d\'État', 'distribuées',
        'Suisse romande', 'd\'utilité publique', 'Tenter sa chance',
        'Jouer pour gagner',
    )

    entries = []
    stack = []  # (line_idx, content)
    stack_start = None

    def commit(montant: int, end_idx: int):
        nonlocal stack, stack_start
        if not stack or montant <= 0:
            stack = []
            stack_start = None
            return
        # Split stack into name + description
        # Description = first run of lines starting from the FIRST line that
        # matches a description prefix
        desc_start_idx = None
        for j, (li, ln) in enumerate(stack):
            if is_description_line(ln):
                desc_start_idx = j
                break

        if desc_start_idx is not None:
            name_lines = [ln for _, ln in stack[:desc_start_idx]]
            desc_lines = [ln for _, ln in stack[desc_start_idx:]]
        else:
            # No description detected — assume last 1-2 lines are description
            name_lines = [ln for _, ln in stack[:-1]] if len(stack) > 1 else []
            desc_lines = [stack[-1][1]] if stack else []
            if not name_lines and desc_lines:
                # Single line — treat as name with empty description
                name_lines = desc_lines
                desc_lines = []

        name_full = ' '.join(s.strip() for s in name_lines if s.strip())
        desc_full = ' '.join(s.strip() for s in desc_lines if s.strip())

        # Filter pseudo-entries (match by prefix to absorb minor variations)
        name_norm = normalize_ville(name_full)
        if name_norm in PSEUDO_ENTRIES:
            stack = []; stack_start = None; return
        # Prefix-match: any pseudo-entry that is a prefix of name_norm
        if any(name_norm.startswith(p) for p in PSEUDO_ENTRIES if len(p) >= 15):
            stack = []; stack_start = None; return
        if any(name_full.lower().startswith(k.lower()) for k in PREAMBLE_KEYWORDS):
            stack = []
            stack_start = None
            return
        if len(name_full) < 4:
            stack = []
            stack_start = None
            return
        # Filter suspicious "concatenated entries" — many commas + named entities
        # (e.g. "Audétat Eileen, Ski de fond Balmer Alexandre, Cyclisme ...")
        # Heuristic: ≥ 4 commas AND ≥ 2 sport-discipline mentions
        if name_full.count(',') >= 4:
            sport_words = re.findall(
                r'\b(Ski|Cyclisme|Football|Hockey|Basket|Tennis|Athlétisme|Natation|'
                r'Athletisme|Athlétique|Tir|Voile|Aviron|Triathlon|Curling|Judo|'
                r'Karaté|Lutte|Rugby|Volleyball|Boxe|Escrime|Patinage|Equitation|'
                r'Snowboard|VTT|Trail|Marathon|Gymnastique|Handball)\b',
                name_full
            )
            if len(sport_words) >= 2:
                stack = []
                stack_start = None
                return
        # Filter very long names with no description (likely concatenated entries)
        if len(name_full) > 200 and not desc_full:
            stack = []
            stack_start = None
            return

        # Extract ville from end of name
        ville = None
        # Strategy 1: last name line, if known ville
        if name_lines and len(name_lines) >= 2:
            last = name_lines[-1].strip().rstrip(',').lstrip(', ')
            if (last and len(last) <= 40
                and not re.search(r'\d', last)
                and not last.endswith((',', '.', ':'))):
                if normalize_ville(last) in v2c_global:
                    ville = last
                    name_full = ' '.join(s.strip() for s in name_lines[:-1] if s.strip())
                    if name_full.endswith(','):
                        name_full = name_full[:-1].strip()
        # Strategy 2: regex ", Ville" at end
        if not ville:
            m = re.match(r'^(.*?),\s*([A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜ][\wÀ-ÿ\-\'\s\(\)\.\/]+?)$', name_full)
            if m:
                cand = m.group(2).strip()
                if (len(cand) <= 35
                    and not re.search(r'\d', cand)
                    and 'Suisse' not in cand[:6]
                    and not cand.endswith(('SA', 'Sàrl', 'Sàrl.'))):
                    if normalize_ville(cand) in v2c_global:
                        name_full = m.group(1).strip()
                        ville = cand
                    elif len(cand) <= 25:
                        # accept anyway, will fall back to SR
                        name_full = m.group(1).strip()
                        ville = cand
        # Strategy 3: scan name for embedded known villes
        if not ville and name_full:
            words = re.findall(r"[A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜ][\wÀ-ÿ\-\'\u2019]+", name_full)
            for length in (3, 2, 1):
                for j in range(len(words) - length + 1):
                    cand = ' '.join(words[j:j + length])
                    if normalize_ville(cand) in v2c_global:
                        ville = cand
                        break
                if ville: break

        entries.append({
            'pos': stack_start,
            'nom': name_full,
            'ville': ville,
            'description': desc_full,
            'montant_CHF': montant,
        })
        stack = []
        stack_start = None

    # Set to track sector header lines (to skip from stack)
    sector_lines = set(li for li, _ in sector_markers)

    for i, ln in enumerate(lines):
        if not ln:
            continue
        # Skip sector header lines
        if i in sector_lines:
            # Reset stack — section change
            stack = []
            stack_start = None
            continue
        # Skip pure noise
        if ln in NOISE_LINES:
            continue
        if re.match(r'^\d+\s*$', ln):
            continue  # page number
        # Skip block-headers with embedded amount (e.g. "Fonds du sport vaudois10'570'983.-")
        m_block = RE_BLOCK_HEADER_WITH_AMOUNT.match(ln)
        if m_block:
            header_text = m_block.group(1).strip().lower()
            # Always drop these — they are block totals, not real entries
            stack = []
            stack_start = None
            continue
        # Skip orphan section fragments ("et personnes âgées" alone)
        if ln in SECTION_FRAGMENTS:
            stack = []
            stack_start = None
            continue
        # Skip preamble paragraphs (long lines with lowercase prose)
        if len(ln) > 60 and ln[0].islower():
            continue
        # Detect money line
        m = RE_MONEY.match(ln)
        if m:
            commit(normalize_money(m.group(1)), i)
            continue
        # Otherwise: stack the line
        if stack_start is None:
            stack_start = i
        stack.append((i, ln))

    return entries, sector_markers


def attribute_sector(pos: int, markers: list) -> str | None:
    best = None
    for li, sec in markers:
        if li <= pos:
            best = sec
        else:
            break
    # Normalize German/short forms to canonical French sectors
    if best in SECTOR_NORMALIZE:
        best = SECTOR_NORMALIZE[best]
    return best


def main():
    global v2c_global
    if not INPUT.exists():
        print(f"❌ Input not found: {INPUT}")
        return

    if OUTPUT.exists():
        BACKUP.write_text(OUTPUT.read_text(encoding='utf-8'), encoding='utf-8')
        print(f"📦 Backup of existing brb2024_full.json → {BACKUP.name}")

    text = INPUT.read_text(encoding='utf-8')
    print(f"Reading {INPUT.name}: {len(text):,} chars, {text.count(chr(10)):,} lines")

    print(f"\nBuilding ville→canton mapping from brb2023/2025…")
    v2c_global = build_ville_to_canton()
    print(f"  {len(v2c_global)} villes mapped")

    print(f"\nParsing entries…")
    raw, sector_markers = parse_entries(text)
    print(f"  {len(raw)} raw entries, {len(sector_markers)} sector markers")

    # Attribute canton (via ville) + sector (via position)
    CANTON_ADJ = {
        'vaudois': 'VD', 'vaudoise': 'VD',
        'fribourgeois': 'FR', 'fribourgeoise': 'FR', 'freiburger': 'FR',
        'valaisan': 'VS', 'valaisanne': 'VS', 'walliser': 'VS',
        'neuchâtelois': 'NE', 'neuchâteloise': 'NE',
        'genevois': 'GE', 'genevoise': 'GE',
        'jurassien': 'JU', 'jurassienne': 'JU',
    }
    out = []
    for e in raw:
        ville = e.get('ville')
        canton = v2c_global.get(normalize_ville(ville)) if ville else None
        if not canton and e['nom']:
            name_lower = e['nom'].lower()
            for adj, c in CANTON_ADJ.items():
                if adj in name_lower:
                    canton = c
                    break
        if not canton:
            canton = 'SR'
        sector = attribute_sector(e['pos'], sector_markers)
        if not e['nom'] or len(e['nom']) < 4 or not re.search(r'[A-Za-zÀ-ÿ]', e['nom']):
            continue
        out.append({
            'nom': e['nom'],
            'ville': ville,
            'description': e['description'],
            'canton': canton,
            'secteur': sector,
            'montant_CHF': e['montant_CHF'],
            'annee': 2024,
        })

    total = sum(e['montant_CHF'] for e in out)
    by_c = {}
    by_s = {}
    for e in out:
        by_c[e['canton']] = by_c.get(e['canton'], 0) + e['montant_CHF']
        s = e['secteur'] or 'AUTRE'
        by_s[s] = by_s.get(s, 0) + e['montant_CHF']

    print(f"\nFinal: {len(out)} entries, total {total:,} CHF\n")
    print("By canton:")
    for c, v in sorted(by_c.items(), key=lambda x: -x[1]):
        print(f"  {c}: {v:>13,} CHF")
    print("\nBy secteur:")
    for s, v in sorted(by_s.items(), key=lambda x: -x[1]):
        print(f"  {s[:50]:<50}: {v:>13,} CHF")

    OUTPUT.write_text(json.dumps({
        '_meta': {
            'source': 'BRB2024.pdf (ra.loro.ch/documents/BRB2024.pdf)',
            'parsed_from': 'BRB2024.md (re-parse v2 with ## prefix handling)',
            'annee': 2024,
            'total_entries': len(out),
            'total_chf': total,
            'canton_attribution': 'via ville→canton mapping from brb2023/brb2025',
        },
        'entries': out,
    }, ensure_ascii=False, indent=2))
    print(f"\nWrote {OUTPUT}")


if __name__ == '__main__':
    main()
