#!/usr/bin/env python3
"""
build_social_classification.py — Pass 10 (v13.10) — Social sub-categorization
================================================================================

Approche : patterns mots-clés + noms d'orgs sociales suisses connues
+ overrides manuels pour les cas web-vérifiés.

Output: docs/data/social_classification.json
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / 'docs' / 'data' / 'brb2025_full.json'
OUTPUT = ROOT / 'docs' / 'data' / 'social_classification.json'

# Patterns ordered from most specific to most generic.
# Each entry matches AT MOST one category (first match wins).
SOCIAL_PATTERNS = [

    # === Violences ===
    ('Violences / Refuges',
     r"\b(LAVI\b|loi\s+(d')?aide\s+aux\s+victimes|violence\s+(conjugale|familiale|domestique|sexuelle|"
     r"faites\s+aux\s+femmes)|maltraitance\b|abus\s+sexuel|protection\s+des\s+(femmes|enfants)|"
     r"refuge\s+(pour\s+)?(femmes|enfants)|au\s+cœur\s+des\s+grottes|frauenhaus|maison\s+d'accueil\s+pour\s+femmes|"
     r"survivantes\b|sos\s+(femmes|enfants|viol)|solidarité\s+femmes)\b"),

    # === Petite enfance ===
    ('Petite enfance / Crèches',
     r"\b(crèche|kita\b|garderie|nurser|petite\s+enfance|accueil\s+(de\s+jour\s+)?des\s+enfants|"
     r"FAJE\b|accueil\s+familial|accueil\s+(extra-scolaire|para-scolaire|extrascolaire)|"
     r"pré-scolaire|preschool|jardin\s+d'enfants|UAPE\b|jardin\s+d'enfance|maman\s+de\s+jour)\b"),

    # === Personnes âgées ===
    ('EMS et personnes âgées',
     r"\b(pro\s+senectute|EMS\b|personnes\s+âgées|aînés|seniors\b|alzheimer|3e\s+âge|troisième\s+âge|"
     r"maison\s+de\s+retraite|résidence\s+(pour\s+)?seniors|home\s+médicalisé|home\s+médicalis|"
     r"vieillesse|vieillir|retraite\s+(active|d'or|positive)|mouvement\s+des\s+aînés|"
     r"elderli\b|colocation\s+intergén|inter-?générationnel|grands-?parents|pause\s+café\s+aîné|"
     r"bénévole\s+aînés|atelier\s+seniors|repas\s+communautaire\s+seniors|seniorenrat|"
     r"tertianum|seniorenzentrum|senioren[-\s]+und\s+pflege|pflegeheim|"
     r"^home\s+\w|fond\.\s+du\s+home|"
     r"^foyer\s+(?:les?\s+)?(?:3\s+sapins?|pierre-?olivier|haut-de-cry|ma\s+vallée|saint-?joseph|beau-?site)|"
     r"^résidence\s+(?:gravelone|plantzette|belle-vue|st-sylvain|beausite|le\s+cottage|beau-?soleil|soleilmont|tour-d[\u2019']?aï|forel|d[\u2019']?anavière|don\s+bosco)|"
     r"\bfegems\b|cogest[\u2019']?ems?|pro[-\s]+home|"
     r"\bmaison\s+(?:de\s+|du\s+)?(?:retraite|soins\s+et\s+de\s+réhabilitation|de\s+repos)|"
     r"maison\s+du\s+vélan|le\s+carillon\s*-\s*maison\s+de\s+retraite|"
     r"fond\.\s+du\s+foyer)\b"),

    # === Handicap ===
    ('Handicap',
     r"\b(pro\s+infirmis|insieme\b|procap|cerebral\b|polyhandicap|handicap|handicapé|invalide|"
     r"déficience|cécité|aveugle|malvoyant|sourd|surdité|paralysie|paraplég|tétraplég|trisomie|"
     r"autisme|autiste|asperger|TDAH\b|dyslexie|dyspraxie|insertion\s+professionnelle\s+(des\s+)?personnes\s+(en\s+situation\s+de\s+)?handicap|"
     r"INSOS|fondation\s+(eben-hézer|delafontaine|claire-fontaine)|mobilité\s+réduite|"
     r"langue\s+des\s+signes|braille|chien\s+guide)\b"),

    # === Addictions ===
    ('Addictions',
     r"\b(addiction|dépendance(s)?\b|alcool|alcoolique|alcoolisme|toxico|toxicomanie|drogue|"
     r"stupéfiant|cocaïne|héroïne|cannabis|jeu\s+excessif|jeu\s+pathologique|tabagisme|sevrage|"
     r"infodrog|sucht|fondation\s+phénix|act\s+ge|first\s+steps|relais\s+contact|"
     r"argos\s+addiction|hôpital\s+de\s+(jour\s+)?addictions?|crochet\s+gold)\b"),

    # === Migration ===
    ('Migration / Intégration',
     r"\b(migrant|réfugié|asile|requérant|naturalisation|intégration|EVAM\b|FAREAS\b|"
     r"sans\s+papiers|migration|étranger|interculturel|EPER\s+(migration|exil)|caritas\s+migrants|"
     r"français\s+en\s+jeu|appui\s+scolaire\s+(aux\s+)?migrants|atelier\s+français|"
     r"centre\s+suisses-immigrés|camarada|centre\s+social\s+protestant.*migration)\b"),

    # === Précarité — incluant orgs nommées et soupe populaire ===
    ('Précarité / Pauvreté',
     r"\b(caritas\b|CSP\s|centre\s+social\s+protestant|EPER\b|entraide\s+protestante|"
     r"banc\s+public|vestiaire\s+social|banque\s+alimentaire|distribution\s+alimentaire|"
     r"table\s+(suisse|du\s+bonheur)|samedi\s+du\s+partage|cartons?\s+du\s+cœur|colis\s+du\s+cœur|"
     r"soupe\s+populaire|emmaüs|emmaus|armée\s+du\s+salut|"
     r"sans-abri|sans\s+domicile|sdf\b|précarité|précaire|pauvreté|exclusion\s+sociale|"
     r"foyer\s+d'(accueil|urgence)|hébergement\s+d'urgence|abri\s+de\s+nuit|"
     r"action\s+sociale\b|service\s+social\b|aide\s+sociale|insertion\s+professionnelle|réinsertion|"
     r"vestiaire\s+(croix-rouge|caritas)|magasin\s+social|épicerie\s+sociale|"
     r"clic\s+ensemble|vaud\s+pour\s+vous|aide\s+(d')?urgence)\b"),

    # === Santé mentale ===
    ('Santé mentale',
     r"\b(santé\s+mentale|psychiatrie|psychiatrique|psychologie|psychothérapie|psychiatres?|"
     r"dépression\b|burn-?out|bipolaire|schizophrén|trouble\s+psychique|trouble\s+anxieux|"
     r"pro\s+mente\s+sana|sanimente|graap|fovahm|équilibre\s+psychique|prévention\s+(du\s+)?suicide)\b"),

    # === Familles ===
    ('Familles / Parentalité',
     r"\b(famille\b|familles|parentalité|parents|maternité|paternité|grossesse|naissance|"
     r"couples\b|médiation\s+familiale|planning\s+familial|conseil\s+conjugal|"
     r"thérapie\s+familiale|école\s+des\s+parents|éducation\s+familiale|"
     r"groupe\s+(des\s+)?(mamans?|papas?|parents)|maman\s+(et|&)\s+papa|& des Papas?\b|"
     r"as'trame|astrame|deuil\s+(des\s+)?(enfants|famille)|protection\s+de\s+l'enfance|"
     r"adoption|placement\s+familial)\b"),

    # === Jeunesse ===
    ('Jeunes / Adolescents',
     r"\b(pro\s+juventute|jeunesse\s+(en|vulnérable|africaine)|jeunes?\s+en\s+(difficulté|errance|rupture)|"
     r"protection\s+de\s+la\s+jeunesse|adolescent[se]?\s+en|protection\s+des\s+mineurs|"
     r"décrochage\s+scolaire|loisirs?\s+pour\s+les\s+jeunes|maison\s+(de\s+|des\s+)jeunes|"
     r"point\s+jeunes|centre\s+de\s+loisirs|colonies?\s+de\s+vacances|colos|camp\s+de\s+vacances|"
     r"scoutisme|scouts?\b|éclaireurs|tipi|cefoc\b)\b"),

    # === Maladies / Santé spécifique ===
    ('Maladies / Soins spécifiques',
     r"\b(ligue\s+(contre\s+le\s+|fribourgeoise\s+contre\s+le\s+|valaisanne\s+contre\s+le\s+|"
     r"vaudoise\s+contre\s+le\s+|neuchâteloise\s+contre\s+le\s+|genevoise\s+contre\s+le\s+|"
     r"jurassienne\s+contre\s+le\s+)?cancer|cancer\b|leucémie|"
     r"maladies?\s+rares?|sclérose|diabète|sida\b|VIH\b|hépatite|parkinson|"
     r"croix-rouge|red\s+cross|soins\s+(à\s+domicile|palliatifs?)|fin\s+de\s+vie|"
     r"deuil\b|palliatif|aidants?\s+(proches|familiaux)|proches\s+aidants|"
     r"fond\.\s+(suisse|romande)?\s*recherche|recherche\s+médicale|recherche\s+sur\s+le\s+cancer)\b"),

    # === Bénévolat / Écoute ===
    ('Bénévolat / Écoute',
     r"\b(bénévolat|bénévole|main\s+tendue|tel\.\s*143|téléphone\s+de\s+l'amitié|"
     r"écoute\s+(téléphonique|sociale)|hotline|service\s+d'écoute|"
     r"telme\b|téléphone\s+ados|prophyl|insieme\s+bénévole)\b"),

    # === Égalité / Femmes / LGBT ===
    ('Égalité / Femmes / LGBT',
     r"\b(égalité\s+(femme|homme|des\s+genres)|féministe|féminisme|LGBT[QI]*|queer|gay\b|"
     r"lesbienne|trans\s+(et|fluide|genre)|transgenre|homophobie|biphobie|transphobie|"
     r"discrimination\s+(sexuelle|de\s+genre)|360\s+\(association\)|lestime|dialogai)\b"),

    # === Logement / Hébergement ===
    ('Logement / Hébergement',
     r"\b(logement\s+(social|adapté|d'urgence|protégé)|hébergement\s+(d'urgence|de\s+nuit|temporaire)|"
     r"abri\s+pc|sleep-in|cigale\b|maison\s+haggar|appartement\s+protégé|appartement\s+accompagn)\b"),
]

COMPILED = [(name, re.compile(p, re.IGNORECASE)) for name, p in SOCIAL_PATTERNS]

# Manual overrides for entries where keyword classifier doesn't trigger
# but web-research has determined the right category. Match by exact nom (case-sensitive).
MANUAL_OVERRIDES = {
    "Banc Public":                    'Précarité / Pauvreté',     # accueil de jour Fribourg
    "Elderli Sàrl":                   'EMS et personnes âgées',           # colocation intergénérationnelle
    "Assoc. La Tuile":                'Précarité / Pauvreté',     # accueil de nuit Fribourg
    "Communauté d'Emmaüs":            'Précarité / Pauvreté',     # bien connu
    "Fond. Au Cœur des Grottes":      'Violences / Refuges',       # survivantes violences GE
    "Assoc. Vestiaire social":        'Précarité / Pauvreté',
    "diabètefribourg - Assoc.":       'Maladies / Soins spécifiques',
}

# Exclude these even if keywords match — they're not really social
EXCLUDE_FROM_SOCIAL = {
    "Conservatoire populaire",        # music school, not social
}


def classify(entry: dict):
    """Returns category name or None."""
    nom = entry.get('nom', '') or ''
    if nom in EXCLUDE_FROM_SOCIAL:
        return None
    # Manual override?
    if nom in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[nom]
    desc = entry.get('description', '') or ''
    text = nom + ' ' + desc
    for name, pat in COMPILED:
        if pat.search(text):
            return name
    return None


def main():
    with open(INPUT, encoding='utf-8') as f:
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
        # Sort samples by amount, slice top 5
        top5_samples = sorted(b['samples'], key=lambda s: -s['montant_CHF'])[:5]
        categories.append({
            'name': name,
            'count': b['count'],
            'total_chf': b['total_chf'],
            'mean_chf': b['total_chf'] // b['count'] if b['count'] else 0,
            'cantons': {c: dict(d) for c, d in b['cantons'].items()},
            'samples': top5_samples,
        })
    categories.sort(key=lambda x: -x['total_chf'])

    total_classified_count = sum(c['count'] for c in categories)
    total_classified_chf = sum(c['total_chf'] for c in categories)

    out = {
        '_meta': {
            'source': 'docs/data/brb2025_full.json (v13.10 cleaned)',
            'method': (
                "Classification par mots-clés sur nom + description + noms d'orgs sociales "
                "suisses connues (Caritas, CSP, Pro Senectute, Pro Infirmis, EPER, Croix-Rouge…). "
                "Overrides manuels pour 7 cas vérifiés par recherche web."
            ),
            'date': '2026-06-03',
            'version': 'v13.10-social',
            'total_entries': len(entries),
            'total_entries_classified': total_classified_count,
            'total_chf_all': total_chf_all,
            'total_chf_classified': total_classified_chf,
            'pct_entries_classified': round(100 * total_classified_count / len(entries), 1),
            'pct_chf_classified': round(100 * total_classified_chf / total_chf_all, 1),
            'manual_overrides': len(MANUAL_OVERRIDES),
            'note': (
                "Le champ 'secteur' de la source étant pollué (Cinémathèque taggée 'Santé', "
                "Conservatoire taggé 'Action sociale'…), classification basée uniquement sur "
                "le contenu textuel et les noms d'orgs."
            ),
        },
        'categories': categories,
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Classified {total_classified_count} entries ({out['_meta']['pct_entries_classified']}%)")
    print(f"Total CHF classified: {total_classified_chf:,} ({out['_meta']['pct_chf_classified']}%)")
    print(f"Categories: {len(categories)}")
    print(f"Manual overrides applied: {len(MANUAL_OVERRIDES)}")
    print()
    print("=== Ranking ===")
    for c in categories:
        print(f"  {c['name']:30s} {c['count']:>4d} attrib.  {c['total_chf']:>11,} CHF")


if __name__ == '__main__':
    main()
