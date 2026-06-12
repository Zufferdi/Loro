#!/usr/bin/env python3
"""
extract_sector_rules_to_yaml.py
================================================================================

Extrait les 232 règles regex des 12 fichiers `fix_sectors_via_keywords_v*.py`
et les consolide en un seul YAML structuré et auditable.

Le YAML conserve l'ORDRE d'application original (v1 → v12 — chaque passe
écrase la précédente sur les mêmes entrées) via le champ `order`. Il regroupe
les règles par secteur cible (Culture, Sport, Santé, etc.) pour audit facile.

Usage :
    python3 scripts/extract_sector_rules_to_yaml.py
    # → écrit scripts/sector_rules.yaml
"""
from __future__ import annotations
import ast
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Ordre canonique des 12 passes
SCRIPTS = [
    ('v1', 'fix_sectors_via_keywords.py', 'OVERRIDE_RULES'),
    ('v2', 'fix_sectors_via_keywords_v2.py', 'OVERRIDE_RULES_V2'),
    ('v3', 'fix_sectors_via_keywords_v3.py', 'OVERRIDE_RULES_V3'),
    ('v4', 'fix_sectors_via_keywords_v4.py', 'OVERRIDE_RULES_V4'),
    ('v5', 'fix_sectors_via_keywords_v5.py', 'RULES'),
    ('v6', 'fix_sectors_via_keywords_v6.py', 'RULES'),
    ('v7', 'fix_sectors_via_keywords_v7.py', 'RULES'),
    ('v8', 'fix_sectors_via_keywords_v8.py', 'RULES'),
    ('v9', 'fix_sectors_via_keywords_v9.py', 'RULES'),
    ('v10', 'fix_sectors_via_keywords_v10.py', 'RULES'),
    ('v11', 'fix_sectors_via_keywords_v11.py', 'RULES'),
    ('v12', 'fix_sectors_via_keywords_v12.py', 'RULES'),
]


def extract_rules_from_file(path: Path, var_name: str) -> list[tuple[str, str]]:
    """Extrait la liste [(pattern, secteur), ...] depuis un fichier Python.

    Utilise ast.parse pour trouver la déclaration `var_name = [...]`, puis
    évalue chaque tuple via ast.literal_eval. Robuste aux chaînes raw r"..."
    et aux concaténations implicites (r"..." r"...").
    """
    source = path.read_text(encoding='utf-8')
    tree = ast.parse(source)
    rules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        for elt in node.value.elts:
                            if not isinstance(elt, ast.Tuple) or len(elt.elts) != 2:
                                continue
                            # 1er = regex (peut être Constant ou BinOp pour les concaténations)
                            pattern_node, sector_node = elt.elts
                            pattern = _eval_string_node(pattern_node)
                            sector = _eval_string_node(sector_node)
                            if pattern is not None and sector is not None:
                                rules.append((pattern, sector))
    return rules


