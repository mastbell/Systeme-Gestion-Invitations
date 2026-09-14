from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import evenements, invites, envoi, scan

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Système de gestion des invitations",
    description="Génération d'invitations avec QR code, envoi WhatsApp/SMS et scan à l'arrivée.",
    version="1.0.0",
)

app.include_router(evenements.router)
app.include_router(invites.router)
app.include_router(envoi.router)
app.include_router(scan.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def accueil():
    return {
        "message": "API du système de gestion des invitations",
        "documentation": "/docs",
        "page_ajout_invite": "/static/scan-app/ajouter_invite.html",
        "page_scan": "/static/scan-app/scan.html",
        "tableau_de_bord": "/static/scan-app/dashboard.html",
    }
