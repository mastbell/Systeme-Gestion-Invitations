"""
Génère un modèle d'invitation par défaut (1200x800 px), élégant et sobre,
dont les zones vides (nom, grade, QR code) correspondent au LAYOUT défini
dans app/services/generation_invitation.py.

Usage : python scripts_utilitaires/generer_modele.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

LARGEUR, HAUTEUR = 1200, 800
FONTS_DIR = "fonts"
SORTIE = "static/modeles/modele_defaut.png"


def degrade_vertical(largeur, hauteur, couleur_haut, couleur_bas):
    base = Image.new("RGB", (largeur, hauteur), couleur_haut)
    top = Image.new("RGB", (largeur, hauteur), couleur_bas)
    masque = Image.new("L", (largeur, hauteur))
    for y in range(hauteur):
        valeur = int(255 * (y / hauteur))
        for x in range(largeur):
            masque.putpixel((x, y), valeur)
    base.paste(top, (0, 0), masque)
    return base


def generer():
    img = degrade_vertical(LARGEUR, HAUTEUR, (18, 20, 28), (35, 28, 20))
    dessin = ImageDraw.Draw(img)

    # Cadre décoratif doré
    marge = 28
    dessin.rectangle(
        [marge, marge, LARGEUR - marge, HAUTEUR - marge],
        outline=(212, 175, 55), width=3,
    )
    dessin.rectangle(
        [marge + 10, marge + 10, LARGEUR - marge - 10, HAUTEUR - marge - 10],
        outline=(212, 175, 55, 120), width=1,
    )

    police_titre = ImageFont.truetype(os.path.join(FONTS_DIR, "DejaVuSerif-Bold.ttf"), 54)
    police_soustitre = ImageFont.truetype(os.path.join(FONTS_DIR, "DejaVuSans.ttf"), 22)
    police_label = ImageFont.truetype(os.path.join(FONTS_DIR, "DejaVuSans.ttf"), 16)

    # Titre
    dessin.text((LARGEUR / 2, 110), "VOUS ÊTES CORDIALEMENT INVITÉ(E)",
                font=police_soustitre, fill=(212, 175, 55), anchor="mm")
    dessin.text((LARGEUR / 2, 175), "ÉVÉNEMENT", font=police_titre, fill="#ffffff", anchor="mm")

    # Ligne décorative
    dessin.line([(LARGEUR / 2 - 120, 225), (LARGEUR / 2 + 120, 225)], fill=(212, 175, 55), width=2)

    # Zones réservées au nom et au grade : simple ligne de soulignement discrète
    # (le texte réel est superposé par app/services/generation_invitation.py
    #  aux coordonnées définies dans LAYOUT — garder ces zones vides ici)
    dessin.line([(380, 450), (780, 450)], fill=(90, 90, 90), width=1)
    dessin.line([(380, 505), (700, 505)], fill=(90, 90, 90), width=1)

    # Zone réservée au QR code — cadre indicatif
    dessin.rectangle([820, 250, 1070, 500], outline=(90, 90, 90), width=1)
    dessin.text((945, 510), "QR CODE D'ACCÈS", font=police_label, fill=(120, 120, 120), anchor="mm")

    # Pied de page
    dessin.text((LARGEUR / 2, HAUTEUR - 60), "Présentez ce QR code à l'entrée",
                font=police_label, fill=(160, 160, 160), anchor="mm")

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    img.save(SORTIE, quality=95)
    print(f"Modèle généré : {SORTIE}")


if __name__ == "__main__":
    generer()
