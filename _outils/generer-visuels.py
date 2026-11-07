#!/usr/bin/env python3
"""Logos, icônes et image de partage du site, à partir des visuels officiels CINOZA (iptv-app/assets).
Redimensionnement seulement : aucun recadrage ni retouche ; l'image de partage garde le visuel entier sur fond noir.
Usage (depuis le dossier du site) : python3 -I _outils/generer-visuels.py
"""
from pathlib import Path

from PIL import Image

SITE = Path(__file__).resolve().parent.parent
SOURCES = SITE.parent / "assets"
IMG = SITE / "assets" / "img"


def main():
    logo = Image.open(SOURCES / "cinoza-logo.png").convert("RGBA")
    icone = Image.open(SOURCES / "cinoza-icon.png").convert("RGB")
    banniere = Image.open(SOURCES / "cinoza-banner.png").convert("RGB")
    for nom, largeur in (("logo-small.png", 280), ("logo.png", 560)):
        logo.resize((largeur, round(logo.height * largeur / logo.width)), Image.LANCZOS).save(IMG / nom, optimize=True)
    logo.resize((1120, round(logo.height * 1120 / logo.width)), Image.LANCZOS).save(IMG / "logo-grand.webp", quality=90)
    for nom, cote in (("favicon-32.png", 32), ("apple-touch-icon.png", 180), ("icon-512.png", 512)):
        icone.resize((cote, cote), Image.LANCZOS).save(IMG / nom, optimize=True)
    # Image de partage (réseaux sociaux) 1200 × 630 : bannière entière, hauteur 630, marges noires sur les côtés.
    hauteur = 630
    b = banniere.resize((round(banniere.width * hauteur / banniere.height), hauteur), Image.LANCZOS)
    partage = Image.new("RGB", (1200, 630), (0, 0, 0))
    partage.paste(b, ((1200 - b.width) // 2, 0))
    partage.save(IMG / "partage.jpg", quality=88, optimize=True)
    for nom in ("logo-small.png", "logo.png", "logo-grand.webp", "favicon-32.png", "apple-touch-icon.png", "icon-512.png", "partage.jpg"):
        im = Image.open(IMG / nom)
        print(f"{nom}  {im.size[0]}×{im.size[1]}")


if __name__ == "__main__":
    main()
