#!/usr/bin/env bash
# ============================================================
# compute_sri.sh — calcule les hashes SHA-384 SRI pour les
# bibliothèques CDN utilisées par le projet.
# ============================================================
# Pourquoi : protéger contre une compromission de jsdelivr/unpkg
# (supply-chain attack). Si le fichier servi ne match plus le hash,
# le navigateur refuse de l'exécuter.
#
# Usage :
#   bash scripts/compute_sri.sh
#
# Le script affiche les lignes à copier dans docs/index.html
# (remplacer les '' dans le 3ᵉ argument de _loadLibFallback).
# Pour explorer.html : copier la valeur dans integrity="..."
#
# Dépendances : curl, openssl (présents sur tout Linux/macOS).
# ============================================================
set -euo pipefail

# Liste des URLs CDN — doit rester aligné avec docs/index.html.
URLS=(
  "https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js"
  "https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js"
  "https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js"
  "https://unpkg.com/scrollama@3.2.0/build/scrollama.min.js"
)

echo "Calcul des hashes SHA-384 SRI…"
echo ""

for url in "${URLS[@]}"; do
  hash=$(curl --silent --fail --location "$url" \
    | openssl dgst -sha384 -binary \
    | openssl base64 -A)
  if [ -z "$hash" ]; then
    echo "  ✗ Échec : $url"
    continue
  fi
  echo "  $url"
  echo "    integrity: 'sha384-${hash}'"
  echo ""
done

cat << 'EOF'
─────────────────────────────────────────────────────────────
Comment utiliser ces hashes :

1. Ouvre docs/index.html, trouve le bloc _loadLibFallback (vers
   la fin du fichier). Remplace les '' du 3ᵉ argument par le
   hash correspondant, p.ex. :
       window._loadLibFallback(
         'https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js',
         'https://unpkg.com/d3@7.8.5/dist/d3.min.js',
         'sha384-XXXX...'
       );

2. Ouvre docs/explorer.html, dans la balise <script src=…d3.min.js>
   ajoute   integrity="sha384-XXXX..."  à côté de crossorigin.

3. Re-test la page dans un navigateur : la console doit être propre.
   Une erreur "Failed to find a valid digest..." signifie que le hash
   ne match pas — le fichier a changé sur le CDN (ou la version du
   loader a un typo).

─────────────────────────────────────────────────────────────
EOF