def _eval_string_node(node: ast.AST) -> str | None:
    """Évalue un node AST en chaîne (gère Constant simple et concaténations BinOp(+))."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        # f-strings (rares ici)
        return ''.join(
            v.value if isinstance(v, ast.Constant) else ''
            for v in node.values
        )
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _eval_string_node(node.left)
        right = _eval_string_node(node.right)
        if left is not None and right is not None:
            return left + right
    return None


def write_yaml(grouped: dict, output_path: Path) -> None:
    """Écrit un YAML lisible sans dépendre de PyYAML (qu'on n'a pas forcément).

    Format choisi : par secteur, liste de règles avec champs `pattern`, `from_pass`.
    """
    lines = []
    lines.append('# ============================================================')
    lines.append('# sector_rules.yaml — règles regex de classification de secteur')
    lines.append('# ============================================================')
    lines.append('#')
    lines.append('# Consolidation des 232 règles des 12 fichiers fix_sectors_via_keywords_v*.py.')
    lines.append("# L'ordre d'application reste v1 → v12 (chaque passe écrase la précédente).")
    lines.append('# Pour appliquer : python3 scripts/apply_sectors_from_yaml.py')
    lines.append('#')
    lines.append('# Format :')
    lines.append('#   <secteur cible> :')
    lines.append('#     - pattern: <regex>   # appliqué case-insensitive sur nom + description')
    lines.append('#       from_pass: v<N>    # passe d\'origine (préserve l\'ordre historique)')
    lines.append('# ============================================================')
    lines.append('')
    lines.append(f'_meta:')
    lines.append(f'  total_rules: {sum(len(r) for r in grouped.values())}')
    lines.append(f'  sectors: {len(grouped)}')
    lines.append(f"  generated_by: extract_sector_rules_to_yaml.py")
    lines.append(f"  source: 12 fichiers fix_sectors_via_keywords_v*.py")
    lines.append('')

    # Trier les secteurs par fréquence décroissante pour lisibilité
    by_freq = sorted(grouped.items(), key=lambda kv: -len(kv[1]))
    for sector, rules in by_freq:
        lines.append(f'{_yaml_key(sector)}:')
        # Trier les règles intra-secteur par (passe, ordre original) pour stabilité
        rules_sorted = sorted(rules, key=lambda r: (r[1], r[3]) if len(r) >= 4 else (r[1], 0))
        for item in rules_sorted:
            if len(item) == 2:
                pattern, from_pass = item
                search_field = 'name+description'
                order = 0
            elif len(item) == 3:
                pattern, from_pass, search_field = item
                order = 0
            else:
                pattern, from_pass, search_field, order = item
            esc = _yaml_string(pattern)
            lines.append(f'  - pattern: {esc}')
            lines.append(f'    from_pass: {from_pass}')
            lines.append(f'    order: {order}')
            # On n'inclut search_field que s'il diffère du défaut, pour garder
            # le YAML lisible (la majorité des règles utilisent name+description)
            if search_field != 'name+description':
                lines.append(f'    search_field: {search_field}')
        lines.append('')

    output_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def _yaml_key(s: str) -> str:
    """Une clé YAML qui contient des accents/spaces doit être quotée."""
    if re.search(r"[^A-Za-z0-9_-]", s):
        return _yaml_string(s)
    return s


def _yaml_string(s: str) -> str:
    """Format YAML string : préfère bloc | si multiline ou si trop de caractères spéciaux."""
    # Pour les regex on préfère single-quoted (pas d'interprétation de backslash)
    # En YAML simple-quoted, seule la simple-quote doit être doublée (' → '')
    escaped = s.replace("'", "''")
    return f"'{escaped}'"


def main() -> None:
    grouped: dict[str, list[tuple[str, str, str, int]]] = defaultdict(list)
    total = 0
    for version, fname, var_name in SCRIPTS:
        path = HERE / fname
        if not path.exists():
            print(f'  ⚠ {fname} absent — skip')
            continue
        try:
            rules = extract_rules_from_file(path, var_name)
        except Exception as exc:
            print(f'  ✗ {fname}: extraction échouée : {exc}')
            continue
        for order_in_pass, (pattern, sector) in enumerate(rules):
            # Cas particulier v1 : "Conservation du patrimoine" se matche uniquement
            # sur le nom (pas la description) pour éviter les faux positifs.
            if version == 'v1' and sector == 'Conservation du patrimoine':
                search_field = 'name'
            else:
                search_field = 'name+description'
            grouped[sector].append((pattern, version, search_field, order_in_pass))
        total += len(rules)
        print(f'  ✓ {version:3s} ({fname}): {len(rules):3d} règles extraites')

    output_path = HERE / 'sector_rules.yaml'
    write_yaml(grouped, output_path)

    print()
    print(f'✓ {output_path.relative_to(HERE.parent)} écrit')
    print(f'  - {total} règles consolidées')
    print(f'  - {len(grouped)} secteurs cibles distincts')
    for sec in sorted(grouped.keys(), key=lambda s: -len(grouped[s])):
        print(f'    {len(grouped[sec]):4d} → {sec}')


if __name__ == '__main__':
    main()
