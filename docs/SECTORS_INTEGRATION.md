# Sectors viz — intégration HTML

Le module `docs/js/sectors.js` rend automatiquement n'importe quel `<div>` ayant
l'attribut `data-sector="<slug>"`. Aucun JS supplémentaire à écrire, il suffit
de placer le `<div>` là où tu veux la viz dans `index.html`.

## Les 6 slugs disponibles

| Slug            | Secteur officiel                       | 2025 — entrées / CHF      |
|-----------------|----------------------------------------|---------------------------|
| `environnement` | Environnement                          | 167 / 7,7 M               |
| `sante`         | Santé et handicap                      | 124 / 8,7 M               |
| `jeunesse`      | Jeunesse et éducation                  | 238 / 10,3 M              |
| `patrimoine`    | Conservation du patrimoine             | 50 / 3,1 M                |
| `formation`     | Formation et recherche                 | 76 / 7,8 M                |
| `promotion`     | Promotion, tourisme et développement   | 44 / 4,4 M                |

## Snippet minimal

Placer où tu veux dans `index.html` (typiquement après les sections existantes
sport/culture/social) :

```html
<section class="viz-section">
  <h2 class="viz-title">Et côté <em>environnement</em> ?</h2>
  <div id="viz-environnement" data-sector="environnement"></div>
</section>

<section class="viz-section">
  <h2 class="viz-title">Et côté <em>santé & handicap</em> ?</h2>
  <div id="viz-sante" data-sector="sante"></div>
</section>

<!-- jeunesse, patrimoine, formation, promotion : même pattern -->
```

L'ID `#viz-{slug}` est conventionnel mais pas obligatoire — c'est
l'attribut `data-sector` qui pilote la viz.

## Fonctionnalités

- ✅ Lazy-load via IntersectionObserver (200px de marge)
- ✅ Toggle 2024 / 2025 en haut à droite
- ✅ Deltas inter-années (vert ↑, rouge ↓, orange "nouveau")
- ✅ Click sur une sous-catégorie pour voir tous les bénéficiaires + recherche texte
- ✅ Pastilles cantons par sous-catégorie
- ✅ Catégorie "Autres" automatique pour les entrées non matchées

## CSS

Le module réutilise les classes `sports-*` existantes (variante `culture`
violet/mauve). Aucune nouvelle règle CSS à ajouter.

## Pour ajouter des patterns

Si tu vois que des bénéficiaires importants sont mal catégorisés (rangés
dans "Autres"), édite `scripts/build_sectors_classification.py`, ajoute des
mots-clés dans la liste appropriée, puis :

```bash
python3 scripts/build_sectors_classification.py
```

→ les 12 JSON sont régénérés (6 secteurs × 2 années).
