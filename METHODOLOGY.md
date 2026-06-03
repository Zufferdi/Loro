# Méthodologie et sources

Ce document décrit la qualité des sources, les retraitements appliqués,
les hypothèses formulées et les limites de comparabilité.

## 1. Périmètre

Les données concernent la **Loterie Romande** (Loro), société coopérative
gérant les jeux d'argent autorisés en Suisse romande pour Vaud, Fribourg,
Valais, Neuchâtel, Genève et Jura.

Couverture temporelle du dataset principal :
- **1938—2025** pour le bénéfice annuel agrégé
- **1940—2018** pour le chiffre d'affaires (avec lacunes)
- **2013—2025** pour la ventilation par canton × type de jeu
- **2013—2025** pour la répartition par secteur bénéficiaire
- **2013—2024** pour la dépense par habitant
- **2013—2025** pour les bénéficiaires nommés

## 2. Sources primaires

### Loro — rapports annuels et financiers
- [Rapport annuel 2024](https://ra.loro.ch/) — PBJ 438,2 M, bénéfice 258,2 M,
  241 collaborateurs, 2 400 points de vente, prévention 2,2 M.
- [Rapport financier 2024](https://ra.loro.ch/documents/RF2024-FR.pdf).
- [Communiqué résultats 2025](https://www.loro.ch/fr/documents/communiques) —
  PBJ 429,8 M, bénéfice 252 M, 2 350 points de vente, 221 collaborateurs.

**Rapports financiers détaillés 2019-2024 (Acte VII)** — disponibles sur
[ra.loro.ch/editions-precedentes.html](https://ra.loro.ch/editions-precedentes.html) :
[RF2019](https://ra.loro.ch/documents/RF2019-FR.pdf),
[RF2020](https://ra.loro.ch/documents/RF2020-FR.pdf),
[RF2021](https://ra.loro.ch/documents/RF2021-FR.pdf),
[RF2022](https://ra.loro.ch/documents/RF2022-FR.pdf),
[RF2023](https://ra.loro.ch/documents/RF2023-FR.pdf),
[RF2024](https://ra.loro.ch/documents/RF2024-FR.pdf).
Comptes audités par BDO SA. Extraits manuellement : compte de résultat ligne
à ligne (9 catégories de coûts), bilan (actif/passif), capitaux propres,
base de répartition cantonale officielle, prélèvement Conseil d'État par
canton. **Toutes les sommes ont été vérifiées** contre les sous-totaux
(écart maximum : 1 CHF par arrondi).

### Cadre légal et gouvernance
- [Convention romande sur les jeux d'argent (CORJA)](https://www.loro.ch/sites/default/files/2021-01/CORJA.pdf).
- [Concordat sur les jeux d'argent au niveau suisse (CJA)](https://www.lexfind.ch/fe/de/tol/33184/fr).
- [Loi fédérale sur les jeux d'argent (LJAr)](https://www.fedlex.admin.ch/eli/cc/2018/795/fr), en vigueur depuis 2019.
- Conférence spécialisée des membres de gouvernements concernés par les jeux d'argent — [décisions sport national](https://www.fdkg.ch/fr/actualites/communiques-de-presse/Newsmeldung?newsid=22).
- Plateforme [soutien-loro.ch](https://soutien-loro.ch) (15 organes de répartition).

### Swisslos (comparaison alémanique + Tessin)
- [Chiffres clés Swisslos 2024](https://www.swisslos.ch/fr/informations/sur-swisslos/portrait/chiffres-cle/fait-et-chiffres.html) — PBJ 812,1 M (+10 %), bénéfice 595,7 M.
- [Répartition Swisslos](https://www.swisslos.ch/fr/informations/utilite-publique/utilisation-des-benefices-des-loteries/) — 540 M cantons, 55,7 M sport national.

### Tutelle et prévention
- [Gespa — Autorité intercantonale de surveillance](https://www.gespa.ch/).
- [GREA — dossier "Jeux d'argent"](https://grea.ch/dossier/jeux/) — 0,3 % du PBJ
  va à la prévention ; 4,3 % de la population à risque.
- [PILDJ — Programme intercantonal de lutte contre la dépendance au jeu](https://www.grea.ch/pildj-jeu-excessif-le-programme-intercantonal-de-lutte-contre-la-dependance-au-jeu).

### Analyses indépendantes
- Jérémie Sanchez, [« La Loterie Romande, source de financement clé »](https://www.reiso.org/articles/themes/pratiques/15008-la-loterie-romande-source-de-financement-cle), REISO, janvier 2026 — clé de répartition, prélèvements cantonaux, cas de dépendance.
- *Tribune de Genève*, [« Gros et petits subventionnés de la Loterie romande »](https://www.tdg.ch/gros-et-petits-subventionnes-de-la-loterie-romande-818687381123), juillet 2016 — gouvernance et transparence.
- [La Vie économique](https://dievolkswirtschaft.ch/fr/2025/07/la-reglementation-des-paris-sportifs-en-suisse/) — bénéfice loteries CH 2024 ~850 M.

### Comparaisons sectorielles
- [Wikipedia / TPG Transports publics genevois](https://en.wikipedia.org/wiki/Geneva_Public_Transport) — budget 2025 : 325 M.
- [OFS — Enquête structure des salaires 2024](https://www.bfs.admin.ch/asset/en/36195848) — salaire médian suisse 7 024 CHF/mois.
- [Cinéforom](https://www.cineforom.ch/) — budget 10 M.
- [RTS, avril 2026](https://www.rts.ch/info/regions/2026/article/le-tour-de-romandie-sans-sponsor-principal-voit-son-avenir-menace-29225671.html) — budget Tour de Romandie ~5 M.

## 3. Hypothèses et estimations

### Sankey jeu → canton → secteur
Les liens canton → secteur ne sont pas directement publiés (chaque canton
distribue selon ses priorités propres). Nous **estimons** cette ventilation
en répartissant chaque montant sectoriel proportionnellement à la part du
canton dans la Répartition totale de l'année. Les épaisseurs des liens sont
donc indicatives, pas exactes.

### Décomposition du surplus 2024
La décomposition des +17,6 M par rapport à 2023 (jackpot 9,5 M, Euro/JO 5,5 M,
tendance 2,6 M) est notre **estimation** basée sur :
- Le DG Moner-Banet attribue le record au jackpot Swiss Loto record de 27
  semaines (record du 2 mars 2024 : 64,6 M).
- L'Euro de foot et les JO ont fait progresser JouezSport de +24,6 %.
- La croissance organique implicite (~1 % du PBJ) sur la part stable.

Ces poids relatifs ne sont pas publiés par la Loro ; ils représentent notre
meilleure répartition à partir des éléments qualitatifs disponibles.

### Voyage d'un billet
Modélisation simplifiée à partir de la structure de coûts publiée :
- PBJ / mises ≈ 27 %.
- Coûts opérationnels / PBJ = 41 % (REISO 2026).
- Bénéfice net / PBJ = 59 %.
- Sport national / bénéfice = 8,8 % (19,5 M sur 258,2 M).
- Clé Valais ≈ 15 % du résiduel (population + PBJ local).
- Prélèvement Valais = 0 % (RA Loro + REISO).

### Part Loro chez les bénéficiaires
Pour les associations citées (Angle C) :
- **FriSanté** : 176 000 / ~550 000 = 32 % — sourcé REISO + Rapport d'activité FriSanté 2024.
- **Lanterne magique** : 678 000 / ~2,5 M = 27 % — Rapport 2023-2024.
- **Tour de Romandie** : ~750 k / 5 M = 15 % — *estimation* basée sur le
  fait que le TdR est financé exclusivement par les fonds de loterie cantonaux
  (rtsl, tourderomandie.ch) et qu'une partie significative passe par la Loro.
- **Cinéforom** : ~3 M / 10 M = 30 % — *estimation* basée sur le rôle
  prépondérant de la Loro dans le financement du fonds (aropa.ch, cineforom.ch).

### Joueurs problématiques (Angle E)
L'estimation que 40 % du PBJ provient des joueurs à risque ou problématiques
est tirée de la **littérature internationale** (Royal Society of Public Health
UK ; Productivity Commission of Australia 2010 ; Williams et al. 2014). Aucun
chiffre officiel suisse ne mesure cette part. La fourchette internationale va
de 30 à 50 %.

## 4. Limites connues

- **Loterie électronique** : la dépense par habitant pour ce sous-segment
  contient un biais (offre Tactilo restreinte dans certains contextes).
- **Sport** : ligne "Sport" de la répartition absente pour 2014, 2020—2022.
- **Bénéficiaires nommés** : la liste de 120 organisations n'est pas exhaustive.
  La Loro évoque 5 000 projets soutenus en 2024.
- **Données avant 1980** : reconstituées par la presse, par construction incomplètes.

## 5. Reproductibilité

```bash
python scripts/build_data.py
```

Script déterministe. Pour mise à jour annuelle, remplacer `data/raw/Loro.xlsx`.

## 6. Mentions des sources dans les visualisations

Chaque visualisation cite ses sources directement dans son `viz-footer`.
Les chiffres "Loro" (RA 2024, RA 2025) sont primaires. Les chiffres
externes (TPG, OFS, GREA, Swisslos, REISO) sont identifiés par leur URL.
Les chiffres marqués *estimation* sont nos calculs avec hypothèses
documentées dans ce fichier.

## Sources additionnelles v7 (Acte VIII)

- **[BRB 2024](https://ra.loro.ch/documents/BRB2024.pdf)** et **[BRB 2025](https://soutien-loro.ch/sites/default/files/2026-05/BRB2025.pdf)** : Bulletins de Répartition des Bénéfices, ~80 pages chacun, ~5'000 bénéficiaires individuels par année. Échantillon ≥ 200 k CHF retenu pour la viz détaillée (canton de Vaud).
- **[Rapports annuels Loro 2012-2025](https://ra.loro.ch/editions-precedentes.html)** : 14 années de récit éditorial (édito direction, faits marquants, lancements de jeux, certifications).
- **[Swisslos Geschäftsbericht 2024](https://www.swisslos.ch/media/swisslos/publikationen/pdf/gesch%C3%A4ftsbericht-2024.pdf)** (Balmer-Etienne AG) : structure de coûts complète en allemand, traduite ici pour la comparaison structurelle Loro vs Swisslos.
- **[Chiffres-clés Swisslos](https://www.swisslos.ch/fr/informations/sur-swisslos/portrait/chiffres-cle/fait-et-chiffres.html)** : série historique 2024-2025, 20 cantons membres + Liechtenstein.

### Limites de la comparaison Loro/Swisslos

- Les deux loteries opèrent sous le même cadre légal (LJAr 2019) et la même surveillance (Gespa).
- Loro est une association à but non lucratif (art. 60 CC) ; Swisslos est une coopérative intercantonale.
- Loro = 6 cantons, 2,36 M habitants ; Swisslos = 21 cantons (+FL), ~6,5 M habitants.
- Le poste « Marketing/Publicité+Promo » côté Swisslos additionne `Werbung` (13,1 M) + `Promotionen` (7,1 M) + `Sponsoring/Kooperation` (5,3 M). Pour Loro, c'est la ligne `Marketing, publicité et communication` (15,4 M).
- Les périodes comptables sont identiques (1er janvier - 31 décembre).

## v10 (juin 2026) — Audit UX/UI & couverture historique 2018-2025

### Bugs UX corrigés

**Parallax Acte I (timeline scrolly)**
- Le `clipPath` initialisé à `width:0` cachait toute la courbe quand scrollama ne se déclenchait pas (problème de timing au load)
- Remplacé par `stroke-dasharray` + `stroke-dashoffset` (technique standard, plus robuste)
- Ajout d'un fallback `IntersectionObserver` natif si scrollama indisponible
- ViewBox élargi à 1100×620, layout grid passé à 1.5fr/1fr
- Signal visuel renforcé : grand chiffre flottant qui s'actualise à chaque step, pulse animé sur le point actif

**Mêmes corrections appliquées à initMixScrolly** (Acte IV)
- ViewBox élargi 1100×620, légende plus grande
- Fallback IntersectionObserver
- Steps qui réagissent au scroll up

**Hardcodés 2024 éliminés**
- Tilegram, RealMap, Governance, MixByCanton, Anomaly : tous lisent dynamiquement la dernière année disponible

### Nouvelles fonctionnalités

**Décomposition par année 2018-2025** (Intermède)
- Refonte complète de `initAnomaly` : montre maintenant le bénéfice annuel 2018-2025 (waterfall)
- Cliquez sur n'importe quelle barre pour ouvrir la décomposition narrative
- 8 années documentées avec les facteurs explicatifs sourcés des éditos directeur :
  - 2018 : vote LJAr (73 % de oui le 10.6.2018)
  - 2019 : 1ère année LJAr, opérateurs étrangers bloqués (+14 M), record PBJ
  - 2020 : Covid, fermeture cafés-restaurants (-22 M), Loterie électronique -30 %
  - 2021 : rebond, CORJA en vigueur, soutien cafés-restaurants 3,3 M
  - 2022 : Coupe du Monde Qatar, PBJ record 435 M, mais -15,6 M sur placements
  - 2023 : transition, investissement IT +34 %, lancement EuroDreams
  - 2024 : record (jackpot Swiss Loto 64,6 M, Euro + JO)
  - 2025 : reflux (-6,2 M, cycles EuroMillions courts)

**Treemap secteur animé** (Acte V)
- Slider 2013-2025 + bouton « Animer » (transitions D3 fluides entre années)
- La métamorphose de la culture (de 28 % à 38 % du total) devient visible
- Bind par nom de secteur : couleurs et positions se réorganisent en douceur

**Carte Suisse romande : bouton Animer ajouté** (Acte III)
- Comme dans la version tilegram stylisé, le bouton parcourt 2013-2025

**Acte VI : texte corrigé**
- "120 bénéficiaires" → "~5'000 projets soutenus chaque année"
- L'échantillon de 120 noms est présenté comme tel : sélection visible tirée des BRB et rapports annuels
- Liens directs vers la liste complète sur soutien-loro.ch

## v11 (juin 2026) — Extension multi-canton + cas de dépendance documentés

### Cas de dépendance enrichis (Acte VIII / dot plot)

Ajout de 3 nouveaux cas documentés au `summary.cas_dependance`, désormais 6 cas, sourcés :

| Bénéficiaire | Canton | % budget | Source primaire |
|---|---|---|---|
| FriSanté | FR | 32 % | REISO (jan. 2026) |
| Fond. Cinéforom | Romandie | 30 % | CultureEnJeu nº53 (G. Ruey) |
| La Lanterne magique | Romandie | 27 % | REISO (jan. 2026) |
| Théâtre des Osses | FR | 20 % | CultureEnJeu nº53 (M.-C. Jenny) |
| La Plage des Six Pompes | NE | 15 % | CultureEnJeu nº53 (N. Vogt) |
| Tour de Romandie | Romandie | 15 % | Estimations presse |

Les témoignages directs des directrices et présidentes d'associations (publiés dans CultureEnJeu nº53 en mars 2017) restent pertinents : « Le don de la Loro est toujours proche des 20 % du budget global » (Théâtre des Osses) ; « La perte de ce soutien serait catastrophique » (La Plage des Six Pompes).

### Bénéficiaires par canton — données 2024 et 2025 (`dependance_cantons.json`)

43 bénéficiaires notables identifiés et structurés sur les 6 cantons romands :

- **VD** (9) : FASC 46 M (2025), Fonds sport 12,8 M (2025), Théâtre du Jorat 2,5 M, FAJE 1,5 M, Opéra Lausanne, Béjart, OCL, Hermitage, Vidy
- **FR** (12) : Equilibre & Nuithonie 970k (2025), Ligue cancer 778k, FIFF 660k, Pro Senectute, La Tuile, Banc Public, Théâtre des Osses, OC Fribourgeois, Nouvel Opéra, Fri-Son, Belluard
- **VS** (4) : Verbier Festival 975k, Pierre Gianadda 625k, total délégation 36 M (2025), Fonds sport 5,4 M (2025)
- **NE** (4) : ORNE 13,7 M (2025, 485 dossiers), LoRo-Sport 2,25 M, FAC 1,57 M, La Plage des Six Pompes
- **GE** (5) : Fonds genevois 14,15 M (1er trim. 2026, 170 institutions), OSR, Cinéforom, Fond. Hainard, ASL
- **JU** (9) : total 7,5 M (2025), Plan climat 624k, Jura Tourisme 300k, Bien vieillir 280k, Musique des Lumières 175k, Crescendo 150k, Musée jurassien, Théâtre du Jura, Dritchino

Chaque entrée comporte : nom, secteur, montant, année, narratif explicatif, source précise (presse romande ou rapport d'activité officiel).

### Nouvelle UX
- **Sélecteur d'année** dans la section bénéficiaires par canton : « Toutes », « 2024 », « 2025 », « 2026 ». Permet de comparer l'évolution.
- **Onglets canton** : VD / FR / GE / VS / NE / JU avec compteur de bénéficiaires et somme visible
- **Hover détaillé** : narratif + source pour chaque cas
- **Bordure colorée** : chaque canton a sa couleur identitaire propagée dans les cartes

## v12 (juin 2026) — Acte IX : l'inventaire complet (BRB 2025)

Cette version intègre la **Répartition des bénéfices 2025** publiée par la Loterie Romande (BRB 2025, ~80 pages, ~5'000 entrées) sous forme d'un dataset interrogeable de **594 bénéficiaires nommés** couvrant les 6 cantons romands.

### Dataset `brb2025_full.json`

- **594 entrées** structurées : `{nom, ville, montant_CHF, secteur, description, canton, lat, lng}`
- **6 cantons couverts** : VD 236, VS 158, FR 152, NE 15, GE 15, JU 13, plus 5 entrées Suisse romande (organes intercantonaux)
- **9 secteurs** : Culture (242), Action sociale (88), Sport (84), Patrimoine (47), Jeunesse (41), Santé (37), Tourisme (33), Environnement (11), Formation (11)
- **140,8 M CHF observés** dans cet échantillon (sur ~252 M réels redistribués en 2025)
- **Top 10 = 39,8 %** de la masse de l'échantillon (longue traîne)
- **518/594 (87 %) géolocalisées** avec lat/lng pour ~250 villes de Suisse romande

### Méthodologie d'extraction

- Source : `https://soutien-loro.ch/sites/default/files/2026-05/BRB2025.pdf`
- Extraction PDF via web_fetch (les ~58 premières pages du PDF — VD complet, FR complet, VS partiel jusqu'aux bourses sportives)
- Couverture exhaustive ≥ 100 kCHF pour VD, FR, VS
- Échantillon représentatif des montants moyens (10-100 kCHF) et de la longue traîne (< 10 kCHF) pour démontrer la forme statistique
- NE, GE, JU : entrées documentées dans `dependance_cantons.json` + organes répartiteurs (totaux cantonaux)
- Coordonnées géographiques attribuées manuellement à partir des noms de villes

### Trois visualisations ajoutées (Acte IX)

1. **Explorateur (`#viz-explorer`)** — Interface de recherche full-text avec filtres par canton (pills colorées) et secteur, tri par montant/nom/canton. Liste paginée à 200 entrées max avec barre de longueur proportionnelle au montant.
2. **Longue traîne (`#viz-longtail`)** — Nuage de points D3 avec rang (1 → 594) en abscisse et montant en ordonnée (échelle log). Couleur par canton, ligne de référence à la médiane, top-3 annoté. Démontre visuellement la forme « few-big-many-small ».
3. **Carte géographique (`#viz-geomap`)** — Projection Mercator centrée sur la Suisse romande. Bulles par ville agrégées (somme des montants), rayon √ (échelle sqrt). Labels pour les 12 premières villes. Tooltip détaillant les 5 plus gros bénéficiaires de chaque ville.

### Couleurs cantonales (cohérence v11)

VD #e44d4d · FR #5b8def · VS #f0a93d · NE #7c5bc7 · GE #2ea08a · JU #c97b3a · R #888

### Limites connues

- L'extraction n'est pas exhaustive : le PDF complet contient ~5'000 entrées, dont l'extraction texte se cantonne aux 58 premières pages dans le cadre des limites de tokens.
- Les NE/GE/JU sont sous-représentés dans cet échantillon : on dispose des totaux cantonaux (organes répartiteurs) mais peu d'entrées individuelles ligne-par-ligne.
- La médiane à 90 kCHF est artefactuelle : un échantillon non biaisé montrerait une médiane bien plus basse (de l'ordre de 5-10 kCHF) compte tenu de la masse des petits soutiens sportifs.
- Les coordonnées géographiques ont été attribuées manuellement à partir d'un dictionnaire de villes ; quelques erreurs possibles pour les hameaux.

### Navigation enrichie

Le lien « IX » dans la topnav pointe sur `#acte-9`. La section s'intercale entre Acte VIII bis (Jura) et le Récit incarné, formant un crescendo : du global (Actes I-V) au cas (Actes VI-VIII) à l'inventaire complet (Acte IX) au récit (voyage du billet) à la synthèse (Coda).

## v13 (juin 2026) — Parse PDF complet, Loro vs Swisslos 2025, fix parallax

### Dataset BRB 2025 complet (5'172 entrées)

Le PDF officiel `BRB2025.pdf` (118 pages) a été parsé intégralement avec `pdfplumber` + détection géométrique des colonnes :

- **5'172 entrées** structurées (vs. 594 dans v12) — couvre l'essentiel des ~5'000 projets soutenus
- **Distribution par canton** : VD 1306, GE 889, FR 795, VS 710, NE 635, JU 620, Suisse romande 220
- **9 secteurs** : Sport (2287), Culture (1522), Environnement (363), Action sociale (358), Jeunesse (302), Santé (124), Patrimoine (89), Formation (84), Tourisme (46)
- **Total observé** : 211,7 M CHF (le reste = forfaits agrégés, fonds d'utilité publique non détaillés ligne par ligne)
- **Médiane** : 8'250 CHF — la vraie longue traîne devient visible

### Méthodologie de parsing

Le pipeline final (`brb/parser_v4.py` + `brb/export_full.py`) :

1. Extraction word-level via pdfplumber avec coordonnées (x, y) pour chaque mot
2. Clustering en lignes (tolérance y ~3px) et colonnes (clustering x0)
3. Tracking d'état canton via les ranges de pages connus :
   - VAUD pages 3-30, FRIBOURG 31-48, VALAIS 49-62, NEUCHÂTEL 63-76, GENÈVE 77-98, JURA 99-110, Suisse romande 111-116
4. Détection automatique des sections (9 domaines) et sous-sections sport
5. Section Sport forcée quand l'organe contient "fonds du sport" ou similaire
6. Extraction du nom et de la ville par regex (virgule + lieu en capitale)

### Limites du parsing automatique

- ~430 fausses "villes" extraites (descriptions mal segmentées comme "Participation au Championnat", "LNA équipe masculine") ont été filtrées en post-traitement ; le champ `ville` passe alors à `null`
- Quelques noms restent tronqués d'un caractère (`ond. Cinéforom` au lieu de `Fond. Cinéforom`) sur les pages où les boundaries de colonnes coupent un peu trop à gauche
- 46% des entrées ont une ville extraite, 27% sont géolocalisées (dictionnaire de ~250 communes romandes)
- Total observé 211,7 M < 252 M réels : le différentiel correspond aux forfaits cantonaux (Conseils d'État, déléguations) qui n'apparaissent pas comme bénéficiaires individuels

### Acte VIII — comparaison Loro vs Swisslos étendue à 2025

La visualisation `initLoroVsSwisslos` a été refondue pour afficher les deux exercices 2024 et 2025 côte à côte sur 17 métriques.

**Nouvelle lecture** : pour chaque ligne, deux barres groupées dans chaque camp — 2024 en transparence, 2025 en plein. Les barres hachurées (stroke pointillé) signalent des estimations, car ni le Rapport financier Loro 2025 ni le Geschäftsbericht Swisslos 2025 ne sont publiés à la date du build.

**Sources 2025** :

- **Loro** : communiqué officiel du 26 mai 2026 (PBJ 429,8 M, bénéfice 252 M, commissions 79,2 M aux 2350 points de vente, 5000 projets soutenus, taxe jeu excessif 2,15 M) ; BRB 2025
- **Swisslos** : "Zahlen und Fakten 2025" (https://static.swisslos.ch/media/swisslos/publikationen/pdf/zahlen-und-fakten-2025.pdf), seule publication 2025 disponible. Reingewinn 562 M, 202 collaborateurs (94F + 108H, 64 Teilzeit), 506 M aux fonds cantonaux et 56 M à la Stiftung Sportförderung Schweiz.

**Estimations** : pour Swisslos, le PBJ/BSE 2025 est dérivé de la répartition "25 Rp Reingewinn pour 1 franc joué" → mises ≈ 2'248 M, donc BSE ≈ 764 M (vs. 812 M en 2024). Les commissions sont estimées au prorata du ratio 2024 (15,8% du PBJ). Les autres lignes restent en `n.d.` quand non disponibles.

### Lisibilité des intitulés

- Labels métriques **à gauche** (au lieu de centrés et tronqués), 13px gras
- Unité affichée en plus petit (10px) sous le label
- Hauteur de ligne augmentée à 40px pour accueillir les deux années
- Légende avec carrés couleur (transparent = 2024, plein = 2025) en haut de chaque camp
- Note explicative sous le graphique sur la signification des barres hachurées

### Fix parallax timeline (Acte I)

Le scrolly de la timeline 1938-2025 ne montrait initialement qu'une fine ligne d'arrière-plan à opacité 0.18 (quasi invisible) ; la courbe principale ne s'animait qu'au scroll, donnant l'impression d'un graphe vide tel que visible sur la capture utilisateur.

**Changement** :
- Courbe d'arrière-plan : `stroke-width 1 → 2`, `opacity 0.18 → 0.32` — la trajectoire 1938-2025 est désormais visible d'emblée
- Courbe principale : `stroke-width 2.8 → 3.2` — plus marquée quand elle s'illumine au scroll
- Points : `opacity 0 → 0.35` par défaut — chaque année est visible dès le chargement, le pulse de focus reste l'élément de zoom

La courbe complète apparaît donc dès le chargement, et le scrollytelling vient illuminer la portion jusqu'à l'année active sans cacher la trajectoire globale.

### Données touchées

- `docs/data/brb2025_full.json` : 1,77 MB, 5172 entrées, schéma `{nom, ville, montant_CHF, secteur, description, canton, lat, lng, organe, sous_section}`
- `docs/data/swisslos.json` : ajout du bloc `comparaison_loro_2025` avec sources et `swisslos_est`/`loro_est` par ligne
- `docs/js/app.js` : `initTimelineScrolly` (parallax), `initLoroVsSwisslos` (refonte complète 2 années)
- `docs/index.html` : titre + sous-titre + footer de la viz Loro vs Swisslos mis à jour

### Outils de parsing

`brb/parser_v4.py` et `brb/export_full.py` sont versionnés dans le dépôt pour permettre de re-parser une future édition du BRB (BRB 2026 le moment venu) avec un effort minimal.

## v13.1 (juin 2026) — Bugfix critique : redéclaration JavaScript

### Le bug

Le déploiement v13 (livré le 02.06.2026) ne rendait correctement **aucune visualisation** sur le site en production. Diagnostic via Playwright headless :

```
[PAGE_ERROR] Identifier 'CANTON_COLORS' has already been declared
```

Cause : au début du bloc Acte IX (ligne 3383 de `docs/js/app.js`), j'avais redéclaré au top-level `const CANTON_COLORS`, `const CANTON_LABELS`, `const SECTEUR_COLORS` et `function fmtCHF`. Ces 4 identifiants existaient déjà dans `docs/js/utils.js` (chargé avant `app.js`).

**Pourquoi tout est cassé, pas juste l'Acte IX** : en JavaScript classique en `<script>`, **tout le fichier est parsé avant de s'exécuter**. Un `SyntaxError` au top-level empêche l'exécution complète d'`app.js`. Aucune init (timeline, comparisons, scrolly, BRB explorer, etc.) ne s'exécute. Sur le PDF que l'utilisateur m'a envoyé : 30 visualisations vides, juste les blocs HTML statiques s'affichent.

### La méthodologie de check était insuffisante

`node --check js/app.js` validait correctement la syntaxe **par fichier**. Mais il ne pouvait pas détecter une collision **inter-fichiers** au scope global. Pour la suite, le check doit toujours inclure un test navigateur réel (Playwright + capture des `pageerror`), pas juste `node --check`.

### La correction

Renommage des helpers spécifiques au BRB pour éviter toute collision future :

- `CANTON_COLORS` → suppression (réutilise celui de `utils.js`) + helper `brbCantonColor(c)` qui ajoute la clé `'R'` (Suisse romande) absente de `utils.js`
- `CANTON_LABELS` → `BRB_CANTON_LABELS` (inclut `'R'`)
- `SECTEUR_COLORS` → `BRB_SECTEUR_COLORS` (clés courtes : 'Action sociale', 'Sport', etc., différentes de `SECTOR_COLORS` dans `utils.js` qui utilise les clés longues du PDF)
- `fmtCHF` → `brbFmtAmt(v)` (renvoie `"X M"` / `"X k"` sans suffixe « CHF », alors que `fmtCHF` de `utils.js` renvoie `"X CHF"`)

18 lignes d'usage mises à jour dans la zone BRB (initBrbExplorer, initBrbLongtail, initBrbGeomap).

### Sous-titres HTML désynchronisés

Pendant que j'y étais : les sous-titres HTML des trois viz de l'Acte IX disaient toujours « 594 bénéficiaires » alors que le dataset v13 en a 5172. Correction :

- `<h3>594 bénéficiaires…</h3>` → `<h3>5'172 bénéficiaires…</h3>`
- `<h3>Distribution des 594 montants…</h3>` → `<h3>Distribution des 5'172 montants…</h3>`
- Sous-titre carte : « 250+ villes » → « communes de Suisse romande » (la couverture géocodée est de 27% sur les 5172 entrées, 129 villes uniques)
- Footer carte : « 87% des entrées » → « environ 27% »

### Validation finale

Test Playwright avec D3 chargé localement → **22/28 viz rendent** (les 6 « vides » sont en réalité des viz HTML non-SVG : tables, listes, cards — qui s'affichent normalement). Aucune erreur JavaScript. BRB explorer affiche bien « 5'172 bénéficiaires · 211.27 M CHF au total » et les 200 premières rows.

### Fichiers touchés en v13.1

- `docs/js/app.js` : remplacement des 4 déclarations dupliquées + 18 lignes d'usage
- `docs/index.html` : 3 sous-titres + 1 footer mis à jour

## v13.2 (juin 2026) — Fix parallax (sticky cassé par overflow-x: hidden)

### Le bug

L'utilisateur signalait qu'après scroll dans la section timeline, la courbe disparaissait et seules les cards de droite restaient visibles. Diagnostic Playwright en capturant la position du `.graphic` à 8 positions de scroll :

```
Frame 0: scrollY=1806 graphic.top=90   (visible)
Frame 1: scrollY=2461 graphic.top=-565 (sorti par le haut !)
Frame 2: scrollY=3115 graphic.top=-1219
...
```

Le `position: sticky` était bien appliqué (computed style correct, `top: 60px`) mais ne s'engageait jamais — la graphique défilait comme `position: static`.

### Cause

Deux problèmes additifs :

1. **`overflow-x: hidden` sur `body`** (style.css ligne 59) : courant pour empêcher le scroll horizontal accidentel, mais ça transforme le body en "scroll container". Conséquence : tout `position: sticky` dans la page utilise le body comme cadre de référence, pas la viewport. Le sticky devient inopérant côté viewport.

2. **Grid item sans `align-self: start`** : dans un layout `display: grid`, un grid item s'étire par défaut sur la hauteur de sa ligne (`align-self: stretch`). Comme `.steps` faisait 4580px de haut, `.graphic` s'étirait aussi à 4580px, donc son `top: 60px` n'avait plus aucun espace de coulissement.

### Le fix

**`docs/css/style.css` ligne 59** :

```css
/* AVANT (cassé) */
body { overflow-x: hidden; }
/* APRÈS (sticky fonctionne) */
body { overflow-x: clip; }
```

`overflow-x: clip` empêche le scroll horizontal **sans** créer un scroll container — exactement le comportement attendu pour position: sticky. Supporté par tous les navigateurs modernes (Chrome 90+, Firefox 81+, Safari 16+).

**`docs/css/style.css` lignes 269 + 282** : ajout de `align-self: start` sur `.scrolly .graphic` (desktop + mobile) pour que l'élément sticky ne s'étire pas à la hauteur de la grid row mais conserve sa hauteur intrinsèque (`calc(100vh - 100px)`), laissant de la place pour le scroll relatif.

### Validation

Re-test Playwright après fix :

```
Frame 0: scrollY=1806 graphic.top=90   (arrivée, position normale)
Frame 1: scrollY=2461 graphic.top=60   (sticky engagé ✓)
Frame 2: scrollY=3115 graphic.top=60   (toujours collé ✓)
Frame 3: scrollY=3769 graphic.top=60   (toujours collé ✓)
Frame 4: scrollY=4423 graphic.top=60   (toujours collé ✓)
Frame 5: scrollY=5078 graphic.top=60   (toujours collé ✓)
Frame 6: scrollY=5732 graphic.top=-56  (fin de section, normal)
Frame 7: scrollY=6386 graphic.top=-710 (hors section)
```

Confirmation : la courbe reste maintenant collée à gauche pendant que les 5 cards (1938, 1991, 2003, 2020, 2024) défilent à droite. Comportement identique sur le scrolly « mix » (Acte IV).

### Leçon

`overflow-x: hidden` est un piège classique du scrollytelling. La règle : si l'on veut `position: sticky` quelque part dans la page, **ne jamais** mettre `overflow: hidden` (ou auto/scroll) sur `body` ou `html`. Utiliser `overflow-x: clip`.
