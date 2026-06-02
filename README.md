# Loro Dataviz · 87 ans de la Loterie Romande

Récit interactif en six actes (plus un intermède, un acte bis et un récit
incarné) sur les données financières de la **Loterie Romande** (1938—2025) :
bénéfices, redistribution, géographie, gouvernance, bénéficiaires,
dépendance, prévention, jeu problématique, le voyage d'un billet.

Site statique HTML/CSS/JS, déployable sur GitHub Pages.

🔗 **Démo** : `https://<user>.github.io/<repo>/` (Settings → Pages →
`main` / `/docs`)

---

## Structure narrative

| Section | Question | Visualisation |
|---|---|---|
| Hero | 252 millions, vraiment ? | Compteur géant animé |
| Comparaisons | Et concrètement ? | 4 équivalents (TPG, salaires, par habitant, % loteries CH) |
| Acte I | La masse — ×121 en 87 ans | Timeline en scrollytelling |
| Rupture | 88 M pour la culture | Full-bleed |
| **Intermède** | **Le record est-il un nouveau plateau ?** | **Décomposition surplus 2024** (Angle B) |
| Acte II | Anatomie d'un franc | Barre empilée |
| Acte III | La géographie | Carte CH romande + tilegram |
| **Acte III bis** | **Le hasard est dans le tirage. Le choix, dans la commission.** | **Table comparée règles cantonales** (Angle A) |
| Rupture | Paris sportifs ×12 | Full-bleed |
| Acte IV | La mutation | Mix scrollytelling + mix par canton |
| L'envers du décor | 0,3 % à la prévention | Waffle + **viz joueurs à risque** (Angle E) |
| Acte V | La redistribution | Treemap + KPIs |
| Rupture | 5 sur 120 | Full-bleed |
| Acte VI | Les visages | **Dépendance Loro** (Angle C) + hexagon + top 10 |
| **Acte VII** | **La transformation invisible** | **Coûts opérationnels 2019-2024 + capitaux propres + bascule vaudoise 2022** |
| **Récit incarné** | **Le voyage d'un billet de 10 CHF** | **8 étapes graphiques** (Angle D) |
| Coda | Vue d'ensemble | Sankey |

**21 visualisations** distinctes, **12 sections**, scrollytelling sur 2 actes.

---

## Les 5 angles éditoriaux (v4)

### Angle A — La main visible (Acte III bis)
Le bénéfice est ventilé entre cantons, mais c'est le Conseil d'État de
chaque canton qui décide combien il prélève (0 % à GE/VS, 25 % à VD).
Table comparée avec barres de prélèvement.

### Angle B — L'anomalie 2024 (Intermède)
Le record 2024 n'est pas un nouveau plateau. Décomposition du surplus
de +17,6 M : jackpot 64,6 M (9,5 M), Euro/JO (5,5 M), tendance (2,6 M).

### Angle C — Le tissu sous perfusion (Acte VI)
4 cas documentés de dépendance Loro : FriSanté 32 % du budget, Lanterne
magique 27 %, Tour de Romandie 15 % (estimation), Cinéforom 30 % (estim.).
Zone critique au-delà de 25 %.

### Angle D — Le voyage d'un billet (Récit incarné)
Récit visuel d'un Tribolo 10 CHF acheté à Sion en mars 2024. 8 étapes,
mathématiquement cohérentes, jusqu'à 22 centimes pour une association.

### Angle E — Le poids invisible (L'envers du décor)
4,3 % de la population suisse joue à risque ou problématique. La
littérature internationale (UK, Australie) estime que **30-50 % du PBJ**
provient d'eux. Deux waffles côte à côte.

### Acte VII — La transformation invisible (rapports financiers 2019-2024)
Trois découvertes en comparant 6 années de comptes audités :
- **Les coûts informatiques ont bondi de +42 %** (16,7 M → 23,7 M),
  notamment en 2023-2024. La digitalisation est silencieuse mais bien réelle.
- **Capitaux propres** : malgré la redistribution intégrale, +22 M en 5 ans.
  Les logiciels valent désormais 46 M à l'actif (+93 %).
- **Vaud a changé ses règles** : prélèvement Conseil d'État à 0 % en 2020,
  puis 25 % dès janvier 2022 (LVLJAr). Fribourg passe de 7 à 9 % en 2024.

---

## Sources principales

**Loro** : [Rapport annuel 2024](https://ra.loro.ch/), Rapport 2025,
[soutien-loro.ch](https://soutien-loro.ch).
**Cadre légal** : LJAr fédérale, CJA, [CORJA](https://www.loro.ch/sites/default/files/2021-01/CORJA.pdf).
**Swisslos** : [chiffres officiels 2024](https://www.swisslos.ch/fr/informations/sur-swisslos/portrait/chiffres-cle/fait-et-chiffres.html).
**Surveillance et prévention** : [Gespa](https://www.gespa.ch/),
[GREA](https://grea.ch/dossier/jeux/), [PILDJ](https://www.grea.ch/pildj-jeu-excessif-le-programme-intercantonal-de-lutte-contre-la-dependance-au-jeu).
**Analyse de fond** : Jérémie Sanchez, [« La Loterie Romande, source de financement clé »](https://www.reiso.org/articles/themes/pratiques/15008-la-loterie-romande-source-de-financement-cle), REISO, janvier 2026.
**Comparaisons** : [OFS salaires 2024](https://www.bfs.admin.ch/asset/en/36195848),
[TPG budget 2025](https://en.wikipedia.org/wiki/Geneva_Public_Transport),
[Tour de Romandie](https://www.rts.ch/info/regions/2026/article/le-tour-de-romandie-sans-sponsor-principal-voit-son-avenir-menace-29225671.html).

Voir [METHODOLOGY.md](METHODOLOGY.md) pour la liste exhaustive et les
hypothèses formulées.

---

## Structure du repo

```
loro-dataviz/
├── index.html                      ← redirige vers docs/
├── data/raw/Loro.xlsx              ← source
├── scripts/build_data.py           ← xlsx → 8 JSON enrichis
├── docs/
│   ├── .nojekyll
│   ├── index.html                  ← récit en 11 sections
│   ├── explorer.html               ← exploration 120 bénéficiaires
│   ├── METHODOLOGY.html
│   ├── css/style.css               (~19 K)
│   ├── js/utils.js, app.js (~80 K), explorer.js
│   └── data/                       ← 8 JSON (summary.json enrichi avec benchmarks + cas dépendance)
├── METHODOLOGY.md
└── README.md
```

## Stack technique

- **D3.js v7** + d3-sankey + topojson-client
- **Scrollama 3.2** pour le scrollytelling
- **swiss-maps@4** pour les contours cantonaux (CDN runtime)
- HTML/CSS vanilla, dark mode automatique
- Aucune dépendance build

## Installation et build

```bash
pip install -r requirements.txt
python scripts/build_data.py
cd docs && python3 -m http.server 8000
```

## Déploiement GitHub Pages

**Settings → Pages → Source = `main` branch · `/docs` folder.**

Le `index.html` racine redirige automatiquement vers `docs/` en cas de
mauvaise config.

## Licence

Code MIT. Chiffres publics (rapports annuels Loro, OFJ, OFS, GREA, REISO).
