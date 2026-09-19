# Système de gestion des invitations

Génère automatiquement des invitations personnalisées (nom, prénom, grade)
avec QR code unique, les envoie par WhatsApp/SMS, et permet de scanner les
QR codes à l'arrivée des invités avec un tableau de bord en temps réel.

Le projet inclut désormais une couche d’authentification multi-rôles pour
séparer les accès entre administrateurs, organisateurs et agents de sécurité,
avec une gestion de confidentialité sur les listes d’invités par événement.

## Fonctionnalités

- Ajout d'invités par **formulaire** ou **import CSV** en masse
- Génération automatique de l'invitation (fusion modèle + nom + grade + QR code)
- Envoi par **WhatsApp** (avec repli SMS automatique) via Twilio
- Application de **scan** (caméra du téléphone ou saisie manuelle) avec 3 statuts :
  accès autorisé / déjà scanné / invitation invalide
- **Tableau de bord temps réel** des arrivées (par grade), mis à jour par WebSocket
- **Pages d’accueil et de connexion** avec rôles distincts :
  - administrateur
  - organisateur
  - agent de sécurité
- **Contrôle d’accès par rôle et par événement** pour préserver la confidentialité
  des listes d’invités et des contenus sensibles

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
- **Page d’accueil** : http://localhost:8000/
- **Connexion** : http://localhost:8000/static/auth/login.html
- **Documentation API interactive** : http://localhost:8000/docs
- **Formulaire événement/invités** : http://localhost:8000/static/scan-app/ajouter_invite.html
- **Page de scan** : http://localhost:8000/static/scan-app/scan.html
- **Tableau de bord** : http://localhost:8000/static/scan-app/dashboard.html

## Comptes de démonstration

Au premier lancement, le projet crée automatiquement des comptes de test :

- Administrateur : `admin@demo.local` / `admin123`
- Organisateur : `organisateur@demo.local` / `org123`
- Agent de sécurité : `securite@demo.local` / `sec123`

Ces comptes sont destinés au test local et permettent de valider les différents
parcours d’accès sans casser le fonctionnement actuel du système.

## Tester le système pas à pas

1. Ouvrir la **page d’accueil** puis aller sur **Connexion**
2. Se connecter avec un compte démo selon le rôle voulu
3. Ouvrir le **formulaire** ou le **dashboard organisateur** pour créer un événement
4. Uploader `static/modeles/modele_defaut.png` comme modèle
5. Ajouter un ou plusieurs invités
6. Scanner le QR depuis la **page de scan**
7. Vérifier le **tableau de bord** pour les arrivées en temps réel

### Flux recommandés par rôle

- **Admin** : contrôle global, supervision, gestion multi-événements
- **Organisateur** : création d’événements et comptes sécurité liés à ses événements
- **Agent de sécurité** : accès limité aux événements qui lui sont assignés

## Sécurité et confidentialité

Le système applique une séparation logique des accès :

- un administrateur peut superviser tous les événements
- un organisateur ne voit que ses propres événements
- un agent de sécurité ne peut accéder qu’aux événements assignés
- les listes d’invités restent filtrées côté backend selon le contexte de l’utilisateur

À titre de démonstration locale, les permissions sont gérées via JWT et rôles,
mais en production il faut aussi renforcer la protection avec :
- HTTPS obligatoire
- mot de passe fort / rotation régulière
- journalisation des accès
- authentification forte côté reverse proxy ou cloud

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
├── main.py                # point d'entrée FastAPI + comptes démo / routes auth
├── config.py               # configuration (.env, JWT)
├── database.py              # connexion SQLAlchemy
├── models/                  # tables de la base de données + utilisateurs / accès
├── schemas/                 # validation des entrées/sorties API
├── routers/                 # endpoints (auth, événements, invités, envoi, scan)
├── services/                # logique métier (auth, QR, génération image, import, envoi)
└── ...

static/
├── index.html               # page d’accueil
├── auth/
│   └── login.html           # page de connexion
├── admin/                   # dashboard administrateur
├── organisateur/            # dashboard organisateur
├── securite/                # dashboard agent de sécurité
├── modeles/                 # modèles d'invitation (dont modele_defaut.png)
├── invitations_generees/    # invitations générées par invité
├── scan-app/                # pages web (formulaire, scan, dashboard)
└── ...

scripts_utilitaires/
├── generer_modele.py         # régénère le modèle d'invitation par défaut
└── test_generation.py        # test rapide de la génération
```
