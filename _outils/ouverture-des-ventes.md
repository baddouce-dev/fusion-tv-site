# Passage du site en version payante (ouverture des ventes)

Le site est prêt à basculer, mais reste en mode **bêta** tant que tout n'est pas validé. Dossier non servi par GitHub Pages.

1. Statut, TVA, médiateur, prestataire de paiement décidés ; CGV et mentions légales finalisées à partir de
   `_brouillons/` puis copiées à la racine (`cgv.html`, `mentions-legales.html`), sans aucun « [À COMPLÉTER] ».
2. `commerce.json` :
   - `"mode": "vente"` ;
   - `"url_commande"` : adresse https:// réelle de la page de commande (lot 7) ;
   - `"url_espace_revendeur"` : adresse de l'espace revendeur, si ouvert ;
   - `"contact_revendeurs"` : `revendeurs@fusion-tv.fr` une fois l'adresse créée ;
   - `"campagne"` : seulement si la campagne est **activée** dans FUSION Access, avec la même date de fin et les mêmes
     quotas (modèle : `_campagne_exemple`). Quota épuisé ou campagne terminée : remettre `null` et régénérer.
3. `python3 _outils/generer-pages.py`
4. `./verifier-avant-publication.sh` : il refuse le mode vente sans adresse de commande réelle, sans CGV définitives,
   avec des mentions légales de particulier, avec un bouton Commander sur Premium ou une campagne terminée.
5. Publication seulement après accord explicite.
