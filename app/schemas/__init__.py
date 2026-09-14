from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


# ---------- Événement ----------
class EvenementCreate(BaseModel):
    nom: str
    date_evenement: date
    lieu: str | None = None


class EvenementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nom: str
    date_evenement: date
    lieu: str | None = None
    modele_invitation: str | None = None


# ---------- Invité ----------
class InviteCreate(BaseModel):
    nom: str
    prenom: str
    telephone: str
    grade: str = "classique"


class InviteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    evenement_id: int
    nom: str
    prenom: str
    telephone: str
    grade: str
    source: str


# ---------- Invitation ----------
class InvitationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    invite_id: int
    token_qr: str
    fichier_genere: str | None = None
    statut_envoi: str


# ---------- Scan ----------
class ScanRequest(BaseModel):
    token_qr: str
    organisateur_id: int | None = None


class ScanResponse(BaseModel):
    resultat: str  # "autorise" | "deja_scanne" | "invalide"
    nom_complet: str | None = None
    grade: str | None = None
    date_premier_scan: datetime | None = None
