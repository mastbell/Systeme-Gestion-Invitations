import os
import shutil

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app import models, schemas

router = APIRouter(prefix="/evenements", tags=["Événements"])


@router.post("/", response_model=schemas.EvenementOut)
def creer_evenement(payload: schemas.EvenementCreate, db: Session = Depends(get_db)):
    evenement = models.Evenement(**payload.model_dump())
    db.add(evenement)
    db.commit()
    db.refresh(evenement)
    return evenement


@router.get("/", response_model=list[schemas.EvenementOut])
def lister_evenements(db: Session = Depends(get_db)):
    return db.query(models.Evenement).all()


@router.get("/{evenement_id}", response_model=schemas.EvenementOut)
def obtenir_evenement(evenement_id: int, db: Session = Depends(get_db)):
    evenement = db.get(models.Evenement, evenement_id)
    if not evenement:
        raise HTTPException(404, "Événement introuvable")
    return evenement


@router.post("/{evenement_id}/modele")
def uploader_modele(evenement_id: int, fichier: UploadFile = File(...), db: Session = Depends(get_db)):
    evenement = db.get(models.Evenement, evenement_id)
    if not evenement:
        raise HTTPException(404, "Événement introuvable")

    os.makedirs(settings.dossier_modeles, exist_ok=True)
    chemin = os.path.join(settings.dossier_modeles, f"modele_evenement_{evenement_id}.png")
    with open(chemin, "wb") as f:
        shutil.copyfileobj(fichier.file, f)

    evenement.modele_invitation = chemin
    db.commit()
    return {"message": "Modèle enregistré", "chemin": chemin}
