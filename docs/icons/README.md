# Icônes PWA + favicons

Les sources sont en SVG (vectoriel), mais les manifests Apple / Android
exigent du PNG. À générer **une fois** localement par l'admin :

```bash
cd docs/icons

# Méthode 1 : rsvg-convert (le plus simple, paquet librsvg2-bin sur Ubuntu)
rsvg-convert -w 192 -h 192 icon-source.svg          -o icon-192.png
rsvg-convert -w 512 -h 512 icon-source.svg          -o icon-512.png
rsvg-convert -w 192 -h 192 icon-source-maskable.svg -o icon-192-maskable.png
rsvg-convert -w 180 -h 180 icon-source.svg          -o apple-touch-icon.png
rsvg-convert -w 32  -h 32  icon-source.svg          -o favicon-32.png
rsvg-convert -w 16  -h 16  icon-source.svg          -o favicon-16.png

# Méthode 2 : Inkscape
inkscape icon-source.svg --export-filename=icon-192.png -w 192 -h 192
# (idem pour les autres tailles)

# Méthode 3 : online (drag-drop)
# https://cloudconvert.com/svg-to-png  → upload SVG, choisir la taille, download
```

Puis pour l'image de partage social :

```bash
cd docs
rsvg-convert -w 1200 -h 630 og-image.svg -o og-image.png
```

Une fois ces fichiers PNG créés, ne pas les commit avec un nom différent —
les chemins sont déjà câblés dans `index.html` et `manifest.webmanifest`.
