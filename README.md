# Système de gestion des invitations

Génère automatiquement des invitations personnalisées (nom, prénom, grade)
avec QR code unique, les envoie par WhatsApp/SMS, et permet de scanner les
QR codes à l'arrivée des invités avec un tableau de bord en temps réel.

## Fonctionnalités

- Ajout d'invités par **formulaire** ou **import CSV** en masse
- Génération automatique de l'invitation (fusion modèle + nom + grade + QR code)
- Envoi par **WhatsApp** (avec repli SMS automatique) via Twilio
- Application de **scan** (caméra du téléphone ou saisie manuelle) avec 3 statuts :
  accès autorisé / déjà scanné / invitation invalide
- **Tableau de bord temps réel** des arrivées (par grade), mis à jour par WebSocket

## Installation

```bash
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # puis éditer .env si besoin (Twilio, etc.)
```

Aucune base de données à installer pour tester : le projet utilise **SQLite**
par défaut (fichier `invitations.db` créé automatiquement au premier lancement).

## Lancer le projet

```bash
uvicorn app.main:app --reload
```

Puis ouvrir :
- **Documentation API interactive** : http://localhost:8000/docs
- **Formulaire événement/invités** : http://localhost:8000/static/scan-app/ajouter_invite.html
- **Page de scan** : http://localhost:8000/static/scan-app/scan.html
- **Tableau de bord** : http://localhost:8000/static/scan-app/dashboard.html

## Tester le système pas à pas

1. Ouvrir le **formulaire** → créer un événement (nom, date, lieu) → noter l'ID retourné
2. Toujours dans le formulaire → uploader `static/modeles/modele_defaut.png` comme modèle
   (un modèle d'exemple est déjà fourni dans ce projet, prêt à l'emploi)
3. Ajouter un ou plusieurs invités (nom, prénom, téléphone, grade) → l'invitation est
   générée automatiquement dans `static/invitations_generees/`
4. Récupérer le token QR d'un invité via `GET /docs` → `/evenements/{id}/invites/`,
   ou simplement ouvrir l'image générée et scanner le QR affiché
5. Ouvrir la **page de scan** sur un téléphone (même réseau Wi-Fi) et scanner le QR,
   ou coller le token dans le champ de saisie manuelle
6. Ouvrir le **tableau de bord**, entrer l'ID de l'événement → voir l'arrivée
   apparaître en temps réel

Sans identifiants Twilio configurés, l'envoi WhatsApp/SMS est **simulé** et
journalisé dans la console du serveur — pratique pour tester sans compte Twilio.

## Configurer l'envoi réel (Twilio)

1. Créer un compte sur https://www.twilio.com et activer WhatsApp Business
   (ou utiliser le bac à sable Twilio pour les tests)
2. Renseigner dans `.env` : `TWILIO_SID`, `TWILIO_AUTH_TOKEN`,
   `TWILIO_WHATSAPP_FROM`, `TWILIO_SMS_FROM`
3. Renseigner `URL_PUBLIQUE` avec l'adresse publique du serveur (obligatoire :
   Twilio doit pouvoir télécharger l'image de l'invitation depuis internet)

## Personnaliser le modèle d'invitation

Le modèle par défaut (`static/modeles/modele_defaut.png`) peut être remplacé
par ton propre visuel (upload via le formulaire ou l'endpoint
`POST /evenements/{id}/modele`). Si tu changes la mise en page, ajuste les
coordonnées dans `app/services/generation_invitation.py` (dictionnaire
`LAYOUT`) pour que le nom, le grade et le QR code tombent au bon endroit.

Pour régénérer le modèle par défaut à partir du script fourni :
```bash
python scripts_utilitaires/generer_modele.py
```

## Passer en production

- **Base de données** : remplacer `DATABASE_URL` dans `.env` par une URL
  PostgreSQL (ajouter `psycopg2-binary` dans `requirements.txt`)
- **Stockage des images** : héberger `static/invitations_generees/` sur un
  stockage externe (Cloudinary, S3) plutôt que le disque local si tu déploies
  sur une plateforme éphémère
- **Hébergement** : voir les recommandations discutées (Railway pour la
  simplicité, ou AWS Lightsail/EC2 pour rester dans l'écosystème AWS à coût
  maîtrisé)
- Ajouter une authentification sur les endpoints d'administration
  (`/evenements`, `/invites`) avant un déploiement public

## Structure du projet

```
app/
├── main.py                # point d'entrée FastAPI
├── config.py               # configuration (.env)
├── database.py              # connexion SQLAlchemy
├── models/                  # tables de la base de données
├── schemas/                 # validation des entrées/sorties API
├── routers/                 # endpoints (événements, invités, envoi, scan)
└── services/                 # logique métier (QR, génération image, import, envoi)

static/
├── modeles/                 # modèles d'invitation (dont modele_defaut.png)
├── invitations_generees/    # invitations générées par invité
└── scan-app/                 # pages web (formulaire, scan, dashboard)

scripts_utilitaires/
├── generer_modele.py         # régénère le modèle d'invitation par défaut
└── test_generation.py        # test rapide de la génération
```
