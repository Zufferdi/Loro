#!/usr/bin/env python3
"""
fix_sectors_run_all.py — Orchestrateur des 12 passes de correction de secteurs.
================================================================================

** DEPRECATED : préférer apply_sectors_from_yaml.py désormais **

Ce script lance les 12 scripts fix_sectors_via_keywords_v*.py individuellement.
Maintenant qu'on a `scripts/sector_rules.yaml` (consolidation de toutes les
règles), l'approche recommandée est :

    python3 scripts/apply_sectors_from_yaml.py

qui produit le MÊME résultat en lisant un seul YAML auditable. Le YAML rend les
358 règles consultables ligne par ligne, et permet d'ajouter/supprimer/modifier
sans toucher au code Python.

Pour reproduire l'historique des 12 passes individuelles (par exemple pour
debug), ce script reste utilisable.

Usage :
    python3 scripts/fix_sectors_run_all.py
    # → recommandé : python3 scripts/apply_sectors_from_yaml.py
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Ordre canonique (v1 = fix_sectors_via_keywords.py sans suffixe)
PASSES = [
    'fix_sectors_via_keywords.py',         # v1
    'fix_sectors_via_keywords_v2.py',
    'fix_sectors_via_keywords_v3.py',
    'fix_sectors_via_keywords_v4.py',
    'fix_sectors_via_keywords_v5.py',
    'fix_sectors_via_keywords_v6.py',
    'fix_sectors_via_keywords_v7.py',
    'fix_sectors_via_keywords_v8.py',
    'fix_sectors_via_keywords_v9.py',
    'fix_sectors_via_keywords_v10.py',
    'fix_sectors_via_keywords_v11.py',
    'fix_sectors_via_keywords_v12.py',
]


def main():
    print("ℹ️  Note : ce script est conservé pour compatibilité historique.")
    print("   Pour les nouvelles utilisations, préférer :")
    print("       python3 scripts/apply_sectors_from_yaml.py")
    print("   (consultable dans scripts/sector_rules.yaml — 358 règles regroupées par secteur)")
    print()

    total_passes = len(PASSES)
    ok = 0
    failed = []
    for i, script in enumerate(PASSES, 1):
        path = HERE / script
        if not path.exists():
            print(f"  [{i:2d}/{total_passes}] ⚠️  Skip (manquant) : {script}")
            continue
        print(f"  [{i:2d}/{total_passes}] ▶ {script}")
        try:
            result = subprocess.run(
                [sys.executable, str(path)],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode != 0:
                print(f"      ✗ Code retour {result.returncode}")
                if result.stderr:
                    print(f"      stderr: {result.stderr[:200]}")
                failed.append(script)
            else:
                last = result.stdout.strip().split('\n')[-1] if result.stdout.strip() else ''
                if last:
                    print(f"      ✓ {last}")
                else:
                    print(f"      ✓")
                ok += 1
        except subprocess.TimeoutExpired:
            print(f"      ✗ Timeout (> 5 min)")
            failed.append(script)

    print()
    print(f"Résumé : {ok}/{total_passes} passes OK")
    if failed:
        print(f"Échecs : {', '.join(failed)}")
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
