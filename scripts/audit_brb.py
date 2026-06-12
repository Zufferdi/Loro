"""
============================================================
DEPRECATED — superseded by scripts/pipeline_brb.py (v13.8)
Kept as historical reference. For new work:
    python scripts/pipeline_brb.py --input <path>
============================================================
"""
"""
audit_brb.py — Audit exhaustif de brb2025_full.json post-v13.6.

Détecte 11 catégories d'anomalies sans rien modifier (read-only).
"""
import json, re, unicodedata
from collections import defaultdict, Counter

with open('docs/data/brb2025_full.json', encoding='utf-8') as f:
    d = json.load(f)
entries = d['entries']
N = len(entries)
print(f"Audit de {N} entrées BRB 2025 (post-v13.6)")
print("=" * 70)

issues = defaultdict(list)

# Aides
def norm_name_strong(name):
    if not name: return ''
    s = name.lower()
    s = re.sub(r"^(assoc\.|association|fond\.|fondation|fond|sté|société|club|comité|verein|federation|féd\.)\s+", '', s)
    s = re.sub(r",\s*[a-zéèôî' -]+$", '', s)
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
    s = re.sub(r"[^a-z0-9]+", ' ', s).strip()
    return s

# === 1. Entrées sans canton ===
no_canton = [(i, e) for i, e in enumerate(entries) if not e.get('canton')]
print(f"\n[1] Entrées sans canton: {len(no_canton)}")
for i, e in no_canton[:5]:
    print(f"    #{i}: {e.get('nom', '?')[:60]} | {e.get('montant_CHF', 0)} CHF")

# === 2. Montants 0 ou null ===
zero_amt = [(i, e) for i, e in enumerate(entries) if not e.get('montant_CHF')]
print(f"\n[2] Montants nuls/zéro: {len(zero_amt)}")
for i, e in zero_amt[:5]:
    print(f"    #{i}: {e.get('nom', '?')[:60]} | canton={e.get('canton')}")

# === 3. Montants négatifs ===
neg_amt = [(i, e) for i, e in enumerate(entries) if (e.get('montant_CHF') or 0) < 0]
print(f"\n[3] Montants négatifs: {len(neg_amt)}")
for i, e in neg_amt[:5]:
    print(f"    #{i}: {e.get('nom', '?')[:60]} | {e['montant_CHF']} CHF")

# === 4. Montants suspectement gros (> 5 M) — vérifier que ce ne sont pas des restes de bug parser ===
huge_amt = [(i, e) for i, e in enumerate(entries) if (e.get('montant_CHF') or 0) > 5_000_000]
print(f"\n[4] Montants > 5 M CHF (à vérifier): {len(huge_amt)}")
for i, e in huge_amt[:10]:
    print(f"    #{i}: {e.get('nom', '?')[:50]} | {e['montant_CHF']:,} CHF | canton={e.get('canton')} | secteur={e.get('secteur')}")

# === 5. Noms vides ou très courts ===
short_name = [(i, e) for i, e in enumerate(entries) if not e.get('nom') or len(e['nom'].strip()) < 3]
print(f"\n[5] Noms vides/<3 chars: {len(short_name)}")
for i, e in short_name[:5]:
    print(f"    #{i}: nom='{e.get('nom')}' | {e.get('montant_CHF', 0)} CHF")

# === 6. Noms tronqués (trailing dash, ' de la' final, etc) ===
truncated = []
for i, e in enumerate(entries):
    n = (e.get('nom') or '').rstrip()
    # Patterns : trailing dash, prepositions orphelines, hyphen final
    if re.search(r'[-—–]$', n) or \
       re.search(r'\s(de|du|de la|de l\'|des|à|au|pour|pour la|pour le|sur|sous)$', n, re.I):
        truncated.append((i, e))
print(f"\n[6] Noms tronqués (trailing dash/préposition orpheline): {len(truncated)}")
for i, e in truncated[:8]:
    print(f"    #{i}: '{e['nom']}' | canton={e.get('canton')}")

# === 7. Doublons exacts (nom + ville + canton + montant) ===
sig = defaultdict(list)
for i, e in enumerate(entries):
    k = (e.get('nom', ''), e.get('ville', ''), e.get('canton', ''), e.get('montant_CHF', 0))
    sig[k].append(i)
exact_dups = {k: ix for k, ix in sig.items() if len(ix) > 1}
total_dup_entries = sum(len(v) for v in exact_dups.values())
print(f"\n[7] Doublons exacts (nom+ville+canton+montant): {len(exact_dups)} groupes, {total_dup_entries} entrées concernées")
for k, ix in list(exact_dups.items())[:5]:
    print(f"    {k[0][:50]} | {k[1]} | {k[2]} | {k[3]:,} CHF → indices {ix}")

# === 8. Villes suspectes (descriptions confondues avec villes) ===
# Indicateurs : ville contenant des verbes/noms communs typiques de description
desc_in_ville_patterns = [
    r'\b(activit|événement|festival|exposition|concert|spectacle|formation|achat|acquisition|aménagement|équipement|fonctionnement|soutien|projet|programme|publication|production|recherche|résidence|sortie|stage|tournée|voyage)',
    r'^\d{4}\b',  # année comme ville
    r'^(divers|matériel|équipement|fonctionnement)\b',
]
desc_in_ville = []
for i, e in enumerate(entries):
    v = e.get('ville') or ''
    if not v: continue
    for pat in desc_in_ville_patterns:
        if re.search(pat, v, re.I):
            desc_in_ville.append((i, e, pat))
            break
