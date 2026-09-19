import uuid
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Grade(str, enum.Enum):
    PRESTIGE = "prestige"
    VIP = "vip"
    CLASSIQUE = "classique"


class StatutEnvoi(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    ENVOYE = "envoye"
    ECHEC = "echec"


class ResultatScan(str, enum.Enum):
    AUTORISE = "autorise"
    DEJA_SCANNE = "deja_scanne"
    INVALIDE = "invalide"


class RoleUtilisateur(str, enum.Enum):
    ADMIN = "admin"
    ORGANISATEUR = "organisateur"
    SECURITE = "securite"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nom = Column(String(100), nullable=True)
    prenom = Column(String(100), nullable=True)
    role = Column(Enum(RoleUtilisateur), nullable=False, default=RoleUtilisateur.ORGANISATEUR)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    evenements = relationship("Evenement", back_populates="organisateur", cascade="all, delete-orphan")
    event_access = relationship("UserEventAccess", back_populates="user", cascade="all, delete-orphan")


class Evenement(Base):
    __tablename__ = "evenement"

    id = Column(Integer, primary_key=True)
    nom = Column(String(150), nullable=False)
    date_evenement = Column(Date, nullable=False)
    lieu = Column(String(200))
    modele_invitation = Column(String(255))  # chemin vers l'image de modèle
    organisateur_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    organisateur = relationship("User", back_populates="evenements")
    invites = relationship("Invite", back_populates="evenement", cascade="all, delete-orphan")
    access = relationship("UserEventAccess", back_populates="evenement", cascade="all, delete-orphan")


class UserEventAccess(Base):
    __tablename__ = "user_event_access"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    evenement_id = Column(Integer, ForeignKey("evenement.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="event_access")
    evenement = relationship("Evenement", back_populates="access")


class Invite(Base):
    __tablename__ = "invite"

    id = Column(Integer, primary_key=True)
    evenement_id = Column(Integer, ForeignKey("evenement.id"), nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    telephone = Column(String(20), nullable=False)
    grade = Column(Enum(Grade), nullable=False, default=Grade.CLASSIQUE)
    source = Column(String(20), default="formulaire")  # "import" ou "formulaire"

    evenement = relationship("Evenement", back_populates="invites")
    invitation = relationship(
        "Invitation", back_populates="invite", uselist=False, cascade="all, delete-orphan"
    )


class Invitation(Base):
    __tablename__ = "invitation"

    id = Column(Integer, primary_key=True)
    invite_id = Column(Integer, ForeignKey("invite.id"), unique=True, nullable=False)
    token_qr = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    fichier_genere = Column(String(255))
    statut_envoi = Column(Enum(StatutEnvoi), default=StatutEnvoi.EN_ATTENTE)
    date_envoi = Column(DateTime)

    invite = relationship("Invite", back_populates="invitation")
    scans = relationship("Scan", back_populates="invitation", cascade="all, delete-orphan")


class Organisateur(Base):
    __tablename__ = "organisateur"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    mot_de_passe_hash = Column(String(255), nullable=False)


class Scan(Base):
    __tablename__ = "scan"

    id = Column(Integer, primary_key=True)
    invitation_id = Column(Integer, ForeignKey("invitation.id"), nullable=False)
    organisateur_id = Column(Integer, ForeignKey("organisateur.id"), nullable=True)
    date_scan = Column(DateTime, default=datetime.utcnow)
    resultat = Column(Enum(ResultatScan), nullable=False)

    invitation = relationship("Invitation", back_populates="scans")
