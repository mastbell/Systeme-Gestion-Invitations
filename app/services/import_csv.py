import csv
import io


COLONNES_ATTENDUES = {"nom", "prenom", "telephone", "grade"}


def lire_csv_invites(contenu_bytes: bytes) -> tuple[list[dict], list[str]]:
    """
    Parse un fichier CSV d'invités. Retourne (lignes_valides, erreurs).
    Colonnes attendues : nom, prenom, telephone, grade
    """
    texte = contenu_bytes.decode("utf-8-sig")
    lecteur = csv.DictReader(io.StringIO(texte))

    if lecteur.fieldnames is None or not COLONNES_ATTENDUES.issubset(
        {c.strip().lower() for c in lecteur.fieldnames}
    ):
        return [], [f"Colonnes attendues manquantes : {', '.join(COLONNES_ATTENDUES)}"]

    lignes_valides = []
    erreurs = []
    grades_valides = {"prestige", "vip", "classique"}

    for i, ligne in enumerate(lecteur, start=2):  # ligne 1 = en-têtes
        ligne = {k.strip().lower(): (v or "").strip() for k, v in ligne.items()}
        if not ligne.get("nom") or not ligne.get("prenom") or not ligne.get("telephone"):
            erreurs.append(f"Ligne {i} : nom, prénom ou téléphone manquant — ignorée")
            continue

        grade = ligne.get("grade", "classique").lower() or "classique"
        if grade not in grades_valides:
            erreurs.append(f"Ligne {i} : grade '{grade}' invalide, remplacé par 'classique'")
            grade = "classique"

        lignes_valides.append({
            "nom": ligne["nom"],
            "prenom": ligne["prenom"],
            "telephone": ligne["telephone"],
            "grade": grade,
        })

    return lignes_valides, erreurs
