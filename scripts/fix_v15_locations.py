#!/usr/bin/env python3
"""fix_v15_locations.py — Corrections de localisations / cantons clairement faux.

Stratégie conservative : on ne corrige que les cas HAUTEMENT confiants.
Section cantonale "Cantonale Vaudoise" → canton VD (pas GE ou VS).
Les multi-cantons (Vaud-Fribourg, Vaud-Valais-Fribourg, Neuchâtel-Jura) restent VD/FR/NE
selon le siège principal.
"""
import json
import re
from pathlib import Path

DATA = Path('/home/claude/audit3/Loro-main/docs/data')

# Patterns CLAIRS de section cantonale + canton attendu
CANTON_PATTERNS = [
    # Cantonale [Canton] = section cantonale claire
    (r'^Assoc\.\s+Cantonale\s+Vaudoise\b', 'VD'),
    (r'^Assoc\.\s+Cantonale\s+Genevoise\b', 'GE'),
    (r'^Assoc\.\s+Cantonale\s+Fribourgeoise\b', 'FR'),
    (r'^Assoc\.\s+Cantonale\s+Valaisanne\b', 'VS'),
    (r'^Assoc\.\s+Cantonale\s+Neuchâteloise\b', 'NE'),
    (r'^Assoc\.\s+Cantonale\s+Jurassienne\b', 'JU'),
    # AVIVO Section de Lausanne / Renens → VD (clair)
    (r'^AVIVO\s+Section\s+de\s+(?:Lausanne|Renens|Yverdon|Vevey|Morges)\b', 'VD'),
    (r'^AVIVO\s+Chablais\s+Vaudois\b', 'VD'),
    (r'^AVIVO\s+Vaud\b', 'VD'),
    # Avivo La Chaux-de-Fonds / Val-de-Travers → NE
    (r"^AVIVO\s+(?:La\s+Chaux-de-Fonds|Val-de-Travers)\b", 'NE'),
    # PROCAP sections
    (r"^Procap\s+La\s+Chaux-de-Fonds", 'NE'),
    (r"^Procap\s+sport\s+\(Neuchâtel", 'NE'),
    (r"^PROCAP,?\s+[Ss]ection\s+(?:Delémont|Franches-Montagnes|Porrentruy|Saignelégier)\b", 'JU'),
    # Assoc. Jura Indoors, Courtedoux → JU (Courtedoux est en JU)
    (r"^Assoc\.\s+Jura\s+Indoors,?\s+Courtedoux", 'JU'),
    # Parc Naturel Jura vaudois → VD (région VD nommée 'Jura')
    # (ce cas est OK, restons VD)
    # Pro Senectute sections
    (r'^Fond\.\s+Pro\s+Senectute\s+Fribourg\b', 'FR'),
    (r'^Fond\.\s+Pro\s+Senectute\s+Valais', 'VS'),
    (r'^Pro\s+Senectute\s+Vaud\b', 'VD'),
    (r'^Pro\s+Senectute\s+Genève\b', 'GE'),
    # Pro Infirmis
    (r'^Pro\s+Infirmis\s+Genève\b', 'GE'),
    (r'^Pro\s+Infirmis\s+Vaud\b', 'VD'),
    (r'^Pro\s+Infirmis\s+Jura\b', 'JU'),
    (r'^Pro\s+Infirmis\s+Fribourg\b', 'FR'),
    # Caritas sections
    (r'^Caritas\s+Vaud\b', 'VD'), (r'^Assoc\.\s+Caritas\s+Vaud\b', 'VD'),
    (r'^Caritas\s+Genève\b', 'GE'), (r'^Assoc\.\s+Caritas\s+Genève\b', 'GE'),
    (r'^Caritas\s+Fribourg\b', 'FR'),
    (r'^Caritas\s+Valais', 'VS'),
    (r'^Caritas\s+Neuchâtel\b', 'NE'),
    (r'^Caritas\s+Jura\b', 'JU'),
    # Croix-Rouge sections
    (r"^Assoc\.\s+Croix-Rouge\s+Valais\b", 'VS'),
    (r"^Croix-Rouge\s+fribourgeoise\b", 'FR'),
    (r"^Croix-Rouge\s+genevoise\b", 'GE'),
    (r"^Croix-Rouge\s+(?:vaudoise|du\s+canton\s+de\s+Vaud)\b", 'VD'),
    # OSEO sections
    (r"^OSEO\s+(?:Neuchâtel|Vaud|Genève|Fribourg)\b", None),  # canton = match
    # Insieme sections — Valais romand → VS, Genève → GE
    (r"^Assoc\.\s+Insieme\s+Valais\s+romand\b", 'VS'),
    (r"^Assoc\.\s+Insieme[\s\-]Genève\b", 'GE'),
    (r"^Insieme\s+Vaud\b", 'VD'),
]

# Compile  
COMPILED = []
for pat, canton in CANTON_PATTERNS:
    COMPILED.append((re.compile(pat, re.IGNORECASE), canton))


def fix_canton(nom, current_canton):
    """Retourne canton corrigé ou None si pas de match."""
    for pat, target_canton in COMPILED:
        if pat.search(nom):
            if target_canton is None:
                # Dynamic : extract from name
                if 'Neuchâtel' in nom: return 'NE'
                elif 'Vaud' in nom: return 'VD'
                elif 'Genève' in nom: return 'GE'
                elif 'Fribourg' in nom: return 'FR'
                elif 'Valais' in nom or 'Wallis' in nom: return 'VS'
                elif 'Jura' in nom: return 'JU'
            return target_canton
    return None


def main():
    total = 0
    for y in ['2021', '2022', '2023', '2024', '2025']:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p))
        fixed = 0
        for e in d['entries']:
            target = fix_canton(e['nom'], e.get('canton'))
            if target and target != e.get('canton') and e.get('canton') not in ('SR',):
                e['canton'] = target
                fixed += 1
        if fixed:
            d['_meta'].setdefault('fixes', {})['v15_locations'] = {'count': fixed}
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
        print(f"  {y}: {fixed} cantons corrigés")
        total += fixed
    print(f"\n  Total : {total} corrections de canton")


if __name__ == '__main__':
    main()