print(f"\n[8] Villes ressemblant à des descriptions: {len(desc_in_ville)}")
for i, e, pat in desc_in_ville[:6]:
    print(f"    #{i}: nom='{e.get('nom','')[:40]}' | ville='{e['ville'][:50]}'")

# === 9. Lat/lng absents mais ville présente ===
no_coord = [(i, e) for i, e in enumerate(entries) if e.get('ville') and (e.get('lat') is None or e.get('lng') is None)]
print(f"\n[9] Ville présente mais lat/lng absent: {len(no_coord)}")
print(f"    (Couverture géocodage actuelle: {(N - len(no_coord) - sum(1 for e in entries if not e.get('ville'))) * 100 / N:.1f}% des entrées avec ville)")

# === 10. Caractères corrompus (encodage) ===
suspicious_chars = []
for i, e in enumerate(entries):
    for k in ('nom', 'ville', 'description'):
        v = e.get(k) or ''
        # Recherche encodage cassé typique
        if re.search(r'[ÃÂ][©®¨§¢]', v) or 'â\x80\x99' in v or '\ufffd' in v:
            suspicious_chars.append((i, e, k))
            break
print(f"\n[10] Caractères encodage cassé: {len(suspicious_chars)}")
for i, e, k in suspicious_chars[:5]:
    print(f"    #{i} ({k}): {e[k][:80]}")

# === 11. Doublons normalisés (même nom normalisé, même ville, même montant ; canton diff peut être légitime) ===
sig_norm = defaultdict(list)
for i, e in enumerate(entries):
    k = (norm_name_strong(e.get('nom', '')), e.get('ville', ''), e.get('montant_CHF', 0), e.get('canton', ''))
    if k[0]:
        sig_norm[k].append(i)
norm_dups = {k: ix for k, ix in sig_norm.items() if len(ix) > 1 and not k in [(e.get('nom',''), e.get('ville',''), e.get('canton',''), e.get('montant_CHF',0)) for _, e in []]}
# Filter to those that aren't already in exact dups
exact_keys = set()
for k in exact_dups:
    nk = (norm_name_strong(k[0]), k[1], k[3], k[2])
    exact_keys.add(nk)
norm_dups_extra = {k: ix for k, ix in norm_dups.items() if k not in exact_keys}
print(f"\n[11] Doublons normalisés non-exacts (mêmes canton/ville/montant, nom légèrement différent): {len(norm_dups_extra)} groupes")
for k, ix in list(norm_dups_extra.items())[:5]:
    names = [entries[i].get('nom', '') for i in ix]
    print(f"    {k[0][:40]} | {k[1]} | {k[3]} | {k[2]:,} CHF")
    for n in names: print(f"      → '{n}'")

print("\n" + "=" * 70)
print("RÉSUMÉ")
print("=" * 70)
total_clean = N
issues_summary = {
    'no_canton': len(no_canton),
    'zero_amount': len(zero_amt),
    'negative_amount': len(neg_amt),
    'huge_amount (>5M)': len(huge_amt),
    'short_name': len(short_name),
    'truncated_name': len(truncated),
    'exact_duplicates_groups': len(exact_dups),
    'exact_duplicates_entries': total_dup_entries,
    'desc_in_ville': len(desc_in_ville),
    'no_coord_with_ville': len(no_coord),
    'encoding_issues': len(suspicious_chars),
    'normalized_duplicates_groups': len(norm_dups_extra),
}
for k, v in issues_summary.items():
    print(f"  {k:40s} {v:>5}")

# Save report
out = {
    'audit_date': '2026-06-03',
    'audit_version': 'v13.7-audit',
    'total_entries': N,
    'issues': issues_summary,
    'samples': {
        'no_canton': [{'i': i, 'nom': e.get('nom'), 'montant': e.get('montant_CHF')} for i, e in no_canton[:20]],
        'zero_amount': [{'i': i, 'nom': e.get('nom'), 'canton': e.get('canton')} for i, e in zero_amt[:20]],
        'huge_amount': [{'i': i, 'nom': e.get('nom'), 'montant': e['montant_CHF'], 'canton': e.get('canton'), 'secteur': e.get('secteur')} for i, e in huge_amt],
        'truncated_name': [{'i': i, 'nom': e['nom'], 'canton': e.get('canton')} for i, e in truncated[:30]],
        'exact_duplicates': [
            {'key': f"{k[0]} | {k[1]} | {k[2]} | {k[3]:,}", 'indices': ix}
            for k, ix in list(exact_dups.items())[:20]
        ],
        'desc_in_ville': [{'i': i, 'nom': e.get('nom'), 'ville': e['ville']} for i, e, _ in desc_in_ville[:20]],
        'encoding_issues': [{'i': i, 'field': k, 'value': e[k]} for i, e, k in suspicious_chars[:10]],
    }
}
with open('audit_report.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"\n✓ Rapport sauvegardé: audit_report.json")
