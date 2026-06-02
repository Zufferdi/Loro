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
