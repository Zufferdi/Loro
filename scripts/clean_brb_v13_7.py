"""
============================================================
DEPRECATED — superseded by scripts/pipeline_brb.py (v13.8)
Kept as historical reference. For new work:
    python scripts/pipeline_brb.py --input <path>
============================================================
"""
"""
clean_brb_v13_7.py — Cleanup additionnel post-v13.6.

Cibles (issues du rapport audit_report.json) :
  [A] 209 noms tronqués     → strip trailing dashes, hyphens, dangling prepositions
  [B] 228 descriptions polluées → strip leftover XX'XXX.- and following text
  [C] 16 villes-descriptions → nullify ville
  [D] 13 doublons 100% identiques → dédup (keep first)
  [E] 1 doublon normalisé Lausanne Marathon → merger
  [F] 54 doublons "legit" → intacts (descriptions distinctes = 2 attributions séparées)

Backup automatique de l'original avant modification.
Idempotent : si lancé deux fois, les opérations [A]-[C] ne changent rien la 2e fois.
"""
from __future__ import annotations
import json, re, sys, shutil
from collections import defaultdict
from pathlib import Path

INPUT = Path('docs/data/brb2025_full.json')
BACKUP = Path('docs/data/brb2025_full.backup_v13_7.json')

if not INPUT.exists():
    sys.exit(f"❌ {INPUT} introuvable")

# Backup
if not BACKUP.exists():
    shutil.copy(INPUT, BACKUP)
    print(f"✓ Backup créé : {BACKUP}")
else:
    print(f"  Backup déjà présent : {BACKUP}")

with open(INPUT) as f: data = json.load(f)
entries = data['entries']
N0 = len(entries)
print(f"\nInput : {N0} entrées")

# === [A] Strip trailing artifacts in 'nom' ===
# Trailing dash with optional whitespace, OR dangling preposition at end
TRAILING_DASH = re.compile(r'\s*[-—–]+\s*$')
DANGLING_PREP = re.compile(r"\s+(de|du|de la|de l'|des|à|au|aux|pour|pour la|pour le|sur|sous|chez|avec|et|par|en)\s*$", re.IGNORECASE)

nom_changes = 0
for e in entries:
    n = e.get('nom') or ''
    n_orig = n
    n = TRAILING_DASH.sub('', n).rstrip()
    # Strip dangling preposition (but only if name is still > 8 chars after — avoid destroying short names)
    new_n = DANGLING_PREP.sub('', n)
    if len(new_n) > 8:
        n = new_n.rstrip()
    if n != n_orig:
        e['nom'] = n
        nom_changes += 1
print(f"[A] {nom_changes} noms nettoyés (trailing dashes / dangling prepositions)")

# === [B] Strip embedded amount in description ===
# Pattern: `... XX'XXX.- next_text` → keep only the part BEFORE the embedded amount
AMOUNT_IN_DESC = re.compile(r"\s*\d{1,3}['']?\d{3}\.-\s.+$")
desc_changes = 0
for e in entries:
    d = e.get('description') or ''
    if not d: continue
    new_d = AMOUNT_IN_DESC.sub('', d).rstrip()
    if new_d != d:
        e['description'] = new_d if new_d else None
        desc_changes += 1
print(f"[B] {desc_changes} descriptions nettoyées (montant suivant strippé)")

# === [C] Nullify ville-descriptions ===
desc_in_ville_patterns = [
    r'\b(activit|événement|festival|exposition|concert|spectacle|formation|achat|acquisition|aménagement|équipement|fonctionnement|soutien|projet|programme|publication|production|recherche|résidence|sortie|stage|tournée|voyage|matériel|tournoi|championnat|circuit)',
    r'^\d{4}\b',
    r'^(divers|matériel|équipement|fonctionnement)\b',
]
patterns = [re.compile(p, re.IGNORECASE) for p in desc_in_ville_patterns]

ville_changes = 0
for e in entries:
    v = e.get('ville') or ''
    if not v: continue
    if any(p.search(v) for p in patterns):
        # Move ville content to description if description is empty
        if not e.get('description'):
            e['description'] = v
        e['ville'] = None
        ville_changes += 1
print(f"[C] {ville_changes} villes nullifiées (étaient des descriptions)")

# === [D] Deduplicate 100%-identical entries ===
# Group by all 9 substantive fields ; keep first occurrence
seen = {}
to_remove = set()
KEY_FIELDS = ('nom', 'ville', 'description', 'montant_CHF', 'canton', 'secteur', 'organe', 'sous_section')
for i, e in enumerate(entries):
    k = tuple(e.get(f) for f in KEY_FIELDS)
    if k in seen:
        to_remove.add(i)
    else:
        seen[k] = i

print(f"[D] {len(to_remove)} doublons 100% identiques supprimés")

# === [E] Merge normalized duplicates that survived ===
# Run AFTER deduplication of identicals. For Lausanne Marathon-like case:
# Same normalized name + canton + ville + amount + description but different nom strings → merge to first
import unicodedata
def norm(name):
    if not name: return ''
    s = name.lower()
    s = re.sub(r"^(assoc\.|association|fond\.|fondation|fond|sté|société|club|comité|verein|federation|féd\.)\s+", '', s)
    s = re.sub(r",\s*[a-zéèôî' -]+$", '', s)
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
    s = re.sub(r"[^a-z0-9]+", ' ', s).strip()
    return s

remaining = [(i, e) for i, e in enumerate(entries) if i not in to_remove]
sig_norm = defaultdict(list)
for i, e in remaining:
    k = (norm(e.get('nom', '')), e.get('ville') or '', e.get('canton', ''), e.get('montant_CHF', 0), e.get('description') or '')
    if k[0]: sig_norm[k].append(i)

merged_normalized = 0
for k, ix in sig_norm.items():
    if len(ix) > 1:
        # All but first → mark for removal
        for i in ix[1:]:
            to_remove.add(i)
            merged_normalized += 1
print(f"[E] {merged_normalized} doublons normalisés (orthographes équivalentes) fusionnés")

# === Apply removals ===
cleaned = [e for i, e in enumerate(entries) if i not in to_remove]
print(f"\nAprès cleanup : {len(cleaned)} entrées (vs {N0} avant — Δ = -{N0 - len(cleaned)})")

# Total CHF
total_old = sum(e.get('montant_CHF', 0) for e in entries)
total_new = sum(e.get('montant_CHF', 0) for e in cleaned)
print(f"Total CHF : {total_old:,} → {total_new:,} (Δ = -{total_old - total_new:,})")

# === Update _meta ===
meta = data.get('_meta', {})
meta['cleanup_v13_7'] = {
    'date': '2026-06-03',
    'nom_trailing_stripped': nom_changes,
    'desc_amount_stripped': desc_changes,
    'ville_nullified': ville_changes,
    'exact_duplicates_removed': len(to_remove) - merged_normalized,
    'normalized_duplicates_merged': merged_normalized,
    'entries_before': N0,
    'entries_after': len(cleaned),
    'total_chf_before': total_old,
    'total_chf_after': total_new,
    'note': 'Audit post-v13.6 ; strip trailing artifacts, embedded amounts in descriptions, nullify desc-villes, dedup identicals & merge normalized variants. 54 « legit » duplicates (same amount, distinct descriptions) preserved.',
}
data['_meta'] = meta
data['entries'] = cleaned

# Write
with open(INPUT, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"\n✓ Écrit : {INPUT}")
