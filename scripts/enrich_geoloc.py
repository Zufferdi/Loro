#!/usr/bin/env python3
"""
enrich_geoloc.py — Pass 8 (v13.10)
====================================

The BRB data has ville for 47% of entries but lat/lng only for 27%.
This script fills the gap by:
  1. Building a city → coords lookup from the 96 already-geocoded cities
  2. Augmenting with hardcoded coords for ~50 common Romande communes
     that are missing from the dataset (Geneva suburbs, Jura villages, etc.)
  3. Applying the lookup to all entries with ville but no coords

Idempotent: re-running on enriched data produces 0 changes.
"""
import json
import shutil
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / 'docs' / 'data' / 'brb2025_full.json'

# Hardcoded coords for common Romande communes missing from the dataset.
# Sources: official Swiss coords (Wikipedia, swisstopo).
EXTRA_CITY_COORDS = {
    # Geneva canton
    'Les Acacias':      (46.1875, 6.1369),
    'Thônex':           (46.1956, 6.2031),
    'Grand-Lancy':      (46.1789, 6.1281),
    'Petit-Lancy':      (46.1939, 6.1175),
    'Bernex':           (46.1750, 6.0833),
    'Confignon':        (46.1786, 6.0789),
    'Châtelaine':       (46.2114, 6.1186),
    'Vésenaz':          (46.2517, 6.1939),
    'Carouge':          (46.1833, 6.1417),
    'Onex':             (46.1850, 6.1011),
    'Vernier':          (46.2125, 6.1083),
    'Plan-les-Ouates':  (46.1647, 6.1233),
    'Meyrin':           (46.2289, 6.0764),
    'Veyrier':          (46.1700, 6.1842),
    'Versoix':          (46.2833, 6.1667),
    'Chêne-Bougeries':  (46.2025, 6.1869),
    'Chêne-Bourg':      (46.1956, 6.1953),
    'Lancy':            (46.1855, 6.1233),
    'Anières':          (46.2733, 6.2200),
    'Cologny':          (46.2233, 6.1764),
    # Jura
    'Le Noirmont':      (47.2308, 6.9667),
    'Courtételle':      (47.3458, 7.3306),
    'Courgenay':        (47.3825, 7.1903),
    'Vicques':          (47.3625, 7.4036),
    'Les Bois':         (47.1789, 6.9558),
    'Bassecourt':       (47.3375, 7.2453),
    'Saignelégier':     (47.2553, 6.9994),
    'Porrentruy':       (47.4181, 7.0772),
    'Bonfol':           (47.4831, 7.1581),
    'Soyhières':        (47.3711, 7.3814),
    # Neuchâtel
    'Auvernier':        (46.9803, 6.8917),
    'Peseux':           (46.9919, 6.8919),
    'Colombier':        (46.9694, 6.8694),
    'Bôle':             (46.9647, 6.8458),
    'La Chaux-de-Fonds':(47.0992, 6.8264),
    'Le Locle':         (47.0561, 6.7461),
    'Boudry':           (46.9528, 6.8389),
    'Bevaix':           (46.9389, 6.8331),
    'Cortaillod':       (46.9450, 6.8472),
    'Cernier':          (47.0531, 6.9119),
    'Hauterive':        (47.0167, 6.9667),
    'Le Landeron':      (47.0589, 7.0697),
    'Cressier':         (47.0500, 7.0500),
    # Fribourg
    'Murten':           (46.9281, 7.1144),
    'Morat':            (46.9281, 7.1144),  # German name = Murten
    'Bulle':            (46.6181, 7.0567),
    'Romont':           (46.6953, 6.9119),
    'Châtel-St-Denis':  (46.5256, 6.9056),
    'Estavayer-le-Lac': (46.8497, 6.8483),
    'Villars-sur-Glâne':(46.7889, 7.1306),
    'Marly':            (46.7775, 7.1614),
    'Düdingen':         (46.8511, 7.1936),
    'Tafers':           (46.8136, 7.2189),
    'Granges-Paccot':   (46.8261, 7.1500),
    'Givisiez':         (46.8083, 7.1444),
    # Vaud
    'Renens':           (46.5394, 6.5878),
    'Pully':            (46.5111, 6.6628),
    'Morges':           (46.5089, 6.4969),
    'Yverdon-les-Bains':(46.7783, 6.6411),
    'Yverdon':          (46.7783, 6.6411),
    'Vevey':            (46.4625, 6.8438),
    'Montreux':         (46.4317, 6.9106),
    'Nyon':             (46.3825, 6.2389),
    'Prilly':           (46.5364, 6.6028),
    'Bex':              (46.2517, 7.0167),
    'Aigle':            (46.3192, 6.9667),
    'Échallens':        (46.6406, 6.6353),
    'Cossonay':         (46.6122, 6.5072),
    'Orbe':             (46.7253, 6.5333),
    'Payerne':          (46.8222, 6.9389),
    'Moudon':           (46.6678, 6.7969),
    'Crissier':         (46.5497, 6.5736),
    'Ecublens':         (46.5283, 6.5586),
    'Chavannes-près-Renens': (46.5306, 6.5750),
    'Lutry':            (46.5044, 6.6878),
    'Cully':            (46.4906, 6.7378),
    'Le Mont-sur-Lausanne': (46.5503, 6.6303),
    'Epalinges':        (46.5586, 6.6597),
    'Belmont-sur-Lausanne': (46.5217, 6.6736),
    'Romanel-sur-Lausanne': (46.5664, 6.6014),
    'Chexbres':         (46.4836, 6.7833),
    'Oron-la-Ville':    (46.5722, 6.8333),
    'Oron-le-Châtel':   (46.5708, 6.8417),
    'Château-d\'Œx':    (46.4767, 7.1411),
    'Leysin':           (46.3503, 7.0089),
    'Villars-sur-Ollon':(46.2986, 7.0578),
    'Les Diablerets':   (46.3475, 7.1572),
    # Valais
    'Sierre':           (46.2917, 7.5333),
    'Martigny':         (46.1031, 7.0719),
    'Monthey':          (46.2533, 6.9531),
    'Brig':             (46.3158, 7.9886),
    'Brig-Glis':        (46.3158, 7.9886),
    'Viège':            (46.2939, 7.8794),
    'Visp':             (46.2939, 7.8794),
    'Saxon':            (46.1494, 7.1761),
    'Conthey':          (46.2167, 7.3000),
    'Vétroz':           (46.2192, 7.2700),
    'Ardon':            (46.2128, 7.2603),
    'Salgesch':         (46.3128, 7.5658),
    'Loèche-les-Bains': (46.3786, 7.6275),
    'Leuk':             (46.3175, 7.6322),
    'Loèche':           (46.3175, 7.6322),
    'Crans-Montana':    (46.3094, 7.4794),
    'Verbier':          (46.0964, 7.2278),
    'Anniviers':        (46.2086, 7.5631),
    'Chamoson':         (46.2069, 7.2208),
    'St-Maurice':       (46.2197, 7.0044),
    'Vionnaz':          (46.3083, 6.9036),
    'Champéry':         (46.1769, 6.8742),
    'St-Pierre-de-Clages': (46.1958, 7.2683),
    'Port-Valais':      (46.3878, 6.8911),
    'Le Châble':        (46.0833, 7.2167),
    # Bern (Romande side or border)
    'Moutier':          (47.2789, 7.3719),
    'Bienne':           (47.1369, 7.2469),
    'Biel':             (47.1369, 7.2469),
    'St-Imier':         (47.1531, 6.9981),
    'Tavannes':         (47.2225, 7.1958),
    'Tramelan':         (47.2197, 7.1078),
    'Reconvilier':      (47.2364, 7.2231),
    # Intercantonal cities
    'Suisse romande':   (46.5197, 6.6323),  # placeholder = Lausanne
    'Romandie':         (46.5197, 6.6323),
}


