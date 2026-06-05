#!/usr/bin/env python3
"""fix_v21_sport_culture.py — Reclassifier entries Sport qui sont en réalité Culture.

CONSERVATEUR : on ne change QUE les cas clairs (Musée, Bibliothèque, "Saison artistique",
"Exposition", certains mots-clés culturels purs).
"""
import json
import re
from pathlib import Path

DATA = Path('/home/claude/audit3/Loro-main/docs/data')

# Patterns à reclassifier (Sport → Culture)
SPORT_TO_CULTURE = [
    # Musées
    r'\bMuseum\b', r'\bMusée\b',
    # Bibliothèques
    r'\bBibliothèque\b',
    # Espace artistique / saison
    # Mais regarder description aussi
]

# Description : Sport→Culture si description contient ces termes
DESC_TO_CULTURE = [
    'saison artistique', 'exposition', 'manifestation / exposition',
    'rénovation et exposition', 'création artistique',
    'edition', 'projets culturels',
]

# Noms évidemment culturels en Sport (mots clés stricts)
NAME_TO_CULTURE = [
    r"\bThéâtres?\b(?![- ]?Club|[- ]?Sport)",
    r"\bOpéra\b",
    r"\bMusique\s+Contemporaine\b",
    r"\bConservatoire\b",
    r"\bRéseau\s+Danse\b", r"\bReso[- ]Réseau\s+Danse\b",
    r"\bCollectif\s+Danse\b",
    r"\bLivre\s+sur\s+les\s+quais\b",
    r"\bMusicae\b",
    r"\bEspace\s+(?:EEEEH|TILT|Horloger)\b",
    r"\bFond\.\s+d'Aigle\s+pour\s+l'Art\b",
    r"\bFond\.\s+du\s+Trait\b",  # gallerie d'art à Lausanne
    r"\bObservatoire\s+romand\s+du\s+droit\b",  # action sociale
    r"\bBande\s+dessinée\s+sur\b",
]


def main():
    total = 0
    for y in ['2021', '2022', '2023', '2024', '2025']:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p))
        fixed = 0
        for e in d['entries']:
            if e.get('secteur') != 'Sport': continue
            nom = e['nom'] or ''
            desc = (e.get('description') or '').lower()
            should_fix = False
            new_sector = 'Culture'  # default
            
            # 1. Pattern nom
            for pat in NAME_TO_CULTURE:
                if re.search(pat, nom):
                    should_fix = True
                    # Exception : ODAE = Action sociale
                    if 'Observatoire' in nom:
                        new_sector = 'Action sociale et personnes âgées'
                    break
            
            # 2. Pattern desc (uniquement si pas de keyword sportif dans nom)
            if not should_fix:
                if any(d2 in desc for d2 in DESC_TO_CULTURE):
                    # Vérifier qu'il n'y a pas de "camp sportif" qui prime
                    if 'camp sport' not in desc and 'champion' not in desc:
                        # Verify le nom n'a pas un mot sport
                        if not re.search(r'\b(?:FC|sport|Sport|sportif|hockey|football|tennis|volley|basket|ski-club|cyclisme|natation|gymnastique|judo|karaté|combat|équitation|escalade|athlétisme|marathon|trail)\b', nom):
                            should_fix = True
            
            # 3. Patterns simples musée/bibliothèque
            for pat in SPORT_TO_CULTURE:
                if re.search(pat, nom):
                    should_fix = True
                    new_sector = 'Conservation du patrimoine' if 'Museum' in nom or 'Musée' in nom else 'Culture'
                    break
            
            if should_fix:
                e['secteur'] = new_sector
                fixed += 1
        
        if fixed:
            d['_meta'].setdefault('fixes', {})['v21_sport_culture'] = {'count': fixed}
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
        print(f"  {y}: {fixed} entries Sport → Culture reclassifiées")
        total += fixed
    print(f"\n  Total : {total}")

if __name__ == '__main__':
    main()
