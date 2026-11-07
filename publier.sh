#!/usr/bin/env bash
# Publication complète d'une version validée de CINOZA, en une commande (utilisable à distance par Claude Code) :
#
#   ./publier.sh <fichier.apk> "<nouveautés affichées dans le bandeau de mise à jour>"
#
# Enchaîne : publier-apk.sh --publier (contrôles bloquants, release GitHub, bouton du site, maj/), puis
# verifier-avant-publication.sh, puis commit et push du site. Refuse de démarrer si le site contient des
# modifications non enregistrées (seule la nouvelle version est publiée). Aucune clé n'est lue ni copiée ici.
set -euo pipefail
cd "$(dirname "$0")"

apk="${1:?Usage : ./publier.sh <fichier.apk> \"<nouveautés>\"}"
notes="${2:?Indiquez les nouveautés entre guillemets (affichées aux utilisateurs).}"
[ -f "$apk" ] || { echo "Fichier introuvable : $apk"; exit 1; }
if [ -n "$(git status --porcelain)" ]; then
  echo "Refusé : le site contient des modifications non enregistrées :"; git status --short; exit 1
fi

OUTILS="${ANDROID_HOME:-$HOME/Android/Sdk}/build-tools/35.0.0"
version="$("$OUTILS/aapt2" dump badging "$apk" | sed -n "s/.*versionName='\([^']*\)'.*/\1/p")"
[ -n "$version" ] || { echo "Version illisible dans $apk"; exit 1; }

echo "== Publication de CINOZA $version"
NOTES="$notes" ./publier-apk.sh "$apk" --publier

echo "== Vérification du site"
./verifier-avant-publication.sh

echo "== Enregistrement et envoi du site"
git add -A
git commit -q -m "CINOZA $version"
git push -q
git log --oneline -1
echo "CINOZA $version publiée. Mise en ligne du site par GitHub Pages en quelques minutes."
