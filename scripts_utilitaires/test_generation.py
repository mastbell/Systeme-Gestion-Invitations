"""Test rapide : simule un invité et génère son invitation complète."""
import sys
sys.path.insert(0, ".")

from types import SimpleNamespace
from app.services.generation_invitation import generer_invitation

invite_test = SimpleNamespace(
    nom="Ndoumbe Ateba",
    prenom="Jean-Baptiste",
    grade=SimpleNamespace(value="prestige"),
    invitation=SimpleNamespace(token_qr="3f9a1e2b-7c4d-4a1e-9f2a-test000001"),
)

image = generer_invitation("static/modeles/modele_defaut.png", invite_test)
image.save("static/invitations_generees/exemple_test.png", quality=95)
print("Invitation d'exemple générée : static/invitations_generees/exemple_test.png")
