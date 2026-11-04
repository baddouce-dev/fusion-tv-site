#!/usr/bin/env bash
# Publication d'une version validée de FUSION TV sur GitHub Releases, puis mise à jour de la section « Installer » du site.
#
#   ./publier-apk.sh <fichier.apk>              essai à blanc : contrôles et aperçu du site, rien n'est envoyé
#   ./publier-apk.sh <fichier.apk> --publier    crée la release (après accord explicite du propriétaire)
#                                               et remplace fusion-tv.apk (adresse courte fusion-tv.fr/fusion-tv.apk)
#
# Avec --publier, met aussi à jour maj/ (manifeste signé + APK) : les applications installées proposent alors la
# mise à jour (https://fusion-tv.fr/maj/). Nouveautés affichées dans la fenêtre : variable NOTES="…" (facultative).
#
# Contrôles bloquants : paquet com.iptv.player, APK non débogable, nom sans « debug » ni « candidat »,
# certificat de signature identique à l'empreinte attendue (compatibilité avec les installations existantes),
# version absente des releases déjà publiées. Aucune clé n'est lue ni copiée par ce script.
set -euo pipefail
cd "$(dirname "$0")"

DEPOT="baddouce-dev/fusion-tv-site"
OUTILS="${ANDROID_HOME:-$HOME/Android/Sdk}/build-tools/35.0.0"
# Empreinte SHA-256 du certificat attendu, conservée hors du dépôt public.
EMPREINTE_FICHIER="${EMPREINTE_FICHIER:-$HOME/.config/fusion-tv/distribution-certificat.sha256}"

apk="${1:?Usage : ./publier-apk.sh <fichier.apk> [--publier]}"
mode="${2:-essai}"
[ -f "$apk" ] || { echo "Fichier introuvable : $apk"; exit 1; }
[ -f "$EMPREINTE_FICHIER" ] || { echo "Empreinte de certificat attendue absente : $EMPREINTE_FICHIER"; exit 1; }

case "$(basename "$apk")" in
  *debug*|*candidat*|*candidate*) echo "Refusé : APK de débogage ou candidat."; exit 1 ;;
esac

badging="$("$OUTILS/aapt2" dump badging "$apk")"
paquet="$(sed -n "s/^package: name='\([^']*\)'.*/\1/p" <<<"$badging")"
version="$(sed -n "s/.*versionName='\([^']*\)'.*/\1/p" <<<"$badging")"
[ "$paquet" = "com.iptv.player" ] || { echo "Refusé : paquet inattendu ($paquet)."; exit 1; }
if grep -q "application-debuggable" <<<"$badging"; then echo "Refusé : APK débogable."; exit 1; fi

certificat="$("$OUTILS/apksigner" verify --print-certs "$apk" | sed -n 's/.*certificate SHA-256 digest: //p' | head -1)"
attendu="$(tr -d ' :\n' < "$EMPREINTE_FICHIER" | tr 'A-F' 'a-f')"
[ "$certificat" = "$attendu" ] || { echo "Refusé : certificat de signature différent de celui des installations existantes."; exit 1; }

empreinte="$(sha256sum "$apk" | cut -d' ' -f1)"
octets="$(stat -c %s "$apk")"
taille="$(LC_ALL=C awk -v o="$octets" 'BEGIN { printf "%.1f Mo", o / 1048576 }' | tr . ,)"
jour="$(date +%-d)"; [ "$jour" = 1 ] && jour="1er"
date_fr="$jour $(LC_ALL=fr_FR.UTF-8 date +'%B %Y')"

echo "FUSION TV $version — $taille — $date_fr"
echo "SHA-256 : $empreinte"

lien="https://github.com/$DEPOT/releases/latest/download/fusion-tv.apk"
bloc="            <!-- APK:DEBUT (bloc remplacé par publier-apk.sh à la publication d'une version validée) -->
            <a class=\"bouton\" href=\"$lien\" download><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.9\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"M12 3.5v11M7.5 10.5 12 15l4.5-4.5\"/><path d=\"M4 15.5v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3\"/></svg><span>Télécharger FUSION TV (.APK)</span></a>
            <dl class=\"apk-infos\">
              <div><dt>Version</dt><dd>$version</dd></div>
              <div><dt>Taille</dt><dd>$taille</dd></div>
              <div><dt>Publiée le</dt><dd>$date_fr</dd></div>
            </dl>
            <p class=\"apk-empreinte\">SHA-256 : <code>$empreinte</code> · <a href=\"https://github.com/$DEPOT/releases\">Versions précédentes</a></p>
            <!-- APK:FIN -->"

remplacer() { # $1 = fichier HTML à mettre à jour
  BLOC="$bloc" python3 -I - "$1" <<'EOF'
import os, re, sys
chemin = sys.argv[1]
texte = open(chemin, encoding="utf-8").read()
nouveau, n = re.subn(r"[ \t]*<!-- APK:DEBUT.*?<!-- APK:FIN -->", lambda _: os.environ["BLOC"], texte, flags=re.S)
if n != 1:
    sys.exit("Marqueurs APK:DEBUT / APK:FIN introuvables.")
open(chemin, "w", encoding="utf-8").write(nouveau)
EOF
}

# Manifeste signé des mises à jour intégrées (clé privée hors dépôt, ~/.config/fusion-updates) ; contrôles identiques.
MAJ_SCRIPT="$(cd .. && pwd)/fusion-updates/scripts/publish.py"
NOTES="${NOTES:-Nouvelle version de FUSION TV.}"
if [ "$mode" != "--publier" ]; then
  python3 -I "$MAJ_SCRIPT" "$apk" --dest maj --keep 1 --notes "$NOTES" --dry-run
  apercu="$(mktemp -d)"
  cp -r ./*.html assets "$apercu/"
  remplacer "$apercu/telecharger.html"
  echo "Essai à blanc : aperçu du site dans $apercu/telecharger.html (rien n'a été publié)."
  exit 0
fi

if gh release view "v$version" --repo "$DEPOT" >/dev/null 2>&1; then
  echo "Refusé : la version $version est déjà publiée."; exit 1
fi
travail="$(mktemp -d)"
cp "$apk" "$travail/fusion-tv-$version.apk"
cp "$apk" "$travail/fusion-tv.apk"
( cd "$travail" && sha256sum "fusion-tv-$version.apk" "fusion-tv.apk" > SHA256SUMS.txt )
gh release create "v$version" --repo "$DEPOT" --title "FUSION TV $version" \
  --notes "Bêta privée gratuite — activation FUSION Access requise. SHA-256 : $empreinte" \
  "$travail/fusion-tv-$version.apk" "$travail/fusion-tv.apk" "$travail/SHA256SUMS.txt"
# Bloc du téléchargement : page « Télécharger » du site.
remplacer telecharger.html
cp "$apk" fusion-tv.apk
python3 -I "$MAJ_SCRIPT" "$apk" --dest maj --keep 1 --notes "$NOTES"
echo "Release v$version publiée. Section « Installer » et maj/ mises à jour : vérifier, puis commiter et pousser le site."
