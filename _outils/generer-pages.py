"""Génère les pages commerciales du site FUSION TV et harmonise la navigation des pages existantes, selon le réglage
commercial de commerce.json (mode bêta ou vente, adresse de commande, campagne de lancement, contacts).

    python3 _outils/generer-pages.py        (depuis la racine du site)

Mode « beta » : tarifs prévus, « Ouverture prochaine », aucune commande. Mode « vente » : boutons Commander vers
l'adresse de commande, tarif de lancement affiché seulement si une campagne est renseignée (avec ses limites réelles et
le tarif prévu ensuite, jamais de prix barré), lien vers les CGV. Le dossier _outils n'est pas servi par GitHub Pages."""
import datetime
import json
import re
from pathlib import Path

SITE = Path(".")
REGLAGE = json.loads((SITE / "commerce.json").read_text())
VENTE = REGLAGE["mode"] == "vente"
CAMPAGNE = REGLAGE.get("campagne") if VENTE else None
URL_COMMANDE = REGLAGE.get("url_commande")
URL_ESPACE_REVENDEUR = REGLAGE.get("url_espace_revendeur")
OFFRES = REGLAGE["offres"]
CONTACT = REGLAGE["contact"]
# Adresse des revendeurs : réglée dans commerce.json (revendeurs@fusion-tv.fr à l'ouverture).
CONTACT_REVENDEURS = REGLAGE["contact_revendeurs"]
if VENTE and not (URL_COMMANDE or "").startswith("https://"):
    raise SystemExit("Mode vente : renseignez une adresse de commande https:// dans commerce.json.")
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


def B(beta, vente):
    """Texte selon le mode : bêta (avant l'ouverture) ou vente."""
    return vente if VENTE else beta


def date_fr(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{'1er' if d.day == 1 else d.day} {MOIS[d.month - 1]} {d.year}"

NAV = [("index.html", "Accueil"), ("fonctionnalites.html", "Fonctionnalités"), ("tarifs.html", "Tarifs"), ("premium.html", "Premium"),
       ("revendeurs.html", "Revendeurs"), ("activation.html", "Activation"), ("assistance.html", "Assistance")]

ICONES = {
    "accueil": '<path d="M3.5 11 12 4l8.5 7v8.5a1 1 0 0 1-1 1H15v-6H9v6H4.5a1 1 0 0 1-1-1z" fill="currentColor"/>',
    "tarifs": '<path d="M3.5 12.5 11 5h8.5v8.5L12 21z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><circle cx="15.5" cy="9" r="1.6" fill="currentColor"/>',
    "activation": '<circle cx="8" cy="15" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="m11 12 8-8M16 7l2 2M14 9l2 2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    "aide": '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M9.6 9.3a2.5 2.5 0 1 1 3.4 2.3c-.7.3-1 .8-1 1.5v.6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><circle cx="12" cy="17" r="1" fill="currentColor"/>',
    "telecharger": '<path d="M12 3.5v11M7.5 10.5 12 15l4.5-4.5M4 15.5v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>',
}
ONGLETS = [("index.html", "Accueil", "accueil"), ("tarifs.html", "Tarifs", "tarifs"), ("activation.html", "Activation", "activation"),
           ("assistance.html", "Aide", "aide"), ("telecharger.html", "Télécharger", "telecharger")]
LIENS_PIED = [("fonctionnalites.html", "Fonctionnalités"), ("tarifs.html", "Tarifs"), ("premium.html", "Premium"), ("revendeurs.html", "Revendeurs"),
              ("activation.html", "Activation"), ("assistance.html", "Assistance"), ("telecharger.html", "Télécharger"),
              ("installation.html", "Installation"), ("compatibilite.html", "Compatibilité"), ("beta.html", "Bêta privée"),
              ("a-propos.html", "À propos"), ("contact.html", "Contact"), ("mentions-legales.html", "Mentions légales"),
              ("confidentialite.html", "Confidentialité")] + ([("cgv.html", "CGV")] if VENTE else [])
SVG_DL = ('<svg viewBox="0 0 24 24" aria-hidden="true">' + ICONES["telecharger"] + "</svg>")


def nav_html(page):
    items = "".join(f'<li><a href="{h}"{" aria-current=\"page\"" if h == page else ""}>{t}</a></li>' for h, t in NAV)
    return ('<nav class="navigation" aria-label="Navigation principale">\n'
            '        <button class="bouton-menu" type="button" aria-expanded="false" aria-controls="menu-principal">Menu</button>\n'
            f'        <ul id="menu-principal">{items}</ul>\n      </nav>')


def onglets_html(page):
    liens = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h == page else ""}><svg viewBox="0 0 24 24" aria-hidden="true">{ICONES[i]}</svg>{t}</a>'
                    for h, t, i in ONGLETS)
    return f'<nav class="onglets" aria-label="Navigation mobile">{liens}</nav>'


