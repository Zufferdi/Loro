#!/usr/bin/env python3
"""
retro_classify_2021.py — classification rétrospective des entrées 2021 sans secteur
================================================================================

Le BRB 2021 contient ~595 entrées dont le secteur n'a pas été déterminé par les
12 passes de fix_sectors_via_keywords (ni par la classification initiale du
parser). Ce script utilise deux signaux pour les classifier :

1. LOOKUP CANONIQUE : si la même organisation apparaît dans 2022-2025 avec un
   secteur, on le copie sur l'entrée 2021 (même clé canonique normalisée).
   C'est l'approche la plus fiable — pas de risque d'erreur de catégorisation
   si une org porte le même nom une année sur l'autre.

2. CLASSIFIER TF-IDF + k-NN : pour les entrées résiduelles (orgs uniques à 2021),
   on entraîne un modèle simple sur la base nom+description → secteur des
   2022-2025 entries classifiées, puis on prédit avec un seuil de confiance.
   Sans sklearn (dépendance pas garantie dans le pipeline) : implémentation TF
   manuelle + cosine sim.

Usage :
    python3 scripts/retro_classify_2021.py [--dry-run] [--threshold 0.25]

Marque les entrées modifiées avec _meta.classification_method ∈ {
    'lookup_canonical',    # signal le plus fiable
    'knn_majority',        # vote majoritaire des k voisins, au-dessus du seuil
    'fallback_default',    # rien n'a marché, on met Culture (catégorie majoritaire 2021)
}
"""
from __future__ import annotations
import argparse
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'docs' / 'data'

# ----------------------------------------------------------------------
# Normalisation (alignée sur build_search_index.py)
# ----------------------------------------------------------------------

def normalize_name(name: str) -> str:
    if not name:
        return ''
    s = name.lower()
    s = re.sub(
        r"^(assoc\.|association|fond\.|fondation|fond|sté|société|club|comité|"
        r"verein|federation|féd\.|coopérative|coop\.|institut|inst\.|centre|"
        r"groupe|gpe\.|service)\s+",
        '', s,
    )
    s = re.sub(r",\s*[a-zéèôî' -]+$", '', s)
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
    s = re.sub(r"[^a-z0-9]+", ' ', s).strip()
    return s


def tokenize(text: str) -> list[str]:
    """Tokenisation pour TF-IDF — minuscules, désaccentuation, alphanum."""
    if not text:
        return []
    s = unicodedata.normalize('NFKD', text.lower()).encode('ASCII', 'ignore').decode('ASCII')
    return [t for t in re.split(r'[^a-z0-9]+', s) if len(t) >= 2 and t not in STOPWORDS]


STOPWORDS = {
    'de', 'la', 'le', 'les', 'des', 'du', 'et', 'pour', 'aux', 'au', 'en',
    'a', 'd', 'l', 'sur', 'par', 'son', 'ses', 'avec', 'sans', 'dans', 'que',
    'qui', 'sa', 'ce', 'cet', 'cette', 'ces', 'leur', 'leurs', 'nos', 'votre',
    'un', 'une', 'pres', 'sous', 'vers', 'chez', 'apres', 'avant', 'depuis',
    'ou', 'mais', 'donc', 'or', 'ni', 'car', 'si',
}


# ----------------------------------------------------------------------
# Phase 1 — Lookup canonique
# ----------------------------------------------------------------------

def build_canonical_index(years: list[str]) -> dict[str, str]:
    """Pour chaque clé canonique (nom normalisé), retourne le secteur
    le plus fréquent observé dans les BRB des années données.

    Skip les entries 'n/a' ou sans secteur (qui ne servent pas).
    """
    by_key_sector_counts: dict[str, Counter] = defaultdict(Counter)
    for year in years:
        brb = DATA / f'brb{year}_full.json'
        if not brb.exists():
            continue
        with open(brb, encoding='utf-8') as f:
            d = json.load(f)
        for e in d.get('entries', []):
            secteur = e.get('secteur')
            if not secteur or secteur in ('n/a', '', None):
                continue
            key = normalize_name(e.get('nom') or '')
            if key:
                by_key_sector_counts[key][secteur] += 1
    # Pour chaque clé, sortir le secteur le plus fréquent
    return {k: c.most_common(1)[0][0] for k, c in by_key_sector_counts.items()}


