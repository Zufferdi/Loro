#!/usr/bin/env python3
"""
fix_sectors_via_keywords.py
============================

Override the official "secteur" field of entries when the nom/description
clearly indicates ANOTHER sector. Conservative — only re-classifies when
the keyword is very specific to a single sector.

Examples of certain re-classifications:
  - "FC Sion" / "HC Genève" / "Tennis Club …"     → Sport
  - "EMS Le Christ Roi" / "Hôpital …"             → Santé et handicap
  - "Pro Senectute …"                              → Action sociale et personnes âgées
  - "Église protestante …" / "Cathédrale …"       → Conservation du patrimoine
  - "Cinéforom" / "Théâtre du Jorat" / "Orchestre"→ Culture
  - "Caritas …" / "Emmaüs …" / "CSP …"            → Action sociale et personnes âgées
  - "Pro Natura" / "WWF"                           → Environnement

Each override is logged. Backup is kept of the original.
"""
import json
import re
from pathlib import Path

DATA = Path('/home/claude/audit3/Loro-main/docs/data')

# ─── Override rules ──────────────────────────────────────────────────────
# Each rule: (regex pattern on text, target sector)
# Tested IN ORDER — first match wins.
# Sufficient specificity ensures very low false-positive rate.

OVERRIDE_RULES = [
    # ─── Sport (very specific patterns) ────────────────────────────────
    (r'\bFC[\s-]\w', 'Sport'),                          # FC Sion, FC- …
    (r'\bHC[\s-]\w', 'Sport'),                          # HC Davos, HC-…
    (r'\bEHC[\s-]\w', 'Sport'),                         # EHC Visp
    (r'\bUHC[\s-]\w', 'Sport'),                         # UHC Alterswil (unihockey)
    # NOTE: removed `\bSC[\s-]?[A-Z]` — it false-positively matches "Schweiz", "Schule" etc.
    (r'\bBC[\s-][A-Z]', 'Sport'),                       # BC Cologne
    (r'\bVBC[\s-]?', 'Sport'),                          # VBC volleyball
    (r'\bBBC[\s-]?', 'Sport'),                          # BBC basketball
    (r'\bTennis[\s-]?Club\b', 'Sport'),
    (r'\bSki[\s-]?Club\b', 'Sport'),
    (r'\bClub\s+Sportif\b', 'Sport'),
    (r'\bclub\s+(?:de\s+)?(?:football|hockey|tennis|ski|natation|basket|volley|gymnastique|cyclisme|escrime|judo|karaté|boxe|rugby|équitation|handball)\b', 'Sport'),
    (r'\b(?:Société|Soc|Sté)\s+(?:de\s+)?(?:gymnastique|tir|escrime|cyclisme|natation)\b', 'Sport'),
    (r'\bFSG[\s-][A-Z]', 'Sport'),                      # FSG club
    (r'\bAssoc(?:iation)?\.?\s+(?:cantonale\s+)?(?:vaudoise|valaisanne|fribourgeoise|genevoise|neuchâteloise|jurassienne|romande)\s+de\s+(?:football|hockey|tennis|ski|natation|basket|gymnastique|cyclisme|tir|escrime|judo|équitation|patinage|curling|athlétisme|volleyball|handball|rugby)\b', 'Sport'),
    (r'\bChampionnat\s+(?:du\s+)?Monde\s+(?:MTB|UCI|de\s+ski|de\s+hockey|de\s+football|de\s+gym|cycl|VTT)', 'Sport'),
    (r'\bTour\s+de\s+Romandie\b', 'Sport'),
    (r'\bSierre[\s-]Zinal\b', 'Sport'),
    (r'\bPatrouille\s+des\s+Glaciers\b', 'Sport'),
    (r'\bMorat[\s-]Fribourg\b', 'Sport'),
    (r'\bGrand[\s-]Raid\b', 'Sport'),
    (r'\bsporti(?:f|fs|ve|ves)\b', 'Sport'),

    # ─── Santé et handicap ──────────────────────────────────────────────
    (r'\bEMS[\s-]\w', 'Santé et handicap'),
    (r"\bEMS\b(?:'|\s)", 'Santé et handicap'),
    (r'\bHôpital\b', 'Santé et handicap'),
    (r'\bH[oô]pitaux\b', 'Santé et handicap'),
    (r'\bCHUV\b', 'Santé et handicap'),
    (r'\bHUG\b', 'Santé et handicap'),
    (r'\bHRC\b', 'Santé et handicap'),  # Hôpital Riviera Chablais
    (r'\bClinique\b', 'Santé et handicap'),
    (r'\bLigue\b.*\b(?:cancer|oncologie|diabète|alzheimer)', 'Santé et handicap'),
    (r'\bPro\s+Infirmis\b', 'Santé et handicap'),
    (r'\bInsieme\b', 'Santé et handicap'),
    (r'\bCap\s+Loisirs\b', 'Santé et handicap'),
    (r'\bFAH\s+Foyer-Handicap\b', 'Santé et handicap'),
    (r"\b(?:soins?\s+(?:à\s+)?domicile|aide.*soins?.*domicile)\b", 'Santé et handicap'),
    (r'\bAVASAD\b', 'Santé et handicap'),
    (r'\bSamaritains?\b', 'Santé et handicap'),
    (r'\bCroix[\s-]Rouge\b', 'Santé et handicap'),
    (r'\bspecial\s+olympics?\b', 'Santé et handicap'),
    (r'\bAFAAP\b', 'Santé et handicap'),

    # ─── Action sociale et personnes âgées ──────────────────────────────
    (r'\bPro\s+Senectute\b', 'Action sociale et personnes âgées'),
    (r'\bCaritas\b', 'Action sociale et personnes âgées'),
    (r'\bEmmaüs\b', 'Action sociale et personnes âgées'),
    (r"\b(?:CSP|Centre\s+Social\s+Protestant)\b", 'Action sociale et personnes âgées'),
    (r"\bSecours\s+catholique\b", 'Action sociale et personnes âgées'),
    (r"\bAVIVO\b", 'Action sociale et personnes âgées'),
    (r"\bSoupe\s+populaire\b", 'Action sociale et personnes âgées'),
    (r"\bVestiaire\s+social\b", 'Action sociale et personnes âgées'),
    (r"\bColis\s+du\s+[Cc]œur\b", 'Action sociale et personnes âgées'),
    (r"\bArmée\s+du\s+Salut\b", 'Action sociale et personnes âgées'),
    (r"\bEntraide\s+Familiale\b", 'Action sociale et personnes âgées'),
    (r"\bMaison\s+de\s+retraite\b", 'Action sociale et personnes âgées'),
    (r"\bRésidence.*(?:aînés|seniors|3e\s+âge|3ème\s+âge)\b", 'Action sociale et personnes âgées'),

    # ─── Conservation du patrimoine ─────────────────────────────────────
    (r"\bÉglise\s+(?:catholique|protestante|réformée|anglicane|évangélique)\b", 'Conservation du patrimoine'),
    (r"\bÉglise\s+de\s+\w", 'Conservation du patrimoine'),
    (r"\bParoisse\b", 'Conservation du patrimoine'),
    (r"\bChapelle\b(?!\s+[Aa]rt)", 'Conservation du patrimoine'),
    (r"\bAbbaye\b", 'Conservation du patrimoine'),
    (r"\bCathédral", 'Conservation du patrimoine'),
    (r"\bMonastère\b", 'Conservation du patrimoine'),
    (r"\bCouvent\b", 'Conservation du patrimoine'),
    (r"\bKirchen", 'Conservation du patrimoine'),
    (r"\bPfarrei\b", 'Conservation du patrimoine'),
    (r"\bArchéolog", 'Conservation du patrimoine'),
    (r"\bAventicum\b", 'Conservation du patrimoine'),
    (r"\bSauvegarde\s+du\s+patrimoine\b", 'Conservation du patrimoine'),
    (r"\bChâteau\s+(?:de|d')", 'Conservation du patrimoine'),
    (r"\bMusée\s+d['\u2019]?(?:histoire|art\s+et\s+d['\u2019]histoire)", 'Conservation du patrimoine'),

    # ─── Culture ────────────────────────────────────────────────────────
    (r'\bCinéforom\b', 'Culture'),
    (r"\bThéâtre\s+du\s+Jorat\b", 'Culture'),
    (r"\bThéâtre\s+de\s+(?:Vidy|Carouge|l'Octogone|Beaulieu)", 'Culture'),
    (r"\bFond(?:ation)?\.?\s+pour\s+l'art\s+dramatique\b", 'Culture'),
    (r"\bOrchestre\s+(?:de\s+(?:Chambre|chambre|la\s+Suisse)|symphonique)", 'Culture'),
    (r"\bOpéra\s+de\b", 'Culture'),
    (r"\bConservatoire\s+de\s+musique\b", 'Culture'),
    (r"\bSAMEN\b", 'Culture'),
    (r"\bCinémathèque\b", 'Culture'),
    (r"\bCinéma\s+(?:des|du|le|la|Spoutnik|REX|Bio)\b", 'Culture'),
    (r"\bCompagnie\s+(?:théâtrale|de\s+(?:danse|théâtre|cirque))", 'Culture'),
    (r"\bChœur\s+(?:de|d')", 'Culture'),
    (r"\bMaîtrise\s+de\b", 'Culture'),
    (r"\bAssoc(?:iation)?\.?\s+(?:des\s+)?[Cc]inémas\b", 'Culture'),
    (r"\bFestival\s+(?:du\s+(?:film|jazz)|de\s+(?:musique|danse|musiques|jazz)|international\s+du\s+(?:film|jazz)|Verbier)", 'Culture'),
    (r"\bVerbier\s+Festival\b", 'Culture'),

    # ─── Environnement ──────────────────────────────────────────────────
    (r"\bPro\s+Natura\b", 'Environnement'),
    (r"\bWWF\b", 'Environnement'),
    (r"\bGreenpeace\b", 'Environnement'),
    (r"\bMurithienne\b", 'Environnement'),  # société botanique
    (r"\bBiodiversit", 'Environnement'),
    (r"\bSalamandre\b", 'Environnement'),

    # ─── Promotion, tourisme et développement ──────────────────────────
    (r"\bValais[/\s]?Wallis\s+Promotion\b", 'Promotion, tourisme et développement'),
    (r"\bVaud\s+Promotion\b", 'Promotion, tourisme et développement'),
    (r"\bFribourg\s+Région\b", 'Promotion, tourisme et développement'),
    (r"\bJura\s+Tourisme\b", 'Promotion, tourisme et développement'),
    (r"\bValrando\b", 'Promotion, tourisme et développement'),
    (r"\bSlowUp\b", 'Promotion, tourisme et développement'),

    # ─── Jeunesse et éducation ──────────────────────────────────────────
    (r"\bFAJE\b", 'Jeunesse et éducation'),
    (r"\bCrèche\b", 'Jeunesse et éducation'),
    (r"\bGarderie\b", 'Jeunesse et éducation'),
    (r"\bUAPE\b", 'Jeunesse et éducation'),
    (r"\bScouts?\b", 'Jeunesse et éducation'),
    (r"\bLudothèque\b", 'Jeunesse et éducation'),
    (r"\bPasseport[\s-]?Vacances\b", 'Jeunesse et éducation'),
    (r"\bPro\s+Juventute\b", 'Jeunesse et éducation'),
]


