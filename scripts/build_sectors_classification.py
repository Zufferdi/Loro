#!/usr/bin/env python3
"""
build_sectors_classification.py — Pass 8 — 6 remaining sector classifications
==============================================================================

Generates classification JSONs for the 6 sectors NOT already covered by
culture / sports / social scripts:
  - Environnement
  - Santé et handicap
  - Jeunesse et éducation
  - Conservation du patrimoine
  - Formation et recherche
  - Promotion, tourisme et développement

Approach (different from culture/sport/social, which ignore the `secteur` field):
  Filter entries by the OFFICIAL `secteur` field first, then classify via
  keyword patterns. This avoids false positives across sectors (e.g. "ferme"
  could mean farm in Environnement or pedagogical farm in Jeunesse).

Generates BOTH 2024 and 2025 JSON outputs per sector.

Output naming convention:
  docs/data/{slug}_classification.json       (2025)
  docs/data/{slug}_classification_2024.json  (2024)

  Where {slug} is environnement / sante / jeunesse / patrimoine /
                  formation / promotion
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'docs' / 'data'

# ============================================================================
# Sector configurations
# ============================================================================
# Each sector: official_name, slug, and ordered list of (category, regex)
# patterns. First match wins, fallback "Autres" for unmatched in-sector entries.

SECTORS = {

    # ────────────────────────────────────────────────────────────────────────
    'Environnement': {
        'slug': 'environnement',
        'patterns': [
            ('Faune & biodiversité',
                r'\b(faune|wildlife|oiseaux?|chauves?[\s-]souris|abeilles?|insectes?|'
                r'amphibiens?|reptiles?|mammifères?|biodiversité|salamandre|'
                r'pro\s+natura|migrateurs|hérisson|loup|lynx|castor|spa\b|protection\s+animale)\b'),
            ('Flore & botanique',
                r'\b(flore|botanique|jardin\s+botanique|herbier|arbres?|plantes?|'
                r'forêt|reboisement|haies?|verger|arboretum|murithienne)\b'),
            ('Eau / Lacs / Rivières',
                r'\b(eau|lac\b|lacs\b|rivière|cours\s+d\'eau|gorges|fontaine|étang|'
                r'pisciculture|truite|poisson|natur(?:al|el)s?\s+aquatique|zones?\s+humides?)\b'),
            ('Montagne & Alpages',
                r'\b(alpage|alpes?\b|montagne|sommet|cabane|refuge|sentier|via\s+ferrata|'
                r'glaciers?|chemins?\s+de\s+montagne|estivage)\b'),
            ('Parcs naturels',
                r'\b(parc\s+(?:naturel|national|régional)|réserve\s+naturelle|biotope|'
                r'pfyn|finges|chasseral|jura\s+vaudois|gruyère\s+pays|doubs)\b'),
            ('Énergie & climat',
                r'\b(énergie|climat|carbone|co2|solaire|photovoltaïque|éolien|'
                r'transition\s+énergétique|renouvelable|décarbonation)\b'),
            ('Déchets & recyclage',
                r'\b(déchets?|recyclage|compost|zero\s+waste|réemploi|circulaire|'
                r'écobilan|tri\s+sélectif|économie\s+circulaire|ecopaper)\b'),
            ('Agriculture durable',
                r'\b(agriculture|paysans?|agro|fermes?|maraîchage|permaculture|'
                r'mellifera|bio\b|biodynamie|semences?|prométerre|carefarming)\b'),
            ('Mobilité douce',
                r'\b(pro\s+vélo|mobilité|cyclable|piéton|bike\s+to|covoiturage)\b'),
            ('Éducation & sensibilisation',
                r'\b(sensibilisation|nature\s+pédagog|éducation\s+environn|fête\s+de\s+la\s+nature|'
                r'magasin\s+du\s+monde|sentier\s+pédagog|découverte\s+nature)\b'),
        ],
    },

    # ────────────────────────────────────────────────────────────────────────
    'Santé et handicap': {
        'slug': 'sante',
        'patterns': [
            ('Handicap mental & autisme',
                r'\b(handicap\s+mental|asa\s+handicap|insieme|autisme|trisomie|'
                r'déficience\s+intellectuelle|cap\s+loisirs|cerebral|atelier\s+manus)\b'),
            ('Handicap physique / fauteuil',
                r'\b(fauteuil\s+roulant|paraplég|tétraplég|hémiplég|handicap\s+physique|'
                r'mobilité\s+réduite|transport\s+handicap|cérébral|sclérose|myopath|'
                r'pro\s+infirmis|forum\s+handicap|handisport)\b'),
            ('Surdité & malentendants',
                r'\b(sourd|surdi|malentendant|langue\s+des\s+signes|cochléaire|'
                r'forom\s+écoute|écoute\s+voir)\b'),
            ('Cécité & malvoyants',
                r'\b(aveugle|malvoyant|cécité|déficient\s+visuel|braille|ucba\b)\b'),
            ('Santé mentale & psychiatrie',
                r'\b(santé\s+mentale|psychiatr|schizophrén|dépression|pro\s+mente\s+sana|'
                r'afaap|pleine\s+conscience|détresse\s+psych|positive\s*minder|burn[\s-]?out|'
                r'minds\b|parole\b|afaap|traversées|stop\s+suicide)\b'),
            ('Addictions',
                r'\b(addiction|alcool|drogue|toxicomanie|tabac|fumeurs?|sevrage|'
                r'tremplin|première\s+ligne|nuit\s+blanche|méthadone|cannabis|cannabinothèque|'
                r'cipret|lvt\b|prévention\s+addiction)\b'),
            ('Cancer & oncologie',
                r'\b(cancer|oncolog|tumeur|leucémie|chimio|mammograph|cytologie|'
                r'ligue.*cancer|ramer\s+en\s+rose)\b'),
            ('Diabète & maladies chroniques',
                r'\b(diabèt|diabète|fibromyalg|sclérose|crohn|colite|rhumatis|'
                r'parkinson|alzheimer|maladie\s+chronique|allergi)\b'),
            ('Maladies rares',
                r'\b(maladie\s+rare|maladies\s+rares|orphelin|maraval|ela\b)\b'),
            ('Aphasie / AVC',
                r'\b(aphasi|avc|attaque\s+cérébrale|accident\s+vasculaire)\b'),
            ('Soins palliatifs',
                r'\b(palliati[fv]|fin\s+de\s+vie|deuil|accompagn.*mort|paix\s+du\s+soir|'
                r'accovimo)\b'),
            ('Aide & assistance médicale',
                r'\b(médecins\s+du\s+monde|sans\s+frontière|terre\s+des\s+hommes|'
                r'aide\s+médicale|secours|sauvetage|samaritains|sisl\b|nez\s+rouge|'
                r'main\s+tendue|tél\s+143|special\s+olympics|chuv|paint\s+a\s+smile|'
                r'croix[\s-]?rouge|caritas)\b'),
            ('Prévention & promotion santé',
                r'\b(prévention|promotion\s+santé|dépistage|vaccin|sensibilisation\s+santé|'
                r'mayd?\s+less\s+sugar|nutrition|alimentation\s+saine|stop\s+skin\s+cancer)\b'),
            ('Chiens & zoothérapie',
                r'\b(chien.*assistance|chien.*thérapie|zoothérapie|chiens?\s+spécialisés?|'
                r'chiki|arthanis|farah[\s-]?dogs|medical\s+flair)\b'),
        ],
    },

    # ────────────────────────────────────────────────────────────────────────
    'Jeunesse et éducation': {
        'slug': 'jeunesse',
        'patterns': [
            ('Petite enfance & crèches',
                r'\b(crèche|kita|kinderkrippe|garderie|petite\s+enfance|nurserie|'
                r'jardin\s+d\'enfants|kindergarten|spielgruppe|halte[\s-]?jeux|'
                r'centre\s+de\s+vie\s+enfantine|cve\b|maternelle|premiers\s+pas|toupti|'
                r'faje\b|fond\.\s+pour\s+l\'accueil\s+de\s+jour|accueil\s+de\s+jour\s+des\s+enfants|'
                r'feuillère)\b'),
            ('Accueil parascolaire',
                r'\b(parascol|uape\b|accueil\s+extrascol|tagesstrukturen|'
                r'accueil\s+enfants|familles\s+accueil|accueil\s+familial|afj\b|'
                r'familientreff|famyl|kibelac|famiya|programme\s+culture\s*&?\s*école)\b'),
            ('Ludothèques & jeux',
                r'\b(ludothèque|ludothek|ludimania|ludimani|ludothèq|jeu.*libre|'
                r'jouets|jeux\s+et\s+activités)\b'),
            ('Scoutisme',
                r'\b(scouts?|scoutisme|éclaireuses?|éclaireurs?|pfadi|jubla|'
                r'mouvement\s+scout|bula|kape)\b'),
            ('Maisons de jeunes & quartier',
                r'\b(maison\s+(?:de\s+)?(?:la\s+)?(?:jeunes|quartier)|centre\s+(?:de\s+)?(?:loisirs|quartier|jeunes)|'
                r'kallo|sleep[\s-]?in|undertown|aslec|centre\s+aéré)\b'),
            ('Passeport vacances & camps',
                r'\b(passeport[\s-]?vacances|ferienpass|camp\s+(?:de\s+)?vacances|'
                r'colonie|colonies|camp\s+d\'été|camp\s+d\'hiver|croque\s+vacances|'
                r'feriencamp|joie\s+de\s+vivre)\b'),
            ('Soutien scolaire & lecture',
                r'\b(lecture|illetrisme|illettrisme|lire\s+et\s+(?:écrire|faire)|'
                r'soutien\s+scolaire|alphabétisation|décrochage|bibliobus|aide\s+école|'
                r'pip\b|lanterne\s+magique|graines?\s+de\s+(?:génie|paix|citoyen))\b'),
            ('Musique & arts jeunes',
                r'\b(éveil\s+musical|chœur\s+(?:d\'?)?enfants|chœur\s+(?:de\s+)?jeunes|'
                r'maîtrise|orchestre\s+(?:des\s+)?jeunes|école\s+(?:de\s+)?musique|'
                r'cadets?|conservatoire\s+enfants|musikkurs|jugendmusik|jeunes\s+musiciens|'
                r'verbier\s+junior|jeunesses\s+musicales)\b'),
            ('Cirque & théâtre jeunes',
                r'\b(cirque\s+(?:pour\s+)?(?:les\s+)?(?:enfants|jeunes)|école\s+de\s+cirque|'
                r'cirq[ou]|fun.*bulle|toamême|labo.*cirque|petit\s+théâtre|théâtre\s+jeune\s+public|'
                r'tajum)\b'),
            ('Soutien parental',
                r'\b(parentalité|parent.*enfant|jeunesparents|école\s+des\s+parents|'
                r'éducation\s+familiale|panaae|pro\s+junior|pro\s+juventute|point\s+rencontre)\b'),
            ('Insertion professionnelle',
                r'\b(insertion\s+professionnelle|formation\s+professionnelle\s+(?:jeune|initiale)|'
                r'avenir\s+(?:professionnel|formation)|orientation\s+professionnelle|seedorf|'
                r'apprentissage|stage)\b'),
            ('Aide à la jeunesse',
                r'\b(stop\s+suicide|prévention\s+jeunes|harcèlement\s+scolaire|'
                r'fontanelle|reper|fontanelle|jeunesse\s+en\s+difficulté|cvaj\b|relais[\s-]?jrc|'
                r'aide\s+jeunesse|fond\.\s+officielle\s+de\s+la\s+jeunesse)\b'),
        ],
    },

    # ────────────────────────────────────────────────────────────────────────
    'Conservation du patrimoine': {
        'slug': 'patrimoine',
        'patterns': [
            ('Patrimoine religieux',
                r'\b(paroisse|église|eglise|chapelle|abbatiale|cathédral|kirchenrat|'
                r'monastère|couvent|abbaye|cure|presbytère|basilique|chœur\s+religieux|'
                r'cloître|saint[\s-]|sainte[\s-]|hauterive|romainmôtier|temple\b|capucin|'
                r'kapuzin|franciscain)\b'),
            ('Châteaux & forts',
                r'\b(château|schloss|forteresse|fort\b|donjon|tour\s+(?:historique|médiéval)|'
                r'castel|gruyères|valère|chillon|aigle|grandson|tourbillon|sarra|sallaz)\b'),
            ('Musées historiques',
                r'\b(musée\s+(?:d\'|de\s+)?(?:histoire|gruérien|valaisan|romand|paysan|'
                r'patrimoine|patriot|patriotique)|fond\.\s+(?:du\s+)?musée|stiftung\s+museum|'
                r'manoir.*ville|maison.*histoire)\b'),
            ('Archéologie',
                r'\b(archéolog|archeolog|aventicum|romain|gallo[\s-]romain|paléolithique|'
                r'néolithique|fouilles?|vestiges?|site\s+archéo|martigny\s+romain|'
                r'octodure|pro\s+vallon|palafittes?)\b'),
            ('Patrimoine alpestre & bisses',
                r'\b(bisses?|suone|alpages?\s+historique|patrimoine\s+alpin|'
                r'mayens|raccards?|grangettes\s+(?:historique|patrimoine))\b'),
            ('Patrimoine industriel & rural',
                r'\b(moulin|forge|four\s+banal|saline|mines?|industrie\s+historique|'
                r'patrimoine\s+(?:industriel|rural|vigneron|vinicole|agricole)|grangé)\b'),
            ('Histoire & archives',
                r'\b(archives|sté\s+d\'histoire|histoire\s+du\s+canton|société\s+d\'histoire|'
                r'cercle\s+d\'études?\s+histor|chronique|annales|histor.*publication|'
                r'glossaire|geschichtsblätter|geschichtsforsch)\b'),
            ('Patois & traditions',
                r'\b(patois|traditions?|folklor|costumes?\s+(?:traditionnel|régional)|'
                r'fifres|tambours|cors?\s+des\s+alpes|fête\s+(?:traditionnelle|alpestre)|'
                r'fête\s+(?:fédérale|cantonale|romande)|jodler|trachten)\b'),
            ('Publications patrimoine',
                r'\b(publication\s+(?:historique|patrimoine)|ouvrage\s+(?:historique|patrimoine)|'
                r'éditions?\s+patrimoine|monographie|livre.*histoire|nouvelle\s+revue)\b'),
            ('Sauvegarde du bâti',
                r'\b(restauration|rénovation\s+(?:historique|patrimoniale)|conservation\s+(?:du\s+)?bâti|'
                r'sauvegarde\s+(?:du\s+)?patrimoine|patrimoine\s+bâti|architecture\s+ancienne|'
                r'orgue|orgues?\s+historique|cloches?\s+historique)\b'),
        ],
    },

    # ────────────────────────────────────────────────────────────────────────
    'Formation et recherche': {
        'slug': 'formation',
        'patterns': [
            ('Université & hautes écoles',
                r'\b(université|université\s+de|epfl|hep\b|haute\s+école|hes[\s-]?so|'
                r'unil\b|unige|university|fond\.\s+epfl|fond\.\s+chuv|hesav\b|'
                r'idiap|institut\s+universit)\b'),
            ('Recherche scientifique',
                r'\b(recherche\s+scientifique|science\b|sciences?\b|innovation|laboratoire|'
                r'institut\s+(?:de\s+)?recherche|csem\b|fsrm|space\s+exploration|'
                r'observatoire|microtechnique|reatch|pathologie\s+2000)\b'),
            ('Recherche médicale',
                r'\b(recherche\s+médicale|chuv|solidar\s+immun|pathologie|fond\.\s+chuv|'
                r'recherche\s+(?:en\s+)?(?:santé|médecine)|hôpital\s+universitaire)\b'),
            ('Salons & orientation métiers',
                r'\b(salon\s+(?:des\s+)?métiers?|orientation\s+professionnelle|cité\s+(?:des\s+)?métiers|'
                r'capa[\'\s]?cité|metiers?|découverte\s+métiers|expo\s+métiers)\b'),
            ('Formation artisanale',
                r'\b(artisanat|artisan|métiers?\s+manuels?|école\s+(?:des?\s+)?(?:vitrail|'
                r'arts\s+appliqués|métiers\s+d\'art)|bakery\s+trophy|boulanger|confiseur)\b'),
            ('Apprentissage & formation continue',
                r'\b(apprentissage|formation\s+continue|université\s+populaire|volkshochschule|'
                r'connaissance\s+3|bildungshaus|école\s+supérieure)\b'),
            ('Recherche & innovation tech',
                r'\b(start[\s-]?up|innovation\s+technol|fond\.\s+the\s+ark|fond\.\s+ipt|'
                r'incubateur|fablab|innopole|microcity|design\s+research)\b'),
            ('Bibliothèques & médiations savoir',
                r'\b(bibliothèque\s+(?:scientifique|spécialisée|universitaire)|'
                r'sociétés?\s+savante|académie\s+suisse|club\s+44|cercle\s+savant)\b'),
        ],
    },

    # ────────────────────────────────────────────────────────────────────────
    'Promotion, tourisme et développement': {
        'slug': 'promotion',
        'patterns': [
            ('Tourisme régional',
                r'\b(tourisme|valais.*wallis\s+promotion|vaud\s+promotion|fribourg\s+région|'
                r'destination|valrando|valais\s+rando|tourist|verkehrsverein|crans[\s-]montana\s+tourisme)\b'),
            ('Sentiers & randonnée',
                r'\b(rando(?:nnée)?|sentier|wander|chemin\s+de\s+(?:randonnée|grande))\b'),
            ('Cyclo & courses populaires',
                r'\b(tour\s+de\s+romandie|tour\s+de\s+suisse|tour\s+des\s+stations|'
                r'tour\s+du\s+pays|sierre[\s-]zinal|patrouille|marathon\s+populaire|'
                r'morat[\s-]fribourg|grand\s+raid)\b'),
            ('Manifestations populaires',
                r'\b(slowup|fête\s+(?:du\s+vin|des\s+vendanges|de\s+la\s+(?:châtaigne|musique))|'
                r'foire\s+du\s+valais|foire\s+(?:régionale|cantonale)|braderie|cortège|'
                r'manif.*tradition|gymnaestrada)\b'),
            ('Parcs régionaux & nature',
                r'\b(parc\s+(?:naturel\s+)?régional|jura\s+vaudois|gruyère\s+pays|'
                r'doubs|chasseral|pfyn|finges|landschaftspark|nature\s+et\s+territoire)\b'),
            ('Cabanes & infrastructures montagne',
                r'\b(cabane\s+(?:cas\b|cas[\s-])|cas\s+section|refuge|via\s+ferrata|'
                r'club\s+alpin\s+suisse|kletterhalle\s+touristique)\b'),
            ('Promotion économique & terroir',
                r'\b(terroir|aoc\b|aop\b|igp\b|raclette\s+valais|gruyère\s+aop|'
                r'fromage\s+aop|jardinsuisse|interprofession|cave\s+coopérative)\b'),
            ('Promotion culture régionale',
                r'\b(culture\s+région|découverte\s+région|rayonnement|promotion\s+culturelle|'
                r'images?\s+région|patrimoine\s+région.*promotion)\b'),
            ('Salons & expositions thématiques',
                r'\b(salon\s+(?:du\s+livre|du\s+goût|de\s+l\'auto|du\s+vin|de\s+l\'hôtellerie)|'
                r'comptoir|exposition\s+(?:régional|cantonal|économique|professionnel))\b'),
        ],
    },
}


# ============================================================================
# Generic classifier
# ============================================================================

def classify_entry(entry: dict, compiled_patterns: list) -> str | None:
    """Return category for entry using first-match wins, or None if no match."""
    nom = entry.get('nom', '') or ''
    desc = entry.get('description', '') or ''
    text = nom + ' ' + desc
    for name, pat in compiled_patterns:
        if pat.search(text):
            return name
    return None


def build_classification(sector_name: str, slug: str, patterns: list,
                         input_path: Path, output_path: Path) -> dict:
    """Build classification for one sector + one year."""
    with open(input_path, encoding='utf-8') as f:
        data = json.load(f)
    entries = data['entries']

    # Pre-compile
    compiled = [(name, re.compile(pat, re.IGNORECASE)) for name, pat in patterns]

    # Filter entries by official sector
    sector_entries = [e for e in entries if e.get('secteur') == sector_name]
    total_chf_sector = sum(e.get('montant_CHF', 0) or 0 for e in sector_entries)

    # Classify
    buckets = defaultdict(lambda: {
        'count': 0, 'total_chf': 0, 'samples': [],
        'cantons': defaultdict(lambda: {'count': 0, 'total_chf': 0})
    })

    for e in sector_entries:
        cat = classify_entry(e, compiled) or 'Autres'
        amt = e.get('montant_CHF', 0) or 0
        b = buckets[cat]
        b['count'] += 1
        b['total_chf'] += amt
        c = e.get('canton', '')
        b['cantons'][c]['count'] += 1
        b['cantons'][c]['total_chf'] += amt
        sample_nom = e.get('nom', '')
        if sample_nom and sample_nom not in [s['nom'] for s in b['samples']]:
            b['samples'].append({
                'nom': sample_nom,
                'ville': e.get('ville'),
                'canton': c,
                'montant_CHF': amt,
            })

    # Prepare output
    categories = []
    for name, b in buckets.items():
        categories.append({
            'name': name,
            'count': b['count'],
            'total_chf': b['total_chf'],
            'mean_chf': b['total_chf'] // b['count'] if b['count'] else 0,
            'cantons': {c: dict(d) for c, d in b['cantons'].items()},
            'samples': sorted(b['samples'], key=lambda s: -s['montant_CHF'])[:5],
        })
    categories.sort(key=lambda s: -s['total_chf'])

    total_classified_count = sum(c['count'] for c in categories if c['name'] != 'Autres')
    total_classified_chf = sum(c['total_chf'] for c in categories if c['name'] != 'Autres')

    out = {
        '_meta': {
            'sector': sector_name,
            'sector_slug': slug,
            'source': str(input_path.relative_to(ROOT)),
            'method': f'Filter by official secteur="{sector_name}", then keyword classification on nom + description',
            'date': '2026-06-04',
            'version': 'v13.10',
            'total_entries_sector': len(sector_entries),
            'total_chf_sector': total_chf_sector,
            'total_entries_classified': total_classified_count,
            'total_chf_classified': total_classified_chf,
            'pct_entries_classified': round(100 * total_classified_count / max(1, len(sector_entries)), 1),
            'pct_chf_classified': round(100 * total_classified_chf / max(1, total_chf_sector), 1),
        },
        'categories': categories,
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return out['_meta']


def main():
    for sector_name, cfg in SECTORS.items():
        slug = cfg['slug']
        patterns = cfg['patterns']
        print(f"\n{'='*70}\n{sector_name}\n{'='*70}")
        for year, suffix in [('2025', ''), ('2024', '_2024'), ('2023', '_2023')]:
            inp = DATA / f'brb{year}_full.json'
            outp = DATA / f'{slug}_classification{suffix}.json'
            meta = build_classification(sector_name, slug, patterns, inp, outp)
            print(f"  {year}: {meta['total_entries_classified']}/{meta['total_entries_sector']} entries "
                  f"({meta['pct_entries_classified']}%) → "
                  f"{meta['total_chf_classified']:>11,} / {meta['total_chf_sector']:>11,} CHF "
                  f"({meta['pct_chf_classified']}%) → {outp.name}")


if __name__ == '__main__':
    main()
