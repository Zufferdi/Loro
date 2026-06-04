#!/usr/bin/env python3
"""
build_culture_classification.py — Pass 9 (v13.10) — Culture sub-categorization
================================================================================

Same approach as build_sport_classification.py but for cultural sub-domains.
Classifies BRB entries by specific cultural genre using keyword patterns on
nom + description (ignoring the unreliable secteur field).

Output: docs/data/culture_classification.json
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / 'docs' / 'data' / 'brb2025_full.json'
OUTPUT = ROOT / 'docs' / 'data' / 'culture_classification.json'

# Ordered from MOST specific (rare keywords, narrow genres) to LEAST specific
# (broad keywords like "festival" that catch many remaining entries).
# Each entry matches AT MOST one category (first match wins).
CULTURE_PATTERNS = [
    # Audiovisuel — very specific keywords
    ('Cinéma / Audiovisuel',
     r'\b(cinéma|cinema|cinémathèque|cinematheque|cinéforom|cinetoile|cinétoile|'
     r'festival\s+(international\s+)?(du\s+)?film|'
     r'films?\s+(documentaire|d\'animation)|FIFF\b|NIFFF\b|GIFF\b|FIFDH\b|'
     r'Visions\s+du\s+Réel|festival\s+(du\s+)?cinéma|cinémas\s+romands|'
     r'audiovisuel|production\s+audiovisuel|courts?\s+métrages?|long\s+métrage)\b'),

    # Danse — distinctive vocabulary
    ('Danse',
     r'\b(danse\b|danses|ballet|chorégrap|tanzhaus|dancer|danseur|danseuse|'
     r'compagnie\s+de\s+danse|festival\s+de\s+danse|danse\s+contemporaine|hip-?hop\s+danse|'
     r'flamenco|tango|capoeira)\b'),

    # Cirque / Arts de la rue
    ('Cirque / Arts de la rue',
     r'\b(cirque|arts\s+de\s+la\s+rue|marionnette|jonglerie|funambule|clown\b|clownesque|'
     r'arts\s+circassiens|festival\s+(des\s+)?arts\s+de\s+la\s+rue)\b'),

    # Photographie — distinctive
    ('Photographie',
     r'\b(photographie\b|photographique|photographe|festival\s+(de\s+)?photo)\b'),

        # Musique classique — orchestres de chambre (avant Musique classique générique)
    ('Orchestres de chambre',
     r"\b(orchestre\s+de\s+chambre|orchestre\s+de\s+ch\.|"
     r"\bOCL\b|\bOCG\b|\bOCJ\b|\bOCV\b|\bOCF\b|"
     r"camerata|sinfonietta|chamber\s+orchestra|"
     r"orchestre\s+de\s+chambre\s+de\s+\w+|"
     r"orchestre\s+de\s+chambre\s+fribourgeois|"
     r"orchestre\s+de\s+chambre\s+jurassien|"
     r"orchestre\s+de\s+chambre\s+des\s+étudiant)\b"),

    # Musique classique — orchestres, opéra, chœurs
    ('Musique classique',
     r"\b(orchestre|philharmonique|symphonique|opéra\b|opera\b|opérette|"
     r"chœur|choeur|chorale\b|chorales|ensemble\s+vocal|musique\s+de\s+chambre|"
     r"musique\s+classique|musique\s+ancienne|musique\s+sacrée|"
     r"concert\s+(choral|d'orgue|sacré)|conservatoire\s+(de\s+|populaire|cantonal)|"
     r"harmonie\s+municipale|chant\s+choral|sonate|symphonie|récital)\b"),

    # Musique populaire / Jazz / Rock
    ('Musique populaire / Jazz',
     r'\b(jazz|rock\b|pop\s+music|hip-?hop\b|fanfare|brass\s+band|musique\s+actuelle|'
     r'fête\s+de\s+la\s+musique|musique\s+du\s+monde|reggae|électro\b|electro\b|metal\b|'
     r'rap\b|chanson\b|chansonnier|festival\s+(de\s+)?jazz|festival\s+(de\s+)?rock|'
     r'festival\s+(de\s+la\s+)?musique|musique\s+populaire)\b'),

    # Théâtre — distinctive
    ('Théâtre',
     r"\b(théâtre|théatre|théâtral|comédie\b|comédien|comédienne|"
     r"art\s+dramatique|spectacle\s+vivant|pièce\s+(de\s+)?théâtre|"
     r"scène\s+nationale|TPR\b|théâtre\s+de\s+|festival\s+de\s+théâtre|"
     r"compagnie\s+théâtrale|drame\b|tragédie|metteur\s+en\s+scène)\b"),

    # Littérature / Édition / Bibliothèques
    ('Littérature / Édition',
     r"\b(librairie\b|maison\s+d'édition|éditions?\s+(de\s+|du\s+|le\s+|la\s+|les\s+)?[A-Z]|"
     r"écrivain|écrivaine|poésie|poète|poétique|littérature|littéraire|"
     r"salon\s+du\s+livre|bibliothèque\b|médiathèque|biennale\s+(de\s+(la\s+)?)?poésie|"
     r"rencontres?\s+littéraires?|festival\s+(de\s+|du\s+)?livre|festival\s+littéraire|"
     r"prix\s+littéraire|nouvelle\s+littéraire)\b"),

    # Musée — must come BEFORE patrimoine/expo to catch "Musée Pierre Gianadda"
    ('Musée',
     r'\b(musée\b|musées\b|museum\b|fond\.\s+pierre\s+gianadda|'
     r'plateforme\s+10|hermitage\b|kunsthaus|kunsthalle)\b'),

    # Patrimoine bâti / Restauration
    ('Patrimoine bâti',
     r"\b(restauration\s+(de\s+|du\s+|d\'|de\s+l\')?(chapelle|église|eglise|abbaye|temple|façade|"
     r"mur|toit|monument|orgue|cloche|patrimoine|fontaine|tour|cabane)|"
     r"(rénovation|réaménagement|assainissement)\s+(du\s+|de\s+la\s+|de\s+l['\u2019])?(église|eglise|temple|chapelle|abbaye|"
     r"clocher|patrimoine)|"
     r"sauvegarde\s+(du\s+|de\s+la\s+)?(patrimoine|château|chapelle|église|temple|monument)|"
     r"monument\s+historique|patrimoine\s+(bâti|culturel|architectural|historique)|"
     r"église\s+(protestante|anglicane|catholique|réformée)|paroisse\s+catholique|"
     r"château\b|ruines\b|conservation\s+(des\s+|du\s+)?(temples?|biens\s+culturels|monuments))\b"),

    # Arts visuels / Exposition / Galerie
    ('Arts visuels',
     r'\b(peinture|peintre\b|sculpture|sculpteur|sculptrice|art\s+contemporain|'
     r'arts\s+plastiques|arts\s+visuels|galerie\s+(d\'|de\s+)?art|biennale\s+d\'art|'
     r'exposition\s+(d\'|de\s+)?(art|peinture|sculpture|photo|design)|'
     r'centre\s+d\'art|art\s+brut|gravure)\b'),

    # Médias
    ('Médias',
     r'\b(radio\s+(régionale|locale|associative|romande)|télévision\s+(régionale|locale|romande)|'
     r'canal\s*9|kanal\s*9|leman\s+bleu|la\s+télé\b|'
     r'magazine\s+(culturel|de\s+culture)|presse\s+écrite|webzine|podcast\s+culturel)\b'),

    # Centres culturels / Maisons de quartier
    ('Centre culturel / Maison',
     r'\b(centre\s+culturel|maison\s+de\s+quartier|maison\s+de\s+la\s+culture|'
     r'MJC\b|espace\s+culturel|maison\s+du\s+livre|maison\s+des?\s+jeunes)\b'),

    # Festival multi-disciplinaire (catch-all for festivals not matched above)
    ('Festival multi-disciplinaire',
     r'\b(festival\b|manifestation\s+culturelle|biennale\b|triennale|'
     r'fête\s+(culturelle|de\s+la\s+ville)|nuit\s+(des\s+musées|blanche))\b'),
]

COMPILED = [(name, re.compile(p, re.IGNORECASE)) for name, p in CULTURE_PATTERNS]

# Manual overrides for entries verified via web research where pattern matching
# is too ambiguous or specific names need explicit categorization.
MANUAL_OVERRIDES = {
    "Fond. Guido Comba":                          'Centre culturel / Maison',  # foundation for art and culture
    "Fond. Horopedia":                            'Musée',                      # Maison des Arts et de la Culture Horlogère (MACH)
    "Fond. pour le développement":                'Centre culturel / Maison',  # FODAC arts et culture
    "CORODIS":                                    'Festival multi-disciplinaire',  # diffusion de spectacles romande
    "La Chaux-de-Fonds capitale":                 'Festival multi-disciplinaire',  # capitale culturelle suisse 2027
}


def classify(entry: dict) -> str | None:
    nom = entry.get('nom', '') or ''
    if nom in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[nom]
    desc = entry.get('description', '') or ''
    text = nom + ' ' + desc
    for name, pat in COMPILED:
        if pat.search(text):
            return name
    return None


def main():
    with open(INPUT) as f:
        data = json.load(f)
    entries = data['entries']
    total_chf_all = sum(e.get('montant_CHF', 0) for e in entries)

    buckets = defaultdict(lambda: {
        'count': 0, 'total_chf': 0, 'samples': [],
        'cantons': defaultdict(lambda: {'count': 0, 'total_chf': 0})
    })

    for e in entries:
        cat = classify(e)
        if not cat:
            continue
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

    categories = []
    for name, b in buckets.items():
        # Take top 5 samples by amount (more interesting than insertion order)
        b['samples'].sort(key=lambda s: -s['montant_CHF'])
        categories.append({
            'name': name,
            'count': b['count'],
            'total_chf': b['total_chf'],
            'mean_chf': b['total_chf'] // b['count'] if b['count'] else 0,
            'cantons': {c: dict(d) for c, d in b['cantons'].items()},
            'samples': b['samples'][:5],
        })
    categories.sort(key=lambda x: -x['total_chf'])

    total_classified_count = sum(c['count'] for c in categories)
    total_classified_chf = sum(c['total_chf'] for c in categories)

    out = {
        '_meta': {
            'source': 'docs/data/brb2025_full.json (v13.10 cleaned)',
            'method': 'Keyword classification on nom + description (ignoring unreliable secteur field).',
            'date': '2026-06-03',
            'version': 'v13.10-culture',
            'total_entries': len(entries),
            'total_entries_classified': total_classified_count,
            'total_chf_all': total_chf_all,
            'total_chf_classified': total_classified_chf,
            'pct_entries_classified': round(100 * total_classified_count / len(entries), 1),
            'pct_chf_classified': round(100 * total_classified_chf / total_chf_all, 1),
            'note': (
                "Classification par mots-clés ordonnés du plus spécifique (Cinéma, Danse, Cirque, "
                "Photographie) au plus générique (Festival multi-disciplinaire). Une entrée n'est "
                "attribuée qu'à une seule catégorie (première qui matche). Les entrées génériques "
                "(« Saison artistique » sans précision) restent non classifiées."
            ),
        },
        'categories': categories,
    }

    with open(OUTPUT, 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Classified {total_classified_count} entries ({out['_meta']['pct_entries_classified']}%)")
    print(f"Total CHF classified: {total_classified_chf:,} ({out['_meta']['pct_chf_classified']}% of all)")
    print(f"Categories: {len(categories)}")
    print(f"Output: {OUTPUT}")
    print()
    print("=== Categories by total CHF ===")
    for c in categories:
        print(f"  {c['name']:30s} {c['count']:>4d} attrib.  {c['total_chf']:>11,} CHF")


if __name__ == '__main__':
    main()
