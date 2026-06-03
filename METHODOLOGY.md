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

## v13.3 (juin 2026) — Vérification croisée avec BFJ + enrichissement contexte

### Source officielle

L'utilisateur a fourni le PDF officiel de l'Office fédéral de la justice (BFJ) : « LOTERIES ET PARIS PROFESSIONNELS VISANT UN BUT D'UTILITÉ PUBLIQUE OU DE BIENFAISANCE DEPUIS 1924 — Chiffres d'affaires », édition 2018. C'est la statistique fédérale de référence pour le secteur.

### Cross-check des CA existants

Vérification systématique des 36 valeurs `ca_M` LoRo déjà présentes dans `historique.json` (1940 à 2018) contre les chiffres BFJ : **correspondance exacte au franc près sur les 36 années**. Les données étaient déjà sourcées correctement (la BFJ était la source originale lors de la construction du dataset en v9).

Les 52 années sans `ca_M` (1939, 1941-1989 sauf décennies, etc.) sont des années que **la BFJ ne publie pas non plus** — avant 1991, la statistique fédérale ne donne que des points décennaux (1940, 1950, 1960, 1970, 1980, 1990). Combler ces 52 trous nécessiterait des sources secondaires (rapports annuels Loro pré-1991, archives cantonales) — pas disponibles facilement.

### Nouveautés apportées

**1. Pré-histoire (1924, 1930)** : ajout de deux entrées de contexte historique. La LoRo n'existait pas encore — ces données représentent le total des loteries d'utilité publique suisses (cantonales, paroissiales, sociétés de bienfaisance) recensées par la BFJ. 1924 : 515k CHF (juillet-décembre, premier semestre statistique). 1930 : 3,5 M CHF (×7 en 6 ans, montre le besoin de financement social qui poussera à la création de la Loterie Romande en 1937-38).

**2. Champ `ca_total_suisse_M`** : ajouté sur 34 années (1940-2018, là où la BFJ publie un total). Représente le CA cumulé de tous les opérateurs (LoRo + Swisslos + Sport-Toto-Gesellschaft jusqu'en 2006, SEVA jusqu'en 2002, Kleinlotterien). Permet de calculer la part de la LoRo dans l'économie loterie suisse :

| Année | LoRo CA | Total Suisse | Part LoRo |
|------:|--------:|-------------:|----------:|
| 1940 | 9 M | 24 M | 38 % |
| 1970 | 11 M | 224 M | 5 % |
| 1990 | 46 M | 806 M | 6 % |
| 2000 | 323 M | 1 374 M | 24 % |
| 2010 | 1 599 M | 2 723 M | 59 % |
| 2018 | 1 576 M | 2 867 M | 55 % |

Cette « part LoRo » trace un récit en U : forte présence aux débuts, dilution par Sport-Toto et SEVA jusqu'aux années 80-90, puis remontée spectaculaire après le transfert opérationnel de Sport-Toto à LoRo+Swisslos en 2007. Donnée disponible pour viz future si pertinent.

**3. `source_ca` standardisé** : 34 entrées voient leur citation `source_ca` harmonisée pour pointer la BFJ comme source officielle. La citation détaillée d'origine (presse romande pour certaines années très anciennes) est préservée en parenthèse.

### Fichier touché

- `docs/data/historique.json` : 88 → **90 entrées**, ajout de `ca_total_suisse_M` sur 34 années. Les nouvelles entrées 1924/1930 n'ont pas de `benefice_M` (pas applicable — LoRo n'existait pas) donc sont automatiquement filtrées par la viz timeline qui ne montre que les points avec bénéfice — pas d'impact visuel sur la narration actuelle, mais la donnée est disponible.

### Décision narrative ouverte

L'histoire « part LoRo dans le total suisse » serait un nouvel acte (entre Acte VII et Acte VIII Loro vs Swisslos). Pas implémenté dans cette release — les données sont là, la viz reste à arbitrer côté éditorial.

## v13.4 (juin 2026) — Élargissement des viz + nouvelle viz « Part LoRo dans l'écosystème suisse »

### Système de colonnes refondu

Les 614px effectifs des viz en `.col` étaient trop serrés sur écran 1440+. Trois bumps dans `css/style.css` :

```css
/* AVANT */
--col-max:  720px;   /* paragraphes + viz étroites → viz effective ~614px */
--col-wide: 1120px;  /* viz standards → ~1014px */
/* (pas de col-xl) */

/* APRÈS */
--col-max:  760px;   /* paragraphes (+5%, garde lisibilité ~70 caractères/ligne) */
--col-wide: 1320px;  /* viz standards → ~1214px (+20%) */
--col-xl:   1500px;  /* nouveau tier pour les viz qui réclament l'espace → ~1334px */
```

**6 viz étroites promues de `.col` à `.col-wide`** dans index.html (viz-franc, viz-prevention, viz-treemap, viz-dependency, viz-topbenefs, viz-capital). Ces viz portaient un contenu cartographique/numérique qui méritait l'espace. Les paragraphes narratifs restent en `.col` (lisibilité prime).

**5 viz promues de `.col-wide` à `.col-xl`** : viz-loro-vs-swisslos (17 lignes ligne-à-ligne), viz-editorial-timeline (14 ans verticaux), viz-explorer (BRB recherchable), viz-geomap (carte 129 villes), viz-sankey (final 3 colonnes). Ces 5 viz portent le récit dense de la dernière section.

Résultat mesurable (Playwright sur viewport 1440px) :
- viz-franc : 614 → **1214px** (×2)
- viz-treemap : 614 → **1214px**
- viz-topbenefs : 614 → **1214px**
- viz-explorer : 1014 → **1334px**

### Nouvelle viz : « Part LoRo dans le CA loterie suisse 1924-2018 »

Insertion d'un intermède narratif entre Acte VII et Acte VIII, juste avant la comparaison Loro-vs-Swisslos en valeur absolue. Le récit en U émerge clairement :

