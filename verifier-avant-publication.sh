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
[ $status -eq 0 ] && echo "Prêt à publier."
exit $status