# ----------------------------------------------------------------------
# Phase 2 — Classifier TF-IDF + k-NN
# ----------------------------------------------------------------------

def build_tfidf_training(years: list[str]) -> tuple[list[dict], dict[str, float]]:
    """Charge les entries 2022-2025 (classifiées) et calcule l'IDF du corpus.

    Retour :
      - docs : liste de {tokens, sector}
      - idf  : dict {token: idf_score}
    """
    docs = []
    df: Counter = Counter()  # document frequency par token
    for year in years:
        brb = DATA / f'brb{year}_full.json'
        if not brb.exists():
            continue
        with open(brb, encoding='utf-8') as f:
            d = json.load(f)
        for e in d.get('entries', []):
            secteur = e.get('secteur')
            if not secteur or secteur in ('n/a', '', None):
                continue
            text = (e.get('nom') or '') + ' ' + (e.get('description') or '')
            tokens = tokenize(text)
            if not tokens:
                continue
            docs.append({'tokens': tokens, 'sector': secteur})
            for t in set(tokens):
                df[t] += 1

    n_docs = len(docs)
    idf = {t: math.log(n_docs / (1 + count)) for t, count in df.items()}
    return docs, idf


def tfidf_vector(tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    """TF-IDF vectorisation (sparse dict)."""
    if not tokens:
        return {}
    tf = Counter(tokens)
    # Normalisation L2
    vec = {}
    for tok, freq in tf.items():
        if tok in idf:
            vec[tok] = freq * idf[tok]
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {k: v / norm for k, v in vec.items()}


def cosine_sim(v1: dict[str, float], v2: dict[str, float]) -> float:
    """Cosine similarity de deux vecteurs sparse (déjà L2-normalisés)."""
    if not v1 or not v2:
        return 0.0
    # On itère sur le plus petit
    if len(v1) > len(v2):
        v1, v2 = v2, v1
    return sum(v1[t] * v2.get(t, 0) for t in v1)


def predict_knn(query_vec: dict[str, float], train_vecs: list[tuple[dict, str]],
                k: int = 5, threshold: float = 0.25) -> tuple[str | None, float]:
    """k-NN cosine. Retourne (secteur_prédit, confiance) ou (None, max_sim)
    si la similarité maxi est sous le seuil.
    """
    if not query_vec:
        return None, 0.0
    sims = []
    for vec, sector in train_vecs:
        s = cosine_sim(query_vec, vec)
        if s > 0:
            sims.append((s, sector))
    sims.sort(reverse=True)
    top_k = sims[:k]
    if not top_k or top_k[0][0] < threshold:
        return None, top_k[0][0] if top_k else 0.0

    # Vote majoritaire pondéré par similarité
    weighted: Counter = Counter()
    for s, sec in top_k:
        weighted[sec] += s
    best_sector, best_score = weighted.most_common(1)[0]
    # Confiance = ratio du gagnant sur la somme
    total = sum(weighted.values())
    confidence = best_score / total if total > 0 else 0.0
    return best_sector, confidence


# ----------------------------------------------------------------------
# Main pipeline
# ----------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description='Classifie rétrospectivement les entrées 2021 sans secteur.')
    parser.add_argument('--dry-run', action='store_true', help='Analyse sans écrire')
    parser.add_argument('--threshold', type=float, default=0.25,
                        help='Seuil de similarité pour le classifier k-NN (défaut 0.25)')
    parser.add_argument('--k', type=int, default=5, help='Nombre de voisins k-NN (défaut 5)')
    args = parser.parse_args()

    # Charger 2021
    brb2021 = DATA / 'brb2021_full.json'
    with open(brb2021, encoding='utf-8') as f:
        data2021 = json.load(f)
    entries = data2021.get('entries', [])
    unclass = [e for e in entries if not e.get('secteur') or e.get('secteur') in ('n/a', '', None)]
    print(f'📊 Entrées 2021 sans secteur : {len(unclass)} / {len(entries)} ({len(unclass)/len(entries)*100:.1f}%)')
    print()

    # Phase 1 : index canonique 2022-2025
    print('🔎 Phase 1 — Lookup par nom canonique (basé sur 2022-2025)…')
    canonical_idx = build_canonical_index(['2022', '2023', '2024', '2025'])
    print(f'   {len(canonical_idx)} noms canoniques uniques dans les 4 années cibles')

    n_phase1 = 0
    for e in unclass:
        key = normalize_name(e.get('nom') or '')
        if key and key in canonical_idx:
            if not args.dry_run:
                e['secteur'] = canonical_idx[key]
            e['_retro_classified'] = 'lookup_canonical'
            n_phase1 += 1
    print(f'   ✓ {n_phase1} entrées classifiées par lookup')
    print()

    # Phase 2 : kNN sur le résiduel
    residual = [e for e in unclass if '_retro_classified' not in e]
    if residual:
        print(f'🤖 Phase 2 — k-NN TF-IDF sur le résiduel ({len(residual)} entries)…')
        train_docs, idf = build_tfidf_training(['2022', '2023', '2024', '2025'])
        print(f'   Corpus d\'entraînement : {len(train_docs)} entries, {len(idf)} tokens distincts')

        # Pré-vectoriser le training set
        train_vecs = [(tfidf_vector(d['tokens'], idf), d['sector']) for d in train_docs]

        n_phase2 = 0
        n_lowconf = 0
        confidence_dist = []
        for e in residual:
            text = (e.get('nom') or '') + ' ' + (e.get('description') or '')
            tokens = tokenize(text)
            qvec = tfidf_vector(tokens, idf)
            predicted, conf = predict_knn(qvec, train_vecs, k=args.k, threshold=args.threshold)
            confidence_dist.append(conf)
            if predicted:
                if not args.dry_run:
                    e['secteur'] = predicted
                e['_retro_classified'] = 'knn_majority'
                e['_retro_confidence'] = round(conf, 3)
                n_phase2 += 1
            else:
                n_lowconf += 1
        print(f'   ✓ {n_phase2} entrées classifiées par k-NN (seuil ≥ {args.threshold})')
        print(f'   ⚠ {n_lowconf} entrées sous le seuil (gardent "n/a")')
        if confidence_dist:
            confidence_dist.sort()
            median = confidence_dist[len(confidence_dist)//2]
            print(f'   📊 Confiance médiane : {median:.3f}, max : {max(confidence_dist):.3f}')

    # Persistance
    if not args.dry_run:
        # Stats meta
        meta = data2021.setdefault('_meta', {})
        meta['retro_classify_2021'] = {
            'date': '2026-06-12',
            'lookup_canonical': n_phase1,
            'knn_majority': sum(1 for e in entries if e.get('_retro_classified') == 'knn_majority'),
            'remaining_na': sum(1 for e in entries if not e.get('secteur') or e['secteur'] in ('n/a', '')),
            'threshold': args.threshold,
            'k': args.k,
        }
        # Nettoyer les marqueurs internes des entries (on ne veut pas polluer le JSON public)
        for e in entries:
            e.pop('_retro_classified', None)
            e.pop('_retro_confidence', None)
        with open(brb2021, 'w', encoding='utf-8') as f:
            json.dump(data2021, f, ensure_ascii=False, indent=2)
        print()
        print(f'✅ brb2021_full.json mis à jour')
    else:
        print()
        print('🔬 Dry-run — aucune écriture.')

    # Stats finales
    final_unclass = [e for e in entries if not e.get('secteur') or e['secteur'] in ('n/a', '')]
    print()
    print(f'📈 Bilan final : {len(unclass)} → {len(final_unclass)} entrées sans secteur')
    print(f'   Coverage 2021 : {(1 - len(final_unclass)/len(entries))*100:.1f}% '
          f'(était {(1 - len(unclass)/len(entries))*100:.1f}%)')


if __name__ == '__main__':
    main()
