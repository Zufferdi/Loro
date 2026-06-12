#!/usr/bin/env python3
"""
apply_sectors_from_yaml.py — applicateur unifié des règles de classification
================================================================================

Lit `scripts/sector_rules.yaml` et applique toutes les règles aux 5 BRB
(2021-2025) dans l'ordre historique v1 → v12. Produit le MÊME résultat que
`fix_sectors_run_all.py` (qui exécute les 12 scripts un par un), mais en
une seule passe, avec un YAML auditable.

Usage :
    python3 scripts/apply_sectors_from_yaml.py [--dry-run]

Le YAML doit avoir été généré au préalable via :
    python3 scripts/extract_sector_rules_to_yaml.py
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / 'docs' / 'data'
YAML_PATH = HERE / 'sector_rules.yaml'

YEARS = ['2021', '2022', '2023', '2024', '2025']

# Ordre canonique des passes (pour reproduire le comportement historique)
PASS_ORDER = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10', 'v11', 'v12']


def parse_yaml_lite(text: str) -> dict:
    """Parser YAML minimaliste pour notre format spécifique.

    Notre YAML est très restreint : top-level keys, listes de dicts avec
    exactement 2 champs (pattern, from_pass), strings simple-quoted. Pas
    besoin d'importer PyYAML (qui n'est pas dans requirements.txt).
    """
    result: dict[str, list[dict]] = {}
    current_key = None
    current_item = None
    for line in text.split('\n'):
        # Skip commentaires et lignes vides
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        # Détection : clé top-level "Quelque chose:" (sans indentation)
        m_key = re.match(r"^([A-Za-z_'][^:]*?):\s*$", line)
        if m_key and not line.startswith(' '):
            current_key = _yaml_strip_quotes(m_key.group(1))
            result[current_key] = []
            current_item = None
            continue
        # Détection : début d'item de liste "  - pattern: ..."
        m_item_start = re.match(r"^\s+-\s+pattern:\s+(.+?)\s*$", line)
        if m_item_start:
            current_item = {'pattern': _yaml_strip_quotes(m_item_start.group(1))}
            if current_key is not None:
                result[current_key].append(current_item)
            continue
        # Suite d'item : "    from_pass: vN"
        m_field = re.match(r"^\s+([a-z_]+):\s+(.+?)\s*$", line)
        if m_field and current_item is not None:
            field_name = m_field.group(1)
            field_value = _yaml_strip_quotes(m_field.group(2))
            current_item[field_name] = field_value
    # Retirer la clé _meta (informationnelle)
    result.pop('_meta', None)
    return result


def _yaml_strip_quotes(s: str) -> str:
    """Enlève les single-quotes YAML et défait l'échappement '' → '."""
    s = s.strip()
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        s = s[1:-1].replace("''", "'")
    return s


def load_rules() -> list[tuple[str, list[tuple[re.Pattern, str, str]]]]:
    """Charge les règles du YAML, groupées par passe v1..v12.

    Les règles sont triées par leur champ `order` original (= position dans le
    fichier .py source), ce qui préserve le comportement "first rule wins
    within a pass" même si le YAML les regroupe par secteur (donc dans un
    ordre différent visuellement).

    Retour : liste ordonnée [(pass_id, [(regex, sector, search_field), ...]), ...].
    """
    if not YAML_PATH.exists():
        sys.exit(f"❌ {YAML_PATH} n'existe pas. Lance d'abord extract_sector_rules_to_yaml.py")
    raw = parse_yaml_lite(YAML_PATH.read_text(encoding='utf-8'))

    by_pass: dict[str, list[tuple[int, str, str, str]]] = defaultdict(list)
    for sector, items in raw.items():
        for item in items:
            pat = item.get('pattern')
            fp = item.get('from_pass', 'v1')
            sf = item.get('search_field', 'name+description')
            order = int(item.get('order', 0))
            if pat:
                by_pass[fp].append((order, pat, sector, sf))

    out = []
    for p in PASS_ORDER:
        # Trier par order pour reproduire l'ordre original intra-passe
        sorted_rules = sorted(by_pass.get(p, []), key=lambda x: x[0])
        compiled = []
        for order, pat, sector, sf in sorted_rules:
            try:
                compiled.append((re.compile(pat, re.IGNORECASE), sector, sf))
            except re.error as exc:
                print(f"  ⚠ regex invalide ignorée ({p} → {sector}): {pat!r} ({exc})")
        if compiled:
            out.append((p, compiled))
    return out


def classify(entry: dict, rules_by_pass: list) -> tuple[str | None, str | None]:
    """Applique les règles ; reproduit le comportement original.

    Comportement historique de fix_sectors_via_keywords_v*.py :
      - Pour CHAQUE passe v1..v12, on cherche la PREMIÈRE règle qui matche
        (first match wins INSIDE the pass).
      - Le champ recherché dépend de search_field (par défaut nom+description).
      - La passe suivante recommence sur l'entrée déjà modifiée
        et l'écrasera si elle matche aussi (last pass wins ACROSS passes).
    """
    nom = entry.get('nom') or ''
    desc = entry.get('description') or ''
    text_both = nom + ' ' + desc
    final_sector = None
    final_pass = None
    for pass_id, rules in rules_by_pass:
        for cre, sector, sf in rules:
            search_text = nom if sf == 'name' else text_both
            if cre.search(search_text):
                final_sector = sector
                final_pass = pass_id
                break  # First match wins inside this pass
    return final_sector, final_pass


def main() -> None:
    parser = argparse.ArgumentParser(description='Applique les règles sector_rules.yaml aux BRB.')
    parser.add_argument('--dry-run', action='store_true',
                        help='Analyse sans écrire les fichiers')
    args = parser.parse_args()

    rules_by_pass = load_rules()
    total_rules = sum(len(r) for _, r in rules_by_pass)
    print(f'📋 {total_rules} règles chargées depuis {YAML_PATH.name}')
    print(f'   ({len(rules_by_pass)} passes : ' +
          ', '.join(f'{p}={len(r)}' for p, r in rules_by_pass) + ')')
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description='Applique les règles sector_rules.yaml aux BRB.')
    parser.add_argument('--dry-run', action='store_true',
                        help='Analyse sans écrire les fichiers')
    args = parser.parse_args()

    rules_by_pass = load_rules()
    total_rules = sum(len(r) for _, r in rules_by_pass)
    print(f'📋 {total_rules} règles chargées depuis {YAML_PATH.name}')
    print(f'   ({len(rules_by_pass)} passes : ' +
          ', '.join(f'{p}={len(r)}' for p, r in rules_by_pass) + ')')
    print()

    grand_total = 0
    for year in YEARS:
        brb_path = DATA / f'brb{year}_full.json'
        if not brb_path.exists():
            print(f'  ⚠ {brb_path.name} absent')
            continue
        with open(brb_path, encoding='utf-8') as f:
            data = json.load(f)
        entries = data.get('entries', [])

        changes = 0
        by_pass_count: dict[str, int] = defaultdict(int)
        for e in entries:
            target_sector, from_pass = classify(e, rules_by_pass)
            if target_sector and target_sector != e.get('secteur'):
                if not args.dry_run:
                    e['secteur'] = target_sector
                changes += 1
                by_pass_count[from_pass] += 1

        if not args.dry_run:
            meta = data.setdefault('_meta', {})
            meta['sector_overrides_yaml'] = {
                'count': changes,
                'by_pass': dict(by_pass_count),
                'total_rules': total_rules,
            }
            data['entries'] = entries
            with open(brb_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        verb = 'analysed' if args.dry_run else 'overrides'
        print(f'  brb{year}: {changes:4d} {verb}')
        grand_total += changes

    print()
    if args.dry_run:
        print(f'🔬 Dry-run : {grand_total} entrées seraient reclassifiées (aucune écriture).')
    else:
        print(f'✅ {grand_total} entrées reclassifiées sur les 5 BRB.')


if __name__ == '__main__':
    main()
