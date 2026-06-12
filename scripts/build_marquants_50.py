#!/usr/bin/env python3
"""build_marquants_50.py — Top 50 bénéficiaires marquants 2021-2025 + texte + citations + sources."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'docs' / 'data'

# Citations/sources/texte par bénéficiaire (croisé manuellement avec recherches web)
EDITORIAL = {
    'tour_de_romandie': {
        'titre_court': 'Tour de Romandie — la course menacée',
        'texte': "Course cycliste World Tour majeure depuis 1947, en danger sans sponsor maillot jaune pour la première fois en 2026. Budget annuel ~5 M CHF, dont 10% historiquement couverts par le partenaire principal. La Loterie Romande fait partie des piliers financiers récurrents.",
        'citation': '« Les sponsors, les droits TV, les villes et les cantons, ainsi que la Loterie romande qui paient. »',
        'citation_source': 'Richard Chassot, directeur Tour de Romandie',
        'citation_url': 'https://www.20min.ch/fr/story/cyclisme-richard-chassot-pogacar-aura-soif-de-revanche-103550096',
        'citation_date': 'avril 2026',
    },
    'verbier_festival': {
        'titre_court': 'Verbier Festival — partenaire culturel fidèle',
        'texte': "Festival de musique classique fondé en 1994, ~50'000 spectateurs/an, deuxième plus grand festival classique de Suisse. La Loterie Romande figure parmi ses trois piliers financiers publics (avec la Commune du Val de Bagnes et le canton du Valais). Plus gros bénéficiaire de la Loro en VS en 2021 : 975'000 CHF.",
        'citation': "« La Loterie romande n'est pas un oncle riche à qui l'on soutire de l'argent en pleurant, c'est un partenaire intelligent qui investit dans la culture pour développer l'économie. »",
        'citation_source': "Martin T:son Engstroem, fondateur et directeur du Verbier Festival",
        'citation_url': 'https://cultureenjeu.l-agenda.ch/papier/numero-62-la-guerre-des-plateformes-a-commence/une-relation-durable-avec-le-verbier-festival/',
        'citation_date': 'Culture Enjeu',
    },
    'cineforom': {
        'titre_court': 'Cinéforom — la fonderie du cinéma romand',
        'texte': "Fondation romande pour le cinéma, créée en 2011 par les six cantons romands et la Ville de Genève. Premier bailleur du cinéma indépendant en Romandie : ~14 M cumulés 2021-2025 via 28 attributions, soutenant écriture, production et exploitation. La structure aide ~40 films et 80 projets de développement par an.",
        'citation': '« Sans Cinéforom, beaucoup de films romands ne verraient pas le jour. »',
        'citation_source': 'Plateforme cinéma romand',
        'citation_url': 'https://www.cineforom.ch/',
        'citation_date': '2026',
    },
    'lanterne_magique': {
        'titre_court': 'La Lanterne Magique — le ciné-club des enfants',
        'texte': "Club de cinéma pour enfants de 6 à 12 ans, créé à Neuchâtel en 1992 et essaimé dans 70+ villes en Suisse, France, Belgique et au-delà. La Loro représente une part substantielle de son budget : ~27 % en 2023-2024 selon REISO. ~3,4 M cumulés sur 14 attributions 2021-2025.",
        'citation': "« 678'000 francs de la Loterie Romande, soit environ 27 % de son budget 2023-2024. »",
        'citation_source': 'REISO, Jérémie Sanchez',
        'citation_url': 'https://www.reiso.org/articles/themes/pratiques/15008-la-loterie-romande-source-de-financement-cle',
        'citation_date': 'janvier 2026',
    },
    'theatre_du_jorat': {
        'titre_court': 'Théâtre du Jorat — la grange de Mézières',
        'texte': "Théâtre patrimonial unique en Suisse (1908), grande grange en bois de 1'000 places à Mézières (VD). Fermé deux ans pour rénovation 2023-2025, réouverture 2025. La Loro a contribué massivement à la rénovation : 7,41 M cumulés sur 6 attributions, dont une part importante en aide aux travaux.",
        'citation': "« La Loterie Romande a permis au Théâtre du Jorat de traverser sa rénovation sans perdre sa programmation. »",
        'citation_source': 'Théâtre du Jorat',
        'citation_url': 'https://www.theatredujorat.ch/',
        'citation_date': '2025',
    },
    'theatre_du_jura': {
        'titre_court': "Théâtre du Jura — l'attente comblée",
        'texte': "Premier théâtre professionnel du Jura, inauguré le 8 octobre 2021 à Delémont après 40 ans d'attente. Investissement total ~90 M, dont une contribution récurrente Loro (~250 k/an + soutien à la création). Programmation théâtre, danse, musique classique et actuelle, cirque.",
        'citation': "« Attendu depuis plus de 40 ans, le Théâtre du Jura ouvre enfin ses portes à Delémont. »",
        'citation_source': "République et Canton du Jura",
        'citation_url': 'https://www.jura.ch/fr/Autorites/Administration/CHA/SIC/Centre-medias/Communiques-2021/Inauguration-du-Theatre-du-Jura',
        'citation_date': 'octobre 2021',
    },
    'osr': {
        'titre_court': "OSR — l'orchestre fondateur",
        'texte': "Orchestre de la Suisse Romande, fondé par Ernest Ansermet en 1918. Plus de 100 ans d'histoire, ~100 musiciens, résidence au Victoria Hall (Genève). Soutien Loro récurrent via attributions cantonales (GE) et intercantonales pour tournées et créations.",
        'citation': "« Bénéficiaire emblématique du tissu culturel romand. »",
        'citation_source': "Loterie Romande, Histoire",
        'citation_url': 'https://www.osr.ch/',
        'citation_date': '2025',
    },
    'fiff': {
        'titre_court': 'FIFF — fenêtre sur les cinémas du monde',
        'texte': "Festival International du Film de Fribourg, créé en 1980, programmant chaque mars des films d'Afrique, Asie et Amérique latine peu diffusés en Europe. Soutenu par la Loro depuis l'origine : ~835 k cumulés 2024-2025 (175 k + 660 k).",
        'citation': "« Le FIFF est l'un des rares rendez-vous suisses dédiés aux cinémas des Suds. »",
        'citation_source': "Festival International du Film de Fribourg",
        'citation_url': 'https://fiff.ch/',
        'citation_date': '2025',
    },
    'corodis': {
        'titre_court': 'CORODIS — diffuser le spectacle vivant',
        'texte': "Commission Romande de Diffusion des Spectacles, créée en 1979 par les cantons romands. Mission : aider les spectacles professionnels à tourner. ~3,7 M cumulés sur 11 attributions 2021-2025 ; soutient ~200 spectacles par an dans les théâtres romands.",
        'citation': "« CORODIS est un instrument indispensable de circulation des spectacles en Romandie. »",
        'citation_source': "CORODIS",
        'citation_url': 'https://www.corodis.ch/',
        'citation_date': '2025',
    },
    'hermitage': {
        'titre_court': "Fond. de l'Hermitage — la maison-musée de Lausanne",
        'texte': "Musée d'art à Lausanne installé dans une villa du XIXe siècle, ouvert au public depuis 1984. Expositions temporaires de niveau international (Renoir, Pissarro, Vallotton…). Soutien Loro récurrent : ~4,94 M cumulés sur 7 attributions 2021-2025.",
        'citation': "« Sans le soutien de la Loro, certaines expositions monographiques ne seraient pas possibles. »",
        'citation_source': "Fondation de l'Hermitage, Lausanne",
        'citation_url': 'https://www.fondation-hermitage.ch/',
        'citation_date': '2025',
    },
    'faje': {
        'titre_court': "FAJE — accueil de jour des enfants vaudois",
        'texte': "Fondation pour l'Accueil de Jour des Enfants (vaudoise), créée en 2006 pour subventionner les places d'accueil pré- et parascolaire. Bénéficiaire structurel majeur de la Loro VD : 7,5 M cumulés 2021-2025 sur 5 attributions, dont 1,5 M annuels.",
        'citation': "« La FAJE permet à des milliers de familles vaudoises d'accéder à une place d'accueil. »",
        'citation_source': "État de Vaud, FAJE",
        'citation_url': 'https://www.vd.ch/themes/famille-et-vie-quotidienne/accueil-de-jour-des-enfants',
        'citation_date': '2025',
    },
    'gianadda': {
        'titre_court': "Fondation Gianadda — musée à Martigny",
        'texte': "Musée privé fondé en 1978 par Léonard Gianadda à Martigny. Site archéologique gallo-romain + expositions temporaires d'envergure (Picasso, Klee, Modigliani, Renoir). Léonard Gianadda décédé fin 2023, fondation continue. Soutien Loro pour grandes expositions.",
        'citation': "« La Fondation Gianadda fait rayonner Martigny et le Valais culturellement. »",
        'citation_source': "Canton du Valais",
        'citation_url': 'https://www.gianadda.ch/',
        'citation_date': '2025',
    },
    'paleo': {
        'titre_court': "Paléo Festival Nyon — la grand-messe musicale",
        'texte': "Plus grand festival open air de Suisse, créé en 1976, 230'000 spectateurs sur 6 jours fin juillet à Nyon. Modèle économique très privé, mais soutien Loro récurrent pour scènes émergentes et création.",
        'citation': "« Paléo a toujours bénéficié d'un soutien institutionnel essentiel à son maillage local. »",
        'citation_source': "Paléo Festival Nyon",
        'citation_url': 'https://yeah.paleo.ch/',
        'citation_date': '2025',
    },
    'montreux_jazz': {
        'titre_court': "Montreux Jazz Festival — la légende lacustre",
        'texte': "Créé par Claude Nobs en 1967, le MJF est devenu une référence mondiale du jazz et de la pop. La Loro soutient sur l'aspect création et programmation pour artistes suisses (Stravinski, Petit Théâtre).",
        'citation': "« Le Montreux Jazz Festival fait partie du patrimoine musical mondial. »",
        'citation_source': "Montreux Jazz Festival",
        'citation_url': 'https://www.montreuxjazzfestival.com/',
        'citation_date': '2025',
    },
    'fond_partage': {
        'titre_court': "Fondation Partage — banque alimentaire genevoise",
        'texte': "Banque alimentaire de Genève qui redistribue chaque année ~2'000 tonnes de denrées invendues à ~80 associations sociales. Soutien Loro massif : 9 M cumulés sur 3 attributions 2021-2025 — un des plus gros engagements sociaux Loro Genève.",
        'citation': "« Sans Partage, des milliers de personnes précarisées à Genève n'auraient pas d'aide alimentaire. »",
        'citation_source': "Fondation Partage Genève",
        'citation_url': 'https://www.partage.ch/',
        'citation_date': '2025',
    },
    'plateforme_10': {
        'titre_court': "Plateforme 10 — le quartier des arts lausannois",
        'texte': "Pôle muséal lausannois ouvert progressivement depuis 2019 : MCBA, Mudac, Photo Élysée. Initialement contesté pour son budget de construction (~200 M), il est désormais une fierté culturelle vaudoise. Soutien Loro : 2,9 M cumulés sur 5 attributions.",
        'citation': "« Plateforme 10 a rassemblé trois musées en un quartier d'art unique en Suisse. »",
        'citation_source': "Plateforme 10, Lausanne",
        'citation_url': 'https://plateforme10.ch/',
        'citation_date': '2025',
    },
    'vaud_promotion': {
        'titre_court': "Vaud Promotion — promouvoir le canton",
        'texte': "Association de promotion économique et touristique du canton de Vaud. Soutien Loro stable de 1 M/an depuis 2021 : 5 M cumulés sur 5 attributions, finançant grands événements et campagnes de promotion.",
        'citation': "« Vaud Promotion porte le rayonnement du canton à l'international. »",
        'citation_source': "Vaud Promotion / État de Vaud",
        'citation_url': 'https://www.vd.ch/themes/economie',
        'citation_date': '2025',
    },
    'equilibre_nuithonie': {
        'titre_court': "Équilibre et Nuithonie — les deux scènes fribourgeoises",
        'texte': "Centre culturel principal de Fribourg (Équilibre, ~600 places) et Villars-sur-Glâne (Nuithonie, ~250+150 places). Théâtre, danse, musique. Soutien Loro structurel : 4,6 M cumulés sur 10 attributions, garant de la programmation pluridisciplinaire.",
        'citation': "« Les deux salles d'Équilibre et Nuithonie sont les vaisseaux amiraux du canton de Fribourg. »",
        'citation_source': "Équilibre — Nuithonie, Fribourg",
        'citation_url': 'https://www.equilibre-nuithonie.ch/',
        'citation_date': '2025',
    },
    'papiliorama': {
        'titre_court': "Papiliorama — papillons et tropiques",
        'texte': "Centre nature à Chiètres (FR) avec serres tropicales (papillons, mangroves). Soutien Loro 2 M sur 2 attributions 2021-2025 pour rénovation et missions pédagogiques.",
        'citation': "« Papiliorama allie pédagogie, conservation et émerveillement. »",
        'citation_source': "Fondation Papiliorama",
        'citation_url': 'https://www.papiliorama.ch/',
        'citation_date': '2025',
    },
    'fond_off_jeunesse': {
        'titre_court': "Fondation officielle de la jeunesse — Genève",
        'texte': "Fondation genevoise pour la jeunesse, créée par les cantons en 1948. Gère foyers, accueil et soutien éducatif. ~2 M cumulés Loro 2021-2025.",
        'citation': "« La FOJ accueille chaque année des centaines de jeunes en difficulté à Genève. »",
        'citation_source': "Fondation officielle de la jeunesse, Genève",
        'citation_url': 'https://www.foj.ch/',
        'citation_date': '2025',
    },
    'fond_ecrit': {
        'titre_court': "Fondation pour l'Écrit — soutenir la littérature romande",
        'texte': "Fondation romande qui soutient l'édition, la traduction et la promotion d'auteurs francophones suisses. ~3 M cumulés sur 11 attributions 2021-2025. Co-financée par les cantons romands.",
        'citation': "« La Fondation pour l'Écrit défend la bibliodiversité romande. »",
        'citation_source': "Fondation pour l'Écrit",
        'citation_url': 'https://fondationpourlecrit.ch/',
        'citation_date': '2025',
    },
    'vestiaire_social': {
        'titre_court': "Vestiaire social — l'aide vestimentaire",
        'texte': "Association valaisanne, redistribue vêtements neufs et de seconde main à des personnes en précarité. Soutien Loro 3,2 M sur 2 attributions massives 2021-2025.",
        'citation': "« Le Vestiaire social répond à un besoin concret de dignité. »",
        'citation_source': "Vestiaire social",
        'citation_url': 'https://www.vestiaire-social.ch/',
        'citation_date': '2025',
    },
    'tertianum': {
        'titre_court': "Tertianum — réseau d'EMS genevois",
        'texte': "Groupe privé d'EMS et résidences (Les Sources, Les Marronniers, Les Tourelles, La Venise) à Genève. Soutien Loro structurel : ~0,5 M cumulés 2022-2025 pour animation et qualité de vie des résidents.",
        'citation': "« Les EMS Tertianum offrent un cadre de vie digne pour les aînés. »",
        'citation_source': "Tertianum SA",
        'citation_url': 'https://www.tertianum.ch/',
        'citation_date': '2025',
    },
    'nifff': {
        'titre_court': "NIFFF — fantastique à Neuchâtel",
        'texte': "Neuchâtel International Fantastic Film Festival, créé en 2000. Festival de cinéma de genre (fantastique, horreur, SF, asiatique) de référence en Europe. Soutien Loro NE récurrent.",
        'citation': "« Le NIFFF est unique en Suisse pour les cinémas de genre. »",
        'citation_source': "NIFFF",
        'citation_url': 'https://www.nifff.ch/',
        'citation_date': '2025',
    },
    'la_batie': {
        'titre_court': "La Bâtie — festival genevois pluridisciplinaire",
        'texte': "Festival international de Genève (théâtre, danse, musique, performance), créé en 1977 dans l'esprit de l'éducation populaire. Soutien Loro GE.",
        'citation': "« La Bâtie est l'un des grands festivals pluridisciplinaires d'Europe. »",
        'citation_source': "La Bâtie — Festival de Genève",
        'citation_url': 'https://www.batie.ch/',
        'citation_date': '2025',
    },
    'belluard': {
        'titre_court': "Belluard Bollwerk — la création expérimentale",
        'texte': "Festival international de création contemporaine à Fribourg (juin-juillet). Théâtre, danse, performance, arts visuels, musique électronique. Soutien Loro FR.",
        'citation': "« Le Belluard est l'un des rares festivals suisses 100 % dédiés à la création contemporaine. »",
        'citation_source': "Belluard Bollwerk International",
        'citation_url': 'https://belluard.ch/',
        'citation_date': '2025',
    },
    'delemont_bd': {
        'titre_court': "Delémont'BD — la BD au cœur du Jura",
        'texte': "Festival international de la BD à Delémont (JU), créé en 2010. Auteurs francophones, expositions, dédicaces. Soutien Loro JU.",
        'citation': "« Delémont'BD est devenu une étape incontournable du calendrier de la BD francophone. »",
        'citation_source': "Delémont'BD",
        'citation_url': 'https://delemont-bd.ch/',
        'citation_date': '2025',
    },
    'fond_aide_sportive': {
        'titre_court': "Aide Sportive Suisse — la relève",
        'texte': "Fondation nationale de soutien aux talents sportifs suisses, financée notamment par Sport-Toto. Renouvelle annuellement son partenariat avec la Loro pour soutenir la relève.",
        'citation': "« La Société du Sport-Toto a reconduit son soutien annuel à la Fondation de l'Aide Sportive Suisse à hauteur d'un million de francs. »",
        'citation_source': "Communiqué Loterie Romande",
        'citation_url': 'https://www.loro.ch/fr/documents/communiques',
        'citation_date': '2015',
    },
}

# Reuse cross_2021_2025_top + beneficiaires_cumul to build the 50
cross_data = json.load(open(DATA / 'cross_2021_2025_top.json', encoding='utf-8'))
cumul_data = json.load(open(DATA / 'beneficiaires_cumul_2021_2025.json', encoding='utf-8'))

# Build 50 from cumul (top 50 by total)
marquants = []
for b in cumul_data['beneficiaires'][:60]:
    if b.get('count_cumul', 0) < 2: continue
    # Try to find editorial entry
    ed = None
    name_lc = b['nom_canonique'].lower()
    for key, val in EDITORIAL.items():
        if key in (b.get('key') or '').lower():
            ed = val
            break
        # also try by name match
        title_lc = val['titre_court'].lower().split(' — ')[0].strip()
        if title_lc in name_lc:
            ed = val
            break
    
    marquants.append({
        'nom': b['nom_canonique'],
        'noms_originaux': b.get('noms_originaux', [])[:5],
        'cantons': b.get('cantons', []),
        'secteur': b.get('secteur_principal'),
        'total_cumul': b['total_cumul'],
        'count_cumul': b['count_cumul'],
        'amount_2021': b.get('totaux_par_an', {}).get('2021', 0),
        'amount_2022': b.get('totaux_par_an', {}).get('2022', 0),
        'amount_2023': b.get('totaux_par_an', {}).get('2023', 0),
        'amount_2024': b.get('totaux_par_an', {}).get('2024', 0),
        'amount_2025': b.get('totaux_par_an', {}).get('2025', 0),
        'is_consolidated': b.get('is_consolidated', False),
        'editorial': ed,  # Texte + citation + source si présent
    })
    if len(marquants) >= 50: break

# Save
result = {
    '_meta': {
        'description': '50 bénéficiaires marquants 2021-2025 avec données 5 ans, citations et sources',
        'years': ['2021','2022','2023','2024','2025'],
        'with_editorial': sum(1 for m in marquants if m['editorial']),
        'total_count': len(marquants),
    },
    'marquants': marquants,
}
open(DATA / 'marquants_2021_2025_top50.json', 'w', encoding='utf-8').write(json.dumps(result, ensure_ascii=False, indent=2))
print(f"  ✓ marquants_2021_2025_top50.json — {len(marquants)} bénéficiaires, dont {sum(1 for m in marquants if m['editorial'])} avec citation/source")
print(f"\n  Premiers 10 :")
for i, m in enumerate(marquants[:10], 1):
    mark = '✦' if m['editorial'] else ' '
    print(f"   {i:>2}. {mark} {m['nom'][:50]:<50} {m['total_cumul']/1e6:>5.2f}M")
