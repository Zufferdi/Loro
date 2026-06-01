# Méthodologie

Ce document décrit la qualité des sources, les retraitements appliqués et
les limites de comparabilité entre les différentes périodes couvertes par
le dataset.

## 1. Périmètre

Les données concernent la **Loterie Romande** (Loro), société coopérative
gérant les jeux d'argent autorisés en Suisse romande pour les cantons de
Vaud, Fribourg, Valais, Neuchâtel, Genève et Jura.

Le dataset couvre :
- **1938—2025** pour le bénéfice annuel agrégé
- **1940—2018** pour le chiffre d'affaires (avec lacunes)
- **2013—2025** pour la ventilation par canton × type de jeu
- **2013—2025** pour la répartition par secteur bénéficiaire
- **2013—2024** pour la dépense par habitant
- **2013—2025** pour les bénéficiaires nommés (Subv_*)

## 2. Qualité des sources par période

### 1938—1980 — Sources de presse

Le bénéfice annuel et la distribution par canton ont été reconstitués à
partir d'**articles de presse romande** d'époque (60 articles cités dans la
feuille `Historique`). Pour ces décennies, **les données sont par construction
ponctuelles et incomplètes** — certaines années (1939—1949, 1951—1969, 1971—1979)
ne disposent d'aucune mesure publique vérifiable.

**Limite** : les comparaisons année par année avant 1980 sont à manier avec
précaution. Préférer la lecture des tendances longues.

### 1980—2000 — Mixte OFJ + presse

L'**Office fédéral de la justice (OFJ)** publie le chiffre d'affaires de la
Loro à partir de 1940 mais avec une couverture irrégulière. Le bénéfice est
complété par la presse romande, dont les chiffres sont eux-mêmes issus des
communiqués Loro.

### 2000—2012 — Rapports annuels

À partir de 2000, les **rapports annuels** de la Loterie Romande deviennent
la source primaire. La couverture est complète pour le bénéfice et le CA.
La ventilation par canton et par secteur n'est pas systématiquement publiée
avant 2013.

### 2013—2025 — Couverture complète

Couverture exhaustive : bénéfice, CA, ventes par canton × type de jeu,
répartition par secteur, et liste des bénéficiaires nommés au-dessus d'un
seuil de subvention.

## 3. Retraitements appliqués

### Conversion en JSON
Le script `scripts/build_data.py` :
- nettoie les valeurs hétérogènes (chaînes vs numériques)
- propage les valeurs d'opérateur (Loro / Swisslos / CFMJ) sur les lignes vides
- convertit les codes cantons (`VAUD` → `VD`, etc.)
- agrège les six feuilles `Subv_*` en un seul tableau `beneficiaires.json` avec
  une dimension `categorie`

### Sankey jeu → canton → secteur

Les liens entre **canton et secteur** ne sont **pas directement publiés** :
chaque canton dispose de son propre organe de répartition qui décide
souverainement de l'allocation par secteur. Pour le Sankey de la section §3,
nous **estimons** cette ventilation en répartissant chaque montant sectoriel
proportionnellement à la part du canton dans la Répartition totale de
l'année.

C'est une **hypothèse simplificatrice** qui ne reflète pas la réalité des
priorités cantonales. Les épaisseurs des liens canton → secteur sont donc
indicatives, pas exactes.

### Dépense par habitant

Calcul = ventes totales par canton / population résidente du canton à la fin
de l'année considérée. La population provient de la même feuille du dataset
(ligne `Vente.8` = Population). Le ratio inclut les ventes physiques et en
ligne et représente une **moyenne par habitant**, pas un comportement de
joueur réel (les non-joueurs sont inclus dans le dénominateur).

### Anatomie d'un franc

La décomposition du PBJ 2024 est calculée à partir des lignes de la feuille
`Total`. Le segment "Autres charges" (~13 % du PBJ) regroupe les éléments
non détaillés explicitement (charges administratives, amortissements,
imposition, etc.).

À noter : le **PBJ** (Produit Brut des Jeux) est défini comme
*ventes − gains versés aux joueurs*. Il ne représente donc pas le total
misé. Pour 2024, le total misé est estimé à environ 1,7 milliard CHF (le PBJ
représente ~26 % du total misé).

## 4. Limites connues

- **Loterie électronique** : la dépense par habitant pour ce sous-segment
  contient un biais — l'offre Tactilo est interdite dans certains contextes
  (voir note dans la feuille `par habitant`). Les comparaisons cantonales
  sur la Loterie électronique sont à interpréter avec prudence.

- **Sport** : la ligne "Sport" de la répartition par secteur est absente
  pour certaines années (2014, 2020, 2021, 2022). Le Fonds suisse pour
  l'encouragement du sport (FSES) reçoit néanmoins une contribution Loro
  fixe d'environ 19,5 M CHF/an, comptabilisée à part dans `metrics_annuels`.

- **Bénéficiaires nommés** : la liste des 120 organisations dans
  `beneficiaires.json` n'est pas exhaustive. Elle correspond aux
  bénéficiaires explicitement listés dans les rapports annuels — les
  petites subventions sont parfois agrégées sous "divers" sans détail.

## 5. Reproductibilité

Pour régénérer entièrement les JSON à partir du fichier source :

```bash
python scripts/build_data.py
```

Le script est déterministe : à fichier source identique, sortie identique.

Pour mettre à jour avec les données de l'année N+1, remplacer
`data/raw/Loro.xlsx` par la nouvelle version (même structure de feuilles)
et relancer le script. Le code des visualisations gère automatiquement
l'extension de la plage temporelle.
