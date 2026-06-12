#!/usr/bin/env python3
"""
fix_sectors_via_keywords_v2.py
================================

Second-pass sector overrides + targeted name patterns to push classification
coverage to ≥60%.

Two phases:
  1. SECTOR OVERRIDES — Re-classify entries whose nom/desc clearly indicates
     a different sector (Nouvel Opéra → Culture, MTB Championnats → Sport, etc.)
  2. NAME-SPECIFIC TARGETING — For very specific high-impact beneficiaries
     that escape pattern matching (CERN, AVASAD, eHnv, etc.).
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'


# ─── Sector corrections (sector officiel manifestly wrong) ────────────────
# Each rule: (regex on text, target sector). FIRST match wins.
OVERRIDE_RULES_V2 = [
    # ─── CULTURE: misclassified entries ───────────────────────────────
    (r'\bNouvel\s+Opéra\b', 'Culture'),
    (r'\bOpéra\s+décentralisé\b', 'Culture'),
    (r'\bMusée\s+de\s+la\s+Bande\s+Dessinée\b', 'Culture'),
    (r'\bMusée\s+BD\b', 'Culture'),
    (r'\bMusée\s+de?\s+l[ae]?', 'Culture'),  # generic museum match
    (r'\bMaison\s+des\s+Amériques\b', 'Culture'),  # musée Châtel-St-Denis
    (r'\bMôtiers\s*-?\s*Art\s+en\s+plein\s+air\b', 'Culture'),
    (r'\bFond\.\s+Hainard\b', 'Culture'),  # musée nature Genève
    (r'\bETM\s+(?:-\s+)?École\s+des\s+musiques\b', 'Culture'),
    (r'\bARSENIC\b', 'Culture'),  # centre d'art scénique Lausanne
    (r'\bFond\.\s+Cinéforom\b', 'Culture'),
    (r'\bFond\.\s+pour\s+le\s+développement\s+des\s+arts\b', 'Culture'),
    (r"\bMaison\s+d['\u2019]?Ailleurs\b", 'Culture'),
    (r'\bGalerie\s+\w', 'Culture'),
    
    # ─── SPORT: misclassified entries ─────────────────────────────────
    (r'\bClubs?\s*[-–]\s*Sports?\s+(?:collectifs|individuels)\b', 'Sport'),
    (r'\bRelève\s+athlètes\s*[-–]\s*Sports?\b', 'Sport'),
    (r'\bChampionnat[s]?\s+(?:du\s+)?Monde\s+(?:MTB|UCI|cycl)', 'Sport'),
    (r'\bChampionnats?\s+(?:de\s+)?Suisse\b', 'Sport'),
    (r'\bMTB\b', 'Sport'),
    (r'\bcrosshockey\b', 'Sport'),
    (r'\b(?:Maison|Centre)\s+du\s+sport\b', 'Sport'),
    
    # ─── SANTE ─────────────────────────────────────────────────────────
    (r'\beHnv\b', 'Santé et handicap'),
    (r"\b(?:Établissements?|Etablissements?)\s+hospitalier", 'Santé et handicap'),
    (r'\bAVASAD\b', 'Santé et handicap'),
    (r"\bEnsemble\s+hospitalier\b", 'Santé et handicap'),
    (r"\bRéseau\s+santé\b", 'Santé et handicap'),
    (r"\bFond\.\s+Trajets\b", 'Santé et handicap'),  # psy/réinsertion
    (r"\bAigues-Vertes\b", 'Santé et handicap'),  # village handicapés
    (r"\bÉtablissements?\s+publics\s+pour\s+l['\u2019]intégration", 'Santé et handicap'),
    (r"\bEPI\b(?:,\s+Genève)?", 'Santé et handicap'),
    (r"\bFoyers?\s+Valais\s+de\s+cœur\b", 'Santé et handicap'),
    (r"\bFond\.\s+Foyer-Handicap\b", 'Santé et handicap'),
    (r"\bFond\.\s+Equilibre\s+et\s+Nuithonie\b", 'Culture'),  # actually venues (Fribourg)
    
    # ─── ACTION SOCIALE ────────────────────────────────────────────────
    (r"\bFond\.\s+Phénix\b", 'Action sociale et personnes âgées'),
    (r"\bUNHCR\b", 'Action sociale et personnes âgées'),  # réfugiés
    (r"\bFond\.\s+ATD\s+Quart\s+Monde\b", 'Action sociale et personnes âgées'),
    (r"\bAccueil\s+à\s+Bas\s+Seuil\b|\bABS\b", 'Action sociale et personnes âgées'),
    (r"\bFond\.\s+Officielle\s+de\s+la\s+jeunesse\b", 'Action sociale et personnes âgées'),
    (r"\bFEA\b", 'Action sociale et personnes âgées'),  # Fond expression assoc
    (r"\bMaison\s+d['\u2019]?enfants\b", 'Action sociale et personnes âgées'),
    (r"\bAssoc\.\s+La\s+Chaloupe\b", 'Action sociale et personnes âgées'),
    (r"\bFond\.\s+Le\s+Camp\b", 'Jeunesse et éducation'),
    
    # ─── CONSERVATION PATRIMOINE ───────────────────────────────────────
    (r"\bCathédrale\s+de\b", 'Conservation du patrimoine'),
    (r"\bLavaux\s+Patrimoine\b", 'Conservation du patrimoine'),
    (r"\bAvenches?\s+Romaine?\b", 'Conservation du patrimoine'),
    (r"\bAventicum\b", 'Conservation du patrimoine'),
    (r"\bFond\.\s+Portail\s+des\s+Nations\b", 'Conservation du patrimoine'),
    (r"\bFort\s+de\s+Chillon\b", 'Conservation du patrimoine'),
    (r"\bSauvegarde\s+du\s+Patrimoine\b", 'Conservation du patrimoine'),
    
    # ─── ENVIRONNEMENT ─────────────────────────────────────────────────
    (r"\bJardin\s+Urbain\b", 'Environnement'),
    (r"\bFond\.\s+des\s+Grangettes\b", 'Environnement'),
    (r"\bGrangettes\b", 'Environnement'),
    (r"\bRéserve\s+naturelle\b", 'Environnement'),
    (r"\bSté\s+Vaudoise\s+d['\u2019]?Astronomie\b", 'Culture'),
    
    # ─── FORMATION & RECHERCHE ─────────────────────────────────────────
    (r"\bCERN\b", 'Formation et recherche'),
    (r"\bFernfachhochschule\b", 'Formation et recherche'),
    (r"\bIdiap\b", 'Formation et recherche'),
    (r"\bISREC\b", 'Formation et recherche'),
    (r"\bFond\.\s+pour\s+la\s+recherche\b", 'Formation et recherche'),
    (r"\bUniversité\s+de\s+\w", 'Formation et recherche'),
    (r"\bHaute\s+école\b", 'Formation et recherche'),
    (r"\bHES[\s-]?SO\b", 'Formation et recherche'),
    (r"\bEPFL\b", 'Formation et recherche'),
    (r"\bCSEM\b", 'Formation et recherche'),
    (r"\bFond\.\s+Pathologie\s+2000\b", 'Formation et recherche'),
    (r"\bNeurocelliA\b", 'Formation et recherche'),
    (r"\bAssoc\.\s+Salon\s+des\s+Métiers\b", 'Formation et recherche'),
    (r"\bCité\s+des\s+Métiers\b", 'Formation et recherche'),
    (r"\bÉcole\s+Suisse\s+d['\u2019]?Archéologie\b", 'Formation et recherche'),
    
    # ─── PROMOTION ─────────────────────────────────────────────────────
    (r"\bFond\.\s+The\s+Ark\b", 'Promotion, tourisme et développement'),
    (r"\bGrandson[\s-]Murten\b", 'Promotion, tourisme et développement'),
    (r"\bVaud\s+Promotion\b", 'Promotion, tourisme et développement'),
    (r"\bValais[/\s]?Wallis\s+Promotion\b", 'Promotion, tourisme et développement'),
    (r"\bFribourg\s+Région\b", 'Promotion, tourisme et développement'),
]


def find_override_sector(entry: dict) -> str | None:
    """Match against rules; first match wins."""
    nom = entry.get('nom') or ''
    desc = entry.get('description') or ''
    text = nom + ' ' + desc
    for pattern, sector in OVERRIDE_RULES_V2:
        if re.search(pattern, text, re.IGNORECASE):
            return sector
    return None


def main():
    total_overrides = 0
    
    for y in ['2021', '2022', '2023', '2024', '2025']:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p, encoding='utf-8'))
        
        overrides_log = []
        for e in d['entries']:
            target = find_override_sector(e)
            if target and target != e['secteur']:
                overrides_log.append({
                    'old': e['secteur'],
                    'new': target,
                    'nom': e['nom'][:60],
                    'chf': e['montant_CHF'],
                })
                e['secteur'] = target
        
        d['_meta']['sector_overrides_v2'] = {
            'count': len(overrides_log),
            'date': '2026-06-04',
        }
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2, encoding='utf-8'))
        
        # Summary
        from collections import Counter
        changes = Counter(f"{op['old'] or 'None'} → {op['new']}" for op in overrides_log)
        print(f"\n─── BRB {y} ({len(overrides_log)} overrides, {sum(op['chf'] for op in overrides_log):,} CHF) ───")
        for c, n in changes.most_common(8):
            print(f"  {n:>4d} × {c}")
        total_overrides += len(overrides_log)
    
    print(f"\nTotal: {total_overrides} sectors re-overridden")


if __name__ == '__main__':
    main()
