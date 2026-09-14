from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services.import_csv import lire_csv_invites
from app.services.generation_invitation import generer_et_sauvegarder

router = APIRouter(prefix="/evenements/{evenement_id}/invites", tags=["Invités"])


def _creer_invite_et_invitation(db: Session, evenement: models.Evenement, data: dict, source: str):
    invite = models.Invite(evenement_id=evenement.id, source=source, **data)
    db.add(invite)
    db.flush()  # pour obtenir invite.id avant de créer l'invitation

    invitation = models.Invitation(invite_id=invite.id)
    db.add(invitation)
    db.flush()
    invite.invitation = invitation

    if evenement.modele_invitation:
        chemin_fichier = generer_et_sauvegarder(evenement.modele_invitation, invite)
        invitation.fichier_genere = chemin_fichier

    return invite


@router.post("/", response_model=schemas.InviteOut)
def ajouter_invite_formulaire(evenement_id: int, payload: schemas.InviteCreate, db: Session = Depends(get_db)):
    evenement = db.get(models.Evenement, evenement_id)
    if not evenement:
        raise HTTPException(404, "Événement introuvable")

    invite = _creer_invite_et_invitation(db, evenement, payload.model_dump(), source="formulaire")
    db.commit()
    db.refresh(invite)
    return invite


@router.post("/import-csv")
def importer_csv(evenement_id: int, fichier: UploadFile = File(...), db: Session = Depends(get_db)):
    evenement = db.get(models.Evenement, evenement_id)
    if not evenement:
        raise HTTPException(404, "Événement introuvable")

    contenu = fichier.file.read()
    lignes_valides, erreurs = lire_csv_invites(contenu)

    invites_crees = []
    for ligne in lignes_valides:
        invite = _creer_invite_et_invitation(db, evenement, ligne, source="import")
        invites_crees.append(invite)

    db.commit()
    return {
        "invites_crees": len(invites_crees),
        "erreurs": erreurs,
    }


@router.get("/", response_model=list[schemas.InviteOut])
def lister_invites(evenement_id: int, db: Session = Depends(get_db)):
    return db.query(models.Invite).filter(models.Invite.evenement_id == evenement_id).all()
