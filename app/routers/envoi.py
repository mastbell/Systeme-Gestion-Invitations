from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app import models
from app.services.envoi_notification import envoyer_invitation

router = APIRouter(prefix="/evenements/{evenement_id}", tags=["Envoi"])


@router.post("/envoyer-invitations")
def envoyer_invitations(evenement_id: int, db: Session = Depends(get_db)):
    evenement = db.get(models.Evenement, evenement_id)
    if not evenement:
        raise HTTPException(404, "Événement introuvable")

    invitations = (
        db.query(models.Invitation)
        .join(models.Invite)
        .filter(
            models.Invite.evenement_id == evenement_id,
            models.Invitation.statut_envoi == models.StatutEnvoi.EN_ATTENTE,
        )
        .all()
    )

    resultats = {"envoyes": 0, "echecs": 0}
    for invitation in invitations:
        invite = invitation.invite
        url_image = f"{settings.url_publique}/{invitation.fichier_genere}" if invitation.fichier_genere else ""

        statut = envoyer_invitation(invite.telephone, url_image, invite.prenom, invite.grade.value)
        invitation.statut_envoi = statut
        invitation.date_envoi = datetime.utcnow()

        resultats["envoyes" if statut == "envoye" else "echecs"] += 1

    db.commit()
    return resultats
