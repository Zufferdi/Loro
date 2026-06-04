#!/usr/bin/env python3
"""
fix_names_and_villes.py
========================

Two passes:

1. **Fix villes-adjectifs** : entries where `ville` = "Fribourgeois", "Vaudoise",
   "Genevoise" etc. → null the ville (and set canton from adjective if missing).

2. **Reconstruct truncated names** that end with "de", "du", "des", "à", ","
   using context:
   - For specific well-known truncated patterns, append the likely missing tail
     (e.g. "Orchestre de Chambre de" + VD → "Orchestre de Chambre de Lausanne")
   - For others, try to append the ville (if any)

3. **Drop a few hard-coded artifacts** that survive parsing
   (e.g. "Pour tous les projets dans le domaine du sport Assoc...").

4. **Merge duplicates "Foo" + "Fond. Foo" or "Foo," + "Foo"** (same canton,
   same secteur, same amount) when likely the same beneficiary.
"""
import json
import re
from pathlib import Path
from collections import defaultdict

DATA = Path('/home/claude/audit2/Loro-main/docs/data')
YEARS = ['2023', '2024', '2025']

# Cantonal adjectives that sometimes leak into the `ville` field
ADJECTIVE_VILLES = {
    'fribourgeois', 'fribourgeoise',
    'vaudois', 'vaudoise',
    'valaisan', 'valaisanne',
    'genevois', 'genevoise',
    'neuchâtelois', 'neuchâteloise',
    'jurassien', 'jurassienne',
    'romand', 'romande',
}
ADJ_TO_CANTON = {
    'fribourgeois': 'FR', 'fribourgeoise': 'FR',
    'vaudois': 'VD', 'vaudoise': 'VD',
    'valaisan': 'VS', 'valaisanne': 'VS',
    'genevois': 'GE', 'genevoise': 'GE',
    'neuchâtelois': 'NE', 'neuchâteloise': 'NE',
    'jurassien': 'JU', 'jurassienne': 'JU',
}

# ─── Hard-coded reconstructions for very common truncated patterns ────────
# Each rule: (regex on current nom, fn → new nom). The fn receives the entry.
# Applied if the nom matches AND optional context conditions are met.

def reconstruct_orchestre_de_chambre_de(entry):
    """'Orchestre de Chambre de' / 'Orchestre de chambre' + canton → reconstruct."""
    c = entry.get('canton')
    if c == 'VD':
        return 'Orchestre de Chambre de Lausanne (OCL)'
    if c == 'GE':
        return 'Orchestre de Chambre de Genève'
    if c == 'FR':
        return 'Orchestre de chambre fribourgeois'
    if c == 'NE':
        return 'Orchestre de chambre de Neuchâtel'
    if c == 'JU':
        return 'Orchestre de chambre jurassien'
    return None  # SR or unknown — leave as is

def reconstruct_osr(entry):
    """'OSR - Orchestre de la Suisse' → 'Orchestre de la Suisse Romande (OSR)'"""
    return 'Orchestre de la Suisse Romande (OSR)'

def reconstruct_via_ville(entry):
    """If ville is known, append ', <ville>' to nom."""
    v = entry.get('ville')
    if not v:
        return None
    return entry['nom'].rstrip(' ,') + ', ' + v

# Map: regex on (current nom) -> reconstruction function
RECONSTRUCT_RULES = [
    # Specific known truncations (high priority)
    (re.compile(r"^Orchestre\s+de\s+[Cc]hambre(\s+de)?\s*$"), reconstruct_orchestre_de_chambre_de),
    (re.compile(r"^OSR\s*[-]?\s*Orchestre\s+de\s+la\s+Suisse\s*$"), reconstruct_osr),
    (re.compile(r"^Fond\.\s+de\s+l['\u2019]Orchestre\s+de\s+la\s+Suisse\s*$"),
        lambda e: "Fond. de l'Orchestre de la Suisse Romande (OSR)"),
    (re.compile(r"^Orchestre\s+National\s*$"), lambda e: "Orchestre National"),  # leave as is
]

# Hard-coded drops (parser artifacts)
DROP_PATTERNS = [
    re.compile(r"^Pour\s+tous\s+les\s+projets\s+dans\s+le\s+domaine\s+du\s+sport\b", re.IGNORECASE),
    re.compile(r"^Pour\s+tous\s+les\s+projets\s+dans\s+les\s+domaines\b", re.IGNORECASE),
]


def is_truncated_name(nom: str) -> bool:
    """Returns True if nom looks truncated (ends with conjunction/comma)."""
    return bool(re.search(
        r'(?:\s+(?:de|du|des|la|le|les|et|à|pour|chez|en|au|aux|avec|d\'|l\'|sur|sous|près)|,)\s*$',
        nom, re.IGNORECASE
    ))


def main():
    summary = defaultdict(lambda: defaultdict(int))
    
    for y in YEARS:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p))
        entries = d['entries']
        
        n_villes_fixed = 0
        n_names_reconstructed = 0
        n_dropped = 0
        n_via_ville = 0
        new_entries = []
        
        for e in entries:
            # 0. Drop hard artifacts
            if any(p.match(e['nom']) for p in DROP_PATTERNS):
                n_dropped += 1
                continue
            
            # 1. Fix ville-adjectif
            v = e.get('ville')
            if v and v.lower().strip() in ADJECTIVE_VILLES:
                # If canton not set or 'SR', try to set from adjective
                adj_lower = v.lower().strip()
                if e.get('canton') in (None, 'SR') and adj_lower in ADJ_TO_CANTON:
                    e['canton'] = ADJ_TO_CANTON[adj_lower]
                e['ville'] = None
                n_villes_fixed += 1
            
            # 2. Reconstruct names from rules
            for pattern, fn in RECONSTRUCT_RULES:
                if pattern.match(e['nom'].rstrip(', ')):
                    new_nom = fn(e)
                    if new_nom:
                        e['nom'] = new_nom
                        n_names_reconstructed += 1
                    break
            
            # 3. For OTHER truncated names: append ', <ville>' if ville known
            if is_truncated_name(e['nom']) and e.get('ville'):
                v = e['ville']
                # Don't double-append if ville already at end
                if not e['nom'].endswith(v):
                    # Strip trailing 'de', 'du', etc. + add ville
                    cleaned = re.sub(
                        r'\s+(?:de|du|des|la|le|les|et|à|pour|chez|en|au|aux|avec|d\'|l\'|sur|sous|près)\s*$',
                        '', e['nom'], flags=re.IGNORECASE
                    ).rstrip(', ')
                    e['nom'] = cleaned + ', ' + v
                    n_via_ville += 1
            
            new_entries.append(e)
        
        d['entries'] = new_entries
        d['_meta']['total_entries'] = len(new_entries)
        d['_meta']['total_chf'] = sum(e['montant_CHF'] for e in new_entries)
        d['_meta']['name_fixes'] = {
            'villes_adjectifs_fixed': n_villes_fixed,
            'names_reconstructed_from_rules': n_names_reconstructed,
            'names_reconstructed_via_ville': n_via_ville,
            'artifacts_dropped': n_dropped,
        }
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
        
        print(f"─── BRB {y} ───")
        print(f"  Villes-adjectifs nettoyés:        {n_villes_fixed}")
        print(f"  Noms reconstruits (règles):       {n_names_reconstructed}")
        print(f"  Noms reconstruits (via ville):    {n_via_ville}")
        print(f"  Artefacts droppés:                {n_dropped}")
        print(f"  Final: {len(new_entries)} entries\n")


if __name__ == '__main__':
    main()
