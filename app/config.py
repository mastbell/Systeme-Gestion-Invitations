"""
Configuration centralisée du projet.
Toutes les valeurs sensibles se règlent via le fichier .env (voir .env.example).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de données — SQLite par défaut pour démarrer sans rien installer.
    # En production, remplacer par une URL PostgreSQL, ex:
    # postgresql://user:password@localhost:5432/invitations_db
    database_url: str = "sqlite:///./invitations.db"

    # Twilio (WhatsApp / SMS) — laisser vide pour désactiver l'envoi réel
    # (le système fonctionne quand même, l'envoi est simplement simulé/journalisé)
    twilio_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""
    twilio_sms_from: str = ""

    # URL publique du serveur, utilisée pour construire les liens d'invitation
    # envoyés par WhatsApp/SMS (doit être accessible depuis internet en prod)
    url_publique: str = "http://localhost:8000"

    # Dossiers de stockage
    dossier_modeles: str = "static/modeles"
    dossier_invitations: str = "static/invitations_generees"
    dossier_fonts: str = "fonts"

    # JWT — clés et algorithme pour l'authentification sécurisée
    jwt_secret_key: str = "cle_secrete_demo_systeme_invitations"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60


settings = Settings()
