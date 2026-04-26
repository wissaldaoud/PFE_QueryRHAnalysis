"""
Appeler l'endpoint pour mettre à jour les types de contrats
"""
import requests

# D'abord, se connecter pour obtenir un token
print("🔐 Connexion...")
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={
        "username": "admin@sopra.com",  # Ajustez si nécessaire
        "password": "admin123"  # Ajustez si nécessaire
    }
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print("✅ Connecté!")
    
    # Appeler l'endpoint de mise à jour
    print("\n🔧 Mise à jour des types de contrats...")
    response = requests.post(
        "http://localhost:8000/api/v1/employees/fix-contract-types",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"📊 Employés mis à jour: {result['updated_count']}")
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(response.text)
else:
    print(f"❌ Échec de connexion: {login_response.status_code}")
    print("Essayez avec d'autres identifiants:")
    print("  Username: admin@sopra.com (ou votre email admin)")
    print("  Password: votre mot de passe")
