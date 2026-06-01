# Loro Dataviz · 87 ans de la Loterie Romande

Visualisations interactives des données financières de la **Loterie Romande**
(1938—2025) : bénéfices, ventes par canton, redistribution aux secteurs
associatifs et bénéficiaires nommés.

Site statique 100 % HTML/CSS/JS, déployable sur GitHub Pages sans backend.

🔗 **Démo en ligne** : `https://<user>.github.io/<repo>/` (active GitHub Pages
sur la branche `main`, dossier `/docs`)

---

## Que contient le repo ?

```
loro-dataviz/
├── data/
│   ├── raw/Loro.xlsx              ← source (10 feuilles, ~280 lignes)
│   └── processed/                  ← jeux JSON intermédiaires (vide après build)
├── scripts/
│   └── build_data.py               ← xlsx → 8 fichiers JSON
├── docs/                           ← racine GitHub Pages
│   ├── index.html                  ← récit principal (8 sections)
│   ├── explorer.html               ← explorer · 120 bénéficiaires nommés
│   ├── css/style.css
│   ├── js/
│   │   ├── utils.js                ← helpers communs (format, tooltip, couleurs)
│   │   ├── app.js                  ← orchestration des 8 vis du récit
│   │   └── explorer.js             ← recherche + filtres + sparklines
│   └── data/                       ← JSON servis au navigateur
├── METHODOLOGY.md                  ← qualité des sources, retraitements, limites
└── README.md
```

---

## Les visualisations

| # | Vis | Section | Stack |
|---|-----|---------|-------|
| 1 | **Timeline 1938—2025** avec annotations de presse | `#timeline` | D3 line + annotations |
| 2 | **Anatomie d'un franc** : décomposition du PBJ | `#franc` | SVG barres empilées animées |
| 3 | **Sankey** Jeu → Canton → Secteur | `#flux` | D3 + d3-sankey |
| 4 | **Treemap** des secteurs bénéficiaires | `#secteurs` | D3 treemap |
| 5 | **Tilegram** des 6 cantons romands + classement par habitant | `#cantons` | D3 SVG, slider + autoplay |
| 6 | **Stacked area** du mix de jeux | `#jeux` | D3 stack |
| 7 | **Focus COVID** 2019 → 2021 | `#covid` | D3 dumbbell |
| 8 | **Top 10 bénéficiaires** avec sparklines | `#benefs` | SVG inline |
| 9 | **Explorer** plein écran : 120 bénéficiaires nommés | `explorer.html` | Recherche + filtres + sparklines |

---

## Installation et build

### Prérequis
- Python ≥ 3.9
- `pandas`, `openpyxl`

```bash
pip install pandas openpyxl
```

### Régénérer les données JSON

```bash
python scripts/build_data.py
```

Cela lit `data/raw/Loro.xlsx` et écrit 8 fichiers JSON dans `docs/data/`.

### Servir localement

```bash
cd docs && python3 -m http.server 8000
```

Puis ouvrir `http://localhost:8000/`.

### Déployer sur GitHub Pages

Settings → Pages → Source : `main` branch · `/docs` folder. Le site sera servi à
`https://<user>.github.io/<repo>/`.

---

## Sources de données

| Période | Source |
|---------|--------|
| 1938—2000 | Presse romande (Courrier de Genève, La Tribune de Genève, La Liberté, L'Impartial, Le Nouvelliste, Le Franc-Montagnard, FAN-L'Express, La Gruyère, Journal du Jura) — citations préservées dans la feuille `Historique` |
| 1940—2000 (CA) | Office fédéral de la justice (OFJ) |
| 2000—2025 | Rapports annuels de la Loterie Romande, ESBK/CFMJ pour les casinos, comptes annuels de Swisslos pour comparaison |
| 2013—2025 (détails) | Rapports annuels Loro, ventilation cantonale et sectorielle |

Voir [METHODOLOGY.md](METHODOLOGY.md) pour les limites de comparabilité entre
périodes et le détail des retraitements appliqués.

---

## Stack technique

- **D3.js v7** (line, area, stack, sankey, treemap, scale, transitions)
- **HTML/CSS** vanilla, dark mode automatique (`prefers-color-scheme`)
- **Aucune dépendance build** (pas de bundler) — tout est servi tel quel
- **Polices** : Inter (sans), Source Serif Pro (serif), via Google Fonts
- **Compatibilité** : navigateurs modernes (Chrome, Firefox, Safari 14+, Edge)

---

## Pistes d'extension

- Carte choroplèthe vraie (topojson Suisse cantons) en remplacement du
  tilegram pour les visiteurs qui préfèrent la projection réaliste
- Scrollytelling avec `scrollama.js` pour transformer le récit en
  expérience pas-à-pas
- Comparaison cross-opérateurs : Loro vs Swisslos vs casinos
  (les données existent dans `metrics_annuels.json` sous les clés `Swisslos`
  et `CFMJ`)
- Export PDF / partage sur les réseaux des cartes individuelles
- API JSON publique exposée via GitHub Pages pour les data journalistes

---

## Licence

Code MIT. Données : les chiffres sont publics (rapports annuels Loro, OFJ).
Les citations de presse appartiennent à leurs ayants-droit respectifs et sont
reproduites à des fins de référence journalistique sous l'exception courte
citation.
