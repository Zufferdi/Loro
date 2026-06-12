#!/usr/bin/env python3
"""fix_sectors_2021_specific.py — patterns spécifiques 2021 pour combler les trous."""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'

# Patterns spécifiques au BRB 2021 (organisations identifiées dans le top 50 sans secteur)
RULES_2021 = [
    # ─── SPORT ───
    (r"\bcourse d['\u2019]?orientation\b", 'Sport'),
    (r"\bwakeboard|wakesurf|enduro|trial\b", 'Sport'),
    (r"\bSport[\u2019']?Ouverte\b", 'Sport'),
    (r"\bbeach\s+volley|petanque|pétanque\b", 'Sport'),
    (r"\bGéraldine Pillonel|Yverdon\s+Sport\b", 'Sport'),
    (r"\bcourse de\s+(?:Suisse|l['\u2019]?\w+)|Coupe\s+de\s+Suisse\b.*(?:Sport|FIM|club)", 'Sport'),
    (r"\bFond\.\s+Leysin\s+Bike\b|Leysin\s+Bike\s+Park\b", 'Sport'),
    (r"\bFéd\.\s+Fribourgeoise\s+de\s+Gymnastique\b|Gymnastique\s+(?:Fribourg|Vaud|Valais|Genève|Jura|Neuchâtel)\b", 'Sport'),
    (r"\bKunst-\s+und\s+Geräteturnen|Geräteturnen\b", 'Sport'),
    (r"\bterrain\s+(?:de\s+)?(?:football|foot|basketball|tennis|hockey|sport)\b", 'Sport'),
    (r"\bbeach\s+volley|volley-pétanque|squash\b", 'Sport'),
    (r"\b(?:Team|Club)\s+(?:Vaud|Genève|Fribourg|Valais|Jura|Neuchâtel)\s+(?:Foot|Hockey|Basketball)\b", 'Sport'),
    (r"\baménagement\s+de\s+(?:terrains?|locaux\s+de\s+sport)\b", 'Sport'),
    (r"\b(?:cours|club)\s+de\s+(?:tennis|gym|squash|natation)\b", 'Sport'),

    # ─── CULTURE ───
    (r"\bL['\u2019]?Avant-Scène\s+Opéra\b|Opéra\s+\w", 'Culture'),
    (r"\bNouvel\s+Ensemble\s+Contemporain\b|NEC\s+", 'Culture'),
    (r"\bMusique\s+des\s+Lumières\b", 'Culture'),
    (r"\bBelluard\s+Bollwerk\b|\bBelluard\b", 'Culture'),
    (r"\bLa\s+Bâtie\b|\bBâtie\s*-\s*Festival\b", 'Culture'),
    (r"\bDelémont['\u2019]?BD\b", 'Culture'),
    (r"\bNIFFF\b|Neuchâtel\s+International\s+Fantastic", 'Culture'),
    (r"\bThéâtre\s+du\s+(?:Loup|Jura|Pré-aux-Sources|Galpon|Petit Salève)\b", 'Culture'),
    (r"\bCentre\s+dramatique\s+\w", 'Culture'),
    (r"\bBiblio\s*(?:FR|VS|VD|GE|NE|JU)\b|\bbibliothèques?\s+(?:fribourgeoises?|vaudoises?|valaisannes?|genevoises?|jurassiennes?)\b", 'Culture'),
    (r"\bMurten\s+Classics\b|Schwarzsee\s+Festival\b|Verein\s+Sommerfestspiele\b", 'Culture'),
    (r"\bAmplitudes\s*$|\bLes\s+Amplitudes\b", 'Culture'),
    (r"\bFrancomanias\b|Les\s+Francomanias\b", 'Culture'),
    (r"\bMagnifique\s+Théâtre\b|Magnifique\s+Théâtre\b", 'Culture'),
    (r"\barTpenteurs\b|Les\s+arTpenteurs\b", 'Culture'),
    (r"\bRadio\s+Vostok\b|Puplinge\s+Classique\b", 'Culture'),
    (r"\bL['\u2019]?Ours\s+Blanc\b|revue\s+L['\u2019]?Ours\b", 'Culture'),
    (r"\bUsine\s+à\s+Gaz\b", 'Culture'),
    (r"\bSirocco\b.*(?:fresque|mural|peinture)|fresque\s+murale", 'Culture'),
    (r"\bP[\u2019']?tit\s+du\s+Gros\b", 'Culture'),
    (r"\bVALPRO\b|Saison\s+artistique\s+VALPRO", 'Culture'),
    (r"\bAssoc\.\s+(?:de\s+)?marionnettes?\b|marionnette\b", 'Culture'),
    (r"\bATMO\s+Assoc|Les\s+6\s+Toits\b|Materia\s+Prima\b", 'Culture'),

    # ─── PATRIMOINE ───
    (r"\bArchives\s+(?:de\s+l['\u2019]?État|cantonales|de\s+la\s+Ville)\b", 'Conservation du patrimoine'),
    (r"\bpanorama\s+(?:de\s+la\s+)?bataille\s+(?:de\s+)?Morat\b|Posat\b", 'Conservation du patrimoine'),
    (r"\bSources\s+du\s+droit\s+\w+\b", 'Conservation du patrimoine'),
    (r"\bcloches?\s+de\s+l[\u2019']?église\b|sonneri\w+\b|restauration\s+du\s+clocher\b", 'Conservation du patrimoine'),
    (r"\bMusée\s+(?:de|d[\u2019']|cantonal|national|régional|Suisse|Romand|d')\w*\b", 'Conservation du patrimoine'),

    # ─── ACTION SOCIALE ───
    (r"\bVALTEX\b", 'Action sociale et personnes âgées'),
    (r"\baccueil\s+familial\s+(?:de\s+jour|en|du)\b|Accueil\s+Familial\b", 'Action sociale et personnes âgées'),
    (r"\bSeniorenzentrum\b|Maison\s+(?:de\s+)?retraite\s+(?:EMS|-)\b|EMS\s+\w", 'Action sociale et personnes âgées'),
    (r"\bDéclics\s+Déclencheurs\b", 'Action sociale et personnes âgées'),
    (r"\bLire\s+et\s+Écrire\b", 'Jeunesse et éducation'),
    
    # ─── JEUNESSE ───
    (r"\bCentres?\s+de\s+formation\b", 'Jeunesse et éducation'),
    (r"\bSwiss\s+Bike\s+Park\b", 'Sport'),
    
    # Patterns plus génériques pour les organisations non identifiées
    (r"\bClub\s+(?:sportif|de\s+\w+)\s+\w+|Sporting\s+Club\b", 'Sport'),
    (r"\bAssoc\.\s+(?:sportive|du\s+club|Club)\b", 'Sport'),
    (r"\bThéâtre\s+\w|Cinéma\s+\w|Orchestre\s+\w|Chorale\b|Chœur\b", 'Culture'),
    (r"\bMusée\b|Galerie\s+d['\u2019]?art\b|Conservation\s+du\b", 'Conservation du patrimoine'),
    (r"\bFestival\b|Concert\s+\w|Saison\s+(?:théâtrale|musicale|artistique)\b", 'Culture'),
    (r"\bÉglise|Cathédrale|Chapelle\b", 'Conservation du patrimoine'),
    (r"\bCommune\s+de\s+\w", 'Promotion, tourisme et développement'),  # défaut commune
]


