#!/usr/bin/env python3
"""fix_v20_ville_canton.py — Corriger canton basé sur ville (cas évidents).

ATTENTION : on ne touche PAS les chefs-lieux ambigus (Lausanne, Genève, Fribourg, Sion, Neuchâtel, Delémont)
car des orgs intercantonales y ont leur siège mais peuvent être financées par un autre canton.

On corrige uniquement les villes secondaires non ambiguës.
"""
import json
from pathlib import Path

DATA = Path('/home/claude/audit3/Loro-main/docs/data')

# Villes secondaires non ambiguës (UNIQUEMENT dans un canton)
# Exclus : Lausanne, Genève, Fribourg, Sion, Neuchâtel, Delémont, Bulle, Sierre, Martigny, Yverdon (peuvent avoir orgs intercantonales)
VILLES_UNIQUES = {
    # VD non-chefs-lieux
    'Bussigny': 'VD', 'Renens': 'VD', 'Pully': 'VD', 'Crissier': 'VD',
    'Le Mont-sur-Lausanne': 'VD', 'La Tour-de-Peilz': 'VD', 'Cully': 'VD',
    'Villeneuve VD': 'VD', 'Echallens': 'VD', 'Ecublens': 'VD',
    'Bex': 'VD', 'Aigle': 'VD', 'Vallorbe': 'VD', 'Romainmôtier': 'VD',
    'Gland': 'VD', 'Lutry': 'VD', 'Payerne': 'VD', 'Moudon': 'VD',
    'Avenches': 'VD', 'Le Sentier': 'VD', 'Oron': 'VD', 'Chexbres': 'VD',
    'Prilly': 'VD', 'Renens': 'VD', 'Saint-Sulpice VD': 'VD',
    'Vevey': 'VD', 'Montreux': 'VD', 'Morges': 'VD', 'Nyon': 'VD',
    # GE non-chefs-lieux
    'Carouge': 'GE', 'Carouge GE': 'GE', 'Vernier': 'GE', 'Meyrin': 'GE',
    'Lancy': 'GE', 'Onex': 'GE', 'Petit-Lancy': 'GE', 'Plan-les-Ouates': 'GE',
    'Châtelaine': 'GE', 'Acacias': 'GE', 'Les Acacias': 'GE', 'Cologny': 'GE',
    'Chêne-Bougeries': 'GE', 'Chêne-Bourg': 'GE', 'Versoix': 'GE',
    'Bernex': 'GE', 'Confignon': 'GE', 'Thônex': 'GE',
    # VS non-chefs-lieux
    'Monthey': 'VS', 'Brig': 'VS', 'Brigue': 'VS', 'Verbier': 'VS',
    'Visp': 'VS', 'Naters': 'VS', 'Saxon': 'VS', 'Vouvry': 'VS',
    'Saint-Maurice': 'VS', 'St-Maurice': 'VS', 'Fully': 'VS', 'Conthey': 'VS',
    'Crans-Montana': 'VS', 'Zermatt': 'VS', 'Aproz': 'VS', 'Fiesch': 'VS',
    'St. Niklaus': 'VS', 'Anniviers': 'VS', 'Salgesch': 'VS', 'Sembrancher': 'VS',
    'Savièse': 'VS', 'Hérémence': 'VS', 'Riddes': 'VS', 'Bagnes': 'VS',
    # FR non-chefs-lieux
    'Villars-sur-Glâne': 'FR', 'Murten': 'FR', 'Morat': 'FR', 'Marly': 'FR',
    'Düdingen': 'FR', 'Givisiez': 'FR', 'Romont': 'FR', 'Estavayer-le-Lac': 'FR',
    'Estavayer': 'FR', 'Granges-Paccot': 'FR', 'Châtel-St-Denis': 'FR',
    'Tafers': 'FR', 'Schmitten': 'FR', 'Autigny': 'FR', 'Semsales': 'FR',
    'Vesin': 'FR', 'Le Mouret': 'FR', 'Belfaux': 'FR',
    # NE non-chefs-lieux
    'La Chaux-de-Fonds': 'NE', 'Le Locle': 'NE', 'Boudry': 'NE', 'Couvet': 'NE',
    'Val-de-Travers': 'NE', 'Val-de-Ruz': 'NE', 'Cortaillod': 'NE',
    'Marin-Epagnier': 'NE', 'Saint-Aubin': 'NE', 'Cornaux': 'NE',
    'Saint-Blaise': 'NE',
    # JU non-chefs-lieux
    'Porrentruy': 'JU', 'Saignelégier': 'JU', 'Bassecourt': 'JU',
    'Courrendlin': 'JU', 'Develier': 'JU', 'Courtedoux': 'JU',
    'Courgenay': 'JU', 'Boncourt': 'JU', 'Movelier': 'JU',
    'Le Noirmont': 'JU', 'Les Bois': 'JU',
}


def main():
    total = 0
    examples = []
    for y in ['2021', '2022', '2023', '2024', '2025']:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p))
        fixed = 0
        for e in d['entries']:
            ville = (e.get('ville') or '').strip()
            canton = e.get('canton', '')
            if not ville or not canton: continue
            if canton == 'SR': continue
            expected = VILLES_UNIQUES.get(ville)
            if expected and expected != canton:
                if len(examples) < 5: examples.append((y, e['nom'][:40], ville, canton, expected))
                e['canton'] = expected
                fixed += 1
        if fixed:
            d['_meta'].setdefault('fixes', {})['v20_ville_canton'] = {'count': fixed}
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
        print(f"  {y}: {fixed} cantons fixés via ville")
        total += fixed
    print(f"\n  Total : {total}")
    print(f"\n  Exemples :")
    for y, nom, ville, c, exp in examples:
        print(f"    {y}: '{nom}' ville={ville} canton {c} → {exp}")


if __name__ == '__main__':
    main()