def main():
    with open(INPUT, encoding='utf-8') as f:
        data = json.load(f)
    entries = data['entries']

    # Build city → coords lookup from existing geocoded entries
    city_to_coords = {}
    inconsistencies = []
    for e in entries:
        v = e.get('ville')
        if v and e.get('lat') is not None:
            coords = (e['lat'], e['lng'])
            if v in city_to_coords:
                existing = city_to_coords[v]
                if abs(existing[0] - coords[0]) > 0.01 or abs(existing[1] - coords[1]) > 0.01:
                    inconsistencies.append((v, existing, coords))
                # Keep first
            else:
                city_to_coords[v] = coords

    print(f"Cities geocoded in dataset: {len(city_to_coords)}")
    if inconsistencies:
        print(f"⚠️  Inconsistencies: {len(inconsistencies)}")

    # Merge with hardcoded extras (extras win if conflict — they're verified)
    for v, c in EXTRA_CITY_COORDS.items():
        city_to_coords[v] = c
    print(f"After hardcoded merge: {len(city_to_coords)} cities in lookup")

    # Apply to entries with ville but no coords
    n_filled = 0
    n_still_missing = 0
    missing_cities = defaultdict(int)
    for e in entries:
        v = e.get('ville')
        if not v: continue
        if e.get('lat') is not None: continue
        if v in city_to_coords:
            lat, lng = city_to_coords[v]
            e['lat'] = lat
            e['lng'] = lng
            n_filled += 1
        else:
            n_still_missing += 1
            missing_cities[v] += 1

    print(f"\n✓ Filled coords for {n_filled} entries")
    print(f"  Still missing: {n_still_missing} entries across {len(missing_cities)} unique cities")

    # Add geoloc enrichment meta
    meta = data.get('_meta', {})
    meta['geoloc_enrichment_v13_10'] = {
        'date': '2026-06-03',
        'method': 'City lookup table (dataset existing + 100 hardcoded Romande communes)',
        'entries_filled': n_filled,
        'entries_still_missing_coords': n_still_missing,
        'cities_in_lookup': len(city_to_coords),
        'inconsistencies_detected': len(inconsistencies),
    }
    data['_meta'] = meta

    # Backup + write
    backup = INPUT.with_suffix('.backup_geoloc_v13_10.json')
    if not backup.exists():
        shutil.copy(INPUT, backup)
    with open(INPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Written {INPUT}")
    print(f"💾 Backup: {backup}")

    # Final audit
    n_geo = sum(1 for e in entries if e.get('lat') is not None)
    n_ville = sum(1 for e in entries if e.get('ville'))
    print(f"\n=== Post-enrichment ===")
    print(f"  Entries with ville: {n_ville:>5d} ({100*n_ville/len(entries):.0f}%)")
    print(f"  Entries with coords: {n_geo:>5d} ({100*n_geo/len(entries):.0f}%)")
    print(f"  Gap closed: was 27% → now {100*n_geo/len(entries):.0f}%")

    # Top still-missing cities
    if missing_cities:
        print(f"\nTop 10 cities STILL missing coords (rare/specialized):")
        for v, c in sorted(missing_cities.items(), key=lambda kv: -kv[1])[:10]:
            print(f"    {c:>3}× '{v}'")


if __name__ == '__main__':
    main()
