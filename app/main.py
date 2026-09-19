from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import evenements, invites, envoi, scan, auth
from app import models
from app.services.auth_service import hash_password

Base.metadata.create_all(bind=engine)

# Comptes de démonstration pour tester les rôles sans impacter le fonctionnement de l’API existante.
def _creer_comptes_demo():
    from sqlalchemy.orm import Session
    db = Session(bind=engine)
    try:
        if not db.query(models.User).first():
            comptes = [
                ("admin@demo.local", "admin123", models.RoleUtilisateur.ADMIN, "Admin", "Système"),
                ("organisateur@demo.local", "org123", models.RoleUtilisateur.ORGANISATEUR, "Dupont", "Claire"),
                ("securite@demo.local", "sec123", models.RoleUtilisateur.SECURITE, "Martin", "Aïcha"),
            ]
            for email, password, role, nom, prenom in comptes:
                db.add(models.User(
                    email=email,
                    password_hash=hash_password(password),
                    nom=nom,
                    prenom=prenom,
                    role=role,
                    is_active=True,
                ))
            db.commit()
    finally:
        db.close()

_creer_comptes_demo()

app = FastAPI(
    title="Système de gestion des invitations",
    description="Génération d'invitations avec QR code, envoi WhatsApp/SMS, scan à l'arrivée et gestion multi-rôles.",
    version="1.1.0",
)

app.include_router(auth.router)
app.include_router(evenements.router)
app.include_router(invites.router)
app.include_router(envoi.router)
app.include_router(scan.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def accueil():
    return RedirectResponse(url="/static/index.html")


@app.get("/api")
def api_info():
    return {
        "message": "API du système de gestion des invitations",
        "documentation": "/docs",
        "page_accueil": "/static/index.html",
        "page_login": "/static/auth/login.html",
        "page_ajout_invite": "/static/scan-app/ajouter_invite.html",
        "page_scan": "/static/scan-app/scan.html",
        "tableau_de_bord": "/static/scan-app/dashboard.html",
    }
