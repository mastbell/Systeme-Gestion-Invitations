import qrcode


def generer_qr(token: str, taille_px: int = 220):
    """Génère une image QR code encodant uniquement le token (jamais les infos en clair)."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # tolère ~15% de dégradation
        box_size=10,
        border=2,
    )
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img.resize((taille_px, taille_px))
