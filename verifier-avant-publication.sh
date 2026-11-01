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
[ $status -eq 0 ] && echo "Prêt à publier."
exit $status
