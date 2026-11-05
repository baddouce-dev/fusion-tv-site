/*
 * FUSION TV — tarifs réels (mode vente seulement). La page est publiée avec les tarifs standards ; ce script demande
 * au catalogue public de FUSION Access, seule source officielle, si un tarif de lancement s'applique maintenant.
 * Règle : aucune promotion n'est affichée sans confirmation du service. Sans réponse (panne, délai, réponse
 * inattendue), la page garde ses tarifs standards. Le prix est de toute façon confirmé par le serveur à la commande.
 */
(function () {
  "use strict";
  var script = document.currentScript;
  var adresse = script && script.dataset.catalogue;
  if (!adresse || !window.fetch) return;
  var DELAI_MS = 4000;
  var dateFr = new Intl.DateTimeFormat("fr-FR", { day: "numeric", month: "long", year: "numeric", timeZone: "Europe/Paris" });

  function valide(c) {
    return c && c.v === 1 && typeof c.sales === "boolean" && Array.isArray(c.offers);
  }

  function appliquer(c) {
    document.querySelectorAll("article.offre[data-offre]").forEach(function (carte) {
      var id = carte.dataset.offre;
      var offre = c.offers.filter(function (o) { return o.id === id; })[0];
      var bouton = carte.querySelector(".offre-commander");
      // Vente fermée par le service, ou offre retirée : plus de bouton Commander.
      if (!c.sales || !offre) {
        if (bouton) {
          var badge = document.createElement("p");
          badge.className = "badge-ouverture";
          badge.textContent = c.sales ? "Offre momentanément indisponible" : "Ouverture prochaine";
          bouton.replaceWith(badge);
        }
        return;
      }
      var prix = carte.querySelector("[data-prix]");
      var note = carte.querySelector("[data-note]");
      var standard = offre.standard && offre.standard.label;
      if (!standard) return;
      var campagne = c.campaign;
      var lancement = offre.launch && offre.launch.label;
      if (lancement && campagne && campagne.endsAt * 1000 > Date.now()) {
        var limite = offre.audience === "PRO"
          ? "sur le premier pack, pour les " + campagne.pro.resellers + " premiers revendeurs"
          : "dans la limite de " + campagne.consumer.licences + " licences";
        prix.textContent = lancement;
        note.textContent = "Tarif de lancement jusqu'au " + dateFr.format(new Date(campagne.endsAt * 1000)) + ", " + limite +
          ". Tarif prévu ensuite : " + standard + " " + offre.tax + ". Prix confirmé à la commande.";
        carte.dataset.lancement = "oui";
      } else {
        // Tarif standard du service (il prime sur celui de la page s'ils diffèrent).
        prix.textContent = standard;
      }
    });
  }

  var annulation = window.AbortController ? new AbortController() : null;
  var minuterie = setTimeout(function () { if (annulation) annulation.abort(); }, DELAI_MS);
  fetch(adresse, { method: "GET", credentials: "omit", cache: "no-cache", signal: annulation ? annulation.signal : undefined })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (c) { if (valide(c)) appliquer(c); })
    .catch(function () { /* service injoignable : tarifs standards conservés */ })
    .then(function () { clearTimeout(minuterie); });
})();
