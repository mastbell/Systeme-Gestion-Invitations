"""
Envoi des invitations par WhatsApp (canal principal) avec repli SMS.

Si les identifiants Twilio ne sont pas configurés dans .env, l'envoi est
simulé et journalisé — pratique pour tester tout le système sans compte
Twilio actif.
"""
from app.config import settings

_twilio_actif = bool(settings.twilio_sid and settings.twilio_auth_token)

if _twilio_actif:
    from twilio.rest import Client
    _client = Client(settings.twilio_sid, settings.twilio_auth_token)


def envoyer_whatsapp(telephone: str, url_image: str, nom: str, grade: str) -> dict:
    if not _twilio_actif:
        print(f"[SIMULATION WhatsApp] -> {telephone} | {nom} ({grade}) | image: {url_image}")
        return {"succes": True, "simule": True}

    try:
        message = _client.messages.create(
            from_=settings.twilio_whatsapp_from,
            to=f"whatsapp:{telephone}",
            body=f"Bonjour {nom}, voici votre invitation ({grade.upper()}).",
            media_url=[url_image],
        )
        return {"succes": True, "message_sid": message.sid}
    except Exception as e:
        return {"succes": False, "erreur": str(e)}


def envoyer_sms(telephone: str, url_image: str, nom: str) -> dict:
    if not _twilio_actif:
        print(f"[SIMULATION SMS] -> {telephone} | {nom} | lien: {url_image}")
        return {"succes": True, "simule": True}

    try:
        message = _client.messages.create(
            from_=settings.twilio_sms_from,
            to=telephone,
            body=f"Bonjour {nom}, voici votre invitation : {url_image}",
        )
        return {"succes": True, "message_sid": message.sid}
    except Exception as e:
        return {"succes": False, "erreur": str(e)}


def envoyer_invitation(telephone: str, url_image: str, nom: str, grade: str) -> str:
    """Retourne le statut à enregistrer : 'envoye' ou 'echec'."""
    resultat = envoyer_whatsapp(telephone, url_image, nom, grade)
    if resultat["succes"]:
        return "envoye"

    resultat_sms = envoyer_sms(telephone, url_image, nom)
    return "envoye" if resultat_sms["succes"] else "echec"