- **1940** : 38 % (LoRo dominante à ses débuts)
- **1970** : 5 % (Sport-Toto-Gesellschaft + SEVA captent l'essentiel)
- **1990** : 6 % (creux persistant)
- **2007** : transfert Sport-Toto à LoRo + Swisslos → saut brutal
- **2018** : 55 % (LoRo capte la majorité du CA loterie suisse)

**Implémentation** (nouvelle fonction `initShareSuisse()` dans `docs/js/app.js`, ~120 lignes) :
- Courbe rouge sur fond avec 4 bandes verticales colorées pour les 4 régimes historiques (avant-LoRo, domination, marginalité, reprise)
- Aire sous la courbe en rouge clair pour donner du poids
- 5 points pivots agrandis (1940, 1970, 1990, 2007, 2018)
- 4 annotations italiques aux moments-clés
- Marqueur vertical pointillé à 1938 (création LoRo)
- Légende explicative à droite
- Tooltips sur chaque point (CA LoRo + Total Suisse + part %)

**Source des données** : champ `ca_total_suisse_M` ajouté dans `historique.json` en v13.3 (PDF BFJ). Aucune nouvelle donnée ajoutée pour cette viz — elle exploite ce qui était déjà là, simplement non visualisé.

### Validation Playwright

Test sur 28 viz : **23/28 rendent en SVG** (les 5 « vides » sont en HTML pur : tables, listes, cards — ces ne sont pas des viz SVG). 0 erreur console (hors warnings `height='auto'` pré-existants). Le nouveau `viz-share-suisse` rend 1214×567px avec 34 points, 44 textes, 4 bandes de période et 4 annotations. La courbe en U est immédiatement lisible.

## v13.5 (juin 2026) — 12 améliorations de production

Tour de finition couvrant performance, accessibilité, UX mobile, polish narratif.

### Performance

**#1 Lazy-load `brb2025_full.json` (1,7 Mo)**. La donnée BRB ne se charge plus au démarrage mais lorsque l'utilisateur approche de l'Acte IX. Implémentation : `IntersectionObserver` avec `rootMargin: '800px 0px'` sur `#viz-explorer`, déclenche `ensureBrbLoaded()` qui charge le JSON, met à jour `DATA.brb2025`, puis appelle `initBrbExplorer` + `initBrbLongtail` + `initBrbGeomap`. Idempotent (cache de la promise via `DATA.brb2025_loading`). Indicateur visuel « Chargement de l'inventaire BRB 2025 (≈ 1,7 Mo)… » dans les 3 containers le temps du fetch.

**Mesure** : 0 requête BRB au chargement initial → 1 requête au scroll vers Acte IX. First Contentful Paint significativement plus rapide.

### UX

**#2 Fix des collisions de labels dans Loro vs Swisslos**. Quand une barre dépasse 65% de la demi-largeur (`INSIDE_THRESHOLD = halfW * 0.65`), l'étiquette de valeur passe **à l'intérieur** de la barre en blanc, au lieu de rester à l'extérieur où elle chevauchait l'étiquette de ligne. Appliqué symétriquement côté Loro (anchor 'end') et côté Swisslos (anchor 'start'), pour les 4 cas (2024/2025 × Loro/Swisslos).

**#6 Pagination BRB explorer**. Le cap dur à 200 lignes est remplacé par un bouton « Voir 200 de plus (X restants) ». `PAGE_SIZE = 200`, `displayCount` augmente de 200 à chaque clic, smooth-scroll vers la dernière ligne précédente pour ne pas perdre la position. Quand toutes les entrées sont affichées : message « Toutes les X entrées affichées ». CSS dédié `.brb-more-btn` avec hover et focus-visible.

**#7 Lien Jura → BRB explorer pré-filtré**. Nouveau lien CTA dans la section Acte VIII bis : « Voir les 200+ bénéficiaires jurassiens 2025 dans l'inventaire complet → ». Le href `#brb=canton:JU` est lu au démarrage de `initBrbExplorer` (`applyHashFilter()`), pré-sélectionne uniquement JU dans `state.cantons`. Sur clic, `hashchange` listener déclenche `ensureBrbLoaded()` + `scrollIntoView` vers Acte IX. Mesure : 620 entrées JU · 8,57 M CHF affichées correctement.

**#10 Mobile UX Loro vs Swisslos**. Le SVG en viewBox 1100×~960 devenait illisible compressé à 274px sur mobile (380px viewport). Solution : `@media (max-width: 760px)` impose `min-width: 900px` sur le SVG dans un container `overflow-x: auto`. Bandeau d'aide collé à gauche : « ← faites défiler horizontalement → ». Données lisibles au prix d'un scroll latéral standard pour tables larges.

**#8 viz-editorial-timeline en onglets par décennie**. La timeline éditoriale faisait 4767px de haut (14 années empilées). Refonte en 3 onglets : 2012-2015 (4), 2016-2019 (4), 2020-2025 (6, actif par défaut). Tab bar sticky à `top: 56px`, switching JS qui re-rend uniquement la décennie active. Hauteur typique par onglet : ~1500px. CSS dédié `.editorial-tabs` + `.editorial-tab` avec état actif rouge.

### Accessibilité (#9)

- **Skip-link** : `<a class="skip-link" href="#main-content">Aller directement au contenu</a>` visible au focus uniquement (top: -40px → top: 8px on :focus), permet aux utilisateurs clavier de sauter la navigation.
- **Landmark `<main id="main-content">`** : enveloppe tout le contenu narratif entre header et footer.
- **Decorateur `initA11yDecoration()`** : runs après toutes les init de viz. Pour chaque `.viz-card`, génère un `id="viz-title-N"` sur le `.viz-title`, applique `role="region"` + `aria-labelledby` sur la card, et `role="img"` + `aria-label` (depuis le titre) sur le SVG. Approche déclarative — pas besoin de toucher les 20 fonctions individuelles d'init.
- **`<nav aria-label="Actes du récit">`** sur la topnav.
- **`aria-hidden="true"`** sur `.reading-progress` (décoratif).
- **`role="alert"`** sur `#app-error`.
- **Focus styles** : `a:focus-visible, button:focus-visible, .brb-pill:focus-visible { outline: 2px solid var(--c-loro); outline-offset: 2px; }` pour ne pas laisser le navigateur stripper les indicateurs de focus.

### Polish

**#3 Footer timestamp**. Nouveau bloc `<div class="last-updated">Dernière mise à jour : <span id="build-date">—</span></div>`. La date est calculée côté client par `initBuildDate()` qui fait un `fetch HEAD` sur `data/historique.json` et extrait le header `Last-Modified`. Si indisponible (ex. en local), fallback à la date du jour. Format `fr-CH` (« 3 juin 2026 »).

**#5 Fix des 4 warnings SVG `height='auto'`**. Pattern uniformisé : `.attr('width', '100%').attr('height', H).style('height', 'auto').style(...)`. L'attribut SVG `height` ne tolère pas `'auto'` (warning console silencieux), mais la propriété CSS oui. Appliqué aux 4 occurrences restantes (lignes 897, 2370, 3753, 3883).

**#11 Print CSS**. Bloc `@media print` qui :
- Force `-webkit-print-color-adjust: exact; print-color-adjust: exact;` sur tout (préserve les fonds noirs du `.fullbleed` qui sinon sortent blanc-sur-blanc à l'impression Chrome).
- Désactive le `position: sticky` des `.scrolly .graphic` (qui ne s'imprime pas correctement).
- Masque `.reading-progress` et `.topnav`.
- Ajoute `page-break-inside: avoid` sur `.viz-card`, `.step-card`, `.fullbleed`.

**#12 Glossaire numérique**. Nouvelle section juste avant le footer, dans `.glossary-section` avec fond `--bg-soft`. Tableau de définitions `<dl class="glossary">` à 7 entrées clarifiant les chiffres qui reviennent (252 M, 258 M, 1,7 Mrd, 438 M PBJ, ~5 000 projets, 5 172 entrées BRB, 2,98 Mrd cumul). Grid 2 colonnes desktop, 1 colonne mobile, séparateurs horizontaux légers.

### Validation Playwright

Tous les tests passent :
- **Lazy load** : 0 requête `brb2025_full.json` au load initial → 1 requête après scroll vers Acte IX (1,7 Mo économisés sur le FCP).
- **Pagination** : 200 rows initiales → 400 après « Voir plus ».
- **Lien Jura** : `#brb=canton:JU` → 620 entrées, seul JU actif, scroll vers Acte IX.
- **Onglets éditorial** : 3 tabs avec compteurs (4/4/6), switching fonctionne, cards renderent.
- **Footer timestamp** : « 3 juin 2026 » affiché correctement.
- **Glossaire** : 7 entrées rendues, grid responsive.
- **A11y** : skip-link présent, `<main>` landmark, ARIA sur les .viz-card.
- **Mobile Loro vs Swisslos** : container 274px, SVG min-width 900px, overflow-x: auto opérationnel.
- **0 erreur JavaScript** dans la console (hors warnings sandbox CDN bloqués).

### Bilan v13.5

- `docs/js/app.js` : +120 lignes (initShareSuisse v13.4 + initBuildDate + initA11yDecoration + initBrbLazyTrigger + ensureBrbLoaded + applyHashFilter + pagination + editorial tabs refactor)
- `docs/css/style.css` : +200 lignes (col-xl + glossaire + a11y + brb-more-btn + cta-link + editorial-tabs + print + mobile rescue)
- `docs/index.html` : +90 lignes (skip-link + main + nav aria + intermède Part LoRo + glossaire + lien Jura + last-updated)

Pas de régression sur les viz existantes : audit final 22 viz SVG OK, 6 viz HTML pures OK (rendent du contenu non-SVG : tables, listes, cards), aucune erreur console.

## v13.6 (juin 2026) — Bug parser BRB, agrégation inter-cantons, règles cantonales 2025, élargissement des cas dépendance, refonte multi-année

### 1. Bug parser BRB 2025 — détection et correction

Audit systématique du fichier `brb2025_full.json` après vérification du cas Tremplin Martigny (signalé suspect car affiché à 10,5 M CHF pour une association locale). Vérification croisée avec le **PDF officiel BRB 2025** (`https://soutien-loro.ch/sites/default/files/2026-05/BRB2025.pdf`, page Valais — Action sociale) :

> Assoc. Tremplin, Martigny · Travaux/Aménagements · **2'500.–**

Bug confirmé. **Pattern parser identifié** : 2 entrées consécutives du PDF étaient parfois fusionnées en une seule, le `nom` portant `<nom1> <amount1>.- <nom2>` et `montant_CHF` portant le montant de la 2e entrée. Audit exhaustif via regex `^(.+?)\s+(\d{1,3}['']\d{3}\.-)\s+(.+)$` sur la champ `nom` :

- **186 entrées corrompues sur 5172** (3,6 %)
- **17,8 M CHF de montants mal-attribués** (8,4 % du total déclaré)
- Cas Tremplin Martigny : le 10,5 M était en réalité le total du « Fonds mis à disposition du Conseil d'État » du Valais (section parasite agrégée comme une entrée).

**Script de cleanup** (`scripts/clean_brb.py`) :
1. Détecte le pattern de fusion via regex
2. Split chaque entrée en 2 : la 1re récupère le montant extrait du nom, la 2e garde le `montant_CHF` actuel
3. Détecte les sections totales parasites (mots-clés « Fonds mis à disposition », « Total pour », et montant > 500'000 CHF) et les supprime
4. Backup automatique de l'original dans `brb2025_full.backup.json`

**Résultats** :
- 206 entrées splittées (+412 nouvelles entrées propres)
- 1 section totale supprimée (-10,5 M parasite)
- **Total post-cleanup : 5377 entrées, 207 M CHF** (vs 5172 entrées, 211 M CHF avant)
- **Tremplin Martigny : 10'500'000 → 2'500 CHF** ✓

### 2. Agrégation inter-cantons

Demande utilisateur : « certains cantons donnent à la même structure, comment faire pour agréger leurs sommes ? ». Implémentation d'une normalisation de nom + group-by :

```python
def normalize_name(name):
    s = name.lower()
    s = re.sub(r"^(assoc\.|fond\.|verein|sté|club|...) +", '', s)  # strip prefix
    s = re.sub(r",\s*[a-zéèôî' -]+$", '', s)                        # strip ville
    s = unicodedata.normalize('NFKD', s).encode('ASCII','ignore')   # strip accents
    return re.sub(r"[^a-z0-9]+", ' ', s).strip()
```

**Résultat** : 97 bénéficiaires uniques reçoivent de 2+ cantons, 290 entrées BRB taguées avec `agg_total_CHF`, `agg_cantons`, `agg_count`. Top multi-canton :

- **Fond. développement** (GE,VS) — 1,66 M cumulé
- **FFG Lausanne 2025** (R,VD) — 1,37 M cumulé
- **Orchestre de Chambre** (FR,GE,VD) — 1,20 M cumulé
- **Fond. EPFL Plus** (VD,VS) — 1,02 M cumulé
- **Tour de Romandie** (FR,R) — 965 k cumulé
- **Verbier Festival** (R,VS) — 925 k cumulé
- **CORODIS** (FR,R) — 738 k cumulé
- **Lanterne Magique** (JU,NE,R) — 678 k cumulé

L'UI BRB Explorer affiche désormais :
- Badge **+N↗** à côté du nom (tooltips listant les autres cantons)
- Ligne **« Cumul tous cantons : XXX CHF (N cantons) »** sous le secteur

### 3. Règles cantonales 2024 → 2025 : recherche et intégration

Refonte de la viz `initGovernance` pour afficher la **comparaison 2024 vs 2025** par canton, avec badge « ÉVOLUTION » et description courte du changement.

**Sources des règles 2024** (table de référence) :
> *REISO — La Loterie Romande, source de financement clé*, Jérémie Sanchez, janvier 2026
> [https://www.reiso.org/articles/themes/pratiques/15008](https://www.reiso.org/articles/themes/pratiques/15008)

| Canton | 2024 | 2025 | Source du changement |
|---|---|---|---|
| Vaud | 25 % | 25 % | — |
| Genève | 0 % | 0 % | — |
| Fribourg | 9 % | 9 % | **+2 % redirigés vers sport** (500 k CHF) · La Liberté 7 oct 2024 ; Frapp 9 juin 2024 |
| Valais | 0 % | 0 % | — |
| Neuchâtel | 10 % | 10 % | **Création FAC-LoRo tourisme** (1,57 M / 13 dossiers) · ne.ch communiqué mai 2026 |
| Jura | 17 % | **20 %** | Recueil officiel cantonal (FO 2025 N° 23) |

### 4. Élargissement des cas de dépendance documentés

Demande utilisateur : « j'aimerai avoir un peu plus d'associations critiques ». 5 nouveaux cas ajoutés à `dependance_cantons.json` avec **part Loro dans budget chiffrée et sourcée** :

| Asso | Loro | Budget | % Loro | Source |
|---|---|---|---|---|
| **FriSanté** (FR) | 176 k | ~550 k | **32 %** | REISO janv. 2026 |
| **Lanterne magique** (R) | 678 k | ~2,5 M | **27 %** | REISO janv. 2026 |
| **Cinéforom** (R) | 2,65 M | 10,6 M | **25 %** | Cinéforom (site officiel) + Cinando |
| Béjart Ballet Lausanne (VD) | 450 k | ~10 M | 5 % | 24 heures juin 2024 |
| Cully Jazz (VD) | ~110 k | ~2 M | 5 % | Le Temps interview Cavin 2023 |

Les 3 premiers cas montrent une **dépendance structurelle** (> 25 % du budget). Les 2 derniers illustrent au contraire un modèle où la Loro est un **complément**, et où le bénéficiaire serait fragilisé mais pas immédiatement menacé sans elle (Ville + billetterie/bars compensent).

### 5. Refonte multi-année des viz

#### `initFranc` — Décomposition du PBJ avec onglets 2023 / 2024 / 2025

Refonte complète. La viz n'utilise plus de données hardcodées 2024 mais lit dynamiquement depuis `rapports_financiers.json` (compte de résultat ligne à ligne pour les 3 années). 3 onglets `[2023] [2024] [2025]` cliquables, transitions D3 animées au changement.

**Décision méthodologique sur le scale de la barre** : la somme des composants (bénéfice + tous les coûts opérationnels) dépasse légèrement le PBJ chaque année (de 5-10 M) à cause du résultat financier positif (produits hors-jeux). Plutôt que de masquer cette réalité comptable, la barre est **échelonnée sur le total des composants**, et l'en-tête affiche les deux : « PBJ 2024 : 438,2 M · Bénéfice : 258,2 M ». Le pourcentage de chaque segment reste calculé par rapport au PBJ.

**Suppression** de l'ancien segment synthétique « FSES + FSC » qui n'apparaît pas dans le compte de résultat (ces distributions sont incluses dans `resultat_net`).

#### `initMixByCanton` — Grille 3 × 2 desktop, SVG agrandis, 2025 inclus

Refonte du layout : `grid-template-columns: repeat(3, 1fr)` forcé en classe `.mc-grid-3x2`, responsive (2 cols à 920px, 1 col à 600px). SVG passés de 280×140 à **380×200** (+36 % largeur, +43 % hauteur). Ajout d'une grille horizontale en pointillé + ticks Y en M CHF (avant : pas de ticks Y). Série étendue de 2013-2024 à **2013-2025** (`d3.range(2013, 2026)`).

### 6. Carte des cantons — dégradé visible

Les viz `initRealMap` et `initTilegram` utilisaient un dégradé `interpolateRgb('#fbfaf6', '#c8102e')` (presque-blanc → rouge Loro) avec domain `[0, maxV]`. Résultat : toutes les valeurs entre 100 et 600 CHF/habitant tombaient dans la moitié pâle de l'échelle, et les cantons paraissaient « tous dans le même rouge ».

**Remplacement** par `d3.interpolateYlOrRd` (jaune → orange → rouge soutenu) avec domain `[minV - 10%, maxV]`. Effet immédiat : sur la métrique « CHF par habitant 2025 », Fribourg (140) s'affiche en **jaune clair**, Genève (175) en **orange**, Vaud (189) en **rouge moyen**, Jura/NE/VS (194-205) en **bordeaux**. La hiérarchie visuelle est désormais évidente.

### 7. Tilegram 2025

Ajout des données 2025 à `per_capita.json`. Calcul fait à partir de `repartition_canton_jeu.json` :

```
per_capita_2025 = ventes_canton_2025 / population_canton_2025
```

Résultats 2025 (CHF / habitant) : VS 205, NE 202, JU 194, VD 189, GE 175, FR 140, Romandie 182. Le slider du tilegram va automatiquement jusqu'à 2025 (lit `max(years)` de `per_capita.tous_jeux.years`).

### 8. Identification des bénéficiaires méritant une série 2013-2025

Demande utilisateur sur la viz « L'échantillon nommé · vue d'ensemble (120 entrées sur ~5'000) ». Audit du fichier `beneficiaires.json` existant : **57 % des 120 entrées sont des sous-entités du Tour de Romandie** (commune X organise une étape de telle année). Le panel est très déséquilibré.

Création de `data/beneficiaires_candidats_2013_2025.json` : **15 structures recommandées** (pérennes, ≥ 500 k CHF en 2025, secteur utilité publique central). Listées par montant 2025 décroissant :

1. Fondation de l'Hermitage (VD) — 4,00 M
2. Fondation pour la conservation des biens culturels (GE) — 3,30 M
3. Fondation CHUV recherche médicale (VD) — 1,41 M
4. CSP Centre Social Protestant Vaud (VD) — 1,38 M
5. Fondation Arc en Scène (NE) — 1,35 M
6. Fondation Equilibre et Nuithonie (FR) — 1,10 M
7. Fondation ISREC cancer (VD) — 1,10 M
8. Fondation EPFL Plus (VD) — 1,02 M
9. Cinémathèque suisse (VD) — 830 k
10. CORODIS intercantonal danse (R+FR) — 738 k
11. FIFF Festival International Film Fribourg (FR) — 660 k
12. Fondation Plateforme 10 musées (VD) — 600 k
13. Fondation du Festival de la Cité Lausanne (VD) — 394 k
14. Fondation Pierre Gianadda (VS) — 350 k
15. Fondation Visions du Réel Nyon (VD) — 270 k

**Pour finaliser** : extraire les montants 2013-2024 des 12 BRB historiques (`ra.loro.ch/documents/BRB2013.pdf` à `BRB2024.pdf`) et fusionner dans `beneficiaires.json` — travail séparé non inclus dans cette livraison.

### 9. Sous-titres HTML mis à jour

- Section franc : « Décomposition du produit brut des jeux Loro · 2023, 2024, 2025 »
- Section gouvernance : « Les règles cantonales · 2024 → 2025 » avec mention explicite des 3 cantons ayant évolué

### Validation finale

- `node --check js/app.js` : OK
- Playwright headless sur viewport 1500×900 : 0 erreur JS
- viz-franc : 3 tabs, transitions OK, 2023/2024/2025 rendent (PBJ 420,7 / 438,2 / 429,8 M, bénéfice 243,7 / 258,2 / 252,0 M)
- viz-governance : 6 lignes comparées, 3 badges ÉVOLUTION (FR, NE, JU)
- viz-mix-canton : 6 cellules en 3×2, axe 2013-2025 effectif
- viz-tilegram : 2025 atteint au slider, palette YlOrRd visible

---

## v13.7 (juin 2026) — Cohérence narrative, transparence parser, viz inter-cantons

Trois petites passes complémentaires à v13.6, traitant les chantiers **E + F + G + D** identifiés dans la rétro post-cleanup.

### Passe 1 — Cohérence des chiffres (E)

Le cleanup parser de v13.6 a fait passer le BRB de 5'172 à **5'377 entrées** (et de 211 M à **207 M CHF**), mais quatre endroits du récit affichaient encore les anciens chiffres. Corrigés :

- `docs/index.html:956` — titre de la viz Explorer : « 5'172 bénéficiaires » → « 5'377 bénéficiaires »
- `docs/index.html:962` — footer Explorer : « 5'172 attributions » → « 5'377 attributions, 207 M CHF total »
- `docs/index.html:984` — titre Longtail : « Distribution des 5'172 » → « Distribution des 5'377 »
- `docs/index.html:1099` — glossaire : entrée « 5 172 entrées BRB 2025 » → « 5 377 entrées BRB 2025 · 207 M CHF »

### Passe 2 — Note d'écart 207 M ≠ 252 M (F)

Le BRB totalise 207 M CHF redistribués alors que le communiqué Loro 2025 annonce un bénéfice de 252 M. L'écart de ~45 M est légitime mais peut prêter à confusion — il vient du fait que le BRB ne capture pas tout. Nouvelle entrée de glossaire qui l'explique en trois points :

- **(a)** versements aux sous-fonds cantonaux (FAC, fonds sport, fonds dépendance) qui sont redistribués ensuite localement, hors BRB
- **(b)** attributions effectuées après clôture du document (versions tardives non encore publiées)
- **(c)** soutiens sportifs liés à des manifestations (Tour de Romandie, FFG, etc.) qui passent par des canaux différents du BRB

### Passe 3 — Encart « Note qualité » sur la viz Explorer (G)

Au-dessus du `#viz-explorer`, une nouvelle `.viz-quality-note` (style discret, fond `--bg-soft`, accent `--c-accent`) informe l'utilisateur du cleanup v13.6 : 186 entrées splittées + 1 section parasite de 10,5 M CHF retirée. Lien direct vers `METHODOLOGY.html#v13-6`.

### Passe 4 — Nouvelle viz « Top 20 inter-cantons » (D)

Précédemment, l'agrégation des 290 entrées inter-cantonales était cachée dans des tooltips de l'Explorer (badge `+N↗` cliquable). Cette information méritait une viz dédiée. Insertion entre `#viz-explorer` et `#viz-longtail` :

**Fonction** `initBrbMulticantons()` dans `app.js` (≈140 LOC) :

- Re-agrège les 5'377 entrées par nom normalisé (même regex que `clean_brb.py` et l'Explorer pour garantir la cohérence des clés)
- Filtre les bénéficiaires actifs dans ≥ 2 cantons (résultat : **97 entités**)
- Top 20 par cumul, rendu en bar horizontal empilé
- Chaque barre = un bénéficiaire ; largeur ∝ cumul (max = 100 %)
- Segments empilés colorés par canton, ordre canonique VD-GE-VS-FR-NE-JU-R
- Label canton inline si segment ≥ 18 % (sinon visible au survol)
- Tooltip par segment avec montant + part en % du cumul du bénéficiaire

**Wiring lazy loader** : `'viz-multicantons'` ajouté aux 3 containers existants (`viz-explorer`, `viz-longtail`, `viz-geomap`) qui partagent le même chargement de `brb2025_full.json` (1,7 Mo). Aucun fetch supplémentaire.

**Cleanup affichage** : `cleanName` strippe `Assoc.` → `Association`, `Fond.` → `Fondation`, `Sté` → `Société`, et les trailing dashes/whitespace causés par les troncatures du parser PDF (« Tour de Romandie - » → « Tour de Romandie », « Centre de Contact Suisses- » → « Centre de Contact Suisses »).

**Top 5 résultats** (post-cleanup, BRB 2025) :

| # | Bénéficiaire | Cumul | Cantons |
|---|---|---:|---|
| 01 | Fondation pour le développement [tronqué] | 1,66 M | GE (94 %) + VS (6 %) |
| 02 | Association FFG Lausanne 2025 | 1,37 M | VD (93 %) + R (7 %) |
| 03 | Orchestre de Chambre | 1,20 M | GE (42 %) + FR (36 %) + VD (22 %) |
| 04 | Fondation EPFL Plus | 1,02 M | VD (98 %) + VS (2 %) |
| 05 | Tour de Romandie | 965 k | R (99,5 %) + FR (0,5 %) |

### Validation

- `node --check docs/js/app.js` : OK
- Test isolé Playwright (`_test_multi.html`, supprimé après validation) sur le sandbox sans CDN d3 : 20 lignes rendues, 7 entrées de légende, barres correctement proportionnées de 100 % (rang 01) à 12 % (rang 20)
- 0 référence orphelin à « 5'172 » dans `docs/`
- Capture d'écran validée : noms lisibles, codes canton inline, totaux alignés à droite, légende compacte au-dessus

### Limites connues (héritées du parser BRB, hors scope v13.7)

- « Fondation pour le développement », « Association pour la sauvegarde », « Association pour la promotion » : noms tronqués par le parseur PDF (perte du `de l'innovation`, `du patrimoine bâti`, etc.). Reste à corriger dans une éventuelle Pass C (re-parseur propre).
- Secteurs parfois incorrects (Orchestre de Chambre classé en `Sport` alors que culturel) : héritage des sections du PDF parfois mal détectées.
- L'agrégation par nom normalisé reste sensible aux orthographes légèrement différentes (`Association` vs `Assoc.`) — la regex est robuste mais pas infaillible.

Reste à attaquer dans les prochaines passes : **B** (audit BRB élargi : montants nuls, doublons exacts), **A** (séries historiques 2013-2024 des 15 candidats), **C** (re-parseur propre du BRB).


---

## v13.7-audit (juin 2026) — Audit BRB élargi (Pass 3 — B)

Suite à v13.7 (cohérence narrative + viz multi-cantons), audit systématique des 5'377 entrées pour détecter les patterns d'erreur résiduels du parser. Script `scripts/audit_brb.py` qui diagnostique 11 catégories sans modification, puis `scripts/clean_brb_v13_7.py` qui applique les corrections sûres.

### Diagnostic initial

| Catégorie | Détectés | Action |
|---|---:|---|
| Entrées sans canton | 0 | — (clean) |
| Montants nuls / négatifs | 0 | — (clean) |
| Montants > 5 M CHF (rescapés de v13.6) | 0 | — (clean) |
| Noms vides / < 3 caractères | 0 | — (clean) |
| Caractères encodage cassé | 0 | — (clean) |
| **Noms tronqués** (trailing dash / préposition orpheline) | **209** | Strip artefact (cleanup [A]) |
| **Descriptions polluées** (`XX'XXX.-` du bénéficiaire suivant fusionné) | **228** | Strip post-amount (cleanup [B]) |
| **Villes contenant des descriptions** (« Matériel athlétisme » comme ville) | **16** | Nullify ville, push to description (cleanup [C]) |
| **Doublons exacts 100% identiques** (nom+ville+canton+montant+desc+organe identiques) | **13** | Dédup, garde le 1er (cleanup [D]) |
| Doublons « legit » (même montant/canton mais descriptions distinctes = attributions multiples) | 54 | **Préservés** — ce sont 2 dons distincts |
| Doublons normalisés (orthographes équivalentes : « Assoc. Lausanne Marathon » vs « Lausanne Marathon ») | 1 | Merge si ville+canton+montant+desc identiques (cleanup [E]) |
| Ville présente mais lat/lng absent | 967 | Hors scope (limites géocodage) |

### Cleanup appliqué

```
[A] 237 noms nettoyés (regex TRAILING_DASH + DANGLING_PREP, longueur post-strip > 8 chars)
[B] 228 descriptions nettoyées (regex AMOUNT_IN_DESC = `\d{1,3}['']?\d{3}\.-\s.+$`)
[C] 22 villes nullifiées (patterns : verbes d'action, années seules, mots génériques)
[D] 18 doublons 100% identiques supprimés
[E] 1 doublon normalisé fusionné

Total : 5'377 → 5'358 entrées (-19), 206,971,511 → 206,947,411 CHF (-24,100 CHF, soit 0,012%)
```

Backup automatique de l'original dans `docs/data/brb2025_full.backup_v13_7.json` avant écriture.

### Effet de bord détecté et corrigé : faux merges en agrégation multi-cantons

Le cleanup [A] (strip des prépositions orphelines) avait pour effet secondaire d'augmenter artificiellement le nombre de bénéficiaires « inter-cantonaux » détectés par la viz `#viz-multicantons` (97 → 106). En réalité, plusieurs de ces nouveaux clusters étaient des **faux positifs** où des noms tronqués différents normalisaient vers la même clé.

Exemple typique :
- `"Assoc. pour la Conservation"` (VD, 90 k CHF) — probablement « Assoc. pour la Conservation du Patrimoine [vaudois] »
- `"Fond. pour la conservation"` (GE, 3,3 M CHF) — probablement « Fond. pour la conservation [de l'art ancien] »
- Après norm : tous deux → `"pour la conservation"` → faux merge attribuant 3,39 M à une seule entité fictive

**Solution** : critère de confiance ajouté dans `initBrbMulticantons()` JavaScript :

```javascript
const STOPWORDS_FR = new Set([
  'le','la','les','l','un','une','des','du','de','d',
  'a','au','aux','et','ou','mais','donc','car','ni',
  'pour','sur','sous','avec','sans','dans','par','vers','en',...
]);
function specificTokens(normalized) {
  return normalized.split(/\s+/).filter(w => w.length >= 2 && !STOPWORDS_FR.has(w));
}
function hasAcronym(originalName) {
  return /\b[A-Z]{3,}\b/.test(originalName);
}
// Un cluster est gardé si :
//   - >= 2 tokens spécifiques dans le nom normalisé (ex. "tour" + "romandie")
//   - OU au moins un acronyme >= 3 lettres en majuscules dans un des noms originaux (ex. "CORODIS", "FFG", "EPFL")
```

**Résultat** : 106 clusters bruts → 82 retenus (haute confiance) + 24 écartés (ambigus).

| Avant filtre | Après filtre |
|---|---|
| #1 « pour la conservation » 3,39 M ❌ | #1 Association FFG Lausanne 2025 — 1,37 M ✓ |
| #2 « pour le développement » 1,66 M ❌ | #2 Orchestre de Chambre — 1,21 M ✓ |
| ... | #6 CORODIS — 738 k ✓ (préservé via acronyme) |

Les 24 clusters écartés (« pour la sauvegarde », « pour la promotion », « romande », « suisse »…) restent visibles individuellement dans la viz Explorer comme entités séparées — par prudence, on les considère comme distincts plutôt que d'agréger à tort.

### Updates HTML

- Acte IX viz-explorer titre : 5'377 → **5'358 bénéficiaires** · 207 M CHF
- Acte IX viz-longtail titre : Distribution des 5'377 → **5'358 montants**
- Acte IX viz-multicantons : « Une centaine » → **« 80 bénéficiaires »**, footer 97/106 → **82 (haute confiance)** + explication des 24 écartés
- Glossaire : entrée « 5 377 entrées BRB » → **« 5 358 entrées BRB · 207 M CHF »**
- Note qualité viz Explorer enrichie : « v13.6 (186 fusions) » → **« v13.6 + v13.7 : 186 fusions, 1 section parasite, 237 noms, 228 descriptions, 19 doublons »**

### Validation

- `node --check docs/js/app.js` : OK
- Test isolé Playwright : 20 lignes rendues, ordre changé vs v13.6 (#1 FFG Lausanne au lieu de « pour le développement »)
- Re-audit : truncated_name 209→0, desc_in_ville 16→0, parser-bug duplicates 13→0
- Doublons résiduels (59 groupes / 129 entrées) : tous avec descriptions distinctes = attributions multiples légitimes
- 0 référence orpheline à « 5'377 » dans le HTML

### Limites restantes (Pass 5 — C : refactor parser)

- 945 entrées sans lat/lng — limite de la couverture géocoding (27 % des entrées avec ville)
- Quelques noms restent ambigus après strip : "Compagnie de" (→ "Compagnie", 9 chars) — entrées probablement issues du parser PDF avec colonne tronquée
- Le critère « acronyme » peut produire de faux merges pour les acronymes très génériques (ex. "ESPAS", "EVAM") — mais ces cas n'apparaissent pas dans les top 20

Reste à attaquer : **A** (séries 2013-2024 des 15 candidats — gros morceau), **C** (re-parseur propre du BRB).


---

## v13.7-historical (juin 2026) — Séries historiques 2023-2025 (Pass 4 — A)

Suite à v13.7-audit, ajout d'une vue temporelle pour 15 bénéficiaires structurels du BRB Loterie Romande. Objectif initial : étendre `beneficiaires.json` (120 entrées dominées à 57 % par le Tour de Romandie) vers un panel équilibré culture / social / recherche / patrimoine couvrant 2013-2025. Cette passe livre une **première itération sur 3 années (2023, 2024, 2025)**, l'extension aux 9 années antérieures restant un chantier ouvert documenté ci-dessous.

### Les 15 bénéficiaires sélectionnés

Critères (cohérents avec `beneficiaires_candidats_2013_2025.json`) : structures pérennes (vs événements one-shot), apparaissant dans le BRB 2025 avec ≥ 270 k CHF cumulés, secteurs d'utilité publique centraux. Liste finale :

- **Culture / muséal** (8) : Fond. de l'Hermitage (VD), Cinémathèque suisse (VD), Fond. Plateforme 10 (VD), Fond. du Festival de la Cité (VD), Fond. Visions du Réel (VD/Nyon), Fond. Arc en Scène / TPR (NE), Fond. Pierre Gianadda (VS), Fond. Equilibre et Nuithonie (FR)
- **Festivals** (2) : Festival International du Film de Fribourg (FIFF), CORODIS (intercantonal danse)
- **Recherche médicale** (2) : Fond. CHUV (VD), Fond. ISREC cancer (VD)
- **Formation / sciences** (1) : Fond. EPFL Plus (VD)
- **Action sociale** (1) : CSP Centre Social Protestant Vaud
- **Patrimoine** (1) : Fond. pour la conservation des biens culturels (Genève)

### Données extraites

Source : PDFs officiels `https://ra.loro.ch/documents/BRB{year}.pdf` (Loterie Romande).
M�thode : `web_fetch` avec `text_content_token_limit=120000` puis parsing manuel du texte extrait du PDF, repérage des candidats par patterns de noms (« Fond. de l'Hermitage », « Fond. CHUV », etc.) et agrégation des montants attribués dans toutes les sections cantonales où ils apparaissent.

**Couverture : 36 points de données sur 45 (80 %)** :

| Bénéficiaire | 2023 | 2024 | 2025 |
|---|---:|---:|---:|
| Fond. de l'Hermitage | 400 k | 300 k | **4'000 k** |
| Fond. pour la conservation (GE) | — | — | 3'300 k |
| Fond. CHUV | 400 k | 68 k | 1'413 k |
| CSP Vaud | 250 k | — | 1'376 k |
| Fond. Arc en Scène / TPR | — | 475 k | 1'345 k |
| Fond. Equilibre et Nuithonie | 900 k | 900 k | 1'100 k |
| Fond. ISREC | — | — | 1'100 k |
| Fond. EPFL Plus | 120 k | 95 k | 1'020 k |
| Cinémathèque suisse | 300 k | 450 k | 830 k |
| CORODIS (partiel) | — | 35 k | 738 k |
| FIFF Fribourg | — | 580 k | 660 k |
| Fond. Plateforme 10 | 550 k | 600 k | 600 k |
| Fond. du Festival de la Cité | 320 k | 350 k | 394 k |
| Fond. Pierre Gianadda | — | 350 k | 350 k |
| Fond. Visions du Réel | 240 k | 245 k | 270 k |

Les cellules « — » signalent que la section cantonale correspondante n'a pas été extraite lors de cette passe — pas que l'attribution n'existe pas. Typiquement, les sections Genève, Neuchâtel et Valais arrivent en fin de PDF (après ~80 pages de Vaud + Fribourg) et sont parfois tronquées par la limite de tokens de `web_fetch`.

### Observations narratives

- **2025 est anomalement haute pour plusieurs piliers** : Hermitage × 10 (300 k → 4 M), EPFL Plus × 10 (95 k → 1 M), CSP Vaud × 5 (250 k → 1,4 M), CHUV × 20 (68 k → 1,4 M). Ces sauts probablement liés à des **financements de projets exceptionnels** (rénovation Hermitage, expansion EPFL Plus, projets immobiliers CSP) plutôt qu'à une augmentation structurelle. À documenter via les rapports d'activité des fondations.
- **Bénéficiaires stables** (variation < 20 %) : Equilibre et Nuithonie (900 k → 1,1 M), Plateforme 10 (550 → 600 → 600 k), Visions du Réel (240 → 245 → 270 k), Gianadda (350 → 350 k). Ce sont les piliers culturels avec budget récurrent.
- **CORODIS** semble exploser entre 2024 et 2025 mais c'est un artefact d'extraction : la valeur 2024 (35 k) ne couvre que la part Fribourg. CORODIS est intercantonal (organe Romand + parts cantonales) ; les valeurs complètes nécessiteraient de sommer toutes les sections.

### Implémentation technique

- **Données** : `docs/data/beneficiaires_series_2023_2025.json` (4,7 kB)
- **Visualisation** : nouveau module `docs/js/historical_series.js` (≈ 100 LOC), grille « small multiples » avec une carte par bénéficiaire, barres en échelle relative au pic local, valeurs annotées
- **HTML** : nouvelle section entre `#viz-multicantons` et `#viz-longtail` (chapter-intro + viz-card)
- **CSS** : nouvelles classes `.hist-series-grid`, `.hist-series-card`, `.hist-series-chart`, `.hist-series-bar`, etc.
- **Lazy loading** : IntersectionObserver auto-trigger (~200 px avant scroll)
- **Données manquantes** : barres rayées + texte « — » + tooltip explicatif

### Limites assumées

Cette passe est intentionnellement partielle. **Extension 2013-2022 reste un chantier ouvert** car :

1. Chaque PDF BRB consomme ~120 k tokens via `web_fetch` (texte extrait du PDF de ~100 pages)
2. Multiplier par 9 ans (2014-2022) = ~1 M tokens juste pour l'extraction, hors raisonnement et code
3. Les sections cantonales sont parfois tronquées en fin de PDF, surtout Genève
4. L'extraction étant manuelle (regex sur patterns de noms), elle ne capture pas les variations orthographiques inattendues

Suites possibles :
- **Pass 5 — C (refactor parser)** : un parseur propre du PDF permettrait l'extraction structurée par bénéficiaire × année × canton, sans dépendre de `web_fetch`
- **Ciblage** : ne traiter qu'une année benchmark (2018 ou 2015) pour avoir 4 points de données et identifier une tendance lente vs des sauts soudains
- **Compléter 2023** : refaire un fetch ciblé sur la fin du PDF BRB 2023 pour récupérer GE, NE, VS

### Updates HTML

- Nouvelle section entre `#viz-multicantons` et `#viz-longtail` : chapter-intro « 3 ans de soutien pour 15 piliers culturels et sociaux » + viz-card avec footer documentant la méthodologie et les limites
- Footer renvoie vers `ra.loro.ch/editions-precedentes.html` (source officielle) et vers cette section de `METHODOLOGY.html#v13-7-historical`
- Script `docs/js/historical_series.js` chargé après `app.js`

### Validation

- Test isolé Playwright sur `_test_hist.html` : 15 cartes rendues, tri par 2025 desc, valeurs et labels conformes au JSON
- `node --check docs/js/historical_series.js` : OK
- Pas de dépendance externe (pas de d3, pas de scrollama)


---

## v13.8 (juin 2026) — Pipeline unifié + idempotent (Pass 5 — C)

Refactor des 3 scripts de nettoyage éparpillés (`clean_brb.py` v13.6, `clean_brb_v13_7.py`, `audit_brb.py`) en un **unique pipeline ré-exécutable**, prêt pour l'arrivée du BRB 2026. Cette passe n'altère pas la narration ni les visualisations — c'est un travail d'outillage pour garantir la reproductibilité.

### Motivation

Au fil des passes v13.6 et v13.7, le nettoyage de `brb2025_full.json` s'est fait par patches successifs : un script découvrait une catégorie de bugs, on l'écrivait, on tournait, on passait à la suivante. Résultat : 3 scripts dans `scripts/`, chacun avec son propre backup, sa propre logique, son propre rapport, et **aucun n'est idempotent** (relancer v13.7 sur des données déjà nettoyées rejoue des transformations partielles). Pour BRB 2026, ce serait reconduire toute la fragilité.

L'objectif de cette passe : **un seul script, idempotent, auditable, documenté**.

### Architecture de `scripts/pipeline_brb.py`

7 stages de nettoyage, chacun étant une fonction pure `entries → (entries, report)` :

1. **`stage_split_glued`** (v13.6 A) — Détecte le pattern `nom1 1'200.- nom2` (deux entrées fusionnées par le parser), split en 2 entries propres
2. **`stage_drop_section_totals`** (v13.6 B) — Supprime les entrées qui sont des agrégats de section (« Fonds mis à disposition du Conseil d'État »…)
3. **`stage_clean_nom`** (v13.7 A) — Strip trailing dashes + prépositions pendantes (`" - "`, `" et"`, `" de la"`…)
4. **`stage_clean_desc`** (v13.7 B) — Strip embedded amounts in description (`XX'XXX.-` qui appartient à l'entrée suivante)
5. **`stage_clean_ville`** (v13.7 C) — Nullify les villes qui contiennent du texte de description (activité, manifestation, équipement…)
6. **`stage_dedup_exact`** (v13.7 D) — Supprime les doublons 100 % identiques (parser duplications)
7. **`stage_merge_normalized`** (v13.7 E) — Fusionne les variantes orthographiques (« Assoc. X » vs « X » avec même ville/canton/montant/desc)

Chacun retourne `(nouvelle_liste, dict_report)`. Le driver enchaîne, log les changements, et fait un audit pre/post.

### Audit intégré

10 catégories diagnostiques (toutes doivent être à 0 pour des données propres) + 1 catégorie informationnelle :

| Catégorie | Critère |
|---|---|
| `no_canton` | Entrées sans canton attribué |
| `zero_amount` | Montant CHF 0 ou null |
| `negative_amount` | Montant CHF négatif |
| `huge_amount_5M+` | Montant > 5 M (vérifier que ce ne sont pas des restes de bug parser) |
| `short_name` | Nom vide ou < 3 caractères |
| `truncated_name` | Trailing dash ou préposition pendante (`de`, `du`, `pour`…) |
| `desc_in_ville` | Ville contenant des mots-clés de description (activité, manifestation…) |
| `exact_duplicates_remaining` | Doublons identiques restants |
| `desc_with_embedded_amount` | Description contenant un montant inline |
| `encoding_corrupt` | Caractères mal encodés (`Ã©`, `Â`, etc.) |
| `ville_with_acronym_INFO` | **INFO seulement** — Villes contenant un acronyme entre parens (cas de scission nom/ville par le parser column-based ; ex. nom=« Assoc. pour la Musique », ville=« Improvisée de Lausanne (AMIL) ») |

La catégorie `ville_with_acronym_INFO` détecte 6 cas pré-existants où le parser v4 (column-based, pdfplumber) a éclaté un nom multi-ligne entre les colonnes nom et ville. Ces cas nécessiteraient un re-parsing du PDF pour être corrigés proprement — laissé en TODO car non bloquant pour les visualisations.

### Propriétés garanties

- **Idempotent** : relancer le pipeline sur des données déjà nettoyées produit 0 changements et 0 issues critiques d'audit
- **Safe** : backup automatique avant écriture (`brb2025_full.backup_v13.8.json`)
- **Auditable** : pre/post audit, rapport stage-par-stage avec compteurs, signature `pipeline_v13.8` dans `_meta`
- **Self-contained** : aucune dépendance externe (stdlib uniquement)
- **CLI** : `python scripts/pipeline_brb.py --help`

### Validation

Tests réalisés sur `docs/data/brb2025_full.json` :

```
RUN 1 (sur données post-v13.7) :
  clean_nom : 4 ops (4 noms avec " et" trailing créés par v13.7 et non détectés par son audit)
  Toutes autres stages : 0 ops
  Audit pre/post : toutes catégories à 0 (sauf INFO ville_with_acronym=6)

RUN 2 (sur données post-v13.8) :
  Toutes stages : 0 ops ✓
  Audit : inchangé ✓
  → Vraie idempotence confirmée
```

Les 4 noms cleanés par RUN 1 :
- `"Amis de la Musique d'Aigle et"` → `"Amis de la Musique d'Aigle"`
- `"EJMA - École de Jazz et"` → `"EJMA - École de Jazz"`
- `"Joyfully Waiting 19 & 20 et Cercle de la Librairie et"` → `"Joyfully Waiting 19 & 20 et Cercle de la Librairie"`
- `"Éditions du goudron et"` → `"Éditions du goudron"`

Ces 4 entrées avaient été créées par v13.7 elle-même (stripping d'un suffixe `du Chablais` qui laissait `" et"` orphelin, non rattrapé par l'audit v13.7 dont le pattern de détection n'incluait pas `et`). v13.8 corrige le pattern d'audit pour la cohérence cleanup ↔ audit.

### Workflow pour BRB 2026

Quand le BRB 2026 sera publié (typiquement juin 2027) :

```bash
# 1. Récupérer le PDF officiel et le parser via le parser v4 existant
#    (ce parser column-based reste utilisé — pas dans le scope de Pass 5)
python scripts/parse_pdf_v4.py --input data/raw/BRB2026.pdf \
                               --output docs/data/brb2026_full.json

# 2. Nettoyer avec le pipeline v13.8 (ou supérieur)
python scripts/pipeline_brb.py --input docs/data/brb2026_full.json

# 3. Le pipeline log les stages, fait un audit pre/post, écrit le résultat
#    avec backup automatique. Idempotent.
```

### Scripts dépréciés

Marqués comme `DEPRECATED` mais conservés dans `scripts/` pour référence historique :
- `clean_brb.py` (v13.6) — split glued + drop section totals (intégré dans pipeline_brb.py stages 1-2)
- `clean_brb_v13_7.py` — nom/desc/ville fixes + dedup (intégré dans stages 3-7)
- `audit_brb.py` — diagnostic standalone (intégré comme `audit()` dans pipeline_brb.py)

Pour tout nouveau travail, utiliser `pipeline_brb.py`.

### Limites connues — chantier Pass 6 potentiel

Le pipeline v13.8 nettoie les artefacts SORTIS du parser v4, mais ne corrige pas le parser lui-même. 6 entrées ont une ville polluée par la suite du nom (signalées par `ville_with_acronym_INFO`) — il faudrait un parser text-based qui regroupe les lignes multi-name avant attribution aux colonnes pour éliminer ces cas.

Pour BRB 2026, deux pistes :
1. **Quick win** : garder le parser v4 + pipeline v13.8 (couvre 99,9 % des cas)
2. **Refactor profond** : écrire un parser text-based (parsing du texte plat extrait via `pdfplumber.extract_text()` ou `web_fetch` + parsing de la séquence linéaire), ce qui éliminerait les bugs de colonnes

