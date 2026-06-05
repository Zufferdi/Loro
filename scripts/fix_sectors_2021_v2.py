#!/usr/bin/env python3
"""fix_sectors_2021_v2.py — patterns additionnels."""
import json
import re
from pathlib import Path

DATA = Path('/home/claude/audit3/Loro-main/docs/data')

RULES = [
    # ─── CULTURE — compagnies, théâtres, festivals ───
    (r"\bCie\s+(?:de\s+)?(?:nuit|Philippe Saire|Julien Mages|De nuit)\b", 'Culture'),
    (r"\bCompagnie\s+(?:Helvètes Underground|de\s+\w)\b", 'Culture'),
    (r"\bCie\s+\w", 'Culture'),  # toute compagnie
    (r"\bPulloff\s+Th[eé]âtres?\b", 'Culture'),
    (r"\bRencontre\s+et\s+Culture\b", 'Culture'),
    (r"\bService\s+de\s+la\s+culture\b", 'Culture'),
    (r"\bMusicales?\s+de\s+\w|Musicales?\b\s*$", 'Culture'),
    (r"\bSt[eé]\.\s+des\s+Concerts\b|Sté\s+des\s+Concerts\b", 'Culture'),
    (r"\bMéta\s*[tT]héâtre\b|\bMétathéâtre\b", 'Culture'),
    (r"\baudiodécrit\w*\b|représentations?\s+audiodécrit", 'Culture'),
    (r"\bErich\s+Herm[eè]s\b|messager\s+des\s+arts\b", 'Culture'),
    (r"\bAssoc\.\s+(?:les\s+)?(?:Créatives|Ufas|Pacifique)\b", 'Culture'),
    (r"\bDanse\s+\(in\)\b|Danse\s+contemporaine\b", 'Culture'),
    (r"\bBee\s+Classical\b", 'Culture'),
    (r"\bCollectif\s+(?:pour\s+une\s+)?vie\s+nocturne\b", 'Culture'),
    (r"\bSculpte-moi\b", 'Culture'),
    (r"\bFond\.\s+(?:Espace\s+)?Jean\s+Tinguely\b|Jean\s+Tinguely\s+", 'Culture'),
    (r"\bMeurtres?\s+et\s+Mystères?\b", 'Culture'),
    (r"\bd['\u2019]?Hauterive\b.*marionnette|marionnette.*Hauterive", 'Culture'),
    (r"\bFond\.\s+d['\u2019]?Hauterive\b", 'Culture'),  # marionnettes
    (r"\bRFI\s*-?\s*Rencontres\s+Internationales\b", 'Culture'),
    
    # ─── PATRIMOINE ───
    (r"\bRechtsquellenstiftung\b|Schweizerischen?\s+Juristenvereins\b", 'Conservation du patrimoine'),
    (r"\bFreiburger\s+Eidbücher\b|Eidbücher\b", 'Conservation du patrimoine'),
    (r"\b(?:Fond\.|Stiftung)\s+du?\s+Village\s+lacustre\b|Village\s+lacustre\b", 'Conservation du patrimoine'),
    (r"\bSaas\s+ischi\s+Heimat\b", 'Conservation du patrimoine'),
    
    # ─── SPORT ───
    (r"\bSté\s+vaudoise\s+des\s+carabiniers\b|Sté\s+cantonale\s+des\s+Tireurs\b|Tireurs\s+\w+\b", 'Sport'),
    (r"\bhalles?\s+de\s+tennis\b|tennis\s+club\b|Vaud\s+Tennis\b", 'Sport'),
    (r"\bManche\s+de\s+la\s+Coupe\s+de\s+Suisse\b", 'Sport'),
    (r"\bcarabiniers?\b", 'Sport'),
    
    # ─── ACTION SOCIALE ───
    (r"\bVéhicules?\s+électriques?\s+(?:réinsertion|projet\s+de\s+réinsertion)\b|projet\s+de\s+réinsertion\s+professionnelle\b", 'Action sociale et personnes âgées'),
    (r"\bRéinsertion\s+professionnelle\b", 'Action sociale et personnes âgées'),
    
    # ─── PROMOTION (communes) ───
    (r"\b(?:Courroux\s+et\s+Moutier|République\s+et\s+Canton\s+du\s+Jura)\b", 'Promotion, tourisme et développement'),
]


def find_sector(entry):
    text = ' '.join([entry.get('nom', ''), entry.get('description', '')])
    for pattern, sector in RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return sector
    return None


def main():
    p = DATA / 'brb2021_full.json'
    d = json.load(open(p))
    fixed = 0
    by_sector = {}
    for e in d['entries']:
        if e.get('secteur'):
            continue
        target = find_sector(e)
        if target:
            e['secteur'] = target
            by_sector[target] = by_sector.get(target, 0) + 1
            fixed += 1
    print(f"  v2 Fixed: {fixed} entries")
    for sec, n in sorted(by_sector.items(), key=lambda x: -x[1]):
        print(f"    {n:>3}× → {sec}")
    remaining = sum(1 for e in d['entries'] if not e.get('secteur'))
    remaining_chf = sum(e['montant_CHF'] for e in d['entries'] if not e.get('secteur'))
    print(f"\n  Restants : {remaining} ({remaining_chf/1e6:.1f} M)")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