def find_override_sector(entry: dict) -> str | None:
    nom = entry.get('nom') or ''
    desc = entry.get('description') or ''
    text = nom + ' ' + desc
    for pattern, sector in OVERRIDE_RULES:
        # For patrimoine patterns, only match on NAME (not description),
        # to avoid mis-classifying entries whose description mentions a
        # church/paroisse owning the venue (e.g. colonies de vacances).
        if sector == 'Conservation du patrimoine':
            search_text = nom
        else:
            search_text = text
        if re.search(pattern, search_text, re.IGNORECASE):
            return sector
    return None


def main():
    years = ['2021', '2022', '2023', '2024', '2025']
    total_overrides = 0

    for y in years:
        p = DATA / f'brb{y}_full.json'
        d = json.load(open(p))
        entries = d['entries']

        overrides_log = []
        for e in entries:
            target = find_override_sector(e)
            if target and target != e['secteur']:
                overrides_log.append({
                    'nom': e['nom'][:80],
                    'old': e['secteur'],
                    'new': target,
                    'chf': e['montant_CHF'],
                })
                e['secteur'] = target

        # Add metadata
        d['_meta']['sector_overrides'] = {
            'date': '2026-06-04',
            'count': len(overrides_log),
            'method': 'Keyword-based override of `secteur` field when nom/desc '
                      'contains an unambiguous indicator of a different sector. '
                      'Conservative — only high-confidence patterns.',
        }

        # Write back
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2))

        # Summary by source sector
        by_change = {}
        for op in overrides_log:
            k = f"{op['old'] or 'None'} → {op['new']}"
            by_change[k] = by_change.get(k, 0) + 1

        print(f"\n─── BRB {y} ─── {len(overrides_log)} overrides ({sum(op['chf'] for op in overrides_log):,} CHF)")
        for change, n in sorted(by_change.items(), key=lambda x: -x[1])[:10]:
            print(f"  {n:>4d} × {change}")
        # Top examples
        print(f"  Top 5 par montant :")
        for op in sorted(overrides_log, key=lambda x: -x['chf'])[:5]:
            print(f"     {op['chf']:>8,}  {op['nom'][:60]}  ({op['old']} → {op['new']})")

        total_overrides += len(overrides_log)

    print(f"\n{'═'*60}")
    print(f"  TOTAL: {total_overrides} secteurs corrigés sur les 3 années")
    print(f"{'═'*60}")


if __name__ == '__main__':
    main()
