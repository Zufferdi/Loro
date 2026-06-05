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

ROOT = Path('/home/claude/audit3/Loro-main')
DATA = ROOT / 'docs' / 'data'
sys.path.insert(0, str(ROOT / 'scripts'))

YEARS = ['2021', '2022', '2023', '2024', '2025']
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


# ─── EXTRA_PATTERNS : patterns supplémentaires pour les top bénéficiaires ─
# qui échappent aux patterns de base. Appliqués après PASS 2 (memo) et avant
# PASS 3 (catch-all). Format : {classif: [(pattern, sub_cat), ...]}
# Mappe sur des sous-catégories existantes dans chaque classification.

EXTRA_PATTERNS = {
    'sante': [
        # Hôpitaux et soins
        (r'\beHnv\b|\bÉtablissements?\s+hospitalier\b|\bEnsemble\s+hospitalier\b|\bHôpital\s+intercantonal\b',
         'Aide & assistance médicale'),
        (r'\bAVASAD\b|\bAide\s+et\s+soins?\s+à\s+domicile\b|\bsoins?\s+à\s+domicile\b',
         'Aide & assistance médicale'),
        (r'\bRéseau\s+santé\b|\bPôle\s+Santé\b', 'Aide & assistance médicale'),
        # Handicap
        (r"\bÉtablissements?\s+publics\s+pour\s+l['\u2019]?intégration\b|\bEPI\b",
         'Handicap mental / intellectuel'),
        (r'\bFoyers?\s+Valais\s+de\s+cœur\b|\bAigues-Vertes\b', 'Handicap mental / intellectuel'),
        (r'\bAssoc\.\s+Intervalle\b', 'Handicap mental / intellectuel'),
        (r'\bFAH\s+Foyer-Handicap\b|\bFoyer-Handicap\b', 'Handicap mental / intellectuel'),
        # Handicap physique / sensoriel
        (r"\bTransport\s+Handicap\b|\bTHV\b|\baveugles?\s+(?:ou\s+)?malvoyant(?:e?s)?|\bUCBA\b|\bAsile\s+des\s+Aveugles\b",
         'Handicap physique / fauteuil'),
        # Santé mentale
        (r'\bFond\.\s+Trajets\b', 'Santé mentale & psychiatrie'),
        # Specific places
        (r'\bImad\b|\bIMAD\b', 'Aide & assistance médicale'),
    ],
    'jeunesse': [
        (r"\bFond\.\s+Le\s+Camp\b|\bCamps?\s+de\s+vacances\b", 'Passeport vacances & camps'),
        (r"\bCentre\s+Universitaire\s+protestant\b", 'Aide à la jeunesse'),
        (r"\bMère\s+Sofia\b", 'Aide à la jeunesse'),
        (r"\bAFIRO\b", 'Aide à la jeunesse'),
        (r"\bJeunes-Loisirs\b", 'Aide à la jeunesse'),
        (r"\bMaison\s+(?:des\s+)?[Jj]eunes\b", 'Aide à la jeunesse'),
        (r"\bMJSR\b|\bMaison(?:s)?\s+des?\s+Jeunes\s+de\s+(?:Suisse\s+)?Romand", 'Aide à la jeunesse'),
        (r"\bMaison\s+d['\u2019]?enfants\b", 'Aide à la jeunesse'),
        (r"\bLudothèque\b", 'Soutien scolaire & lecture'),
        # Nouveaux 2024 — entries dans Jeunesse mal classés
        (r"\bFond\.\s+officielle\s+de\s+la\s+jeunesse\b", 'Aide à la jeunesse'),
        (r"\bYverdonnoise\s+pour\s+l['\u2019]?Accueil\s+de\s+l['\u2019]?Enfance\b|\bFYAE\b",
         'Petite enfance & crèches'),
        (r"\bFond\.\s+de\s+l['\u2019]?Enfance\s+et\s+de\s+la\s+Jeunesse\b", 'Aide à la jeunesse'),
        (r"\bREPER\b", 'Aide à la jeunesse'),
        (r"\bAccueil\s+familial\s+de\s+jour\b|\bAccueil\s+(?:familial|extra)?scolaire\b",
         'Petite enfance & crèches'),
    ],
    'environnement': [
        (r"\bJardin\s+Urbain\b|\bJardin\s+botanique\b", 'Faune & biodiversité'),
        (r"\bGrangettes\b", 'Eau / Lacs / Rivières'),
        (r"\bFaune\b|\bornithologi", 'Faune & biodiversité'),
        (r"\bForêt\s+", 'Flore & botanique'),
        (r"\b(?:Réserve|réserve)\s+naturelle\b", 'Parcs naturels'),
        (r"\bAstronomie\b", 'Faune & biodiversité'),
        # Nouveaux : refuges & SPA
        (r"\bErminea\b|\brefuge\s+(?:pour\s+)?animaux", 'Faune & biodiversité'),
        (r"\bSPA\s+(?:de\s+|du\s+)?\w", 'Faune & biodiversité'),
        (r"\bLa\s+Vaux-Lierre\b|\bGarenne\b", 'Faune & biodiversité'),
        (r"\bPapiliorama\b", 'Faune & biodiversité'),
        (r"\bMaison\s+de\s+la\s+Rivière\b|\bAquaviva\b", 'Eau / Lacs / Rivières'),
        (r"\bASPO\b|\bBirdLife\b", 'Faune & biodiversité'),
    ],
    'patrimoine': [
        (r"\bLavaux\s+Patrimoine\b|\bPatrimoine\s+mondial\b|\bUNESCO\b",
         'Sites UNESCO / Patrimoine mondial'),
        (r"\bCathédrale\b", 'Patrimoine religieux'),
        (r"\bAutomates?\s+et\s+Merveilles\b", 'Musées spécialisés'),
        (r"\bMusée\s+jurassien\s+d['\u2019]?(?:art|histoire)\b", 'Musées d\'histoire'),
        (r"\bMusée\s+d['\u2019]?histoire\b", 'Musées d\'histoire'),
        (r"\bPortail\s+des\s+Nations\b", 'Musées spécialisés'),
        (r"\bFond\.\s+pour\s+l['\u2019]?Écrit\b", 'Histoire & archives'),
        (r"\b(?:Patrimoine|patrimoine)\s+(?:religieux|bâti|industriel|architectural)\b",
         'Sauvegarde du bâti'),
        # Nouveaux
        (r"\bSauvetage\s+de\s+la\s+Belotte\b|\bBelotte[\s-]Bellerive\b",
         'Musées spécialisés'),
        (r"\bASPAM\b|\bprotection\s+du\s+patrimoine\b", 'Sauvegarde du bâti'),
        (r"\bEspace\s+du\s+Blé\s+au\s+Pain\b", 'Sauvegarde du bâti'),
        # Musées spécifiques romands
        (r"\bMartin\s+Bodmer\b|\bMusée\s+Bodmer\b|\bBibliothèque\s+Bodmer\b", 'Musées spécialisés'),
        (r"\bFond\.\s+Pierre\s+Gianadda\b|\bPierre\s+Gianadda\b", 'Musées spécialisés'),
        (r"\bFond\.\s+Opale\b", 'Musées spécialisés'),
        (r"\bFond\.\s+Maurice\s+Favre\b", 'Histoire & archives'),
        (r"\bFond\.\s+La\s+Tour\s+de\s+Choully\b|\bTour\s+de\s+Choully\b", 'Sauvegarde du bâti'),
        (r"\bVallée\s+des\s+dinosaures\b|\bJurassica\b|\bPaléojura\b", 'Musées spécialisés'),
        (r"\bMusée\s+(?:Olympique|olympique)\b", 'Musées spécialisés'),
        (r"\bChâteau\s+de\s+(?:Chillon|Gruyères|Aigle|Prangins)\b", 'Sauvegarde du bâti'),
        (r"\bMusée\s+(?:cantonal|romain|d['\u2019]?archéologie)", "Musées d'histoire"),
    ],
    'formation': [
        (r"\bCERN\b", 'Recherche scientifique'),
        (r"\bFernfachhochschule\b|\bHaute\s+école\b|\bHES[\s-]?SO\b|\bHEIA\b",
         'Université & hautes écoles'),
        (r"\bCité\s+universitaire\b", 'Université & hautes écoles'),
        (r"\bMaison\s+d['\u2019]?Albert\b", 'Université & hautes écoles'),
        (r"\bISREC\b", 'Recherche scientifique'),
        (r"\bIdiap\b", 'Recherche scientifique'),
        (r"\bCSEM\b", 'Recherche scientifique'),
        (r"\bFond\.\s+pour\s+la\s+recherche\b", 'Recherche scientifique'),
        (r"\bÉcole\s+Suisse\s+d['\u2019]?Archéologie\b", 'Recherche scientifique'),
        (r"\brecherche\s+(?:en\s+)?(?:bio|méd|onco|cell|santé|cancer|pharma|neuro)\w*", 'Recherche scientifique'),
        (r"\bNeurocelliA\b|\bneurosciences\b", 'Recherche scientifique'),
        (r"\bdéveloppement\s+de\s+l['\u2019]?on(?:co|to)logie\b", 'Recherche scientifique'),
        (r"\bSwiss\s+Solar\s+Boat\b", 'Recherche & innovation tech'),
        (r"\bLire\s+et\s+écrire\b", 'Apprentissage & formation continue'),
        (r"\bAssoc\.\s+(?:Salon\s+des\s+Métiers|Cité\s+des\s+Métiers)\b",
         'Salons & orientation métiers'),
        (r"\bUniversité\s+de\s+(?:Lausanne|Genève|Neuchâtel|Fribourg)\b", 'Université & hautes écoles'),
        (r"\bEPFL\b", 'Université & hautes écoles'),
        (r"\bFond\.\s+Pathologie\b", 'Recherche scientifique'),
        # Nouveaux : recherche & formation
        (r"\bInstitut\s+de\s+Hautes\s+Études\s+Internationales\b|\bIHEID\b",
         'Université & hautes écoles'),
        (r"\bDind\s+Cottier\b", 'Recherche scientifique'),
        (r"\bEuroVacc\b", 'Recherche scientifique'),
        (r"\bSwiss\s+Biobanking\b|\bBiobanking\b", 'Recherche scientifique'),
        (r"\bFond\.\s+EspeRare\b|\bEspeRare\b", 'Recherche scientifique'),
        (r"\bRudolf\s+Steiner\b", 'Apprentissage & formation continue'),
        (r"\bInstallateurs?\s+en\s+chauffage\b|\bApprentissage\s+du\s+chauffage\b|\bcours\s+de\s+formation\s+des?\b",
         'Apprentissage & formation continue'),
        (r"\bConservatoire\s+(?:cantonal\s+)?de\s+musique\b", 'Apprentissage & formation continue'),
        (r"\bCFC\b|\bCertificat\s+fédéral\b", 'Apprentissage & formation continue'),
        (r"\bRecherche\s+(?:fondamentale|appliquée|clinique)\b", 'Recherche scientifique'),
    ],
    'promotion': [
        (r"\bFond\.\s+The\s+Ark\b", 'Promotion économique & terroir'),
        (r"\bChocolaterie\b", 'Promotion économique & terroir'),
        (r"\bSAC\s+Sektion\b|\bClub\s+Alpin\s+Suisse\b|\bSection\s+Monte\s+Rosa\b|\bCabane\s+\w",
         'Cabanes & infrastructures montagne'),
        (r"\bSlowUp\b|\bSlow\s+Up\b", 'Manifestations populaires'),
        (r"\bGrandson[\s-]Murten\b|\bJura-24\b|\bGeneva\s+Trophy\b|\bStand['\u2019]?été\b",
         'Manifestations populaires'),
        (r"\bGrande\s+Bourgeoisie\b", 'Promotion économique & terroir'),
        (r"\bComptoir\s+", 'Manifestations populaires'),
        (r"\bFort\s+de\s+Chillon\b", 'Tourisme régional'),
        # Nouveaux
        (r"\bIVV\b|\bInterprofession\s+de\s+la\s+Vigne\b", 'Promotion économique & terroir'),
        (r"\bVapeur\s+Val[\s-]de[\s-]Travers\b|\bVVT\b", 'Tourisme régional'),
    ],
    'culture': [
        (r"\bEquilibre\s+et\s+Nuithonie\b", 'Théâtre'),
        (r"\bFond\.\s+Hainard\b", 'Musique classique'),  # actually musée
        (r"\bETM\s+(?:-\s+)?École\s+des\s+musiques\s+actuelles?\b", 'Musique populaire / Jazz'),
        (r"\bFond\.\s+pour\s+le\s+développement\s+des\s+arts\b", 'Soutien artistique'),
        (r"\bFond\.\s+Guido\s+Comba\b", 'Soutien artistique'),
        (r"\bFond\.\s+Horopedia\b", 'Musées spécialisés'),
        (r"\bLa\s+Chaux-de-Fonds\s+capitale\b|\bCapitale\s+culturelle\s+suisse\b", 'Festival multi-disciplinaire'),
        (r"\bMaison\s+des\s+Amériques\b", 'Musées d\'histoire'),
        (r"\bMaison\s+d['\u2019]?Ailleurs\b", 'Musées spécialisés'),
        # Nouveaux après audit Passe 3
        (r"\bPôle\s+Musique\s+Sion\b", 'Musique classique'),
        (r"\bCORODIS\b|\bAssoc\.\s+CORODIS\b", 'Soutien artistique'),
        (r"\bKultur\s+im\s+Podium\b", 'Théâtre'),
        (r"\bBex\s+&\s+Arts\b|\bFond\.\s+Bex\b", 'Soutien artistique'),
        (r"\bGrand\s+Mirific\b", 'Festival multi-disciplinaire'),
        (r"\bTour\s+Vagabonde\b", 'Théâtre'),
        (r"\bPetit\s+Théâtre\s+de\s+Lausanne\b", 'Théâtre'),
        (r"\bPrix\s+de\s+Lausanne\b|\bArt\s+chorégraphique\b", 'Danse'),
        (r"\bSinfonietta\s+de\s+Lausanne\b", 'Musique classique'),
        (r"\bAssoc\.\s+CMA\b|\bCMA\s+Nyon\b", 'Musique classique'),
        (r"\bMusique\s+des\s+Lumières\b", 'Musique classique'),
        (r"\bTKM\b|\bThéâtre\s+Kléber[\s-]Méleau\b", 'Théâtre'),
        (r"\bAssoc\.\s+du\s+Théâtre\b", 'Théâtre'),
        (r"\bFond\.\s+OSR\b|\bOrchestre\s+de\s+la\s+Suisse\s+Romande\b", 'Musique classique'),
        (r"\bRencontres\s+Internationales\s+de\s+Folklore\b|\bRFI\b", 'Festival multi-disciplinaire'),
        (r"\bLes\s+Docks\b|\bFond\.\s+pour\s+les\s+musiques\s+actuelles\b|\bFMA\b", 'Musique populaire / Jazz'),
        (r"\bMaison\s+du\s+dessin\s+de\s+presse\b", 'Musées spécialisés'),
        (r"\bClub\s+44\b", 'Théâtre'),
        (r"\bCentre\s+Culturel\s+Neuchâtelois\b|\bCCN\b", 'Théâtre'),
        (r"\bEnsemble\s+Symphonique\s+Neuchâtel\b|\bESN\b", 'Musique classique'),
        (r"\bFond\.\s+Arc\s+en\s+Scène\b", 'Théâtre'),
        (r"\bCentre\s+culturel\s+ABC\b", 'Théâtre'),
        (r"\bDreamAgo\b", 'Soutien artistique'),
        (r"\bFerme[\s-]Asile\b", 'Soutien artistique'),
        (r"\bAssoc\.\s+Culture\s+Valais\b", 'Soutien artistique'),
        (r"\bFond\.\s+Visions\s+du\s+Réel\b", 'Cinéma'),
        (r"\bBelluard\s+Bollwerk\b", 'Festival multi-disciplinaire'),
        (r"\bLe\s+Temple\s+du\s+Polar\b", 'Festival multi-disciplinaire'),
        (r"\bCrans-Montana\s+Classics\b", 'Musique classique'),
        (r"\bFri[\s-]Son\b", 'Musique populaire / Jazz'),
        (r"\bBéjart\s+Ballet\b|\bBBL\b", 'Danse'),
        (r"\bFond\.\s+de\s+l['\u2019]?Hermitage\b", 'Musées spécialisés'),
        (r"\bFond\.\s+Plateforme\s+10\b", 'Musées spécialisés'),
        (r"\bFond\.\s+du\s+Festival\s+de\s+la\s+Cité\b", 'Festival multi-disciplinaire'),
        (r"\bFond\.\s+FIFDH\b", 'Cinéma'),
        (r"\bUsine\s+à\s+Gaz\b", 'Théâtre'),
        (r"\bL'avant-scène\s+Opéra\b|\bL\u2019avant-scène\s+Opéra\b", 'Musique classique'),
        (r"\bmarionNEttes\b", 'Théâtre'),
        (r"\bCentre\s+dramatique\b", 'Théâtre'),
        (r"\bArts\s+et\s+Spectacles\s+de\s+Vevey\b|\bThéâtre\s+Le\s+Reflet\b", 'Théâtre'),
        (r"\bThéâtre\s+(?:de\s+|du\s+)?Jorat\b", 'Théâtre'),
        (r"\bCinéforom\b", 'Cinéma'),
        (r"\bAssoc\.\s+des\s+cinémas?\s+romands?\b", 'Cinéma'),
        # Passe 5 — ajouts ensembles musique + festivals trouvés en sante catch-all 2024
        (r"\bEnsemble\s+Vocal\s+de\s+Lausanne\b|\bEVL\b", 'Musique classique'),
        (r"\bFAR\s+Festival\b", 'Festival multi-disciplinaire'),
        (r"\bJazzOnze\s*\+\s*Festival\b|\bJazz\s+Onze\s*\+\b", 'Musique populaire / Jazz'),
        (r"\bFrancomanias\b|\bLes\s+Francomanias\b", 'Musique populaire / Jazz'),
        (r"\bMontreux\s+Jazz\b|\bMJF\b", 'Musique populaire / Jazz'),
        (r"\bLeysin\s+Jazz\b", 'Musique populaire / Jazz'),
        (r"\bEnsemble\s+Vocal\b|\bChœur\s+\w", 'Musique classique'),
        (r"\bConcours\s+(?:Géza\s+)?Anda\b|\bClara\s+Haskil\b", 'Musique classique'),
        (r"\bPaléo\s+Festival\b|\bPaléo\b", 'Musique populaire / Jazz'),
    ],
    'social': [
        (r"\bFond\.\s+Phénix\b", 'Précarité / Pauvreté'),
        (r"\bATD[\s-]?Quart\s+Monde\b", 'Précarité / Pauvreté'),
        (r"\bUNHCR\b|\bSwitzerland\s+for\s+UNHCR\b", 'Migration / Intégration'),
        (r"\bFond\.\s+Immobilière\s+Privée\b", 'Précarité / Pauvreté'),  # logement social GE
        (r"\bAccueil\s+à\s+Bas\s+Seuil\b|\bABS\b", 'Précarité / Pauvreté'),
        (r"\bAssoc\.\s+Argos\b", 'Aide à la jeunesse'),  # protection victimes
        (r"\bCoopérative\s+Cité\s+Derrière\b", 'Précarité / Pauvreté'),  # logement Lausanne
        (r"\bMaison\s+d['\u2019]?enfants\b", 'Aide à la jeunesse'),
        (r"\bFEA\b|\bFond\.\s+pour\s+l['\u2019]?expression\s+associative\b",
         'Soutien général à l\'action associative'),
        # Nouveaux après audit Passe 3
        (r"\bFond\.\s+Partage\b", 'Précarité / Pauvreté'),  # aide alimentaire GE
        (r"\bUnions\s+Chrétiennes\b|\bUCG\b", 'Précarité / Pauvreté'),
        (r"\ble\s+C\.A\.R\.É\b|\bC\.A\.R\.É\b", 'Migration / Intégration'),
        (r"\bAssoc\.\s+SemoNord\b|\bSEMO\b", 'Précarité / Pauvreté'),  # mesure emploi
        (r"\bHome\s+(?:Saint\s+Pierre|St[\s-]Pierre)\b|\bPetershöfli\b", 'EMS & personnes âgées'),
        (r"\bLa\s+Rozavère\b|\bRésidence\s+(?:de\s+|du\s+)?\w+|\bEMS\s+\w", 'EMS & personnes âgées'),
        (r"\bFond\.\s+de\s+l['\u2019]?Orme\b", 'EMS & personnes âgées'),
        (r"\bMère\s+Sofia\b", 'Précarité / Pauvreté'),
        (r"\bEducation\s+Familiale\b", 'Aide à la jeunesse'),
        (r"\bSolidarité\s+Femmes\b|\bMalley\s+Prairie\b", 'Égalité / Femmes / LGBT'),
        (r"\bCEFORI\b", 'Précarité / Pauvreté'),
        (r"\bcentre\s+social\s+protestant\b|\bCSP\b", 'Précarité / Pauvreté'),
    ],
    'sports': [
        (r"\bPro\s+Junior\b", 'Multi-sports'),
        (r"\b(?:Assoc|Association)\s+Cantonale\s+\w+\s+de\s+(?:Gymnastique|Football|Tennis|Tir)\b",
         'Multi-sports'),
        (r"\bCabane\s+des\s+Bossons\b|\bBlécherette\b", 'Aviation / Sports aériens'),
        # Nouveaux après audit Passe 3
        (r"\bAssoc\.\s+Cantonale\s+\w+\s*,?\s+Football\b", 'Football'),
        (r"\bJura\s+Bike\s+Park\b", 'Cyclisme'),
        (r"\bWorldcup\s+Veysonnaz\b|\bChampionnats?\s+du\s+monde\s+de\s+Ski\b|\bFIS\s+Ski\s+Alpin\b", 'Ski / sports d\'hiver'),
        (r"\bLions\s+de\s+Genève\b", 'Basketball'),
        (r"\bGenève\s+Snowsports\b", 'Ski / sports d\'hiver'),
        (r"\bSwiss\s+Volley\b", 'Volleyball'),
    ],
}


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
        
        # ─── PASS 2.5: apply EXTRA_PATTERNS for high-value entries ─────
        extra = EXTRA_PATTERNS.get(classif, [])
        compiled_extra = [(re.compile(p, re.IGNORECASE), sc) for p, sc in extra]
        pass2_5_recovered = 0
        pass2_5_chf = 0
        if compiled_extra:
            for y in YEARS:
                for i, (entry, sub_cat) in enumerate(classifs_by_year[y]):
                    if sub_cat is not None:
                        continue
                    text = (entry.get('nom') or '') + ' ' + (entry.get('description') or '')
                    for pat, target in compiled_extra:
                        if pat.search(text):
                            classifs_by_year[y][i] = (entry, target)
                            pass2_5_recovered += 1
                            pass2_5_chf += entry['montant_CHF']
                            break
            print(f"  PASS 2.5 extra patterns: {pass2_5_recovered} entries / {pass2_5_chf:,} CHF")
        
        # ─── PASS 3: 'Action générale' pour les entries du secteur officiel
        # restantes en Autres (= bonne entrée, juste pas de sous-catégorie précise) ─
        # Applicable uniquement pour les sectoral classifications (où on filtre
        # par secteur officiel en amont). Pas pour culture/sports/social qui
        # classifient déjà à un niveau supérieur.
        SECTOR_NAMES_REVERSE = {
            'culture': 'Culture',
            'sports': 'Sport',
            'social': 'Action sociale et personnes âgées',
            'environnement': 'Environnement',
            'sante': 'Santé et handicap',
            'jeunesse': 'Jeunesse et éducation',
            'patrimoine': 'Conservation du patrimoine',
            'formation': 'Formation et recherche',
            'promotion': 'Promotion, tourisme et développement',
        }
        target_sector = SECTOR_NAMES_REVERSE.get(classif)
        pass3_recovered = 0
        pass3_chf = 0
        if target_sector:
            # Label pour la sous-cat "catch-all"
            CATCHALL_LABELS = {
                'culture': 'Soutien général à la culture',
                'sports': 'Soutien général au sport',
                'social': "Soutien général à l'action sociale",
                'environnement': "Soutien général à l'environnement",
                'sante': 'Soutien général à la santé / handicap',
                'jeunesse': "Soutien général à la jeunesse",
                'patrimoine': 'Soutien général au patrimoine',
                'formation': "Soutien général à la formation / recherche",
                'promotion': 'Soutien général à la promotion / tourisme',
            }
            catchall_label = CATCHALL_LABELS[classif]
            for y in YEARS:
                for i, (entry, sub_cat) in enumerate(classifs_by_year[y]):
                    if sub_cat is None and entry.get('secteur') == target_sector:
                        classifs_by_year[y][i] = (entry, catchall_label)
        if target_sector:
            print(f"  PASS 3 catch-all secteur: {pass3_recovered} entries / {pass3_chf:,} CHF")
        
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
                # all_entries: top 200 by amount (suffisant pour ~99% des cats,
                # protège contre les cats énormes comme 'Soutien général à X')
                all_sorted = sorted(b['samples'], key=lambda s: -s['montant_CHF'])
                cat_list.append({
                    'name': name,
                    'count': b['count'],
                    'total_chf': b['total_chf'],
                    'mean_chf': b['total_chf'] // b['count'] if b['count'] else 0,
                    'cantons': {c: dict(d) for c, d in b['cantons'].items()},
                    'samples': all_sorted[:5],
                    'all_entries': all_sorted[:200],  # NEW: pour drill-down dans viz
                })
            cat_list.sort(key=lambda c: -c['total_chf'])
            
            # Meta
            total_entries = len(entries_with_cat)
            total_chf = sum(e['montant_CHF'] for e, _ in entries_with_cat)
            
            # Détecter la cat catch-all 'Soutien général à X' (si présente)
            catchall_cats = [c for c in cat_list if c['name'].startswith('Soutien général')]
            catchall_chf = sum(c['total_chf'] for c in catchall_cats)
            
            # Vraie classification précise = tout sauf Autres et catch-all
            precise_classified = sum(c['count'] for c in cat_list
                                     if c['name'] != 'Autres' and not c['name'].startswith('Soutien général'))
            precise_classified_chf = sum(c['total_chf'] for c in cat_list
                                         if c['name'] != 'Autres' and not c['name'].startswith('Soutien général'))
            # Classification "secteur" = tout sauf Autres (inclut catch-all)
            total_classified = sum(c['count'] for c in cat_list if c['name'] != 'Autres')
            total_classified_chf = sum(c['total_chf'] for c in cat_list if c['name'] != 'Autres')
            
            meta = {
                'classif': classif,
                'year': y,
                'source': f'brb{y}_full.json',
                'method': 'Pattern matching (PASS 1) + cross-year memo (PASS 2) + sector catch-all (PASS 3)',
                'date': '2026-06-04',
                'total_entries': total_entries,
                'total_chf': total_chf,
                # NEW: 2 separate metrics
                'precise_classified_entries': precise_classified,
                'precise_classified_chf': precise_classified_chf,
                'pct_chf_precisely_classified': round(100 * precise_classified_chf / max(1, total_chf), 1),
                'pct_chf_classified': round(100 * total_classified_chf / max(1, total_chf), 1),
                'total_entries_classified': total_classified,
                'total_chf_classified': total_classified_chf,
                'catchall_chf': catchall_chf,
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