def pied_html():
    liens = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in LIENS_PIED)
    return ('<footer class="pied-page">\n    <div class="conteneur">\n'
            '      <img src="assets/img/logo-small.png" alt="FUSION TV" width="280" height="93" loading="lazy">\n'
            f'      <p class="ligne-pied">© <span id="annee">2026</span> FUSION TV — Lecteur IPTV pour Android{"" if VENTE else " — Bêta privée, vente non ouverte"}</p>\n'
            f'      <ul class="pied-liens">{liens}</ul>\n    </div>\n  </footer>')


def page(fichier, titre, description, corps):
    url = "https://fusion-tv.fr/" + ("" if fichier == "index.html" else fichier)
    html = f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{titre}</title>
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#08090c">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="FUSION TV">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:title" content="{titre}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="https://fusion-tv.fr/assets/img/partage.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="assets/img/favicon-32.png">
  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body class="accueil page-{fichier[:-5]}" data-mode="{REGLAGE["mode"]}">
  <a class="lien-evitement" href="#contenu">Aller au contenu</a>

  <header class="entete">
    <div class="conteneur">
      <a class="logo" href="index.html" aria-label="FUSION TV — accueil"><img src="assets/img/logo-small.png" alt="FUSION TV" width="280" height="93"></a>
      {nav_html(fichier)}
      <a class="lien-telecharger" href="telecharger.html">{SVG_DL}<span>Télécharger</span></a>
    </div>
  </header>

  <main id="contenu">
{corps}
  </main>

  {pied_html()}

  {onglets_html(fichier)}

  <script>
    const nav = document.querySelector(".navigation");
    const bouton = nav.querySelector(".bouton-menu");
    bouton.addEventListener("click", () => {{
      const ouvert = nav.classList.toggle("ouverte");
      bouton.setAttribute("aria-expanded", String(ouvert));
    }});
    document.getElementById("annee").textContent = new Date().getFullYear();
  </script>
