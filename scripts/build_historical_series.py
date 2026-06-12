"""
Historical series extraction — Pass 4 — A (v13.7-historical)
=============================================================

15 bénéficiaires candidats × années 2023, 2024, 2025.

Source : BRB officiels Loterie Romande
   https://ra.loro.ch/documents/BRB{year}.pdf
"""
import json

CANDIDATS = [
    {"key": "hermitage", "nom_canonique": "Fondation de l'Hermitage", "canton_principal": "VD", "secteur": "Culture (Patrimoine)"},
    {"key": "fondation_conservation_ge", "nom_canonique": "Fondation pour la conservation des biens culturels (Genève)", "canton_principal": "GE", "secteur": "Patrimoine"},
    {"key": "csp_vaud", "nom_canonique": "CSP Centre Social Protestant Vaud", "canton_principal": "VD", "secteur": "Action sociale"},
    {"key": "chuv", "nom_canonique": "Fondation CHUV (recherche médicale)", "canton_principal": "VD", "secteur": "Recherche médicale"},
    {"key": "arc_en_scene", "nom_canonique": "Fondation Arc en Scène (TPR)", "canton_principal": "NE", "secteur": "Culture"},
    {"key": "equilibre_nuithonie", "nom_canonique": "Fondation Equilibre et Nuithonie", "canton_principal": "FR", "secteur": "Culture"},
    {"key": "isrec", "nom_canonique": "Fondation ISREC (cancer)", "canton_principal": "VD", "secteur": "Recherche médicale"},
    {"key": "epfl_plus", "nom_canonique": "Fondation EPFL Plus", "canton_principal": "VD", "secteur": "Formation"},
    {"key": "cinematheque", "nom_canonique": "Cinémathèque suisse", "canton_principal": "VD", "secteur": "Culture"},
    {"key": "plateforme_10", "nom_canonique": "Fondation Plateforme 10 (Lausanne)", "canton_principal": "VD", "secteur": "Culture (Musées)"},
    {"key": "fiff", "nom_canonique": "Festival International du Film de Fribourg (FIFF)", "canton_principal": "FR", "secteur": "Culture"},
    {"key": "gianadda", "nom_canonique": "Fondation Pierre Gianadda", "canton_principal": "VS", "secteur": "Culture"},
    {"key": "corodis", "nom_canonique": "CORODIS (intercantonal danse)", "canton_principal": "R+FR", "secteur": "Culture"},
    {"key": "visions_du_reel", "nom_canonique": "Fondation Visions du Réel (Nyon)", "canton_principal": "VD", "secteur": "Culture"},
    {"key": "festival_cite", "nom_canonique": "Fondation du Festival de la Cité (Lausanne)", "canton_principal": "VD", "secteur": "Culture"},
]

# Extraction manuelle depuis BRB2023.pdf + BRB2024.pdf
# Montants en CHF (attributions de l'année dans le BRB cité)
SERIES = {
    "hermitage":               {2023: 400_000, 2024: 300_000, 2025: 4_000_000},  # 2023 inclut 100k+300k (saison + budget 2024 anticipé)
    "fondation_conservation_ge":{2023: None,    2024: None,    2025: 3_300_000},  # Section GE non extraite
    "csp_vaud":                {2023: 250_000, 2024: None,    2025: 1_376_000},  # 2024 pas trouvé directement (peut-être réparti)
    "chuv":                    {2023: 400_000, 2024: 68_000,  2025: 1_413_378},
    "arc_en_scene":            {2023: None,    2024: 475_000, 2025: 1_345_000},  # Section NE 2023 non extraite
    "equilibre_nuithonie":     {2023: 900_000, 2024: 900_000, 2025: 1_100_000},  # FR Culture
    "isrec":                   {2023: None,    2024: None,    2025: 1_100_000},  # Pas trouvé dans extraits BRB23/24
    "epfl_plus":               {2023: 120_000, 2024: 95_000,  2025: 1_020_000},
    "cinematheque":            {2023: 300_000, 2024: 450_000, 2025: 830_000},
    "plateforme_10":           {2023: 550_000, 2024: 600_000, 2025: 600_000},
    "fiff":                    {2023: None,    2024: 580_000, 2025: 660_000},   # Section FR Culture 2023 non extraite
    "gianadda":                {2023: None,    2024: 350_000, 2025: 350_000},   # Section VS 2023 non extraite
    "corodis":                 {2023: None,    2024: 34_500,  2025: 737_970},   # Réparti sur plusieurs cantons; valeurs partielles
    "visions_du_reel":         {2023: 240_000, 2024: 245_000, 2025: 270_000},
    "festival_cite":           {2023: 320_000, 2024: 350_000, 2025: 393_500},
}

OUT = {
    "_meta": {
        "source": "BRB officiels Loterie Romande, années 2023-2025",
        "urls": "https://ra.loro.ch/documents/BRB{year}.pdf",
        "extraction_method": "Extraction manuelle via web_fetch + parsing PDF text",
        "limitations": (
            "Échantillon récent 2023-2025 (3 années). L'extraction complète 2013-2024 reste à faire — "
            "chaque PDF BRB fait ~100 pages et consomme un budget contexte significatif. "
            "Pour certains candidats, les valeurs 2023 sont None lorsque la section canton "
            "correspondante n'a pas été extraite dans cette passe (typiquement GE, NE, VS, et FR Culture)."
        ),
        "version": "v13.7-historical",
        "todo_continuation": "Compléter sections GE/NE/VS/FR Culture pour BRB2023 + étendre à 2018, 2015, 2013 pour benchmark long-terme.",
    },
    "candidats": [
        {**c, "series": SERIES[c["key"]]}
        for c in CANDIDATS
    ],
}

import os
os.makedirs("docs/data", exist_ok=True)
with open("docs/data/beneficiaires_series_2023_2025.json", "w", encoding='utf-8') as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(CANDIDATS)} candidats")
total_data_points = sum(1 for s in SERIES.values() for v in s.values() if v is not None)
total_slots = sum(len(s) for s in SERIES.values())
print(f"Data points populated: {total_data_points}/{total_slots} ({100*total_data_points/total_slots:.0f}%)")
for c in CANDIDATS:
    ys = SERIES[c["key"]]
    found = sum(1 for v in ys.values() if v is not None)
    print(f"  {c['key']:30s} {found}/3 years")