def find_sector(entry):
    """Match patterns. Returns target sector or None."""
    text = ' '.join([
        entry.get('nom', ''),
        entry.get('description', ''),
    ])
    for pattern, sector in RULES_2021:
        if re.search(pattern, text, re.IGNORECASE):
            return sector
    return None


def main():
    p = DATA / 'brb2021_full.json'
    d = json.load(open(p, encoding='utf-8'))
    fixed = 0
    by_sector = {}
    for e in d['entries']:
        if e.get('secteur'):  # déjà classifié
            continue
        target = find_sector(e)
        if target:
            e['secteur'] = target
            by_sector[target] = by_sector.get(target, 0) + 1
            fixed += 1
    
    print(f"  Fixed: {fixed} entries reclassifiées")
    for sec, n in sorted(by_sector.items(), key=lambda x: -x[1]):
        print(f"    {n:>3}× → {sec}")
    
    # Remaining sans secteur
    remaining = sum(1 for e in d['entries'] if not e.get('secteur'))
    remaining_chf = sum(e['montant_CHF'] for e in d['entries'] if not e.get('secteur'))
    print(f"\n  Restants sans secteur : {remaining} ({remaining_chf/1e6:.1f} M)")
    
    d['_meta']['fix_2021_specific'] = {
        'date': '2026-06-04',
        'patterns_count': len(RULES_2021),
        'entries_reclassified': fixed,
        'remaining_unclassified': remaining,
        'remaining_chf': remaining_chf,
    }
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"  ✓ brb2021_full.json updated")


if __name__ == '__main__':
    main()
