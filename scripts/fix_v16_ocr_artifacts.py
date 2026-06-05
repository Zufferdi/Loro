#!/usr/bin/env python3
"""fix_v16_ocr_artifacts.py — Nettoyage des artifacts OCR du parser BRB 2021.

Patterns détectés :
1. Nom commence par "e " (= "1re", "2e", "3e" édition tronqué) → extraire vraie organisation
2. Nom commence par minuscule + manque préfixe (ex: "aménagements Fond. X" → "Fond. X")
"""
import json
import re
from pathlib import Path

DATA = Path('/home/claude/audit3/Loro-main/docs/data')

def extract_org_from_polluted(nom):
    """Extrait l'organisation d'un nom pollué par descriptions.
    
    Patterns :
    - "e [description] [Fond./Assoc.] X" → "Fond./Assoc. X"
    - "[adjectif] Fond./Assoc. X" → "Fond./Assoc. X"
    - "[verbe au participe] Fond./Assoc. X" → "Fond./Assoc. X"
    """
    # Pattern 1 : trouver "Fond.|Assoc.|Sté|Fédération" suivi d'un nom
    match = re.search(r'\b((?:Fond\.|Assoc\.|Sté|Société|Fédération|Féd\.|Club|Stiftung|Verein|Comité|Comite|Compagnie|Cie|Centre|Conservatoire|Ecole|École|Institut|Maison|Théâtre|Festival|Orchestre|Choeur|Chœur|Ballet|Compagnie|Ville|Commune|Hôpital|Clinique)\s+[A-Za-zÀ-ÿ][\w\sÀ-ÿ\-\.\'\,]{3,80})', nom)
    if match:
        org = match.group(1).strip()
        # Nettoyer le suffix de la description : couper aux 2-3 mots après "Fond. X"
        # Essayons d'arrêter au premier "," ou point-virgule
        org = re.split(r'[,;]', org)[0].strip()
        return org
    return None


def main():
    total = 0
    examples = []
    for y in ['2021', '2022', '2023', '2024', '2025']:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p))
        fixed = 0
        for e in d['entries']:
            nom = e['nom']
            if not nom: continue
            
            # Case 1 : starts with 'e ' (artifact OCR édition tronquée)
            if nom.startswith('e ') and len(nom) > 10:
                new_nom = extract_org_from_polluted(nom)
                if new_nom and new_nom != nom:
                    # Ajouter description si déjà pas là
                    desc = e.get('description', '') or ''
                    desc_part = nom[:nom.find(new_nom)].strip() if new_nom in nom else nom
                    if desc_part and desc_part not in desc:
                        e['description'] = ('e ' + desc_part).strip() + '. ' + desc if desc else 'e ' + desc_part
                    e['nom'] = new_nom
                    fixed += 1
                    if len(examples) < 5: examples.append((y, nom[:60], new_nom[:50]))
            
            # Case 2 : starts with lowercase (artifact OCR)
            elif nom[0].islower() and len(nom) > 15:
                new_nom = extract_org_from_polluted(nom)
                if new_nom and new_nom != nom:
                    desc = e.get('description', '') or ''
                    desc_part = nom[:nom.find(new_nom)].strip() if new_nom in nom else ''
                    if desc_part and desc_part not in desc:
                        e['description'] = desc_part + '. ' + desc if desc else desc_part
                    e['nom'] = new_nom
                    fixed += 1
                    if len(examples) < 5: examples.append((y, nom[:60], new_nom[:50]))
        
        if fixed:
            d['_meta'].setdefault('fixes', {})['v16_ocr'] = {'count': fixed}
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
        print(f"  {y}: {fixed} artifacts OCR nettoyés")
        total += fixed
    print(f"\n  Total : {total}")
    print(f"\n  Exemples :")
    for y, old, new in examples:
        print(f"    {y}: '{old}…' → '{new}…'")


if __name__ == '__main__':
    main()
