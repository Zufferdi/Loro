#!/usr/bin/env python3
"""build_15_piliers.py — Top 15 bénéficiaires structurels présents les 5 ans."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'

# Charger trajectoires consolidées
trajs = json.load(open(DATA / 'trajectories_2021_2025.json', encoding='utf-8'))['beneficiaires']

# Filtre : présence ≥4 années + total ≥1M
piliers = [t for t in trajs if t['nb_years_active'] >= 4 and t['total'] >= 1_000_000]
# Sort par total
piliers.sort(key=lambda x: -x['total'])
# Top 15
top15 = piliers[:15]

# Convertir au format attendu par historical_series.js
out_candidats = []
for t in top15:
    out_candidats.append({
        'nom_canonique': t['nom'],
        'canton_principal': t['canton'] or '—',
        'secteur': t['secteur'] or '—',
        'series': {
            '2021': t['amount_2021'] if t['amount_2021'] > 0 else None,
            '2022': t['amount_2022'] if t['amount_2022'] > 0 else None,
            '2023': t['amount_2023'] if t['amount_2023'] > 0 else None,
            '2024': t['amount_2024'] if t['amount_2024'] > 0 else None,
            '2025': t['amount_2025'] if t['amount_2025'] > 0 else None,
        },
    })

result = {
    '_meta': {
        'description': '15 bénéficiaires structurels (≥4/5 ans actifs, ≥1M cumulé)',
        'years': [2021, 2022, 2023, 2024, 2025],
        'criteria': "Top 15 par cumul 5 ans, présents ≥4 années, ≥1 M CHF cumulés",
        'with_full_5_years': sum(1 for c in out_candidats if all(c['series'].values())),
    },
    'candidats': out_candidats,
    'beneficiaires': out_candidats,  # double key pour compat
}
open(DATA / 'beneficiaires_series_2021_2025.json', 'w', encoding='utf-8').write(json.dumps(result, ensure_ascii=False, indent=2))
print(f"  ✓ beneficiaires_series_2021_2025 — {len(out_candidats)} piliers structurels")
print(f"\n  15 piliers :")
for i, c in enumerate(out_candidats, 1):
    vals = c['series']
    s = '|'.join(f"{vals[str(y)]/1e6:.2f}" if vals[str(y)] else '—' for y in [2021,2022,2023,2024,2025])
    total = sum(v for v in vals.values() if v) / 1e6
    print(f"   {i:>2}. {c['nom_canonique'][:48]:<48} {total:.2f}M  {s}")
