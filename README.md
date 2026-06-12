# Loro Dataviz — Anatomie de la Loterie Romande (1937 → 2025)

Une dataviz éditoriale longue en **neuf actes** racontant 88 ans de Loterie Romande, de la convention intercantonale du 26 juillet 1937 jusqu'au bénéfice 2025 de 252 M CHF. Le récit articule les **chiffres financiers** (PBJ, bénéfice, structure de coûts), la **géographie cantonale** des reversements, et le **détail nominatif** des ~5 000 projets soutenus chaque année.

[**🔗 Lire en ligne**](https://zufferdi.github.io/Loro/docs/)

---

## 🎯 Ce que la dataviz montre

- **88 ans d'évolution** du bénéfice net (1937 → 2025) avec annotations sur les ruptures (LJAr 2019, COVID 2020, pic 2024 à 258 M)
- **5 ans de détail nominatif** (2021-2025) — 23 205 attributions au total à ~17 600 organisations distinctes
- **Distribution par canton** : VD 856k, GE 530k, VS 371k, FR 342k, NE 180k, JU 75k (populations OFS fin 2024)
- **Distribution par secteur** : Culture 38 %, Sport 18 %, Action sociale 16 %, etc.
- **Visualisations** : timeline scrolly, treemap, sankey, courbes per capita, drill-downs cliquables

---

## 📊 Sources

| Source | Période | Usage |
|---|---|---|
| **BRB (Bulletin de Répartition des Bénéfices)** | 2021 → 2025 (5 ans) | Détail nominatif 23 205 attributions |
| **Rapports financiers Loro** | 2013 → 2025 (13 ans) | Bilan, compte résultat, PBJ, coûts |
| **Rapports annuels Loro** | 2012 → 2025 (14 ans) | Éditos, faits marquants, gouvernance |
| **historique.json** | 1938 → 2025 (88 ans) | Bénéfice net annuel, séries longues |
| **Swisslos Geschäftsbericht** | 2018 → 2025 | Comparaison cousine alémanique |
| **OFS / Statistiques cantonales** | 2024 | Populations par canton |
| **OFSP / ESS 2022** | 2022 | 4,3 % comportement jeu à risque |
| **CFMJ / Gespa** | 2019 → 2024 | Casinos en ligne, exclusions, PBJ |
| **REISO, GREA, Wikipedia, RTS, 24h, Watson** | 2017 → 2026 | Croisement éditorial |

---

## 🏗 Pipeline de traitement (résumé)

```
PDF BRB officiel
   ↓ (parser_brbXXXX.py — un par année car formats différents)
brbXXXX_full.json brut
   ↓ (fix_sectors_via_keywords_v{1..12}.py — 12 passes de classification)
brbXXXX_full.json classifié
   ↓ (build_classifications_with_cross_year_memo.py)
9 fichiers <secteur>_classification_XXXX.json (culture, sports, social…)
   ↓ (build_aggregations_XXXX.py)
top30_beneficiaires, top20_villes, treemap, per_capita
   ↓ (build temporels 5 ans)
beneficiaires_cumul_2021_2025, comparison, cross, trajectories, series
```

**Particularité 2021** : format BRB spécifique (cantons en `VaudVaud`, montants collés au nom, sections multi-lignes, dates 18XX/19XX dans les noms d'associations). Parser dédié `parse_brb2021.py` ; taux de classification 85 % (vs 100 % pour 2022-2025) à cause d'organisations 2021-only sans pattern keyword.

---

## 🗂 Structure des fichiers

```
Loro-main/
├── README.md                       # ce fichier
├── METHODOLOGY.md                  # méthodologie détaillée
├── docs/                           # GitHub Pages root
│   ├── index.html                  # 9 actes narratifs, ~30 visualisations
│   ├── METHODOLOGY.html
│   ├── css/style.css
│   ├── js/
│   │   ├── app.js                  # 5 200 lignes (viz principales)
│   │   ├── utils.js                # helpers communs
│   │   ├── year_selector.js        # toggle 2021-2025
│   │   ├── trajectories.js         # sparklines 5 ans
│   │   ├── compare_2024_2025.js    # comparaison canton 5 ans
│   │   ├── cross_2024_2025.js      # inter-cantonaux
│   │   ├── historical_series.js    # piliers 5 ans
│   │   ├── beneficiaires_cumul.js  # top cumul 5 ans drill-down
│   │   └── …
│   └── data/                       # 104 fichiers JSON validés
│       ├── brb{2021..2025}_full.json   # détail nominatif 5 ans
│       ├── *_classification_XXXX.json  # 9 secteurs × 5 ans = 45 fichiers
│       ├── beneficiaires_cumul_2021_2025.json
│       ├── comparison_2021_2025.json
│       ├── trajectories_2021_2025.json
│       ├── cross_2021_2025_top.json
│       ├── historique.json         # 88 ans bénéfice annuel
│       ├── repartition_secteur.json    # 13 ans × 9 secteurs
│       ├── repartition_canton_jeu.json # 13 ans × 7 jeux × 6 cantons
│       ├── per_capita_{XXXX}.json  # populations fin 2024
│       └── …
└── scripts/                        # 45 scripts Python (pipeline)
    ├── parse_brb{2021..2025}.py
    ├── fix_sectors_via_keywords_v{1..12}.py
    ├── build_classifications_with_cross_year_memo.py
    ├── build_aggregations_XXXX.py
    └── …
```

---

## ✅ Garanties qualité

Les chiffres ont été **systématiquement croisés contre les sources officielles** dans une passe de fact-checking dédiée :

- **17+ bugs factuels corrigés** : date fondation 1937 (pas 1938), Tactilo lancé 1999 (pas 2003), Théâtre du Jura inauguré 8 octobre 2021 (pas 2016), populations cantonales fin 2024, paris sportifs +1129 % (pas +1226 %), bénéfice ×121 depuis 1937, etc.
- **26 affirmations chiffrées validées** : 252 M (2025), 258 M (2024), 438 M PBJ, 19,5 M sport national, 79 M commissions, LJAr 72,9 %, 4,3 % jeu à risque, etc.
- **Sources officielles** : Loro.ch, RTS, 24h, Watson, REISO, OFSP, GREA, presseportal, admin.ch, OCSTAT, vs.ch, vd.ch, stat.ne.ch, stat.jura.ch.

---

## 📐 Note méthodologique

Le BRB capture les **attributions nominatives directes** allant des Organes cantonaux de répartition aux bénéficiaires. Il représente ~85 % du bénéfice total Loro (le reste = sport national Swiss Olympic/ASF/SIHF + FSC + intercantonal). Les chiffres parsés diffèrent donc légèrement des totaux officiels :

- 2021 : 204 M parsé / 220 M officiel aux organes cantonaux / 235 M bénéfice total
- 2025 : 206 M parsé / 230 M officiel aux organes / 252 M bénéfice total

Voir [`METHODOLOGY.md`](METHODOLOGY.md) pour les détails complets.

---

## 🛠 Reproduire / contribuer

```bash
# 1. Servir localement
cd docs/
python3 -m http.server 8000
# → http://localhost:8000/

# 2. Pipeline complète (depuis un PDF BRB téléchargé en .md)
# Tous les scripts utilisent maintenant Path(__file__).resolve().parent.parent,
# aucune édition de chemin nécessaire.

# Parser un nouveau BRB (le chemin du .md peut être passé en argv) :
python3 scripts/parse_brb2025.py /chemin/vers/BRB2025.md

# Appliquer toutes les passes de correction de secteur (v1 → v12 dans l'ordre) :
for v in "" _v2 _v3 _v4 _v5 _v6 _v7 _v8 _v9 _v10 _v11 _v12; do
  python3 "scripts/fix_sectors_via_keywords${v}.py"
done

# Régénérer les classifications par secteur (avec mémoire cross-année) :
python3 scripts/build_classifications_with_cross_year_memo.py

# Régénérer les agrégations finales (top30, villes, treemap, per_capita) :
python3 scripts/build_aggregations.py        # année courante (2025)
python3 scripts/build_aggregations_2024.py   # idem pour les autres années
```

> **Note** — Le pipeline a beaucoup évolué (v13.10+). Les douze scripts `fix_sectors_via_keywords_v{1..12}.py` sont des *passes cumulatives* : chacune ajoute des règles d'override aux précédentes. Une future refactorisation consolidant ces règles dans un seul fichier YAML est envisagée.

---

## 📅 Versions

- **v13.10** (juin 2026) — Passe fact-checking ; corrections factuelles 17 bugs ; populations cantonales fin 2024 ; mise à jour Tactilo 1999, Théâtre du Jura 2021 ; multiplication ×121 (et non ×123)
- **v13.9** (juin 2026) — Intégration BRB 2021 (parser dédié format spécifique) ; pipeline étendue 4 → 5 ans 2021-2025 ; viz toggle 5 boutons
- **v13.8** (juin 2026) — Refonte 5 viz (timeline Jura, flux gov, sankey règles cantons, récit éditorial, carte communes) ; fix sectoriel `repartition_secteur` (trous Sport 2014/2020/2021/2022) ; 12 fix sectoriels keyword
- **v13.7** (mai 2026) — 82 inter-cantonaux ; cross-year memo classification
- **v13.6** (avril 2026) — Nettoyage parser qualité approfondi (186 fusions, 237 noms tronqués, 228 descriptions polluées)

