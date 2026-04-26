"""
Script pour diagnostiquer et réparer l'utilisateur Keycloak
"""
import requests
from requests.auth import HTTPBasicAuth
import json

# Configuration Keycloak
KEYCLOAK_URL = "http://localhost:8080"
REALM = "hr-analytics"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "admin"

def get_admin_token():
    """Obtenir un token admin"""
    url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": "admin-cli",
        "username": ADMIN_USER,
        "password": ADMIN_PASSWORD
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Erreur obtention token: {response.status_code}")
        print(response.text)
        return None

def check_user(token, username):
    """Vérifier l'état d'un utilisateur"""
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"username": username}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        users = response.json()
        if users:
            user = users[0]
            print(f"\n✅ Utilisateur trouvé: {user['username']}")
            print(f"   - ID: {user['id']}")
            print(f"   - Email: {user.get('email', 'N/A')}")
            print(f"   - Enabled: {user.get('enabled', False)}")
            print(f"   - Email Verified: {user.get('emailVerified', False)}")
            return user
        else:
            print(f"❌ Utilisateur '{username}' introuvable dans Keycloak")
            return None
    else:
        print(f"❌ Erreur recherche utilisateur: {response.status_code}")
        print(response.text)
        return None

def enable_user(token, user_id):
    """Activer un utilisateur"""
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "enabled": True,
        "emailVerified": True
    }
    
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 204:
        print("✅ Utilisateur activé avec succès")
        return True
    else:
        print(f"❌ Erreur activation: {response.status_code}")
        print(response.text)
        return False

def reset_password(token, user_id, new_password):
    """Réinitialiser le mot de passe"""
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/reset-password"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "password",
        "value": new_password,
        "temporary": False
    }
    
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 204:
        print(f"✅ Mot de passe réinitialisé: {new_password}")
        return True
    else:
        print(f"❌ Erreur reset password: {response.status_code}")
        print(response.text)
        return False

def test_login(username, password):
    """Tester la connexion"""
    url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": "hr-analytics-app",
        "username": username,
        "password": password
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print(f"✅ Connexion réussie pour {username}")
        return True
    else:
        print(f"❌ Échec connexion: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DIAGNOSTIC KEYCLOAK - Utilisateur karim.alaoui")
    print("=" * 60)
    
    # 1. Obtenir token admin
    print("\n[1] Connexion admin...")
    token = get_admin_token()
    if not token:
        print("❌ Impossible de se connecter comme admin")
        print("Vérifiez que Keycloak est démarré sur http://localhost:8080")
        exit(1)
    
    # 2. Vérifier l'utilisateur
    print("\n[2] Recherche utilisateur karim.alaoui...")
    user = check_user(token, "karim.alaoui")
    
    if user:
        user_id = user["id"]
        
        # 3. Activer l'utilisateur si nécessaire
        if not user.get("enabled", False):
            print("\n[3] Activation de l'utilisateur...")
            enable_user(token, user_id)
        else:
            print("\n[3] L'utilisateur est déjà activé")
        
        # 4. Réinitialiser le mot de passe
        print("\n[4] Réinitialisation du mot de passe...")
        reset_password(token, user_id, "Manager2026!")
        
        # 5. Tester la connexion
        print("\n[5] Test de connexion...")
        test_login("karim.alaoui", "Manager2026!")
    else:
        print("\n⚠️  L'utilisateur n'existe pas dans Keycloak")
        print("Tu dois créer l'utilisateur manuellement dans l'admin console:")
        print("1. Ouvre http://localhost:8080/admin")
        print("2. Realm: hr-analytics")
        print("3. Users > Add user")
        print("   - Username: karim.alaoui")
        print("   - Email: karim.alaoui@soprahr.com")
        print("   - Email verified: ON")
        print("   - Enabled: ON")
        print("4. Credentials > Set password: Manager2026!")
        print("   - Temporary: OFF")
    
    print("\n" + "=" * 60)
    print("FIN DU DIAGNOSTIC")
    print("=" * 60)
