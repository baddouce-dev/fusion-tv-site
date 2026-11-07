#!/usr/bin/env bash
# Refuse la publication tant qu'une information reste à compléter ou qu'un secret apparaît dans les fichiers.
set -euo pipefail
cd "$(dirname "$0")"
status=0
if grep -rn "__[A-Z]*__" --include=*.html . ; then
  echo "À compléter avant publication : marqueurs ci-dessus."; status=1
fi
if grep -rniE "api_key|password|mot de passe :|get\.php\?|player_api|BEGIN (EC|RSA|OPENSSH) PRIVATE" --include=*.html --include=*.css --include=*.js . ; then
  echo "Contenu sensible détecté."; status=1
fi
# Jamais de faux bouton actif : un lien de téléchargement doit pointer vers une release réellement publiée.
lien_apk="$(grep -o 'https://github.com/[^"]*/releases/latest/download/cinoza.apk' telecharger.html | head -1 || true)"
if [ -n "$lien_apk" ] && ! curl -sfIL -o /dev/null "$lien_apk"; then
  echo "Bouton de téléchargement actif mais APK introuvable : $lien_apk"; status=1
fi
# La copie directe doit être identique à l'APK de la dernière release (même empreinte que celle affichée).
if [ -f cinoza.apk ]; then
  affichee="$(grep -o 'SHA-256 : <code>[0-9a-f]\{64\}' telecharger.html | grep -o '[0-9a-f]\{64\}' | head -1)"
  [ "$(sha256sum cinoza.apk | cut -d' ' -f1)" = "$affichee" ] || { echo "cinoza.apk ne correspond pas à l'empreinte affichée."; status=1; }
fi
# Mises à jour intégrées : le manifeste doit désigner un APK présent dans maj/, à l'empreinte annoncée.
if [ -f maj/manifest.json ]; then
  python3 -I - <<'EOF' || status=1
import base64, hashlib, json, pathlib, sys
contenu = json.loads(base64.b64decode(json.loads(pathlib.Path("maj/manifest.json").read_text())["payload"]))
apk = pathlib.Path("maj") / contenu["apk"]["path"]
if not apk.is_file() or hashlib.sha256(apk.read_bytes()).hexdigest() != contenu["apk"]["sha256"]:
    sys.exit(f"maj/manifest.json désigne un APK absent ou différent : {apk}")
print(f"Mise à jour proposée aux applications : {contenu['versionName']} ({apk.name})")
EOF
fi
# Réglage commercial (commerce.json) : en bêta, aucune commande possible ; en vente, seulement si tout est définitif.
if [ -f commerce.json ]; then
  python3 -I - <<'EOF' || status=1
import json, pathlib, re, sys
r = json.loads(pathlib.Path("commerce.json").read_text())
pages = {p.name: p.read_text(encoding="utf-8") for p in pathlib.Path(".").glob("*.html")}
erreurs = []
commander = [n for n, t in pages.items() if 'class="bouton offre-commander"' in t]
if r["mode"] == "beta":
    if commander:
        erreurs.append(f"Mode bêta : bouton Commander présent ({', '.join(commander)}) — relancez _outils/generer-pages.py.")
elif r["mode"] == "vente":
    url = r.get("url_commande") or ""
    if not url.startswith("https://") or ".invalid" in url:
        erreurs.append("Mode vente : adresse de commande https:// réelle manquante dans commerce.json.")
    cgv = pages.get("cgv.html", "")
    if not cgv or re.search(r"À COMPLÉTER|BROUILLON", cgv):
        erreurs.append("Mode vente : cgv.html définitive absente du site (le brouillon de _brouillons/ n'est pas publiable).")
    mentions = pages.get("mentions-legales.html", "")
    if "éditeur non professionnel" in mentions or "À COMPLÉTER" in mentions:
        erreurs.append("Mode vente : mentions légales commerciales (identité de l'éditeur, SIRET…) à mettre en place.")
    if "offre-commander" in pages.get("premium.html", ""):
        erreurs.append("Premium n'est pas commercialisée : aucun bouton Commander sur premium.html.")
    if not (r.get("url_catalogue") or "").startswith("https://"):
        erreurs.append("Mode vente : adresse https:// du catalogue public de CINOZA Access manquante dans commerce.json.")
    # Tarif de lancement : jamais écrit dans les pages (seul le catalogue de CINOZA Access le confirme).
    for n, t in pages.items():
        if "Tarif de lancement jusqu" in t:
            erreurs.append(f"{n} : tarif de lancement écrit en dur — il ne doit venir que du catalogue de CINOZA Access.")
else:
    erreurs.append("commerce.json : mode inconnu (beta ou vente).")
for e in erreurs:
    print(e)
sys.exit(1 if erreurs else 0)
EOF
fi
[ $status -eq 0 ] && echo "Prêt à publier."
exit $status
