"""
Fusionne le modèle d'invitation (image de fond) avec les informations
de l'invité et son QR code, pour produire une invitation personnalisée.

Le modèle original n'est jamais modifié : il est rechargé à chaque génération.
"""
import os
from PIL import Image, ImageDraw, ImageFont

from app.config import settings
from app.services.qr_code import generer_qr

# Coordonnées des zones sur le modèle par défaut (1200x800 px).
# Si tu utilises un autre modèle avec une mise en page différente,
# ajuste ces valeurs en conséquence.
LAYOUT = {
    "nom_prenom": {"x": 380, "y": 430, "font_size": 42, "couleur": "#ffffff"},
    "grade": {"x": 380, "y": 490, "font_size": 26},
    "qr_code": {"x": 830, "y": 260, "taille": 220},
}

COULEURS_GRADE = {
    "prestige": "#D4AF37",
    "vip": "#B497FF",
    "classique": "#CFCFCF",
}


def _police(nom_fichier: str, taille: int) -> ImageFont.FreeTypeFont:
    chemin = os.path.join(settings.dossier_fonts, nom_fichier)
    return ImageFont.truetype(chemin, taille)


def _ajuster_taille_texte(dessin, texte, police_base, chemin_police, taille_max, largeur_max):
    """Réduit la taille de police si le texte dépasse la largeur disponible."""
    taille = taille_max
    police = police_base
    while dessin.textlength(texte, font=police) > largeur_max and taille > 14:
        taille -= 2
        police = ImageFont.truetype(chemin_police, taille)
    return police


def generer_invitation(chemin_modele: str, invite, layout: dict = None) -> Image.Image:
    layout = layout or LAYOUT
    modele = Image.open(chemin_modele).convert("RGB")
    dessin = ImageDraw.Draw(modele)

    chemin_police_nom = os.path.join(settings.dossier_fonts, "DejaVuSerif-Bold.ttf")
    police_nom = ImageFont.truetype(chemin_police_nom, layout["nom_prenom"]["font_size"])
    texte_nom = f"{invite.prenom} {invite.nom}"
    police_nom = _ajuster_taille_texte(
        dessin, texte_nom, police_nom, chemin_police_nom,
        layout["nom_prenom"]["font_size"], largeur_max=420,
    )
    dessin.text(
        (layout["nom_prenom"]["x"], layout["nom_prenom"]["y"]),
        texte_nom,
        font=police_nom,
        fill=layout["nom_prenom"]["couleur"],
        anchor="lm",
    )

    police_grade = _police("DejaVuSans-Bold.ttf", layout["grade"]["font_size"])
    grade_valeur = invite.grade.value if hasattr(invite.grade, "value") else invite.grade
    couleur_grade = COULEURS_GRADE.get(grade_valeur, "#ffffff")
    dessin.text(
        (layout["grade"]["x"], layout["grade"]["y"]),
        grade_valeur.upper(),
        font=police_grade,
        fill=couleur_grade,
        anchor="lm",
    )

    qr_img = generer_qr(invite.invitation.token_qr, layout["qr_code"]["taille"])
    # petit cadre blanc autour du QR pour un meilleur contraste sur fond sombre
    cadre = Image.new("RGB", (qr_img.width + 20, qr_img.height + 20), "#ffffff")
    cadre.paste(qr_img, (10, 10))
    modele.paste(cadre, (layout["qr_code"]["x"], layout["qr_code"]["y"]))

    return modele


def generer_et_sauvegarder(chemin_modele: str, invite, layout: dict = None) -> str:
    os.makedirs(settings.dossier_invitations, exist_ok=True)
    image = generer_invitation(chemin_modele, invite, layout)
    nom_fichier = f"invitation_{invite.invitation.token_qr}.png"
    chemin_sortie = os.path.join(settings.dossier_invitations, nom_fichier)
    image.save(chemin_sortie, quality=95)
    return chemin_sortie
