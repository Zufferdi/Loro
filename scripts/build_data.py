"""
build_data.py
=============

Transforme data/raw/Loro.xlsx en un ensemble de fichiers JSON exploitables
par les visualisations du dossier docs/.

Usage :
    python scripts/build_data.py

Sorties produites dans docs/data/ :
  - historique.json              Bénéfice + chiffre d'affaires + sources 1938-2025
  - metrics_annuels.json         KPIs annuels (commissions, marketing, direction…)
  - repartition_canton_jeu.json  Ventes par canton × type de jeu 2013-2025
  - repartition_secteur.json     Répartition par secteur bénéficiaire 2013-2025
  - per_capita.json              Dépense par habitant par canton 2013-2024
  - beneficiaires.json           Tous les bénéficiaires nommés consolidés
  - population.json              Population par canton (extraite de la ventilation)
  - summary.json                 Indicateurs résumés pour la page d'accueil
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "Loro.xlsx"
OUT = ROOT / "docs" / "data"
OUT.mkdir(parents=True, exist_ok=True)

CANTONS = ["VAUD", "FRIBOURG", "VALAIS", "NEUCHÂTEL", "GENÈVE", "JURA"]
CANTON_CODES = {
    "VAUD": "VD", "FRIBOURG": "FR", "VALAIS": "VS",
    "NEUCHÂTEL": "NE", "GENÈVE": "GE", "JURA": "JU",
}

# Annotations historiques clés — extraites des citations de presse présentes
# dans la feuille « Historique ». Chaque entrée associe une année à un titre
# court et au libellé exact de la source.
KEY_ANNOTATIONS = {
    1938: ("Première loterie", "Courrier de Genève, 30 janvier 1938"),
    1991: ("Cap des 50 M", "La Gruyère, 12 décembre 1991"),
    1999: ("Cap des 100 M", "La Tribune de Genève, 29 juillet 2000"),
    2003: ("Décollage post-libéralisation", "Le Nouvelliste, 30 juin 2004"),
    2020: ("Année COVID", "Rapport annuel Loterie Romande 2020"),
    2024: ("Record historique", "Rapport annuel Loterie Romande 2024"),
}


def _clean_num(x):
    """Convertit en float ou None les valeurs hétérogènes (NaN, str, etc.)."""
    if x is None:
        return None
    if isinstance(x, str):
        x = x.strip()
        if not x:
            return None
        try:
            return float(x.replace(" ", "").replace(",", "."))
        except ValueError:
            return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(v):
        return None
    return v


def _clean_str(x):
    if x is None:
        return None
    if isinstance(x, float) and math.isnan(x):
        return None
    s = str(x).strip()
    return s or None


def build_historique(sheets) -> list[dict]:
    df = sheets["Historique"].copy()
    df.columns = [
        "annee", "benefice_M", "ca_M", "rbj_M", "pbj_M", "source_ca",
        "rep_fr", "rep_vd", "rep_ge", "rep_ne", "rep_vs", "rep_ju",
        "_n", "note",
    ]
    df = df.iloc[1:].copy()           # première ligne = en-têtes
    df["annee"] = pd.to_numeric(df["annee"], errors="coerce")
    df = df.dropna(subset=["annee"])
    df["annee"] = df["annee"].astype(int)

    rows = []
    for _, r in df.iterrows():
        year = int(r["annee"])
        entry = {
            "annee": year,
            "benefice_M": _clean_num(r["benefice_M"]),
            "ca_M": _clean_num(r["ca_M"]),
            "rbj_M": _clean_num(r["rbj_M"]),
            "pbj_M": _clean_num(r["pbj_M"]),
            "source_ca": _clean_str(r["source_ca"]),
            "repartition": {
                "FR": _clean_num(r["rep_fr"]),
                "VD": _clean_num(r["rep_vd"]),
                "GE": _clean_num(r["rep_ge"]),
                "NE": _clean_num(r["rep_ne"]),
                "VS": _clean_num(r["rep_vs"]),
                "JU": _clean_num(r["rep_ju"]),
            },
            "note": _clean_str(r["note"]),
        }
        if year in KEY_ANNOTATIONS:
            t, src = KEY_ANNOTATIONS[year]
            entry["annotation"] = {"titre": t, "source": src}
        rows.append(entry)
    return rows


def build_metrics_annuels(sheets) -> dict:
    """Lit la feuille « Total » et la convertit en un dict {label: {annee: val}}."""
    df = sheets["Total"].copy()
    df.columns = ["operateur", "label"] + [int(c) if not isinstance(c, str) else c for c in df.columns[2:]]
    year_cols = [c for c in df.columns if isinstance(c, int)]

    # propagate operateur
    df["operateur"] = df["operateur"].ffill()

    out = {"Loro": {}, "Swisslos": {}, "CFMJ": {}, "Suisse": {}}
    for _, r in df.iterrows():
        label = _clean_str(r["label"])
        if not label:
            continue
        op = _clean_str(r["operateur"]) or "Suisse"
        op = op if op in out else "Suisse"
        series = {}
        for y in year_cols:
            v = _clean_num(r[y])
            if v is not None:
                series[str(y)] = v
        if series:
            out[op][label] = series
    return out


def build_repartition_canton_jeu(sheets) -> list[dict]:
    """Ventile les ventes par canton × type de jeu × année."""
    df = sheets["Détail"].copy()
    rows = []
    for _, r in df.iterrows():
        annee = _clean_num(r["Année"])
        poste = _clean_str(r["Poste"])
        libelle = _clean_str(r["Libellé"])
        if annee is None or poste is None:
            continue
        entry = {
            "annee": int(annee),
            "poste": poste,
            "libelle": libelle,
            "cantons": {},
            "total": _clean_num(r.get("TOTAL")),
            "intercantonal": _clean_num(r.get("Intercantonal")),
            "swisslos": _clean_num(r.get("Swisslos")),
        }
        for c in CANTONS:
            entry["cantons"][CANTON_CODES[c]] = _clean_num(r.get(c))
        # secteurs (uniquement présents pour Répartition)
        secteurs = {}
        for col in [
            "Culture", "Santé et handicap", "Jeunesse et éducation",
            "Action sociale et personnes âgées", "Sport",
            "Promotion, tourisme et développement", "Environnement",
            "Conservation du patrimoine", "Formation et recherche",
        ]:
            v = _clean_num(r.get(col))
            if v is not None:
                secteurs[col] = v
        if secteurs:
            entry["secteurs"] = secteurs
        rows.append(entry)
    return rows


def build_repartition_secteur(detail_rows) -> dict:
    """À partir des lignes Répartition de la feuille Détail, construit une
    structure {secteur: {annee: montant}}."""
    secteurs = {}
    for row in detail_rows:
        if row["poste"] != "Répartition" or "secteurs" not in row:
            continue
        for sec, val in row["secteurs"].items():
            secteurs.setdefault(sec, {})[str(row["annee"])] = val
    return secteurs


def build_per_capita(sheets) -> dict:
    """Lit la feuille « par habitant » et structure les deux tables présentes
    (toutes catégories puis Loterie électronique seule)."""
    df = sheets["par habitant"]
    rows = df.values.tolist()

    blocks = []
    cur = None
    for r in rows:
        first = r[0]
        if isinstance(first, str) and first.strip() == "Canton":
            cur = {"years": [int(v) for v in r[1:] if isinstance(v, (int, float)) and not math.isnan(v)],
                   "data": {}}
            blocks.append(cur)
            continue
        if cur and isinstance(first, str) and first.strip() in {"Vaud", "Fribourg", "Valais", "Neuchâtel", "Genève", "Jura", "Romandie"}:
            vals = []
            for v in r[1:]:
                vals.append(_clean_num(v))
            cur["data"][first.strip()] = vals

    return {
        "tous_jeux": blocks[0] if len(blocks) >= 1 else {},
        "loterie_electronique": blocks[1] if len(blocks) >= 2 else {},
    }


def build_beneficiaires(sheets) -> list[dict]:
    """Consolide toutes les feuilles Subv_* en une liste plate de bénéficiaires."""
    categories = {
        "Subv_TdR": "Sport / Tour de Romandie",
        "Subv_Cinéforom": "Culture / Cinéma (Cinéforom)",
        "Subv_EMS": "Santé / EMS",
        "Subv_musique classique": "Culture / Musique classique",
        "Subv_Festival Cinéma": "Culture / Festivals de cinéma",
        "Subv_divers": "Divers",
    }
    out = []
    seen_id = 0
    for sheet_name, cat in categories.items():
        if sheet_name not in sheets:
            continue
        df = sheets[sheet_name].copy()
        # Repère les colonnes années
        year_cols = [c for c in df.columns if isinstance(c, int)]
        for _, r in df.iterrows():
            name = _clean_str(r.get("Unnamed: 0"))
            if not name:
                continue
            canton = _clean_str(r.get("Canton"))
            sub_cat = _clean_str(r.get("Unnamed: 2"))
            series = {}
            for y in year_cols:
                v = _clean_num(r[y])
                if v is not None and v > 0:
                    series[str(y)] = v
            if not series:
                continue
            seen_id += 1
            out.append({
                "id": seen_id,
                "nom": name,
                "canton": canton,
                "categorie": cat,
                "sous_categorie": sub_cat,
                "series": series,
                "total": round(sum(series.values()), 2),
                "max_annee": max(series, key=lambda y: series[y]),
            })
    return out


def build_population(detail_rows) -> dict:
    """Extrait la population annuelle par canton depuis la ligne Vente.8."""
    out = {}
    for row in detail_rows:
        if row.get("libelle") == "Population":
            out[str(row["annee"])] = row["cantons"]
    return out


def build_summary(hist, metrics, detail_rows, benefs) -> dict:
    """Indicateurs résumés pour la page d'accueil."""
    last_year = max(r["annee"] for r in hist if r["benefice_M"] is not None)
    last_benefice = next(r["benefice_M"] for r in hist if r["annee"] == last_year)
    peak = max((r for r in hist if r["benefice_M"] is not None), key=lambda r: r["benefice_M"])

    # Croissance annuelle moyenne 1938 → dernière année
    first = next(r for r in hist if r["annee"] == 1938 and r["benefice_M"])
    n_years = last_year - 1938
    cagr = (last_benefice / first["benefice_M"]) ** (1 / n_years) - 1

    # Total redistribué dernière année connue de Détail
    last_rep_year = max(
        r["annee"] for r in detail_rows
        if r["poste"] == "Répartition" and r.get("total")
    )
    last_rep = next(
        r for r in detail_rows
        if r["poste"] == "Répartition" and r["annee"] == last_rep_year
    )

    return {
        "derniere_annee": last_year,
        "premiere_annee": 1938,
        "benefice_dernier": last_benefice,
        "benefice_premier": first["benefice_M"],
        "benefice_pic": peak["benefice_M"],
        "annee_pic": peak["annee"],
        "cagr_long_terme": cagr,
        "redistribue_dernier_M": (last_rep.get("total") or 0) / 1_000_000,
        "annee_redistribue": last_rep_year,
        "nb_beneficiaires_nommes": len(benefs),
        "nb_annees_couvertes": len(set(r["annee"] for r in hist if r["benefice_M"])),
    }


def write_json(name, data):
    path = OUT / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"  ✓ {name} ({path.stat().st_size:,} octets)")


def main():
    print(f"Lecture de {RAW}…")
    sheets = pd.read_excel(RAW, sheet_name=None)
    print(f"  {len(sheets)} feuilles trouvées : {list(sheets.keys())}")
    print()

    print("Construction des fichiers JSON :")
    hist = build_historique(sheets)
    write_json("historique.json", hist)

    metrics = build_metrics_annuels(sheets)
    write_json("metrics_annuels.json", metrics)

    detail = build_repartition_canton_jeu(sheets)
    write_json("repartition_canton_jeu.json", detail)

    secteurs = build_repartition_secteur(detail)
    write_json("repartition_secteur.json", secteurs)

    per_capita = build_per_capita(sheets)
    write_json("per_capita.json", per_capita)

    benefs = build_beneficiaires(sheets)
    write_json("beneficiaires.json", benefs)

    pop = build_population(detail)
    write_json("population.json", pop)

    summary = build_summary(hist, metrics, detail, benefs)
    write_json("summary.json", summary)

    print()
    print(f"✅ Terminé — {len(list(OUT.glob('*.json')))} fichiers dans {OUT}")


if __name__ == "__main__":
    main()