</body>
</html>
"""
    (SITE / fichier).write_text(html)


def titre_section(ident, texte):
    return f'<h2 class="titre-section" id="{ident}"><span>{texte}</span></h2>'


AUCUN_CONTENU = ('<p class="avertissement-contenu">FUSION TV est uniquement un lecteur IPTV. Aucun abonnement IPTV, aucune chaîne, '
                 "aucun film ni aucune série n'est fourni : vous utilisez vos propres sources, dont vous devez détenir les droits.</p>")

# --- Accueil ---------------------------------------------------------------------------------------------------
ACCUEIL = f"""    <section class="principale" id="accueil" aria-labelledby="titre-principal">
      <div class="conteneur">
        <div class="principale-texte">
          <h1 id="titre-principal" class="principale-logo"><img src="assets/img/logo-grand.webp" alt="FUSION TV — Tous vos contenus. Un seul univers." width="1120" height="373"></h1>
          <p class="sous-titre">Le lecteur IPTV premium pour vos écrans Android.</p>
          <p class="description">FUSION TV lit vos propres sources IPTV (Xtream, listes M3U, guides XMLTV) avec une interface pensée pour chaque écran : téléviseur Android TV et Google TV, tablette et smartphone Android. Une seule licence pour les trois.</p>
          <div class="actions">
            <a class="bouton" href="tarifs.html"><span>{B("Voir les tarifs prévus", "Choisir ma licence")}</span><svg class="chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></a>
            {B('<p class="badge-ouverture">Ouverture prochaine</p>', "")}
            <a class="lien-telecharger lien-telecharger-mobile" href="telecharger.html">{SVG_DL}<span>{B("Télécharger la bêta", "Télécharger")}</span></a>
          </div>
        </div>
        <figure class="televiseur">
          <div class="televiseur-cadre">
            <img class="televiseur-image" src="assets/img/televiseur.webp" srcset="assets/img/televiseur-940.webp 940w, assets/img/televiseur.webp 1410w" sizes="(max-width: 900px) 100vw, 640px" alt="" width="1410" height="890">
            <div class="televiseur-ecran"><img src="assets/img/ecran-guide.jpg" alt="Guide TV de FUSION TV sur téléviseur : programme en cours, groupes de chaînes et grille horaire (données de démonstration)." width="1280" height="720" fetchpriority="high"></div>
          </div>
          <figcaption>Capture réelle de l'application sur téléviseur — Guide TV, données de démonstration.</figcaption>
        </figure>
      </div>
    </section>

    <div class="separateur" aria-hidden="true"></div>

    <section aria-labelledby="titre-ecrans">
      <div class="conteneur">
        {titre_section("titre-ecrans", 'Une licence, <span class="or">trois interfaces</span>')}
        <p class="chapeau">Chaque écran a son interface : la télécommande sur le téléviseur, le toucher en paysage sur la tablette, une application mobile dédiée sur le smartphone. Une licence couvre un téléviseur, un téléphone et une tablette.</p>
        <div class="trois-ecrans">
          <figure class="appareil appareil-tv">
            <div class="appareil-cadre"><img src="assets/img/ecran-films.jpg" alt="Films sur téléviseur : film à la une et rangées par catégorie (données de démonstration)." width="1280" height="720" loading="lazy"></div>
            <figcaption><strong>Téléviseur</strong><span>Android TV et Google TV, tout à la télécommande.</span></figcaption>
          </figure>
          <figure class="appareil appareil-tablette">
            <div class="appareil-cadre"><img src="assets/img/ecran-tablette-guide.webp" alt="Guide TV sur tablette, au doigt et en paysage (données de démonstration)." width="1280" height="800" loading="lazy"></div>
            <figcaption><strong>Tablette</strong><span>L'interface du téléviseur, au doigt et en paysage.</span></figcaption>
          </figure>
          <figure class="appareil appareil-mobile">
            <div class="appareil-cadre"><img src="assets/img/ecran-mobile-accueil.webp" alt="Accueil de l'application mobile : direct à la une, accès rapides et reprise de lecture (données de démonstration)." width="620" height="1344" loading="lazy"></div>
            <figcaption><strong>Smartphone</strong><span>Une interface mobile spécifique.</span></figcaption>
          </figure>
        </div>
        <p class="mention-captures">Captures réelles de l'application, avec le catalogue de démonstration intégré (aucune chaîne ni aucun film réel).</p>
      </div>
    </section>

    <section class="decouvrir" aria-labelledby="titre-avantages">
      <div class="conteneur">
        {titre_section("titre-avantages", 'Pourquoi <span class="or">FUSION TV</span>')}
        <div class="cartes">
          <article class="carte"><img src="assets/img/icone-sources.webp" alt="" width="192" height="192" loading="lazy"><div><h3>Vos sources, bien rangées</h3><p>Connexions Xtream et listes M3U, guide XMLTV. Un abonnement s'envoie d'un appareil à l'autre par QR code, chiffré de bout en bout.</p></div></article>
          <article class="carte"><img src="assets/img/icone-guide.webp" alt="" width="192" height="192" loading="lazy"><div><h3>Direct et Guide TV</h3><p>Chaînes par groupes, programme en cours et suivant, grille horaire, replay lorsque votre fournisseur le propose.</p></div></article>
          <article class="carte"><img src="assets/img/icone-films.webp" alt="" width="192" height="192" loading="lazy"><div><h3>Films et séries</h3><p>Catalogue organisé, recherche, reprise de lecture, épisode suivant, pistes audio et sous-titres.</p></div></article>
          <article class="carte"><img src="assets/img/icone-favoris.webp" alt="" width="192" height="192" loading="lazy"><div><h3>Profils et favoris</h3><p>Plusieurs profils sur un même appareil, chacun avec ses favoris et son historique.</p></div></article>
          <article class="carte"><img src="assets/img/icone-telecommande.webp" alt="" width="192" height="192" loading="lazy"><div><h3>Une lecture à la fois</h3><p>Une licence : un téléviseur, un téléphone et une tablette, avec une seule lecture simultanée.</p></div></article>
          <article class="carte"><img src="assets/img/icone-direct.webp" alt="" width="192" height="192" loading="lazy"><div><h3>12 mois, sans engagement</h3><p>La licence dure 12 mois à partir de sa première activation. Aucun renouvellement automatique.</p></div></article>
        </div>
      </div>
    </section>

    <section aria-labelledby="titre-formules">
      <div class="conteneur">
        {titre_section("titre-formules", 'Deux <span class="or">formules</span>')}
        <div class="formules">
          <article class="formule">
            <span class="etat{B("", " etat-or")}">{B("Prévue à l'ouverture", "Disponible")}</span>
            <h3>Standard</h3>
            <p>Toutes les fonctions de lecture et de gestion de vos sources IPTV, sur téléviseur, tablette et smartphone.</p>
            <a class="bouton bouton-contour" href="tarifs.html"><span>{B("Tarifs prévus", "Voir les tarifs")}</span></a>
          </article>
          <article class="formule formule-premium">
            <span class="etat etat-or">En préparation</span>
            <h3>Premium</h3>
            <p>Tout Standard, avec des fiches enrichies grâce à The Movie Database (TMDB). Pas encore commercialisée : ni prix ni date annoncés.</p>
            <a class="bouton bouton-contour" href="premium.html"><span>Découvrir Premium</span></a>
          </article>
        </div>
        {AUCUN_CONTENU}
      </div>
    </section>

    <section class="contact" aria-labelledby="titre-appel">
      <div class="conteneur">
        <div class="appel">
          <h2 id="titre-appel">{B("La vente des licences ouvrira prochainement", "Prêt à installer FUSION TV ?")}</h2>
          <p>{B("Aucune commande ni aucun paiement pour le moment. La bêta privée reste gratuite pour les testeurs.",
                "Téléchargez l'application, choisissez votre licence et activez votre code sur chacun de vos appareils.")}</p>
          <div class="actions"><a class="bouton" href="tarifs.html"><span>{B("Tarifs prévus", "Choisir ma licence")}</span></a><a class="bouton bouton-contour" href="telecharger.html"><span>{B("Télécharger la bêta", "Télécharger")}</span></a></div>
        </div>
      </div>
    </section>"""

# --- Tarifs ----------------------------------------------------------------------------------------------------
def offre(ident, contenu, unite, points, mise_en_avant=False, etiquette=None):
    """Carte d'une offre. Bêta : tarif prévu et « Ouverture prochaine ». Vente : bouton Commander ; pendant une campagne
    de lancement, le tarif de lancement, ses limites réelles et le tarif prévu ensuite (aucun prix barré)."""
    o = OFFRES[ident]
    classe = "offre offre-mise-en-avant" if mise_en_avant else "offre"
    tag = f'<span class="offre-etiquette">{etiquette}</span>' if etiquette else ""
    lis = "".join(f"<li>{p}</li>" for p in points)
    unite = f"{o['taxe']}{unite}"
    lancement = (CAMPAGNE or {}).get("lancement", {}).get(ident)
    if not VENTE:
        prix, note, action = o["prix"], "Tarif prévu à l'ouverture", '<p class="badge-ouverture">Ouverture prochaine</p>'
    else:
        action = f'<a class="bouton offre-commander" href="{URL_COMMANDE}?offre={ident}" data-offre="{ident}"><span>Commander</span></a>'
        if lancement:
            pro = o["taxe"] == "HT"
            limite = (f"sur le premier pack, pour les {CAMPAGNE['quota_revendeurs']} premiers revendeurs" if pro
                      else f"dans la limite de {CAMPAGNE['quota_licences']} licences")
            prix = lancement
            note = f"Tarif de lancement jusqu'au {date_fr(CAMPAGNE['fin'])}, {limite}. Tarif prévu ensuite : {o['prix']} {o['taxe']}."
        else:
            prix, note = o["prix"], "Licence de 12 mois, sans renouvellement automatique"
    return (f'<article class="{classe}">{tag}<h2>{o["nom"]}</h2><p class="offre-contenu">{contenu}</p>'
            f'<p class="offre-prix">{prix} <small>{unite}</small></p><p class="offre-note">{note}</p>'
            f'<ul>{lis}</ul>{action}</article>')

TARIFS = f"""    <section class="page-titre" aria-labelledby="titre-tarifs">
      <div class="conteneur">
        <p class="surtitre">Particuliers · formule Standard</p>
        <h1 id="titre-tarifs">{B("Tarifs prévus à l'ouverture", "Tarifs")}</h1>
        <p>Des licences annuelles simples : chaque licence dure 12 mois à partir de sa première activation, sur un téléviseur, un téléphone et une tablette.{B(" La vente n'est pas encore ouverte.", "")}</p>
      </div>
    </section>

    <section aria-label="Offres particuliers">
      <div class="conteneur">
        <div class="offres">
          {offre("solo", "1 licence", " / an", ["1 téléviseur, 1 téléphone, 1 tablette", "1 lecture à la fois", "12 mois dès la première activation", "Sans renouvellement automatique"])}
          {offre("famille3", "3 licences indépendantes", " / an", ["3 licences de 12 mois", "Jusqu'à 3 lectures simultanées, une par licence", "Chaque licence : 1 téléviseur, 1 téléphone, 1 tablette", "Un nom pour chaque licence (Salon, Chambre…)"], True, "Pour la famille")}
          {offre("famille5", "5 licences indépendantes", " / an", ["5 licences de 12 mois", "Jusqu'à 5 lectures simultanées, une par licence", "Chaque licence : 1 téléviseur, 1 téléphone, 1 tablette", "Codes à répartir dans le foyer"])}
        </div>
        <div class="precisions">
          <div><h3>Comment fonctionne une licence</h3><ul><li>Un code de 16 caractères, à saisir dans l'application.</li><li>12 mois à partir de la première activation ; un code non activé ne démarre pas sa période.</li><li>Renouvellement : un nouveau code ajoute 12 mois après l'échéance, sans perdre de jours.</li></ul></div>
          <div><h3>Packs Famille</h3><ul><li>Les licences d'un pack sont indépendantes : chacune a ses trois appareils et sa lecture.</li><li>Un pack est acheté par une seule personne, qui répartit les codes.</li></ul></div>
          <div><h3>Ce qui n'est pas inclus</h3><p>Aucun abonnement IPTV, aucune chaîne, aucun film ni aucune série. FUSION TV lit les sources que vous ajoutez vous-même.</p></div>
          {B("<div><h3>Avant l'ouverture</h3><p>Ces tarifs sont ceux prévus à l'ouverture. Les conditions de vente définitives seront publiées au moment de l'ouverture des ventes. Aucune commande n'est possible pour l'instant.</p></div>",
             '<div><h3>Conditions de vente</h3><p>Prix TTC. Codes remis après paiement, affichés une seule fois. Avant de commander, consultez les <a href="cgv.html">conditions générales de vente</a>, notamment sur le droit de rétractation des contenus numériques.</p></div>')}
        </div>
      </div>
    </section>

    <section aria-labelledby="titre-premium-teaser">
      <div class="conteneur">
        <div class="appel">
          <h2 id="titre-premium-teaser">Premium, en préparation</h2>
          <p>Une formule avec des fiches enrichies par The Movie Database (TMDB). Elle n'est pas encore commercialisée : aucun prix n'est annoncé.</p>
          <div class="actions"><a class="bouton bouton-contour" href="premium.html"><span>En savoir plus</span></a><a class="bouton bouton-contour" href="revendeurs.html"><span>Programme revendeur</span></a></div>
        </div>
      </div>
    </section>"""

# --- Premium ---------------------------------------------------------------------------------------------------
PREMIUM = f"""    <section class="page-titre" aria-labelledby="titre-premium">
      <div class="conteneur">
        <p class="surtitre">Formule en préparation</p>
        <h1 id="titre-premium">FUSION TV Premium</h1>
        <p>Toutes les fonctions de Standard, avec l'enrichissement des fiches de films et de séries par The Movie Database (TMDB). Premium n'est pas encore commercialisée : aucun prix ni aucune date ne sont annoncés.</p>
      </div>
    </section>

    <section aria-labelledby="titre-enrichissements">
      <div class="conteneur">
        {titre_section("titre-enrichissements", 'Ce que <span class="or">TMDB</span> apporte')}
        <p class="chapeau">Les compléments ne remplissent que ce que votre fournisseur ne donne pas, après vérification de la correspondance (titre et année). Les informations de votre fournisseur restent prioritaires.</p>
        <div class="cartes">
          <article class="carte carte-texte"><div><h3>Classifications françaises</h3><p>Âge conseillé des films et des séries (Tous publics, -10, -12, -16, -18).</p></div></article>
          <article class="carte carte-texte"><div><h3>Fiches complétées</h3><p>Synopsis, genres, distribution, réalisation et bande-annonce lorsqu'ils manquent.</p></div></article>
          <article class="carte carte-texte"><div><h3>Sagas</h3><p>Les films d'une même saga regroupés, avec une catégorie « Par saga ».</p></div></article>
          <article class="carte carte-texte"><div><h3>Recommandations</h3><p>Des titres proches, choisis uniquement parmi ceux de votre propre catalogue.</p></div></article>
          <article class="carte carte-texte"><div><h3>Recherche étendue</h3><p>Retrouver un film ou une série par un acteur, la réalisation ou un genre connus de TMDB.</p></div></article>
          <article class="carte carte-texte"><div><h3>Affiches et images</h3><p>Affiche et image de fond lorsque votre fournisseur n'en propose pas.</p></div></article>
        </div>
      </div>
    </section>

    <section aria-labelledby="titre-premium-regles">
      <div class="conteneur">
        <div class="precisions">
          <div><h3>Standard garde tout le reste</h3><p>Lecture, Guide TV, replay, films, séries, profils, favoris et reprise : tout fonctionne en Standard, avec les informations de votre fournisseur.</p></div>
          <div><h3>Si Premium prend fin</h3><p>Les compléments TMDB ne sont plus affichés et sont effacés de l'appareil. Vos sources, favoris et historiques sont conservés.</p></div>
          <div><h3>Pourquoi « en préparation »</h3><p>Une utilisation commerciale de TMDB demande un accord avec TMDB. Premium ne sera proposée qu'une fois ces conditions connues.</p></div>
          <div class="attribution"><img src="assets/img/tmdb-logo.svg" alt="The Movie Database (TMDB)" width="160" height="21" loading="lazy"><p>Ce produit utilise l'API TMDB mais n'est ni approuvé ni certifié par TMDB.</p></div>
        </div>
        {AUCUN_CONTENU}
      </div>
    </section>"""

# --- Revendeurs ------------------------------------------------------------------------------------------------
REVENDEURS = f"""    <section class="page-titre" aria-labelledby="titre-revendeurs">
      <div class="conteneur">
        <p class="surtitre">Professionnels</p>
        <h1 id="titre-revendeurs">Programme revendeur</h1>
        <p>Des packs de licences FUSION TV Standard pour les professionnels qui équipent ou accompagnent leurs clients. {B("Le programme ouvrira avec la vente des licences.", "")}</p>
      </div>
    </section>

    <section aria-label="Packs revendeurs">
      <div class="conteneur">
        <div class="offres">
          {offre("pro10", "10 licences indépendantes", "", ["10 codes de licence de 12 mois", "Chaque licence : 1 téléviseur, 1 téléphone, 1 tablette", "Période démarrée à l'activation de chaque code"])}
          {offre("pro25", "25 licences indépendantes", "", ["25 codes de licence de 12 mois", "Chaque licence : 1 téléviseur, 1 téléphone, 1 tablette", "Période démarrée à l'activation de chaque code"])}
          {offre("pro50", "50 licences indépendantes", "", ["50 codes de licence de 12 mois", "Chaque licence : 1 téléviseur, 1 téléphone, 1 tablette", "Période démarrée à l'activation de chaque code"])}
        </div>
        <div class="precisions">
          <div><h3>Les codes</h3><ul><li>Remis une seule fois, à conserver et à transmettre à vos clients.</li><li>Un code non activé ne commence pas sa période de 12 mois.</li><li>Chaque licence est indépendante des autres.</li></ul></div>
          <div><h3>{B("Prévu pour les revendeurs", "Espace revendeur")}</h3><ul><li>{B("Un espace revendeur sécurisé pour suivre vos packs (en préparation).", f'Suivi de vos packs dans l\'<a href="{URL_ESPACE_REVENDEUR}">espace revendeur sécurisé</a>.' if URL_ESPACE_REVENDEUR else "Un espace revendeur sécurisé pour suivre vos packs (en préparation).")}</li><li>Réservé aux professionnels identifiés.</li></ul></div>
          <div><h3>Règle essentielle</h3><p>FUSION TV est un lecteur : il ne fournit aucun contenu. Les licences ne doivent jamais être vendues avec des abonnements ou des contenus dont les droits ne sont pas détenus.</p></div>
          <div><h3>{B("Être informé de l'ouverture", "Devenir revendeur")}</h3><p>Écrivez-nous en précisant votre activité : <a href="mailto:{CONTACT_REVENDEURS}" data-contact="revendeurs"><!-- CONTACT-REVENDEURS -->{CONTACT_REVENDEURS}</a>.</p></div>
        </div>
        <p class="avertissement-contenu">{B("Prix hors taxes prévus à l'ouverture, par pack. Aucune commande n'est possible pour l'instant ; les conditions de vente aux professionnels seront publiées à l'ouverture.",
                                             "Prix hors taxes, par pack. Vente réservée aux professionnels, selon les conditions de vente aux professionnels.")}</p>
      </div>
    </section>"""

# --- Activation ------------------------------------------------------------------------------------------------
ACTIVATION = f"""    <section class="page-titre" aria-labelledby="titre-activation">
      <div class="conteneur">
        <p class="surtitre">Licence FUSION TV</p>
        <h1 id="titre-activation">Activer votre licence</h1>
        <p>Un code de 16 caractères, saisi une fois sur chaque appareil. L'activation se fait toujours en ligne, auprès du service FUSION Access.{B(" Disponible à l'ouverture des ventes.", "")}</p>
      </div>
    </section>

    <section class="document" aria-label="Étapes d'activation">
      <div class="conteneur">
        <ol class="etapes">
          <li><h2>Installez FUSION TV</h2><p>Sur votre téléviseur Android TV ou Google TV, votre tablette ou votre smartphone Android, depuis la page <a href="telecharger.html">Télécharger</a>.</p></li>
          <li><h2>Saisissez votre code</h2><p>Au premier lancement, choisissez « J'ai un code de licence », puis saisissez les 16 caractères (par exemple <code>XXXX-XXXX-XXXX-XXXX</code>). Les tirets s'ajoutent tout seuls ; une faute de frappe est signalée avant tout envoi.</p></li>
          <li><h2>Vérifiez puis confirmez</h2><p>« Vérifier le code » affiche ce que fera le code — durée, dates, appareil — sans rien utiliser. Vous confirmez ensuite l'activation.</p></li>
          <li><h2>Ajoutez vos autres appareils</h2><p>Saisissez le même code sur votre téléphone et votre tablette : chaque licence accepte un téléviseur, un téléphone et une tablette, avec une seule lecture à la fois.</p></li>
        </ol>
        <div class="illustrations">
          <figure><img src="assets/img/activation-tv-apercu.webp" alt="Téléviseur : aperçu d'un code avant confirmation — Licence Standard de 12 mois, avec les dates." width="1280" height="720" loading="lazy"><figcaption>Téléviseur : l'aperçu avant confirmation.</figcaption></figure>
          <figure><img src="assets/img/activation-mobile-apercu.webp" alt="Smartphone : aperçu d'un code avant confirmation." width="620" height="1344" loading="lazy"><figcaption>Smartphone.</figcaption></figure>
        </div>
        <p class="mention-captures">Captures réelles de l'application, réalisées avec un serveur d'essai (codes fictifs).</p>

        <h2>Renouveler</h2>
        <p>Dans Paramètres › FUSION Access (téléviseur, tablette) ou Plus › Mon compte (smartphone), choisissez « Ajouter un code ». Un code de la même formule ajoute 12 mois après l'échéance de votre licence : aucun jour n'est perdu.</p>
        <p>Un code d'une autre formule prend effet à l'échéance de la licence en cours ; l'application vous l'annonce et vous demande de le confirmer avant de l'enregistrer.</p>
        <div class="illustrations">
          <figure><img src="assets/img/activation-tv-formule.webp" alt="Téléviseur : changement de formule annoncé avant confirmation, avec les dates de début et de fin." width="1280" height="720" loading="lazy"><figcaption>Changement de formule annoncé avant confirmation.</figcaption></figure>
          <figure><img src="assets/img/activation-mobile-compte.webp" alt="Smartphone : page Mon compte avec la licence — nom, formule, état, dates et appareil." width="620" height="1344" loading="lazy"><figcaption>Smartphone : Mon compte.</figcaption></figure>
        </div>

        <h2>Changer d'appareil</h2>
        <p>Nouveau téléviseur, téléphone remplacé ? Saisissez le code de la licence sur le nouvel appareil. Si la licence a déjà un appareil de ce type, une demande de changement d'appareil est envoyée : après validation par l'assistance FUSION TV, le nouvel appareil remplace l'ancien.</p>

        <h2>Si le code est refusé</h2>
        <ul>
          <li><strong>Code mal saisi</strong> : vérifiez les 16 caractères ; les lettres I, L, O et les chiffres 0 et 1 n'existent pas dans les codes.</li>
          <li><strong>Code inconnu ou déjà utilisé</strong> : un code ne sert qu'à une seule licence. Contactez l'assistance si vous pensez à une erreur.</li>
          <li><strong>Service injoignable</strong> : un nouveau code ne s'active qu'en ligne. Réessayez une fois connecté.</li>
          <li><strong>Trop d'essais</strong> : la saisie est suspendue un moment, par sécurité.</li>
        </ul>
        <p>Conservez vos codes : ils ne sont affichés qu'une seule fois, à l'achat.</p>
      </div>
    </section>"""

# --- Assistance ------------------------------------------------------------------------------------------------
def q(question, *paragraphes):
    return "<details><summary>" + question + "</summary><div>" + "".join(f"<p>{p}</p>" for p in paragraphes) + "</div></details>"

ASSISTANCE = f"""    <section class="page-titre" aria-labelledby="titre-assistance">
      <div class="conteneur">
        <p class="surtitre">Assistance</p>
        <h1 id="titre-assistance">Questions fréquentes</h1>
        <p>Licences, appareils, lecture et sources IPTV. Une autre question ? Écrivez à <a href="mailto:{CONTACT}">{CONTACT}</a>.</p>
      </div>
    </section>

    <section class="document" aria-label="Questions fréquentes">
      <div class="conteneur">
        <h2 class="faq-groupe">FUSION TV et vos sources</h2>
        <div class="faq">
          {q("FUSION TV fournit-il des chaînes, des films ou des séries ?", "Non. FUSION TV est uniquement un lecteur IPTV : aucun abonnement, aucune chaîne, aucun film ni aucune série n'est fourni. Vous ajoutez vos propres sources, dont vous devez détenir les droits.")}
          {q("Quelles sources puis-je ajouter ?", "Une connexion Xtream (adresse du serveur, identifiant, mot de passe) ou une liste M3U, avec un guide des programmes XMLTV facultatif. Le replay est proposé lorsque votre fournisseur l'annonce, sur les connexions Xtream.", "Vos identifiants restent chiffrés sur votre appareil : ils ne sont jamais envoyés au service de licences FUSION Access.")}
          {q("Sur quels appareils fonctionne FUSION TV ?", "Téléviseurs et boîtiers Android TV et Google TV, tablettes et smartphones Android (Android 8.0 ou plus récent). Il n'existe pas de version pour iPhone, iPad, Apple TV ni pour les téléviseurs non Android.")}
        </div>

        <h2 class="faq-groupe">Licences</h2>
        <div class="faq">
          {q("Combien d'appareils par licence ?", "Une licence accepte un téléviseur, un téléphone et une tablette, rattachés à la licence.")}
          {q("Puis-je regarder sur deux appareils en même temps ?", "Une licence permet une seule lecture à la fois, quel que soit le nombre de sources ou d'abonnements IPTV configurés. Avec un pack Famille, chaque licence a sa propre lecture : trois lectures simultanées avec Famille 3, une par licence.")}
          {q("Quand commence ma licence ?", "À sa première activation, pour 12 mois. Un code non activé ne commence pas sa période. Il n'y a aucun renouvellement automatique.")}
          {q("Comment renouveler ?", "Ajoutez un nouveau code depuis les réglages de l'application : 12 mois s'ajoutent après l'échéance, sans perdre de jours. Voir <a href=\"activation.html\">Activation</a>.")}
          {q("J'ai changé de téléviseur ou de téléphone.", "Saisissez le code de votre licence sur le nouvel appareil. Si la place de ce type est déjà prise, une demande de changement d'appareil est envoyée et validée par l'assistance.")}
          {q("Quelle différence entre Standard et Premium ?", "Standard comprend toutes les fonctions de lecture et de gestion de vos sources. Premium, en préparation, y ajoute l'enrichissement des fiches par TMDB. Voir <a href=\"premium.html\">Premium</a>.")}
        </div>

        <h2 class="faq-groupe">Connexion et hors ligne</h2>
        <div class="faq">
          {q("FUSION TV fonctionne-t-il sans connexion au service FUSION Access ?", "Oui, pendant un temps : la licence est vérifiée régulièrement, et si le service est momentanément injoignable alors qu'Internet fonctionne, FUSION TV continue de fonctionner jusqu'à 7 jours. La vérification reprend dès que le service répond.", "Vos sources IPTV, elles, demandent bien sûr une connexion à Internet pour être regardées.")}
          {q("Puis-je activer un code hors ligne ?", "Non : un nouveau code s'active uniquement en ligne, auprès du service FUSION Access.")}
          {q("Changer l'heure de l'appareil prolonge-t-il la licence ?", "Non. L'application utilise l'heure du service de licences ; reculer l'horloge de l'appareil ne change rien.")}
        </div>

        <h2 class="faq-groupe">Vos données</h2>
        <div class="faq">
          {q("Que conserve le service FUSION Access ?", "Ce qui sert à la licence : l'appareil (type, modèle, version de l'application), l'état et les dates de la licence, la durée d'utilisation de l'application et, pendant une lecture, une empreinte illisible de l'abonnement lu, pour la règle d'une lecture à la fois.", "Jamais vos identifiants IPTV, vos listes, vos favoris ni votre historique, qui restent sur vos appareils. Voir la <a href=\"confidentialite.html\">politique de confidentialité</a>.")}
        </div>
      </div>
    </section>"""


def harmoniser(fichier):
    """Pages existantes : même navigation, même pied de page et mêmes onglets que les nouvelles pages."""
    chemin = SITE / fichier
    html = chemin.read_text()
    html = re.sub(r'<nav class="navigation".*?</nav>', nav_html(fichier), html, count=1, flags=re.S)
    html = re.sub(r'<footer class="pied-page">.*?</footer>', pied_html(), html, count=1, flags=re.S)
    if '<nav class="onglets"' in html:
        html = re.sub(r'<nav class="onglets".*?</nav>', onglets_html(fichier), html, count=1, flags=re.S)
    if fichier == "telecharger.html":
        html = re.sub(r'<p class="installer-mention">.*?</p>', '<p class="installer-mention">'
                      + B("Bêta privée gratuite — activation requise", "Licence FUSION TV requise — code à saisir après l'installation") + "</p>", html, count=1)
    chemin.write_text(html)


if __name__ == "__main__":
    page("index.html", "FUSION TV — Lecteur IPTV premium pour Android TV, tablette et smartphone",
         "FUSION TV, lecteur IPTV pour Android TV, Google TV, tablette et smartphone Android : une licence pour trois appareils. Aucun contenu fourni.", ACCUEIL)
    page("tarifs.html", "Tarifs — FUSION TV", B("Tarifs prévus à l'ouverture des licences FUSION TV Standard", "Tarifs des licences FUSION TV Standard") + " : Solo, Famille 3 et Famille 5. Licence de 12 mois, sans renouvellement automatique.", TARIFS)
    page("premium.html", "Premium — FUSION TV", "FUSION TV Premium, en préparation : fiches enrichies par The Movie Database (TMDB). Non commercialisée, aucun prix annoncé.", PREMIUM)
    page("revendeurs.html", "Programme revendeur — FUSION TV", "Packs de licences FUSION TV pour les professionnels : Pro 10, Pro 25 et Pro 50." + B(" Ouverture avec la vente des licences.", ""), REVENDEURS)
    page("activation.html", "Activation — FUSION TV", "Activer une licence FUSION TV avec un code de 16 caractères, la renouveler et changer d'appareil.", ACTIVATION)
    page("assistance.html", "Assistance — FUSION TV", "Questions fréquentes sur FUSION TV : licences, appareils, lecture simultanée, fonctionnement hors ligne, sources IPTV.", ASSISTANCE)
    for existante in ("fonctionnalites.html", "compatibilite.html", "beta.html", "a-propos.html", "contact.html", "telecharger.html",
                      "installation.html", "mentions-legales.html", "confidentialite.html"):
        harmoniser(existante)
