# Changelog Loro Dataviz

## v13.10 — juin 2026 (passe big-batch)

### Data fixes
- **EMS reclassifications v13** : 83 entries Culture → Action sociale (Tertianum, Foyer, Home, Résidence, Seniorenzentrum, Pflegeheim, Fegems, Cogest'ems, Pro-Home)
- **Aliases consolidation** : 30+ aliases canoniques pour fusion noms multi-formes :
  - Tour de Romandie (toutes variantes "Fond. du Tour de Romandie", "Fond. Tour de Romandie", "Tour de Romandie", étapes, etc.)
  - Cinéforom (5 noms fragmentés → 1 entrée : 14M cumulés 2021-2025)
  - FIFF, OSR, Verbier Festival, Tertianum, Théâtre du Jura/Jorat
  - Hermitage, Plateforme 10, Vaud Promotion, FAJE, Lanterne Magique, Hermitage
  - Gianadda, Paléo, Montreux Jazz, NIFFF, Belluard, La Bâtie, Delémont'BD
  - CORODIS, Sport-Toto, Aide Sportive
- **Pattern EMS Personnes âgées** étendu (50 entries → 3,19 M en 2025)
- **Re-build dérivés** avec aliases : cross_2021_2025_top, trajectories_2021_2025, top30_beneficiaires_{2021..2025}, top20_villes_{2021..2025}, beneficiaires_cumul_2021_2025
- **40 fichiers classification** post-traités pour cohérence inter-viz (samples + all_entries consolidés)

### Nouvelles données
- `marquants_2021_2025_top50.json` : 50 bénéficiaires avec 15 enrichis (texte éditorial + citation + source URL + date) — TDR (Chassot, 20min.ch), Verbier Festival (Engstroem, Culture Enjeu), Cinéforom, Lanterne Magique (REISO), Théâtre du Jorat, Théâtre du Jura, OSR, Hermitage, FAJE, Plateforme 10, Vaud Promotion, Équilibre & Nuithonie, Papiliorama, FOJ, Vestiaire social
- `beneficiaires_series_2021_2025.json` : 15 piliers structurels (≥4 ans actifs, ≥1M cumulé)
- `ecosysteme_jeux_2025` dans swisslos.json (Loro 252M / Swisslos 570M / Casinos 348M ; total 1170M vs 1212M en 2024 ; –3,5 %)

### Nouvelle viz JS
- `marquants_50.js` (192 lignes) — viz cliquable avec sparklines 5 ans, filtres "Tous/Avec citation/Consolidés", expand/collapse pour texte éditorial avec citation + source URL + date

### Narratif HTML
- **README** v13.10 réécrit (142 lignes)
- **Acte I** : timeline `curveCatmullRom.alpha(0.5)` (fluidité) ; step 1991 enrichi (Tribolo 1985, PMU Romand 1990, Sport-Toto) ; NEW step **1999** "doublement 50→100M en 8 ans" (Loto Express 5 sept 1994 Yverdon + Tactilo février 1999) ; step 2003 fix (Tactilo lancé 1999, monte à 30 % PBJ en 2003)
- **Acte VI** : intro "Les visages" étendue (fidélité 13 ans, Cinéforom 37M, TDR 13.4M, Verbier 11.8M, Vaud Promotion 13M)
- **Acte VII** : toggle 2024/2025 (drawEcoChart closure refactorisé)
- **Trajectoires** : titre 2023-2025 → **2021-2025** (5 ans), beneficiaires field correct (fix `data.trajectories` → `data.beneficiaires`)
- **26 marquants → 50 marquants** : nouvelle viz `viz-marquants-50` cliquable avec citations en ligne
- **Distribution 5'291** : toggle year 2021-2025 (au lieu de 2025 seul)
- **Jura/NE** : populations actualisées 75k / 180k (OFS fin 2024-2025) ; toggle absolu/proportionnel CHF/hab
- **Top 20 inter-cantonaux** (`initBrbMulticantons`) : `normName` enrichi avec 25 aliases inline (TDR, Cinéforom, FIFF, OSR, Tertianum, Théâtre Jura/Jorat, Gianadda, Paléo, Montreux Jazz, NIFFF, Belluard, La Bâtie, CORODIS, FAJE, Lanterne, Hermitage, Plateforme 10, Fond. Partage, Vaud Promotion, Sport-Toto, Aide Sportive, etc.)
- **15 piliers structurels** : data prête au bon format pour historical_series.js

### Fact-checking (17+ bugs corrigés)
- Date fondation 1937 (pas 1938 ; convention 26 juillet 1937, 1er tirage 22 décembre 1937 Sion par sage-femme valaisanne)
- ×121 multiplication depuis 1937 (258 / 2,13 = 121,24)
- +1129 % paris sportifs 2013→2024 (pas +1226 %)
- Loterie élec −41 % sur 11 ans (2013→2024)
- Tactilo lancé 1999 (pas 2003 ; 30 % PBJ en 2003)
- Théâtre du Jura inauguré 8 octobre 2021 (pas 2016)
- Moutier transfert au Jura 1.1.2026
- +28 M en 6 ans (2019→2025), pas +34 M en 7 ans
- Populations fin 2024 : VD 856k / GE 530k / VS 371k / FR 342k / NE 180k / JU 75k
- LJAr 72,9 % ✓ · 4,3 % jeu à risque ✓ · 5,8 M prévention 2023 ✓ · Casinos ligne ×12 ✓
- "1,7 milliard misés/an" (pas 2 G)
- Step 2020 : −37 % Loterie électronique + bénéfice 224,7 M stable grâce aux réserves

### Stats finales
- 23 195 attributions parsées 2021-2025
- 991,2 M CHF cumulés sur 5 ans
- 107 fichiers JSON
- 15 scripts JS (dont nouveau marquants_50.js)
- 52 scripts Python (pipeline complète)
- 1 734 lignes HTML, 9 actes narratifs, ~32 visualisations
