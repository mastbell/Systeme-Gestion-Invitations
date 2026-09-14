from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(tags=["Scan"])

# Connexions WebSocket actives, groupées par événement
_connexions_actives: dict[int, list[WebSocket]] = {}


@router.post("/scan", response_model=schemas.ScanResponse)
async def scanner_invitation(payload: schemas.ScanRequest, db: Session = Depends(get_db)):
    invitation = (
        db.query(models.Invitation)
        .filter(models.Invitation.token_qr == payload.token_qr)
        .first()
    )

    if invitation is None:
        return schemas.ScanResponse(resultat="invalide")

    scan_existant = (
        db.query(models.Scan)
        .filter(
            models.Scan.invitation_id == invitation.id,
            models.Scan.resultat == models.ResultatScan.AUTORISE,
        )
        .first()
    )

    invite = invitation.invite

    if scan_existant is not None:
        db.add(models.Scan(
            invitation_id=invitation.id,
            organisateur_id=payload.organisateur_id,
            resultat=models.ResultatScan.DEJA_SCANNE,
        ))
        db.commit()
        return schemas.ScanResponse(
            resultat="deja_scanne",
            nom_complet=f"{invite.prenom} {invite.nom}",
            grade=invite.grade.value,
            date_premier_scan=scan_existant.date_scan,
        )

    nouveau_scan = models.Scan(
        invitation_id=invitation.id,
        organisateur_id=payload.organisateur_id,
        resultat=models.ResultatScan.AUTORISE,
    )
    db.add(nouveau_scan)
    db.commit()

    await _diffuser_arrivee(invite.evenement_id, invite.prenom, invite.nom, invite.grade.value)

    return schemas.ScanResponse(
        resultat="autorise",
        nom_complet=f"{invite.prenom} {invite.nom}",
        grade=invite.grade.value,
    )


@router.websocket("/ws/evenement/{evenement_id}")
async def websocket_dashboard(websocket: WebSocket, evenement_id: int):
    await websocket.accept()
    _connexions_actives.setdefault(evenement_id, []).append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _connexions_actives[evenement_id].remove(websocket)


async def _diffuser_arrivee(evenement_id: int, prenom: str, nom: str, grade: str):
    for connexion in _connexions_actives.get(evenement_id, []):
        await connexion.send_json({"prenom": prenom, "nom": nom, "grade": grade})


@router.get("/evenements/{evenement_id}/stats")
def stats_arrivees(evenement_id: int, db: Session = Depends(get_db)):
    invites = db.query(models.Invite).filter(models.Invite.evenement_id == evenement_id).all()
    total = len(invites)
    arrives_ids = {
        s.invitation_id for s in db.query(models.Scan).filter(
            models.Scan.resultat == models.ResultatScan.AUTORISE,
            models.Scan.invitation_id.in_([i.invitation.id for i in invites if i.invitation]),
        )
    }
    par_grade = {"prestige": [0, 0], "vip": [0, 0], "classique": [0, 0]}  # [arrivés, total]
    for invite in invites:
        g = invite.grade.value
        par_grade[g][1] += 1
        if invite.invitation and invite.invitation.id in arrives_ids:
            par_grade[g][0] += 1

    return {
        "total_invites": total,
        "total_arrives": len(arrives_ids),
        "par_grade": {g: {"arrives": v[0], "total": v[1]} for g, v in par_grade.items()},
    }
