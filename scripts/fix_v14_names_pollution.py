#!/usr/bin/env python3
"""fix_v14_names_pollution.py — Nettoyage des noms pollués

Patterns détectés :
1. "Publication X" au début (93 entries 2021, 3 entries 2025)
2. "Investissement X", "Formation X", "Equipement X", "Achat X" — préfixes description
3. "AVIVO" / "Avivo" — uniformisation case
4. "Section Franches- Montagnes" → "Section Franches-Montagnes" (espace cassé)
5. "Pro Senectute Valais- Wallis / Pour la Vieillesse" → "Pro Senectute Valais-Wallis"
6. Cantons mal assignés sur sections cantonales (AVIVO Lausanne avec canton JU,VD ?)
"""
import json
import re
from pathlib import Path

DATA = Path('/home/claude/audit3/Loro-main/docs/data')

# Préfixes à retirer (description polluant le nom)
PREFIX_TO_STRIP = [
    'Publication ',
    'Investissement ',
    'Formation Assoc. ', 'Formation Fond. ',
    'Equipement ', 'Équipement ',
    'Achat ',
    'Construction ', 'Rénovation ',
    'Aménagement ',
    'Acquisition ',
    'Recueil de textes des Jeunes Auteurs 2021 ',
    'Déménagement à l\'Espace Tourbillon ',
    'Evénement ', 'Événement ',
    'Soutien à l\'organisation ',
    'Mise en place ',
    'Création ',
    'Camp d\'entraînement ',
    'Activité Fond. ', 'Activité Assoc. ',
    'Organisation du Noël ', 'Organisation de l\'événement ',
]

# Remplacements de cassure noms
NAME_FIXES = [
    (r'\bFranches-\s+Montagnes\b', 'Franches-Montagnes'),
    (r'\bValais-\s+Wallis\b', 'Valais-Wallis'),
    (r'\bPro Senectute Valais-?\s*Wallis\s*/\s*Pour la Vieillesse\b', 'Pro Senectute Valais-Wallis'),
    (r'\bChaux-de-\s+Fonds\b', 'Chaux-de-Fonds'),
    (r'\bVal-\s+de-Travers\b', 'Val-de-Travers'),
    (r'\bVal-\s+de-Ruz\b', 'Val-de-Ruz'),
    (r'\b3e\s+âge\b', '3e âge'),
]

# Uniformisation case
CASE_FIXES = {
    'Avivo': 'AVIVO',  # toujours majuscule
    'AVIVO ': 'AVIVO ',
    'procap': 'Procap',  # PROCAP en majuscules est utilisé selon contexte
}


def fix_name(nom):
    n = nom
    # Strip preflux
    for pref in PREFIX_TO_STRIP:
        if n.startswith(pref):
            n = n[len(pref):].strip()
            break
    # Apply regex fixes
    for pat, repl in NAME_FIXES:
        n = re.sub(pat, repl, n)
    # Case
    # Avivo → AVIVO (mot entier seulement)
    n = re.sub(r'\bAvivo\b', 'AVIVO', n)
    return n.strip()


def main():
    total_changed = 0
    for y in ['2021', '2022', '2023', '2024', '2025']:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p))
        changed = 0
        for e in d['entries']:
            old = e['nom']
            new = fix_name(old)
            if new != old:
                # Move into description if not already there
                desc = e.get('description', '') or ''
                # If old name started with strip prefix, add the prefix to description
                stripped_part = old[:len(old) - len(new)].strip()
                if stripped_part and stripped_part not in desc:
                    if desc:
                        e['description'] = stripped_part + '. ' + desc
                    else:
                        e['description'] = stripped_part
                e['nom'] = new
                changed += 1
        if changed:
            d['_meta'].setdefault('fixes', {})['v14_names'] = {'count': changed}
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
        print(f"  {y}: {changed} noms nettoyés")
        total_changed += changed
    print(f"\n  Total : {total_changed} entries nettoyées")


if __name__ == '__main__':
    main()
