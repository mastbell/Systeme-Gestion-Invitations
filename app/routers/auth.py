from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.services.auth_service import create_access_token, get_current_user, hash_password, require_role, user_can_access_event, verify_password

router = APIRouter(tags=["Authentification"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    nom: str | None = None
    prenom: str | None = None
    role: str = "organisateur"


class SecurityAssignmentRequest(BaseModel):
    email: str
    password: str
    nom: str | None = None
    prenom: str | None = None
    evenement_id: int


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    email: str


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compte désactivé")

    token = create_access_token(user)
    return LoginResponse(
        access_token=token,
        role=user.role.value,
        user_id=user.id,
        email=user.email,
    )


@router.get("/auth/me")
def me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value,
        "nom": current_user.nom,
        "prenom": current_user.prenom,
    }


@router.post("/auth/register")
def register_admin_or_organisateur(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "organisateur")),
):
    if current_user.role == models.RoleUtilisateur.ORGANISATEUR and payload.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Un organisateur ne peut pas créer un administrateur")

    if db.query(models.User).filter(models.User.email == payload.email.lower()).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet email est déjà utilisé")

    role = models.RoleUtilisateur(payload.role)
    user = models.User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        nom=payload.nom,
        prenom=payload.prenom,
        role=role,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Compte créé", "user_id": user.id, "role": user.role.value}


@router.post("/auth/register-security")
def register_security(
    payload: SecurityAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "organisateur")),
):
    if current_user.role == models.RoleUtilisateur.ORGANISATEUR:
        evenement = db.get(models.Evenement, payload.evenement_id)
        if not evenement or evenement.organisateur_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous ne pouvez créer un agent pour cet événement")

    if db.query(models.User).filter(models.User.email == payload.email.lower()).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet email est déjà utilisé")

    user = models.User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        nom=payload.nom,
        prenom=payload.prenom,
        role=models.RoleUtilisateur.SECURITE,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.flush()

    db.add(models.UserEventAccess(user_id=user.id, evenement_id=payload.evenement_id))
    db.commit()

    return {
        "message": "Compte sécurité créé",
        "user_id": user.id,
        "email": user.email,
        "evenement_id": payload.evenement_id,
    }


@router.get("/auth/demo-users")
def demo_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [
        {
            "email": user.email,
            "role": user.role.value,
            "password": "admin123" if user.role == models.RoleUtilisateur.ADMIN else "org123" if user.role == models.RoleUtilisateur.ORGANISATEUR else "sec123",
        }
        for user in users
    ]


@router.get("/auth/event-access/{evenement_id}")
def event_access(evenement_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    allowed = user_can_access_event(current_user, evenement_id, db)
    return {"evenement_id": evenement_id, "allowed": allowed, "role": current_user.role.value}
