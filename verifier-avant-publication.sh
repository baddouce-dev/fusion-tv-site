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
lien_apk="$(grep -o 'https://github.com/[^"]*/releases/latest/download/fusion-tv.apk' index.html | head -1 || true)"
if [ -n "$lien_apk" ] && ! curl -sfIL -o /dev/null "$lien_apk"; then
  echo "Bouton de téléchargement actif mais APK introuvable : $lien_apk"; status=1
fi
# La copie directe doit être identique à l'APK de la dernière release (même empreinte que celle affichée).
if [ -f fusion-tv.apk ]; then
  affichee="$(grep -o 'SHA-256 : <code>[0-9a-f]\{64\}' index.html | grep -o '[0-9a-f]\{64\}' | head -1)"
  [ "$(sha256sum fusion-tv.apk | cut -d' ' -f1)" = "$affichee" ] || { echo "fusion-tv.apk ne correspond pas à l'empreinte affichée."; status=1; }
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
[ $status -eq 0 ] && echo "Prêt à publier."
exit $status
