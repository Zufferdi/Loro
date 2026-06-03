# Loro Dataviz — Anatomie de la Loterie Romande

Une dataviz éditoriale en 12 actes sur les finances et l'utilité publique de la Loterie Romande (1937-2025).

## Sources principales

- **Rapports financiers Loro 2013-2025** (13 années auditées) — bilan, compte de résultat, répartition par canton
- **Rapports annuels Loro 2012-2025** (14 années) — édito, faits marquants, gouvernance
- **BRB 2024 et 2025** — détail des ~5'000 bénéficiaires par année et par canton
- **Swisslos Geschäftsbericht 2024** — comparaison structurelle avec la cousine alémanique
- **Données historiques 1938-2025** — fichier Excel récapitulatif fourni par la Loro

## Structure

```
loro-dataviz/
├── docs/                       # GitHub Pages root
│   ├── index.html             # 12 actes narratifs, 24 visualisations
│   ├── METHODOLOGY.html       # méthodologie complète
│   ├── css/style.css
│   ├── js/
│   │   ├── utils.js
│   │   └── app.js             # 2'500 lignes, 24 fonctions de viz
│   └── data/                  # 12 JSONs validés
│       ├── summary.json
│       ├── historique.json
│       ├── rapports_financiers.json    # 13 ans 2013-2025
│       ├── beneficiaires_top_vd.json   # 93 bénéficiaires VD 2024-2025
│       ├── swisslos.json               # comparaison structurelle
│       ├── editorial_loro.json         # récit éditorial 2012-2025
│       └── (autres JSONs)
├── scripts/                   # scripts Python build_data
├── README.md
└── METHODOLOGY.md
```

## Sommaire des 12 actes

1. **Acte I — la masse** : 252 M de bénéfice 2025, mis à l'échelle de comparaisons
2. **Intermède** : un siècle de chiffres en perspective
3. **Acte II — l'anatomie** : ventilation des 252 M par mix de jeux
4. **Acte III — la géographie** : carte choroplèthe par canton
5. **Acte III bis — la main visible** : le système de répartition cantonal
6. **Acte IV — la mutation** : changement de mix entre 2010 et 2024
7. **Acte V — la redistribution** : les 9 domaines bénéficiaires
8. **Acte VI — les visages** : 120 bénéficiaires en hexagones
9. **Acte VII — la transformation invisible** : 13 ans de coûts d'exploitation, capital, prélèvements
10. **Acte VIII — l'argent prend des visages** : top bénéficiaires Vaud, Loro vs Swisslos, récit éditorial
11. **Récit incarné** : le voyage d'un billet de 10 CHF
12. **Coda** : ce que la Loro est, ce qu'elle n'est pas

## Déploiement

GitHub Pages directement depuis `docs/`. Aucune build step requise — tout est statique (HTML/CSS/JS/JSON). Le fichier `docs/.nojekyll` désactive Jekyll, qui sinon planterait sur les markdown énormes du dépôt.

## Pipeline de données

Le nettoyage du BRB (Bénéfices Répartis Bruts) est consolidé dans `scripts/pipeline_brb.py` — un pipeline idempotent, auditable, ré-exécutable pour les BRB futurs (2026+). Voir [METHODOLOGY.md](METHODOLOGY.md) section v13.8 et v13.9 pour le détail des 8 stages (split, drop totals, reconstruct_name, clean_nom, clean_desc, clean_ville, dedup, merge_normalized) et des 11 catégories d'audit intégré.

Chiffres BRB 2025 après v13.9 : **5'358 attributions à 4'431 bénéficiaires distincts**, pour un total de **206'947'411 CHF**.

## Crédits données

- Loterie Romande — rapports financiers, BRB, rapports annuels
- Swisslos — Geschäftsbericht 2024 (Bâle, Balmer-Etienne AG)
- BDO SA (Lausanne) — audit Loro 2018-2025
- Deloitte SA — audit Loro 2013-2017
